"""🎼 Model Serving Orchestrator - Multi-Model Enterprise Serving
===========================================================
Module: ml/inference/model_serving_orchestrator.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MULTI-MODEL SERVING ORCHESTRATION
Enterprise-grade multi-model serving with resource allocation optimization
- Multi-model inference orchestration
- Dynamic resource allocation and scaling
- Model routing and load balancing
- Performance optimization and monitoring
"""

import asyncio
import logging
import json
import time
import uuid
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pickle
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import psutil
import torch

logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    """Model deployment status"""
    LOADING = "loading"
    READY = "ready"
    SERVING = "serving"
    SCALING = "scaling"
    ERROR = "error"
    UNLOADING = "unloading"

class RoutingStrategy(Enum):
    """Model routing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESOURCE_AWARE = "resource_aware"
    PERFORMANCE_BASED = "performance_based"
    CREATOR_AFFINITY = "creator_affinity"

class ScalingPolicy(Enum):
    """Auto-scaling policies"""
    CPU_BASED = "cpu_based"
    LATENCY_BASED = "latency_based"
    QUEUE_BASED = "queue_based"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"

@dataclass
class ModelDeployment:
    """Model deployment configuration"""
    model_id: str
    deployment_id: str
    model_path: str
    model_format: str
    instances: int = 1
    min_instances: int = 1
    max_instances: int = 10
    cpu_request: float = 0.5
    memory_request: float = 1.0  # GB
    gpu_request: int = 0
    priority: int = 1
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ModelInstance:
    """Individual model instance"""
    instance_id: str
    model_id: str
    deployment_id: str
    status: ModelStatus
    endpoint_url: str
    resource_allocation: Dict[str, float]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    active_connections: int = 0
    total_requests: int = 0
    error_count: int = 0
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class InferenceRequest:
    """Inference request with routing information"""
    request_id: str
    model_id: str
    input_data: Any
    priority: int = 1
    creator_id: Optional[str] = None
    timeout_seconds: float = 30.0
    routing_hints: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RoutingDecision:
    """Model routing decision result"""
    selected_instance: ModelInstance
    routing_strategy: RoutingStrategy
    routing_score: float
    alternative_instances: List[ModelInstance]
    routing_metadata: Dict[str, Any] = field(default_factory=dict)

class ResourceMonitor:
    """Monitor system and model instance resources"""
    
    def __init__(self):
        self.monitoring_interval = 10  # seconds
        self.resource_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.monitoring_active = False
        
    async def start_monitoring(self) -> None:
        """Start continuous resource monitoring"""
        self.monitoring_active = True
        asyncio.create_task(self._monitoring_loop())
        logger.info("Resource monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop resource monitoring"""
        self.monitoring_active = False
        logger.info("Resource monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # System resources
                system_metrics = await self._collect_system_metrics()
                self.resource_history['system'].append({
                    'timestamp': datetime.utcnow(),
                    'metrics': system_metrics
                })
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self) -> Dict[str, float]:
        """Collect system-level metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
            'gpu_memory_used': self._get_gpu_memory_usage()
        }
    
    def _get_gpu_memory_usage(self) -> float:
        """Get GPU memory usage percentage"""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated(0)
            reserved = torch.cuda.memory_reserved(0)
            return (allocated / reserved * 100) if reserved > 0 else 0
        return 0
    
    async def get_instance_metrics(self, instance_id: str) -> Dict[str, float]:
        """Get metrics for specific model instance"""
        # In a real implementation, this would query the actual instance
        # For now, return simulated metrics
        return {
            'cpu_usage': np.random.uniform(10, 80),
            'memory_usage': np.random.uniform(20, 90),
            'latency_ms': np.random.uniform(50, 200),
            'throughput_rps': np.random.uniform(10, 100),
            'error_rate': np.random.uniform(0, 0.05)
        }
    
    async def predict_resource_needs(
        self,
        model_id: str,
        projected_load: float
    ) -> Dict[str, float]:
        """Predict resource needs for given load"""
        # Simplified predictive model
        base_cpu = 0.5
        base_memory = 1.0
        
        # Scale based on projected load
        predicted_cpu = base_cpu * (1 + projected_load / 100)
        predicted_memory = base_memory * (1 + projected_load / 200)
        
        return {
            'cpu_cores': min(predicted_cpu, 4.0),
            'memory_gb': min(predicted_memory, 8.0),
            'confidence': 0.8
        }

class ModelRouter:
    """Intelligent model routing system"""
    
    def __init__(self, routing_strategy: RoutingStrategy = RoutingStrategy.PERFORMANCE_BASED):
        self.routing_strategy = routing_strategy
        self.routing_history: List[RoutingDecision] = []
        self.creator_affinity_cache: Dict[str, str] = {}  # creator_id -> preferred_instance
        
    async def route_request(
        self,
        request: InferenceRequest,
        available_instances: List[ModelInstance]
    ) -> RoutingDecision:
        """Route request to optimal model instance"""
        try:
            if not available_instances:
                raise ValueError("No available instances for routing")
            
            # Filter instances by model ID
            model_instances = [
                instance for instance in available_instances 
                if instance.model_id == request.model_id and instance.status == ModelStatus.READY
            ]
            
            if not model_instances:
                raise ValueError(f"No ready instances found for model {request.model_id}")
            
            # Apply routing strategy
            selected_instance = await self._apply_routing_strategy(
                request, model_instances
            )
            
            # Calculate routing score
            routing_score = await self._calculate_routing_score(
                selected_instance, request, model_instances
            )
            
            # Create routing decision
            decision = RoutingDecision(
                selected_instance=selected_instance,
                routing_strategy=self.routing_strategy,
                routing_score=routing_score,
                alternative_instances=[i for i in model_instances if i != selected_instance],
                routing_metadata={
                    'total_instances': len(model_instances),
                    'request_priority': request.priority,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.routing_history.append(decision)
            return decision
            
        except Exception as e:
            logger.error(f"Request routing failed: {e}")
            raise
    
    async def _apply_routing_strategy(
        self,
        request: InferenceRequest,
        instances: List[ModelInstance]
    ) -> ModelInstance:
        """Apply specific routing strategy"""
        if self.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            return await self._round_robin_routing(instances)
        
        elif self.routing_strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return await self._least_connections_routing(instances)
        
        elif self.routing_strategy == RoutingStrategy.RESOURCE_AWARE:
            return await self._resource_aware_routing(instances)
        
        elif self.routing_strategy == RoutingStrategy.PERFORMANCE_BASED:
            return await self._performance_based_routing(instances)
        
        elif self.routing_strategy == RoutingStrategy.CREATOR_AFFINITY:
            return await self._creator_affinity_routing(request, instances)
        
        else:
            return instances[0]  # Default fallback
    
    async def _round_robin_routing(self, instances: List[ModelInstance]) -> ModelInstance:
        """Simple round-robin routing"""
        # Use request count as round-robin counter
        total_requests = sum(len(self.routing_history) for _ in instances)
        selected_index = total_requests % len(instances)
        return instances[selected_index]
    
    async def _least_connections_routing(self, instances: List[ModelInstance]) -> ModelInstance:
        """Route to instance with least active connections"""
        return min(instances, key=lambda i: i.active_connections)
    
    async def _resource_aware_routing(self, instances: List[ModelInstance]) -> ModelInstance:
        """Route based on resource utilization"""
        best_instance = instances[0]
        best_score = float('inf')
        
        for instance in instances:
            # Calculate resource utilization score (lower is better)
            cpu_weight = instance.performance_metrics.get('cpu_usage', 50) / 100
            memory_weight = instance.performance_metrics.get('memory_usage', 50) / 100
            utilization_score = (cpu_weight + memory_weight) / 2
            
            if utilization_score < best_score:
                best_score = utilization_score
                best_instance = instance
        
        return best_instance
    
    async def _performance_based_routing(self, instances: List[ModelInstance]) -> ModelInstance:
        """Route based on performance metrics"""
        best_instance = instances[0]
        best_score = 0
        
        for instance in instances:
            # Calculate performance score (higher is better)
            latency_score = max(0, 1 - instance.performance_metrics.get('latency_ms', 100) / 200)
            throughput_score = min(1, instance.performance_metrics.get('throughput_rps', 50) / 100)
            error_score = max(0, 1 - instance.performance_metrics.get('error_rate', 0.01))
            
            performance_score = (latency_score + throughput_score + error_score) / 3
            
            if performance_score > best_score:
                best_score = performance_score
                best_instance = instance
        
        return best_instance
    
    async def _creator_affinity_routing(
        self,
        request: InferenceRequest,
        instances: List[ModelInstance]
    ) -> ModelInstance:
        """Route based on creator affinity"""
        if request.creator_id and request.creator_id in self.creator_affinity_cache:
            # Try to use cached affinity
            preferred_instance_id = self.creator_affinity_cache[request.creator_id]
            for instance in instances:
                if instance.instance_id == preferred_instance_id:
                    return instance
        
        # Fallback to performance-based routing and cache the result
        selected_instance = await self._performance_based_routing(instances)
        
        if request.creator_id:
            self.creator_affinity_cache[request.creator_id] = selected_instance.instance_id
        
        return selected_instance
    
    async def _calculate_routing_score(
        self,
        selected_instance: ModelInstance,
        request: InferenceRequest,
        all_instances: List[ModelInstance]
    ) -> float:
        """Calculate routing decision confidence score"""
        # Base score from instance performance
        performance_metrics = selected_instance.performance_metrics
        latency_score = max(0, 1 - performance_metrics.get('latency_ms', 100) / 200)
        throughput_score = min(1, performance_metrics.get('throughput_rps', 50) / 100)
        
        # Availability score
        availability_score = (len(all_instances) - selected_instance.error_count) / max(1, len(all_instances))
        
        # Priority alignment score
        priority_score = min(1, request.priority / 5)
        
        # Combined score
        routing_score = (
            latency_score * 0.3 +
            throughput_score * 0.3 +
            availability_score * 0.2 +
            priority_score * 0.2
        )
        
        return min(1.0, max(0.0, routing_score))

class AutoScaler:
    """Automatic model instance scaling"""
    
    def __init__(self, scaling_policy: ScalingPolicy = ScalingPolicy.HYBRID):
        self.scaling_policy = scaling_policy
        self.scaling_decisions: List[Dict[str, Any]] = []
        self.cooldown_period = 60  # seconds
        self.last_scaling_time: Dict[str, datetime] = {}
        
    async def evaluate_scaling_need(
        self,
        deployment: ModelDeployment,
        current_instances: List[ModelInstance],
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Evaluate if scaling is needed"""
        try:
            current_count = len([i for i in current_instances if i.status == ModelStatus.READY])
            
            # Check cooldown period
            if deployment.model_id in self.last_scaling_time:
                time_since_last = (datetime.utcnow() - self.last_scaling_time[deployment.model_id]).total_seconds()
                if time_since_last < self.cooldown_period:
                    return {
                        'action': 'none',
                        'reason': 'cooldown_active',
                        'current_instances': current_count
                    }
            
            # Apply scaling policy
            scaling_decision = await self._apply_scaling_policy(
                deployment, current_instances, metrics
            )
            
            # Enforce limits
            target_instances = max(deployment.min_instances, 
                                 min(deployment.max_instances, scaling_decision['target_instances']))
            
            if target_instances == current_count:
                action = 'none'
            elif target_instances > current_count:
                action = 'scale_up'
            else:
                action = 'scale_down'
            
            decision = {
                'action': action,
                'current_instances': current_count,
                'target_instances': target_instances,
                'scaling_policy': self.scaling_policy.value,
                'reason': scaling_decision['reason'],
                'confidence': scaling_decision.get('confidence', 0.8),
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if action != 'none':
                self.last_scaling_time[deployment.model_id] = datetime.utcnow()
                self.scaling_decisions.append(decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Scaling evaluation failed: {e}")
            return {
                'action': 'none',
                'reason': 'evaluation_error',
                'error': str(e)
            }
    
    async def _apply_scaling_policy(
        self,
        deployment: ModelDeployment,
        instances: List[ModelInstance],
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Apply specific scaling policy"""
        current_count = len(instances)
        
        if self.scaling_policy == ScalingPolicy.CPU_BASED:
            return await self._cpu_based_scaling(current_count, metrics)
        
        elif self.scaling_policy == ScalingPolicy.LATENCY_BASED:
            return await self._latency_based_scaling(current_count, metrics)
        
        elif self.scaling_policy == ScalingPolicy.QUEUE_BASED:
            return await self._queue_based_scaling(current_count, metrics)
        
        elif self.scaling_policy == ScalingPolicy.PREDICTIVE:
            return await self._predictive_scaling(current_count, metrics)
        
        elif self.scaling_policy == ScalingPolicy.HYBRID:
            return await self._hybrid_scaling(current_count, metrics)
        
        else:
            return {'target_instances': current_count, 'reason': 'no_policy'}
    
    async def _cpu_based_scaling(self, current_count: int, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Scale based on CPU utilization"""
        avg_cpu = metrics.get('avg_cpu_usage', 50)
        
        if avg_cpu > 80:
            target = min(current_count + 1, current_count * 2)
            return {'target_instances': target, 'reason': 'high_cpu', 'confidence': 0.9}
        elif avg_cpu < 20 and current_count > 1:
            target = max(1, current_count - 1)
            return {'target_instances': target, 'reason': 'low_cpu', 'confidence': 0.7}
        else:
            return {'target_instances': current_count, 'reason': 'cpu_stable'}
    
    async def _latency_based_scaling(self, current_count: int, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Scale based on response latency"""
        avg_latency = metrics.get('avg_latency_ms', 100)
        
        if avg_latency > 150:
            target = min(current_count + 2, current_count * 2)
            return {'target_instances': target, 'reason': 'high_latency', 'confidence': 0.85}
        elif avg_latency < 50 and current_count > 1:
            target = max(1, current_count - 1)
            return {'target_instances': target, 'reason': 'low_latency', 'confidence': 0.6}
        else:
            return {'target_instances': current_count, 'reason': 'latency_stable'}
    
    async def _queue_based_scaling(self, current_count: int, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Scale based on request queue length"""
        queue_length = metrics.get('queue_length', 0)
        
        if queue_length > 10:
            target = min(current_count + 1, current_count * 2)
            return {'target_instances': target, 'reason': 'queue_backlog', 'confidence': 0.95}
        elif queue_length == 0 and current_count > 1:
            target = max(1, current_count - 1)
            return {'target_instances': target, 'reason': 'queue_empty', 'confidence': 0.5}
        else:
            return {'target_instances': current_count, 'reason': 'queue_stable'}
    
    async def _predictive_scaling(self, current_count: int, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Scale based on predicted load"""
        # Simplified predictive model
        current_hour = datetime.utcnow().hour
        
        # Predict higher load during business hours
        if 9 <= current_hour <= 17:
            predicted_load_multiplier = 1.5
        elif 6 <= current_hour <= 21:
            predicted_load_multiplier = 1.2
        else:
            predicted_load_multiplier = 0.8
        
        target = max(1, int(current_count * predicted_load_multiplier))
        
        return {
            'target_instances': target,
            'reason': f'predicted_load_{predicted_load_multiplier}x',
            'confidence': 0.7
        }
    
    async def _hybrid_scaling(self, current_count: int, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Hybrid scaling combining multiple signals"""
        # Get recommendations from different policies
        cpu_decision = await self._cpu_based_scaling(current_count, metrics)
        latency_decision = await self._latency_based_scaling(current_count, metrics)
        queue_decision = await self._queue_based_scaling(current_count, metrics)
        
        # Weight the decisions
        cpu_target = cpu_decision['target_instances']
        latency_target = latency_decision['target_instances']
        queue_target = queue_decision['target_instances']
        
        # Use max for scale-up, min for scale-down
        if any(target > current_count for target in [cpu_target, latency_target, queue_target]):
            target = max(cpu_target, latency_target, queue_target)
            reason = 'hybrid_scale_up'
        elif all(target < current_count for target in [cpu_target, latency_target, queue_target]):
            target = min(cpu_target, latency_target, queue_target)
            reason = 'hybrid_scale_down'
        else:
            target = current_count
            reason = 'hybrid_stable'
        
        return {
            'target_instances': target,
            'reason': reason,
            'confidence': 0.8,
            'component_decisions': {
                'cpu': cpu_decision,
                'latency': latency_decision,
                'queue': queue_decision
            }
        }

class ModelServingOrchestrator:
    """Main model serving orchestration system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Core components
        self.resource_monitor = ResourceMonitor()
        self.model_router = ModelRouter(
            RoutingStrategy[self.config.get('routing_strategy', 'PERFORMANCE_BASED')]
        )
        self.auto_scaler = AutoScaler(
            ScalingPolicy[self.config.get('scaling_policy', 'HYBRID')]
        )
        
        # State management
        self.deployments: Dict[str, ModelDeployment] = {}
        self.instances: Dict[str, ModelInstance] = {}
        self.orchestration_metrics: Dict[str, Any] = {}
        
        # Configuration
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.scaling_check_interval = self.config.get('scaling_check_interval', 60)
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.running = False
        
        logger.info("Model Serving Orchestrator initialized")
    
    async def start(self) -> None:
        """Start the orchestration system"""
        try:
            self.running = True
            
            # Start resource monitoring
            await self.resource_monitor.start_monitoring()
            
            # Start background tasks
            self.background_tasks = [
                asyncio.create_task(self._health_check_loop()),
                asyncio.create_task(self._scaling_loop()),
                asyncio.create_task(self._metrics_collection_loop())
            ]
            
            logger.info("Model Serving Orchestrator started")
            
        except Exception as e:
            logger.error(f"Failed to start orchestrator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the orchestration system"""
        try:
            self.running = False
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Stop resource monitoring
            await self.resource_monitor.stop_monitoring()
            
            logger.info("Model Serving Orchestrator stopped")
            
        except Exception as e:
            logger.error(f"Error stopping orchestrator: {e}")
    
    async def deploy_model(
        self,
        model_id: str,
        model_path: str,
        deployment_config: Dict[str, Any] = None
    ) -> str:
        """Deploy a new model for serving"""
        try:
            deployment_id = f"deploy_{model_id}_{int(time.time())}"
            config = deployment_config or {}
            
            # Create deployment
            deployment = ModelDeployment(
                model_id=model_id,
                deployment_id=deployment_id,
                model_path=model_path,
                model_format=config.get('model_format', 'pytorch'),
                instances=config.get('initial_instances', 1),
                min_instances=config.get('min_instances', 1),
                max_instances=config.get('max_instances', 10),
                cpu_request=config.get('cpu_request', 0.5),
                memory_request=config.get('memory_request', 1.0),
                gpu_request=config.get('gpu_request', 0),
                priority=config.get('priority', 1),
                tags=config.get('tags', {})
            )
            
            self.deployments[deployment_id] = deployment
            
            # Create initial instances
            for i in range(deployment.instances):
                instance_id = await self._create_model_instance(deployment, i)
                logger.info(f"Created instance {instance_id} for deployment {deployment_id}")
            
            logger.info(f"Model {model_id} deployed with ID {deployment_id}")
            return deployment_id
            
        except Exception as e:
            logger.error(f"Model deployment failed: {e}")
            raise
    
    async def _create_model_instance(
        self,
        deployment: ModelDeployment,
        instance_index: int
    ) -> str:
        """Create a new model instance"""
        instance_id = f"{deployment.deployment_id}_instance_{instance_index}"
        
        instance = ModelInstance(
            instance_id=instance_id,
            model_id=deployment.model_id,
            deployment_id=deployment.deployment_id,
            status=ModelStatus.LOADING,
            endpoint_url=f"http://localhost:8000/models/{instance_id}",
            resource_allocation={
                'cpu': deployment.cpu_request,
                'memory': deployment.memory_request,
                'gpu': deployment.gpu_request
            }
        )
        
        self.instances[instance_id] = instance
        
        # Simulate instance startup
        asyncio.create_task(self._simulate_instance_startup(instance_id))
        
        return instance_id
    
    async def _simulate_instance_startup(self, instance_id: str) -> None:
        """Simulate model instance startup process"""
        try:
            instance = self.instances[instance_id]
            
            # Simulate loading time
            await asyncio.sleep(np.random.uniform(2, 5))
            
            # Update status to ready
            instance.status = ModelStatus.READY
            instance.last_health_check = datetime.utcnow()
            
            # Initialize performance metrics
            instance.performance_metrics = await self.resource_monitor.get_instance_metrics(instance_id)
            
            logger.info(f"Instance {instance_id} is now ready")
            
        except Exception as e:
            logger.error(f"Instance startup failed for {instance_id}: {e}")
            if instance_id in self.instances:
                self.instances[instance_id].status = ModelStatus.ERROR
    
    async def predict(
        self,
        model_id: str,
        input_data: Any,
        creator_id: Optional[str] = None,
        priority: int = 1,
        timeout_seconds: float = 30.0
    ) -> Dict[str, Any]:
        """Make prediction using orchestrated model serving"""
        try:
            request_id = str(uuid.uuid4())
            
            # Create inference request
            request = InferenceRequest(
                request_id=request_id,
                model_id=model_id,
                input_data=input_data,
                priority=priority,
                creator_id=creator_id,
                timeout_seconds=timeout_seconds
            )
            
            # Get available instances
            available_instances = [
                instance for instance in self.instances.values()
                if instance.model_id == model_id and instance.status == ModelStatus.READY
            ]
            
            if not available_instances:
                raise ValueError(f"No available instances for model {model_id}")
            
            # Route request
            routing_decision = await self.model_router.route_request(request, available_instances)
            selected_instance = routing_decision.selected_instance
            
            # Update instance metrics
            selected_instance.active_connections += 1
            selected_instance.total_requests += 1
            
            # Simulate inference
            start_time = time.time()
            prediction_result = await self._simulate_inference(selected_instance, input_data)
            inference_time = (time.time() - start_time) * 1000  # ms
            
            # Update instance metrics
            selected_instance.active_connections -= 1
            selected_instance.performance_metrics['latency_ms'] = inference_time
            
            response = {
                'request_id': request_id,
                'model_id': model_id,
                'predictions': prediction_result,
                'inference_time_ms': inference_time,
                'instance_id': selected_instance.instance_id,
                'routing_score': routing_decision.routing_score,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            # Update error metrics
            if 'selected_instance' in locals():
                selected_instance.error_count += 1
                selected_instance.active_connections = max(0, selected_instance.active_connections - 1)
            raise
    
    async def _simulate_inference(self, instance: ModelInstance, input_data: Any) -> Dict[str, Any]:
        """Simulate model inference"""
        # Simulate inference time based on instance performance
        base_latency = instance.performance_metrics.get('latency_ms', 100)
        inference_time = base_latency + np.random.normal(0, 10)
        
        await asyncio.sleep(max(0.01, inference_time / 1000))  # Convert to seconds
        
        # Return mock prediction
        if isinstance(input_data, (list, np.ndarray)):
            predictions = np.random.random(len(input_data)).tolist()
        else:
            predictions = [np.random.random()]
        
        return {
            'predictions': predictions,
            'confidence_scores': [0.8 + np.random.random() * 0.2 for _ in predictions],
            'model_version': '1.0'
        }
    
    async def _health_check_loop(self) -> None:
        """Continuous health checking of instances"""
        while self.running:
            try:
                for instance in self.instances.values():
                    # Simulate health check
                    health_status = await self._check_instance_health(instance)
                    
                    if not health_status and instance.status == ModelStatus.READY:
                        instance.status = ModelStatus.ERROR
                        logger.warning(f"Instance {instance.instance_id} failed health check")
                    elif health_status and instance.status == ModelStatus.ERROR:
                        instance.status = ModelStatus.READY
                        logger.info(f"Instance {instance.instance_id} recovered")
                    
                    instance.last_health_check = datetime.utcnow()
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)
    
    async def _check_instance_health(self, instance: ModelInstance) -> bool:
        """Check health of a specific instance"""
        try:
            # Simulate health check (in real implementation, would make HTTP request)
            return np.random.random() > 0.05  # 95% success rate
        except Exception as e:
            logger.error(f"Health check failed for {instance.instance_id}: {e}")
            return False
    
    async def _scaling_loop(self) -> None:
        """Continuous auto-scaling evaluation"""
        while self.running:
            try:
                for deployment in self.deployments.values():
                    # Get current instances for this deployment
                    deployment_instances = [
                        instance for instance in self.instances.values()
                        if instance.deployment_id == deployment.deployment_id
                    ]
                    
                    # Collect metrics
                    metrics = await self._collect_deployment_metrics(deployment_instances)
                    
                    # Evaluate scaling need
                    scaling_decision = await self.auto_scaler.evaluate_scaling_need(
                        deployment, deployment_instances, metrics
                    )
                    
                    # Execute scaling action
                    if scaling_decision['action'] == 'scale_up':
                        await self._scale_up_deployment(deployment, scaling_decision)
                    elif scaling_decision['action'] == 'scale_down':
                        await self._scale_down_deployment(deployment, scaling_decision)
                
                await asyncio.sleep(self.scaling_check_interval)
                
            except Exception as e:
                logger.error(f"Scaling loop error: {e}")
                await asyncio.sleep(10)
    
    async def _collect_deployment_metrics(self, instances: List[ModelInstance]) -> Dict[str, float]:
        """Collect aggregated metrics for deployment"""
        if not instances:
            return {}
        
        ready_instances = [i for i in instances if i.status == ModelStatus.READY]
        
        if not ready_instances:
            return {'ready_instances': 0}
        
        # Aggregate metrics
        avg_cpu = np.mean([i.performance_metrics.get('cpu_usage', 50) for i in ready_instances])
        avg_memory = np.mean([i.performance_metrics.get('memory_usage', 50) for i in ready_instances])
        avg_latency = np.mean([i.performance_metrics.get('latency_ms', 100) for i in ready_instances])
        total_connections = sum(i.active_connections for i in ready_instances)
        total_requests = sum(i.total_requests for i in ready_instances)
        total_errors = sum(i.error_count for i in ready_instances)
        
        return {
            'ready_instances': len(ready_instances),
            'avg_cpu_usage': avg_cpu,
            'avg_memory_usage': avg_memory,
            'avg_latency_ms': avg_latency,
            'total_active_connections': total_connections,
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate': total_errors / max(1, total_requests),
            'queue_length': max(0, total_connections - len(ready_instances) * 5)  # Simulated
        }
    
    async def _scale_up_deployment(
        self,
        deployment: ModelDeployment,
        scaling_decision: Dict[str, Any]
    ) -> None:
        """Scale up deployment instances"""
        try:
            current_count = scaling_decision['current_instances']
            target_count = scaling_decision['target_instances']
            instances_to_add = target_count - current_count
            
            for i in range(instances_to_add):
                instance_index = current_count + i
                instance_id = await self._create_model_instance(deployment, instance_index)
                logger.info(f"Scaled up: created instance {instance_id}")
            
            logger.info(f"Scaled up deployment {deployment.deployment_id} from {current_count} to {target_count} instances")
            
        except Exception as e:
            logger.error(f"Scale up failed for deployment {deployment.deployment_id}: {e}")
    
    async def _scale_down_deployment(
        self,
        deployment: ModelDeployment,
        scaling_decision: Dict[str, Any]
    ) -> None:
        """Scale down deployment instances"""
        try:
            current_count = scaling_decision['current_instances']
            target_count = scaling_decision['target_instances']
            instances_to_remove = current_count - target_count
            
            # Get instances for this deployment
            deployment_instances = [
                instance for instance in self.instances.values()
                if instance.deployment_id == deployment.deployment_id and instance.status == ModelStatus.READY
            ]
            
            # Sort by least active connections for removal
            deployment_instances.sort(key=lambda i: i.active_connections)
            
            for i in range(min(instances_to_remove, len(deployment_instances))):
                instance_to_remove = deployment_instances[i]
                await self._remove_model_instance(instance_to_remove.instance_id)
                logger.info(f"Scaled down: removed instance {instance_to_remove.instance_id}")
            
            logger.info(f"Scaled down deployment {deployment.deployment_id} from {current_count} to {target_count} instances")
            
        except Exception as e:
            logger.error(f"Scale down failed for deployment {deployment.deployment_id}: {e}")
    
    async def _remove_model_instance(self, instance_id: str) -> None:
        """Remove model instance"""
        try:
            if instance_id in self.instances:
                instance = self.instances[instance_id]
                instance.status = ModelStatus.UNLOADING
                
                # Wait for active connections to complete (simplified)
                while instance.active_connections > 0:
                    await asyncio.sleep(1)
                    instance.active_connections = max(0, instance.active_connections - 1)
                
                # Remove instance
                del self.instances[instance_id]
                logger.info(f"Instance {instance_id} removed")
                
        except Exception as e:
            logger.error(f"Failed to remove instance {instance_id}: {e}")
    
    async def _metrics_collection_loop(self) -> None:
        """Collect orchestration metrics"""
        while self.running:
            try:
                # Collect overall metrics
                total_instances = len(self.instances)
                ready_instances = len([i for i in self.instances.values() if i.status == ModelStatus.READY])
                total_deployments = len(self.deployments)
                
                # Performance metrics
                if ready_instances > 0:
                    avg_latency = np.mean([
                        i.performance_metrics.get('latency_ms', 100) 
                        for i in self.instances.values() 
                        if i.status == ModelStatus.READY
                    ])
                    total_requests = sum(i.total_requests for i in self.instances.values())
                    total_errors = sum(i.error_count for i in self.instances.values())
                else:
                    avg_latency = 0
                    total_requests = 0
                    total_errors = 0
                
                self.orchestration_metrics = {
                    'total_deployments': total_deployments,
                    'total_instances': total_instances,
                    'ready_instances': ready_instances,
                    'avg_latency_ms': avg_latency,
                    'total_requests': total_requests,
                    'total_errors': total_errors,
                    'error_rate': total_errors / max(1, total_requests),
                    'instance_utilization': ready_instances / max(1, total_instances),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                await asyncio.sleep(30)  # Collect metrics every 30 seconds
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration status"""
        try:
            # Deployment status
            deployment_status = {}
            for deployment_id, deployment in self.deployments.items():
                deployment_instances = [
                    i for i in self.instances.values() 
                    if i.deployment_id == deployment_id
                ]
                
                deployment_status[deployment_id] = {
                    'model_id': deployment.model_id,
                    'total_instances': len(deployment_instances),
                    'ready_instances': len([i for i in deployment_instances if i.status == ModelStatus.READY]),
                    'min_instances': deployment.min_instances,
                    'max_instances': deployment.max_instances,
                    'created_at': deployment.created_at.isoformat()
                }
            
            # Instance status
            instance_status = {}
            for instance_id, instance in self.instances.items():
                instance_status[instance_id] = {
                    'model_id': instance.model_id,
                    'status': instance.status.value,
                    'active_connections': instance.active_connections,
                    'total_requests': instance.total_requests,
                    'error_count': instance.error_count,
                    'performance_metrics': instance.performance_metrics
                }
            
            status = {
                'orchestrator': {
                    'running': self.running,
                    'uptime_seconds': (datetime.utcnow() - datetime.utcnow()).total_seconds(),  # Placeholder
                    'background_tasks': len(self.background_tasks)
                },
                'deployments': deployment_status,
                'instances': instance_status,
                'metrics': self.orchestration_metrics,
                'routing': {
                    'strategy': self.model_router.routing_strategy.value,
                    'total_routing_decisions': len(self.model_router.routing_history)
                },
                'scaling': {
                    'policy': self.auto_scaler.scaling_policy.value,
                    'total_scaling_decisions': len(self.auto_scaler.scaling_decisions)
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get orchestration status: {e}")
            return {'error': str(e)}

# Example usage and testing
async def main():
    """Test model serving orchestrator"""
    try:
        # Initialize orchestrator
        config = {
            'routing_strategy': 'PERFORMANCE_BASED',
            'scaling_policy': 'HYBRID',
            'health_check_interval': 10,
            'scaling_check_interval': 20
        }
        
        orchestrator = ModelServingOrchestrator(config)
        
        # Start orchestrator
        await orchestrator.start()
        
        # Deploy a test model
        deployment_id = await orchestrator.deploy_model(
            model_id="test_classifier",
            model_path="/tmp/test_model.pkl",
            deployment_config={
                'initial_instances': 2,
                'min_instances': 1,
                'max_instances': 5,
                'model_format': 'pytorch'
            }
        )
        
        print(f"Model deployed with ID: {deployment_id}")
        
        # Wait for instances to start
        await asyncio.sleep(6)
        
        # Make predictions
        for i in range(5):
            prediction = await orchestrator.predict(
                model_id="test_classifier",
                input_data=[1, 2, 3, 4, 5],
                creator_id=f"creator_{i % 2}",
                priority=1
            )
            print(f"Prediction {i+1}: {prediction['inference_time_ms']:.1f}ms on {prediction['instance_id']}")
        
        # Get status
        status = await orchestrator.get_orchestration_status()
        print(f"Orchestrator status: {status['metrics']['ready_instances']} ready instances")
        print(f"Total requests: {status['metrics']['total_requests']}")
        
        # Stop orchestrator
        await orchestrator.stop()
        
        return True
        
    except Exception as e:
        logger.error(f"Model serving orchestrator test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())