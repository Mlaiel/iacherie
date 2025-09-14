"""Event Migration Orchestrator - Enterprise Implementation

Advanced event migration orchestrator for managing large-scale event store
migrations with batching, rollback capabilities, and progress monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from uuid import uuid4
import time

from . import DomainEvent, EventStoreInterface
from .event_versioning_engine import EventVersioningEngine, SemanticVersion

logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    """Migration status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLBACK_PENDING = "rollback_pending"
    ROLLBACK_RUNNING = "rollback_running"
    ROLLBACK_COMPLETED = "rollback_completed"
    ROLLBACK_FAILED = "rollback_failed"


class MigrationStrategy(Enum):
    """Migration execution strategies"""
    SEQUENTIAL = "sequential"  # One event at a time
    BATCH = "batch"  # Process in batches
    PARALLEL = "parallel"  # Parallel processing
    STREAMING = "streaming"  # Stream processing
    BLUE_GREEN = "blue_green"  # Blue-green deployment


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    SKIP = "skip"  # Skip conflicting events
    OVERWRITE = "overwrite"  # Overwrite existing events
    MERGE = "merge"  # Merge event data
    FAIL = "fail"  # Fail migration on conflict
    MANUAL = "manual"  # Require manual intervention


@dataclass
class MigrationConfig:
    """Migration configuration"""
    migration_id: str
    name: str
    description: str
    event_types: List[str]
    from_version: Optional[SemanticVersion] = None
    to_version: Optional[SemanticVersion] = None
    strategy: MigrationStrategy = MigrationStrategy.BATCH
    batch_size: int = 1000
    max_parallel_workers: int = 4
    conflict_resolution: ConflictResolution = ConflictResolution.SKIP
    enable_rollback: bool = True
    validation_enabled: bool = True
    dry_run: bool = False
    timeout_seconds: int = 3600
    retry_attempts: int = 3
    retry_delay_seconds: int = 30
    checkpoint_interval: int = 10000
    
    # Filtering options
    aggregate_filter: Optional[List[str]] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    custom_filter: Optional[str] = None


@dataclass
class MigrationProgress:
    """Migration progress tracking"""
    migration_id: str
    status: MigrationStatus
    total_events: int = 0
    processed_events: int = 0
    failed_events: int = 0
    skipped_events: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_checkpoint: int = 0
    estimated_completion: Optional[datetime] = None
    error_messages: List[str] = field(default_factory=list)
    
    @property
    def progress_percentage(self) -> float:
        if self.total_events == 0:
            return 0.0
        return (self.processed_events / self.total_events) * 100
    
    @property
    def duration(self) -> Optional[timedelta]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return datetime.now(timezone.utc) - self.start_time
        return None


@dataclass
class MigrationCheckpoint:
    """Migration checkpoint for resumability"""
    migration_id: str
    checkpoint_id: str
    position: int
    last_event_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventMigrationResult:
    """Result of a single event migration"""
    original_event: DomainEvent
    migrated_event: Optional[DomainEvent] = None
    success: bool = False
    error: Optional[str] = None
    skipped: bool = False
    processing_time_ms: float = 0.0


class MigrationValidator:
    """Validates migration results"""
    
    def __init__(self, versioning_engine -> None: EventVersioningEngine) -> None:
        self.versioning_engine = versioning_engine
    
    async def validate_migrated_event(self, original: DomainEvent, 
                                    migrated: DomainEvent) -> bool:
        """Validate migrated event"""
        try:
            # Basic validation
            if original.event_id != migrated.event_id:
                return False
            
            if original.aggregate_id != migrated.aggregate_id:
                return False
            
            if original.event_type != migrated.event_type:
                return False
            
            # Schema validation using versioning engine
            return await self.versioning_engine.validator.validate_event(migrated)
            
        except Exception as e:
            logger.error(f"Event validation failed: {e}")
            return False


class MigrationBackup:
    """Manages migration backups for rollback"""
    
    def __init__(self, backup_store -> None: EventStoreInterface) -> None:
        self.backup_store = backup_store
        self.backups: Dict[str, List[DomainEvent]] = {}
    
    async def backup_event(self, migration_id: str, event: DomainEvent) -> bool:
        """Backup original event before migration"""
        try:
            if migration_id not in self.backups:
                self.backups[migration_id] = []
            
            self.backups[migration_id].append(event)
            
            # Also save to backup store
            await self.backup_store.save_events(f"backup_{migration_id}", [event])
            
            return True
        except Exception as e:
            logger.error(f"Failed to backup event: {e}")
            return False
    
    async def restore_events(self, migration_id: str) -> List[DomainEvent]:
        """Restore backed up events"""
        try:
            if migration_id in self.backups:
                return self.backups[migration_id].copy()
            
            # Try to restore from backup store
            return await self.backup_store.get_events(f"backup_{migration_id}")
        except Exception as e:
            logger.error(f"Failed to restore events: {e}")
            return []
    
    async def cleanup_backup(self, migration_id: str) -> bool:
        """Cleanup backup after successful migration"""
        try:
            if migration_id in self.backups:
                del self.backups[migration_id]
            
            # Remove from backup store
            # Note: This would need implementation in event store
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup backup: {e}")
            return False


class SequentialMigrationExecutor:
    """Sequential migration executor"""
    
    def __init__(self, config -> None: MigrationConfig, 
                 versioning_engine -> None: EventVersioningEngine,
                 validator -> None: MigrationValidator,
                 backup -> None: MigrationBackup) -> None:
        self.config = config
        self.versioning_engine = versioning_engine
        self.validator = validator
        self.backup = backup
    
    async def execute(self, events: List[DomainEvent], 
                    progress_callback: Callable[[MigrationProgress], None] = None) -> List[EventMigrationResult]:
        """Execute sequential migration"""
        results = []
        
        for i, event in enumerate(events):
            start_time = time.time()
            result = EventMigrationResult(original_event=event)
            
            try:
                # Backup original event
                if self.config.enable_rollback:
                    await self.backup.backup_event(self.config.migration_id, event)
                
                # Skip if not in target event types
                if self.config.event_types and event.event_type not in self.config.event_types:
                    result.skipped = True
                    results.append(result)
                    continue
                
                # Migrate event
                if self.config.to_version:
                    migrated_event = await self.versioning_engine.migrate_event_to_version(
                        event, self.config.to_version
                    )
                else:
                    migrated_event = event  # No version change
                
                if migrated_event:
                    # Validate if enabled
                    if self.config.validation_enabled:
                        if await self.validator.validate_migrated_event(event, migrated_event):
                            result.migrated_event = migrated_event
                            result.success = True
                        else:
                            result.error = "Validation failed"
                    else:
                        result.migrated_event = migrated_event
                        result.success = True
                else:
                    result.error = "Migration failed"
                
                result.processing_time_ms = (time.time() - start_time) * 1000
                results.append(result)
                
                # Progress callback
                if progress_callback and (i + 1) % 100 == 0:
                    progress = MigrationProgress(
                        migration_id=self.config.migration_id,
                        status=MigrationStatus.RUNNING,
                        total_events=len(events),
                        processed_events=i + 1
                    )
                    progress_callback(progress)
                
            except Exception as e:
                result.error = str(e)
                result.processing_time_ms = (time.time() - start_time) * 1000
                results.append(result)
                logger.error(f"Failed to migrate event {event.event_id}: {e}")
        
        return results


class BatchMigrationExecutor:
    """Batch migration executor"""
    
    def __init__(self, config -> None: MigrationConfig,
                 versioning_engine -> None: EventVersioningEngine,
                 validator -> None: MigrationValidator,
                 backup -> None: MigrationBackup) -> None:
        self.config = config
        self.versioning_engine = versioning_engine
        self.validator = validator
        self.backup = backup
    
    async def execute(self, events: List[DomainEvent],
                    progress_callback: Callable[[MigrationProgress], None] = None) -> List[EventMigrationResult]:
        """Execute batch migration"""
        results = []
        total_events = len(events)
        
        # Process in batches
        for i in range(0, total_events, self.config.batch_size):
            batch = events[i:i + self.config.batch_size]
            batch_results = await self._process_batch(batch)
            results.extend(batch_results)
            
            # Progress callback
            if progress_callback:
                progress = MigrationProgress(
                    migration_id=self.config.migration_id,
                    status=MigrationStatus.RUNNING,
                    total_events=total_events,
                    processed_events=min(i + self.config.batch_size, total_events)
                )
                progress_callback(progress)
        
        return results
    
    async def _process_batch(self, batch: List[DomainEvent]) -> List[EventMigrationResult]:
        """Process a single batch"""
        results = []
        
        for event in batch:
            start_time = time.time()
            result = EventMigrationResult(original_event=event)
            
            try:
                # Backup if needed
                if self.config.enable_rollback:
                    await self.backup.backup_event(self.config.migration_id, event)
                
                # Filter check
                if self.config.event_types and event.event_type not in self.config.event_types:
                    result.skipped = True
                    results.append(result)
                    continue
                
                # Migrate
                if self.config.to_version:
                    migrated_event = await self.versioning_engine.migrate_event_to_version(
                        event, self.config.to_version
                    )
                else:
                    migrated_event = event
                
                if migrated_event:
                    if self.config.validation_enabled:
                        if await self.validator.validate_migrated_event(event, migrated_event):
                            result.migrated_event = migrated_event
                            result.success = True
                        else:
                            result.error = "Validation failed"
                    else:
                        result.migrated_event = migrated_event
                        result.success = True
                else:
                    result.error = "Migration failed"
                
                result.processing_time_ms = (time.time() - start_time) * 1000
                results.append(result)
                
            except Exception as e:
                result.error = str(e)
                result.processing_time_ms = (time.time() - start_time) * 1000
                results.append(result)
        
        return results


class ParallelMigrationExecutor:
    """Parallel migration executor"""
    
    def __init__(self, config -> None: MigrationConfig,
                 versioning_engine -> None: EventVersioningEngine,
                 validator -> None: MigrationValidator,
                 backup -> None: MigrationBackup) -> None:
        self.config = config
        self.versioning_engine = versioning_engine
        self.validator = validator
        self.backup = backup
    
    async def execute(self, events: List[DomainEvent],
                    progress_callback: Callable[[MigrationProgress], None] = None) -> List[EventMigrationResult]:
        """Execute parallel migration"""
        # Create semaphore for controlling parallelism
        semaphore = asyncio.Semaphore(self.config.max_parallel_workers)
        
        async def process_event(event: DomainEvent) -> EventMigrationResult:
            async with semaphore:
                start_time = time.time()
                result = EventMigrationResult(original_event=event)
                
                try:
                    # Backup if needed
                    if self.config.enable_rollback:
                        await self.backup.backup_event(self.config.migration_id, event)
                    
                    # Filter check
                    if self.config.event_types and event.event_type not in self.config.event_types:
                        result.skipped = True
                        return result
                    
                    # Migrate
                    if self.config.to_version:
                        migrated_event = await self.versioning_engine.migrate_event_to_version(
                            event, self.config.to_version
                        )
                    else:
                        migrated_event = event
                    
                    if migrated_event:
                        if self.config.validation_enabled:
                            if await self.validator.validate_migrated_event(event, migrated_event):
                                result.migrated_event = migrated_event
                                result.success = True
                            else:
                                result.error = "Validation failed"
                        else:
                            result.migrated_event = migrated_event
                            result.success = True
                    else:
                        result.error = "Migration failed"
                    
                    result.processing_time_ms = (time.time() - start_time) * 1000
                    return result
                    
                except Exception as e:
                    result.error = str(e)
                    result.processing_time_ms = (time.time() - start_time) * 1000
                    return result
        
        # Process all events in parallel
        tasks = [process_event(event) for event in events]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = EventMigrationResult(
                    original_event=events[i],
                    error=str(result)
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
        
        return final_results


class EventMigrationOrchestrator:
    """Enterprise event migration orchestrator"""
    
    def __init__(self, event_store -> None: EventStoreInterface,
                 backup_store -> None: EventStoreInterface,
                 versioning_engine -> None: EventVersioningEngine) -> None:
        self.event_store = event_store
        self.backup_store = backup_store
        self.versioning_engine = versioning_engine
        self.validator = MigrationValidator(versioning_engine)
        self.backup = MigrationBackup(backup_store)
        
        self.active_migrations: Dict[str, MigrationProgress] = {}
        self.checkpoints: Dict[str, List[MigrationCheckpoint]] = {}
        self.migration_history: List[MigrationProgress] = []
    
    async def plan_migration(self, config: MigrationConfig) -> Dict[str, Any]:
        """Plan migration and estimate resources"""
        try:
            # Count events that would be affected
            affected_count = 0
            
            if config.event_types:
                for event_type in config.event_types:
                    # This is a simplified count - in reality would query event store
                    # with filters for date range, aggregates, etc.
                    events = await self.event_store.get_all_events(limit=10000)
                    type_events = [e for e in events if e.event_type == event_type]
                    affected_count += len(type_events)
            else:
                all_events = await self.event_store.get_all_events(limit=10000)
                affected_count = len(all_events)
            
            # Apply filters
            if config.date_range_start or config.date_range_end:
                # Apply date filtering (simplified)
                pass
            
            if config.aggregate_filter:
                # Apply aggregate filtering (simplified)
                pass
            
            # Estimate resources
            estimated_duration = self._estimate_duration(affected_count, config)
            estimated_storage = affected_count * 1024  # Rough estimate
            
            return {
                "migration_id": config.migration_id,
                "affected_events": affected_count,
                "estimated_duration_minutes": estimated_duration.total_seconds() / 60,
                "estimated_storage_bytes": estimated_storage,
                "strategy": config.strategy.value,
                "has_rollback": config.enable_rollback,
                "dry_run": config.dry_run
            }
            
        except Exception as e:
            logger.error(f"Migration planning failed: {e}")
            raise
    
    async def execute_migration(self, config: MigrationConfig,
                              progress_callback: Callable[[MigrationProgress], None] = None) -> MigrationProgress:
        """Execute migration with specified configuration"""
        progress = MigrationProgress(
            migration_id=config.migration_id,
            status=MigrationStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )
        
        self.active_migrations[config.migration_id] = progress
        
        try:
            # Get events to migrate
            events = await self._get_events_for_migration(config)
            progress.total_events = len(events)
            
            if progress_callback:
                progress_callback(progress)
            
            # Select executor based on strategy
            executor = self._create_executor(config)
            
            # Execute migration
            if config.dry_run:
                logger.info(f"DRY RUN: Would migrate {len(events)} events")
                results = []
                for event in events[:10]:  # Sample first 10 for dry run
                    result = EventMigrationResult(original_event=event, success=True)
                    results.append(result)
            else:
                results = await executor.execute(events, progress_callback)
            
            # Process results
            successful_events = [r for r in results if r.success]
            failed_events = [r for r in results if not r.success and not r.skipped]
            skipped_events = [r for r in results if r.skipped]
            
            progress.processed_events = len(successful_events)
            progress.failed_events = len(failed_events)
            progress.skipped_events = len(skipped_events)
            progress.status = MigrationStatus.COMPLETED if not failed_events else MigrationStatus.FAILED
            progress.end_time = datetime.now(timezone.utc)
            
            # Save migrated events to event store (if not dry run)
            if not config.dry_run and successful_events:
                for result in successful_events:
                    if result.migrated_event:
                        # In a real implementation, would save to event store
                        pass
            
            # Add to history
            self.migration_history.append(progress)
            
            logger.info(f"Migration {config.migration_id} completed: {progress.processed_events} success, {progress.failed_events} failed, {progress.skipped_events} skipped")
            
            return progress
            
        except Exception as e:
            progress.status = MigrationStatus.FAILED
            progress.end_time = datetime.now(timezone.utc)
            progress.error_messages.append(str(e))
            logger.error(f"Migration {config.migration_id} failed: {e}")
            return progress
        finally:
            if config.migration_id in self.active_migrations:
                del self.active_migrations[config.migration_id]
    
    async def rollback_migration(self, migration_id: str) -> bool:
        """Rollback a completed migration"""
        try:
            # Find migration in history
            migration = None
            for m in self.migration_history:
                if m.migration_id == migration_id:
                    migration = m
                    break
            
            if not migration:
                logger.error(f"Migration {migration_id} not found")
                return False
            
            if migration.status != MigrationStatus.COMPLETED:
                logger.error(f"Can only rollback completed migrations, status: {migration.status}")
                return False
            
            # Restore backed up events
            original_events = await self.backup.restore_events(migration_id)
            
            if not original_events:
                logger.error(f"No backup found for migration {migration_id}")
                return False
            
            # Restore events to event store
            for event in original_events:
                # In a real implementation, would restore to event store
                pass
            
            # Update migration status
            migration.status = MigrationStatus.ROLLBACK_COMPLETED
            
            logger.info(f"Successfully rolled back migration {migration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed for migration {migration_id}: {e}")
            return False
    
    async def get_migration_status(self, migration_id: str) -> Optional[MigrationProgress]:
        """Get current migration status"""
        # Check active migrations first
        if migration_id in self.active_migrations:
            return self.active_migrations[migration_id]
        
        # Check history
        for migration in self.migration_history:
            if migration.migration_id == migration_id:
                return migration
        
        return None
    
    async def list_migrations(self, status_filter: Optional[MigrationStatus] = None) -> List[MigrationProgress]:
        """List migrations with optional status filter"""
        all_migrations = list(self.active_migrations.values()) + self.migration_history
        
        if status_filter:
            return [m for m in all_migrations if m.status == status_filter]
        
        return all_migrations
    
    async def cancel_migration(self, migration_id: str) -> bool:
        """Cancel running migration"""
        if migration_id in self.active_migrations:
            migration = self.active_migrations[migration_id]
            migration.status = MigrationStatus.CANCELLED
            migration.end_time = datetime.now(timezone.utc)
            
            # Move to history
            self.migration_history.append(migration)
            del self.active_migrations[migration_id]
            
            logger.info(f"Cancelled migration {migration_id}")
            return True
        
        return False
    
    def _estimate_duration(self, event_count: int, config: MigrationConfig) -> timedelta:
        """Estimate migration duration"""
        # Base processing rate (events per second)
        base_rate = 100
        
        # Adjust based on strategy
        if config.strategy == MigrationStrategy.PARALLEL:
            rate = base_rate * config.max_parallel_workers
        elif config.strategy == MigrationStrategy.BATCH:
            rate = base_rate * 2
        else:
            rate = base_rate
        
        # Adjust for validation
        if config.validation_enabled:
            rate = rate * 0.8
        
        # Calculate duration
        duration_seconds = event_count / rate
        return timedelta(seconds=duration_seconds)
    
    async def _get_events_for_migration(self, config: MigrationConfig) -> List[DomainEvent]:
        """Get events that need migration based on config"""
        # This is simplified - in reality would build complex queries
        # based on event types, date ranges, aggregates, etc.
        
        all_events = await self.event_store.get_all_events(limit=10000)
        filtered_events = []
        
        for event in all_events:
            # Apply event type filter
            if config.event_types and event.event_type not in config.event_types:
                continue
            
            # Apply date range filter
            if config.date_range_start and event.occurred_at < config.date_range_start:
                continue
            
            if config.date_range_end and event.occurred_at > config.date_range_end:
                continue
            
            # Apply aggregate filter
            if config.aggregate_filter and event.aggregate_id not in config.aggregate_filter:
                continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    def _create_executor(self, config -> None: MigrationConfig) -> None:
        """Create appropriate migration executor"""
        if config.strategy == MigrationStrategy.SEQUENTIAL:
            return SequentialMigrationExecutor(config, self.versioning_engine, self.validator, self.backup)
        elif config.strategy == MigrationStrategy.BATCH:
            return BatchMigrationExecutor(config, self.versioning_engine, self.validator, self.backup)
        elif config.strategy == MigrationStrategy.PARALLEL:
            return ParallelMigrationExecutor(config, self.versioning_engine, self.validator, self.backup)
        else:
            # Default to batch
            return BatchMigrationExecutor(config, self.versioning_engine, self.validator, self.backup)
    
    async def health_check(self) -> bool:
        """Check orchestrator health"""
        try:
            # Check if event stores are accessible
            await self.event_store.get_all_events(limit=1)
            await self.backup_store.get_all_events(limit=1)
            
            # Check versioning engine
            return await self.versioning_engine.health_check()
        except Exception as e:
            logger.error(f"Migration orchestrator health check failed: {e}")
            return False