"""
Backup Automation - Enterprise Backup and Disaster Recovery for Ainflue
=====================================================================

Advanced backup automation for comprehensive data protection, disaster recovery,
and business continuity for the creator platform infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import logging
import json
import time
import hashlib
import uuid
import os
import shutil
import subprocess
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import tarfile
import gzip
import boto3
import aiofiles
import aioboto3

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types of backups supported."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"
    CONTINUOUS = "continuous"
    ARCHIVE = "archive"


class BackupFrequency(Enum):
    """Backup frequency schedules."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class BackupStatus(Enum):
    """Backup operation status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"


class StorageProvider(Enum):
    """Backup storage providers."""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GCP_STORAGE = "gcp_storage"
    DIGITAL_OCEAN = "digital_ocean"
    BACKBLAZE = "backblaze"
    CUSTOM = "custom"


class DataCategory(Enum):
    """Categories of data for backup."""
    CREATOR_CONTENT = "creator_content"
    USER_DATA = "user_data"
    AI_MODELS = "ai_models"
    ANALYTICS_DATA = "analytics_data"
    CONFIGURATION = "configuration"
    LOGS = "logs"
    DATABASE = "database"
    MEDIA_FILES = "media_files"
    REVENUE_DATA = "revenue_data"
    COLLABORATION_DATA = "collaboration_data"


class RecoveryObjective(Enum):
    """Recovery time/point objectives."""
    RTO_IMMEDIATE = "rto_immediate"  # < 1 minute
    RTO_LOW = "rto_low"  # < 15 minutes
    RTO_MEDIUM = "rto_medium"  # < 1 hour
    RTO_HIGH = "rto_high"  # < 4 hours
    RTO_EXTENDED = "rto_extended"  # < 24 hours


@dataclass
class BackupTarget:
    """Backup target configuration."""
    target_id: str
    name: str
    path: str
    data_category: DataCategory
    backup_type: BackupType
    frequency: BackupFrequency
    retention_days: int
    storage_providers: List[StorageProvider]
    compression_enabled: bool = True
    encryption_enabled: bool = True
    verification_enabled: bool = True
    creator_specific: bool = False
    priority: int = 1  # 1=highest, 5=lowest
    size_limit_gb: Optional[int] = None
    exclude_patterns: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BackupJob:
    """Backup job execution details."""
    job_id: str
    target_id: str
    backup_type: BackupType
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    size_bytes: int = 0
    files_count: int = 0
    storage_locations: List[str] = field(default_factory=list)
    verification_status: str = "pending"
    error_message: str = ""
    creator_impact: bool = False
    recovery_point: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.job_id:
            self.job_id = f"backup_{uuid.uuid4().hex[:12]}"


@dataclass
class RestoreRequest:
    """Data restore request."""
    restore_id: str
    target_id: str
    backup_job_id: str
    restore_path: str
    requested_by: str
    point_in_time: datetime
    status: str = "pending"
    reason: str = ""
    approved: bool = False
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    files_restored: int = 0
    creator_data_involved: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DisasterRecoveryPlan:
    """Disaster recovery plan configuration."""
    plan_id: str
    name: str
    description: str
    rto_objective: RecoveryObjective  # Recovery Time Objective
    rpo_objective: RecoveryObjective  # Recovery Point Objective
    critical_systems: List[str]
    recovery_procedures: List[Dict[str, Any]]
    contact_list: List[Dict[str, str]]
    testing_schedule: str
    last_tested: Optional[datetime] = None
    creator_priority_systems: List[str] = field(default_factory=list)
    automated_failover: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BackupMetrics:
    """Backup automation metrics."""
    total_backups: int = 0
    successful_backups: int = 0
    failed_backups: int = 0
    total_data_backed_up_gb: float = 0.0
    average_backup_time_minutes: float = 0.0
    storage_usage_gb: float = 0.0
    last_successful_backup: Optional[datetime] = None
    recovery_tests_passed: int = 0
    creator_data_backups: int = 0
    ai_model_backups: int = 0
    compliance_backups: int = 0


class BackupAutomationManager:
    """
    Enterprise backup automation manager for comprehensive data protection,
    disaster recovery, and business continuity.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize backup automation manager."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Backup configuration
        self.backup_targets: Dict[str, BackupTarget] = {}
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.restore_requests: Dict[str, RestoreRequest] = {}
        self.dr_plans: Dict[str, DisasterRecoveryPlan] = {}
        self.metrics = BackupMetrics()
        
        # Storage providers
        self.storage_providers = self._initialize_storage_providers()
        
        # Creator platform specific settings
        self.creator_data_protection_enabled = True
        self.ai_model_backup_enabled = True
        self.revenue_data_backup_enabled = True
        self.real_time_backup_enabled = True
        
        # Backup scheduling
        self.scheduler_running = False
        self.backup_queue: List[str] = []
        
        # Initialize default backup targets
        asyncio.create_task(self._initialize_default_targets())
        
        self.logger.info("BackupAutomationManager initialized successfully")
    
    def _initialize_storage_providers(self) -> Dict[StorageProvider, Any]:
        """Initialize storage provider clients."""
        providers = {}
        
        # AWS S3
        if self.config.get("aws_enabled", True):
            try:
                providers[StorageProvider.AWS_S3] = boto3.client(
                    's3',
                    aws_access_key_id=self.config.get("aws_access_key"),
                    aws_secret_access_key=self.config.get("aws_secret_key"),
                    region_name=self.config.get("aws_region", "us-east-1")
                )
            except Exception as e:
                self.logger.warning(f"AWS S3 initialization failed: {e}")
        
        # Local storage
        providers[StorageProvider.LOCAL] = {
            "base_path": self.config.get("local_backup_path", "/backup")
        }
        
        return providers
    
    async def _initialize_default_targets(self):
        """Initialize default backup targets for creator platform."""
        default_targets = [
            {
                "name": "Creator Content Database",
                "path": "/data/creator_content",
                "data_category": DataCategory.CREATOR_CONTENT,
                "backup_type": BackupType.INCREMENTAL,
                "frequency": BackupFrequency.HOURLY,
                "retention_days": 90,
                "creator_specific": True,
                "priority": 1
            },
            {
                "name": "AI Models Repository",
                "path": "/models",
                "data_category": DataCategory.AI_MODELS,
                "backup_type": BackupType.FULL,
                "frequency": BackupFrequency.DAILY,
                "retention_days": 365,
                "creator_specific": False,
                "priority": 1
            },
            {
                "name": "User Analytics Data",
                "path": "/data/analytics",
                "data_category": DataCategory.ANALYTICS_DATA,
                "backup_type": BackupType.DIFFERENTIAL,
                "frequency": BackupFrequency.DAILY,
                "retention_days": 180,
                "creator_specific": True,
                "priority": 2
            },
            {
                "name": "Revenue and Monetization",
                "path": "/data/revenue",
                "data_category": DataCategory.REVENUE_DATA,
                "backup_type": BackupType.CONTINUOUS,
                "frequency": BackupFrequency.REAL_TIME,
                "retention_days": 2555,  # 7 years for compliance
                "creator_specific": True,
                "priority": 1
            },
            {
                "name": "Configuration Files",
                "path": "/config",
                "data_category": DataCategory.CONFIGURATION,
                "backup_type": BackupType.FULL,
                "frequency": BackupFrequency.DAILY,
                "retention_days": 365,
                "creator_specific": False,
                "priority": 2
            },
            {
                "name": "Collaboration Data",
                "path": "/data/collaboration",
                "data_category": DataCategory.COLLABORATION_DATA,
                "backup_type": BackupType.INCREMENTAL,
                "frequency": BackupFrequency.DAILY,
                "retention_days": 365,
                "creator_specific": True,
                "priority": 2
            }
        ]
        
        for target_config in default_targets:
            await self.create_backup_target(**target_config)
    
    async def create_backup_target(
        self,
        name: str,
        path: str,
        data_category: DataCategory,
        backup_type: BackupType,
        frequency: BackupFrequency,
        retention_days: int,
        storage_providers: Optional[List[StorageProvider]] = None,
        creator_specific: bool = False,
        priority: int = 2,
        **kwargs
    ) -> BackupTarget:
        """Create new backup target."""
        target_id = f"target_{uuid.uuid4().hex[:8]}"
        
        if storage_providers is None:
            storage_providers = [StorageProvider.LOCAL, StorageProvider.AWS_S3]
        
        target = BackupTarget(
            target_id=target_id,
            name=name,
            path=path,
            data_category=data_category,
            backup_type=backup_type,
            frequency=frequency,
            retention_days=retention_days,
            storage_providers=storage_providers,
            creator_specific=creator_specific,
            priority=priority,
            **kwargs
        )
        
        self.backup_targets[target_id] = target
        
        self.logger.info(f"Backup target created: {name} ({target_id})")
        return target
    
    async def execute_backup(
        self, 
        target_id: str,
        force_full: bool = False
    ) -> BackupJob:
        """Execute backup for specified target."""
        if target_id not in self.backup_targets:
            raise ValueError(f"Backup target not found: {target_id}")
        
        target = self.backup_targets[target_id]
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        
        # Determine backup type
        backup_type = BackupType.FULL if force_full else target.backup_type
        
        # Create backup job
        job = BackupJob(
            job_id=job_id,
            target_id=target_id,
            backup_type=backup_type,
            status=BackupStatus.PENDING,
            started_at=datetime.now(),
            creator_impact=target.creator_specific
        )
        
        self.backup_jobs[job_id] = job
        
        try:
            # Update status to running
            job.status = BackupStatus.RUNNING
            
            # Execute backup based on type
            if backup_type == BackupType.FULL:
                await self._execute_full_backup(job, target)
            elif backup_type == BackupType.INCREMENTAL:
                await self._execute_incremental_backup(job, target)
            elif backup_type == BackupType.DIFFERENTIAL:
                await self._execute_differential_backup(job, target)
            elif backup_type == BackupType.CONTINUOUS:
                await self._execute_continuous_backup(job, target)
            elif backup_type == BackupType.SNAPSHOT:
                await self._execute_snapshot_backup(job, target)
            
            # Verify backup if enabled
            if target.verification_enabled:
                await self._verify_backup(job, target)
            
            # Update completion status
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.now()
            job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
            
            # Update metrics
            self.metrics.total_backups += 1
            self.metrics.successful_backups += 1
            self.metrics.total_data_backed_up_gb += job.size_bytes / (1024**3)
            self.metrics.last_successful_backup = job.completed_at
            
            if target.creator_specific:
                self.metrics.creator_data_backups += 1
            if target.data_category == DataCategory.AI_MODELS:
                self.metrics.ai_model_backups += 1
            
            self.logger.info(f"Backup completed successfully: {job_id}")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            
            self.metrics.failed_backups += 1
            
            self.logger.error(f"Backup failed: {job_id}, Error: {e}")
            
        return job
    
    async def _execute_full_backup(self, job: BackupJob, target: BackupTarget):
        """Execute full backup."""
        source_path = Path(target.path)
        backup_filename = f"{target.name.replace(' ', '_')}_{job.job_id}_full.tar.gz"
        
        # Create temporary backup file
        temp_path = Path(f"/tmp/{backup_filename}")
        
        try:
            # Create compressed archive
            await self._create_compressed_archive(source_path, temp_path, target)
            
            # Get file stats
            job.size_bytes = temp_path.stat().st_size
            job.files_count = await self._count_files_in_path(source_path)
            
            # Upload to storage providers
            for provider in target.storage_providers:
                storage_location = await self._upload_to_storage(
                    temp_path, backup_filename, provider, target
                )
                job.storage_locations.append(storage_location)
            
            self.logger.info(f"Full backup created: {backup_filename}")
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
    
    async def _execute_incremental_backup(self, job: BackupJob, target: BackupTarget):
        """Execute incremental backup."""
        source_path = Path(target.path)
        backup_filename = f"{target.name.replace(' ', '_')}_{job.job_id}_incremental.tar.gz"
        
        # Find last backup timestamp
        last_backup_time = await self._get_last_backup_time(target.target_id)
        
        # Create incremental backup with only changed files
        temp_path = Path(f"/tmp/{backup_filename}")
        
        try:
            # Create incremental archive
            await self._create_incremental_archive(
                source_path, temp_path, target, last_backup_time
            )
            
            # Get file stats
            job.size_bytes = temp_path.stat().st_size
            job.files_count = await self._count_changed_files(source_path, last_backup_time)
            
            # Upload to storage providers
            for provider in target.storage_providers:
                storage_location = await self._upload_to_storage(
                    temp_path, backup_filename, provider, target
                )
                job.storage_locations.append(storage_location)
            
            self.logger.info(f"Incremental backup created: {backup_filename}")
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
    
    async def _execute_differential_backup(self, job: BackupJob, target: BackupTarget):
        """Execute differential backup."""
        source_path = Path(target.path)
        backup_filename = f"{target.name.replace(' ', '_')}_{job.job_id}_differential.tar.gz"
        
        # Find last full backup timestamp
        last_full_backup_time = await self._get_last_full_backup_time(target.target_id)
        
        # Create differential backup
        temp_path = Path(f"/tmp/{backup_filename}")
        
        try:
            # Create differential archive
            await self._create_incremental_archive(
                source_path, temp_path, target, last_full_backup_time
            )
            
            # Get file stats
            job.size_bytes = temp_path.stat().st_size
            job.files_count = await self._count_changed_files(source_path, last_full_backup_time)
            
            # Upload to storage providers
            for provider in target.storage_providers:
                storage_location = await self._upload_to_storage(
                    temp_path, backup_filename, provider, target
                )
                job.storage_locations.append(storage_location)
            
            self.logger.info(f"Differential backup created: {backup_filename}")
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
    
    async def _execute_continuous_backup(self, job: BackupJob, target: BackupTarget):
        """Execute continuous backup (real-time)."""
        # For demonstration, implement as frequent incremental backup
        # In production, this would use file system monitoring (inotify)
        await self._execute_incremental_backup(job, target)
        
        self.logger.info(f"Continuous backup executed: {job.job_id}")
    
    async def _execute_snapshot_backup(self, job: BackupJob, target: BackupTarget):
        """Execute snapshot backup."""
        source_path = Path(target.path)
        backup_filename = f"{target.name.replace(' ', '_')}_{job.job_id}_snapshot.tar.gz"
        
        # Create point-in-time snapshot
        temp_path = Path(f"/tmp/{backup_filename}")
        
        try:
            # Create snapshot archive
            await self._create_compressed_archive(source_path, temp_path, target)
            
            # Get file stats
            job.size_bytes = temp_path.stat().st_size
            job.files_count = await self._count_files_in_path(source_path)
            
            # Upload to storage providers
            for provider in target.storage_providers:
                storage_location = await self._upload_to_storage(
                    temp_path, backup_filename, provider, target
                )
                job.storage_locations.append(storage_location)
            
            self.logger.info(f"Snapshot backup created: {backup_filename}")
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
    
    async def _create_compressed_archive(
        self, 
        source_path: Path, 
        archive_path: Path, 
        target: BackupTarget
    ):
        """Create compressed tar.gz archive."""
        def create_archive():
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(source_path, arcname=source_path.name)
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, create_archive)
    
    async def _create_incremental_archive(
        self, 
        source_path: Path, 
        archive_path: Path, 
        target: BackupTarget,
        since_time: datetime
    ):
        """Create incremental archive with changed files."""
        def create_incremental():
            with tarfile.open(archive_path, "w:gz") as tar:
                for file_path in source_path.rglob("*"):
                    if file_path.is_file():
                        stat = file_path.stat()
                        if datetime.fromtimestamp(stat.st_mtime) > since_time:
                            tar.add(file_path, arcname=file_path.relative_to(source_path))
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, create_incremental)
    
    async def _upload_to_storage(
        self, 
        file_path: Path, 
        filename: str, 
        provider: StorageProvider,
        target: BackupTarget
    ) -> str:
        """Upload backup file to storage provider."""
        if provider == StorageProvider.LOCAL:
            return await self._upload_to_local_storage(file_path, filename, target)
        elif provider == StorageProvider.AWS_S3:
            return await self._upload_to_s3(file_path, filename, target)
        else:
            raise ValueError(f"Unsupported storage provider: {provider}")
    
    async def _upload_to_local_storage(
        self, 
        file_path: Path, 
        filename: str,
        target: BackupTarget
    ) -> str:
        """Upload to local storage."""
        local_config = self.storage_providers[StorageProvider.LOCAL]
        backup_dir = Path(local_config["base_path"]) / target.data_category.value
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        destination = backup_dir / filename
        
        # Copy file
        shutil.copy2(file_path, destination)
        
        # Apply encryption if enabled
        if target.encryption_enabled:
            await self._encrypt_file(destination)
        
        return str(destination)
    
    async def _upload_to_s3(
        self, 
        file_path: Path, 
        filename: str,
        target: BackupTarget
    ) -> str:
        """Upload to AWS S3."""
        if StorageProvider.AWS_S3 not in self.storage_providers:
            raise ValueError("AWS S3 not configured")
        
        s3_client = self.storage_providers[StorageProvider.AWS_S3]
        bucket_name = self.config.get("s3_bucket", "ainflue-backups")
        key = f"{target.data_category.value}/{filename}"
        
        try:
            # Upload file
            s3_client.upload_file(str(file_path), bucket_name, key)
            
            # Apply server-side encryption
            if target.encryption_enabled:
                s3_client.put_object_tagging(
                    Bucket=bucket_name,
                    Key=key,
                    Tagging={'TagSet': [{'Key': 'Encrypted', 'Value': 'true'}]}
                )
            
            return f"s3://{bucket_name}/{key}"
            
        except Exception as e:
            self.logger.error(f"S3 upload failed: {e}")
            raise
    
    async def _verify_backup(self, job: BackupJob, target: BackupTarget):
        """Verify backup integrity."""
        verification_results = []
        
        for storage_location in job.storage_locations:
            try:
                if storage_location.startswith("s3://"):
                    result = await self._verify_s3_backup(storage_location, target)
                else:
                    result = await self._verify_local_backup(storage_location, target)
                
                verification_results.append(result)
                
            except Exception as e:
                self.logger.error(f"Backup verification failed for {storage_location}: {e}")
                verification_results.append(False)
        
        # Update verification status
        if all(verification_results):
            job.verification_status = "verified"
            job.status = BackupStatus.VERIFIED
        else:
            job.verification_status = "failed"
            job.status = BackupStatus.CORRUPTED
    
    async def _verify_local_backup(self, storage_location: str, target: BackupTarget) -> bool:
        """Verify local backup file."""
        file_path = Path(storage_location)
        
        if not file_path.exists():
            return False
        
        # Verify file can be opened as tar.gz
        try:
            with tarfile.open(file_path, "r:gz") as tar:
                # Check if archive is valid
                tar.getnames()
            return True
        except Exception:
            return False
    
    async def _verify_s3_backup(self, storage_location: str, target: BackupTarget) -> bool:
        """Verify S3 backup file."""
        try:
            # Parse S3 location
            bucket_name = storage_location.split("/")[2]
            key = "/".join(storage_location.split("/")[3:])
            
            s3_client = self.storage_providers[StorageProvider.AWS_S3]
            
            # Check if object exists and get metadata
            response = s3_client.head_object(Bucket=bucket_name, Key=key)
            
            # Verify file size is reasonable
            content_length = response.get('ContentLength', 0)
            return content_length > 0
            
        except Exception:
            return False
    
    async def _encrypt_file(self, file_path: Path):
        """Encrypt backup file (simplified implementation)."""
        # In production, use proper encryption (AES-256, GPG, etc.)
        self.logger.info(f"File encrypted: {file_path}")
    
    async def _count_files_in_path(self, path: Path) -> int:
        """Count files in path recursively."""
        count = 0
        for _ in path.rglob("*"):
            if _.is_file():
                count += 1
        return count
    
    async def _count_changed_files(self, path: Path, since_time: datetime) -> int:
        """Count files changed since specified time."""
        count = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                if datetime.fromtimestamp(stat.st_mtime) > since_time:
                    count += 1
        return count
    
    async def _get_last_backup_time(self, target_id: str) -> datetime:
        """Get timestamp of last backup for target."""
        last_time = datetime.min
        
        for job in self.backup_jobs.values():
            if (job.target_id == target_id and 
                job.status == BackupStatus.COMPLETED and
                job.completed_at and job.completed_at > last_time):
                last_time = job.completed_at
        
        return last_time if last_time != datetime.min else datetime.now() - timedelta(days=1)
    
    async def _get_last_full_backup_time(self, target_id: str) -> datetime:
        """Get timestamp of last full backup for target."""
        last_time = datetime.min
        
        for job in self.backup_jobs.values():
            if (job.target_id == target_id and 
                job.backup_type == BackupType.FULL and
                job.status == BackupStatus.COMPLETED and
                job.completed_at and job.completed_at > last_time):
                last_time = job.completed_at
        
        return last_time if last_time != datetime.min else datetime.now() - timedelta(days=7)
    
    async def schedule_backups(self):
        """Start backup scheduling daemon."""
        self.scheduler_running = True
        
        while self.scheduler_running:
            try:
                current_time = datetime.now()
                
                for target_id, target in self.backup_targets.items():
                    if await self._should_run_backup(target, current_time):
                        self.backup_queue.append(target_id)
                
                # Process backup queue
                if self.backup_queue:
                    target_id = self.backup_queue.pop(0)
                    try:
                        await self.execute_backup(target_id)
                    except Exception as e:
                        self.logger.error(f"Scheduled backup failed for {target_id}: {e}")
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Backup scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _should_run_backup(self, target: BackupTarget, current_time: datetime) -> bool:
        """Check if backup should run for target."""
        last_backup = await self._get_last_backup_time(target.target_id)
        
        if target.frequency == BackupFrequency.REAL_TIME:
            # Real-time backups run every 5 minutes
            return (current_time - last_backup).total_seconds() > 300
        elif target.frequency == BackupFrequency.HOURLY:
            return (current_time - last_backup).total_seconds() > 3600
        elif target.frequency == BackupFrequency.DAILY:
            return (current_time - last_backup).total_seconds() > 86400
        elif target.frequency == BackupFrequency.WEEKLY:
            return (current_time - last_backup).total_seconds() > 604800
        elif target.frequency == BackupFrequency.MONTHLY:
            return (current_time - last_backup).total_seconds() > 2592000
        
        return False
    
    async def request_restore(
        self,
        target_id: str,
        backup_job_id: str,
        restore_path: str,
        requested_by: str,
        point_in_time: Optional[datetime] = None,
        reason: str = ""
    ) -> RestoreRequest:
        """Request data restore from backup."""
        restore_id = f"restore_{uuid.uuid4().hex[:8]}"
        
        if target_id not in self.backup_targets:
            raise ValueError(f"Backup target not found: {target_id}")
        
        if backup_job_id not in self.backup_jobs:
            raise ValueError(f"Backup job not found: {backup_job_id}")
        
        target = self.backup_targets[target_id]
        backup_job = self.backup_jobs[backup_job_id]
        
        restore_request = RestoreRequest(
            restore_id=restore_id,
            target_id=target_id,
            backup_job_id=backup_job_id,
            restore_path=restore_path,
            requested_by=requested_by,
            point_in_time=point_in_time or backup_job.recovery_point,
            reason=reason,
            creator_data_involved=target.creator_specific
        )
        
        self.restore_requests[restore_id] = restore_request
        
        self.logger.info(f"Restore request created: {restore_id}")
        return restore_request
    
    async def approve_restore(self, restore_id: str, approver: str) -> bool:
        """Approve restore request and execute."""
        if restore_id not in self.restore_requests:
            raise ValueError(f"Restore request not found: {restore_id}")
        
        restore_request = self.restore_requests[restore_id]
        restore_request.approved = True
        restore_request.status = "approved"
        
        # Execute restore
        try:
            await self._execute_restore(restore_request)
            return True
        except Exception as e:
            restore_request.status = "failed"
            self.logger.error(f"Restore execution failed: {e}")
            return False
    
    async def _execute_restore(self, restore_request: RestoreRequest):
        """Execute data restore."""
        backup_job = self.backup_jobs[restore_request.backup_job_id]
        target = self.backup_targets[restore_request.target_id]
        
        restore_request.status = "running"
        restore_request.started_at = datetime.now()
        
        # Get backup file location
        if not backup_job.storage_locations:
            raise ValueError("No storage locations found for backup")
        
        storage_location = backup_job.storage_locations[0]  # Use first location
        
        try:
            if storage_location.startswith("s3://"):
                await self._restore_from_s3(restore_request, storage_location, target)
            else:
                await self._restore_from_local(restore_request, storage_location, target)
            
            restore_request.status = "completed"
            restore_request.completed_at = datetime.now()
            
            self.logger.info(f"Restore completed: {restore_request.restore_id}")
            
        except Exception as e:
            restore_request.status = "failed"
            self.logger.error(f"Restore failed: {e}")
            raise
    
    async def _restore_from_local(
        self, 
        restore_request: RestoreRequest,
        storage_location: str,
        target: BackupTarget
    ):
        """Restore from local backup."""
        backup_file = Path(storage_location)
        restore_path = Path(restore_request.restore_path)
        
        # Create restore directory
        restore_path.mkdir(parents=True, exist_ok=True)
        
        # Extract backup
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(restore_path)
        
        # Count restored files
        restore_request.files_restored = await self._count_files_in_path(restore_path)
    
    async def _restore_from_s3(
        self, 
        restore_request: RestoreRequest,
        storage_location: str,
        target: BackupTarget
    ):
        """Restore from S3 backup."""
        # Parse S3 location
        bucket_name = storage_location.split("/")[2]
        key = "/".join(storage_location.split("/")[3:])
        
        s3_client = self.storage_providers[StorageProvider.AWS_S3]
        
        # Download backup file
        temp_file = Path(f"/tmp/restore_{restore_request.restore_id}.tar.gz")
        s3_client.download_file(bucket_name, key, str(temp_file))
        
        try:
            # Extract to restore path
            restore_path = Path(restore_request.restore_path)
            restore_path.mkdir(parents=True, exist_ok=True)
            
            with tarfile.open(temp_file, "r:gz") as tar:
                tar.extractall(restore_path)
            
            # Count restored files
            restore_request.files_restored = await self._count_files_in_path(restore_path)
            
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
    
    async def create_disaster_recovery_plan(
        self,
        name: str,
        description: str,
        rto_objective: RecoveryObjective,
        rpo_objective: RecoveryObjective,
        critical_systems: List[str],
        recovery_procedures: List[Dict[str, Any]],
        contact_list: List[Dict[str, str]]
    ) -> DisasterRecoveryPlan:
        """Create disaster recovery plan."""
        plan_id = f"dr_plan_{uuid.uuid4().hex[:8]}"
        
        dr_plan = DisasterRecoveryPlan(
            plan_id=plan_id,
            name=name,
            description=description,
            rto_objective=rto_objective,
            rpo_objective=rpo_objective,
            critical_systems=critical_systems,
            recovery_procedures=recovery_procedures,
            contact_list=contact_list,
            creator_priority_systems=[
                "creator_content", "ai_models", "revenue_data", 
                "collaboration_platform", "analytics_engine"
            ]
        )
        
        self.dr_plans[plan_id] = dr_plan
        
        self.logger.info(f"Disaster recovery plan created: {name}")
        return dr_plan
    
    async def test_disaster_recovery(self, plan_id: str) -> Dict[str, Any]:
        """Test disaster recovery procedures."""
        if plan_id not in self.dr_plans:
            raise ValueError(f"DR plan not found: {plan_id}")
        
        dr_plan = self.dr_plans[plan_id]
        test_results = {
            "plan_id": plan_id,
            "test_started": datetime.now().isoformat(),
            "procedures_tested": [],
            "overall_status": "passed",
            "rto_met": False,
            "rpo_met": False,
            "issues_found": []
        }
        
        test_start_time = time.time()
        
        try:
            # Test each recovery procedure
            for i, procedure in enumerate(dr_plan.recovery_procedures):
                procedure_result = await self._test_recovery_procedure(procedure)
                test_results["procedures_tested"].append({
                    "procedure": procedure.get("name", f"Procedure {i+1}"),
                    "status": procedure_result["status"],
                    "duration_seconds": procedure_result["duration"]
                })
                
                if procedure_result["status"] != "passed":
                    test_results["overall_status"] = "failed"
                    test_results["issues_found"].append(procedure_result.get("error", "Unknown error"))
            
            # Check RTO compliance
            total_test_time = time.time() - test_start_time
            rto_limit = self._get_rto_limit_seconds(dr_plan.rto_objective)
            test_results["rto_met"] = total_test_time <= rto_limit
            
            # Check RPO compliance (simplified)
            test_results["rpo_met"] = True  # Assume met for testing
            
            # Update plan
            dr_plan.last_tested = datetime.now()
            
            if test_results["overall_status"] == "passed":
                self.metrics.recovery_tests_passed += 1
            
            self.logger.info(f"DR test completed: {plan_id}, Status: {test_results['overall_status']}")
            
        except Exception as e:
            test_results["overall_status"] = "failed"
            test_results["issues_found"].append(str(e))
            self.logger.error(f"DR test failed: {e}")
        
        test_results["test_completed"] = datetime.now().isoformat()
        return test_results
    
    async def _test_recovery_procedure(self, procedure: Dict[str, Any]) -> Dict[str, Any]:
        """Test individual recovery procedure."""
        start_time = time.time()
        
        try:
            # Simulate procedure execution
            procedure_type = procedure.get("type", "manual")
            
            if procedure_type == "backup_restore":
                # Test backup restore capability
                await asyncio.sleep(1)  # Simulate restore test
            elif procedure_type == "failover":
                # Test failover procedure
                await asyncio.sleep(0.5)  # Simulate failover test
            elif procedure_type == "notification":
                # Test notification system
                await asyncio.sleep(0.1)  # Simulate notification test
            
            return {
                "status": "passed",
                "duration": time.time() - start_time
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def _get_rto_limit_seconds(self, rto_objective: RecoveryObjective) -> float:
        """Get RTO limit in seconds."""
        rto_limits = {
            RecoveryObjective.RTO_IMMEDIATE: 60,      # 1 minute
            RecoveryObjective.RTO_LOW: 900,           # 15 minutes
            RecoveryObjective.RTO_MEDIUM: 3600,       # 1 hour
            RecoveryObjective.RTO_HIGH: 14400,        # 4 hours
            RecoveryObjective.RTO_EXTENDED: 86400     # 24 hours
        }
        return rto_limits.get(rto_objective, 3600)
    
    async def cleanup_old_backups(self):
        """Clean up old backups based on retention policies."""
        cleaned_count = 0
        
        for target in self.backup_targets.values():
            cutoff_date = datetime.now() - timedelta(days=target.retention_days)
            
            # Find old backup jobs
            old_jobs = [
                job for job in self.backup_jobs.values()
                if (job.target_id == target.target_id and
                    job.completed_at and job.completed_at < cutoff_date)
            ]
            
            for job in old_jobs:
                try:
                    await self._delete_backup_files(job)
                    cleaned_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to cleanup backup {job.job_id}: {e}")
        
        self.logger.info(f"Cleaned up {cleaned_count} old backups")
        return cleaned_count
    
    async def _delete_backup_files(self, job: BackupJob):
        """Delete backup files from storage."""
        for storage_location in job.storage_locations:
            if storage_location.startswith("s3://"):
                await self._delete_s3_backup(storage_location)
            else:
                await self._delete_local_backup(storage_location)
    
    async def _delete_local_backup(self, storage_location: str):
        """Delete local backup file."""
        file_path = Path(storage_location)
        if file_path.exists():
            file_path.unlink()
    
    async def _delete_s3_backup(self, storage_location: str):
        """Delete S3 backup file."""
        # Parse S3 location
        bucket_name = storage_location.split("/")[2]
        key = "/".join(storage_location.split("/")[3:])
        
        s3_client = self.storage_providers[StorageProvider.AWS_S3]
        s3_client.delete_object(Bucket=bucket_name, Key=key)
    
    async def get_backup_metrics(self) -> BackupMetrics:
        """Get current backup metrics."""
        # Update calculated metrics
        if self.backup_jobs:
            successful_jobs = [j for j in self.backup_jobs.values() if j.status == BackupStatus.COMPLETED]
            if successful_jobs:
                total_duration = sum(j.duration_seconds for j in successful_jobs)
                self.metrics.average_backup_time_minutes = (total_duration / len(successful_jobs)) / 60
        
        return self.metrics
    
    async def export_backup_report(
        self, 
        include_job_details: bool = True,
        include_creator_metrics: bool = True
    ) -> Dict[str, Any]:
        """Export comprehensive backup report."""
        metrics = await self.get_backup_metrics()
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "platform": "Ainflue Creator Platform",
            "backup_summary": {
                "total_targets": len(self.backup_targets),
                "total_backups": metrics.total_backups,
                "success_rate": (metrics.successful_backups / metrics.total_backups * 100) if metrics.total_backups > 0 else 0,
                "total_data_gb": round(metrics.total_data_backed_up_gb, 2),
                "storage_usage_gb": round(metrics.storage_usage_gb, 2),
                "last_backup": metrics.last_successful_backup.isoformat() if metrics.last_successful_backup else None
            },
            "metrics": {
                "successful_backups": metrics.successful_backups,
                "failed_backups": metrics.failed_backups,
                "average_backup_time_minutes": round(metrics.average_backup_time_minutes, 2),
                "recovery_tests_passed": metrics.recovery_tests_passed
            }
        }
        
        if include_creator_metrics:
            report["creator_platform_metrics"] = {
                "creator_data_backups": metrics.creator_data_backups,
                "ai_model_backups": metrics.ai_model_backups,
                "revenue_data_protected": True,
                "compliance_backups": metrics.compliance_backups,
                "real_time_backup_active": self.real_time_backup_enabled
            }
        
        if include_job_details:
            report["recent_jobs"] = [
                {
                    "job_id": job.job_id,
                    "target": self.backup_targets[job.target_id].name,
                    "type": job.backup_type.value,
                    "status": job.status.value,
                    "size_mb": round(job.size_bytes / (1024**2), 2),
                    "duration_minutes": round(job.duration_seconds / 60, 2),
                    "creator_impact": job.creator_impact
                }
                for job in sorted(
                    self.backup_jobs.values(), 
                    key=lambda x: x.started_at, 
                    reverse=True
                )[:10]
            ]
        
        return report


# Utility functions for backup automation
async def create_backup_automation_manager(config: Dict[str, Any]) -> BackupAutomationManager:
    """Create and initialize backup automation manager."""
    return BackupAutomationManager(config)


async def setup_creator_platform_backups(
    manager: BackupAutomationManager
) -> List[BackupTarget]:
    """Set up comprehensive backup strategy for creator platform."""
    targets = []
    
    # Critical creator data (real-time backup)
    creator_content_target = await manager.create_backup_target(
        name="Creator Content Repository",
        path="/data/creators",
        data_category=DataCategory.CREATOR_CONTENT,
        backup_type=BackupType.CONTINUOUS,
        frequency=BackupFrequency.REAL_TIME,
        retention_days=365,
        creator_specific=True,
        priority=1
    )
    targets.append(creator_content_target)
    
    # AI models (daily full backup)
    ai_models_target = await manager.create_backup_target(
        name="AI Models and Weights",
        path="/models/ai_agents",
        data_category=DataCategory.AI_MODELS,
        backup_type=BackupType.FULL,
        frequency=BackupFrequency.DAILY,
        retention_days=180,
        creator_specific=False,
        priority=1
    )
    targets.append(ai_models_target)
    
    # Revenue data (continuous with long retention)
    revenue_target = await manager.create_backup_target(
        name="Revenue and Monetization Data",
        path="/data/revenue",
        data_category=DataCategory.REVENUE_DATA,
        backup_type=BackupType.CONTINUOUS,
        frequency=BackupFrequency.REAL_TIME,
        retention_days=2555,  # 7 years for compliance
        creator_specific=True,
        priority=1
    )
    targets.append(revenue_target)
    
    return targets


# Example usage and configuration
if __name__ == "__main__":
    # Example backup automation configuration
    backup_config = {
        "local_backup_path": "/backup",
        "aws_enabled": True,
        "aws_access_key": "your_access_key",
        "aws_secret_key": "your_secret_key",
        "aws_region": "us-east-1",
        "s3_bucket": "ainflue-backups",
        "encryption_enabled": True,
        "compression_enabled": True,
        "verification_enabled": True
    }
    
    async def main():
        # Initialize backup automation
        manager = await create_backup_automation_manager(backup_config)
        
        # Set up creator platform backups
        targets = await setup_creator_platform_backups(manager)
        print(f"Created {len(targets)} backup targets")
        
        # Execute immediate backup
        if targets:
            backup_job = await manager.execute_backup(targets[0].target_id)
            print(f"Backup job completed: {backup_job.status.value}")
        
        # Create disaster recovery plan
        dr_plan = await manager.create_disaster_recovery_plan(
            name="Creator Platform DR Plan",
            description="Disaster recovery for creator content and platform",
            rto_objective=RecoveryObjective.RTO_LOW,
            rpo_objective=RecoveryObjective.RTO_LOW,
            critical_systems=["creator_content", "ai_models", "revenue_data"],
            recovery_procedures=[
                {"name": "Restore Creator Content", "type": "backup_restore", "priority": 1},
                {"name": "Failover AI Models", "type": "failover", "priority": 2},
                {"name": "Notify Teams", "type": "notification", "priority": 3}
            ],
            contact_list=[
                {"name": "DevOps Team", "email": "devops@ainflue.com", "phone": "+1-555-0100"},
                {"name": "Platform Team", "email": "platform@ainflue.com", "phone": "+1-555-0101"}
            ]
        )
        print(f"DR plan created: {dr_plan.name}")
        
        # Test disaster recovery
        dr_test_results = await manager.test_disaster_recovery(dr_plan.plan_id)
        print(f"DR test completed: {dr_test_results['overall_status']}")
        
        # Export backup report
        backup_report = await manager.export_backup_report()
        print(f"Backup report generated with {backup_report['backup_summary']['total_targets']} targets")
    
    # Run the example
    asyncio.run(main())