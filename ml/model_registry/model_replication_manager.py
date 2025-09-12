"""🔄 Model Replication Manager - Enterprise ML Infrastructure
===========================================================
Module: ml/model_registry/model_replication_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODEL REPLICATION & DISTRIBUTION SYSTEM
Enterprise model replication across data centers and edge locations
- Multi-region model replication
- Automatic failover and load balancing
- Consistency validation and conflict resolution
- Performance optimization for global distribution
"""

import asyncio
import logging
import time
import uuid
import hashlib
import zlib
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import aiofiles
import aiohttp

logger = logging.getLogger(__name__)


class ReplicationStrategy(Enum):
    """Model replication strategies"""
    MASTER_SLAVE = "master_slave"
    MASTER_MASTER = "master_master"
    RING_TOPOLOGY = "ring_topology"
    MESH_TOPOLOGY = "mesh_topology"
    HIERARCHICAL = "hierarchical"


class ReplicationStatus(Enum):
    """Replication status"""
    SYNCED = "synced"
    SYNCING = "syncing"
    OUT_OF_SYNC = "out_of_sync"
    FAILED = "failed"
    CONFLICTED = "conflicted"
    DISABLED = "disabled"


class RegionStatus(Enum):
    """Region status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"


@dataclass
class ReplicationNode:
    """Replication node configuration"""
    node_id: str
    region: str
    endpoint: str
    priority: int = 1
    status: RegionStatus = RegionStatus.ACTIVE
    last_sync: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplicationConfig:
    """Model replication configuration"""
    model_id: str
    strategy: ReplicationStrategy
    source_nodes: List[str]
    target_nodes: List[str]
    consistency_level: str = "eventual"
    sync_interval: int = 300  # seconds
    conflict_resolution: str = "timestamp"
    enabled: bool = True


@dataclass
class ReplicationMetrics:
    """Replication metrics"""
    model_id: str
    node_id: str
    sync_time: float
    data_transferred: int
    success_rate: float
    latency: float
    conflicts_resolved: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ModelReplicationManager:
    """Enterprise Model Replication Manager"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.nodes: Dict[str, ReplicationNode] = {}
        self.replication_configs: Dict[str, ReplicationConfig] = {}
        self.replication_status: Dict[str, Dict[str, ReplicationStatus]] = {}
        self.metrics: Dict[str, List[ReplicationMetrics]] = {}
        
        # Configuration
        self.default_sync_interval = self.config.get('default_sync_interval', 300)
        self.max_retry_attempts = self.config.get('max_retry_attempts', 3)
        self.compression_enabled = self.config.get('compression_enabled', True)
        self.encryption_enabled = self.config.get('encryption_enabled', True)
        
        # Monitoring
        self.sync_tasks: Dict[str, asyncio.Task] = {}
        self.health_check_interval = self.config.get('health_check_interval', 60)
        
        logger.info("🔄 Model Replication Manager initialized")
    
    async def register_node(self, node: ReplicationNode) -> bool:
        """Register a replication node"""
        try:
            self.nodes[node.node_id] = node
            
            # Initialize replication status for all models
            for model_id in self.replication_configs.keys():
                if model_id not in self.replication_status:
                    self.replication_status[model_id] = {}
                self.replication_status[model_id][node.node_id] = ReplicationStatus.OUT_OF_SYNC
            
            # Start health check for the node
            await self._start_health_check(node.node_id)
            
            logger.info(f"✅ Node registered: {node.node_id} in region {node.region}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registering node {node.node_id}: {e}")
            return False
    
    async def configure_replication(self, config: ReplicationConfig) -> bool:
        """Configure model replication"""
        try:
            self.replication_configs[config.model_id] = config
            
            # Initialize replication status
            if config.model_id not in self.replication_status:
                self.replication_status[config.model_id] = {}
            
            for node_id in config.target_nodes:
                self.replication_status[config.model_id][node_id] = ReplicationStatus.OUT_OF_SYNC
            
            # Start replication sync task if enabled
            if config.enabled:
                await self._start_replication_sync(config.model_id)
            
            logger.info(f"✅ Replication configured for model: {config.model_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configuring replication for {config.model_id}: {e}")
            return False
    
    async def replicate_model(
        self,
        model_id: str,
        source_node: str,
        target_nodes: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """Replicate model to target nodes"""
        try:
            if model_id not in self.replication_configs:
                raise ValueError(f"No replication config found for model {model_id}")
            
            config = self.replication_configs[model_id]
            targets = target_nodes or config.target_nodes
            
            results = {}
            
            # Get model data from source
            model_data = await self._get_model_data(model_id, source_node)
            if not model_data:
                raise ValueError(f"Failed to get model data from source {source_node}")
            
            # Replicate to each target
            for target_node in targets:
                if target_node not in self.nodes:
                    logger.warning(f"Target node {target_node} not registered")
                    results[target_node] = False
                    continue
                
                # Update status to syncing
                self.replication_status[model_id][target_node] = ReplicationStatus.SYNCING
                
                # Perform replication
                success = await self._replicate_to_node(
                    model_id, model_data, target_node
                )
                
                # Update status
                if success:
                    self.replication_status[model_id][target_node] = ReplicationStatus.SYNCED
                    self.nodes[target_node].last_sync = datetime.utcnow()
                else:
                    self.replication_status[model_id][target_node] = ReplicationStatus.FAILED
                
                results[target_node] = success
            
            # Record metrics
            await self._record_replication_metrics(model_id, source_node, targets, results)
            
            logger.info(f"✅ Model replication completed: {model_id}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error replicating model {model_id}: {e}")
            return {node: False for node in (target_nodes or [])}
    
    async def sync_all_models(self) -> Dict[str, Dict[str, bool]]:
        """Sync all configured models"""
        try:
            results = {}
            
            for model_id, config in self.replication_configs.items():
                if not config.enabled:
                    continue
                
                # Find the best source node
                source_node = await self._select_source_node(model_id, config.source_nodes)
                if not source_node:
                    logger.warning(f"No suitable source node for model {model_id}")
                    continue
                
                # Replicate to all targets
                model_results = await self.replicate_model(
                    model_id, source_node, config.target_nodes
                )
                results[model_id] = model_results
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error syncing all models: {e}")
            return {}
    
    async def get_replication_status(
        self,
        model_id: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get replication status"""
        try:
            if model_id:
                if model_id not in self.replication_status:
                    return {}
                
                status_data = {}
                for node_id, status in self.replication_status[model_id].items():
                    node = self.nodes.get(node_id)
                    status_data[node_id] = {
                        'status': status.value,
                        'region': node.region if node else 'unknown',
                        'last_sync': node.last_sync.isoformat() if node else None,
                        'priority': node.priority if node else 0
                    }
                
                return {model_id: status_data}
            else:
                # Return status for all models
                all_status = {}
                for mid, node_statuses in self.replication_status.items():
                    status_data = {}
                    for node_id, status in node_statuses.items():
                        node = self.nodes.get(node_id)
                        status_data[node_id] = {
                            'status': status.value,
                            'region': node.region if node else 'unknown',
                            'last_sync': node.last_sync.isoformat() if node else None,
                            'priority': node.priority if node else 0
                        }
                    all_status[mid] = status_data
                
                return all_status
                
        except Exception as e:
            logger.error(f"❌ Error getting replication status: {e}")
            return {}
    
    async def resolve_conflicts(self, model_id: str) -> bool:
        """Resolve replication conflicts"""
        try:
            if model_id not in self.replication_configs:
                return False
            
            config = self.replication_configs[model_id]
            conflicted_nodes = []
            
            # Find conflicted nodes
            for node_id, status in self.replication_status[model_id].items():
                if status == ReplicationStatus.CONFLICTED:
                    conflicted_nodes.append(node_id)
            
            if not conflicted_nodes:
                return True  # No conflicts to resolve
            
            # Apply conflict resolution strategy
            if config.conflict_resolution == "timestamp":
                await self._resolve_by_timestamp(model_id, conflicted_nodes)
            elif config.conflict_resolution == "priority":
                await self._resolve_by_priority(model_id, conflicted_nodes)
            elif config.conflict_resolution == "manual":
                await self._queue_manual_resolution(model_id, conflicted_nodes)
            
            logger.info(f"✅ Conflicts resolved for model: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resolving conflicts for {model_id}: {e}")
            return False
    
    async def failover_to_region(self, failed_region: str, target_region: str) -> bool:
        """Failover models from failed region to target region"""
        try:
            failed_nodes = [
                node_id for node_id, node in self.nodes.items()
                if node.region == failed_region
            ]
            
            target_nodes = [
                node_id for node_id, node in self.nodes.items()
                if node.region == target_region and node.status == RegionStatus.ACTIVE
            ]
            
            if not target_nodes:
                logger.error(f"No active nodes in target region {target_region}")
                return False
            
            # Mark failed nodes as inactive
            for node_id in failed_nodes:
                self.nodes[node_id].status = RegionStatus.INACTIVE
            
            # Redistribute models to target region
            for model_id, config in self.replication_configs.items():
                # Check if any source/target nodes are in failed region
                affected_sources = [n for n in config.source_nodes if n in failed_nodes]
                affected_targets = [n for n in config.target_nodes if n in failed_nodes]
                
                if affected_sources or affected_targets:
                    # Find alternative source
                    available_sources = [
                        n for n in config.source_nodes
                        if n not in failed_nodes and self.nodes[n].status == RegionStatus.ACTIVE
                    ]
                    
                    if available_sources:
                        source_node = available_sources[0]
                        # Replicate to target region
                        await self.replicate_model(model_id, source_node, target_nodes[:1])
            
            logger.info(f"✅ Failover completed: {failed_region} -> {target_region}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during failover: {e}")
            return False
    
    async def _get_model_data(self, model_id: str, source_node: str) -> Optional[bytes]:
        """Get model data from source node"""
        try:
            node = self.nodes.get(source_node)
            if not node:
                return None
            
            # In practice, this would fetch from the actual node
            # For now, simulate model data
            model_info = {
                'model_id': model_id,
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'source_node': source_node
            }
            
            data = json.dumps(model_info).encode('utf-8')
            
            # Apply compression if enabled
            if self.compression_enabled:
                data = zlib.compress(data)
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error getting model data: {e}")
            return None
    
    async def _replicate_to_node(
        self,
        model_id: str,
        model_data: bytes,
        target_node: str
    ) -> bool:
        """Replicate model data to target node"""
        try:
            node = self.nodes.get(target_node)
            if not node or node.status != RegionStatus.ACTIVE:
                return False
            
            # Simulate network transfer
            start_time = time.time()
            
            # In practice, this would make HTTP/gRPC call to target node
            # For now, simulate successful transfer
            await asyncio.sleep(0.1)  # Simulate network latency
            
            transfer_time = time.time() - start_time
            
            # Record metrics
            metrics = ReplicationMetrics(
                model_id=model_id,
                node_id=target_node,
                sync_time=transfer_time,
                data_transferred=len(model_data),
                success_rate=1.0,
                latency=transfer_time,
                conflicts_resolved=0
            )
            
            if model_id not in self.metrics:
                self.metrics[model_id] = []
            self.metrics[model_id].append(metrics)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error replicating to node {target_node}: {e}")
            return False
    
    async def _select_source_node(
        self,
        model_id: str,
        source_nodes: List[str]
    ) -> Optional[str]:
        """Select best source node for replication"""
        try:
            available_nodes = []
            
            for node_id in source_nodes:
                node = self.nodes.get(node_id)
                if node and node.status == RegionStatus.ACTIVE:
                    # Check if node has the model synced
                    if (model_id in self.replication_status and
                        node_id in self.replication_status[model_id] and
                        self.replication_status[model_id][node_id] == ReplicationStatus.SYNCED):
                        available_nodes.append((node_id, node.priority))
            
            if not available_nodes:
                return None
            
            # Sort by priority (higher priority first)
            available_nodes.sort(key=lambda x: x[1], reverse=True)
            return available_nodes[0][0]
            
        except Exception as e:
            logger.error(f"❌ Error selecting source node: {e}")
            return None
    
    async def _start_replication_sync(self, model_id: str):
        """Start background replication sync task"""
        try:
            if model_id in self.sync_tasks:
                self.sync_tasks[model_id].cancel()
            
            async def sync_loop():
                config = self.replication_configs[model_id]
                while config.enabled:
                    try:
                        source_node = await self._select_source_node(
                            model_id, config.source_nodes
                        )
                        if source_node:
                            await self.replicate_model(
                                model_id, source_node, config.target_nodes
                            )
                    except Exception as e:
                        logger.error(f"Error in sync loop for {model_id}: {e}")
                    
                    await asyncio.sleep(config.sync_interval)
            
            self.sync_tasks[model_id] = asyncio.create_task(sync_loop())
            
        except Exception as e:
            logger.error(f"❌ Error starting sync task for {model_id}: {e}")
    
    async def _start_health_check(self, node_id: str):
        """Start health check for node"""
        try:
            async def health_check_loop():
                while node_id in self.nodes:
                    try:
                        node = self.nodes[node_id]
                        
                        # Simulate health check
                        # In practice, this would ping the node endpoint
                        is_healthy = True  # Simulate healthy node
                        
                        if is_healthy:
                            if node.status == RegionStatus.INACTIVE:
                                node.status = RegionStatus.ACTIVE
                        else:
                            node.status = RegionStatus.DEGRADED
                    
                    except Exception as e:
                        logger.error(f"Health check error for {node_id}: {e}")
                        if node_id in self.nodes:
                            self.nodes[node_id].status = RegionStatus.DEGRADED
                    
                    await asyncio.sleep(self.health_check_interval)
            
            asyncio.create_task(health_check_loop())
            
        except Exception as e:
            logger.error(f"❌ Error starting health check for {node_id}: {e}")
    
    async def _resolve_by_timestamp(self, model_id: str, conflicted_nodes: List[str]):
        """Resolve conflicts by timestamp (latest wins)"""
        try:
            latest_node = None
            latest_time = None
            
            for node_id in conflicted_nodes:
                node = self.nodes.get(node_id)
                if node and (latest_time is None or node.last_sync > latest_time):
                    latest_time = node.last_sync
                    latest_node = node_id
            
            if latest_node:
                # Use latest node as source to sync others
                other_nodes = [n for n in conflicted_nodes if n != latest_node]
                await self.replicate_model(model_id, latest_node, other_nodes)
            
        except Exception as e:
            logger.error(f"❌ Error resolving by timestamp: {e}")
    
    async def _resolve_by_priority(self, model_id: str, conflicted_nodes: List[str]):
        """Resolve conflicts by node priority"""
        try:
            highest_priority_node = None
            highest_priority = -1
            
            for node_id in conflicted_nodes:
                node = self.nodes.get(node_id)
                if node and node.priority > highest_priority:
                    highest_priority = node.priority
                    highest_priority_node = node_id
            
            if highest_priority_node:
                # Use highest priority node as source
                other_nodes = [n for n in conflicted_nodes if n != highest_priority_node]
                await self.replicate_model(model_id, highest_priority_node, other_nodes)
            
        except Exception as e:
            logger.error(f"❌ Error resolving by priority: {e}")
    
    async def _queue_manual_resolution(self, model_id: str, conflicted_nodes: List[str]):
        """Queue conflict for manual resolution"""
        try:
            # In practice, this would notify administrators
            logger.warning(
                f"Manual conflict resolution required for model {model_id} "
                f"on nodes: {conflicted_nodes}"
            )
            
            # Mark as conflicted until manual resolution
            for node_id in conflicted_nodes:
                self.replication_status[model_id][node_id] = ReplicationStatus.CONFLICTED
            
        except Exception as e:
            logger.error(f"❌ Error queuing manual resolution: {e}")
    
    async def _record_replication_metrics(
        self,
        model_id: str,
        source_node: str,
        target_nodes: List[str],
        results: Dict[str, bool]
    ):
        """Record replication metrics"""
        try:
            success_count = sum(1 for success in results.values() if success)
            success_rate = success_count / len(results) if results else 0
            
            # Record overall metrics
            overall_metrics = ReplicationMetrics(
                model_id=model_id,
                node_id=source_node,
                sync_time=time.time(),
                data_transferred=0,  # Would be calculated from actual transfer
                success_rate=success_rate,
                latency=0,  # Would be measured
                conflicts_resolved=0
            )
            
            if model_id not in self.metrics:
                self.metrics[model_id] = []
            self.metrics[model_id].append(overall_metrics)
            
        except Exception as e:
            logger.error(f"❌ Error recording metrics: {e}")
    
    async def get_metrics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get replication metrics"""
        try:
            if model_id:
                if model_id not in self.metrics:
                    return {}
                
                model_metrics = self.metrics[model_id]
                if not model_metrics:
                    return {}
                
                # Calculate aggregated metrics
                recent_metrics = model_metrics[-10:]  # Last 10 records
                avg_success_rate = sum(m.success_rate for m in recent_metrics) / len(recent_metrics)
                avg_latency = sum(m.latency for m in recent_metrics) / len(recent_metrics)
                total_data_transferred = sum(m.data_transferred for m in model_metrics)
                
                return {
                    'model_id': model_id,
                    'total_replications': len(model_metrics),
                    'average_success_rate': avg_success_rate,
                    'average_latency': avg_latency,
                    'total_data_transferred': total_data_transferred,
                    'last_replication': model_metrics[-1].timestamp.isoformat()
                }
            else:
                # Return metrics for all models
                all_metrics = {}
                for mid in self.metrics.keys():
                    all_metrics[mid] = await self.get_metrics(mid)
                
                return all_metrics
                
        except Exception as e:
            logger.error(f"❌ Error getting metrics: {e}")
            return {}


# Global instance
replication_manager = ModelReplicationManager()


async def main():
    """Test the Model Replication Manager"""
    manager = ModelReplicationManager()
    
    print("🔄 Testing Model Replication Manager...")
    
    # Register nodes
    node1 = ReplicationNode(
        node_id="us-east-1",
        region="us-east",
        endpoint="https://us-east-1.models.ainflue.com",
        priority=1
    )
    node2 = ReplicationNode(
        node_id="eu-west-1",
        region="eu-west",
        endpoint="https://eu-west-1.models.ainflue.com",
        priority=2
    )
    
    await manager.register_node(node1)
    await manager.register_node(node2)
    
    # Configure replication
    config = ReplicationConfig(
        model_id="creator-classifier-v1",
        strategy=ReplicationStrategy.MASTER_SLAVE,
        source_nodes=["us-east-1"],
        target_nodes=["eu-west-1"],
        sync_interval=60
    )
    
    await manager.configure_replication(config)
    
    # Replicate model
    results = await manager.replicate_model(
        "creator-classifier-v1", "us-east-1", ["eu-west-1"]
    )
    print(f"Replication results: {results}")
    
    # Get status
    status = await manager.get_replication_status("creator-classifier-v1")
    print(f"Replication status: {status}")
    
    # Get metrics
    metrics = await manager.get_metrics("creator-classifier-v1")
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())