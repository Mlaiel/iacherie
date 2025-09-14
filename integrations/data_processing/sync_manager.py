"""Data Synchronization Engine - Multi-Platform Data Sync
========================================================

Advanced data synchronization engine for maintaining consistency 
across multiple third-party integrations and platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Callable, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import redis.asyncio as redis
import httpx


class SyncDirection(Enum):
    """Data synchronization directions."""
    BIDIRECTIONAL = "bidirectional"
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"


class SyncStatus(Enum):
    """Synchronization status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ConflictResolution(Enum):
    """Conflict resolution strategies."""
    LATEST_WINS = "latest_wins"
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    MANUAL_REVIEW = "manual_review"
    MERGE_FIELDS = "merge_fields"


@dataclass
class SyncRule:
    """Data synchronization rule configuration."""
    id: str
    name: str
    source_platform: str
    target_platform: str
    data_type: str
    direction: SyncDirection
    schedule: str  # Cron expression
    conflict_resolution: ConflictResolution
    field_mappings: Dict[str, str] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    transformations: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    retry_count: int = 3
    timeout: float = 300.0


@dataclass
class SyncJob:
    """Synchronization job instance."""
    id: str
    rule_id: str
    status: SyncStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_synced: int = 0
    records_failed: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataRecord:
    """Data record for synchronization."""
    id: str
    platform: str
    data_type: str
    data: Dict[str, Any]
    checksum: str
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncConflict:
    """Data synchronization conflict."""
    id: str
    job_id: str
    record_id: str
    source_data: Dict[str, Any]
    target_data: Dict[str, Any]
    conflict_fields: List[str]
    resolution_strategy: ConflictResolution
    resolved: bool = False
    resolution_data: Optional[Dict[str, Any]] = None


Base = declarative_base()


class SyncJobModel(Base):
    """Sync job database model."""
    __tablename__ = 'sync_jobs'
    
    id = sa.Column(sa.String(36), primary_key=True)
    rule_id = sa.Column(sa.String(36), nullable=False)
    status = sa.Column(sa.String(20), nullable=False)
    started_at = sa.Column(sa.DateTime)
    completed_at = sa.Column(sa.DateTime)
    records_processed = sa.Column(sa.Integer, default=0)
    records_synced = sa.Column(sa.Integer, default=0)
    records_failed = sa.Column(sa.Integer, default=0)
    errors = sa.Column(sa.Text)
    metadata = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)


class DataSyncEngine:
    """Advanced data synchronization engine."""
    
    def __init__(
        self,
        database_url -> None: str,
        redis_url -> None: str,
        config -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.engine = create_async_engine(database_url)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Redis setup for caching and coordination
        self.redis_url = redis_url
        self.redis_client = None
        
        # Sync state
        self.sync_rules: Dict[str, SyncRule] = {}
        self.active_jobs: Dict[str, SyncJob] = {}
        self.platform_adapters: Dict[str, Any] = {}
        self.conflict_resolvers: Dict[ConflictResolution, Callable] = {}
        
        # Scheduling
        self.scheduler_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self.sync_metrics = {
            'total_jobs': 0,
            'successful_jobs': 0,
            'failed_jobs': 0,
            'total_records_synced': 0,
            'average_sync_time': 0.0
        }
        
        self._setup_conflict_resolvers()
        
    async def initialize(self) -> None:
        """Initialize the sync engine."""
        # Create database tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Connect to Redis
        self.redis_client = redis.from_url(self.redis_url)
        
        self.logger.info("Data sync engine initialized")
    
    def _setup_conflict_resolvers(self) -> None:
        """Setup conflict resolution strategies."""
        self.conflict_resolvers = {
            ConflictResolution.LATEST_WINS: self._resolve_latest_wins,
            ConflictResolution.SOURCE_WINS: self._resolve_source_wins,
            ConflictResolution.TARGET_WINS: self._resolve_target_wins,
            ConflictResolution.MERGE_FIELDS: self._resolve_merge_fields
        }
    
    def register_platform_adapter(self, platform -> None: str, adapter -> None: Any) -> None:
        """Register platform-specific data adapter."""
        self.platform_adapters[platform] = adapter
        self.logger.info(f"Registered adapter for platform: {platform}")
    
    def add_sync_rule(self, sync_rule -> None: SyncRule) -> None:
        """Add synchronization rule."""
        self.sync_rules[sync_rule.id] = sync_rule
        self.logger.info(f"Added sync rule: {sync_rule.name}")
    
    def remove_sync_rule(self, rule_id -> None: str) -> None:
        """Remove synchronization rule."""
        if rule_id in self.sync_rules:
            del self.sync_rules[rule_id]
            self.logger.info(f"Removed sync rule: {rule_id}")
    
    async def start_scheduler(self) -> None:
        """Start the synchronization scheduler."""
        if self.scheduler_running:
            return
        
        self.scheduler_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Sync scheduler started")
    
    async def stop_scheduler(self) -> None:
        """Stop the synchronization scheduler."""
        if not self.scheduler_running:
            return
        
        self.scheduler_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Sync scheduler stopped")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.scheduler_running:
            try:
                await self._check_scheduled_syncs()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_scheduled_syncs(self) -> None:
        """Check for scheduled synchronizations."""
        from croniter import croniter
        
        current_time = datetime.now()
        
        for rule in self.sync_rules.values():
            if not rule.enabled:
                continue
            
            # Check if sync should run based on schedule
            cron = croniter(rule.schedule, current_time)
            next_run = cron.get_prev(datetime)
            
            # Check if we should run this sync
            last_run_key = f"sync_last_run:{rule.id}"
            last_run_str = await self.redis_client.get(last_run_key)
            
            if last_run_str:
                last_run = datetime.fromisoformat(last_run_str.decode())
                if next_run <= last_run:
                    continue
            
            # Create and start sync job
            job = await self.create_sync_job(rule.id)
            await self.start_sync_job(job.id)
            
            # Update last run time
            await self.redis_client.set(
                last_run_key,
                current_time.isoformat(),
                ex=86400 * 7  # Expire in 7 days
            )
    
    async def create_sync_job(self, rule_id: str) -> SyncJob:
        """Create a new synchronization job."""
        if rule_id not in self.sync_rules:
            raise ValueError(f"Sync rule not found: {rule_id}")
        
        job = SyncJob(
            id=str(uuid.uuid4()),
            rule_id=rule_id,
            status=SyncStatus.PENDING
        )
        
        self.active_jobs[job.id] = job
        
        # Persist to database
        async with self.async_session() as session:
            db_job = SyncJobModel(
                id=job.id,
                rule_id=job.rule_id,
                status=job.status.value
            )
            session.add(db_job)
            await session.commit()
        
        self.logger.info(f"Created sync job: {job.id}")
        return job
    
    async def start_sync_job(self, job_id -> None: str) -> None:
        """Start a synchronization job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Sync job not found: {job_id}")
        
        job = self.active_jobs[job_id]
        rule = self.sync_rules[job.rule_id]
        
        job.status = SyncStatus.IN_PROGRESS
        job.started_at = datetime.now()
        
        # Update database
        await self._update_job_status(job)
        
        # Start sync task
        sync_task = asyncio.create_task(self._execute_sync_job(job, rule))
        self.logger.info(f"Started sync job: {job_id}")
    
    async def _execute_sync_job(self, job -> None: SyncJob, rule -> None: SyncRule) -> None:
        """Execute synchronization job."""
        try:
            # Get platform adapters
            source_adapter = self.platform_adapters.get(rule.source_platform)
            target_adapter = self.platform_adapters.get(rule.target_platform)
            
            if not source_adapter or not target_adapter:
                raise ValueError("Platform adapters not found")
            
            # Fetch data from source
            source_data = await self._fetch_platform_data(
                source_adapter, rule.data_type, rule.filters
            )
            
            # Fetch existing data from target for comparison
            target_data = await self._fetch_platform_data(
                target_adapter, rule.data_type, rule.filters
            )
            
            # Create data record mappings
            source_records = self._create_data_records(
                source_data, rule.source_platform, rule.data_type
            )
            target_records = self._create_data_records(
                target_data, rule.target_platform, rule.data_type
            )
            
            # Perform synchronization
            if rule.direction in [SyncDirection.BIDIRECTIONAL, SyncDirection.SOURCE_TO_TARGET]:
                await self._sync_records(
                    source_records, target_records, rule, job, 
                    source_adapter, target_adapter, "source_to_target"
                )
            
            if rule.direction in [SyncDirection.BIDIRECTIONAL, SyncDirection.TARGET_TO_SOURCE]:
                await self._sync_records(
                    target_records, source_records, rule, job,
                    target_adapter, source_adapter, "target_to_source"
                )
            
            # Complete job
            job.status = SyncStatus.COMPLETED
            job.completed_at = datetime.now()
            
            # Update metrics
            self.sync_metrics['successful_jobs'] += 1
            self.sync_metrics['total_records_synced'] += job.records_synced
            
        except Exception as e:
            self.logger.error(f"Sync job {job.id} failed: {e}")
            job.status = SyncStatus.FAILED
            job.errors.append(str(e))
            job.completed_at = datetime.now()
            
            self.sync_metrics['failed_jobs'] += 1
        
        finally:
            # Update final status
            await self._update_job_status(job)
            self.sync_metrics['total_jobs'] += 1
            
            # Calculate average sync time
            if job.started_at and job.completed_at:
                sync_time = (job.completed_at - job.started_at).total_seconds()
                total_time = self.sync_metrics['average_sync_time'] * (self.sync_metrics['total_jobs'] - 1)
                self.sync_metrics['average_sync_time'] = (total_time + sync_time) / self.sync_metrics['total_jobs']
    
    async def _fetch_platform_data(
        self, 
        adapter: Any, 
        data_type: str, 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fetch data from platform adapter."""
        if hasattr(adapter, 'fetch_data'):
            return await adapter.fetch_data(data_type, filters)
        else:
            raise ValueError(f"Adapter does not support data fetching")
    
    def _create_data_records(
        self, 
        data: List[Dict[str, Any]], 
        platform: str, 
        data_type: str
    ) -> Dict[str, DataRecord]:
        """Create data records from platform data."""
        records = {}
        
        for item in data:
            record_id = item.get('id') or str(uuid.uuid4())
            checksum = hashlib.md5(json.dumps(item, sort_keys=True).encode()).hexdigest()
            
            record = DataRecord(
                id=record_id,
                platform=platform,
                data_type=data_type,
                data=item,
                checksum=checksum,
                updated_at=datetime.fromisoformat(item.get('updated_at', datetime.now().isoformat()))
            )
            
            records[record_id] = record
        
        return records
    
    async def _sync_records(
        self,
        source_records -> None: Dict[str, DataRecord],
        target_records -> None: Dict[str, DataRecord],
        rule -> None: SyncRule,
        job -> None: SyncJob,
        source_adapter -> None: Any,
        target_adapter -> None: Any,
        direction -> None: str
    ) -> None:
        """Synchronize records between platforms."""
        for record_id, source_record in source_records.items():
            try:
                job.records_processed += 1
                
                # Check if record exists in target
                if record_id in target_records:
                    target_record = target_records[record_id]
                    
                    # Check for conflicts
                    if source_record.checksum != target_record.checksum:
                        conflict = SyncConflict(
                            id=str(uuid.uuid4()),
                            job_id=job.id,
                            record_id=record_id,
                            source_data=source_record.data,
                            target_data=target_record.data,
                            conflict_fields=self._detect_conflict_fields(
                                source_record.data, target_record.data
                            ),
                            resolution_strategy=rule.conflict_resolution
                        )
                        
                        # Resolve conflict
                        resolved_data = await self._resolve_conflict(conflict, rule)
                        if resolved_data:
                            # Update target with resolved data
                            transformed_data = self._apply_transformations(
                                resolved_data, rule.transformations
                            )
                            mapped_data = self._apply_field_mappings(
                                transformed_data, rule.field_mappings
                            )
                            
                            await self._update_platform_record(
                                target_adapter, record_id, mapped_data
                            )
                            job.records_synced += 1
                else:
                    # New record - create in target
                    transformed_data = self._apply_transformations(
                        source_record.data, rule.transformations
                    )
                    mapped_data = self._apply_field_mappings(
                        transformed_data, rule.field_mappings
                    )
                    
                    await self._create_platform_record(
                        target_adapter, mapped_data
                    )
                    job.records_synced += 1
                
            except Exception as e:
                self.logger.error(f"Failed to sync record {record_id}: {e}")
                job.records_failed += 1
                job.errors.append(f"Record {record_id}: {str(e)}")
    
    def _detect_conflict_fields(
        self, 
        source_data: Dict[str, Any], 
        target_data: Dict[str, Any]
    ) -> List[str]:
        """Detect fields with conflicts."""
        conflicts = []
        
        all_keys = set(source_data.keys()) | set(target_data.keys())
        for key in all_keys:
            source_value = source_data.get(key)
            target_value = target_data.get(key)
            
            if source_value != target_value:
                conflicts.append(key)
        
        return conflicts
    
    async def _resolve_conflict(
        self, 
        conflict: SyncConflict, 
        rule: SyncRule
    ) -> Optional[Dict[str, Any]]:
        """Resolve synchronization conflict."""
        resolver = self.conflict_resolvers.get(rule.conflict_resolution)
        if resolver:
            return await resolver(conflict)
        else:
            self.logger.warning(f"No resolver for strategy: {rule.conflict_resolution}")
            return None
    
    async def _resolve_latest_wins(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Resolve conflict with latest timestamp wins strategy."""
        source_updated = conflict.source_data.get('updated_at')
        target_updated = conflict.target_data.get('updated_at')
        
        if source_updated and target_updated:
            source_time = datetime.fromisoformat(source_updated)
            target_time = datetime.fromisoformat(target_updated)
            
            return conflict.source_data if source_time > target_time else conflict.target_data
        
        return conflict.source_data  # Default to source if timestamps unavailable
    
    async def _resolve_source_wins(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Resolve conflict with source wins strategy."""
        return conflict.source_data
    
    async def _resolve_target_wins(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Resolve conflict with target wins strategy."""
        return conflict.target_data
    
    async def _resolve_merge_fields(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Resolve conflict by merging non-conflicting fields."""
        merged_data = conflict.target_data.copy()
        
        for field in conflict.conflict_fields:
            # For merge strategy, prefer source for conflicting fields
            if field in conflict.source_data:
                merged_data[field] = conflict.source_data[field]
        
        return merged_data
    
    def _apply_transformations(
        self, 
        data: Dict[str, Any], 
        transformations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply data transformations."""
        transformed_data = data.copy()
        
        for transformation in transformations:
            transform_type = transformation.get('type')
            field = transformation.get('field')
            
            if transform_type == 'rename':
                old_name = transformation.get('from')
                new_name = transformation.get('to')
                if old_name in transformed_data:
                    transformed_data[new_name] = transformed_data.pop(old_name)
            
            elif transform_type == 'format':
                format_str = transformation.get('format')
                if field in transformed_data:
                    transformed_data[field] = format_str.format(transformed_data[field])
            
            elif transform_type == 'default':
                default_value = transformation.get('value')
                if field not in transformed_data or transformed_data[field] is None:
                    transformed_data[field] = default_value
        
        return transformed_data
    
    def _apply_field_mappings(
        self, 
        data: Dict[str, Any], 
        field_mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """Apply field mappings."""
        mapped_data = {}
        
        for source_field, target_field in field_mappings.items():
            if source_field in data:
                mapped_data[target_field] = data[source_field]
        
        # Include unmapped fields
        for field, value in data.items():
            if field not in field_mappings and field not in mapped_data:
                mapped_data[field] = value
        
        return mapped_data
    
    async def _create_platform_record(
        self, 
        adapter -> None: Any, 
        data -> None: Dict[str, Any]
    ) -> None:
        """Create record in platform."""
        if hasattr(adapter, 'create_record'):
            return await adapter.create_record(data)
        else:
            raise ValueError("Adapter does not support record creation")
    
    async def _update_platform_record(
        self, 
        adapter -> None: Any, 
        record_id -> None: str, 
        data -> None: Dict[str, Any]
    ) -> None:
        """Update record in platform."""
        if hasattr(adapter, 'update_record'):
            return await adapter.update_record(record_id, data)
        else:
            raise ValueError("Adapter does not support record updates")
    
    async def _update_job_status(self, job -> None: SyncJob) -> None:
        """Update job status in database."""
        async with self.async_session() as session:
            result = await session.execute(
                sa.select(SyncJobModel).where(SyncJobModel.id == job.id)
            )
            db_job = result.scalar_one_or_none()
            
            if db_job:
                db_job.status = job.status.value
                db_job.started_at = job.started_at
                db_job.completed_at = job.completed_at
                db_job.records_processed = job.records_processed
                db_job.records_synced = job.records_synced
                db_job.records_failed = job.records_failed
                db_job.errors = json.dumps(job.errors)
                db_job.metadata = json.dumps(job.metadata)
                
                await session.commit()
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get synchronization job status."""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                'id': job.id,
                'rule_id': job.rule_id,
                'status': job.status.value,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'records_processed': job.records_processed,
                'records_synced': job.records_synced,
                'records_failed': job.records_failed,
                'errors': job.errors
            }
        
        # Check database
        async with self.async_session() as session:
            result = await session.execute(
                sa.select(SyncJobModel).where(SyncJobModel.id == job_id)
            )
            db_job = result.scalar_one_or_none()
            
            if db_job:
                return {
                    'id': db_job.id,
                    'rule_id': db_job.rule_id,
                    'status': db_job.status,
                    'started_at': db_job.started_at.isoformat() if db_job.started_at else None,
                    'completed_at': db_job.completed_at.isoformat() if db_job.completed_at else None,
                    'records_processed': db_job.records_processed,
                    'records_synced': db_job.records_synced,
                    'records_failed': db_job.records_failed,
                    'errors': json.loads(db_job.errors) if db_job.errors else []
                }
        
        return None
    
    def get_sync_metrics(self) -> Dict[str, Any]:
        """Get synchronization metrics."""
        return self.sync_metrics.copy()
    
    async def cleanup_completed_jobs(self, older_than_days -> None: int = 7) -> None:
        """Clean up completed jobs older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        async with self.async_session() as session:
            result = await session.execute(
                sa.delete(SyncJobModel).where(
                    sa.and_(
                        SyncJobModel.status.in_(['completed', 'failed']),
                        SyncJobModel.completed_at < cutoff_date
                    )
                )
            )
            await session.commit()
            
            self.logger.info(f"Cleaned up {result.rowcount} old sync jobs")


# Example platform adapter interface
class PlatformAdapter:
    """Base platform adapter interface."""
    
    async def fetch_data(
        self, 
        data_type: str, 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fetch data from platform."""
        raise NotImplementedError
    
    async def create_record(self, data: Dict[str, Any]) -> str:
        """Create record in platform."""
        raise NotImplementedError
    
    async def update_record(self, record_id -> None: str, data -> None: Dict[str, Any]) -> None:
        """Update record in platform."""
        raise NotImplementedError
    
    async def delete_record(self, record_id -> None: str) -> None:
        """Delete record from platform."""
        raise NotImplementedError


# Example usage
if __name__ == "__main__":
    async def main() -> None:
        # Initialize sync engine
        sync_engine = DataSyncEngine(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await sync_engine.initialize()
        
        # Register platform adapters
        # sync_engine.register_platform_adapter("platform1", adapter1)
        # sync_engine.register_platform_adapter("platform2", adapter2)
        
        # Create sync rule
        sync_rule = SyncRule(
            id=str(uuid.uuid4()),
            name="User Profile Sync",
            source_platform="platform1",
            target_platform="platform2",
            data_type="user_profiles",
            direction=SyncDirection.BIDIRECTIONAL,
            schedule="0 */6 * * *",  # Every 6 hours
            conflict_resolution=ConflictResolution.LATEST_WINS,
            field_mappings={
                "full_name": "name",
                "email_address": "email"
            }
        )
        
        sync_engine.add_sync_rule(sync_rule)
        
        # Start scheduler
        await sync_engine.start_scheduler()
        
        # Keep running
        await asyncio.sleep(3600)
        
        await sync_engine.stop_scheduler()
    
    asyncio.run(main())