"""Transaction Coordinator - Main Transaction Orchestration Engine

Enterprise-grade transaction coordination system providing centralized transaction
management, state tracking, and resource coordination across multiple databases
and microservices.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.
"""import asyncio
import uuid
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class TransactionState(Enum):
    """Transaction state enumeration"""    INIT = "initialized"
    ACTIVE = "active"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TransactionPriority(Enum):
    """Transaction priority levels"""    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TransactionContext:
    """Transaction context containing all transaction metadata"""    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: TransactionState = TransactionState.INIT
    priority: TransactionPriority = TransactionPriority.NORMAL
    timeout: int = 30  # seconds
    max_retries: int = 3
    retry_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    participants: List[str] = field(default_factory=list)
    rollback_handlers: List[Callable] = field(default_factory=list)
    commit_handlers: List[Callable] = field(default_factory=list)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate transaction duration in seconds"""        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now(timezone.utc) - self.started_at).total_seconds()
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if transaction has expired"""        if self.started_at:
            elapsed = (datetime.now(timezone.utc) - self.started_at).total_seconds()
            return elapsed > self.timeout
        return False


class ResourceManager:
    """Resource manager for transaction coordination"""    
    def __init__(self):
        self.locks: Dict[str, threading.RLock] = {}
        self.resources: Dict[str, Any] = {}
        self.lock = threading.RLock()
    
    def acquire_resource(self, resource_id: str, timeout: float = 10.0) -> bool:
        """Acquire exclusive access to a resource"""        with self.lock:
            if resource_id not in self.locks:
                self.locks[resource_id] = threading.RLock()
        
        return self.locks[resource_id].acquire(timeout=timeout)
    
    def release_resource(self, resource_id: str) -> None:
        """Release resource lock"""        if resource_id in self.locks:
            self.locks[resource_id].release()
    
    def register_resource(self, resource_id: str, resource: Any) -> None:
        """Register a resource for management"""        with self.lock:
            self.resources[resource_id] = resource
    
    def get_resource(self, resource_id: str) -> Optional[Any]:
        """Get registered resource"""        return self.resources.get(resource_id)


class TransactionCoordinator:
    """    Main transaction coordinator providing enterprise-grade transaction orchestration
    
    Features:
    - Distributed transaction coordination
    - Two-phase commit protocol
    - Resource management and locking
    - Transaction state tracking
    - Timeout and retry handling
    - Performance monitoring
    - Rollback and recovery
    """    
    def __init__(self, max_concurrent_transactions: int = 1000):
        self.active_transactions: Dict[str, TransactionContext] = {}
        self.resource_manager = ResourceManager()
        self.max_concurrent = max_concurrent_transactions
        self.executor = ThreadPoolExecutor(max_workers=100)
        self.lock = asyncio.Lock()
        self.performance_metrics = {
            "total_transactions": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "average_duration": 0.0,
            "throughput": 0.0,
        }
        self._shutdown = False
        
        # Start background tasks
        asyncio.create_task(self._monitor_transactions())
        asyncio.create_task(self._cleanup_expired_transactions())
        
        logger.info("TransactionCoordinator initialized with max_concurrent=%d", max_concurrent_transactions)
    
    async def begin_transaction(
        self,
        priority: TransactionPriority = TransactionPriority.NORMAL,
        timeout: int = 30,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TransactionContext:
        """Begin a new transaction"""        
        async with self.lock:
            if len(self.active_transactions) >= self.max_concurrent:
                raise RuntimeError(f"Maximum concurrent transactions reached: {self.max_concurrent}")
            
            context = TransactionContext(
                priority=priority,
                timeout=timeout,
                metadata=metadata or {}
            )
            
            context.state = TransactionState.ACTIVE
            context.started_at = datetime.now(timezone.utc)
            
            self.active_transactions[context.transaction_id] = context
            
            logger.info("Transaction started: %s (priority=%s, timeout=%d)", 
                       context.transaction_id, priority.name, timeout)
            
            return context
    
    async def prepare_transaction(self, transaction_id: str) -> bool:
        """Prepare transaction for commit (Phase 1 of 2PC)"""        
        context = self.active_transactions.get(transaction_id)
        if not context:
            logger.error("Transaction not found: %s", transaction_id)
            return False
        
        if context.state != TransactionState.ACTIVE:
            logger.error("Transaction not in active state: %s (state=%s)", 
                        transaction_id, context.state.value)
            return False
        
        if context.is_expired:
            await self._abort_transaction(context, TransactionState.TIMEOUT)
            return False
        
        try:
            context.state = TransactionState.PREPARING
            
            # Prepare all participants
            prepare_tasks = []
            for participant in context.participants:
                task = asyncio.create_task(self._prepare_participant(participant, context))
                prepare_tasks.append(task)
            
            if prepare_tasks:
                results = await asyncio.gather(*prepare_tasks, return_exceptions=True)
                
                # Check if all participants prepared successfully
                for result in results:
                    if isinstance(result, Exception) or not result:
                        await self._abort_transaction(context, TransactionState.FAILED)
                        return False
            
            context.state = TransactionState.PREPARED
            logger.info("Transaction prepared: %s", transaction_id)
            return True
            
        except Exception as e:
            logger.error("Failed to prepare transaction %s: %s", transaction_id, str(e))
            await self._abort_transaction(context, TransactionState.FAILED)
            return False
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit transaction (Phase 2 of 2PC)"""        
        context = self.active_transactions.get(transaction_id)
        if not context:
            logger.error("Transaction not found: %s", transaction_id)
            return False
        
        if context.state != TransactionState.PREPARED:
            logger.error("Transaction not prepared: %s (state=%s)", 
                        transaction_id, context.state.value)
            return False
        
        try:
            context.state = TransactionState.COMMITTING
            
            # Execute commit handlers
            for handler in context.commit_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(context)
                    else:
                        await asyncio.get_event_loop().run_in_executor(
                            self.executor, handler, context
                        )
                except Exception as e:
                    logger.error("Commit handler failed for transaction %s: %s", 
                               transaction_id, str(e))
                    # Continue with other handlers
            
            # Commit all participants
            commit_tasks = []
            for participant in context.participants:
                task = asyncio.create_task(self._commit_participant(participant, context))
                commit_tasks.append(task)
            
            if commit_tasks:
                await asyncio.gather(*commit_tasks, return_exceptions=True)
            
            context.state = TransactionState.COMMITTED
            context.completed_at = datetime.now(timezone.utc)
            
            # Update performance metrics
            await self._update_metrics(context, success=True)
            
            # Release resources
            await self._release_transaction_resources(context)
            
            # Remove from active transactions
            async with self.lock:
                self.active_transactions.pop(transaction_id, None)
            
            logger.info("Transaction committed: %s (duration=%.3fs)", 
                       transaction_id, context.duration or 0)
            return True
            
        except Exception as e:
            logger.error("Failed to commit transaction %s: %s", transaction_id, str(e))
            await self._abort_transaction(context, TransactionState.FAILED)
            return False
    
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback transaction"""        
        context = self.active_transactions.get(transaction_id)
        if not context:
            logger.warning("Transaction not found for rollback: %s", transaction_id)
            return False
        
        return await self._abort_transaction(context, TransactionState.ABORTED)
    
    async def add_participant(self, transaction_id: str, participant_id: str) -> bool:
        """Add participant to transaction"""        
        context = self.active_transactions.get(transaction_id)
        if not context:
            return False
        
        if context.state not in [TransactionState.ACTIVE]:
            return False
        
        context.participants.append(participant_id)
        logger.debug("Added participant %s to transaction %s", participant_id, transaction_id)
        return True
    
    def add_rollback_handler(self, transaction_id: str, handler: Callable) -> bool:
        """Add rollback handler to transaction"""        
        context = self.active_transactions.get(transaction_id)
        if not context:
            return False
        
        context.rollback_handlers.append(handler)
        return True
    
    def add_commit_handler(self, transaction_id: str, handler: Callable) -> bool:
        """Add commit handler to transaction"""        
        context = self.active_transactions.get(transaction_id)
        if not context:
            return False
        
        context.commit_handlers.append(handler)
        return True
    
    @asynccontextmanager
    async def transaction(
        self,
        priority: TransactionPriority = TransactionPriority.NORMAL,
        timeout: int = 30,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Context manager for automatic transaction management"""        
        context = await self.begin_transaction(priority, timeout, metadata)
        
        try:
            yield context
            
            # Prepare and commit
            if await self.prepare_transaction(context.transaction_id):
                success = await self.commit_transaction(context.transaction_id)
                if not success:
                    raise RuntimeError("Failed to commit transaction")
            else:
                raise RuntimeError("Failed to prepare transaction")
                
        except Exception as e:
            await self.rollback_transaction(context.transaction_id)
            raise e
    
    async def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction status and metrics"""        
        context = self.active_transactions.get(transaction_id)
        if not context:
            return None
        
        return {
            "transaction_id": context.transaction_id,
            "state": context.state.value,
            "priority": context.priority.value,
            "duration": context.duration,
            "participants": len(context.participants),
            "retry_count": context.retry_count,
            "is_expired": context.is_expired,
            "metadata": context.metadata,
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get coordinator performance metrics"""        return {
            **self.performance_metrics,
            "active_transactions": len(self.active_transactions),
            "max_concurrent": self.max_concurrent,
        }
    
    async def _prepare_participant(self, participant_id: str, context: TransactionContext) -> bool:
        """Prepare individual participant"""        try:
            # In a real implementation, this would call the participant's prepare method
            # For now, simulate preparation
            await asyncio.sleep(0.001)  # Simulate network delay
            return True
        except Exception as e:
            logger.error("Failed to prepare participant %s: %s", participant_id, str(e))
            return False
    
    async def _commit_participant(self, participant_id: str, context: TransactionContext) -> bool:
        """Commit individual participant"""        try:
            # In a real implementation, this would call the participant's commit method
            await asyncio.sleep(0.001)  # Simulate network delay
            return True
        except Exception as e:
            logger.error("Failed to commit participant %s: %s", participant_id, str(e))
            return False
    
    async def _abort_transaction(self, context: TransactionContext, state: TransactionState) -> bool:
        """Abort transaction and execute rollback handlers"""        
        try:
            context.state = TransactionState.ABORTING
            
            # Execute rollback handlers
            for handler in context.rollback_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(context)
                    else:
                        await asyncio.get_event_loop().run_in_executor(
                            self.executor, handler, context
                        )
                except Exception as e:
                    logger.error("Rollback handler failed for transaction %s: %s", 
                               context.transaction_id, str(e))
            
            context.state = state
            context.completed_at = datetime.now(timezone.utc)
            
            # Update performance metrics
            await self._update_metrics(context, success=False)
            
            # Release resources
            await self._release_transaction_resources(context)
            
            # Remove from active transactions
            async with self.lock:
                self.active_transactions.pop(context.transaction_id, None)
            
            logger.info("Transaction aborted: %s (state=%s, duration=%.3fs)", 
                       context.transaction_id, state.value, context.duration or 0)
            return True
            
        except Exception as e:
            logger.error("Failed to abort transaction %s: %s", context.transaction_id, str(e))
            return False
    
    async def _release_transaction_resources(self, context: TransactionContext) -> None:
        """Release all resources held by transaction"""        for participant in context.participants:
            try:
                self.resource_manager.release_resource(participant)
            except Exception as e:
                logger.error("Failed to release resource %s: %s", participant, str(e))
    
    async def _update_metrics(self, context: TransactionContext, success: bool) -> None:
        """Update performance metrics"""        self.performance_metrics["total_transactions"] += 1
        
        if success:
            self.performance_metrics["successful_transactions"] += 1
        else:
            self.performance_metrics["failed_transactions"] += 1
        
        if context.duration:
            total_duration = (self.performance_metrics["average_duration"] * 
                            (self.performance_metrics["total_transactions"] - 1) + 
                            context.duration)
            self.performance_metrics["average_duration"] = (
                total_duration / self.performance_metrics["total_transactions"]
            )
    
    async def _monitor_transactions(self) -> None:
        """Background task to monitor transaction health"""        while not self._shutdown:
            try:
                # Calculate throughput
                start_time = time.time()
                start_count = self.performance_metrics["total_transactions"]
                
                await asyncio.sleep(60)  # Monitor every minute
                
                end_time = time.time()
                end_count = self.performance_metrics["total_transactions"]
                
                duration = end_time - start_time
                transactions = end_count - start_count
                
                self.performance_metrics["throughput"] = transactions / duration if duration > 0 else 0
                
                logger.debug("Transaction throughput: %.2f TPS", self.performance_metrics["throughput"])
                
            except Exception as e:
                logger.error("Error in transaction monitoring: %s", str(e))
                await asyncio.sleep(5)
    
    async def _cleanup_expired_transactions(self) -> None:
        """Background task to cleanup expired transactions"""        while not self._shutdown:
            try:
                expired_transactions = []
                
                async with self.lock:
                    for transaction_id, context in self.active_transactions.items():
                        if context.is_expired:
                            expired_transactions.append(context)
                
                for context in expired_transactions:
                    logger.warning("Transaction expired: %s", context.transaction_id)
                    await self._abort_transaction(context, TransactionState.TIMEOUT)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error("Error in expired transaction cleanup: %s", str(e))
                await asyncio.sleep(5)
    
    async def shutdown(self) -> None:
        """Graceful shutdown of coordinator"""        logger.info("Shutting down TransactionCoordinator...")
        self._shutdown = True
        
        # Abort all active transactions
        active_transactions = list(self.active_transactions.values())
        for context in active_transactions:
            await self._abort_transaction(context, TransactionState.ABORTED)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("TransactionCoordinator shutdown complete")
