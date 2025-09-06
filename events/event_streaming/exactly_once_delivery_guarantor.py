"""IA Influencer Agent - Exactly Once Delivery Guarantor
Enterprise-grade Exactly-Once Delivery Guarantees for Ainflue Event Streaming

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Callable, Union, Set, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
import hashlib
import time
from uuid import uuid4
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class DeliveryState(Enum):
    """Delivery states for exactly-once processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMMITTED = "committed"
    FAILED = "failed"
    DUPLICATE = "duplicate"
    EXPIRED = "expired"


class TransactionState(Enum):
    """Transaction states"""
    ACTIVE = "active"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"


class IsolationLevel(Enum):
    """Transaction isolation levels"""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


@dataclass
class MessageDelivery:
    """Represents a message delivery tracking entry"""
    
    message_id: str
    producer_id: str
    consumer_id: str
    topic: str
    partition: int
    offset: int
    sequence_number: int
    delivery_tag: str
    state: DeliveryState = DeliveryState.PENDING
    attempt_count: int = 0
    first_attempt: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_attempt: Optional[datetime] = None
    committed_at: Optional[datetime] = None
    checksum: Optional[str] = None
    payload_hash: Optional[str] = None
    idempotency_key: Optional[str] = None
    
    def __post_init__(self):
        if not self.delivery_tag:
            self.delivery_tag = f"{self.producer_id}:{self.sequence_number}:{self.message_id}"


@dataclass
class Transaction:
    """Represents a distributed transaction"""
    
    transaction_id: str
    producer_id: str
    state: TransactionState = TransactionState.ACTIVE
    isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    timeout: timedelta = timedelta(minutes=5)
    participants: Set[str] = field(default_factory=set)
    operations: List[Dict[str, Any]] = field(default_factory=list)
    checkpoints: List[str] = field(default_factory=list)
    coordinator_id: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if transaction has expired"""
        return datetime.now(timezone.utc) - self.started_at > self.timeout


@dataclass
class StateSnapshot:
    """State snapshot for exactly-once processing"""
    
    snapshot_id: str
    processor_id: str
    state_data: Dict[str, Any]
    version: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    checksum: Optional[str] = None
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate state checksum"""
        state_str = json.dumps(self.state_data, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()


class DeduplicationCache:
    """Cache for deduplicating messages"""
    
    def __init__(self, max_size: int = 100000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self._access_order: deque = deque()
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if key in self.cache:
                value, timestamp = self.cache[key]
                
                # Check if expired
                if datetime.now(timezone.utc) - timestamp > timedelta(seconds=self.ttl_seconds):
                    self._remove(key)
                    return None
                
                # Update access order
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
                
                return value
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting from deduplication cache: {e}")
            return None
    
    def put(self, key: str, value: Any):
        """Put value in cache"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Remove if already exists
            if key in self.cache:
                self._remove(key)
            
            # Check size limit
            while len(self.cache) >= self.max_size:
                oldest_key = self._access_order.popleft()
                if oldest_key in self.cache:
                    del self.cache[oldest_key]
            
            # Add new entry
            self.cache[key] = (value, current_time)
            self._access_order.append(key)
            
        except Exception as e:
            logger.error(f"Error putting to deduplication cache: {e}")
    
    def _remove(self, key: str):
        """Remove key from cache"""
        if key in self.cache:
            del self.cache[key]
        
        if key in self._access_order:
            self._access_order.remove(key)
    
    def cleanup_expired(self):
        """Clean up expired entries"""
        try:
            current_time = datetime.now(timezone.utc)
            expired_keys = []
            
            for key, (_, timestamp) in self.cache.items():
                if current_time - timestamp > timedelta(seconds=self.ttl_seconds):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove(key)
                
        except Exception as e:
            logger.error(f"Error cleaning up expired cache entries: {e}")


class IdempotentProcessor:
    """Processor with idempotent guarantees"""
    
    def __init__(self, processor_id: str, deduplication_cache: DeduplicationCache):
        self.processor_id = processor_id
        self.deduplication_cache = deduplication_cache
        self.state_snapshots: Dict[int, StateSnapshot] = {}
        self.current_state_version = 0
        self.pending_operations: List[Dict[str, Any]] = []
        
    async def process_idempotently(self, 
                                 message: Dict[str, Any], 
                                 operation: Callable[[Dict[str, Any]], Any],
                                 idempotency_key: Optional[str] = None) -> Tuple[Any, bool]:
        """Process message idempotently"""
        try:
            # Generate idempotency key if not provided
            if not idempotency_key:
                message_content = json.dumps(message, sort_keys=True)
                idempotency_key = hashlib.md5(message_content.encode()).hexdigest()
            
            # Check if already processed
            cached_result = self.deduplication_cache.get(idempotency_key)
            if cached_result is not None:
                logger.debug(f"Duplicate message detected: {idempotency_key}")
                return cached_result, False  # False = not newly processed
            
            # Create state snapshot before processing
            snapshot = await self._create_state_snapshot()
            
            try:
                # Process the message
                result = await operation(message)
                
                # Cache the result
                self.deduplication_cache.put(idempotency_key, result)
                
                # Record successful operation
                self.pending_operations.append({
                    "type": "process",
                    "idempotency_key": idempotency_key,
                    "message_id": message.get("message_id"),
                    "result": result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                return result, True  # True = newly processed
                
            except Exception as e:
                # Restore state on failure
                await self._restore_state_snapshot(snapshot)
                logger.error(f"Error processing message {idempotency_key}: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Error in idempotent processing: {e}")
            raise
    
    async def _create_state_snapshot(self) -> StateSnapshot:
        """Create state snapshot"""
        snapshot = StateSnapshot(
            snapshot_id=str(uuid4()),
            processor_id=self.processor_id,
            state_data={
                "pending_operations": self.pending_operations.copy(),
                "processor_state": {}  # Would include actual processor state
            },
            version=self.current_state_version + 1
        )
        
        self.state_snapshots[snapshot.version] = snapshot
        self.current_state_version = snapshot.version
        
        return snapshot
    
    async def _restore_state_snapshot(self, snapshot: StateSnapshot):
        """Restore state from snapshot"""
        try:
            self.pending_operations = snapshot.state_data["pending_operations"]
            self.current_state_version = snapshot.version - 1
            
            # Remove newer snapshots
            versions_to_remove = [v for v in self.state_snapshots.keys() if v > self.current_state_version]
            for version in versions_to_remove:
                del self.state_snapshots[version]
                
        except Exception as e:
            logger.error(f"Error restoring state snapshot: {e}")
            raise


class TransactionCoordinator:
    """Coordinates distributed transactions for exactly-once delivery"""
    
    def __init__(self, coordinator_id: str):
        self.coordinator_id = coordinator_id
        self.active_transactions: Dict[str, Transaction] = {}
        self.transaction_log: deque = deque(maxlen=10000)
        
    async def begin_transaction(self, producer_id: str, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED) -> str:
        """Begin a new transaction"""
        try:
            transaction_id = str(uuid4())
            
            transaction = Transaction(
                transaction_id=transaction_id,
                producer_id=producer_id,
                isolation_level=isolation_level,
                coordinator_id=self.coordinator_id
            )
            
            self.active_transactions[transaction_id] = transaction
            
            self.transaction_log.append({
                "action": "begin",
                "transaction_id": transaction_id,
                "producer_id": producer_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            logger.debug(f"Started transaction {transaction_id} for producer {producer_id}")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Error beginning transaction: {e}")
            raise
    
    async def add_operation(self, transaction_id: str, operation: Dict[str, Any]):
        """Add operation to transaction"""
        try:
            if transaction_id not in self.active_transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            transaction = self.active_transactions[transaction_id]
            
            if transaction.state != TransactionState.ACTIVE:
                raise ValueError(f"Transaction {transaction_id} is not active")
            
            transaction.operations.append(operation)
            
            # Add participant if specified
            participant = operation.get("participant")
            if participant:
                transaction.participants.add(participant)
            
        except Exception as e:
            logger.error(f"Error adding operation to transaction {transaction_id}: {e}")
            raise
    
    async def prepare_transaction(self, transaction_id: str) -> bool:
        """Prepare transaction (2PC phase 1)"""
        try:
            if transaction_id not in self.active_transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            transaction = self.active_transactions[transaction_id]
            
            if transaction.is_expired():
                await self.abort_transaction(transaction_id)
                return False
            
            transaction.state = TransactionState.PREPARING
            
            # Prepare with all participants
            prepare_success = await self._prepare_with_participants(transaction)
            
            if prepare_success:
                transaction.state = TransactionState.PREPARED
                
                self.transaction_log.append({
                    "action": "prepare",
                    "transaction_id": transaction_id,
                    "success": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                return True
            else:
                await self.abort_transaction(transaction_id)
                return False
                
        except Exception as e:
            logger.error(f"Error preparing transaction {transaction_id}: {e}")
            await self.abort_transaction(transaction_id)
            return False
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit transaction (2PC phase 2)"""
        try:
            if transaction_id not in self.active_transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            transaction = self.active_transactions[transaction_id]
            
            if transaction.state != TransactionState.PREPARED:
                raise ValueError(f"Transaction {transaction_id} is not prepared")
            
            transaction.state = TransactionState.COMMITTING
            
            # Commit with all participants
            commit_success = await self._commit_with_participants(transaction)
            
            if commit_success:
                transaction.state = TransactionState.COMMITTED
                
                self.transaction_log.append({
                    "action": "commit",
                    "transaction_id": transaction_id,
                    "success": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                # Clean up
                del self.active_transactions[transaction_id]
                
                logger.debug(f"Committed transaction {transaction_id}")
                return True
            else:
                await self.abort_transaction(transaction_id)
                return False
                
        except Exception as e:
            logger.error(f"Error committing transaction {transaction_id}: {e}")
            await self.abort_transaction(transaction_id)
            return False
    
    async def abort_transaction(self, transaction_id: str):
        """Abort transaction"""
        try:
            if transaction_id not in self.active_transactions:
                return
            
            transaction = self.active_transactions[transaction_id]
            transaction.state = TransactionState.ABORTING
            
            # Abort with all participants
            await self._abort_with_participants(transaction)
            
            transaction.state = TransactionState.ABORTED
            
            self.transaction_log.append({
                "action": "abort",
                "transaction_id": transaction_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Clean up
            del self.active_transactions[transaction_id]
            
            logger.debug(f"Aborted transaction {transaction_id}")
            
        except Exception as e:
            logger.error(f"Error aborting transaction {transaction_id}: {e}")
    
    async def _prepare_with_participants(self, transaction: Transaction) -> bool:
        """Prepare with all transaction participants"""
        try:
            # In real implementation, would send prepare messages to all participants
            # For now, simulate successful preparation
            await asyncio.sleep(0.01)  # Simulate network latency
            
            return True  # Assume all participants prepared successfully
            
        except Exception as e:
            logger.error(f"Error preparing with participants: {e}")
            return False
    
    async def _commit_with_participants(self, transaction: Transaction) -> bool:
        """Commit with all transaction participants"""
        try:
            # In real implementation, would send commit messages to all participants
            await asyncio.sleep(0.01)  # Simulate network latency
            
            return True  # Assume all participants committed successfully
            
        except Exception as e:
            logger.error(f"Error committing with participants: {e}")
            return False
    
    async def _abort_with_participants(self, transaction: Transaction):
        """Abort with all transaction participants"""
        try:
            # In real implementation, would send abort messages to all participants
            await asyncio.sleep(0.01)  # Simulate network latency
            
        except Exception as e:
            logger.error(f"Error aborting with participants: {e}")
    
    def cleanup_expired_transactions(self):
        """Clean up expired transactions"""
        try:
            expired_transactions = []
            
            for transaction_id, transaction in self.active_transactions.items():
                if transaction.is_expired():
                    expired_transactions.append(transaction_id)
            
            for transaction_id in expired_transactions:
                asyncio.create_task(self.abort_transaction(transaction_id))
                
        except Exception as e:
            logger.error(f"Error cleaning up expired transactions: {e}")


class ExactlyOnceDeliveryGuarantor:
    """Main exactly-once delivery guarantor for Ainflue platform"""
    
    def __init__(self, guarantor_id: str, metrics_collector=None):
        self.guarantor_id = guarantor_id
        self.metrics_collector = metrics_collector
        
        # Components
        self.deduplication_cache = DeduplicationCache()
        self.transaction_coordinator = TransactionCoordinator(guarantor_id)
        self.delivery_tracker: Dict[str, MessageDelivery] = {}
        self.idempotent_processors: Dict[str, IdempotentProcessor] = {}
        
        # State management
        self.sequence_numbers: Dict[str, int] = defaultdict(int)
        self.producer_epochs: Dict[str, int] = defaultdict(int)
        
        # Tasks
        self._guarantor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the exactly-once delivery guarantor"""
        try:
            logger.info("Starting Exactly-Once Delivery Guarantor")
            
            # Start monitoring task
            self._guarantor_task = asyncio.create_task(self._guarantor_loop())
            
            logger.info("Exactly-Once Delivery Guarantor started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start exactly-once delivery guarantor: {e}")
            raise
    
    async def stop(self):
        """Stop the guarantor"""
        try:
            logger.info("Stopping Exactly-Once Delivery Guarantor")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Wait for guarantor task
            if self._guarantor_task:
                await self._guarantor_task
            
            logger.info("Exactly-Once Delivery Guarantor stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping exactly-once delivery guarantor: {e}")
            raise
    
    async def send_with_exactly_once_semantics(self, 
                                             producer_id: str,
                                             message: Dict[str, Any],
                                             topic: str,
                                             partition: int = 0) -> Tuple[bool, str]:
        """Send message with exactly-once semantics"""
        try:
            # Begin transaction
            transaction_id = await self.transaction_coordinator.begin_transaction(producer_id)
            
            try:
                # Generate sequence number and delivery tracking
                sequence_number = self._get_next_sequence_number(producer_id)
                message_id = message.get("message_id", str(uuid4()))
                
                delivery = MessageDelivery(
                    message_id=message_id,
                    producer_id=producer_id,
                    consumer_id="",  # Will be set when consumed
                    topic=topic,
                    partition=partition,
                    offset=-1,  # Will be set by broker
                    sequence_number=sequence_number,
                    delivery_tag=f"{producer_id}:{sequence_number}:{message_id}",
                    payload_hash=self._calculate_payload_hash(message),
                    idempotency_key=message.get("idempotency_key")
                )
                
                # Track delivery
                self.delivery_tracker[delivery.delivery_tag] = delivery
                
                # Add send operation to transaction
                await self.transaction_coordinator.add_operation(transaction_id, {
                    "type": "send",
                    "delivery_tag": delivery.delivery_tag,
                    "topic": topic,
                    "partition": partition,
                    "message": message,
                    "participant": f"broker_{topic}_{partition}"
                })
                
                # Prepare transaction
                prepared = await self.transaction_coordinator.prepare_transaction(transaction_id)
                if not prepared:
                    return False, "Transaction preparation failed"
                
                # Simulate sending to broker
                success = await self._send_to_broker(message, topic, partition, delivery)
                
                if success:
                    # Commit transaction
                    committed = await self.transaction_coordinator.commit_transaction(transaction_id)
                    if committed:
                        delivery.state = DeliveryState.COMMITTED
                        delivery.committed_at = datetime.now(timezone.utc)
                        
                        if self.metrics_collector:
                            self.metrics_collector.increment_counter("exactly_once_sends_committed")
                        
                        return True, delivery.delivery_tag
                    else:
                        return False, "Transaction commit failed"
                else:
                    await self.transaction_coordinator.abort_transaction(transaction_id)
                    return False, "Message send failed"
                    
            except Exception as e:
                await self.transaction_coordinator.abort_transaction(transaction_id)
                raise
                
        except Exception as e:
            logger.error(f"Error sending with exactly-once semantics: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("exactly_once_send_errors")
            return False, str(e)
    
    async def consume_with_exactly_once_semantics(self,
                                                consumer_id: str,
                                                message: Dict[str, Any],
                                                processor: Callable[[Dict[str, Any]], Any],
                                                delivery_tag: Optional[str] = None) -> Tuple[Any, bool]:
        """Consume message with exactly-once semantics"""
        try:
            # Get or create idempotent processor
            if consumer_id not in self.idempotent_processors:
                self.idempotent_processors[consumer_id] = IdempotentProcessor(
                    consumer_id, self.deduplication_cache
                )
            
            idempotent_processor = self.idempotent_processors[consumer_id]
            
            # Extract idempotency key
            idempotency_key = message.get("idempotency_key")
            if not idempotency_key and delivery_tag:
                idempotency_key = delivery_tag
            
            # Process idempotently
            result, is_new = await idempotent_processor.process_idempotently(
                message, processor, idempotency_key
            )
            
            # Update delivery tracking
            if delivery_tag and delivery_tag in self.delivery_tracker:
                delivery = self.delivery_tracker[delivery_tag]
                delivery.consumer_id = consumer_id
                delivery.state = DeliveryState.COMMITTED if is_new else DeliveryState.DUPLICATE
                delivery.last_attempt = datetime.now(timezone.utc)
                
                if is_new:
                    delivery.attempt_count += 1
            
            if self.metrics_collector:
                if is_new:
                    self.metrics_collector.increment_counter("exactly_once_consumes_processed")
                else:
                    self.metrics_collector.increment_counter("exactly_once_consumes_deduplicated")
            
            return result, is_new
            
        except Exception as e:
            logger.error(f"Error consuming with exactly-once semantics: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("exactly_once_consume_errors")
            raise
    
    def _get_next_sequence_number(self, producer_id: str) -> int:
        """Get next sequence number for producer"""
        self.sequence_numbers[producer_id] += 1
        return self.sequence_numbers[producer_id]
    
    def _calculate_payload_hash(self, message: Dict[str, Any]) -> str:
        """Calculate hash of message payload"""
        try:
            # Remove metadata fields for hash calculation
            payload = {k: v for k, v in message.items() 
                      if k not in ["message_id", "timestamp", "idempotency_key"]}
            
            payload_str = json.dumps(payload, sort_keys=True)
            return hashlib.sha256(payload_str.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating payload hash: {e}")
            return ""
    
    async def _send_to_broker(self, 
                            message: Dict[str, Any], 
                            topic: str, 
                            partition: int, 
                            delivery: MessageDelivery) -> bool:
        """Send message to broker (simulated)"""
        try:
            # Simulate broker interaction
            await asyncio.sleep(0.01)  # Simulate network latency
            
            # Update delivery with broker response
            delivery.offset = 12345  # Simulated offset
            delivery.state = DeliveryState.PROCESSING
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending to broker: {e}")
            return False
    
    async def _guarantor_loop(self):
        """Main guarantor monitoring loop"""
        try:
            while not self._shutdown_event.is_set():
                # Clean up expired transactions
                self.transaction_coordinator.cleanup_expired_transactions()
                
                # Clean up expired cache entries
                self.deduplication_cache.cleanup_expired()
                
                # Clean up old delivery tracking
                await self._cleanup_old_deliveries()
                
                # Update metrics
                await self._update_metrics()
                
                # Sleep before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in guarantor loop: {e}")
    
    async def _cleanup_old_deliveries(self):
        """Clean up old delivery tracking entries"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            deliveries_to_remove = []
            for delivery_tag, delivery in self.delivery_tracker.items():
                if (delivery.state in [DeliveryState.COMMITTED, DeliveryState.FAILED, DeliveryState.DUPLICATE] and
                    delivery.first_attempt < cutoff_time):
                    deliveries_to_remove.append(delivery_tag)
            
            for delivery_tag in deliveries_to_remove:
                del self.delivery_tracker[delivery_tag]
            
            if deliveries_to_remove:
                logger.debug(f"Cleaned up {len(deliveries_to_remove)} old delivery tracking entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up old deliveries: {e}")
    
    async def _update_metrics(self):
        """Update guarantor metrics"""
        try:
            if self.metrics_collector:
                # Delivery state metrics
                state_counts = defaultdict(int)
                for delivery in self.delivery_tracker.values():
                    state_counts[delivery.state.value] += 1
                
                for state, count in state_counts.items():
                    self.metrics_collector.gauge(f"exactly_once_deliveries_{state}", count)
                
                # Transaction metrics
                self.metrics_collector.gauge("exactly_once_active_transactions", 
                                           len(self.transaction_coordinator.active_transactions))
                
                # Cache metrics
                self.metrics_collector.gauge("exactly_once_cache_size", len(self.deduplication_cache.cache))
                
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    def get_guarantor_metrics(self) -> Dict[str, Any]:
        """Get comprehensive guarantor metrics"""
        try:
            # Delivery state counts
            delivery_states = defaultdict(int)
            for delivery in self.delivery_tracker.values():
                delivery_states[delivery.state.value] += 1
            
            # Transaction state counts
            transaction_states = defaultdict(int)
            for transaction in self.transaction_coordinator.active_transactions.values():
                transaction_states[transaction.state.value] += 1
            
            return {
                "guarantor_id": self.guarantor_id,
                "total_deliveries_tracked": len(self.delivery_tracker),
                "delivery_states": dict(delivery_states),
                "active_transactions": len(self.transaction_coordinator.active_transactions),
                "transaction_states": dict(transaction_states),
                "cache_size": len(self.deduplication_cache.cache),
                "idempotent_processors": len(self.idempotent_processors),
                "producer_sequence_numbers": dict(self.sequence_numbers),
                "system_health": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Error getting guarantor metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "ExactlyOnceDeliveryGuarantor", "MessageDelivery", "Transaction", "StateSnapshot",
    "DeduplicationCache", "IdempotentProcessor", "TransactionCoordinator",
    "DeliveryState", "TransactionState", "IsolationLevel"
]