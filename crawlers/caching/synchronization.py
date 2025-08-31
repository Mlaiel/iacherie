#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cache Synchronization - Multi-Node Cache Coordination
=====================================================

Advanced synchronization system for distributed cache coordination
with conflict resolution and consistency guarantees.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import weakref

from ...core.config import get_settings
from ...core.utils import generate_uuid, get_timestamp

logger = logging.getLogger(__name__)

class SyncOperation(Enum):
    """Synchronization operations."""
    SET = "set"
    DELETE = "delete"
    INVALIDATE = "invalidate"
    CLEAR = "clear"

class ConflictResolution(Enum):
    """Conflict resolution strategies."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    CUSTOM = "custom"

class ConsistencyLevel(Enum):
    """Consistency levels."""
    EVENTUAL = "eventual"
    STRONG = "strong"
    WEAK = "weak"

@dataclass
class SyncEvent:
    """Synchronization event."""
    event_id: str
    node_id: str
    operation: SyncOperation
    key: str
    value: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_id': self.event_id,
            'node_id': self.node_id,
            'operation': self.operation.value,
            'key': self.key,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncEvent':
        """Create from dictionary."""
        return cls(
            event_id=data['event_id'],
            node_id=data['node_id'],
            operation=SyncOperation(data['operation']),
            key=data['key'],
            value=data.get('value'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            version=data.get('version', 1),
            metadata=data.get('metadata', {})
        )

@dataclass
class ConflictInfo:
    """Conflict information."""
    key: str
    local_event: SyncEvent
    remote_event: SyncEvent
    resolution_strategy: ConflictResolution
    resolved_value: Any = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

class CacheSynchronizer:
    """
    Advanced cache synchronization system.
    
    Features:
    - Multi-node coordination
    - Conflict resolution
    - Version tracking
    - Eventual consistency
    - Custom merge functions
    """
    
    def __init__(self, node_id: str,
                 consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL,
                 conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS):
        """
        Initialize cache synchronizer.
        
        Args:
            node_id: Unique node identifier
            consistency_level: Consistency level
            conflict_resolution: Default conflict resolution strategy
        """
        self.node_id = node_id
        self.consistency_level = consistency_level
        self.conflict_resolution = conflict_resolution
        self.logger = logging.getLogger(f"{__name__}.CacheSynchronizer")
        
        # Event tracking
        self.pending_events: Dict[str, SyncEvent] = {}
        self.event_history: List[SyncEvent] = []
        self.version_vectors: Dict[str, Dict[str, int]] = {}  # node_id -> {key -> version}
        
        # Conflict management
        self.conflict_resolvers: Dict[str, Callable] = {}
        self.conflict_history: List[ConflictInfo] = []
        
        # Synchronization state
        self.sync_callbacks: List[Callable] = []
        self.sync_stats: Dict[str, Any] = {
            'events_sent': 0,
            'events_received': 0,
            'conflicts_resolved': 0,
            'last_sync': None
        }
        
        # Node management
        self.connected_nodes: Set[str] = set()
        self.node_heartbeats: Dict[str, datetime] = {}
        
        self.logger.info(f"Cache synchronizer initialized for node {node_id}")
    
    async def add_sync_callback(self, callback: Callable) -> None:
        """Add synchronization callback."""
        self.sync_callbacks.append(callback)
    
    async def remove_sync_callback(self, callback: Callable) -> None:
        """Remove synchronization callback."""
        if callback in self.sync_callbacks:
            self.sync_callbacks.remove(callback)
    
    async def register_conflict_resolver(self, key_pattern: str, 
                                       resolver: Callable) -> None:
        """
        Register custom conflict resolver.
        
        Args:
            key_pattern: Key pattern for resolver
            resolver: Conflict resolution function
        """
        self.conflict_resolvers[key_pattern] = resolver
        self.logger.debug(f"Registered conflict resolver for pattern {key_pattern}")
    
    async def create_sync_event(self, operation: SyncOperation, 
                              key: str, value: Any = None,
                              metadata: Optional[Dict[str, Any]] = None) -> SyncEvent:
        """Create synchronization event."""
        # Get current version for key
        current_version = self.version_vectors.get(self.node_id, {}).get(key, 0)
        new_version = current_version + 1
        
        # Update version vector
        if self.node_id not in self.version_vectors:
            self.version_vectors[self.node_id] = {}
        self.version_vectors[self.node_id][key] = new_version
        
        event = SyncEvent(
            event_id=generate_uuid(),
            node_id=self.node_id,
            operation=operation,
            key=key,
            value=value,
            version=new_version,
            metadata=metadata or {}
        )
        
        # Track event
        self.pending_events[event.event_id] = event
        self.event_history.append(event)
        
        # Keep history manageable
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]
        
        return event
    
    async def broadcast_event(self, event: SyncEvent) -> None:
        """
        Broadcast synchronization event to all nodes.
        
        Args:
            event: Event to broadcast
        """
        try:
            # Notify all sync callbacks
            for callback in self.sync_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    self.logger.error(f"Sync callback error: {e}")
            
            self.sync_stats['events_sent'] += 1
            self.sync_stats['last_sync'] = datetime.now()
            
            self.logger.debug(f"Broadcasted event {event.event_id}")
            
        except Exception as e:
            self.logger.error(f"Error broadcasting event: {e}")
    
    async def receive_event(self, event: SyncEvent) -> bool:
        """
        Receive and process synchronization event.
        
        Args:
            event: Received event
            
        Returns:
            True if processed successfully
        """
        try:
            self.sync_stats['events_received'] += 1
            
            # Check if we already processed this event
            if event.event_id in [e.event_id for e in self.event_history]:
                return True
            
            # Update node heartbeat
            self.node_heartbeats[event.node_id] = datetime.now()
            self.connected_nodes.add(event.node_id)
            
            # Check for conflicts
            conflict = await self._detect_conflict(event)
            if conflict:
                resolved_event = await self._resolve_conflict(conflict)
                if resolved_event:
                    await self._apply_event(resolved_event)
            else:
                await self._apply_event(event)
            
            # Update version vector
            if event.node_id not in self.version_vectors:
                self.version_vectors[event.node_id] = {}
            
            current_version = self.version_vectors[event.node_id].get(event.key, 0)
            if event.version > current_version:
                self.version_vectors[event.node_id][event.key] = event.version
            
            # Add to history
            self.event_history.append(event)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error receiving event: {e}")
            return False
    
    async def _detect_conflict(self, incoming_event: SyncEvent) -> Optional[ConflictInfo]:
        """Detect conflicts with incoming event."""
        try:
            # Look for concurrent operations on the same key
            for event in reversed(self.event_history[-10:]):  # Check recent events
                if (event.key == incoming_event.key and 
                    event.node_id != incoming_event.node_id and
                    abs((event.timestamp - incoming_event.timestamp).total_seconds()) < 60):
                    
                    # We have a potential conflict
                    return ConflictInfo(
                        key=incoming_event.key,
                        local_event=event,
                        remote_event=incoming_event,
                        resolution_strategy=self.conflict_resolution
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting conflict: {e}")
            return None
    
    async def _resolve_conflict(self, conflict: ConflictInfo) -> Optional[SyncEvent]:
        """Resolve conflict between events."""
        try:
            self.sync_stats['conflicts_resolved'] += 1
            
            # Check for custom resolver
            for pattern, resolver in self.conflict_resolvers.items():
                import fnmatch
                if fnmatch.fnmatch(conflict.key, pattern):
                    try:
                        resolved_value = resolver(conflict.local_event, conflict.remote_event)
                        conflict.resolved_value = resolved_value
                        conflict.resolved_by = "custom_resolver"
                        conflict.resolved_at = datetime.now()
                        
                        # Create resolved event
                        return await self.create_sync_event(
                            SyncOperation.SET,
                            conflict.key,
                            resolved_value,
                            {'conflict_resolved': True}
                        )
                    except Exception as e:
                        self.logger.error(f"Custom resolver error: {e}")
            
            # Use default resolution strategy
            if conflict.resolution_strategy == ConflictResolution.LAST_WRITE_WINS:
                winner = (conflict.remote_event if 
                         conflict.remote_event.timestamp > conflict.local_event.timestamp 
                         else conflict.local_event)
                conflict.resolved_value = winner.value
                conflict.resolved_by = "last_write_wins"
                
            elif conflict.resolution_strategy == ConflictResolution.FIRST_WRITE_WINS:
                winner = (conflict.local_event if 
                         conflict.local_event.timestamp < conflict.remote_event.timestamp 
                         else conflict.remote_event)
                conflict.resolved_value = winner.value
                conflict.resolved_by = "first_write_wins"
                
            elif conflict.resolution_strategy == ConflictResolution.MERGE:
                # Simple merge strategy - combine values if possible
                try:
                    if isinstance(conflict.local_event.value, dict) and isinstance(conflict.remote_event.value, dict):
                        merged = {**conflict.local_event.value, **conflict.remote_event.value}
                        conflict.resolved_value = merged
                        conflict.resolved_by = "dict_merge"
                    elif isinstance(conflict.local_event.value, list) and isinstance(conflict.remote_event.value, list):
                        merged = list(set(conflict.local_event.value + conflict.remote_event.value))
                        conflict.resolved_value = merged
                        conflict.resolved_by = "list_merge"
                    else:
                        # Fall back to last write wins
                        winner = (conflict.remote_event if 
                                 conflict.remote_event.timestamp > conflict.local_event.timestamp 
                                 else conflict.local_event)
                        conflict.resolved_value = winner.value
                        conflict.resolved_by = "merge_fallback"
                except Exception:
                    # Merge failed, use last write wins
                    winner = (conflict.remote_event if 
                             conflict.remote_event.timestamp > conflict.local_event.timestamp 
                             else conflict.local_event)
                    conflict.resolved_value = winner.value
                    conflict.resolved_by = "merge_failed_fallback"
            
            conflict.resolved_at = datetime.now()
            self.conflict_history.append(conflict)
            
            # Keep conflict history manageable
            if len(self.conflict_history) > 100:
                self.conflict_history = self.conflict_history[-50:]
            
            self.logger.info(f"Resolved conflict for key {conflict.key} using {conflict.resolved_by}")
            
            # Return the winning event or create a new one
            if conflict.resolution_strategy in [ConflictResolution.LAST_WRITE_WINS, ConflictResolution.FIRST_WRITE_WINS]:
                return (conflict.remote_event if conflict.resolved_value == conflict.remote_event.value 
                       else conflict.local_event)
            else:
                # Create new event with resolved value
                return await self.create_sync_event(
                    SyncOperation.SET,
                    conflict.key,
                    conflict.resolved_value,
                    {'conflict_resolved': True, 'resolution_strategy': conflict.resolved_by}
                )
            
        except Exception as e:
            self.logger.error(f"Error resolving conflict: {e}")
            return None
    
    async def _apply_event(self, event: SyncEvent) -> None:
        """Apply synchronization event locally."""
        try:
            # This would integrate with the actual cache implementation
            # For now, we just log the event
            self.logger.debug(f"Applied event {event.event_id}: {event.operation.value} {event.key}")
            
        except Exception as e:
            self.logger.error(f"Error applying event: {e}")
    
    async def sync_with_node(self, target_node_id: str, 
                           since_timestamp: Optional[datetime] = None) -> bool:
        """
        Synchronize with specific node.
        
        Args:
            target_node_id: Target node ID
            since_timestamp: Sync events since this timestamp
            
        Returns:
            True if successful
        """
        try:
            # Get events to sync
            if since_timestamp:
                events_to_sync = [
                    event for event in self.event_history
                    if event.timestamp >= since_timestamp and event.node_id == self.node_id
                ]
            else:
                # Sync recent events
                cutoff_time = datetime.now() - timedelta(hours=1)
                events_to_sync = [
                    event for event in self.event_history
                    if event.timestamp >= cutoff_time and event.node_id == self.node_id
                ]
            
            # Send events to target node
            for event in events_to_sync:
                await self.broadcast_event(event)
            
            self.logger.info(f"Synchronized {len(events_to_sync)} events with node {target_node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing with node {target_node_id}: {e}")
            return False
    
    async def get_node_status(self) -> Dict[str, Any]:
        """Get synchronization node status."""
        try:
            now = datetime.now()
            active_nodes = []
            
            for node_id, last_heartbeat in self.node_heartbeats.items():
                if (now - last_heartbeat).total_seconds() < 300:  # 5 minutes
                    active_nodes.append({
                        'node_id': node_id,
                        'last_heartbeat': last_heartbeat.isoformat(),
                        'seconds_since_heartbeat': (now - last_heartbeat).total_seconds()
                    })
            
            return {
                'node_id': self.node_id,
                'consistency_level': self.consistency_level.value,
                'conflict_resolution': self.conflict_resolution.value,
                'active_nodes': active_nodes,
                'connected_node_count': len(active_nodes),
                'pending_events': len(self.pending_events),
                'total_events': len(self.event_history),
                'total_conflicts': len(self.conflict_history),
                'stats': self.sync_stats
            }
            
        except Exception as e:
            self.logger.error(f"Error getting node status: {e}")
            return {}
    
    async def cleanup_old_events(self, max_age_hours: int = 24) -> int:
        """Clean up old synchronization events."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            # Clean event history
            original_count = len(self.event_history)
            self.event_history = [
                event for event in self.event_history
                if event.timestamp >= cutoff_time
            ]
            
            # Clean pending events
            self.pending_events = {
                event_id: event for event_id, event in self.pending_events.items()
                if event.timestamp >= cutoff_time
            }
            
            # Clean conflict history
            self.conflict_history = [
                conflict for conflict in self.conflict_history
                if conflict.resolved_at and conflict.resolved_at >= cutoff_time
            ]
            
            cleaned_count = original_count - len(self.event_history)
            self.logger.info(f"Cleaned up {cleaned_count} old sync events")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up events: {e}")
            return 0

class SyncCoordinator:
    """
    Coordination system for multiple cache synchronizers.
    
    Manages cluster-wide synchronization and consistency.
    """
    
    def __init__(self, cluster_id: str):
        """Initialize sync coordinator."""
        self.cluster_id = cluster_id
        self.logger = logging.getLogger(f"{__name__}.SyncCoordinator")
        
        # Node management
        self.synchronizers: Dict[str, CacheSynchronizer] = {}
        self.cluster_state: Dict[str, Any] = {}
        
        # Coordination tasks
        self.coordination_tasks: List[asyncio.Task] = []
        
    async def register_synchronizer(self, synchronizer: CacheSynchronizer) -> None:
        """Register cache synchronizer."""
        self.synchronizers[synchronizer.node_id] = synchronizer
        
        # Add coordination callback
        await synchronizer.add_sync_callback(self._coordinate_event)
        
        self.logger.info(f"Registered synchronizer for node {synchronizer.node_id}")
    
    async def unregister_synchronizer(self, node_id: str) -> None:
        """Unregister cache synchronizer."""
        if node_id in self.synchronizers:
            del self.synchronizers[node_id]
            self.logger.info(f"Unregistered synchronizer for node {node_id}")
    
    async def _coordinate_event(self, event: SyncEvent) -> None:
        """Coordinate event across all nodes."""
        try:
            # Broadcast to all other synchronizers
            for node_id, synchronizer in self.synchronizers.items():
                if node_id != event.node_id:
                    await synchronizer.receive_event(event)
            
        except Exception as e:
            self.logger.error(f"Error coordinating event: {e}")
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster synchronization status."""
        try:
            node_statuses = {}
            
            for node_id, synchronizer in self.synchronizers.items():
                node_statuses[node_id] = await synchronizer.get_node_status()
            
            total_events = sum(
                status.get('total_events', 0) 
                for status in node_statuses.values()
            )
            
            total_conflicts = sum(
                status.get('total_conflicts', 0)
                for status in node_statuses.values()
            )
            
            return {
                'cluster_id': self.cluster_id,
                'node_count': len(self.synchronizers),
                'node_statuses': node_statuses,
                'total_events': total_events,
                'total_conflicts': total_conflicts,
                'cluster_health': 'healthy' if len(self.synchronizers) > 0 else 'unhealthy'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cluster status: {e}")
            return {}
    
    async def force_cluster_sync(self) -> bool:
        """Force cluster-wide synchronization."""
        try:
            # Get the most recent timestamp from all nodes
            max_timestamp = None
            
            for synchronizer in self.synchronizers.values():
                if synchronizer.event_history:
                    node_max = max(event.timestamp for event in synchronizer.event_history)
                    if max_timestamp is None or node_max > max_timestamp:
                        max_timestamp = node_max
            
            if not max_timestamp:
                return True  # Nothing to sync
            
            # Sync each node with others
            sync_tasks = []
            for node_id, synchronizer in self.synchronizers.items():
                for target_node_id in self.synchronizers.keys():
                    if target_node_id != node_id:
                        task = synchronizer.sync_with_node(target_node_id, max_timestamp)
                        sync_tasks.append(task)
            
            results = await asyncio.gather(*sync_tasks, return_exceptions=True)
            success_count = sum(1 for result in results if result is True)
            
            self.logger.info(f"Cluster sync completed: {success_count}/{len(sync_tasks)} successful")
            return success_count == len(sync_tasks)
            
        except Exception as e:
            self.logger.error(f"Error forcing cluster sync: {e}")
            return False
