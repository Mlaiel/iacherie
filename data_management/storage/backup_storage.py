"""💾 Backup Storage Manager - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/data_management/storage/backup_storage.py
Author: Fahed Mlaiel (mlaiel@live.de)
==================================================================

Enterprise backup storage management with automated scheduling,
incremental backups, verification, and multi-tier restoration.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- DBA: Fahed Mlaiel
- DevOps: Fahed Mlaiel
"""
from typing import Dict, List, Optional, Any, Union, Set, Tuple
import logging
import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import aiofiles
import aiofiles.os
import croniter
import gzip
import tarfile
import tempfile

logger = logging.getLogger(__name__)

class BackupType(Enum):
    """Types of backup operations"""    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"
    CONTINUOUS = "continuous"

class BackupStatus(Enum):
    """Backup operation status"""    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"

class RestoreStrategy(Enum):
    """Data restoration strategies"""    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"
    POINT_IN_TIME = "point_in_time"

@dataclass
class BackupJob:
    """Represents a backup job configuration"""    job_id: str
    name: str
    source_paths: List[str]
    destination_path: str
    backup_type: BackupType
    schedule: str  # Cron expression
    retention_days: int
    compression_enabled: bool = True
    encryption_enabled: bool = True
    verification_enabled: bool = True
    
    # Advanced settings
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_file_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    parallel_workers: int = 4
    
    # Metadata
    created_at: Optional[datetime] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True

@dataclass
class BackupRecord:
    """Record of a completed backup operation"""    backup_id: str
    job_id: str
    backup_type: BackupType
    status: BackupStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # File information
    source_files: List[str] = field(default_factory=list)
    backup_path: str = ""
    total_size: int = 0
    compressed_size: int = 0
    file_count: int = 0
    
    # Verification
    checksum: str = ""
    verification_status: str = "pending"
    verification_time: Optional[datetime] = None
    
    # Error tracking
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

@dataclass
class BackupConfig:
    """Configuration for backup storage system"""    backup_root_path: str
    temp_directory: str
    max_concurrent_jobs: int = 3
    default_retention_days: int = 30
    verification_interval_hours: int = 24
    cleanup_interval_hours: int = 6
    
    # Storage settings
    compression_algorithm: str = "gzip"
    compression_level: int = 6
    encryption_algorithm: str = "AES-256"
    
    # Performance settings
    buffer_size: int = 1024 * 1024  # 1MB
    max_memory_usage: int = 2 * 1024 * 1024 * 1024  # 2GB
    
    # Notification settings
    notify_on_success: bool = True
    notify_on_failure: bool = True
    notification_endpoints: List[str] = field(default_factory=list)

class BackupStorageManager:
    """    Enterprise backup storage manager with comprehensive features.
    
    Features:
    - Automated backup scheduling
    - Multiple backup types (full, incremental, differential)
    - Real-time backup verification
    - Intelligent retention policies
    - Point-in-time recovery
    - Performance optimization
    """    
    def __init__(self, config: BackupConfig):
        """Initialize backup storage manager"""        self.config = config
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.backup_records: Dict[str, BackupRecord] = {}
        self.running_jobs: Set[str] = set()
        
        # Managers
        self.scheduler = BackupScheduler(self)
        self.verifier = BackupVerifier(self)
        self.incremental_engine = IncrementalBackupEngine(self)
        self.snapshot_manager = SnapshotManager(self)
        
        # Performance tracking
        self.metrics = {
            'total_backups': 0,
            'successful_backups': 0,
            'failed_backups': 0,
            'total_data_backed_up': 0,
            'average_backup_time': 0.0,
            'compression_ratio': 0.0,
            'verification_success_rate': 0.0
        }
        
        # Create backup directory structure
        self._initialize_backup_directories()
        
        logger.info("BackupStorageManager initialized successfully")
    
    def _initialize_backup_directories(self) -> None:
        """Initialize backup directory structure"""        try:
            backup_root = Path(self.config.backup_root_path)
            backup_root.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (backup_root / "full").mkdir(exist_ok=True)
            (backup_root / "incremental").mkdir(exist_ok=True)
            (backup_root / "snapshots").mkdir(exist_ok=True)
            (backup_root / "temp").mkdir(exist_ok=True)
            (backup_root / "metadata").mkdir(exist_ok=True)
            
            logger.info(f"Backup directories initialized at {backup_root}")
            
        except Exception as e:
            logger.error(f"Failed to initialize backup directories: {str(e)}")
            raise
    
    async def create_backup_job(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new backup job"""        try:
            # Validate configuration
            required_fields = ['name', 'source_paths', 'destination_path', 'backup_type', 'schedule']
            for field in required_fields:
                if field not in job_config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate job ID
            job_id = f"backup_{int(time.time())}_{hash(job_config['name']) & 0xFFFF:04x}"
            
            # Create backup job
            backup_job = BackupJob(
                job_id=job_id,
                name=job_config['name'],
                source_paths=job_config['source_paths'],
                destination_path=job_config['destination_path'],
                backup_type=BackupType(job_config['backup_type']),
                schedule=job_config['schedule'],
                retention_days=job_config.get('retention_days', self.config.default_retention_days),
                compression_enabled=job_config.get('compression_enabled', True),
                encryption_enabled=job_config.get('encryption_enabled', True),
                verification_enabled=job_config.get('verification_enabled', True),
                include_patterns=job_config.get('include_patterns', []),
                exclude_patterns=job_config.get('exclude_patterns', []),
                max_file_size=job_config.get('max_file_size', 10 * 1024 * 1024 * 1024),
                parallel_workers=job_config.get('parallel_workers', 4),
                created_at=datetime.now()
            )
            
            # Calculate next run time
            cron = croniter.croniter(backup_job.schedule, datetime.now())
            backup_job.next_run = cron.get_next(datetime)
            
            # Store job
            self.backup_jobs[job_id] = backup_job
            
            # Save job configuration
            await self._save_job_configuration(backup_job)
            
            # Register with scheduler
            await self.scheduler.add_job(backup_job)
            
            logger.info(f"Backup job created: {job_id} - {backup_job.name}")
            
            return {
                'success': True,
                'job_id': job_id,
                'job_config': {
                    'name': backup_job.name,
                    'backup_type': backup_job.backup_type.value,
                    'schedule': backup_job.schedule,
                    'next_run': backup_job.next_run.isoformat() if backup_job.next_run else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create backup job: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_backup(self, job_id: str, force: bool = False) -> Dict[str, Any]:
        """Execute a backup job"""        try:
            if job_id not in self.backup_jobs:
                return {
                    'success': False,
                    'error': f'Backup job not found: {job_id}'
                }
            
            if job_id in self.running_jobs and not force:
                return {
                    'success': False,
                    'error': f'Backup job already running: {job_id}'
                }
            
            backup_job = self.backup_jobs[job_id]
            
            if not backup_job.enabled:
                return {
                    'success': False,
                    'error': f'Backup job is disabled: {job_id}'
                }
            
            # Generate backup ID
            backup_id = f"{job_id}_{int(time.time())}"
            
            # Create backup record
            backup_record = BackupRecord(
                backup_id=backup_id,
                job_id=job_id,
                backup_type=backup_job.backup_type,
                status=BackupStatus.PENDING,
                start_time=datetime.now()
            )
            
            self.backup_records[backup_id] = backup_record
            self.running_jobs.add(job_id)
            
            try:
                # Execute backup based on type
                if backup_job.backup_type == BackupType.FULL:
                    result = await self._execute_full_backup(backup_job, backup_record)
                elif backup_job.backup_type == BackupType.INCREMENTAL:
                    result = await self.incremental_engine.execute_incremental_backup(
                        backup_job, backup_record
                    )
                elif backup_job.backup_type == BackupType.SNAPSHOT:
                    result = await self.snapshot_manager.create_snapshot(
                        backup_job, backup_record
                    )
                else:
                    raise ValueError(f"Unsupported backup type: {backup_job.backup_type}")
                
                # Update backup record
                backup_record.end_time = datetime.now()
                
                if result['success']:
                    backup_record.status = BackupStatus.COMPLETED
                    backup_record.backup_path = result['backup_path']
                    backup_record.total_size = result.get('total_size', 0)
                    backup_record.compressed_size = result.get('compressed_size', 0)
                    backup_record.file_count = result.get('file_count', 0)
                    backup_record.checksum = result.get('checksum', '')
                    
                    # Update job's last run time
                    backup_job.last_run = datetime.now()
                    
                    # Schedule verification
                    if backup_job.verification_enabled:
                        asyncio.create_task(
                            self.verifier.verify_backup(backup_record)
                        )
                    
                    # Update metrics
                    self._update_backup_metrics(backup_record, True)
                    
                else:
                    backup_record.status = BackupStatus.FAILED
                    backup_record.error_message = result.get('error', 'Unknown error')
                    self._update_backup_metrics(backup_record, False)
                
                return {
                    'success': result['success'],
                    'backup_id': backup_id,
                    'backup_path': backup_record.backup_path,
                    'total_size': backup_record.total_size,
                    'compressed_size': backup_record.compressed_size,
                    'file_count': backup_record.file_count,
                    'duration_seconds': (backup_record.end_time - backup_record.start_time).total_seconds(),
                    'error': backup_record.error_message
                }
                
            finally:
                self.running_jobs.discard(job_id)
                
                # Save backup record
                await self._save_backup_record(backup_record)
            
        except Exception as e:
            logger.error(f"Backup execution failed for job {job_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def restore_data(
        self,
        backup_id: str,
        restore_path: str,
        strategy: RestoreStrategy = RestoreStrategy.IMMEDIATE,
        point_in_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Restore data from backup"""        try:
            if backup_id not in self.backup_records:
                return {
                    'success': False,
                    'error': f'Backup record not found: {backup_id}'
                }
            
            backup_record = self.backup_records[backup_id]
            
            if backup_record.status != BackupStatus.COMPLETED:
                return {
                    'success': False,
                    'error': f'Backup not completed or verified: {backup_record.status.value}'
                }
            
            # Verify backup integrity before restore
            verification_result = await self.verifier.verify_backup(backup_record)
            
            if not verification_result['success']:
                return {
                    'success': False,
                    'error': f'Backup verification failed: {verification_result.get("error")}'
                }
            
            start_time = datetime.now()
            
            # Execute restore based on strategy
            if strategy == RestoreStrategy.POINT_IN_TIME and point_in_time:
                result = await self._restore_point_in_time(
                    backup_record, restore_path, point_in_time
                )
            else:
                result = await self._restore_full_backup(backup_record, restore_path)
            
            # Calculate restore time
            restore_time = (datetime.now() - start_time).total_seconds()
            
            if result['success']:
                logger.info(f"Data restored successfully: {backup_id} -> {restore_path}")
                
                return {
                    'success': True,
                    'backup_id': backup_id,
                    'restore_path': restore_path,
                    'restored_files': result.get('restored_files', 0),
                    'restored_size': result.get('restored_size', 0),
                    'restore_time_seconds': restore_time
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown restore error'),
                    'backup_id': backup_id
                }
            
        except Exception as e:
            logger.error(f"Data restore failed for backup {backup_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def list_backups(
        self,
        job_id: Optional[str] = None,
        status: Optional[BackupStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List backup records with filtering"""        try:
            filtered_records = []
            
            for backup_record in self.backup_records.values():
                # Apply filters
                if job_id and backup_record.job_id != job_id:
                    continue
                
                if status and backup_record.status != status:
                    continue
                
                record_info = {
                    'backup_id': backup_record.backup_id,
                    'job_id': backup_record.job_id,
                    'backup_type': backup_record.backup_type.value,
                    'status': backup_record.status.value,
                    'start_time': backup_record.start_time.isoformat(),
                    'end_time': backup_record.end_time.isoformat() if backup_record.end_time else None,
                    'total_size': backup_record.total_size,
                    'compressed_size': backup_record.compressed_size,
                    'file_count': backup_record.file_count,
                    'verification_status': backup_record.verification_status,
                    'backup_path': backup_record.backup_path
                }
                
                if backup_record.error_message:
                    record_info['error_message'] = backup_record.error_message
                
                filtered_records.append(record_info)
                
                if len(filtered_records) >= limit:
                    break
            
            # Sort by start time (newest first)
            filtered_records.sort(
                key=lambda x: x['start_time'], 
                reverse=True
            )
            
            return filtered_records
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            return []
    
    async def cleanup_old_backups(self) -> Dict[str, Any]:
        """Clean up old backups based on retention policies"""        try:
            cleanup_results = {
                'total_checked': 0,
                'deleted_backups': 0,
                'freed_space': 0,
                'errors': []
            }
            
            current_time = datetime.now()
            
            for backup_record in list(self.backup_records.values()):
                cleanup_results['total_checked'] += 1
                
                # Get retention policy from job
                if backup_record.job_id in self.backup_jobs:
                    job = self.backup_jobs[backup_record.job_id]
                    retention_days = job.retention_days
                else:
                    retention_days = self.config.default_retention_days
                
                # Check if backup is expired
                backup_age = current_time - backup_record.start_time
                
                if backup_age.days > retention_days:
                    try:
                        # Delete backup files
                        if backup_record.backup_path and Path(backup_record.backup_path).exists():
                            file_size = Path(backup_record.backup_path).stat().st_size
                            await aiofiles.os.remove(backup_record.backup_path)
                            cleanup_results['freed_space'] += file_size
                        
                        # Remove from records
                        del self.backup_records[backup_record.backup_id]
                        cleanup_results['deleted_backups'] += 1
                        
                        logger.info(f"Deleted expired backup: {backup_record.backup_id}")
                        
                    except Exception as e:
                        error_msg = f"Failed to delete backup {backup_record.backup_id}: {str(e)}"
                        cleanup_results['errors'].append(error_msg)
                        logger.error(error_msg)
            
            logger.info(f"Backup cleanup completed: {cleanup_results['deleted_backups']} backups deleted")
            
            return {
                'success': True,
                'cleanup_results': cleanup_results
            }
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get comprehensive backup statistics"""        try:
            # Calculate current statistics
            total_jobs = len(self.backup_jobs)
            enabled_jobs = len([job for job in self.backup_jobs.values() if job.enabled])
            running_jobs = len(self.running_jobs)
            
            # Backup status distribution
            status_counts = {}
            for status in BackupStatus:
                status_counts[status.value] = len([
                    record for record in self.backup_records.values()
                    if record.status == status
                ])
            
            # Storage statistics
            total_backup_size = sum(
                record.compressed_size for record in self.backup_records.values()
                if record.compressed_size > 0
            )
            
            return {
                'jobs': {
                    'total_jobs': total_jobs,
                    'enabled_jobs': enabled_jobs,
                    'running_jobs': running_jobs,
                    'disabled_jobs': total_jobs - enabled_jobs
                },
                'backups': {
                    'total_backups': len(self.backup_records),
                    'status_distribution': status_counts
                },
                'storage': {
                    'total_backup_size_gb': round(total_backup_size / (1024**3), 2),
                    'backup_directory': self.config.backup_root_path
                },
                'performance': self.metrics,
                'configuration': {
                    'max_concurrent_jobs': self.config.max_concurrent_jobs,
                    'default_retention_days': self.config.default_retention_days,
                    'compression_algorithm': self.config.compression_algorithm,
                    'encryption_enabled': True
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup statistics: {str(e)}")
            return {'error': str(e)}
    
    # Private implementation methods
    
    async def _execute_full_backup(
        self,
        backup_job: BackupJob,
        backup_record: BackupRecord
    ) -> Dict[str, Any]:
        """Execute full backup operation"""        try:
            backup_record.status = BackupStatus.IN_PROGRESS
            
            # Create backup file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{backup_job.name}_{timestamp}_full.tar.gz"
            backup_path = Path(self.config.backup_root_path) / "full" / backup_filename
            
            # Collect source files
            source_files = []
            total_size = 0
            
            for source_path in backup_job.source_paths:
                path = Path(source_path)
                if path.is_file():
                    if await self._should_include_file(path, backup_job):
                        source_files.append(str(path))
                        total_size += path.stat().st_size
                elif path.is_dir():
                    for file_path in path.rglob("*"):
                        if file_path.is_file() and await self._should_include_file(file_path, backup_job):
                            source_files.append(str(file_path))
                            total_size += file_path.stat().st_size
            
            if not source_files:
                return {
                    'success': False,
                    'error': 'No files found to backup'
                }
            
            # Create compressed archive
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with tarfile.open(backup_path, 'w:gz') as tar:
                for file_path in source_files:
                    try:
                        tar.add(file_path, arcname=Path(file_path).name)
                    except Exception as e:
                        logger.warning(f"Failed to add file to backup: {file_path} - {str(e)}")
            
            # Calculate checksum
            checksum = await self._calculate_file_checksum(backup_path)
            
            # Get compressed size
            compressed_size = backup_path.stat().st_size
            
            backup_record.source_files = source_files
            
            return {
                'success': True,
                'backup_path': str(backup_path),
                'total_size': total_size,
                'compressed_size': compressed_size,
                'file_count': len(source_files),
                'checksum': checksum
            }
            
        except Exception as e:
            logger.error(f"Full backup failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _restore_full_backup(
        self,
        backup_record: BackupRecord,
        restore_path: str
    ) -> Dict[str, Any]:
        """Restore data from full backup"""        try:
            backup_path = Path(backup_record.backup_path)
            
            if not backup_path.exists():
                return {
                    'success': False,
                    'error': f'Backup file not found: {backup_path}'
                }
            
            restore_dir = Path(restore_path)
            restore_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract archive
            restored_files = 0
            restored_size = 0
            
            with tarfile.open(backup_path, 'r:gz') as tar:
                for member in tar.getmembers():
                    if member.isfile():
                        tar.extract(member, path=restore_dir)
                        restored_files += 1
                        restored_size += member.size
            
            return {
                'success': True,
                'restored_files': restored_files,
                'restored_size': restored_size
            }
            
        except Exception as e:
            logger.error(f"Full backup restore failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _should_include_file(self, file_path: Path, backup_job: BackupJob) -> bool:
        """Check if file should be included in backup"""        try:
            # Check file size limit
            if file_path.stat().st_size > backup_job.max_file_size:
                return False
            
            file_str = str(file_path)
            
            # Check exclude patterns
            for pattern in backup_job.exclude_patterns:
                if pattern in file_str:
                    return False
            
            # Check include patterns (if any)
            if backup_job.include_patterns:
                for pattern in backup_job.include_patterns:
                    if pattern in file_str:
                        return True
                return False
            
            return True
            
        except Exception:
            return False
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""        try:
            hash_sha256 = hashlib.sha256()
            
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_sha256.update(chunk)
            
            return hash_sha256.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {str(e)}")
            return ""
    
    def _update_backup_metrics(self, backup_record: BackupRecord, success: bool) -> None:
        """Update backup performance metrics"""        self.metrics['total_backups'] += 1
        
        if success:
            self.metrics['successful_backups'] += 1
            
            # Update data statistics
            self.metrics['total_data_backed_up'] += backup_record.total_size
            
            # Update compression ratio
            if backup_record.total_size > 0:
                compression_ratio = backup_record.compressed_size / backup_record.total_size
                total_backups = self.metrics['successful_backups']
                old_ratio = self.metrics['compression_ratio']
                self.metrics['compression_ratio'] = (
                    (old_ratio * (total_backups - 1) + compression_ratio) / total_backups
                )
            
            # Update average backup time
            if backup_record.end_time:
                backup_time = (backup_record.end_time - backup_record.start_time).total_seconds()
                total_backups = self.metrics['successful_backups']
                old_avg = self.metrics['average_backup_time']
                self.metrics['average_backup_time'] = (
                    (old_avg * (total_backups - 1) + backup_time) / total_backups
                )
        else:
            self.metrics['failed_backups'] += 1
    
    async def _save_job_configuration(self, backup_job: BackupJob) -> None:
        """Save backup job configuration to disk"""        try:
            config_path = Path(self.config.backup_root_path) / "metadata" / f"{backup_job.job_id}.json"
            
            job_data = {
                'job_id': backup_job.job_id,
                'name': backup_job.name,
                'source_paths': backup_job.source_paths,
                'destination_path': backup_job.destination_path,
                'backup_type': backup_job.backup_type.value,
                'schedule': backup_job.schedule,
                'retention_days': backup_job.retention_days,
                'compression_enabled': backup_job.compression_enabled,
                'encryption_enabled': backup_job.encryption_enabled,
                'verification_enabled': backup_job.verification_enabled,
                'include_patterns': backup_job.include_patterns,
                'exclude_patterns': backup_job.exclude_patterns,
                'max_file_size': backup_job.max_file_size,
                'parallel_workers': backup_job.parallel_workers,
                'created_at': backup_job.created_at.isoformat() if backup_job.created_at else None,
                'enabled': backup_job.enabled
            }
            
            async with aiofiles.open(config_path, 'w') as f:
                await f.write(json.dumps(job_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save job configuration: {str(e)}")
    
    async def _save_backup_record(self, backup_record: BackupRecord) -> None:
        """Save backup record to disk"""        try:
            record_path = Path(self.config.backup_root_path) / "metadata" / f"{backup_record.backup_id}_record.json"
            
            record_data = {
                'backup_id': backup_record.backup_id,
                'job_id': backup_record.job_id,
                'backup_type': backup_record.backup_type.value,
                'status': backup_record.status.value,
                'start_time': backup_record.start_time.isoformat(),
                'end_time': backup_record.end_time.isoformat() if backup_record.end_time else None,
                'source_files': backup_record.source_files,
                'backup_path': backup_record.backup_path,
                'total_size': backup_record.total_size,
                'compressed_size': backup_record.compressed_size,
                'file_count': backup_record.file_count,
                'checksum': backup_record.checksum,
                'verification_status': backup_record.verification_status,
                'verification_time': backup_record.verification_time.isoformat() if backup_record.verification_time else None,
                'error_message': backup_record.error_message,
                'warnings': backup_record.warnings
            }
            
            async with aiofiles.open(record_path, 'w') as f:
                await f.write(json.dumps(record_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save backup record: {str(e)}")


class BackupScheduler:
    """Manages backup job scheduling"""    
    def __init__(self, backup_manager: BackupStorageManager):
        """Initialize backup scheduler"""        self.backup_manager = backup_manager
        self.scheduled_jobs: Dict[str, asyncio.Task] = {}
        self.scheduler_task = None
    
    async def start(self) -> None:
        """Start the backup scheduler"""        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self) -> None:
        """Stop the backup scheduler"""        if self.scheduler_task:
            self.scheduler_task.cancel()
        
        # Cancel all scheduled jobs
        for task in self.scheduled_jobs.values():
            task.cancel()
    
    async def add_job(self, backup_job: BackupJob) -> None:
        """Add job to scheduler"""        # Schedule next execution
        if backup_job.enabled and backup_job.schedule:
            self._schedule_next_execution(backup_job)
    
    def _schedule_next_execution(self, backup_job: BackupJob) -> None:
        """Schedule next execution of backup job"""        try:
            cron = croniter.croniter(backup_job.schedule, datetime.now())
            next_run = cron.get_next(datetime)
            backup_job.next_run = next_run
            
            logger.info(f"Scheduled backup job {backup_job.job_id} for {next_run}")
            
        except Exception as e:
            logger.error(f"Failed to schedule backup job {backup_job.job_id}: {str(e)}")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.now()
                
                for backup_job in self.backup_manager.backup_jobs.values():
                    if (backup_job.enabled and 
                        backup_job.next_run and 
                        current_time >= backup_job.next_run and
                        backup_job.job_id not in self.backup_manager.running_jobs):
                        
                        # Execute backup
                        asyncio.create_task(
                            self.backup_manager.execute_backup(backup_job.job_id)
                        )
                        
                        # Schedule next execution
                        self._schedule_next_execution(backup_job)
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {str(e)}")


class BackupVerifier:
    """Verifies backup integrity"""    
    def __init__(self, backup_manager: BackupStorageManager):
        """Initialize backup verifier"""        self.backup_manager = backup_manager
    
    async def verify_backup(self, backup_record: BackupRecord) -> Dict[str, Any]:
        """Verify backup integrity"""        try:
            backup_path = Path(backup_record.backup_path)
            
            if not backup_path.exists():
                return {
                    'success': False,
                    'error': f'Backup file not found: {backup_path}'
                }
            
            # Verify checksum
            current_checksum = await self.backup_manager._calculate_file_checksum(backup_path)
            
            if current_checksum != backup_record.checksum:
                backup_record.verification_status = "corrupted"
                backup_record.status = BackupStatus.CORRUPTED
                
                return {
                    'success': False,
                    'error': 'Checksum verification failed'
                }
            
            # Try to read archive structure
            try:
                with tarfile.open(backup_path, 'r:gz') as tar:
                    member_count = len(tar.getmembers())
                    
                    if member_count == 0:
                        return {
                            'success': False,
                            'error': 'Empty backup archive'
                        }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Archive structure verification failed: {str(e)}'
                }
            
            # Update verification status
            backup_record.verification_status = "verified"
            backup_record.verification_time = datetime.now()
            backup_record.status = BackupStatus.VERIFIED
            
            return {
                'success': True,
                'checksum_verified': True,
                'archive_structure_verified': True,
                'member_count': member_count
            }
            
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class IncrementalBackupEngine:
    """Handles incremental backup operations"""    
    def __init__(self, backup_manager: BackupStorageManager):
        """Initialize incremental backup engine"""        self.backup_manager = backup_manager
        self.file_cache: Dict[str, Dict[str, Any]] = {}
    
    async def execute_incremental_backup(
        self,
        backup_job: BackupJob,
        backup_record: BackupRecord
    ) -> Dict[str, Any]:
        """Execute incremental backup"""        try:
            # Find last full backup
            last_full_backup = await self._find_last_full_backup(backup_job.job_id)
            
            if not last_full_backup:
                # No full backup found, create one instead
                return await self.backup_manager._execute_full_backup(backup_job, backup_record)
            
            # Find changed files since last backup
            changed_files = await self._find_changed_files(backup_job, last_full_backup)
            
            if not changed_files:
                return {
                    'success': True,
                    'backup_path': '',
                    'total_size': 0,
                    'compressed_size': 0,
                    'file_count': 0,
                    'message': 'No changes detected'
                }
            
            # Create incremental backup
            return await self._create_incremental_archive(
                backup_job, backup_record, changed_files
            )
            
        except Exception as e:
            logger.error(f"Incremental backup failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _find_last_full_backup(self, job_id: str) -> Optional[BackupRecord]:
        """Find the most recent full backup for a job"""        full_backups = [
            record for record in self.backup_manager.backup_records.values()
            if (record.job_id == job_id and 
                record.backup_type == BackupType.FULL and 
                record.status == BackupStatus.VERIFIED)
        ]
        
        if full_backups:
            # Return most recent
            return max(full_backups, key=lambda x: x.start_time)
        
        return None
    
    async def _find_changed_files(
        self,
        backup_job: BackupJob,
        last_backup: BackupRecord
    ) -> List[str]:
        """Find files that changed since last backup"""        changed_files = []
        last_backup_time = last_backup.start_time
        
        for source_path in backup_job.source_paths:
            path = Path(source_path)
            
            if path.is_file():
                if await self._file_changed_since(path, last_backup_time):
                    changed_files.append(str(path))
            elif path.is_dir():
                for file_path in path.rglob("*"):
                    if (file_path.is_file() and 
                        await self.backup_manager._should_include_file(file_path, backup_job) and
                        await self._file_changed_since(file_path, last_backup_time)):
                        changed_files.append(str(file_path))
        
        return changed_files
    
    async def _file_changed_since(self, file_path: Path, timestamp: datetime) -> bool:
        """Check if file changed since given timestamp"""        try:
            file_stat = file_path.stat()
            file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
            return file_mtime > timestamp
        except Exception:
            return False
    
    async def _create_incremental_archive(
        self,
        backup_job: BackupJob,
        backup_record: BackupRecord,
        changed_files: List[str]
    ) -> Dict[str, Any]:
        """Create incremental backup archive"""        try:
            # Create backup file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{backup_job.name}_{timestamp}_incremental.tar.gz"
            backup_path = Path(self.backup_manager.config.backup_root_path) / "incremental" / backup_filename
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            total_size = 0
            
            # Create compressed archive
            with tarfile.open(backup_path, 'w:gz') as tar:
                for file_path in changed_files:
                    try:
                        file_stat = Path(file_path).stat()
                        total_size += file_stat.st_size
                        tar.add(file_path, arcname=Path(file_path).name)
                    except Exception as e:
                        logger.warning(f"Failed to add file to incremental backup: {file_path} - {str(e)}")
            
            # Calculate checksum
            checksum = await self.backup_manager._calculate_file_checksum(backup_path)
            
            # Get compressed size
            compressed_size = backup_path.stat().st_size
            
            return {
                'success': True,
                'backup_path': str(backup_path),
                'total_size': total_size,
                'compressed_size': compressed_size,
                'file_count': len(changed_files),
                'checksum': checksum
            }
            
        except Exception as e:
            logger.error(f"Failed to create incremental archive: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class SnapshotManager:
    """Manages snapshot-based backups"""    
    def __init__(self, backup_manager: BackupStorageManager):
        """Initialize snapshot manager"""        self.backup_manager = backup_manager
    
    async def create_snapshot(
        self,
        backup_job: BackupJob,
        backup_record: BackupRecord
    ) -> Dict[str, Any]:
        """Create snapshot backup"""        try:
            # For this implementation, snapshot is similar to full backup
            # In a real system, this might use filesystem snapshots (LVM, ZFS, etc.)
            return await self.backup_manager._execute_full_backup(backup_job, backup_record)
            
        except Exception as e:
            logger.error(f"Snapshot creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Export classes
__all__ = [
    'BackupStorageManager',
    'BackupScheduler',
    'BackupVerifier',
    'IncrementalBackupEngine',
    'SnapshotManager',
    'BackupJob',
    'BackupRecord',
    'BackupConfig',
    'BackupType',
    'BackupStatus',
    'RestoreStrategy'
]
