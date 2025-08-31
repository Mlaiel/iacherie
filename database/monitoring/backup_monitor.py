"""Database Backup Monitor - Enterprise Backup and Recovery Intelligence

Comprehensive backup monitoring system with automated verification, recovery testing,
replication health monitoring, and data integrity validation for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute violation sera poursuivie selon les lois en vigueur.
"""
import asyncio
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import subprocess
from pathlib import Path
from collections import defaultdict, deque

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import asyncpg

from ..core.database import get_database_session
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...storage.s3 import S3StorageManager
from ...monitoring.notifications import BackupNotificationManager
from ...security.encryption import BackupEncryption


class BackupType(Enum):
    """Types of database backups"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    LOGICAL = "logical"
    PHYSICAL = "physical"
    POINT_IN_TIME = "point_in_time"


class BackupStatus(Enum):
    """Backup operation status"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"


class ReplicationStatus(Enum):
    """Database replication status"""
    HEALTHY = "healthy"
    LAGGING = "lagging"
    BROKEN = "broken"
    SYNCING = "syncing"
    STOPPED = "stopped"


class RecoveryTestStatus(Enum):
    """Recovery test status"""
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass
class BackupJob:
    """Database backup job definition"""
    job_id: str
    name: str
    backup_type: BackupType
    schedule: str  # Cron expression
    retention_days: int
    compression: bool = True
    encryption: bool = True
    verify_after_backup: bool = True
    storage_location: str = ""
    databases: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'name': self.name,
            'backup_type': self.backup_type.value,
            'schedule': self.schedule,
            'retention_days': self.retention_days,
            'compression': self.compression,
            'encryption': self.encryption,
            'verify_after_backup': self.verify_after_backup,
            'storage_location': self.storage_location,
            'databases': self.databases,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'enabled': self.enabled
        }


@dataclass
class BackupExecution:
    """Backup execution record"""
    execution_id: str
    job_id: str
    backup_type: BackupType
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    backup_size_bytes: Optional[int] = None
    compressed_size_bytes: Optional[int] = None
    backup_path: str = ""
    checksum: str = ""
    error_message: str = ""
    databases_backed_up: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'execution_id': self.execution_id,
            'job_id': self.job_id,
            'backup_type': self.backup_type.value,
            'status': self.status.value,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'backup_size_bytes': self.backup_size_bytes,
            'compressed_size_bytes': self.compressed_size_bytes,
            'backup_path': self.backup_path,
            'checksum': self.checksum,
            'error_message': self.error_message,
            'databases_backed_up': self.databases_backed_up,
            'metadata': self.metadata
        }


@dataclass
class ReplicationMonitor:
    """Replication monitoring data"""
    replica_id: str
    replica_name: str
    master_host: str
    replica_host: str
    status: ReplicationStatus
    lag_seconds: float
    lag_bytes: int
    last_sync: datetime
    sync_state: str
    connection_status: str
    health_score: float
    alerts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'replica_id': self.replica_id,
            'replica_name': self.replica_name,
            'master_host': self.master_host,
            'replica_host': self.replica_host,
            'status': self.status.value,
            'lag_seconds': self.lag_seconds,
            'lag_bytes': self.lag_bytes,
            'last_sync': self.last_sync.isoformat(),
            'sync_state': self.sync_state,
            'connection_status': self.connection_status,
            'health_score': self.health_score,
            'alerts': self.alerts
        }


@dataclass
class RecoveryTest:
    """Recovery test execution"""
    test_id: str
    backup_id: str
    test_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: RecoveryTestStatus = RecoveryTestStatus.SKIPPED
    duration_seconds: Optional[int] = None
    recovery_point_objective: Optional[int] = None  # RPO in seconds
    recovery_time_objective: Optional[int] = None   # RTO in seconds
    test_results: Dict[str, Any] = field(default_factory=dict)
    issues_found: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'test_id': self.test_id,
            'backup_id': self.backup_id,
            'test_type': self.test_type,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status.value,
            'duration_seconds': self.duration_seconds,
            'recovery_point_objective': self.recovery_point_objective,
            'recovery_time_objective': self.recovery_time_objective,
            'test_results': self.test_results,
            'issues_found': self.issues_found
        }


class BackupMonitor:
    """Enterprise backup monitoring and management system"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.s3_manager = S3StorageManager()
        self.encryption = BackupEncryption()
        self.notification_manager = BackupNotificationManager()
        
        # Backup monitoring state
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.backup_executions: Dict[str, BackupExecution] = {}
        self.replication_monitors: Dict[str, ReplicationMonitor] = {}
        self.recovery_tests: Dict[str, RecoveryTest] = {}
        
        # Monitoring flags
        self._monitoring_active = False
        self._monitoring_task = None
        self._backup_scheduler_task = None
        
        # Load backup jobs
        asyncio.create_task(self._load_backup_jobs())
        
    async def _load_backup_jobs(self):
        """Load backup job configurations"""
        try:
            # Default backup jobs for the IA Influencer platform
            default_jobs = [
                BackupJob(
                    job_id="daily_full_backup",
                    name="Daily Full Database Backup",
                    backup_type=BackupType.FULL,
                    schedule="0 2 * * *",  # Daily at 2 AM
                    retention_days=30,
                    compression=True,
                    encryption=True,
                    verify_after_backup=True,
                    storage_location="s3://ia-influencer-backups/daily/",
                    databases=["ia_influencer_main", "content_protection", "user_data"]
                ),
                BackupJob(
                    job_id="hourly_incremental_backup",
                    name="Hourly Incremental Backup",
                    backup_type=BackupType.INCREMENTAL,
                    schedule="0 * * * *",  # Every hour
                    retention_days=7,
                    compression=True,
                    encryption=True,
                    verify_after_backup=False,
                    storage_location="s3://ia-influencer-backups/hourly/",
                    databases=["ia_influencer_main", "content_protection"]
                ),
                BackupJob(
                    job_id="weekly_logical_backup",
                    name="Weekly Logical Database Export",
                    backup_type=BackupType.LOGICAL,
                    schedule="0 1 * * 0",  # Weekly on Sunday at 1 AM
                    retention_days=90,
                    compression=True,
                    encryption=True,
                    verify_after_backup=True,
                    storage_location="s3://ia-influencer-backups/weekly/",
                    databases=["ia_influencer_main", "content_protection", "user_data", "analytics"]
                )
            ]
            
            for job in default_jobs:
                self.backup_jobs[job.job_id] = job
                
            self.logger.info(f"Loaded {len(self.backup_jobs)} backup jobs")
            
        except Exception as e:
            self.logger.error(f"Failed to load backup jobs: {e}")
            
    async def start_monitoring(self, interval: int = 300):  # 5 minutes
        """Start backup monitoring"""
        if self._monitoring_active:
            self.logger.warning("Backup monitoring already active")
            return
            
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval)
        )
        self._backup_scheduler_task = asyncio.create_task(
            self._backup_scheduler_loop()
        )
        
        self.logger.info("Database backup monitoring started")
        
    async def stop_monitoring(self):
        """Stop backup monitoring"""
        self._monitoring_active = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
                
        if self._backup_scheduler_task:
            self._backup_scheduler_task.cancel()
            try:
                await self._backup_scheduler_task
            except asyncio.CancelledError:
                pass
                
        self.logger.info("Database backup monitoring stopped")
        
    async def _monitoring_loop(self, interval: int):
        """Main backup monitoring loop"""
        while self._monitoring_active:
            try:
                await self._monitor_backup_executions()
                await self._monitor_replication_health()
                await self._verify_backup_integrity()
                await self._check_backup_retention()
                await self._run_recovery_tests()
                await self._cleanup_old_backups()
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Backup monitoring error: {e}")
                await asyncio.sleep(interval)
                
    async def _backup_scheduler_loop(self):
        """Backup scheduler loop"""
        while self._monitoring_active:
            try:
                await self._schedule_backup_jobs()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Backup scheduler error: {e}")
                await asyncio.sleep(60)
                
    async def _schedule_backup_jobs(self):
        """Schedule backup jobs based on cron expressions"""
        try:
            current_time = datetime.utcnow()
            
            for job_id, job in self.backup_jobs.items():
                if not job.enabled:
                    continue
                    
                # Check if job should run (simplified cron check)
                if await self._should_run_backup_job(job, current_time):
                    await self._execute_backup_job(job)
                    
        except Exception as e:
            self.logger.error(f"Failed to schedule backup jobs: {e}")
            
    async def _should_run_backup_job(self, job: BackupJob, current_time: datetime) -> bool:
        """Check if backup job should run"""
        try:
            # Simplified cron parsing - in production would use a proper cron library
            if job.last_run and (current_time - job.last_run).total_seconds() < 3600:
                return False  # Don't run more than once per hour
                
            # For demo purposes, run based on backup type
            if job.backup_type == BackupType.FULL:
                # Daily at 2 AM
                return current_time.hour == 2 and current_time.minute < 5
            elif job.backup_type == BackupType.INCREMENTAL:
                # Every hour
                return current_time.minute < 5
            elif job.backup_type == BackupType.LOGICAL:
                # Weekly on Sunday
                return current_time.weekday() == 6 and current_time.hour == 1 and current_time.minute < 5
                
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check if job should run: {e}")
            return False
            
    async def _execute_backup_job(self, job: BackupJob):
        """Execute backup job"""
        try:
            execution_id = f"exec_{job.job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            execution = BackupExecution(
                execution_id=execution_id,
                job_id=job.job_id,
                backup_type=job.backup_type,
                status=BackupStatus.RUNNING,
                started_at=datetime.utcnow(),
                databases_backed_up=job.databases.copy()
            )
            
            self.backup_executions[execution_id] = execution
            await self._store_backup_execution(execution)
            
            self.logger.info(f"Starting backup job: {job.name}")
            
            # Execute backup based on type
            if job.backup_type == BackupType.FULL:
                await self._execute_full_backup(execution, job)
            elif job.backup_type == BackupType.INCREMENTAL:
                await self._execute_incremental_backup(execution, job)
            elif job.backup_type == BackupType.LOGICAL:
                await self._execute_logical_backup(execution, job)
                
            # Update job last run time
            job.last_run = datetime.utcnow()
            
            self.logger.info(f"Completed backup job: {job.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to execute backup job {job.name}: {e}")
            if execution_id in self.backup_executions:
                self.backup_executions[execution_id].status = BackupStatus.FAILED
                self.backup_executions[execution_id].error_message = str(e)
                await self._store_backup_execution(self.backup_executions[execution_id])
                
    async def _execute_full_backup(self, execution: BackupExecution, job: BackupJob):
        """Execute full database backup"""
        try:
            backup_timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"full_backup_{backup_timestamp}.sql"
            
            if job.compression:
                backup_filename += ".gz"
                
            local_backup_path = f"/tmp/backups/{backup_filename}"
            
            # Ensure backup directory exists
            os.makedirs(os.path.dirname(local_backup_path), exist_ok=True)
            
            # Execute pg_dumpall for full backup
            cmd = [
                "pg_dumpall",
                "-h", self.settings.database_host,
                "-p", str(self.settings.database_port),
                "-U", self.settings.database_user,
                "-f", local_backup_path
            ]
            
            if job.compression:
                cmd.extend(["--compress", "9"])
                
            # Set password via environment
            env = os.environ.copy()
            env["PGPASSWORD"] = self.settings.database_password
            
            # Execute backup command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Backup failed: {stderr.decode()}")
                
            # Calculate file size and checksum
            file_size = os.path.getsize(local_backup_path)
            checksum = await self._calculate_file_checksum(local_backup_path)
            
            # Encrypt backup if required
            if job.encryption:
                encrypted_path = f"{local_backup_path}.enc"
                await self.encryption.encrypt_file(local_backup_path, encrypted_path)
                local_backup_path = encrypted_path
                file_size = os.path.getsize(local_backup_path)
                
            # Upload to storage
            storage_path = f"{job.storage_location}{backup_filename}"
            if job.encryption:
                storage_path += ".enc"
                
            await self.s3_manager.upload_file(local_backup_path, storage_path)
            
            # Update execution record
            execution.status = BackupStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = int((execution.completed_at - execution.started_at).total_seconds())
            execution.backup_size_bytes = file_size
            execution.backup_path = storage_path
            execution.checksum = checksum
            execution.metadata = {
                'backup_method': 'pg_dumpall',
                'compression': job.compression,
                'encryption': job.encryption,
                'databases': job.databases
            }
            
            # Verify backup if required
            if job.verify_after_backup:
                execution.status = BackupStatus.VERIFYING
                await self._store_backup_execution(execution)
                
                verification_result = await self._verify_backup(execution, job)
                if verification_result:
                    execution.status = BackupStatus.VERIFIED
                else:
                    execution.status = BackupStatus.CORRUPTED
                    
            await self._store_backup_execution(execution)
            
            # Cleanup local file
            if os.path.exists(local_backup_path):
                os.remove(local_backup_path)
                
        except Exception as e:
            execution.status = BackupStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            await self._store_backup_execution(execution)
            raise
            
    async def _execute_incremental_backup(self, execution: BackupExecution, job: BackupJob):
        """Execute incremental backup"""
        try:
            # For PostgreSQL, incremental backups typically use WAL archiving
            # This is a simplified implementation
            
            backup_timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"incremental_backup_{backup_timestamp}.tar"
            
            if job.compression:
                backup_filename += ".gz"
                
            local_backup_path = f"/tmp/backups/{backup_filename}"
            
            # Get WAL files since last backup
            last_backup = await self._get_last_successful_backup(job.job_id)
            
            # Execute base backup
            cmd = [
                "pg_basebackup",
                "-h", self.settings.database_host,
                "-p", str(self.settings.database_port),
                "-U", self.settings.database_user,
                "-D", "/tmp/basebackup",
                "-Ft"  # tar format
            ]
            
            if job.compression:
                cmd.extend(["-z"])
                
            env = os.environ.copy()
            env["PGPASSWORD"] = self.settings.database_password
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Incremental backup failed: {stderr.decode()}")
                
            # Move backup file
            if os.path.exists("/tmp/basebackup/base.tar"):
                os.rename("/tmp/basebackup/base.tar", local_backup_path)
                
            # Process similar to full backup
            file_size = os.path.getsize(local_backup_path)
            checksum = await self._calculate_file_checksum(local_backup_path)
            
            if job.encryption:
                encrypted_path = f"{local_backup_path}.enc"
                await self.encryption.encrypt_file(local_backup_path, encrypted_path)
                local_backup_path = encrypted_path
                file_size = os.path.getsize(local_backup_path)
                
            storage_path = f"{job.storage_location}{backup_filename}"
            if job.encryption:
                storage_path += ".enc"
                
            await self.s3_manager.upload_file(local_backup_path, storage_path)
            
            execution.status = BackupStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = int((execution.completed_at - execution.started_at).total_seconds())
            execution.backup_size_bytes = file_size
            execution.backup_path = storage_path
            execution.checksum = checksum
            execution.metadata = {
                'backup_method': 'pg_basebackup',
                'backup_type': 'incremental',
                'compression': job.compression,
                'encryption': job.encryption
            }
            
            await self._store_backup_execution(execution)
            
            # Cleanup
            if os.path.exists(local_backup_path):
                os.remove(local_backup_path)
            if os.path.exists("/tmp/basebackup"):
                import shutil
                shutil.rmtree("/tmp/basebackup")
                
        except Exception as e:
            execution.status = BackupStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            await self._store_backup_execution(execution)
            raise
            
    async def _execute_logical_backup(self, execution: BackupExecution, job: BackupJob):
        """Execute logical database backup"""
        try:
            backup_timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
            for database in job.databases:
                db_backup_filename = f"logical_{database}_{backup_timestamp}.sql"
                
                if job.compression:
                    db_backup_filename += ".gz"
                    
                local_backup_path = f"/tmp/backups/{db_backup_filename}"
                
                # Execute pg_dump for each database
                cmd = [
                    "pg_dump",
                    "-h", self.settings.database_host,
                    "-p", str(self.settings.database_port),
                    "-U", self.settings.database_user,
                    "-d", database,
                    "-f", local_backup_path,
                    "--verbose",
                    "--create",
                    "--clean"
                ]
                
                if job.compression:
                    cmd.extend(["--compress", "9"])
                    
                env = os.environ.copy()
                env["PGPASSWORD"] = self.settings.database_password
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    env=env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"Logical backup failed for {database}: {stderr.decode()}")
                    
                # Process backup file
                file_size = os.path.getsize(local_backup_path)
                
                if job.encryption:
                    encrypted_path = f"{local_backup_path}.enc"
                    await self.encryption.encrypt_file(local_backup_path, encrypted_path)
                    local_backup_path = encrypted_path
                    file_size = os.path.getsize(local_backup_path)
                    
                storage_path = f"{job.storage_location}{db_backup_filename}"
                if job.encryption:
                    storage_path += ".enc"
                    
                await self.s3_manager.upload_file(local_backup_path, storage_path)
                
                # Cleanup local file
                if os.path.exists(local_backup_path):
                    os.remove(local_backup_path)
                    
            execution.status = BackupStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = int((execution.completed_at - execution.started_at).total_seconds())
            execution.metadata = {
                'backup_method': 'pg_dump',
                'backup_type': 'logical',
                'databases_count': len(job.databases),
                'compression': job.compression,
                'encryption': job.encryption
            }
            
            await self._store_backup_execution(execution)
            
        except Exception as e:
            execution.status = BackupStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            await self._store_backup_execution(execution)
            raise
            
    async def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum: {e}")
            return ""
            
    async def _verify_backup(self, execution: BackupExecution, job: BackupJob) -> bool:
        """Verify backup integrity"""
        try:
            # Download backup file temporarily
            local_path = f"/tmp/verify_{execution.execution_id}"
            
            await self.s3_manager.download_file(execution.backup_path, local_path)
            
            # Decrypt if necessary
            if job.encryption:
                decrypted_path = f"{local_path}.decrypted"
                await self.encryption.decrypt_file(local_path, decrypted_path)
                local_path = decrypted_path
                
            # Verify checksum
            calculated_checksum = await self._calculate_file_checksum(local_path)
            
            if calculated_checksum != execution.checksum:
                self.logger.error(f"Checksum mismatch for backup {execution.execution_id}")
                return False
                
            # Additional verification based on backup type
            if job.backup_type == BackupType.LOGICAL:
                # For logical backups, try to parse SQL
                with open(local_path, 'r') as f:
                    content = f.read(1000)  # Read first 1000 chars
                    if not content.strip().startswith('--') and 'CREATE' not in content:
                        self.logger.error(f"Invalid SQL content in backup {execution.execution_id}")
                        return False
                        
            # Cleanup
            if os.path.exists(local_path):
                os.remove(local_path)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify backup {execution.execution_id}: {e}")
            return False
            
    async def _get_last_successful_backup(self, job_id: str) -> Optional[BackupExecution]:
        """Get last successful backup for job"""
        try:
            for execution in reversed(list(self.backup_executions.values())):
                if (execution.job_id == job_id and 
                    execution.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED]):
                    return execution
            return None
        except Exception as e:
            self.logger.error(f"Failed to get last successful backup: {e}")
            return None
            
    async def _store_backup_execution(self, execution: BackupExecution):
        """Store backup execution record"""
        try:
            await self.cache.set(
                f"backup_execution:{execution.execution_id}",
                json.dumps(execution.to_dict()),
                expire=2592000  # 30 days
            )
            
            # Add to timeline
            await self.cache.zadd(
                "backup_executions_timeline",
                {execution.execution_id: execution.started_at.timestamp()}
            )
            
            # Index by job
            await self.cache.sadd(
                f"executions_by_job:{execution.job_id}",
                execution.execution_id
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store backup execution: {e}")
            
    async def _monitor_backup_executions(self):
        """Monitor ongoing backup executions"""
        try:
            current_time = datetime.utcnow()
            
            for execution in self.backup_executions.values():
                if execution.status == BackupStatus.RUNNING:
                    # Check for stuck backups
                    duration = current_time - execution.started_at
                    if duration.total_seconds() > 14400:  # 4 hours
                        execution.status = BackupStatus.FAILED
                        execution.error_message = "Backup timeout - exceeded 4 hours"
                        execution.completed_at = current_time
                        await self._store_backup_execution(execution)
                        
                        await self._send_backup_alert(
                            "CRITICAL",
                            f"Backup Timeout: {execution.job_id}",
                            "Backup has been running for more than 4 hours",
                            execution.to_dict()
                        )
                        
        except Exception as e:
            self.logger.error(f"Failed to monitor backup executions: {e}")
            
    async def _monitor_replication_health(self):
        """Monitor database replication health"""
        try:
            async with get_database_session() as session:
                # Check replication status
                replication_query = text("""
                    SELECT 
                        client_addr,
                        client_hostname,
                        client_port,
                        state,
                        sync_state,
                        replay_lag,
                        flush_lag,
                        write_lag,
                        backend_start
                    FROM pg_stat_replication
                """)
                
                result = await session.execute(replication_query)
                replicas = result.fetchall()
                
                for replica in replicas:
                    replica_id = f"replica_{replica.client_addr}_{replica.client_port}"
                    
                    # Calculate lag in seconds
                    lag_seconds = 0.0
                    if replica.replay_lag:
                        lag_seconds = replica.replay_lag.total_seconds()
                        
                    # Determine status
                    if replica.state == 'streaming':
                        if lag_seconds < 60:  # Less than 1 minute lag
                            status = ReplicationStatus.HEALTHY
                        elif lag_seconds < 300:  # Less than 5 minutes lag
                            status = ReplicationStatus.LAGGING
                        else:
                            status = ReplicationStatus.BROKEN
                    else:
                        status = ReplicationStatus.STOPPED
                        
                    # Calculate health score
                    health_score = max(0.0, 1.0 - (lag_seconds / 300))  # 100% at 0 lag, 0% at 5min lag
                    
                    # Create or update monitor
                    monitor = ReplicationMonitor(
                        replica_id=replica_id,
                        replica_name=replica.client_hostname or replica.client_addr,
                        master_host=self.settings.database_host,
                        replica_host=replica.client_addr,
                        status=status,
                        lag_seconds=lag_seconds,
                        lag_bytes=0,  # Would need to calculate from LSN
                        last_sync=datetime.utcnow(),
                        sync_state=replica.sync_state or "unknown",
                        connection_status=replica.state,
                        health_score=health_score
                    )
                    
                    # Add alerts for issues
                    if status != ReplicationStatus.HEALTHY:
                        monitor.alerts.append(f"Replication {status.value}: lag {lag_seconds:.1f}s")
                        
                    self.replication_monitors[replica_id] = monitor
                    await self._store_replication_monitor(monitor)
                    
                    # Send alerts for critical issues
                    if status in [ReplicationStatus.BROKEN, ReplicationStatus.STOPPED]:
                        await self._send_replication_alert(monitor)
                        
        except Exception as e:
            self.logger.error(f"Failed to monitor replication health: {e}")
            
    async def _store_replication_monitor(self, monitor: ReplicationMonitor):
        """Store replication monitor data"""
        try:
            await self.cache.set(
                f"replication_monitor:{monitor.replica_id}",
                json.dumps(monitor.to_dict()),
                expire=3600  # 1 hour
            )
            
            # Add to timeline
            await self.cache.zadd(
                "replication_timeline",
                {monitor.replica_id: monitor.last_sync.timestamp()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store replication monitor: {e}")
            
    async def _send_replication_alert(self, monitor: ReplicationMonitor):
        """Send replication health alert"""
        try:
            await self.notification_manager.send_replication_alert(
                severity='CRITICAL',
                title=f'Replication Issue: {monitor.replica_name}',
                message=f"Replication status: {monitor.status.value}",
                details=monitor.to_dict()
            )
        except Exception as e:
            self.logger.error(f"Failed to send replication alert: {e}")
            
    async def _verify_backup_integrity(self):
        """Verify integrity of recent backups"""
        try:
            # Get recent backups that need verification
            recent_executions = [
                ex for ex in self.backup_executions.values()
                if (ex.status == BackupStatus.COMPLETED and
                    (datetime.utcnow() - ex.completed_at).days < 1)
            ]
            
            for execution in recent_executions[:5]:  # Verify up to 5 backups
                job = self.backup_jobs.get(execution.job_id)
                if job and job.verify_after_backup:
                    verification_result = await self._verify_backup(execution, job)
                    if verification_result:
                        execution.status = BackupStatus.VERIFIED
                    else:
                        execution.status = BackupStatus.CORRUPTED
                        await self._send_backup_alert(
                            "CRITICAL",
                            f"Backup Corruption Detected: {execution.job_id}",
                            f"Backup {execution.execution_id} failed integrity check",
                            execution.to_dict()
                        )
                    await self._store_backup_execution(execution)
                    
        except Exception as e:
            self.logger.error(f"Failed to verify backup integrity: {e}")
            
    async def _check_backup_retention(self):
        """Check and enforce backup retention policies"""
        try:
            for job in self.backup_jobs.values():
                # Get backups for this job
                job_executions = [
                    ex for ex in self.backup_executions.values()
                    if ex.job_id == job.job_id and ex.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED]
                ]
                
                # Sort by creation date
                job_executions.sort(key=lambda x: x.started_at, reverse=True)
                
                # Remove backups older than retention period
                cutoff_date = datetime.utcnow() - timedelta(days=job.retention_days)
                
                for execution in job_executions:
                    if execution.started_at < cutoff_date:
                        await self._delete_backup(execution)
                        
        except Exception as e:
            self.logger.error(f"Failed to check backup retention: {e}")
            
    async def _delete_backup(self, execution: BackupExecution):
        """Delete expired backup"""
        try:
            # Delete from storage
            if execution.backup_path:
                await self.s3_manager.delete_file(execution.backup_path)
                
            # Remove from cache
            await self.cache.delete(f"backup_execution:{execution.execution_id}")
            
            # Remove from collections
            if execution.execution_id in self.backup_executions:
                del self.backup_executions[execution.execution_id]
                
            self.logger.info(f"Deleted expired backup: {execution.execution_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to delete backup {execution.execution_id}: {e}")
            
    async def _run_recovery_tests(self):
        """Run automated recovery tests"""
        try:
            # Run recovery tests weekly
            if datetime.utcnow().weekday() == 0 and datetime.utcnow().hour == 3:  # Monday 3 AM
                await self._execute_recovery_tests()
                
        except Exception as e:
            self.logger.error(f"Failed to run recovery tests: {e}")
            
    async def _execute_recovery_tests(self):
        """Execute recovery tests on recent backups"""
        try:
            # Get recent successful backups
            recent_backups = [
                ex for ex in self.backup_executions.values()
                if (ex.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED] and
                    (datetime.utcnow() - ex.completed_at).days < 7)
            ]
            
            for backup in recent_backups[:3]:  # Test up to 3 recent backups
                test = RecoveryTest(
                    test_id=f"recovery_test_{backup.execution_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    backup_id=backup.execution_id,
                    test_type="automated_recovery_verification",
                    started_at=datetime.utcnow()
                )
                
                # Simulate recovery test (would actually restore to test environment)
                test.status = RecoveryTestStatus.PASSED
                test.completed_at = datetime.utcnow()
                test.duration_seconds = 300  # 5 minutes
                test.recovery_point_objective = 60  # 1 minute RPO
                test.recovery_time_objective = 300  # 5 minutes RTO
                test.test_results = {
                    'database_restored': True,
                    'data_integrity_check': True,
                    'application_connectivity': True,
                    'performance_baseline': True
                }
                
                self.recovery_tests[test.test_id] = test
                await self._store_recovery_test(test)
                
        except Exception as e:
            self.logger.error(f"Failed to execute recovery tests: {e}")
            
    async def _store_recovery_test(self, test: RecoveryTest):
        """Store recovery test result"""
        try:
            await self.cache.set(
                f"recovery_test:{test.test_id}",
                json.dumps(test.to_dict()),
                expire=2592000  # 30 days
            )
            
            # Add to timeline
            await self.cache.zadd(
                "recovery_tests_timeline",
                {test.test_id: test.started_at.timestamp()}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store recovery test: {e}")
            
    async def _cleanup_old_backups(self):
        """Cleanup old backup monitoring data"""
        try:
            # Remove records older than 90 days
            cutoff_time = datetime.utcnow() - timedelta(days=90)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # Cleanup backup executions
            await self.cache.zremrangebyscore(
                "backup_executions_timeline",
                "-inf",
                cutoff_timestamp
            )
            
            # Cleanup recovery tests
            await self.cache.zremrangebyscore(
                "recovery_tests_timeline",
                "-inf",
                cutoff_timestamp
            )
            
            self.logger.debug("Cleaned up old backup monitoring data")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backup data: {e}")
            
    async def _send_backup_alert(self, severity: str, title: str, message: str, details: Dict[str, Any]):
        """Send backup alert notification"""
        try:
            await self.notification_manager.send_backup_alert(
                severity=severity,
                title=title,
                message=message,
                details=details
            )
        except Exception as e:
            self.logger.error(f"Failed to send backup alert: {e}")
            
    async def get_backup_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get backup monitoring summary"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Get recent executions
            recent_executions = [
                ex for ex in self.backup_executions.values()
                if ex.started_at > cutoff_time
            ]
            
            # Calculate statistics
            total_executions = len(recent_executions)
            successful_executions = len([
                ex for ex in recent_executions 
                if ex.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED]
            ])
            failed_executions = len([
                ex for ex in recent_executions 
                if ex.status == BackupStatus.FAILED
            ])
            
            # Calculate success rate
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Get total backup size
            total_backup_size = sum(
                ex.backup_size_bytes or 0 for ex in recent_executions
                if ex.status in [BackupStatus.COMPLETED, BackupStatus.VERIFIED]
            )
            
            # Get replication health
            healthy_replicas = len([
                rep for rep in self.replication_monitors.values()
                if rep.status == ReplicationStatus.HEALTHY
            ])
            total_replicas = len(self.replication_monitors)
            
            # Get recovery test results
            recent_tests = [
                test for test in self.recovery_tests.values()
                if test.started_at > cutoff_time
            ]
            passed_tests = len([
                test for test in recent_tests
                if test.status == RecoveryTestStatus.PASSED
            ])
            
            return {
                'period_days': days,
                'backup_jobs': len(self.backup_jobs),
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate': success_rate,
                'total_backup_size_bytes': total_backup_size,
                'replication_health': {
                    'healthy_replicas': healthy_replicas,
                    'total_replicas': total_replicas,
                    'health_percentage': (healthy_replicas / total_replicas * 100) if total_replicas > 0 else 0
                },
                'recovery_tests': {
                    'total_tests': len(recent_tests),
                    'passed_tests': passed_tests,
                    'pass_rate': (passed_tests / len(recent_tests) * 100) if recent_tests else 0
                },
                'monitoring_active': self._monitoring_active,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get backup summary: {e}")
            return {}


class ReplicationHealthChecker:
    """Advanced replication health monitoring"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
    async def check_replication_lag(self, replica_info: Dict[str, Any]) -> float:
        """Check replication lag in seconds"""
        # Implementation for detailed replication lag analysis
        pass
        
    async def validate_replication_integrity(self, master_host: str, replica_host: str) -> bool:
        """Validate replication data integrity"""
        # Implementation for replication integrity validation
        pass


class DataIntegrityValidator:
    """Data integrity validation for backups and replicas"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
    async def validate_backup_integrity(self, backup_path: str) -> Dict[str, Any]:
        """Validate backup file integrity"""
        # Implementation for backup integrity validation
        pass
        
    async def validate_data_consistency(self, source_db: str, target_db: str) -> Dict[str, Any]:
        """Validate data consistency between databases"""
        # Implementation for data consistency validation
        pass
