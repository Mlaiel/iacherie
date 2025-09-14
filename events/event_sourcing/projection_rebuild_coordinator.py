"""Projection Rebuild Coordinator - Enterprise Implementation

Advanced projection rebuild coordinator for managing read model reconstruction
with parallel processing, incremental updates, and consistency validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Type, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from uuid import uuid4
import time

from . import DomainEvent, EventStoreInterface

logger = logging.getLogger(__name__)


class ProjectionType(Enum):
    """Types of projections"""
    AGGREGATE_VIEW = "aggregate_view"  # Single aggregate view
    CROSS_AGGREGATE = "cross_aggregate"  # Multiple aggregates
    ANALYTICS = "analytics"  # Analytics/reporting
    SEARCH_INDEX = "search_index"  # Search indexing
    MATERIALIZED_VIEW = "materialized_view"  # Database views
    CACHE = "cache"  # Cache projections


class RebuildStrategy(Enum):
    """Projection rebuild strategies"""
    FULL_REBUILD = "full_rebuild"  # Complete rebuild from scratch
    INCREMENTAL = "incremental"  # Incremental updates only
    HYBRID = "hybrid"  # Combination of full and incremental
    PARALLEL = "parallel"  # Parallel processing
    BATCH = "batch"  # Batch processing


class ProjectionStatus(Enum):
    """Projection status"""
    ACTIVE = "active"
    REBUILDING = "rebuilding"
    STALE = "stale"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class ProjectionDefinition:
    """Defines a projection"""
    projection_id: str
    name: str
    description: str
    projection_type: ProjectionType
    event_types: List[str]
    aggregate_types: Optional[List[str]] = None
    version: str = "1.0.0"
    enabled: bool = True
    
    # Rebuild configuration
    rebuild_strategy: RebuildStrategy = RebuildStrategy.INCREMENTAL
    batch_size: int = 1000
    parallel_workers: int = 4
    checkpoint_interval: int = 5000
    
    # Performance settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_compression: bool = False
    
    # Business rules
    consistency_requirements: str = "eventual"  # eventual, strong
    retention_days: int = 365
    custom_filters: List[str] = field(default_factory=list)


@dataclass
class ProjectionMetrics:
    """Projection performance metrics"""
    total_events_processed: int = 0
    events_per_second: float = 0.0
    current_position: str = ""
    last_processed_event: Optional[str] = None
    last_update_time: Optional[datetime] = None
    lag_seconds: float = 0.0
    error_count: int = 0
    rebuild_count: int = 0
    cache_hit_ratio: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_events_processed": self.total_events_processed,
            "events_per_second": self.events_per_second,
            "current_position": self.current_position,
            "last_processed_event": self.last_processed_event,
            "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None,
            "lag_seconds": self.lag_seconds,
            "error_count": self.error_count,
            "rebuild_count": self.rebuild_count,
            "cache_hit_ratio": self.cache_hit_ratio
        }


@dataclass
class RebuildJob:
    """Represents a projection rebuild job"""
    job_id: str
    projection_id: str
    strategy: RebuildStrategy
    scheduled_time: datetime
    status: str = "pending"  # pending, running, completed, failed, cancelled
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress_percentage: float = 0.0
    events_processed: int = 0
    total_events: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "projection_id": self.projection_id,
            "strategy": self.strategy.value,
            "scheduled_time": self.scheduled_time.isoformat(),
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "progress_percentage": self.progress_percentage,
            "events_processed": self.events_processed,
            "total_events": self.total_events,
            "error_message": self.error_message,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None
        }


class ProjectionCheckpoint:
    """Manages projection checkpoints"""
    
    def __init__(self, projection_id -> None: str) -> None:
        self.projection_id = projection_id
        self.checkpoints: Dict[str, Any] = {}
    
    def save_checkpoint(self, position: str, metadata: Dict[str, Any] = None) -> None:
        """Save checkpoint"""
        self.checkpoints[position] = {
            "position": position,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
    
    def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Get latest checkpoint"""
        if not self.checkpoints:
            return None
        
        latest_key = max(self.checkpoints.keys(), key=lambda k: self.checkpoints[k]["timestamp"])
        return self.checkpoints[latest_key]
    
    def clear_checkpoints(self) -> None:
        """Clear all checkpoints"""
        self.checkpoints.clear()


class ProjectionHandler(ABC):
    """Abstract projection handler"""
    
    @abstractmethod
    async def handle_event(self, event: DomainEvent) -> bool:
        """Handle a single event"""
        pass
    
    @abstractmethod
    async def handle_batch(self, events: List[DomainEvent]) -> int:
        """Handle batch of events"""
        pass
    
    @abstractmethod
    async def rebuild_projection(self, events: List[DomainEvent]) -> bool:
        """Rebuild entire projection"""
        pass
    
    @abstractmethod
    async def validate_consistency(self) -> bool:
        """Validate projection consistency"""
        pass
    
    @abstractmethod
    async def get_current_state(self) -> Dict[str, Any]:
        """Get current projection state"""
        pass


class AggregateViewProjection(ProjectionHandler):
    """Simple aggregate view projection"""
    
    def __init__(self, projection_id -> None: str) -> None:
        self.projection_id = projection_id
        self.aggregate_views: Dict[str, Dict[str, Any]] = {}
        self.processed_events: Set[str] = set()
    
    async def handle_event(self, event: DomainEvent) -> bool:
        """Handle single event"""
        try:
            if event.event_id in self.processed_events:
                return True  # Already processed
            
            # Update aggregate view
            if event.aggregate_id not in self.aggregate_views:
                self.aggregate_views[event.aggregate_id] = {
                    "aggregate_id": event.aggregate_id,
                    "aggregate_type": event.aggregate_type,
                    "version": 0,
                    "last_updated": None,
                    "event_count": 0,
                    "data": {}
                }
            
            view = self.aggregate_views[event.aggregate_id]
            view["version"] = max(view["version"], event.event_version)
            view["last_updated"] = event.occurred_at.isoformat()
            view["event_count"] += 1
            
            # Apply event to view data
            if event.event_type == "ContentCreated":
                view["data"]["content_type"] = event.event_data.get("content_type")
                view["data"]["creator_id"] = event.event_data.get("creator_id")
            elif event.event_type == "ContentUpdated":
                view["data"].update(event.event_data)
            
            self.processed_events.add(event.event_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle event {event.event_id}: {e}")
            return False
    
    async def handle_batch(self, events: List[DomainEvent]) -> int:
        """Handle batch of events"""
        processed_count = 0
        
        for event in events:
            if await self.handle_event(event):
                processed_count += 1
        
        return processed_count
    
    async def rebuild_projection(self, events: List[DomainEvent]) -> bool:
        """Rebuild entire projection"""
        try:
            # Clear existing state
            self.aggregate_views.clear()
            self.processed_events.clear()
            
            # Process all events
            await self.handle_batch(events)
            
            return True
        except Exception as e:
            logger.error(f"Failed to rebuild projection: {e}")
            return False
    
    async def validate_consistency(self) -> bool:
        """Validate projection consistency"""
        try:
            # Basic validation - check that all views have required fields
            for aggregate_id, view in self.aggregate_views.items():
                if not view.get("aggregate_id") or view.get("version", 0) < 1:
                    logger.warning(f"Inconsistent view for aggregate {aggregate_id}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Consistency validation failed: {e}")
            return False
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get current projection state"""
        return {
            "projection_id": self.projection_id,
            "aggregate_count": len(self.aggregate_views),
            "processed_events": len(self.processed_events),
            "aggregates": self.aggregate_views
        }


class SearchIndexProjection(ProjectionHandler):
    """Search index projection"""
    
    def __init__(self, projection_id -> None: str) -> None:
        self.projection_id = projection_id
        self.search_documents: Dict[str, Dict[str, Any]] = {}
        self.indexed_events: Set[str] = set()
    
    async def handle_event(self, event: DomainEvent) -> bool:
        """Handle single event for search indexing"""
        try:
            if event.event_id in self.indexed_events:
                return True
            
            # Create search document
            doc_id = f"{event.aggregate_id}_{event.event_type}"
            
            if doc_id not in self.search_documents:
                self.search_documents[doc_id] = {
                    "id": doc_id,
                    "aggregate_id": event.aggregate_id,
                    "aggregate_type": event.aggregate_type,
                    "content": [],
                    "tags": set(),
                    "last_updated": event.occurred_at.isoformat()
                }
            
            doc = self.search_documents[doc_id]
            
            # Extract searchable content
            if event.event_type in ["ContentCreated", "ContentUpdated"]:
                title = event.event_data.get("title", "")
                description = event.event_data.get("description", "")
                tags = event.event_data.get("tags", [])
                
                if title:
                    doc["content"].append(title)
                if description:
                    doc["content"].append(description)
                if tags:
                    doc["tags"].update(tags)
                
                doc["last_updated"] = event.occurred_at.isoformat()
            
            self.indexed_events.add(event.event_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to index event {event.event_id}: {e}")
            return False
    
    async def handle_batch(self, events: List[DomainEvent]) -> int:
        """Handle batch of events"""
        processed_count = 0
        
        for event in events:
            if await self.handle_event(event):
                processed_count += 1
        
        return processed_count
    
    async def rebuild_projection(self, events: List[DomainEvent]) -> bool:
        """Rebuild search index"""
        try:
            self.search_documents.clear()
            self.indexed_events.clear()
            
            await self.handle_batch(events)
            
            return True
        except Exception as e:
            logger.error(f"Failed to rebuild search index: {e}")
            return False
    
    async def validate_consistency(self) -> bool:
        """Validate search index consistency"""
        try:
            # Check that all documents have required fields
            for doc_id, doc in self.search_documents.items():
                if not doc.get("aggregate_id") or not doc.get("id"):
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Search index validation failed: {e}")
            return False
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get current search index state"""
        return {
            "projection_id": self.projection_id,
            "document_count": len(self.search_documents),
            "indexed_events": len(self.indexed_events),
            "documents": {
                doc_id: {
                    "id": doc["id"],
                    "aggregate_id": doc["aggregate_id"],
                    "content_length": len(" ".join(doc["content"])),
                    "tag_count": len(doc["tags"]),
                    "last_updated": doc["last_updated"]
                } for doc_id, doc in self.search_documents.items()
            }
        }


class ProjectionRegistry:
    """Registry for managing projection definitions and handlers"""
    
    def __init__(self) -> None:
        self.projections: Dict[str, ProjectionDefinition] = {}
        self.handlers: Dict[str, ProjectionHandler] = {}
        self.metrics: Dict[str, ProjectionMetrics] = {}
        self.checkpoints: Dict[str, ProjectionCheckpoint] = {}
    
    def register_projection(self, definition: ProjectionDefinition, 
                          handler: ProjectionHandler) -> None:
        """Register a projection"""
        self.projections[definition.projection_id] = definition
        self.handlers[definition.projection_id] = handler
        self.metrics[definition.projection_id] = ProjectionMetrics()
        self.checkpoints[definition.projection_id] = ProjectionCheckpoint(definition.projection_id)
        
        logger.info(f"Registered projection: {definition.name}")
    
    def unregister_projection(self, projection_id: str) -> bool:
        """Unregister a projection"""
        if projection_id in self.projections:
            del self.projections[projection_id]
            del self.handlers[projection_id]
            del self.metrics[projection_id]
            del self.checkpoints[projection_id]
            return True
        return False
    
    def get_projection(self, projection_id: str) -> Optional[ProjectionDefinition]:
        """Get projection definition"""
        return self.projections.get(projection_id)
    
    def get_handler(self, projection_id: str) -> Optional[ProjectionHandler]:
        """Get projection handler"""
        return self.handlers.get(projection_id)
    
    def get_metrics(self, projection_id: str) -> Optional[ProjectionMetrics]:
        """Get projection metrics"""
        return self.metrics.get(projection_id)
    
    def get_checkpoint(self, projection_id: str) -> Optional[ProjectionCheckpoint]:
        """Get projection checkpoint"""
        return self.checkpoints.get(projection_id)
    
    def list_projections(self, enabled_only: bool = False) -> List[ProjectionDefinition]:
        """List all projections"""
        projections = list(self.projections.values())
        if enabled_only:
            projections = [p for p in projections if p.enabled]
        return projections
    
    def get_projections_for_event_type(self, event_type: str) -> List[str]:
        """Get projections that handle specific event type"""
        matching_projections = []
        
        for projection_id, definition in self.projections.items():
            if definition.enabled and event_type in definition.event_types:
                matching_projections.append(projection_id)
        
        return matching_projections


class ProjectionRebuildCoordinator:
    """Enterprise projection rebuild coordinator"""
    
    def __init__(self, event_store -> None: EventStoreInterface) -> None:
        self.event_store = event_store
        self.registry = ProjectionRegistry()
        self.rebuild_jobs: List[RebuildJob] = []
        self.active_jobs: Dict[str, asyncio.Task] = {}
        
        # Configuration
        self.max_concurrent_rebuilds = 4
        self.default_batch_size = 1000
        self.rebuild_timeout_hours = 24
        
        # Initialize default projections
        self._initialize_default_projections()
    
    def _initialize_default_projections(self) -> None:
        """Initialize default projections"""
        # Aggregate view projection
        aggregate_def = ProjectionDefinition(
            projection_id="aggregate_views",
            name="Aggregate Views",
            description="Materialized views of aggregate states",
            projection_type=ProjectionType.AGGREGATE_VIEW,
            event_types=["ContentCreated", "ContentUpdated", "ContentDeleted"],
            rebuild_strategy=RebuildStrategy.INCREMENTAL
        )
        
        aggregate_handler = AggregateViewProjection("aggregate_views")
        self.registry.register_projection(aggregate_def, aggregate_handler)
        
        # Search index projection
        search_def = ProjectionDefinition(
            projection_id="search_index",
            name="Search Index",
            description="Search index for content discovery",
            projection_type=ProjectionType.SEARCH_INDEX,
            event_types=["ContentCreated", "ContentUpdated", "TagsAdded"],
            rebuild_strategy=RebuildStrategy.BATCH
        )
        
        search_handler = SearchIndexProjection("search_index")
        self.registry.register_projection(search_def, search_handler)
    
    def register_projection(self, definition: ProjectionDefinition, 
                          handler: ProjectionHandler) -> None:
        """Register a new projection"""
        self.registry.register_projection(definition, handler)
    
    async def process_event(self, event: DomainEvent) -> Dict[str, bool]:
        """Process event through relevant projections"""
        results = {}
        
        # Find projections that handle this event type
        projection_ids = self.registry.get_projections_for_event_type(event.event_type)
        
        for projection_id in projection_ids:
            handler = self.registry.get_handler(projection_id)
            metrics = self.registry.get_metrics(projection_id)
            
            if handler and metrics:
                try:
                    start_time = time.time()
                    success = await handler.handle_event(event)
                    processing_time = time.time() - start_time
                    
                    # Update metrics
                    if success:
                        metrics.total_events_processed += 1
                        metrics.last_processed_event = event.event_id
                        metrics.last_update_time = datetime.now(timezone.utc)
                        metrics.events_per_second = 1.0 / max(processing_time, 0.001)
                    else:
                        metrics.error_count += 1
                    
                    results[projection_id] = success
                    
                except Exception as e:
                    logger.error(f"Failed to process event in projection {projection_id}: {e}")
                    metrics.error_count += 1
                    results[projection_id] = False
        
        return results
    
    async def schedule_rebuild(self, projection_id: str, 
                             strategy: RebuildStrategy = None) -> RebuildJob:
        """Schedule projection rebuild"""
        definition = self.registry.get_projection(projection_id)
        if not definition:
            raise ValueError(f"Projection {projection_id} not found")
        
        # Create rebuild job
        job = RebuildJob(
            job_id=str(uuid4()),
            projection_id=projection_id,
            strategy=strategy or definition.rebuild_strategy,
            scheduled_time=datetime.now(timezone.utc)
        )
        
        self.rebuild_jobs.append(job)
        logger.info(f"Scheduled rebuild for projection {projection_id}")
        
        return job
    
    async def execute_rebuild(self, job_id: str) -> RebuildJob:
        """Execute projection rebuild"""
        # Find job
        job = None
        for rebuild_job in self.rebuild_jobs:
            if rebuild_job.job_id == job_id:
                job = rebuild_job
                break
        
        if not job:
            raise ValueError(f"Rebuild job {job_id} not found")
        
        # Check if already running
        if job_id in self.active_jobs:
            raise ValueError(f"Rebuild job {job_id} is already running")
        
        # Execute rebuild
        task = asyncio.create_task(self._execute_rebuild_task(job))
        self.active_jobs[job_id] = task
        
        try:
            await task
        except Exception as e:
            logger.error(f"Rebuild job {job_id} failed: {e}")
        finally:
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
        
        return job
    
    async def _execute_rebuild_task(self, job: RebuildJob) -> None:
        """Execute rebuild task"""
        job.status = "running"
        job.start_time = datetime.now(timezone.utc)
        
        try:
            definition = self.registry.get_projection(job.projection_id)
            handler = self.registry.get_handler(job.projection_id)
            metrics = self.registry.get_metrics(job.projection_id)
            
            if not definition or not handler or not metrics:
                raise ValueError(f"Projection {job.projection_id} not properly configured")
            
            # Get events to process
            if job.strategy == RebuildStrategy.FULL_REBUILD:
                events = await self._get_all_events_for_projection(definition)
            elif job.strategy == RebuildStrategy.INCREMENTAL:
                events = await self._get_incremental_events_for_projection(definition)
            else:
                events = await self._get_all_events_for_projection(definition)
            
            job.total_events = len(events)
            
            if job.strategy == RebuildStrategy.PARALLEL:
                await self._execute_parallel_rebuild(job, definition, handler, events)
            elif job.strategy == RebuildStrategy.BATCH:
                await self._execute_batch_rebuild(job, definition, handler, events)
            else:
                await self._execute_sequential_rebuild(job, definition, handler, events)
            
            # Validate consistency
            if await handler.validate_consistency():
                job.status = "completed"
                metrics.rebuild_count += 1
            else:
                job.status = "failed"
                job.error_message = "Consistency validation failed"
                
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            logger.error(f"Rebuild job {job.job_id} failed: {e}")
        finally:
            job.end_time = datetime.now(timezone.utc)
            job.progress_percentage = 100.0
    
    async def _execute_sequential_rebuild(self, job: RebuildJob, 
                                        definition: ProjectionDefinition,
                                        handler: ProjectionHandler, 
                                        events: List[DomainEvent]) -> None:
        """Execute sequential rebuild"""
        if job.strategy == RebuildStrategy.FULL_REBUILD:
            success = await handler.rebuild_projection(events)
            if not success:
                raise Exception("Full rebuild failed")
            job.events_processed = len(events)
            job.progress_percentage = 100.0
        else:
            # Process events one by one
            for i, event in enumerate(events):
                await handler.handle_event(event)
                job.events_processed = i + 1
                job.progress_percentage = (i + 1) / len(events) * 100
                
                # Save checkpoint periodically
                if i % definition.checkpoint_interval == 0:
                    checkpoint = self.registry.get_checkpoint(job.projection_id)
                    if checkpoint:
                        checkpoint.save_checkpoint(
                            position=str(i),
                            metadata={"event_id": event.event_id}
                        )
    
    async def _execute_batch_rebuild(self, job: RebuildJob,
                                    definition: ProjectionDefinition,
                                    handler: ProjectionHandler,
                                    events: List[DomainEvent]) -> None:
        """Execute batch rebuild"""
        batch_size = definition.batch_size
        total_batches = (len(events) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(events))
            batch = events[start_idx:end_idx]
            
            processed_count = await handler.handle_batch(batch)
            job.events_processed += processed_count
            job.progress_percentage = (batch_idx + 1) / total_batches * 100
            
            # Save checkpoint
            checkpoint = self.registry.get_checkpoint(job.projection_id)
            if checkpoint:
                checkpoint.save_checkpoint(
                    position=str(end_idx),
                    metadata={"batch_index": batch_idx}
                )
    
    async def _execute_parallel_rebuild(self, job: RebuildJob,
                                       definition: ProjectionDefinition,
                                       handler: ProjectionHandler,
                                       events: List[DomainEvent]) -> None:
        """Execute parallel rebuild"""
        worker_count = definition.parallel_workers
        chunk_size = len(events) // worker_count
        
        async def process_chunk(chunk: List[DomainEvent], chunk_idx: int) -> int:
            processed = 0
            for event in chunk:
                if await handler.handle_event(event):
                    processed += 1
            return processed
        
        # Create chunks
        chunks = []
        for i in range(worker_count):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < worker_count - 1 else len(events)
            chunks.append(events[start_idx:end_idx])
        
        # Process chunks in parallel
        tasks = [process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        results = await asyncio.gather(*tasks)
        
        job.events_processed = sum(results)
        job.progress_percentage = 100.0
    
    async def _get_all_events_for_projection(self, definition: ProjectionDefinition) -> List[DomainEvent]:
        """Get all events relevant to projection"""
        all_events = await self.event_store.get_all_events(limit=100000)  # Large limit
        
        # Filter by event types
        filtered_events = [
            event for event in all_events 
            if event.event_type in definition.event_types
        ]
        
        # Filter by aggregate types if specified
        if definition.aggregate_types:
            filtered_events = [
                event for event in filtered_events
                if event.aggregate_type in definition.aggregate_types
            ]
        
        return filtered_events
    
    async def _get_incremental_events_for_projection(self, definition: ProjectionDefinition) -> List[DomainEvent]:
        """Get incremental events for projection"""
        # Get checkpoint
        checkpoint = self.registry.get_checkpoint(definition.projection_id)
        latest_checkpoint = checkpoint.get_latest_checkpoint() if checkpoint else None
        
        # Get events from checkpoint
        from_event_id = None
        if latest_checkpoint:
            from_event_id = latest_checkpoint.get("metadata", {}).get("event_id")
        
        # Get all events and filter
        all_events = await self.event_store.get_all_events(from_event_id=from_event_id, limit=100000)
        
        # Filter by event types and aggregate types
        filtered_events = [
            event for event in all_events
            if event.event_type in definition.event_types
        ]
        
        if definition.aggregate_types:
            filtered_events = [
                event for event in filtered_events
                if event.aggregate_type in definition.aggregate_types
            ]
        
        return filtered_events
    
    async def rebuild_all_projections(self, strategy: RebuildStrategy = None) -> List[RebuildJob]:
        """Rebuild all enabled projections"""
        projections = self.registry.list_projections(enabled_only=True)
        jobs = []
        
        for definition in projections:
            job = await self.schedule_rebuild(definition.projection_id, strategy)
            jobs.append(job)
        
        # Execute rebuilds with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent_rebuilds)
        
        async def execute_with_semaphore(job -> None: RebuildJob) -> None:
            async with semaphore:
                return await self.execute_rebuild(job.job_id)
        
        # Execute all jobs
        tasks = [execute_with_semaphore(job) for job in jobs]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return jobs
    
    async def validate_all_projections(self) -> Dict[str, bool]:
        """Validate consistency of all projections"""
        results = {}
        projections = self.registry.list_projections(enabled_only=True)
        
        for definition in projections:
            handler = self.registry.get_handler(definition.projection_id)
            if handler:
                try:
                    results[definition.projection_id] = await handler.validate_consistency()
                except Exception as e:
                    logger.error(f"Validation failed for {definition.projection_id}: {e}")
                    results[definition.projection_id] = False
            else:
                results[definition.projection_id] = False
        
        return results
    
    def get_projection_status(self, projection_id: str) -> Dict[str, Any]:
        """Get detailed projection status"""
        definition = self.registry.get_projection(projection_id)
        metrics = self.registry.get_metrics(projection_id)
        handler = self.registry.get_handler(projection_id)
        
        if not definition or not metrics or not handler:
            return {"error": "Projection not found"}
        
        # Calculate lag
        lag_seconds = 0.0
        if metrics.last_update_time:
            lag_seconds = (datetime.now(timezone.utc) - metrics.last_update_time).total_seconds()
        
        # Determine status
        status = ProjectionStatus.ACTIVE
        if lag_seconds > 3600:  # 1 hour lag
            status = ProjectionStatus.STALE
        if metrics.error_count > 10:
            status = ProjectionStatus.ERROR
        if not definition.enabled:
            status = ProjectionStatus.DISABLED
        
        # Check if rebuilding
        for job in self.rebuild_jobs:
            if job.projection_id == projection_id and job.status == "running":
                status = ProjectionStatus.REBUILDING
                break
        
        return {
            "projection_id": projection_id,
            "name": definition.name,
            "type": definition.projection_type.value,
            "status": status.value,
            "enabled": definition.enabled,
            "metrics": metrics.to_dict(),
            "lag_seconds": lag_seconds,
            "last_rebuild": None,  # Would track from job history
            "version": definition.version
        }
    
    def get_all_projection_status(self) -> List[Dict[str, Any]]:
        """Get status of all projections"""
        projections = self.registry.list_projections()
        return [self.get_projection_status(p.projection_id) for p in projections]
    
    def get_rebuild_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent rebuild jobs"""
        recent_jobs = self.rebuild_jobs[-limit:] if limit > 0 else self.rebuild_jobs
        return [job.to_dict() for job in recent_jobs]
    
    async def cancel_rebuild(self, job_id: str) -> bool:
        """Cancel running rebuild job"""
        if job_id in self.active_jobs:
            task = self.active_jobs[job_id]
            task.cancel()
            
            # Update job status
            for job in self.rebuild_jobs:
                if job.job_id == job_id:
                    job.status = "cancelled"
                    job.end_time = datetime.now(timezone.utc)
                    break
            
            return True
        
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check coordinator health"""
        try:
            projections = self.registry.list_projections(enabled_only=True)
            healthy_projections = 0
            
            for definition in projections:
                handler = self.registry.get_handler(definition.projection_id)
                if handler:
                    try:
                        await handler.validate_consistency()
                        healthy_projections += 1
                    except:
                        pass
            
            return {
                "healthy": healthy_projections == len(projections),
                "total_projections": len(projections),
                "healthy_projections": healthy_projections,
                "active_rebuilds": len(self.active_jobs),
                "pending_jobs": len([j for j in self.rebuild_jobs if j.status == "pending"])
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"healthy": False, "error": str(e)}