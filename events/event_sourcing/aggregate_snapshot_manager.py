"""Aggregate Snapshot Manager - Advanced Implementation

Enterprise-grade snapshot management for event sourcing aggregates with
multiple storage strategies, compression, validation, and automatic cleanup.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import hashlib
import gzip
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Type, Union, Protocol
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from uuid import uuid4

from . import AggregateRoot, DomainEvent

logger = logging.getLogger(__name__)


class SnapshotStrategy(Enum):
    """Snapshot creation strategies"""
    TIME_BASED = "time_based"  # Create snapshots based on time intervals
    EVENT_BASED = "event_based"  # Create snapshots after N events
    SIZE_BASED = "size_based"  # Create snapshots when aggregate size exceeds threshold
    BUSINESS_BASED = "business_based"  # Create snapshots at important business events
    HYBRID = "hybrid"  # Combination of multiple strategies


class CompressionType(Enum):
    """Snapshot compression types"""
    NONE = "none"
    GZIP = "gzip"
    LZMA = "lzma"
    BROTLI = "brotli"


class SnapshotStatus(Enum):
    """Snapshot status"""
    PENDING = "pending"
    CREATING = "creating"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class SnapshotMetadata:
    """Snapshot metadata information"""
    snapshot_id: str
    aggregate_id: str
    aggregate_type: str
    version: int
    created_at: datetime
    event_count: int
    original_size_bytes: int
    compressed_size_bytes: int
    compression_ratio: float
    checksum: str
    status: SnapshotStatus
    strategy_used: SnapshotStrategy
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SnapshotConfig:
    """Snapshot configuration"""
    # Strategy settings
    strategy: SnapshotStrategy = SnapshotStrategy.HYBRID
    time_interval_hours: int = 24
    event_threshold: int = 100
    size_threshold_mb: float = 10.0
    business_events: List[str] = field(default_factory=list)
    
    # Storage settings
    compression_type: CompressionType = CompressionType.GZIP
    max_snapshots_per_aggregate: int = 10
    retention_days: int = 30
    
    # Performance settings
    enable_async_creation: bool = True
    validation_enabled: bool = True
    auto_cleanup_enabled: bool = True
    
    # Business settings
    critical_aggregates: List[str] = field(default_factory=list)
    high_frequency_aggregates: List[str] = field(default_factory=list)


class SnapshotData:
    """Serializable snapshot data container"""
    
    def __init__(self, aggregate_state: Dict[str, Any], metadata: Dict[str, Any] = None):
        self.aggregate_state = aggregate_state
        self.metadata = metadata or {}
        self.created_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "aggregate_state": self.aggregate_state,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SnapshotData':
        """Create from dictionary"""
        instance = cls(
            aggregate_state=data["aggregate_state"],
            metadata=data.get("metadata", {})
        )
        instance.created_at = datetime.fromisoformat(data["created_at"])
        return instance


class SnapshotStorageInterface(ABC):
    """Interface for snapshot storage implementations"""
    
    @abstractmethod
    async def save_snapshot(self, metadata: SnapshotMetadata, 
                          data: SnapshotData) -> bool:
        """Save snapshot to storage"""
        pass
    
    @abstractmethod
    async def load_snapshot(self, snapshot_id: str) -> Optional[SnapshotData]:
        """Load snapshot from storage"""
        pass
    
    @abstractmethod
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete snapshot from storage"""
        pass
    
    @abstractmethod
    async def list_snapshots(self, aggregate_id: str) -> List[SnapshotMetadata]:
        """List snapshots for aggregate"""
        pass
    
    @abstractmethod
    async def cleanup_expired_snapshots(self, retention_days: int) -> int:
        """Cleanup expired snapshots"""
        pass


class MemorySnapshotStorage(SnapshotStorageInterface):
    """In-memory snapshot storage for testing/development"""
    
    def __init__(self):
        self.snapshots: Dict[str, SnapshotData] = {}
        self.metadata_store: Dict[str, SnapshotMetadata] = {}
        self.aggregate_snapshots: Dict[str, List[str]] = {}
    
    async def save_snapshot(self, metadata: SnapshotMetadata, 
                          data: SnapshotData) -> bool:
        """Save snapshot to memory"""
        try:
            self.snapshots[metadata.snapshot_id] = data
            self.metadata_store[metadata.snapshot_id] = metadata
            
            if metadata.aggregate_id not in self.aggregate_snapshots:
                self.aggregate_snapshots[metadata.aggregate_id] = []
            self.aggregate_snapshots[metadata.aggregate_id].append(metadata.snapshot_id)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return False
    
    async def load_snapshot(self, snapshot_id: str) -> Optional[SnapshotData]:
        """Load snapshot from memory"""
        return self.snapshots.get(snapshot_id)
    
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete snapshot from memory"""
        try:
            if snapshot_id in self.snapshots:
                del self.snapshots[snapshot_id]
            
            if snapshot_id in self.metadata_store:
                metadata = self.metadata_store[snapshot_id]
                del self.metadata_store[snapshot_id]
                
                # Remove from aggregate list
                if metadata.aggregate_id in self.aggregate_snapshots:
                    self.aggregate_snapshots[metadata.aggregate_id].remove(snapshot_id)
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete snapshot: {e}")
            return False
    
    async def list_snapshots(self, aggregate_id: str) -> List[SnapshotMetadata]:
        """List snapshots for aggregate"""
        snapshot_ids = self.aggregate_snapshots.get(aggregate_id, [])
        return [self.metadata_store[sid] for sid in snapshot_ids if sid in self.metadata_store]
    
    async def cleanup_expired_snapshots(self, retention_days: int) -> int:
        """Cleanup expired snapshots"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        expired_count = 0
        
        expired_snapshots = []
        for snapshot_id, metadata in self.metadata_store.items():
            if metadata.created_at < cutoff_date:
                expired_snapshots.append(snapshot_id)
        
        for snapshot_id in expired_snapshots:
            if await self.delete_snapshot(snapshot_id):
                expired_count += 1
        
        return expired_count


class FileSystemSnapshotStorage(SnapshotStorageInterface):
    """File system based snapshot storage"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        import os
        os.makedirs(base_path, exist_ok=True)
    
    async def save_snapshot(self, metadata: SnapshotMetadata, 
                          data: SnapshotData) -> bool:
        """Save snapshot to file system"""
        try:
            import os
            import pickle
            
            # Create aggregate directory
            aggregate_dir = os.path.join(self.base_path, metadata.aggregate_id)
            os.makedirs(aggregate_dir, exist_ok=True)
            
            # Save snapshot data
            data_path = os.path.join(aggregate_dir, f"{metadata.snapshot_id}.data")
            with open(data_path, 'wb') as f:
                pickle.dump(data, f)
            
            # Save metadata
            metadata_path = os.path.join(aggregate_dir, f"{metadata.snapshot_id}.meta")
            with open(metadata_path, 'w') as f:
                json.dump({
                    "snapshot_id": metadata.snapshot_id,
                    "aggregate_id": metadata.aggregate_id,
                    "aggregate_type": metadata.aggregate_type,
                    "version": metadata.version,
                    "created_at": metadata.created_at.isoformat(),
                    "event_count": metadata.event_count,
                    "original_size_bytes": metadata.original_size_bytes,
                    "compressed_size_bytes": metadata.compressed_size_bytes,
                    "compression_ratio": metadata.compression_ratio,
                    "checksum": metadata.checksum,
                    "status": metadata.status.value,
                    "strategy_used": metadata.strategy_used.value,
                    "metadata": metadata.metadata
                }, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save snapshot to filesystem: {e}")
            return False
    
    async def load_snapshot(self, snapshot_id: str) -> Optional[SnapshotData]:
        """Load snapshot from file system"""
        try:
            import os
            import pickle
            import glob
            
            # Find snapshot file
            pattern = os.path.join(self.base_path, "*", f"{snapshot_id}.data")
            files = glob.glob(pattern)
            
            if not files:
                return None
            
            with open(files[0], 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load snapshot from filesystem: {e}")
            return None
    
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete snapshot from file system"""
        try:
            import os
            import glob
            
            # Find and delete files
            pattern = os.path.join(self.base_path, "*", f"{snapshot_id}.*")
            files = glob.glob(pattern)
            
            for file_path in files:
                os.remove(file_path)
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete snapshot from filesystem: {e}")
            return False
    
    async def list_snapshots(self, aggregate_id: str) -> List[SnapshotMetadata]:
        """List snapshots for aggregate"""
        try:
            import os
            import glob
            
            aggregate_dir = os.path.join(self.base_path, aggregate_id)
            if not os.path.exists(aggregate_dir):
                return []
            
            metadata_files = glob.glob(os.path.join(aggregate_dir, "*.meta"))
            snapshots = []
            
            for metadata_file in metadata_files:
                try:
                    with open(metadata_file, 'r') as f:
                        data = json.load(f)
                        
                    metadata = SnapshotMetadata(
                        snapshot_id=data["snapshot_id"],
                        aggregate_id=data["aggregate_id"],
                        aggregate_type=data["aggregate_type"],
                        version=data["version"],
                        created_at=datetime.fromisoformat(data["created_at"]),
                        event_count=data["event_count"],
                        original_size_bytes=data["original_size_bytes"],
                        compressed_size_bytes=data["compressed_size_bytes"],
                        compression_ratio=data["compression_ratio"],
                        checksum=data["checksum"],
                        status=SnapshotStatus(data["status"]),
                        strategy_used=SnapshotStrategy(data["strategy_used"]),
                        metadata=data.get("metadata", {})
                    )
                    snapshots.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to load metadata from {metadata_file}: {e}")
            
            return sorted(snapshots, key=lambda x: x.created_at, reverse=True)
        except Exception as e:
            logger.error(f"Failed to list snapshots: {e}")
            return []
    
    async def cleanup_expired_snapshots(self, retention_days: int) -> int:
        """Cleanup expired snapshots"""
        try:
            import os
            import glob
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
            expired_count = 0
            
            metadata_files = glob.glob(os.path.join(self.base_path, "*", "*.meta"))
            
            for metadata_file in metadata_files:
                try:
                    with open(metadata_file, 'r') as f:
                        data = json.load(f)
                    
                    created_at = datetime.fromisoformat(data["created_at"])
                    if created_at < cutoff_date:
                        snapshot_id = data["snapshot_id"]
                        if await self.delete_snapshot(snapshot_id):
                            expired_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process metadata file {metadata_file}: {e}")
            
            return expired_count
        except Exception as e:
            logger.error(f"Failed to cleanup expired snapshots: {e}")
            return 0


class SnapshotCompressor:
    """Snapshot compression utilities"""
    
    @staticmethod
    def compress(data: bytes, compression_type: CompressionType) -> bytes:
        """Compress snapshot data"""
        if compression_type == CompressionType.NONE:
            return data
        elif compression_type == CompressionType.GZIP:
            return gzip.compress(data)
        elif compression_type == CompressionType.LZMA:
            import lzma
            return lzma.compress(data)
        elif compression_type == CompressionType.BROTLI:
            try:
                import brotli
                return brotli.compress(data)
            except ImportError:
                logger.warning("Brotli not available, using gzip")
                return gzip.compress(data)
        else:
            return data
    
    @staticmethod
    def decompress(data: bytes, compression_type: CompressionType) -> bytes:
        """Decompress snapshot data"""
        if compression_type == CompressionType.NONE:
            return data
        elif compression_type == CompressionType.GZIP:
            return gzip.decompress(data)
        elif compression_type == CompressionType.LZMA:
            import lzma
            return lzma.decompress(data)
        elif compression_type == CompressionType.BROTLI:
            try:
                import brotli
                return brotli.decompress(data)
            except ImportError:
                logger.warning("Brotli not available, using gzip")
                return gzip.decompress(data)
        else:
            return data


class SnapshotValidator:
    """Snapshot validation utilities"""
    
    @staticmethod
    def calculate_checksum(data: SnapshotData) -> str:
        """Calculate checksum for snapshot data"""
        data_str = json.dumps(data.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def validate_snapshot(metadata: SnapshotMetadata, data: SnapshotData) -> bool:
        """Validate snapshot integrity"""
        try:
            # Check checksum
            calculated_checksum = SnapshotValidator.calculate_checksum(data)
            if calculated_checksum != metadata.checksum:
                logger.error(f"Checksum mismatch for snapshot {metadata.snapshot_id}")
                return False
            
            # Check data structure
            if not isinstance(data.aggregate_state, dict):
                logger.error(f"Invalid aggregate state for snapshot {metadata.snapshot_id}")
                return False
            
            # Check metadata consistency
            if data.created_at != metadata.created_at:
                logger.warning(f"Timestamp mismatch for snapshot {metadata.snapshot_id}")
            
            return True
        except Exception as e:
            logger.error(f"Snapshot validation failed: {e}")
            return False


class AggregateSnapshotManager:
    """Enterprise aggregate snapshot manager"""
    
    def __init__(self, config: SnapshotConfig, storage: SnapshotStorageInterface):
        self.config = config
        self.storage = storage
        self.compressor = SnapshotCompressor()
        self.validator = SnapshotValidator()
        self.pending_snapshots: Dict[str, asyncio.Task] = {}
        self.snapshot_cache: Dict[str, SnapshotData] = {}
        self.last_cleanup = datetime.now(timezone.utc)
    
    async def should_create_snapshot(self, aggregate: AggregateRoot, 
                                   latest_event: DomainEvent = None) -> bool:
        """Determine if a snapshot should be created"""
        try:
            # Get existing snapshots
            snapshots = await self.storage.list_snapshots(aggregate.aggregate_id)
            
            if not snapshots:
                # No snapshots exist, create first one
                return True
            
            latest_snapshot = max(snapshots, key=lambda x: x.version)
            events_since_snapshot = aggregate.version - latest_snapshot.version
            
            # Check time-based strategy
            if self.config.strategy in [SnapshotStrategy.TIME_BASED, SnapshotStrategy.HYBRID]:
                time_since_snapshot = datetime.now(timezone.utc) - latest_snapshot.created_at
                if time_since_snapshot.total_seconds() >= self.config.time_interval_hours * 3600:
                    return True
            
            # Check event-based strategy
            if self.config.strategy in [SnapshotStrategy.EVENT_BASED, SnapshotStrategy.HYBRID]:
                if events_since_snapshot >= self.config.event_threshold:
                    return True
            
            # Check business-based strategy
            if self.config.strategy in [SnapshotStrategy.BUSINESS_BASED, SnapshotStrategy.HYBRID]:
                if latest_event and latest_event.event_type in self.config.business_events:
                    return True
            
            # Check size-based strategy (simplified)
            if self.config.strategy in [SnapshotStrategy.SIZE_BASED, SnapshotStrategy.HYBRID]:
                # Estimate size based on number of events
                estimated_size_mb = events_since_snapshot * 0.001  # Rough estimate
                if estimated_size_mb >= self.config.size_threshold_mb:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to determine snapshot need: {e}")
            return False
    
    async def create_snapshot(self, aggregate: AggregateRoot, 
                            strategy: SnapshotStrategy = None) -> Optional[str]:
        """Create a snapshot of the aggregate"""
        snapshot_id = str(uuid4())
        
        try:
            # Serialize aggregate state
            aggregate_state = self._serialize_aggregate(aggregate)
            
            # Create snapshot data
            snapshot_data = SnapshotData(
                aggregate_state=aggregate_state,
                metadata={
                    "aggregate_type": aggregate.aggregate_type,
                    "version": aggregate.version,
                    "strategy": (strategy or self.config.strategy).value
                }
            )
            
            # Calculate sizes and compression
            original_data = json.dumps(snapshot_data.to_dict(), default=str).encode()
            original_size = len(original_data)
            
            compressed_data = self.compressor.compress(original_data, self.config.compression_type)
            compressed_size = len(compressed_data)
            
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            # Calculate checksum
            checksum = self.validator.calculate_checksum(snapshot_data)
            
            # Create metadata
            metadata = SnapshotMetadata(
                snapshot_id=snapshot_id,
                aggregate_id=aggregate.aggregate_id,
                aggregate_type=aggregate.aggregate_type,
                version=aggregate.version,
                created_at=datetime.now(timezone.utc),
                event_count=aggregate.version,
                original_size_bytes=original_size,
                compressed_size_bytes=compressed_size,
                compression_ratio=compression_ratio,
                checksum=checksum,
                status=SnapshotStatus.CREATING,
                strategy_used=strategy or self.config.strategy
            )
            
            # Save snapshot
            if self.config.enable_async_creation:
                # Create snapshot asynchronously
                task = asyncio.create_task(
                    self._save_snapshot_async(metadata, snapshot_data)
                )
                self.pending_snapshots[snapshot_id] = task
            else:
                # Create snapshot synchronously
                success = await self.storage.save_snapshot(metadata, snapshot_data)
                if not success:
                    logger.error(f"Failed to save snapshot {snapshot_id}")
                    return None
                
                metadata.status = SnapshotStatus.COMPLETED
                await self.storage.save_snapshot(metadata, snapshot_data)
            
            # Cache snapshot
            self.snapshot_cache[snapshot_id] = snapshot_data
            
            # Cleanup old snapshots
            await self._cleanup_old_snapshots(aggregate.aggregate_id)
            
            logger.info(f"Created snapshot {snapshot_id} for aggregate {aggregate.aggregate_id}")
            return snapshot_id
            
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            return None
    
    async def load_latest_snapshot(self, aggregate_id: str) -> Optional[SnapshotData]:
        """Load the latest snapshot for an aggregate"""
        try:
            snapshots = await self.storage.list_snapshots(aggregate_id)
            if not snapshots:
                return None
            
            # Get latest completed snapshot
            completed_snapshots = [s for s in snapshots if s.status == SnapshotStatus.COMPLETED]
            if not completed_snapshots:
                return None
            
            latest_snapshot = max(completed_snapshots, key=lambda x: x.version)
            
            # Check cache first
            if latest_snapshot.snapshot_id in self.snapshot_cache:
                return self.snapshot_cache[latest_snapshot.snapshot_id]
            
            # Load from storage
            snapshot_data = await self.storage.load_snapshot(latest_snapshot.snapshot_id)
            
            if snapshot_data and self.config.validation_enabled:
                if not self.validator.validate_snapshot(latest_snapshot, snapshot_data):
                    logger.error(f"Snapshot validation failed for {latest_snapshot.snapshot_id}")
                    return None
            
            # Cache for future use
            if snapshot_data:
                self.snapshot_cache[latest_snapshot.snapshot_id] = snapshot_data
            
            return snapshot_data
            
        except Exception as e:
            logger.error(f"Failed to load latest snapshot: {e}")
            return None
    
    async def restore_aggregate(self, aggregate_id: str, 
                              aggregate_class: Type[AggregateRoot]) -> Optional[AggregateRoot]:
        """Restore aggregate from latest snapshot"""
        try:
            snapshot_data = await self.load_latest_snapshot(aggregate_id)
            if not snapshot_data:
                return None
            
            # Create new aggregate instance
            aggregate = aggregate_class(aggregate_id)
            
            # Restore state from snapshot
            self._deserialize_aggregate(aggregate, snapshot_data.aggregate_state)
            
            # Mark as committed to prevent uncommitted events
            aggregate.mark_events_as_committed()
            
            logger.info(f"Restored aggregate {aggregate_id} from snapshot")
            return aggregate
            
        except Exception as e:
            logger.error(f"Failed to restore aggregate from snapshot: {e}")
            return None
    
    async def delete_snapshots(self, aggregate_id: str) -> int:
        """Delete all snapshots for an aggregate"""
        try:
            snapshots = await self.storage.list_snapshots(aggregate_id)
            deleted_count = 0
            
            for snapshot in snapshots:
                if await self.storage.delete_snapshot(snapshot.snapshot_id):
                    deleted_count += 1
                    # Remove from cache
                    if snapshot.snapshot_id in self.snapshot_cache:
                        del self.snapshot_cache[snapshot.snapshot_id]
            
            logger.info(f"Deleted {deleted_count} snapshots for aggregate {aggregate_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete snapshots: {e}")
            return 0
    
    async def cleanup_expired_snapshots(self) -> int:
        """Cleanup expired snapshots"""
        if not self.config.auto_cleanup_enabled:
            return 0
        
        try:
            expired_count = await self.storage.cleanup_expired_snapshots(self.config.retention_days)
            self.last_cleanup = datetime.now(timezone.utc)
            
            logger.info(f"Cleaned up {expired_count} expired snapshots")
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired snapshots: {e}")
            return 0
    
    async def get_snapshot_statistics(self, aggregate_id: str = None) -> Dict[str, Any]:
        """Get snapshot statistics"""
        try:
            if aggregate_id:
                snapshots = await self.storage.list_snapshots(aggregate_id)
            else:
                # This would need to be implemented in storage interface
                snapshots = []
            
            if not snapshots:
                return {"total_snapshots": 0}
            
            total_size = sum(s.compressed_size_bytes for s in snapshots)
            avg_compression = sum(s.compression_ratio for s in snapshots) / len(snapshots)
            
            return {
                "total_snapshots": len(snapshots),
                "total_size_mb": total_size / (1024 * 1024),
                "average_compression_ratio": avg_compression,
                "latest_snapshot": max(snapshots, key=lambda x: x.created_at).created_at.isoformat(),
                "strategies_used": list(set(s.strategy_used.value for s in snapshots))
            }
            
        except Exception as e:
            logger.error(f"Failed to get snapshot statistics: {e}")
            return {}
    
    def _serialize_aggregate(self, aggregate: AggregateRoot) -> Dict[str, Any]:
        """Serialize aggregate state to dictionary"""
        # This is a basic implementation - should be customized per aggregate type
        state = {}
        
        # Copy basic attributes
        for attr in dir(aggregate):
            if not attr.startswith('_') and not callable(getattr(aggregate, attr)):
                value = getattr(aggregate, attr)
                if isinstance(value, (str, int, float, bool, list, dict)):
                    state[attr] = value
                elif hasattr(value, '__dict__'):
                    state[attr] = value.__dict__
        
        return state
    
    def _deserialize_aggregate(self, aggregate: AggregateRoot, state: Dict[str, Any]) -> None:
        """Deserialize state into aggregate"""
        # This is a basic implementation - should be customized per aggregate type
        for attr, value in state.items():
            if hasattr(aggregate, attr):
                setattr(aggregate, attr, value)
    
    async def _save_snapshot_async(self, metadata: SnapshotMetadata, 
                                 data: SnapshotData) -> None:
        """Save snapshot asynchronously"""
        try:
            success = await self.storage.save_snapshot(metadata, data)
            
            metadata.status = SnapshotStatus.COMPLETED if success else SnapshotStatus.FAILED
            
            # Update metadata
            await self.storage.save_snapshot(metadata, data)
            
            # Remove from pending
            if metadata.snapshot_id in self.pending_snapshots:
                del self.pending_snapshots[metadata.snapshot_id]
                
        except Exception as e:
            logger.error(f"Async snapshot save failed: {e}")
            metadata.status = SnapshotStatus.FAILED
    
    async def _cleanup_old_snapshots(self, aggregate_id: str) -> None:
        """Cleanup old snapshots for aggregate"""
        try:
            snapshots = await self.storage.list_snapshots(aggregate_id)
            
            if len(snapshots) <= self.config.max_snapshots_per_aggregate:
                return
            
            # Sort by creation time and keep only the latest ones
            sorted_snapshots = sorted(snapshots, key=lambda x: x.created_at, reverse=True)
            snapshots_to_delete = sorted_snapshots[self.config.max_snapshots_per_aggregate:]
            
            for snapshot in snapshots_to_delete:
                await self.storage.delete_snapshot(snapshot.snapshot_id)
                if snapshot.snapshot_id in self.snapshot_cache:
                    del self.snapshot_cache[snapshot.snapshot_id]
            
            logger.info(f"Cleaned up {len(snapshots_to_delete)} old snapshots for {aggregate_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old snapshots: {e}")
    
    async def health_check(self) -> bool:
        """Check snapshot manager health"""
        try:
            # Check storage health if it has a health check method
            if hasattr(self.storage, 'health_check'):
                return await self.storage.health_check()
            return True
        except Exception as e:
            logger.error(f"Snapshot manager health check failed: {e}")
            return False