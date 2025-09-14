"""MongoDB Load Balancer
======================

Intelligent database load balancing and traffic distribution for MongoDB clusters
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import random
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import threading

try:
    import pymongo
    from pymongo import MongoClient, ReadPreference
    from pymongo.errors import ServerSelectionTimeoutError, NetworkTimeout
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    GEOGRAPHIC = "geographic"
    INTELLIGENT = "intelligent"

class NodeRole(Enum):
    """Database node roles."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ARBITER = "arbiter"

@dataclass
class NodeMetrics:
    """Node performance metrics."""
    node_id: str
    host: str
    port: int
    role: NodeRole
    active_connections: int
    response_time_ms: float
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    error_rate: float
    last_updated: datetime
    weight: float = 1.0
    available: bool = True

@dataclass
class ConnectionPool:
    """Connection pool information."""
    pool_id: str
    max_connections: int
    active_connections: int
    idle_connections: int
    waiting_requests: int
    created_connections: int
    destroyed_connections: int

class LoadBalancer:
    """Enterprise-grade MongoDB load balancer with intelligent routing."""
    
    def __init__(self, 
                 nodes -> None: List[Dict[str, Any]], 
                 strategy -> None: LoadBalancingStrategy = LoadBalancingStrategy.INTELLIGENT) -> None:
        """Initialize load balancer."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for load balancing")
            
        self.nodes = {}
        self.strategy = strategy
        self.current_index = 0
        self.metrics_history = {}
        self.connection_pools = {}
        
        # Configuration
        self.health_check_interval = 30  # seconds
        self.metrics_window = 300  # 5 minutes
        self.connection_timeout = 5000  # milliseconds
        self.max_retries = 3
        
        # Initialize nodes
        for node_config in nodes:
            self._add_node(node_config)
        
        # Start monitoring
        self._start_monitoring()
    
    def _add_node(self, node_config -> None: Dict[str, Any]) -> None:
        """Add a node to the load balancer."""
        node_id = f"{node_config['host']}:{node_config['port']}"
        
        metrics = NodeMetrics(
            node_id=node_id,
            host=node_config['host'],
            port=node_config['port'],
            role=NodeRole(node_config.get('role', 'secondary')),
            active_connections=0,
            response_time_ms=0.0,
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_io=0.0,
            network_io=0.0,
            error_rate=0.0,
            last_updated=datetime.now(),
            weight=node_config.get('weight', 1.0),
            available=True
        )
        
        self.nodes[node_id] = metrics
        self.metrics_history[node_id] = []
        
        # Create connection pool
        self.connection_pools[node_id] = self._create_connection_pool(node_config)
        
        logger.info(f"Added node to load balancer: {node_id}")
    
    def _create_connection_pool(self, node_config: Dict[str, Any]) -> MongoClient:
        """Create a connection pool for a node."""
        connection_string = f"mongodb://{node_config['host']}:{node_config['port']}/"
        
        client = MongoClient(
            connection_string,
            maxPoolSize=node_config.get('max_connections', 100),
            minPoolSize=node_config.get('min_connections', 10),
            connectTimeoutMS=self.connection_timeout,
            serverSelectionTimeoutMS=self.connection_timeout,
            socketTimeoutMS=30000,
            retryWrites=True,
            retryReads=True
        )
        
        return client
    
    def get_connection(self, 
                      read_preference: str = "secondary", 
                      operation_type: str = "read") -> Optional[MongoClient]:
        """Get an optimal connection based on the load balancing strategy."""
        try:
            if operation_type == "write":
                # Always route writes to primary
                primary_node = self._find_primary_node()
                if primary_node:
                    return self.connection_pools[primary_node]
                else:
                    logger.error("No primary node available for write operations")
                    return None
            
            # For read operations, use load balancing strategy
            selected_node = self._select_node_for_read(read_preference)
            
            if selected_node:
                self._update_connection_metrics(selected_node)
                return self.connection_pools[selected_node]
            else:
                logger.warning("No available nodes for read operations")
                return None
                
        except Exception as e:
            logger.error(f"Error getting connection: {e}")
            return None
    
    def _select_node_for_read(self, read_preference: str) -> Optional[str]:
        """Select the best node for read operations."""
        available_nodes = [
            node_id for node_id, metrics in self.nodes.items()
            if metrics.available and self._is_readable_node(metrics, read_preference)
        ]
        
        if not available_nodes:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_nodes)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(available_nodes)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(available_nodes)
        elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
            return self._response_time_selection(available_nodes)
        elif self.strategy == LoadBalancingStrategy.INTELLIGENT:
            return self._intelligent_selection(available_nodes)
        else:
            return random.choice(available_nodes)
    
    def _round_robin_selection(self, nodes: List[str]) -> str:
        """Round-robin node selection."""
        if not nodes:
            return None
        
        selected = nodes[self.current_index % len(nodes)]
        self.current_index += 1
        return selected
    
    def _weighted_round_robin_selection(self, nodes: List[str]) -> str:
        """Weighted round-robin selection based on node weights."""
        if not nodes:
            return None
        
        # Calculate total weight
        total_weight = sum(self.nodes[node_id].weight for node_id in nodes)
        
        # Generate random number and select based on weight
        target = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for node_id in nodes:
            cumulative_weight += self.nodes[node_id].weight
            if cumulative_weight >= target:
                return node_id
        
        return nodes[0]  # Fallback
    
    def _least_connections_selection(self, nodes: List[str]) -> str:
        """Select node with least active connections."""
        if not nodes:
            return None
        
        return min(nodes, key=lambda n: self.nodes[n].active_connections)
    
    def _response_time_selection(self, nodes: List[str]) -> str:
        """Select node with best response time."""
        if not nodes:
            return None
        
        return min(nodes, key=lambda n: self.nodes[n].response_time_ms)
    
    def _intelligent_selection(self, nodes: List[str]) -> str:
        """Intelligent node selection based on multiple factors."""
        if not nodes:
            return None
        
        # Calculate composite score for each node
        scored_nodes = []
        
        for node_id in nodes:
            metrics = self.nodes[node_id]
            
            # Normalize metrics (lower is better for these metrics)
            connection_score = 1.0 / (1.0 + metrics.active_connections)
            response_score = 1.0 / (1.0 + metrics.response_time_ms)
            cpu_score = 1.0 / (1.0 + metrics.cpu_usage)
            error_score = 1.0 / (1.0 + metrics.error_rate)
            
            # Weight factors
            composite_score = (
                connection_score * 0.3 +
                response_score * 0.3 +
                cpu_score * 0.2 +
                error_score * 0.2
            ) * metrics.weight
            
            scored_nodes.append((node_id, composite_score))
        
        # Select node with highest score
        best_node = max(scored_nodes, key=lambda x: x[1])
        return best_node[0]
    
    def _is_readable_node(self, metrics: NodeMetrics, read_preference: str) -> bool:
        """Check if a node is suitable for read operations."""
        if read_preference == "primary":
            return metrics.role == NodeRole.PRIMARY
        elif read_preference == "secondary":
            return metrics.role == NodeRole.SECONDARY
        elif read_preference == "primaryPreferred":
            return True  # Can read from any node, prefer primary
        elif read_preference == "secondaryPreferred":
            return True  # Can read from any node, prefer secondary
        else:  # nearest
            return metrics.role != NodeRole.ARBITER
    
    def _find_primary_node(self) -> Optional[str]:
        """Find the current primary node."""
        for node_id, metrics in self.nodes.items():
            if metrics.role == NodeRole.PRIMARY and metrics.available:
                return node_id
        return None
    
    def _update_connection_metrics(self, node_id -> None: str) -> None:
        """Update connection metrics for a node."""
        if node_id in self.nodes:
            self.nodes[node_id].active_connections += 1
    
    def release_connection(self, node_id -> None: str) -> None:
        """Release a connection back to the pool."""
        if node_id in self.nodes:
            self.nodes[node_id].active_connections = max(0, 
                self.nodes[node_id].active_connections - 1)
    
    def _start_monitoring(self) -> None:
        """Start background monitoring of node health and metrics."""
        def monitor() -> None:
            while True:
                try:
                    self._update_node_metrics()
                    self._cleanup_old_metrics()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"Error in monitoring thread: {e}")
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        logger.info("Started load balancer monitoring")
    
    def _update_node_metrics(self) -> None:
        """Update metrics for all nodes."""
        for node_id, client in self.connection_pools.items():
            try:
                start_time = time.time()
                
                # Perform health check
                result = client.admin.command("isMaster")
                
                response_time = (time.time() - start_time) * 1000  # milliseconds
                
                # Update metrics
                metrics = self.nodes[node_id]
                metrics.response_time_ms = response_time
                metrics.last_updated = datetime.now()
                metrics.available = True
                
                # Update role if changed
                if result.get("ismaster"):
                    metrics.role = NodeRole.PRIMARY
                elif result.get("secondary"):
                    metrics.role = NodeRole.SECONDARY
                
                # Get additional metrics if available
                try:
                    server_status = client.admin.command("serverStatus")
                    metrics.active_connections = server_status.get("connections", {}).get("current", 0)
                    
                    # Store metrics history
                    self.metrics_history[node_id].append({
                        "timestamp": datetime.now(),
                        "response_time": response_time,
                        "connections": metrics.active_connections
                    })
                    
                except Exception as e:
                    logger.debug(f"Could not get detailed metrics for {node_id}: {e}")
                
            except Exception as e:
                logger.warning(f"Health check failed for node {node_id}: {e}")
                self.nodes[node_id].available = False
                self.nodes[node_id].error_rate += 0.1
    
    def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics data."""
        cutoff_time = datetime.now() - timedelta(seconds=self.metrics_window)
        
        for node_id in self.metrics_history:
            self.metrics_history[node_id] = [
                m for m in self.metrics_history[node_id]
                if m["timestamp"] > cutoff_time
            ]
    
    def get_node_metrics(self) -> Dict[str, NodeMetrics]:
        """Get current metrics for all nodes."""
        return self.nodes.copy()
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """Get load balancing statistics."""
        total_connections = sum(m.active_connections for m in self.nodes.values())
        available_nodes = sum(1 for m in self.nodes.values() if m.available)
        
        avg_response_time = 0
        if self.nodes:
            avg_response_time = sum(m.response_time_ms for m in self.nodes.values()) / len(self.nodes)
        
        return {
            "total_nodes": len(self.nodes),
            "available_nodes": available_nodes,
            "total_connections": total_connections,
            "average_response_time_ms": avg_response_time,
            "strategy": self.strategy.value,
            "last_updated": datetime.now()
        }
    
    def add_node(self, node_config -> None: Dict[str, Any]) -> None:
        """Add a new node to the load balancer."""
        self._add_node(node_config)
    
    def remove_node(self, host -> None: str, port -> None: int) -> None:
        """Remove a node from the load balancer."""
        node_id = f"{host}:{port}"
        
        if node_id in self.nodes:
            # Close connection pool
            if node_id in self.connection_pools:
                self.connection_pools[node_id].close()
                del self.connection_pools[node_id]
            
            # Remove from tracking
            del self.nodes[node_id]
            del self.metrics_history[node_id]
            
            logger.info(f"Removed node from load balancer: {node_id}")
    
    def set_node_weight(self, host -> None: str, port -> None: int, weight -> None: float) -> None:
        """Set the weight for a specific node."""
        node_id = f"{host}:{port}"
        if node_id in self.nodes:
            self.nodes[node_id].weight = weight
            logger.info(f"Updated weight for node {node_id}: {weight}")
    
    def close(self) -> None:
        """Close all connection pools."""
        for client in self.connection_pools.values():
            client.close()
        
        logger.info("Load balancer connections closed")

# Export the main class
__all__ = ['LoadBalancer', 'LoadBalancingStrategy', 'NodeMetrics', 'NodeRole']