"""Real-Time Data Synchronization System
Enterprise-grade real-time data sync with conflict resolution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
License: Proprietary - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, or use without explicit written permission from Fahed Mlaiel
is strictly prohibited and may result in legal action.
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import websockets
import aiohttp
from contextlib import asynccontextmanager

from ..core.exceptions import SyncException, ConflictResolutionError
from ..core.metrics import MetricsCollector
from ..database.connection import get_database_session
from ..security.encryption import EncryptionService


class SyncOperation(Enum):
    """
Synchronization operation types"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BULK_UPDATE = "bulk_update"
    SCHEMA_CHANGE = "schema_change"


class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies"""

    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE_FIELDS = "merge_fields"
    CUSTOM_RESOLVER = "custom_resolver"
    MANUAL_RESOLUTION = "manual_resolution"
    VERSION_BASED = "version_based"


class SyncStatus(Enum):
    """Synchronization status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICTED = "conflicted"
    RETRYING = "retrying"


class SyncDirection(Enum):
    """Synchronization direction"""

    BIDIRECTIONAL = "bidirectional"
    PUSH_ONLY = "push_only"
    PULL_ONLY = "pull_only"
    MASTER_SLAVE = "master_slave"


@dataclass
class SyncChange:
    """Represents a synchronization change"""
    id: str
    operation: SyncOperation
    entity_type: str
    entity_id: str
    data: Dict[str, Any]
    timestamp: datetime
    version: int
    source_node: str
    target_nodes: List[str]
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    
    @property
    def is_expired(self) -> bool:
        """
Check if change is expired"""
        return datetime.utcnow() > self.timestamp + timedelta(hours=24)


@dataclass
class SyncConflict:
    """
Represents a synchronization conflict"""
    id: str
    entity_type: str
    entity_id: str
    local_change: SyncChange
    remote_change: SyncChange
    conflict_type: str
    detected_at: datetime
    resolution_strategy: ConflictResolutionStrategy
    resolved: bool = False
    resolution_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert conflict to dictionary"""
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "conflict_type": self.conflict_type,
            "detected_at": self.detected_at.isoformat(),
            "local_change": {
                "operation": self.local_change.operation.value,
                "timestamp": self.local_change.timestamp.isoformat(),
                "version": self.local_change.version,
                "data": self.local_change.data
            },
            "remote_change": {
                "operation": self.remote_change.operation.value,
                "timestamp": self.remote_change.timestamp.isoformat(),
                "version": self.remote_change.version,
                "data": self.remote_change.data
            },
            "resolved": self.resolved
        }


@dataclass
class SyncNode:
    """Represents a synchronization node"""
    id: str
    name: str
    endpoint: str
    is_master: bool
    is_online: bool
    last_sync: Optional[datetime]
    sync_direction: SyncDirection
    priority: int = 1
    auth_token: Optional[str] = None
    capabilities: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RealtimeSyncManager:
    """
    Advanced real-time data synchronization system with conflict resolution,
    multi-node support, and intelligent routing
    """
    
    def __init__(
        self,
        node_id: str,
        config: Optional[Dict[str, Any]] = None,
        encryption_service: Optional[EncryptionService] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.node_id = node_id
        self.config = config or self._get_default_config()
        self.encryption_service = encryption_service
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
        
        # Sync state management
        self.pending_changes: Dict[str, SyncChange] = {}
        self.conflicts: Dict[str, SyncConflict] = {}
        self.sync_nodes: Dict[str, SyncNode] = {}
        self.change_listeners: Dict[str, List[Callable]] = defaultdict(list)
        self.conflict_resolvers: Dict[str, Callable] = {}
        
        # Real-time connections
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.websocket_server: Optional[websockets.WebSocketServer] = None
        self.client_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        
        # Performance tracking
        self.sync_metrics = {
            "changes_sent": 0,
            "changes_received": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0,
            "sync_failures": 0,
            "average_sync_time": 0.0
        }
        
        # Background tasks
        self._sync_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        # Initialize sync manager
        asyncio.create_task(self._initialize_sync_manager())
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default synchronization configuration"""
        return {
            "websocket_port": 8765,
            "sync_interval": 5,  # seconds
            "heartbeat_interval": 30,  # seconds
            "cleanup_interval": 300,  # seconds
            "max_pending_changes": 10000,
            "conflict_resolution_timeout": 300,  # seconds
            "retry_delay": 5,  # seconds
            "enable_encryption": True,
            "enable_compression": True,
            "batch_size": 100,
            "connection_timeout": 30,
            "default_conflict_strategy": "last_write_wins"
        }
    
    async def _initialize_sync_manager(self):
        """Initialize synchronization manager"""
        try:
            # Start WebSocket server
            await self._start_websocket_server()
            
            # Start background tasks
            self._sync_task = asyncio.create_task(self._periodic_sync())
            self._heartbeat_task = asyncio.create_task(self._periodic_heartbeat())
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            
            self.logger.info(f"Real-time sync manager initialized for node {self.node_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize sync manager: {e}")
            raise SyncException(f"Sync manager initialization failed: {e}")
    
    async def _start_websocket_server(self):
        """Start WebSocket server for real-time communication"""
        try:
            self.websocket_server = await websockets.serve(
                self._handle_websocket_connection,
                "0.0.0.0",
                self.config["websocket_port"]
            )
            
            self.logger.info(f"WebSocket server started on port {self.config['websocket_port']}")
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    async def _handle_websocket_connection(
        self,
        websocket: websockets.WebSocketServerProtocol,
        path: str
    ):
        """Handle incoming WebSocket connections"""
        client_id = None
        try:
            async for message in websocket:
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type == "handshake":
                    client_id = data.get("node_id")
                    if client_id:
                        self.websocket_connections[client_id] = websocket
                        await websocket.send(json.dumps({
                            "type": "handshake_ack",
                            "node_id": self.node_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                        self.logger.info(f"Client {client_id} connected")
                
                elif message_type == "sync_change":
                    await self._handle_incoming_change(data, client_id)
                
                elif message_type == "conflict_resolution":
                    await self._handle_conflict_resolution(data, client_id)
                
                elif message_type == "heartbeat":
                    await websocket.send(json.dumps({
                        "type": "heartbeat_ack",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            if client_id and client_id in self.websocket_connections:
                del self.websocket_connections[client_id]
    
    async def add_sync_node(
        self,
        node: SyncNode,
        connect_immediately: bool = True
    ) -> bool:
        """Add a synchronization node"""
        try:
            async with self._lock:
                self.sync_nodes[node.id] = node
                
                if connect_immediately and node.endpoint:
                    await self._connect_to_node(node)
                
                self.logger.info(f"Added sync node: {node.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to add sync node {node.id}: {e}")
            return False
    
    async def _connect_to_node(self, node: SyncNode):
        """Connect to a remote sync node"""
        try:
            if node.id in self.client_connections:
                return  # Already connected
            
            # Parse WebSocket endpoint
            ws_url = f"ws://{node.endpoint}/sync"
            
            # Connect to remote node
            websocket = await websockets.connect(
                ws_url,
                timeout=self.config["connection_timeout"]
            )
            
            # Send handshake
            await websocket.send(json.dumps({
                "type": "handshake",
                "node_id": self.node_id,
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            # Wait for handshake acknowledgment
            response = await asyncio.wait_for(
                websocket.recv(),
                timeout=self.config["connection_timeout"]
            )
            
            handshake_data = json.loads(response)
            if handshake_data.get("type") == "handshake_ack":
                self.client_connections[node.id] = websocket
                node.is_online = True
                node.last_sync = datetime.utcnow()
                
                # Start listening for messages
                asyncio.create_task(self._listen_to_node(node.id, websocket))
                
                self.logger.info(f"Connected to sync node: {node.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to node {node.id}: {e}")
            node.is_online = False
    
    async def _listen_to_node(self, node_id: str, websocket: websockets.WebSocketClientProtocol):
        """Listen for messages from a remote node"""
        try:
            async for message in websocket:
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type == "sync_change":
                    await self._handle_incoming_change(data, node_id)
                elif message_type == "conflict_resolution":
                    await self._handle_conflict_resolution(data, node_id)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Connection to node {node_id} closed")
        except Exception as e:
            self.logger.error(f"Error listening to node {node_id}: {e}")
        finally:
            if node_id in self.client_connections:
                del self.client_connections[node_id]
            if node_id in self.sync_nodes:
                self.sync_nodes[node_id].is_online = False
    
    async def queue_change(
        self,
        operation: SyncOperation,
        entity_type: str,
        entity_id: str,
        data: Dict[str, Any],
        target_nodes: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Queue a change for synchronization"""
        try:
            # Generate change ID
            change_id = f"{self.node_id}_{entity_type}_{entity_id}_{int(time.time() * 1000)}"
            
            # Create change object
            change = SyncChange(
                id=change_id,
                operation=operation,
                entity_type=entity_type,
                entity_id=entity_id,
                data=data,
                timestamp=datetime.utcnow(),
                version=await self._get_entity_version(entity_type, entity_id),
                source_node=self.node_id,
                target_nodes=target_nodes or list(self.sync_nodes.keys()),
                checksum=self._calculate_checksum(data),
                metadata=metadata or {}
            )
            
            async with self._lock:
                self.pending_changes[change_id] = change
                
                # Trigger immediate sync for high-priority changes
                if operation in [SyncOperation.CREATE, SyncOperation.DELETE]:
                    asyncio.create_task(self._sync_change(change))
            
            self.logger.debug(f"Queued change: {change_id}")
            return change_id
            
        except Exception as e:
            self.logger.error(f"Failed to queue change: {e}")
            raise SyncException(f"Failed to queue change: {e}")
    
    async def _sync_change(self, change: SyncChange):
        """Synchronize a single change to target nodes"""
        try:
            change_data = {
                "type": "sync_change",
                "change": {
                    "id": change.id,
                    "operation": change.operation.value,
                    "entity_type": change.entity_type,
                    "entity_id": change.entity_id,
                    "data": change.data,
                    "timestamp": change.timestamp.isoformat(),
                    "version": change.version,
                    "source_node": change.source_node,
                    "checksum": change.checksum,
                    "metadata": change.metadata
                }
            }
            
            # Encrypt data if enabled
            if self.config["enable_encryption"] and self.encryption_service:
                change_data["change"]["data"] = await self.encryption_service.encrypt(
                    json.dumps(change.data)
                )
                change_data["encrypted"] = True
            
            # Send to target nodes
            for node_id in change.target_nodes:
                if node_id == self.node_id:
                    continue  # Skip self
                
                await self._send_to_node(node_id, change_data)
            
            # Mark as sent
            self.sync_metrics["changes_sent"] += 1
            
            if self.metrics_collector:
                await self.metrics_collector.record_metric(
                    "sync_change_sent",
                    1,
                    tags={"operation": change.operation.value, "entity_type": change.entity_type}
                )
            
        except Exception as e:
            self.logger.error(f"Failed to sync change {change.id}: {e}")
            change.retry_count += 1
            
            if change.retry_count < change.max_retries:
                # Schedule retry
                await asyncio.sleep(self.config["retry_delay"])
                asyncio.create_task(self._sync_change(change))
            else:
                self.sync_metrics["sync_failures"] += 1
    
    async def _send_to_node(self, node_id: str, data: Dict[str, Any]):
        """Send data to a specific node"""
        try:
            # Try WebSocket connection first
            if node_id in self.websocket_connections:
                await self.websocket_connections[node_id].send(json.dumps(data))
            elif node_id in self.client_connections:
                await self.client_connections[node_id].send(json.dumps(data))
            else:
                # Try to reconnect
                if node_id in self.sync_nodes:
                    await self._connect_to_node(self.sync_nodes[node_id])
                    if node_id in self.client_connections:
                        await self.client_connections[node_id].send(json.dumps(data))
                    else:
                        raise SyncException(f"Unable to connect to node {node_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to send data to node {node_id}: {e}")
            raise
    
    async def _handle_incoming_change(self, data: Dict[str, Any], source_node: str):
        """Handle incoming synchronization change"""
        try:
            change_data = data.get("change", {})
            
            # Decrypt data if needed
            if data.get("encrypted", False) and self.encryption_service:
                decrypted_data = await self.encryption_service.decrypt(change_data["data"])
                change_data["data"] = json.loads(decrypted_data)
            
            # Create change object
            change = SyncChange(
                id=change_data["id"],
                operation=SyncOperation(change_data["operation"]),
                entity_type=change_data["entity_type"],
                entity_id=change_data["entity_id"],
                data=change_data["data"],
                timestamp=datetime.fromisoformat(change_data["timestamp"]),
                version=change_data["version"],
                source_node=change_data["source_node"],
                target_nodes=[],
                checksum=change_data["checksum"],
                metadata=change_data.get("metadata", {})
            )
            
            # Verify checksum
            if not self._verify_checksum(change.data, change.checksum):
                raise SyncException("Checksum verification failed")
            
            # Check for conflicts
            conflict = await self._detect_conflict(change)
            
            if conflict:
                await self._handle_conflict(conflict)
            else:
                await self._apply_change(change)
            
            self.sync_metrics["changes_received"] += 1
            
            if self.metrics_collector:
                await self.metrics_collector.record_metric(
                    "sync_change_received",
                    1,
                    tags={"operation": change.operation.value, "entity_type": change.entity_type}
                )
            
        except Exception as e:
            self.logger.error(f"Failed to handle incoming change: {e}")
    
    async def _detect_conflict(self, remote_change: SyncChange) -> Optional[SyncConflict]:
        """Detect conflicts between remote and local changes"""
        try:
            # Check if we have a local change for the same entity
            local_changes = [
                change for change in self.pending_changes.values()
                if (change.entity_type == remote_change.entity_type and
                    change.entity_id == remote_change.entity_id and
                    change.timestamp > remote_change.timestamp - timedelta(seconds=1))
            ]
            
            if not local_changes:
                return None
            
            # Find the most recent local change
            local_change = max(local_changes, key=lambda c: c.timestamp)
            
            # Determine conflict type
            conflict_type = self._determine_conflict_type(local_change, remote_change)
            
            if conflict_type:
                conflict = SyncConflict(
                    id=f"conflict_{remote_change.entity_type}_{remote_change.entity_id}_{int(time.time())}",
                    entity_type=remote_change.entity_type,
                    entity_id=remote_change.entity_id,
                    local_change=local_change,
                    remote_change=remote_change,
                    conflict_type=conflict_type,
                    detected_at=datetime.utcnow(),
                    resolution_strategy=ConflictResolutionStrategy(
                        self.config["default_conflict_strategy"]
                    )
                )
                
                return conflict
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting conflict: {e}")
            return None
    
    def _determine_conflict_type(
        self,
        local_change: SyncChange,
        remote_change: SyncChange
    ) -> Optional[str]:
        """Determine the type of conflict between changes"""
        if local_change.operation != remote_change.operation:
            return "operation_conflict"
        
        if local_change.version != remote_change.version:
            return "version_conflict"
        
        if local_change.checksum != remote_change.checksum:
            return "data_conflict"
        
        return None
    
    async def _handle_conflict(self, conflict: SyncConflict):
        """Handle synchronization conflict"""
        try:
            async with self._lock:
                self.conflicts[conflict.id] = conflict
                self.sync_metrics["conflicts_detected"] += 1
            
            # Attempt automatic resolution
            resolved = await self._resolve_conflict_automatically(conflict)
            
            if not resolved:
                # Notify conflict listeners
                await self._notify_conflict_listeners(conflict)
            
            if self.metrics_collector:
                await self.metrics_collector.record_metric(
                    "sync_conflict_detected",
                    1,
                    tags={"conflict_type": conflict.conflict_type, "entity_type": conflict.entity_type}
                )
            
        except Exception as e:
            self.logger.error(f"Failed to handle conflict {conflict.id}: {e}")
    
    async def _resolve_conflict_automatically(self, conflict: SyncConflict) -> bool:
        """Attempt to resolve conflict automatically"""
        try:
            strategy = conflict.resolution_strategy
            
            if strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
                # Apply the change with the later timestamp
                if conflict.remote_change.timestamp > conflict.local_change.timestamp:
                    await self._apply_change(conflict.remote_change)
                else:
                    await self._apply_change(conflict.local_change)
                
                conflict.resolved = True
                conflict.resolution_data = {"strategy": "last_write_wins"}
                
            elif strategy == ConflictResolutionStrategy.VERSION_BASED:
                # Apply the change with the higher version
                if conflict.remote_change.version > conflict.local_change.version:
                    await self._apply_change(conflict.remote_change)
                else:
                    await self._apply_change(conflict.local_change)
                
                conflict.resolved = True
                conflict.resolution_data = {"strategy": "version_based"}
            
            elif strategy == ConflictResolutionStrategy.MERGE_FIELDS:
                # Attempt to merge the changes
                merged_data = await self._merge_change_data(
                    conflict.local_change.data,
                    conflict.remote_change.data
                )
                
                if merged_data:
                    # Create merged change
                    merged_change = SyncChange(
                        id=f"merged_{conflict.id}",
                        operation=conflict.local_change.operation,
                        entity_type=conflict.entity_type,
                        entity_id=conflict.entity_id,
                        data=merged_data,
                        timestamp=datetime.utcnow(),
                        version=max(conflict.local_change.version, conflict.remote_change.version) + 1,
                        source_node=self.node_id,
                        target_nodes=[],
                        checksum=self._calculate_checksum(merged_data)
                    )
                    
                    await self._apply_change(merged_change)
                    conflict.resolved = True
                    conflict.resolution_data = {"strategy": "merge_fields", "merged_data": merged_data}
            
            if conflict.resolved:
                self.sync_metrics["conflicts_resolved"] += 1
                self.logger.info(f"Automatically resolved conflict: {conflict.id}")
                
                if self.metrics_collector:
                    await self.metrics_collector.record_metric(
                        "sync_conflict_resolved",
                        1,
                        tags={"strategy": strategy.value, "entity_type": conflict.entity_type}
                    )
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to resolve conflict automatically: {e}")
            return False
    
    async def _merge_change_data(
        self,
        local_data: Dict[str, Any],
        remote_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Attempt to merge change data"""
        try:
            merged = local_data.copy()
            
            for key, value in remote_data.items():
                if key not in merged:
                    merged[key] = value
                elif merged[key] != value:
                    # Simple conflict resolution: prefer non-null values
                    if merged[key] is None and value is not None:
                        merged[key] = value
                    elif isinstance(merged[key], (int, float)) and isinstance(value, (int, float)):
                        # For numeric values, take the average
                        merged[key] = (merged[key] + value) / 2
                    elif isinstance(merged[key], str) and isinstance(value, str):
                        # For strings, concatenate with a separator
                        merged[key] = f"{merged[key]} | {value}"
            
            return merged
            
        except Exception as e:
            self.logger.error(f"Failed to merge change data: {e}")
            return None
    
    async def _apply_change(self, change: SyncChange):
        """Apply synchronization change to local data"""
        try:
            # Notify change listeners
            await self._notify_change_listeners(change)
            
            # Remove from pending changes if it's ours
            if change.id in self.pending_changes:
                del self.pending_changes[change.id]
            
            self.logger.debug(f"Applied change: {change.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply change {change.id}: {e}")
            raise
    
    async def _notify_change_listeners(self, change: SyncChange):
        """Notify registered change listeners"""
        try:
            listeners = self.change_listeners.get(change.entity_type, [])
            listeners.extend(self.change_listeners.get("*", []))  # Global listeners
            
            for listener in listeners:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(change)
                    else:
                        listener(change)
                except Exception as e:
                    self.logger.error(f"Error in change listener: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to notify change listeners: {e}")
    
    async def _notify_conflict_listeners(self, conflict: SyncConflict):
        """Notify registered conflict listeners"""
        try:
            listeners = self.change_listeners.get(f"conflict_{conflict.entity_type}", [])
            listeners.extend(self.change_listeners.get("conflict_*", []))  # Global conflict listeners
            
            for listener in listeners:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(conflict)
                    else:
                        listener(conflict)
                except Exception as e:
                    self.logger.error(f"Error in conflict listener: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to notify conflict listeners: {e}")
    
    def register_change_listener(
        self,
        entity_type: str,
        listener: Callable[[SyncChange], None]
    ):
        """Register a listener for entity changes"""
        self.change_listeners[entity_type].append(listener)
    
    def register_conflict_resolver(
        self,
        entity_type: str,
        resolver: Callable[[SyncConflict], Optional[Dict[str, Any]]]
    ):
        """
Register a custom conflict resolver"""
        self.conflict_resolvers[entity_type] = resolver
    
    async def resolve_conflict_manually(
        self,
        conflict_id: str,
        resolution_data: Dict[str, Any]
    ) -> bool:
        """
Manually resolve a conflict"""
        try:
            if conflict_id not in self.conflicts:
                return False
            
            conflict = self.conflicts[conflict_id]
            
            # Apply manual resolution
            if "apply_local" in resolution_data:
                await self._apply_change(conflict.local_change)
            elif "apply_remote" in resolution_data:
                await self._apply_change(conflict.remote_change)
            elif "merged_data" in resolution_data:
                # Create merged change
                merged_change = SyncChange(
                    id=f"manual_merged_{conflict.id}",
                    operation=conflict.local_change.operation,
                    entity_type=conflict.entity_type,
                    entity_id=conflict.entity_id,
                    data=resolution_data["merged_data"],
                    timestamp=datetime.utcnow(),
                    version=max(conflict.local_change.version, conflict.remote_change.version) + 1,
                    source_node=self.node_id,
                    target_nodes=[],
                    checksum=self._calculate_checksum(resolution_data["merged_data"])
                )
                
                await self._apply_change(merged_change)
            
            conflict.resolved = True
            conflict.resolution_data = resolution_data
            
            self.sync_metrics["conflicts_resolved"] += 1
            self.logger.info(f"Manually resolved conflict: {conflict_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resolve conflict manually: {e}")
            return False
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get comprehensive synchronization status"""
        return {
            "node_id": self.node_id,
            "metrics": self.sync_metrics,
            "nodes": {
                node_id: {
                    "name": node.name,
                    "is_online": node.is_online,
                    "last_sync": node.last_sync.isoformat() if node.last_sync else None,
                    "sync_direction": node.sync_direction.value
                }
                for node_id, node in self.sync_nodes.items()
            },
            "pending_changes": len(self.pending_changes),
            "active_conflicts": len([c for c in self.conflicts.values() if not c.resolved]),
            "websocket_connections": len(self.websocket_connections),
            "client_connections": len(self.client_connections)
        }
    
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for data"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _verify_checksum(self, data: Dict[str, Any], expected_checksum: str) -> bool:
        """
Verify data checksum"""
        return self._calculate_checksum(data) == expected_checksum
    
    async def _get_entity_version(self, entity_type: str, entity_id: str) -> int:
        """
Get current version of an entity"""
        # This would typically query the database
        # For now, return a simple timestamp-based version
        return int(time.time() * 1000)
    
    async def _periodic_sync(self):
        """
Periodic synchronization of pending changes"""
        while True:
            try:
                await asyncio.sleep(self.config["sync_interval"])
                
                async with self._lock:
                    changes_to_sync = list(self.pending_changes.values())
                
                for change in changes_to_sync:
                    if not change.is_expired:
                        await self._sync_change(change)
                    else:
                        # Remove expired changes
                        if change.id in self.pending_changes:
                            del self.pending_changes[change.id]
                
            except Exception as e:
                self.logger.error(f"Error in periodic sync: {e}")
    
    async def _periodic_heartbeat(self):
        """Send periodic heartbeats to connected nodes"""
        while True:
            try:
                await asyncio.sleep(self.config["heartbeat_interval"])
                
                heartbeat_data = {
                    "type": "heartbeat",
                    "node_id": self.node_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Send to all connected nodes
                for node_id in list(self.websocket_connections.keys()):
                    try:
                        await self.websocket_connections[node_id].send(
                            json.dumps(heartbeat_data)
                        )
                    except Exception as e:
                        self.logger.warning(f"Failed to send heartbeat to {node_id}: {e}")
                        # Remove dead connection
                        if node_id in self.websocket_connections:
                            del self.websocket_connections[node_id]
                
                for node_id in list(self.client_connections.keys()):
                    try:
                        await self.client_connections[node_id].send(
                            json.dumps(heartbeat_data)
                        )
                    except Exception as e:
                        self.logger.warning(f"Failed to send heartbeat to {node_id}: {e}")
                        # Remove dead connection
                        if node_id in self.client_connections:
                            del self.client_connections[node_id]
                        if node_id in self.sync_nodes:
                            self.sync_nodes[node_id].is_online = False
                
            except Exception as e:
                self.logger.error(f"Error in periodic heartbeat: {e}")
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired data"""
        while True:
            try:
                await asyncio.sleep(self.config["cleanup_interval"])
                
                current_time = datetime.utcnow()
                
                # Clean up expired changes
                expired_changes = [
                    change_id for change_id, change in self.pending_changes.items()
                    if change.is_expired
                ]
                
                for change_id in expired_changes:
                    del self.pending_changes[change_id]
                
                # Clean up old resolved conflicts
                old_conflicts = [
                    conflict_id for conflict_id, conflict in self.conflicts.items()
                    if (conflict.resolved and 
                        current_time > conflict.detected_at + timedelta(hours=24))
                ]
                
                for conflict_id in old_conflicts:
                    del self.conflicts[conflict_id]
                
                self.logger.debug(f"Cleanup completed: removed {len(expired_changes)} expired changes, {len(old_conflicts)} old conflicts")
                
            except Exception as e:
                self.logger.error(f"Error in periodic cleanup: {e}")
    
    async def close(self):
        """Close sync manager and cleanup resources"""
        # Cancel background tasks
        for task in [self._sync_task, self._heartbeat_task, self._cleanup_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Close WebSocket connections
        for websocket in self.websocket_connections.values():
            await websocket.close()
        
        for websocket in self.client_connections.values():
            await websocket.close()
        
        # Close WebSocket server
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        self.logger.info("Real-time sync manager closed")


# Global sync manager instance
_sync_manager: Optional[RealtimeSyncManager] = None


async def get_sync_manager(
    node_id: str,
    config: Optional[Dict[str, Any]] = None,
    encryption_service: Optional[EncryptionService] = None,
    metrics_collector: Optional[MetricsCollector] = None
) -> RealtimeSyncManager:
    """Get or create sync manager instance"""
    global _sync_manager
    
    if _sync_manager is None:
        _sync_manager = RealtimeSyncManager(
            node_id=node_id,
            config=config,
            encryption_service=encryption_service,
            metrics_collector=metrics_collector
        )
    
    return _sync_manager


@asynccontextmanager
async def sync_context(
    node_id: str,
    config: Optional[Dict[str, Any]] = None,
    encryption_service: Optional[EncryptionService] = None,
    metrics_collector: Optional[MetricsCollector] = None
):
    """
Context manager for sync operations"""
    sync_manager = await get_sync_manager(node_id, config, encryption_service, metrics_collector)
    try:
        yield sync_manager
    finally:
        # Sync manager stays alive for reuse
        pass
