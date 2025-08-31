"""Atomicity Manager - ACID Transaction Atomicity Controller

Enterprise-grade atomicity management ensuring all-or-nothing transaction
semantics across distributed systems and multiple database resources.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.
"""import asyncio
import uuid
import logging
import weakref
from typing import Dict, List, Any, Optional, Callable, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import threading
from concurrent.futures import ThreadPoolExecutor
import traceback

logger = logging.getLogger(__name__)


class OperationState(Enum):
    """Operation state enumeration"""    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class AtomicOperationType(Enum):
    """Types of atomic operations"""    DATABASE_WRITE = "database_write"
    FILE_OPERATION = "file_operation"
    EXTERNAL_API = "external_api"
    CACHE_UPDATE = "cache_update"
    MESSAGE_QUEUE = "message_queue"
    CUSTOM = "custom"


@dataclass
class AtomicOperation:
    """Individual atomic operation within a transaction"""    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: AtomicOperationType = AtomicOperationType.CUSTOM
    state: OperationState = OperationState.PENDING
    execute_func: Optional[Callable] = None
    rollback_func: Optional[Callable] = None
    validate_func: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate operation duration"""        if self.executed_at and self.completed_at:
            return (self.completed_at - self.executed_at).total_seconds()
        return None
    
    def is_executable(self) -> bool:
        """Check if operation can be executed"""        return (self.state == OperationState.PENDING and 
                self.execute_func is not None and
                self.retry_count <= self.max_retries)
    
    def is_rollbackable(self) -> bool:
        """Check if operation can be rolled back"""        return (self.state == OperationState.COMPLETED and 
                self.rollback_func is not None)


class AtomicOperationGroup:
    """Group of operations that must execute atomically"""    
    def __init__(self, group_id: str = None):
        self.group_id = group_id or str(uuid.uuid4())
        self.operations: List[AtomicOperation] = []
        self.dependencies: Dict[str, Set[str]] = {}  # operation_id -> set of dependency operation_ids
        self.execution_order: List[str] = []
        self.lock = threading.RLock()
    
    def add_operation(self, operation: AtomicOperation, dependencies: Optional[List[str]] = None) -> None:
        """Add operation to group with optional dependencies"""        with self.lock:
            self.operations.append(operation)
            if dependencies:
                self.dependencies[operation.operation_id] = set(dependencies)
            else:
                self.dependencies[operation.operation_id] = set()
    
    def get_executable_operations(self) -> List[AtomicOperation]:
        """Get operations that can be executed (dependencies satisfied)"""        with self.lock:
            completed_ops = {op.operation_id for op in self.operations 
                           if op.state == OperationState.COMPLETED}
            
            executable = []
            for operation in self.operations:
                if (operation.is_executable() and 
                    self.dependencies[operation.operation_id].issubset(completed_ops)):
                    executable.append(operation)
            
            return executable
    
    def get_rollback_operations(self) -> List[AtomicOperation]:
        """Get operations that need to be rolled back (in reverse execution order)"""        with self.lock:
            rollbackable = [op for op in self.operations if op.is_rollbackable()]
            # Sort by completion time in reverse order
            rollbackable.sort(key=lambda x: x.completed_at or datetime.min, reverse=True)
            return rollbackable


class CompensationRegistry:
    """Registry for compensation actions for atomic operations"""    
    def __init__(self):
        self.compensations: Dict[str, List[Callable]] = {}
        self.lock = threading.RLock()
    
    def register_compensation(self, operation_id: str, compensation_func: Callable) -> None:
        """Register compensation function for operation"""        with self.lock:
            if operation_id not in self.compensations:
                self.compensations[operation_id] = []
            self.compensations[operation_id].append(compensation_func)
    
    async def execute_compensations(self, operation_id: str) -> None:
        """Execute all compensation functions for operation"""        with self.lock:
            compensations = self.compensations.get(operation_id, [])
        
        for compensation_func in reversed(compensations):  # Execute in reverse order
            try:
                if asyncio.iscoroutinefunction(compensation_func):
                    await compensation_func()
                else:
                    await asyncio.get_event_loop().run_in_executor(None, compensation_func)
                logger.debug("Compensation executed for operation %s", operation_id)
            except Exception as e:
                logger.error("Compensation failed for operation %s: %s", operation_id, str(e))


class AtomicityManager:
    """    Atomicity manager ensuring all-or-nothing semantics for transactions
    
    Features:
    - Atomic operation execution
    - Automatic rollback on failure
    - Dependency-aware execution ordering
    - Compensation pattern support
    - Performance monitoring
    - Concurrent operation support
    - Resource cleanup
    """    
    def __init__(self, max_concurrent_operations: int = 100):
        self.active_groups: Dict[str, AtomicOperationGroup] = {}
        self.compensation_registry = CompensationRegistry()
        self.max_concurrent = max_concurrent_operations
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_operations)
        self.semaphore = asyncio.Semaphore(max_concurrent_operations)
        self.lock = asyncio.Lock()
        self.performance_metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "rolled_back_operations": 0,
            "average_duration": 0.0,
        }
        
        logger.info("AtomicityManager initialized with max_concurrent=%d", max_concurrent_operations)
    
    async def create_operation_group(self, group_id: Optional[str] = None) -> str:
        """Create new atomic operation group"""        group = AtomicOperationGroup(group_id)
        
        async with self.lock:
            self.active_groups[group.group_id] = group
        
        logger.debug("Created operation group: %s", group.group_id)
        return group.group_id
    
    async def add_operation(
        self,
        group_id: str,
        execute_func: Callable,
        rollback_func: Optional[Callable] = None,
        validate_func: Optional[Callable] = None,
        operation_type: AtomicOperationType = AtomicOperationType.CUSTOM,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
        max_retries: int = 3
    ) -> str:
        """Add operation to atomic group"""        
        group = self.active_groups.get(group_id)
        if not group:
            raise ValueError(f"Operation group not found: {group_id}")
        
        operation = AtomicOperation(
            operation_type=operation_type,
            execute_func=execute_func,
            rollback_func=rollback_func,
            validate_func=validate_func,
            metadata=metadata or {},
            timeout=timeout,
            max_retries=max_retries
        )
        
        group.add_operation(operation, dependencies)
        
        logger.debug("Added operation %s to group %s", operation.operation_id, group_id)
        return operation.operation_id
    
    async def execute_atomic_group(self, group_id: str) -> bool:
        """Execute all operations in group atomically"""        
        group = self.active_groups.get(group_id)
        if not group:
            raise ValueError(f"Operation group not found: {group_id}")
        
        try:
            logger.info("Starting atomic execution of group %s (%d operations)", 
                       group_id, len(group.operations))
            
            # Execute operations in dependency order
            while True:
                executable_ops = group.get_executable_operations()
                
                if not executable_ops:
                    # Check if all operations are completed
                    remaining_ops = [op for op in group.operations 
                                   if op.state not in [OperationState.COMPLETED, OperationState.FAILED]]
                    
                    if not remaining_ops:
                        break  # All operations completed
                    else:
                        # Deadlock or circular dependency
                        logger.error("Deadlock detected in operation group %s", group_id)
                        await self._rollback_group(group)
                        return False
                
                # Execute operations concurrently where possible
                execution_tasks = []
                for operation in executable_ops:
                    task = asyncio.create_task(self._execute_operation(operation))
                    execution_tasks.append(task)
                
                results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                
                # Check results
                for i, result in enumerate(results):
                    operation = executable_ops[i]
                    
                    if isinstance(result, Exception):
                        logger.error("Operation %s failed: %s", operation.operation_id, str(result))
                        operation.state = OperationState.FAILED
                        operation.error = str(result)
                        await self._rollback_group(group)
                        return False
                    elif not result:
                        logger.error("Operation %s returned false", operation.operation_id)
                        operation.state = OperationState.FAILED
                        await self._rollback_group(group)
                        return False
            
            # All operations completed successfully
            logger.info("Atomic group %s executed successfully", group_id)
            await self._update_metrics(group, success=True)
            return True
            
        except Exception as e:
            logger.error("Atomic group execution failed: %s", str(e))
            await self._rollback_group(group)
            return False
        finally:
            # Cleanup group
            async with self.lock:
                self.active_groups.pop(group_id, None)
    
    async def _execute_operation(self, operation: AtomicOperation) -> bool:
        """Execute individual atomic operation"""        
        async with self.semaphore:  # Limit concurrent operations
            operation.state = OperationState.EXECUTING
            operation.executed_at = datetime.now(timezone.utc)
            
            try:
                # Validate operation if validator provided
                if operation.validate_func:
                    valid = await self._call_function(operation.validate_func, operation.timeout)
                    if not valid:
                        logger.warning("Operation validation failed: %s", operation.operation_id)
                        return False
                
                # Execute operation
                result = await self._call_function(operation.execute_func, operation.timeout)
                
                operation.result = result
                operation.state = OperationState.COMPLETED
                operation.completed_at = datetime.now(timezone.utc)
                
                logger.debug("Operation %s completed successfully (duration=%.3fs)", 
                           operation.operation_id, operation.duration or 0)
                
                return True
                
            except asyncio.TimeoutError:
                logger.error("Operation %s timed out", operation.operation_id)
                operation.state = OperationState.FAILED
                operation.error = "Operation timeout"
                return False
                
            except Exception as e:
                logger.error("Operation %s failed: %s", operation.operation_id, str(e))
                operation.state = OperationState.FAILED
                operation.error = str(e)
                
                # Retry if allowed
                operation.retry_count += 1
                if operation.retry_count <= operation.max_retries:
                    logger.info("Retrying operation %s (attempt %d/%d)", 
                               operation.operation_id, operation.retry_count, operation.max_retries)
                    operation.state = OperationState.PENDING
                    await asyncio.sleep(min(2 ** operation.retry_count, 10))  # Exponential backoff
                    return await self._execute_operation(operation)
                
                return False
    
    async def _rollback_group(self, group: AtomicOperationGroup) -> None:
        """Rollback all completed operations in group"""        
        logger.info("Rolling back operation group %s", group.group_id)
        
        rollback_operations = group.get_rollback_operations()
        
        for operation in rollback_operations:
            try:
                await self._rollback_operation(operation)
                operation.state = OperationState.ROLLED_BACK
                logger.debug("Operation %s rolled back successfully", operation.operation_id)
                
            except Exception as e:
                logger.error("Rollback failed for operation %s: %s", 
                           operation.operation_id, str(e))
        
        await self._update_metrics(group, success=False)
    
    async def _rollback_operation(self, operation: AtomicOperation) -> None:
        """Rollback individual operation"""        
        if operation.rollback_func:
            await self._call_function(operation.rollback_func, operation.timeout)
        
        # Execute compensations
        await self.compensation_registry.execute_compensations(operation.operation_id)
    
    async def _call_function(self, func: Callable, timeout: float) -> Any:
        """Call function with proper async/sync handling and timeout"""        
        try:
            if asyncio.iscoroutinefunction(func):
                return await asyncio.wait_for(func(), timeout=timeout)
            else:
                # Run in executor for CPU-bound operations
                return await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(self.executor, func),
                    timeout=timeout
                )
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Function call timed out after {timeout} seconds")
    
    async def _update_metrics(self, group: AtomicOperationGroup, success: bool) -> None:
        """Update performance metrics"""        
        total_ops = len(group.operations)
        self.performance_metrics["total_operations"] += total_ops
        
        if success:
            self.performance_metrics["successful_operations"] += total_ops
        else:
            failed_ops = sum(1 for op in group.operations if op.state == OperationState.FAILED)
            rolled_back_ops = sum(1 for op in group.operations if op.state == OperationState.ROLLED_BACK)
            
            self.performance_metrics["failed_operations"] += failed_ops
            self.performance_metrics["rolled_back_operations"] += rolled_back_ops
        
        # Update average duration
        completed_ops = [op for op in group.operations if op.duration is not None]
        if completed_ops:
            avg_duration = sum(op.duration for op in completed_ops) / len(completed_ops)
            
            total_measured = (self.performance_metrics["successful_operations"] + 
                            self.performance_metrics["rolled_back_operations"])
            
            if total_measured > 0:
                current_avg = self.performance_metrics["average_duration"]
                new_avg = ((current_avg * (total_measured - len(completed_ops)) + 
                          avg_duration * len(completed_ops)) / total_measured)
                self.performance_metrics["average_duration"] = new_avg
    
    def register_compensation(self, operation_id: str, compensation_func: Callable) -> None:
        """Register compensation function for operation"""        self.compensation_registry.register_compensation(operation_id, compensation_func)
    
    async def get_group_status(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get status of operation group"""        
        group = self.active_groups.get(group_id)
        if not group:
            return None
        
        operation_states = {}
        for state in OperationState:
            operation_states[state.value] = sum(1 for op in group.operations if op.state == state)
        
        return {
            "group_id": group_id,
            "total_operations": len(group.operations),
            "operation_states": operation_states,
            "has_dependencies": any(deps for deps in group.dependencies.values()),
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get atomicity manager performance metrics"""        return {
            **self.performance_metrics,
            "active_groups": len(self.active_groups),
            "max_concurrent": self.max_concurrent,
        }
    
    @asynccontextmanager
    async def atomic_context(self, group_id: Optional[str] = None):
        """Context manager for atomic operations"""        
        group_id = await self.create_operation_group(group_id)
        
        try:
            yield group_id
            
            # Execute all operations atomically
            success = await self.execute_atomic_group(group_id)
            if not success:
                raise RuntimeError("Atomic operation group execution failed")
                
        except Exception as e:
            # Cleanup on error
            async with self.lock:
                self.active_groups.pop(group_id, None)
            raise e
    
    async def shutdown(self) -> None:
        """Graceful shutdown of atomicity manager"""        logger.info("Shutting down AtomicityManager...")
        
        # Rollback all active groups
        active_groups = list(self.active_groups.values())
        for group in active_groups:
            await self._rollback_group(group)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("AtomicityManager shutdown complete")
