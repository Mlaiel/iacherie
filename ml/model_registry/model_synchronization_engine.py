"""⚡ Model Synchronization Engine - Enterprise ML Infrastructure
==============================================================
Module: ml/model_registry/model_synchronization_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODEL SYNCHRONIZATION & CONSISTENCY ENGINE
Enterprise model synchronization and consistency across distributed environments
- Real-time model synchronization
- Consistency verification and validation
- Conflict detection and resolution
- Performance optimization for sync operations
"""

import asyncio
import logging
import time
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class SyncMode(Enum):
    """Synchronization modes"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"
    DELTA = "delta"


class ConsistencyLevel(Enum):
    """Consistency levels"""
    STRONG = "strong"
    EVENTUAL = "eventual"
    WEAK = "weak"
    CAUSAL = "causal"


class SyncStatus(Enum):
    """Synchronization status"""
    IN_SYNC = "in_sync"
    OUT_OF_SYNC = "out_of_sync"
    SYNCING = "syncing"
    FAILED = "failed"
    CONFLICT = "conflict"
    UNKNOWN = "unknown"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    TIMESTAMP = "timestamp"
    VERSION = "version"
    PRIORITY = "priority"
    MANUAL = "manual"
    MERGE = "merge"


@dataclass
class ModelSnapshot:
    """Model snapshot for synchronization"""
    model_id: str
    version: str
    checksum: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    size: int = 0
    node_id: str = ""


@dataclass
class SyncOperation:
    """Synchronization operation"""
    operation_id: str
    model_id: str
    source_node: str
    target_nodes: List[str]
    sync_mode: SyncMode
    status: SyncStatus = SyncStatus.SYNCING
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsistencyCheck:
    """Consistency check result"""
    model_id: str
    nodes_checked: List[str]
    consistent: bool
    checksum_map: Dict[str, str]
    version_map: Dict[str, str]
    conflicts: List[Dict[str, Any]]
    check_time: datetime = field(default_factory=datetime.utcnow)


class ModelSynchronizationEngine:
    """Enterprise Model Synchronization Engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.model_snapshots: Dict[str, Dict[str, ModelSnapshot]] = {}
        self.sync_operations: Dict[str, SyncOperation] = {}
        self.consistency_checks: Dict[str, ConsistencyCheck] = {}
        
        # Configuration
        self.default_sync_mode = SyncMode(self.config.get('default_sync_mode', 'eventual'))
        self.consistency_level = ConsistencyLevel(self.config.get('consistency_level', 'eventual'))
        self.conflict_resolution = ConflictResolution(self.config.get('conflict_resolution', 'timestamp'))
        self.max_concurrent_syncs = self.config.get('max_concurrent_syncs', 5)
        self.sync_timeout = self.config.get('sync_timeout', 300)  # seconds
        
        # Synchronization state
        self.active_syncs: Set[str] = set()
        self.sync_queue: asyncio.Queue = asyncio.Queue()
        self.consistency_schedule: Dict[str, datetime] = {}
        
        # Performance tracking
        self.sync_metrics = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'conflicts_resolved': 0,
            'average_sync_time': 0.0,
            'last_sync': None
        }
        
        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("⚡ Model Synchronization Engine initialized")
    
    async def register_model_snapshot(
        self,
        model_id: str,
        node_id: str,
        version: str,
        checksum: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register a model snapshot"""
        try:
            snapshot = ModelSnapshot(
                model_id=model_id,
                version=version,
                checksum=checksum,
                timestamp=datetime.utcnow(),
                metadata=metadata or {},
                node_id=node_id
            )
            
            if model_id not in self.model_snapshots:
                self.model_snapshots[model_id] = {}
            
            self.model_snapshots[model_id][node_id] = snapshot
            
            # Schedule consistency check if needed
            await self._schedule_consistency_check(model_id)
            
            logger.info(f"✅ Model snapshot registered: {model_id}@{node_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registering snapshot: {e}")
            return False
    
    async def synchronize_model(
        self,
        model_id: str,
        source_node: str,
        target_nodes: List[str],
        sync_mode: Optional[SyncMode] = None,
        force: bool = False
    ) -> str:
        """Synchronize model across nodes"""
        try:
            operation_id = str(uuid.uuid4())
            sync_mode = sync_mode or self.default_sync_mode
            
            # Create sync operation
            operation = SyncOperation(
                operation_id=operation_id,
                model_id=model_id,
                source_node=source_node,
                target_nodes=target_nodes,
                sync_mode=sync_mode
            )
            
            self.sync_operations[operation_id] = operation
            
            # Check if sync is already in progress
            if not force and model_id in self.active_syncs:
                operation.status = SyncStatus.FAILED
                operation.error_message = "Sync already in progress"
                return operation_id
            
            # Add to active syncs
            self.active_syncs.add(model_id)
            
            # Execute synchronization based on mode
            if sync_mode == SyncMode.REAL_TIME:
                asyncio.create_task(self._sync_real_time(operation))
            elif sync_mode == SyncMode.BATCH:
                await self.sync_queue.put(operation)
                if not hasattr(self, '_batch_worker_started'):
                    asyncio.create_task(self._batch_sync_worker())
                    self._batch_worker_started = True
            else:
                asyncio.create_task(self._sync_standard(operation))
            
            logger.info(f"🔄 Sync started: {model_id} [{operation_id}]")
            return operation_id
            
        except Exception as e:
            logger.error(f"❌ Error starting sync: {e}")
            raise
    
    async def check_consistency(
        self,
        model_id: str,
        nodes: Optional[List[str]] = None
    ) -> ConsistencyCheck:
        """Check model consistency across nodes"""
        try:
            if model_id not in self.model_snapshots:
                raise ValueError(f"No snapshots found for model {model_id}")
            
            model_snapshots = self.model_snapshots[model_id]
            check_nodes = nodes or list(model_snapshots.keys())
            
            # Gather checksums and versions
            checksum_map = {}
            version_map = {}
            conflicts = []
            
            for node_id in check_nodes:
                if node_id in model_snapshots:
                    snapshot = model_snapshots[node_id]
                    checksum_map[node_id] = snapshot.checksum
                    version_map[node_id] = snapshot.version
            
            # Check for inconsistencies
            unique_checksums = set(checksum_map.values())
            unique_versions = set(version_map.values())
            
            consistent = len(unique_checksums) == 1 and len(unique_versions) == 1
            
            # Identify conflicts
            if not consistent:
                for node_id, checksum in checksum_map.items():
                    version = version_map[node_id]
                    # Find nodes with different checksum/version
                    conflicting_nodes = [
                        nid for nid, cs in checksum_map.items()
                        if cs != checksum and nid != node_id
                    ]
                    
                    if conflicting_nodes:
                        conflicts.append({
                            'node': node_id,
                            'checksum': checksum,
                            'version': version,
                            'conflicting_with': conflicting_nodes
                        })
            
            check = ConsistencyCheck(
                model_id=model_id,
                nodes_checked=check_nodes,
                consistent=consistent,
                checksum_map=checksum_map,
                version_map=version_map,
                conflicts=conflicts
            )
            
            self.consistency_checks[model_id] = check
            
            logger.info(f"🔍 Consistency check: {model_id} - {'✅ Consistent' if consistent else '❌ Inconsistent'}")
            return check
            
        except Exception as e:
            logger.error(f"❌ Error checking consistency: {e}")
            raise
    
    async def resolve_conflicts(
        self,
        model_id: str,
        resolution_strategy: Optional[ConflictResolution] = None
    ) -> bool:
        """Resolve synchronization conflicts"""
        try:
            if model_id not in self.consistency_checks:
                await self.check_consistency(model_id)
            
            check = self.consistency_checks[model_id]
            if check.consistent:
                return True  # No conflicts to resolve
            
            resolution_strategy = resolution_strategy or self.conflict_resolution
            
            # Select authoritative source based on strategy
            authoritative_node = await self._select_authoritative_node(
                model_id, resolution_strategy
            )
            
            if not authoritative_node:
                logger.error(f"No authoritative node found for {model_id}")
                return False
            
            # Get other nodes
            other_nodes = [
                node for node in check.nodes_checked
                if node != authoritative_node
            ]
            
            # Synchronize from authoritative node
            operation_id = await self.synchronize_model(
                model_id, authoritative_node, other_nodes, force=True
            )
            
            # Wait for sync completion
            success = await self._wait_for_sync_completion(operation_id)
            
            if success:
                self.sync_metrics['conflicts_resolved'] += 1
                logger.info(f"✅ Conflicts resolved for {model_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error resolving conflicts: {e}")
            return False
    
    async def get_sync_status(self, operation_id: str) -> Optional[SyncOperation]:
        """Get synchronization status"""
        return self.sync_operations.get(operation_id)
    
    async def list_active_syncs(self) -> List[SyncOperation]:
        """List active synchronization operations"""
        active_operations = []
        
        for operation in self.sync_operations.values():
            if operation.status == SyncStatus.SYNCING:
                active_operations.append(operation)
        
        return active_operations
    
    async def cancel_sync(self, operation_id: str) -> bool:
        """Cancel synchronization operation"""
        try:
            if operation_id not in self.sync_operations:
                return False
            
            operation = self.sync_operations[operation_id]
            if operation.status != SyncStatus.SYNCING:
                return False
            
            operation.status = SyncStatus.FAILED
            operation.error_message = "Cancelled by user"
            operation.completed_at = datetime.utcnow()
            
            # Remove from active syncs
            if operation.model_id in self.active_syncs:
                self.active_syncs.remove(operation.model_id)
            
            logger.info(f"🚫 Sync cancelled: {operation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cancelling sync: {e}")
            return False
    
    async def _sync_real_time(self, operation: SyncOperation):
        """Execute real-time synchronization"""
        try:
            start_time = time.time()
            
            # Get source snapshot
            source_snapshot = self._get_snapshot(operation.model_id, operation.source_node)
            if not source_snapshot:
                raise ValueError(f"Source snapshot not found: {operation.source_node}")
            
            # Sync to each target
            failed_targets = []
            
            for target_node in operation.target_nodes:
                try:
                    # Check if target needs update
                    target_snapshot = self._get_snapshot(operation.model_id, target_node)
                    
                    if (target_snapshot and 
                        target_snapshot.checksum == source_snapshot.checksum):
                        continue  # Already in sync
                    
                    # Perform sync
                    success = await self._transfer_model(
                        operation.model_id,
                        operation.source_node,
                        target_node
                    )
                    
                    if not success:
                        failed_targets.append(target_node)
                
                except Exception as e:
                    logger.error(f"Error syncing to {target_node}: {e}")
                    failed_targets.append(target_node)
            
            # Update operation status
            if failed_targets:
                operation.status = SyncStatus.FAILED
                operation.error_message = f"Failed targets: {failed_targets}"
            else:
                operation.status = SyncStatus.IN_SYNC
            
            operation.completed_at = datetime.utcnow()
            
            # Update metrics
            sync_time = time.time() - start_time
            await self._update_sync_metrics(sync_time, operation.status == SyncStatus.IN_SYNC)
            
        except Exception as e:
            operation.status = SyncStatus.FAILED
            operation.error_message = str(e)
            operation.completed_at = datetime.utcnow()
            logger.error(f"❌ Real-time sync failed: {e}")
        
        finally:
            # Remove from active syncs
            if operation.model_id in self.active_syncs:
                self.active_syncs.remove(operation.model_id)
    
    async def _sync_standard(self, operation: SyncOperation):
        """Execute standard synchronization"""
        try:
            start_time = time.time()
            
            # Perform consistency check first
            check = await self.check_consistency(
                operation.model_id,
                [operation.source_node] + operation.target_nodes
            )
            
            if check.consistent:
                operation.status = SyncStatus.IN_SYNC
                operation.completed_at = datetime.utcnow()
                return
            
            # Sync needed - get source snapshot
            source_snapshot = self._get_snapshot(operation.model_id, operation.source_node)
            if not source_snapshot:
                raise ValueError(f"Source snapshot not found: {operation.source_node}")
            
            # Sync to targets
            failed_targets = []
            
            for target_node in operation.target_nodes:
                try:
                    success = await self._transfer_model(
                        operation.model_id,
                        operation.source_node,
                        target_node
                    )
                    
                    if not success:
                        failed_targets.append(target_node)
                        
                except Exception as e:
                    logger.error(f"Error syncing to {target_node}: {e}")
                    failed_targets.append(target_node)
            
            # Update status
            if failed_targets:
                operation.status = SyncStatus.FAILED
                operation.error_message = f"Failed targets: {failed_targets}"
            else:
                operation.status = SyncStatus.IN_SYNC
            
            operation.completed_at = datetime.utcnow()
            
            # Update metrics
            sync_time = time.time() - start_time
            await self._update_sync_metrics(sync_time, operation.status == SyncStatus.IN_SYNC)
            
        except Exception as e:
            operation.status = SyncStatus.FAILED
            operation.error_message = str(e)
            operation.completed_at = datetime.utcnow()
            logger.error(f"❌ Standard sync failed: {e}")
        
        finally:
            if operation.model_id in self.active_syncs:
                self.active_syncs.remove(operation.model_id)
    
    async def _batch_sync_worker(self):
        """Background worker for batch synchronization"""
        try:
            while True:
                try:
                    # Wait for sync operations
                    operation = await asyncio.wait_for(
                        self.sync_queue.get(), timeout=60
                    )
                    
                    # Execute sync
                    await self._sync_standard(operation)
                    
                    # Mark task done
                    self.sync_queue.task_done()
                    
                except asyncio.TimeoutError:
                    continue  # Continue waiting
                
                except Exception as e:
                    logger.error(f"❌ Batch sync worker error: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Batch sync worker failed: {e}")
    
    async def _transfer_model(
        self,
        model_id: str,
        source_node: str,
        target_node: str
    ) -> bool:
        """Transfer model from source to target node"""
        try:
            # Simulate model transfer
            # In practice, this would:
            # 1. Download model from source node
            # 2. Upload to target node
            # 3. Verify transfer integrity
            
            await asyncio.sleep(0.1)  # Simulate transfer time
            
            # Update target snapshot
            source_snapshot = self._get_snapshot(model_id, source_node)
            if source_snapshot:
                await self.register_model_snapshot(
                    model_id,
                    target_node,
                    source_snapshot.version,
                    source_snapshot.checksum,
                    source_snapshot.metadata
                )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model transfer failed: {e}")
            return False
    
    def _get_snapshot(self, model_id: str, node_id: str) -> Optional[ModelSnapshot]:
        """Get model snapshot for node"""
        if model_id in self.model_snapshots:
            return self.model_snapshots[model_id].get(node_id)
        return None
    
    async def _select_authoritative_node(
        self,
        model_id: str,
        strategy: ConflictResolution
    ) -> Optional[str]:
        """Select authoritative node for conflict resolution"""
        try:
            if model_id not in self.model_snapshots:
                return None
            
            snapshots = self.model_snapshots[model_id]
            
            if strategy == ConflictResolution.TIMESTAMP:
                # Choose node with latest timestamp
                latest_node = None
                latest_time = None
                
                for node_id, snapshot in snapshots.items():
                    if latest_time is None or snapshot.timestamp > latest_time:
                        latest_time = snapshot.timestamp
                        latest_node = node_id
                
                return latest_node
            
            elif strategy == ConflictResolution.VERSION:
                # Choose node with highest version
                highest_node = None
                highest_version = None
                
                for node_id, snapshot in snapshots.items():
                    if highest_version is None or snapshot.version > highest_version:
                        highest_version = snapshot.version
                        highest_node = node_id
                
                return highest_node
            
            elif strategy == ConflictResolution.PRIORITY:
                # Choose node with highest priority (from metadata)
                highest_priority_node = None
                highest_priority = -1
                
                for node_id, snapshot in snapshots.items():
                    priority = snapshot.metadata.get('priority', 0)
                    if priority > highest_priority:
                        highest_priority = priority
                        highest_priority_node = node_id
                
                return highest_priority_node
            
            else:
                # Default to first available node
                return next(iter(snapshots.keys())) if snapshots else None
                
        except Exception as e:
            logger.error(f"❌ Error selecting authoritative node: {e}")
            return None
    
    async def _schedule_consistency_check(self, model_id: str):
        """Schedule periodic consistency check"""
        try:
            check_interval = self.config.get('consistency_check_interval', 3600)  # 1 hour
            next_check = datetime.utcnow() + timedelta(seconds=check_interval)
            
            self.consistency_schedule[model_id] = next_check
            
            # Start background check task if not already running
            if not hasattr(self, '_consistency_checker_started'):
                asyncio.create_task(self._consistency_checker())
                self._consistency_checker_started = True
                
        except Exception as e:
            logger.error(f"❌ Error scheduling consistency check: {e}")
    
    async def _consistency_checker(self):
        """Background consistency checker"""
        try:
            while True:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.utcnow()
                
                for model_id, scheduled_time in list(self.consistency_schedule.items()):
                    if current_time >= scheduled_time:
                        try:
                            check = await self.check_consistency(model_id)
                            
                            # Auto-resolve conflicts if configured
                            if not check.consistent and self.config.get('auto_resolve_conflicts', False):
                                await self.resolve_conflicts(model_id)
                            
                            # Reschedule next check
                            await self._schedule_consistency_check(model_id)
                            
                        except Exception as e:
                            logger.error(f"Error in scheduled consistency check for {model_id}: {e}")
                            
        except Exception as e:
            logger.error(f"❌ Consistency checker failed: {e}")
    
    async def _wait_for_sync_completion(
        self,
        operation_id: str,
        timeout: int = 300
    ) -> bool:
        """Wait for sync operation completion"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                operation = self.sync_operations.get(operation_id)
                if not operation:
                    return False
                
                if operation.status in [SyncStatus.IN_SYNC, SyncStatus.FAILED]:
                    return operation.status == SyncStatus.IN_SYNC
                
                await asyncio.sleep(1)
            
            return False  # Timeout
            
        except Exception as e:
            logger.error(f"❌ Error waiting for sync completion: {e}")
            return False
    
    async def _update_sync_metrics(self, sync_time: float, success: bool):
        """Update synchronization metrics"""
        try:
            self.sync_metrics['total_syncs'] += 1
            
            if success:
                self.sync_metrics['successful_syncs'] += 1
            else:
                self.sync_metrics['failed_syncs'] += 1
            
            # Update average sync time
            total_time = (self.sync_metrics['average_sync_time'] * 
                         (self.sync_metrics['total_syncs'] - 1) + sync_time)
            self.sync_metrics['average_sync_time'] = total_time / self.sync_metrics['total_syncs']
            
            self.sync_metrics['last_sync'] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"❌ Error updating sync metrics: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get synchronization metrics"""
        return {
            **self.sync_metrics,
            'active_syncs': len(self.active_syncs),
            'total_models': len(self.model_snapshots),
            'pending_consistency_checks': len(self.consistency_schedule)
        }


# Global instance
sync_engine = ModelSynchronizationEngine()


async def main():
    """Test the Model Synchronization Engine"""
    engine = ModelSynchronizationEngine()
    
    print("⚡ Testing Model Synchronization Engine...")
    
    # Register snapshots
    await engine.register_model_snapshot(
        "model_a", "node_1", "1.0.0", "abc123", {"priority": 1}
    )
    await engine.register_model_snapshot(
        "model_a", "node_2", "1.0.1", "def456", {"priority": 2}
    )
    
    # Check consistency
    check = await engine.check_consistency("model_a")
    print(f"Consistency check: {check.consistent}")
    print(f"Conflicts: {len(check.conflicts)}")
    
    # Resolve conflicts
    if not check.consistent:
        success = await engine.resolve_conflicts("model_a")
        print(f"Conflict resolution: {'✅ Success' if success else '❌ Failed'}")
    
    # Get metrics
    metrics = await engine.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())