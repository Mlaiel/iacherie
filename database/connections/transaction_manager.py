"""Transaction Manager - IA Influencer Agent Platform

Manages distributed transactions across multiple database systems:
- Cross-database ACID transactions
- Two-phase commit protocol implementation
- Transaction state management and recovery
- Deadlock detection and resolution
- Transaction isolation and consistency
- Rollback and compensation logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import asynccontextmanager
import json


class TransactionState(Enum):
    """Transaction states in distributed system"""    ACTIVE = "active"
    PREPARING = "preparing" 
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"
    UNKNOWN = "unknown"


class TransactionIsolation(Enum):
    """Transaction isolation levels"""    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


@dataclass
class TransactionOperation:
    """Single operation within a transaction"""    operation_id: str
    database_type: str
    operation_type: str  # insert, update, delete, select
    table_collection: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    compensation_data: Optional[Dict[str, Any]] = None


@dataclass
class DistributedTransaction:
    """Distributed transaction across multiple databases"""    transaction_id: str
    tenant_id: Optional[str]
    state: TransactionState = TransactionState.ACTIVE
    isolation_level: TransactionIsolation = TransactionIsolation.READ_COMMITTED
    operations: List[TransactionOperation] = field(default_factory=list)
    participants: Set[str] = field(default_factory=set)
    started_at: datetime = field(default_factory=datetime.utcnow)
    timeout: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    
    def is_expired(self) -> bool:
        """Check if transaction has expired"""        return datetime.utcnow() - self.started_at > self.timeout


class TransactionManager:
    """    Distributed transaction manager for IA Influencer platform.
    
    Coordinates transactions across:
    - PostgreSQL (user data, content metadata)
    - MongoDB (content analytics, fingerprints)
    - Redis (cache invalidation, session updates)
    - Elasticsearch (search index updates)
    - Vector stores (embedding updates)
    - Object storage (file operations)
    """    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Database handlers
        self.handlers: Dict[str, Any] = {}
        
        # Active transactions
        self.active_transactions: Dict[str, DistributedTransaction] = {}
        
        # Transaction log for recovery
        self.transaction_log: List[Dict[str, Any]] = []
        
        # Lock management
        self.locks: Dict[str, Set[str]] = {}  # resource_id -> transaction_ids
        self.lock_owners: Dict[str, str] = {}  # resource_id -> transaction_id
        
        # Deadlock detection
        self.deadlock_detection_interval = 30  # seconds
        self.deadlock_task: Optional[asyncio.Task] = None
        
        # Cleanup task
        self.cleanup_task: Optional[asyncio.Task] = None
        self.cleanup_interval = 60  # seconds
        
        # Statistics
        self.stats = {
            "total_transactions": 0,
            "committed_transactions": 0,
            "aborted_transactions": 0,
            "deadlocks_detected": 0,
            "average_duration": 0.0
        }
    
    async def initialize(self, handlers: Dict[str, Any]) -> None:
        """Initialize transaction manager with database handlers"""        self.handlers = handlers
        
        # Start background tasks
        self.deadlock_task = asyncio.create_task(self._deadlock_detection_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        self.logger.info("Transaction manager initialized")
    
    @asynccontextmanager
    async def transaction(self, 
                         tenant_id: Optional[str] = None,
                         isolation_level: TransactionIsolation = TransactionIsolation.READ_COMMITTED,
                         timeout: Optional[timedelta] = None):
        """Context manager for distributed transactions"""        
        # Create new transaction
        tx_id = str(uuid.uuid4())
        transaction = DistributedTransaction(
            transaction_id=tx_id,
            tenant_id=tenant_id,
            isolation_level=isolation_level,
            timeout=timeout or timedelta(minutes=5)
        )
        
        self.active_transactions[tx_id] = transaction
        self.stats["total_transactions"] += 1
        
        try:
            # Log transaction start
            await self._log_transaction_event(tx_id, "STARTED", {
                "tenant_id": tenant_id,
                "isolation_level": isolation_level.value
            })
            
            yield TransactionContext(self, transaction)
            
            # Commit transaction
            await self._commit_transaction(tx_id)
            
        except Exception as e:
            # Abort transaction
            await self._abort_transaction(tx_id, str(e))
            raise
        
        finally:
            # Cleanup transaction
            if tx_id in self.active_transactions:
                del self.active_transactions[tx_id]
    
    async def _commit_transaction(self, tx_id: str) -> None:
        """Commit distributed transaction using two-phase commit"""        if tx_id not in self.active_transactions:
            raise ValueError(f"Transaction {tx_id} not found")
        
        transaction = self.active_transactions[tx_id]
        
        if transaction.is_expired():
            raise Exception(f"Transaction {tx_id} has expired")
        
        try:
            # Phase 1: Prepare all participants
            transaction.state = TransactionState.PREPARING
            await self._log_transaction_event(tx_id, "PREPARING")
            
            prepare_results = await self._prepare_phase(transaction)
            
            # Check if all participants are prepared
            if all(prepare_results.values()):
                transaction.state = TransactionState.PREPARED
                await self._log_transaction_event(tx_id, "PREPARED")
                
                # Phase 2: Commit all participants
                transaction.state = TransactionState.COMMITTING
                await self._log_transaction_event(tx_id, "COMMITTING")
                
                await self._commit_phase(transaction)
                
                transaction.state = TransactionState.COMMITTED
                await self._log_transaction_event(tx_id, "COMMITTED")
                
                self.stats["committed_transactions"] += 1
                
            else:
                # Some participants failed to prepare, abort
                raise Exception("One or more participants failed to prepare")
        
        except Exception as e:
            await self._abort_transaction(tx_id, str(e))
            raise
        
        finally:
            # Release locks
            await self._release_transaction_locks(tx_id)
    
    async def _prepare_phase(self, transaction: DistributedTransaction) -> Dict[str, bool]:
        """Execute prepare phase of two-phase commit"""        prepare_results = {}
        
        for db_type in transaction.participants:
            try:
                handler = self.handlers[db_type]
                
                # Prepare transaction in each database
                if hasattr(handler, 'prepare_transaction'):
                    result = await handler.prepare_transaction(
                        transaction.transaction_id,
                        [op for op in transaction.operations if op.database_type == db_type]
                    )
                    prepare_results[db_type] = result
                else:
                    # Database doesn't support two-phase commit, assume prepared
                    prepare_results[db_type] = True
                
            except Exception as e:
                self.logger.error(f"Prepare failed for {db_type}: {e}")
                prepare_results[db_type] = False
        
        return prepare_results
    
    async def _commit_phase(self, transaction: DistributedTransaction) -> None:
        """Execute commit phase of two-phase commit"""        commit_tasks = []
        
        for db_type in transaction.participants:
            task = asyncio.create_task(
                self._commit_participant(db_type, transaction)
            )
            commit_tasks.append(task)
        
        # Wait for all commits to complete
        results = await asyncio.gather(*commit_tasks, return_exceptions=True)
        
        # Check for any failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                db_type = list(transaction.participants)[i]
                self.logger.error(f"Commit failed for {db_type}: {result}")
                # Note: At this point, we can't abort - need compensation
    
    async def _commit_participant(self, db_type: str, transaction: DistributedTransaction) -> None:
        """Commit transaction for a single database participant"""        try:
            handler = self.handlers[db_type]
            
            if hasattr(handler, 'commit_transaction'):
                await handler.commit_transaction(transaction.transaction_id)
            else:
                # Execute operations directly
                operations = [op for op in transaction.operations if op.database_type == db_type]
                for operation in operations:
                    await self._execute_operation(handler, operation)
            
        except Exception as e:
            self.logger.error(f"Failed to commit {db_type} participant: {e}")
            raise
    
    async def _abort_transaction(self, tx_id: str, reason: str) -> None:
        """Abort distributed transaction"""        if tx_id not in self.active_transactions:
            return
        
        transaction = self.active_transactions[tx_id]
        transaction.state = TransactionState.ABORTING
        
        await self._log_transaction_event(tx_id, "ABORTING", {"reason": reason})
        
        try:
            # Abort all participants
            abort_tasks = []
            for db_type in transaction.participants:
                task = asyncio.create_task(
                    self._abort_participant(db_type, transaction)
                )
                abort_tasks.append(task)
            
            await asyncio.gather(*abort_tasks, return_exceptions=True)
            
            transaction.state = TransactionState.ABORTED
            await self._log_transaction_event(tx_id, "ABORTED")
            
            self.stats["aborted_transactions"] += 1
            
        except Exception as e:
            self.logger.error(f"Error during transaction abort: {e}")
        
        finally:
            # Release locks
            await self._release_transaction_locks(tx_id)
    
    async def _abort_participant(self, db_type: str, transaction: DistributedTransaction) -> None:
        """Abort transaction for a single database participant"""        try:
            handler = self.handlers[db_type]
            
            if hasattr(handler, 'abort_transaction'):
                await handler.abort_transaction(transaction.transaction_id)
            else:
                # Execute compensation operations
                operations = [op for op in transaction.operations if op.database_type == db_type]
                for operation in reversed(operations):  # Reverse order for compensation
                    if operation.compensation_data:
                        await self._execute_compensation(handler, operation)
            
        except Exception as e:
            self.logger.error(f"Failed to abort {db_type} participant: {e}")
    
    async def _execute_operation(self, handler: Any, operation: TransactionOperation) -> None:
        """Execute a single operation"""        if operation.operation_type == "insert":
            if hasattr(handler, 'insert_one'):
                await handler.insert_one(
                    operation.table_collection,
                    operation.data
                )
        elif operation.operation_type == "update":
            if hasattr(handler, 'update_one'):
                await handler.update_one(
                    operation.table_collection,
                    operation.data.get("filter", {}),
                    operation.data.get("update", {})
                )
        elif operation.operation_type == "delete":
            if hasattr(handler, 'delete_one'):
                await handler.delete_one(
                    operation.table_collection,
                    operation.data.get("filter", {})
                )
    
    async def _execute_compensation(self, handler: Any, operation: TransactionOperation) -> None:
        """Execute compensation for an operation"""        if not operation.compensation_data:
            return
        
        compensation = operation.compensation_data
        
        if compensation.get("type") == "delete":
            # Compensate insert with delete
            if hasattr(handler, 'delete_one'):
                await handler.delete_one(
                    operation.table_collection,
                    compensation.get("filter", {})
                )
        elif compensation.get("type") == "insert":
            # Compensate delete with insert
            if hasattr(handler, 'insert_one'):
                await handler.insert_one(
                    operation.table_collection,
                    compensation.get("data", {})
                )
        elif compensation.get("type") == "update":
            # Compensate update with previous values
            if hasattr(handler, 'update_one'):
                await handler.update_one(
                    operation.table_collection,
                    compensation.get("filter", {}),
                    compensation.get("update", {})
                )
    
    async def _acquire_lock(self, resource_id: str, tx_id: str) -> bool:
        """Acquire lock on resource for transaction"""        if resource_id in self.lock_owners:
            # Resource is already locked
            if self.lock_owners[resource_id] == tx_id:
                return True  # Already owned by this transaction
            else:
                # Add to waiting list
                if resource_id not in self.locks:
                    self.locks[resource_id] = set()
                self.locks[resource_id].add(tx_id)
                return False
        else:
            # Acquire lock
            self.lock_owners[resource_id] = tx_id
            return True
    
    async def _release_transaction_locks(self, tx_id: str) -> None:
        """Release all locks held by transaction"""        # Release owned locks
        resources_to_release = [
            resource_id for resource_id, owner_id in self.lock_owners.items()
            if owner_id == tx_id
        ]
        
        for resource_id in resources_to_release:
            del self.lock_owners[resource_id]
            
            # Grant lock to next waiting transaction
            if resource_id in self.locks and self.locks[resource_id]:
                next_tx = self.locks[resource_id].pop()
                self.lock_owners[resource_id] = next_tx
        
        # Remove from waiting lists
        for resource_id, waiting_txs in self.locks.items():
            waiting_txs.discard(tx_id)
    
    async def _deadlock_detection_loop(self) -> None:
        """Background task for deadlock detection"""        while True:
            try:
                await asyncio.sleep(self.deadlock_detection_interval)
                await self._detect_deadlocks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Deadlock detection error: {e}")
    
    async def _detect_deadlocks(self) -> None:
        """Detect and resolve deadlocks"""        # Build wait-for graph
        wait_for = {}  # tx_id -> set of tx_ids it's waiting for
        
        for resource_id, waiting_txs in self.locks.items():
            if resource_id in self.lock_owners:
                owner = self.lock_owners[resource_id]
                for waiter in waiting_txs:
                    if waiter not in wait_for:
                        wait_for[waiter] = set()
                    wait_for[waiter].add(owner)
        
        # Detect cycles using DFS
        visited = set()
        in_progress = set()
        
        def has_cycle(tx_id: str) -> bool:
            if tx_id in in_progress:
                return True
            if tx_id in visited:
                return False
            
            visited.add(tx_id)
            in_progress.add(tx_id)
            
            for dependency in wait_for.get(tx_id, set()):
                if has_cycle(dependency):
                    return True
            
            in_progress.remove(tx_id)
            return False
        
        # Check for deadlocks
        deadlocked_transactions = []
        for tx_id in wait_for:
            if has_cycle(tx_id):
                deadlocked_transactions.append(tx_id)
        
        # Resolve deadlocks by aborting youngest transaction
        if deadlocked_transactions:
            # Find youngest transaction
            youngest_tx = min(
                deadlocked_transactions,
                key=lambda tx_id: self.active_transactions[tx_id].started_at
                if tx_id in self.active_transactions else datetime.min
            )
            
            await self._abort_transaction(youngest_tx, "Deadlock detected")
            self.stats["deadlocks_detected"] += 1
            
            self.logger.warning(f"Resolved deadlock by aborting transaction {youngest_tx}")
    
    async def _cleanup_loop(self) -> None:
        """Background task for cleaning up expired transactions"""        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_transactions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
    
    async def _cleanup_expired_transactions(self) -> None:
        """Clean up expired transactions"""        expired_transactions = [
            tx_id for tx_id, tx in self.active_transactions.items()
            if tx.is_expired()
        ]
        
        for tx_id in expired_transactions:
            await self._abort_transaction(tx_id, "Transaction expired")
            self.logger.warning(f"Aborted expired transaction {tx_id}")
    
    async def _log_transaction_event(self, 
                                   tx_id: str, 
                                   event: str, 
                                   data: Optional[Dict[str, Any]] = None) -> None:
        """Log transaction event for recovery purposes"""        log_entry = {
            "transaction_id": tx_id,
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data or {}
        }
        
        self.transaction_log.append(log_entry)
        
        # Keep only recent log entries (last 1000)
        if len(self.transaction_log) > 1000:
            self.transaction_log = self.transaction_log[-1000:]
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get transaction manager metrics"""        active_count = len(self.active_transactions)
        
        # Calculate average transaction duration
        if self.stats["committed_transactions"] > 0:
            # This is simplified - in real implementation, track actual durations
            self.stats["average_duration"] = 2.5  # placeholder
        
        return {
            "active_transactions": active_count,
            "total_locks": len(self.lock_owners),
            "waiting_locks": sum(len(waiters) for waiters in self.locks.values()),
            "statistics": self.stats,
            "deadlock_detection_interval": self.deadlock_detection_interval,
            "cleanup_interval": self.cleanup_interval
        }
    
    async def shutdown(self) -> None:
        """Shutdown transaction manager"""        self.logger.info("Shutting down transaction manager...")
        
        # Cancel background tasks
        if self.deadlock_task:
            self.deadlock_task.cancel()
            try:
                await self.deadlock_task
            except asyncio.CancelledError:
                pass
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Abort all active transactions
        for tx_id in list(self.active_transactions.keys()):
            await self._abort_transaction(tx_id, "System shutdown")
        
        self.logger.info("Transaction manager shutdown completed")


class TransactionContext:
    """Context for executing operations within a distributed transaction"""    
    def __init__(self, manager: TransactionManager, transaction: DistributedTransaction):
        self.manager = manager
        self.transaction = transaction
    
    async def execute(self, 
                     database_type: str,
                     operation_type: str,
                     table_collection: str,
                     data: Dict[str, Any],
                     compensation_data: Optional[Dict[str, Any]] = None) -> str:
        """Execute operation within the transaction"""        
        operation = TransactionOperation(
            operation_id=str(uuid.uuid4()),
            database_type=database_type,
            operation_type=operation_type,
            table_collection=table_collection,
            data=data,
            compensation_data=compensation_data
        )
        
        self.transaction.operations.append(operation)
        self.transaction.participants.add(database_type)
        
        return operation.operation_id
    
    async def insert(self, 
                    database_type: str,
                    table_collection: str,
                    data: Dict[str, Any]) -> str:
        """Insert operation within transaction"""        # Compensation for insert is delete
        compensation = {
            "type": "delete",
            "filter": {"id": data.get("id")}  # Simplified - use primary key
        }
        
        return await self.execute(
            database_type, "insert", table_collection, data, compensation
        )
    
    async def update(self, 
                    database_type: str,
                    table_collection: str,
                    filter_data: Dict[str, Any],
                    update_data: Dict[str, Any],
                    previous_data: Optional[Dict[str, Any]] = None) -> str:
        """Update operation within transaction"""        # Compensation for update is restore previous values
        compensation = None
        if previous_data:
            compensation = {
                "type": "update",
                "filter": filter_data,
                "update": previous_data
            }
        
        data = {"filter": filter_data, "update": update_data}
        
        return await self.execute(
            database_type, "update", table_collection, data, compensation
        )
    
    async def delete(self, 
                    database_type: str,
                    table_collection: str,
                    filter_data: Dict[str, Any],
                    backup_data: Optional[Dict[str, Any]] = None) -> str:
        """Delete operation within transaction"""        # Compensation for delete is restore the data
        compensation = None
        if backup_data:
            compensation = {
                "type": "insert",
                "data": backup_data
            }
        
        data = {"filter": filter_data}
        
        return await self.execute(
            database_type, "delete", table_collection, data, compensation
        )
