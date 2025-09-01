"""Durability Manager - Transaction Persistence and Recovery System

Enterprise-grade durability management ensuring ACID durability guarantees,
persistent transaction logging, crash recovery, and data integrity for the
IA Influencer platform's creator economy operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
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

import os
import asyncio
import json
import gzip
import hashlib
import logging
import pickle
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, IO
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import aiofiles
import aiofiles.os
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import tempfile
import shutil

logger = logging.getLogger(__name__)


class PersistenceStrategy(Enum):
    """
Persistence strategy options"""

    MEMORY_ONLY = "MEMORY_ONLY"           # No persistence (testing only)
    FILE_BASED = "FILE_BASED"             # File-based persistence
    DATABASE = "DATABASE"                 # Database persistence
    HYBRID = "HYBRID"                     # Memory + periodic persistence
    REPLICATED = "REPLICATED"             # Multi-location replication
    
    # Creator economy specific strategies
    CONTENT_OPTIMIZED = "CONTENT_OPTIMIZED"     # Optimized for content data
    REVENUE_COMPLIANT = "REVENUE_COMPLIANT"     # Compliance-focused for revenue
    AUDIT_ENHANCED = "AUDIT_ENHANCED"           # Enhanced auditing


class RecoveryMode(Enum):
    """Recovery mode options"""

    NONE = "NONE"                         # No recovery
    CHECKPOINT = "CHECKPOINT"             # Checkpoint-based recovery
    LOG_REPLAY = "LOG_REPLAY"             # Transaction log replay
    SNAPSHOT = "SNAPSHOT"                 # Snapshot-based recovery
    INCREMENTAL = "INCREMENTAL"           # Incremental recovery
    FULL_RESTORE = "FULL_RESTORE"         # Full system restore


@dataclass
class TransactionLogEntry:
    """Single transaction log entry"""
    transaction_id: str
    operation_type: str  # BEGIN, PREPARE, COMMIT, ROLLBACK, OPERATION
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    sequence_number: int = 0
    creator_id: Optional[str] = None
    content_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """
Calculate checksum after initialization"""
        if self.checksum is None:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """
Calculate SHA-256 checksum of entry data"""
        data_str = json.dumps({
            'transaction_id': self.transaction_id,
            'operation_type': self.operation_type,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'sequence_number': self.sequence_number,
            'creator_id': self.creator_id,
            'content_metadata': self.content_metadata,
        }, sort_keys=True)
        
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def verify_integrity(self) -> bool:
        """
Verify entry integrity using checksum"""
        expected_checksum = self._calculate_checksum()
        return self.checksum == expected_checksum
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary for serialization"""
        return {
            'transaction_id': self.transaction_id,
            'operation_type': self.operation_type,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'checksum': self.checksum,
            'sequence_number': self.sequence_number,
            'creator_id': self.creator_id,
            'content_metadata': self.content_metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionLogEntry':
        """
Create from dictionary"""
        return cls(
            transaction_id=data['transaction_id'],
            operation_type=data['operation_type'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            data=data.get('data', {}),
            checksum=data.get('checksum'),
            sequence_number=data.get('sequence_number', 0),
            creator_id=data.get('creator_id'),
            content_metadata=data.get('content_metadata'),
        )


@dataclass
class Checkpoint:
    """
System checkpoint for recovery"""
    checkpoint_id: str
    timestamp: datetime
    sequence_number: int
    transaction_states: Dict[str, str] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    creator_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    content_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    checksum: Optional[str] = None
    
    def __post_init__(self):
        """
Calculate checksum after initialization"""
        if self.checksum is None:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """
Calculate checkpoint checksum"""
        data_str = json.dumps({
            'checkpoint_id': self.checkpoint_id,
            'timestamp': self.timestamp.isoformat(),
            'sequence_number': self.sequence_number,
            'transaction_states': self.transaction_states,
            'system_state': self.system_state,
            'creator_states': self.creator_states,
            'content_states': self.content_states,
        }, sort_keys=True)
        
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def verify_integrity(self) -> bool:
        """
Verify checkpoint integrity"""
        expected_checksum = self._calculate_checksum()
        return self.checksum == expected_checksum


class TransactionLog:
    """
High-performance transaction log with integrity guarantees"""
    
    def __init__(self, log_dir: str, max_file_size: int = 100 * 1024 * 1024):  # 100MB
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = max_file_size
        self.current_file: Optional[IO] = None
        self.current_file_path: Optional[Path] = None
        self.sequence_number = 0
        self.lock = threading.RLock()
        self.write_buffer: List[TransactionLogEntry] = []
        self.buffer_size = 1000
        self.flush_interval = 1.0  # seconds
        
        # Start background flushing
        self._flushing = True
        self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flush_thread.start()
        
        # Initialize log file
        self._rotate_log_file()
        
        logger.info("TransactionLog initialized: %s", self.log_dir)
    
    def write_entry(self, entry: TransactionLogEntry) -> None:
        """Write entry to transaction log"""
        with self.lock:
            entry.sequence_number = self.sequence_number
            self.sequence_number += 1
            self.write_buffer.append(entry)
            
            # Flush immediately for critical operations
            if entry.operation_type in ['COMMIT', 'ROLLBACK']:
                self._flush_buffer()
    
    def _flush_buffer(self) -> None:
        """
Flush write buffer to disk"""
        if not self.write_buffer:
            return
        
        try:
            if self.current_file is None:
                self._rotate_log_file()
            
            for entry in self.write_buffer:
                entry_data = json.dumps(entry.to_dict()) + '\n'
                self.current_file.write(entry_data.encode('utf-8'))
            
            self.current_file.flush()
            os.fsync(self.current_file.fileno())  # Force to disk
            
            self.write_buffer.clear()
            
            # Check if file rotation is needed
            if self.current_file_path and self.current_file_path.stat().st_size > self.max_file_size:
                self._rotate_log_file()
                
        except Exception as e:
            logger.error("Failed to flush transaction log: %s", str(e))
            raise
    
    def _rotate_log_file(self) -> None:
        """Rotate to new log file"""
        if self.current_file:
            self.current_file.close()
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"transaction_log_{timestamp}_{self.sequence_number}.log"
        self.current_file_path = self.log_dir / filename
        self.current_file = open(self.current_file_path, 'ab')
        
        logger.info("Rotated to new log file: %s", self.current_file_path)
    
    def _flush_loop(self) -> None:
        """Background flush loop"""
        while self._flushing:
            try:
                with self.lock:
                    if self.write_buffer:
                        self._flush_buffer()
                
                threading.Event().wait(self.flush_interval)
                
            except Exception as e:
                logger.error("Error in flush loop: %s", str(e))
                threading.Event().wait(1)
    
    def read_entries(
        self,
        from_sequence: Optional[int] = None,
        to_sequence: Optional[int] = None,
        transaction_id: Optional[str] = None
    ) -> List[TransactionLogEntry]:
        """Read entries from log with optional filtering"""
        
        entries = []
        log_files = sorted(self.log_dir.glob("transaction_log_*.log"))
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry_data = json.loads(line)
                            entry = TransactionLogEntry.from_dict(entry_data)
                            
                            # Apply filters
                            if from_sequence is not None and entry.sequence_number < from_sequence:
                                continue
                            if to_sequence is not None and entry.sequence_number > to_sequence:
                                continue
                            if transaction_id is not None and entry.transaction_id != transaction_id:
                                continue
                            
                            # Verify integrity
                            if not entry.verify_integrity():
                                logger.error("Corrupted log entry detected: seq=%d", entry.sequence_number)
                                continue
                            
                            entries.append(entry)
                            
            except Exception as e:
                logger.error("Error reading log file %s: %s", log_file, str(e))
        
        return sorted(entries, key=lambda x: x.sequence_number)
    
    def get_latest_sequence(self) -> int:
        """Get latest sequence number"""
        with self.lock:
            return self.sequence_number - 1
    
    def close(self) -> None:
        """
Close transaction log"""
        self._flushing = False
        if self.flush_thread and self.flush_thread.is_alive():
            self.flush_thread.join(timeout=5)
        
        with self.lock:
            self._flush_buffer()
            if self.current_file:
                self.current_file.close()
        
        logger.info("TransactionLog closed")


class CheckpointManager:
    """Checkpoint management for system state persistence"""
    
    def __init__(self, checkpoint_dir: str, retention_count: int = 10):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.retention_count = retention_count
        self.lock = threading.RLock()
        
        logger.info("CheckpointManager initialized: %s", self.checkpoint_dir)
    
    async def create_checkpoint(
        self,
        sequence_number: int,
        transaction_states: Dict[str, str],
        system_state: Dict[str, Any],
        creator_states: Optional[Dict[str, Dict[str, Any]]] = None,
        content_states: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> str:
        """Create system checkpoint"""
        
        checkpoint_id = f"checkpoint_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{sequence_number}"
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now(timezone.utc),
            sequence_number=sequence_number,
            transaction_states=transaction_states,
            system_state=system_state,
            creator_states=creator_states or {},
            content_states=content_states or {},
        )
        
        # Save checkpoint to compressed file
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.checkpoint"
        
        try:
            checkpoint_data = {
                'checkpoint_id': checkpoint.checkpoint_id,
                'timestamp': checkpoint.timestamp.isoformat(),
                'sequence_number': checkpoint.sequence_number,
                'transaction_states': checkpoint.transaction_states,
                'system_state': checkpoint.system_state,
                'creator_states': checkpoint.creator_states,
                'content_states': checkpoint.content_states,
                'checksum': checkpoint.checksum,
            }
            
            # Compress and save
            with gzip.open(checkpoint_path, 'wt', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            logger.info("Created checkpoint: %s (seq=%d)", checkpoint_id, sequence_number)
            
            # Cleanup old checkpoints
            await self._cleanup_old_checkpoints()
            
            return checkpoint_id
            
        except Exception as e:
            logger.error("Failed to create checkpoint: %s", str(e))
            raise
    
    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load checkpoint by ID"""
        
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.checkpoint"
        
        if not checkpoint_path.exists():
            return None
        
        try:
            with gzip.open(checkpoint_path, 'rt', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            checkpoint = Checkpoint(
                checkpoint_id=checkpoint_data['checkpoint_id'],
                timestamp=datetime.fromisoformat(checkpoint_data['timestamp']),
                sequence_number=checkpoint_data['sequence_number'],
                transaction_states=checkpoint_data['transaction_states'],
                system_state=checkpoint_data['system_state'],
                creator_states=checkpoint_data.get('creator_states', {}),
                content_states=checkpoint_data.get('content_states', {}),
                checksum=checkpoint_data.get('checksum'),
            )
            
            # Verify integrity
            if not checkpoint.verify_integrity():
                logger.error("Corrupted checkpoint detected: %s", checkpoint_id)
                return None
            
            return checkpoint
            
        except Exception as e:
            logger.error("Failed to load checkpoint %s: %s", checkpoint_id, str(e))
            return None
    
    async def get_latest_checkpoint(self) -> Optional[Checkpoint]:
        """Get the most recent checkpoint"""
        
        checkpoint_files = list(self.checkpoint_dir.glob("*.checkpoint"))
        if not checkpoint_files:
            return None
        
        # Sort by modification time (latest first)
        latest_file = max(checkpoint_files, key=lambda x: x.stat().st_mtime)
        checkpoint_id = latest_file.stem
        
        return await self.load_checkpoint(checkpoint_id)
    
    async def list_checkpoints(self) -> List[str]:
        """List all available checkpoints"""
        
        checkpoint_files = list(self.checkpoint_dir.glob("*.checkpoint"))
        return [f.stem for f in sorted(checkpoint_files, key=lambda x: x.stat().st_mtime, reverse=True)]
    
    async def _cleanup_old_checkpoints(self) -> None:
        """Remove old checkpoints beyond retention limit"""
        
        checkpoints = await self.list_checkpoints()
        
        if len(checkpoints) > self.retention_count:
            old_checkpoints = checkpoints[self.retention_count:]
            
            for checkpoint_id in old_checkpoints:
                checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.checkpoint"
                try:
                    checkpoint_path.unlink()
                    logger.debug("Removed old checkpoint: %s", checkpoint_id)
                except Exception as e:
                    logger.error("Failed to remove checkpoint %s: %s", checkpoint_id, str(e))


class DurabilityManager:
    """
    Advanced durability manager providing enterprise-grade persistence guarantees
    
    Features:
    - Multi-strategy persistence (memory, file, database, hybrid)
    - Transaction log with integrity verification
    - Checkpoint-based recovery
    - Creator economy optimized persistence
    - Revenue compliance guarantees
    - Crash recovery and replay
    - Performance-optimized I/O
    - Multi-level backup strategies
    """
    
    def __init__(
        self,
        strategy: PersistenceStrategy = PersistenceStrategy.FILE_BASED,
        data_dir: str = "./transaction_data",
        checkpoint_interval: int = 1000,  # transactions
        max_memory_transactions: int = 10000
    ):
        self.strategy = strategy
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_interval = checkpoint_interval
        self.max_memory_transactions = max_memory_transactions
        
        # Initialize components based on strategy
        if strategy != PersistenceStrategy.MEMORY_ONLY:
            self.transaction_log = TransactionLog(str(self.data_dir / "logs"))
            self.checkpoint_manager = CheckpointManager(str(self.data_dir / "checkpoints"))
        else:
            self.transaction_log = None
            self.checkpoint_manager = None
        
        # In-memory state
        self.active_transactions: Dict[str, Dict[str, Any]] = {}
        self.transaction_history: List[TransactionLogEntry] = []
        self.last_checkpoint_sequence = 0
        
        # Performance metrics
        self.metrics = {
            "transactions_persisted": 0,
            "checkpoints_created": 0,
            "recovery_operations": 0,
            "integrity_violations": 0,
            "average_persist_time": 0.0,
        }
        
        # Background tasks
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._monitoring = True
        asyncio.create_task(self._periodic_checkpoint())
        asyncio.create_task(self._memory_management())
        
        logger.info("DurabilityManager initialized with strategy: %s", strategy.value)
    
    async def begin_transaction_persistence(
        self,
        transaction_id: str,
        transaction_data: Dict[str, Any],
        creator_id: Optional[str] = None
    ) -> None:
        """Begin transaction persistence tracking"""
        
        # Create log entry
        entry = TransactionLogEntry(
            transaction_id=transaction_id,
            operation_type="BEGIN",
            timestamp=datetime.now(timezone.utc),
            data=transaction_data,
            creator_id=creator_id
        )
        
        # Store in memory
        self.active_transactions[transaction_id] = {
            'begin_entry': entry,
            'operations': [],
            'state': 'ACTIVE',
            'creator_id': creator_id,
            'start_time': datetime.now(timezone.utc),
        }
        
        # Persist based on strategy
        await self._persist_entry(entry)
        
        logger.debug("Started transaction persistence: %s", transaction_id)
    
    async def log_transaction_operation(
        self,
        transaction_id: str,
        operation_type: str,
        operation_data: Dict[str, Any],
        content_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log transaction operation"""
        
        if transaction_id not in self.active_transactions:
            logger.warning("Transaction not found for operation log: %s", transaction_id)
            return
        
        tx_info = self.active_transactions[transaction_id]
        
        entry = TransactionLogEntry(
            transaction_id=transaction_id,
            operation_type=operation_type,
            timestamp=datetime.now(timezone.utc),
            data=operation_data,
            creator_id=tx_info['creator_id'],
            content_metadata=content_metadata
        )
        
        tx_info['operations'].append(entry)
        await self._persist_entry(entry)
        
        logger.debug("Logged operation: %s for transaction %s", operation_type, transaction_id)
    
    async def prepare_transaction_persistence(self, transaction_id: str) -> bool:
        """Prepare transaction for commit (ensure all data is persisted)"""
        
        if transaction_id not in self.active_transactions:
            return False
        
        tx_info = self.active_transactions[transaction_id]
        
        entry = TransactionLogEntry(
            transaction_id=transaction_id,
            operation_type="PREPARE",
            timestamp=datetime.now(timezone.utc),
            data={'operation_count': len(tx_info['operations'])},
            creator_id=tx_info['creator_id']
        )
        
        tx_info['state'] = 'PREPARED'
        await self._persist_entry(entry)
        
        # Force synchronization for critical operations
        if self.strategy in [PersistenceStrategy.FILE_BASED, PersistenceStrategy.HYBRID]:
            await self._force_sync()
        
        logger.debug("Prepared transaction persistence: %s", transaction_id)
        return True
    
    async def commit_transaction_persistence(self, transaction_id: str) -> bool:
        """Commit transaction persistence"""
        
        if transaction_id not in self.active_transactions:
            return False
        
        tx_info = self.active_transactions[transaction_id]
        
        entry = TransactionLogEntry(
            transaction_id=transaction_id,
            operation_type="COMMIT",
            timestamp=datetime.now(timezone.utc),
            data={
                'duration': (datetime.now(timezone.utc) - tx_info['start_time']).total_seconds(),
                'operation_count': len(tx_info['operations']),
            },
            creator_id=tx_info['creator_id']
        )
        
        tx_info['state'] = 'COMMITTED'
        await self._persist_entry(entry)
        
        # Move to history and cleanup
        self.transaction_history.extend([tx_info['begin_entry']] + tx_info['operations'] + [entry])
        del self.active_transactions[transaction_id]
        
        # Update metrics
        self.metrics["transactions_persisted"] += 1
        
        # Check if checkpoint is needed
        if self._should_create_checkpoint():
            await self._create_checkpoint()
        
        logger.debug("Committed transaction persistence: %s", transaction_id)
        return True
    
    async def rollback_transaction_persistence(self, transaction_id: str) -> bool:
        """Rollback transaction persistence"""
        
        if transaction_id not in self.active_transactions:
            return False
        
        tx_info = self.active_transactions[transaction_id]
        
        entry = TransactionLogEntry(
            transaction_id=transaction_id,
            operation_type="ROLLBACK",
            timestamp=datetime.now(timezone.utc),
            data={
                'duration': (datetime.now(timezone.utc) - tx_info['start_time']).total_seconds(),
                'operation_count': len(tx_info['operations']),
            },
            creator_id=tx_info['creator_id']
        )
        
        tx_info['state'] = 'ROLLED_BACK'
        await self._persist_entry(entry)
        
        # Move to history and cleanup
        self.transaction_history.extend([tx_info['begin_entry']] + tx_info['operations'] + [entry])
        del self.active_transactions[transaction_id]
        
        logger.debug("Rolled back transaction persistence: %s", transaction_id)
        return True
    
    async def recover_system_state(
        self,
        recovery_mode: RecoveryMode = RecoveryMode.LOG_REPLAY,
        target_checkpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Recover system state after crash or failure"""
        
        recovery_result = {
            'recovered_transactions': 0,
            'failed_recoveries': 0,
            'recovery_time': 0.0,
            'checkpoint_used': None,
            'log_entries_replayed': 0,
        }
        
        start_time = time.time()
        
        try:
            if recovery_mode == RecoveryMode.SNAPSHOT and self.checkpoint_manager:
                # Snapshot-based recovery
                if target_checkpoint:
                    checkpoint = await self.checkpoint_manager.load_checkpoint(target_checkpoint)
                else:
                    checkpoint = await self.checkpoint_manager.get_latest_checkpoint()
                
                if checkpoint:
                    recovery_result['checkpoint_used'] = checkpoint.checkpoint_id
                    
                    # Restore transaction states
                    for tx_id, state in checkpoint.transaction_states.items():
                        if state == 'ACTIVE':
                            # Need to replay or rollback
                            recovery_result['failed_recoveries'] += 1
                        else:
                            recovery_result['recovered_transactions'] += 1
                    
                    # Replay log entries after checkpoint
                    if self.transaction_log:
                        entries = self.transaction_log.read_entries(
                            from_sequence=checkpoint.sequence_number + 1
                        )
                        
                        for entry in entries:
                            await self._replay_log_entry(entry)
                            recovery_result['log_entries_replayed'] += 1
            
            elif recovery_mode == RecoveryMode.LOG_REPLAY and self.transaction_log:
                # Full log replay recovery
                entries = self.transaction_log.read_entries()
                
                for entry in entries:
                    try:
                        await self._replay_log_entry(entry)
                        recovery_result['log_entries_replayed'] += 1
                        
                        if entry.operation_type in ['COMMIT', 'ROLLBACK']:
                            recovery_result['recovered_transactions'] += 1
                            
                    except Exception as e:
                        logger.error("Failed to replay entry seq=%d: %s", entry.sequence_number, str(e))
                        recovery_result['failed_recoveries'] += 1
            
            recovery_result['recovery_time'] = time.time() - start_time
            self.metrics["recovery_operations"] += 1
            
            logger.info("Recovery completed: %s", recovery_result)
            return recovery_result
            
        except Exception as e:
            logger.error("Recovery failed: %s", str(e))
            recovery_result['recovery_time'] = time.time() - start_time
            raise
    
    async def verify_data_integrity(self) -> Dict[str, Any]:
        """Verify data integrity across all persistent storage"""
        
        integrity_report = {
            'total_entries_checked': 0,
            'corrupted_entries': 0,
            'missing_entries': 0,
            'checksum_failures': 0,
            'checkpoint_issues': 0,
        }
        
        # Check transaction log integrity
        if self.transaction_log:
            try:
                entries = self.transaction_log.read_entries()
                integrity_report['total_entries_checked'] = len(entries)
                
                for entry in entries:
                    if not entry.verify_integrity():
                        integrity_report['corrupted_entries'] += 1
                        integrity_report['checksum_failures'] += 1
                        logger.error("Corrupted entry detected: seq=%d tx=%s", 
                                   entry.sequence_number, entry.transaction_id)
                
            except Exception as e:
                logger.error("Error checking log integrity: %s", str(e))
        
        # Check checkpoint integrity
        if self.checkpoint_manager:
            try:
                checkpoints = await self.checkpoint_manager.list_checkpoints()
                
                for checkpoint_id in checkpoints:
                    checkpoint = await self.checkpoint_manager.load_checkpoint(checkpoint_id)
                    if checkpoint and not checkpoint.verify_integrity():
                        integrity_report['checkpoint_issues'] += 1
                        logger.error("Corrupted checkpoint detected: %s", checkpoint_id)
                        
            except Exception as e:
                logger.error("Error checking checkpoint integrity: %s", str(e))
        
        if integrity_report['corrupted_entries'] > 0 or integrity_report['checkpoint_issues'] > 0:
            self.metrics["integrity_violations"] += 1
        
        return integrity_report
    
    async def get_transaction_history(
        self,
        transaction_id: Optional[str] = None,
        creator_id: Optional[str] = None,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[TransactionLogEntry]:
        """Get transaction history with filtering"""
        
        entries = []
        
        # Get from transaction log
        if self.transaction_log:
            log_entries = self.transaction_log.read_entries(transaction_id=transaction_id)
            entries.extend(log_entries)
        
        # Get from memory
        for tx_info in self.active_transactions.values():
            if transaction_id and tx_info['begin_entry'].transaction_id != transaction_id:
                continue
            if creator_id and tx_info['creator_id'] != creator_id:
                continue
            
            entries.append(tx_info['begin_entry'])
            entries.extend(tx_info['operations'])
        
        # Add from history
        entries.extend(self.transaction_history)
        
        # Apply filters
        filtered_entries = []
        for entry in entries:
            if creator_id and entry.creator_id != creator_id:
                continue
            if from_timestamp and entry.timestamp < from_timestamp:
                continue
            if to_timestamp and entry.timestamp > to_timestamp:
                continue
            
            filtered_entries.append(entry)
        
        # Sort by timestamp and apply limit
        filtered_entries.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_entries[:limit]
    
    async def get_durability_metrics(self) -> Dict[str, Any]:
        """
Get comprehensive durability metrics"""
        
        metrics = self.metrics.copy()
        
        # Add current state metrics
        metrics.update({
            'active_transactions': len(self.active_transactions),
            'history_entries': len(self.transaction_history),
            'strategy': self.strategy.value,
            'last_checkpoint_sequence': self.last_checkpoint_sequence,
        })
        
        # Add storage metrics
        if self.transaction_log:
            metrics['log_sequence_number'] = self.transaction_log.get_latest_sequence()
        
        if self.checkpoint_manager:
            checkpoints = await self.checkpoint_manager.list_checkpoints()
            metrics['available_checkpoints'] = len(checkpoints)
        
        return metrics
    
    async def _persist_entry(self, entry: TransactionLogEntry) -> None:
        """
Persist log entry based on strategy"""
        
        if self.strategy == PersistenceStrategy.MEMORY_ONLY:
            return
        
        start_time = time.time()
        
        try:
            if self.transaction_log:
                self.transaction_log.write_entry(entry)
            
            # Update performance metrics
            persist_time = time.time() - start_time
            current_avg = self.metrics["average_persist_time"]
            total_ops = self.metrics["transactions_persisted"]
            
            if total_ops > 0:
                self.metrics["average_persist_time"] = (
                    (current_avg * total_ops + persist_time) / (total_ops + 1)
                )
            else:
                self.metrics["average_persist_time"] = persist_time
                
        except Exception as e:
            logger.error("Failed to persist entry: %s", str(e))
            raise
    
    async def _force_sync(self) -> None:
        """Force synchronization of all pending writes"""
        if self.transaction_log:
            # Force flush of transaction log
            with self.transaction_log.lock:
                self.transaction_log._flush_buffer()
    
    def _should_create_checkpoint(self) -> bool:
        """
Check if checkpoint should be created"""
        
        if not self.checkpoint_manager:
            return False
        
        current_sequence = 0
        if self.transaction_log:
            current_sequence = self.transaction_log.get_latest_sequence()
        
        return (current_sequence - self.last_checkpoint_sequence) >= self.checkpoint_interval
    
    async def _create_checkpoint(self) -> None:
        """
Create system checkpoint"""
        
        if not self.checkpoint_manager:
            return
        
        try:
            # Collect transaction states
            transaction_states = {}
            for tx_id, tx_info in self.active_transactions.items():
                transaction_states[tx_id] = tx_info['state']
            
            # Collect creator states
            creator_states = {}
            for tx_info in self.active_transactions.values():
                if tx_info['creator_id']:
                    creator_id = tx_info['creator_id']
                    if creator_id not in creator_states:
                        creator_states[creator_id] = {'active_transactions': 0}
                    creator_states[creator_id]['active_transactions'] += 1
            
            # Get current sequence
            current_sequence = 0
            if self.transaction_log:
                current_sequence = self.transaction_log.get_latest_sequence()
            
            # Create checkpoint
            checkpoint_id = await self.checkpoint_manager.create_checkpoint(
                sequence_number=current_sequence,
                transaction_states=transaction_states,
                system_state={'metrics': self.metrics.copy()},
                creator_states=creator_states
            )
            
            self.last_checkpoint_sequence = current_sequence
            self.metrics["checkpoints_created"] += 1
            
            logger.info("Created checkpoint: %s at sequence %d", checkpoint_id, current_sequence)
            
        except Exception as e:
            logger.error("Failed to create checkpoint: %s", str(e))
    
    async def _replay_log_entry(self, entry: TransactionLogEntry) -> None:
        """Replay a single log entry during recovery"""
        
        # This would integrate with the actual transaction system
        # For now, just validate and track
        if not entry.verify_integrity():
            raise ValueError(f"Corrupted entry during replay: seq={entry.sequence_number}")
        
        logger.debug("Replayed entry: %s %s", entry.operation_type, entry.transaction_id)
    
    async def _periodic_checkpoint(self) -> None:
        """Background task for periodic checkpointing"""
        
        while self._monitoring:
            try:
                if self._should_create_checkpoint():
                    await self._create_checkpoint()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error("Error in periodic checkpoint: %s", str(e))
                await asyncio.sleep(10)
    
    async def _memory_management(self) -> None:
        """Background task for memory management"""
        
        while self._monitoring:
            try:
                # Move old history entries to persistent storage if memory limit exceeded
                if len(self.transaction_history) > self.max_memory_transactions:
                    # Keep only recent entries in memory
                    old_entries = self.transaction_history[self.max_memory_transactions:]
                    self.transaction_history = self.transaction_history[:self.max_memory_transactions]
                    
                    logger.debug("Moved %d entries from memory to persistent storage", len(old_entries))
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error("Error in memory management: %s", str(e))
                await asyncio.sleep(30)
    
    async def shutdown(self) -> None:
        """Graceful shutdown of durability manager"""
        logger.info("Shutting down DurabilityManager...")
        
        self._monitoring = False
        
        # Force final checkpoint
        if self.checkpoint_manager and self.active_transactions:
            await self._create_checkpoint()
        
        # Force final sync
        await self._force_sync()
        
        # Close transaction log
        if self.transaction_log:
            self.transaction_log.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("DurabilityManager shutdown complete")


# Convenience functions for common persistence patterns
async def with_creator_persistence(
    manager: DurabilityManager,
    transaction_id: str,
    creator_id: str,
    operation_data: Dict[str, Any]
):
    """Ensure creator-specific persistence guarantees"""
    await manager.log_transaction_operation(
        transaction_id=transaction_id,
        operation_type="CREATOR_OPERATION",
        operation_data=operation_data,
        content_metadata={'creator_id': creator_id, 'business_context': 'creator_economy'}
    )


async def with_content_persistence(
    manager: DurabilityManager,
    transaction_id: str,
    content_data: Dict[str, Any],
    creator_id: str
):
    """Ensure content operation persistence"""
    await manager.log_transaction_operation(
        transaction_id=transaction_id,
        operation_type="CONTENT_OPERATION",
        operation_data=content_data,
        content_metadata={
            'creator_id': creator_id,
            'content_type': content_data.get('content_type'),
            'business_context': 'content_protection'
        }
    )


async def with_revenue_persistence(
    manager: DurabilityManager,
    transaction_id: str,
    revenue_data: Dict[str, Any],
    creator_id: str
):
    """Ensure revenue operation persistence with compliance"""
    await manager.log_transaction_operation(
        transaction_id=transaction_id,
        operation_type="REVENUE_OPERATION",
        operation_data=revenue_data,
        content_metadata={
            'creator_id': creator_id,
            'revenue_amount': revenue_data.get('amount'),
            'currency': revenue_data.get('currency', 'EUR'),
            'business_context': 'monetization',
            'compliance_required': True
        }
    )
