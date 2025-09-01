#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cache Persistence - Persistent Storage and Backup Management
===========================================================

Advanced persistence layer for cache data with backup, recovery,
and distributed storage capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import pickle
import json
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import tempfile

from ...core.config import get_settings
from ...core.utils import generate_uuid, get_timestamp

logger = logging.getLogger(__name__)

class StorageFormat(Enum):
    """
Persistent storage formats."""

    PICKLE = "pickle"
    JSON = "json"
    COMPRESSED_PICKLE = "compressed_pickle"
    COMPRESSED_JSON = "compressed_json"

class BackupStrategy(Enum):
    """Backup strategies."""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

@dataclass
class PersistentEntry:
    """Persistent cache entry."""
    key: str
    value: Any
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    
    def calculate_checksum(self) -> str:
        """
Calculate entry checksum."""
        data = json.dumps({
            'key': self.key,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_checksum(self) -> bool:
        """
Verify entry integrity."""
        if not self.checksum:
            return True
        return self.checksum == self.calculate_checksum()

@dataclass
class BackupInfo:
    """
Backup information."""
    backup_id: str
    strategy: BackupStrategy
    format: StorageFormat
    created_at: datetime
    file_path: str
    size_bytes: int
    entry_count: int
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class CachePersistence:
    """
    Advanced cache persistence system.
    
    Features:
    - Multiple storage formats
    - Compression support
    - Integrity checking
    - Incremental backups
    - Recovery mechanisms
    """
    
    def __init__(self, storage_path: str, 
                 format: StorageFormat = StorageFormat.COMPRESSED_PICKLE,
                 auto_backup_interval: int = 3600):
        """
        Initialize cache persistence.
        
        Args:
            storage_path: Base storage directory
            format: Default storage format
            auto_backup_interval: Auto backup interval in seconds
        """
        self.storage_path = Path(storage_path)
        self.format = format
        self.auto_backup_interval = auto_backup_interval
        self.logger = logging.getLogger(f"{__name__}.CachePersistence")
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Backup management
        self.backup_info: Dict[str, BackupInfo] = {}
        self.last_backup_time: Optional[datetime] = None
        self.auto_backup_task: Optional[asyncio.Task] = None
        
        # File paths
        self.data_dir = self.storage_path / "data"
        self.backup_dir = self.storage_path / "backups"
        self.index_file = self.storage_path / "index.json"
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load existing index
        self.index: Dict[str, Dict[str, Any]] = self._load_index()
        
        self.logger.info(f"Cache persistence initialized at {storage_path}")
    
    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load persistence index."""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading index: {e}")
        return {}
    
    def _save_index(self) -> None:
        """Save persistence index."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving index: {e}")
    
    def _get_entry_path(self, key: str) -> Path:
        """Get file path for cache entry."""
        # Create hash-based directory structure
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        dir_name = key_hash[:2]
        file_name = f"{key_hash[2:]}.dat"
        
        entry_dir = self.data_dir / dir_name
        entry_dir.mkdir(exist_ok=True)
        
        return entry_dir / file_name
    
    def _serialize_entry(self, entry: PersistentEntry, 
                        format: StorageFormat) -> bytes:
        """Serialize entry to bytes."""
        data = {
            'key': entry.key,
            'value': entry.value,
            'timestamp': entry.timestamp.isoformat(),
            'metadata': entry.metadata,
            'checksum': entry.checksum
        }
        
        if format in [StorageFormat.PICKLE, StorageFormat.COMPRESSED_PICKLE]:
            serialized = pickle.dumps(data)
        else:  # JSON formats
            serialized = json.dumps(data, default=str).encode('utf-8')
        
        if format in [StorageFormat.COMPRESSED_PICKLE, StorageFormat.COMPRESSED_JSON]:
            serialized = gzip.compress(serialized)
        
        return serialized
    
    def _deserialize_entry(self, data: bytes, 
                          format: StorageFormat) -> PersistentEntry:
        """
Deserialize entry from bytes."""
        if format in [StorageFormat.COMPRESSED_PICKLE, StorageFormat.COMPRESSED_JSON]:
            data = gzip.decompress(data)
        
        if format in [StorageFormat.PICKLE, StorageFormat.COMPRESSED_PICKLE]:
            entry_data = pickle.loads(data)
        else:  # JSON formats
            entry_data = json.loads(data.decode('utf-8'))
        
        return PersistentEntry(
            key=entry_data['key'],
            value=entry_data['value'],
            timestamp=datetime.fromisoformat(entry_data['timestamp']),
            metadata=entry_data.get('metadata', {}),
            checksum=entry_data.get('checksum')
        )
    
    async def store_entry(self, key: str, value: Any, 
                         metadata: Optional[Dict[str, Any]] = None,
                         format: Optional[StorageFormat] = None) -> bool:
        """
        Store cache entry persistently.
        
        Args:
            key: Cache key
            value: Value to store
            metadata: Entry metadata
            format: Storage format override
            
        Returns:
            True if successful
        """
        try:
            entry = PersistentEntry(
                key=key,
                value=value,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            # Calculate checksum
            entry.checksum = entry.calculate_checksum()
            
            # Serialize entry
            storage_format = format or self.format
            serialized_data = self._serialize_entry(entry, storage_format)
            
            # Write to file
            entry_path = self._get_entry_path(key)
            with open(entry_path, 'wb') as f:
                f.write(serialized_data)
            
            # Update index
            self.index[key] = {
                'path': str(entry_path),
                'format': storage_format.value,
                'timestamp': entry.timestamp.isoformat(),
                'size': len(serialized_data),
                'checksum': entry.checksum
            }
            
            self._save_index()
            
            self.logger.debug(f"Stored entry {key} persistently")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing entry {key}: {e}")
            return False
    
    async def load_entry(self, key: str) -> Optional[PersistentEntry]:
        """
        Load cache entry from storage.
        
        Args:
            key: Cache key
            
        Returns:
            Persistent entry or None if not found
        """
        try:
            if key not in self.index:
                return None
            
            entry_info = self.index[key]
            entry_path = Path(entry_info['path'])
            
            if not entry_path.exists():
                # Clean up stale index entry
                del self.index[key]
                self._save_index()
                return None
            
            # Read and deserialize
            with open(entry_path, 'rb') as f:
                data = f.read()
            
            storage_format = StorageFormat(entry_info['format'])
            entry = self._deserialize_entry(data, storage_format)
            
            # Verify integrity
            if not entry.verify_checksum():
                self.logger.warning(f"Checksum mismatch for entry {key}")
                return None
            
            return entry
            
        except Exception as e:
            self.logger.error(f"Error loading entry {key}: {e}")
            return None
    
    async def delete_entry(self, key: str) -> bool:
        """Delete persistent entry."""
        try:
            if key not in self.index:
                return False
            
            entry_info = self.index[key]
            entry_path = Path(entry_info['path'])
            
            # Delete file
            if entry_path.exists():
                entry_path.unlink()
            
            # Remove from index
            del self.index[key]
            self._save_index()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting entry {key}: {e}")
            return False
    
    async def list_entries(self, pattern: Optional[str] = None) -> List[str]:
        """List all persistent entries."""
        try:
            keys = list(self.index.keys())
            
            if pattern:
                import fnmatch
                keys = [key for key in keys if fnmatch.fnmatch(key, pattern)]
            
            return keys
            
        except Exception as e:
            self.logger.error(f"Error listing entries: {e}")
            return []
    
    async def create_backup(self, strategy: BackupStrategy = BackupStrategy.FULL,
                          format: Optional[StorageFormat] = None) -> Optional[str]:
        """
        Create cache backup.
        
        Args:
            strategy: Backup strategy
            format: Storage format override
            
        Returns:
            Backup ID if successful
        """
        try:
            backup_id = generate_uuid()
            backup_format = format or self.format
            timestamp = datetime.now()
            
            # Create backup file
            backup_filename = f"backup_{backup_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.dat"
            backup_path = self.backup_dir / backup_filename
            
            # Collect entries based on strategy
            if strategy == BackupStrategy.FULL:
                entries_to_backup = list(self.index.keys())
            elif strategy == BackupStrategy.INCREMENTAL:
                # Only entries modified since last backup
                entries_to_backup = self._get_incremental_entries()
            else:
                # For now, treat other strategies as full backup
                entries_to_backup = list(self.index.keys())
            
            # Create backup data
            backup_data = {
                'backup_id': backup_id,
                'strategy': strategy.value,
                'format': backup_format.value,
                'created_at': timestamp.isoformat(),
                'entries': {}
            }
            
            entry_count = 0
            for key in entries_to_backup:
                entry = await self.load_entry(key)
                if entry:
                    backup_data['entries'][key] = {
                        'value': entry.value,
                        'timestamp': entry.timestamp.isoformat(),
                        'metadata': entry.metadata,
                        'checksum': entry.checksum
                    }
                    entry_count += 1
            
            # Serialize and write backup
            if backup_format in [StorageFormat.PICKLE, StorageFormat.COMPRESSED_PICKLE]:
                serialized_backup = pickle.dumps(backup_data)
            else:
                serialized_backup = json.dumps(backup_data, default=str).encode('utf-8')
            
            if backup_format in [StorageFormat.COMPRESSED_PICKLE, StorageFormat.COMPRESSED_JSON]:
                serialized_backup = gzip.compress(serialized_backup)
            
            with open(backup_path, 'wb') as f:
                f.write(serialized_backup)
            
            # Calculate backup checksum
            backup_checksum = hashlib.sha256(serialized_backup).hexdigest()
            
            # Create backup info
            backup_info = BackupInfo(
                backup_id=backup_id,
                strategy=strategy,
                format=backup_format,
                created_at=timestamp,
                file_path=str(backup_path),
                size_bytes=len(serialized_backup),
                entry_count=entry_count,
                checksum=backup_checksum
            )
            
            self.backup_info[backup_id] = backup_info
            self.last_backup_time = timestamp
            
            self.logger.info(f"Created {strategy.value} backup {backup_id} with {entry_count} entries")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return None
    
    async def restore_backup(self, backup_id: str, 
                           overwrite: bool = False) -> bool:
        """
        Restore from backup.
        
        Args:
            backup_id: Backup ID to restore
            overwrite: Whether to overwrite existing entries
            
        Returns:
            True if successful
        """
        try:
            if backup_id not in self.backup_info:
                self.logger.error(f"Backup {backup_id} not found")
                return False
            
            backup_info = self.backup_info[backup_id]
            backup_path = Path(backup_info.file_path)
            
            if not backup_path.exists():
                self.logger.error(f"Backup file {backup_path} not found")
                return False
            
            # Read backup file
            with open(backup_path, 'rb') as f:
                backup_data_raw = f.read()
            
            # Verify backup integrity
            backup_checksum = hashlib.sha256(backup_data_raw).hexdigest()
            if backup_checksum != backup_info.checksum:
                self.logger.error(f"Backup {backup_id} checksum mismatch")
                return False
            
            # Decompress if needed
            if backup_info.format in [StorageFormat.COMPRESSED_PICKLE, StorageFormat.COMPRESSED_JSON]:
                backup_data_raw = gzip.decompress(backup_data_raw)
            
            # Deserialize backup
            if backup_info.format in [StorageFormat.PICKLE, StorageFormat.COMPRESSED_PICKLE]:
                backup_data = pickle.loads(backup_data_raw)
            else:
                backup_data = json.loads(backup_data_raw.decode('utf-8'))
            
            # Restore entries
            restored_count = 0
            for key, entry_data in backup_data['entries'].items():
                if not overwrite and key in self.index:
                    continue
                
                success = await self.store_entry(
                    key=key,
                    value=entry_data['value'],
                    metadata=entry_data['metadata']
                )
                
                if success:
                    restored_count += 1
            
            self.logger.info(f"Restored {restored_count} entries from backup {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring backup {backup_id}: {e}")
            return False
    
    def _get_incremental_entries(self) -> List[str]:
        """Get entries for incremental backup."""
        if not self.last_backup_time:
            return list(self.index.keys())
        
        incremental_entries = []
        for key, entry_info in self.index.items():
            entry_timestamp = datetime.fromisoformat(entry_info['timestamp'])
            if entry_timestamp > self.last_backup_time:
                incremental_entries.append(key)
        
        return incremental_entries
    
    async def start_auto_backup(self) -> None:
        """
Start automatic backup process."""
        if self.auto_backup_task is not None:
            return
        
        async def auto_backup_loop():
            while True:
                try:
                    await asyncio.sleep(self.auto_backup_interval)
                    await self.create_backup(BackupStrategy.INCREMENTAL)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Auto backup error: {e}")
        
        self.auto_backup_task = asyncio.create_task(auto_backup_loop())
        self.logger.info("Started automatic backup process")
    
    async def stop_auto_backup(self) -> None:
        """Stop automatic backup process."""
        if self.auto_backup_task:
            self.auto_backup_task.cancel()
            try:
                await self.auto_backup_task
            except asyncio.CancelledError:
                pass
            self.auto_backup_task = None
            self.logger.info("Stopped automatic backup process")
    
    async def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Clean up old backup files."""
        try:
            # Sort backups by creation time
            sorted_backups = sorted(
                self.backup_info.items(),
                key=lambda x: x[1].created_at,
                reverse=True
            )
            
            deleted_count = 0
            for backup_id, backup_info in sorted_backups[keep_count:]:
                backup_path = Path(backup_info.file_path)
                if backup_path.exists():
                    backup_path.unlink()
                    deleted_count += 1
                
                del self.backup_info[backup_id]
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up backups: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get persistence statistics."""
        try:
            total_entries = len(self.index)
            total_size = sum(info['size'] for info in self.index.values())
            
            # Calculate storage efficiency
            data_files = list(self.data_dir.rglob("*.dat"))
            actual_disk_usage = sum(f.stat().st_size for f in data_files if f.exists())
            
            return {
                "total_entries": total_entries,
                "total_size_bytes": total_size,
                "disk_usage_bytes": actual_disk_usage,
                "storage_efficiency": total_size / actual_disk_usage if actual_disk_usage > 0 else 0,
                "backup_count": len(self.backup_info),
                "last_backup": self.last_backup_time.isoformat() if self.last_backup_time else None,
                "auto_backup_enabled": self.auto_backup_task is not None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting persistence stats: {e}")
            return {}

class BackupManager:
    """
    Backup management system for cache persistence.
    
    Provides advanced backup scheduling and management capabilities.
    """
    
    def __init__(self, persistence: CachePersistence):
        """
Initialize backup manager."""
        self.persistence = persistence
        self.logger = logging.getLogger(f"{__name__}.BackupManager")
        
        # Backup schedules
        self.backup_schedules: Dict[str, Dict[str, Any]] = {}
        self.schedule_tasks: Dict[str, asyncio.Task] = {}
        
    async def add_schedule(self, schedule_id: str, 
                          strategy: BackupStrategy,
                          interval_seconds: int,
                          enabled: bool = True) -> bool:
        """Add backup schedule."""
        try:
            schedule = {
                'strategy': strategy,
                'interval_seconds': interval_seconds,
                'enabled': enabled,
                'last_run': None,
                'next_run': None
            }
            
            self.backup_schedules[schedule_id] = schedule
            
            if enabled:
                await self._start_schedule(schedule_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding backup schedule: {e}")
            return False
    
    async def _start_schedule(self, schedule_id: str) -> None:
        """Start scheduled backup task."""
        if schedule_id in self.schedule_tasks:
            return
        
        schedule = self.backup_schedules[schedule_id]
        
        async def schedule_loop():
            while True:
                try:
                    await asyncio.sleep(schedule['interval_seconds'])
                    
                    if schedule['enabled']:
                        backup_id = await self.persistence.create_backup(schedule['strategy'])
                        if backup_id:
                            schedule['last_run'] = datetime.now()
                            self.logger.info(f"Scheduled backup {schedule_id} completed: {backup_id}")
                        
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Scheduled backup {schedule_id} error: {e}")
        
        self.schedule_tasks[schedule_id] = asyncio.create_task(schedule_loop())
    
    async def stop_all_schedules(self) -> None:
        """Stop all backup schedules."""
        for task in self.schedule_tasks.values():
            task.cancel()
        
        # Wait for all tasks to complete
        if self.schedule_tasks:
            await asyncio.gather(*self.schedule_tasks.values(), return_exceptions=True)
        
        self.schedule_tasks.clear()
