"""
Event Sourcing Manager module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Event Sourcing Manager - Enterprise Event Management Component
Event store management, replay, versioning, and snapshot capabilities

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive event sourcing capabilities including:
- Event store management and persistence
- Event replay and reconstruction capabilities
- Event versioning and migration handling
- Snapshot management for performance optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Type, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import hashlib
from abc import ABC, abstractmethod
import pickle
import gzip
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventStatus(Enum):
    """Event status enumeration"""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    REPLAYING = "replaying"


class SnapshotStatus(Enum):
    """Snapshot status enumeration"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class Event:
    """Base event structure"""
    event_id: str
    event_type: str
    aggregate_id: str
    aggregate_type: str
    event_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    status: EventStatus = EventStatus.PENDING


@dataclass
class EventStream:
    """Event stream definition"""
    stream_id: str
    aggregate_id: str
    aggregate_type: str
    events: List[Event] = field(default_factory=list)
    current_version: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Snapshot:
    """Aggregate snapshot"""
    snapshot_id: str
    aggregate_id: str
    aggregate_type: str
    aggregate_data: Dict[str, Any]
    version: int
    timestamp: datetime
    checksum: str
    compressed_data: Optional[bytes] = None
    status: SnapshotStatus = SnapshotStatus.ACTIVE


@dataclass
class EventProjection:
    """Event projection definition"""
    projection_id: str
    name: str
    event_types: List[str]
    projection_data: Dict[str, Any] = field(default_factory=dict)
    last_processed_event: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


class EventHandler(ABC):
    """Abstract base class for event handlers"""
    
    @abstractmethod
    async def handle(self, event: Event) -> bool:
        """Handle an event"""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Check if handler can process event type"""
        pass


class EventSourcingManager:
    """
    Enterprise Event Sourcing Manager
    
    Provides comprehensive event sourcing capabilities including event store
    management, replay functionality, versioning, and snapshot management
    for enterprise-grade event-driven architectures.
    """
    
    def __init__(self, snapshot_frequency -> None: int = 100) -> None:
        self.event_store: Dict[str, EventStream] = {}
        self.snapshots: Dict[str, List[Snapshot]] = defaultdict(list)
        self.projections: Dict[str, EventProjection] = {}
        self.event_handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self.replay_sessions: Dict[str, Dict[str, Any]] = {}
        self.global_event_log: List[Event] = []
        self.snapshot_frequency = snapshot_frequency
        self.event_index: Dict[str, List[str]] = defaultdict(list)  # event_type -> event_ids
        
        logger.info("Event Sourcing Manager initialized")
    
    # Event Management
    async def append_event(self, event: Event) -> bool:
        """Append event to event store"""
        try:
            # Validate event
            if not event.event_id or not event.aggregate_id:
                raise ValueError("Event ID and Aggregate ID are required")
            
            # Generate event ID if not provided
            if not event.event_id:
                event.event_id = str(uuid.uuid4())
            
            # Get or create event stream
            stream_key = f"{event.aggregate_type}_{event.aggregate_id}"
            if stream_key not in self.event_store:
                self.event_store[stream_key] = EventStream(
                    stream_id=stream_key,
                    aggregate_id=event.aggregate_id,
                    aggregate_type=event.aggregate_type
                )
            
            stream = self.event_store[stream_key]
            
            # Set event version
            stream.current_version += 1
            event.version = stream.current_version
            
            # Add to stream
            stream.events.append(event)
            stream.last_updated = datetime.utcnow()
            
            # Add to global log
            self.global_event_log.append(event)
            
            # Update index
            self.event_index[event.event_type].append(event.event_id)
            
            # Process event handlers
            await self._process_event_handlers(event)
            
            # Check if snapshot is needed
            if len(stream.events) % self.snapshot_frequency == 0:
                await self._create_snapshot(stream)
            
            # Update projections
            await self._update_projections(event)
            
            logger.debug(f"Event {event.event_id} appended to stream {stream_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append event {event.event_id}: {e}")
            return False
    
    async def get_events(self, aggregate_id: str, aggregate_type: str, 
                        from_version: int = 0, to_version: Optional[int] = None) -> List[Event]:
        """Get events for an aggregate"""
        try:
            stream_key = f"{aggregate_type}_{aggregate_id}"
            if stream_key not in self.event_store:
                return []
            
            stream = self.event_store[stream_key]
            events = stream.events
            
            # Filter by version range
            if from_version > 0:
                events = [e for e in events if e.version >= from_version]
            
            if to_version is not None:
                events = [e for e in events if e.version <= to_version]
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events for {aggregate_type}_{aggregate_id}: {e}")
            return []
    
    async def get_events_by_type(self, event_type: str, limit: Optional[int] = None) -> List[Event]:
        """Get events by type"""
        try:
            event_ids = self.event_index.get(event_type, [])
            
            if limit:
                event_ids = event_ids[-limit:]
            
            events = []
            for event_id in event_ids:
                event = await self.get_event_by_id(event_id)
                if event:
                    events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events by type {event_type}: {e}")
            return []
    
    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        try:
            for stream in self.event_store.values():
                for event in stream.events:
                    if event.event_id == event_id:
                        return event
            return None
            
        except Exception as e:
            logger.error(f"Failed to get event {event_id}: {e}")
            return None
    
    # Snapshot Management
    async def create_snapshot(self, aggregate_id: str, aggregate_type: str, 
                            aggregate_data: Dict[str, Any]) -> bool:
        """Create snapshot for aggregate"""
        try:
            stream_key = f"{aggregate_type}_{aggregate_id}"
            if stream_key not in self.event_store:
                logger.error(f"Event stream {stream_key} not found")
                return False
            
            stream = self.event_store[stream_key]
            
            snapshot = Snapshot(
                snapshot_id=str(uuid.uuid4()),
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                aggregate_data=aggregate_data,
                version=stream.current_version,
                timestamp=datetime.utcnow(),
                checksum=self._calculate_checksum(aggregate_data)
            )
            
            # Compress snapshot data if large
            if len(json.dumps(aggregate_data)) > 10000:  # 10KB threshold
                compressed_data = gzip.compress(pickle.dumps(aggregate_data))
                snapshot.compressed_data = compressed_data
            
            # Store snapshot
            snapshot_key = f"{aggregate_type}_{aggregate_id}"
            self.snapshots[snapshot_key].append(snapshot)
            
            # Keep only last 10 snapshots
            if len(self.snapshots[snapshot_key]) > 10:
                old_snapshots = self.snapshots[snapshot_key][:-10]
                for old_snapshot in old_snapshots:
                    old_snapshot.status = SnapshotStatus.ARCHIVED
                self.snapshots[snapshot_key] = self.snapshots[snapshot_key][-10:]
            
            logger.info(f"Snapshot created for {aggregate_type}_{aggregate_id} at version {snapshot.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create snapshot for {aggregate_type}_{aggregate_id}: {e}")
            return False
    
    async def get_latest_snapshot(self, aggregate_id: str, aggregate_type: str) -> Optional[Snapshot]:
        """Get latest snapshot for aggregate"""
        try:
            snapshot_key = f"{aggregate_type}_{aggregate_id}"
            snapshots = self.snapshots.get(snapshot_key, [])
            
            if not snapshots:
                return None
            
            # Return latest active snapshot
            active_snapshots = [s for s in snapshots if s.status == SnapshotStatus.ACTIVE]
            if active_snapshots:
                return max(active_snapshots, key=lambda s: s.version)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest snapshot for {aggregate_type}_{aggregate_id}: {e}")
            return None
    
    async def _create_snapshot(self, stream: EventStream) -> None:
        """Create automatic snapshot for stream"""
        try:
            # In a real implementation, you would reconstruct the aggregate state
            # from events and then create a snapshot
            aggregate_data = {
                "stream_id": stream.stream_id,
                "event_count": len(stream.events),
                "last_updated": stream.last_updated.isoformat(),
                "auto_generated": True
            }
            
            await self.create_snapshot(
                stream.aggregate_id,
                stream.aggregate_type,
                aggregate_data
            )
            
        except Exception as e:
            logger.error(f"Failed to create automatic snapshot for {stream.stream_id}: {e}")
    
    # Event Replay
    async def replay_events(self, aggregate_id: str, aggregate_type: str, 
                          from_version: int = 0, to_version: Optional[int] = None) -> List[Event]:
        """Replay events for an aggregate"""
        try:
            session_id = str(uuid.uuid4())
            
            # Get events to replay
            events = await self.get_events(aggregate_id, aggregate_type, from_version, to_version)
            
            if not events:
                logger.warning(f"No events found for replay: {aggregate_type}_{aggregate_id}")
                return []
            
            # Create replay session
            self.replay_sessions[session_id] = {
                "aggregate_id": aggregate_id,
                "aggregate_type": aggregate_type,
                "start_time": datetime.utcnow(),
                "total_events": len(events),
                "processed_events": 0,
                "status": "running"
            }
            
            replayed_events = []
            
            for event in events:
                try:
                    # Mark event as replaying
                    event.status = EventStatus.REPLAYING
                    
                    # Process event handlers
                    await self._process_event_handlers(event)
                    
                    # Mark as processed
                    event.status = EventStatus.PROCESSED
                    replayed_events.append(event)
                    
                    # Update session progress
                    self.replay_sessions[session_id]["processed_events"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to replay event {event.event_id}: {e}")
                    event.status = EventStatus.FAILED
            
            # Complete replay session
            self.replay_sessions[session_id]["status"] = "completed"
            self.replay_sessions[session_id]["end_time"] = datetime.utcnow()
            
            logger.info(f"Replayed {len(replayed_events)} events for {aggregate_type}_{aggregate_id}")
            return replayed_events
            
        except Exception as e:
            logger.error(f"Failed to replay events for {aggregate_type}_{aggregate_id}: {e}")
            return []
    
    async def replay_events_by_type(self, event_type: str, from_time: Optional[datetime] = None,
                                  to_time: Optional[datetime] = None) -> List[Event]:
        """Replay events by type within time range"""
        try:
            events = await self.get_events_by_type(event_type)
            
            # Filter by time range
            if from_time:
                events = [e for e in events if e.timestamp >= from_time]
            
            if to_time:
                events = [e for e in events if e.timestamp <= to_time]
            
            # Sort by timestamp
            events.sort(key=lambda e: e.timestamp)
            
            replayed_events = []
            for event in events:
                try:
                    event.status = EventStatus.REPLAYING
                    await self._process_event_handlers(event)
                    event.status = EventStatus.PROCESSED
                    replayed_events.append(event)
                except Exception as e:
                    logger.error(f"Failed to replay event {event.event_id}: {e}")
                    event.status = EventStatus.FAILED
            
            logger.info(f"Replayed {len(replayed_events)} events of type {event_type}")
            return replayed_events
            
        except Exception as e:
            logger.error(f"Failed to replay events by type {event_type}: {e}")
            return []
    
    # Event Handlers
    def register_event_handler(self, event_type: str, handler: EventHandler) -> None:
        """Register event handler"""
        try:
            self.event_handlers[event_type].append(handler)
            logger.info(f"Event handler registered for type: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to register event handler: {e}")
    
    def unregister_event_handler(self, event_type: str, handler: EventHandler) -> None:
        """Unregister event handler"""
        try:
            if event_type in self.event_handlers:
                self.event_handlers[event_type].remove(handler)
                logger.info(f"Event handler unregistered for type: {event_type}")
                
        except Exception as e:
            logger.error(f"Failed to unregister event handler: {e}")
    
    async def _process_event_handlers(self, event: Event) -> None:
        """Process event through registered handlers"""
        try:
            handlers = self.event_handlers.get(event.event_type, [])
            
            for handler in handlers:
                try:
                    if handler.can_handle(event.event_type):
                        await handler.handle(event)
                except Exception as e:
                    logger.error(f"Event handler failed for {event.event_id}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to process event handlers: {e}")
    
    # Projections
    async def create_projection(self, projection: EventProjection) -> bool:
        """Create event projection"""
        try:
            if projection.projection_id in self.projections:
                logger.warning(f"Projection {projection.projection_id} already exists")
                return False
            
            self.projections[projection.projection_id] = projection
            
            # Initialize projection with existing events
            await self._initialize_projection(projection)
            
            logger.info(f"Projection {projection.projection_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create projection {projection.projection_id}: {e}")
            return False
    
    async def _initialize_projection(self, projection: EventProjection) -> None:
        """Initialize projection with existing events"""
        try:
            for event_type in projection.event_types:
                events = await self.get_events_by_type(event_type)
                for event in events:
                    await self._update_projection_with_event(projection, event)
            
        except Exception as e:
            logger.error(f"Failed to initialize projection {projection.projection_id}: {e}")
    
    async def _update_projections(self, event: Event) -> None:
        """Update all relevant projections with new event"""
        try:
            for projection in self.projections.values():
                if projection.is_active and event.event_type in projection.event_types:
                    await self._update_projection_with_event(projection, event)
            
        except Exception as e:
            logger.error(f"Failed to update projections: {e}")
    
    async def _update_projection_with_event(self, projection: EventProjection, event: Event) -> None:
        """Update specific projection with event"""
        try:
            # In a real implementation, this would update the projection based on event type
            if "event_count" not in projection.projection_data:
                projection.projection_data["event_count"] = 0
            
            projection.projection_data["event_count"] += 1
            projection.last_processed_event = event.event_id
            projection.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update projection {projection.projection_id}: {e}")
    
    # Utility Methods
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for data"""
        try:
            data_str = json.dumps(data, sort_keys=True)
            return hashlib.sha256(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {e}")
            return ""
    
    async def get_event_store_stats(self) -> Dict[str, Any]:
        """Get event store statistics"""
        try:
            total_events = sum(len(stream.events) for stream in self.event_store.values())
            total_streams = len(self.event_store)
            total_snapshots = sum(len(snapshots) for snapshots in self.snapshots.values())
            total_projections = len(self.projections)
            
            # Calculate storage size estimate
            storage_estimate = len(json.dumps([asdict(event) for stream in self.event_store.values() 
                                             for event in stream.events]))
            
            return {
                "total_events": total_events,
                "total_streams": total_streams,
                "total_snapshots": total_snapshots,
                "total_projections": total_projections,
                "storage_estimate_bytes": storage_estimate,
                "event_types": list(self.event_index.keys()),
                "active_replay_sessions": len([s for s in self.replay_sessions.values() 
                                             if s["status"] == "running"])
            }
            
        except Exception as e:
            logger.error(f"Failed to get event store stats: {e}")
            return {}
    
    async def cleanup_old_events(self, retention_days: int = 365) -> int:
        """Clean up old events beyond retention period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            cleaned_count = 0
            
            for stream in self.event_store.values():
                original_count = len(stream.events)
                stream.events = [e for e in stream.events if e.timestamp > cutoff_date]
                cleaned_count += original_count - len(stream.events)
            
            # Clean up global event log
            original_global_count = len(self.global_event_log)
            self.global_event_log = [e for e in self.global_event_log if e.timestamp > cutoff_date]
            cleaned_count += original_global_count - len(self.global_event_log)
            
            # Rebuild event index
            self.event_index.clear()
            for stream in self.event_store.values():
                for event in stream.events:
                    self.event_index[event.event_type].append(event.event_id)
            
            logger.info(f"Cleaned up {cleaned_count} old events")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
            return 0


# Example Event Handlers
class CreatorContentEventHandler(EventHandler):
    """Example event handler for creator content events"""
    
    async def handle(self, event: Event) -> bool:
        """Handle creator content events"""
        try:
            logger.info(f"Processing creator content event: {event.event_type}")
            
            if event.event_type == "content_uploaded":
                # Process content upload
                content_data = event.event_data
                logger.info(f"Content uploaded: {content_data.get('content_id')}")
                
            elif event.event_type == "content_published":
                # Process content publication
                content_data = event.event_data
                logger.info(f"Content published: {content_data.get('content_id')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle creator content event: {e}")
            return False
    
    def can_handle(self, event_type: str) -> bool:
        """Check if handler can process event type"""
        return event_type.startswith("content_")


# Factory function for easier instantiation
def create_event_sourcing_manager(snapshot_frequency: int = 100) -> EventSourcingManager:
    """Factory function to create an Event Sourcing Manager"""
    return EventSourcingManager(snapshot_frequency)


# Example usage
async def main() -> None:
    """Example usage of Event Sourcing Manager"""
    event_manager = create_event_sourcing_manager()
    
    # Register event handler
    content_handler = CreatorContentEventHandler()
    event_manager.register_event_handler("content_uploaded", content_handler)
    event_manager.register_event_handler("content_published", content_handler)
    
    # Create some test events
    content_upload_event = Event(
        event_id=str(uuid.uuid4()),
        event_type="content_uploaded",
        aggregate_id="creator_123",
        aggregate_type="creator",
        event_data={
            "content_id": "content_456",
            "title": "Amazing Music Track",
            "type": "audio",
            "size": 5242880
        },
        metadata={"user_id": "user_789"}
    )
    
    content_publish_event = Event(
        event_id=str(uuid.uuid4()),
        event_type="content_published",
        aggregate_id="creator_123",
        aggregate_type="creator",
        event_data={
            "content_id": "content_456",
            "published_at": datetime.utcnow().isoformat(),
            "visibility": "public"
        }
    )
    
    # Append events
    await event_manager.append_event(content_upload_event)
    await event_manager.append_event(content_publish_event)
    
    # Create snapshot
    creator_data = {
        "creator_id": "creator_123",
        "total_content": 1,
        "last_activity": datetime.utcnow().isoformat()
    }
    await event_manager.create_snapshot("creator_123", "creator", creator_data)
    
    # Get events
    events = await event_manager.get_events("creator_123", "creator")
    print(f"Retrieved {len(events)} events for creator_123")
    
    # Replay events
    replayed_events = await event_manager.replay_events("creator_123", "creator")
    print(f"Replayed {len(replayed_events)} events")
    
    # Get statistics
    stats = await event_manager.get_event_store_stats()
    print(f"Event store stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())