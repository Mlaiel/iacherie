"""Distributed Cache Configuration for IA-Influencer Agent Platform
=================================================================

Enterprise-grade distributed caching configuration for multi-region
deployment and high availability scenarios.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, validator


class DistributionStrategy(str, Enum):
    """Distributed cache distribution strategies"""    CONSISTENT_HASHING = "consistent_hashing"
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LOCALITY_AWARE = "locality_aware"
    LOAD_BASED = "load_based"
    CUSTOM = "custom"


class ReplicationMode(str, Enum):
    """Cache replication modes"""    NONE = "none"  # No replication
    ASYNC = "async"  # Asynchronous replication
    SYNC = "sync"  # Synchronous replication
    MASTER_SLAVE = "master_slave"  # Master-slave replication
    MULTI_MASTER = "multi_master"  # Multi-master replication


class ConsistencyLevel(str, Enum):
    """Distributed cache consistency levels"""    EVENTUAL = "eventual"  # Eventual consistency
    STRONG = "strong"  # Strong consistency
    CAUSAL = "causal"  # Causal consistency
    SESSION = "session"  # Session consistency
    MONOTONIC_READ = "monotonic_read"  # Monotonic read consistency


class FailoverPolicy(str, Enum):
    """Failover policies for distributed cache"""    FAIL_FAST = "fail_fast"  # Return error immediately
    FAIL_SILENT = "fail_silent"  # Return None/empty
    RETRY = "retry"  # Retry on other nodes
    CIRCUIT_BREAKER = "circuit_breaker"  # Circuit breaker pattern


@dataclass
class CacheNode:
    """Distributed cache node configuration"""    id: str
    host: str
    port: int
    region: str = "default"
    zone: str = "default"
    weight: int = 1
    is_master: bool = False
    max_connections: int = 100
    health_check_interval: int = 30
    
    # Performance characteristics
    cpu_cores: int = 4
    memory_gb: int = 8
    network_bandwidth_mbps: int = 1000
    
    # Status tracking
    is_healthy: bool = True
    last_health_check: Optional[float] = None
    response_time_ms: float = 0.0
    load_factor: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.host}:{self.port}"
    
    def get_endpoint(self) -> str:
        return f"{self.host}:{self.port}"
    
    def calculate_load_score(self) -> float:
        """Calculate node load score for load balancing"""        base_score = self.weight * (self.cpu_cores * self.memory_gb)
        
        # Adjust for current load and response time
        load_penalty = self.load_factor * 0.5
        latency_penalty = min(self.response_time_ms / 100.0, 2.0)
        
        return max(base_score - load_penalty - latency_penalty, 0.1)


@dataclass
class RegionConfig:
    """Configuration for a cache region"""    name: str
    primary_nodes: List[str] = field(default_factory=list)
    replica_nodes: List[str] = field(default_factory=list)
    read_preference: str = "primary_preferred"  # primary, secondary, primary_preferred
    write_concern: str = "majority"  # majority, all, one
    max_latency_ms: int = 100
    
    def get_read_nodes(self, all_nodes: Dict[str, CacheNode]) -> List[CacheNode]:
        """Get nodes for read operations based on preference"""        nodes = []
        
        if self.read_preference in ["primary", "primary_preferred"]:
            nodes.extend([all_nodes[node_id] for node_id in self.primary_nodes 
                         if node_id in all_nodes and all_nodes[node_id].is_healthy])
        
        if self.read_preference in ["secondary", "primary_preferred"] and not nodes:
            nodes.extend([all_nodes[node_id] for node_id in self.replica_nodes 
                         if node_id in all_nodes and all_nodes[node_id].is_healthy])
        
        return nodes
    
    def get_write_nodes(self, all_nodes: Dict[str, CacheNode]) -> List[CacheNode]:
        """Get nodes for write operations based on write concern"""        nodes = []
        
        if self.write_concern == "all":
            node_ids = self.primary_nodes + self.replica_nodes
            nodes = [all_nodes[node_id] for node_id in node_ids 
                    if node_id in all_nodes and all_nodes[node_id].is_healthy]
        elif self.write_concern == "majority":
            # Use primary nodes first, then replicas if needed
            nodes.extend([all_nodes[node_id] for node_id in self.primary_nodes 
                         if node_id in all_nodes and all_nodes[node_id].is_healthy])
        else:  # "one"
            nodes = [all_nodes[node_id] for node_id in self.primary_nodes[:1] 
                    if node_id in all_nodes and all_nodes[node_id].is_healthy]
        
        return nodes


class DistributedCacheConfig(BaseModel):
    """    Comprehensive distributed cache configuration
    """    
    # Cluster configuration
    cluster_name: str = "ia-agent-cache"
    nodes: Dict[str, CacheNode] = field(default_factory=dict)
    regions: Dict[str, RegionConfig] = field(default_factory=dict)
    
    # Distribution settings
    distribution_strategy: DistributionStrategy = DistributionStrategy.CONSISTENT_HASHING
    hash_function: str = "md5"  # md5, sha1, sha256, crc32
    virtual_nodes: int = 100  # For consistent hashing
    
    # Replication settings
    replication_mode: ReplicationMode = ReplicationMode.ASYNC
    replication_factor: int = 2
    read_repair_enabled: bool = True
    
    # Consistency settings
    consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL
    read_quorum: int = 1
    write_quorum: int = 1
    
    # Failover and recovery
    failover_policy: FailoverPolicy = FailoverPolicy.RETRY
    max_retry_attempts: int = 3
    retry_delay_ms: int = 100
    retry_exponential_backoff: bool = True
    
    # Health monitoring
    health_check_enabled: bool = True
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 5  # seconds
    unhealthy_threshold: int = 3  # consecutive failures
    recovery_threshold: int = 2  # consecutive successes
    
    # Performance settings
    connection_pool_size: int = 10
    request_timeout: int = 5000  # milliseconds
    batch_size: int = 100
    pipeline_enabled: bool = True
    compression_enabled: bool = True
    
    # Load balancing
    load_balancing_enabled: bool = True
    load_update_interval: int = 60  # seconds
    locality_preference: bool = True
    cross_region_penalty: int = 50  # milliseconds
    
    # Circuit breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 10
    circuit_breaker_timeout: int = 60  # seconds
    circuit_breaker_recovery_timeout: int = 30  # seconds
    
    # Monitoring and metrics
    enable_metrics: bool = True
    metrics_collection_interval: int = 60
    track_node_performance: bool = True
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @validator('replication_factor')
    def validate_replication_factor(cls, v, values):
        nodes_count = len(values.get('nodes', {}))
        if nodes_count > 0 and v > nodes_count:
            raise ValueError(f"Replication factor ({v}) cannot exceed number of nodes ({nodes_count})")
        return v
    
    @validator('read_quorum', 'write_quorum')
    def validate_quorum(cls, v, values):
        replication_factor = values.get('replication_factor', 1)
        if v > replication_factor:
            raise ValueError(f"Quorum ({v}) cannot exceed replication factor ({replication_factor})")
        return v
    
    def add_node(self, node: CacheNode):
        """Add node to cluster"""        self.nodes[node.id] = node
    
    def remove_node(self, node_id: str) -> bool:
        """Remove node from cluster"""        if node_id in self.nodes:
            del self.nodes[node_id]
            
            # Remove from regions
            for region in self.regions.values():
                if node_id in region.primary_nodes:
                    region.primary_nodes.remove(node_id)
                if node_id in region.replica_nodes:
                    region.replica_nodes.remove(node_id)
            
            return True
        return False
    
    def get_healthy_nodes(self) -> List[CacheNode]:
        """Get list of healthy nodes"""        return [node for node in self.nodes.values() if node.is_healthy]
    
    def get_nodes_by_region(self, region_name: str) -> List[CacheNode]:
        """Get nodes in specific region"""        return [node for node in self.nodes.values() if node.region == region_name]
    
    def calculate_consistent_hash(self, key: str) -> List[CacheNode]:
        """Calculate consistent hash ring for key distribution"""        if self.distribution_strategy != DistributionStrategy.CONSISTENT_HASHING:
            return list(self.get_healthy_nodes())
        
        # Create virtual nodes
        hash_ring = []
        healthy_nodes = self.get_healthy_nodes()
        
        for node in healthy_nodes:
            for i in range(self.virtual_nodes):
                virtual_key = f"{node.id}:{i}"
                hash_value = self._hash_key(virtual_key)
                hash_ring.append((hash_value, node))
        
        # Sort by hash value
        hash_ring.sort(key=lambda x: x[0])
        
        if not hash_ring:
            return []
        
        # Find position for key
        key_hash = self._hash_key(key)
        
        # Find first node with hash >= key_hash
        selected_nodes = []
        for hash_value, node in hash_ring:
            if hash_value >= key_hash:
                if node not in selected_nodes:
                    selected_nodes.append(node)
                if len(selected_nodes) >= self.replication_factor:
                    break
        
        # If we need more nodes, wrap around
        if len(selected_nodes) < self.replication_factor:
            for hash_value, node in hash_ring:
                if node not in selected_nodes:
                    selected_nodes.append(node)
                if len(selected_nodes) >= self.replication_factor:
                    break
        
        return selected_nodes[:self.replication_factor]
    
    def get_read_nodes(self, key: str, region: Optional[str] = None) -> List[CacheNode]:
        """Get nodes for read operation"""        if region and region in self.regions:
            region_config = self.regions[region]
            nodes = region_config.get_read_nodes(self.nodes)
            if nodes:
                return nodes
        
        # Fallback to distribution strategy
        candidate_nodes = self.calculate_consistent_hash(key)
        
        if self.locality_preference and region:
            # Prefer nodes in same region
            local_nodes = [n for n in candidate_nodes if n.region == region]
            if local_nodes:
                return local_nodes[:self.read_quorum]
        
        return candidate_nodes[:self.read_quorum]
    
    def get_write_nodes(self, key: str, region: Optional[str] = None) -> List[CacheNode]:
        """Get nodes for write operation"""        if region and region in self.regions:
            region_config = self.regions[region]
            nodes = region_config.get_write_nodes(self.nodes)
            if nodes:
                return nodes
        
        # Fallback to distribution strategy
        candidate_nodes = self.calculate_consistent_hash(key)
        return candidate_nodes[:self.write_quorum]
    
    def select_nodes_by_load(self, candidate_nodes: List[CacheNode], count: int) -> List[CacheNode]:
        """Select nodes based on load balancing"""        if not self.load_balancing_enabled or not candidate_nodes:
            return candidate_nodes[:count]
        
        # Sort by load score (higher is better)
        sorted_nodes = sorted(candidate_nodes, key=lambda n: n.calculate_load_score(), reverse=True)
        return sorted_nodes[:count]
    
    def _hash_key(self, key: str) -> int:
        """Hash key using configured hash function"""        if self.hash_function == "md5":
            return int(hashlib.md5(key.encode()).hexdigest(), 16)
        elif self.hash_function == "sha1":
            return int(hashlib.sha1(key.encode()).hexdigest(), 16)
        elif self.hash_function == "sha256":
            return int(hashlib.sha256(key.encode()).hexdigest(), 16)
        elif self.hash_function == "crc32":
            import zlib
            return zlib.crc32(key.encode()) & 0xffffffff
        else:
            # Default to MD5
            return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def get_cluster_topology(self) -> Dict[str, Any]:
        """Get cluster topology information"""        healthy_nodes = self.get_healthy_nodes()
        total_nodes = len(self.nodes)
        
        regions_info = {}
        for region_name, region_config in self.regions.items():
            region_nodes = self.get_nodes_by_region(region_name)
            regions_info[region_name] = {
                "total_nodes": len(region_nodes),
                "healthy_nodes": len([n for n in region_nodes if n.is_healthy]),
                "primary_nodes": len(region_config.primary_nodes),
                "replica_nodes": len(region_config.replica_nodes)
            }
        
        return {
            "cluster_name": self.cluster_name,
            "total_nodes": total_nodes,
            "healthy_nodes": len(healthy_nodes),
            "unhealthy_nodes": total_nodes - len(healthy_nodes),
            "distribution_strategy": self.distribution_strategy,
            "replication_factor": self.replication_factor,
            "consistency_level": self.consistency_level,
            "regions": regions_info
        }


class DistributedCacheManager:
    """    Manager for distributed cache operations
    """    
    def __init__(self, config: DistributedCacheConfig):
        self.config = config
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.node_stats: Dict[str, Dict[str, Any]] = {}
        self.health_check_task = None
    
    async def start(self):
        """Start distributed cache manager"""        if self.config.health_check_enabled:
            self.health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def stop(self):
        """Stop distributed cache manager"""        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
    
    async def get_distributed(self, key: str, region: Optional[str] = None) -> Optional[Any]:
        """Get value from distributed cache"""        read_nodes = self.config.get_read_nodes(key, region)
        
        if not read_nodes:
            return None
        
        # Try nodes in order until success or exhaustion
        for node in read_nodes:
            if not self._is_node_available(node):
                continue
            
            try:
                value = await self._get_from_node(node, key)
                if value is not None:
                    self._record_success(node)
                    return value
            except Exception as e:
                self._record_failure(node, str(e))
                continue
        
        return None
    
    async def set_distributed(self, key: str, value: Any, ttl: Optional[int] = None, 
                            region: Optional[str] = None) -> bool:
        """Set value in distributed cache"""        write_nodes = self.config.get_write_nodes(key, region)
        
        if not write_nodes:
            return False
        
        if self.config.consistency_level == ConsistencyLevel.STRONG:
            # Synchronous replication - all nodes must succeed
            return await self._set_sync(write_nodes, key, value, ttl)
        else:
            # Asynchronous replication - fire and forget for replicas
            return await self._set_async(write_nodes, key, value, ttl)
    
    async def delete_distributed(self, key: str, region: Optional[str] = None) -> bool:
        """Delete value from distributed cache"""        nodes = self.config.get_write_nodes(key, region)
        
        if not nodes:
            return False
        
        success_count = 0
        
        for node in nodes:
            if not self._is_node_available(node):
                continue
            
            try:
                if await self._delete_from_node(node, key):
                    success_count += 1
                    self._record_success(node)
            except Exception as e:
                self._record_failure(node, str(e))
        
        # Consider successful if at least one write succeeded
        return success_count > 0
    
    async def _set_sync(self, nodes: List[CacheNode], key: str, value: Any, ttl: Optional[int]) -> bool:
        """Synchronous distributed set operation"""        tasks = []
        
        for node in nodes:
            if self._is_node_available(node):
                task = self._set_to_node(node, key, value, ttl)
                tasks.append((node, task))
        
        if not tasks:
            return False
        
        # Wait for all operations
        success_count = 0
        
        for node, task in tasks:
            try:
                result = await task
                if result:
                    success_count += 1
                    self._record_success(node)
                else:
                    self._record_failure(node, "Set operation failed")
            except Exception as e:
                self._record_failure(node, str(e))
        
        # Success if quorum is met
        return success_count >= self.config.write_quorum
    
    async def _set_async(self, nodes: List[CacheNode], key: str, value: Any, ttl: Optional[int]) -> bool:
        """Asynchronous distributed set operation"""        if not nodes:
            return False
        
        # Set to first available node synchronously
        primary_node = nodes[0]
        
        if not self._is_node_available(primary_node):
            return False
        
        try:
            result = await self._set_to_node(primary_node, key, value, ttl)
            
            if result:
                self._record_success(primary_node)
                
                # Replicate to other nodes asynchronously
                if len(nodes) > 1:
                    asyncio.create_task(self._replicate_async(nodes[1:], key, value, ttl))
                
                return True
            else:
                self._record_failure(primary_node, "Set operation failed")
                return False
                
        except Exception as e:
            self._record_failure(primary_node, str(e))
            return False
    
    async def _replicate_async(self, nodes: List[CacheNode], key: str, value: Any, ttl: Optional[int]):
        """Asynchronously replicate to replica nodes"""        tasks = []
        
        for node in nodes:
            if self._is_node_available(node):
                task = self._set_to_node(node, key, value, ttl)
                tasks.append((node, task))
        
        # Execute replication without waiting
        for node, task in tasks:
            try:
                result = await task
                if result:
                    self._record_success(node)
                else:
                    self._record_failure(node, "Replication failed")
            except Exception as e:
                self._record_failure(node, str(e))
    
    async def _get_from_node(self, node: CacheNode, key: str) -> Optional[Any]:
        """Get value from specific node"""        # This would be implemented with actual cache client
        # Placeholder implementation
        return None
    
    async def _set_to_node(self, node: CacheNode, key: str, value: Any, ttl: Optional[int]) -> bool:
        """Set value to specific node"""        # This would be implemented with actual cache client
        # Placeholder implementation
        return True
    
    async def _delete_from_node(self, node: CacheNode, key: str) -> bool:
        """Delete value from specific node"""        # This would be implemented with actual cache client
        # Placeholder implementation
        return True
    
    def _is_node_available(self, node: CacheNode) -> bool:
        """Check if node is available for operations"""        if not node.is_healthy:
            return False
        
        # Check circuit breaker
        if self.config.circuit_breaker_enabled:
            breaker_state = self.circuit_breakers.get(node.id, {"state": "closed", "failures": 0})
            if breaker_state["state"] == "open":
                # Check if enough time has passed for recovery attempt
                if time.time() - breaker_state.get("opened_at", 0) > self.config.circuit_breaker_timeout:
                    breaker_state["state"] = "half_open"
                    self.circuit_breakers[node.id] = breaker_state
                    return True
                return False
        
        return True
    
    def _record_success(self, node: CacheNode):
        """Record successful operation for node"""        if node.id not in self.node_stats:
            self.node_stats[node.id] = {"successes": 0, "failures": 0, "last_success": None}
        
        self.node_stats[node.id]["successes"] += 1
        self.node_stats[node.id]["last_success"] = time.time()
        
        # Reset circuit breaker on success
        if self.config.circuit_breaker_enabled and node.id in self.circuit_breakers:
            breaker = self.circuit_breakers[node.id]
            if breaker["state"] == "half_open":
                breaker["state"] = "closed"
                breaker["failures"] = 0
    
    def _record_failure(self, node: CacheNode, error: str):
        """Record failed operation for node"""        if node.id not in self.node_stats:
            self.node_stats[node.id] = {"successes": 0, "failures": 0, "last_failure": None}
        
        self.node_stats[node.id]["failures"] += 1
        self.node_stats[node.id]["last_failure"] = time.time()
        
        # Update circuit breaker
        if self.config.circuit_breaker_enabled:
            if node.id not in self.circuit_breakers:
                self.circuit_breakers[node.id] = {"state": "closed", "failures": 0}
            
            breaker = self.circuit_breakers[node.id]
            breaker["failures"] += 1
            
            if breaker["failures"] >= self.config.circuit_breaker_threshold:
                breaker["state"] = "open"
                breaker["opened_at"] = time.time()
    
    async def _health_check_loop(self):
        """Periodic health check for all nodes"""        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception:
                # Log error and continue
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _perform_health_checks(self):
        """Perform health checks on all nodes"""        tasks = []
        
        for node in self.config.nodes.values():
            task = self._check_node_health(node)
            tasks.append((node, task))
        
        # Execute health checks concurrently
        for node, task in tasks:
            try:
                is_healthy = await asyncio.wait_for(task, timeout=self.config.health_check_timeout)
                self._update_node_health(node, is_healthy)
            except asyncio.TimeoutError:
                self._update_node_health(node, False)
            except Exception:
                self._update_node_health(node, False)
    
    async def _check_node_health(self, node: CacheNode) -> bool:
        """Check health of specific node"""        # This would be implemented with actual health check logic
        # Placeholder implementation
        return True
    
    def _update_node_health(self, node: CacheNode, is_healthy: bool):
        """Update node health status"""        node.last_health_check = time.time()
        
        if is_healthy and not node.is_healthy:
            # Node recovered
            node.is_healthy = True
        elif not is_healthy and node.is_healthy:
            # Node failed
            node.is_healthy = False


# Default configurations for different deployment scenarios
SINGLE_REGION_CONFIG = DistributedCacheConfig(
    cluster_name="single-region-cache",
    nodes={
        "node1": CacheNode("node1", "cache-1.local", 6379, region="us-east-1"),
        "node2": CacheNode("node2", "cache-2.local", 6379, region="us-east-1"),
        "node3": CacheNode("node3", "cache-3.local", 6379, region="us-east-1")
    },
    replication_factor=2,
    consistency_level=ConsistencyLevel.EVENTUAL
)

MULTI_REGION_CONFIG = DistributedCacheConfig(
    cluster_name="multi-region-cache",
    nodes={
        "us-east-1-1": CacheNode("us-east-1-1", "cache-us-1.internal", 6379, region="us-east-1"),
        "us-east-1-2": CacheNode("us-east-1-2", "cache-us-2.internal", 6379, region="us-east-1"),
        "eu-west-1-1": CacheNode("eu-west-1-1", "cache-eu-1.internal", 6379, region="eu-west-1"),
        "eu-west-1-2": CacheNode("eu-west-1-2", "cache-eu-2.internal", 6379, region="eu-west-1")
    },
    regions={
        "us-east-1": RegionConfig("us-east-1", ["us-east-1-1"], ["us-east-1-2"]),
        "eu-west-1": RegionConfig("eu-west-1", ["eu-west-1-1"], ["eu-west-1-2"])
    },
    replication_factor=3,
    consistency_level=ConsistencyLevel.EVENTUAL,
    locality_preference=True,
    cross_region_penalty=100
)

HIGH_AVAILABILITY_CONFIG = DistributedCacheConfig(
    cluster_name="ha-cache",
    nodes={
        f"node{i}": CacheNode(f"node{i}", f"cache-{i}.internal", 6379, weight=2)
        for i in range(1, 6)  # 5 nodes
    },
    replication_factor=3,
    consistency_level=ConsistencyLevel.STRONG,
    read_quorum=2,
    write_quorum=2,
    health_check_enabled=True,
    health_check_interval=15,
    circuit_breaker_enabled=True,
    failover_policy=FailoverPolicy.RETRY
)
