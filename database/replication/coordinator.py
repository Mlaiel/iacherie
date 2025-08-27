"""
Replication Coordinator - IA Influencer Agent Platform

Cross-database replication coordination and synchronization manager.
Orchestrates replication across PostgreSQL, Redis, MongoDB, Elasticsearch,
and Vector stores with conflict resolution and data consistency.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib


class SyncOperation(Enum):
    """Synchronization operation types"""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    BULK_SYNC = "bulk_sync"
    SCHEMA_SYNC = "schema_sync"


class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL_REVIEW = "manual_review"
    MERGE_FIELDS = "merge_fields"
    SOURCE_PRIORITY = "source_priority"


@dataclass
class SyncRecord:
    """Synchronization record"""
    id: str
    database_type: str
    table_name: str
    operation: SyncOperation
    data: Dict[str, Any]
    timestamp: datetime
    source_region: str
    target_regions: List[str]
    checksum: str
    status: str = "pending"
    retry_count: int = 0
    error_message: Optional[str] = None


@dataclass
class ConflictRecord:
    """Data conflict record"""
    id: str
    table_name: str
    record_id: str
    conflict_type: str
    source_data: Dict[str, Any]
    target_data: Dict[str, Any]
    resolution_strategy: ConflictResolutionStrategy
    timestamp: datetime
    resolved: bool = False
    resolution_data: Optional[Dict[str, Any]] = None


class ReplicationCoordinator:
    """
    Central coordinator for cross-database replication synchronization.
    
    Manages data consistency, conflict resolution, and synchronization
    across multiple database systems for the content creator platform.
    """
    
    def __init__(self, config):
        """Initialize replication coordinator"""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ReplicationCoordinator")
        
        # Database handlers registry
        self.handlers: Dict[str, Any] = {}
        
        # Synchronization state
        self.sync_queue: List[SyncRecord] = []
        self.conflict_queue: List[ConflictRecord] = []
        self.sync_history: List[SyncRecord] = []
        
        # Configuration
        self.batch_size = config.batch_size
        self.sync_interval = config.monitoring_interval
        self.conflict_strategy = ConflictResolutionStrategy(
            config.get_topology_config().get("conflict_resolution", "last_write_wins")
        )
        
        # State tracking
        self.is_coordinating = False
        self.last_sync_time: Optional[datetime] = None
        self.sync_statistics: Dict[str, int] = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0
        }
        
        self.logger.info("ReplicationCoordinator initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize replication coordinator.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("Initializing replication coordinator...")
            
            # Start coordination loop
            await self._start_coordination()
            
            self.logger.info("Replication coordinator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize replication coordinator: {e}")
            return False
    
    def register_handler(self, database_type: str, handler: Any) -> None:
        """
        Register database replication handler.
        
        Args:
            database_type: Type of database
            handler: Replication handler instance
        """
        self.handlers[database_type] = handler
        self.logger.debug(f"Registered handler for {database_type}")
    
    async def _start_coordination(self) -> None:
        """Start coordination processes"""
        self.is_coordinating = True
        
        # Start coordination tasks
        coordination_tasks = [
            self._sync_processing_loop(),
            self._conflict_resolution_loop(),
            self._periodic_sync_check()
        ]
        
        for task in coordination_tasks:
            asyncio.create_task(task)
        
        self.logger.info("Coordination processes started")
    
    async def _sync_processing_loop(self) -> None:
        """Main synchronization processing loop"""
        while self.is_coordinating:
            try:
                if self.sync_queue:
                    # Process batch of sync records
                    batch = self.sync_queue[:self.batch_size]
                    self.sync_queue = self.sync_queue[self.batch_size:]
                    
                    await self._process_sync_batch(batch)
                
                await asyncio.sleep(1)  # Short delay between batches
                
            except Exception as e:
                self.logger.error(f"Error in sync processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _conflict_resolution_loop(self) -> None:
        """Conflict resolution processing loop"""
        while self.is_coordinating:
            try:
                if self.conflict_queue:
                    # Process conflicts
                    conflicts_to_process = self.conflict_queue.copy()
                    self.conflict_queue.clear()
                    
                    for conflict in conflicts_to_process:
                        await self._resolve_conflict(conflict)
                
                await asyncio.sleep(5)  # Check for conflicts every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in conflict resolution loop: {e}")
                await asyncio.sleep(10)
    
    async def _periodic_sync_check(self) -> None:
        """Periodic synchronization health check"""
        while self.is_coordinating:
            try:
                await asyncio.sleep(self.sync_interval)
                await self._validate_sync_consistency()
                
            except Exception as e:
                self.logger.error(f"Error in periodic sync check: {e}")
    
    async def _process_sync_batch(self, batch: List[SyncRecord]) -> None:
        """Process a batch of synchronization records"""
        for sync_record in batch:
            try:
                await self._process_sync_record(sync_record)
                self.sync_statistics["successful_syncs"] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to process sync record {sync_record.id}: {e}")
                sync_record.status = "failed"
                sync_record.error_message = str(e)
                sync_record.retry_count += 1
                
                self.sync_statistics["failed_syncs"] += 1
                
                # Retry logic
                if sync_record.retry_count < 3:
                    self.sync_queue.append(sync_record)
                else:
                    self.logger.error(f"Max retries exceeded for sync record {sync_record.id}")
            
            finally:
                self.sync_history.append(sync_record)
                self.sync_statistics["total_syncs"] += 1
    
    async def _process_sync_record(self, sync_record: SyncRecord) -> None:
        """Process individual synchronization record"""
        handler = self.handlers.get(sync_record.database_type)
        if not handler:
            raise ValueError(f"No handler for database type: {sync_record.database_type}")
        
        # Validate data integrity
        if not self._validate_record_checksum(sync_record):
            raise ValueError(f"Checksum validation failed for record {sync_record.id}")
        
        # Check for conflicts before applying
        conflicts = await self._detect_conflicts(sync_record)
        if conflicts:
            for conflict in conflicts:
                self.conflict_queue.append(conflict)
                self.sync_statistics["conflicts_detected"] += 1
            return
        
        # Apply synchronization based on operation type
        if sync_record.operation == SyncOperation.INSERT:
            await self._apply_insert(handler, sync_record)
        elif sync_record.operation == SyncOperation.UPDATE:
            await self._apply_update(handler, sync_record)
        elif sync_record.operation == SyncOperation.DELETE:
            await self._apply_delete(handler, sync_record)
        elif sync_record.operation == SyncOperation.BULK_SYNC:
            await self._apply_bulk_sync(handler, sync_record)
        
        sync_record.status = "completed"
        self.last_sync_time = datetime.utcnow()
    
    def _validate_record_checksum(self, sync_record: SyncRecord) -> bool:
        """Validate record data integrity using checksum"""
        try:
            # Create checksum from data
            data_str = json.dumps(sync_record.data, sort_keys=True, separators=(',', ':'))
            calculated_checksum = hashlib.sha256(data_str.encode()).hexdigest()
            
            return calculated_checksum == sync_record.checksum
            
        except Exception as e:
            self.logger.error(f"Error validating checksum: {e}")
            return False
    
    async def _detect_conflicts(self, sync_record: SyncRecord) -> List[ConflictRecord]:
        """Detect potential data conflicts"""
        conflicts = []
        
        try:
            # Get current data from target
            handler = self.handlers.get(sync_record.database_type)
            if not handler:
                return conflicts
            
            # This would depend on the specific handler implementation
            # For now, we'll simulate conflict detection
            current_data = await self._get_current_record_data(
                handler, 
                sync_record.table_name, 
                sync_record.data.get("id")
            )
            
            if current_data:
                # Compare timestamps to detect conflicts
                sync_timestamp = sync_record.timestamp
                current_timestamp = current_data.get("updated_at")
                
                if current_timestamp and current_timestamp > sync_timestamp:
                    conflict = ConflictRecord(
                        id=f"conflict_{sync_record.id}_{int(datetime.utcnow().timestamp())}",
                        table_name=sync_record.table_name,
                        record_id=str(sync_record.data.get("id")),
                        conflict_type="timestamp_conflict",
                        source_data=sync_record.data,
                        target_data=current_data,
                        resolution_strategy=self.conflict_strategy,
                        timestamp=datetime.utcnow()
                    )
                    conflicts.append(conflict)
            
        except Exception as e:
            self.logger.error(f"Error detecting conflicts: {e}")
        
        return conflicts
    
    async def _get_current_record_data(
        self, 
        handler: Any, 
        table_name: str, 
        record_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get current record data from database"""
        try:
            # This would be implemented based on the specific handler
            # For now, we'll return None to simulate no existing data
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting current record data: {e}")
            return None
    
    async def _resolve_conflict(self, conflict: ConflictRecord) -> None:
        """Resolve data conflict based on strategy"""
        try:
            self.logger.info(f"Resolving conflict {conflict.id} using {conflict.resolution_strategy.value}")
            
            if conflict.resolution_strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
                # Use the data with the latest timestamp
                source_timestamp = conflict.source_data.get("updated_at", datetime.min)
                target_timestamp = conflict.target_data.get("updated_at", datetime.min)
                
                if source_timestamp >= target_timestamp:
                    conflict.resolution_data = conflict.source_data
                else:
                    conflict.resolution_data = conflict.target_data
                    
            elif conflict.resolution_strategy == ConflictResolutionStrategy.FIRST_WRITE_WINS:
                # Keep the existing data
                conflict.resolution_data = conflict.target_data
                
            elif conflict.resolution_strategy == ConflictResolutionStrategy.MERGE_FIELDS:
                # Merge non-conflicting fields
                merged_data = conflict.target_data.copy()
                for key, value in conflict.source_data.items():
                    if key not in merged_data or merged_data[key] is None:
                        merged_data[key] = value
                conflict.resolution_data = merged_data
                
            elif conflict.resolution_strategy == ConflictResolutionStrategy.MANUAL_REVIEW:
                # Mark for manual review
                self.logger.warning(f"Conflict {conflict.id} requires manual review")
                return
            
            # Apply resolved data
            if conflict.resolution_data:
                await self._apply_conflict_resolution(conflict)
                conflict.resolved = True
                self.sync_statistics["conflicts_resolved"] += 1
            
        except Exception as e:
            self.logger.error(f"Error resolving conflict {conflict.id}: {e}")
    
    async def _apply_conflict_resolution(self, conflict: ConflictRecord) -> None:
        """Apply conflict resolution to the database"""
        try:
            # Create a sync record for the resolution
            resolution_sync = SyncRecord(
                id=f"resolution_{conflict.id}",
                database_type="postgresql",  # Assuming primary database
                table_name=conflict.table_name,
                operation=SyncOperation.UPDATE,
                data=conflict.resolution_data,
                timestamp=datetime.utcnow(),
                source_region="conflict_resolution",
                target_regions=["all"],
                checksum=self._calculate_checksum(conflict.resolution_data)
            )
            
            # Process the resolution
            await self._process_sync_record(resolution_sync)
            
            self.logger.info(f"Conflict resolution applied for {conflict.id}")
            
        except Exception as e:
            self.logger.error(f"Error applying conflict resolution: {e}")
            raise
    
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for data"""
        data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def _apply_insert(self, handler: Any, sync_record: SyncRecord) -> None:
        """Apply insert operation"""
        # Implementation would depend on the specific handler
        self.logger.debug(f"Applying insert for {sync_record.table_name}")
    
    async def _apply_update(self, handler: Any, sync_record: SyncRecord) -> None:
        """Apply update operation"""
        # Implementation would depend on the specific handler
        self.logger.debug(f"Applying update for {sync_record.table_name}")
    
    async def _apply_delete(self, handler: Any, sync_record: SyncRecord) -> None:
        """Apply delete operation"""
        # Implementation would depend on the specific handler
        self.logger.debug(f"Applying delete for {sync_record.table_name}")
    
    async def _apply_bulk_sync(self, handler: Any, sync_record: SyncRecord) -> None:
        """Apply bulk synchronization"""
        # Implementation would depend on the specific handler
        self.logger.debug(f"Applying bulk sync for {sync_record.table_name}")
    
    async def _validate_sync_consistency(self) -> None:
        """Validate synchronization consistency across databases"""
        try:
            self.logger.debug("Validating sync consistency...")
            
            # Check for stale sync records
            stale_threshold = datetime.utcnow() - timedelta(hours=1)
            stale_records = [
                record for record in self.sync_queue 
                if record.timestamp < stale_threshold
            ]
            
            if stale_records:
                self.logger.warning(f"Found {len(stale_records)} stale sync records")
                
                # Remove stale records
                self.sync_queue = [
                    record for record in self.sync_queue
                    if record.timestamp >= stale_threshold
                ]
            
            # Check conflict queue size
            if len(self.conflict_queue) > 100:
                self.logger.warning(f"High number of unresolved conflicts: {len(self.conflict_queue)}")
            
        except Exception as e:
            self.logger.error(f"Error validating sync consistency: {e}")
    
    async def queue_sync(
        self, 
        database_type: str,
        table_name: str,
        operation: SyncOperation,
        data: Dict[str, Any],
        target_regions: List[str] = None
    ) -> str:
        """
        Queue a synchronization operation.
        
        Args:
            database_type: Type of database
            table_name: Table/collection name
            operation: Sync operation type
            data: Data to synchronize
            target_regions: Target regions for sync
            
        Returns:
            str: Sync record ID
        """
        try:
            sync_record = SyncRecord(
                id=f"sync_{int(datetime.utcnow().timestamp())}_{len(self.sync_queue)}",
                database_type=database_type,
                table_name=table_name,
                operation=operation,
                data=data,
                timestamp=datetime.utcnow(),
                source_region=self.config.get_topology_config().get("primary_region", "unknown"),
                target_regions=target_regions or ["all"],
                checksum=self._calculate_checksum(data)
            )
            
            self.sync_queue.append(sync_record)
            
            self.logger.debug(f"Queued sync operation: {sync_record.id}")
            return sync_record.id
            
        except Exception as e:
            self.logger.error(f"Error queueing sync operation: {e}")
            raise
    
    async def validate_all_replications(self) -> bool:
        """
        Validate all replication channels.
        
        Returns:
            bool: True if all replications are healthy
        """
        try:
            all_healthy = True
            
            for database_type, handler in self.handlers.items():
                try:
                    health = await handler.check_health()
                    if not health.get("healthy", False):
                        all_healthy = False
                        self.logger.warning(f"Replication unhealthy for {database_type}: {health}")
                        
                except Exception as e:
                    all_healthy = False
                    self.logger.error(f"Error checking replication health for {database_type}: {e}")
            
            return all_healthy
            
        except Exception as e:
            self.logger.error(f"Error validating replications: {e}")
            return False
    
    async def reconfigure_after_failover(self, database_type: str, new_primary_region: str) -> None:
        """
        Reconfigure coordination after database failover.
        
        Args:
            database_type: Database that failed over
            new_primary_region: New primary region
        """
        try:
            self.logger.info(f"Reconfiguring coordination after {database_type} failover to {new_primary_region}")
            
            # Update configuration
            topology_config = self.config.get_topology_config()
            if database_type in topology_config.get("databases", {}):
                topology_config["databases"][database_type]["primary_region"] = new_primary_region
            
            # Requeue failed sync records for retry
            failed_records = [r for r in self.sync_history if r.status == "failed" and r.database_type == database_type]
            for record in failed_records[-10:]:  # Retry last 10 failed records
                record.retry_count = 0
                record.status = "pending"
                record.error_message = None
                self.sync_queue.append(record)
            
            self.logger.info(f"Coordination reconfigured for {database_type}")
            
        except Exception as e:
            self.logger.error(f"Error reconfiguring coordination: {e}")
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """
        Get comprehensive synchronization status.
        
        Returns:
            Dict containing sync status information
        """
        return {
            "is_coordinating": self.is_coordinating,
            "queue_size": len(self.sync_queue),
            "conflict_queue_size": len(self.conflict_queue),
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "statistics": self.sync_statistics.copy(),
            "registered_handlers": list(self.handlers.keys()),
            "conflict_strategy": self.conflict_strategy.value,
            "recent_conflicts": [
                {
                    "id": c.id,
                    "table": c.table_name,
                    "type": c.conflict_type,
                    "resolved": c.resolved,
                    "timestamp": c.timestamp.isoformat()
                }
                for c in self.conflict_queue[-5:]  # Last 5 conflicts
            ]
        }
    
    async def shutdown(self) -> None:
        """Shutdown replication coordinator"""
        try:
            self.logger.info("Shutting down replication coordinator...")
            
            self.is_coordinating = False
            
            # Process remaining sync queue
            if self.sync_queue:
                self.logger.info(f"Processing {len(self.sync_queue)} remaining sync records...")
                remaining_batch = self.sync_queue.copy()
                self.sync_queue.clear()
                await self._process_sync_batch(remaining_batch)
            
            # Clear state
            self.handlers.clear()
            self.conflict_queue.clear()
            
            self.logger.info("Replication coordinator shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during coordinator shutdown: {e}")
            raise
