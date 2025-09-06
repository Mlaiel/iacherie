#!/usr/bin/env python3
"""Transaction Coordination Service - Distributed Transaction Management
=======================================================================

Distributed transaction coordination service for managing ACID compliance
across microservices in saga patterns. Provides two-phase commit coordination,
distributed locking, and consensus mechanisms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TransactionStatus(Enum):
    """Transaction status enumeration"""
    INITIATED = "initiated"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"
    FAILED = "failed"


class ParticipantStatus(Enum):
    """Participant status in transaction"""
    UNKNOWN = "unknown"
    PREPARE_OK = "prepare_ok"
    PREPARE_ABORT = "prepare_abort"
    COMMITTED = "committed"
    ABORTED = "aborted"
    TIMEOUT = "timeout"


@dataclass
class TransactionParticipant:
    """Represents a participant in distributed transaction"""
    participant_id: str
    service_name: str
    endpoint: str
    status: ParticipantStatus = ParticipantStatus.UNKNOWN
    prepare_timestamp: Optional[datetime] = None
    commit_timestamp: Optional[datetime] = None
    rollback_data: Optional[Dict[str, Any]] = None


@dataclass
class DistributedTransaction:
    """Represents a distributed transaction"""
    transaction_id: str
    saga_id: str
    coordinator_id: str
    status: TransactionStatus
    participants: List[TransactionParticipant]
    started_at: datetime
    timeout_seconds: int = 300
    context: Dict[str, Any] = field(default_factory=dict)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class TransactionCoordinationService:
    """Main service for distributed transaction coordination"""
    
    def __init__(self):
        self.active_transactions: Dict[str, DistributedTransaction] = {}
        self.completed_transactions: List[DistributedTransaction] = []
        self.coordination_locks: Dict[str, asyncio.Lock] = {}
        self.timeout_tasks: Dict[str, asyncio.Task] = {}
        self.coordinator_id = f"coordinator_{uuid.uuid4().hex[:8]}"
    
    async def begin_distributed_transaction(
        self,
        saga_id: str,
        participants: List[Dict[str, str]],
        timeout_seconds: int = 300,
        context: Dict[str, Any] = None
    ) -> str:
        """Begin new distributed transaction"""
        transaction_id = str(uuid.uuid4())
        
        # Create participant objects
        transaction_participants = [
            TransactionParticipant(
                participant_id=f"{p['service_name']}_{uuid.uuid4().hex[:8]}",
                service_name=p["service_name"],
                endpoint=p["endpoint"]
            )
            for p in participants
        ]
        
        # Create transaction
        transaction = DistributedTransaction(
            transaction_id=transaction_id,
            saga_id=saga_id,
            coordinator_id=self.coordinator_id,
            status=TransactionStatus.INITIATED,
            participants=transaction_participants,
            started_at=datetime.now(timezone.utc),
            timeout_seconds=timeout_seconds,
            context=context or {}
        )
        
        self.active_transactions[transaction_id] = transaction
        
        # Start timeout monitoring
        timeout_task = asyncio.create_task(
            self._monitor_transaction_timeout(transaction_id)
        )
        self.timeout_tasks[transaction_id] = timeout_task
        
        logger.info(f"Started distributed transaction {transaction_id} for saga {saga_id}")
        return transaction_id
    
    async def execute_two_phase_commit(self, transaction_id: str) -> bool:
        """Execute two-phase commit protocol"""
        if transaction_id not in self.active_transactions:
            logger.error(f"Transaction {transaction_id} not found")
            return False
        
        transaction = self.active_transactions[transaction_id]
        
        try:
            # Phase 1: Prepare
            transaction.status = TransactionStatus.PREPARING
            logger.info(f"Starting prepare phase for transaction {transaction_id}")
            
            prepare_success = await self._prepare_phase(transaction)
            
            if not prepare_success:
                # Abort transaction
                transaction.status = TransactionStatus.ABORTING
                await self._abort_phase(transaction)
                transaction.status = TransactionStatus.ABORTED
                return False
            
            # Phase 2: Commit
            transaction.status = TransactionStatus.COMMITTING
            logger.info(f"Starting commit phase for transaction {transaction_id}")
            
            commit_success = await self._commit_phase(transaction)
            
            if commit_success:
                transaction.status = TransactionStatus.COMMITTED
                transaction.completed_at = datetime.now(timezone.utc)
                logger.info(f"Transaction {transaction_id} committed successfully")
                return True
            else:
                transaction.status = TransactionStatus.FAILED
                transaction.error_message = "Commit phase failed"
                return False
                
        except Exception as e:
            logger.error(f"Two-phase commit failed for {transaction_id}: {e}")
            transaction.status = TransactionStatus.FAILED
            transaction.error_message = str(e)
            return False
        finally:
            # Cleanup
            await self._cleanup_transaction(transaction_id)
    
    async def _prepare_phase(self, transaction: DistributedTransaction) -> bool:
        """Execute prepare phase of 2PC"""
        prepare_tasks = []
        
        for participant in transaction.participants:
            task = asyncio.create_task(
                self._send_prepare_request(participant, transaction.context)
            )
            prepare_tasks.append((participant, task))
        
        # Wait for all prepare responses
        all_prepared = True
        
        for participant, task in prepare_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=30.0)
                participant.status = ParticipantStatus.PREPARE_OK if result else ParticipantStatus.PREPARE_ABORT
                participant.prepare_timestamp = datetime.now(timezone.utc)
                
                if not result:
                    all_prepared = False
                    
            except asyncio.TimeoutError:
                participant.status = ParticipantStatus.TIMEOUT
                all_prepared = False
                logger.warning(f"Prepare timeout for participant {participant.participant_id}")
            except Exception as e:
                participant.status = ParticipantStatus.PREPARE_ABORT
                all_prepared = False
                logger.error(f"Prepare failed for participant {participant.participant_id}: {e}")
        
        logger.info(f"Prepare phase result: {all_prepared}")
        return all_prepared
    
    async def _commit_phase(self, transaction: DistributedTransaction) -> bool:
        """Execute commit phase of 2PC"""
        commit_tasks = []
        
        for participant in transaction.participants:
            if participant.status == ParticipantStatus.PREPARE_OK:
                task = asyncio.create_task(
                    self._send_commit_request(participant, transaction.context)
                )
                commit_tasks.append((participant, task))
        
        # Wait for all commit responses
        all_committed = True
        
        for participant, task in commit_tasks:
            try:
                result = await asyncio.wait_for(task, timeout=30.0)
                participant.status = ParticipantStatus.COMMITTED if result else ParticipantStatus.ABORTED
                participant.commit_timestamp = datetime.now(timezone.utc)
                
                if not result:
                    all_committed = False
                    
            except asyncio.TimeoutError:
                participant.status = ParticipantStatus.TIMEOUT
                all_committed = False
                logger.warning(f"Commit timeout for participant {participant.participant_id}")
            except Exception as e:
                participant.status = ParticipantStatus.ABORTED
                all_committed = False
                logger.error(f"Commit failed for participant {participant.participant_id}: {e}")
        
        return all_committed
    
    async def _abort_phase(self, transaction: DistributedTransaction):
        """Execute abort phase"""
        abort_tasks = []
        
        for participant in transaction.participants:
            task = asyncio.create_task(
                self._send_abort_request(participant, transaction.context)
            )
            abort_tasks.append(task)
        
        # Wait for all abort responses (best effort)
        await asyncio.gather(*abort_tasks, return_exceptions=True)
        
        # Mark all participants as aborted
        for participant in transaction.participants:
            participant.status = ParticipantStatus.ABORTED
    
    async def _send_prepare_request(
        self, 
        participant: TransactionParticipant,
        context: Dict[str, Any]
    ) -> bool:
        """Send prepare request to participant"""
        # Mock prepare request - in real implementation would make HTTP call
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Mock success rate of 90%
        import random
        success = random.random() > 0.1
        
        logger.debug(f"Prepare request to {participant.service_name}: {'OK' if success else 'ABORT'}")
        return success
    
    async def _send_commit_request(
        self,
        participant: TransactionParticipant,
        context: Dict[str, Any]
    ) -> bool:
        """Send commit request to participant"""
        # Mock commit request
        await asyncio.sleep(0.05)  # Simulate network delay
        
        # Mock success rate of 95%
        import random
        success = random.random() > 0.05
        
        logger.debug(f"Commit request to {participant.service_name}: {'OK' if success else 'FAILED'}")
        return success
    
    async def _send_abort_request(
        self,
        participant: TransactionParticipant,
        context: Dict[str, Any]
    ):
        """Send abort request to participant"""
        # Mock abort request
        await asyncio.sleep(0.03)  # Simulate network delay
        logger.debug(f"Abort request sent to {participant.service_name}")
    
    async def _monitor_transaction_timeout(self, transaction_id: str):
        """Monitor transaction for timeout"""
        transaction = self.active_transactions.get(transaction_id)
        if not transaction:
            return
        
        try:
            await asyncio.sleep(transaction.timeout_seconds)
            
            # Check if transaction is still active
            if (transaction_id in self.active_transactions and 
                transaction.status not in [TransactionStatus.COMMITTED, TransactionStatus.ABORTED]):
                
                logger.warning(f"Transaction {transaction_id} timed out")
                transaction.status = TransactionStatus.ABORTING
                await self._abort_phase(transaction)
                transaction.status = TransactionStatus.ABORTED
                transaction.error_message = "Transaction timeout"
                
                await self._cleanup_transaction(transaction_id)
                
        except asyncio.CancelledError:
            # Timeout was cancelled (transaction completed)
            pass
    
    async def _cleanup_transaction(self, transaction_id: str):
        """Cleanup completed transaction"""
        if transaction_id in self.active_transactions:
            transaction = self.active_transactions[transaction_id]
            
            # Move to completed transactions
            self.completed_transactions.append(transaction)
            del self.active_transactions[transaction_id]
            
            # Cancel timeout task
            if transaction_id in self.timeout_tasks:
                self.timeout_tasks[transaction_id].cancel()
                del self.timeout_tasks[transaction_id]
            
            # Keep only recent completed transactions
            if len(self.completed_transactions) > 1000:
                self.completed_transactions = self.completed_transactions[-1000:]
    
    async def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction status"""
        # Check active transactions
        if transaction_id in self.active_transactions:
            transaction = self.active_transactions[transaction_id]
        else:
            # Check completed transactions
            transaction = next(
                (t for t in self.completed_transactions if t.transaction_id == transaction_id),
                None
            )
        
        if not transaction:
            return None
        
        return {
            "transaction_id": transaction.transaction_id,
            "saga_id": transaction.saga_id,
            "status": transaction.status.value,
            "started_at": transaction.started_at.isoformat(),
            "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None,
            "participants": [
                {
                    "participant_id": p.participant_id,
                    "service_name": p.service_name,
                    "status": p.status.value,
                    "prepare_timestamp": p.prepare_timestamp.isoformat() if p.prepare_timestamp else None,
                    "commit_timestamp": p.commit_timestamp.isoformat() if p.commit_timestamp else None
                }
                for p in transaction.participants
            ],
            "error_message": transaction.error_message
        }
    
    async def list_active_transactions(self) -> List[Dict[str, Any]]:
        """List all active transactions"""
        return [
            {
                "transaction_id": t.transaction_id,
                "saga_id": t.saga_id,
                "status": t.status.value,
                "participant_count": len(t.participants),
                "started_at": t.started_at.isoformat()
            }
            for t in self.active_transactions.values()
        ]
    
    async def abort_transaction(self, transaction_id: str) -> bool:
        """Manually abort transaction"""
        if transaction_id not in self.active_transactions:
            return False
        
        transaction = self.active_transactions[transaction_id]
        
        if transaction.status in [TransactionStatus.COMMITTED, TransactionStatus.ABORTED]:
            return False
        
        transaction.status = TransactionStatus.ABORTING
        await self._abort_phase(transaction)
        transaction.status = TransactionStatus.ABORTED
        transaction.error_message = "Manually aborted"
        
        await self._cleanup_transaction(transaction_id)
        
        logger.info(f"Transaction {transaction_id} manually aborted")
        return True
    
    async def get_coordination_stats(self) -> Dict[str, Any]:
        """Get coordination service statistics"""
        total_transactions = len(self.active_transactions) + len(self.completed_transactions)
        committed_count = len([t for t in self.completed_transactions 
                             if t.status == TransactionStatus.COMMITTED])
        aborted_count = len([t for t in self.completed_transactions 
                           if t.status == TransactionStatus.ABORTED])
        
        return {
            "coordinator_id": self.coordinator_id,
            "active_transactions": len(self.active_transactions),
            "total_transactions": total_transactions,
            "committed_transactions": committed_count,
            "aborted_transactions": aborted_count,
            "success_rate": committed_count / max(committed_count + aborted_count, 1),
            "average_transaction_time": self._calculate_average_transaction_time()
        }
    
    def _calculate_average_transaction_time(self) -> float:
        """Calculate average transaction completion time"""
        completed_with_times = [
            t for t in self.completed_transactions 
            if t.completed_at and t.started_at
        ]
        
        if not completed_with_times:
            return 0.0
        
        total_time = sum(
            (t.completed_at - t.started_at).total_seconds()
            for t in completed_with_times
        )
        
        return total_time / len(completed_with_times)


class DistributedLockManager:
    """Manager for distributed locks"""
    
    def __init__(self):
        self.locks: Dict[str, Dict[str, Any]] = {}
        self.lock_timeouts: Dict[str, asyncio.Task] = {}
    
    async def acquire_lock(
        self,
        resource_id: str,
        owner_id: str,
        timeout_seconds: int = 300
    ) -> bool:
        """Acquire distributed lock"""
        if resource_id in self.locks:
            current_owner = self.locks[resource_id]["owner_id"]
            if current_owner != owner_id:
                return False  # Lock already held by another owner
        
        # Acquire lock
        self.locks[resource_id] = {
            "owner_id": owner_id,
            "acquired_at": datetime.now(timezone.utc),
            "timeout_seconds": timeout_seconds
        }
        
        # Set timeout
        timeout_task = asyncio.create_task(
            self._lock_timeout(resource_id, timeout_seconds)
        )
        self.lock_timeouts[resource_id] = timeout_task
        
        logger.debug(f"Lock acquired for resource {resource_id} by {owner_id}")
        return True
    
    async def release_lock(self, resource_id: str, owner_id: str) -> bool:
        """Release distributed lock"""
        if resource_id not in self.locks:
            return False
        
        lock_info = self.locks[resource_id]
        if lock_info["owner_id"] != owner_id:
            return False  # Can only release own locks
        
        # Release lock
        del self.locks[resource_id]
        
        # Cancel timeout
        if resource_id in self.lock_timeouts:
            self.lock_timeouts[resource_id].cancel()
            del self.lock_timeouts[resource_id]
        
        logger.debug(f"Lock released for resource {resource_id} by {owner_id}")
        return True
    
    async def _lock_timeout(self, resource_id: str, timeout_seconds: int):
        """Handle lock timeout"""
        try:
            await asyncio.sleep(timeout_seconds)
            
            if resource_id in self.locks:
                owner_id = self.locks[resource_id]["owner_id"]
                logger.warning(f"Lock timeout for resource {resource_id}, owner {owner_id}")
                del self.locks[resource_id]
                
                if resource_id in self.lock_timeouts:
                    del self.lock_timeouts[resource_id]
                    
        except asyncio.CancelledError:
            # Lock was released before timeout
            pass
    
    def is_locked(self, resource_id: str) -> bool:
        """Check if resource is locked"""
        return resource_id in self.locks
    
    def get_lock_owner(self, resource_id: str) -> Optional[str]:
        """Get lock owner"""
        if resource_id in self.locks:
            return self.locks[resource_id]["owner_id"]
        return None


# Global instances
_coordination_service: Optional[TransactionCoordinationService] = None
_lock_manager: Optional[DistributedLockManager] = None


def get_transaction_coordination_service() -> TransactionCoordinationService:
    """Get global transaction coordination service"""
    global _coordination_service
    if _coordination_service is None:
        _coordination_service = TransactionCoordinationService()
    
    return _coordination_service


def get_distributed_lock_manager() -> DistributedLockManager:
    """Get global distributed lock manager"""
    global _lock_manager
    if _lock_manager is None:
        _lock_manager = DistributedLockManager()
    
    return _lock_manager


async def begin_transaction(
    saga_id: str,
    participants: List[Dict[str, str]],
    timeout_seconds: int = 300
) -> str:
    """Convenience function to begin transaction"""
    service = get_transaction_coordination_service()
    return await service.begin_distributed_transaction(saga_id, participants, timeout_seconds)


async def commit_transaction(transaction_id: str) -> bool:
    """Convenience function to commit transaction"""
    service = get_transaction_coordination_service()
    return await service.execute_two_phase_commit(transaction_id)


__all__ = [
    "TransactionCoordinationService",
    "DistributedLockManager",
    "DistributedTransaction",
    "TransactionParticipant",
    "TransactionStatus",
    "ParticipantStatus",
    "get_transaction_coordination_service",
    "get_distributed_lock_manager",
    "begin_transaction",
    "commit_transaction"
]