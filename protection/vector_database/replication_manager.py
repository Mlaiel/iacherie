"""
🔄 Vector Database Replication Manager
======================================

Advanced multi-region replication and synchronization for vector databases.
Ensures high availability and data consistency across distributed deployments.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL IMPORTANT ⚠️
=====================================
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et constitue une violation 
des droits d'auteur passible de poursuites judiciaires.

Contact: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

logger = logging.getLogger(__name__)


class ReplicationMode(Enum):
    """Replication modes supported"""
    MASTER_SLAVE = "master_slave"
    MASTER_MASTER = "master_master"
    EVENTUAL_CONSISTENCY = "eventual_consistency"
    STRONG_CONSISTENCY = "strong_consistency"


class NodeRole(Enum):
    """Node roles in replication cluster"""
    MASTER = "master"
    SLAVE = "slave"
    REPLICA = "replica"
    BACKUP = "backup"


class ReplicationStatus(Enum):
    """Replication operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class ReplicationNode:
    """Replication cluster node configuration"""
    node_id: str
    role: NodeRole
    endpoint: str
    region: str
    priority: int = 1
    health_status: str = "unknown"
    last_heartbeat: Optional[float] = None
    lag_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplicationOperation:
    """Individual replication operation"""
    operation_id: str
    operation_type: str  # insert, update, delete, bulk_insert
    source_node: str
    target_nodes: List[str]
    data: Dict[str, Any]
    timestamp: float
    status: ReplicationStatus
    retry_count: int = 0
    error_message: Optional[str] = None


@dataclass
class ConflictResolution:
    """Conflict resolution result"""
    conflict_id: str
    resolution_strategy: str
    winning_version: Dict[str, Any]
    losing_versions: List[Dict[str, Any]]
    resolved_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class VectorHashCalculator:
    """Calculate consistent hashes for vector data"""
    
    @staticmethod
    def calculate_vector_hash(vector_id: str, embedding: np.ndarray, metadata: Dict[str, Any]) -> str:
        """Calculate deterministic hash for vector data"""
        try:
            # Create consistent data representation
            data_components = [
                vector_id,
                embedding.tobytes(),
                json.dumps(metadata, sort_keys=True)
            ]
            
            combined_data = b''.join(str(comp).encode() if isinstance(comp, str) else comp for comp in data_components)
            return hashlib.sha256(combined_data).hexdigest()
            
        except Exception as e:
            logger.error(f"Hash calculation failed: {e}")
            return hashlib.sha256(str(time.time()).encode()).hexdigest()
    
    @staticmethod
    def calculate_index_hash(index_metadata: Dict[str, Any]) -> str:
        """Calculate hash for entire index state"""
        try:
            # Include key index characteristics
            index_data = {
                'total_vectors': index_metadata.get('total_vectors', 0),
                'dimension': index_metadata.get('dimension', 0),
                'index_type': index_metadata.get('index_type', ''),
                'last_modified': index_metadata.get('last_modified', 0)
            }
            
            data_str = json.dumps(index_data, sort_keys=True)
            return hashlib.sha256(data_str.encode()).hexdigest()
            
        except Exception:
            return hashlib.sha256(str(time.time()).encode()).hexdigest()


class ConflictResolver:
    """Resolve conflicts in multi-master replication"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ConflictResolver")
        
        # Conflict resolution strategies
        self.strategies = {
            'last_write_wins': self._resolve_last_write_wins,
            'vector_version_priority': self._resolve_vector_version_priority,
            'metadata_merge': self._resolve_metadata_merge,
            'custom_priority': self._resolve_custom_priority
        }
        
        self.default_strategy = config.get('default_strategy', 'last_write_wins')
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        conflicting_versions: List[Dict[str, Any]],
        strategy: Optional[str] = None
    ) -> ConflictResolution:
        """Resolve conflict between multiple versions"""
        try:
            strategy = strategy or self.default_strategy
            
            if strategy not in self.strategies:
                raise ValueError(f"Unknown conflict resolution strategy: {strategy}")
            
            # Apply resolution strategy
            winning_version, losing_versions = await self.strategies[strategy](conflicting_versions)
            
            resolution = ConflictResolution(
                conflict_id=conflict_id,
                resolution_strategy=strategy,
                winning_version=winning_version,
                losing_versions=losing_versions,
                resolved_at=time.time()
            )
            
            self.logger.info(f"Resolved conflict {conflict_id} using {strategy}")
            return resolution
            
        except Exception as e:
            self.logger.error(f"Conflict resolution failed for {conflict_id}: {e}")
            
            # Return first version as fallback
            return ConflictResolution(
                conflict_id=conflict_id,
                resolution_strategy='fallback',
                winning_version=conflicting_versions[0] if conflicting_versions else {},
                losing_versions=conflicting_versions[1:] if len(conflicting_versions) > 1 else [],
                resolved_at=time.time(),
                metadata={'error': str(e)}
            )
    
    async def _resolve_last_write_wins(self, versions: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Last write wins strategy"""
        if not versions:
            return {}, []
        
        # Sort by timestamp
        sorted_versions = sorted(
            versions,
            key=lambda v: v.get('timestamp', 0),
            reverse=True
        )
        
        return sorted_versions[0], sorted_versions[1:]
    
    async def _resolve_vector_version_priority(self, versions: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Prioritize by vector version number"""
        if not versions:
            return {}, []
        
        # Sort by version number if available
        sorted_versions = sorted(
            versions,
            key=lambda v: v.get('metadata', {}).get('version', 0),
            reverse=True
        )
        
        return sorted_versions[0], sorted_versions[1:]
    
    async def _resolve_metadata_merge(self, versions: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Merge metadata from all versions"""
        if not versions:
            return {}, []
        
        # Use latest vector data but merge metadata
        base_version = versions[0]
        merged_metadata = {}
        
        for version in versions:
            version_metadata = version.get('metadata', {})
            merged_metadata.update(version_metadata)
        
        # Create merged version
        merged_version = base_version.copy()
        merged_version['metadata'] = merged_metadata
        merged_version['timestamp'] = time.time()
        
        return merged_version, versions
    
    async def _resolve_custom_priority(self, versions: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Custom priority based on node priority"""
        if not versions:
            return {}, []
        
        # Sort by source node priority
        sorted_versions = sorted(
            versions,
            key=lambda v: v.get('source_priority', 0),
            reverse=True
        )
        
        return sorted_versions[0], sorted_versions[1:]


class ReplicationManager:
    """Main replication coordination manager"""
    
    def __init__(self, vector_store, config: Dict[str, Any]):
        self.vector_store = vector_store
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ReplicationManager")
        
        # Cluster configuration
        self.local_node_id = config['local_node_id']
        self.replication_mode = ReplicationMode(config.get('replication_mode', 'master_slave'))
        self.nodes: Dict[str, ReplicationNode] = {}
        
        # Replication state
        self.pending_operations: Dict[str, ReplicationOperation] = {}
        self.operation_log: List[ReplicationOperation] = []
        self.last_sync_timestamps: Dict[str, float] = {}
        
        # Components
        self.conflict_resolver = ConflictResolver(config.get('conflict_resolution', {}))
        self.hash_calculator = VectorHashCalculator()
        
        # Configuration
        self.sync_interval = config.get('sync_interval_seconds', 30)
        self.heartbeat_interval = config.get('heartbeat_interval_seconds', 10)
        self.max_retry_attempts = config.get('max_retry_attempts', 3)
        self.operation_timeout = config.get('operation_timeout_seconds', 60)
        
        # Background tasks
        self.sync_task = None
        self.heartbeat_task = None
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 4))
        
        # Initialize cluster
        self._initialize_cluster()
    
    def _initialize_cluster(self):
        """Initialize replication cluster configuration"""
        try:
            # Load node configurations
            nodes_config = self.config.get('cluster_nodes', [])
            
            for node_config in nodes_config:
                node = ReplicationNode(
                    node_id=node_config['node_id'],
                    role=NodeRole(node_config['role']),
                    endpoint=node_config['endpoint'],
                    region=node_config['region'],
                    priority=node_config.get('priority', 1)
                )
                self.nodes[node.node_id] = node
            
            self.logger.info(f"Initialized cluster with {len(self.nodes)} nodes")
            
        except Exception as e:
            self.logger.error(f"Cluster initialization failed: {e}")
    
    async def start_replication(self):
        """Start background replication tasks"""
        try:
            if self.sync_task is None:
                self.sync_task = asyncio.create_task(self._sync_loop())
            
            if self.heartbeat_task is None:
                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            self.logger.info("Replication manager started")
            
        except Exception as e:
            self.logger.error(f"Failed to start replication: {e}")
    
    async def stop_replication(self):
        """Stop background replication tasks"""
        try:
            if self.sync_task:
                self.sync_task.cancel()
                try:
                    await self.sync_task
                except asyncio.CancelledError:
                    pass
                self.sync_task = None
            
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
                self.heartbeat_task = None
            
            self.executor.shutdown(wait=True)
            self.logger.info("Replication manager stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop replication: {e}")
    
    async def replicate_operation(
        self,
        operation_type: str,
        vector_id: str,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None,
        target_nodes: Optional[List[str]] = None
    ) -> str:
        """Queue operation for replication"""
        try:
            operation_id = f"{self.local_node_id}_{int(time.time() * 1000000)}"
            
            # Determine target nodes
            if target_nodes is None:
                target_nodes = [
                    node_id for node_id, node in self.nodes.items()
                    if node_id != self.local_node_id and node.role in [NodeRole.SLAVE, NodeRole.REPLICA]
                ]
            
            # Create operation data
            operation_data = {
                'vector_id': vector_id,
                'operation_type': operation_type,
                'timestamp': time.time(),
                'source_node': self.local_node_id
            }
            
            if embedding is not None:
                operation_data['embedding'] = embedding.tolist()
            
            if metadata is not None:
                operation_data['metadata'] = metadata
            
            # Calculate data hash for consistency
            if embedding is not None:
                operation_data['data_hash'] = self.hash_calculator.calculate_vector_hash(
                    vector_id, embedding, metadata or {}
                )
            
            # Create replication operation
            operation = ReplicationOperation(
                operation_id=operation_id,
                operation_type=operation_type,
                source_node=self.local_node_id,
                target_nodes=target_nodes,
                data=operation_data,
                timestamp=time.time(),
                status=ReplicationStatus.PENDING
            )
            
            # Queue for replication
            self.pending_operations[operation_id] = operation
            self.operation_log.append(operation)
            
            self.logger.debug(f"Queued operation {operation_id} for replication to {len(target_nodes)} nodes")
            
            return operation_id
            
        except Exception as e:
            self.logger.error(f"Failed to queue replication operation: {e}")
            raise
    
    async def sync_with_node(self, node_id: str) -> bool:
        """Synchronize with specific node"""
        try:
            if node_id not in self.nodes:
                raise ValueError(f"Unknown node: {node_id}")
            
            node = self.nodes[node_id]
            
            # Check if node is healthy
            if not await self._check_node_health(node):
                return False
            
            # Get last sync timestamp
            last_sync = self.last_sync_timestamps.get(node_id, 0)
            
            # Get operations since last sync
            operations_to_sync = [
                op for op in self.operation_log
                if op.timestamp > last_sync and node_id in op.target_nodes
            ]
            
            if not operations_to_sync:
                self.logger.debug(f"No operations to sync with {node_id}")
                return True
            
            # Send operations to node
            success_count = 0
            for operation in operations_to_sync:
                if await self._send_operation_to_node(operation, node):
                    success_count += 1
                    operation.status = ReplicationStatus.COMPLETED
                else:
                    operation.status = ReplicationStatus.FAILED
                    operation.retry_count += 1
            
            # Update last sync timestamp
            if success_count > 0:
                self.last_sync_timestamps[node_id] = time.time()
            
            sync_rate = success_count / len(operations_to_sync) if operations_to_sync else 1.0
            
            self.logger.info(f"Synced with {node_id}: {success_count}/{len(operations_to_sync)} operations successful")
            
            return sync_rate > 0.8  # Consider successful if >80% operations synced
            
        except Exception as e:
            self.logger.error(f"Sync with {node_id} failed: {e}")
            return False
    
    async def _sync_loop(self):
        """Background synchronization loop"""
        while True:
            try:
                # Sync with all nodes
                sync_tasks = [
                    self.sync_with_node(node_id)
                    for node_id in self.nodes.keys()
                    if node_id != self.local_node_id
                ]
                
                if sync_tasks:
                    results = await asyncio.gather(*sync_tasks, return_exceptions=True)
                    
                    successful_syncs = sum(1 for result in results if isinstance(result, bool) and result)
                    self.logger.debug(f"Sync round completed: {successful_syncs}/{len(sync_tasks)} successful")
                
                # Clean up old operations
                await self._cleanup_old_operations()
                
                await asyncio.sleep(self.sync_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Sync loop error: {e}")
                await asyncio.sleep(self.sync_interval)
    
    async def _heartbeat_loop(self):
        """Background heartbeat monitoring loop"""
        while True:
            try:
                # Send heartbeat to all nodes
                for node_id, node in self.nodes.items():
                    if node_id != self.local_node_id:
                        is_healthy = await self._check_node_health(node)
                        node.health_status = "healthy" if is_healthy else "unhealthy"
                        node.last_heartbeat = time.time()
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def _check_node_health(self, node: ReplicationNode) -> bool:
        """Check if node is healthy and responsive"""
        try:
            # This would typically make an HTTP request to the node's health endpoint
            # For now, we'll simulate based on last heartbeat
            
            if node.last_heartbeat is None:
                return True  # Assume healthy if never checked
            
            time_since_heartbeat = time.time() - node.last_heartbeat
            max_heartbeat_age = self.heartbeat_interval * 3  # Allow 3 missed heartbeats
            
            return time_since_heartbeat < max_heartbeat_age
            
        except Exception as e:
            self.logger.error(f"Health check failed for {node.node_id}: {e}")
            return False
    
    async def _send_operation_to_node(self, operation: ReplicationOperation, node: ReplicationNode) -> bool:
        """Send operation to specific node"""
        try:
            # This would typically send HTTP request to node's replication endpoint
            # For simulation, we'll just log and return success
            
            self.logger.debug(f"Sending operation {operation.operation_id} to {node.node_id}")
            
            # Simulate network delay
            await asyncio.sleep(0.01)
            
            # Simulate success rate based on node health
            if node.health_status == "healthy":
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send operation to {node.node_id}: {e}")
            return False
    
    async def _cleanup_old_operations(self):
        """Clean up old completed operations"""
        try:
            current_time = time.time()
            retention_period = self.config.get('operation_retention_seconds', 3600)  # 1 hour
            
            # Remove old completed operations
            self.operation_log = [
                op for op in self.operation_log
                if current_time - op.timestamp < retention_period or op.status != ReplicationStatus.COMPLETED
            ]
            
            # Remove old pending operations (failed or completed)
            operations_to_remove = [
                op_id for op_id, op in self.pending_operations.items()
                if current_time - op.timestamp > retention_period
            ]
            
            for op_id in operations_to_remove:
                del self.pending_operations[op_id]
            
            if operations_to_remove:
                self.logger.debug(f"Cleaned up {len(operations_to_remove)} old operations")
                
        except Exception as e:
            self.logger.error(f"Operation cleanup failed: {e}")
    
    def get_replication_status(self) -> Dict[str, Any]:
        """Get current replication status and statistics"""
        try:
            # Calculate statistics
            total_operations = len(self.operation_log)
            pending_operations = len(self.pending_operations)
            
            completed_operations = sum(
                1 for op in self.operation_log
                if op.status == ReplicationStatus.COMPLETED
            )
            
            failed_operations = sum(
                1 for op in self.operation_log
                if op.status == ReplicationStatus.FAILED
            )
            
            # Node health summary
            healthy_nodes = sum(
                1 for node in self.nodes.values()
                if node.health_status == "healthy"
            )
            
            return {
                'cluster_info': {
                    'local_node_id': self.local_node_id,
                    'replication_mode': self.replication_mode.value,
                    'total_nodes': len(self.nodes),
                    'healthy_nodes': healthy_nodes
                },
                'operation_statistics': {
                    'total_operations': total_operations,
                    'pending_operations': pending_operations,
                    'completed_operations': completed_operations,
                    'failed_operations': failed_operations,
                    'success_rate': completed_operations / total_operations if total_operations > 0 else 0
                },
                'node_status': {
                    node_id: {
                        'role': node.role.value,
                        'health_status': node.health_status,
                        'last_heartbeat': node.last_heartbeat,
                        'lag_ms': node.lag_ms,
                        'last_sync': self.last_sync_timestamps.get(node_id, 0)
                    }
                    for node_id, node in self.nodes.items()
                },
                'sync_intervals': {
                    'sync_interval_seconds': self.sync_interval,
                    'heartbeat_interval_seconds': self.heartbeat_interval
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get replication status: {e}")
            return {'error': str(e)}
