"""Data Management Module - Enterprise Observability Data Lifecycle

Provides comprehensive data management for observability data including
storage, retention, archival, purging, compression, and lifecycle policies
for logs, metrics, traces, and analytics data.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""import asyncio
import json
import logging
import gzip
import shutil
import sqlite3
import time
import threading
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union, Iterator
from uuid import uuid4
import os
import hashlib
import pickle
import tempfile
import warnings
from functools import lru_cache
import psutil

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Data compression imports
try:
    import lz4.frame
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False


class DataType(Enum):
    """Types of observability data"""    LOGS = "logs"
    METRICS = "metrics"
    TRACES = "traces"
    ANALYTICS = "analytics"
    ALERTS = "alerts"
    DIAGNOSTICS = "diagnostics"
    HEALTH_CHECKS = "health_checks"
    EVENTS = "events"


class StorageTier(Enum):
    """Storage tiers for data lifecycle"""    HOT = "hot"          # Recent data, fast access
    WARM = "warm"        # Older data, medium access speed
    COLD = "cold"        # Archived data, slow access
    FROZEN = "frozen"    # Long-term archive, very slow access
    DELETED = "deleted"  # Marked for deletion


class CompressionType(Enum):
    """Data compression algorithms"""    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    BROTLI = "brotli"


class DataStatus(Enum):
    """Status of data records"""    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPRESSED = "compressed"
    SCHEDULED_DELETE = "scheduled_delete"
    DELETED = "deleted"
    CORRUPTED = "corrupted"


@dataclass
class DataRecord:
    """Represents a data record in the system"""    record_id: str
    data_type: DataType
    storage_tier: StorageTier
    compression: CompressionType
    status: DataStatus
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    size_bytes: int
    compressed_size_bytes: int = 0
    file_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    retention_policy: str = ""
    tags: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        result = asdict(self)
        result['data_type'] = self.data_type.value
        result['storage_tier'] = self.storage_tier.value
        result['compression'] = self.compression.value
        result['status'] = self.status.value
        result['created_at'] = self.created_at.isoformat()
        result['modified_at'] = self.modified_at.isoformat()
        result['accessed_at'] = self.accessed_at.isoformat()
        result['tags'] = list(self.tags)
        return result
    
    def get_age_days(self) -> int:
        """Get age of record in days"""        return (datetime.utcnow() - self.created_at).days
    
    def is_compressed(self) -> bool:
        """Check if record is compressed"""        return self.compression != CompressionType.NONE
    
    def compression_ratio(self) -> float:
        """Calculate compression ratio"""        if self.compressed_size_bytes > 0 and self.size_bytes > 0:
            return self.compressed_size_bytes / self.size_bytes
        return 1.0


@dataclass
class RetentionPolicy:
    """Data retention policy configuration"""    policy_id: str
    name: str
    description: str
    data_types: List[DataType]
    hot_retention_days: int = 7
    warm_retention_days: int = 30
    cold_retention_days: int = 365
    frozen_retention_days: int = 2555  # 7 years
    compression_after_days: int = 1
    preferred_compression: CompressionType = CompressionType.GZIP
    purge_after_days: int = 2555
    tags: Set[str] = field(default_factory=set)
    conditions: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def applies_to_record(self, record: DataRecord) -> bool:
        """Check if policy applies to a data record"""        if not self.enabled:
            return False
        
        # Check data type
        if self.data_types and record.data_type not in self.data_types:
            return False
        
        # Check tags
        if self.tags and not self.tags.intersection(record.tags):
            return False
        
        # Check conditions
        for condition_key, condition_value in self.conditions.items():
            if condition_key in record.metadata:
                if record.metadata[condition_key] != condition_value:
                    return False
        
        return True
    
    def get_target_tier(self, record: DataRecord) -> StorageTier:
        """Determine target storage tier for record"""        age_days = record.get_age_days()
        
        if age_days >= self.purge_after_days:
            return StorageTier.DELETED
        elif age_days >= self.frozen_retention_days:
            return StorageTier.FROZEN
        elif age_days >= self.cold_retention_days:
            return StorageTier.COLD
        elif age_days >= self.warm_retention_days:
            return StorageTier.WARM
        else:
            return StorageTier.HOT
    
    def should_compress(self, record: DataRecord) -> bool:
        """Check if record should be compressed"""        return (record.get_age_days() >= self.compression_after_days and 
                record.compression == CompressionType.NONE)


class BaseStorageBackend(ABC):
    """Abstract base class for storage backends"""    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"data_management.storage.{name}")
    
    @abstractmethod
    async def store_data(self, record_id: str, data: bytes, metadata: Dict[str, Any] = None) -> str:
        """Store data and return file path"""        pass
    
    @abstractmethod
    async def retrieve_data(self, file_path: str) -> bytes:
        """Retrieve data from storage"""        pass
    
    @abstractmethod
    async def delete_data(self, file_path: str) -> bool:
        """Delete data from storage"""        pass
    
    @abstractmethod
    async def list_files(self, prefix: str = "") -> List[str]:
        """List files with optional prefix"""        pass
    
    @abstractmethod
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""        pass


class FileSystemStorageBackend(BaseStorageBackend):
    """File system storage backend"""    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("filesystem", config)
        self.base_path = Path(config.get("base_path", "/var/data/observability"))
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create tier directories
        for tier in StorageTier:
            if tier != StorageTier.DELETED:
                tier_path = self.base_path / tier.value
                tier_path.mkdir(exist_ok=True)
    
    async def store_data(self, record_id: str, data: bytes, metadata: Dict[str, Any] = None) -> str:
        """Store data to filesystem"""        # Determine storage tier from metadata
        tier = metadata.get("tier", StorageTier.HOT.value) if metadata else StorageTier.HOT.value
        data_type = metadata.get("data_type", "unknown") if metadata else "unknown"
        
        # Create hierarchical path: tier/data_type/year/month/day/record_id
        now = datetime.utcnow()
        relative_path = Path(tier) / data_type / f"{now.year}" / f"{now.month:02d}" / f"{now.day:02d}" / f"{record_id}.dat"
        
        file_path = self.base_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write data
        async with asyncio.Lock():  # Ensure thread safety
            with open(file_path, 'wb') as f:
                f.write(data)
        
        self.logger.debug(f"Stored data for record {record_id} at {file_path}")
        return str(relative_path)
    
    async def retrieve_data(self, file_path: str) -> bytes:
        """Retrieve data from filesystem"""        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        with open(full_path, 'rb') as f:
            data = f.read()
        
        self.logger.debug(f"Retrieved data from {file_path}, size: {len(data)} bytes")
        return data
    
    async def delete_data(self, file_path: str) -> bool:
        """Delete data from filesystem"""        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                full_path.unlink()
                self.logger.debug(f"Deleted data file: {file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete {file_path}: {str(e)}")
            return False
    
    async def list_files(self, prefix: str = "") -> List[str]:
        """List files with optional prefix"""        files = []
        search_path = self.base_path / prefix if prefix else self.base_path
        
        if search_path.is_dir():
            for file_path in search_path.rglob("*.dat"):
                relative_path = file_path.relative_to(self.base_path)
                files.append(str(relative_path))
        
        return files
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""        full_path = self.base_path / file_path
        
        if not full_path.exists():
            return {}
        
        stat = full_path.stat()
        return {
            "size_bytes": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "accessed_at": datetime.fromtimestamp(stat.st_atime)
        }


class CompressionManager:
    """Manages data compression and decompression"""    
    def __init__(self):
        self.logger = logging.getLogger("data_management.compression")
        self.supported_algorithms = self._get_supported_algorithms()
    
    def _get_supported_algorithms(self) -> Set[CompressionType]:
        """Get list of supported compression algorithms"""        supported = {CompressionType.NONE, CompressionType.GZIP}
        
        if HAS_LZ4:
            supported.add(CompressionType.LZ4)
        if HAS_ZSTD:
            supported.add(CompressionType.ZSTD)
        
        return supported
    
    async def compress_data(self, data: bytes, algorithm: CompressionType) -> bytes:
        """Compress data using specified algorithm"""        if algorithm == CompressionType.NONE:
            return data
        
        if algorithm not in self.supported_algorithms:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")
        
        start_time = time.time()
        original_size = len(data)
        
        try:
            if algorithm == CompressionType.GZIP:
                compressed_data = gzip.compress(data, compresslevel=6)
            elif algorithm == CompressionType.LZ4 and HAS_LZ4:
                compressed_data = lz4.frame.compress(data)
            elif algorithm == CompressionType.ZSTD and HAS_ZSTD:
                compressor = zstd.ZstdCompressor(level=3)
                compressed_data = compressor.compress(data)
            else:
                raise ValueError(f"Compression algorithm {algorithm} not available")
            
            compression_time = time.time() - start_time
            compression_ratio = len(compressed_data) / original_size
            
            self.logger.debug(f"Compressed {original_size} bytes to {len(compressed_data)} bytes "
                            f"using {algorithm.value} in {compression_time:.3f}s "
                            f"(ratio: {compression_ratio:.3f})")
            
            return compressed_data
            
        except Exception as e:
            self.logger.error(f"Compression failed with {algorithm.value}: {str(e)}")
            raise
    
    async def decompress_data(self, compressed_data: bytes, algorithm: CompressionType) -> bytes:
        """Decompress data using specified algorithm"""        if algorithm == CompressionType.NONE:
            return compressed_data
        
        if algorithm not in self.supported_algorithms:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")
        
        start_time = time.time()
        compressed_size = len(compressed_data)
        
        try:
            if algorithm == CompressionType.GZIP:
                data = gzip.decompress(compressed_data)
            elif algorithm == CompressionType.LZ4 and HAS_LZ4:
                data = lz4.frame.decompress(compressed_data)
            elif algorithm == CompressionType.ZSTD and HAS_ZSTD:
                decompressor = zstd.ZstdDecompressor()
                data = decompressor.decompress(compressed_data)
            else:
                raise ValueError(f"Decompression algorithm {algorithm} not available")
            
            decompression_time = time.time() - start_time
            
            self.logger.debug(f"Decompressed {compressed_size} bytes to {len(data)} bytes "
                            f"using {algorithm.value} in {decompression_time:.3f}s")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Decompression failed with {algorithm.value}: {str(e)}")
            raise
    
    def get_best_algorithm(self, data: bytes, target_ratio: float = 0.7) -> CompressionType:
        """Get the best compression algorithm for given data"""        if len(data) < 1024:  # Don't compress small data
            return CompressionType.NONE
        
        # Test available algorithms and pick the best one
        best_algorithm = CompressionType.GZIP
        best_ratio = 1.0
        
        for algorithm in self.supported_algorithms:
            if algorithm == CompressionType.NONE:
                continue
                
            try:
                # Test compress a small sample
                sample = data[:min(10240, len(data))]  # First 10KB
                compressed_sample = asyncio.run(self.compress_data(sample, algorithm))
                ratio = len(compressed_sample) / len(sample)
                
                if ratio < best_ratio and ratio <= target_ratio:
                    best_ratio = ratio
                    best_algorithm = algorithm
                    
            except Exception:
                continue
        
        return best_algorithm


class DataLifecycleManager:
    """Manages data lifecycle policies and operations"""    
    def __init__(self, storage_backend: BaseStorageBackend, 
                 compression_manager: CompressionManager,
                 metadata_db_path: str = None):
        self.storage_backend = storage_backend
        self.compression_manager = compression_manager
        self.metadata_db_path = metadata_db_path or "/var/data/observability/metadata.db"
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        self.logger = logging.getLogger("data_management.lifecycle")
        self._init_metadata_db()
        
        # Background task management
        self._lifecycle_task: Optional[asyncio.Task] = None
        self._running = False
        self._last_cleanup_time = datetime.utcnow()
        
        # Statistics
        self.stats = {
            "records_created": 0,
            "records_compressed": 0,
            "records_archived": 0,
            "records_deleted": 0,
            "bytes_stored": 0,
            "bytes_compressed": 0,
            "bytes_saved": 0
        }
    
    def _init_metadata_db(self):
        """Initialize metadata database"""        os.makedirs(os.path.dirname(self.metadata_db_path), exist_ok=True)
        
        with sqlite3.connect(self.metadata_db_path) as conn:
            conn.execute("""                CREATE TABLE IF NOT EXISTS data_records (
                    record_id TEXT PRIMARY KEY,
                    data_type TEXT NOT NULL,
                    storage_tier TEXT NOT NULL,
                    compression TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    modified_at TEXT NOT NULL,
                    accessed_at TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    compressed_size_bytes INTEGER DEFAULT 0,
                    file_path TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    checksum TEXT DEFAULT '',
                    retention_policy TEXT DEFAULT '',
                    tags TEXT DEFAULT ''
                )
            """)
            
            conn.execute("""                CREATE INDEX IF NOT EXISTS idx_data_type ON data_records(data_type)
            """)
            
            conn.execute("""                CREATE INDEX IF NOT EXISTS idx_created_at ON data_records(created_at)
            """)
            
            conn.execute("""                CREATE INDEX IF NOT EXISTS idx_status ON data_records(status)
            """)
            
            conn.commit()
    
    def register_retention_policy(self, policy: RetentionPolicy):
        """Register a retention policy"""        self.retention_policies[policy.policy_id] = policy
        self.logger.info(f"Registered retention policy: {policy.policy_id}")
    
    def get_default_retention_policies(self) -> List[RetentionPolicy]:
        """Get default retention policies for different data types"""        policies = [
            RetentionPolicy(
                policy_id="logs_standard",
                name="Standard Log Retention",
                description="Standard retention for application logs",
                data_types=[DataType.LOGS],
                hot_retention_days=3,
                warm_retention_days=15,
                cold_retention_days=90,
                frozen_retention_days=365,
                compression_after_days=1,
                preferred_compression=CompressionType.GZIP,
                purge_after_days=730
            ),
            RetentionPolicy(
                policy_id="metrics_standard",
                name="Standard Metrics Retention",
                description="Standard retention for metrics data",
                data_types=[DataType.METRICS],
                hot_retention_days=7,
                warm_retention_days=30,
                cold_retention_days=365,
                frozen_retention_days=1095,  # 3 years
                compression_after_days=7,
                preferred_compression=CompressionType.LZ4 if HAS_LZ4 else CompressionType.GZIP,
                purge_after_days=1825  # 5 years
            ),
            RetentionPolicy(
                policy_id="traces_standard",
                name="Standard Trace Retention", 
                description="Standard retention for distributed traces",
                data_types=[DataType.TRACES],
                hot_retention_days=2,
                warm_retention_days=7,
                cold_retention_days=30,
                frozen_retention_days=90,
                compression_after_days=1,
                preferred_compression=CompressionType.ZSTD if HAS_ZSTD else CompressionType.GZIP,
                purge_after_days=180
            ),
            RetentionPolicy(
                policy_id="analytics_standard",
                name="Standard Analytics Retention",
                description="Standard retention for analytics data",
                data_types=[DataType.ANALYTICS],
                hot_retention_days=14,
                warm_retention_days=60,
                cold_retention_days=730,  # 2 years
                frozen_retention_days=2555,  # 7 years
                compression_after_days=14,
                preferred_compression=CompressionType.ZSTD if HAS_ZSTD else CompressionType.GZIP,
                purge_after_days=3650  # 10 years
            ),
            RetentionPolicy(
                policy_id="security_logs",
                name="Security Log Retention",
                description="Extended retention for security-related logs",
                data_types=[DataType.LOGS],
                hot_retention_days=7,
                warm_retention_days=30,
                cold_retention_days=365,
                frozen_retention_days=2555,  # 7 years for compliance
                compression_after_days=1,
                preferred_compression=CompressionType.GZIP,
                purge_after_days=2555,
                tags={"security", "audit", "compliance"}
            )
        ]
        
        # Register all default policies
        for policy in policies:
            self.register_retention_policy(policy)
        
        return policies
    
    async def store_data(self, data_type: DataType, data: Union[bytes, str, Dict],
                        metadata: Dict[str, Any] = None, tags: Set[str] = None) -> str:
        """Store observability data with proper lifecycle management"""        record_id = str(uuid4())
        now = datetime.utcnow()
        metadata = metadata or {}
        tags = tags or set()
        
        # Convert data to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            data_bytes = json.dumps(data).encode('utf-8')
        else:
            data_bytes = data
        
        # Calculate checksum
        checksum = hashlib.sha256(data_bytes).hexdigest()
        
        # Find applicable retention policy
        record = DataRecord(
            record_id=record_id,
            data_type=data_type,
            storage_tier=StorageTier.HOT,
            compression=CompressionType.NONE,
            status=DataStatus.ACTIVE,
            created_at=now,
            modified_at=now,
            accessed_at=now,
            size_bytes=len(data_bytes),
            metadata=metadata,
            checksum=checksum,
            tags=tags
        )
        
        retention_policy_id = ""
        for policy_id, policy in self.retention_policies.items():
            if policy.applies_to_record(record):
                retention_policy_id = policy_id
                break
        
        record.retention_policy = retention_policy_id
        
        # Store data
        storage_metadata = {
            "tier": record.storage_tier.value,
            "data_type": data_type.value,
            "record_id": record_id
        }
        
        file_path = await self.storage_backend.store_data(record_id, data_bytes, storage_metadata)
        record.file_path = file_path
        
        # Save metadata to database
        await self._save_record_metadata(record)
        
        # Update statistics
        self.stats["records_created"] += 1
        self.stats["bytes_stored"] += len(data_bytes)
        
        self.logger.debug(f"Stored {data_type.value} record {record_id}, size: {len(data_bytes)} bytes")
        return record_id
    
    async def retrieve_data(self, record_id: str) -> Optional[bytes]:
        """Retrieve data by record ID"""        record = await self._get_record_metadata(record_id)
        if not record:
            return None
        
        if record.status == DataStatus.DELETED:
            return None
        
        # Retrieve data from storage
        data = await self.storage_backend.retrieve_data(record.file_path)
        
        # Decompress if needed
        if record.compression != CompressionType.NONE:
            data = await self.compression_manager.decompress_data(data, record.compression)
        
        # Update access time
        record.accessed_at = datetime.utcnow()
        await self._save_record_metadata(record)
        
        return data
    
    async def delete_data(self, record_id: str) -> bool:
        """Delete data by record ID"""        record = await self._get_record_metadata(record_id)
        if not record:
            return False
        
        # Mark as deleted first
        record.status = DataStatus.DELETED
        record.modified_at = datetime.utcnow()
        await self._save_record_metadata(record)
        
        # Actually delete from storage
        success = await self.storage_backend.delete_data(record.file_path)
        
        if success:
            self.stats["records_deleted"] += 1
            self.logger.debug(f"Deleted record {record_id}")
        
        return success
    
    async def _save_record_metadata(self, record: DataRecord):
        """Save record metadata to database"""        with sqlite3.connect(self.metadata_db_path) as conn:
            conn.execute("""                INSERT OR REPLACE INTO data_records (
                    record_id, data_type, storage_tier, compression, status,
                    created_at, modified_at, accessed_at, size_bytes, compressed_size_bytes,
                    file_path, metadata, checksum, retention_policy, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.record_id,
                record.data_type.value,
                record.storage_tier.value,
                record.compression.value,
                record.status.value,
                record.created_at.isoformat(),
                record.modified_at.isoformat(),
                record.accessed_at.isoformat(),
                record.size_bytes,
                record.compressed_size_bytes,
                record.file_path,
                json.dumps(record.metadata),
                record.checksum,
                record.retention_policy,
                json.dumps(list(record.tags))
            ))
            conn.commit()
    
    async def _get_record_metadata(self, record_id: str) -> Optional[DataRecord]:
        """Get record metadata from database"""        with sqlite3.connect(self.metadata_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""                SELECT * FROM data_records WHERE record_id = ?
            """, (record_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return DataRecord(
                record_id=row['record_id'],
                data_type=DataType(row['data_type']),
                storage_tier=StorageTier(row['storage_tier']),
                compression=CompressionType(row['compression']),
                status=DataStatus(row['status']),
                created_at=datetime.fromisoformat(row['created_at']),
                modified_at=datetime.fromisoformat(row['modified_at']),
                accessed_at=datetime.fromisoformat(row['accessed_at']),
                size_bytes=row['size_bytes'],
                compressed_size_bytes=row['compressed_size_bytes'],
                file_path=row['file_path'],
                metadata=json.loads(row['metadata'] or '{}'),
                checksum=row['checksum'],
                retention_policy=row['retention_policy'],
                tags=set(json.loads(row['tags'] or '[]'))
            )
    
    async def start_lifecycle_management(self, interval_hours: int = 1):
        """Start background lifecycle management"""        if self._running:
            return
        
        self._running = True
        self._lifecycle_task = asyncio.create_task(
            self._lifecycle_worker(interval_hours)
        )
        self.logger.info("Started data lifecycle management")
    
    async def stop_lifecycle_management(self):
        """Stop background lifecycle management"""        self._running = False
        if self._lifecycle_task:
            self._lifecycle_task.cancel()
            try:
                await self._lifecycle_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped data lifecycle management")
    
    async def _lifecycle_worker(self, interval_hours: int):
        """Background worker for lifecycle management"""        while self._running:
            try:
                await self._process_lifecycle_policies()
                await asyncio.sleep(interval_hours * 3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Lifecycle management error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _process_lifecycle_policies(self):
        """Process all lifecycle policies"""        self.logger.info("Processing data lifecycle policies")
        
        # Get all active records
        with sqlite3.connect(self.metadata_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""                SELECT record_id FROM data_records 
                WHERE status IN ('active', 'archived', 'compressed')
                ORDER BY created_at
            """)
            
            record_ids = [row['record_id'] for row in cursor.fetchall()]
        
        # Process each record
        processed = 0
        for record_id in record_ids:
            try:
                record = await self._get_record_metadata(record_id)
                if not record:
                    continue
                
                # Find applicable policy
                policy = None
                if record.retention_policy:
                    policy = self.retention_policies.get(record.retention_policy)
                
                if not policy:
                    # Find first applicable policy
                    for policy_obj in self.retention_policies.values():
                        if policy_obj.applies_to_record(record):
                            policy = policy_obj
                            break
                
                if not policy:
                    continue
                
                # Apply policy
                await self._apply_policy_to_record(record, policy)
                processed += 1
                
                # Yield control periodically
                if processed % 100 == 0:
                    await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error processing record {record_id}: {str(e)}")
        
        self.logger.info(f"Processed lifecycle policies for {processed} records")
        self._last_cleanup_time = datetime.utcnow()
    
    async def _apply_policy_to_record(self, record: DataRecord, policy: RetentionPolicy):
        """Apply lifecycle policy to a specific record"""        original_tier = record.storage_tier
        target_tier = policy.get_target_tier(record)
        
        # Handle deletion
        if target_tier == StorageTier.DELETED:
            await self.delete_data(record.record_id)
            return
        
        # Handle tier transitions
        if target_tier != record.storage_tier:
            await self._transition_storage_tier(record, target_tier)
        
        # Handle compression
        if (policy.should_compress(record) and 
            record.status == DataStatus.ACTIVE):
            await self._compress_record(record, policy.preferred_compression)
    
    async def _transition_storage_tier(self, record: DataRecord, target_tier: StorageTier):
        """Transition record to different storage tier"""        if target_tier == record.storage_tier:
            return
        
        # This would involve moving data between storage tiers
        # For filesystem backend, we might move files to different directories
        # For cloud storage, we might change storage classes
        
        record.storage_tier = target_tier
        record.modified_at = datetime.utcnow()
        
        if target_tier in [StorageTier.COLD, StorageTier.FROZEN]:
            record.status = DataStatus.ARCHIVED
            self.stats["records_archived"] += 1
        
        await self._save_record_metadata(record)
        
        self.logger.debug(f"Transitioned record {record.record_id} to {target_tier.value}")
    
    async def _compress_record(self, record: DataRecord, compression: CompressionType):
        """Compress a record"""        if record.compression != CompressionType.NONE:
            return  # Already compressed
        
        try:
            # Retrieve original data
            data = await self.storage_backend.retrieve_data(record.file_path)
            
            # Compress data
            compressed_data = await self.compression_manager.compress_data(data, compression)
            
            # Store compressed data (replace original)
            storage_metadata = {
                "tier": record.storage_tier.value,
                "data_type": record.data_type.value,
                "record_id": record.record_id,
                "compressed": True
            }
            
            new_file_path = await self.storage_backend.store_data(
                f"{record.record_id}_compressed", compressed_data, storage_metadata
            )
            
            # Delete original data
            await self.storage_backend.delete_data(record.file_path)
            
            # Update record metadata
            record.file_path = new_file_path
            record.compression = compression
            record.compressed_size_bytes = len(compressed_data)
            record.status = DataStatus.COMPRESSED
            record.modified_at = datetime.utcnow()
            
            await self._save_record_metadata(record)
            
            # Update statistics
            self.stats["records_compressed"] += 1
            self.stats["bytes_compressed"] += record.size_bytes
            self.stats["bytes_saved"] += record.size_bytes - len(compressed_data)
            
            compression_ratio = len(compressed_data) / record.size_bytes
            self.logger.debug(f"Compressed record {record.record_id} "
                            f"from {record.size_bytes} to {len(compressed_data)} bytes "
                            f"(ratio: {compression_ratio:.3f})")
            
        except Exception as e:
            self.logger.error(f"Failed to compress record {record.record_id}: {str(e)}")
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage usage statistics"""        with sqlite3.connect(self.metadata_db_path) as conn:
            # Total records by type
            cursor = conn.execute("""                SELECT data_type, COUNT(*) as count, SUM(size_bytes) as total_bytes,
                       SUM(compressed_size_bytes) as compressed_bytes
                FROM data_records 
                WHERE status != 'deleted'
                GROUP BY data_type
            """)
            
            by_type = {}
            for row in cursor.fetchall():
                by_type[row[0]] = {
                    "count": row[1],
                    "total_bytes": row[2],
                    "compressed_bytes": row[3] or 0
                }
            
            # Total records by tier
            cursor = conn.execute("""                SELECT storage_tier, COUNT(*) as count, SUM(size_bytes) as total_bytes
                FROM data_records 
                WHERE status != 'deleted'
                GROUP BY storage_tier
            """)
            
            by_tier = {}
            for row in cursor.fetchall():
                by_tier[row[0]] = {
                    "count": row[1],
                    "total_bytes": row[2]
                }
            
            # Total records by status
            cursor = conn.execute("""                SELECT status, COUNT(*) as count
                FROM data_records
                GROUP BY status
            """)
            
            by_status = {}
            for row in cursor.fetchall():
                by_status[row[0]] = row[1]
            
            # Overall statistics
            cursor = conn.execute("""                SELECT 
                    COUNT(*) as total_records,
                    SUM(size_bytes) as total_bytes,
                    SUM(compressed_size_bytes) as total_compressed_bytes,
                    MIN(created_at) as oldest_record,
                    MAX(created_at) as newest_record
                FROM data_records
                WHERE status != 'deleted'
            """)
            
            overall = cursor.fetchone()
            
            return {
                "overall": {
                    "total_records": overall[0] or 0,
                    "total_bytes": overall[1] or 0,
                    "total_compressed_bytes": overall[2] or 0,
                    "oldest_record": overall[3],
                    "newest_record": overall[4],
                    "compression_ratio": (overall[2] or 0) / (overall[1] or 1)
                },
                "by_data_type": by_type,
                "by_storage_tier": by_tier,
                "by_status": by_status,
                "lifecycle_stats": self.stats.copy(),
                "last_cleanup_time": self._last_cleanup_time.isoformat()
            }
    
    async def cleanup_expired_data(self, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up expired data according to retention policies"""        cleanup_stats = {
            "records_processed": 0,
            "records_deleted": 0,
            "bytes_freed": 0,
            "errors": []
        }
        
        # Find records that should be deleted
        with sqlite3.connect(self.metadata_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""                SELECT record_id FROM data_records
                WHERE status IN ('active', 'archived', 'compressed')
                ORDER BY created_at
            """)
            
            record_ids = [row['record_id'] for row in cursor.fetchall()]
        
        for record_id in record_ids:
            try:
                record = await self._get_record_metadata(record_id)
                if not record:
                    continue
                
                cleanup_stats["records_processed"] += 1
                
                # Find applicable policy
                policy = None
                if record.retention_policy:
                    policy = self.retention_policies.get(record.retention_policy)
                
                if not policy:
                    continue
                
                # Check if should be deleted
                target_tier = policy.get_target_tier(record)
                if target_tier == StorageTier.DELETED:
                    cleanup_stats["bytes_freed"] += record.size_bytes
                    
                    if not dry_run:
                        success = await self.delete_data(record_id)
                        if success:
                            cleanup_stats["records_deleted"] += 1
                    else:
                        cleanup_stats["records_deleted"] += 1
                
            except Exception as e:
                error_msg = f"Error processing record {record_id}: {str(e)}"
                cleanup_stats["errors"].append(error_msg)
                self.logger.error(error_msg)
        
        return cleanup_stats


class DataManager:
    """Main data management coordinator"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("data_management.manager")
        
        # Initialize components
        storage_config = self.config.get("storage", {"type": "filesystem"})
        
        if storage_config["type"] == "filesystem":
            self.storage_backend = FileSystemStorageBackend(storage_config)
        else:
            raise ValueError(f"Unsupported storage backend: {storage_config['type']}")
        
        self.compression_manager = CompressionManager()
        
        metadata_db_path = self.config.get("metadata_db_path", "/var/data/observability/metadata.db")
        self.lifecycle_manager = DataLifecycleManager(
            self.storage_backend,
            self.compression_manager,
            metadata_db_path
        )
        
        # Set up default retention policies
        self.lifecycle_manager.get_default_retention_policies()
        
        # Initialize statistics tracking
        self.stats = {
            "start_time": datetime.utcnow(),
            "operations": defaultdict(int),
            "errors": defaultdict(int)
        }
    
    async def start(self):
        """Start data management services"""        try:
            # Start lifecycle management
            cleanup_interval = self.config.get("cleanup_interval_hours", 1)
            await self.lifecycle_manager.start_lifecycle_management(cleanup_interval)
            
            self.logger.info("Data management started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start data management: {str(e)}")
            raise
    
    async def stop(self):
        """Stop data management services"""        try:
            await self.lifecycle_manager.stop_lifecycle_management()
            self.logger.info("Data management stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to stop data management: {str(e)}")
    
    async def store_observability_data(self, data_type: DataType, data: Any,
                                     metadata: Dict[str, Any] = None, 
                                     tags: Set[str] = None) -> str:
        """Store observability data"""        try:
            record_id = await self.lifecycle_manager.store_data(data_type, data, metadata, tags)
            self.stats["operations"]["store"] += 1
            return record_id
            
        except Exception as e:
            self.stats["errors"]["store"] += 1
            self.logger.error(f"Failed to store data: {str(e)}")
            raise
    
    async def retrieve_observability_data(self, record_id: str) -> Optional[bytes]:
        """Retrieve observability data"""        try:
            data = await self.lifecycle_manager.retrieve_data(record_id)
            self.stats["operations"]["retrieve"] += 1
            return data
            
        except Exception as e:
            self.stats["errors"]["retrieve"] += 1
            self.logger.error(f"Failed to retrieve data: {str(e)}")
            raise
    
    async def delete_observability_data(self, record_id: str) -> bool:
        """Delete observability data"""        try:
            success = await self.lifecycle_manager.delete_data(record_id)
            self.stats["operations"]["delete"] += 1
            return success
            
        except Exception as e:
            self.stats["errors"]["delete"] += 1
            self.logger.error(f"Failed to delete data: {str(e)}")
            return False
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive data management statistics"""        storage_stats = self.lifecycle_manager.get_storage_statistics()
        
        uptime = datetime.utcnow() - self.stats["start_time"]
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "operations": dict(self.stats["operations"]),
            "errors": dict(self.stats["errors"]),
            "storage": storage_stats,
            "compression": {
                "supported_algorithms": [alg.value for alg in self.compression_manager.supported_algorithms]
            },
            "retention_policies": {
                policy_id: {
                    "name": policy.name,
                    "description": policy.description,
                    "data_types": [dt.value for dt in policy.data_types],
                    "enabled": policy.enabled
                }
                for policy_id, policy in self.lifecycle_manager.retention_policies.items()
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics"""        return self.get_comprehensive_statistics()


# Factory function
def create_data_manager(config: Dict[str, Any] = None) -> DataManager:
    """Factory function to create data manager"""    return DataManager(config)


# Export data management components
__all__ = [
    "DataManager",
    "DataLifecycleManager", 
    "CompressionManager",
    "FileSystemStorageBackend",
    "BaseStorageBackend",
    "DataRecord",
    "RetentionPolicy",
    "RemediationAction",
    "DataType",
    "StorageTier",
    "CompressionType",
    "DataStatus",
    "create_data_manager"
]
