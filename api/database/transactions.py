"""
Database Transactions Management - IA Influencer Agent Platform
Enterprise-grade transaction handling with ACID compliance and advanced patterns

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

import asyncio
import uuid
from typing import Optional, Dict, Any, List, Callable, TypeVar, Generic, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import logging
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import text, event
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
import redis

from ..core.config import get_settings
from ..core.logging import get_logger
from .connection import DatabaseConnection, SessionManager

logger = get_logger(__name__)
settings = get_settings()

T = TypeVar('T')


class TransactionState(Enum):
    """Transaction state enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    TIMEOUT = "timeout"


class IsolationLevel(Enum):
    """Transaction isolation levels"""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


class TransactionType(Enum):
    """Transaction types for different patterns"""
    SIMPLE = "simple"                    # Basic single-database transaction
    DISTRIBUTED = "distributed"         # Multi-database transaction
    SAGA = "saga"                       # Saga pattern for microservices
    COMPENSATING = "compensating"       # Compensating transaction
    NESTED = "nested"                   # Nested transaction


@dataclass
class TransactionConfig:
    """Transaction configuration"""
    timeout_seconds: int = 30
    isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    read_only: bool = False
    retry_count: int = 3
    retry_delay_seconds: float = 1.0
    enable_savepoints: bool = True
    auto_commit: bool = True
    track_changes: bool = True


@dataclass
class TransactionContext:
    """Transaction execution context"""
    transaction_id: str
    transaction_type: TransactionType
    state: TransactionState
    config: TransactionConfig
    started_at: datetime
    completed_at: Optional[datetime] = None
    session_ids: List[str] = field(default_factory=list)
    savepoints: List[str] = field(default_factory=list)
    executed_operations: List[Dict[str, Any]] = field(default_factory=list)
    compensation_operations: List[Dict[str, Any]] = field(default_factory=list)
    error_details: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Get transaction duration in milliseconds"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return None


class TransactionOperation(ABC):
    """Abstract transaction operation"""
    
    def __init__(self, operation_id: str, operation_type: str):
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.executed = False
        self.compensated = False
    
    @abstractmethod
    async def execute(self, session: AsyncSession, context: TransactionContext) -> Any:
        """Execute the operation"""
        pass
    
    @abstractmethod
    async def compensate(self, session: AsyncSession, context: TransactionContext) -> Any:
        """Compensate (undo) the operation"""
        pass


class DatabaseOperation(TransactionOperation):
    """Database operation with SQL execution"""
    
    def __init__(self, operation_id: str, sql: str, params: Dict[str, Any] = None):
        super().__init__(operation_id, "database")
        self.sql = sql
        self.params = params or {}
        self.result = None
        self.compensation_sql: Optional[str] = None
        self.compensation_params: Dict[str, Any] = {}
    
    async def execute(self, session: AsyncSession, context: TransactionContext) -> Any:
        """Execute database operation"""



        try:
            result = await session.execute(text(self.sql), self.params)
            self.result = result
            self.executed = True
            
            # Track operation in context
            context.executed_operations.append({
                'operation_id': self.operation_id,
                'type': self.operation_type,
                'sql': self.sql,
                'params': self.params,
                'executed_at': datetime.utcnow()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Database operation {self.operation_id} failed: {e}")
            raise
    
    async def compensate(self, session: AsyncSession, context: TransactionContext) -> Any:
        """Compensate database operation"""
        if not self.compensation_sql:
            logger.warning(f"No compensation SQL for operation {self.operation_id}")
            return None
        
        try:
            result = await session.execute(text(self.compensation_sql), self.compensation_params)
            self.compensated = True
            
            # Track compensation in context
            context.compensation_operations.append({
                'operation_id': self.operation_id,
                'type': 'compensation',
                'sql': self.compensation_sql,
                'params': self.compensation_params,
                'compensated_at': datetime.utcnow()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Compensation for operation {self.operation_id} failed: {e}")
            raise
    
    def set_compensation(self, sql: str, params: Dict[str, Any] = None):
        """Set compensation SQL for this operation"""
        self.compensation_sql = sql
        self.compensation_params = params or {}


class TransactionManager:
    """
    Advanced transaction manager supporting multiple transaction patterns:
    - Simple transactions
    - Distributed transactions
    - Saga pattern
    - Compensating transactions
    - Nested transactions
    """
    
    def __init__(self):
        self.active_transactions: Dict[str, TransactionContext] = {}
        self.transaction_history: List[TransactionContext] = []
        self.session_manager = SessionManager()
        self.db_connection: Optional[DatabaseConnection] = None
        self.redis_client: Optional[redis.Redis] = None
        self.thread_executor = ThreadPoolExecutor(max_workers=10)
        self._locks: Dict[str, asyncio.Lock] = {}
    
    async def initialize(self):
        """Initialize transaction manager"""



        try:
            self.db_connection = await DatabaseConnection.get_instance()
            self.redis_client = self.db_connection.connections.get('redis_primary')
            
            # Setup transaction event handlers
            self._setup_event_handlers()
            
            logger.info("Transaction manager initialized")
            
        except Exception as e:
            logger.error(f"Transaction manager initialization failed: {e}")
            raise
    
    def _setup_event_handlers(self):
        """Setup SQLAlchemy event handlers for transaction monitoring"""
        if not self.db_connection:
            return
        
        # Transaction begin event
        @event.listens_for(self.db_connection.connections.get('postgresql_sync'), 'begin')
        def on_begin(conn):
            logger.debug("Transaction began")
        
        # Transaction commit event
        @event.listens_for(self.db_connection.connections.get('postgresql_sync'), 'commit')
        def on_commit(conn):
            logger.debug("Transaction committed")
        
        # Transaction rollback event
        @event.listens_for(self.db_connection.connections.get('postgresql_sync'), 'rollback')
        def on_rollback(conn):
            logger.debug("Transaction rolled back")
    
    @asynccontextmanager
    async def transaction(self, 
                         transaction_type: TransactionType = TransactionType.SIMPLE,
                         config: Optional[TransactionConfig] = None):
        """
        Context manager for transaction handling
        
        Usage:
            async with transaction_manager.transaction() as tx:
                await tx.execute_operation(operation)
        """
        config = config or TransactionConfig()
        context = await self.begin_transaction(transaction_type, config)
        
        try:
            yield TransactionExecutor(self, context)
            await self.commit_transaction(context.transaction_id)
            
        except Exception as e:
            await self.rollback_transaction(context.transaction_id, str(e))
            raise
    
    async def begin_transaction(self, 
                              transaction_type: TransactionType,
                              config: TransactionConfig) -> TransactionContext:
        """Begin a new transaction"""
        transaction_id = str(uuid.uuid4())
        
        context = TransactionContext(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            state=TransactionState.PENDING,
            config=config,
            started_at=datetime.utcnow()
        )
        
        # Store context
        self.active_transactions[transaction_id] = context
        
        # Create lock for this transaction
        self._locks[transaction_id] = asyncio.Lock()
        
        try:
            if transaction_type == TransactionType.SIMPLE:
                await self._begin_simple_transaction(context)
            elif transaction_type == TransactionType.DISTRIBUTED:
                await self._begin_distributed_transaction(context)
            elif transaction_type == TransactionType.SAGA:
                await self._begin_saga_transaction(context)
            elif transaction_type == TransactionType.COMPENSATING:
                await self._begin_compensating_transaction(context)
            elif transaction_type == TransactionType.NESTED:
                await self._begin_nested_transaction(context)
            
            context.state = TransactionState.ACTIVE
            logger.info(f"Transaction {transaction_id} started ({transaction_type.value})")
            
        except Exception as e:
            context.state = TransactionState.FAILED
            context.error_details = {'error': str(e), 'phase': 'begin'}
            logger.error(f"Failed to begin transaction {transaction_id}: {e}")
            raise
        
        return context
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit a transaction"""
        if transaction_id not in self.active_transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        context = self.active_transactions[transaction_id]
        
        if context.state != TransactionState.ACTIVE:
            raise ValueError(f"Transaction {transaction_id} is not active (state: {context.state.value})")
        
        async with self._locks[transaction_id]:
            try:
                if context.transaction_type == TransactionType.SIMPLE:
                    await self._commit_simple_transaction(context)
                elif context.transaction_type == TransactionType.DISTRIBUTED:
                    await self._commit_distributed_transaction(context)
                elif context.transaction_type == TransactionType.SAGA:
                    await self._commit_saga_transaction(context)
                elif context.transaction_type == TransactionType.COMPENSATING:
                    await self._commit_compensating_transaction(context)
                elif context.transaction_type == TransactionType.NESTED:
                    await self._commit_nested_transaction(context)
                
                context.state = TransactionState.COMMITTED
                context.completed_at = datetime.utcnow()
                
                logger.info(f"Transaction {transaction_id} committed successfully")
                
            except Exception as e:
                context.state = TransactionState.FAILED
                context.error_details = {'error': str(e), 'phase': 'commit'}
                context.completed_at = datetime.utcnow()
                
                logger.error(f"Failed to commit transaction {transaction_id}: {e}")
                
                # Attempt rollback
                await self.rollback_transaction(transaction_id, str(e))
                raise
            
            finally:
                # Move to history and cleanup
                self.transaction_history.append(context)
                del self.active_transactions[transaction_id]
                del self._locks[transaction_id]
                
                # Keep history manageable
                if len(self.transaction_history) > 1000:
                    self.transaction_history.pop(0)
        
        return context.state == TransactionState.COMMITTED
    
    async def rollback_transaction(self, transaction_id: str, reason: str = None) -> bool:
        """Rollback a transaction"""
        if transaction_id not in self.active_transactions:
            logger.warning(f"Transaction {transaction_id} not found for rollback")
            return False
        
        context = self.active_transactions[transaction_id]
        
        async with self._locks.get(transaction_id, asyncio.Lock()):
            try:
                if context.transaction_type == TransactionType.SIMPLE:
                    await self._rollback_simple_transaction(context)
                elif context.transaction_type == TransactionType.DISTRIBUTED:
                    await self._rollback_distributed_transaction(context)
                elif context.transaction_type == TransactionType.SAGA:
                    await self._rollback_saga_transaction(context)
                elif context.transaction_type == TransactionType.COMPENSATING:
                    await self._rollback_compensating_transaction(context)
                elif context.transaction_type == TransactionType.NESTED:
                    await self._rollback_nested_transaction(context)
                
                context.state = TransactionState.ROLLED_BACK
                context.completed_at = datetime.utcnow()
                
                if reason:
                    context.error_details = context.error_details or {}
                    context.error_details['rollback_reason'] = reason
                
                logger.info(f"Transaction {transaction_id} rolled back: {reason}")
                
            except Exception as e:
                context.state = TransactionState.FAILED
                context.error_details = {'error': str(e), 'phase': 'rollback'}
                context.completed_at = datetime.utcnow()
                
                logger.error(f"Failed to rollback transaction {transaction_id}: {e}")
            
            finally:
                # Move to history and cleanup
                self.transaction_history.append(context)
                if transaction_id in self.active_transactions:
                    del self.active_transactions[transaction_id]
                if transaction_id in self._locks:
                    del self._locks[transaction_id]
        
        return context.state == TransactionState.ROLLED_BACK
    
    # === Simple Transaction Implementation ===
    
    async def _begin_simple_transaction(self, context: TransactionContext):
        """Begin simple transaction"""
        session = await self.session_manager.get_async_session()
        context.session_ids.append(id(session))
        context.metadata['session'] = session
    
    async def _commit_simple_transaction(self, context: TransactionContext):
        """Commit simple transaction"""
        session = context.metadata.get('session')
        if session:
            await session.commit()
    
    async def _rollback_simple_transaction(self, context: TransactionContext):
        """Rollback simple transaction"""
        session = context.metadata.get('session')
        if session:
            await session.rollback()
    
    # === Distributed Transaction Implementation ===
    
    async def _begin_distributed_transaction(self, context: TransactionContext):
        """Begin distributed transaction using 2PC pattern"""
        # For now, use simple approach - in production, implement proper 2PC
        await self._begin_simple_transaction(context)
        
        # Store transaction state in Redis for coordination
        if self.redis_client:
            tx_data = {
                'transaction_id': context.transaction_id,
                'state': context.state.value,
                'started_at': context.started_at.isoformat(),
                'participants': []  # Would list all participating databases
            }
            
            await self.redis_client.setex(
                f"tx:{context.transaction_id}", 
                context.config.timeout_seconds, 
                str(tx_data)
            )
    
    async def _commit_distributed_transaction(self, context: TransactionContext):
        """Commit distributed transaction"""
        # Phase 1: Prepare all participants
        # Phase 2: Commit all participants
        await self._commit_simple_transaction(context)
        
        # Update Redis state
        if self.redis_client:
            await self.redis_client.delete(f"tx:{context.transaction_id}")
    
    async def _rollback_distributed_transaction(self, context: TransactionContext):
        """Rollback distributed transaction"""
        await self._rollback_simple_transaction(context)
        
        # Update Redis state
        if self.redis_client:
            await self.redis_client.delete(f"tx:{context.transaction_id}")
    
    # === Saga Transaction Implementation ===
    
    async def _begin_saga_transaction(self, context: TransactionContext):
        """Begin saga transaction"""
        # Saga transactions are managed through operation execution
        context.metadata['operations'] = []
        context.metadata['compensations'] = []
    
    async def _commit_saga_transaction(self, context: TransactionContext):
        """Commit saga transaction - all operations already executed"""
        # In saga pattern, operations are executed immediately
        # Commit just marks the saga as successful
        pass
    
    async def _rollback_saga_transaction(self, context: TransactionContext):
        """Rollback saga transaction by executing compensations"""
        operations = context.metadata.get('operations', [])
        
        # Execute compensations in reverse order
        for operation in reversed(operations):
            if hasattr(operation, 'compensate'):
                try:
                    session = context.metadata.get('session')
                    if session:
                        await operation.compensate(session, context)
                except Exception as e:
                    logger.error(f"Saga compensation failed for operation {operation.operation_id}: {e}")
    
    # === Compensating Transaction Implementation ===
    
    async def _begin_compensating_transaction(self, context: TransactionContext):
        """Begin compensating transaction"""
        await self._begin_simple_transaction(context)
        context.metadata['compensations_enabled'] = True
    
    async def _commit_compensating_transaction(self, context: TransactionContext):
        """Commit compensating transaction"""
        await self._commit_simple_transaction(context)
    
    async def _rollback_compensating_transaction(self, context: TransactionContext):
        """Rollback compensating transaction"""
        # Execute all registered compensations
        for comp_op in context.compensation_operations:
            try:
                # Execute compensation operation
                session = context.metadata.get('session')
                if session:
                    await session.execute(text(comp_op.get('sql', '')), comp_op.get('params', {}))
            except Exception as e:
                logger.error(f"Compensating operation failed: {e}")
        
        await self._rollback_simple_transaction(context)
    
    # === Nested Transaction Implementation ===
    
    async def _begin_nested_transaction(self, context: TransactionContext):
        """Begin nested transaction using savepoints"""
        await self._begin_simple_transaction(context)
        
        if context.config.enable_savepoints:
            session = context.metadata.get('session')
            if session:
                savepoint_name = f"sp_{len(context.savepoints)}"
                await session.execute(text(f"SAVEPOINT {savepoint_name}"))
                context.savepoints.append(savepoint_name)
    
    async def _commit_nested_transaction(self, context: TransactionContext):
        """Commit nested transaction"""
        await self._commit_simple_transaction(context)
    
    async def _rollback_nested_transaction(self, context: TransactionContext):
        """Rollback to savepoint or full rollback"""
        session = context.metadata.get('session')
        
        if session and context.savepoints:
            # Rollback to most recent savepoint
            savepoint_name = context.savepoints[-1]
            await session.execute(text(f"ROLLBACK TO {savepoint_name}"))
            context.savepoints.pop()
        else:
            await self._rollback_simple_transaction(context)
    
    # === Query and Management Methods ===
    
    async def get_transaction_status(self, transaction_id: str) -> Optional[TransactionContext]:
        """Get transaction status"""
        if transaction_id in self.active_transactions:
            return self.active_transactions[transaction_id]
        
        # Check history
        for tx in self.transaction_history:
            if tx.transaction_id == transaction_id:
                return tx
        
        return None
    
    async def get_active_transactions(self) -> List[TransactionContext]:
        """Get all active transactions"""



        return list(self.active_transactions.values())
    
    async def get_transaction_statistics(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        total_transactions = len(self.transaction_history) + len(self.active_transactions)
        
        if not self.transaction_history:
            return {
                'total_transactions': total_transactions,
                'active_transactions': len(self.active_transactions),
                'completed_transactions': 0,
                'success_rate': 0.0,
                'average_duration_ms': 0.0
            }
        
        completed = [tx for tx in self.transaction_history if tx.completed_at]
        successful = [tx for tx in completed if tx.state == TransactionState.COMMITTED]
        
        durations = [tx.duration_ms for tx in completed if tx.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        return {
            'total_transactions': total_transactions,
            'active_transactions': len(self.active_transactions),
            'completed_transactions': len(completed),
            'successful_transactions': len(successful),
            'failed_transactions': len(completed) - len(successful),
            'success_rate': (len(successful) / len(completed)) * 100 if completed else 0.0,
            'average_duration_ms': avg_duration,
            'longest_duration_ms': max(durations) if durations else 0.0,
            'shortest_duration_ms': min(durations) if durations else 0.0
        }
    
    async def cleanup_stale_transactions(self, max_age_hours: int = 24):
        """Clean up stale transactions"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        stale_transaction_ids = []
        
        for tx_id, context in self.active_transactions.items():
            if context.started_at < cutoff_time:
                stale_transaction_ids.append(tx_id)
        
        # Rollback stale transactions
        for tx_id in stale_transaction_ids:
            try:
                await self.rollback_transaction(tx_id, f"Stale transaction cleanup after {max_age_hours}h")
                logger.warning(f"Cleaned up stale transaction: {tx_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup stale transaction {tx_id}: {e}")
        
        return len(stale_transaction_ids)


class TransactionExecutor:
    """Transaction executor for operation management"""
    
    def __init__(self, manager: TransactionManager, context: TransactionContext):
        self.manager = manager
        self.context = context
        self.operations: List[TransactionOperation] = []
    
    async def add_operation(self, operation: TransactionOperation):
        """Add operation to transaction"""
        self.operations.append(operation)
    
    async def execute_operation(self, operation: TransactionOperation) -> Any:
        """Execute a single operation"""
        session = self.context.metadata.get('session')
        
        if not session:
            raise RuntimeError("No session available for operation execution")
        
        result = await operation.execute(session, self.context)
        
        # Store operation for potential compensation
        if self.context.transaction_type in [TransactionType.SAGA, TransactionType.COMPENSATING]:
            self.context.metadata.setdefault('operations', []).append(operation)
        
        return result
    
    async def create_savepoint(self, name: Optional[str] = None) -> str:
        """Create savepoint in nested transaction"""
        if self.context.transaction_type != TransactionType.NESTED:
            raise RuntimeError("Savepoints only available in nested transactions")
        
        session = self.context.metadata.get('session')
        if not session:
            raise RuntimeError("No session available for savepoint")
        
        savepoint_name = name or f"sp_{len(self.context.savepoints)}"
        await session.execute(text(f"SAVEPOINT {savepoint_name}"))
        self.context.savepoints.append(savepoint_name)
        
        return savepoint_name
    
    async def rollback_to_savepoint(self, savepoint_name: str):
        """Rollback to specific savepoint"""
        if self.context.transaction_type != TransactionType.NESTED:
            raise RuntimeError("Savepoints only available in nested transactions")
        
        if savepoint_name not in self.context.savepoints:
            raise ValueError(f"Savepoint {savepoint_name} not found")
        
        session = self.context.metadata.get('session')
        if not session:
            raise RuntimeError("No session available for savepoint rollback")
        
        await session.execute(text(f"ROLLBACK TO {savepoint_name}"))
        
        # Remove savepoints after the rollback point
        while self.context.savepoints and self.context.savepoints[-1] != savepoint_name:
            self.context.savepoints.pop()
    
    async def execute_batch_operations(self, operations: List[TransactionOperation]) -> List[Any]:
        """Execute multiple operations in batch"""
        results = []
        
        for operation in operations:
            try:
                result = await self.execute_operation(operation)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch operation {operation.operation_id} failed: {e}")
                
                # In saga pattern, start compensations immediately
                if self.context.transaction_type == TransactionType.SAGA:
                    await self._compensate_executed_operations()
                
                raise
        
        return results
    
    async def _compensate_executed_operations(self):
        """Compensate all executed operations in reverse order"""
        operations = self.context.metadata.get('operations', [])
        
        for operation in reversed(operations):
            if hasattr(operation, 'compensate'):
                try:
                    session = self.context.metadata.get('session')
                    if session:
                        await operation.compensate(session, self.context)
                except Exception as e:
                    logger.error(f"Compensation failed for operation {operation.operation_id}: {e}")


class DistributedTransactionCoordinator:
    """Coordinator for distributed transactions across multiple services"""
    
    def __init__(self, transaction_manager: TransactionManager):
        self.transaction_manager = transaction_manager
        self.participants: Dict[str, Any] = {}
        self.coordinator_state: Dict[str, Dict[str, Any]] = {}
    
    def register_participant(self, participant_id: str, participant_client: Any):
        """Register a participant in distributed transactions"""
        self.participants[participant_id] = participant_client
    
    async def coordinate_distributed_transaction(self, 
                                               transaction_id: str,
                                               operations_by_participant: Dict[str, List[Any]]) -> bool:
        """Coordinate distributed transaction using 2PC protocol"""
        
        # Phase 1: Prepare
        prepare_results = {}
        
        for participant_id, operations in operations_by_participant.items():
            if participant_id not in self.participants:
                raise ValueError(f"Participant {participant_id} not registered")
            
            participant = self.participants[participant_id]
            
            try:
                # Send prepare request to participant
                prepare_result = await self._send_prepare_request(
                    participant, transaction_id, operations
                )
                prepare_results[participant_id] = prepare_result
            except Exception as e:
                logger.error(f"Prepare phase failed for participant {participant_id}: {e}")
                
                # Abort transaction - send abort to all participants
                await self._send_abort_to_all_participants(transaction_id, prepare_results.keys())
                return False
        
        # Check if all participants are prepared
        if not all(prepare_results.values()):
            await self._send_abort_to_all_participants(transaction_id, prepare_results.keys())
            return False
        
        # Phase 2: Commit
        commit_results = {}
        
        for participant_id in operations_by_participant.keys():
            participant = self.participants[participant_id]
            
            try:
                commit_result = await self._send_commit_request(participant, transaction_id)
                commit_results[participant_id] = commit_result
            except Exception as e:
                logger.error(f"Commit phase failed for participant {participant_id}: {e}")
                # In 2PC, if commit fails, we have a problem - log and alert
                logger.critical(f"Distributed transaction {transaction_id} in inconsistent state")
                return False
        
        return all(commit_results.values())
    
    async def _send_prepare_request(self, participant: Any, transaction_id: str, operations: List[Any]) -> bool:
        """Send prepare request to participant"""
        # Implementation depends on participant interface
        # This is a placeholder - implement based on your service communication protocol
        try:
            if hasattr(participant, 'prepare_transaction'):
                return await participant.prepare_transaction(transaction_id, operations)
            return True
        except Exception as e:
            logger.error(f"Prepare request failed: {e}")
            return False
    
    async def _send_commit_request(self, participant: Any, transaction_id: str) -> bool:
        """Send commit request to participant"""



        try:
            if hasattr(participant, 'commit_transaction'):
                return await participant.commit_transaction(transaction_id)
            return True
        except Exception as e:
            logger.error(f"Commit request failed: {e}")
            return False
    
    async def _send_abort_to_all_participants(self, transaction_id: str, participant_ids: List[str]):
        """Send abort to all participants"""
        for participant_id in participant_ids:
            if participant_id in self.participants:
                participant = self.participants[participant_id]
                try:
                    if hasattr(participant, 'abort_transaction'):
                        await participant.abort_transaction(transaction_id)
                except Exception as e:
                    logger.error(f"Abort request failed for participant {participant_id}: {e}")


# Global transaction manager instance
_transaction_manager: Optional[TransactionManager] = None


async def get_transaction_manager() -> TransactionManager:
    """Get global transaction manager instance"""
    global _transaction_manager
    
    if _transaction_manager is None:
        _transaction_manager = TransactionManager()
        await _transaction_manager.initialize()
    
    return _transaction_manager


# Convenience transaction decorators and context managers

@asynccontextmanager
async def simple_transaction(config: Optional[TransactionConfig] = None):
    """Simple transaction context manager"""
    manager = await get_transaction_manager()
    async with manager.transaction(TransactionType.SIMPLE, config) as tx:
        yield tx


@asynccontextmanager
async def saga_transaction(config: Optional[TransactionConfig] = None):
    """Saga transaction context manager"""
    manager = await get_transaction_manager()
    async with manager.transaction(TransactionType.SAGA, config) as tx:
        yield tx


@asynccontextmanager
async def distributed_transaction(config: Optional[TransactionConfig] = None):
    """Distributed transaction context manager"""
    manager = await get_transaction_manager()
    async with manager.transaction(TransactionType.DISTRIBUTED, config) as tx:
        yield tx


# Transaction retry decorator
def retry_transaction(max_retries: int = 3, 
                     delay_seconds: float = 1.0,
                     backoff_multiplier: float = 2.0):
    """Decorator for automatic transaction retry on failure"""
    
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = delay_seconds
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except (OperationalError, IntegrityError) as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(f"Transaction attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                        await asyncio.sleep(delay)
                        delay *= backoff_multiplier
                    else:
                        logger.error(f"Transaction failed after {max_retries} retries: {e}")
                        raise
                
                except Exception as e:
                    # Don't retry non-recoverable exceptions
                    logger.error(f"Non-recoverable transaction error: {e}")
                    raise
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator
