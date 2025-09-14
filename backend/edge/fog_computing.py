"""Fog Computing Orchestration
===========================

Distributed processing coordination layer for fog computing environments,
providing workload distribution, resource management, and task orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, asdict, field
import json
import uuid
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor
import pickle

logger = logging.getLogger(__name__)


class ProcessingTier(str, Enum):
    """Fog computing processing tiers."""
    DEVICE_TIER = "device_tier"        # IoT devices and sensors
    FOG_TIER = "fog_tier"             # Edge servers and gateways
    CLOUD_TIER = "cloud_tier"         # Central cloud infrastructure
    HYBRID_TIER = "hybrid_tier"       # Mixed processing


class WorkloadType(str, Enum):
    """Types of workloads in fog computing."""
    REAL_TIME_ANALYTICS = "real_time_analytics"
    BATCH_PROCESSING = "batch_processing"
    STREAM_PROCESSING = "stream_processing"
    AI_INFERENCE = "ai_inference"
    DATA_AGGREGATION = "data_aggregation"
    EVENT_PROCESSING = "event_processing"
    MULTIMEDIA_PROCESSING = "multimedia_processing"
    CONTROL_LOGIC = "control_logic"
    MONITORING = "monitoring"
    BACKUP_REPLICATION = "backup_replication"


class ResourceType(str, Enum):
    """Resource types for fog computing."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK_BANDWIDTH = "network_bandwidth"
    GPU = "gpu"
    SPECIALIZED_HARDWARE = "specialized_hardware"


class TaskPriority(str, Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    NEAREST_NODE = "nearest_node"
    RESOURCE_AWARE = "resource_aware"
    LATENCY_OPTIMIZED = "latency_optimized"
    COST_OPTIMIZED = "cost_optimized"


@dataclass
class FogNode:
    """Fog computing node representation."""
    node_id: str
    node_name: str
    tier: ProcessingTier
    location: Optional[Dict[str, float]] = None  # latitude, longitude
    capabilities: List[str] = field(default_factory=list)
    resources: Dict[ResourceType, float] = field(default_factory=dict)
    available_resources: Dict[ResourceType, float] = field(default_factory=dict)
    current_load: float = 0.0  # 0.0 to 1.0
    network_latency_ms: float = 0.0
    network_bandwidth_mbps: float = 100.0
    is_online: bool = True
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingTask:
    """Distributed processing task."""
    task_id: str
    task_name: str
    workload_type: WorkloadType
    priority: TaskPriority
    resource_requirements: Dict[ResourceType, float]
    estimated_duration_seconds: float
    max_execution_time_seconds: float
    data_size_mb: float
    input_data: Any = None
    processing_function: Optional[Callable] = None
    dependencies: List[str] = field(default_factory=list)  # task_ids
    target_tier: Optional[ProcessingTier] = None
    preferred_nodes: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None


@dataclass
class TaskExecution:
    """Task execution tracking."""
    execution_id: str
    task_id: str
    assigned_node_id: str
    status: TaskStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_duration_seconds: Optional[float] = None
    result: Any = None
    error_message: Optional[str] = None
    resource_usage: Dict[ResourceType, float] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class FogComputingConfig:
    """Configuration for fog computing orchestrator."""
    orchestrator_name: str = "ainflue-fog"
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.RESOURCE_AWARE
    enable_auto_scaling: bool = True
    enable_task_migration: bool = True
    enable_fault_tolerance: bool = True
    max_concurrent_tasks_per_node: int = 10
    task_timeout_seconds: int = 300
    heartbeat_interval_seconds: int = 30
    resource_monitoring_interval_seconds: int = 10
    load_balancing_interval_seconds: int = 60
    cleanup_completed_tasks_hours: int = 24
    enable_data_caching: bool = True
    enable_result_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_performance_optimization: bool = True


class FogComputingOrchestrator:
    """Fog computing orchestrator.
    
    Coordinates distributed processing across fog computing tiers,
    managing workload distribution, resource allocation, and task execution.
    """
    
    def __init__(self, config -> None: Optional[FogComputingConfig] = None) -> None:
        self.config = config or FogComputingConfig()
        
        # State management
        self.fog_nodes: Dict[str, FogNode] = {}
        self.pending_tasks: Dict[str, ProcessingTask] = {}
        self.running_tasks: Dict[str, TaskExecution] = {}
        self.completed_tasks: Dict[str, TaskExecution] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # Caching
        self.data_cache: Dict[str, Any] = {}
        self.result_cache: Dict[str, Any] = {}
        
        # Thread pool for CPU-bound tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Background tasks
        self.running = False
        self.background_tasks: List[asyncio.Task] = []
        
        # Performance metrics
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time_seconds": 0.0,
            "average_queue_time_seconds": 0.0,
            "total_nodes": 0,
            "active_nodes": 0,
            "total_resource_utilization": 0.0,
            "tasks_per_second": 0.0
        }
        
        logger.info(f"Fog computing orchestrator initialized: {self.config.orchestrator_name}")
    
    async def start(self) -> None:
        """Start the fog computing orchestrator."""
        if self.running:
            logger.warning("Fog computing orchestrator already running")
            return
        
        self.running = True
        
        # Start background tasks
        self.background_tasks.extend([
            asyncio.create_task(self._task_scheduler()),
            asyncio.create_task(self._resource_monitor()),
            asyncio.create_task(self._load_balancer()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._cleanup_manager())
        ])
        
        if self.config.enable_auto_scaling:
            self.background_tasks.append(
                asyncio.create_task(self._auto_scaler())
            )
        
        if self.config.enable_task_migration:
            self.background_tasks.append(
                asyncio.create_task(self._migration_manager())
            )
        
        logger.info("Fog computing orchestrator started")
    
    async def stop(self) -> None:
        """Stop the fog computing orchestrator."""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.background_tasks.clear()
        
        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)
        
        logger.info("Fog computing orchestrator stopped")
    
    async def register_fog_node(
        self,
        node_name: str,
        tier: ProcessingTier,
        capabilities: List[str],
        resources: Dict[ResourceType, float],
        location: Optional[Dict[str, float]] = None,
        network_latency_ms: float = 10.0,
        network_bandwidth_mbps: float = 100.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a fog computing node."""
        node_id = str(uuid.uuid4())
        
        fog_node = FogNode(
            node_id=node_id,
            node_name=node_name,
            tier=tier,
            location=location,
            capabilities=capabilities,
            resources=resources.copy(),
            available_resources=resources.copy(),
            network_latency_ms=network_latency_ms,
            network_bandwidth_mbps=network_bandwidth_mbps,
            metadata=metadata or {}
        )
        
        self.fog_nodes[node_id] = fog_node
        
        logger.info(f"Registered fog node: {node_name} ({tier}) with ID: {node_id}")
        return node_id
    
    async def unregister_fog_node(self, node_id: str) -> bool:
        """Unregister a fog computing node."""
        if node_id not in self.fog_nodes:
            logger.warning(f"Fog node {node_id} not found")
            return False
        
        node = self.fog_nodes.pop(node_id)
        
        # Cancel running tasks on this node
        tasks_to_cancel = [
            execution for execution in self.running_tasks.values()
            if execution.assigned_node_id == node_id
        ]
        
        for execution in tasks_to_cancel:
            execution.status = TaskStatus.CANCELLED
            execution.completed_at = datetime.now()
            self.completed_tasks[execution.execution_id] = execution
            self.running_tasks.pop(execution.execution_id)
        
        logger.info(f"Unregistered fog node: {node.node_name}")
        return True
    
    async def submit_task(
        self,
        task_name: str,
        workload_type: WorkloadType,
        processing_function: Callable,
        input_data: Any = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        resource_requirements: Optional[Dict[ResourceType, float]] = None,
        estimated_duration_seconds: float = 60.0,
        max_execution_time_seconds: Optional[float] = None,
        target_tier: Optional[ProcessingTier] = None,
        preferred_nodes: Optional[List[str]] = None,
        deadline: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit a task for distributed processing."""
        task_id = str(uuid.uuid4())
        
        # Calculate data size
        data_size_mb = 0.0
        if input_data is not None:
            try:
                data_size_mb = len(pickle.dumps(input_data)) / (1024 * 1024)
            except:
                data_size_mb = 1.0  # Default estimate
        
        task = ProcessingTask(
            task_id=task_id,
            task_name=task_name,
            workload_type=workload_type,
            priority=priority,
            resource_requirements=resource_requirements or {ResourceType.CPU: 1.0, ResourceType.MEMORY: 512.0},
            estimated_duration_seconds=estimated_duration_seconds,
            max_execution_time_seconds=max_execution_time_seconds or (estimated_duration_seconds * 2),
            data_size_mb=data_size_mb,
            input_data=input_data,
            processing_function=processing_function,
            target_tier=target_tier,
            preferred_nodes=preferred_nodes or [],
            deadline=deadline,
            metadata=metadata or {}
        )
        
        self.pending_tasks[task_id] = task
        
        # Add to priority queue (lower number = higher priority)
        priority_value = self._get_priority_value(priority)
        await self.task_queue.put((priority_value, time.time(), task_id))
        
        self.metrics["total_tasks"] += 1
        
        logger.info(f"Submitted task: {task_name} (ID: {task_id})")
        return task_id
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        # Check pending tasks
        if task_id in self.pending_tasks:
            task = self.pending_tasks.pop(task_id)
            logger.info(f"Cancelled pending task: {task.task_name}")
            return True
        
        # Check running tasks
        for execution_id, execution in self.running_tasks.items():
            if execution.task_id == task_id:
                execution.status = TaskStatus.CANCELLED
                execution.completed_at = datetime.now()
                self.completed_tasks[execution_id] = execution
                self.running_tasks.pop(execution_id)
                logger.info(f"Cancelled running task: {task_id}")
                return True
        
        logger.warning(f"Task {task_id} not found for cancellation")
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task."""
        # Check pending tasks
        if task_id in self.pending_tasks:
            task = self.pending_tasks[task_id]
            return {
                "task_id": task_id,
                "status": "pending",
                "task_info": asdict(task)
            }
        
        # Check running and completed tasks
        for execution in list(self.running_tasks.values()) + list(self.completed_tasks.values()):
            if execution.task_id == task_id:
                return {
                    "task_id": task_id,
                    "status": execution.status,
                    "execution_info": asdict(execution)
                }
        
        return None
    
    async def get_node_status(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a fog node."""
        if node_id not in self.fog_nodes:
            return None
        
        node = self.fog_nodes[node_id]
        
        # Count running tasks on this node
        running_tasks_count = sum(
            1 for execution in self.running_tasks.values()
            if execution.assigned_node_id == node_id
        )
        
        return {
            "node_info": asdict(node),
            "running_tasks": running_tasks_count,
            "resource_utilization": {
                resource_type.value: 1.0 - (available / total) if total > 0 else 0.0
                for resource_type, (available, total) in [
                    (rt, (node.available_resources.get(rt, 0), node.resources.get(rt, 0)))
                    for rt in ResourceType
                ]
            }
        }
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status."""
        # Update metrics
        active_nodes = sum(1 for node in self.fog_nodes.values() if node.is_online)
        
        total_utilization = 0.0
        if self.fog_nodes:
            for node in self.fog_nodes.values():
                if node.is_online:
                    node_utilization = sum(
                        1.0 - (node.available_resources.get(rt, 0) / node.resources.get(rt, 1))
                        for rt in ResourceType
                        if node.resources.get(rt, 0) > 0
                    ) / len(ResourceType)
                    total_utilization += node_utilization
            total_utilization /= active_nodes if active_nodes > 0 else 1
        
        self.metrics.update({
            "total_nodes": len(self.fog_nodes),
            "active_nodes": active_nodes,
            "total_resource_utilization": total_utilization
        })
        
        return {
            "orchestrator_info": {
                "name": self.config.orchestrator_name,
                "running": self.running,
                "strategy": self.config.load_balancing_strategy
            },
            "metrics": self.metrics,
            "task_counts": {
                "pending": len(self.pending_tasks),
                "running": len(self.running_tasks),
                "completed": len(self.completed_tasks)
            },
            "node_summary": {
                "total": len(self.fog_nodes),
                "by_tier": {
                    tier.value: sum(1 for node in self.fog_nodes.values() if node.tier == tier)
                    for tier in ProcessingTier
                }
            },
            "cache_stats": {
                "data_cache_entries": len(self.data_cache),
                "result_cache_entries": len(self.result_cache)
            }
        }
    
    def _get_priority_value(self, priority: TaskPriority) -> int:
        """Convert task priority to numeric value for queue ordering."""
        priority_map = {
            TaskPriority.CRITICAL: 1,
            TaskPriority.HIGH: 2,
            TaskPriority.NORMAL: 3,
            TaskPriority.LOW: 4,
            TaskPriority.BACKGROUND: 5
        }
        return priority_map.get(priority, 3)
    
    async def _task_scheduler(self) -> None:
        """Main task scheduling loop."""
        while self.running:
            try:
                # Get next task from queue
                try:
                    priority, submit_time, task_id = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                if task_id not in self.pending_tasks:
                    continue  # Task was cancelled
                
                task = self.pending_tasks[task_id]
                
                # Find suitable node
                suitable_node = await self._find_suitable_node(task)
                
                if suitable_node:
                    # Schedule task
                    await self._schedule_task_on_node(task, suitable_node)
                else:
                    # No suitable node found, put back in queue
                    await self.task_queue.put((priority, submit_time, task_id))
                    await asyncio.sleep(1)  # Wait before retry
                
            except Exception as e:
                logger.error(f"Task scheduler error: {e}")
                await asyncio.sleep(1)
    
    async def _find_suitable_node(self, task: ProcessingTask) -> Optional[str]:
        """Find a suitable node for task execution."""
        suitable_nodes = []
        
        for node_id, node in self.fog_nodes.items():
            if not node.is_online:
                continue
            
            # Check tier preference
            if task.target_tier and node.tier != task.target_tier:
                continue
            
            # Check preferred nodes
            if task.preferred_nodes and node_id not in task.preferred_nodes:
                continue
            
            # Check resource availability
            if not self._node_has_resources(node, task.resource_requirements):
                continue
            
            # Check current load
            running_tasks_count = sum(
                1 for execution in self.running_tasks.values()
                if execution.assigned_node_id == node_id
            )
            
            if running_tasks_count >= self.config.max_concurrent_tasks_per_node:
                continue
            
            suitable_nodes.append(node_id)
        
        if not suitable_nodes:
            return None
        
        # Apply load balancing strategy
        return self._select_node_by_strategy(suitable_nodes, task)
    
    def _node_has_resources(self, node: FogNode, requirements: Dict[ResourceType, float]) -> bool:
        """Check if node has sufficient resources."""
        for resource_type, required_amount in requirements.items():
            available = node.available_resources.get(resource_type, 0)
            if available < required_amount:
                return False
        return True
    
    def _select_node_by_strategy(self, node_ids: List[str], task: ProcessingTask) -> str:
        """Select node based on load balancing strategy."""
        if not node_ids:
            return None
        
        if len(node_ids) == 1:
            return node_ids[0]
        
        strategy = self.config.load_balancing_strategy
        
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            # Simple round-robin based on task count
            task_counts = {
                node_id: sum(1 for ex in self.running_tasks.values() if ex.assigned_node_id == node_id)
                for node_id in node_ids
            }
            return min(task_counts, key=task_counts.get)
        
        elif strategy == LoadBalancingStrategy.LEAST_LOADED:
            # Select node with lowest current load
            return min(node_ids, key=lambda nid: self.fog_nodes[nid].current_load)
        
        elif strategy == LoadBalancingStrategy.RESOURCE_AWARE:
            # Select node with best resource availability for this task
            scores = {}
            for node_id in node_ids:
                node = self.fog_nodes[node_id]
                score = 0.0
                
                for resource_type, required in task.resource_requirements.items():
                    available = node.available_resources.get(resource_type, 0)
                    total = node.resources.get(resource_type, 1)
                    if total > 0:
                        score += (available / total) * (required / sum(task.resource_requirements.values()))
                
                scores[node_id] = score
            
            return max(scores, key=scores.get)
        
        elif strategy == LoadBalancingStrategy.LATENCY_OPTIMIZED:
            # Select node with lowest network latency
            return min(node_ids, key=lambda nid: self.fog_nodes[nid].network_latency_ms)
        
        else:
            # Default to first available
            return node_ids[0]
    
    async def _schedule_task_on_node(self, task -> None: ProcessingTask, node_id -> None: str) -> None:
        """Schedule a task on a specific node."""
        node = self.fog_nodes[node_id]
        execution_id = str(uuid.uuid4())
        
        # Reserve resources
        for resource_type, amount in task.resource_requirements.items():
            current_available = node.available_resources.get(resource_type, 0)
            node.available_resources[resource_type] = max(0, current_available - amount)
        
        # Create execution record
        execution = TaskExecution(
            execution_id=execution_id,
            task_id=task.task_id,
            assigned_node_id=node_id,
            status=TaskStatus.SCHEDULED,
            started_at=datetime.now()
        )
        
        # Move task from pending to running
        self.pending_tasks.pop(task.task_id)
        self.running_tasks[execution_id] = execution
        
        # Execute task asynchronously
        asyncio.create_task(self._execute_task(task, execution))
        
        logger.info(f"Scheduled task {task.task_name} on node {node.node_name}")
    
    async def _execute_task(self, task -> None: ProcessingTask, execution -> None: TaskExecution) -> None:
        """Execute a task and handle the result."""
        try:
            execution.status = TaskStatus.RUNNING
            start_time = time.time()
            
            # Execute the processing function
            if task.processing_function:
                if asyncio.iscoroutinefunction(task.processing_function):
                    result = await asyncio.wait_for(
                        task.processing_function(task.input_data),
                        timeout=task.max_execution_time_seconds
                    )
                else:
                    # Run CPU-bound function in thread pool
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.thread_pool,
                        task.processing_function,
                        task.input_data
                    )
            else:
                result = f"Task {task.task_name} completed"
            
            # Task completed successfully
            execution.status = TaskStatus.COMPLETED
            execution.result = result
            execution.completed_at = datetime.now()
            execution.actual_duration_seconds = time.time() - start_time
            
            # Cache result if enabled
            if self.config.enable_result_caching:
                cache_key = hashlib.md5(f"{task.task_id}_{task.input_data}".encode()).hexdigest()
                self.result_cache[cache_key] = {
                    "result": result,
                    "timestamp": datetime.now(),
                    "ttl": datetime.now() + timedelta(seconds=self.config.cache_ttl_seconds)
                }
            
            self.metrics["completed_tasks"] += 1
            
            logger.info(f"Task {task.task_name} completed successfully")
            
        except asyncio.TimeoutError:
            execution.status = TaskStatus.TIMEOUT
            execution.error_message = "Task execution timeout"
            execution.completed_at = datetime.now()
            self.metrics["failed_tasks"] += 1
            logger.error(f"Task {task.task_name} timed out")
            
        except Exception as e:
            execution.status = TaskStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            self.metrics["failed_tasks"] += 1
            logger.error(f"Task {task.task_name} failed: {e}")
        
        finally:
            # Release resources
            node = self.fog_nodes[execution.assigned_node_id]
            for resource_type, amount in task.resource_requirements.items():
                current_available = node.available_resources.get(resource_type, 0)
                total_available = node.resources.get(resource_type, 0)
                node.available_resources[resource_type] = min(total_available, current_available + amount)
            
            # Move from running to completed
            self.running_tasks.pop(execution.execution_id)
            self.completed_tasks[execution.execution_id] = execution
    
    async def _resource_monitor(self) -> None:
        """Monitor resource usage across fog nodes."""
        while self.running:
            try:
                for node_id, node in self.fog_nodes.items():
                    # Update current load based on running tasks
                    running_tasks_count = sum(
                        1 for execution in self.running_tasks.values()
                        if execution.assigned_node_id == node_id
                    )
                    
                    max_tasks = self.config.max_concurrent_tasks_per_node
                    node.current_load = running_tasks_count / max_tasks if max_tasks > 0 else 0.0
                
                await asyncio.sleep(self.config.resource_monitoring_interval_seconds)
                
            except Exception as e:
                logger.error(f"Resource monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _load_balancer(self) -> None:
        """Perform load balancing operations."""
        while self.running:
            try:
                # This is a placeholder for load balancing logic
                # In a real implementation, you would analyze load distribution
                # and potentially trigger task migrations
                
                await asyncio.sleep(self.config.load_balancing_interval_seconds)
                
            except Exception as e:
                logger.error(f"Load balancer error: {e}")
                await asyncio.sleep(60)
    
    async def _health_monitor(self) -> None:
        """Monitor health of fog nodes."""
        while self.running:
            try:
                current_time = datetime.now()
                
                for node_id, node in self.fog_nodes.items():
                    # Check heartbeat
                    time_since_heartbeat = (current_time - node.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat > self.config.heartbeat_interval_seconds * 3:
                        if node.is_online:
                            node.is_online = False
                            logger.warning(f"Node {node.node_name} marked as offline")
                    else:
                        if not node.is_online:
                            node.is_online = True
                            logger.info(f"Node {node.node_name} is back online")
                
                await asyncio.sleep(self.config.heartbeat_interval_seconds)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_manager(self) -> None:
        """Clean up old completed tasks and cache entries."""
        while self.running:
            try:
                current_time = datetime.now()
                cleanup_threshold = current_time - timedelta(hours=self.config.cleanup_completed_tasks_hours)
                
                # Clean up old completed tasks
                old_executions = [
                    execution_id for execution_id, execution in self.completed_tasks.items()
                    if execution.completed_at and execution.completed_at < cleanup_threshold
                ]
                
                for execution_id in old_executions:
                    self.completed_tasks.pop(execution_id)
                
                if old_executions:
                    logger.info(f"Cleaned up {len(old_executions)} old task executions")
                
                # Clean up expired cache entries
                if self.config.enable_result_caching:
                    expired_cache_keys = [
                        key for key, value in self.result_cache.items()
                        if value["ttl"] < current_time
                    ]
                    
                    for key in expired_cache_keys:
                        self.result_cache.pop(key)
                
                await asyncio.sleep(3600)  # Run cleanup every hour
                
            except Exception as e:
                logger.error(f"Cleanup manager error: {e}")
                await asyncio.sleep(3600)
    
    async def _auto_scaler(self) -> None:
        """Auto-scaling logic for fog nodes."""
        while self.running:
            try:
                # This is a placeholder for auto-scaling logic
                # In a real implementation, you would:
                # - Monitor resource usage trends
                # - Trigger node addition/removal
                # - Coordinate with cloud providers for dynamic scaling
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Auto-scaler error: {e}")
                await asyncio.sleep(300)
    
    async def _migration_manager(self) -> None:
        """Manage task migration between nodes."""
        while self.running:
            try:
                # This is a placeholder for migration logic
                # In a real implementation, you would:
                # - Identify overloaded nodes
                # - Find migration targets
                # - Migrate tasks while preserving state
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Migration manager error: {e}")
                await asyncio.sleep(120)


# Convenience function
async def create_fog_computing_orchestrator(config: Optional[FogComputingConfig] = None) -> FogComputingOrchestrator:
    """Create and start a fog computing orchestrator."""
    orchestrator = FogComputingOrchestrator(config)
    await orchestrator.start()
    return orchestrator


# Example processing functions
def cpu_intensive_task(data: Any) -> str:
    """Example CPU-intensive processing function."""
    import math
    result = 0
    for i in range(1000000):
        result += math.sqrt(i)
    return f"CPU task completed with result: {result}"


async def async_processing_task(data: Any) -> Dict[str, Any]:
    """Example async processing function."""
    await asyncio.sleep(2)  # Simulate I/O operation
    return {
        "processed_data": f"Processed: {data}",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }


# Example usage
async def main() -> None:
    """Example usage of the fog computing orchestrator."""
    try:
        # Create configuration
        config = FogComputingConfig(
            orchestrator_name="ainflue-fog-demo",
            load_balancing_strategy=LoadBalancingStrategy.RESOURCE_AWARE,
            enable_auto_scaling=False
        )
        
        # Create and start orchestrator
        orchestrator = await create_fog_computing_orchestrator(config)
        
        try:
            # Register fog nodes
            edge_node_id = await orchestrator.register_fog_node(
                node_name="edge-server-1",
                tier=ProcessingTier.FOG_TIER,
                capabilities=["ai_inference", "data_processing"],
                resources={
                    ResourceType.CPU: 8.0,
                    ResourceType.MEMORY: 16384.0,
                    ResourceType.STORAGE: 500000.0
                },
                network_latency_ms=5.0
            )
            
            cloud_node_id = await orchestrator.register_fog_node(
                node_name="cloud-instance-1",
                tier=ProcessingTier.CLOUD_TIER,
                capabilities=["batch_processing", "machine_learning"],
                resources={
                    ResourceType.CPU: 32.0,
                    ResourceType.MEMORY: 65536.0,
                    ResourceType.STORAGE: 2000000.0
                },
                network_latency_ms=50.0
            )
            
            # Submit tasks
            task1_id = await orchestrator.submit_task(
                task_name="cpu-intensive-analysis",
                workload_type=WorkloadType.BATCH_PROCESSING,
                processing_function=cpu_intensive_task,
                input_data={"dataset": "sensor_data_batch_1"},
                priority=TaskPriority.HIGH,
                estimated_duration_seconds=30.0
            )
            
            task2_id = await orchestrator.submit_task(
                task_name="async-data-processing",
                workload_type=WorkloadType.STREAM_PROCESSING,
                processing_function=async_processing_task,
                input_data={"stream": "live_sensor_feed"},
                priority=TaskPriority.NORMAL,
                estimated_duration_seconds=10.0
            )
            
            # Wait for tasks to complete
            await asyncio.sleep(5)
            
            # Check task status
            status1 = await orchestrator.get_task_status(task1_id)
            status2 = await orchestrator.get_task_status(task2_id)
            
            print("Task 1 Status:")
            print(json.dumps(status1, indent=2, default=str))
            print("\nTask 2 Status:")
            print(json.dumps(status2, indent=2, default=str))
            
            # Get orchestrator status
            orchestrator_status = orchestrator.get_orchestrator_status()
            print("\nFog Computing Orchestrator Status:")
            print(json.dumps(orchestrator_status, indent=2, default=str))
            
        finally:
            await orchestrator.stop()
            
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())