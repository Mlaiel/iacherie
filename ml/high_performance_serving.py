"""High-Performance Model Serving - Auto-scaling inference engine

Enterprise-grade model serving infrastructure with auto-scaling, load balancing,
and performance optimization for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import threading
from collections import deque, defaultdict
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ServingStatus(Enum):
    """Model serving status"""
    INITIALIZING = "initializing"
    READY = "ready"
    SERVING = "serving"
    SCALING = "scaling"
    ERROR = "error"
    STOPPED = "stopped"


class ScalingDirection(Enum):
    """Auto-scaling direction"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    PERFORMANCE_BASED = "performance_based"


@dataclass
class ServingMetrics:
    """Model serving performance metrics"""
    requests_per_second: float = 0.0
    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_connections: int = 0
    queue_size: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ModelInstance:
    """Model serving instance"""
    instance_id: str
    model_id: str
    model_version: str
    status: ServingStatus = ServingStatus.INITIALIZING
    host: str = "localhost"
    port: int = 8000
    weight: float = 1.0
    max_connections: int = 100
    current_connections: int = 0
    health_score: float = 1.0
    last_health_check: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingConfig:
    """Auto-scaling configuration"""
    min_instances: int = 1
    max_instances: int = 10
    target_cpu_utilization: float = 70.0
    target_latency_ms: float = 100.0
    scale_up_threshold_requests: float = 100.0
    scale_down_threshold_requests: float = 20.0
    cooldown_period_seconds: int = 300
    scale_up_step: int = 1
    scale_down_step: int = 1


@dataclass
class ServingRequest:
    """Model serving request"""
    request_id: str
    model_id: str
    input_data: Any
    priority: int = 0  # Higher values = higher priority
    timeout_ms: int = 5000
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServingResponse:
    """Model serving response"""
    request_id: str
    output_data: Any
    latency_ms: float
    instance_id: str
    success: bool = True
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class HighPerformanceModelServing:
    """Enterprise high-performance model serving with auto-scaling"""
    
    def __init__(self, scaling_config: ScalingConfig = None):
        self.scaling_config = scaling_config or ScalingConfig()
        self.instances: Dict[str, ModelInstance] = {}
        self.models: Dict[str, Dict[str, Any]] = {}
        self.request_queue = asyncio.Queue()
        self.priority_queues: Dict[int, asyncio.Queue] = defaultdict(lambda: asyncio.Queue())
        self.load_balancer_strategy = LoadBalancingStrategy.PERFORMANCE_BASED
        
        # Performance tracking
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.current_metrics: Dict[str, ServingMetrics] = {}
        self.latency_measurements: deque = deque(maxlen=10000)
        
        # Auto-scaling state
        self.last_scaling_action: Dict[str, datetime] = {}
        self.scaling_decisions: List[Dict[str, Any]] = []
        
        # Thread pools for inference
        self.inference_executor = ThreadPoolExecutor(max_workers=10)
        self.monitoring_executor = ThreadPoolExecutor(max_workers=2)
        
        # Control flags
        self.serving_active = False
        self.monitoring_active = False
        
        logger.info("High-performance model serving initialized")
    
    
    async def deploy_model(self, model_id: str, model_version: str, 
                           model_config: Dict[str, Any]) -> bool:
        """Deploy a model for serving"""
        try:
            # Register model
            self.models[model_id] = {
                "version": model_version,
                "config": model_config,
                "deployed_at": datetime.now(),
                "status": "deploying"
            }
            
            # Create initial instances
            initial_instances = max(1, self.scaling_config.min_instances)
            
            for i in range(initial_instances):
                instance_id = f"{model_id}_{model_version}_{i}"
                instance = ModelInstance(
                    instance_id=instance_id,
                    model_id=model_id,
                    model_version=model_version,
                    port=8000 + i
                )
                
                # Initialize instance (simplified)
                await self._initialize_instance(instance)
                self.instances[instance_id] = instance
            
            self.models[model_id]["status"] = "deployed"
            
            # Start monitoring for this model
            if not self.monitoring_active:
                await self._start_monitoring()
            
            logger.info(f"Model deployed: {model_id} v{model_version} with {initial_instances} instances")
            return True
            
        except Exception as e:
            logger.error(f"Model deployment failed: {e}")
            if model_id in self.models:
                self.models[model_id]["status"] = "failed"
            return False
    
    
    async def serve_request(self, request: ServingRequest) -> ServingResponse:
        """Serve a model inference request"""
        start_time = time.time()
        
        try:
            # Find best instance for the request
            instance = await self._select_instance(request.model_id)
            
            if not instance:
                return ServingResponse(
                    request_id=request.request_id,
                    output_data=None,
                    latency_ms=(time.time() - start_time) * 1000,
                    instance_id="",
                    success=False,
                    error_message="No available instances"
                )
            
            # Execute inference
            result = await self._execute_inference(instance, request)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            self.latency_measurements.append(latency_ms)
            
            # Update instance metrics
            await self._update_instance_metrics(instance.instance_id, latency_ms, result.success)
            
            return ServingResponse(
                request_id=request.request_id,
                output_data=result,
                latency_ms=latency_ms,
                instance_id=instance.instance_id,
                success=True
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Request serving failed: {e}")
            
            return ServingResponse(
                request_id=request.request_id,
                output_data=None,
                latency_ms=latency_ms,
                instance_id="",
                success=False,
                error_message=str(e)
            )
    
    
    async def batch_serve_requests(self, requests: List[ServingRequest]) -> List[ServingResponse]:
        """Serve multiple requests with optimized batching"""
        try:
            # Group requests by model
            model_groups = defaultdict(list)
            for request in requests:
                model_groups[request.model_id].append(request)
            
            # Process each model group
            all_responses = []
            
            for model_id, model_requests in model_groups.items():
                # Sort by priority
                model_requests.sort(key=lambda r: r.priority, reverse=True)
                
                # Batch process
                batch_responses = await self._batch_process_model_requests(model_id, model_requests)
                all_responses.extend(batch_responses)
            
            return all_responses
            
        except Exception as e:
            logger.error(f"Batch serving failed: {e}")
            return []
    
    
    async def get_serving_metrics(self, model_id: str = None) -> Dict[str, Any]:
        """Get current serving metrics"""
        try:
            if model_id:
                model_instances = [i for i in self.instances.values() if i.model_id == model_id]
                metrics_key = model_id
            else:
                model_instances = list(self.instances.values())
                metrics_key = "global"
            
            if not model_instances:
                return {"error": "No instances found"}
            
            # Calculate aggregate metrics
            total_connections = sum(i.current_connections for i in model_instances)
            avg_health_score = statistics.mean(i.health_score for i in model_instances)
            
            # Latency metrics
            if self.latency_measurements:
                recent_latencies = list(self.latency_measurements)[-1000:]  # Last 1000 requests
                avg_latency = statistics.mean(recent_latencies)
                p95_latency = statistics.quantiles(recent_latencies, n=20)[18] if len(recent_latencies) > 20 else avg_latency
                p99_latency = statistics.quantiles(recent_latencies, n=100)[98] if len(recent_latencies) > 100 else avg_latency
            else:
                avg_latency = p95_latency = p99_latency = 0.0
            
            # Calculate RPS
            recent_requests = self.metrics_history.get(metrics_key, deque())
            if len(recent_requests) >= 2:
                time_window = 60  # 1 minute
                cutoff_time = datetime.now() - timedelta(seconds=time_window)
                recent_count = sum(1 for m in recent_requests if m.timestamp >= cutoff_time)
                rps = recent_count / time_window
            else:
                rps = 0.0
            
            return {
                "instances": {
                    "total": len(model_instances),
                    "ready": len([i for i in model_instances if i.status == ServingStatus.READY]),
                    "serving": len([i for i in model_instances if i.status == ServingStatus.SERVING]),
                    "error": len([i for i in model_instances if i.status == ServingStatus.ERROR])
                },
                "performance": {
                    "requests_per_second": rps,
                    "average_latency_ms": avg_latency,
                    "p95_latency_ms": p95_latency,
                    "p99_latency_ms": p99_latency,
                    "active_connections": total_connections,
                    "average_health_score": avg_health_score
                },
                "scaling": {
                    "min_instances": self.scaling_config.min_instances,
                    "max_instances": self.scaling_config.max_instances,
                    "current_instances": len(model_instances),
                    "last_scaling_action": self.last_scaling_action.get(model_id, "Never").isoformat() if isinstance(self.last_scaling_action.get(model_id), datetime) else "Never"
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Metrics retrieval failed: {e}")
            return {"error": str(e)}
    
    
    async def scale_model(self, model_id: str, target_instances: int) -> bool:
        """Manually scale a model to target instance count"""
        try:
            current_instances = [i for i in self.instances.values() if i.model_id == model_id]
            current_count = len(current_instances)
            
            if target_instances == current_count:
                logger.info(f"Model {model_id} already at target scale: {target_instances}")
                return True
            
            # Validate target
            if target_instances < self.scaling_config.min_instances:
                target_instances = self.scaling_config.min_instances
            elif target_instances > self.scaling_config.max_instances:
                target_instances = self.scaling_config.max_instances
            
            # Scale up
            if target_instances > current_count:
                instances_to_add = target_instances - current_count
                for i in range(instances_to_add):
                    await self._add_instance(model_id)
            
            # Scale down
            elif target_instances < current_count:
                instances_to_remove = current_count - target_instances
                for i in range(instances_to_remove):
                    await self._remove_instance(model_id)
            
            self.last_scaling_action[model_id] = datetime.now()
            
            logger.info(f"Model {model_id} scaled to {target_instances} instances")
            return True
            
        except Exception as e:
            logger.error(f"Manual scaling failed: {e}")
            return False
    
    
    async def _select_instance(self, model_id: str) -> Optional[ModelInstance]:
        """Select the best instance for a request"""
        try:
            available_instances = [
                i for i in self.instances.values() 
                if i.model_id == model_id and i.status in [ServingStatus.READY, ServingStatus.SERVING]
                and i.current_connections < i.max_connections
            ]
            
            if not available_instances:
                return None
            
            # Apply load balancing strategy
            if self.load_balancer_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return min(available_instances, key=lambda i: i.current_connections)
            
            elif self.load_balancer_strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
                # Select based on health score and current load
                def score_instance(instance):
                    load_factor = instance.current_connections / instance.max_connections
                    return instance.health_score * (1 - load_factor)
                
                return max(available_instances, key=score_instance)
            
            elif self.load_balancer_strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                # Simple weighted selection (simplified implementation)
                weights = [i.weight for i in available_instances]
                total_weight = sum(weights)
                import random
                rand_val = random.uniform(0, total_weight)
                current_weight = 0
                for instance, weight in zip(available_instances, weights):
                    current_weight += weight
                    if rand_val <= current_weight:
                        return instance
                
                return available_instances[0]  # Fallback
            
            else:  # ROUND_ROBIN or default
                # Simple round-robin (simplified implementation)
                return available_instances[0]
            
        except Exception as e:
            logger.error(f"Instance selection failed: {e}")
            return None
    
    
    async def _execute_inference(self, instance: ModelInstance, request: ServingRequest) -> Any:
        """Execute inference on a specific instance"""
        try:
            # Update instance connection count
            instance.current_connections += 1
            instance.status = ServingStatus.SERVING
            
            # Simulate inference (in production, this would call the actual model)
            await asyncio.sleep(0.01)  # Simulate processing time
            
            # Mock result based on request
            result = {
                "prediction": f"result_for_{request.request_id}",
                "confidence": 0.95,
                "processed_by": instance.instance_id
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Inference execution failed: {e}")
            raise
        finally:
            # Update instance state
            instance.current_connections = max(0, instance.current_connections - 1)
            if instance.current_connections == 0:
                instance.status = ServingStatus.READY
    
    
    async def _batch_process_model_requests(self, model_id: str, 
                                            requests: List[ServingRequest]) -> List[ServingResponse]:
        """Process a batch of requests for a specific model"""
        try:
            responses = []
            
            # Process in parallel with available instances
            available_instances = [
                i for i in self.instances.values() 
                if i.model_id == model_id and i.status in [ServingStatus.READY, ServingStatus.SERVING]
            ]
            
            if not available_instances:
                # Return error responses
                for request in requests:
                    responses.append(ServingResponse(
                        request_id=request.request_id,
                        output_data=None,
                        latency_ms=0.0,
                        instance_id="",
                        success=False,
                        error_message="No available instances"
                    ))
                return responses
            
            # Submit requests to thread pool
            future_to_request = {}
            
            for request in requests:
                instance = await self._select_instance(model_id)
                if instance:
                    future = self.inference_executor.submit(
                        self._sync_execute_inference, instance, request
                    )
                    future_to_request[future] = (request, instance)
            
            # Collect results
            for future in as_completed(future_to_request.keys()):
                request, instance = future_to_request[future]
                
                try:
                    result = future.result()
                    responses.append(ServingResponse(
                        request_id=request.request_id,
                        output_data=result,
                        latency_ms=0.0,  # Would be calculated properly
                        instance_id=instance.instance_id,
                        success=True
                    ))
                except Exception as e:
                    responses.append(ServingResponse(
                        request_id=request.request_id,
                        output_data=None,
                        latency_ms=0.0,
                        instance_id=instance.instance_id,
                        success=False,
                        error_message=str(e)
                    ))
            
            return responses
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return []
    
    
    def _sync_execute_inference(self, instance: ModelInstance, request: ServingRequest) -> Any:
        """Synchronous wrapper for inference execution"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._execute_inference(instance, request))
        finally:
            loop.close()
    
    
    async def _initialize_instance(self, instance: ModelInstance):
        """Initialize a model instance"""
        try:
            # Simulate instance initialization
            await asyncio.sleep(0.1)
            
            instance.status = ServingStatus.READY
            instance.health_score = 1.0
            instance.last_health_check = datetime.now()
            
            logger.debug(f"Instance initialized: {instance.instance_id}")
            
        except Exception as e:
            logger.error(f"Instance initialization failed: {e}")
            instance.status = ServingStatus.ERROR
    
    
    async def _update_instance_metrics(self, instance_id: str, latency_ms: float, success: bool):
        """Update metrics for an instance"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                return
            
            # Update health score based on performance
            if success:
                # Good request - improve health score
                instance.health_score = min(1.0, instance.health_score + 0.01)
            else:
                # Failed request - decrease health score
                instance.health_score = max(0.0, instance.health_score - 0.05)
            
            instance.last_health_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Metrics update failed: {e}")
    
    
    async def _start_monitoring(self):
        """Start monitoring and auto-scaling"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._auto_scale_models())
        
        logger.info("Performance monitoring and auto-scaling started")
    
    
    async def _monitor_performance(self):
        """Monitor performance metrics"""
        while self.monitoring_active:
            try:
                for model_id in self.models.keys():
                    await self._collect_model_metrics(model_id)
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    
    async def _auto_scale_models(self):
        """Auto-scale models based on metrics"""
        while self.monitoring_active:
            try:
                for model_id in self.models.keys():
                    await self._evaluate_scaling_decision(model_id)
                
                await asyncio.sleep(30)  # Check scaling every 30 seconds
                
            except Exception as e:
                logger.error(f"Auto-scaling error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    
    async def _collect_model_metrics(self, model_id: str):
        """Collect metrics for a specific model"""
        try:
            model_instances = [i for i in self.instances.values() if i.model_id == model_id]
            
            if not model_instances:
                return
            
            # Calculate current metrics
            total_connections = sum(i.current_connections for i in model_instances)
            avg_health = statistics.mean(i.health_score for i in model_instances)
            
            # Recent latency
            recent_latencies = list(self.latency_measurements)[-100:]
            avg_latency = statistics.mean(recent_latencies) if recent_latencies else 0.0
            
            # Store metrics
            metrics = ServingMetrics(
                requests_per_second=len(recent_latencies) / 10.0,  # Approximate RPS
                average_latency_ms=avg_latency,
                active_connections=total_connections,
                timestamp=datetime.now()
            )
            
            self.current_metrics[model_id] = metrics
            self.metrics_history[model_id].append(metrics)
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
    
    
    async def _evaluate_scaling_decision(self, model_id: str):
        """Evaluate if scaling is needed for a model"""
        try:
            # Check cooldown period
            last_action = self.last_scaling_action.get(model_id)
            if last_action:
                cooldown_end = last_action + timedelta(seconds=self.scaling_config.cooldown_period_seconds)
                if datetime.now() < cooldown_end:
                    return  # Still in cooldown
            
            current_instances = [i for i in self.instances.values() if i.model_id == model_id]
            current_count = len(current_instances)
            
            # Get recent metrics
            metrics = self.current_metrics.get(model_id)
            if not metrics:
                return
            
            # Scaling decision logic
            should_scale_up = (
                metrics.average_latency_ms > self.scaling_config.target_latency_ms * 1.5 or
                metrics.requests_per_second > self.scaling_config.scale_up_threshold_requests or
                metrics.active_connections > current_count * 80  # 80% capacity
            )
            
            should_scale_down = (
                metrics.average_latency_ms < self.scaling_config.target_latency_ms * 0.5 and
                metrics.requests_per_second < self.scaling_config.scale_down_threshold_requests and
                metrics.active_connections < current_count * 20  # 20% capacity
            )
            
            if should_scale_up and current_count < self.scaling_config.max_instances:
                target = min(
                    current_count + self.scaling_config.scale_up_step,
                    self.scaling_config.max_instances
                )
                await self.scale_model(model_id, target)
                
                self.scaling_decisions.append({
                    "model_id": model_id,
                    "direction": "up",
                    "from_instances": current_count,
                    "to_instances": target,
                    "reason": "performance_threshold",
                    "timestamp": datetime.now()
                })
                
            elif should_scale_down and current_count > self.scaling_config.min_instances:
                target = max(
                    current_count - self.scaling_config.scale_down_step,
                    self.scaling_config.min_instances
                )
                await self.scale_model(model_id, target)
                
                self.scaling_decisions.append({
                    "model_id": model_id,
                    "direction": "down",
                    "from_instances": current_count,
                    "to_instances": target,
                    "reason": "low_utilization",
                    "timestamp": datetime.now()
                })
            
        except Exception as e:
            logger.error(f"Scaling evaluation failed: {e}")
    
    
    async def _add_instance(self, model_id: str) -> bool:
        """Add a new instance for a model"""
        try:
            model = self.models.get(model_id)
            if not model:
                return False
            
            # Find next available port
            existing_ports = [i.port for i in self.instances.values() if i.model_id == model_id]
            next_port = max(existing_ports) + 1 if existing_ports else 8000
            
            instance_id = f"{model_id}_{model['version']}_{len(existing_ports)}"
            
            instance = ModelInstance(
                instance_id=instance_id,
                model_id=model_id,
                model_version=model["version"],
                port=next_port
            )
            
            await self._initialize_instance(instance)
            self.instances[instance_id] = instance
            
            logger.info(f"Instance added: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Instance addition failed: {e}")
            return False
    
    
    async def _remove_instance(self, model_id: str) -> bool:
        """Remove an instance for a model"""
        try:
            # Find an instance to remove (prefer least healthy)
            model_instances = [i for i in self.instances.values() if i.model_id == model_id]
            
            if not model_instances:
                return False
            
            # Select instance with lowest health score and connections
            instance_to_remove = min(
                model_instances, 
                key=lambda i: (i.health_score, i.current_connections)
            )
            
            # Wait for current requests to complete (simplified)
            max_wait = 30  # seconds
            wait_time = 0
            while instance_to_remove.current_connections > 0 and wait_time < max_wait:
                await asyncio.sleep(1)
                wait_time += 1
            
            # Remove instance
            instance_to_remove.status = ServingStatus.STOPPED
            del self.instances[instance_to_remove.instance_id]
            
            logger.info(f"Instance removed: {instance_to_remove.instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Instance removal failed: {e}")
            return False