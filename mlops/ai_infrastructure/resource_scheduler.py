#!/usr/bin/env python3
"""
📊 MLOps Resource Scheduler - Intelligent ML Workload Management

Scheduler de ressources intelligent pour workloads ML avec optimisation automatique.
Allocation optimale des ressources CPU/GPU/Memory avec prédiction de charge.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: DevOps Expert + Backend Senior + ML Engineer
"""

import asyncio
import time
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import heapq
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types de ressources"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"


class WorkloadPriority(Enum):
    """Priorités des workloads"""
    CRITICAL = 1      # Production inference
    HIGH = 2          # Important training jobs
    MEDIUM = 3        # Development workloads
    LOW = 4           # Experimental jobs
    BACKGROUND = 5    # Data processing


class SchedulingStrategy(Enum):
    """Stratégies de scheduling"""
    ROUND_ROBIN = "round_robin"
    LEAST_USED = "least_used"
    PRIORITY_BASED = "priority_based"
    ML_OPTIMIZED = "ml_optimized"
    COST_OPTIMIZED = "cost_optimized"


@dataclass
class ResourceRequest:
    """Demande de ressources"""
    cpu_cores: float = 1.0
    memory_gb: float = 2.0
    gpu_count: int = 0
    gpu_memory_gb: float = 0.0
    storage_gb: float = 10.0
    network_bandwidth_mbps: float = 100.0
    duration_hours: Optional[float] = None
    priority: WorkloadPriority = WorkloadPriority.MEDIUM


@dataclass
class Node:
    """Nœud de calcul"""
    name: str
    cpu_cores: float
    memory_gb: float
    gpu_count: int
    gpu_memory_gb: float
    storage_gb: float
    network_bandwidth_mbps: float
    labels: Dict[str, str] = field(default_factory=dict)
    taints: List[str] = field(default_factory=list)
    cost_per_hour: float = 0.5
    is_spot: bool = False
    
    # Current usage
    used_cpu: float = 0.0
    used_memory: float = 0.0
    used_gpu: int = 0
    used_gpu_memory: float = 0.0
    used_storage: float = 0.0
    used_network: float = 0.0
    
    # Metadata
    zone: str = "default"
    instance_type: str = "standard"
    created_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    is_healthy: bool = True


@dataclass
class ScheduledWorkload:
    """Workload schedulé"""
    id: str
    name: str
    image: str
    resource_request: ResourceRequest
    assigned_node: Optional[str] = None
    status: str = "pending"  # pending, scheduled, running, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    environment: Dict[str, str] = field(default_factory=dict)
    command: List[str] = field(default_factory=list)
    estimated_runtime: Optional[float] = None  # hours


@dataclass
class SchedulingDecision:
    """Décision de scheduling"""
    workload_id: str
    node_name: str
    score: float
    reasoning: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    strategy_used: SchedulingStrategy = SchedulingStrategy.ML_OPTIMIZED


class WorkloadPredictor:
    """Prédicteur de comportement des workloads ML"""
    
    def __init__(self):
        self.historical_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.runtime_patterns: Dict[str, float] = {}
        
    def record_workload_completion(self, workload: ScheduledWorkload, 
                                 actual_runtime: float, resource_usage: Dict[str, float]):
        """Enregistre la completion d'un workload pour apprentissage"""
        workload_signature = self._get_workload_signature(workload)
        
        self.historical_data[workload_signature].append({
            'runtime': actual_runtime,
            'requested_cpu': workload.resource_request.cpu_cores,
            'requested_memory': workload.resource_request.memory_gb,
            'requested_gpu': workload.resource_request.gpu_count,
            'actual_cpu_usage': resource_usage.get('cpu', 0),
            'actual_memory_usage': resource_usage.get('memory', 0),
            'actual_gpu_usage': resource_usage.get('gpu', 0),
            'timestamp': datetime.now()
        })
        
        # Update runtime prediction
        runtimes = [entry['runtime'] for entry in self.historical_data[workload_signature]]
        self.runtime_patterns[workload_signature] = sum(runtimes) / len(runtimes)
    
    def predict_runtime(self, workload: ScheduledWorkload) -> float:
        """Prédit la durée d'exécution d'un workload"""
        workload_signature = self._get_workload_signature(workload)
        
        if workload_signature in self.runtime_patterns:
            return self.runtime_patterns[workload_signature]
        
        # Heuristiques basées sur le type de workload
        if "training" in workload.name.lower():
            return 4.0  # 4 hours default for training
        elif "inference" in workload.name.lower():
            return 0.1  # 6 minutes for inference batch jobs
        elif "processing" in workload.name.lower():
            return 2.0  # 2 hours for data processing
        else:
            return 1.0  # 1 hour default
    
    def predict_resource_usage(self, workload: ScheduledWorkload) -> Dict[str, float]:
        """Prédit l'utilisation réelle des ressources"""
        workload_signature = self._get_workload_signature(workload)
        
        if workload_signature in self.historical_data:
            recent_data = self.historical_data[workload_signature][-5:]  # Last 5 runs
            
            if recent_data:
                avg_cpu_usage = sum(d['actual_cpu_usage'] for d in recent_data) / len(recent_data)
                avg_memory_usage = sum(d['actual_memory_usage'] for d in recent_data) / len(recent_data)
                avg_gpu_usage = sum(d['actual_gpu_usage'] for d in recent_data) / len(recent_data)
                
                return {
                    'cpu': avg_cpu_usage,
                    'memory': avg_memory_usage,
                    'gpu': avg_gpu_usage
                }
        
        # Default to 70% of requested resources
        return {
            'cpu': workload.resource_request.cpu_cores * 0.7,
            'memory': workload.resource_request.memory_gb * 0.7,
            'gpu': workload.resource_request.gpu_count * 0.7
        }
    
    def _get_workload_signature(self, workload: ScheduledWorkload) -> str:
        """Génère une signature pour identifier des workloads similaires"""
        # Combine image, resource requirements, and workload patterns
        signature_data = f"{workload.image}_{workload.resource_request.cpu_cores}_{workload.resource_request.memory_gb}_{workload.resource_request.gpu_count}"
        return hashlib.md5(signature_data.encode()).hexdigest()[:16]


class ResourceScheduler:
    """
    📊 Scheduler de ressources intelligent pour MLOps
    
    Fonctionnalités:
    - Allocation optimale de ressources CPU/GPU/Memory
    - Prédiction de charge avec ML
    - Multi-strategy scheduling (priority, cost, performance)
    - Auto-scaling intelligent
    - Resource fragmentation optimization
    - Spot instance management
    - Multi-zone load balancing
    - Workload affinity/anti-affinity
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.nodes: Dict[str, Node] = {}
        self.workload_queue: List[ScheduledWorkload] = []
        self.running_workloads: Dict[str, ScheduledWorkload] = {}
        self.completed_workloads: List[ScheduledWorkload] = []
        
        # Scheduler configuration
        self.default_strategy = SchedulingStrategy(
            self.config.get('default_strategy', 'ml_optimized')
        )
        self.max_queue_size = self.config.get('max_queue_size', 1000)
        self.scheduling_interval = self.config.get('scheduling_interval', 30)  # seconds
        
        # Predictor for ML-based optimization
        self.predictor = WorkloadPredictor()
        
        # Metrics
        self.metrics = {
            'scheduled_workloads': 0,
            'failed_schedules': 0,
            'average_wait_time': 0.0,
            'resource_utilization': {},
            'node_efficiency': {}
        }
        
        # Initialize with some default nodes
        self._initialize_default_nodes()
        
        logger.info("📊 Resource Scheduler initialized for intelligent ML workload management")
    
    def _initialize_default_nodes(self):
        """Initialize with default compute nodes"""
        # CPU-optimized nodes
        for i in range(3):
            node = Node(
                name=f"cpu-node-{i+1}",
                cpu_cores=16.0,
                memory_gb=64.0,
                gpu_count=0,
                gpu_memory_gb=0.0,
                storage_gb=500.0,
                network_bandwidth_mbps=1000.0,
                labels={"node-type": "cpu-optimized", "zone": f"zone-{i%2+1}"},
                cost_per_hour=0.8,
                instance_type="cpu-optimized"
            )
            self.nodes[node.name] = node
        
        # GPU-optimized nodes
        for i in range(2):
            node = Node(
                name=f"gpu-node-{i+1}",
                cpu_cores=8.0,
                memory_gb=32.0,
                gpu_count=4,
                gpu_memory_gb=64.0,
                storage_gb=200.0,
                network_bandwidth_mbps=2000.0,
                labels={"node-type": "gpu-optimized", "zone": f"zone-{i%2+1}"},
                cost_per_hour=3.5,
                instance_type="gpu-optimized"
            )
            self.nodes[node.name] = node
        
        # Spot instances (cheaper but preemptible)
        for i in range(2):
            node = Node(
                name=f"spot-node-{i+1}",
                cpu_cores=8.0,
                memory_gb=32.0,
                gpu_count=1,
                gpu_memory_gb=16.0,
                storage_gb=100.0,
                network_bandwidth_mbps=500.0,
                labels={"node-type": "spot", "zone": f"zone-{i%2+1}"},
                cost_per_hour=0.4,
                is_spot=True,
                instance_type="spot"
            )
            self.nodes[node.name] = node
    
    async def add_node(self, node: Node) -> bool:
        """Ajoute un nouveau nœud au cluster"""
        try:
            self.nodes[node.name] = node
            logger.info(f"✅ Added node {node.name} ({node.instance_type}) to cluster")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add node {node.name}: {e}")
            return False
    
    async def remove_node(self, node_name: str, drain: bool = True) -> bool:
        """Retire un nœud du cluster"""
        try:
            if node_name not in self.nodes:
                return False
            
            if drain:
                # Move running workloads to other nodes
                await self._drain_node(node_name)
            
            del self.nodes[node_name]
            logger.info(f"🗑️ Removed node {node_name} from cluster")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove node {node_name}: {e}")
            return False
    
    async def _drain_node(self, node_name: str):
        """Drain workloads from a node"""
        workloads_to_reschedule = [
            workload for workload in self.running_workloads.values()
            if workload.assigned_node == node_name
        ]
        
        for workload in workloads_to_reschedule:
            logger.info(f"🔄 Rescheduling workload {workload.name} from draining node {node_name}")
            workload.assigned_node = None
            workload.status = "pending"
            self.workload_queue.append(workload)
            del self.running_workloads[workload.id]
    
    async def submit_workload(self, workload: ScheduledWorkload) -> str:
        """Soumet un workload pour scheduling"""
        try:
            if len(self.workload_queue) >= self.max_queue_size:
                raise Exception("Queue is full")
            
            # Predict runtime if not provided
            if not workload.estimated_runtime:
                workload.estimated_runtime = self.predictor.predict_runtime(workload)
            
            # Add to queue
            self.workload_queue.append(workload)
            
            # Sort queue by priority
            self.workload_queue.sort(key=lambda w: w.resource_request.priority.value)
            
            logger.info(f"📥 Submitted workload {workload.name} ({workload.id}) to scheduling queue")
            return workload.id
            
        except Exception as e:
            logger.error(f"❌ Failed to submit workload {workload.name}: {e}")
            raise
    
    async def schedule_workloads(self, strategy: Optional[SchedulingStrategy] = None) -> int:
        """Schedule pending workloads to available nodes"""
        strategy = strategy or self.default_strategy
        scheduled_count = 0
        
        try:
            while self.workload_queue:
                workload = self.workload_queue[0]
                
                # Find best node for workload
                decision = await self._find_best_node(workload, strategy)
                
                if decision:
                    # Schedule workload
                    await self._assign_workload_to_node(workload, decision)
                    self.workload_queue.pop(0)
                    scheduled_count += 1
                    
                    self.metrics['scheduled_workloads'] += 1
                else:
                    # No suitable node found, break to avoid infinite loop
                    logger.warning(f"⚠️ No suitable node found for workload {workload.name}")
                    self.metrics['failed_schedules'] += 1
                    break
            
            if scheduled_count > 0:
                logger.info(f"✅ Scheduled {scheduled_count} workloads using {strategy.value} strategy")
            
            return scheduled_count
            
        except Exception as e:
            logger.error(f"❌ Error in scheduling: {e}")
            return scheduled_count
    
    async def _find_best_node(self, workload: ScheduledWorkload, 
                            strategy: SchedulingStrategy) -> Optional[SchedulingDecision]:
        """Find the best node for a workload"""
        suitable_nodes = []
        
        # Filter nodes that can accommodate the workload
        for node_name, node in self.nodes.items():
            if self._can_node_accommodate_workload(node, workload):
                score = await self._calculate_node_score(node, workload, strategy)
                suitable_nodes.append((node, score))
        
        if not suitable_nodes:
            return None
        
        # Sort by score (higher is better)
        suitable_nodes.sort(key=lambda x: x[1], reverse=True)
        best_node, score = suitable_nodes[0]
        
        # Generate reasoning
        reasoning = await self._generate_scheduling_reasoning(best_node, workload, strategy, score)
        
        return SchedulingDecision(
            workload_id=workload.id,
            node_name=best_node.name,
            score=score,
            reasoning=reasoning,
            strategy_used=strategy
        )
    
    def _can_node_accommodate_workload(self, node: Node, workload: ScheduledWorkload) -> bool:
        """Check if node can accommodate workload"""
        req = workload.resource_request
        
        # Check available resources
        available_cpu = node.cpu_cores - node.used_cpu
        available_memory = node.memory_gb - node.used_memory
        available_gpu = node.gpu_count - node.used_gpu
        available_gpu_memory = node.gpu_memory_gb - node.used_gpu_memory
        
        return (
            available_cpu >= req.cpu_cores and
            available_memory >= req.memory_gb and
            available_gpu >= req.gpu_count and
            available_gpu_memory >= req.gpu_memory_gb and
            node.is_healthy
        )
    
    async def _calculate_node_score(self, node: Node, workload: ScheduledWorkload,
                                  strategy: SchedulingStrategy) -> float:
        """Calculate node suitability score"""
        score = 0.0
        req = workload.resource_request
        
        if strategy == SchedulingStrategy.LEAST_USED:
            # Prefer nodes with lowest resource utilization
            cpu_util = node.used_cpu / node.cpu_cores
            memory_util = node.used_memory / node.memory_gb
            score = 100 - (cpu_util + memory_util) * 50
            
        elif strategy == SchedulingStrategy.PRIORITY_BASED:
            # Prefer GPU nodes for high priority workloads
            if req.priority.value <= 2 and node.gpu_count > 0:
                score += 50
            score += (5 - req.priority.value) * 10
            
        elif strategy == SchedulingStrategy.COST_OPTIMIZED:
            # Prefer cheaper nodes, especially spot instances
            score = 100 - (node.cost_per_hour * 10)
            if node.is_spot:
                score += 20
                
        elif strategy == SchedulingStrategy.ML_OPTIMIZED:
            # ML-specific optimizations
            score = await self._calculate_ml_optimized_score(node, workload)
            
        else:  # ROUND_ROBIN
            # Simple round-robin scoring
            score = 50
        
        # Apply node-specific bonuses/penalties
        if node.is_spot and req.priority.value <= 2:
            score -= 30  # Don't put critical workloads on spot instances
        
        # Zone affinity (prefer spreading across zones)
        zone_workloads = sum(1 for w in self.running_workloads.values() 
                           if w.assigned_node and self.nodes[w.assigned_node].zone == node.zone)
        score -= zone_workloads * 5  # Penalty for concentration
        
        return max(0, score)
    
    async def _calculate_ml_optimized_score(self, node: Node, workload: ScheduledWorkload) -> float:
        """Calculate ML-optimized scoring"""
        score = 50.0
        req = workload.resource_request
        
        # GPU workloads prefer GPU nodes
        if req.gpu_count > 0 and node.gpu_count > 0:
            score += 40
            # Prefer nodes with better GPU memory fit
            gpu_memory_fit = node.gpu_memory_gb / max(req.gpu_memory_gb, 1)
            score += min(20, gpu_memory_fit * 5)
        
        # CPU-intensive workloads prefer CPU-optimized nodes
        if req.cpu_cores >= 4 and "cpu-optimized" in node.labels.get("node-type", ""):
            score += 30
        
        # Memory-intensive workloads
        if req.memory_gb >= 16:
            memory_ratio = node.memory_gb / node.cpu_cores
            if memory_ratio >= 4:  # High memory-to-CPU ratio
                score += 25
        
        # Predicted resource usage optimization
        predicted_usage = self.predictor.predict_resource_usage(workload)
        
        # Prefer nodes where predicted usage fits well
        cpu_efficiency = predicted_usage['cpu'] / node.cpu_cores
        memory_efficiency = predicted_usage['memory'] / node.memory_gb
        
        if 0.3 <= cpu_efficiency <= 0.8 and 0.3 <= memory_efficiency <= 0.8:
            score += 20  # Good resource utilization
        
        # Training workloads prefer stable nodes (not spot)
        if "training" in workload.name.lower() and not node.is_spot:
            score += 15
        
        # Inference workloads prefer low-latency nodes
        if "inference" in workload.name.lower():
            if node.network_bandwidth_mbps >= 1000:
                score += 15
        
        return score
    
    async def _generate_scheduling_reasoning(self, node: Node, workload: ScheduledWorkload,
                                           strategy: SchedulingStrategy, score: float) -> List[str]:
        """Generate human-readable reasoning for scheduling decision"""
        reasoning = []
        
        reasoning.append(f"Selected node {node.name} with score {score:.1f}")
        reasoning.append(f"Strategy: {strategy.value}")
        
        # Resource fit
        req = workload.resource_request
        reasoning.append(f"Resource fit: {req.cpu_cores}CPU/{req.memory_gb}GB RAM/{req.gpu_count}GPU")
        
        # Node characteristics
        if node.is_spot:
            reasoning.append("Spot instance (cost-effective but preemptible)")
        
        if node.gpu_count > 0 and req.gpu_count > 0:
            reasoning.append(f"GPU acceleration: {req.gpu_count}/{node.gpu_count} GPUs")
        
        # Efficiency prediction
        predicted_usage = self.predictor.predict_resource_usage(workload)
        reasoning.append(f"Predicted efficiency: {predicted_usage['cpu']:.1f} CPU cores")
        
        return reasoning
    
    async def _assign_workload_to_node(self, workload: ScheduledWorkload, 
                                     decision: SchedulingDecision):
        """Assign workload to a node"""
        node = self.nodes[decision.node_name]
        req = workload.resource_request
        
        # Update node resource usage
        node.used_cpu += req.cpu_cores
        node.used_memory += req.memory_gb
        node.used_gpu += req.gpu_count
        node.used_gpu_memory += req.gpu_memory_gb
        
        # Update workload status
        workload.assigned_node = decision.node_name
        workload.scheduled_at = datetime.now()
        workload.status = "scheduled"
        
        # Move to running workloads
        self.running_workloads[workload.id] = workload
        
        logger.info(f"🎯 Assigned workload {workload.name} to node {decision.node_name}")
        logger.debug(f"Reasoning: {', '.join(decision.reasoning)}")
    
    async def complete_workload(self, workload_id: str, success: bool = True,
                              actual_resource_usage: Optional[Dict[str, float]] = None):
        """Mark a workload as completed"""
        if workload_id not in self.running_workloads:
            return False
        
        workload = self.running_workloads[workload_id]
        node = self.nodes[workload.assigned_node]
        
        # Update workload status
        workload.completed_at = datetime.now()
        workload.status = "completed" if success else "failed"
        
        # Calculate actual runtime
        if workload.started_at:
            actual_runtime = (workload.completed_at - workload.started_at).total_seconds() / 3600
        else:
            actual_runtime = workload.estimated_runtime or 1.0
        
        # Record for learning
        if actual_resource_usage:
            self.predictor.record_workload_completion(workload, actual_runtime, actual_resource_usage)
        
        # Free node resources
        req = workload.resource_request
        node.used_cpu -= req.cpu_cores
        node.used_memory -= req.memory_gb
        node.used_gpu -= req.gpu_count
        node.used_gpu_memory -= req.gpu_memory_gb
        
        # Move to completed workloads
        del self.running_workloads[workload_id]
        self.completed_workloads.append(workload)
        
        logger.info(f"✅ Workload {workload.name} completed in {actual_runtime:.1f}h")
        return True
    
    async def auto_schedule_loop(self):
        """Continuous scheduling loop"""
        logger.info("🔄 Starting automatic scheduling loop")
        
        while True:
            try:
                # Schedule pending workloads
                scheduled = await self.schedule_workloads()
                
                # Update metrics
                await self._update_metrics()
                
                # Check for node health
                await self._check_node_health()
                
                # Sleep before next iteration
                await asyncio.sleep(self.scheduling_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in scheduling loop: {e}")
                await asyncio.sleep(5)
    
    async def _update_metrics(self):
        """Update scheduler metrics"""
        # Calculate resource utilization
        for node_name, node in self.nodes.items():
            if node.cpu_cores > 0:
                cpu_util = (node.used_cpu / node.cpu_cores) * 100
                memory_util = (node.used_memory / node.memory_gb) * 100
                
                self.metrics['resource_utilization'][node_name] = {
                    'cpu': cpu_util,
                    'memory': memory_util,
                    'gpu': (node.used_gpu / max(node.gpu_count, 1)) * 100
                }
        
        # Calculate average wait time
        if self.workload_queue:
            wait_times = [
                (datetime.now() - w.created_at).total_seconds() / 60
                for w in self.workload_queue
            ]
            self.metrics['average_wait_time'] = sum(wait_times) / len(wait_times)
    
    async def _check_node_health(self):
        """Check node health and remove unhealthy nodes"""
        current_time = datetime.now()
        
        for node_name, node in list(self.nodes.items()):
            # Check if node is responsive (last heartbeat)
            time_since_heartbeat = (current_time - node.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > 300:  # 5 minutes
                logger.warning(f"⚠️ Node {node_name} appears unhealthy (no heartbeat)")
                node.is_healthy = False
                
                # Reschedule workloads from unhealthy nodes
                await self._drain_node(node_name)
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status overview"""
        total_nodes = len(self.nodes)
        healthy_nodes = len([n for n in self.nodes.values() if n.is_healthy])
        
        total_cpu = sum(n.cpu_cores for n in self.nodes.values())
        used_cpu = sum(n.used_cpu for n in self.nodes.values())
        
        total_memory = sum(n.memory_gb for n in self.nodes.values())
        used_memory = sum(n.used_memory for n in self.nodes.values())
        
        total_gpu = sum(n.gpu_count for n in self.nodes.values())
        used_gpu = sum(n.used_gpu for n in self.nodes.values())
        
        return {
            'cluster': {
                'total_nodes': total_nodes,
                'healthy_nodes': healthy_nodes,
                'unhealthy_nodes': total_nodes - healthy_nodes
            },
            'resources': {
                'cpu': {
                    'total': total_cpu,
                    'used': used_cpu,
                    'utilization': (used_cpu / total_cpu * 100) if total_cpu > 0 else 0
                },
                'memory': {
                    'total': total_memory,
                    'used': used_memory,
                    'utilization': (used_memory / total_memory * 100) if total_memory > 0 else 0
                },
                'gpu': {
                    'total': total_gpu,
                    'used': used_gpu,
                    'utilization': (used_gpu / total_gpu * 100) if total_gpu > 0 else 0
                }
            },
            'workloads': {
                'queued': len(self.workload_queue),
                'running': len(self.running_workloads),
                'completed': len(self.completed_workloads)
            },
            'metrics': self.metrics
        }
    
    def get_node_details(self, node_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific node"""
        if node_name not in self.nodes:
            return None
        
        node = self.nodes[node_name]
        running_workloads = [
            w for w in self.running_workloads.values()
            if w.assigned_node == node_name
        ]
        
        return {
            'name': node.name,
            'instance_type': node.instance_type,
            'zone': node.zone,
            'is_spot': node.is_spot,
            'cost_per_hour': node.cost_per_hour,
            'resources': {
                'cpu': {'total': node.cpu_cores, 'used': node.used_cpu},
                'memory': {'total': node.memory_gb, 'used': node.used_memory},
                'gpu': {'total': node.gpu_count, 'used': node.used_gpu},
                'storage': {'total': node.storage_gb, 'used': node.used_storage}
            },
            'workloads': [
                {
                    'id': w.id,
                    'name': w.name,
                    'status': w.status,
                    'started_at': w.started_at.isoformat() if w.started_at else None
                }
                for w in running_workloads
            ],
            'health': {
                'is_healthy': node.is_healthy,
                'last_heartbeat': node.last_heartbeat.isoformat()
            }
        }


# Demo function
async def demo_resource_scheduler():
    """Démonstration du scheduler de ressources"""
    print("📊 MLOps Resource Scheduler Demo")
    
    # Initialize scheduler
    scheduler = ResourceScheduler({
        'default_strategy': 'ml_optimized',
        'scheduling_interval': 5
    })
    
    # Create sample workloads
    workloads = [
        ScheduledWorkload(
            id="train-001",
            name="bert-training-job",
            image="ainflue/bert-trainer:v1.0",
            resource_request=ResourceRequest(
                cpu_cores=4.0,
                memory_gb=16.0,
                gpu_count=2,
                gpu_memory_gb=32.0,
                priority=WorkloadPriority.HIGH
            )
        ),
        ScheduledWorkload(
            id="infer-001", 
            name="sentiment-inference-service",
            image="ainflue/sentiment-api:v1.0",
            resource_request=ResourceRequest(
                cpu_cores=2.0,
                memory_gb=4.0,
                gpu_count=0,
                priority=WorkloadPriority.CRITICAL
            )
        ),
        ScheduledWorkload(
            id="batch-001",
            name="data-preprocessing-job",
            image="ainflue/data-processor:v1.0", 
            resource_request=ResourceRequest(
                cpu_cores=8.0,
                memory_gb=32.0,
                gpu_count=0,
                priority=WorkloadPriority.MEDIUM
            )
        ),
        ScheduledWorkload(
            id="exp-001",
            name="hyperparameter-tuning",
            image="ainflue/hyperparam-tuner:v1.0",
            resource_request=ResourceRequest(
                cpu_cores=1.0,
                memory_gb=2.0,
                gpu_count=1,
                gpu_memory_gb=8.0,
                priority=WorkloadPriority.LOW
            )
        )
    ]
    
    # Submit workloads
    print("📥 Submitting workloads...")
    for workload in workloads:
        await scheduler.submit_workload(workload)
        print(f"  - Submitted {workload.name} (Priority: {workload.resource_request.priority.name})")
    
    # Schedule workloads with different strategies
    strategies = [
        SchedulingStrategy.ML_OPTIMIZED,
        SchedulingStrategy.PRIORITY_BASED,
        SchedulingStrategy.COST_OPTIMIZED
    ]
    
    for strategy in strategies:
        print(f"\n🎯 Scheduling with {strategy.value} strategy...")
        scheduled = await scheduler.schedule_workloads(strategy)
        print(f"✅ Scheduled {scheduled} workloads")
    
    # Show cluster status
    print(f"\n📊 Cluster Status:")
    status = scheduler.get_cluster_status()
    
    print(f"  Nodes: {status['cluster']['healthy_nodes']}/{status['cluster']['total_nodes']} healthy")
    print(f"  CPU Utilization: {status['resources']['cpu']['utilization']:.1f}%")
    print(f"  Memory Utilization: {status['resources']['memory']['utilization']:.1f}%")
    print(f"  GPU Utilization: {status['resources']['gpu']['utilization']:.1f}%")
    print(f"  Workloads: {status['workloads']['running']} running, {status['workloads']['queued']} queued")
    
    # Show node details
    print(f"\n🖥️ Node Details:")
    for node_name in list(scheduler.nodes.keys())[:3]:  # Show first 3 nodes
        node_details = scheduler.get_node_details(node_name)
        if node_details:
            print(f"  {node_name} ({node_details['instance_type']}):")
            print(f"    CPU: {node_details['resources']['cpu']['used']:.1f}/{node_details['resources']['cpu']['total']} cores")
            print(f"    Memory: {node_details['resources']['memory']['used']:.1f}/{node_details['resources']['memory']['total']} GB")
            print(f"    Workloads: {len(node_details['workloads'])}")
    
    # Simulate workload completion
    print(f"\n✅ Simulating workload completion...")
    for workload_id in list(scheduler.running_workloads.keys())[:2]:
        await scheduler.complete_workload(
            workload_id, 
            success=True,
            actual_resource_usage={'cpu': 1.5, 'memory': 3.0, 'gpu': 0.8}
        )
    
    # Final status
    final_status = scheduler.get_cluster_status()
    print(f"\n📈 Final Status:")
    print(f"  Completed workloads: {final_status['workloads']['completed']}")
    print(f"  Total scheduled: {scheduler.metrics['scheduled_workloads']}")
    print(f"  Failed schedules: {scheduler.metrics['failed_schedules']}")


if __name__ == "__main__":
    asyncio.run(demo_resource_scheduler())