"""
Enterprise Backup Manager for IA Influencer Agent Platform.

Orchestrates all backup operations including content protection,
user data, and system configurations with enterprise-grade features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .content_backup import ContentBackupService
from .user_backup import UserDataBackupService
from .system_backup import SystemConfigBackupService
from .backup_scheduler import BackupScheduler
from .backup_monitor import BackupMonitor
from .recovery_manager import RecoveryManager
from .backup_encryption import BackupEncryption
from .backup_validator import BackupValidator
from .backup_storage import BackupStorage


class BackupType(Enum):
    """Backup type enumeration."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Backup status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackupMetadata:
    """Backup metadata container."""
    backup_id: str
    backup_type: BackupType
    created_at: datetime
    completed_at: Optional[datetime]
    size_bytes: int
    file_count: int
    checksum: str
    encryption_enabled: bool
    compression_ratio: float
    storage_location: str
    tags: List[str]


class BackupManager:
    """
    Enterprise backup manager orchestrating all backup operations.
    
    Manages content protection backups, user data backups, system configs,
    with scheduling, monitoring, encryption, and recovery capabilities.
    """

    def __init__(
        self,
        storage_config: Dict[str, Any],
        encryption_key: Optional[str] = None,
        compression_level: int = 6,
        max_concurrent_backups: int = 3
    ):
        """
        Initialize backup manager.
        
        Args:
            storage_config: Storage configuration
            encryption_key: Encryption key for backups
            compression_level: Compression level (0-9)
            max_concurrent_backups: Maximum concurrent backup operations
        """
        self.logger = logging.getLogger(__name__)
        self.storage_config = storage_config
        self.compression_level = compression_level
        self.max_concurrent_backups = max_concurrent_backups
        
        # Initialize backup services
        self.content_backup = ContentBackupService(storage_config)
        self.user_backup = UserDataBackupService(storage_config)
        self.system_backup = SystemConfigBackupService(storage_config)
        
        # Initialize supporting services
        self.scheduler = BackupScheduler()
        self.monitor = BackupMonitor()
        self.recovery_manager = RecoveryManager(storage_config)
        self.encryption = BackupEncryption(encryption_key)
        self.validator = BackupValidator()
        self.storage = BackupStorage(storage_config)
        
        # Active backup tracking
        self.active_backups: Dict[str, BackupMetadata] = {}
        self.backup_history: List[BackupMetadata] = []
        self._backup_lock = asyncio.Semaphore(max_concurrent_backups)

    async def create_full_backup(
        self,
        include_content: bool = True,
        include_user_data: bool = True,
        include_system_config: bool = True,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create comprehensive full backup.
        
        Args:
            include_content: Include content protection data
            include_user_data: Include user data
            include_system_config: Include system configurations
            tags: Backup tags for organization
            
        Returns:
            Backup ID
        """
        backup_id = f"full_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        async with self._backup_lock:
            try:
                self.logger.info(f"Starting full backup: {backup_id}")
                
                backup_metadata = BackupMetadata(
                    backup_id=backup_id,
                    backup_type=BackupType.FULL,
                    created_at=datetime.now(),
                    completed_at=None,
                    size_bytes=0,
                    file_count=0,
                    checksum="",
                    encryption_enabled=self.encryption.is_enabled(),
                    compression_ratio=0.0,
                    storage_location="",
                    tags=tags or []
                )
                
                self.active_backups[backup_id] = backup_metadata
                
                # Collect all backup data
                backup_data = {}
                
                if include_content:
                    self.logger.info("Backing up content protection data...")
                    backup_data['content'] = await self.content_backup.backup_all_content()
                
                if include_user_data:
                    self.logger.info("Backing up user data...")
                    backup_data['users'] = await self.user_backup.backup_all_users()
                
                if include_system_config:
                    self.logger.info("Backing up system configuration...")
                    backup_data['system'] = await self.system_backup.backup_configurations()
                
                # Process and store backup
                processed_backup = await self._process_backup_data(
                    backup_id, backup_data
                )
                
                # Store backup
                storage_location = await self.storage.store_backup(
                    backup_id, processed_backup
                )
                
                # Update metadata
                backup_metadata.completed_at = datetime.now()
                backup_metadata.size_bytes = len(processed_backup)
                backup_metadata.storage_location = storage_location
                backup_metadata.checksum = await self.validator.calculate_checksum(
                    processed_backup
                )
                
                # Move to history
                del self.active_backups[backup_id]
                self.backup_history.append(backup_metadata)
                
                self.logger.info(f"Full backup completed: {backup_id}")
                return backup_id
                
            except Exception as e:
                self.logger.error(f"Full backup failed: {backup_id} - {e}")
                if backup_id in self.active_backups:
                    del self.active_backups[backup_id]
                raise

    async def create_incremental_backup(
        self,
        base_backup_id: str,
        include_content: bool = True,
        include_user_data: bool = True,
        include_system_config: bool = True,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create incremental backup based on previous backup.
        
        Args:
            base_backup_id: Base backup for incremental changes
            include_content: Include content changes
            include_user_data: Include user data changes
            include_system_config: Include system config changes
            tags: Backup tags
            
        Returns:
            Backup ID
        """
        backup_id = f"inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        async with self._backup_lock:
            try:
                self.logger.info(f"Starting incremental backup: {backup_id}")
                
                # Get base backup metadata
                base_metadata = await self._get_backup_metadata(base_backup_id)
                if not base_metadata:
                    raise ValueError(f"Base backup not found: {base_backup_id}")
                
                backup_metadata = BackupMetadata(
                    backup_id=backup_id,
                    backup_type=BackupType.INCREMENTAL,
                    created_at=datetime.now(),
                    completed_at=None,
                    size_bytes=0,
                    file_count=0,
                    checksum="",
                    encryption_enabled=self.encryption.is_enabled(),
                    compression_ratio=0.0,
                    storage_location="",
                    tags=(tags or []) + [f"base:{base_backup_id}"]
                )
                
                self.active_backups[backup_id] = backup_metadata
                
                # Collect incremental changes
                changes_since = base_metadata.created_at
                backup_data = {}
                
                if include_content:
                    backup_data['content'] = await self.content_backup.backup_changes_since(
                        changes_since
                    )
                
                if include_user_data:
                    backup_data['users'] = await self.user_backup.backup_changes_since(
                        changes_since
                    )
                
                if include_system_config:
                    backup_data['system'] = await self.system_backup.backup_changes_since(
                        changes_since
                    )
                
                # Process and store backup
                processed_backup = await self._process_backup_data(
                    backup_id, backup_data
                )
                
                storage_location = await self.storage.store_backup(
                    backup_id, processed_backup
                )
                
                # Update metadata
                backup_metadata.completed_at = datetime.now()
                backup_metadata.size_bytes = len(processed_backup)
                backup_metadata.storage_location = storage_location
                backup_metadata.checksum = await self.validator.calculate_checksum(
                    processed_backup
                )
                
                del self.active_backups[backup_id]
                self.backup_history.append(backup_metadata)
                
                self.logger.info(f"Incremental backup completed: {backup_id}")
                return backup_id
                
            except Exception as e:
                self.logger.error(f"Incremental backup failed: {backup_id} - {e}")
                if backup_id in self.active_backups:
                    del self.active_backups[backup_id]
                raise

    async def restore_backup(
        self,
        backup_id: str,
        restore_content: bool = True,
        restore_user_data: bool = True,
        restore_system_config: bool = True,
        target_path: Optional[str] = None
    ) -> bool:
        """
        Restore backup by ID.
        
        Args:
            backup_id: Backup to restore
            restore_content: Restore content data
            restore_user_data: Restore user data
            restore_system_config: Restore system config
            target_path: Custom restore path
            
        Returns:
            Success status
        """
        try:
            self.logger.info(f"Starting backup restoration: {backup_id}")
            
            # Retrieve backup data
            backup_data = await self.storage.retrieve_backup(backup_id)
            if not backup_data:
                raise ValueError(f"Backup not found: {backup_id}")
            
            # Decrypt and decompress if needed
            processed_data = await self._process_restore_data(backup_id, backup_data)
            
            # Restore components
            if restore_content and 'content' in processed_data:
                await self.content_backup.restore_content(
                    processed_data['content'], target_path
                )
            
            if restore_user_data and 'users' in processed_data:
                await self.user_backup.restore_users(
                    processed_data['users'], target_path
                )
            
            if restore_system_config and 'system' in processed_data:
                await self.system_backup.restore_configurations(
                    processed_data['system'], target_path
                )
            
            self.logger.info(f"Backup restoration completed: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup restoration failed: {backup_id} - {e}")
            return False

    async def schedule_automatic_backup(
        self,
        schedule_config: Dict[str, Any]
    ) -> str:
        """
        Schedule automatic backup.
        
        Args:
            schedule_config: Scheduling configuration
            
        Returns:
            Schedule ID
        """
        return await self.scheduler.add_schedule(schedule_config, self.create_full_backup)

    async def get_backup_status(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Get backup status and metadata.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Backup status information
        """
        # Check active backups
        if backup_id in self.active_backups:
            metadata = self.active_backups[backup_id]
            return {
                "status": BackupStatus.RUNNING.value,
                "metadata": metadata,
                "progress": await self.monitor.get_backup_progress(backup_id)
            }
        
        # Check completed backups
        for metadata in self.backup_history:
            if metadata.backup_id == backup_id:
                return {
                    "status": BackupStatus.COMPLETED.value,
                    "metadata": metadata
                }
        
        return None

    async def list_backups(
        self,
        backup_type: Optional[BackupType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[BackupMetadata]:
        """
        List available backups with filtering.
        
        Args:
            backup_type: Filter by backup type
            tags: Filter by tags
            limit: Maximum results
            
        Returns:
            List of backup metadata
        """
        backups = self.backup_history.copy()
        
        if backup_type:
            backups = [b for b in backups if b.backup_type == backup_type]
        
        if tags:
            backups = [
                b for b in backups 
                if any(tag in b.tags for tag in tags)
            ]
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.created_at, reverse=True)
        
        return backups[:limit]

    async def delete_backup(self, backup_id: str) -> bool:
        """
        Delete backup and cleanup storage.
        
        Args:
            backup_id: Backup to delete
            
        Returns:
            Success status
        """
        try:
            # Remove from storage
            await self.storage.delete_backup(backup_id)
            
            # Remove from history
            self.backup_history = [
                b for b in self.backup_history 
                if b.backup_id != backup_id
            ]
            
            self.logger.info(f"Backup deleted: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete backup: {backup_id} - {e}")
            return False

    async def verify_backup_integrity(self, backup_id: str) -> bool:
        """
        Verify backup integrity and consistency.
        
        Args:
            backup_id: Backup to verify
            
        Returns:
            Integrity status
        """
        return await self.validator.verify_backup(backup_id)

    async def cleanup_old_backups(
        self,
        retention_days: int = 30,
        keep_weekly: int = 4,
        keep_monthly: int = 12
    ) -> int:
        """
        Cleanup old backups based on retention policy.
        
        Args:
            retention_days: Days to keep daily backups
            keep_weekly: Number of weekly backups to keep
            keep_monthly: Number of monthly backups to keep
            
        Returns:
            Number of deleted backups
        """
        deleted_count = 0
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Group backups by time periods
        daily_backups = []
        weekly_backups = []
        monthly_backups = []
        
        for backup in self.backup_history:
            if backup.created_at > cutoff_date:
                daily_backups.append(backup)
            elif backup.created_at > cutoff_date - timedelta(weeks=keep_weekly):
                weekly_backups.append(backup)
            elif backup.created_at > cutoff_date - timedelta(days=30 * keep_monthly):
                monthly_backups.append(backup)
            else:
                # Delete very old backups
                if await self.delete_backup(backup.backup_id):
                    deleted_count += 1
        
        # Keep only specified number of weekly/monthly backups
        if len(weekly_backups) > keep_weekly:
            for backup in weekly_backups[keep_weekly:]:
                if await self.delete_backup(backup.backup_id):
                    deleted_count += 1
        
        if len(monthly_backups) > keep_monthly:
            for backup in monthly_backups[keep_monthly:]:
                if await self.delete_backup(backup.backup_id):
                    deleted_count += 1
        
        self.logger.info(f"Cleanup completed: {deleted_count} backups deleted")
        return deleted_count

    async def _process_backup_data(
        self, 
        backup_id: str, 
        backup_data: Dict[str, Any]
    ) -> bytes:
        """Process backup data with compression and encryption."""
        # Serialize data
        import json
        import gzip
        
        serialized = json.dumps(backup_data, default=str).encode()
        
        # Compress
        compressed = gzip.compress(serialized, compresslevel=self.compression_level)
        
        # Encrypt if enabled
        if self.encryption.is_enabled():
            encrypted = await self.encryption.encrypt_data(compressed)
            return encrypted
        
        return compressed

    async def _process_restore_data(
        self, 
        backup_id: str, 
        backup_data: bytes
    ) -> Dict[str, Any]:
        """Process restore data with decryption and decompression."""
        import json
        import gzip
        
        # Decrypt if needed
        if self.encryption.is_enabled():
            decrypted = await self.encryption.decrypt_data(backup_data)
            backup_data = decrypted
        
        # Decompress
        decompressed = gzip.decompress(backup_data)
        
        # Deserialize
        data = json.loads(decompressed.decode())
        return data

    async def _get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get backup metadata by ID."""
        for metadata in self.backup_history:
            if metadata.backup_id == backup_id:
                return metadata
        return None

    async def get_backup_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive backup statistics.
        
        Returns:
            Backup statistics
        """
        total_backups = len(self.backup_history)
        total_size = sum(b.size_bytes for b in self.backup_history)
        
        backup_types = {}
        for backup in self.backup_history:
            backup_type = backup.backup_type.value
            if backup_type not in backup_types:
                backup_types[backup_type] = {"count": 0, "size": 0}
            backup_types[backup_type]["count"] += 1
            backup_types[backup_type]["size"] += backup.size_bytes
        
        recent_backups = [
            b for b in self.backup_history 
            if b.created_at > datetime.now() - timedelta(days=7)
        ]
        
        return {
            "total_backups": total_backups,
            "total_size_bytes": total_size,
            "total_size_gb": round(total_size / (1024**3), 2),
            "backup_types": backup_types,
            "recent_backups_count": len(recent_backups),
            "active_backups_count": len(self.active_backups),
            "average_backup_size": total_size // total_backups if total_backups > 0 else 0,
            "oldest_backup": min(self.backup_history, key=lambda x: x.created_at).created_at if self.backup_history else None,
            "newest_backup": max(self.backup_history, key=lambda x: x.created_at).created_at if self.backup_history else None
        }
