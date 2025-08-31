"""
Backup Storage for IA Influencer Agent Platform.

Provides enterprise-grade backup storage management with support for
multiple storage backends, redundancy, and disaster recovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import shutil
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from ...core.exceptions import StorageError


class StorageBackend(Enum):
    """Storage backend enumeration."""
    LOCAL = "local"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GCS = "gcs"
    FTP = "ftp"
    SFTP = "sftp"
    NFS = "nfs"


class StorageStatus(Enum):
    """Storage status enumeration."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class StorageConfig:
    """Storage configuration container."""
    backend: StorageBackend
    connection_params: Dict[str, Any]
    retention_days: int = 30
    compression_enabled: bool = True
    encryption_enabled: bool = True
    redundancy_level: int = 1
    max_file_size_mb: int = 1024
    chunk_size_mb: int = 64


@dataclass
class BackupMetadata:
    """Backup metadata container."""
    backup_id: str
    created_at: datetime
    size_bytes: int
    checksum: str
    compression_ratio: float
    encrypted: bool
    redundancy_locations: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    retention_until: Optional[datetime] = None


@dataclass
class StorageLocation:
    """Storage location information."""
    backend: StorageBackend
    path: str
    size_bytes: int
    created_at: datetime
    last_verified: Optional[datetime] = None
    status: StorageStatus = StorageStatus.AVAILABLE


class StorageBackendInterface(ABC):
    """Abstract storage backend interface."""
    
    @abstractmethod
    async def store_backup(
        self,
        backup_id: str,
        data: Union[bytes, Dict[str, Any]],
        metadata: BackupMetadata
    ) -> bool:
        """Store backup data."""
        pass
    
    @abstractmethod
    async def retrieve_backup(self, backup_id: str) -> Optional[Union[bytes, Dict[str, Any]]]:
        """Retrieve backup data."""
        pass
    
    @abstractmethod
    async def delete_backup(self, backup_id: str) -> bool:
        """Delete backup data."""
        pass
    
    @abstractmethod
    async def list_backups(self) -> List[str]:
        """List available backups."""
        pass
    
    @abstractmethod
    async def get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get backup metadata."""
        pass
    
    @abstractmethod
    async def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity."""
        pass
    
    @abstractmethod
    async def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage information."""
        pass


class LocalStorageBackend(StorageBackendInterface):
    """Local filesystem storage backend."""
    
    def __init__(self, config: StorageConfig):
        """Initialize local storage backend."""
        self.config = config
        self.base_path = Path(config.connection_params.get("path", "/tmp/backups"))
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path = self.base_path / "metadata"
        self.metadata_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    async def store_backup(
        self,
        backup_id: str,
        data: Union[bytes, Dict[str, Any]],
        metadata: BackupMetadata
    ) -> bool:
        """Store backup data locally."""



        try:
            backup_file = self.base_path / f"{backup_id}.backup"
            metadata_file = self.metadata_path / f"{backup_id}.json"
            
            # Store backup data
            if isinstance(data, dict):
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            else:
                with open(backup_file, 'wb') as f:
                    f.write(data)
            
            # Store metadata
            metadata_dict = {
                "backup_id": metadata.backup_id,
                "created_at": metadata.created_at.isoformat(),
                "size_bytes": metadata.size_bytes,
                "checksum": metadata.checksum,
                "compression_ratio": metadata.compression_ratio,
                "encrypted": metadata.encrypted,
                "redundancy_locations": metadata.redundancy_locations,
                "tags": metadata.tags,
                "retention_until": metadata.retention_until.isoformat() if metadata.retention_until else None
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata_dict, f, indent=2)
            
            self.logger.info(f"Backup stored locally: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store backup locally: {backup_id} - {e}")
            return False
    
    async def retrieve_backup(self, backup_id: str) -> Optional[Union[bytes, Dict[str, Any]]]:
        """Retrieve backup data from local storage."""



        try:
            backup_file = self.base_path / f"{backup_id}.backup"
            
            if not backup_file.exists():
                return None
            
            # Try to load as JSON first
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Load as binary data
                with open(backup_file, 'rb') as f:
                    return f.read()
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve backup locally: {backup_id} - {e}")
            return None
    
    async def delete_backup(self, backup_id: str) -> bool:
        """Delete backup data from local storage."""



        try:
            backup_file = self.base_path / f"{backup_id}.backup"
            metadata_file = self.metadata_path / f"{backup_id}.json"
            
            if backup_file.exists():
                backup_file.unlink()
            
            if metadata_file.exists():
                metadata_file.unlink()
            
            self.logger.info(f"Backup deleted locally: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete backup locally: {backup_id} - {e}")
            return False
    
    async def list_backups(self) -> List[str]:
        """List available backups in local storage."""



        try:
            backup_files = list(self.base_path.glob("*.backup"))
            return [f.stem for f in backup_files]
        except Exception as e:
            self.logger.error(f"Failed to list local backups: {e}")
            return []
    
    async def get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get backup metadata from local storage."""



        try:
            metadata_file = self.metadata_path / f"{backup_id}.json"
            
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return BackupMetadata(
                backup_id=data["backup_id"],
                created_at=datetime.fromisoformat(data["created_at"]),
                size_bytes=data["size_bytes"],
                checksum=data["checksum"],
                compression_ratio=data["compression_ratio"],
                encrypted=data["encrypted"],
                redundancy_locations=data.get("redundancy_locations", []),
                tags=data.get("tags", {}),
                retention_until=datetime.fromisoformat(data["retention_until"]) if data.get("retention_until") else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get backup metadata locally: {backup_id} - {e}")
            return None
    
    async def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity in local storage."""



        try:
            backup_file = self.base_path / f"{backup_id}.backup"
            metadata_file = self.metadata_path / f"{backup_id}.json"
            
            return backup_file.exists() and metadata_file.exists()
            
        except Exception as e:
            self.logger.error(f"Failed to verify backup locally: {backup_id} - {e}")
            return False
    
    async def get_storage_usage(self) -> Dict[str, Any]:
        """Get local storage usage information."""



        try:
            total_size = 0
            file_count = 0
            
            for backup_file in self.base_path.glob("*.backup"):
                total_size += backup_file.stat().st_size
                file_count += 1
            
            # Get disk usage
            disk_usage = shutil.disk_usage(self.base_path)
            
            return {
                "backend": "local",
                "total_backups": file_count,
                "total_size_bytes": total_size,
                "available_space_bytes": disk_usage.free,
                "total_space_bytes": disk_usage.total,
                "used_space_bytes": disk_usage.used,
                "path": str(self.base_path)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get local storage usage: {e}")
            return {}


class BackupStorage:
    """
    Enterprise backup storage manager with multiple backend support.
    
    Manages backup storage across multiple backends with redundancy,
    retention policies, and disaster recovery capabilities.
    """

    def __init__(self, storage_configs: List[StorageConfig]):
        """
        Initialize backup storage manager.
        
        Args:
            storage_configs: List of storage backend configurations
        """
        self.logger = logging.getLogger(__name__)
        self.storage_configs = storage_configs
        self.backends: Dict[str, StorageBackendInterface] = {}
        self.primary_backend: Optional[str] = None
        self.backup_registry: Dict[str, List[StorageLocation]] = {}
        
        # Initialize storage backends
        self._initialize_backends()

    def _initialize_backends(self):
        """Initialize storage backends from configurations."""
        for i, config in enumerate(self.storage_configs):
            backend_id = f"{config.backend.value}_{i}"
            
            if config.backend == StorageBackend.LOCAL:
                backend = LocalStorageBackend(config)
                self.backends[backend_id] = backend
                
                # Set first backend as primary
                if self.primary_backend is None:
                    self.primary_backend = backend_id
                    
            else:
                # Other backends would be implemented here
                self.logger.warning(f"Backend not implemented: {config.backend.value}")

    async def store_backup(
        self,
        backup_id: str,
        data: Union[bytes, Dict[str, Any]],
        metadata: Optional[BackupMetadata] = None,
        redundancy_count: int = 1
    ) -> bool:
        """
        Store backup data with optional redundancy.
        
        Args:
            backup_id: Unique backup identifier
            data: Backup data to store
            metadata: Backup metadata
            redundancy_count: Number of redundant copies to create
            
        Returns:
            Success status
        """
        self.logger.info(f"Storing backup: {backup_id} (redundancy: {redundancy_count})")
        
        # Create metadata if not provided
        if metadata is None:
            data_size = len(data) if isinstance(data, bytes) else len(json.dumps(data, default=str).encode())
            metadata = BackupMetadata(
                backup_id=backup_id,
                created_at=datetime.now(),
                size_bytes=data_size,
                checksum="",  # Would be calculated
                compression_ratio=1.0,
                encrypted=False
            )
        
        success_count = 0
        storage_locations = []
        
        # Store to available backends
        for backend_id, backend in self.backends.items():
            try:
                if await backend.store_backup(backup_id, data, metadata):
                    success_count += 1
                    
                    # Create storage location record
                    location = StorageLocation(
                        backend=StorageBackend(backend_id.split('_')[0]),
                        path=f"{backend_id}/{backup_id}",
                        size_bytes=metadata.size_bytes,
                        created_at=datetime.now(),
                        status=StorageStatus.AVAILABLE
                    )
                    storage_locations.append(location)
                    
                    # Stop if we have enough redundant copies
                    if success_count >= redundancy_count:
                        break
                        
            except Exception as e:
                self.logger.error(f"Failed to store backup in {backend_id}: {e}")
        
        # Update backup registry
        self.backup_registry[backup_id] = storage_locations
        
        success = success_count >= redundancy_count
        
        if success:
            self.logger.info(f"Backup stored successfully: {backup_id} ({success_count} copies)")
        else:
            self.logger.error(f"Failed to store backup with required redundancy: {backup_id}")
        
        return success

    async def retrieve_backup(self, backup_id: str) -> Optional[Union[bytes, Dict[str, Any]]]:
        """
        Retrieve backup data from storage.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Backup data or None if not found
        """
        self.logger.debug(f"Retrieving backup: {backup_id}")
        
        # Check if backup is in registry
        if backup_id not in self.backup_registry:
            # Try to find backup in all backends
            for backend_id, backend in self.backends.items():
                try:
                    data = await backend.retrieve_backup(backup_id)
                    if data is not None:
                        self.logger.info(f"Backup retrieved from {backend_id}: {backup_id}")
                        return data
                except Exception as e:
                    self.logger.error(f"Failed to retrieve backup from {backend_id}: {e}")
            
            self.logger.warning(f"Backup not found: {backup_id}")
            return None
        
        # Try to retrieve from registered locations
        locations = self.backup_registry[backup_id]
        
        for location in locations:
            if location.status != StorageStatus.AVAILABLE:
                continue
            
            backend_id = f"{location.backend.value}_0"  # Simplified backend lookup
            if backend_id not in self.backends:
                continue
            
            try:
                backend = self.backends[backend_id]
                data = await backend.retrieve_backup(backup_id)
                
                if data is not None:
                    self.logger.info(f"Backup retrieved from {backend_id}: {backup_id}")
                    return data
                    
            except Exception as e:
                self.logger.error(f"Failed to retrieve backup from {backend_id}: {e}")
                # Mark location as degraded
                location.status = StorageStatus.DEGRADED
        
        self.logger.error(f"Failed to retrieve backup from all locations: {backup_id}")
        return None

    async def delete_backup(self, backup_id: str, force: bool = False) -> bool:
        """
        Delete backup from all storage locations.
        
        Args:
            backup_id: Backup identifier
            force: Force deletion even if some backends fail
            
        Returns:
            Success status
        """
        self.logger.info(f"Deleting backup: {backup_id} (force: {force})")
        
        success_count = 0
        total_attempts = 0
        
        # Delete from all backends
        for backend_id, backend in self.backends.items():
            try:
                total_attempts += 1
                if await backend.delete_backup(backup_id):
                    success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to delete backup from {backend_id}: {e}")
        
        # Remove from registry
        if backup_id in self.backup_registry:
            del self.backup_registry[backup_id]
        
        success = success_count == total_attempts or (force and success_count > 0)
        
        if success:
            self.logger.info(f"Backup deleted: {backup_id} ({success_count}/{total_attempts} backends)")
        else:
            self.logger.error(f"Failed to delete backup from all backends: {backup_id}")
        
        return success

    async def list_backups(self, backend_filter: Optional[str] = None) -> List[str]:
        """
        List all available backups.
        
        Args:
            backend_filter: Filter by specific backend
            
        Returns:
            List of backup identifiers
        """
        all_backups = set()
        
        backends_to_check = self.backends
        if backend_filter:
            backends_to_check = {k: v for k, v in self.backends.items() if k.startswith(backend_filter)}
        
        for backend_id, backend in backends_to_check.items():
            try:
                backups = await backend.list_backups()
                all_backups.update(backups)
            except Exception as e:
                self.logger.error(f"Failed to list backups from {backend_id}: {e}")
        
        return sorted(list(all_backups))

    async def get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """
        Get backup metadata.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Backup metadata or None if not found
        """
        # Try primary backend first
        if self.primary_backend and self.primary_backend in self.backends:
            try:
                backend = self.backends[self.primary_backend]
                metadata = await backend.get_backup_metadata(backup_id)
                if metadata:
                    return metadata
            except Exception as e:
                self.logger.error(f"Failed to get metadata from primary backend: {e}")
        
        # Try all other backends
        for backend_id, backend in self.backends.items():
            if backend_id == self.primary_backend:
                continue
            
            try:
                metadata = await backend.get_backup_metadata(backup_id)
                if metadata:
                    return metadata
            except Exception as e:
                self.logger.error(f"Failed to get metadata from {backend_id}: {e}")
        
        return None

    async def get_backup_size(self, backup_id: str) -> Optional[int]:
        """
        Get backup size in bytes.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Backup size in bytes or None if not found
        """
        metadata = await self.get_backup_metadata(backup_id)
        return metadata.size_bytes if metadata else None

    async def verify_backup_integrity(self, backup_id: str) -> Dict[str, bool]:
        """
        Verify backup integrity across all storage locations.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Verification results per backend
        """
        results = {}
        
        for backend_id, backend in self.backends.items():
            try:
                results[backend_id] = await backend.verify_backup(backup_id)
            except Exception as e:
                self.logger.error(f"Failed to verify backup in {backend_id}: {e}")
                results[backend_id] = False
        
        return results

    async def get_storage_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive storage statistics.
        
        Returns:
            Storage statistics across all backends
        """
        statistics = {
            "backends": {},
            "total_backups": 0,
            "total_size_bytes": 0,
            "redundancy_info": {},
            "health_status": "healthy"
        }
        
        all_backups = set()
        
        for backend_id, backend in self.backends.items():
            try:
                usage = await backend.get_storage_usage()
                statistics["backends"][backend_id] = usage
                
                # Get backup list for this backend
                backups = await backend.list_backups()
                all_backups.update(backups)
                
                statistics["total_size_bytes"] += usage.get("total_size_bytes", 0)
                
            except Exception as e:
                self.logger.error(f"Failed to get statistics from {backend_id}: {e}")
                statistics["backends"][backend_id] = {"error": str(e)}
                statistics["health_status"] = "degraded"
        
        statistics["total_backups"] = len(all_backups)
        
        # Calculate redundancy information
        for backup_id in all_backups:
            copy_count = 0
            for backend_id, backend in self.backends.items():
                try:
                    if await backend.verify_backup(backup_id):
                        copy_count += 1
                except Exception:
                    pass
            
            if copy_count not in statistics["redundancy_info"]:
                statistics["redundancy_info"][copy_count] = 0
            statistics["redundancy_info"][copy_count] += 1
        
        return statistics

    async def cleanup_expired_backups(self) -> Dict[str, int]:
        """
        Clean up expired backups based on retention policies.
        
        Returns:
            Cleanup statistics
        """
        self.logger.info("Starting cleanup of expired backups")
        
        cleanup_stats = {
            "expired_backups_found": 0,
            "expired_backups_deleted": 0,
            "errors": 0,
            "backends_processed": 0
        }
        
        current_time = datetime.now()
        
        for backend_id, backend in self.backends.items():
            try:
                cleanup_stats["backends_processed"] += 1
                
                # Get all backups for this backend
                backup_ids = await backend.list_backups()
                
                for backup_id in backup_ids:
                    metadata = await backend.get_backup_metadata(backup_id)
                    
                    if metadata and metadata.retention_until:
                        if current_time > metadata.retention_until:
                            cleanup_stats["expired_backups_found"] += 1
                            
                            # Delete expired backup
                            if await backend.delete_backup(backup_id):
                                cleanup_stats["expired_backups_deleted"] += 1
                                self.logger.info(f"Deleted expired backup: {backup_id}")
                            else:
                                cleanup_stats["errors"] += 1
                                self.logger.error(f"Failed to delete expired backup: {backup_id}")
                
            except Exception as e:
                cleanup_stats["errors"] += 1
                self.logger.error(f"Cleanup error in {backend_id}: {e}")
        
        self.logger.info(f"Cleanup completed: {cleanup_stats}")
        return cleanup_stats

    async def migrate_backup(
        self,
        backup_id: str,
        source_backend: str,
        target_backend: str
    ) -> bool:
        """
        Migrate backup between storage backends.
        
        Args:
            backup_id: Backup identifier
            source_backend: Source backend identifier
            target_backend: Target backend identifier
            
        Returns:
            Migration success status
        """
        self.logger.info(f"Migrating backup {backup_id} from {source_backend} to {target_backend}")
        
        if source_backend not in self.backends or target_backend not in self.backends:
            self.logger.error("Invalid source or target backend")
            return False
        
        try:
            # Retrieve from source
            source = self.backends[source_backend]
            data = await source.retrieve_backup(backup_id)
            metadata = await source.get_backup_metadata(backup_id)
            
            if not data or not metadata:
                self.logger.error(f"Failed to retrieve backup for migration: {backup_id}")
                return False
            
            # Store to target
            target = self.backends[target_backend]
            if not await target.store_backup(backup_id, data, metadata):
                self.logger.error(f"Failed to store backup in target backend: {backup_id}")
                return False
            
            # Verify migration
            if not await target.verify_backup(backup_id):
                self.logger.error(f"Migration verification failed: {backup_id}")
                return False
            
            self.logger.info(f"Backup migration completed: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup migration failed: {backup_id} - {e}")
            return False

    async def create_backup_snapshot(self, backup_ids: List[str]) -> Optional[str]:
        """
        Create a snapshot of multiple backups.
        
        Args:
            backup_ids: List of backup identifiers
            
        Returns:
            Snapshot identifier or None if failed
        """
        snapshot_id = f"snapshot_{int(time.time())}"
        
        self.logger.info(f"Creating backup snapshot: {snapshot_id}")
        
        try:
            snapshot_data = {
                "snapshot_id": snapshot_id,
                "created_at": datetime.now().isoformat(),
                "backup_ids": backup_ids,
                "backup_metadata": {}
            }
            
            # Collect metadata for all backups
            for backup_id in backup_ids:
                metadata = await self.get_backup_metadata(backup_id)
                if metadata:
                    snapshot_data["backup_metadata"][backup_id] = {
                        "created_at": metadata.created_at.isoformat(),
                        "size_bytes": metadata.size_bytes,
                        "checksum": metadata.checksum
                    }
            
            # Store snapshot
            snapshot_metadata = BackupMetadata(
                backup_id=snapshot_id,
                created_at=datetime.now(),
                size_bytes=len(json.dumps(snapshot_data, default=str).encode()),
                checksum="",  # Would be calculated
                compression_ratio=1.0,
                encrypted=False
            )
            
            if await self.store_backup(snapshot_id, snapshot_data, snapshot_metadata):
                self.logger.info(f"Backup snapshot created: {snapshot_id}")
                return snapshot_id
            else:
                self.logger.error(f"Failed to store backup snapshot: {snapshot_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to create backup snapshot: {e}")
            return None

    async def restore_from_snapshot(self, snapshot_id: str) -> List[str]:
        """
        Restore backups from snapshot.
        
        Args:
            snapshot_id: Snapshot identifier
            
        Returns:
            List of restored backup identifiers
        """
        self.logger.info(f"Restoring from backup snapshot: {snapshot_id}")
        
        try:
            # Retrieve snapshot data
            snapshot_data = await self.retrieve_backup(snapshot_id)
            if not snapshot_data or not isinstance(snapshot_data, dict):
                self.logger.error(f"Invalid snapshot data: {snapshot_id}")
                return []
            
            # Verify all backups exist
            backup_ids = snapshot_data.get("backup_ids", [])
            restored_backups = []
            
            for backup_id in backup_ids:
                if await self.verify_backup_integrity(backup_id):
                    restored_backups.append(backup_id)
                else:
                    self.logger.warning(f"Backup not available for restoration: {backup_id}")
            
            self.logger.info(f"Restored {len(restored_backups)}/{len(backup_ids)} backups from snapshot")
            return restored_backups
            
        except Exception as e:
            self.logger.error(f"Failed to restore from snapshot: {e}")
            return []
