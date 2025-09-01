"""Storage interfaces for IA Influencer Agent.

Defines interfaces for data storage, database operations,
caching, file system management and backup operations.

Author: Fahed Mlaiel <mlaiel@live.de>
© 2025 - All rights reserved. Unauthorized use prohibited.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple, Generator
from datetime import datetime
from enum import Enum
import asyncio


class StorageType(Enum):
    """Storage system types."""
    RELATIONAL_DB = "relational_db"
    DOCUMENT_DB = "document_db"
    KEY_VALUE_STORE = "key_value_store"
    OBJECT_STORAGE = "object_storage"
    VECTOR_DB = "vector_db"
    TIME_SERIES_DB = "time_series_db"
    GRAPH_DB = "graph_db"


class DatabaseType(Enum):
    """Database system types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    CASSANDRA = "cassandra"
    NEO4J = "neo4j"


class CacheStrategy(Enum):
    """Cache management strategies."""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"


class BackupStrategy(Enum):
    """Backup strategies."""
    AUTOMATED = "automated"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    CONTINUOUS = "continuous"
    ON_DEMAND = "on_demand"


class BackupType(Enum):
    """Backup operation types."""
    FULL_BACKUP = "full_backup"
    INCREMENTAL_BACKUP = "incremental_backup"
    DIFFERENTIAL_BACKUP = "differential_backup"
    SNAPSHOT = "snapshot"


class StorageInterface(ABC):
    """Core interface for storage operations."""
    
    @abstractmethod
    async def store_data(
        self,
        data: Union[Dict[str, Any], bytes, str],
        storage_key: str,
        storage_type: StorageType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store data in specified storage system.
        
        Args:
            data: Data to store
            storage_key: Unique storage identifier
            storage_type: Type of storage system to use
            metadata: Optional metadata for the stored data
            
        Returns:
            Storage operation result ID
        """
        pass
    
    @abstractmethod
    async def retrieve_data(
        self,
        storage_key: str,
        storage_type: StorageType
    ) -> Union[Dict[str, Any], bytes, str, None]:
        """Retrieve data from storage system."""
        pass
    
    @abstractmethod
    async def update_data(
        self,
        storage_key: str,
        updated_data: Union[Dict[str, Any], bytes, str],
        storage_type: StorageType
    ) -> bool:
        """Update existing data in storage system."""
        pass
    
    @abstractmethod
    async def delete_data(
        self,
        storage_key: str,
        storage_type: StorageType,
        hard_delete: bool = False
    ) -> bool:
        """Delete data from storage system."""
        pass
    
    @abstractmethod
    async def list_storage_items(
        self,
        storage_type: StorageType,
        filter_criteria: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List items in storage with optional filtering."""
        pass
    
    @abstractmethod
    async def get_storage_statistics(
        self,
        storage_type: StorageType
    ) -> Dict[str, Any]:
        """Get storage usage statistics and metrics."""
        pass


class DatabaseInterface(ABC):
    """Interface for database operations."""
    
    @abstractmethod
    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute database query with parameters.
        
        Args:
            query: SQL or NoSQL query string
            parameters: Query parameters for safe execution
            database_name: Specific database to query
            
        Returns:
            Query results as list of dictionaries
        """
        pass
    
    @abstractmethod
    async def execute_transaction(
        self,
        operations: List[Dict[str, Any]],
        database_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute multiple operations as atomic transaction."""
        pass
    
    @abstractmethod
    async def create_index(
        self,
        table_name: str,
        index_definition: Dict[str, Any],
        database_name: Optional[str] = None
    ) -> bool:
        """Create database index for performance optimization."""
        pass
    
    @abstractmethod
    async def optimize_database_performance(
        self,
        optimization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize database performance based on usage patterns."""
        pass
    
    @abstractmethod
    async def backup_database(
        self,
        backup_config: Dict[str, Any]
    ) -> str:
        """Create database backup with specified configuration."""
        pass
    
    @abstractmethod
    async def restore_database(
        self,
        backup_id: str,
        restore_config: Dict[str, Any]
    ) -> bool:
        """Restore database from backup."""
        pass


class CacheInterface(ABC):
    """Interface for caching operations."""
    
    @abstractmethod
    async def cache_data(
        self,
        cache_key: str,
        data: Any,
        ttl: Optional[int] = None,
        strategy: CacheStrategy = CacheStrategy.LRU
    ) -> bool:
        """
        Cache data with specified strategy.
        
        Args:
            cache_key: Unique cache identifier
            data: Data to cache
            ttl: Time to live in seconds
            strategy: Cache management strategy
            
        Returns:
            Success status of cache operation
        """
        pass
    
    @abstractmethod
    async def get_cached_data(
        self,
        cache_key: str
    ) -> Optional[Any]:
        """Retrieve data from cache."""
        pass
    
    @abstractmethod
    async def invalidate_cache(
        self,
        cache_key: Optional[str] = None,
        pattern: Optional[str] = None
    ) -> bool:
        """Invalidate cache entries by key or pattern."""
        pass
    
    @abstractmethod
    async def update_cache(
        self,
        cache_key: str,
        updated_data: Any,
        extend_ttl: bool = False
    ) -> bool:
        """Update cached data and optionally extend TTL."""
        pass
    
    @abstractmethod
    async def get_cache_statistics(
        self
    ) -> Dict[str, Any]:
        """Get cache performance statistics."""
        pass
    
    @abstractmethod
    async def configure_cache_policies(
        self,
        policy_config: Dict[str, Any]
    ) -> bool:
        """Configure cache management policies."""
        pass


class FileSystemInterface(ABC):
    """Interface for file system operations."""
    
    @abstractmethod
    async def upload_file(
        self,
        file_data: bytes,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to storage system.
        
        Args:
            file_data: File binary data
            file_path: Target file path
            metadata: File metadata and properties
            
        Returns:
            Upload result with file information
        """
        pass
    
    @abstractmethod
    async def download_file(
        self,
        file_path: str
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Download file and metadata from storage."""
        pass
    
    @abstractmethod
    async def delete_file(
        self,
        file_path: str,
        permanent: bool = False
    ) -> bool:
        """Delete file from storage system."""
        pass
    
    @abstractmethod
    async def move_file(
        self,
        source_path: str,
        destination_path: str
    ) -> bool:
        """Move file to new location."""
        pass
    
    @abstractmethod
    async def get_file_metadata(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """Get file metadata and properties."""
        pass
    
    @abstractmethod
    async def list_directory(
        self,
        directory_path: str,
        recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """List files and subdirectories in directory."""
        pass
    
    @abstractmethod
    async def create_presigned_url(
        self,
        file_path: str,
        operation: str,
        expiration_seconds: int = 3600
    ) -> str:
        """Create presigned URL for file access."""
        pass


class BackupInterface(ABC):
    """Interface for backup and recovery operations."""
    
    @abstractmethod
    async def create_backup(
        self,
        backup_source: str,
        backup_type: BackupType,
        backup_config: Dict[str, Any]
    ) -> str:
        """
        Create backup of specified data source.
        
        Args:
            backup_source: Source to backup (database, files, etc.)
            backup_type: Type of backup operation
            backup_config: Backup configuration settings
            
        Returns:
            Backup operation ID
        """
        pass
    
    @abstractmethod
    async def restore_from_backup(
        self,
        backup_id: str,
        restore_target: str,
        restore_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Restore data from backup."""
        pass
    
    @abstractmethod
    async def schedule_backup(
        self,
        backup_schedule: Dict[str, Any],
        backup_targets: List[str]
    ) -> str:
        """Schedule automated backup operations."""
        pass
    
    @abstractmethod
    async def verify_backup_integrity(
        self,
        backup_id: str
    ) -> Dict[str, Any]:
        """Verify backup data integrity and completeness."""
        pass
    
    @abstractmethod
    async def list_available_backups(
        self,
        source_filter: Optional[str] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[Dict[str, Any]]:
        """List available backups with optional filtering."""
        pass
    
    @abstractmethod
    async def delete_backup(
        self,
        backup_id: str,
        confirmation_required: bool = True
    ) -> bool:
        """Delete backup with optional confirmation."""
        pass
    
    @abstractmethod
    async def get_backup_statistics(
        self,
        time_period: str
    ) -> Dict[str, Any]:
        """Get backup operation statistics and metrics."""
        pass
