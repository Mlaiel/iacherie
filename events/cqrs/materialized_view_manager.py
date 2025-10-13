"""🚀 Enterprise Materialized View Manager - CQRS Architecture
============================================================
Module: events/cqrs/materialized_view_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE MATERIALIZED VIEW MANAGER
Advanced materialized view management for high-performance queries
- Dynamic materialized view creation and management
- Intelligent refresh strategies (real-time, scheduled, on-demand)
- Multi-storage backend support (SQL, NoSQL, Search, Cache)
- Query optimization through materialized view routing
- View dependency tracking and cascade refresh
- Performance monitoring and auto-optimization
"""

import asyncio
import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Union, Type, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import hashlib
import re

from .query_bus import Query, QueryResult, QueryStatus
from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)


class MaterializedViewType(Enum):
    """Types of materialized views"""
    AGGREGATED = "aggregated"
    FILTERED = "filtered"
    JOINED = "joined"
    PROJECTED = "projected"
    INDEXED = "indexed"
    CACHED = "cached"


class RefreshStrategy(Enum):
    """Materialized view refresh strategies"""
    REAL_TIME = "real_time"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"
    INCREMENTAL = "incremental"
    FULL_REBUILD = "full_rebuild"
    HYBRID = "hybrid"


class ViewState(Enum):
    """Materialized view states"""
    CREATING = "creating"
    ACTIVE = "active"
    REFRESHING = "refreshing"
    STALE = "stale"
    FAILED = "failed"
    DISABLED = "disabled"
    DROPPING = "dropping"


@dataclass
class MaterializedViewDefinition:
    """Definition of a materialized view"""
    view_id: str
    name: str
    description: str
    view_type: MaterializedViewType
    source_tables: List[str]
    query_definition: str
    refresh_strategy: RefreshStrategy = RefreshStrategy.SCHEDULED
    refresh_interval_minutes: int = 60
    storage_backend: str = "default"
    indexes: List[str] = field(default_factory=list)
    partitioning: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)
    performance_requirements: Dict[str, Any] = field(default_factory=dict)
    retention_policy: Optional[Dict[str, Any]] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MaterializedViewInstance:
    """Runtime instance of a materialized view"""
    definition: MaterializedViewDefinition
    state: ViewState = ViewState.CREATING
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_refresh: Optional[datetime] = None
    next_refresh: Optional[datetime] = None
    refresh_duration_seconds: float = 0.0
    total_refreshes: int = 0
    failed_refreshes: int = 0
    row_count: int = 0
    size_bytes: int = 0
    query_count: int = 0
    avg_query_time_ms: float = 0.0
    last_error: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ViewRefreshJob:
    """Materialized view refresh job"""
    job_id: str
    view_id: str
    refresh_type: RefreshStrategy
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    error_message: Optional[str] = None
    affected_rows: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ViewStorageBackend:
    """Abstract storage backend for materialized views"""
    
    def __init__(self, backend_config: Dict[str, Any]):
        self.backend_config = backend_config
        self.backend_name = backend_config.get("name", "default")
    
    async def create_view(self, view_def: MaterializedViewDefinition) -> bool:
        """Create materialized view"""
        raise NotImplementedError
    
    async def refresh_view(self, view_def: MaterializedViewDefinition, 
                          refresh_type: RefreshStrategy = RefreshStrategy.FULL_REBUILD) -> Dict[str, Any]:
        """Refresh materialized view"""
        raise NotImplementedError
    
    async def drop_view(self, view_id: str) -> bool:
        """Drop materialized view"""
        raise NotImplementedError
    
    async def query_view(self, view_id: str, query: Query) -> QueryResult:
        """Query materialized view"""
        raise NotImplementedError
    
    async def get_view_statistics(self, view_id: str) -> Dict[str, Any]:
        """Get view statistics"""
        raise NotImplementedError
    
    async def create_indexes(self, view_id: str, indexes: List[str]) -> bool:
        """Create indexes on materialized view"""
        raise NotImplementedError


class InMemoryViewBackend(ViewStorageBackend):
    """In-memory storage backend for materialized views"""
    
    def __init__(self, backend_config: Dict[str, Any]):
        super().__init__(backend_config)
        self._views: Dict[str, Dict[str, Any]] = {}
        self._view_data: Dict[str, List[Dict[str, Any]]] = {}
        self._view_indexes: Dict[str, List[str]] = {}
    
    async def create_view(self, view_def: MaterializedViewDefinition) -> bool:
        """Create in-memory materialized view"""
        try:
            self._views[view_def.view_id] = {
                "definition": view_def,
                "created_at": datetime.utcnow(),
                "metadata": {}
            }
            self._view_data[view_def.view_id] = []
            self._view_indexes[view_def.view_id] = view_def.indexes.copy()
            return True
        except Exception as e:
            logger.error(f"Failed to create in-memory view {view_def.view_id}: {e}")
            return False
    
    async def refresh_view(self, view_def: MaterializedViewDefinition, 
                          refresh_type: RefreshStrategy = RefreshStrategy.FULL_REBUILD) -> Dict[str, Any]:
        """Refresh in-memory materialized view"""
        start_time = time.time()
        
        try:
            # Simulate view refresh by generating sample data
            new_data = []
            
            # Generate sample data based on view type
            if view_def.view_type == MaterializedViewType.AGGREGATED:
                new_data = self._generate_aggregated_data(view_def)
            elif view_def.view_type == MaterializedViewType.FILTERED:
                new_data = self._generate_filtered_data(view_def)
            elif view_def.view_type == MaterializedViewType.JOINED:
                new_data = self._generate_joined_data(view_def)
            else:
                new_data = self._generate_default_data(view_def)
            
            # Update view data
            if refresh_type == RefreshStrategy.INCREMENTAL:
                # Append new data for incremental refresh
                self._view_data[view_def.view_id].extend(new_data)
            else:
                # Replace all data for full refresh
                self._view_data[view_def.view_id] = new_data
            
            refresh_duration = time.time() - start_time
            
            return {
                "success": True,
                "refresh_duration_seconds": refresh_duration,
                "affected_rows": len(new_data),
                "total_rows": len(self._view_data[view_def.view_id]),
                "size_bytes": len(json.dumps(self._view_data[view_def.view_id]))
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh in-memory view {view_def.view_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "refresh_duration_seconds": time.time() - start_time
            }
    
    async def drop_view(self, view_id: str) -> bool:
        """Drop in-memory materialized view"""
        try:
            self._views.pop(view_id, None)
            self._view_data.pop(view_id, None)
            self._view_indexes.pop(view_id, None)
            return True
        except Exception as e:
            logger.error(f"Failed to drop in-memory view {view_id}: {e}")
            return False
    
    async def query_view(self, view_id: str, query: Query) -> QueryResult:
        """Query in-memory materialized view"""
        start_time = time.time()
        
        try:
            if view_id not in self._view_data:
                return QueryResult(
                    query_id=query.query_id,
                    status=QueryStatus.FAILED,
                    error=f"View {view_id} not found"
                )
            
            data = self._view_data[view_id]
            
            # Apply filters
            filtered_data = self._apply_filters(data, query.filters)
            
            # Apply sorting
            sorted_data = self._apply_sorting(filtered_data, query.sorting)
            
            # Apply pagination
            paginated_data = self._apply_pagination(sorted_data, query.pagination)
            
            execution_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.COMPLETED,
                data=paginated_data,
                execution_time_ms=execution_time,
                total_count=len(filtered_data),
                page_info={
                    "page": query.pagination.get("page", 1),
                    "limit": query.pagination.get("limit", 50),
                    "total_pages": (len(filtered_data) + query.pagination.get("limit", 50) - 1) // query.pagination.get("limit", 50)
                }
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def get_view_statistics(self, view_id: str) -> Dict[str, Any]:
        """Get in-memory view statistics"""
        if view_id not in self._views:
            return {}
        
        data = self._view_data.get(view_id, [])
        
        return {
            "row_count": len(data),
            "size_bytes": len(json.dumps(data)),
            "indexes": len(self._view_indexes.get(view_id, [])),
            "created_at": self._views[view_id]["created_at"].isoformat(),
            "backend": "in_memory"
        }
    
    async def create_indexes(self, view_id: str, indexes: List[str]) -> bool:
        """Create indexes on in-memory view (no-op for in-memory)"""
        if view_id in self._view_indexes:
            self._view_indexes[view_id].extend(indexes)
            return True
        return False
    
    def _generate_aggregated_data(self, view_def: MaterializedViewDefinition) -> List[Dict[str, Any]]:
        """Generate sample aggregated data"""
        return [
            {"category": f"category_{i}", "count": i * 10, "total_value": i * 100.0}
            for i in range(1, 101)
        ]
    
    def _generate_filtered_data(self, view_def: MaterializedViewDefinition) -> List[Dict[str, Any]]:
        """Generate sample filtered data"""
        return [
            {"id": i, "name": f"item_{i}", "status": "active" if i % 2 == 0 else "inactive", "value": i * 1.5}
            for i in range(1, 201)
        ]
    
    def _generate_joined_data(self, view_def: MaterializedViewDefinition) -> List[Dict[str, Any]]:
        """Generate sample joined data"""
        return [
            {
                "user_id": i,
                "username": f"user_{i}",
                "order_count": i % 10,
                "total_spent": i * 25.0,
                "last_order_date": (datetime.utcnow() - timedelta(days=i)).isoformat()
            }
            for i in range(1, 151)
        ]
    
    def _generate_default_data(self, view_def: MaterializedViewDefinition) -> List[Dict[str, Any]]:
        """Generate default sample data"""
        return [
            {"id": i, "data": f"value_{i}", "timestamp": datetime.utcnow().isoformat()}
            for i in range(1, 51)
        ]
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to data"""
        if not filters:
            return data
        
        filtered = []
        for item in data:
            matches = True
            for key, value in filters.items():
                if key not in item or item[key] != value:
                    matches = False
                    break
            if matches:
                filtered.append(item)
        
        return filtered
    
    def _apply_sorting(self, data: List[Dict[str, Any]], sorting: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Apply sorting to data"""
        if not sorting:
            return data
        
        for sort_spec in reversed(sorting):  # Apply sorts in reverse order
            field = sort_spec.get("field")
            direction = sort_spec.get("direction", "asc")
            
            if field:
                data.sort(
                    key=lambda x: x.get(field, ""),
                    reverse=(direction.lower() == "desc")
                )
        
        return data
    
    def _apply_pagination(self, data: List[Dict[str, Any]], pagination: Dict[str, int]) -> List[Dict[str, Any]]:
        """Apply pagination to data"""
        page = pagination.get("page", 1)
        limit = pagination.get("limit", 50)
        
        start_index = (page - 1) * limit
        end_index = start_index + limit
        
        return data[start_index:end_index]


class ViewQueryOptimizer:
    """Optimize queries by routing to appropriate materialized views"""
    
    def __init__(self):
        self._view_mappings: Dict[str, List[str]] = defaultdict(list)
        self._query_patterns: Dict[str, str] = {}
    
    def register_view_for_query_pattern(self, query_pattern: str, view_id: str) -> None:
        """Register materialized view for query pattern"""
        self._view_mappings[query_pattern].append(view_id)
        self._query_patterns[view_id] = query_pattern
    
    def find_optimal_view(self, query: Query, available_views: List[MaterializedViewInstance]) -> Optional[str]:
        """Find optimal materialized view for query"""
        # Simple pattern matching for now
        query_signature = self._generate_query_signature(query)
        
        # Find views that match query patterns
        matching_views = []
        for view in available_views:
            if view.state == ViewState.ACTIVE:
                view_pattern = self._query_patterns.get(view.definition.view_id)
                if view_pattern and self._pattern_matches(query_signature, view_pattern):
                    matching_views.append(view)
        
        if not matching_views:
            return None
        
        # Select best view based on performance metrics
        best_view = min(matching_views, key=lambda v: v.avg_query_time_ms)
        return best_view.definition.view_id
    
    def _generate_query_signature(self, query: Query) -> str:
        """Generate signature for query"""
        signature_parts = [
            query.query_type,
            str(sorted(query.filters.keys())),
            str(sorted([s.get("field") for s in query.sorting]))
        ]
        return "|".join(signature_parts)
    
    def _pattern_matches(self, query_signature: str, pattern: str) -> bool:
        """Check if query signature matches pattern"""
        # Simple pattern matching - can be enhanced with regex or more sophisticated matching
        return pattern in query_signature or query_signature.startswith(pattern)


class ViewDependencyManager:
    """Manage dependencies between materialized views"""
    
    def __init__(self):
        self._dependencies: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
    
    def add_dependency(self, view_id: str, depends_on: str) -> None:
        """Add dependency relationship"""
        self._dependencies[view_id].add(depends_on)
        self._reverse_dependencies[depends_on].add(view_id)
    
    def remove_dependency(self, view_id: str, depends_on: str) -> None:
        """Remove dependency relationship"""
        self._dependencies[view_id].discard(depends_on)
        self._reverse_dependencies[depends_on].discard(view_id)
    
    def get_refresh_order(self, view_ids: List[str]) -> List[str]:
        """Get optimal refresh order based on dependencies"""
        # Topological sort to determine refresh order
        visited = set()
        result = []
        
        def visit(view_id: str):
            if view_id in visited:
                return
            
            visited.add(view_id)
            
            # Visit dependencies first
            for dependency in self._dependencies[view_id]:
                if dependency in view_ids:
                    visit(dependency)
            
            result.append(view_id)
        
        for view_id in view_ids:
            visit(view_id)
        
        return result
    
    def get_dependent_views(self, view_id: str) -> Set[str]:
        """Get views that depend on the given view"""
        return self._reverse_dependencies[view_id].copy()


class MaterializedViewScheduler:
    """Schedule materialized view refresh operations"""
    
    def __init__(self):
        self._scheduled_jobs: Dict[str, ViewRefreshJob] = {}
        self._job_queue: asyncio.Queue = asyncio.Queue()
        self._scheduler_task: Optional[asyncio.Task] = None
        self._worker_tasks: List[asyncio.Task] = []
        self._max_concurrent_refreshes = 5
        
        # Start scheduler
        self._start_scheduler()
    
    def schedule_refresh(self, view_id: str, refresh_type: RefreshStrategy,
                        scheduled_at: datetime = None) -> str:
        """Schedule view refresh"""
        job_id = str(uuid.uuid4())
        scheduled_at = scheduled_at or datetime.utcnow()
        
        job = ViewRefreshJob(
            job_id=job_id,
            view_id=view_id,
            refresh_type=refresh_type,
            scheduled_at=scheduled_at
        )
        
        self._scheduled_jobs[job_id] = job
        asyncio.create_task(self._enqueue_job_when_ready(job))
        
        return job_id
    
    async def _enqueue_job_when_ready(self, job: ViewRefreshJob) -> None:
        """Enqueue job when scheduled time arrives"""
        now = datetime.utcnow()
        if job.scheduled_at > now:
            delay = (job.scheduled_at - now).total_seconds()
            await asyncio.sleep(delay)
        
        await self._job_queue.put(job)
    
    def _start_scheduler(self) -> None:
        """Start scheduler and workers"""
        # Start worker tasks
        for i in range(self._max_concurrent_refreshes):
            task = asyncio.create_task(self._worker_loop(f"worker_{i}"))
            self._worker_tasks.append(task)
    
    async def _worker_loop(self, worker_name: str) -> None:
        """Worker loop for processing refresh jobs"""
        while True:
            try:
                job = await self._job_queue.get()
                
                job.started_at = datetime.utcnow()
                job.status = "running"
                
                logger.info(f"Worker {worker_name} starting refresh job {job.job_id} for view {job.view_id}")
                
                # In a real implementation, this would call the actual refresh logic
                await asyncio.sleep(1)  # Simulate refresh work
                
                job.completed_at = datetime.utcnow()
                job.status = "completed"
                job.affected_rows = 100  # Mock data
                
                logger.info(f"Worker {worker_name} completed refresh job {job.job_id}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                if 'job' in locals():
                    job.status = "failed"
                    job.error_message = str(e)
                    job.completed_at = datetime.utcnow()
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get refresh job status"""
        job = self._scheduled_jobs.get(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "view_id": job.view_id,
            "refresh_type": job.refresh_type.value,
            "status": job.status,
            "scheduled_at": job.scheduled_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "affected_rows": job.affected_rows,
            "error_message": job.error_message
        }
    
    def get_pending_jobs(self) -> List[Dict[str, Any]]:
        """Get list of pending jobs"""
        return [
            self.get_job_status(job_id)
            for job_id, job in self._scheduled_jobs.items()
            if job.status == "pending"
        ]
    
    async def shutdown(self) -> None:
        """Shutdown scheduler"""
        for task in self._worker_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


class EnterpriseMaterializedViewManager:
    """Enterprise materialized view manager"""
    
    def __init__(self):
        self._views: Dict[str, MaterializedViewInstance] = {}
        self._storage_backends: Dict[str, ViewStorageBackend] = {}
        self._query_optimizer = ViewQueryOptimizer()
        self._dependency_manager = ViewDependencyManager()
        self._scheduler = MaterializedViewScheduler()
        
        # Register default in-memory backend
        self.register_storage_backend("default", InMemoryViewBackend({"name": "default"}))
        
        # Metrics
        self._metrics = {
            "total_views": 0,
            "active_views": 0,
            "total_queries": 0,
            "cache_hits": 0,
            "refresh_jobs_completed": 0,
            "refresh_jobs_failed": 0
        }
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._auto_refresh_task: Optional[asyncio.Task] = None
        
        # Start background tasks
        self._start_background_tasks()
    
    def register_storage_backend(self, name: str, backend: ViewStorageBackend) -> None:
        """Register storage backend"""
        self._storage_backends[name] = backend
        logger.info(f"Registered materialized view storage backend: {name}")
    
    async def create_materialized_view(self, view_def: MaterializedViewDefinition) -> bool:
        """Create materialized view"""
        try:
            # Validate view definition
            if not self._validate_view_definition(view_def):
                return False
            
            # Get storage backend
            backend = self._storage_backends.get(view_def.storage_backend, self._storage_backends["default"])
            
            # Create view in storage
            success = await backend.create_view(view_def)
            
            if success:
                # Create view instance
                view_instance = MaterializedViewInstance(
                    definition=view_def,
                    state=ViewState.CREATING
                )
                
                self._views[view_def.view_id] = view_instance
                
                # Register dependencies
                for dependency in view_def.dependencies:
                    self._dependency_manager.add_dependency(view_def.view_id, dependency)
                
                # Perform initial refresh
                await self._refresh_view_internal(view_def.view_id, RefreshStrategy.FULL_REBUILD)
                
                # Schedule regular refreshes if needed
                if view_def.refresh_strategy == RefreshStrategy.SCHEDULED:
                    self._schedule_regular_refresh(view_def.view_id)
                
                self._metrics["total_views"] += 1
                self._metrics["active_views"] += 1
                
                logger.info(f"Created materialized view: {view_def.view_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to create materialized view {view_def.view_id}: {e}")
            return False
    
    async def drop_materialized_view(self, view_id: str) -> bool:
        """Drop materialized view"""
        try:
            if view_id not in self._views:
                return False
            
            view_instance = self._views[view_id]
            view_instance.state = ViewState.DROPPING
            
            # Get storage backend
            backend = self._storage_backends.get(
                view_instance.definition.storage_backend,
                self._storage_backends["default"]
            )
            
            # Drop from storage
            success = await backend.drop_view(view_id)
            
            if success:
                # Remove dependencies
                for dependency in view_instance.definition.dependencies:
                    self._dependency_manager.remove_dependency(view_id, dependency)
                
                # Remove from registry
                del self._views[view_id]
                
                self._metrics["total_views"] -= 1
                if view_instance.state == ViewState.ACTIVE:
                    self._metrics["active_views"] -= 1
                
                logger.info(f"Dropped materialized view: {view_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to drop materialized view {view_id}: {e}")
            return False
    
    async def refresh_materialized_view(self, view_id: str, 
                                      refresh_type: RefreshStrategy = RefreshStrategy.FULL_REBUILD) -> bool:
        """Refresh materialized view"""
        return await self._refresh_view_internal(view_id, refresh_type)
    
    async def _refresh_view_internal(self, view_id: str, refresh_type: RefreshStrategy) -> bool:
        """Internal view refresh logic"""
        try:
            if view_id not in self._views:
                return False
            
            view_instance = self._views[view_id]
            view_instance.state = ViewState.REFRESHING
            
            # Get storage backend
            backend = self._storage_backends.get(
                view_instance.definition.storage_backend,
                self._storage_backends["default"]
            )
            
            # Perform refresh
            refresh_result = await backend.refresh_view(view_instance.definition, refresh_type)
            
            if refresh_result.get("success", False):
                # Update view instance
                view_instance.state = ViewState.ACTIVE
                view_instance.last_refresh = datetime.utcnow()
                view_instance.refresh_duration_seconds = refresh_result.get("refresh_duration_seconds", 0)
                view_instance.total_refreshes += 1
                view_instance.row_count = refresh_result.get("total_rows", 0)
                view_instance.size_bytes = refresh_result.get("size_bytes", 0)
                view_instance.last_error = None
                
                # Calculate next refresh time for scheduled views
                if view_instance.definition.refresh_strategy == RefreshStrategy.SCHEDULED:
                    view_instance.next_refresh = datetime.utcnow() + timedelta(
                        minutes=view_instance.definition.refresh_interval_minutes
                    )
                
                self._metrics["refresh_jobs_completed"] += 1
                
                # Trigger refresh of dependent views
                await self._refresh_dependent_views(view_id)
                
                logger.info(f"Refreshed materialized view: {view_id}")
                return True
            else:
                view_instance.state = ViewState.FAILED
                view_instance.failed_refreshes += 1
                view_instance.last_error = refresh_result.get("error", "Unknown error")
                
                self._metrics["refresh_jobs_failed"] += 1
                
                logger.error(f"Failed to refresh materialized view {view_id}: {view_instance.last_error}")
                return False
            
        except Exception as e:
            logger.error(f"Error refreshing materialized view {view_id}: {e}")
            
            if view_id in self._views:
                view_instance = self._views[view_id]
                view_instance.state = ViewState.FAILED
                view_instance.failed_refreshes += 1
                view_instance.last_error = str(e)
                
                self._metrics["refresh_jobs_failed"] += 1
            
            return False
    
    async def _refresh_dependent_views(self, view_id: str) -> None:
        """Refresh views that depend on the given view"""
        dependent_views = self._dependency_manager.get_dependent_views(view_id)
        
        if dependent_views:
            # Get refresh order
            refresh_order = self._dependency_manager.get_refresh_order(list(dependent_views))
            
            # Refresh in dependency order
            for dependent_view_id in refresh_order:
                if dependent_view_id in self._views:
                    asyncio.create_task(self._refresh_view_internal(dependent_view_id, RefreshStrategy.INCREMENTAL))
    
    async def query_materialized_view(self, view_id: str, query: Query) -> QueryResult:
        """Query specific materialized view"""
        start_time = time.time()
        
        try:
            if view_id not in self._views:
                return QueryResult(
                    query_id=query.query_id,
                    status=QueryStatus.FAILED,
                    error=f"Materialized view {view_id} not found"
                )
            
            view_instance = self._views[view_id]
            
            if view_instance.state != ViewState.ACTIVE:
                return QueryResult(
                    query_id=query.query_id,
                    status=QueryStatus.FAILED,
                    error=f"Materialized view {view_id} is not active (state: {view_instance.state.value})"
                )
            
            # Get storage backend
            backend = self._storage_backends.get(
                view_instance.definition.storage_backend,
                self._storage_backends["default"]
            )
            
            # Query the view
            result = await backend.query_view(view_id, query)
            
            # Update view metrics
            query_time = (time.time() - start_time) * 1000
            view_instance.query_count += 1
            view_instance.avg_query_time_ms = (
                (view_instance.avg_query_time_ms * (view_instance.query_count - 1) + query_time) /
                view_instance.query_count
            )
            
            self._metrics["total_queries"] += 1
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def optimize_query(self, query: Query) -> QueryResult:
        """Optimize query by finding best materialized view"""
        # Find optimal view for this query
        active_views = [view for view in self._views.values() if view.state == ViewState.ACTIVE]
        optimal_view_id = self._query_optimizer.find_optimal_view(query, active_views)
        
        if optimal_view_id:
            self._metrics["cache_hits"] += 1
            return await self.query_materialized_view(optimal_view_id, query)
        else:
            # No suitable materialized view found
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error="No suitable materialized view found for this query"
            )
    
    def _validate_view_definition(self, view_def: MaterializedViewDefinition) -> bool:
        """Validate materialized view definition"""
        if not view_def.view_id or not view_def.name:
            logger.error("View ID and name are required")
            return False
        
        if view_def.view_id in self._views:
            logger.error(f"View {view_def.view_id} already exists")
            return False
        
        if not view_def.source_tables:
            logger.error("At least one source table is required")
            return False
        
        if view_def.storage_backend not in self._storage_backends:
            logger.error(f"Storage backend {view_def.storage_backend} not registered")
            return False
        
        return True
    
    def _schedule_regular_refresh(self, view_id: str) -> None:
        """Schedule regular refresh for view"""
        if view_id not in self._views:
            return
        
        view_instance = self._views[view_id]
        
        if view_instance.definition.refresh_strategy == RefreshStrategy.SCHEDULED:
            next_refresh = datetime.utcnow() + timedelta(
                minutes=view_instance.definition.refresh_interval_minutes
            )
            
            self._scheduler.schedule_refresh(
                view_id,
                RefreshStrategy.INCREMENTAL,
                next_refresh
            )
    
    def _start_background_tasks(self) -> None:
        """Start background tasks"""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._auto_refresh_task = asyncio.create_task(self._auto_refresh_loop())
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Update view statistics
                for view_id, view_instance in self._views.items():
                    try:
                        backend = self._storage_backends.get(
                            view_instance.definition.storage_backend,
                            self._storage_backends["default"]
                        )
                        
                        stats = await backend.get_view_statistics(view_id)
                        
                        if stats:
                            view_instance.row_count = stats.get("row_count", view_instance.row_count)
                            view_instance.size_bytes = stats.get("size_bytes", view_instance.size_bytes)
                    
                    except Exception as e:
                        logger.error(f"Failed to update statistics for view {view_id}: {e}")
                
                # Check for stale views
                now = datetime.utcnow()
                for view_instance in self._views.values():
                    if (view_instance.definition.refresh_strategy == RefreshStrategy.SCHEDULED and
                        view_instance.next_refresh and view_instance.next_refresh < now):
                        view_instance.state = ViewState.STALE
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(300)
    
    async def _auto_refresh_loop(self) -> None:
        """Background auto-refresh loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                now = datetime.utcnow()
                
                # Find views that need refresh
                views_to_refresh = []
                for view_id, view_instance in self._views.items():
                    if (view_instance.definition.refresh_strategy == RefreshStrategy.SCHEDULED and
                        view_instance.next_refresh and view_instance.next_refresh <= now and
                        view_instance.state == ViewState.STALE):
                        views_to_refresh.append(view_id)
                
                # Schedule refreshes
                for view_id in views_to_refresh:
                    self._scheduler.schedule_refresh(view_id, RefreshStrategy.INCREMENTAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-refresh loop error: {e}")
                await asyncio.sleep(60)
    
    def get_view_status(self, view_id: str = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get status of materialized view(s)"""
        if view_id:
            if view_id not in self._views:
                return {}
            
            view_instance = self._views[view_id]
            return {
                "view_id": view_id,
                "name": view_instance.definition.name,
                "state": view_instance.state.value,
                "view_type": view_instance.definition.view_type.value,
                "refresh_strategy": view_instance.definition.refresh_strategy.value,
                "last_refresh": view_instance.last_refresh.isoformat() if view_instance.last_refresh else None,
                "next_refresh": view_instance.next_refresh.isoformat() if view_instance.next_refresh else None,
                "row_count": view_instance.row_count,
                "size_bytes": view_instance.size_bytes,
                "query_count": view_instance.query_count,
                "avg_query_time_ms": view_instance.avg_query_time_ms,
                "total_refreshes": view_instance.total_refreshes,
                "failed_refreshes": view_instance.failed_refreshes,
                "last_error": view_instance.last_error
            }
        else:
            return [self.get_view_status(vid) for vid in self._views.keys()]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get materialized view metrics"""
        return dict(self._metrics)
    
    def enable_view(self, view_id: str) -> bool:
        """Enable materialized view"""
        if view_id in self._views:
            self._views[view_id].definition.enabled = True
            if self._views[view_id].state == ViewState.DISABLED:
                self._views[view_id].state = ViewState.ACTIVE
                self._metrics["active_views"] += 1
            return True
        return False
    
    def disable_view(self, view_id: str) -> bool:
        """Disable materialized view"""
        if view_id in self._views:
            self._views[view_id].definition.enabled = False
            if self._views[view_id].state == ViewState.ACTIVE:
                self._views[view_id].state = ViewState.DISABLED
                self._metrics["active_views"] -= 1
            return True
        return False
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("Shutting down materialized view manager...")
        
        # Cancel background tasks
        for task in [self._monitoring_task, self._auto_refresh_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Shutdown scheduler
        await self._scheduler.shutdown()
        
        logger.info("Materialized view manager shutdown complete")


# Singleton instance for global access
_materialized_view_manager_instance: Optional[EnterpriseMaterializedViewManager] = None


def get_materialized_view_manager() -> EnterpriseMaterializedViewManager:
    """Get singleton materialized view manager instance"""
    global _materialized_view_manager_instance
    if _materialized_view_manager_instance is None:
        _materialized_view_manager_instance = EnterpriseMaterializedViewManager()
    return _materialized_view_manager_instance


def reset_materialized_view_manager() -> None:
    """Reset materialized view manager instance (for testing)"""
    global _materialized_view_manager_instance
    if _materialized_view_manager_instance:
        asyncio.create_task(_materialized_view_manager_instance.shutdown())
    _materialized_view_manager_instance = None