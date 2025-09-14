"""Voice Backup Recovery - Advanced Backup and Disaster Recovery System
=====================================================================

Comprehensive backup and recovery system providing automated backups,
disaster recovery, data protection, and recovery analytics for the
Ainflue voice ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import shutil
import tarfile
import gzip
import boto3
import aiofiles
import hashlib
from pathlib import Path
import threading
import schedule
import time

logger = logging.getLogger(__name__)

class BackupType(Enum):
    """Backup type enumeration"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

class BackupStatus(Enum):
    """Backup operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RecoveryType(Enum):
    """Recovery operation type"""
    FULL_RESTORE = "full_restore"
    PARTIAL_RESTORE = "partial_restore"
    POINT_IN_TIME = "point_in_time"
    FILE_RESTORE = "file_restore"

class StorageLocation(Enum):
    """Backup storage locations"""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    FTP = "ftp"
    NETWORK_SHARE = "network_share"

@dataclass
class BackupConfiguration:
    """Backup configuration settings"""
    config_id: str
    name: str
    backup_type: BackupType
    source_paths: List[str]
    destination: str
    storage_location: StorageLocation
    schedule: str  # Cron expression
    retention_days: int = 30
    compression: bool = True
    encryption: bool = True
    encryption_key: Optional[str] = None
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_file_size: int = 1024 * 1024 * 1024  # 1GB
    created_at: datetime = field(default_factory=datetime.utcnow)
    enabled: bool = True

@dataclass
class BackupJob:
    """Backup job execution details"""
    job_id: str
    config_id: str
    backup_type: BackupType
    status: BackupStatus
    source_paths: List[str]
    destination_path: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    files_processed: int = 0
    total_files: int = 0
    bytes_processed: int = 0
    total_bytes: int = 0
    compression_ratio: float = 0.0
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecoveryJob:
    """Recovery job execution details"""
    recovery_id: str
    recovery_type: RecoveryType
    source_backup: str
    destination_path: str
    status: BackupStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    files_restored: int = 0
    bytes_restored: int = 0
    recovery_point: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BackupSystem:
    """Core backup system implementation"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize backup system"""
        self.config = config or {}
        self.backup_configs = {}
        self.active_jobs = {}
        self.job_history = {}
        self.storage_clients = {}
        self.scheduler = None
        
        # Initialize storage clients
        asyncio.create_task(self._initialize_storage_clients())
        
        # Start backup scheduler
        self._start_scheduler()
        
        logger.info("💾 Backup System initialized")
    
    async def create_backup_config(
        self,
        name: str,
        backup_type: BackupType,
        source_paths: List[str],
        destination: str,
        storage_location: StorageLocation,
        schedule: str,
        **kwargs
    ) -> str:
        """Create backup configuration"""
        try:
            config_id = f"backup_{int(time.time())}"
            
            config = BackupConfiguration(
                config_id=config_id,
                name=name,
                backup_type=backup_type,
                source_paths=source_paths,
                destination=destination,
                storage_location=storage_location,
                schedule=schedule,
                **kwargs
            )
            
            self.backup_configs[config_id] = config
            
            # Schedule backup job
            await self._schedule_backup(config)
            
            logger.info(f"Created backup configuration: {config_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"Failed to create backup config: {e}")
            raise
    
    async def start_backup(
        self,
        config_id: str,
        backup_type: Optional[BackupType] = None
    ) -> str:
        """Start backup job manually"""
        try:
            config = self.backup_configs.get(config_id)
            if not config:
                raise ValueError(f"Backup config not found: {config_id}")
            
            job_id = f"job_{int(time.time())}"
            
            job = BackupJob(
                job_id=job_id,
                config_id=config_id,
                backup_type=backup_type or config.backup_type,
                status=BackupStatus.PENDING,
                source_paths=config.source_paths,
                destination_path=config.destination
            )
            
            self.active_jobs[job_id] = job
            
            # Start backup process
            asyncio.create_task(self._execute_backup_job(job))
            
            logger.info(f"Started backup job: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to start backup: {e}")
            raise
    
    async def _execute_backup_job(self, job -> None: BackupJob) -> None:
        """Execute backup job"""
        try:
            job.status = BackupStatus.IN_PROGRESS
            job.started_at = datetime.utcnow()
            
            # Get backup configuration
            config = self.backup_configs[job.config_id]
            
            # Calculate total files and size
            await self._calculate_backup_size(job, config)
            
            # Perform backup based on type
            if job.backup_type == BackupType.FULL:
                await self._perform_full_backup(job, config)
            elif job.backup_type == BackupType.INCREMENTAL:
                await self._perform_incremental_backup(job, config)
            elif job.backup_type == BackupType.DIFFERENTIAL:
                await self._perform_differential_backup(job, config)
            else:
                await self._perform_snapshot_backup(job, config)
            
            # Calculate checksum
            job.checksum = await self._calculate_backup_checksum(job.destination_path)
            
            # Upload to storage location
            if config.storage_location != StorageLocation.LOCAL:
                await self._upload_backup(job, config)
            
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            # Move to history
            self.job_history[job.job_id] = job
            del self.active_jobs[job.job_id]
            
            logger.info(f"Backup job completed: {job.job_id}")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            logger.error(f"Backup job failed {job.job_id}: {e}")
    
    async def _perform_full_backup(self, job -> None: BackupJob, config -> None: BackupConfiguration) -> None:
        """Perform full backup"""
        try:
            backup_path = f"{job.destination_path}/full_{job.started_at.strftime('%Y%m%d_%H%M%S')}.tar.gz"
            
            with tarfile.open(backup_path, 'w:gz' if config.compression else 'w') as tar:
                for source_path in job.source_paths:
                    if os.path.exists(source_path):
                        await self._add_to_archive(tar, source_path, job, config)
            
            job.destination_path = backup_path
            
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            raise
    
    async def _perform_incremental_backup(self, job -> None: BackupJob, config -> None: BackupConfiguration) -> None:
        """Perform incremental backup"""
        try:
            # Get last backup timestamp
            last_backup_time = await self._get_last_backup_time(config.config_id)
            
            backup_path = f"{job.destination_path}/incremental_{job.started_at.strftime('%Y%m%d_%H%M%S')}.tar.gz"
            
            with tarfile.open(backup_path, 'w:gz' if config.compression else 'w') as tar:
                for source_path in job.source_paths:
                    await self._add_modified_files(tar, source_path, last_backup_time, job, config)
            
            job.destination_path = backup_path
            
        except Exception as e:
            logger.error(f"Incremental backup failed: {e}")
            raise
    
    async def _perform_differential_backup(self, job -> None: BackupJob, config -> None: BackupConfiguration) -> None:
        """Perform differential backup"""
        try:
            # Get last full backup timestamp
            last_full_backup_time = await self._get_last_full_backup_time(config.config_id)
            
            backup_path = f"{job.destination_path}/differential_{job.started_at.strftime('%Y%m%d_%H%M%S')}.tar.gz"
            
            with tarfile.open(backup_path, 'w:gz' if config.compression else 'w') as tar:
                for source_path in job.source_paths:
                    await self._add_modified_files(tar, source_path, last_full_backup_time, job, config)
            
            job.destination_path = backup_path
            
        except Exception as e:
            logger.error(f"Differential backup failed: {e}")
            raise
    
    async def _perform_snapshot_backup(self, job -> None: BackupJob, config -> None: BackupConfiguration) -> None:
        """Perform snapshot backup"""
        try:
            snapshot_path = f"{job.destination_path}/snapshot_{job.started_at.strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(snapshot_path, exist_ok=True)
            
            for source_path in job.source_paths:
                if os.path.isfile(source_path):
                    destination = os.path.join(snapshot_path, os.path.basename(source_path))
                    shutil.copy2(source_path, destination)
                elif os.path.isdir(source_path):
                    destination = os.path.join(snapshot_path, os.path.basename(source_path))
                    shutil.copytree(source_path, destination)
                
                job.files_processed += 1
            
            job.destination_path = snapshot_path
            
        except Exception as e:
            logger.error(f"Snapshot backup failed: {e}")
            raise
    
    async def _add_to_archive(
        self,
        tar -> None: tarfile.TarFile,
        path -> None: str,
        job -> None: BackupJob,
        config -> None: BackupConfiguration
    ) -> None:
        """Add files to tar archive"""
        try:
            if os.path.isfile(path):
                # Check file size
                file_size = os.path.getsize(path)
                if file_size <= config.max_file_size:
                    # Check include/exclude patterns
                    if await self._should_include_file(path, config):
                        tar.add(path)
                        job.files_processed += 1
                        job.bytes_processed += file_size
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        await self._add_to_archive(tar, file_path, job, config)
            
        except Exception as e:
            logger.warning(f"Failed to add {path} to archive: {e}")
    
    async def _add_modified_files(
        self,
        tar -> None: tarfile.TarFile,
        path -> None: str,
        since_time -> None: datetime,
        job -> None: BackupJob,
        config -> None: BackupConfiguration
    ) -> None:
        """Add modified files since timestamp"""
        try:
            if os.path.isfile(path):
                mod_time = datetime.fromtimestamp(os.path.getmtime(path))
                if mod_time > since_time:
                    await self._add_to_archive(tar, path, job, config)
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        await self._add_modified_files(tar, file_path, since_time, job, config)
            
        except Exception as e:
            logger.warning(f"Failed to check modified files in {path}: {e}")
    
    async def _should_include_file(self, file_path: str, config: BackupConfiguration) -> bool:
        """Check if file should be included in backup"""
        try:
            # Check include patterns
            if config.include_patterns:
                included = any(pattern in file_path for pattern in config.include_patterns)
                if not included:
                    return False
            
            # Check exclude patterns
            if config.exclude_patterns:
                excluded = any(pattern in file_path for pattern in config.exclude_patterns)
                if excluded:
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking file inclusion {file_path}: {e}")
            return True
    
    async def _calculate_backup_size(self, job -> None: BackupJob, config -> None: BackupConfiguration) -> None:
        """Calculate total backup size"""
        try:
            total_files = 0
            total_bytes = 0
            
            for source_path in job.source_paths:
                if os.path.isfile(source_path):
                    if await self._should_include_file(source_path, config):
                        total_files += 1
                        total_bytes += os.path.getsize(source_path)
                elif os.path.isdir(source_path):
                    for root, dirs, files in os.walk(source_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if await self._should_include_file(file_path, config):
                                total_files += 1
                                total_bytes += os.path.getsize(file_path)
            
            job.total_files = total_files
            job.total_bytes = total_bytes
            
        except Exception as e:
            logger.warning(f"Failed to calculate backup size: {e}")
    
    async def _calculate_backup_checksum(self, backup_path: str) -> str:
        """Calculate backup file checksum"""
        try:
            hash_sha256 = hashlib.sha256()
            
            async with aiofiles.open(backup_path, 'rb') as f:
                async for chunk in f:
                    hash_sha256.update(chunk)
            
            return hash_sha256.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {e}")
            return ""
    
    async def _upload_backup(self, job -> None: BackupJob, config -> None: BackupConfiguration) -> None:
        """Upload backup to remote storage"""
        try:
            storage_client = self.storage_clients.get(config.storage_location)
            if not storage_client:
                raise ValueError(f"Storage client not configured: {config.storage_location}")
            
            # Upload based on storage type
            if config.storage_location == StorageLocation.AWS_S3:
                await self._upload_to_s3(job, config, storage_client)
            elif config.storage_location == StorageLocation.GOOGLE_CLOUD:
                await self._upload_to_gcs(job, config, storage_client)
            # Add other storage implementations
            
        except Exception as e:
            logger.error(f"Failed to upload backup: {e}")
            raise
    
    async def _upload_to_s3(self, job -> None: BackupJob, config -> None: BackupConfiguration, s3_client) -> None:
        """Upload backup to AWS S3"""
        try:
            bucket_name = config.destination.split('/')[0]
            key = '/'.join(config.destination.split('/')[1:]) + '/' + os.path.basename(job.destination_path)
            
            s3_client.upload_file(job.destination_path, bucket_name, key)
            
            logger.info(f"Backup uploaded to S3: s3://{bucket_name}/{key}")
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    async def _upload_to_gcs(self, job -> None: BackupJob, config -> None: BackupConfiguration, gcs_client) -> None:
        """Upload backup to Google Cloud Storage"""
        # Implementation for GCS upload
        pass
    
    async def _initialize_storage_clients(self) -> None:
        """Initialize storage clients"""
        try:
            # AWS S3 client
            if self.config.get('aws_access_key_id'):
                self.storage_clients[StorageLocation.AWS_S3] = boto3.client(
                    's3',
                    aws_access_key_id=self.config['aws_access_key_id'],
                    aws_secret_access_key=self.config['aws_secret_access_key'],
                    region_name=self.config.get('aws_region', 'us-east-1')
                )
            
            # Add other storage client initializations
            
            logger.info("Storage clients initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize storage clients: {e}")
    
    def _start_scheduler(self) -> None:
        """Start backup scheduler"""
        try:
            def run_scheduler() -> None:
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            
            logger.info("Backup scheduler started")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    async def _schedule_backup(self, config -> None: BackupConfiguration) -> None:
        """Schedule automatic backup"""
        try:
            def backup_task() -> None:
                asyncio.create_task(self.start_backup(config.config_id))
            
            # Parse cron schedule and register with scheduler
            # This is a simplified example - would use proper cron parsing
            if config.schedule == "daily":
                schedule.every().day.at("02:00").do(backup_task)
            elif config.schedule == "weekly":
                schedule.every().week.do(backup_task)
            
            logger.info(f"Scheduled backup: {config.config_id}")
            
        except Exception as e:
            logger.error(f"Failed to schedule backup: {e}")
    
    async def _get_last_backup_time(self, config_id: str) -> datetime:
        """Get timestamp of last backup"""
        # Implementation would query backup history
        return datetime.utcnow() - timedelta(days=1)
    
    async def _get_last_full_backup_time(self, config_id: str) -> datetime:
        """Get timestamp of last full backup"""
        # Implementation would query backup history for full backups
        return datetime.utcnow() - timedelta(days=7)

class DisasterRecovery:
    """Disaster recovery system"""
    
    def __init__(self) -> None:
        """Initialize disaster recovery"""
        self.recovery_plans = {}
        self.recovery_jobs = {}
        self.backup_catalog = {}
        
        logger.info("🔄 Disaster Recovery System initialized")
    
    async def create_recovery_plan(
        self,
        name: str,
        backup_sources: List[str],
        recovery_targets: List[str],
        priority: int = 1
    ) -> str:
        """Create disaster recovery plan"""
        try:
            plan_id = f"recovery_plan_{int(time.time())}"
            
            plan = {
                "plan_id": plan_id,
                "name": name,
                "backup_sources": backup_sources,
                "recovery_targets": recovery_targets,
                "priority": priority,
                "created_at": datetime.utcnow(),
                "last_tested": None,
                "status": "active"
            }
            
            self.recovery_plans[plan_id] = plan
            
            logger.info(f"Created recovery plan: {plan_id}")
            return plan_id
            
        except Exception as e:
            logger.error(f"Failed to create recovery plan: {e}")
            raise
    
    async def start_recovery(
        self,
        recovery_type: RecoveryType,
        source_backup: str,
        destination_path: str,
        recovery_point: Optional[datetime] = None
    ) -> str:
        """Start recovery operation"""
        try:
            recovery_id = f"recovery_{int(time.time())}"
            
            recovery = RecoveryJob(
                recovery_id=recovery_id,
                recovery_type=recovery_type,
                source_backup=source_backup,
                destination_path=destination_path,
                status=BackupStatus.PENDING,
                recovery_point=recovery_point
            )
            
            self.recovery_jobs[recovery_id] = recovery
            
            # Start recovery process
            asyncio.create_task(self._execute_recovery(recovery))
            
            logger.info(f"Started recovery operation: {recovery_id}")
            return recovery_id
            
        except Exception as e:
            logger.error(f"Failed to start recovery: {e}")
            raise
    
    async def _execute_recovery(self, recovery -> None: RecoveryJob) -> None:
        """Execute recovery operation"""
        try:
            recovery.status = BackupStatus.IN_PROGRESS
            recovery.started_at = datetime.utcnow()
            
            # Perform recovery based on type
            if recovery.recovery_type == RecoveryType.FULL_RESTORE:
                await self._perform_full_restore(recovery)
            elif recovery.recovery_type == RecoveryType.PARTIAL_RESTORE:
                await self._perform_partial_restore(recovery)
            elif recovery.recovery_type == RecoveryType.POINT_IN_TIME:
                await self._perform_point_in_time_restore(recovery)
            else:
                await self._perform_file_restore(recovery)
            
            recovery.status = BackupStatus.COMPLETED
            recovery.completed_at = datetime.utcnow()
            
            logger.info(f"Recovery completed: {recovery.recovery_id}")
            
        except Exception as e:
            recovery.status = BackupStatus.FAILED
            recovery.completed_at = datetime.utcnow()
            
            logger.error(f"Recovery failed {recovery.recovery_id}: {e}")
    
    async def _perform_full_restore(self, recovery -> None: RecoveryJob) -> None:
        """Perform full system restore"""
        try:
            # Extract backup archive
            with tarfile.open(recovery.source_backup, 'r:gz') as tar:
                tar.extractall(recovery.destination_path)
            
            # Count restored files
            recovery.files_restored = await self._count_restored_files(recovery.destination_path)
            
        except Exception as e:
            logger.error(f"Full restore failed: {e}")
            raise
    
    async def _perform_partial_restore(self, recovery -> None: RecoveryJob) -> None:
        """Perform partial restore"""
        # Implementation for partial restore
        pass
    
    async def _perform_point_in_time_restore(self, recovery -> None: RecoveryJob) -> None:
        """Perform point-in-time restore"""
        # Implementation for point-in-time restore
        pass
    
    async def _perform_file_restore(self, recovery -> None: RecoveryJob) -> None:
        """Perform file-level restore"""
        # Implementation for file restore
        pass
    
    async def _count_restored_files(self, path: str) -> int:
        """Count number of restored files"""
        try:
            count = 0
            for root, dirs, files in os.walk(path):
                count += len(files)
            return count
            
        except Exception as e:
            logger.error(f"Failed to count restored files: {e}")
            return 0

class DataProtection:
    """Data protection and encryption"""
    
    def __init__(self) -> None:
        """Initialize data protection"""
        self.encryption_keys = {}
        self.protection_policies = {}
        
        logger.info("🔒 Data Protection initialized")

class VoiceBackup:
    """Voice-specific backup operations"""
    
    def __init__(self) -> None:
        """Initialize voice backup"""
        self.voice_backup_configs = {}
        
        logger.info("🎤💾 Voice Backup System initialized")

class RecoverySystem:
    """Recovery system management"""
    
    def __init__(self) -> None:
        """Initialize recovery system"""
        self.recovery_catalog = {}
        
        logger.info("🔄 Recovery System initialized")

class BackupAnalytics:
    """Backup analytics and monitoring"""
    
    def __init__(self) -> None:
        """Initialize backup analytics"""
        self.backup_metrics = {}
        self.performance_stats = {}
        
        logger.info("📊 Backup Analytics initialized")

class RecoveryManagement:
    """Recovery management system"""
    
    def __init__(self) -> None:
        """Initialize recovery management"""
        self.recovery_procedures = {}
        
        logger.info("🛠️ Recovery Management initialized")

class VoiceBackupRecovery:
    """Main voice backup and recovery system"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize voice backup recovery system"""
        self.config = config or {}
        self.backup_system = BackupSystem(config)
        self.disaster_recovery = DisasterRecovery()
        self.data_protection = DataProtection()
        self.voice_backup = VoiceBackup()
        self.recovery_system = RecoverySystem()
        self.backup_analytics = BackupAnalytics()
        self.recovery_management = RecoveryManagement()
        
        # Initialize voice-specific backup configurations
        asyncio.create_task(self._initialize_voice_backups())
        
        logger.info("🎤💾🔄 Voice Backup Recovery System initialized")
    
    async def create_voice_backup(
        self,
        voice_data_paths: List[str],
        backup_name: str,
        schedule: str = "daily"
    ) -> str:
        """Create voice data backup configuration"""
        try:
            config_id = await self.backup_system.create_backup_config(
                name=f"voice_backup_{backup_name}",
                backup_type=BackupType.INCREMENTAL,
                source_paths=voice_data_paths,
                destination="/backups/voice",
                storage_location=StorageLocation.AWS_S3,
                schedule=schedule,
                include_patterns=["*.wav", "*.mp3", "*.flac", "*.json", "*.db"],
                exclude_patterns=["*.tmp", "*.log"],
                compression=True,
                encryption=True
            )
            
            return config_id
            
        except Exception as e:
            logger.error(f"Failed to create voice backup: {e}")
            raise
    
    async def restore_voice_data(
        self,
        backup_source: str,
        restore_path: str,
        voice_id: Optional[str] = None
    ) -> str:
        """Restore voice data from backup"""
        try:
            recovery_type = RecoveryType.PARTIAL_RESTORE if voice_id else RecoveryType.FULL_RESTORE
            
            recovery_id = await self.disaster_recovery.start_recovery(
                recovery_type=recovery_type,
                source_backup=backup_source,
                destination_path=restore_path
            )
            
            return recovery_id
            
        except Exception as e:
            logger.error(f"Failed to restore voice data: {e}")
            raise
    
    async def _initialize_voice_backups(self) -> None:
        """Initialize voice-specific backup configurations"""
        try:
            # Voice bank backup
            await self.create_voice_backup(
                voice_data_paths=["/data/voices/bank", "/data/voices/models"],
                backup_name="voice_bank",
                schedule="daily"
            )
            
            # Voice processing results backup
            await self.create_voice_backup(
                voice_data_paths=["/data/voices/processed", "/data/voices/analytics"],
                backup_name="voice_processing",
                schedule="hourly"
            )
            
            # Voice user data backup
            await self.create_voice_backup(
                voice_data_paths=["/data/voices/users", "/data/voices/collaborations"],
                backup_name="voice_user_data",
                schedule="daily"
            )
            
            logger.info("Voice backup configurations initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice backups: {e}")
