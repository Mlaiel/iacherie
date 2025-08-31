"""Analytics Storage - Advanced Data Warehousing and Storage
========================================================

Comprehensive storage system for analytics data with high-performance
querying, data warehousing, and real-time access capabilities.

Features:
- Multi-tier storage architecture
- Time-series data optimization
- Real-time and batch processing
- Data compression and archiving
- Advanced caching strategies

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: Proprietary - All rights reserved
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import pickle
import gzip
from pathlib import Path
import redis
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, insert, update, delete, func, and_, or_
from sqlalchemy.dialects.postgresql import insert as pg_insert

from ...core.database import get_database_session
from ...core.config import get_settings


class StorageTier(Enum):
    """Storage tier classification."""
    HOT = "hot"          # Real-time access, high performance
    WARM = "warm"        # Frequent access, good performance  
    COLD = "cold"        # Infrequent access, cost optimized
    ARCHIVE = "archive"  # Long-term storage, minimal access


class DataFormat(Enum):
    """Data storage formats."""
    JSON = "json"
    PARQUET = "parquet"
    CSV = "csv"
    BINARY = "binary"
    COMPRESSED = "compressed"


@dataclass
class StorageConfig:
    """Storage configuration settings."""
    tier: StorageTier
    retention_days: int
    compression_enabled: bool = True
    encryption_enabled: bool = True
    replication_factor: int = 2
    backup_enabled: bool = True


@dataclass
class StorageMetadata:
    """Metadata for stored analytics data."""
    data_id: str
    data_type: str
    storage_tier: StorageTier
    format: DataFormat
    size_bytes: int
    created_at: datetime
    last_accessed: datetime
    access_count: int
    expiry_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)


class AnalyticsStorage:
    """
    Advanced analytics data storage system.
    
    Provides multi-tier storage with automatic data lifecycle
    management, compression, and high-performance querying.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = get_settings()
        self._redis_client = None
        self._storage_configs = self._initialize_storage_configs()
        
    def _initialize_storage_configs(self) -> Dict[StorageTier, StorageConfig]:
        """Initialize storage tier configurations."""
        
        return {
            StorageTier.HOT: StorageConfig(
                tier=StorageTier.HOT,
                retention_days=7,
                compression_enabled=False,
                encryption_enabled=True,
                replication_factor=3,
                backup_enabled=True
            ),
            StorageTier.WARM: StorageConfig(
                tier=StorageTier.WARM,
                retention_days=30,
                compression_enabled=True,
                encryption_enabled=True,
                replication_factor=2,
                backup_enabled=True
            ),
            StorageTier.COLD: StorageConfig(
                tier=StorageTier.COLD,
                retention_days=365,
                compression_enabled=True,
                encryption_enabled=True,
                replication_factor=1,
                backup_enabled=False
            ),
            StorageTier.ARCHIVE: StorageConfig(
                tier=StorageTier.ARCHIVE,
                retention_days=2555,  # 7 years
                compression_enabled=True,
                encryption_enabled=True,
                replication_factor=1,
                backup_enabled=False
            )
        }
        
    async def store_analytics_data(
        self,
        data: Any,
        data_type: str,
        data_id: Optional[str] = None,
        tier: StorageTier = StorageTier.HOT,
        tags: Optional[List[str]] = None,
        expiry_hours: Optional[int] = None
    ) -> str:
        """
        Store analytics data with automatic tier management.
        
        Args:
            data: Data to store
            data_type: Type classification of data
            data_id: Optional custom data identifier
            tier: Storage tier for the data
            tags: Optional tags for data categorization
            expiry_hours: Optional expiry time in hours
            
        Returns:
            Data identifier for retrieval
        """
        try:
            if not data_id:
                data_id = f"{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                
            # Determine optimal storage format
            storage_format = self._determine_storage_format(data, tier)
            
            # Serialize and compress data if needed
            serialized_data = await self._serialize_data(data, storage_format, tier)
            
            # Calculate expiry date
            expiry_date = None
            if expiry_hours:
                expiry_date = datetime.now() + timedelta(hours=expiry_hours)
                
            # Create metadata
            metadata = StorageMetadata(
                data_id=data_id,
                data_type=data_type,
                storage_tier=tier,
                format=storage_format,
                size_bytes=len(serialized_data) if isinstance(serialized_data, bytes) else len(str(serialized_data)),
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                expiry_date=expiry_date,
                tags=tags or []
            )
            
            # Store data based on tier
            if tier == StorageTier.HOT:
                await self._store_hot_data(data_id, serialized_data, metadata)
            elif tier == StorageTier.WARM:
                await self._store_warm_data(data_id, serialized_data, metadata)
            elif tier == StorageTier.COLD:
                await self._store_cold_data(data_id, serialized_data, metadata)
            else:  # ARCHIVE
                await self._store_archive_data(data_id, serialized_data, metadata)
                
            # Store metadata
            await self._store_metadata(metadata)
            
            self.logger.info(f"Stored analytics data: {data_id} in {tier.value} tier")
            return data_id
            
        except Exception as e:
            self.logger.error(f"Error storing analytics data: {e}")
            raise
            
    def _determine_storage_format(self, data: Any, tier: StorageTier) -> DataFormat:
        """Determine optimal storage format based on data type and tier."""
        
        if isinstance(data, (dict, list)):
            if tier in [StorageTier.COLD, StorageTier.ARCHIVE]:
                return DataFormat.COMPRESSED
            return DataFormat.JSON
        elif isinstance(data, pd.DataFrame):
            return DataFormat.PARQUET
        elif isinstance(data, (bytes, bytearray)):
            return DataFormat.BINARY
        else:
            return DataFormat.JSON
            
    async def _serialize_data(
        self,
        data: Any,
        format: DataFormat,
        tier: StorageTier
    ) -> Union[str, bytes]:
        """Serialize data according to format and tier requirements."""
        
        config = self._storage_configs[tier]
        
        if format == DataFormat.JSON:
            serialized = json.dumps(data, default=str, ensure_ascii=False)
            if config.compression_enabled:
                serialized = gzip.compress(serialized.encode('utf-8'))
                
        elif format == DataFormat.PARQUET:
            if isinstance(data, pd.DataFrame):
                buffer = data.to_parquet(compression='gzip' if config.compression_enabled else None)
                serialized = buffer
            else:
                # Convert to DataFrame first
                df = pd.DataFrame(data)
                serialized = df.to_parquet(compression='gzip' if config.compression_enabled else None)
                
        elif format == DataFormat.BINARY:
            serialized = pickle.dumps(data)
            if config.compression_enabled:
                serialized = gzip.compress(serialized)
                
        elif format == DataFormat.COMPRESSED:
            json_data = json.dumps(data, default=str, ensure_ascii=False)
            serialized = gzip.compress(json_data.encode('utf-8'))
            
        else:
            # Default to JSON
            serialized = json.dumps(data, default=str, ensure_ascii=False)
            
        return serialized
        
    async def _store_hot_data(
        self,
        data_id: str,
        data: Union[str, bytes],
        metadata: StorageMetadata
    ) -> None:
        """Store data in hot tier (Redis for fast access)."""
        
        redis_client = await self._get_redis_client()
        
        # Store in Redis with TTL
        ttl_seconds = 7 * 24 * 3600  # 7 days for hot data
        
        if metadata.expiry_date:
            ttl_seconds = min(
                ttl_seconds,
                int((metadata.expiry_date - datetime.now()).total_seconds())
            )
            
        await redis_client.setex(
            f"analytics:hot:{data_id}",
            ttl_seconds,
            data
        )
        
    async def _store_warm_data(
        self,
        data_id: str,
        data: Union[str, bytes],
        metadata: StorageMetadata
    ) -> None:
        """Store data in warm tier (Database with indexing)."""
        
        async with get_database_session() as session:
            # Store in analytics_data table
            query = pg_insert(AnalyticsData).values(
                data_id=data_id,
                data_type=metadata.data_type,
                data_content=data,
                storage_tier=metadata.storage_tier.value,
                format=metadata.format.value,
                size_bytes=metadata.size_bytes,
                created_at=metadata.created_at,
                expiry_date=metadata.expiry_date
            )
            
            # Use ON CONFLICT for upsert behavior
            query = query.on_conflict_do_update(
                index_elements=['data_id'],
                set_=dict(
                    data_content=query.excluded.data_content,
                    size_bytes=query.excluded.size_bytes,
                    updated_at=datetime.now()
                )
            )
            
            await session.execute(query)
            await session.commit()
            
    async def _store_cold_data(
        self,
        data_id: str,
        data: Union[str, bytes],
        metadata: StorageMetadata
    ) -> None:
        """Store data in cold tier (File system with compression)."""
        
        # Create cold storage directory
        cold_storage_path = Path("storage/cold")
        cold_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Organize by date for better management
        date_path = cold_storage_path / datetime.now().strftime("%Y/%m/%d")
        date_path.mkdir(parents=True, exist_ok=True)
        
        # Store file
        file_extension = ".gz" if metadata.format == DataFormat.COMPRESSED else ".dat"
        file_path = date_path / f"{data_id}{file_extension}"
        
        if isinstance(data, bytes):
            with open(file_path, 'wb') as f:
                f.write(data)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
                
        # Update metadata with file path
        metadata.tags.append(f"file_path:{str(file_path)}")
        
    async def _store_archive_data(
        self,
        data_id: str,
        data: Union[str, bytes],
        metadata: StorageMetadata
    ) -> None:
        """Store data in archive tier (Long-term storage)."""
        
        # Create archive storage directory
        archive_path = Path("storage/archive")
        archive_path.mkdir(parents=True, exist_ok=True)
        
        # Organize by year/month for archive management
        date_path = archive_path / datetime.now().strftime("%Y/%m")
        date_path.mkdir(parents=True, exist_ok=True)
        
        # Always compress archive data
        if not isinstance(data, bytes):
            data = gzip.compress(data.encode('utf-8'))
        elif metadata.format != DataFormat.COMPRESSED:
            data = gzip.compress(data)
            
        file_path = date_path / f"{data_id}.archive.gz"
        
        with open(file_path, 'wb') as f:
            f.write(data)
            
        metadata.tags.append(f"archive_path:{str(file_path)}")
        
    async def _store_metadata(self, metadata: StorageMetadata) -> None:
        """Store metadata in database for efficient querying."""
        
        async with get_database_session() as session:
            query = pg_insert(AnalyticsMetadata).values(
                data_id=metadata.data_id,
                data_type=metadata.data_type,
                storage_tier=metadata.storage_tier.value,
                format=metadata.format.value,
                size_bytes=metadata.size_bytes,
                created_at=metadata.created_at,
                last_accessed=metadata.last_accessed,
                access_count=metadata.access_count,
                expiry_date=metadata.expiry_date,
                tags=json.dumps(metadata.tags)
            )
            
            query = query.on_conflict_do_update(
                index_elements=['data_id'],
                set_=dict(
                    last_accessed=query.excluded.last_accessed,
                    access_count=query.excluded.access_count,
                    updated_at=datetime.now()
                )
            )
            
            await session.execute(query)
            await session.commit()
            
    async def retrieve_analytics_data(
        self,
        data_id: str,
        update_access_stats: bool = True
    ) -> Optional[Any]:
        """
        Retrieve analytics data by ID with automatic tier management.
        
        Args:
            data_id: Data identifier
            update_access_stats: Whether to update access statistics
            
        Returns:
            Retrieved data or None if not found
        """
        try:
            # Get metadata first
            metadata = await self._get_metadata(data_id)
            if not metadata:
                return None
                
            # Check if data has expired
            if metadata.expiry_date and datetime.now() > metadata.expiry_date:
                await self._delete_expired_data(data_id)
                return None
                
            # Retrieve data based on storage tier
            data = None
            
            if metadata.storage_tier == StorageTier.HOT:
                data = await self._retrieve_hot_data(data_id)
            elif metadata.storage_tier == StorageTier.WARM:
                data = await self._retrieve_warm_data(data_id)
            elif metadata.storage_tier == StorageTier.COLD:
                data = await self._retrieve_cold_data(data_id, metadata)
            else:  # ARCHIVE
                data = await self._retrieve_archive_data(data_id, metadata)
                
            if data is not None:
                # Deserialize data
                deserialized_data = await self._deserialize_data(
                    data, metadata.format, metadata.storage_tier
                )
                
                # Update access statistics
                if update_access_stats:
                    await self._update_access_stats(data_id)
                    
                # Consider tier promotion based on access patterns
                await self._consider_tier_promotion(data_id, metadata)
                
                return deserialized_data
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving analytics data {data_id}: {e}")
            raise
            
    async def _get_metadata(self, data_id: str) -> Optional[StorageMetadata]:
        """Retrieve metadata for data ID."""
        
        async with get_database_session() as session:
            query = select(AnalyticsMetadata).where(
                AnalyticsMetadata.data_id == data_id
            )
            result = await session.execute(query)
            row = result.first()
            
            if row:
                return StorageMetadata(
                    data_id=row.data_id,
                    data_type=row.data_type,
                    storage_tier=StorageTier(row.storage_tier),
                    format=DataFormat(row.format),
                    size_bytes=row.size_bytes,
                    created_at=row.created_at,
                    last_accessed=row.last_accessed,
                    access_count=row.access_count,
                    expiry_date=row.expiry_date,
                    tags=json.loads(row.tags) if row.tags else []
                )
                
            return None
            
    async def _retrieve_hot_data(self, data_id: str) -> Optional[Union[str, bytes]]:
        """Retrieve data from hot tier (Redis)."""
        
        redis_client = await self._get_redis_client()
        data = await redis_client.get(f"analytics:hot:{data_id}")
        return data
        
    async def _retrieve_warm_data(self, data_id: str) -> Optional[Union[str, bytes]]:
        """Retrieve data from warm tier (Database)."""
        
        async with get_database_session() as session:
            query = select(AnalyticsData.data_content).where(
                AnalyticsData.data_id == data_id
            )
            result = await session.execute(query)
            row = result.first()
            
            return row.data_content if row else None
            
    async def _retrieve_cold_data(
        self,
        data_id: str,
        metadata: StorageMetadata
    ) -> Optional[Union[str, bytes]]:
        """Retrieve data from cold tier (File system)."""
        
        # Find file path from metadata tags
        file_path = None
        for tag in metadata.tags:
            if tag.startswith("file_path:"):
                file_path = Path(tag.split(":", 1)[1])
                break
                
        if not file_path or not file_path.exists():
            return None
            
        # Read file
        if metadata.format == DataFormat.COMPRESSED:
            with open(file_path, 'rb') as f:
                return f.read()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
    async def _retrieve_archive_data(
        self,
        data_id: str,
        metadata: StorageMetadata
    ) -> Optional[Union[str, bytes]]:
        """Retrieve data from archive tier."""
        
        # Find archive path from metadata tags
        archive_path = None
        for tag in metadata.tags:
            if tag.startswith("archive_path:"):
                archive_path = Path(tag.split(":", 1)[1])
                break
                
        if not archive_path or not archive_path.exists():
            return None
            
        # Read compressed archive file
        with open(archive_path, 'rb') as f:
            return f.read()
            
    async def _deserialize_data(
        self,
        data: Union[str, bytes],
        format: DataFormat,
        tier: StorageTier
    ) -> Any:
        """Deserialize data according to format and tier."""
        
        config = self._storage_configs[tier]
        
        try:
            if format == DataFormat.JSON:
                if isinstance(data, bytes):
                    if config.compression_enabled:
                        data = gzip.decompress(data).decode('utf-8')
                    else:
                        data = data.decode('utf-8')
                return json.loads(data)
                
            elif format == DataFormat.PARQUET:
                if isinstance(data, bytes):
                    return pd.read_parquet(data)
                else:
                    return pd.read_parquet(data.encode('utf-8'))
                    
            elif format == DataFormat.BINARY:
                if config.compression_enabled:
                    data = gzip.decompress(data)
                return pickle.loads(data)
                
            elif format == DataFormat.COMPRESSED:
                if isinstance(data, bytes):
                    json_data = gzip.decompress(data).decode('utf-8')
                else:
                    json_data = data
                return json.loads(json_data)
                
            else:
                # Default JSON handling
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return json.loads(data)
                
        except Exception as e:
            self.logger.error(f"Error deserializing data: {e}")
            return data  # Return raw data if deserialization fails
            
    async def _update_access_stats(self, data_id: str) -> None:
        """Update access statistics for data."""
        
        async with get_database_session() as session:
            query = update(AnalyticsMetadata).where(
                AnalyticsMetadata.data_id == data_id
            ).values(
                last_accessed=datetime.now(),
                access_count=AnalyticsMetadata.access_count + 1
            )
            
            await session.execute(query)
            await session.commit()
            
    async def _consider_tier_promotion(
        self,
        data_id: str,
        metadata: StorageMetadata
    ) -> None:
        """Consider promoting data to higher tier based on access patterns."""
        
        # Simple promotion logic based on access frequency
        access_frequency = metadata.access_count / max(
            (datetime.now() - metadata.created_at).days, 1
        )
        
        promote_to_tier = None
        
        if metadata.storage_tier == StorageTier.COLD and access_frequency > 5:
            promote_to_tier = StorageTier.WARM
        elif metadata.storage_tier == StorageTier.WARM and access_frequency > 20:
            promote_to_tier = StorageTier.HOT
            
        if promote_to_tier:
            await self._promote_data_tier(data_id, promote_to_tier)
            
    async def _promote_data_tier(self, data_id: str, new_tier: StorageTier) -> None:
        """Promote data to higher performance tier."""
        
        try:
            # Retrieve current data
            data = await self.retrieve_analytics_data(data_id, update_access_stats=False)
            
            if data is not None:
                # Store in new tier
                await self.store_analytics_data(
                    data=data,
                    data_type="promoted_data",
                    data_id=data_id,
                    tier=new_tier
                )
                
                self.logger.info(f"Promoted data {data_id} to {new_tier.value} tier")
                
        except Exception as e:
            self.logger.error(f"Error promoting data tier: {e}")
            
    async def _delete_expired_data(self, data_id: str) -> None:
        """Delete expired data from all storage tiers."""
        
        try:
            # Get metadata to determine storage locations
            metadata = await self._get_metadata(data_id)
            
            if metadata:
                # Delete from appropriate tier
                if metadata.storage_tier == StorageTier.HOT:
                    redis_client = await self._get_redis_client()
                    await redis_client.delete(f"analytics:hot:{data_id}")
                    
                elif metadata.storage_tier == StorageTier.WARM:
                    async with get_database_session() as session:
                        query = delete(AnalyticsData).where(
                            AnalyticsData.data_id == data_id
                        )
                        await session.execute(query)
                        await session.commit()
                        
                else:  # COLD or ARCHIVE
                    # Delete files from filesystem
                    for tag in metadata.tags:
                        if tag.startswith(("file_path:", "archive_path:")):
                            file_path = Path(tag.split(":", 1)[1])
                            if file_path.exists():
                                file_path.unlink()
                                
                # Delete metadata
                async with get_database_session() as session:
                    query = delete(AnalyticsMetadata).where(
                        AnalyticsMetadata.data_id == data_id
                    )
                    await session.execute(query)
                    await session.commit()
                    
                self.logger.info(f"Deleted expired data: {data_id}")
                
        except Exception as e:
            self.logger.error(f"Error deleting expired data: {e}")
            
    async def _get_redis_client(self):
        """Get Redis client for hot tier storage."""
        
        if not self._redis_client:
            import redis.asyncio as redis
            self._redis_client = redis.Redis(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                decode_responses=False  # Handle binary data
            )
            
        return self._redis_client
        
    async def query_analytics_data(
        self,
        data_type: Optional[str] = None,
        tier: Optional[StorageTier] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query analytics data with flexible filtering.
        
        Args:
            data_type: Filter by data type
            tier: Filter by storage tier
            tags: Filter by tags
            start_date: Filter by creation date start
            end_date: Filter by creation date end
            limit: Maximum results to return
            
        Returns:
            List of matching data metadata
        """
        try:
            async with get_database_session() as session:
                query = select(AnalyticsMetadata)
                
                # Apply filters
                conditions = []
                
                if data_type:
                    conditions.append(AnalyticsMetadata.data_type == data_type)
                    
                if tier:
                    conditions.append(AnalyticsMetadata.storage_tier == tier.value)
                    
                if start_date:
                    conditions.append(AnalyticsMetadata.created_at >= start_date)
                    
                if end_date:
                    conditions.append(AnalyticsMetadata.created_at <= end_date)
                    
                if tags:
                    for tag in tags:
                        conditions.append(AnalyticsMetadata.tags.contains(tag))
                        
                if conditions:
                    query = query.where(and_(*conditions))
                    
                query = query.order_by(AnalyticsMetadata.created_at.desc()).limit(limit)
                
                result = await session.execute(query)
                rows = result.fetchall()
                
                # Convert to dictionaries
                results = []
                for row in rows:
                    results.append({
                        'data_id': row.data_id,
                        'data_type': row.data_type,
                        'storage_tier': row.storage_tier,
                        'format': row.format,
                        'size_bytes': row.size_bytes,
                        'created_at': row.created_at.isoformat(),
                        'last_accessed': row.last_accessed.isoformat(),
                        'access_count': row.access_count,
                        'expiry_date': row.expiry_date.isoformat() if row.expiry_date else None,
                        'tags': json.loads(row.tags) if row.tags else []
                    })
                    
                return results
                
        except Exception as e:
            self.logger.error(f"Error querying analytics data: {e}")
            raise
            
    async def cleanup_expired_data(self) -> int:
        """Clean up all expired data across tiers."""
        
        try:
            cleanup_count = 0
            
            # Find expired data
            async with get_database_session() as session:
                query = select(AnalyticsMetadata.data_id).where(
                    and_(
                        AnalyticsMetadata.expiry_date.is_not(None),
                        AnalyticsMetadata.expiry_date <= datetime.now()
                    )
                )
                
                result = await session.execute(query)
                expired_ids = [row.data_id for row in result.fetchall()]
                
            # Delete expired data
            for data_id in expired_ids:
                await self._delete_expired_data(data_id)
                cleanup_count += 1
                
            self.logger.info(f"Cleaned up {cleanup_count} expired data entries")
            return cleanup_count
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0


class MetricsWarehouse:
    """
    Data warehouse optimized for analytics metrics with
    advanced aggregation and analytical query capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def store_aggregated_metrics(
        self,
        metrics: List[Dict[str, Any]],
        aggregation_level: str = "daily"
    ) -> None:
        """Store pre-aggregated metrics for fast querying."""
        
        try:
            async with get_database_session() as session:
                for metric in metrics:
                    query = pg_insert(AggregatedMetrics).values(
                        metric_name=metric['name'],
                        metric_value=metric['value'],
                        aggregation_level=aggregation_level,
                        aggregation_date=metric.get('date', datetime.now().date()),
                        metadata=json.dumps(metric.get('metadata', {})),
                        created_at=datetime.now()
                    )
                    
                    # Upsert behavior
                    query = query.on_conflict_do_update(
                        index_elements=['metric_name', 'aggregation_level', 'aggregation_date'],
                        set_=dict(
                            metric_value=query.excluded.metric_value,
                            metadata=query.excluded.metadata,
                            updated_at=datetime.now()
                        )
                    )
                    
                    await session.execute(query)
                    
                await session.commit()
                
            self.logger.info(f"Stored {len(metrics)} aggregated metrics")
            
        except Exception as e:
            self.logger.error(f"Error storing aggregated metrics: {e}")
            raise


class TimeSeriesStore:
    """
    Specialized time-series storage for high-frequency analytics data
    with efficient compression and querying capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def store_time_series_data(
        self,
        metric_name: str,
        timestamp: datetime,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Store time-series data point."""
        
        try:
            async with get_database_session() as session:
                query = insert(TimeSeriesData).values(
                    metric_name=metric_name,
                    timestamp=timestamp,
                    value=value,
                    tags=json.dumps(tags) if tags else None,
                    created_at=datetime.now()
                )
                
                await session.execute(query)
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing time series data: {e}")
            raise
            
    async def query_time_series(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        aggregation: Optional[str] = None,
        interval: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query time-series data with optional aggregation."""
        
        try:
            async with get_database_session() as session:
                if aggregation and interval:
                    # Aggregated query
                    if aggregation == "avg":
                        agg_func = func.avg(TimeSeriesData.value)
                    elif aggregation == "sum":
                        agg_func = func.sum(TimeSeriesData.value)
                    elif aggregation == "max":
                        agg_func = func.max(TimeSeriesData.value)
                    elif aggregation == "min":
                        agg_func = func.min(TimeSeriesData.value)
                    else:
                        agg_func = func.avg(TimeSeriesData.value)
                        
                    # Group by time intervals
                    time_bucket = func.date_trunc(interval, TimeSeriesData.timestamp)
                    
                    query = select(
                        time_bucket.label('time_bucket'),
                        agg_func.label('value')
                    ).where(
                        and_(
                            TimeSeriesData.metric_name == metric_name,
                            TimeSeriesData.timestamp >= start_time,
                            TimeSeriesData.timestamp <= end_time
                        )
                    ).group_by(time_bucket).order_by(time_bucket)
                    
                else:
                    # Raw data query
                    query = select(
                        TimeSeriesData.timestamp,
                        TimeSeriesData.value,
                        TimeSeriesData.tags
                    ).where(
                        and_(
                            TimeSeriesData.metric_name == metric_name,
                            TimeSeriesData.timestamp >= start_time,
                            TimeSeriesData.timestamp <= end_time
                        )
                    ).order_by(TimeSeriesData.timestamp)
                    
                result = await session.execute(query)
                rows = result.fetchall()
                
                # Convert to list of dictionaries
                data = []
                for row in rows:
                    if aggregation:
                        data.append({
                            'timestamp': row.time_bucket.isoformat(),
                            'value': float(row.value)
                        })
                    else:
                        data.append({
                            'timestamp': row.timestamp.isoformat(),
                            'value': float(row.value),
                            'tags': json.loads(row.tags) if row.tags else None
                        })
                        
                return data
                
        except Exception as e:
            self.logger.error(f"Error querying time series: {e}")
            raise


class CacheManager:
    """
    Advanced caching system for frequently accessed analytics data
    with intelligent cache warming and eviction policies.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
    async def get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Retrieve data from cache."""
        
        try:
            redis_client = redis.Redis()  # Use sync Redis for caching
            
            cached_data = redis_client.get(f"cache:{cache_key}")
            
            if cached_data:
                self._cache_stats['hits'] += 1
                return pickle.loads(cached_data)
            else:
                self._cache_stats['misses'] += 1
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving cached data: {e}")
            return None
            
    async def set_cached_data(
        self,
        cache_key: str,
        data: Any,
        ttl_seconds: int = 3600
    ) -> None:
        """Store data in cache with TTL."""
        
        try:
            redis_client = redis.Redis()
            
            serialized_data = pickle.dumps(data)
            redis_client.setex(f"cache:{cache_key}", ttl_seconds, serialized_data)
            
        except Exception as e:
            self.logger.error(f"Error setting cached data: {e}")
            
    async def invalidate_cache(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        
        try:
            redis_client = redis.Redis()
            
            keys = redis_client.keys(f"cache:{pattern}")
            if keys:
                deleted_count = redis_client.delete(*keys)
                self._cache_stats['evictions'] += deleted_count
                return deleted_count
                
            return 0
            
        except Exception as e:
            self.logger.error(f"Error invalidating cache: {e}")
            return 0
            
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        
        total_requests = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = (self._cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._cache_stats,
            'hit_rate_percentage': hit_rate,
            'total_requests': total_requests
        }
