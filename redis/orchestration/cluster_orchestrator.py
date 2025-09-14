#!/usr/bin/env python3
"""
Redis Cluster Orchestrator - Ainflue Platform
==============================================

Enterprise-grade Redis cluster orchestration with intelligent management
and automatic scaling capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Roles: Lead Dev IA + Backend Senior + DBA + Microservices + DevOps
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from redis.asyncio.cluster import RedisCluster
import aiohttp
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """Redis node status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class ClusterState(Enum):
    """Redis cluster state enumeration"""
    STABLE = "stable"
    SCALING = "scaling"
    REBALANCING = "rebalancing"
    RECOVERING = "recovering"
    CRITICAL = "critical"


@dataclass
class NodeInfo:
    """Redis cluster node information"""
    node_id: str
    host: str
    port: int
    role: str  # master, replica
    status: NodeStatus
    slots: List[Tuple[int, int]]  # slot ranges
    memory_usage: float
    cpu_usage: float
    connections: int
    last_ping: float
    version: str
    uptime: int
    replication_lag: Optional[float] = None


@dataclass
class ClusterMetrics:
    """Redis cluster metrics"""
    total_nodes: int
    healthy_nodes: int
    total_memory: int
    used_memory: int
    total_connections: int
    operations_per_second: float
    average_latency: float
    hit_ratio: float
    state: ClusterState
    last_updated: float


class RedisClusterOrchestrator:
    """
    Enterprise Redis Cluster Orchestrator
    
    Features:
    - Intelligent cluster management
    - Automatic failover coordination
    - Real-time health monitoring
    - Performance optimization
    - Scaling automation
    - Disaster recovery
    """

    def __init__(self, config_path: str = "redis/config/cluster.yaml"):
        """Initialize cluster orchestrator"""
        self.config = self._load_config(config_path)
        self.cluster_client: Optional[RedisCluster] = None
        self.nodes: Dict[str, NodeInfo] = {}
        self.metrics: Optional[ClusterMetrics] = None
        self.monitoring_tasks: List[asyncio.Task] = []
        self.event_handlers: Dict[str, List[callable]] = {}
        self.last_health_check = 0
        
        # Performance thresholds
        self.memory_threshold = self.config.get('memory_threshold', 0.85)
        self.cpu_threshold = self.config.get('cpu_threshold', 0.80)
        self.latency_threshold = self.config.get('latency_threshold', 10.0)  # ms
        self.connection_threshold = self.config.get('connection_threshold', 1000)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load cluster configuration"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'cluster_nodes': [
                {'host': 'redis-node-1', 'port': 6379},
                {'host': 'redis-node-2', 'port': 6379},
                {'host': 'redis-node-3', 'port': 6379}
            ],
            'health_check_interval': 30,
            'failover_timeout': 10000,
            'monitoring_enabled': True,
            'auto_scaling': True,
            'memory_threshold': 0.85,
            'cpu_threshold': 0.80,
            'latency_threshold': 10.0,
            'connection_threshold': 1000
        }

    async def initialize(self) -> None:
        """Initialize cluster connection and monitoring"""
        try:
            # Create cluster client
            startup_nodes = [
                {"host": node['host'], "port": node['port']}
                for node in self.config['cluster_nodes']
            ]
            
            self.cluster_client = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=True,
                skip_full_coverage_check=True,
                max_connections_per_node=50,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                health_check_interval=30
            )
            
            # Test connection
            await self.cluster_client.ping()
            logger.info("Redis cluster connection established")
            
            # Initialize monitoring
            if self.config.get('monitoring_enabled', True):
                await self._start_monitoring()
                
            # Perform initial health check
            await self.health_check()
            
        except Exception as e:
            logger.error(f"Failed to initialize cluster orchestrator: {e}")
            raise

    async def _start_monitoring(self) -> None:
        """Start monitoring tasks"""
        try:
            # Health check task
            health_task = asyncio.create_task(self._health_check_loop())
            self.monitoring_tasks.append(health_task)
            
            # Metrics collection task
            metrics_task = asyncio.create_task(self._metrics_collection_loop())
            self.monitoring_tasks.append(metrics_task)
            
            # Auto-scaling task
            if self.config.get('auto_scaling', True):
                scaling_task = asyncio.create_task(self._auto_scaling_loop())
                self.monitoring_tasks.append(scaling_task)
            
            logger.info("Monitoring tasks started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")

    async def _health_check_loop(self) -> None:
        """Continuous health check loop"""
        while True:
            try:
                await self.health_check()
                interval = self.config.get('health_check_interval', 30)
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(10)

    async def _metrics_collection_loop(self) -> None:
        """Continuous metrics collection loop"""
        while True:
            try:
                await self.collect_metrics()
                await asyncio.sleep(30)  # Collect metrics every 30 seconds
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                await asyncio.sleep(10)

    async def _auto_scaling_loop(self) -> None:
        """Continuous auto-scaling loop"""
        while True:
            try:
                await self._check_scaling_needs()
                await asyncio.sleep(60)  # Check scaling needs every minute
            except Exception as e:
                logger.error(f"Auto-scaling loop error: {e}")
                await asyncio.sleep(30)

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive cluster health check"""
        health_status = {
            'timestamp': time.time(),
            'cluster_state': ClusterState.UNKNOWN.value,
            'nodes': {},
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Get cluster nodes info
            nodes_info = await self.cluster_client.cluster_nodes()
            
            # Parse nodes information
            self.nodes = {}
            healthy_count = 0
            total_count = 0
            
            for line in nodes_info.split('\n'):
                if line.strip():
                    node_info = await self._parse_node_info(line)
                    if node_info:
                        self.nodes[node_info.node_id] = node_info
                        health_status['nodes'][node_info.node_id] = asdict(node_info)
                        total_count += 1
                        
                        if node_info.status == NodeStatus.HEALTHY:
                            healthy_count += 1
            
            # Determine cluster state
            if healthy_count == total_count:
                health_status['cluster_state'] = ClusterState.STABLE.value
            elif healthy_count >= total_count * 0.8:
                health_status['cluster_state'] = ClusterState.DEGRADED.value
            else:
                health_status['cluster_state'] = ClusterState.CRITICAL.value
                
            # Check for issues and generate recommendations
            await self._analyze_cluster_health(health_status)
            
            self.last_health_check = time.time()
            
            # Trigger event handlers
            await self._trigger_event('health_check_completed', health_status)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status['cluster_state'] = ClusterState.CRITICAL.value
            health_status['issues'].append(f"Health check failed: {str(e)}")
            return health_status

    async def _parse_node_info(self, node_line: str) -> Optional[NodeInfo]:
        """Parse Redis cluster node information"""
        try:
            parts = node_line.split()
            if len(parts) < 8:
                return None
                
            node_id = parts[0]
            endpoint = parts[1].split('@')[0]  # Remove bus port
            host, port = endpoint.split(':')
            flags = parts[2]
            
            # Determine role and status
            role = 'master' if 'master' in flags else 'replica'
            if 'fail' in flags:
                status = NodeStatus.FAILED
            elif 'handshake' in flags or 'noaddr' in flags:
                status = NodeStatus.UNKNOWN
            else:
                status = NodeStatus.HEALTHY
            
            # Parse slot ranges
            slots = []
            for i in range(8, len(parts)):
                if '-' in parts[i]:
                    start, end = parts[i].split('-')
                    slots.append((int(start), int(end)))
                elif parts[i].isdigit():
                    slot_num = int(parts[i])
                    slots.append((slot_num, slot_num))
            
            return NodeInfo(
                node_id=node_id,
                host=host,
                port=int(port),
                role=role,
                status=status,
                slots=slots,
                memory_usage=0.0,  # Will be updated with detailed metrics
                cpu_usage=0.0,
                connections=0,
                last_ping=time.time(),
                version="unknown",
                uptime=0
            )
            
        except Exception as e:
            logger.error(f"Failed to parse node info: {e}")
            return None

    async def _analyze_cluster_health(self, health_status: Dict[str, Any]) -> None:
        """Analyze cluster health and generate recommendations"""
        issues = health_status['issues']
        recommendations = health_status['recommendations']
        
        # Check for failed nodes
        failed_nodes = [
            node for node in self.nodes.values()
            if node.status == NodeStatus.FAILED
        ]
        
        if failed_nodes:
            issues.append(f"Found {len(failed_nodes)} failed nodes")
            recommendations.append("Investigate and replace failed nodes")
        
        # Check memory usage
        high_memory_nodes = [
            node for node in self.nodes.values()
            if node.memory_usage > self.memory_threshold
        ]
        
        if high_memory_nodes:
            issues.append(f"High memory usage on {len(high_memory_nodes)} nodes")
            recommendations.append("Consider scaling cluster or optimizing memory usage")
        
        # Check for uneven slot distribution
        slot_distribution = {}
        for node in self.nodes.values():
            if node.role == 'master':
                slot_count = sum(end - start + 1 for start, end in node.slots)
                slot_distribution[node.node_id] = slot_count
        
        if slot_distribution:
            avg_slots = sum(slot_distribution.values()) / len(slot_distribution)
            unbalanced_nodes = [
                node_id for node_id, slots in slot_distribution.items()
                if abs(slots - avg_slots) > avg_slots * 0.2  # 20% variance
            ]
            
            if unbalanced_nodes:
                issues.append("Uneven slot distribution detected")
                recommendations.append("Consider rebalancing cluster slots")

    async def collect_metrics(self) -> ClusterMetrics:
        """Collect comprehensive cluster metrics"""
        try:
            total_memory = 0
            used_memory = 0
            total_connections = 0
            operations_count = 0
            latency_sum = 0.0
            hit_count = 0
            miss_count = 0
            
            healthy_nodes = 0
            total_nodes = len(self.nodes)
            
            # Collect metrics from each node
            for node in self.nodes.values():
                if node.status == NodeStatus.HEALTHY:
                    healthy_nodes += 1
                    
                    try:
                        # Connect to individual node for detailed metrics
                        node_client = redis.Redis(
                            host=node.host,
                            port=node.port,
                            decode_responses=True
                        )
                        
                        # Get memory info
                        memory_info = await node_client.info('memory')
                        node_used_memory = memory_info.get('used_memory', 0)
                        node_max_memory = memory_info.get('maxmemory', 0)
                        
                        if node_max_memory > 0:
                            node.memory_usage = node_used_memory / node_max_memory
                        
                        total_memory += node_max_memory
                        used_memory += node_used_memory
                        
                        # Get connection info
                        clients_info = await node_client.info('clients')
                        node_connections = clients_info.get('connected_clients', 0)
                        node.connections = node_connections
                        total_connections += node_connections
                        
                        # Get stats info
                        stats_info = await node_client.info('stats')
                        operations_count += stats_info.get('total_commands_processed', 0)
                        hit_count += stats_info.get('keyspace_hits', 0)
                        miss_count += stats_info.get('keyspace_misses', 0)
                        
                        # Measure latency
                        start_time = time.time()
                        await node_client.ping()
                        latency = (time.time() - start_time) * 1000  # ms
                        latency_sum += latency
                        
                        await node_client.close()
                        
                    except Exception as e:
                        logger.warning(f"Failed to collect metrics from node {node.node_id}: {e}")
            
            # Calculate averages and ratios
            avg_latency = latency_sum / healthy_nodes if healthy_nodes > 0 else 0
            hit_ratio = hit_count / (hit_count + miss_count) if (hit_count + miss_count) > 0 else 0
            
            # Determine cluster state
            state = ClusterState.STABLE
            if healthy_nodes < total_nodes:
                state = ClusterState.DEGRADED
            if healthy_nodes < total_nodes * 0.5:
                state = ClusterState.CRITICAL
            
            self.metrics = ClusterMetrics(
                total_nodes=total_nodes,
                healthy_nodes=healthy_nodes,
                total_memory=total_memory,
                used_memory=used_memory,
                total_connections=total_connections,
                operations_per_second=operations_count,  # Simplified calculation
                average_latency=avg_latency,
                hit_ratio=hit_ratio,
                state=state,
                last_updated=time.time()
            )
            
            # Trigger metrics event
            await self._trigger_event('metrics_collected', asdict(self.metrics))
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            raise

    async def _check_scaling_needs(self) -> None:
        """Check if cluster needs scaling"""
        if not self.metrics:
            return
            
        recommendations = []
        
        # Check memory usage
        memory_ratio = self.metrics.used_memory / self.metrics.total_memory if self.metrics.total_memory > 0 else 0
        if memory_ratio > self.memory_threshold:
            recommendations.append({
                'type': 'scale_out',
                'reason': f'High memory usage: {memory_ratio:.2%}',
                'priority': 'high'
            })
        
        # Check latency
        if self.metrics.average_latency > self.latency_threshold:
            recommendations.append({
                'type': 'performance_optimization',
                'reason': f'High latency: {self.metrics.average_latency:.2f}ms',
                'priority': 'medium'
            })
        
        # Check hit ratio
        if self.metrics.hit_ratio < 0.9:  # Less than 90% hit ratio
            recommendations.append({
                'type': 'cache_optimization',
                'reason': f'Low hit ratio: {self.metrics.hit_ratio:.2%}',
                'priority': 'medium'
            })
        
        if recommendations:
            await self._trigger_event('scaling_recommendations', recommendations)

    async def failover_node(self, node_id: str, force: bool = False) -> Dict[str, Any]:
        """Initiate failover for a specific node"""
        try:
            if node_id not in self.nodes:
                raise ValueError(f"Node {node_id} not found")
                
            node = self.nodes[node_id]
            if node.role != 'master':
                raise ValueError(f"Cannot failover replica node {node_id}")
            
            # Find replica for this master
            replica_node = None
            for replica in self.nodes.values():
                if replica.role == 'replica' and replica.status == NodeStatus.HEALTHY:
                    # Simple logic - in production, this should check actual master-replica relationships
                    replica_node = replica
                    break
            
            if not replica_node and not force:
                raise ValueError(f"No healthy replica found for master {node_id}")
            
            # Execute failover
            failover_result = await self.cluster_client.cluster_failover()
            
            result = {
                'timestamp': time.time(),
                'failed_node': node_id,
                'new_master': replica_node.node_id if replica_node else None,
                'success': True,
                'details': failover_result
            }
            
            # Trigger failover event
            await self._trigger_event('node_failover', result)
            
            logger.info(f"Failover completed for node {node_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failover failed for node {node_id}: {e}")
            result = {
                'timestamp': time.time(),
                'failed_node': node_id,
                'success': False,
                'error': str(e)
            }
            return result

    async def rebalance_cluster(self) -> Dict[str, Any]:
        """Rebalance cluster slots for optimal distribution"""
        try:
            # This is a simplified rebalancing - production version would be more sophisticated
            rebalance_result = await self.cluster_client.cluster_rebalance()
            
            result = {
                'timestamp': time.time(),
                'success': True,
                'details': rebalance_result
            }
            
            await self._trigger_event('cluster_rebalanced', result)
            logger.info("Cluster rebalancing completed")
            
            return result
            
        except Exception as e:
            logger.error(f"Cluster rebalancing failed: {e}")
            return {
                'timestamp': time.time(),
                'success': False,
                'error': str(e)
            }

    def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def _trigger_event(self, event_type: str, data: Any) -> None:
        """Trigger event handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_type, data)
                    else:
                        handler(event_type, data)
                except Exception as e:
                    logger.error(f"Event handler error for {event_type}: {e}")

    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status"""
        return {
            'nodes': {node_id: asdict(node) for node_id, node in self.nodes.items()},
            'metrics': asdict(self.metrics) if self.metrics else None,
            'last_health_check': self.last_health_check,
            'monitoring_active': len(self.monitoring_tasks) > 0
        }

    async def shutdown(self) -> None:
        """Gracefully shutdown orchestrator"""
        try:
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            # Close cluster client
            if self.cluster_client:
                await self.cluster_client.close()
            
            logger.info("Cluster orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Example usage and testing
async def main():
    """Example usage of Redis Cluster Orchestrator"""
    try:
        # Initialize orchestrator
        orchestrator = RedisClusterOrchestrator()
        
        # Register event handlers
        async def health_event_handler(event_type: str, data: Any):
            print(f"Health Event: {event_type}")
            if data.get('issues'):
                print(f"Issues found: {data['issues']}")
        
        orchestrator.register_event_handler('health_check_completed', health_event_handler)
        
        # Start orchestrator
        await orchestrator.initialize()
        
        # Run for a while to demonstrate monitoring
        print("Orchestrator running... Press Ctrl+C to stop")
        await asyncio.sleep(300)  # Run for 5 minutes
        
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'orchestrator' in locals():
            await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())