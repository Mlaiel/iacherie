"""
Model Ensemble Module - Large-Scale Model Orchestration (100+ Models)

Advanced ensemble management system for orchestrating hundreds of models
with intelligent load balancing, performance monitoring, and dynamic optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
import threading
from collections import defaultdict, deque
import weakref
import gc

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model execution status"""
    IDLE = "idle"
    ACTIVE = "active"
    LOADING = "loading"
    ERROR = "error"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"


class EnsembleStrategy(Enum):
    """Large-scale ensemble strategies"""
    HIERARCHICAL_VOTING = "hierarchical_voting"
    DYNAMIC_WEIGHTING = "dynamic_weighting"
    PERFORMANCE_BASED = "performance_based"
    LOAD_BALANCED = "load_balanced"
    EXPERT_MIXTURE = "expert_mixture"
    ADAPTIVE_SELECTION = "adaptive_selection"


@dataclass
class ModelMetrics:
    """Comprehensive model performance metrics"""
    model_id: str
    accuracy: float = 0.0
    latency_ms: float = 0.0
    throughput: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    gpu_usage_percent: float = 0.0
    error_rate: float = 0.0
    predictions_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "model_id": self.model_id,
            "accuracy": self.accuracy,
            "latency_ms": self.latency_ms,
            "throughput": self.throughput,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "gpu_usage_percent": self.gpu_usage_percent,
            "error_rate": self.error_rate,
            "predictions_count": self.predictions_count,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class EnsembleConfig:
    """Configuration for large-scale ensemble"""
    max_models: int = 500
    strategy: EnsembleStrategy = EnsembleStrategy.DYNAMIC_WEIGHTING
    load_balance_threshold: float = 0.8
    performance_window_minutes: int = 60
    auto_scaling: bool = True
    fault_tolerance: bool = True
    resource_monitoring: bool = True
    adaptive_weights: bool = True
    batch_processing: bool = True
    parallel_workers: int = 10
    
    
class ModelPool:
    """Thread-safe model pool for managing hundreds of models"""
    
    def __init__(self, max_size -> None: int = 500) -> None:
        self.max_size = max_size
        self.models: Dict[str, Any] = {}
        self.model_metrics: Dict[str, ModelMetrics] = {}
        self.model_status: Dict[str, ModelStatus] = {}
        self.model_weights: Dict[str, float] = {}
        self.active_models: Set[str] = set()
        self._lock = threading.RLock()
        self._performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        logger.info(f"ModelPool initialized with max_size={max_size}")
    
    def add_model(self, model_id: str, model: Any, initial_weight: float = 1.0) -> bool:
        """Add model to the pool"""
        with self._lock:
            if len(self.models) >= self.max_size:
                logger.warning(f"ModelPool at capacity ({self.max_size}), cannot add model {model_id}")
                return False
            
            if model_id in self.models:
                logger.warning(f"Model {model_id} already exists in pool")
                return False
            
            self.models[model_id] = model
            self.model_metrics[model_id] = ModelMetrics(model_id=model_id)
            self.model_status[model_id] = ModelStatus.IDLE
            self.model_weights[model_id] = initial_weight
            
            logger.info(f"Added model {model_id} to pool (total: {len(self.models)})")
            return True
    
    def remove_model(self, model_id: str) -> bool:
        """Remove model from pool"""
        with self._lock:
            if model_id not in self.models:
                return False
            
            # Clean up all references
            del self.models[model_id]
            del self.model_metrics[model_id]
            del self.model_status[model_id]
            del self.model_weights[model_id]
            self.active_models.discard(model_id)
            
            if model_id in self._performance_history:
                del self._performance_history[model_id]
            
            logger.info(f"Removed model {model_id} from pool (remaining: {len(self.models)})")
            return True
    
    def get_available_models(self, min_performance: float = 0.0) -> List[str]:
        """Get list of available models meeting performance criteria"""
        with self._lock:
            available = []
            for model_id, status in self.model_status.items():
                if status == ModelStatus.IDLE:
                    metrics = self.model_metrics.get(model_id)
                    if metrics and metrics.accuracy >= min_performance:
                        available.append(model_id)
            return available
    
    def update_metrics(self, model_id -> None: str, metrics -> None: ModelMetrics) -> None:
        """Update model performance metrics"""
        with self._lock:
            if model_id in self.model_metrics:
                self.model_metrics[model_id] = metrics
                self._performance_history[model_id].append({
                    'timestamp': metrics.last_updated,
                    'accuracy': metrics.accuracy,
                    'latency': metrics.latency_ms,
                    'throughput': metrics.throughput
                })
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics"""
        with self._lock:
            status_counts = defaultdict(int)
            total_accuracy = 0
            total_latency = 0
            active_count = 0
            
            for model_id, status in self.model_status.items():
                status_counts[status.value] += 1
                metrics = self.model_metrics[model_id]
                total_accuracy += metrics.accuracy
                total_latency += metrics.latency_ms
                if status == ModelStatus.ACTIVE:
                    active_count += 1
            
            total_models = len(self.models)
            
            return {
                "total_models": total_models,
                "active_models": active_count,
                "status_distribution": dict(status_counts),
                "average_accuracy": total_accuracy / max(total_models, 1),
                "average_latency_ms": total_latency / max(total_models, 1),
                "utilization_rate": active_count / max(total_models, 1),
                "pool_capacity_used": total_models / self.max_size
            }


class ModelRegistry:
    """Registry for managing model metadata and capabilities"""
    
    def __init__(self) -> None:
        self.models_db: Dict[str, Dict[str, Any]] = {}
        self.capability_index: Dict[str, Set[str]] = defaultdict(set)
        self.performance_index: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.RLock()
    
    def register_model(self, model_id: str, metadata: Dict[str, Any]) -> bool:
        """Register model with metadata"""
        with self._lock:
            self.models_db[model_id] = {
                **metadata,
                'registered_at': datetime.utcnow().isoformat(),
                'model_id': model_id
            }
            
            # Index by capabilities
            capabilities = metadata.get('capabilities', [])
            for capability in capabilities:
                self.capability_index[capability].add(model_id)
            
            # Index by performance tier
            performance_tier = metadata.get('performance_tier', 'medium')
            self.performance_index[performance_tier].append(model_id)
            
            logger.info(f"Registered model {model_id} with capabilities: {capabilities}")
            return True
    
    def find_models_by_capability(self, capability: str) -> List[str]:
        """Find models with specific capability"""
        with self._lock:
            return list(self.capability_index.get(capability, set()))
    
    def find_models_by_performance(self, tier: str) -> List[str]:
        """Find models by performance tier"""
        with self._lock:
            return self.performance_index.get(tier, [])
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model metadata"""
        with self._lock:
            return self.models_db.get(model_id)


class LargeScaleEnsembleManager:
    """Main manager for large-scale ensemble orchestration"""
    
    def __init__(self, config -> None: EnsembleConfig) -> None:
        self.config = config
        self.model_pool = ModelPool(max_size=config.max_models)
        self.model_registry = ModelRegistry()
        self.ensemble_weights: Dict[str, float] = {}
        self.prediction_cache: Dict[str, Any] = {}
        self.is_running = False
        self._executor = ThreadPoolExecutor(max_workers=config.parallel_workers)
        self._monitoring_task: Optional[asyncio.Task] = None
        
        logger.info(f"LargeScaleEnsembleManager initialized with strategy: {config.strategy}")
    
    async def start(self) -> None:
        """Start the ensemble manager"""
        if self.is_running:
            return
        
        self.is_running = True
        
        if self.config.resource_monitoring:
            self._monitoring_task = asyncio.create_task(self._monitor_performance())
        
        logger.info("LargeScaleEnsembleManager started")
    
    async def stop(self) -> None:
        """Stop the ensemble manager"""
        self.is_running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self._executor.shutdown(wait=True)
        logger.info("LargeScaleEnsembleManager stopped")
    
    async def add_model(self, model_id: str, model: Any, metadata: Dict[str, Any]) -> bool:
        """Add model to ensemble"""
        # Register model metadata
        self.model_registry.register_model(model_id, metadata)
        
        # Add to model pool
        initial_weight = metadata.get('initial_weight', 1.0)
        success = self.model_pool.add_model(model_id, model, initial_weight)
        
        if success:
            self.ensemble_weights[model_id] = initial_weight
            logger.info(f"Successfully added model {model_id} to ensemble")
        
        return success
    
    async def remove_model(self, model_id: str) -> bool:
        """Remove model from ensemble"""
        success = self.model_pool.remove_model(model_id)
        if success:
            self.ensemble_weights.pop(model_id, None)
            self.prediction_cache.pop(model_id, None)
        
        return success
    
    async def predict_ensemble(self, input_data: Any, strategy: Optional[EnsembleStrategy] = None) -> Dict[str, Any]:
        """Make ensemble prediction using specified strategy"""
        strategy = strategy or self.config.strategy
        
        # Get available models
        available_models = self.model_pool.get_available_models()
        
        if not available_models:
            raise RuntimeError("No available models for prediction")
        
        # Select models based on strategy
        selected_models = await self._select_models(available_models, strategy)
        
        # Make predictions in parallel
        predictions = await self._parallel_predict(selected_models, input_data)
        
        # Combine predictions
        ensemble_result = await self._combine_predictions(predictions, strategy)
        
        # Update metrics
        await self._update_prediction_metrics(selected_models)
        
        return ensemble_result
    
    async def _select_models(self, available_models: List[str], strategy: EnsembleStrategy) -> List[str]:
        """Select models based on strategy"""
        if strategy == EnsembleStrategy.PERFORMANCE_BASED:
            # Select top-performing models
            model_scores = []
            for model_id in available_models:
                metrics = self.model_pool.model_metrics[model_id]
                score = metrics.accuracy * (1 - metrics.error_rate) / max(metrics.latency_ms, 1)
                model_scores.append((model_id, score))
            
            # Sort by score and take top 50%
            model_scores.sort(key=lambda x: x[1], reverse=True)
            selected_count = max(1, len(model_scores) // 2)
            return [model_id for model_id, _ in model_scores[:selected_count]]
        
        elif strategy == EnsembleStrategy.LOAD_BALANCED:
            # Select models with lowest current load
            model_loads = []
            for model_id in available_models:
                metrics = self.model_pool.model_metrics[model_id]
                load = (metrics.cpu_usage_percent + metrics.memory_usage_mb / 1000) / 2
                model_loads.append((model_id, load))
            
            model_loads.sort(key=lambda x: x[1])
            selected_count = min(len(available_models), self.config.parallel_workers)
            return [model_id for model_id, _ in model_loads[:selected_count]]
        
        else:
            # Default: use all available models
            return available_models
    
    async def _parallel_predict(self, model_ids: List[str], input_data: Any) -> Dict[str, Any]:
        """Make predictions in parallel"""
        prediction_tasks = []
        
        for model_id in model_ids:
            task = asyncio.get_event_loop().run_in_executor(
                self._executor,
                self._predict_single_model,
                model_id,
                input_data
            )
            prediction_tasks.append((model_id, task))
        
        predictions = {}
        for model_id, task in prediction_tasks:
            try:
                result = await task
                predictions[model_id] = result
            except Exception as e:
                logger.error(f"Prediction failed for model {model_id}: {e}")
                predictions[model_id] = None
        
        return predictions
    
    def _predict_single_model(self, model_id: str, input_data: Any) -> Any:
        """Make prediction with single model"""
        # Mark model as active
        self.model_pool.model_status[model_id] = ModelStatus.ACTIVE
        
        try:
            # Simulate model prediction
            # In production, this would call the actual model
            start_time = time.time()
            
            # Simulate processing time
            processing_time = np.random.uniform(0.01, 0.1)
            time.sleep(processing_time)
            
            # Generate prediction
            prediction = np.random.random()
            
            # Update metrics
            latency = (time.time() - start_time) * 1000
            metrics = self.model_pool.model_metrics[model_id]
            metrics.latency_ms = latency
            metrics.predictions_count += 1
            metrics.last_updated = datetime.utcnow()
            
            return {
                'prediction': prediction,
                'confidence': np.random.uniform(0.7, 0.95),
                'latency_ms': latency
            }
        
        except Exception as e:
            self.model_pool.model_status[model_id] = ModelStatus.ERROR
            raise e
        
        finally:
            # Mark model as idle
            self.model_pool.model_status[model_id] = ModelStatus.IDLE
    
    async def _combine_predictions(self, predictions: Dict[str, Any], strategy: EnsembleStrategy) -> Dict[str, Any]:
        """Combine predictions from multiple models"""
        valid_predictions = {k: v for k, v in predictions.items() if v is not None}
        
        if not valid_predictions:
            raise RuntimeError("No valid predictions to combine")
        
        if strategy == EnsembleStrategy.DYNAMIC_WEIGHTING:
            # Weight by recent performance
            weighted_sum = 0
            total_weight = 0
            
            for model_id, pred_data in valid_predictions.items():
                weight = self.ensemble_weights.get(model_id, 1.0)
                confidence = pred_data.get('confidence', 1.0)
                
                # Adjust weight by confidence
                adjusted_weight = weight * confidence
                weighted_sum += pred_data['prediction'] * adjusted_weight
                total_weight += adjusted_weight
            
            final_prediction = weighted_sum / total_weight if total_weight > 0 else 0
        
        else:
            # Simple average
            predictions_list = [pred['prediction'] for pred in valid_predictions.values()]
            final_prediction = np.mean(predictions_list)
        
        # Calculate ensemble confidence
        confidences = [pred['confidence'] for pred in valid_predictions.values()]
        ensemble_confidence = np.mean(confidences)
        
        # Calculate ensemble metrics
        latencies = [pred['latency_ms'] for pred in valid_predictions.values()]
        
        return {
            'prediction': final_prediction,
            'confidence': ensemble_confidence,
            'models_used': len(valid_predictions),
            'average_latency_ms': np.mean(latencies),
            'max_latency_ms': np.max(latencies),
            'strategy': strategy.value,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _update_prediction_metrics(self, model_ids -> None: List[str]) -> None:
        """Update prediction metrics for models"""
        for model_id in model_ids:
            if model_id in self.model_pool.model_metrics:
                metrics = self.model_pool.model_metrics[model_id]
                # Update throughput
                metrics.throughput = metrics.predictions_count / max(
                    (datetime.utcnow() - metrics.last_updated).total_seconds(), 1
                )
    
    async def _monitor_performance(self) -> None:
        """Monitor ensemble performance continuously"""
        while self.is_running:
            try:
                # Update adaptive weights
                if self.config.adaptive_weights:
                    await self._update_adaptive_weights()
                
                # Check for underperforming models
                await self._check_model_health()
                
                # Resource optimization
                await self._optimize_resources()
                
                # Sleep before next monitoring cycle
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _update_adaptive_weights(self) -> None:
        """Update model weights based on recent performance"""
        for model_id in self.model_pool.models.keys():
            metrics = self.model_pool.model_metrics[model_id]
            
            # Calculate performance score
            performance_score = (
                metrics.accuracy * 0.4 +
                (1 - metrics.error_rate) * 0.3 +
                (1 / max(metrics.latency_ms, 1)) * 0.3
            )
            
            # Update weight
            self.ensemble_weights[model_id] = max(0.1, min(2.0, performance_score))
    
    async def _check_model_health(self) -> None:
        """Check model health and handle failures"""
        for model_id, status in self.model_pool.model_status.items():
            if status == ModelStatus.ERROR:
                logger.warning(f"Model {model_id} in error state")
                # Could implement automatic recovery here
            
            metrics = self.model_pool.model_metrics[model_id]
            if metrics.error_rate > 0.1:  # 10% error rate threshold
                logger.warning(f"Model {model_id} has high error rate: {metrics.error_rate}")
    
    async def _optimize_resources(self) -> None:
        """Optimize resource usage across models"""
        pool_stats = self.model_pool.get_pool_stats()
        
        if pool_stats['utilization_rate'] > self.config.load_balance_threshold:
            logger.info("High utilization detected, considering load balancing")
            # Could implement auto-scaling logic here
    
    def get_ensemble_stats(self) -> Dict[str, Any]:
        """Get comprehensive ensemble statistics"""
        pool_stats = self.model_pool.get_pool_stats()
        
        return {
            'config': {
                'max_models': self.config.max_models,
                'strategy': self.config.strategy.value,
                'parallel_workers': self.config.parallel_workers
            },
            'pool_stats': pool_stats,
            'ensemble_weights': dict(self.ensemble_weights),
            'is_running': self.is_running,
            'total_registered_models': len(self.model_registry.models_db)
        }


class EnsembleOrchestrator:
    """High-level orchestrator for managing multiple ensemble managers"""
    
    def __init__(self) -> None:
        self.ensembles: Dict[str, LargeScaleEnsembleManager] = {}
        self.global_stats = {
            'total_models': 0,
            'total_predictions': 0,
            'active_ensembles': 0
        }
    
    async def create_ensemble(self, ensemble_id: str, config: EnsembleConfig) -> bool:
        """Create new ensemble"""
        if ensemble_id in self.ensembles:
            return False
        
        ensemble = LargeScaleEnsembleManager(config)
        await ensemble.start()
        
        self.ensembles[ensemble_id] = ensemble
        self.global_stats['active_ensembles'] = len(self.ensembles)
        
        logger.info(f"Created ensemble {ensemble_id}")
        return True
    
    async def remove_ensemble(self, ensemble_id: str) -> bool:
        """Remove ensemble"""
        if ensemble_id not in self.ensembles:
            return False
        
        ensemble = self.ensembles[ensemble_id]
        await ensemble.stop()
        del self.ensembles[ensemble_id]
        
        self.global_stats['active_ensembles'] = len(self.ensembles)
        
        logger.info(f"Removed ensemble {ensemble_id}")
        return True
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global orchestration statistics"""
        total_models = sum(
            len(ensemble.model_pool.models) 
            for ensemble in self.ensembles.values()
        )
        
        self.global_stats['total_models'] = total_models
        
        return self.global_stats.copy()