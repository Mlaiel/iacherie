"""🚀 Enterprise Read Model Projector - CQRS Architecture
======================================================
Module: events/cqrs/read_model_projector.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE READ MODEL PROJECTOR
Advanced event projection to optimized read models
- Multi-storage read model projection (SQL, NoSQL, Search, Cache)
- Real-time and batch projection modes
- Event replay and read model rebuilding
- Schema evolution and migration support
- Conflict resolution and eventual consistency
- Performance optimization and monitoring
"""

import asyncio
import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Union, Type, TypeVar, Generic
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import hashlib

from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ProjectionMode(Enum):
    """Projection processing modes"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    HYBRID = "hybrid"
    REPLAY = "replay"


class ReadModelType(Enum):
    """Read model storage types"""
    RELATIONAL = "relational"
    DOCUMENT = "document"
    KEY_VALUE = "key_value"
    SEARCH_INDEX = "search_index"
    GRAPH = "graph"
    TIME_SERIES = "time_series"
    CACHE = "cache"


class ProjectionState(Enum):
    """Projection processing state"""
    ACTIVE = "active"
    PAUSED = "paused"
    REBUILDING = "rebuilding"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class ReadModelSchema:
    """Schema definition for read model"""
    schema_id: str
    version: str
    model_type: ReadModelType
    fields: Dict[str, Any] = field(default_factory=dict)
    indexes: List[str] = field(default_factory=list)
    partitioning: Optional[Dict[str, Any]] = None
    constraints: List[str] = field(default_factory=list)
    migrations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectionDefinition:
    """Definition of event-to-read-model projection"""
    projection_id: str
    name: str
    event_types: List[str]
    read_model_name: str
    read_model_schema: ReadModelSchema
    projection_mode: ProjectionMode = ProjectionMode.REAL_TIME
    batch_size: int = 100
    batch_interval_seconds: int = 60
    checkpoint_interval: int = 1000
    max_retries: int = 3
    timeout_seconds: int = 30
    parallel_processing: bool = True
    max_parallel_workers: int = 5
    conflict_resolution_strategy: str = "last_writer_wins"
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectionCheckpoint:
    """Projection processing checkpoint"""
    projection_id: str
    last_processed_event_id: str
    last_processed_timestamp: datetime
    processed_event_count: int = 0
    last_checkpoint_time: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectionMetrics:
    """Metrics for projection performance"""
    projection_id: str
    events_processed: int = 0
    events_failed: int = 0
    last_processing_time_ms: float = 0.0
    average_processing_time_ms: float = 0.0
    throughput_events_per_second: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    lag_seconds: float = 0.0
    error_rate_percent: float = 0.0


class EventProjector:
    """Base class for event projectors"""
    
    def __init__(self, projection_definition -> None: ProjectionDefinition) -> None:
        self.projection_definition = projection_definition
        self.schema = projection_definition.read_model_schema
    
    async def project_event(self, event: BaseEvent, read_model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Project event to read model data"""
        raise NotImplementedError
    
    async def handle_event_replay(self, events: List[BaseEvent]) -> Dict[str, Any]:
        """Handle batch event replay for read model rebuild"""
        result_data = {}
        
        for event in events:
            try:
                result_data = await self.project_event(event, result_data)
            except Exception as e:
                logger.error(f"Event replay failed for event {event.event_id}: {e}")
                raise
        
        return result_data
    
    def get_read_model_key(self, event: BaseEvent) -> str:
        """Generate read model key from event"""
        # Default implementation uses aggregate_id or event_id
        return event.aggregate_id or event.event_id
    
    def should_process_event(self, event: BaseEvent) -> bool:
        """Determine if event should be processed by this projector"""
        return event.event_type in self.projection_definition.event_types


class ReadModelStore:
    """Abstract read model storage interface"""
    
    def __init__(self, store_config -> None: Dict[str, Any]) -> None:
        self.store_config = store_config
        self.store_type = ReadModelType(store_config.get("type", "document"))
    
    async def save_read_model(self, model_name: str, key: str, data: Dict[str, Any], 
                            metadata: Dict[str, Any] = None) -> bool:
        """Save read model data"""
        raise NotImplementedError
    
    async def get_read_model(self, model_name: str, key: str) -> Optional[Dict[str, Any]]:
        """Get read model data"""
        raise NotImplementedError
    
    async def delete_read_model(self, model_name: str, key: str) -> bool:
        """Delete read model data"""
        raise NotImplementedError
    
    async def query_read_models(self, model_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query read models"""
        raise NotImplementedError
    
    async def create_indexes(self, model_name: str, indexes: List[str]) -> bool:
        """Create indexes for read model"""
        raise NotImplementedError
    
    async def migrate_schema(self, model_name: str, old_schema: ReadModelSchema, 
                           new_schema: ReadModelSchema) -> bool:
        """Migrate read model schema"""
        raise NotImplementedError
    
    async def get_statistics(self, model_name: str) -> Dict[str, Any]:
        """Get read model statistics"""
        raise NotImplementedError


class InMemoryReadModelStore(ReadModelStore):
    """In-memory read model store for testing/development"""
    
    def __init__(self, store_config -> None: Dict[str, Any]) -> None:
        super().__init__(store_config)
        self._data: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        self._metadata: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    
    async def save_read_model(self, model_name: str, key: str, data: Dict[str, Any], 
                            metadata: Dict[str, Any] = None) -> bool:
        self._data[model_name][key] = data.copy()
        if metadata:
            self._metadata[model_name][key] = metadata.copy()
        return True
    
    async def get_read_model(self, model_name: str, key: str) -> Optional[Dict[str, Any]]:
        return self._data[model_name].get(key)
    
    async def delete_read_model(self, model_name: str, key: str) -> bool:
        self._data[model_name].pop(key, None)
        self._metadata[model_name].pop(key, None)
        return True
    
    async def query_read_models(self, model_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Simple query implementation for in-memory store
        results = []
        for key, data in self._data[model_name].items():
            matches = True
            for field, value in query.items():
                if field not in data or data[field] != value:
                    matches = False
                    break
            if matches:
                results.append(data)
        return results
    
    async def create_indexes(self, model_name: str, indexes: List[str]) -> bool:
        # No-op for in-memory store
        return True
    
    async def migrate_schema(self, model_name: str, old_schema: ReadModelSchema, 
                           new_schema: ReadModelSchema) -> bool:
        # Simple migration for in-memory store
        return True
    
    async def get_statistics(self, model_name: str) -> Dict[str, Any]:
        return {
            "total_documents": len(self._data[model_name]),
            "storage_size_bytes": len(json.dumps(self._data[model_name])),
            "last_updated": datetime.utcnow().isoformat()
        }


class ConflictResolver:
    """Resolve conflicts in read model updates"""
    
    def __init__(self, strategy -> None: str = "last_writer_wins") -> None:
        self.strategy = strategy
    
    async def resolve_conflict(self, existing_data: Dict[str, Any], 
                             new_data: Dict[str, Any], 
                             event: BaseEvent) -> Dict[str, Any]:
        """Resolve conflict between existing and new data"""
        
        if self.strategy == "last_writer_wins":
            return new_data
        
        elif self.strategy == "merge":
            # Deep merge strategy
            return self._deep_merge(existing_data, new_data)
        
        elif self.strategy == "timestamp_based":
            # Use event timestamp to determine winner
            existing_timestamp = existing_data.get("_last_updated", datetime.min)
            if event.timestamp > existing_timestamp:
                return new_data
            else:
                return existing_data
        
        elif self.strategy == "custom":
            # Custom conflict resolution logic can be implemented here
            return await self._custom_conflict_resolution(existing_data, new_data, event)
        
        else:
            # Default to last writer wins
            return new_data
    
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    async def _custom_conflict_resolution(self, existing_data: Dict[str, Any], 
                                        new_data: Dict[str, Any], 
                                        event: BaseEvent) -> Dict[str, Any]:
        """Custom conflict resolution logic"""
        # Implement business-specific conflict resolution here
        return new_data


class CheckpointManager:
    """Manage projection checkpoints"""
    
    def __init__(self) -> None:
        self._checkpoints: Dict[str, ProjectionCheckpoint] = {}
        self._checkpoint_store: Optional[ReadModelStore] = None
    
    def set_checkpoint_store(self, store: ReadModelStore) -> None:
        """Set persistent checkpoint store"""
        self._checkpoint_store = store
    
    async def save_checkpoint(self, checkpoint: ProjectionCheckpoint) -> bool:
        """Save projection checkpoint"""
        self._checkpoints[checkpoint.projection_id] = checkpoint
        
        if self._checkpoint_store:
            try:
                await self._checkpoint_store.save_read_model(
                    "_projection_checkpoints",
                    checkpoint.projection_id,
                    {
                        "last_processed_event_id": checkpoint.last_processed_event_id,
                        "last_processed_timestamp": checkpoint.last_processed_timestamp.isoformat(),
                        "processed_event_count": checkpoint.processed_event_count,
                        "last_checkpoint_time": checkpoint.last_checkpoint_time.isoformat(),
                        "metadata": checkpoint.metadata
                    }
                )
                return True
            except Exception as e:
                logger.error(f"Failed to persist checkpoint for {checkpoint.projection_id}: {e}")
                return False
        
        return True
    
    async def load_checkpoint(self, projection_id: str) -> Optional[ProjectionCheckpoint]:
        """Load projection checkpoint"""
        if projection_id in self._checkpoints:
            return self._checkpoints[projection_id]
        
        if self._checkpoint_store:
            try:
                checkpoint_data = await self._checkpoint_store.get_read_model(
                    "_projection_checkpoints", projection_id
                )
                
                if checkpoint_data:
                    checkpoint = ProjectionCheckpoint(
                        projection_id=projection_id,
                        last_processed_event_id=checkpoint_data["last_processed_event_id"],
                        last_processed_timestamp=datetime.fromisoformat(checkpoint_data["last_processed_timestamp"]),
                        processed_event_count=checkpoint_data.get("processed_event_count", 0),
                        last_checkpoint_time=datetime.fromisoformat(checkpoint_data["last_checkpoint_time"]),
                        metadata=checkpoint_data.get("metadata", {})
                    )
                    
                    self._checkpoints[projection_id] = checkpoint
                    return checkpoint
                    
            except Exception as e:
                logger.error(f"Failed to load checkpoint for {projection_id}: {e}")
        
        return None
    
    async def get_checkpoint(self, projection_id: str) -> Optional[ProjectionCheckpoint]:
        """Get checkpoint (load if not in memory)"""
        if projection_id not in self._checkpoints:
            return await self.load_checkpoint(projection_id)
        return self._checkpoints[projection_id]


class EnterpriseReadModelProjector:
    """Enterprise read model projector with advanced features"""
    
    def __init__(self) -> None:
        self._projections: Dict[str, ProjectionDefinition] = {}
        self._projectors: Dict[str, EventProjector] = {}
        self._read_model_stores: Dict[str, ReadModelStore] = {}
        self._checkpoint_manager = CheckpointManager()
        self._conflict_resolver = ConflictResolver()
        
        # State management
        self._projection_states: Dict[str, ProjectionState] = {}
        self._processing_tasks: Dict[str, asyncio.Task] = {}
        self._metrics: Dict[str, ProjectionMetrics] = {}
        
        # Configuration
        self._max_concurrent_projections = 10
        self._processing_semaphore = asyncio.Semaphore(self._max_concurrent_projections)
        
        # Performance monitoring
        self._performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Event queues for different projection modes
        self._real_time_queue: asyncio.Queue = asyncio.Queue()
        self._batch_queues: Dict[str, List[BaseEvent]] = defaultdict(list)
        
        # Background tasks
        self._real_time_processor_task: Optional[asyncio.Task] = None
        self._batch_processor_task: Optional[asyncio.Task] = None
        self._metrics_collector_task: Optional[asyncio.Task] = None
        
        # Start background processing
        self._start_background_tasks()
    
    def register_read_model_store(self, store_name: str, store: ReadModelStore) -> None:
        """Register read model store"""
        self._read_model_stores[store_name] = store
        
        # Set as checkpoint store if it's the first one
        if len(self._read_model_stores) == 1:
            self._checkpoint_manager.set_checkpoint_store(store)
        
        logger.info(f"Registered read model store: {store_name} ({store.store_type.value})")
    
    def register_projection(self, projection_def: ProjectionDefinition, 
                          projector: EventProjector) -> None:
        """Register event projection"""
        self._projections[projection_def.projection_id] = projection_def
        self._projectors[projection_def.projection_id] = projector
        self._projection_states[projection_def.projection_id] = ProjectionState.ACTIVE
        self._metrics[projection_def.projection_id] = ProjectionMetrics(
            projection_id=projection_def.projection_id
        )
        
        logger.info(f"Registered projection: {projection_def.projection_id} for events {projection_def.event_types}")
    
    async def project_event(self, event: BaseEvent) -> None:
        """Project single event to all applicable read models"""
        # Find applicable projections
        applicable_projections = [
            projection_id for projection_id, projection_def in self._projections.items()
            if (event.event_type in projection_def.event_types and 
                self._projection_states[projection_id] == ProjectionState.ACTIVE)
        ]
        
        if not applicable_projections:
            return
        
        # Route event based on projection mode
        for projection_id in applicable_projections:
            projection_def = self._projections[projection_id]
            
            if projection_def.projection_mode == ProjectionMode.REAL_TIME:
                await self._real_time_queue.put((projection_id, event))
            
            elif projection_def.projection_mode == ProjectionMode.BATCH:
                self._batch_queues[projection_id].append(event)
            
            elif projection_def.projection_mode == ProjectionMode.HYBRID:
                # For hybrid mode, use real-time for high-priority events
                if event.priority in [EventPriority.HIGH, EventPriority.CRITICAL]:
                    await self._real_time_queue.put((projection_id, event))
                else:
                    self._batch_queues[projection_id].append(event)
    
    async def project_events_batch(self, events: List[BaseEvent]) -> None:
        """Project batch of events"""
        for event in events:
            await self.project_event(event)
    
    async def rebuild_read_model(self, projection_id: str, events: List[BaseEvent]) -> bool:
        """Rebuild read model from event history"""
        if projection_id not in self._projections:
            raise EventValidationError(f"Unknown projection: {projection_id}")
        
        projection_def = self._projections[projection_id]
        projector = self._projectors[projection_id]
        
        # Set state to rebuilding
        original_state = self._projection_states[projection_id]
        self._projection_states[projection_id] = ProjectionState.REBUILDING
        
        try:
            # Get read model store
            store = self._get_read_model_store(projection_def)
            if not store:
                raise EventProcessingError(f"No read model store available for projection {projection_id}")
            
            # Clear existing read model data
            await self._clear_read_model(projection_def, store)
            
            # Process events in batches
            batch_size = projection_def.batch_size
            total_events = len(events)
            processed_events = 0
            
            for i in range(0, total_events, batch_size):
                batch = events[i:i + batch_size]
                
                try:
                    # Project batch of events
                    for event in batch:
                        if projector.should_process_event(event):
                            await self._process_single_event(projection_id, event, store)
                            processed_events += 1
                    
                    # Update checkpoint
                    if batch:
                        last_event = batch[-1]
                        checkpoint = ProjectionCheckpoint(
                            projection_id=projection_id,
                            last_processed_event_id=last_event.event_id,
                            last_processed_timestamp=last_event.timestamp,
                            processed_event_count=processed_events
                        )
                        await self._checkpoint_manager.save_checkpoint(checkpoint)
                    
                    logger.info(f"Rebuild progress for {projection_id}: {processed_events}/{total_events} events")
                    
                except Exception as e:
                    logger.error(f"Batch processing failed during rebuild: {e}")
                    self._projection_states[projection_id] = ProjectionState.FAILED
                    return False
            
            # Restore original state
            self._projection_states[projection_id] = original_state
            logger.info(f"Read model rebuild completed for {projection_id}: {processed_events} events processed")
            return True
            
        except Exception as e:
            logger.error(f"Read model rebuild failed for {projection_id}: {e}")
            self._projection_states[projection_id] = ProjectionState.FAILED
            return False
    
    async def _process_single_event(self, projection_id: str, event: BaseEvent, 
                                  store: ReadModelStore) -> None:
        """Process single event for projection"""
        start_time = time.time()
        
        try:
            projection_def = self._projections[projection_id]
            projector = self._projectors[projection_id]
            
            # Get read model key
            read_model_key = projector.get_read_model_key(event)
            
            # Get existing read model data
            existing_data = await store.get_read_model(
                projection_def.read_model_name, read_model_key
            ) or {}
            
            # Project event
            new_data = await projector.project_event(event, existing_data)
            
            # Resolve conflicts if data exists
            if existing_data:
                resolved_data = await self._conflict_resolver.resolve_conflict(
                    existing_data, new_data, event
                )
            else:
                resolved_data = new_data
            
            # Add metadata
            resolved_data["_last_updated"] = datetime.utcnow()
            resolved_data["_last_event_id"] = event.event_id
            resolved_data["_version"] = resolved_data.get("_version", 0) + 1
            
            # Save to read model store
            await store.save_read_model(
                projection_def.read_model_name,
                read_model_key,
                resolved_data,
                metadata={
                    "projection_id": projection_id,
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat()
                }
            )
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            await self._update_projection_metrics(projection_id, processing_time, True)
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            await self._update_projection_metrics(projection_id, processing_time, False)
            logger.error(f"Event processing failed for projection {projection_id}: {e}")
            raise
    
    def _get_read_model_store(self, projection_def: ProjectionDefinition) -> Optional[ReadModelStore]:
        """Get appropriate read model store for projection"""
        # For now, return the first available store
        # In a real implementation, this would consider the read model type and requirements
        return next(iter(self._read_model_stores.values())) if self._read_model_stores else None
    
    async def _clear_read_model(self, projection_def: ProjectionDefinition, store: ReadModelStore) -> None:
        """Clear read model data for rebuild"""
        # This is a simplified implementation
        # In a real system, this would efficiently clear the specific read model
        logger.info(f"Clearing read model data for {projection_def.read_model_name}")
    
    def _start_background_tasks(self) -> None:
        """Start background processing tasks"""
        self._real_time_processor_task = asyncio.create_task(self._real_time_processor())
        self._batch_processor_task = asyncio.create_task(self._batch_processor())
        self._metrics_collector_task = asyncio.create_task(self._metrics_collector())
    
    async def _real_time_processor(self) -> None:
        """Process real-time events"""
        while True:
            try:
                projection_id, event = await self._real_time_queue.get()
                
                async with self._processing_semaphore:
                    projection_def = self._projections[projection_id]
                    store = self._get_read_model_store(projection_def)
                    
                    if store:
                        await self._process_single_event(projection_id, event, store)
                
                self._real_time_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Real-time processing error: {e}")
                await asyncio.sleep(1)
    
    async def _batch_processor(self) -> None:
        """Process batch events periodically"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for projection_id, events in self._batch_queues.items():
                    if not events:
                        continue
                    
                    projection_def = self._projections[projection_id]
                    
                    # Check if batch should be processed
                    should_process = (
                        len(events) >= projection_def.batch_size or
                        (events and (datetime.utcnow() - events[0].timestamp).total_seconds() >= projection_def.batch_interval_seconds)
                    )
                    
                    if should_process:
                        batch_to_process = events.copy()
                        self._batch_queues[projection_id].clear()
                        
                        # Process batch
                        asyncio.create_task(self._process_event_batch(projection_id, batch_to_process))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                await asyncio.sleep(30)
    
    async def _process_event_batch(self, projection_id: str, events: List[BaseEvent]) -> None:
        """Process batch of events for projection"""
        try:
            projection_def = self._projections[projection_id]
            store = self._get_read_model_store(projection_def)
            
            if not store:
                logger.error(f"No store available for projection {projection_id}")
                return
            
            # Process events in parallel if enabled
            if projection_def.parallel_processing:
                semaphore = asyncio.Semaphore(projection_def.max_parallel_workers)
                
                async def process_with_semaphore(event) -> None:
                    async with semaphore:
                        await self._process_single_event(projection_id, event, store)
                
                await asyncio.gather(*[
                    process_with_semaphore(event) for event in events
                    if self._projectors[projection_id].should_process_event(event)
                ])
            else:
                # Sequential processing
                for event in events:
                    if self._projectors[projection_id].should_process_event(event):
                        await self._process_single_event(projection_id, event, store)
            
            # Update checkpoint
            if events:
                last_event = events[-1]
                checkpoint = ProjectionCheckpoint(
                    projection_id=projection_id,
                    last_processed_event_id=last_event.event_id,
                    last_processed_timestamp=last_event.timestamp,
                    processed_event_count=len(events)
                )
                await self._checkpoint_manager.save_checkpoint(checkpoint)
            
            logger.info(f"Batch processing completed for {projection_id}: {len(events)} events")
            
        except Exception as e:
            logger.error(f"Batch processing failed for {projection_id}: {e}")
            self._projection_states[projection_id] = ProjectionState.FAILED
    
    async def _metrics_collector(self) -> None:
        """Collect and update projection metrics"""
        while True:
            try:
                await asyncio.sleep(60)  # Update metrics every minute
                
                for projection_id, metrics in self._metrics.items():
                    # Update lag calculation
                    checkpoint = await self._checkpoint_manager.get_checkpoint(projection_id)
                    if checkpoint:
                        lag = (datetime.utcnow() - checkpoint.last_processed_timestamp).total_seconds()
                        metrics.lag_seconds = lag
                    
                    # Calculate error rate
                    total_events = metrics.events_processed + metrics.events_failed
                    if total_events > 0:
                        metrics.error_rate_percent = (metrics.events_failed / total_events) * 100
                    
                    # Calculate throughput
                    history = self._performance_history[projection_id]
                    if history:
                        recent_history = [
                            h for h in history 
                            if datetime.utcnow() - h["timestamp"] < timedelta(minutes=5)
                        ]
                        if recent_history:
                            time_span = (recent_history[-1]["timestamp"] - recent_history[0]["timestamp"]).total_seconds()
                            if time_span > 0:
                                metrics.throughput_events_per_second = len(recent_history) / time_span
                    
                    metrics.last_updated = datetime.utcnow()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _update_projection_metrics(self, projection_id: str, processing_time_ms: float, 
                                       success: bool) -> None:
        """Update projection metrics"""
        metrics = self._metrics[projection_id]
        
        if success:
            metrics.events_processed += 1
        else:
            metrics.events_failed += 1
        
        metrics.last_processing_time_ms = processing_time_ms
        
        # Update average processing time
        total_events = metrics.events_processed + metrics.events_failed
        if total_events > 0:
            metrics.average_processing_time_ms = (
                (metrics.average_processing_time_ms * (total_events - 1) + processing_time_ms) / total_events
            )
        
        # Add to performance history
        self._performance_history[projection_id].append({
            "processing_time_ms": processing_time_ms,
            "success": success,
            "timestamp": datetime.utcnow()
        })
    
    def pause_projection(self, projection_id: str) -> bool:
        """Pause projection processing"""
        if projection_id in self._projection_states:
            self._projection_states[projection_id] = ProjectionState.PAUSED
            logger.info(f"Paused projection: {projection_id}")
            return True
        return False
    
    def resume_projection(self, projection_id: str) -> bool:
        """Resume projection processing"""
        if projection_id in self._projection_states:
            self._projection_states[projection_id] = ProjectionState.ACTIVE
            logger.info(f"Resumed projection: {projection_id}")
            return True
        return False
    
    def get_projection_metrics(self, projection_id: str = None) -> Dict[str, Any]:
        """Get projection metrics"""
        if projection_id:
            metrics = self._metrics.get(projection_id)
            if metrics:
                return {
                    "projection_id": metrics.projection_id,
                    "events_processed": metrics.events_processed,
                    "events_failed": metrics.events_failed,
                    "last_processing_time_ms": metrics.last_processing_time_ms,
                    "average_processing_time_ms": metrics.average_processing_time_ms,
                    "throughput_events_per_second": metrics.throughput_events_per_second,
                    "lag_seconds": metrics.lag_seconds,
                    "error_rate_percent": metrics.error_rate_percent,
                    "last_updated": metrics.last_updated.isoformat(),
                    "state": self._projection_states.get(projection_id, ProjectionState.DISABLED).value
                }
            return {}
        else:
            # Return all metrics
            return {
                proj_id: self.get_projection_metrics(proj_id)
                for proj_id in self._metrics.keys()
            }
    
    def get_projection_status(self) -> Dict[str, Any]:
        """Get overall projection status"""
        total_projections = len(self._projections)
        active_projections = sum(1 for state in self._projection_states.values() if state == ProjectionState.ACTIVE)
        
        return {
            "total_projections": total_projections,
            "active_projections": active_projections,
            "paused_projections": sum(1 for state in self._projection_states.values() if state == ProjectionState.PAUSED),
            "failed_projections": sum(1 for state in self._projection_states.values() if state == ProjectionState.FAILED),
            "real_time_queue_size": self._real_time_queue.qsize(),
            "batch_queue_sizes": {proj_id: len(events) for proj_id, events in self._batch_queues.items()},
            "registered_stores": len(self._read_model_stores)
        }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of projector"""
        logger.info("Shutting down read model projector...")
        
        # Cancel background tasks
        for task in [self._real_time_processor_task, self._batch_processor_task, self._metrics_collector_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Process remaining events in queues
        logger.info("Processing remaining events...")
        
        # Process remaining real-time events
        while not self._real_time_queue.empty():
            try:
                projection_id, event = self._real_time_queue.get_nowait()
                projection_def = self._projections[projection_id]
                store = self._get_read_model_store(projection_def)
                if store:
                    await self._process_single_event(projection_id, event, store)
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                logger.error(f"Error processing remaining real-time event: {e}")
        
        # Process remaining batch events
        for projection_id, events in self._batch_queues.items():
            if events:
                try:
                    await self._process_event_batch(projection_id, events)
                except Exception as e:
                    logger.error(f"Error processing remaining batch events for {projection_id}: {e}")
        
        logger.info("Read model projector shutdown complete")


# Default read model store for development
def create_default_in_memory_store() -> InMemoryReadModelStore:
    """Create default in-memory read model store"""
    return InMemoryReadModelStore({"type": "document"})


# Singleton instance for global access
_read_model_projector_instance: Optional[EnterpriseReadModelProjector] = None


def get_read_model_projector() -> EnterpriseReadModelProjector:
    """Get singleton read model projector instance"""
    global _read_model_projector_instance
    if _read_model_projector_instance is None:
        _read_model_projector_instance = EnterpriseReadModelProjector()
    return _read_model_projector_instance


def reset_read_model_projector() -> None:
    """Reset read model projector instance (for testing)"""
    global _read_model_projector_instance
    if _read_model_projector_instance:
        asyncio.create_task(_read_model_projector_instance.shutdown())
    _read_model_projector_instance = None