"""Distributed Cache Coordinator - Multi-Instance Cache Coordination

Advanced coordination system for distributed cache instances providing
consistency, synchronization, and intelligent load distribution across nodes.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from enum import Enum
import uuid

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    """
Cache node status states"""

    ACTIVE = "active"
    STANDBY = "standby"
    MAINTENANCE = "maintenance"
    FAILED = "failed"
    JOINING = "joining"
    LEAVING = "leaving"

class CoordinationEvent(Enum):
    """Types of coordination events"""

    NODE_JOIN = "node_join"
    NODE_LEAVE = "node_leave"
    CACHE_UPDATE = "cache_update"
    CACHE_DELETE = "cache_delete"
    INVALIDATION = "invalidation"
    REBALANCE = "rebalance"
    HEALTH_CHECK = "health_check"

@dataclass
class CacheNode:
    """Distributed cache node information"""
    node_id: str
    hostname: str
    port: int
    status: NodeStatus = NodeStatus.JOINING
    last_seen: datetime = field(default_factory=datetime.utcnow)
    capabilities: Set[str] = field(default_factory=set)
    metrics: Dict[str, Any] = field(default_factory=dict)
    region: Optional[str] = None
    zone: Optional[str] = None
    load_factor: float = 0.0
    memory_usage: int = 0
    connection_count: int = 0

@dataclass
class ConsistencyHash:
    """
Consistent hashing for key distribution"""
    ring: Dict[int, str] = field(default_factory=dict)
    nodes: Dict[str, CacheNode] = field(default_factory=dict)
    virtual_nodes: int = 150
    
    def add_node(self, node: CacheNode):
        """
Add node to consistent hash ring"""
        self.nodes[node.node_id] = node
        
        for i in range(self.virtual_nodes):
            virtual_key = f"{node.node_id}:{i}"
            hash_value = self._hash_key(virtual_key)
            self.ring[hash_value] = node.node_id
    
    def remove_node(self, node_id: str):
        """Remove node from hash ring"""
        if node_id not in self.nodes:
            return
        
        # Remove virtual nodes
        to_remove = []
        for hash_value, stored_node_id in self.ring.items():
            if stored_node_id == node_id:
                to_remove.append(hash_value)
        
        for hash_value in to_remove:
            del self.ring[hash_value]
        
        del self.nodes[node_id]
    
    def get_node_for_key(self, key: str) -> Optional[str]:
        """
Get responsible node for cache key"""
        if not self.ring:
            return None
        
        key_hash = self._hash_key(key)
        
        # Find the first node clockwise from the key hash
        sorted_hashes = sorted(self.ring.keys())
        
        for ring_hash in sorted_hashes:
            if ring_hash >= key_hash:
                return self.ring[ring_hash]
        
        # Wrap around to first node
        return self.ring[sorted_hashes[0]]
    
    def get_replica_nodes(self, key: str, replica_count: int = 2) -> List[str]:
        """
Get replica nodes for key"""
        nodes = []
        key_hash = self._hash_key(key)
        sorted_hashes = sorted(self.ring.keys())
        
        # Find starting position
        start_index = 0
        for i, ring_hash in enumerate(sorted_hashes):
            if ring_hash >= key_hash:
                start_index = i
                break
        
        # Get unique nodes
        seen_nodes = set()
        for i in range(len(sorted_hashes)):
            index = (start_index + i) % len(sorted_hashes)
            node_id = self.ring[sorted_hashes[index]]
            
            if node_id not in seen_nodes:
                nodes.append(node_id)
                seen_nodes.add(node_id)
                
                if len(nodes) >= replica_count + 1:  # +1 for primary
                    break
        
        return nodes
    
    def _hash_key(self, key: str) -> int:
        """
Hash key to ring position"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

@dataclass
class CoordinationMessage:
    """
Message for inter-node coordination"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: CoordinationEvent = CoordinationEvent.HEALTH_CHECK
    source_node: str = ""
    target_nodes: List[str] = field(default_factory=list)  # Empty = broadcast
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    requires_response: bool = False
    correlation_id: Optional[str] = None

class DistributedCacheCoordinator:
    """
    Advanced distributed cache coordination system providing:
    - Node discovery and health monitoring
    - Consistent hashing for key distribution
    - Cache coherency and synchronization
    - Load balancing and failover handling
    - Conflict resolution and data consistency
    """
    
    def __init__(
        self,
        node_id: str,
        redis_url: str = "redis://localhost:6379",
        coordination_channel: str = "cache_coordination"
    ):
        self.node_id = node_id
        self.redis_url = redis_url
        self.coordination_channel = coordination_channel
        
        # Node management
        self.local_node = CacheNode(
            node_id=node_id,
            hostname="localhost",  # Would be determined dynamically
            port=8080
        )
        
        # Distributed state
        self.consistent_hash = ConsistencyHash()
        self.known_nodes: Dict[str, CacheNode] = {}
        self.pending_operations: Dict[str, Dict[str, Any]] = {}
        
        # Communication
        self._redis: Optional[aioredis.Redis] = None
        self._pubsub: Optional[aioredis.client.PubSub] = None
        
        # Coordination state
        self.is_coordinator = False
        self.coordinator_node_id: Optional[str] = None
        self.last_heartbeat = datetime.utcnow()
        
        # Event handlers
        self.event_handlers: Dict[CoordinationEvent, List[Callable]] = {}
        
        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._coordination_task: Optional[asyncio.Task] = None
        self._health_monitor_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize distributed coordination"""
        try:
            # Setup Redis connection
            self._redis = aioredis.from_url(self.redis_url)
            await self._redis.ping()
            
            # Setup pub/sub for coordination
            self._pubsub = self._redis.pubsub()
            await self._pubsub.subscribe(self.coordination_channel)
            
            # Join the cluster
            await self._join_cluster()
            
            # Start background tasks
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self._coordination_task = asyncio.create_task(self._coordination_loop())
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            
            logger.info(f"DistributedCacheCoordinator {self.node_id} initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize coordinator: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown with cluster notification"""
        try:
            # Notify cluster of departure
            await self._leave_cluster()
            
            # Cancel background tasks
            for task in [self._heartbeat_task, self._coordination_task, self._health_monitor_task]:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Close connections
            if self._pubsub:
                await self._pubsub.unsubscribe(self.coordination_channel)
                await self._pubsub.close()
            
            if self._redis:
                await self._redis.close()
            
            logger.info(f"DistributedCacheCoordinator {self.node_id} shut down")
            
        except Exception as e:
            logger.error(f"Error during coordinator shutdown: {e}")
    
    def register_event_handler(
        self,
        event_type: CoordinationEvent,
        handler: Callable
    ):
        """Register handler for coordination events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
    
    async def notify_cache_update(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
Notify cluster of cache update"""
        message = CoordinationMessage(
            event_type=CoordinationEvent.CACHE_UPDATE,
            source_node=self.node_id,
            payload={
                'key': key,
                'value': value,
                'ttl': ttl,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        await self._broadcast_message(message)
    
    async def notify_cache_delete(self, key: str):
        """
Notify cluster of cache deletion"""
        message = CoordinationMessage(
            event_type=CoordinationEvent.CACHE_DELETE,
            source_node=self.node_id,
            payload={'key': key}
        )
        
        await self._broadcast_message(message)
    
    async def notify_invalidation(
        self,
        keys: List[str] = None,
        patterns: List[str] = None,
        tags: List[str] = None
    ):
        """
Notify cluster of cache invalidation"""
        message = CoordinationMessage(
            event_type=CoordinationEvent.INVALIDATION,
            source_node=self.node_id,
            payload={
                'keys': keys or [],
                'patterns': patterns or [],
                'tags': tags or []
            }
        )
        
        await self._broadcast_message(message)
    
    async def get_responsible_nodes(
        self,
        key: str,
        replica_count: int = 2
    ) -> List[CacheNode]:
        """
Get nodes responsible for caching a key"""
        node_ids = self.consistent_hash.get_replica_nodes(key, replica_count)
        
        nodes = []
        for node_id in node_ids:
            if node_id in self.known_nodes:
                nodes.append(self.known_nodes[node_id])
        
        return nodes
    
    async def is_local_key(self, key: str) -> bool:
        """
Check if key should be handled by local node"""
        primary_node = self.consistent_hash.get_node_for_key(key)
        return primary_node == self.node_id
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """
Get comprehensive cluster status"""
        return {
            'local_node_id': self.node_id,
            'is_coordinator': self.is_coordinator,
            'coordinator_node_id': self.coordinator_node_id,
            'total_nodes': len(self.known_nodes),
            'active_nodes': len([
                node for node in self.known_nodes.values()
                if node.status == NodeStatus.ACTIVE
            ]),
            'cluster_health': self._calculate_cluster_health(),
            'known_nodes': {
                node_id: {
                    'status': node.status.value,
                    'last_seen': node.last_seen.isoformat(),
                    'load_factor': node.load_factor
                }
                for node_id, node in self.known_nodes.items()
            }
        }
    
    async def trigger_rebalance(self, reason: str = "manual"):
        """Trigger cluster rebalancing"""
        if not self.is_coordinator:
            logger.warning("Only coordinator can trigger rebalance")
            return
        
        message = CoordinationMessage(
            event_type=CoordinationEvent.REBALANCE,
            source_node=self.node_id,
            payload={'reason': reason}
        )
        
        await self._broadcast_message(message)
        await self._perform_rebalance()
    
    # Private implementation methods
    
    async def _join_cluster(self):
        """Join the cache cluster"""
        # Register local node
        await self._register_node(self.local_node)
        
        # Discover existing nodes
        await self._discover_nodes()
        
        # Determine coordinator
        await self._elect_coordinator()
        
        # Add self to consistent hash
        self.consistent_hash.add_node(self.local_node)
        self.known_nodes[self.node_id] = self.local_node
        
        # Broadcast join message
        join_message = CoordinationMessage(
            event_type=CoordinationEvent.NODE_JOIN,
            source_node=self.node_id,
            payload={
                'node_info': {
                    'node_id': self.local_node.node_id,
                    'hostname': self.local_node.hostname,
                    'port': self.local_node.port,
                    'capabilities': list(self.local_node.capabilities)
                }
            }
        )
        
        await self._broadcast_message(join_message)
        
        self.local_node.status = NodeStatus.ACTIVE
    
    async def _leave_cluster(self):
        """
Leave the cache cluster gracefully"""
        # Broadcast leave message
        leave_message = CoordinationMessage(
            event_type=CoordinationEvent.NODE_LEAVE,
            source_node=self.node_id,
            payload={'reason': 'graceful_shutdown'}
        )
        
        await self._broadcast_message(leave_message)
        
        # Update status
        self.local_node.status = NodeStatus.LEAVING
        
        # Remove from Redis
        await self._unregister_node(self.node_id)
        
        # Remove from consistent hash
        self.consistent_hash.remove_node(self.node_id)
    
    async def _register_node(self, node: CacheNode):
        """
Register node in Redis"""
        node_key = f"cache_nodes:{node.node_id}"
        node_data = {
            'node_id': node.node_id,
            'hostname': node.hostname,
            'port': node.port,
            'status': node.status.value,
            'last_seen': node.last_seen.isoformat(),
            'capabilities': list(node.capabilities),
            'region': node.region,
            'zone': node.zone
        }
        
        await self._redis.hset(node_key, mapping=node_data)
        await self._redis.expire(node_key, 300)  # 5 minute TTL
    
    async def _unregister_node(self, node_id: str):
        """Remove node from Redis"""
        node_key = f"cache_nodes:{node_id}"
        await self._redis.delete(node_key)
    
    async def _discover_nodes(self):
        """Discover existing cluster nodes"""
        pattern = "cache_nodes:*"
        node_keys = await self._redis.keys(pattern)
        
        for node_key in node_keys:
            node_data = await self._redis.hgetall(node_key)
            
            if not node_data:
                continue
            
            node_id = node_data.get('node_id')
            if node_id and node_id != self.node_id:
                node = CacheNode(
                    node_id=node_id,
                    hostname=node_data.get('hostname', ''),
                    port=int(node_data.get('port', 0)),
                    status=NodeStatus(node_data.get('status', 'active')),
                    last_seen=datetime.fromisoformat(node_data.get('last_seen', datetime.utcnow().isoformat())),
                    capabilities=set(node_data.get('capabilities', '').split(',')),
                    region=node_data.get('region'),
                    zone=node_data.get('zone')
                )
                
                self.known_nodes[node_id] = node
                self.consistent_hash.add_node(node)
    
    async def _elect_coordinator(self):
        """Elect coordinator node (simple implementation)"""
        active_nodes = [
            node_id for node_id, node in self.known_nodes.items()
            if node.status == NodeStatus.ACTIVE
        ]
        
        # Add self if active
        if self.local_node.status == NodeStatus.ACTIVE:
            active_nodes.append(self.node_id)
        
        if active_nodes:
            # Simple election: lowest node_id becomes coordinator
            coordinator_id = min(active_nodes)
            self.coordinator_node_id = coordinator_id
            self.is_coordinator = (coordinator_id == self.node_id)
        
        logger.info(f"Coordinator elected: {self.coordinator_node_id} (local: {self.is_coordinator})")
    
    async def _broadcast_message(self, message: CoordinationMessage):
        """Broadcast coordination message to cluster"""
        message_data = {
            'message_id': message.message_id,
            'event_type': message.event_type.value,
            'source_node': message.source_node,
            'target_nodes': message.target_nodes,
            'payload': message.payload,
            'timestamp': message.timestamp.isoformat(),
            'requires_response': message.requires_response,
            'correlation_id': message.correlation_id
        }
        
        await self._redis.publish(
            self.coordination_channel,
            json.dumps(message_data)
        )
    
    async def _heartbeat_loop(self):
        """
Send periodic heartbeats"""
        while True:
            try:
                # Update last heartbeat
                self.last_heartbeat = datetime.utcnow()
                
                # Update node registration
                self.local_node.last_seen = self.last_heartbeat
                await self._register_node(self.local_node)
                
                # Send heartbeat message
                heartbeat_message = CoordinationMessage(
                    event_type=CoordinationEvent.HEALTH_CHECK,
                    source_node=self.node_id,
                    payload={
                        'load_factor': self.local_node.load_factor,
                        'memory_usage': self.local_node.memory_usage,
                        'connection_count': self.local_node.connection_count
                    }
                )
                
                await self._broadcast_message(heartbeat_message)
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(30)
    
    async def _coordination_loop(self):
        """Process coordination messages"""
        while True:
            try:
                message = await self._pubsub.get_message(timeout=1.0)
                
                if message and message['type'] == 'message':
                    await self._handle_coordination_message(message['data'])
                
            except Exception as e:
                logger.error(f"Coordination loop error: {e}")
                await asyncio.sleep(1)
    
    async def _handle_coordination_message(self, message_data: bytes):
        """Handle incoming coordination message"""
        try:
            data = json.loads(message_data.decode())
            
            # Skip own messages
            if data.get('source_node') == self.node_id:
                return
            
            event_type = CoordinationEvent(data['event_type'])
            
            # Handle different event types
            if event_type == CoordinationEvent.NODE_JOIN:
                await self._handle_node_join(data)
            elif event_type == CoordinationEvent.NODE_LEAVE:
                await self._handle_node_leave(data)
            elif event_type == CoordinationEvent.CACHE_UPDATE:
                await self._handle_cache_update(data)
            elif event_type == CoordinationEvent.CACHE_DELETE:
                await self._handle_cache_delete(data)
            elif event_type == CoordinationEvent.INVALIDATION:
                await self._handle_invalidation(data)
            elif event_type == CoordinationEvent.HEALTH_CHECK:
                await self._handle_health_check(data)
            elif event_type == CoordinationEvent.REBALANCE:
                await self._handle_rebalance(data)
            
            # Call registered event handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(data)
                    except Exception as e:
                        logger.error(f"Event handler error: {e}")
            
        except Exception as e:
            logger.error(f"Error handling coordination message: {e}")
    
    async def _handle_node_join(self, data: Dict[str, Any]):
        """Handle node join event"""
        node_info = data.get('payload', {}).get('node_info', {})
        node_id = node_info.get('node_id')
        
        if node_id and node_id not in self.known_nodes:
            node = CacheNode(
                node_id=node_id,
                hostname=node_info.get('hostname', ''),
                port=node_info.get('port', 0),
                status=NodeStatus.ACTIVE,
                capabilities=set(node_info.get('capabilities', []))
            )
            
            self.known_nodes[node_id] = node
            self.consistent_hash.add_node(node)
            
            logger.info(f"Node joined cluster: {node_id}")
            
            # Re-elect coordinator if needed
            await self._elect_coordinator()
    
    async def _handle_node_leave(self, data: Dict[str, Any]):
        """Handle node leave event"""
        source_node = data.get('source_node')
        
        if source_node in self.known_nodes:
            self.consistent_hash.remove_node(source_node)
            del self.known_nodes[source_node]
            
            logger.info(f"Node left cluster: {source_node}")
            
            # Re-elect coordinator if needed
            if source_node == self.coordinator_node_id:
                await self._elect_coordinator()
    
    async def _handle_cache_update(self, data: Dict[str, Any]):
        """Handle cache update notification"""
        payload = data.get('payload', {})
        key = payload.get('key')
        
        # This would integrate with local cache to update/sync data
        logger.debug(f"Cache update notification for key: {key}")
    
    async def _handle_cache_delete(self, data: Dict[str, Any]):
        """Handle cache delete notification"""
        payload = data.get('payload', {})
        key = payload.get('key')
        
        # This would integrate with local cache to delete data
        logger.debug(f"Cache delete notification for key: {key}")
    
    async def _handle_invalidation(self, data: Dict[str, Any]):
        """Handle invalidation notification"""
        payload = data.get('payload', {})
        
        # This would trigger local cache invalidation
        logger.debug(f"Cache invalidation notification: {payload}")
    
    async def _handle_health_check(self, data: Dict[str, Any]):
        """Handle health check from other node"""
        source_node = data.get('source_node')
        payload = data.get('payload', {})
        
        if source_node in self.known_nodes:
            node = self.known_nodes[source_node]
            node.last_seen = datetime.utcnow()
            node.load_factor = payload.get('load_factor', 0.0)
            node.memory_usage = payload.get('memory_usage', 0)
            node.connection_count = payload.get('connection_count', 0)
    
    async def _handle_rebalance(self, data: Dict[str, Any]):
        """
Handle rebalance notification"""
        if self.is_coordinator:
            await self._perform_rebalance()
    
    async def _health_monitor_loop(self):
        """
Monitor node health and detect failures"""
        while True:
            try:
                current_time = datetime.utcnow()
                failed_nodes = []
                
                for node_id, node in self.known_nodes.items():
                    # Check if node hasn't been seen recently
                    time_since_seen = (current_time - node.last_seen).total_seconds()
                    
                    if time_since_seen > 120:  # 2 minutes without heartbeat
                        if node.status == NodeStatus.ACTIVE:
                            node.status = NodeStatus.FAILED
                            failed_nodes.append(node_id)
                            logger.warning(f"Node marked as failed: {node_id}")
                
                # Remove failed nodes from cluster
                for node_id in failed_nodes:
                    self.consistent_hash.remove_node(node_id)
                    del self.known_nodes[node_id]
                
                # Re-elect coordinator if current one failed
                if self.coordinator_node_id in failed_nodes:
                    await self._elect_coordinator()
                
                await asyncio.sleep(60)  # Health check every minute
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_rebalance(self):
        """Perform cluster rebalancing"""
        logger.info("Starting cluster rebalance")
        
        # This would implement intelligent data redistribution
        # based on node capacity and performance metrics
        
        # For now, just rebuild the consistent hash ring
        self.consistent_hash = ConsistencyHash()
        
        for node in self.known_nodes.values():
            if node.status == NodeStatus.ACTIVE:
                self.consistent_hash.add_node(node)
        
        logger.info("Cluster rebalance completed")
    
    def _calculate_cluster_health(self) -> str:
        """Calculate overall cluster health"""
        if not self.known_nodes:
            return "unknown"
        
        active_nodes = len([
            node for node in self.known_nodes.values()
            if node.status == NodeStatus.ACTIVE
        ])
        
        total_nodes = len(self.known_nodes)
        health_ratio = active_nodes / total_nodes
        
        if health_ratio >= 0.9:
            return "healthy"
        elif health_ratio >= 0.7:
            return "warning"
        else:
            return "critical"
