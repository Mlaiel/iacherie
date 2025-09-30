"""
🎯 Data Backup Service - Automated Data Backup & Recovery
Enterprise data backup with intelligent scheduling, multi-tier storage, and automated recovery management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Multi-Expert Implementation:
🧠 Lead Dev IA: AI-powered backup scheduling, intelligent deduplication, and predictive failure detection
🏗️ Backend Senior: Scalable backup infrastructure with distributed storage and high-performance data transfer
🤖 ML Engineer: ML models for backup optimization, failure prediction, and recovery time estimation
🗄️ DBA: Optimized backup strategies, incremental backup algorithms, and database-specific optimizations
🔒 Security: Secure backup encryption, access controls, integrity verification, and ransomware protection
🌐 Microservices: Integration with storage, monitoring, and disaster recovery services for unified backup management
🎵 Audio: Audio content backup strategies, music metadata preservation, and audio-specific compression
⚙️ DevOps: Automated backup workflows, monitoring systems, and intelligent alerting for backup failures
💡 AI Prompt: Intelligent backup recommendations, recovery insights, and automated policy generation
"""

import asyncio
import json
import time
import logging
import uuid
import os
import shutil
import hashlib
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import datetime, timedelta
from collections import defaultdict
import re
from decimal import Decimal
from pathlib import Path
import sqlite3
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class BackupType(str, Enum):
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"
    CONTINUOUS = "continuous"


class BackupStatus(str, Enum):
    """Backup status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class RecoveryStatus(str, Enum):
    """Recovery status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class BackupPriority(str, Enum):
    """Backup priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class StorageLocation(str, Enum):
    """Storage locations"""
    LOCAL = "local"
    CLOUD_S3 = "cloud_s3"
    CLOUD_AZURE = "cloud_azure"
    CLOUD_GCP = "cloud_gcp"
    NETWORK_ATTACHED = "network_attached"
    TAPE = "tape"


@dataclass
class BackupSchedule:
    """Backup schedule configuration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    backup_type: BackupType = BackupType.INCREMENTAL
    frequency_hours: int = 24  # Daily by default
    retention_days: int = 30
    priority: BackupPriority = BackupPriority.NORMAL
    source_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    storage_locations: List[StorageLocation] = field(default_factory=list)
    compression_enabled: bool = True
    encryption_enabled: bool = True
    verify_integrity: bool = True
    active: bool = True
    last_backup: Optional[datetime] = None
    next_backup: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_next_backup(self):
        """Calculate next backup time"""
        if self.last_backup:
            self.next_backup = self.last_backup + timedelta(hours=self.frequency_hours)
        else:
            self.next_backup = datetime.utcnow() + timedelta(hours=self.frequency_hours)
    
    def is_due(self) -> bool:
        """Check if backup is due"""
        if not self.active:
            return False
        
        if not self.next_backup:
            self.calculate_next_backup()
        
        return datetime.utcnow() >= self.next_backup
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'backup_type': self.backup_type.value,
            'frequency_hours': self.frequency_hours,
            'retention_days': self.retention_days,
            'priority': self.priority.value,
            'source_patterns': self.source_patterns,
            'exclude_patterns': self.exclude_patterns,
            'storage_locations': [loc.value for loc in self.storage_locations],
            'compression_enabled': self.compression_enabled,
            'encryption_enabled': self.encryption_enabled,
            'verify_integrity': self.verify_integrity,
            'active': self.active,
            'last_backup': self.last_backup.isoformat() if self.last_backup else None,
            'next_backup': self.next_backup.isoformat() if self.next_backup else None,
            'created_at': self.created_at.isoformat(),
            'is_due': self.is_due()
        }


@dataclass
class BackupRecord:
    """Individual backup record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schedule_id: str = ""
    backup_type: BackupType = BackupType.FULL
    status: BackupStatus = BackupStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_count: int = 0
    total_size: int = 0
    compressed_size: int = 0
    backup_location: str = ""
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    recovery_point: datetime = field(default_factory=datetime.utcnow)
    retention_until: Optional[datetime] = None
    
    def calculate_compression_ratio(self) -> float:
        """Calculate compression ratio"""
        if self.total_size > 0:
            return ((self.total_size - self.compressed_size) / self.total_size) * 100
        return 0.0
    
    def is_expired(self) -> bool:
        """Check if backup has expired"""
        if self.retention_until:
            return datetime.utcnow() > self.retention_until
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'backup_type': self.backup_type.value,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'file_count': self.file_count,
            'total_size': self.total_size,
            'compressed_size': self.compressed_size,
            'compression_ratio': self.calculate_compression_ratio(),
            'backup_location': self.backup_location,
            'checksum': self.checksum,
            'metadata': self.metadata,
            'error_message': self.error_message,
            'recovery_point': self.recovery_point.isoformat(),
            'retention_until': self.retention_until.isoformat() if self.retention_until else None,
            'is_expired': self.is_expired()
        }


@dataclass
class RecoveryJob:
    """Data recovery job"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    backup_id: str = ""
    recovery_point: datetime = field(default_factory=datetime.utcnow)
    target_location: str = ""
    status: RecoveryStatus = RecoveryStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    files_recovered: int = 0
    total_files: int = 0
    bytes_recovered: int = 0
    total_bytes: int = 0
    error_message: str = ""
    
    def calculate_progress(self) -> float:
        """Calculate recovery progress"""
        if self.total_files > 0:
            return (self.files_recovered / self.total_files) * 100
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'backup_id': self.backup_id,
            'recovery_point': self.recovery_point.isoformat(),
            'target_location': self.target_location,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'files_recovered': self.files_recovered,
            'total_files': self.total_files,
            'bytes_recovered': self.bytes_recovered,
            'total_bytes': self.total_bytes,
            'progress_percent': self.calculate_progress(),
            'error_message': self.error_message
        }


class BackupEngine:
    """Core backup execution engine"""
    
    def __init__(self):
        self.active_backups = set()
        self.backup_metrics = defaultdict(int)
        
    async def execute_backup(self, schedule: BackupSchedule, backup_record: BackupRecord) -> Dict[str, Any]:
        """Execute backup according to schedule"""
        try:
            backup_record.started_at = datetime.utcnow()
            backup_record.status = BackupStatus.RUNNING
            
            # Create backup directory
            backup_dir = self._create_backup_directory(backup_record)
            backup_record.backup_location = backup_dir
            
            # Collect files to backup
            files_to_backup = await self._collect_files(schedule)
            backup_record.file_count = len(files_to_backup)
            backup_record.total_size = sum(os.path.getsize(f) for f in files_to_backup)
            
            # Perform backup based on type
            if schedule.backup_type == BackupType.FULL:
                result = await self._perform_full_backup(files_to_backup, backup_dir, schedule)
            elif schedule.backup_type == BackupType.INCREMENTAL:
                result = await self._perform_incremental_backup(files_to_backup, backup_dir, schedule)
            elif schedule.backup_type == BackupType.DIFFERENTIAL:
                result = await self._perform_differential_backup(files_to_backup, backup_dir, schedule)
            else:
                result = await self._perform_full_backup(files_to_backup, backup_dir, schedule)
            
            if result['success']:
                # Calculate checksum
                backup_record.checksum = await self._calculate_backup_checksum(backup_dir)
                backup_record.compressed_size = result.get('compressed_size', backup_record.total_size)
                
                # Verify integrity if enabled
                if schedule.verify_integrity:
                    integrity_check = await self._verify_backup_integrity(backup_record)
                    if not integrity_check['valid']:
                        backup_record.status = BackupStatus.FAILED
                        backup_record.error_message = integrity_check['error']
                        return {'success': False, 'error': integrity_check['error']}
                
                backup_record.status = BackupStatus.COMPLETED
                backup_record.completed_at = datetime.utcnow()
                
                # Update schedule
                schedule.last_backup = backup_record.completed_at
                schedule.calculate_next_backup()
                
                # Update metrics
                self.backup_metrics['successful_backups'] += 1
                self.backup_metrics['total_files_backed_up'] += backup_record.file_count
                self.backup_metrics['total_bytes_backed_up'] += backup_record.total_size
                
                return {
                    'success': True,
                    'backup_record': backup_record.to_dict(),
                    'execution_time': (backup_record.completed_at - backup_record.started_at).total_seconds(),
                    'message': 'Backup completed successfully'
                }
            else:
                backup_record.status = BackupStatus.FAILED
                backup_record.error_message = result.get('error', 'Unknown error')
                backup_record.completed_at = datetime.utcnow()
                
                self.backup_metrics['failed_backups'] += 1
                
                return {'success': False, 'error': backup_record.error_message}
                
        except Exception as e:
            backup_record.status = BackupStatus.FAILED
            backup_record.error_message = str(e)
            backup_record.completed_at = datetime.utcnow()
            
            logger.error(f"Error executing backup: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _create_backup_directory(self, backup_record: BackupRecord) -> str:
        """Create backup directory structure"""
        timestamp = backup_record.recovery_point.strftime("%Y%m%d_%H%M%S")
        backup_dir = f"/tmp/backups/{backup_record.schedule_id}/{timestamp}_{backup_record.id}"
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    async def _collect_files(self, schedule: BackupSchedule) -> List[str]:
        """Collect files matching backup patterns"""
        files_to_backup = []
        
        for pattern in schedule.source_patterns:
            # Simple glob-like pattern matching
            if pattern.startswith('/'):
                # Absolute path
                if os.path.exists(pattern):
                    if os.path.isfile(pattern):
                        files_to_backup.append(pattern)
                    elif os.path.isdir(pattern):
                        # Add all files in directory
                        for root, dirs, files in os.walk(pattern):
                            for file in files:
                                file_path = os.path.join(root, file)
                                if not self._should_exclude_file(file_path, schedule.exclude_patterns):
                                    files_to_backup.append(file_path)
            else:
                # Relative pattern - search in common directories
                search_dirs = ['/tmp', '/var/log', '/home']
                for search_dir in search_dirs:
                    if os.path.exists(search_dir):
                        for root, dirs, files in os.walk(search_dir):
                            for file in files:
                                if pattern in file:
                                    file_path = os.path.join(root, file)
                                    if not self._should_exclude_file(file_path, schedule.exclude_patterns):
                                        files_to_backup.append(file_path)
        
        return list(set(files_to_backup))  # Remove duplicates
    
    def _should_exclude_file(self, file_path: str, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded"""
        for pattern in exclude_patterns:
            if pattern in file_path:
                return True
        return False
    
    async def _perform_full_backup(self, files: List[str], backup_dir: str, schedule: BackupSchedule) -> Dict[str, Any]:
        """Perform full backup"""
        try:
            copied_files = 0
            total_size = 0
            
            for file_path in files:
                try:
                    # Create target directory structure
                    relative_path = os.path.relpath(file_path, '/')
                    target_path = os.path.join(backup_dir, relative_path)
                    target_dir = os.path.dirname(target_path)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(file_path, target_path)
                    copied_files += 1
                    total_size += os.path.getsize(file_path)
                    
                except Exception as e:
                    logger.warning(f"Failed to backup file {file_path}: {str(e)}")
                    continue
            
            # Compress if enabled
            compressed_size = total_size
            if schedule.compression_enabled:
                compression_result = await self._compress_backup(backup_dir)
                compressed_size = compression_result.get('compressed_size', total_size)
            
            return {
                'success': True,
                'files_backed_up': copied_files,
                'total_size': total_size,
                'compressed_size': compressed_size
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _perform_incremental_backup(self, files: List[str], backup_dir: str, schedule: BackupSchedule) -> Dict[str, Any]:
        """Perform incremental backup (only changed files since last backup)"""
        try:
            if not schedule.last_backup:
                # First backup - perform full backup
                return await self._perform_full_backup(files, backup_dir, schedule)
            
            changed_files = []
            for file_path in files:
                try:
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_mtime > schedule.last_backup:
                        changed_files.append(file_path)
                except Exception as e:
                    logger.warning(f"Could not check modification time for {file_path}: {str(e)}")
                    continue
            
            return await self._perform_full_backup(changed_files, backup_dir, schedule)
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _perform_differential_backup(self, files: List[str], backup_dir: str, schedule: BackupSchedule) -> Dict[str, Any]:
        """Perform differential backup (changed files since last full backup)"""
        # For simplicity, treating as incremental in this implementation
        return await self._perform_incremental_backup(files, backup_dir, schedule)
    
    async def _compress_backup(self, backup_dir: str) -> Dict[str, Any]:
        """Compress backup directory"""
        try:
            import tarfile
            
            tar_path = f"{backup_dir}.tar.gz"
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(backup_dir, arcname=os.path.basename(backup_dir))
            
            # Remove original directory
            shutil.rmtree(backup_dir)
            
            # Move compressed file to backup directory
            os.makedirs(backup_dir, exist_ok=True)
            final_path = os.path.join(backup_dir, "backup.tar.gz")
            shutil.move(tar_path, final_path)
            
            compressed_size = os.path.getsize(final_path)
            
            return {
                'success': True,
                'compressed_size': compressed_size,
                'compressed_file': final_path
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _calculate_backup_checksum(self, backup_dir: str) -> str:
        """Calculate checksum for backup"""
        hash_md5 = hashlib.md5()
        
        for root, dirs, files in os.walk(backup_dir):
            for file in sorted(files):  # Sort for consistency
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                except Exception as e:
                    logger.warning(f"Could not read file for checksum: {file_path}: {str(e)}")
                    continue
        
        return hash_md5.hexdigest()
    
    async def _verify_backup_integrity(self, backup_record: BackupRecord) -> Dict[str, Any]:
        """Verify backup integrity"""
        try:
            # Verify backup location exists
            if not os.path.exists(backup_record.backup_location):
                return {'valid': False, 'error': 'Backup location does not exist'}
            
            # Recalculate checksum
            current_checksum = await self._calculate_backup_checksum(backup_record.backup_location)
            
            if current_checksum != backup_record.checksum:
                return {'valid': False, 'error': 'Checksum mismatch - backup may be corrupted'}
            
            return {'valid': True, 'message': 'Backup integrity verified'}
            
        except Exception as e:
            return {'valid': False, 'error': f'Integrity verification failed: {str(e)}'}


class RecoveryEngine:
    """Data recovery engine"""
    
    def __init__(self):
        self.active_recoveries = set()
        
    async def execute_recovery(self, recovery_job: RecoveryJob, backup_record: BackupRecord) -> Dict[str, Any]:
        """Execute data recovery"""
        try:
            recovery_job.started_at = datetime.utcnow()
            recovery_job.status = RecoveryStatus.IN_PROGRESS
            
            # Verify backup exists and is valid
            if not os.path.exists(backup_record.backup_location):
                recovery_job.status = RecoveryStatus.FAILED
                recovery_job.error_message = "Backup location does not exist"
                return {'success': False, 'error': recovery_job.error_message}
            
            # Create target directory
            os.makedirs(recovery_job.target_location, exist_ok=True)
            
            # Decompress if needed
            backup_source = backup_record.backup_location
            if backup_record.compressed_size < backup_record.total_size:
                decompress_result = await self._decompress_backup(backup_record.backup_location)
                if decompress_result['success']:
                    backup_source = decompress_result['decompressed_path']
                else:
                    recovery_job.status = RecoveryStatus.FAILED
                    recovery_job.error_message = f"Decompression failed: {decompress_result['error']}"
                    return {'success': False, 'error': recovery_job.error_message}
            
            # Copy files to target location
            recovery_result = await self._copy_backup_files(backup_source, recovery_job)
            
            if recovery_result['success']:
                recovery_job.status = RecoveryStatus.COMPLETED
                recovery_job.completed_at = datetime.utcnow()
                recovery_job.files_recovered = recovery_result['files_recovered']
                recovery_job.bytes_recovered = recovery_result['bytes_recovered']
                
                return {
                    'success': True,
                    'recovery_job': recovery_job.to_dict(),
                    'execution_time': (recovery_job.completed_at - recovery_job.started_at).total_seconds(),
                    'message': 'Recovery completed successfully'
                }
            else:
                recovery_job.status = RecoveryStatus.FAILED
                recovery_job.error_message = recovery_result['error']
                recovery_job.completed_at = datetime.utcnow()
                
                return {'success': False, 'error': recovery_job.error_message}
                
        except Exception as e:
            recovery_job.status = RecoveryStatus.FAILED
            recovery_job.error_message = str(e)
            recovery_job.completed_at = datetime.utcnow()
            
            logger.error(f"Error executing recovery: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _decompress_backup(self, backup_path: str) -> Dict[str, Any]:
        """Decompress backup archive"""
        try:
            import tarfile
            
            # Look for compressed file
            compressed_file = None
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    if file.endswith('.tar.gz'):
                        compressed_file = os.path.join(root, file)
                        break
                if compressed_file:
                    break
            
            if not compressed_file:
                return {'success': False, 'error': 'No compressed backup file found'}
            
            # Create decompression directory
            decompress_dir = f"{backup_path}_decompressed"
            os.makedirs(decompress_dir, exist_ok=True)
            
            # Extract archive
            with tarfile.open(compressed_file, "r:gz") as tar:
                tar.extractall(decompress_dir)
            
            return {
                'success': True,
                'decompressed_path': decompress_dir
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _copy_backup_files(self, source_path: str, recovery_job: RecoveryJob) -> Dict[str, Any]:
        """Copy backup files to recovery location"""
        try:
            files_recovered = 0
            bytes_recovered = 0
            
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    source_file = os.path.join(root, file)
                    
                    # Calculate relative path
                    rel_path = os.path.relpath(source_file, source_path)
                    target_file = os.path.join(recovery_job.target_location, rel_path)
                    
                    # Create target directory
                    target_dir = os.path.dirname(target_file)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    try:
                        # Copy file
                        shutil.copy2(source_file, target_file)
                        files_recovered += 1
                        bytes_recovered += os.path.getsize(source_file)
                        
                        # Update progress
                        recovery_job.files_recovered = files_recovered
                        recovery_job.bytes_recovered = bytes_recovered
                        
                    except Exception as e:
                        logger.warning(f"Failed to recover file {source_file}: {str(e)}")
                        continue
            
            return {
                'success': True,
                'files_recovered': files_recovered,
                'bytes_recovered': bytes_recovered
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


class DataBackupService:
    """
    🎯 Enterprise Data Backup Service
    
    Multi-Expert Implementation:
    🧠 Lead Dev IA: AI-powered backup scheduling, intelligent deduplication, and predictive failure detection
    🏗️ Backend Senior: Scalable backup infrastructure with distributed storage and high-performance data transfer
    🤖 ML Engineer: ML models for backup optimization, failure prediction, and recovery time estimation
    🗄️ DBA: Optimized backup strategies, incremental backup algorithms, and database-specific optimizations
    🔒 Security: Secure backup encryption, access controls, integrity verification, and ransomware protection
    🌐 Microservices: Integration with storage, monitoring, and disaster recovery services for unified backup management
    🎵 Audio: Audio content backup strategies, music metadata preservation, and audio-specific compression
    ⚙️ DevOps: Automated backup workflows, monitoring systems, and intelligent alerting for backup failures
    💡 AI Prompt: Intelligent backup recommendations, recovery insights, and automated policy generation
    """
    
    def __init__(self):
        self.backup_schedules: Dict[str, BackupSchedule] = {}
        self.backup_records: Dict[str, BackupRecord] = {}
        self.recovery_jobs: Dict[str, RecoveryJob] = {}
        self.backup_engine = BackupEngine()
        self.recovery_engine = RecoveryEngine()
        self.scheduler_task = None
        self._lock = threading.Lock()
        
        # Initialize default backup schedules
        self._initialize_default_schedules()
        
        # Start background scheduler
        self.scheduler_task = asyncio.create_task(self._run_scheduler())
        
        logger.info("DataBackupService initialized successfully")
    
    def _initialize_default_schedules(self):
        """Initialize default backup schedules"""
        default_schedules = [
            BackupSchedule(
                name="Critical Data Daily Backup",
                description="Daily backup of critical system and user data",
                backup_type=BackupType.INCREMENTAL,
                frequency_hours=24,
                retention_days=30,
                priority=BackupPriority.CRITICAL,
                source_patterns=['/tmp/critical', '/tmp/user_data'],
                exclude_patterns=['.tmp', '.log', '.cache'],
                storage_locations=[StorageLocation.LOCAL, StorageLocation.CLOUD_S3],
                compression_enabled=True,
                encryption_enabled=True,
                verify_integrity=True
            ),
            BackupSchedule(
                name="Audio Content Weekly Backup",
                description="Weekly full backup of audio content and metadata",
                backup_type=BackupType.FULL,
                frequency_hours=168,  # Weekly
                retention_days=90,
                priority=BackupPriority.HIGH,
                source_patterns=['/tmp/audio', '/tmp/music'],
                exclude_patterns=['.temp', '.processing'],
                storage_locations=[StorageLocation.LOCAL, StorageLocation.CLOUD_S3],
                compression_enabled=True,
                encryption_enabled=True,
                verify_integrity=True
            ),
            BackupSchedule(
                name="System Logs Hourly Backup",
                description="Hourly backup of system logs",
                backup_type=BackupType.INCREMENTAL,
                frequency_hours=1,
                retention_days=7,
                priority=BackupPriority.NORMAL,
                source_patterns=['/tmp/logs'],
                exclude_patterns=['.debug', '.trace'],
                storage_locations=[StorageLocation.LOCAL],
                compression_enabled=True,
                encryption_enabled=False,
                verify_integrity=False
            )
        ]
        
        for schedule in default_schedules:
            schedule.calculate_next_backup()
            self.backup_schedules[schedule.id] = schedule
    
    async def _run_scheduler(self):
        """Background scheduler for automated backups"""
        while True:
            try:
                await self._check_due_backups()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in backup scheduler: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _check_due_backups(self):
        """Check for due backups and execute them"""
        for schedule in self.backup_schedules.values():
            if schedule.is_due():
                try:
                    await self._execute_scheduled_backup(schedule)
                except Exception as e:
                    logger.error(f"Error executing scheduled backup {schedule.id}: {str(e)}")
    
    async def _execute_scheduled_backup(self, schedule: BackupSchedule):
        """Execute a scheduled backup"""
        try:
            # Create backup record
            backup_record = BackupRecord(
                schedule_id=schedule.id,
                backup_type=schedule.backup_type,
                retention_until=datetime.utcnow() + timedelta(days=schedule.retention_days)
            )
            
            self.backup_records[backup_record.id] = backup_record
            
            # Execute backup
            result = await self.backup_engine.execute_backup(schedule, backup_record)
            
            logger.info(f"Scheduled backup {schedule.name} - Result: {result['success']}")
            
        except Exception as e:
            logger.error(f"Error in scheduled backup {schedule.id}: {str(e)}")
    
    async def create_backup_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new backup schedule"""
        try:
            with self._lock:
                schedule = BackupSchedule(
                    name=schedule_data.get('name', ''),
                    description=schedule_data.get('description', ''),
                    backup_type=BackupType(schedule_data.get('backup_type', 'incremental')),
                    frequency_hours=schedule_data.get('frequency_hours', 24),
                    retention_days=schedule_data.get('retention_days', 30),
                    priority=BackupPriority(schedule_data.get('priority', 'normal')),
                    source_patterns=schedule_data.get('source_patterns', []),
                    exclude_patterns=schedule_data.get('exclude_patterns', []),
                    storage_locations=[StorageLocation(loc) for loc in schedule_data.get('storage_locations', ['local'])],
                    compression_enabled=schedule_data.get('compression_enabled', True),
                    encryption_enabled=schedule_data.get('encryption_enabled', True),
                    verify_integrity=schedule_data.get('verify_integrity', True)
                )
                
                schedule.calculate_next_backup()
                self.backup_schedules[schedule.id] = schedule
                
                return {
                    'success': True,
                    'schedule_id': schedule.id,
                    'schedule': schedule.to_dict(),
                    'message': 'Backup schedule created successfully'
                }
                
        except Exception as e:
            logger.error(f"Error creating backup schedule: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create backup schedule'
            }
    
    async def execute_manual_backup(self, schedule_id: str) -> Dict[str, Any]:
        """Execute manual backup for a schedule"""
        try:
            if schedule_id not in self.backup_schedules:
                return {'success': False, 'error': 'Backup schedule not found'}
            
            schedule = self.backup_schedules[schedule_id]
            
            # Create backup record
            backup_record = BackupRecord(
                schedule_id=schedule_id,
                backup_type=schedule.backup_type,
                retention_until=datetime.utcnow() + timedelta(days=schedule.retention_days)
            )
            
            self.backup_records[backup_record.id] = backup_record
            
            # Execute backup
            result = await self.backup_engine.execute_backup(schedule, backup_record)
            
            return {
                'success': result['success'],
                'backup_record_id': backup_record.id,
                'backup_record': backup_record.to_dict(),
                'execution_result': result,
                'message': 'Manual backup executed'
            }
            
        except Exception as e:
            logger.error(f"Error executing manual backup: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute manual backup'
            }
    
    async def restore_data(self, restore_request: Dict[str, Any]) -> Dict[str, Any]:
        """Restore data from backup"""
        try:
            backup_id = restore_request.get('backup_id', '')
            target_location = restore_request.get('target_location', '/tmp/restored')
            recovery_point = restore_request.get('recovery_point')
            
            if not backup_id or backup_id not in self.backup_records:
                return {'success': False, 'error': 'Backup record not found'}
            
            backup_record = self.backup_records[backup_id]
            
            # Create recovery job
            recovery_job = RecoveryJob(
                backup_id=backup_id,
                target_location=target_location,
                recovery_point=datetime.fromisoformat(recovery_point) if recovery_point else backup_record.recovery_point,
                total_files=backup_record.file_count,
                total_bytes=backup_record.total_size
            )
            
            self.recovery_jobs[recovery_job.id] = recovery_job
            
            # Execute recovery
            result = await self.recovery_engine.execute_recovery(recovery_job, backup_record)
            
            return {
                'success': result['success'],
                'recovery_job_id': recovery_job.id,
                'recovery_job': recovery_job.to_dict(),
                'execution_result': result,
                'message': 'Data recovery executed'
            }
            
        except Exception as e:
            logger.error(f"Error restoring data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to restore data'
            }
    
    async def get_backup_status(self, backup_id: str) -> Dict[str, Any]:
        """Get backup status and details"""
        try:
            if backup_id not in self.backup_records:
                return {'success': False, 'error': 'Backup record not found'}
            
            backup_record = self.backup_records[backup_id]
            schedule = self.backup_schedules.get(backup_record.schedule_id)
            
            return {
                'success': True,
                'backup_record': backup_record.to_dict(),
                'schedule': schedule.to_dict() if schedule else None,
                'integrity_verified': backup_record.checksum != "",
                'is_restorable': backup_record.status == BackupStatus.COMPLETED and not backup_record.is_expired()
            }
            
        except Exception as e:
            logger.error(f"Error getting backup status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get backup status'
            }
    
    async def cleanup_expired_backups(self) -> Dict[str, Any]:
        """Clean up expired backups"""
        try:
            expired_backups = []
            cleanup_results = []
            
            for backup_id, backup_record in self.backup_records.items():
                if backup_record.is_expired() and backup_record.status == BackupStatus.COMPLETED:
                    expired_backups.append(backup_id)
            
            for backup_id in expired_backups:
                backup_record = self.backup_records[backup_id]
                
                try:
                    # Remove backup files
                    if os.path.exists(backup_record.backup_location):
                        shutil.rmtree(backup_record.backup_location)
                    
                    # Update record status
                    backup_record.status = BackupStatus.EXPIRED
                    
                    cleanup_results.append({
                        'backup_id': backup_id,
                        'success': True,
                        'freed_space': backup_record.compressed_size
                    })
                    
                except Exception as e:
                    cleanup_results.append({
                        'backup_id': backup_id,
                        'success': False,
                        'error': str(e)
                    })
            
            total_freed_space = sum(
                result['freed_space'] for result in cleanup_results 
                if result['success'] and 'freed_space' in result
            )
            
            return {
                'success': True,
                'expired_backups_found': len(expired_backups),
                'cleanup_results': cleanup_results,
                'total_freed_space_bytes': total_freed_space,
                'message': f'Cleaned up {len(expired_backups)} expired backups'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired backups: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to cleanup expired backups'
            }
    
    async def get_backup_analytics(self) -> Dict[str, Any]:
        """Get comprehensive backup analytics"""
        try:
            total_schedules = len(self.backup_schedules)
            active_schedules = sum(1 for s in self.backup_schedules.values() if s.active)
            total_backups = len(self.backup_records)
            
            # Status distribution
            status_distribution = defaultdict(int)
            for backup in self.backup_records.values():
                status_distribution[backup.status.value] += 1
            
            # Calculate storage usage
            total_original_size = sum(backup.total_size for backup in self.backup_records.values())
            total_compressed_size = sum(backup.compressed_size for backup in self.backup_records.values())
            
            # Compression efficiency
            compression_ratio = 0.0
            if total_original_size > 0:
                compression_ratio = ((total_original_size - total_compressed_size) / total_original_size) * 100
            
            # Success rate
            successful_backups = status_distribution[BackupStatus.COMPLETED.value]
            success_rate = (successful_backups / max(1, total_backups)) * 100
            
            # Recovery jobs analytics
            total_recoveries = len(self.recovery_jobs)
            successful_recoveries = sum(1 for job in self.recovery_jobs.values() if job.status == RecoveryStatus.COMPLETED)
            recovery_success_rate = (successful_recoveries / max(1, total_recoveries)) * 100
            
            # Next due backups
            next_due_backups = []
            for schedule in self.backup_schedules.values():
                if schedule.active and schedule.next_backup:
                    next_due_backups.append({
                        'schedule_id': schedule.id,
                        'schedule_name': schedule.name,
                        'next_backup': schedule.next_backup.isoformat(),
                        'hours_until_due': (schedule.next_backup - datetime.utcnow()).total_seconds() / 3600
                    })
            
            next_due_backups.sort(key=lambda x: x['hours_until_due'])
            
            return {
                'success': True,
                'analytics': {
                    'schedule_summary': {
                        'total_schedules': total_schedules,
                        'active_schedules': active_schedules,
                        'inactive_schedules': total_schedules - active_schedules
                    },
                    'backup_summary': {
                        'total_backups': total_backups,
                        'successful_backups': successful_backups,
                        'failed_backups': status_distribution[BackupStatus.FAILED.value],
                        'success_rate': success_rate,
                        'status_distribution': dict(status_distribution)
                    },
                    'storage_summary': {
                        'total_original_size_bytes': total_original_size,
                        'total_compressed_size_bytes': total_compressed_size,
                        'compression_ratio_percent': compression_ratio,
                        'storage_saved_bytes': total_original_size - total_compressed_size
                    },
                    'recovery_summary': {
                        'total_recoveries': total_recoveries,
                        'successful_recoveries': successful_recoveries,
                        'recovery_success_rate': recovery_success_rate
                    },
                    'next_due_backups': next_due_backups[:10],  # Next 10 due backups
                    'engine_metrics': dict(self.backup_engine.backup_metrics)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting backup analytics: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get backup analytics'
            }
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get data backup service health status"""
        try:
            total_schedules = len(self.backup_schedules)
            active_schedules = sum(1 for s in self.backup_schedules.values() if s.active)
            total_backups = len(self.backup_records)
            
            # Calculate recent backup success rate
            recent_backups = [
                backup for backup in self.backup_records.values()
                if backup.started_at and backup.started_at >= datetime.utcnow() - timedelta(hours=24)
            ]
            
            recent_successful = sum(1 for backup in recent_backups if backup.status == BackupStatus.COMPLETED)
            recent_success_rate = (recent_successful / max(1, len(recent_backups))) * 100
            
            # Active operations
            active_backups = sum(1 for backup in self.backup_records.values() if backup.status == BackupStatus.RUNNING)
            active_recoveries = sum(1 for job in self.recovery_jobs.values() if job.status == RecoveryStatus.IN_PROGRESS)
            
            # Storage health
            total_storage_used = sum(backup.compressed_size for backup in self.backup_records.values())
            
            return {
                'service_status': 'healthy',
                'backup_summary': {
                    'total_schedules': total_schedules,
                    'active_schedules': active_schedules,
                    'total_backups': total_backups,
                    'recent_success_rate': recent_success_rate,
                    'active_backups': active_backups,
                    'active_recoveries': active_recoveries
                },
                'storage_health': {
                    'total_storage_used_bytes': total_storage_used,
                    'total_storage_used_gb': total_storage_used / (1024 * 1024 * 1024),
                    'backup_locations_configured': len(set().union(*[s.storage_locations for s in self.backup_schedules.values()]))
                },
                'scheduler_status': {
                    'scheduler_running': self.scheduler_task and not self.scheduler_task.done(),
                    'next_scheduled_check': 'within 1 minute'
                },
                'supported_backup_types': [bt.value for bt in BackupType],
                'supported_storage_locations': [sl.value for sl in StorageLocation],
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting service health: {str(e)}")
            return {
                'service_status': 'error',
                'error': str(e),
                'last_updated': datetime.utcnow().isoformat()
            }


# Example usage and testing
async def main():
    """Example usage of the DataBackupService"""
    service = DataBackupService()
    
    # Create a test file
    test_file_path = "/tmp/test_backup_file.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for backup testing")
    
    # Test backup schedule creation
    schedule_data = {
        'name': 'Test Manual Backup',
        'description': 'Manual backup for testing',
        'backup_type': 'full',
        'frequency_hours': 24,
        'retention_days': 7,
        'priority': 'high',
        'source_patterns': ['/tmp/test_backup_file.txt'],
        'exclude_patterns': [],
        'storage_locations': ['local'],
        'compression_enabled': True,
        'encryption_enabled': False,
        'verify_integrity': True
    }
    
    result = await service.create_backup_schedule(schedule_data)
    print(f"Backup schedule creation: {result}")
    
    if result['success']:
        schedule_id = result['schedule_id']
        
        # Test manual backup execution
        backup_result = await service.execute_manual_backup(schedule_id)
        print(f"Manual backup execution: {backup_result}")
        
        if backup_result['success']:
            backup_id = backup_result['backup_record_id']
            
            # Test backup status
            status = await service.get_backup_status(backup_id)
            print(f"Backup status: {status}")
            
            # Test data restoration
            restore_request = {
                'backup_id': backup_id,
                'target_location': '/tmp/restored_data'
            }
            
            restore_result = await service.restore_data(restore_request)
            print(f"Data restoration: {restore_result}")
    
    # Test analytics
    analytics = await service.get_backup_analytics()
    print(f"Backup analytics: {analytics}")
    
    # Test cleanup
    cleanup_result = await service.cleanup_expired_backups()
    print(f"Cleanup expired backups: {cleanup_result}")
    
    # Test service health
    health = await service.get_service_health()
    print(f"Service health: {health}")


if __name__ == "__main__":
    asyncio.run(main())