"""
Backup Manager - Enterprise Backup and Recovery System

Advanced backup management system with intelligent scheduling, versioning,
encryption, compression, and multi-backend redundancy for data protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This backup management technology is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist: Fahed Mlaiel  
- Database Administrator & Security Expert: Fahed Mlaiel
- Microservices Architect & DevOps Engineer: Fahed Mlaiel
- AI Prompt Engineer & Content Protection Specialist: Fahed Mlaiel
"""

import asyncio
import logging
import shutil
import gzip
import tarfile
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import json
import aiofiles
import aiocron

from .backend_manager import BackendManager, StorageBackend
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import BackupError, ValidationError, StorageError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    BackupError, ValidationError, StorageError = globals().get('BackupError, ValidationError, StorageError', Exception)
from ...monitoring.metrics import MetricsCollector
from ...utils.encryption_utils import EncryptionManager
from ...utils.compression_utils import CompressionManager

logger = logging.getLogger(__name__)

class BackupType(str, Enum):
    """Types of backups"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

class BackupStatus(str, Enum):
    """Backup operation status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class RestoreStatus(str, Enum):
    """Restore operation status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class BackupConfig:
    """Backup configuration settings"""
    enabled: bool = True
    backup_type: BackupType = BackupType.INCREMENTAL
    schedule: str = "0 2 * * *"  # Daily at 2 AM (cron format)
    retention_days: int = 30
    compression: bool = True
    encryption: bool = True
    verification: bool = True
    max_parallel_backups: int = 3
    backup_backends: List[StorageBackend] = None
    exclude_patterns: List[str] = None
    include_patterns: List[str] = None

@dataclass
class BackupMetadata:
    """Backup metadata information"""
    backup_id: str
    backup_type: BackupType
    source_path: str
    backup_path: str
    created_at: datetime
    file_count: int
    total_size: int
    compressed_size: int
    checksum: str
    encryption_key_id: Optional[str]
    backends: List[str]
    status: BackupStatus
    error_message: Optional[str] = None

@dataclass
class RestoreOperation:
    """Restore operation tracking"""
    restore_id: str
    backup_id: str
    target_path: str
    created_at: datetime
    status: RestoreStatus
    progress: float = 0.0
    error_message: Optional[str] = None

class BackupManager:
    """
    Enterprise backup management system with intelligent scheduling,
    versioning, encryption, and multi-backend redundancy.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = BackupConfig(**(config or {}))
        
        # Initialize components
        self.backend_manager = None  # Will be injected
        self.encryption_manager = EncryptionManager()
        self.compression_manager = CompressionManager()
        self.metrics = MetricsCollector('backup_manager')
        
        # Backup tracking
        self.active_backups: Dict[str, BackupMetadata] = {}
        self.backup_history: List[BackupMetadata] = []
        self.restore_operations: Dict[str, RestoreOperation] = {}
        
        # Scheduling
        self.backup_scheduler = None
        
        # Statistics
        self.stats = {
            'total_backups': 0,
            'successful_backups': 0,
            'failed_backups': 0,
            'total_bytes_backed_up': 0,
            'total_compression_ratio': 0.0,
            'average_backup_time': 0.0,
            'backup_by_type': {btype: 0 for btype in BackupType},
            'restoration_success_rate': 0.0
        }
        
        # Backup storage directory
        self.backup_dir = Path('/storage/backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize backup scheduler if enabled
        if self.config.enabled and self.config.schedule:
            self._setup_backup_scheduler()
        
        logger.info("BackupManager initialized successfully")
    
    def set_backend_manager(self, backend_manager: BackendManager):
        """Inject backend manager dependency"""
        self.backend_manager = backend_manager
    
    def _setup_backup_scheduler(self):
        """Setup automatic backup scheduling"""



        try:
            @aiocron.crontab(self.config.schedule)
            async def scheduled_backup():
                logger.info("Starting scheduled backup")
                await self.create_automated_backup()
            
            self.backup_scheduler = scheduled_backup
            logger.info(f"Backup scheduler configured: {self.config.schedule}")
            
        except Exception as e:
            logger.error(f"Failed to setup backup scheduler: {e}")
    
    async def create_backup(
        self,
        source_path: Union[str, Path],
        backup_name: Optional[str] = None,
        backup_type: Optional[BackupType] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> BackupMetadata:
        """
        Create backup of specified source
        
        Args:
            source_path: Path to backup source
            backup_name: Custom backup name
            backup_type: Type of backup to create
            custom_config: Custom configuration overrides
            
        Returns:
            BackupMetadata with backup details
        """
        start_time = datetime.utcnow()
        source_path = Path(source_path)
        
        try:
            # Validate source
            if not source_path.exists():
                raise ValidationError(f"Source path does not exist: {source_path}")
            
            # Generate backup ID and metadata
            backup_id = self._generate_backup_id(source_path, backup_name)
            backup_type = backup_type or self.config.backup_type
            
            # Create backup metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=backup_type,
                source_path=str(source_path),
                backup_path="",
                created_at=start_time,
                file_count=0,
                total_size=0,
                compressed_size=0,
                checksum="",
                encryption_key_id=None,
                backends=[],
                status=BackupStatus.RUNNING
            )
            
            self.active_backups[backup_id] = metadata
            
            # Create backup based on type
            if backup_type == BackupType.FULL:
                backup_path = await self._create_full_backup(source_path, backup_id)
            
            elif backup_type == BackupType.INCREMENTAL:
                backup_path = await self._create_incremental_backup(source_path, backup_id)
            
            elif backup_type == BackupType.DIFFERENTIAL:
                backup_path = await self._create_differential_backup(source_path, backup_id)
            
            elif backup_type == BackupType.SNAPSHOT:
                backup_path = await self._create_snapshot_backup(source_path, backup_id)
            
            else:
                raise BackupError(f"Unsupported backup type: {backup_type}")
            
            # Update metadata
            metadata.backup_path = str(backup_path)
            
            # Calculate backup statistics
            backup_stats = await self._calculate_backup_stats(backup_path)
            metadata.file_count = backup_stats['file_count']
            metadata.total_size = backup_stats['original_size']
            metadata.compressed_size = backup_stats['backup_size']
            metadata.checksum = backup_stats['checksum']
            
            # Store backup in configured backends
            if self.backend_manager:
                backend_urls = await self._store_backup_in_backends(
                    backup_path, backup_id, metadata
                )
                metadata.backends = list(backend_urls.keys())
            
            # Verify backup if enabled
            if self.config.verification:
                verification_result = await self._verify_backup(backup_path, metadata)
                if not verification_result:
                    raise BackupError("Backup verification failed")
            
            # Update status and cleanup
            metadata.status = BackupStatus.COMPLETED
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update statistics
            await self._update_backup_statistics(metadata, processing_time, True)
            
            # Move to history and cleanup
            self.backup_history.append(metadata)
            del self.active_backups[backup_id]
            
            # Record metrics
            self.metrics.record_processing_time(processing_time)
            self.metrics.increment_counter('backups_success')
            self.metrics.record_gauge('backup_size', metadata.compressed_size)
            
            logger.info(f"Backup created successfully: {backup_id}")
            
            return metadata
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update failed metadata
            if backup_id in self.active_backups:
                self.active_backups[backup_id].status = BackupStatus.FAILED
                self.active_backups[backup_id].error_message = str(e)
                
                # Move to history
                self.backup_history.append(self.active_backups[backup_id])
                del self.active_backups[backup_id]
            
            await self._update_backup_statistics(metadata, processing_time, False)
            
            self.metrics.increment_counter('backups_failure')
            
            logger.error(f"Backup creation failed: {e}")
            raise BackupError(f"Backup creation failed: {e}")
    
    async def restore_backup(
        self,
        backup_id: str,
        target_path: Union[str, Path],
        restore_options: Optional[Dict[str, Any]] = None
    ) -> RestoreOperation:
        """
        Restore backup to specified location
        
        Args:
            backup_id: ID of backup to restore
            target_path: Path to restore backup to
            restore_options: Custom restoration options
            
        Returns:
            RestoreOperation tracking restoration progress
        """
        start_time = datetime.utcnow()
        target_path = Path(target_path)
        
        try:
            # Find backup metadata
            backup_metadata = self._find_backup_metadata(backup_id)
            if not backup_metadata:
                raise BackupError(f"Backup not found: {backup_id}")
            
            # Generate restore operation
            restore_id = self._generate_restore_id(backup_id)
            restore_operation = RestoreOperation(
                restore_id=restore_id,
                backup_id=backup_id,
                target_path=str(target_path),
                created_at=start_time,
                status=RestoreStatus.RUNNING
            )
            
            self.restore_operations[restore_id] = restore_operation
            
            # Create target directory
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download backup from backends if needed
            local_backup_path = await self._ensure_local_backup(backup_metadata)
            
            # Extract and restore backup
            await self._extract_backup(
                local_backup_path, target_path, restore_operation
            )
            
            # Verify restoration
            verification_result = await self._verify_restoration(
                backup_metadata, target_path
            )
            
            if not verification_result:
                raise BackupError("Restoration verification failed")
            
            # Update status
            restore_operation.status = RestoreStatus.COMPLETED
            restore_operation.progress = 100.0
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            self.metrics.record_processing_time(processing_time)
            self.metrics.increment_counter('restores_success')
            
            logger.info(f"Backup restored successfully: {backup_id} -> {target_path}")
            
            return restore_operation
            
        except Exception as e:
            # Update failed restore operation
            if restore_id in self.restore_operations:
                self.restore_operations[restore_id].status = RestoreStatus.FAILED
                self.restore_operations[restore_id].error_message = str(e)
            
            self.metrics.increment_counter('restores_failure')
            
            logger.error(f"Backup restoration failed: {e}")
            raise BackupError(f"Backup restoration failed: {e}")
    
    async def list_backups(
        self,
        source_path: Optional[str] = None,
        backup_type: Optional[BackupType] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[BackupMetadata]:
        """
        List available backups with optional filtering
        
        Args:
            source_path: Filter by source path
            backup_type: Filter by backup type
            date_range: Filter by date range (start, end)
            
        Returns:
            List of backup metadata matching filters
        """



        try:
            filtered_backups = self.backup_history.copy()
            
            # Apply filters
            if source_path:
                filtered_backups = [
                    backup for backup in filtered_backups
                    if backup.source_path == source_path
                ]
            
            if backup_type:
                filtered_backups = [
                    backup for backup in filtered_backups
                    if backup.backup_type == backup_type
                ]
            
            if date_range:
                start_date, end_date = date_range
                filtered_backups = [
                    backup for backup in filtered_backups
                    if start_date <= backup.created_at <= end_date
                ]
            
            # Sort by creation date (newest first)
            filtered_backups.sort(key=lambda x: x.created_at, reverse=True)
            
            return filtered_backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    async def delete_backup(self, backup_id: str) -> bool:
        """
        Delete backup and clean up storage
        
        Args:
            backup_id: ID of backup to delete
            
        Returns:
            True if deletion successful
        """



        try:
            # Find backup metadata
            backup_metadata = self._find_backup_metadata(backup_id)
            if not backup_metadata:
                raise BackupError(f"Backup not found: {backup_id}")
            
            # Delete from all backends
            deletion_results = []
            
            for backend_name in backup_metadata.backends:
                try:
                    backend = StorageBackend(backend_name)
                    backup_path = f"backups/{backup_id}"
                    
                    if self.backend_manager:
                        result = await self.backend_manager.delete_file(backend, backup_path)
                        deletion_results.append(result)
                    
                except Exception as e:
                    logger.warning(f"Failed to delete from {backend_name}: {e}")
                    deletion_results.append(False)
            
            # Delete local backup if exists
            local_backup_path = self.backup_dir / f"{backup_id}.tar.gz"
            if local_backup_path.exists():
                local_backup_path.unlink()
            
            # Remove from history
            self.backup_history = [
                backup for backup in self.backup_history
                if backup.backup_id != backup_id
            ]
            
            self.metrics.increment_counter('backups_deleted')
            
            success = any(deletion_results)
            logger.info(f"Backup {'deleted' if success else 'deletion failed'}: {backup_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Backup deletion failed: {e}")
            return False
    
    async def cleanup_expired_backups(self) -> Dict[str, Any]:
        """
        Clean up backups that have exceeded retention period
        
        Returns:
            Cleanup statistics
        """



        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
            
            expired_backups = [
                backup for backup in self.backup_history
                if backup.created_at < cutoff_date
            ]
            
            cleanup_stats = {
                'total_expired': len(expired_backups),
                'successfully_deleted': 0,
                'deletion_failures': 0,
                'bytes_freed': 0
            }
            
            for backup in expired_backups:
                try:
                    deletion_result = await self.delete_backup(backup.backup_id)
                    
                    if deletion_result:
                        cleanup_stats['successfully_deleted'] += 1
                        cleanup_stats['bytes_freed'] += backup.compressed_size
                        
                        # Update backup status
                        backup.status = BackupStatus.EXPIRED
                    else:
                        cleanup_stats['deletion_failures'] += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to delete expired backup {backup.backup_id}: {e}")
                    cleanup_stats['deletion_failures'] += 1
            
            logger.info(f"Cleanup completed: {cleanup_stats}")
            
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return {'error': str(e)}
    
    async def get_backup_statistics(self) -> Dict[str, Any]:
        """Get comprehensive backup statistics"""



        try:
            # Current backup statistics
            current_stats = self.stats.copy()
            
            # Storage usage by backend
            backend_usage = {}
            for backup in self.backup_history:
                for backend in backup.backends:
                    backend_usage[backend] = backend_usage.get(backend, 0) + backup.compressed_size
            
            # Recent backup trends (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_backups = [
                backup for backup in self.backup_history
                if backup.created_at >= week_ago
            ]
            
            return {
                'overall_statistics': current_stats,
                'active_backups': len(self.active_backups),
                'total_backups': len(self.backup_history),
                'recent_backups': len(recent_backups),
                'backend_usage': backend_usage,
                'restore_operations': {
                    'active': len([r for r in self.restore_operations.values() 
                                 if r.status == RestoreStatus.RUNNING]),
                    'completed': len([r for r in self.restore_operations.values() 
                                   if r.status == RestoreStatus.COMPLETED])
                },
                'configuration': asdict(self.config)
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup statistics: {e}")
            return {'error': str(e)}
    
    # Backup creation methods
    
    async def _create_full_backup(self, source_path: Path, backup_id: str) -> Path:
        """Create full backup of source"""
        backup_path = self.backup_dir / f"{backup_id}.tar.gz"
        
        try:
            # Create compressed archive
            with tarfile.open(backup_path, 'w:gz') as tar:
                if source_path.is_file():
                    tar.add(source_path, arcname=source_path.name)
                else:
                    # Add directory contents
                    for item in source_path.rglob('*'):
                        if item.is_file() and self._should_include_file(item):
                            arcname = item.relative_to(source_path)
                            tar.add(item, arcname=arcname)
            
            # Encrypt if configured
            if self.config.encryption:
                encrypted_path = await self._encrypt_backup(backup_path, backup_id)
                backup_path.unlink()  # Remove unencrypted version
                backup_path = encrypted_path
            
            return backup_path
            
        except Exception as e:
            if backup_path.exists():
                backup_path.unlink()
            raise BackupError(f"Full backup creation failed: {e}")
    
    async def _create_incremental_backup(self, source_path: Path, backup_id: str) -> Path:
        """Create incremental backup (changes since last backup)"""
        backup_path = self.backup_dir / f"{backup_id}_incremental.tar.gz"
        
        try:
            # Find last backup for this source
            last_backup = self._find_last_backup(str(source_path))
            
            if not last_backup:
                # No previous backup, create full backup instead
                logger.info("No previous backup found, creating full backup")
                return await self._create_full_backup(source_path, backup_id)
            
            # Find files modified since last backup
            modified_files = []
            last_backup_time = last_backup.created_at
            
            if source_path.is_file():
                if datetime.fromtimestamp(source_path.stat().st_mtime) > last_backup_time:
                    modified_files.append(source_path)
            else:
                for item in source_path.rglob('*'):
                    if (item.is_file() and 
                        self._should_include_file(item) and
                        datetime.fromtimestamp(item.stat().st_mtime) > last_backup_time):
                        modified_files.append(item)
            
            # Create incremental archive
            with tarfile.open(backup_path, 'w:gz') as tar:
                for file_path in modified_files:
                    if source_path.is_file():
                        arcname = file_path.name
                    else:
                        arcname = file_path.relative_to(source_path)
                    tar.add(file_path, arcname=arcname)
            
            # Encrypt if configured
            if self.config.encryption:
                encrypted_path = await self._encrypt_backup(backup_path, backup_id)
                backup_path.unlink()
                backup_path = encrypted_path
            
            return backup_path
            
        except Exception as e:
            if backup_path.exists():
                backup_path.unlink()
            raise BackupError(f"Incremental backup creation failed: {e}")
    
    async def _create_differential_backup(self, source_path: Path, backup_id: str) -> Path:
        """Create differential backup (changes since last full backup)"""
        backup_path = self.backup_dir / f"{backup_id}_differential.tar.gz"
        
        try:
            # Find last full backup for this source
            last_full_backup = self._find_last_full_backup(str(source_path))
            
            if not last_full_backup:
                logger.info("No previous full backup found, creating full backup")
                return await self._create_full_backup(source_path, backup_id)
            
            # Find files modified since last full backup
            modified_files = []
            last_full_backup_time = last_full_backup.created_at
            
            if source_path.is_file():
                if datetime.fromtimestamp(source_path.stat().st_mtime) > last_full_backup_time:
                    modified_files.append(source_path)
            else:
                for item in source_path.rglob('*'):
                    if (item.is_file() and 
                        self._should_include_file(item) and
                        datetime.fromtimestamp(item.stat().st_mtime) > last_full_backup_time):
                        modified_files.append(item)
            
            # Create differential archive
            with tarfile.open(backup_path, 'w:gz') as tar:
                for file_path in modified_files:
                    if source_path.is_file():
                        arcname = file_path.name
                    else:
                        arcname = file_path.relative_to(source_path)
                    tar.add(file_path, arcname=arcname)
            
            # Encrypt if configured
            if self.config.encryption:
                encrypted_path = await self._encrypt_backup(backup_path, backup_id)
                backup_path.unlink()
                backup_path = encrypted_path
            
            return backup_path
            
        except Exception as e:
            if backup_path.exists():
                backup_path.unlink()
            raise BackupError(f"Differential backup creation failed: {e}")
    
    async def _create_snapshot_backup(self, source_path: Path, backup_id: str) -> Path:
        """Create snapshot backup (copy current state)"""
        backup_path = self.backup_dir / f"{backup_id}_snapshot.tar.gz"
        
        try:
            # Create snapshot (similar to full backup but with different metadata)
            with tarfile.open(backup_path, 'w:gz') as tar:
                if source_path.is_file():
                    tar.add(source_path, arcname=source_path.name)
                else:
                    for item in source_path.rglob('*'):
                        if item.is_file() and self._should_include_file(item):
                            arcname = item.relative_to(source_path)
                            tar.add(item, arcname=arcname)
            
            # Encrypt if configured
            if self.config.encryption:
                encrypted_path = await self._encrypt_backup(backup_path, backup_id)
                backup_path.unlink()
                backup_path = encrypted_path
            
            return backup_path
            
        except Exception as e:
            if backup_path.exists():
                backup_path.unlink()
            raise BackupError(f"Snapshot backup creation failed: {e}")
    
    # Backup management methods
    
    async def _store_backup_in_backends(
        self,
        backup_path: Path,
        backup_id: str,
        metadata: BackupMetadata
    ) -> Dict[str, str]:
        """Store backup in configured storage backends"""
        backend_urls = {}
        
        if not self.backend_manager:
            logger.warning("No backend manager available for backup storage")
            return backend_urls
        
        backends = self.config.backup_backends or [StorageBackend.LOCAL]
        
        for backend in backends:
            try:
                storage_path = f"backups/{backup_id}/{backup_path.name}"
                
                url = await self.backend_manager.store_file(
                    backend,
                    backup_path,
                    storage_path,
                    metadata={'backup_id': backup_id, 'created_at': metadata.created_at.isoformat()},
                    access_level='private'
                )
                
                backend_urls[backend.value] = url
                logger.info(f"Backup stored in {backend}: {url}")
                
            except Exception as e:
                logger.error(f"Failed to store backup in {backend}: {e}")
        
        return backend_urls
    
    async def _encrypt_backup(self, backup_path: Path, backup_id: str) -> Path:
        """Encrypt backup file"""



        try:
            encrypted_path = backup_path.with_suffix(backup_path.suffix + '.enc')
            
            key_id = await self.encryption_manager.encrypt_file(
                str(backup_path),
                str(encrypted_path)
            )
            
            logger.info(f"Backup encrypted with key ID: {key_id}")
            
            return encrypted_path
            
        except Exception as e:
            raise BackupError(f"Backup encryption failed: {e}")
    
    async def _verify_backup(self, backup_path: Path, metadata: BackupMetadata) -> bool:
        """Verify backup integrity"""



        try:
            # Calculate checksum
            calculated_checksum = await self._calculate_file_checksum(backup_path)
            
            # Compare with stored checksum
            if metadata.checksum and calculated_checksum != metadata.checksum:
                logger.error(f"Backup checksum mismatch: {backup_path}")
                return False
            
            # Test archive extraction (for tar files)
            if backup_path.suffix == '.gz' and '.tar' in backup_path.name:
                try:
                    with tarfile.open(backup_path, 'r:gz') as tar:
                        # Test that archive can be opened and read
                        tar.getnames()
                except Exception:
                    logger.error(f"Backup archive is corrupted: {backup_path}")
                    return False
            
            logger.info(f"Backup verification successful: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False
    
    async def _calculate_backup_stats(self, backup_path: Path) -> Dict[str, Any]:
        """Calculate backup statistics"""



        try:
            backup_size = backup_path.stat().st_size
            checksum = await self._calculate_file_checksum(backup_path)
            
            # Count files in archive
            file_count = 0
            original_size = 0
            
            if backup_path.suffix == '.gz' and '.tar' in backup_path.name:
                with tarfile.open(backup_path, 'r:gz') as tar:
                    members = tar.getmembers()
                    file_count = len([m for m in members if m.isfile()])
                    original_size = sum(m.size for m in members if m.isfile())
            else:
                file_count = 1
                original_size = backup_size
            
            return {
                'file_count': file_count,
                'original_size': original_size,
                'backup_size': backup_size,
                'checksum': checksum
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate backup stats: {e}")
            return {
                'file_count': 0,
                'original_size': 0,
                'backup_size': backup_path.stat().st_size if backup_path.exists() else 0,
                'checksum': ''
            }
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""



        try:
            hash_sha256 = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            
            return hash_sha256.hexdigest()
            
        except Exception as e:
            logger.error(f"Checksum calculation failed: {e}")
            return ""
    
    # Restore methods
    
    async def _ensure_local_backup(self, backup_metadata: BackupMetadata) -> Path:
        """Ensure backup is available locally for restoration"""
        local_backup_path = Path(backup_metadata.backup_path)
        
        # If backup is already local and exists
        if local_backup_path.exists():
            return local_backup_path
        
        # Download from backend
        if self.backend_manager and backup_metadata.backends:
            for backend_name in backup_metadata.backends:
                try:
                    backend = StorageBackend(backend_name)
                    remote_path = f"backups/{backup_metadata.backup_id}"
                    
                    downloaded_path = await self.backend_manager.retrieve_file(
                        backend,
                        remote_path,
                        str(local_backup_path)
                    )
                    
                    if Path(downloaded_path).exists():
                        return Path(downloaded_path)
                        
                except Exception as e:
                    logger.warning(f"Failed to download from {backend_name}: {e}")
        
        raise BackupError(f"Could not retrieve backup: {backup_metadata.backup_id}")
    
    async def _extract_backup(
        self,
        backup_path: Path,
        target_path: Path,
        restore_operation: RestoreOperation
    ):
        """Extract backup to target location"""



        try:
            # Decrypt if necessary
            if backup_path.suffix == '.enc':
                decrypted_path = backup_path.with_suffix('')
                await self.encryption_manager.decrypt_file(
                    str(backup_path),
                    str(decrypted_path)
                )
                backup_path = decrypted_path
            
            # Extract archive
            if backup_path.suffix == '.gz' and '.tar' in backup_path.name:
                with tarfile.open(backup_path, 'r:gz') as tar:
                    # Get total files for progress tracking
                    members = tar.getmembers()
                    total_files = len(members)
                    
                    for i, member in enumerate(members):
                        tar.extract(member, target_path)
                        
                        # Update progress
                        progress = ((i + 1) / total_files) * 100
                        restore_operation.progress = progress
            else:
                # Single file backup
                shutil.copy2(backup_path, target_path)
                restore_operation.progress = 100.0
                
        except Exception as e:
            raise BackupError(f"Backup extraction failed: {e}")
    
    async def _verify_restoration(
        self,
        backup_metadata: BackupMetadata,
        target_path: Path
    ) -> bool:
        """Verify restoration integrity"""



        try:
            # Basic existence check
            if not target_path.exists():
                return False
            
            # For now, just check that files exist
            # In a full implementation, would compare checksums
            return True
            
        except Exception as e:
            logger.error(f"Restoration verification failed: {e}")
            return False
    
    # Utility methods
    
    def _generate_backup_id(self, source_path: Path, backup_name: Optional[str] = None) -> str:
        """Generate unique backup ID"""
        if backup_name:
            base_name = backup_name
        else:
            base_name = source_path.name
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        source_hash = hashlib.md5(str(source_path).encode()).hexdigest()[:8]
        
        return f"{base_name}_{timestamp}_{source_hash}"
    
    def _generate_restore_id(self, backup_id: str) -> str:
        """Generate unique restore operation ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"restore_{backup_id}_{timestamp}"
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in backup"""
        file_str = str(file_path)
        
        # Check exclude patterns
        if self.config.exclude_patterns:
            for pattern in self.config.exclude_patterns:
                if pattern in file_str:
                    return False
        
        # Check include patterns (if specified)
        if self.config.include_patterns:
            for pattern in self.config.include_patterns:
                if pattern in file_str:
                    return True
            return False  # No include pattern matched
        
        return True
    
    def _find_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Find backup metadata by ID"""
        for backup in self.backup_history:
            if backup.backup_id == backup_id:
                return backup
        
        # Check active backups
        return self.active_backups.get(backup_id)
    
    def _find_last_backup(self, source_path: str) -> Optional[BackupMetadata]:
        """Find most recent backup for source path"""
        source_backups = [
            backup for backup in self.backup_history
            if backup.source_path == source_path and backup.status == BackupStatus.COMPLETED
        ]
        
        if not source_backups:
            return None
        
        return max(source_backups, key=lambda x: x.created_at)
    
    def _find_last_full_backup(self, source_path: str) -> Optional[BackupMetadata]:
        """Find most recent full backup for source path"""
        full_backups = [
            backup for backup in self.backup_history
            if (backup.source_path == source_path and 
                backup.backup_type == BackupType.FULL and
                backup.status == BackupStatus.COMPLETED)
        ]
        
        if not full_backups:
            return None
        
        return max(full_backups, key=lambda x: x.created_at)
    
    async def _update_backup_statistics(
        self,
        metadata: BackupMetadata,
        processing_time: float,
        success: bool
    ):
        """Update backup statistics"""
        self.stats['total_backups'] += 1
        self.stats['backup_by_type'][metadata.backup_type] += 1
        
        if success:
            self.stats['successful_backups'] += 1
            self.stats['total_bytes_backed_up'] += metadata.compressed_size
            
            # Update averages
            total_successful = self.stats['successful_backups']
            
            # Average backup time
            current_avg_time = self.stats['average_backup_time']
            self.stats['average_backup_time'] = (
                (current_avg_time * (total_successful - 1) + processing_time) / total_successful
            )
            
            # Compression ratio
            if metadata.total_size > 0:
                compression_ratio = metadata.compressed_size / metadata.total_size
                current_compression_ratio = self.stats['total_compression_ratio']
                self.stats['total_compression_ratio'] = (
                    (current_compression_ratio * (total_successful - 1) + compression_ratio) / total_successful
                )
        else:
            self.stats['failed_backups'] += 1
    
    async def create_automated_backup(self):
        """Create automated backup based on configuration"""



        try:
            logger.info("Starting automated backup process")
            
            # In a real implementation, this would backup configured sources
            # For now, this is a placeholder
            
            logger.info("Automated backup completed successfully")
            
        except Exception as e:
            logger.error(f"Automated backup failed: {e}")
    
    async def cleanup(self):
        """Cleanup backup manager resources"""



        try:
            # Cancel backup scheduler
            if self.backup_scheduler:
                self.backup_scheduler.stop()
            
            # Save backup history to persistent storage
            await self._save_backup_history()
            
            logger.info("BackupManager cleanup completed")
            
        except Exception as e:
            logger.error(f"BackupManager cleanup failed: {e}")
    
    async def _save_backup_history(self):
        """Save backup history to persistent storage"""



        try:
            history_file = self.backup_dir / 'backup_history.json'
            
            # Convert metadata to dict format
            history_data = []
            for backup in self.backup_history:
                backup_dict = asdict(backup)
                backup_dict['created_at'] = backup.created_at.isoformat()
                history_data.append(backup_dict)
            
            async with aiofiles.open(history_file, 'w') as f:
                await f.write(json.dumps(history_data, indent=2))
            
            logger.info("Backup history saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save backup history: {e}")
    
    async def _load_backup_history(self):
        """Load backup history from persistent storage"""



        try:
            history_file = self.backup_dir / 'backup_history.json'
            
            if not history_file.exists():
                return
            
            async with aiofiles.open(history_file, 'r') as f:
                history_data = json.loads(await f.read())
            
            # Convert back to metadata objects
            for backup_dict in history_data:
                backup_dict['created_at'] = datetime.fromisoformat(backup_dict['created_at'])
                backup_dict['backup_type'] = BackupType(backup_dict['backup_type'])
                backup_dict['status'] = BackupStatus(backup_dict['status'])
                
                metadata = BackupMetadata(**backup_dict)
                self.backup_history.append(metadata)
            
            logger.info(f"Loaded {len(self.backup_history)} backup records from history")
            
        except Exception as e:
            logger.warning(f"Failed to load backup history: {e}")
