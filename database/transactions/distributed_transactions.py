"""Distributed Transaction Manager - Cross-Service Transaction Coordination

Enterprise-grade distributed transaction management providing two-phase commit
protocol, saga pattern implementation, and microservices transaction coordination
for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.
"""import asyncio
import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import aiohttp
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class DistributedTransactionState(Enum):
    """Distributed transaction state enumeration"""    INIT = "initialized"
    COORDINATING = "coordinating"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ParticipantState(Enum):
    """Participant state in distributed transaction"""    PENDING = "pending"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"
    COMPENSATED = "compensated"
    FAILED = "failed"


@dataclass
class ServiceParticipant:
    """Service participant in distributed transaction"""    service_id: str
    endpoint: str
    state: ParticipantState = ParticipantState.PENDING
    prepare_timeout: int = 10
    commit_timeout: int = 30
    compensation_handler: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None


@dataclass
class DistributedTransaction:
    """Distributed transaction context"""    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: DistributedTransactionState = DistributedTransactionState.INIT
    participants: List[ServiceParticipant] = field(default_factory=list)
    coordinator_id: str = ""
    saga_steps: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout: int = 300  # 5 minutes default
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate transaction duration"""        if self.started_at and self.completed_at:
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


class SagaOrchestrator:
    """Saga pattern orchestrator for long-running distributed transactions"""    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.active_sagas: Dict[str, DistributedTransaction] = {}
        self.compensation_handlers: Dict[str, Callable] = {}
    
    async def execute_saga(self, transaction: DistributedTransaction) -> bool:
        """Execute saga pattern with compensation"""        try:
            transaction.state = DistributedTransactionState.COORDINATING
            self.active_sagas[transaction.transaction_id] = transaction
            
            executed_steps = []
            
            for step_index, step in enumerate(transaction.saga_steps):
                try:
                    # Execute step
                    result = await self._execute_saga_step(step, transaction)
                    
                    if result:
                        executed_steps.append((step_index, step))
                        logger.debug("Saga step %d completed: %s", step_index, step.get('name', 'unnamed'))
                    else:
                        # Step failed, trigger compensation
                        await self._compensate_saga_steps(executed_steps, transaction)
                        transaction.state = DistributedTransactionState.FAILED
                        return False
                        
                except Exception as e:
                    logger.error("Saga step %d failed: %s", step_index, str(e))
                    await self._compensate_saga_steps(executed_steps, transaction)
                    transaction.state = DistributedTransactionState.FAILED
                    return False
            
            transaction.state = DistributedTransactionState.COMMITTED
            transaction.completed_at = datetime.now(timezone.utc)
            return True
            
        except Exception as e:
            logger.error("Saga execution failed: %s", str(e))
            transaction.state = DistributedTransactionState.FAILED
            return False
        finally:
            self.active_sagas.pop(transaction.transaction_id, None)
    
    async def _execute_saga_step(self, step: Dict[str, Any], transaction: DistributedTransaction) -> bool:
        """Execute individual saga step"""        service_url = step.get('service_url')
        action = step.get('action')
        payload = step.get('payload', {})
        
        if not service_url or not action:
            logger.error("Invalid saga step: missing service_url or action")
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{service_url}/{action}",
                    json={
                        'transaction_id': transaction.transaction_id,
                        'payload': payload
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error("Saga step execution failed: %s", str(e))
            return False
    
    async def _compensate_saga_steps(self, executed_steps: List[tuple], transaction: DistributedTransaction) -> None:
        """Execute compensation for completed saga steps"""        transaction.state = DistributedTransactionState.COMPENSATING
        
        # Compensate in reverse order
        for step_index, step in reversed(executed_steps):
            try:
                compensation_url = step.get('compensation_url')
                if compensation_url:
                    await self._execute_compensation(compensation_url, step, transaction)
                    logger.debug("Compensated saga step %d", step_index)
            except Exception as e:
                logger.error("Compensation failed for step %d: %s", step_index, str(e))
        
        transaction.state = DistributedTransactionState.COMPENSATED
    
    async def _execute_compensation(self, compensation_url: str, step: Dict[str, Any], 
                                  transaction: DistributedTransaction) -> None:
        """Execute compensation for a specific step"""        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    compensation_url,
                    json={
                        'transaction_id': transaction.transaction_id,
                        'step': step
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        logger.error("Compensation request failed with status: %d", response.status)
        except Exception as e:
            logger.error("Compensation execution failed: %s", str(e))


class DistributedTransactionManager:
    """    Distributed transaction manager providing enterprise-grade coordination
    
    Features:
    - Two-phase commit protocol (2PC)
    - Saga pattern for long-running transactions
    - Service participant management
    - Automatic retry and recovery
    - Redis-based coordination state
    - Timeout and failure handling
    - Performance monitoring
    """    
    def __init__(self, redis_url: str = "redis://localhost:6379", coordinator_id: Optional[str] = None):
        self.coordinator_id = coordinator_id or f"coord-{uuid.uuid4().hex[:8]}"
        self.redis_client = None
        self.redis_url = redis_url
        self.active_transactions: Dict[str, DistributedTransaction] = {}
        self.service_registry: Dict[str, Dict[str, Any]] = {}
        self.saga_orchestrator = None
        self.executor = ThreadPoolExecutor(max_workers=50)
        self._shutdown = False
        
        logger.info("DistributedTransactionManager initialized with coordinator_id=%s", 
                   self.coordinator_id)
    
    async def initialize(self) -> None:
        """Initialize Redis connection and saga orchestrator"""        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            self.saga_orchestrator = SagaOrchestrator(self.redis_client)
            
            # Start background tasks
            asyncio.create_task(self._monitor_transactions())
            asyncio.create_task(self._cleanup_expired_transactions())
            
            logger.info("DistributedTransactionManager initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize DistributedTransactionManager: %s", str(e))
            raise
    
    async def register_service(self, service_id: str, endpoint: str, 
                             capabilities: Optional[List[str]] = None) -> None:
        """Register a service participant"""        service_info = {
            'endpoint': endpoint,
            'capabilities': capabilities or [],
            'registered_at': datetime.now(timezone.utc).isoformat(),
            'health_status': 'unknown'
        }
        
        self.service_registry[service_id] = service_info
        
        # Store in Redis for coordination
        await self.redis_client.hset(
            f"services:{self.coordinator_id}",
            service_id,
            json.dumps(service_info)
        )
        
        logger.info("Service registered: %s at %s", service_id, endpoint)
    
    async def begin_distributed_transaction(
        self,
        participants: List[Dict[str, Any]],
        timeout: int = 300,
        use_saga: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DistributedTransaction:
        """Begin a new distributed transaction"""        
        transaction = DistributedTransaction(
            coordinator_id=self.coordinator_id,
            timeout=timeout,
            metadata=metadata or {}
        )
        
        # Add participants
        for participant_info in participants:
            participant = ServiceParticipant(
                service_id=participant_info['service_id'],
                endpoint=participant_info['endpoint'],
                prepare_timeout=participant_info.get('prepare_timeout', 10),
                commit_timeout=participant_info.get('commit_timeout', 30),
                compensation_handler=participant_info.get('compensation_handler'),
                metadata=participant_info.get('metadata', {})
            )
            transaction.participants.append(participant)
        
        # Setup saga steps if using saga pattern
        if use_saga:
            transaction.saga_steps = participants
        
        transaction.started_at = datetime.now(timezone.utc)
        self.active_transactions[transaction.transaction_id] = transaction
        
        # Store transaction state in Redis
        await self._persist_transaction_state(transaction)
        
        logger.info("Distributed transaction started: %s (participants=%d, saga=%s)",
                   transaction.transaction_id, len(participants), use_saga)
        
        return transaction
    
    async def execute_two_phase_commit(self, transaction_id: str) -> bool:
        """Execute two-phase commit protocol"""        
        transaction = self.active_transactions.get(transaction_id)
        if not transaction:
            logger.error("Transaction not found: %s", transaction_id)
            return False
        
        if transaction.is_expired:
            await self._abort_transaction(transaction, DistributedTransactionState.TIMEOUT)
            return False
        
        try:
            # Phase 1: Prepare
            transaction.state = DistributedTransactionState.PREPARING
            await self._persist_transaction_state(transaction)
            
            prepare_success = await self._prepare_all_participants(transaction)
            
            if not prepare_success:
                await self._abort_transaction(transaction, DistributedTransactionState.FAILED)
                return False
            
            transaction.state = DistributedTransactionState.PREPARED
            await self._persist_transaction_state(transaction)
            
            # Phase 2: Commit
            transaction.state = DistributedTransactionState.COMMITTING
            await self._persist_transaction_state(transaction)
            
            commit_success = await self._commit_all_participants(transaction)
            
            if commit_success:
                transaction.state = DistributedTransactionState.COMMITTED
                transaction.completed_at = datetime.now(timezone.utc)
                await self._persist_transaction_state(transaction)
                
                logger.info("Distributed transaction committed: %s (duration=%.3fs)",
                           transaction_id, transaction.duration or 0)
                return True
            else:
                await self._abort_transaction(transaction, DistributedTransactionState.FAILED)
                return False
                
        except Exception as e:
            logger.error("Two-phase commit failed for transaction %s: %s", transaction_id, str(e))
            await self._abort_transaction(transaction, DistributedTransactionState.FAILED)
            return False
    
    async def execute_saga_transaction(self, transaction_id: str) -> bool:
        """Execute saga pattern transaction"""        
        transaction = self.active_transactions.get(transaction_id)
        if not transaction:
            logger.error("Transaction not found: %s", transaction_id)
            return False
        
        if not self.saga_orchestrator:
            logger.error("Saga orchestrator not initialized")
            return False
        
        try:
            success = await self.saga_orchestrator.execute_saga(transaction)
            
            if success:
                logger.info("Saga transaction completed: %s (duration=%.3fs)",
                           transaction_id, transaction.duration or 0)
            else:
                logger.error("Saga transaction failed: %s", transaction_id)
            
            await self._persist_transaction_state(transaction)
            return success
            
        except Exception as e:
            logger.error("Saga execution failed for transaction %s: %s", transaction_id, str(e))
            transaction.state = DistributedTransactionState.FAILED
            await self._persist_transaction_state(transaction)
            return False
    
    async def _prepare_all_participants(self, transaction: DistributedTransaction) -> bool:
        """Prepare all transaction participants"""        
        prepare_tasks = []
        for participant in transaction.participants:
            task = asyncio.create_task(self._prepare_participant(participant, transaction))
            prepare_tasks.append(task)
        
        results = await asyncio.gather(*prepare_tasks, return_exceptions=True)
        
        # Check if all participants prepared successfully
        all_prepared = True
        for i, result in enumerate(results):
            participant = transaction.participants[i]
            
            if isinstance(result, Exception):
                logger.error("Prepare failed for participant %s: %s", 
                           participant.service_id, str(result))
                participant.state = ParticipantState.FAILED
                participant.last_error = str(result)
                all_prepared = False
            elif result:
                participant.state = ParticipantState.PREPARED
            else:
                participant.state = ParticipantState.FAILED
                all_prepared = False
        
        return all_prepared
    
    async def _commit_all_participants(self, transaction: DistributedTransaction) -> bool:
        """Commit all transaction participants"""        
        commit_tasks = []
        for participant in transaction.participants:
            if participant.state == ParticipantState.PREPARED:
                task = asyncio.create_task(self._commit_participant(participant, transaction))
                commit_tasks.append(task)
        
        results = await asyncio.gather(*commit_tasks, return_exceptions=True)
        
        # Update participant states
        task_index = 0
        for participant in transaction.participants:
            if participant.state == ParticipantState.PREPARED:
                result = results[task_index]
                task_index += 1
                
                if isinstance(result, Exception):
                    logger.error("Commit failed for participant %s: %s", 
                               participant.service_id, str(result))
                    participant.state = ParticipantState.FAILED
                    participant.last_error = str(result)
                elif result:
                    participant.state = ParticipantState.COMMITTED
                else:
                    participant.state = ParticipantState.FAILED
        
        # Check if all participants committed successfully
        return all(p.state == ParticipantState.COMMITTED for p in transaction.participants 
                  if p.state != ParticipantState.FAILED)
    
    async def _prepare_participant(self, participant: ServiceParticipant, 
                                 transaction: DistributedTransaction) -> bool:
        """Prepare individual participant"""        
        try:
            async with aiohttp.ClientSession() as session:
                prepare_data = {
                    'transaction_id': transaction.transaction_id,
                    'coordinator_id': transaction.coordinator_id,
                    'timeout': participant.prepare_timeout,
                    'metadata': participant.metadata
                }
                
                async with session.post(
                    f"{participant.endpoint}/prepare",
                    json=prepare_data,
                    timeout=aiohttp.ClientTimeout(total=participant.prepare_timeout)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return result.get('prepared', False)
                    else:
                        logger.error("Prepare request failed for %s: HTTP %d", 
                                   participant.service_id, response.status)
                        return False
                        
        except asyncio.TimeoutError:
            logger.error("Prepare timeout for participant %s", participant.service_id)
            return False
        except Exception as e:
            logger.error("Prepare failed for participant %s: %s", participant.service_id, str(e))
            return False
    
    async def _commit_participant(self, participant: ServiceParticipant, 
                                transaction: DistributedTransaction) -> bool:
        """Commit individual participant"""        
        try:
            async with aiohttp.ClientSession() as session:
                commit_data = {
                    'transaction_id': transaction.transaction_id,
                    'coordinator_id': transaction.coordinator_id,
                    'metadata': participant.metadata
                }
                
                async with session.post(
                    f"{participant.endpoint}/commit",
                    json=commit_data,
                    timeout=aiohttp.ClientTimeout(total=participant.commit_timeout)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return result.get('committed', False)
                    else:
                        logger.error("Commit request failed for %s: HTTP %d", 
                                   participant.service_id, response.status)
                        return False
                        
        except asyncio.TimeoutError:
            logger.error("Commit timeout for participant %s", participant.service_id)
            return False
        except Exception as e:
            logger.error("Commit failed for participant %s: %s", participant.service_id, str(e))
            return False
    
    async def _abort_transaction(self, transaction: DistributedTransaction, 
                               state: DistributedTransactionState) -> None:
        """Abort transaction and notify participants"""        
        transaction.state = state
        transaction.completed_at = datetime.now(timezone.utc)
        
        # Notify participants to abort
        abort_tasks = []
        for participant in transaction.participants:
            if participant.state in [ParticipantState.PREPARED, ParticipantState.PENDING]:
                task = asyncio.create_task(self._abort_participant(participant, transaction))
                abort_tasks.append(task)
        
        if abort_tasks:
            await asyncio.gather(*abort_tasks, return_exceptions=True)
        
        await self._persist_transaction_state(transaction)
        
        logger.info("Distributed transaction aborted: %s (state=%s)", 
                   transaction.transaction_id, state.value)
    
    async def _abort_participant(self, participant: ServiceParticipant, 
                               transaction: DistributedTransaction) -> None:
        """Abort individual participant"""        
        try:
            async with aiohttp.ClientSession() as session:
                abort_data = {
                    'transaction_id': transaction.transaction_id,
                    'coordinator_id': transaction.coordinator_id
                }
                
                async with session.post(
                    f"{participant.endpoint}/abort",
                    json=abort_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        participant.state = ParticipantState.ABORTED
                    else:
                        logger.error("Abort request failed for %s: HTTP %d", 
                                   participant.service_id, response.status)
                        
        except Exception as e:
            logger.error("Abort failed for participant %s: %s", participant.service_id, str(e))
    
    async def _persist_transaction_state(self, transaction: DistributedTransaction) -> None:
        """Persist transaction state to Redis"""        
        if not self.redis_client:
            return
        
        try:
            transaction_data = {
                'transaction_id': transaction.transaction_id,
                'state': transaction.state.value,
                'coordinator_id': transaction.coordinator_id,
                'created_at': transaction.created_at.isoformat(),
                'started_at': transaction.started_at.isoformat() if transaction.started_at else None,
                'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None,
                'timeout': transaction.timeout,
                'metadata': transaction.metadata,
                'participants': [
                    {
                        'service_id': p.service_id,
                        'endpoint': p.endpoint,
                        'state': p.state.value,
                        'retry_count': p.retry_count,
                        'last_error': p.last_error
                    }
                    for p in transaction.participants
                ]
            }
            
            await self.redis_client.setex(
                f"transaction:{transaction.transaction_id}",
                3600,  # 1 hour TTL
                json.dumps(transaction_data)
            )
            
        except Exception as e:
            logger.error("Failed to persist transaction state: %s", str(e))
    
    async def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction status"""        
        transaction = self.active_transactions.get(transaction_id)
        if transaction:
            return {
                'transaction_id': transaction.transaction_id,
                'state': transaction.state.value,
                'duration': transaction.duration,
                'participants': [
                    {
                        'service_id': p.service_id,
                        'state': p.state.value,
                        'retry_count': p.retry_count,
                        'last_error': p.last_error
                    }
                    for p in transaction.participants
                ]
            }
        
        # Try to get from Redis
        if self.redis_client:
            try:
                data = await self.redis_client.get(f"transaction:{transaction_id}")
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error("Failed to get transaction status from Redis: %s", str(e))
        
        return None
    
    async def _monitor_transactions(self) -> None:
        """Background task to monitor transaction health"""        while not self._shutdown:
            try:
                current_time = datetime.now(timezone.utc)
                
                for transaction in list(self.active_transactions.values()):
                    if transaction.is_expired:
                        logger.warning("Transaction expired: %s", transaction.transaction_id)
                        await self._abort_transaction(transaction, DistributedTransactionState.TIMEOUT)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error("Error in transaction monitoring: %s", str(e))
                await asyncio.sleep(10)
    
    async def _cleanup_expired_transactions(self) -> None:
        """Cleanup expired transactions from memory"""        while not self._shutdown:
            try:
                expired_transactions = []
                
                for transaction_id, transaction in self.active_transactions.items():
                    if transaction.state in [
                        DistributedTransactionState.COMMITTED,
                        DistributedTransactionState.COMPENSATED,
                        DistributedTransactionState.FAILED,
                        DistributedTransactionState.TIMEOUT
                    ]:
                        if transaction.duration and transaction.duration > 3600:  # 1 hour
                            expired_transactions.append(transaction_id)
                
                for transaction_id in expired_transactions:
                    self.active_transactions.pop(transaction_id, None)
                    logger.debug("Cleaned up completed transaction: %s", transaction_id)
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error("Error in transaction cleanup: %s", str(e))
                await asyncio.sleep(60)
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""        logger.info("Shutting down DistributedTransactionManager...")
        self._shutdown = True
        
        # Abort all active transactions
        for transaction in list(self.active_transactions.values()):
            if transaction.state not in [
                DistributedTransactionState.COMMITTED,
                DistributedTransactionState.COMPENSATED
            ]:
                await self._abort_transaction(transaction, DistributedTransactionState.FAILED)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("DistributedTransactionManager shutdown complete")
