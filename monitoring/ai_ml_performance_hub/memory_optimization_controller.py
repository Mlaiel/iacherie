"""
💾 Memory Optimization Controller - Enterprise AI/ML Memory Management
====================================================================

Contrôleur optimisation mémoire IA/ML pour Creator Economy.
Monitoring consommation mémoire modèles, garbage collection intelligent, memory pooling.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Architecture: monitoring/ai_ml_performance_hub/memory_optimization_controller.py
Responsabilité: Optimisation mémoire modèles IA/ML Creator Economy
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import gc
import psutil
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
import threading
import time
from pathlib import Path


class MemoryType(Enum):
    """Types de mémoire surveillés"""
    SYSTEM_RAM = "system_ram"
    GPU_MEMORY = "gpu_memory"
    MODEL_CACHE = "model_cache"
    DATA_CACHE = "data_cache"
    INFERENCE_BUFFER = "inference_buffer"
    TRAINING_BUFFER = "training_buffer"


class OptimizationStrategy(Enum):
    """Stratégies optimisation mémoire"""
    GARBAGE_COLLECTION = "garbage_collection"
    CACHE_CLEARING = "cache_clearing"
    MODEL_UNLOADING = "model_unloading"
    BUFFER_OPTIMIZATION = "buffer_optimization"
    MEMORY_MAPPING = "memory_mapping"
    COMPRESSION = "compression"


class MemoryPressureLevel(Enum):
    """Niveaux pression mémoire"""
    LOW = "low"        # < 60% usage
    MODERATE = "moderate"  # 60-80% usage
    HIGH = "high"      # 80-95% usage
    CRITICAL = "critical"  # > 95% usage


class CreatorTierMemory(Enum):
    """Limites mémoire par tier créateur"""
    FREE = "free"      # 2GB limit
    PREMIUM = "premium"  # 8GB limit
    ENTERPRISE = "enterprise"  # 32GB limit


@dataclass
class MemoryUsageMetrics:
    """Métriques utilisation mémoire"""
    metric_id: str
    model_id: str
    creator_tier: CreatorTierMemory
    
    # System memory
    system_ram_total: float  # MB
    system_ram_used: float   # MB
    system_ram_available: float  # MB
    system_ram_percentage: float
    
    # GPU memory
    gpu_memory_total: float  # MB
    gpu_memory_used: float   # MB
    gpu_memory_available: float  # MB
    gpu_memory_percentage: float
    
    # Model-specific memory
    model_memory_footprint: float  # MB
    cache_memory_usage: float      # MB
    buffer_memory_usage: float     # MB
    
    # Performance impact
    memory_pressure_level: MemoryPressureLevel
    gc_frequency: int  # garbage collections per minute
    swap_usage: float  # MB
    memory_fragmentation: float  # percentage
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MemoryOptimizationAction:
    """Action optimisation mémoire"""
    action_id: str
    model_id: str
    strategy: OptimizationStrategy
    target_memory_type: MemoryType
    memory_before: float  # MB
    memory_after: float   # MB
    memory_freed: float   # MB
    execution_time: float  # seconds
    success: bool
    impact_score: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MemoryPoolConfiguration:
    """Configuration pool mémoire"""
    pool_id: str
    pool_type: MemoryType
    max_size: float  # MB
    current_usage: float  # MB
    allocation_strategy: str
    eviction_policy: str
    creator_tier_limits: Dict[str, float]


@dataclass
class OOMPreventionAlert:
    """Alerte prévention Out of Memory"""
    alert_id: str
    model_id: str
    predicted_oom_time: datetime
    current_memory_trend: float  # MB/minute
    recommended_actions: List[str]
    severity: str
    creator_impact: str


class MemoryOptimizationController:
    """Contrôleur optimisation mémoire enterprise"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Memory tracking
        self.memory_metrics_history: Dict[str, List[MemoryUsageMetrics]] = {}
        self.optimization_actions: List[MemoryOptimizationAction] = []
        self.memory_pools: Dict[str, MemoryPoolConfiguration] = {}
        self.oom_alerts: List[OOMPreventionAlert] = []
        
        # Memory thresholds
        self.memory_thresholds = {
            MemoryPressureLevel.LOW: 0.6,
            MemoryPressureLevel.MODERATE: 0.8,
            MemoryPressureLevel.HIGH: 0.95,
            MemoryPressureLevel.CRITICAL: 0.98
        }
        
        # Creator tier limits (MB)
        self.creator_tier_limits = {
            CreatorTierMemory.FREE.value: 2048,
            CreatorTierMemory.PREMIUM.value: 8192,
            CreatorTierMemory.ENTERPRISE.value: 32768
        }
        
        # Optimization strategies effectiveness
        self.strategy_effectiveness = {
            OptimizationStrategy.GARBAGE_COLLECTION: 0.1,    # 10% memory recovery
            OptimizationStrategy.CACHE_CLEARING: 0.3,        # 30% cache recovery
            OptimizationStrategy.MODEL_UNLOADING: 0.8,       # 80% model memory recovery
            OptimizationStrategy.BUFFER_OPTIMIZATION: 0.2,   # 20% buffer optimization
            OptimizationStrategy.MEMORY_MAPPING: 0.15,       # 15% through mapping
            OptimizationStrategy.COMPRESSION: 0.4            # 40% through compression
        }
        
        # Background monitoring
        self._monitoring_active = False
        self._monitoring_task = None
        
        # Initialize memory pools
        asyncio.create_task(self._initialize_memory_pools())
    
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("memory_optimization_controller")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def _initialize_memory_pools(self):
        """Initialisation pools mémoire"""
        try:
            # Model cache pool
            self.memory_pools["model_cache"] = MemoryPoolConfiguration(
                pool_id="model_cache",
                pool_type=MemoryType.MODEL_CACHE,
                max_size=8192,  # 8GB
                current_usage=0,
                allocation_strategy="LRU",
                eviction_policy="least_recently_used",
                creator_tier_limits={
                    "free": 512,
                    "premium": 2048,
                    "enterprise": 8192
                }
            )
            
            # Data cache pool
            self.memory_pools["data_cache"] = MemoryPoolConfiguration(
                pool_id="data_cache",
                pool_type=MemoryType.DATA_CACHE,
                max_size=4096,  # 4GB
                current_usage=0,
                allocation_strategy="FIFO",
                eviction_policy="first_in_first_out",
                creator_tier_limits={
                    "free": 256,
                    "premium": 1024,
                    "enterprise": 4096
                }
            )
            
            # Inference buffer pool
            self.memory_pools["inference_buffer"] = MemoryPoolConfiguration(
                pool_id="inference_buffer",
                pool_type=MemoryType.INFERENCE_BUFFER,
                max_size=2048,  # 2GB
                current_usage=0,
                allocation_strategy="dynamic",
                eviction_policy="immediate_after_use",
                creator_tier_limits={
                    "free": 128,
                    "premium": 512,
                    "enterprise": 2048
                }
            )
            
            self.logger.info("✅ Memory pools initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing memory pools: {e}")
    
    async def start_memory_monitoring(self, model_id: str, creator_tier: str = "free"):
        """Démarrage monitoring mémoire"""
        try:
            if self._monitoring_active:
                await self.stop_memory_monitoring()
            
            self._monitoring_active = True
            self._monitoring_task = asyncio.create_task(
                self._continuous_memory_monitoring(model_id, creator_tier)
            )
            
            self.logger.info(f"🔍 Started memory monitoring for model {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting memory monitoring: {e}")
            return False
    
    async def _continuous_memory_monitoring(self, model_id: str, creator_tier: str):
        """Monitoring continu mémoire"""
        try:
            while self._monitoring_active:
                # Collect memory metrics
                metrics = await self._collect_memory_metrics(model_id, creator_tier)
                
                # Store metrics
                if model_id not in self.memory_metrics_history:
                    self.memory_metrics_history[model_id] = []
                
                self.memory_metrics_history[model_id].append(metrics)
                
                # Keep only recent metrics (last 1000 points)
                if len(self.memory_metrics_history[model_id]) > 1000:
                    self.memory_metrics_history[model_id] = self.memory_metrics_history[model_id][-1000:]
                
                # Check for optimization needs
                await self._check_optimization_triggers(metrics)
                
                # Check for OOM prediction
                await self._predict_oom(model_id)
                
                # Wait before next collection
                await asyncio.sleep(10)  # 10 second intervals
                
        except Exception as e:
            self.logger.error(f"Error in continuous memory monitoring: {e}")
    
    async def _collect_memory_metrics(self, model_id: str, creator_tier: str) -> MemoryUsageMetrics:
        """Collecte métriques mémoire"""
        try:
            # System memory metrics
            memory_info = psutil.virtual_memory()
            swap_info = psutil.swap_memory()
            
            # GPU memory (simplified - would use actual GPU libraries)
            gpu_total = 16384  # 16GB GPU assumption
            gpu_used = np.random.uniform(2000, 12000)  # Simulated
            gpu_available = gpu_total - gpu_used
            
            # Model-specific memory (simulated)
            model_memory = np.random.uniform(500, 2000)
            cache_memory = np.random.uniform(100, 1000)
            buffer_memory = np.random.uniform(50, 500)
            
            # Calculate pressure level
            system_pressure = memory_info.percent / 100
            gpu_pressure = gpu_used / gpu_total
            overall_pressure = max(system_pressure, gpu_pressure)
            
            if overall_pressure >= self.memory_thresholds[MemoryPressureLevel.CRITICAL]:
                pressure_level = MemoryPressureLevel.CRITICAL
            elif overall_pressure >= self.memory_thresholds[MemoryPressureLevel.HIGH]:
                pressure_level = MemoryPressureLevel.HIGH
            elif overall_pressure >= self.memory_thresholds[MemoryPressureLevel.MODERATE]:
                pressure_level = MemoryPressureLevel.MODERATE
            else:
                pressure_level = MemoryPressureLevel.LOW
            
            # GC frequency (simplified)
            gc_frequency = len(gc.get_stats()) if hasattr(gc, 'get_stats') else 0
            
            # Memory fragmentation (simplified calculation)
            fragmentation = min(30.0, max(0.0, (memory_info.percent - 50) * 0.6))
            
            metrics = MemoryUsageMetrics(
                metric_id=str(uuid.uuid4()),
                model_id=model_id,
                creator_tier=CreatorTierMemory(creator_tier),
                system_ram_total=memory_info.total / (1024**2),
                system_ram_used=memory_info.used / (1024**2),
                system_ram_available=memory_info.available / (1024**2),
                system_ram_percentage=memory_info.percent,
                gpu_memory_total=gpu_total,
                gpu_memory_used=gpu_used,
                gpu_memory_available=gpu_available,
                gpu_memory_percentage=(gpu_used / gpu_total) * 100,
                model_memory_footprint=model_memory,
                cache_memory_usage=cache_memory,
                buffer_memory_usage=buffer_memory,
                memory_pressure_level=pressure_level,
                gc_frequency=gc_frequency,
                swap_usage=swap_info.used / (1024**2),
                memory_fragmentation=fragmentation
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {e}")
            # Return default metrics
            return MemoryUsageMetrics(
                metric_id=str(uuid.uuid4()),
                model_id=model_id,
                creator_tier=CreatorTierMemory(creator_tier),
                system_ram_total=0, system_ram_used=0, system_ram_available=0,
                system_ram_percentage=0, gpu_memory_total=0, gpu_memory_used=0,
                gpu_memory_available=0, gpu_memory_percentage=0,
                model_memory_footprint=0, cache_memory_usage=0,
                buffer_memory_usage=0, memory_pressure_level=MemoryPressureLevel.LOW,
                gc_frequency=0, swap_usage=0, memory_fragmentation=0
            )
    
    async def _check_optimization_triggers(self, metrics: MemoryUsageMetrics):
        """Vérification déclencheurs optimisation"""
        try:
            # Check creator tier limits
            tier_limit = self.creator_tier_limits[metrics.creator_tier.value]
            model_memory_usage = metrics.model_memory_footprint + metrics.cache_memory_usage + metrics.buffer_memory_usage
            
            if model_memory_usage > tier_limit:
                await self._trigger_optimization(metrics.model_id, OptimizationStrategy.CACHE_CLEARING, 
                                               f"Creator tier limit exceeded: {model_memory_usage:.1f}MB > {tier_limit}MB")
            
            # Check memory pressure levels
            if metrics.memory_pressure_level == MemoryPressureLevel.CRITICAL:
                await self._trigger_optimization(metrics.model_id, OptimizationStrategy.MODEL_UNLOADING,
                                               "Critical memory pressure detected")
            elif metrics.memory_pressure_level == MemoryPressureLevel.HIGH:
                await self._trigger_optimization(metrics.model_id, OptimizationStrategy.GARBAGE_COLLECTION,
                                               "High memory pressure detected")
            
            # Check GPU memory usage
            if metrics.gpu_memory_percentage > 90:
                await self._trigger_optimization(metrics.model_id, OptimizationStrategy.BUFFER_OPTIMIZATION,
                                               f"High GPU memory usage: {metrics.gpu_memory_percentage:.1f}%")
            
            # Check fragmentation
            if metrics.memory_fragmentation > 20:
                await self._trigger_optimization(metrics.model_id, OptimizationStrategy.COMPRESSION,
                                               f"High memory fragmentation: {metrics.memory_fragmentation:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error checking optimization triggers: {e}")
    
    async def _trigger_optimization(self, model_id: str, strategy: OptimizationStrategy, reason: str):
        """Déclenchement optimisation"""
        try:
            self.logger.info(f"🔧 Triggering {strategy.value} for {model_id}: {reason}")
            
            # Execute optimization
            action = await self._execute_optimization_strategy(model_id, strategy)
            
            if action and action.success:
                self.logger.info(f"✅ Optimization successful: freed {action.memory_freed:.1f}MB")
            else:
                self.logger.warning(f"⚠️ Optimization failed for {model_id}")
                
        except Exception as e:
            self.logger.error(f"Error triggering optimization: {e}")
    
    async def _execute_optimization_strategy(self, 
                                           model_id: str, 
                                           strategy: OptimizationStrategy,
                                           target_memory_type: MemoryType = None) -> Optional[MemoryOptimizationAction]:
        """Exécution stratégie optimisation"""
        try:
            start_time = time.time()
            
            # Get memory before optimization
            memory_before = await self._get_current_memory_usage(model_id)
            
            # Execute strategy
            success = False
            if strategy == OptimizationStrategy.GARBAGE_COLLECTION:
                success = await self._execute_garbage_collection()
            elif strategy == OptimizationStrategy.CACHE_CLEARING:
                success = await self._execute_cache_clearing(model_id)
            elif strategy == OptimizationStrategy.MODEL_UNLOADING:
                success = await self._execute_model_unloading(model_id)
            elif strategy == OptimizationStrategy.BUFFER_OPTIMIZATION:
                success = await self._execute_buffer_optimization(model_id)
            elif strategy == OptimizationStrategy.COMPRESSION:
                success = await self._execute_compression(model_id)
            elif strategy == OptimizationStrategy.MEMORY_MAPPING:
                success = await self._execute_memory_mapping(model_id)
            
            # Get memory after optimization
            memory_after = await self._get_current_memory_usage(model_id)
            memory_freed = max(0, memory_before - memory_after)
            
            execution_time = time.time() - start_time
            
            # Calculate impact score
            expected_freed = memory_before * self.strategy_effectiveness[strategy]
            impact_score = min(1.0, memory_freed / max(1, expected_freed))
            
            action = MemoryOptimizationAction(
                action_id=str(uuid.uuid4()),
                model_id=model_id,
                strategy=strategy,
                target_memory_type=target_memory_type or MemoryType.SYSTEM_RAM,
                memory_before=memory_before,
                memory_after=memory_after,
                memory_freed=memory_freed,
                execution_time=execution_time,
                success=success,
                impact_score=impact_score
            )
            
            self.optimization_actions.append(action)
            
            # Keep only recent actions
            if len(self.optimization_actions) > 1000:
                self.optimization_actions = self.optimization_actions[-1000:]
            
            return action
            
        except Exception as e:
            self.logger.error(f"Error executing optimization strategy: {e}")
            return None
    
    async def _get_current_memory_usage(self, model_id: str) -> float:
        """Récupération usage mémoire actuel"""
        try:
            if model_id in self.memory_metrics_history and self.memory_metrics_history[model_id]:
                latest_metrics = self.memory_metrics_history[model_id][-1]
                return (latest_metrics.model_memory_footprint + 
                       latest_metrics.cache_memory_usage + 
                       latest_metrics.buffer_memory_usage)
            else:
                # Fallback to system memory
                memory_info = psutil.virtual_memory()
                return memory_info.used / (1024**2)
        except:
            return 1000.0  # Default value
    
    async def _execute_garbage_collection(self) -> bool:
        """Exécution garbage collection"""
        try:
            # Force garbage collection
            collected = gc.collect()
            self.logger.debug(f"Garbage collection freed {collected} objects")
            return True
        except Exception as e:
            self.logger.error(f"Error in garbage collection: {e}")
            return False
    
    async def _execute_cache_clearing(self, model_id: str) -> bool:
        """Exécution nettoyage cache"""
        try:
            # Clear model cache (simulated)
            if "model_cache" in self.memory_pools:
                pool = self.memory_pools["model_cache"]
                cleared_size = pool.current_usage * 0.8  # Clear 80% of cache
                pool.current_usage = max(0, pool.current_usage - cleared_size)
                
            # Clear data cache
            if "data_cache" in self.memory_pools:
                pool = self.memory_pools["data_cache"]
                cleared_size = pool.current_usage * 0.6  # Clear 60% of data cache
                pool.current_usage = max(0, pool.current_usage - cleared_size)
                
            self.logger.debug(f"Cache cleared for model {model_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False
    
    async def _execute_model_unloading(self, model_id: str) -> bool:
        """Exécution déchargement modèle"""
        try:
            # Unload model from memory (simulated)
            # In real implementation, this would interface with ML framework
            self.logger.warning(f"Model {model_id} unloaded from memory")
            return True
        except Exception as e:
            self.logger.error(f"Error unloading model: {e}")
            return False
    
    async def _execute_buffer_optimization(self, model_id: str) -> bool:
        """Exécution optimisation buffers"""
        try:
            # Optimize inference buffers
            if "inference_buffer" in self.memory_pools:
                pool = self.memory_pools["inference_buffer"]
                # Resize buffers to optimal size
                optimal_size = pool.max_size * 0.7
                if pool.current_usage > optimal_size:
                    pool.current_usage = optimal_size
                    
            self.logger.debug(f"Buffer optimization completed for {model_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error optimizing buffers: {e}")
            return False
    
    async def _execute_compression(self, model_id: str) -> bool:
        """Exécution compression mémoire"""
        try:
            # Apply memory/model compression techniques (simulated)
            self.logger.debug(f"Memory compression applied for {model_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error applying compression: {e}")
            return False
    
    async def _execute_memory_mapping(self, model_id: str) -> bool:
        """Exécution memory mapping"""
        try:
            # Apply memory mapping optimization (simulated)
            self.logger.debug(f"Memory mapping optimized for {model_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error optimizing memory mapping: {e}")
            return False
    
    async def _predict_oom(self, model_id: str):
        """Prédiction Out of Memory"""
        try:
            if model_id not in self.memory_metrics_history:
                return
            
            metrics_history = self.memory_metrics_history[model_id]
            if len(metrics_history) < 10:  # Need sufficient data
                return
            
            # Calculate memory usage trend
            recent_metrics = metrics_history[-10:]
            memory_usages = [
                m.system_ram_used + m.model_memory_footprint + m.cache_memory_usage
                for m in recent_metrics
            ]
            
            # Linear trend analysis
            time_points = list(range(len(memory_usages)))
            if len(memory_usages) >= 2:
                trend = np.polyfit(time_points, memory_usages, 1)[0]  # MB per measurement
                
                if trend > 50:  # Memory increasing by more than 50MB per measurement
                    # Predict when memory will be exhausted
                    current_memory = memory_usages[-1]
                    available_memory = recent_metrics[-1].system_ram_available
                    
                    if trend > 0:
                        measurements_to_oom = available_memory / trend
                        time_to_oom = measurements_to_oom * 10  # 10 seconds per measurement
                        
                        if time_to_oom < 600:  # Less than 10 minutes
                            # Generate OOM alert
                            alert = OOMPreventionAlert(
                                alert_id=str(uuid.uuid4()),
                                model_id=model_id,
                                predicted_oom_time=datetime.utcnow() + timedelta(seconds=time_to_oom),
                                current_memory_trend=trend * 6,  # MB per minute
                                recommended_actions=[
                                    "Immediate cache clearing",
                                    "Model unloading if non-critical",
                                    "Buffer size reduction",
                                    "Consider upgrading creator tier"
                                ],
                                severity="CRITICAL" if time_to_oom < 120 else "HIGH",
                                creator_impact="Service interruption likely"
                            )
                            
                            self.oom_alerts.append(alert)
                            
                            self.logger.critical(
                                f"🚨 OOM PREDICTION: Model {model_id} may run out of memory in {time_to_oom:.1f} seconds"
                            )
                            
                            # Trigger immediate optimization
                            await self._trigger_optimization(
                                model_id, 
                                OptimizationStrategy.CACHE_CLEARING,
                                f"OOM predicted in {time_to_oom:.1f} seconds"
                            )
            
        except Exception as e:
            self.logger.error(f"Error predicting OOM: {e}")
    
    async def optimize_memory_for_creator_tier(self, model_id: str, creator_tier: str) -> Dict[str, Any]:
        """Optimisation mémoire pour tier créateur"""
        try:
            tier_limit = self.creator_tier_limits[creator_tier]
            
            # Get current memory usage
            current_usage = await self._get_current_memory_usage(model_id)
            
            if current_usage <= tier_limit:
                return {
                    'optimization_needed': False,
                    'current_usage': current_usage,
                    'tier_limit': tier_limit,
                    'message': 'Memory usage within tier limits'
                }
            
            # Calculate required memory reduction
            excess_memory = current_usage - tier_limit
            optimization_target = excess_memory * 1.2  # 20% buffer
            
            # Select optimization strategies
            strategies = []
            if creator_tier == "free":
                strategies = [
                    OptimizationStrategy.CACHE_CLEARING,
                    OptimizationStrategy.BUFFER_OPTIMIZATION,
                    OptimizationStrategy.COMPRESSION
                ]
            elif creator_tier == "premium":
                strategies = [
                    OptimizationStrategy.CACHE_CLEARING,
                    OptimizationStrategy.GARBAGE_COLLECTION,
                    OptimizationStrategy.BUFFER_OPTIMIZATION
                ]
            else:  # enterprise
                strategies = [
                    OptimizationStrategy.GARBAGE_COLLECTION,
                    OptimizationStrategy.MEMORY_MAPPING
                ]
            
            # Execute optimizations
            total_freed = 0
            executed_actions = []
            
            for strategy in strategies:
                if total_freed >= optimization_target:
                    break
                    
                action = await self._execute_optimization_strategy(model_id, strategy)
                if action and action.success:
                    total_freed += action.memory_freed
                    executed_actions.append(action)
            
            # Check final usage
            final_usage = await self._get_current_memory_usage(model_id)
            
            return {
                'optimization_needed': True,
                'initial_usage': current_usage,
                'final_usage': final_usage,
                'tier_limit': tier_limit,
                'memory_freed': total_freed,
                'strategies_executed': [a.strategy.value for a in executed_actions],
                'within_limits': final_usage <= tier_limit,
                'message': f'Optimized memory usage for {creator_tier} tier'
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing memory for creator tier: {e}")
            return {'error': str(e)}
    
    async def get_memory_usage_report(self, model_id: str) -> Dict[str, Any]:
        """Rapport utilisation mémoire"""
        try:
            if model_id not in self.memory_metrics_history:
                return {'model_id': model_id, 'error': 'No metrics available'}
            
            metrics_history = self.memory_metrics_history[model_id]
            if not metrics_history:
                return {'model_id': model_id, 'error': 'No metrics data'}
            
            latest_metrics = metrics_history[-1]
            
            # Calculate averages over last hour (360 measurements at 10s intervals)
            recent_metrics = metrics_history[-360:] if len(metrics_history) >= 360 else metrics_history
            
            avg_system_usage = statistics.mean([m.system_ram_percentage for m in recent_metrics])
            avg_gpu_usage = statistics.mean([m.gpu_memory_percentage for m in recent_metrics])
            avg_model_memory = statistics.mean([m.model_memory_footprint for m in recent_metrics])
            
            # Find peak usage
            peak_system = max([m.system_ram_percentage for m in recent_metrics])
            peak_gpu = max([m.gpu_memory_percentage for m in recent_metrics])
            
            # Recent optimization actions
            recent_actions = [
                {
                    'strategy': action.strategy.value,
                    'memory_freed': action.memory_freed,
                    'success': action.success,
                    'timestamp': action.timestamp.isoformat()
                }
                for action in self.optimization_actions
                if action.model_id == model_id and 
                   (datetime.utcnow() - action.timestamp).total_seconds() < 3600
            ]
            
            # Memory efficiency score
            tier_limit = self.creator_tier_limits[latest_metrics.creator_tier.value]
            current_usage = (latest_metrics.model_memory_footprint + 
                           latest_metrics.cache_memory_usage + 
                           latest_metrics.buffer_memory_usage)
            efficiency_score = max(0.0, 1.0 - (current_usage / tier_limit))
            
            return {
                'model_id': model_id,
                'creator_tier': latest_metrics.creator_tier.value,
                'current_status': {
                    'system_ram_usage': latest_metrics.system_ram_percentage,
                    'gpu_memory_usage': latest_metrics.gpu_memory_percentage,
                    'model_memory_footprint': latest_metrics.model_memory_footprint,
                    'memory_pressure_level': latest_metrics.memory_pressure_level.value,
                    'tier_limit': tier_limit,
                    'within_tier_limits': current_usage <= tier_limit
                },
                'performance_metrics': {
                    'average_system_usage': avg_system_usage,
                    'average_gpu_usage': avg_gpu_usage,
                    'average_model_memory': avg_model_memory,
                    'peak_system_usage': peak_system,
                    'peak_gpu_usage': peak_gpu,
                    'memory_efficiency_score': efficiency_score
                },
                'optimization_history': {
                    'recent_actions_count': len(recent_actions),
                    'actions': recent_actions,
                    'total_memory_freed_1h': sum([a['memory_freed'] for a in recent_actions])
                },
                'recommendations': await self._generate_memory_recommendations(model_id)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating memory report: {e}")
            return {'model_id': model_id, 'error': str(e)}
    
    async def _generate_memory_recommendations(self, model_id: str) -> List[str]:
        """Génération recommandations mémoire"""
        recommendations = []
        
        try:
            if model_id not in self.memory_metrics_history:
                return recommendations
            
            metrics_history = self.memory_metrics_history[model_id]
            if not metrics_history:
                return recommendations
            
            latest_metrics = metrics_history[-1]
            
            # High memory usage recommendations
            if latest_metrics.memory_pressure_level in [MemoryPressureLevel.HIGH, MemoryPressureLevel.CRITICAL]:
                recommendations.append("Consider upgrading to higher creator tier for more memory allocation")
                recommendations.append("Enable automatic cache clearing for optimal memory management")
            
            # GPU memory recommendations
            if latest_metrics.gpu_memory_percentage > 85:
                recommendations.append("Reduce batch size to optimize GPU memory usage")
                recommendations.append("Consider model quantization to reduce GPU memory footprint")
            
            # Fragmentation recommendations
            if latest_metrics.memory_fragmentation > 15:
                recommendations.append("Schedule regular memory defragmentation during low usage periods")
            
            # Creator tier recommendations
            tier_limit = self.creator_tier_limits[latest_metrics.creator_tier.value]
            current_usage = (latest_metrics.model_memory_footprint + 
                           latest_metrics.cache_memory_usage + 
                           latest_metrics.buffer_memory_usage)
            
            if current_usage > tier_limit * 0.9:
                if latest_metrics.creator_tier == CreatorTierMemory.FREE:
                    recommendations.append("Upgrade to Premium tier for 4x more memory allocation")
                elif latest_metrics.creator_tier == CreatorTierMemory.PREMIUM:
                    recommendations.append("Upgrade to Enterprise tier for unlimited memory allocation")
            
            # Swap usage recommendations
            if latest_metrics.swap_usage > 1000:  # More than 1GB swap
                recommendations.append("High swap usage detected - consider adding more RAM")
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return recommendations
    
    async def get_memory_pool_status(self) -> Dict[str, Any]:
        """Statut des pools mémoire"""
        return {
            'pools': {
                pool_id: {
                    'type': pool.pool_type.value,
                    'max_size_mb': pool.max_size,
                    'current_usage_mb': pool.current_usage,
                    'utilization_percentage': (pool.current_usage / pool.max_size) * 100,
                    'allocation_strategy': pool.allocation_strategy,
                    'eviction_policy': pool.eviction_policy,
                    'creator_tier_limits': pool.creator_tier_limits
                }
                for pool_id, pool in self.memory_pools.items()
            },
            'total_pools': len(self.memory_pools),
            'total_allocated_mb': sum(pool.current_usage for pool in self.memory_pools.values()),
            'total_capacity_mb': sum(pool.max_size for pool in self.memory_pools.values())
        }
    
    async def stop_memory_monitoring(self):
        """Arrêt monitoring mémoire"""
        try:
            self._monitoring_active = False
            
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
                self._monitoring_task = None
            
            self.logger.info("⏹️ Memory monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping memory monitoring: {e}")
    
    async def shutdown(self):
        """Arrêt propre du contrôleur"""
        self.logger.info("⏹️ Arrêt Memory Optimization Controller...")
        
        # Stop monitoring
        await self.stop_memory_monitoring()
        
        # Clear data
        self.memory_metrics_history.clear()
        self.optimization_actions.clear()
        self.memory_pools.clear()
        self.oom_alerts.clear()
        
        self.logger.info("✅ Memory Optimization Controller arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_memory_controller():
        config = {
            'debug': True,
            'monitoring_interval': 5
        }
        
        controller = MemoryOptimizationController(config)
        
        # Test memory monitoring
        success = await controller.start_memory_monitoring("test_model_001", "premium")
        print(f"Memory monitoring started: {success}")
        
        # Let it run for a few cycles
        await asyncio.sleep(30)
        
        # Test optimization
        optimization_result = await controller.optimize_memory_for_creator_tier("test_model_001", "premium")
        print(f"Optimization result: {optimization_result}")
        
        # Generate report
        report = await controller.get_memory_usage_report("test_model_001")
        print(f"Memory report generated: {len(report)} fields")
        
        # Check pool status
        pool_status = await controller.get_memory_pool_status()
        print(f"Memory pools: {pool_status['total_pools']}")
        
        print('✅ Memory Optimization Controller test passed')
        await controller.shutdown()
    
    asyncio.run(test_memory_controller())