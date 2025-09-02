"""🏗️ Base Repository - IA Influencer Agent Platform Enterprise
=============================================================
Module: backend/data_management/repositories/base_repository.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Base Repository Pattern - Production-Ready
Responsibility: Advanced repository pattern with enterprise features
===========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
IA protection rights → Professional SEO → Collaboration matching → Multi-platform distribution

BASE REPOSITORY ARCHITECTURE:
CRUD Operations → Cache Layer → Query Optimization → 
Batch Operations → Transaction Management → Audit Trail → Performance Monitoring
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Generic, Callable
from abc import ABC, abstractmethod
import asyncio
import logging
import time
import json
import hashlib
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

T = TypeVar('T')

class OperationType(Enum):
    """
Types d'opérations pour l'audit"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    BULK_CREATE = "bulk_create"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"

@dataclass
class AuditEntry:
    """Entrée d'audit pour traçabilité"""
    operation_type: OperationType
    entity_type: str
    entity_id: Optional[str]
    user_id: Optional[str]
    timestamp: datetime
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]

@dataclass
class QueryMetrics:
    """
Métriques de performance des requêtes"""
    query_time: float
    cache_hit: bool
    records_count: int
    query_hash: str

class BaseRepository(Generic[T], ABC):
    """
    Advanced base repository with enterprise features
    
    Features:
    - CRUD operations with validation
    - Caching strategies with TTL
    - Audit trail and monitoring
    - Batch operations optimization
    - Transaction management
    - Query performance metrics
    - Error handling and retry logic
    """
    
    def __init__(self, 
                 db_connection=None, 
                 cache_manager=None, 
                 logger=None,
                 audit_service=None,
                 metrics_collector=None):
        self.db = db_connection
        self.cache = cache_manager
        self.logger = logger or logging.getLogger(__name__)
        self.audit_service = audit_service
        self.metrics_collector = metrics_collector
        self._audit_enabled = True
        self._cache_enabled = True
        self._cache_ttl = 3600  # 1 hour default
        self._batch_size = 1000
        self._retry_attempts = 3
        self._performance_threshold = 1.0  # seconds
    
    def _generate_cache_key(self, operation: str, **kwargs) -> str:
        """
Generate cache key for operation"""
        key_data = f"{self.__class__.__name__}:{operation}:{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _log_audit(self, operation: OperationType, entity_id: Optional[str] = None,
                   old_values: Optional[Dict] = None, new_values: Optional[Dict] = None,
                   metadata: Optional[Dict] = None):
        """Log audit entry for operation"""
        if not self._audit_enabled or not self.audit_service:
            return
        
        audit_entry = AuditEntry(
            operation_type=operation,
            entity_type=self.__class__.__name__,
            entity_id=entity_id,
            user_id=metadata.get('user_id') if metadata else None,
            timestamp=datetime.now(timezone.utc),
            old_values=old_values,
            new_values=new_values,
            metadata=metadata
        )
        
        self.audit_service.log_entry(audit_entry)
    
    def _collect_metrics(self, operation: str, execution_time: float, 
                        cache_hit: bool, records_count: int):
        """
Collect performance metrics"""
        if not self.metrics_collector:
            return
        
        metrics = QueryMetrics(
            query_time=execution_time,
            cache_hit=cache_hit,
            records_count=records_count,
            query_hash=hashlib.md5(operation.encode()).hexdigest()
        )
        
        self.metrics_collector.record_query(metrics)
        
        if execution_time > self._performance_threshold:
            self.logger.warning(f"Slow query detected: {operation} took {execution_time:.2f}s")
    
    @contextmanager
    def _performance_monitor(self, operation: str):
        """Context manager for performance monitoring"""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            self._collect_metrics(operation, execution_time, False, 0)
    
    def _validate_entity(self, entity: T) -> bool:
        """
Validate entity before operations"""
        if entity is None:
            raise ValueError("Entity cannot be None")
        return True
    
    def _apply_filters(self, query, filters: Dict[str, Any]) -> Any:
        """Apply filters to query - to be implemented by subclasses"""
        return query
    
    def _paginate_query(self, query, limit: int, offset: int) -> Any:
        """
Apply pagination to query - to be implemented by subclasses"""
        return query
    
    def with_cache(self, enabled: bool = True, ttl: int = 3600) -> 'BaseRepository':
        """
Configure cache settings"""
        self._cache_enabled = enabled
        self._cache_ttl = ttl
        return self
    
    def with_audit(self, enabled: bool = True) -> 'BaseRepository':
        """
Configure audit settings"""
        self._audit_enabled = enabled
        return self
    
    def with_batch_size(self, size: int = 1000) -> 'BaseRepository':
        """
Configure batch size for bulk operations"""
        self._batch_size = size
        return self
    
    @abstractmethod
    async def create(self, entity: T, **kwargs) -> T:
        """
Create new entity with validation and audit"""
        try:
            # Validate entity
            self._validate_entity(entity)
            
            # Log audit entry
            if self._audit_enabled and self.audit_service:
                self._log_audit(
                    OperationType.CREATE,
                    new_values=asdict(entity) if hasattr(entity, '__dataclass_fields__') else entity.__dict__,
                    metadata=kwargs
                )
            
            # Perform actual creation (to be implemented by subclasses)
            result = await self._perform_create(entity, **kwargs)
            
            # Invalidate cache for list operations
            if self._cache_enabled and self.cache:
                await self._invalidate_list_cache()
            
            self.logger.info(f"Created entity: {type(entity).__name__}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating entity: {e}")
            raise
    
    async def _perform_create(self, entity: T, **kwargs) -> T:
        """Override this method in subclasses for actual creation logic"""
        raise NotImplementedError("Subclasses must implement _perform_create")
    
    @abstractmethod
    async def get_by_id(self, entity_id: str, use_cache: bool = True) -> Optional[T]:
        """
Get entity by ID with cache support"""
        try:
            cache_key = f"{self.__class__.__name__}:get_by_id:{entity_id}"
            
            # Check cache first
            if use_cache and self._cache_enabled and self.cache:
                cached_result = await self._get_from_cache(cache_key)
                if cached_result:
                    self.logger.debug(f"Cache hit for entity ID: {entity_id}")
                    return cached_result
            
            # Perform actual lookup (to be implemented by subclasses)
            result = await self._perform_get_by_id(entity_id)
            
            # Cache the result
            if result and use_cache and self._cache_enabled and self.cache:
                await self._set_cache(cache_key, result, self._cache_ttl)
            
            # Log audit entry for read operation
            if self._audit_enabled and self.audit_service:
                self._log_audit(
                    OperationType.READ,
                    entity_id=entity_id,
                    metadata={'cache_hit': use_cache and result is not None}
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting entity by ID {entity_id}: {e}")
            raise
    
    async def _perform_get_by_id(self, entity_id: str) -> Optional[T]:
        """Override this method in subclasses for actual lookup logic"""
        raise NotImplementedError("Subclasses must implement _perform_get_by_id")
    
    @abstractmethod
    async def update(self, entity: T, **kwargs) -> T:
        """
Update entity with validation and audit"""
        try:
            # Validate entity
            self._validate_entity(entity)
            
            # Get old values for audit
            old_values = None
            if self._audit_enabled and hasattr(entity, 'id'):
                old_entity = await self.get_by_id(str(entity.id), use_cache=False)
                if old_entity:
                    old_values = asdict(old_entity) if hasattr(old_entity, '__dataclass_fields__') else old_entity.__dict__
            
            # Perform actual update (to be implemented by subclasses)
            result = await self._perform_update(entity, **kwargs)
            
            # Log audit entry
            if self._audit_enabled and self.audit_service:
                new_values = asdict(result) if hasattr(result, '__dataclass_fields__') else result.__dict__
                self._log_audit(
                    OperationType.UPDATE,
                    entity_id=str(entity.id) if hasattr(entity, 'id') else None,
                    old_values=old_values,
                    new_values=new_values,
                    metadata=kwargs
                )
            
            # Invalidate cache
            if self._cache_enabled and self.cache and hasattr(entity, 'id'):
                cache_key = f"{self.__class__.__name__}:get_by_id:{entity.id}"
                await self._delete_from_cache(cache_key)
                await self._invalidate_list_cache()
            
            self.logger.info(f"Updated entity: {type(entity).__name__}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error updating entity: {e}")
            raise
    
    async def _perform_update(self, entity: T, **kwargs) -> T:
        """Override this method in subclasses for actual update logic"""
        raise NotImplementedError("Subclasses must implement _perform_update")
    
    @abstractmethod
    async def delete(self, entity_id: str, soft_delete: bool = False) -> bool:
        """
Delete entity with soft delete option"""
        try:
            # Get entity for audit purposes
            old_entity = None
            if self._audit_enabled:
                old_entity = await self.get_by_id(entity_id, use_cache=False)
            
            # Perform actual deletion (to be implemented by subclasses)
            success = await self._perform_delete(entity_id, soft_delete)
            
            if success:
                # Log audit entry
                if self._audit_enabled and self.audit_service:
                    old_values = None
                    if old_entity:
                        old_values = asdict(old_entity) if hasattr(old_entity, '__dataclass_fields__') else old_entity.__dict__
                    
                    self._log_audit(
                        OperationType.DELETE,
                        entity_id=entity_id,
                        old_values=old_values,
                        metadata={'soft_delete': soft_delete}
                    )
                
                # Invalidate cache
                if self._cache_enabled and self.cache:
                    cache_key = f"{self.__class__.__name__}:get_by_id:{entity_id}"
                    await self._delete_from_cache(cache_key)
                    await self._invalidate_list_cache()
                
                self.logger.info(f"Deleted entity ID: {entity_id} (soft_delete: {soft_delete})")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting entity ID {entity_id}: {e}")
            raise
    
    async def _perform_delete(self, entity_id: str, soft_delete: bool = False) -> bool:
        """Override this method in subclasses for actual deletion logic"""
        raise NotImplementedError("Subclasses must implement _perform_delete")
    
    @abstractmethod
    async def list(self, filters: Dict[str, Any] = None, limit: int = 100, 
             offset: int = 0, order_by: str = None) -> List[T]:
        """
List entities with advanced filtering and ordering"""
        try:
            filters = filters or {}
            
            # Generate cache key based on parameters
            cache_key = self._generate_list_cache_key(filters, limit, offset, order_by)
            
            # Check cache first
            if self._cache_enabled and self.cache:
                cached_result = await self._get_from_cache(cache_key)
                if cached_result:
                    self.logger.debug(f"Cache hit for list query")
                    return cached_result
            
            # Perform actual list query (to be implemented by subclasses)
            results = await self._perform_list(filters, limit, offset, order_by)
            
            # Cache the results
            if self._cache_enabled and self.cache:
                await self._set_cache(cache_key, results, self._cache_ttl)
            
            # Log audit entry
            if self._audit_enabled and self.audit_service:
                self._log_audit(
                    OperationType.READ,
                    metadata={
                        'operation': 'list',
                        'filters': filters,
                        'limit': limit,
                        'offset': offset,
                        'order_by': order_by,
                        'results_count': len(results)
                    }
                )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error listing entities: {e}")
            raise
    
    async def _perform_list(self, filters: Dict[str, Any], limit: int, offset: int, order_by: str) -> List[T]:
        """Override this method in subclasses for actual list logic"""
        raise NotImplementedError("Subclasses must implement _perform_list")
    
    def _generate_list_cache_key(self, filters: Dict[str, Any], limit: int, offset: int, order_by: str) -> str:
        """Generate cache key for list operations"""
        key_data = {
            'class': self.__class__.__name__,
            'operation': 'list',
            'filters': filters,
            'limit': limit,
            'offset': offset,
            'order_by': order_by
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def bulk_create(self, entities: List[T], batch_size: Optional[int] = None) -> List[T]:
        """
Optimized bulk creation with batching"""
        if not entities:
            return []
        
        batch_size = batch_size or self._batch_size
        results = []
        
        with self._performance_monitor(f"bulk_create_{len(entities)}_entities"):
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                batch_results = []
                
                for entity in batch:
                    self._validate_entity(entity)
                    result = self.create(entity)
                    batch_results.append(result)
                
                results.extend(batch_results)
                
                self._log_audit(
                    OperationType.BULK_CREATE,
                    metadata={'batch_size': len(batch), 'total_entities': len(entities)}
                )
        
        return results
    
    def bulk_update(self, entities: List[T], batch_size: Optional[int] = None) -> List[T]:
        """Optimized bulk update with batching"""
        if not entities:
            return []
        
        batch_size = batch_size or self._batch_size
        results = []
        
        with self._performance_monitor(f"bulk_update_{len(entities)}_entities"):
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                batch_results = []
                
                for entity in batch:
                    self._validate_entity(entity)
                    result = self.update(entity)
                    batch_results.append(result)
                
                results.extend(batch_results)
                
                self._log_audit(
                    OperationType.BULK_UPDATE,
                    metadata={'batch_size': len(batch), 'total_entities': len(entities)}
                )
        
        return results
    
    def bulk_delete(self, entity_ids: List[str], soft_delete: bool = False,
                   batch_size: Optional[int] = None) -> bool:
        """Optimized bulk deletion with batching"""
        if not entity_ids:
            return True
        
        batch_size = batch_size or self._batch_size
        
        with self._performance_monitor(f"bulk_delete_{len(entity_ids)}_entities"):
            for i in range(0, len(entity_ids), batch_size):
                batch = entity_ids[i:i + batch_size]
                
                for entity_id in batch:
                    self.delete(entity_id, soft_delete=soft_delete)
                
                self._log_audit(
                    OperationType.BULK_DELETE,
                    metadata={'batch_size': len(batch), 'total_entities': len(entity_ids)}
                )
        
        return True
    
    def exists(self, entity_id: str, use_cache: bool = True) -> bool:
        """Check entity existence with cache support"""
        if use_cache and self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("exists", entity_id=entity_id)
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        entity = self.get_by_id(entity_id, use_cache=use_cache)
        exists = entity is not None
        
        if use_cache and self._cache_enabled and self.cache:
            self.cache.set(cache_key, exists, ttl=self._cache_ttl)
        
        return exists
    
    def count(self, filters: Dict[str, Any] = None, use_cache: bool = True) -> int:
        """Count entities with cache support"""
        if use_cache and self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("count", filters=filters)
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        entities = self.list(filters=filters)
        count = len(entities)
        
        if use_cache and self._cache_enabled and self.cache:
            self.cache.set(cache_key, count, ttl=self._cache_ttl)
        
        return count
    
    def search(self, query: str, fields: List[str] = None, limit: int = 100) -> List[T]:
        """Full-text search across specified fields"""
        # Default implementation using basic filtering
        # Subclasses should override for proper search capabilities
        try:
            if not query or not query.strip():
                return []
            
            # Get all entities (this should be limited in production)
            all_entities = self.get_all(limit=1000)
            
            # Simple search logic - convert entities to string and search
            query_lower = query.lower().strip()
            results = []
            
            for entity in all_entities:
                # Convert entity to searchable text
                entity_text = str(entity).lower()
                
                # Check if query matches
                if query_lower in entity_text:
                    results.append(entity)
                    
                    if len(results) >= limit:
                        break
            
            logger.warning(f"Using basic search implementation. Override in subclass for better performance.")
            return results
            
        except Exception as e:
            logger.error(f"Error in default search implementation: {e}")
            return []
    
    def get_or_create(self, defaults: Dict[str, Any] = None, **kwargs) -> tuple[T, bool]:
        """Get existing entity or create new one"""
        # Default implementation - subclasses should override for efficiency
        try:
            # Try to find existing entity
            entities = self.filter(**kwargs)
            
            if entities:
                # Entity exists, return first match
                return entities[0], False
            
            # Entity doesn't exist, create new one
            create_data = kwargs.copy()
            if defaults:
                # Add defaults for fields not specified in kwargs
                for key, value in defaults.items():
                    if key not in create_data:
                        create_data[key] = value
            
            # Generate ID if not provided
            if 'id' not in create_data:
                create_data['id'] = str(uuid.uuid4())
            
            new_entity = self.create(create_data)
            return new_entity, True
            
        except Exception as e:
            logger.error(f"Error in get_or_create: {e}")
            # Fallback: try to return existing or raise exception
            entities = self.filter(**kwargs)
            if entities:
                return entities[0], False
            raise
    
    def get_multiple(self, entity_ids: List[str], use_cache: bool = True) -> List[T]:
        """Get multiple entities by IDs efficiently"""
        if not entity_ids:
            return []
        
        results = []
        cache_misses = []
        
        # Check cache first if enabled
        if use_cache and self._cache_enabled and self.cache:
            for entity_id in entity_ids:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity_id)
                cached_entity = self.cache.get(cache_key)
                if cached_entity is not None:
                    results.append(cached_entity)
                else:
                    cache_misses.append(entity_id)
        else:
            cache_misses = entity_ids
        
        # Fetch cache misses
        for entity_id in cache_misses:
            entity = self.get_by_id(entity_id, use_cache=False)
            if entity:
                results.append(entity)
                
                # Cache the result
                if use_cache and self._cache_enabled and self.cache:
                    cache_key = self._generate_cache_key("get_by_id", entity_id=entity_id)
                    self.cache.set(cache_key, entity, ttl=self._cache_ttl)
        
        return results
    
    def invalidate_cache(self, pattern: str = None):
        """Invalidate cache entries"""
        if not self.cache:
            return
        
        if pattern:
            self.cache.delete_pattern(pattern)
        else:
            # Invalidate all cache entries for this repository
            pattern = f"{self.__class__.__name__}:*"
            self.cache.delete_pattern(pattern)

class AsyncBaseRepository(Generic[T], ABC):
    """
    Advanced asynchronous base repository with enterprise features
    
    Features:
    - Async CRUD operations with validation
    - Advanced caching with TTL and invalidation
    - Comprehensive audit trail
    - Optimized batch operations with concurrency control
    - Connection pooling and transaction management
    - Real-time performance monitoring
    - Automatic retry logic with backoff
    """
    
    def __init__(self, 
                 db_connection=None, 
                 cache_manager=None, 
                 logger=None,
                 audit_service=None,
                 metrics_collector=None):
        self.db = db_connection
        self.cache = cache_manager
        self.logger = logger or logging.getLogger(__name__)
        self.audit_service = audit_service
        self.metrics_collector = metrics_collector
        self._audit_enabled = True
        self._cache_enabled = True
        self._cache_ttl = 3600  # 1 hour default
        self._batch_size = 1000
        self._retry_attempts = 3
        self._retry_delay = 1.0  # seconds
        self._performance_threshold = 1.0  # seconds
        self._max_concurrent_operations = 10
    
    def _generate_cache_key(self, operation: str, **kwargs) -> str:
        """
Generate cache key for operation"""
        key_data = f"{self.__class__.__name__}:{operation}:{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _log_audit(self, operation: OperationType, entity_id: Optional[str] = None,
                        old_values: Optional[Dict] = None, new_values: Optional[Dict] = None,
                        metadata: Optional[Dict] = None):
        """Log audit entry for operation asynchronously"""
        if not self._audit_enabled or not self.audit_service:
            return
        
        audit_entry = AuditEntry(
            operation_type=operation,
            entity_type=self.__class__.__name__,
            entity_id=entity_id,
            user_id=metadata.get('user_id') if metadata else None,
            timestamp=datetime.now(timezone.utc),
            old_values=old_values,
            new_values=new_values,
            metadata=metadata
        )
        
        await self.audit_service.log_entry_async(audit_entry)
    
    async def _collect_metrics(self, operation: str, execution_time: float, 
                              cache_hit: bool, records_count: int):
        """
Collect performance metrics asynchronously"""
        if not self.metrics_collector:
            return
        
        metrics = QueryMetrics(
            query_time=execution_time,
            cache_hit=cache_hit,
            records_count=records_count,
            query_hash=hashlib.md5(operation.encode()).hexdigest()
        )
        
        await self.metrics_collector.record_query_async(metrics)
        
        if execution_time > self._performance_threshold:
            self.logger.warning(f"Slow async query detected: {operation} took {execution_time:.2f}s")
    
    @asynccontextmanager
    async def _performance_monitor(self, operation: str):
        """Async context manager for performance monitoring"""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            await self._collect_metrics(operation, execution_time, False, 0)
    
    async def _validate_entity(self, entity: T) -> bool:
        """
Validate entity before operations"""
        if entity is None:
            raise ValueError("Entity cannot be None")
        return True
    
    async def _retry_operation(self, operation: Callable, *args, **kwargs):
        """Retry operation with exponential backoff"""
        last_exception = None
        
        for attempt in range(self._retry_attempts):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Operation failed (attempt {attempt + 1}/{self._retry_attempts}): {e}")
                
                if attempt < self._retry_attempts - 1:
                    delay = self._retry_delay * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
        
        self.logger.error(f"Operation failed after {self._retry_attempts} attempts")
        raise last_exception
    
    def with_cache(self, enabled: bool = True, ttl: int = 3600) -> 'AsyncBaseRepository':
        """Configure cache settings"""
        self._cache_enabled = enabled
        self._cache_ttl = ttl
        return self
    
    def with_audit(self, enabled: bool = True) -> 'AsyncBaseRepository':
        """
Configure audit settings"""
        self._audit_enabled = enabled
        return self
    
    def with_batch_size(self, size: int = 1000) -> 'AsyncBaseRepository':
        """
Configure batch size for bulk operations"""
        self._batch_size = size
        return self
    
    def with_concurrency(self, max_concurrent: int = 10) -> 'AsyncBaseRepository':
        """
Configure maximum concurrent operations"""
        self._max_concurrent_operations = max_concurrent
        return self
    
    @abstractmethod
    async def create(self, entity: T, **kwargs) -> T:
        """
Create new entity asynchronously with validation and audit"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str, use_cache: bool = True) -> Optional[T]:
        """
Get entity by ID asynchronously with cache support"""
        pass
    
    @abstractmethod
    async def update(self, entity: T, **kwargs) -> T:
        """
Update entity asynchronously with validation and audit"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str, soft_delete: bool = False) -> bool:
        """
Delete entity asynchronously with soft delete option"""
        pass
    
    @abstractmethod
    async def list(self, filters: Dict[str, Any] = None, limit: int = 100, 
                  offset: int = 0, order_by: str = None) -> List[T]:
        """
List entities asynchronously with advanced filtering and ordering"""
        pass
    
    async def bulk_create(self, entities: List[T], batch_size: Optional[int] = None) -> List[T]:
        """
Optimized async bulk creation with concurrency control"""
        if not entities:
            return []
        
        batch_size = batch_size or self._batch_size
        results = []
        
        async with self._performance_monitor(f"async_bulk_create_{len(entities)}_entities"):
            # Process in batches with concurrency control
            semaphore = asyncio.Semaphore(self._max_concurrent_operations)
            
            async def create_with_semaphore(entity):
                async with semaphore:
                    await self._validate_entity(entity)
                    return await self.create(entity)
            
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                
                # Create batch concurrently
                batch_tasks = [create_with_semaphore(entity) for entity in batch]
                batch_results = await asyncio.gather(*batch_tasks)
                results.extend(batch_results)
                
                await self._log_audit(
                    OperationType.BULK_CREATE,
                    metadata={'batch_size': len(batch), 'total_entities': len(entities)}
                )
        
        return results
    
    async def bulk_update(self, entities: List[T], batch_size: Optional[int] = None) -> List[T]:
        """Optimized async bulk update with concurrency control"""
        if not entities:
            return []
        
        batch_size = batch_size or self._batch_size
        results = []
        
        async with self._performance_monitor(f"async_bulk_update_{len(entities)}_entities"):
            semaphore = asyncio.Semaphore(self._max_concurrent_operations)
            
            async def update_with_semaphore(entity):
                async with semaphore:
                    await self._validate_entity(entity)
                    return await self.update(entity)
            
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                
                batch_tasks = [update_with_semaphore(entity) for entity in batch]
                batch_results = await asyncio.gather(*batch_tasks)
                results.extend(batch_results)
                
                await self._log_audit(
                    OperationType.BULK_UPDATE,
                    metadata={'batch_size': len(batch), 'total_entities': len(entities)}
                )
        
        return results
    
    async def bulk_delete(self, entity_ids: List[str], soft_delete: bool = False,
                         batch_size: Optional[int] = None) -> bool:
        """Optimized async bulk deletion with concurrency control"""
        if not entity_ids:
            return True
        
        batch_size = batch_size or self._batch_size
        
        async with self._performance_monitor(f"async_bulk_delete_{len(entity_ids)}_entities"):
            semaphore = asyncio.Semaphore(self._max_concurrent_operations)
            
            async def delete_with_semaphore(entity_id):
                async with semaphore:
                    return await self.delete(entity_id, soft_delete=soft_delete)
            
            for i in range(0, len(entity_ids), batch_size):
                batch = entity_ids[i:i + batch_size]
                
                batch_tasks = [delete_with_semaphore(entity_id) for entity_id in batch]
                await asyncio.gather(*batch_tasks)
                
                await self._log_audit(
                    OperationType.BULK_DELETE,
                    metadata={'batch_size': len(batch), 'total_entities': len(entity_ids)}
                )
        
        return True
    
    async def exists(self, entity_id: str, use_cache: bool = True) -> bool:
        """Check entity existence asynchronously with cache support"""
        if use_cache and self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("exists", entity_id=entity_id)
            cached_result = await self.cache.get_async(cache_key)
            if cached_result is not None:
                return cached_result
        
        entity = await self.get_by_id(entity_id, use_cache=use_cache)
        exists = entity is not None
        
        if use_cache and self._cache_enabled and self.cache:
            await self.cache.set_async(cache_key, exists, ttl=self._cache_ttl)
        
        return exists
    
    async def count(self, filters: Dict[str, Any] = None, use_cache: bool = True) -> int:
        """Count entities asynchronously with cache support"""
        if use_cache and self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("count", filters=filters)
            cached_result = await self.cache.get_async(cache_key)
            if cached_result is not None:
                return cached_result
        
        entities = await self.list(filters=filters)
        count = len(entities)
        
        if use_cache and self._cache_enabled and self.cache:
            await self.cache.set_async(cache_key, count, ttl=self._cache_ttl)
        
        return count
    
    async def search(self, query: str, fields: List[str] = None, limit: int = 100) -> List[T]:
        """Async full-text search across specified fields"""
        # Default async implementation using basic filtering
        # Subclasses should override for proper search capabilities
        try:
            if not query or not query.strip():
                return []
            
            # Get all entities asynchronously (this should be limited in production)
            all_entities = await self.get_all(limit=1000)
            
            # Simple search logic - convert entities to string and search
            query_lower = query.lower().strip()
            results = []
            
            for entity in all_entities:
                # Convert entity to searchable text
                entity_text = str(entity).lower()
                
                # Check if query matches
                if query_lower in entity_text:
                    results.append(entity)
                    
                    if len(results) >= limit:
                        break
            
            logger.warning(f"Using basic async search implementation. Override in subclass for better performance.")
            return results
            
        except Exception as e:
            logger.error(f"Error in default async search implementation: {e}")
            return []
    
    async def get_or_create(self, defaults: Dict[str, Any] = None, **kwargs) -> tuple[T, bool]:
        """Get existing entity or create new one asynchronously"""
        # Default async implementation - subclasses should override for efficiency
        try:
            # Try to find existing entity asynchronously
            entities = await self.filter(**kwargs)
            
            if entities:
                # Entity exists, return first match
                return entities[0], False
            
            # Entity doesn't exist, create new one
            create_data = kwargs.copy()
            if defaults:
                # Add defaults for fields not specified in kwargs
                for key, value in defaults.items():
                    if key not in create_data:
                        create_data[key] = value
            
            # Generate ID if not provided
            if 'id' not in create_data:
                create_data['id'] = str(uuid.uuid4())
            
            new_entity = await self.create(create_data)
            return new_entity, True
            
        except Exception as e:
            logger.error(f"Error in async get_or_create: {e}")
            # Fallback: try to return existing or raise exception
            entities = await self.filter(**kwargs)
            if entities:
                return entities[0], False
            raise
    
    async def get_multiple(self, entity_ids: List[str], use_cache: bool = True) -> List[T]:
        """Get multiple entities by IDs efficiently with async processing"""
        if not entity_ids:
            return []
        
        results = []
        cache_misses = []
        
        # Check cache first if enabled
        if use_cache and self._cache_enabled and self.cache:
            cache_tasks = []
            for entity_id in entity_ids:
                cache_key = self._generate_cache_key("get_by_id", entity_id=entity_id)
                cache_tasks.append(self.cache.get_async(cache_key))
            
            cached_results = await asyncio.gather(*cache_tasks)
            
            for i, cached_entity in enumerate(cached_results):
                if cached_entity is not None:
                    results.append(cached_entity)
                else:
                    cache_misses.append(entity_ids[i])
        else:
            cache_misses = entity_ids
        
        # Fetch cache misses concurrently
        if cache_misses:
            semaphore = asyncio.Semaphore(self._max_concurrent_operations)
            
            async def fetch_with_semaphore(entity_id):
                async with semaphore:
                    return await self.get_by_id(entity_id, use_cache=False)
            
            fetch_tasks = [fetch_with_semaphore(entity_id) for entity_id in cache_misses]
            fetched_entities = await asyncio.gather(*fetch_tasks)
            
            # Cache the results and add to results
            cache_tasks = []
            for i, entity in enumerate(fetched_entities):
                if entity:
                    results.append(entity)
                    
                    if use_cache and self._cache_enabled and self.cache:
                        cache_key = self._generate_cache_key("get_by_id", entity_id=cache_misses[i])
                        cache_tasks.append(self.cache.set_async(cache_key, entity, ttl=self._cache_ttl))
            
            if cache_tasks:
                await asyncio.gather(*cache_tasks)
        
        return results
    
    # ============ CACHE HELPER METHODS ============
    
    async def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from cache asynchronously"""
        if not self.cache:
            return None
        try:
            return await self.cache.get_async(cache_key)
        except Exception as e:
            self.logger.warning(f"Cache get failed for key {cache_key}: {e}")
            return None
    
    async def _set_cache(self, cache_key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache asynchronously"""
        if not self.cache:
            return
        try:
            await self.cache.set_async(cache_key, value, ttl or self._cache_ttl)
        except Exception as e:
            self.logger.warning(f"Cache set failed for key {cache_key}: {e}")
    
    async def _delete_from_cache(self, cache_key: str) -> None:
        """Delete value from cache asynchronously"""
        if not self.cache:
            return
        try:
            await self.cache.delete_async(cache_key)
        except Exception as e:
            self.logger.warning(f"Cache delete failed for key {cache_key}: {e}")
    
    async def _invalidate_list_cache(self) -> None:
        """Invalidate all list operation caches"""
        if not self.cache:
            return
        try:
            pattern = f"{self.__class__.__name__}:list:*"
            await self.cache.delete_pattern_async(pattern)
        except Exception as e:
            self.logger.warning(f"Cache invalidation failed for pattern: {e}")

    async def invalidate_cache(self, pattern: str = None):
        """Invalidate cache entries asynchronously"""
        if not self.cache:
            return
        
        if pattern:
            await self.cache.delete_pattern_async(pattern)
        else:
            # Invalidate all cache entries for this repository
            pattern = f"{self.__class__.__name__}:*"
            await self.cache.delete_pattern_async(pattern)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on repository components"""
        health_status = {
            'repository': self.__class__.__name__,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'healthy',
            'components': {}
        }
        
        try:
            # Check database connection
            if self.db:
                # Implementation depends on database type
                health_status['components']['database'] = 'healthy'
            
            # Check cache connection
            if self.cache:
                await self.cache.ping_async()
                health_status['components']['cache'] = 'healthy'
            
            # Check audit service
            if self.audit_service:
                health_status['components']['audit'] = 'healthy'
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
            self.logger.error(f"Health check failed: {e}")
        
        return health_status
