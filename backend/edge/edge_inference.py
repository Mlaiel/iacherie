"""Edge AI Inference Orchestrator
================================

High-level orchestrator for local AI inference that integrates with
the existing LocalInferenceEngine and provides edge-optimized functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import json
import time

from .local_inference import (
    LocalInferenceEngine, 
    ModelType, 
    InferenceBackend,
    InferenceResult,
    InferenceRequest,
    ModelConfig
)

logger = logging.getLogger(__name__)


class EdgeOptimizationStrategy(str, Enum):
    """Edge optimization strategies."""
    LATENCY_OPTIMIZED = "latency_optimized"
    THROUGHPUT_OPTIMIZED = "throughput_optimized"
    ENERGY_EFFICIENT = "energy_efficient"
    BALANCED = "balanced"
    MEMORY_CONSTRAINED = "memory_constrained"


class EdgeDeploymentMode(str, Enum):
    """Edge deployment modes."""
    STANDALONE = "standalone"
    DISTRIBUTED = "distributed"
    FAILOVER = "failover"
    LOAD_BALANCED = "load_balanced"


@dataclass
class EdgeInferenceConfig:
    """Configuration for edge inference orchestrator."""
    optimization_strategy: EdgeOptimizationStrategy = EdgeOptimizationStrategy.BALANCED
    deployment_mode: EdgeDeploymentMode = EdgeDeploymentMode.STANDALONE
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 30
    model_cache_size_mb: int = 2048
    enable_request_batching: bool = True
    batch_timeout_ms: int = 50
    enable_model_warming: bool = True
    health_check_interval_seconds: int = 60
    metrics_collection_enabled: bool = True
    auto_scaling_enabled: bool = False
    resource_monitoring_enabled: bool = True


@dataclass
class EdgeInferenceMetrics:
    """Edge inference performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    requests_per_second: float = 0.0
    model_load_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    gpu_usage_percent: float = 0.0
    last_updated: datetime = None


class EdgeInferenceOrchestrator:
    """Edge AI inference orchestrator.
    
    Provides high-level orchestration for edge AI inference with
    optimization strategies, load balancing, and monitoring.
    """
    
    def __init__(self, config -> None: Optional[EdgeInferenceConfig] = None) -> None:
        self.config = config or EdgeInferenceConfig()
        
        # Initialize local inference engine
        self.inference_engine = LocalInferenceEngine(
            max_concurrent_requests=self.config.max_concurrent_requests,
            optimization_enabled=True,
            metrics_enabled=self.config.metrics_collection_enabled
        )
        
        # Metrics and monitoring
        self.metrics = EdgeInferenceMetrics(last_updated=datetime.now())
        self.request_latencies: List[float] = []
        self.request_history: List[Dict[str, Any]] = []
        
        # Internal state
        self.running = False
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info(f"Edge inference orchestrator initialized with strategy: {self.config.optimization_strategy}")
    
    async def start(self) -> None:
        """Start the edge inference orchestrator."""
        if self.running:
            logger.warning("Edge inference orchestrator already running")
            return
        
        self.running = True
        
        # Start the local inference engine
        await self.inference_engine.start()
        
        # Start background monitoring tasks
        if self.config.resource_monitoring_enabled:
            self.background_tasks.append(
                asyncio.create_task(self._resource_monitor())
            )
        
        if self.config.metrics_collection_enabled:
            self.background_tasks.append(
                asyncio.create_task(self._metrics_updater())
            )
        
        # Perform model warming if enabled
        if self.config.enable_model_warming:
            asyncio.create_task(self._warm_default_models())
        
        logger.info("Edge inference orchestrator started")
    
    async def stop(self) -> None:
        """Stop the edge inference orchestrator."""
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
        
        # Stop the inference engine
        await self.inference_engine.stop()
        
        logger.info("Edge inference orchestrator stopped")
    
    async def infer(
        self,
        model_id: str,
        input_data: Any,
        priority: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InferenceResult:
        """Perform edge-optimized inference."""
        if not self.running:
            raise RuntimeError("Edge inference orchestrator not running")
        
        start_time = time.time()
        
        try:
            # Apply edge optimization strategy
            optimized_params = self._apply_optimization_strategy(model_id, input_data)
            
            # Perform inference using the local engine
            result = await self.inference_engine.infer(
                model_id=model_id,
                input_data=input_data,
                priority=priority,
                timeout_seconds=self.config.request_timeout_seconds,
                preprocessing_params=optimized_params,
                metadata=metadata
            )
            
            # Update metrics
            latency_ms = (time.time() - start_time) * 1000
            self._update_request_metrics(latency_ms, success=True)
            
            return result
            
        except Exception as e:
            # Update metrics for failed request
            latency_ms = (time.time() - start_time) * 1000
            self._update_request_metrics(latency_ms, success=False)
            
            logger.error(f"Edge inference failed: {e}")
            raise
    
    async def load_model(
        self,
        model_id: str,
        model_config: ModelConfig,
        priority: int = 5
    ) -> bool:
        """Load a model for edge inference."""
        try:
            success = await self.inference_engine.load_model(model_id, model_config, priority)
            
            if success:
                logger.info(f"Model {model_id} loaded successfully for edge inference")
            else:
                logger.warning(f"Failed to load model {model_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {e}")
            return False
    
    def get_metrics(self) -> EdgeInferenceMetrics:
        """Get current edge inference metrics."""
        return self.metrics
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the edge inference system."""
        base_status = self.inference_engine.get_engine_status()
        
        edge_status = {
            "edge_orchestrator": {
                "running": self.running,
                "optimization_strategy": self.config.optimization_strategy,
                "deployment_mode": self.config.deployment_mode,
                "metrics": asdict(self.metrics),
                "background_tasks": len(self.background_tasks),
                "recent_latencies": self.request_latencies[-10:] if self.request_latencies else [],
            }
        }
        
        return {**base_status, **edge_status}
    
    def _apply_optimization_strategy(self, model_id: str, input_data: Any) -> Dict[str, Any]:
        """Apply edge optimization strategy to inference request."""
        params = {}
        
        if self.config.optimization_strategy == EdgeOptimizationStrategy.LATENCY_OPTIMIZED:
            params.update({
                "low_latency_mode": True,
                "precision": "fp16",
                "batch_size": 1
            })
        elif self.config.optimization_strategy == EdgeOptimizationStrategy.THROUGHPUT_OPTIMIZED:
            params.update({
                "batch_size": 8,
                "precision": "fp32",
                "enable_batching": True
            })
        elif self.config.optimization_strategy == EdgeOptimizationStrategy.ENERGY_EFFICIENT:
            params.update({
                "power_save_mode": True,
                "precision": "int8",
                "cpu_only": True
            })
        elif self.config.optimization_strategy == EdgeOptimizationStrategy.MEMORY_CONSTRAINED:
            params.update({
                "model_sharding": True,
                "gradient_checkpointing": True,
                "precision": "int8"
            })
        
        return params
    
    def _update_request_metrics(self, latency_ms -> None: float, success -> None: bool) -> None:
        """Update request metrics."""
        self.metrics.total_requests += 1
        
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        # Update latency metrics
        self.request_latencies.append(latency_ms)
        if len(self.request_latencies) > 1000:  # Keep last 1000 requests
            self.request_latencies = self.request_latencies[-1000:]
        
        if self.request_latencies:
            self.metrics.average_latency_ms = sum(self.request_latencies) / len(self.request_latencies)
            sorted_latencies = sorted(self.request_latencies)
            n = len(sorted_latencies)
            self.metrics.p95_latency_ms = sorted_latencies[int(n * 0.95)] if n > 0 else 0
            self.metrics.p99_latency_ms = sorted_latencies[int(n * 0.99)] if n > 0 else 0
    
    async def _resource_monitor(self) -> None:
        """Monitor system resources."""
        import psutil
        
        while self.running:
            try:
                # Update CPU and memory metrics
                self.metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                self.metrics.memory_usage_mb = (memory.total - memory.available) / 1024 / 1024
                
                # Try to get GPU metrics if available
                try:
                    import GPUtil
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        self.metrics.gpu_usage_percent = gpus[0].load * 100
                except:
                    self.metrics.gpu_usage_percent = 0
                
                await asyncio.sleep(self.config.health_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_updater(self) -> None:
        """Update metrics periodically."""
        while self.running:
            try:
                # Calculate requests per second
                current_time = datetime.now()
                time_window = timedelta(seconds=60)
                recent_requests = [
                    req for req in self.request_history
                    if current_time - req['timestamp'] <= time_window
                ]
                self.metrics.requests_per_second = len(recent_requests) / 60.0
                
                # Update timestamp
                self.metrics.last_updated = current_time
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Metrics updater error: {e}")
                await asyncio.sleep(60)
    
    async def _warm_default_models(self) -> None:
        """Warm up default models for better performance."""
        try:
            # This is a placeholder for model warming logic
            # In a real implementation, you would load commonly used models
            logger.info("Model warming completed")
            
        except Exception as e:
            logger.error(f"Model warming error: {e}")


# Convenience functions for easy usage
async def create_edge_inference_orchestrator(
    config: Optional[EdgeInferenceConfig] = None
) -> EdgeInferenceOrchestrator:
    """Create and start an edge inference orchestrator."""
    orchestrator = EdgeInferenceOrchestrator(config)
    await orchestrator.start()
    return orchestrator


# Example usage
async def main() -> None:
    """Example usage of the edge inference orchestrator."""
    try:
        # Create configuration optimized for latency
        config = EdgeInferenceConfig(
            optimization_strategy=EdgeOptimizationStrategy.LATENCY_OPTIMIZED,
            max_concurrent_requests=5,
            request_timeout_seconds=10
        )
        
        # Create and start orchestrator
        orchestrator = await create_edge_inference_orchestrator(config)
        
        try:
            # Get status
            status = orchestrator.get_engine_status()
            print("Edge Inference Orchestrator Status:")
            print(json.dumps(status, indent=2, default=str))
            
            # Get metrics
            metrics = orchestrator.get_metrics()
            print(f"\nCurrent metrics: {asdict(metrics)}")
            
        finally:
            await orchestrator.stop()
            
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())