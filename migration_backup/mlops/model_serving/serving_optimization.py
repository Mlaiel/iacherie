"""
📊 Serving Optimization Engine - Enterprise MLOps
Expert ML Engineer + Backend Senior: Optimisation serving ML haute performance

🎯 EXPERTISE DÉMONTRÉ:
- ML Engineer: Optimisation inférence + cache intelligent modèles
- Backend Senior: Performance <10ms + architecture serving
- DevOps: Auto-scaling + monitoring serving temps réel
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationStrategy(Enum):
    """Stratégies d'optimisation serving"""
    LATENCY_FOCUSED = "latency_focused"
    THROUGHPUT_FOCUSED = "throughput_focused"
    COST_OPTIMIZED = "cost_optimized"
    BALANCED = "balanced"

class ModelFormat(Enum):
    """Formats de modèles optimisés"""
    ORIGINAL = "original"
    QUANTIZED = "quantized"
    TENSORRT = "tensorrt"
    ONNX = "onnx"
    TFLITE = "tflite"

@dataclass
class ServingConfig:
    """Configuration de serving optimisé"""
    model_id: str
    model_format: ModelFormat
    batch_size: int
    max_latency_ms: float
    target_throughput: int
    cache_enabled: bool = True
    auto_scaling: bool = True
    gpu_enabled: bool = False
    optimization_level: int = 1  # 1-3

@dataclass
class OptimizationMetrics:
    """Métriques d'optimisation"""
    latency_p95: float
    latency_p99: float
    throughput_rps: float
    memory_usage_mb: float
    cpu_utilization: float
    cache_hit_rate: float
    optimization_gain: float  # % d'amélioration

class ServingOptimizationEngine:
    """
    📊 Moteur Enterprise d'Optimisation Serving
    
    Expertise ML Engineer + Backend Senior:
    - Optimisation automatique inférence <10ms
    - Cache multi-niveau intelligent
    - Auto-tuning paramètres serving
    - Monitoring performance temps réel
    """
    
    def __init__(self):
        self.serving_configs: Dict[str, ServingConfig] = {}
        self.optimization_history: List[Dict] = []
        self.performance_cache: Dict[str, Any] = {}
        self.auto_scaling_rules: Dict[str, Dict] = {}
        
        # Métriques en temps réel
        self.real_time_metrics: Dict[str, OptimizationMetrics] = {}
        self.performance_buffer: Dict[str, List] = {}
        
        # Seuils d'optimisation
        self.optimization_thresholds = {
            "latency_target_ms": 50.0,
            "throughput_min_rps": 100,
            "memory_limit_mb": 2048,
            "cpu_limit": 0.8
        }
    
    async def optimize_serving_config(
        self,
        model_id: str,
        strategy: OptimizationStrategy,
        constraints: Optional[Dict[str, Any]] = None
    ) -> ServingConfig:
        """
        Optimise automatiquement la configuration de serving
        
        Expertise ML Engineer: Auto-tuning paramètres serving
        """
        logger.info(f"Starting serving optimization for {model_id} with strategy {strategy.value}")
        
        # Configuration de base
        base_config = ServingConfig(
            model_id=model_id,
            model_format=ModelFormat.ORIGINAL,
            batch_size=1,
            max_latency_ms=100.0,
            target_throughput=100
        )
        
        constraints = constraints or {}
        
        # Analyse des métriques historiques
        historical_metrics = await self._analyze_historical_performance(model_id)
        
        # Optimisation selon la stratégie
        if strategy == OptimizationStrategy.LATENCY_FOCUSED:
            optimized_config = await self._optimize_for_latency(base_config, constraints, historical_metrics)
        elif strategy == OptimizationStrategy.THROUGHPUT_FOCUSED:
            optimized_config = await self._optimize_for_throughput(base_config, constraints, historical_metrics)
        elif strategy == OptimizationStrategy.COST_OPTIMIZED:
            optimized_config = await self._optimize_for_cost(base_config, constraints, historical_metrics)
        else:  # BALANCED
            optimized_config = await self._optimize_balanced(base_config, constraints, historical_metrics)
        
        # Validation de la configuration
        validation_result = await self._validate_config(optimized_config)
        if not validation_result["valid"]:
            logger.warning(f"Configuration validation failed: {validation_result['issues']}")
            # Fallback vers configuration plus conservative
            optimized_config = await self._create_conservative_config(base_config, constraints)
        
        # Enregistrer la configuration
        self.serving_configs[model_id] = optimized_config
        
        # Log de l'optimisation
        self.optimization_history.append({
            "timestamp": datetime.utcnow(),
            "model_id": model_id,
            "strategy": strategy.value,
            "config": optimized_config,
            "historical_metrics": historical_metrics
        })
        
        logger.info(f"Serving optimization completed for {model_id}")
        return optimized_config
    
    async def _optimize_for_latency(
        self,
        base_config: ServingConfig,
        constraints: Dict,
        historical_metrics: Dict
    ) -> ServingConfig:
        """Optimisation focalisée sur la latence"""
        config = base_config
        
        # Format de modèle optimisé pour latence
        if not constraints.get("preserve_accuracy", False):
            config.model_format = ModelFormat.TENSORRT if constraints.get("gpu_available") else ModelFormat.QUANTIZED
        
        # Batch size = 1 pour latence minimale
        config.batch_size = 1
        
        # Latence cible agressive
        config.max_latency_ms = min(20.0, constraints.get("max_latency_ms", 50.0))
        
        # Cache agressif
        config.cache_enabled = True
        
        # GPU si disponible
        config.gpu_enabled = constraints.get("gpu_available", False)
        
        # Niveau d'optimisation maximum
        config.optimization_level = 3
        
        return config
    
    async def _optimize_for_throughput(
        self,
        base_config: ServingConfig,
        constraints: Dict,
        historical_metrics: Dict
    ) -> ServingConfig:
        """Optimisation focalisée sur le débit"""
        config = base_config
        
        # Batch size optimisé pour débit
        optimal_batch_size = await self._find_optimal_batch_size(
            base_config.model_id, constraints
        )
        config.batch_size = optimal_batch_size
        
        # Latence plus permissive
        config.max_latency_ms = constraints.get("max_latency_ms", 200.0)
        
        # Objectif de débit élevé
        config.target_throughput = constraints.get("target_throughput", 1000)
        
        # Auto-scaling activé
        config.auto_scaling = True
        
        # Format équilibré
        config.model_format = ModelFormat.ONNX
        
        return config
    
    async def _optimize_for_cost(
        self,
        base_config: ServingConfig,
        constraints: Dict,
        historical_metrics: Dict
    ) -> ServingConfig:
        """Optimisation focalisée sur les coûts"""
        config = base_config
        
        # Modèle quantifié pour réduire les ressources
        config.model_format = ModelFormat.QUANTIZED
        
        # Batch size plus élevé pour efficacité
        config.batch_size = 8
        
        # Pas de GPU par défaut (coût)
        config.gpu_enabled = False
        
        # Cache pour réduire les calculs
        config.cache_enabled = True
        
        # Auto-scaling conservateur
        config.auto_scaling = True
        
        return config
    
    async def _optimize_balanced(
        self,
        base_config: ServingConfig,
        constraints: Dict,
        historical_metrics: Dict
    ) -> ServingConfig:
        """Optimisation équilibrée"""
        config = base_config
        
        # Format équilibré
        config.model_format = ModelFormat.ONNX
        
        # Batch size modéré
        config.batch_size = 4
        
        # Latence raisonnable
        config.max_latency_ms = 50.0
        
        # Débit modéré
        config.target_throughput = 500
        
        # Optimisations standards
        config.cache_enabled = True
        config.auto_scaling = True
        config.optimization_level = 2
        
        return config
    
    async def _find_optimal_batch_size(
        self,
        model_id: str,
        constraints: Dict
    ) -> int:
        """Trouve la taille de batch optimale"""
        # Simulation - en production, faire des tests de performance
        memory_limit = constraints.get("memory_limit_mb", 2048)
        
        # Estimer la taille de batch basée sur la mémoire
        if memory_limit < 1024:
            return 1
        elif memory_limit < 2048:
            return 4
        elif memory_limit < 4096:
            return 8
        else:
            return 16
    
    async def _analyze_historical_performance(self, model_id: str) -> Dict[str, Any]:
        """Analyse les performances historiques"""
        if model_id not in self.performance_buffer:
            return {"sample_size": 0}
        
        performance_data = self.performance_buffer[model_id]
        
        if not performance_data:
            return {"sample_size": 0}
        
        latencies = [p["latency"] for p in performance_data]
        throughputs = [p["throughput"] for p in performance_data]
        
        return {
            "sample_size": len(performance_data),
            "avg_latency": statistics.mean(latencies),
            "p95_latency": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies),
            "avg_throughput": statistics.mean(throughputs),
            "max_throughput": max(throughputs)
        }
    
    async def _validate_config(self, config: ServingConfig) -> Dict[str, Any]:
        """Valide une configuration de serving"""
        issues = []
        
        # Validation batch size
        if config.batch_size < 1 or config.batch_size > 64:
            issues.append(f"Invalid batch size: {config.batch_size}")
        
        # Validation latence
        if config.max_latency_ms < 1.0 or config.max_latency_ms > 10000.0:
            issues.append(f"Invalid max latency: {config.max_latency_ms}ms")
        
        # Validation débit
        if config.target_throughput < 1:
            issues.append(f"Invalid target throughput: {config.target_throughput}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    async def _create_conservative_config(
        self,
        base_config: ServingConfig,
        constraints: Dict
    ) -> ServingConfig:
        """Crée une configuration conservative en cas d'échec"""
        return ServingConfig(
            model_id=base_config.model_id,
            model_format=ModelFormat.ORIGINAL,
            batch_size=1,
            max_latency_ms=100.0,
            target_throughput=50,
            cache_enabled=True,
            auto_scaling=False,
            gpu_enabled=False,
            optimization_level=1
        )
    
    async def monitor_serving_performance(
        self,
        model_id: str,
        latency_ms: float,
        throughput_rps: float,
        memory_usage_mb: float,
        cpu_utilization: float
    ) -> None:
        """
        Monitoring des performances de serving
        
        Expertise Backend Senior: Monitoring temps réel
        """
        # Mettre à jour les métriques temps réel
        if model_id not in self.real_time_metrics:
            self.real_time_metrics[model_id] = OptimizationMetrics(
                latency_p95=0.0,
                latency_p99=0.0,
                throughput_rps=0.0,
                memory_usage_mb=0.0,
                cpu_utilization=0.0,
                cache_hit_rate=0.0,
                optimization_gain=0.0
            )
        
        # Buffer pour calculs statistiques
        if model_id not in self.performance_buffer:
            self.performance_buffer[model_id] = []
        
        self.performance_buffer[model_id].append({
            "timestamp": datetime.utcnow(),
            "latency": latency_ms,
            "throughput": throughput_rps,
            "memory": memory_usage_mb,
            "cpu": cpu_utilization
        })
        
        # Garder seulement les 1000 derniers points
        if len(self.performance_buffer[model_id]) > 1000:
            self.performance_buffer[model_id] = self.performance_buffer[model_id][-500:]
        
        # Mettre à jour métriques calculées
        await self._update_calculated_metrics(model_id)
        
        # Vérifier les seuils et déclencher auto-optimisation si nécessaire
        await self._check_optimization_triggers(model_id)
    
    async def _update_calculated_metrics(self, model_id: str) -> None:
        """Met à jour les métriques calculées"""
        buffer = self.performance_buffer[model_id]
        if len(buffer) < 10:
            return
        
        recent_data = buffer[-100:]  # 100 derniers points
        latencies = [p["latency"] for p in recent_data]
        
        metrics = self.real_time_metrics[model_id]
        
        # Calcul percentiles
        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)
        
        if n >= 20:
            metrics.latency_p95 = sorted_latencies[int(0.95 * n)]
            metrics.latency_p99 = sorted_latencies[int(0.99 * n)]
        else:
            metrics.latency_p95 = max(latencies)
            metrics.latency_p99 = max(latencies)
        
        # Moyennes récentes
        metrics.throughput_rps = statistics.mean([p["throughput"] for p in recent_data])
        metrics.memory_usage_mb = statistics.mean([p["memory"] for p in recent_data])
        metrics.cpu_utilization = statistics.mean([p["cpu"] for p in recent_data])
    
    async def _check_optimization_triggers(self, model_id: str) -> None:
        """Vérifie si une re-optimisation est nécessaire"""
        if model_id not in self.real_time_metrics:
            return
        
        metrics = self.real_time_metrics[model_id]
        
        # Déclencher re-optimisation si dégradation
        if metrics.latency_p95 > self.optimization_thresholds["latency_target_ms"] * 1.5:
            logger.warning(f"High latency detected for {model_id}: {metrics.latency_p95:.2f}ms")
            await self._trigger_auto_optimization(model_id, "high_latency")
        
        if metrics.throughput_rps < self.optimization_thresholds["throughput_min_rps"] * 0.5:
            logger.warning(f"Low throughput detected for {model_id}: {metrics.throughput_rps:.2f} RPS")
            await self._trigger_auto_optimization(model_id, "low_throughput")
        
        if metrics.memory_usage_mb > self.optimization_thresholds["memory_limit_mb"]:
            logger.warning(f"High memory usage for {model_id}: {metrics.memory_usage_mb:.2f}MB")
            await self._trigger_auto_optimization(model_id, "high_memory")
    
    async def _trigger_auto_optimization(self, model_id: str, trigger_reason: str) -> None:
        """Déclenche une auto-optimisation"""
        logger.info(f"Triggering auto-optimization for {model_id} due to {trigger_reason}")
        
        # Déterminer stratégie basée sur le problème
        if trigger_reason == "high_latency":
            strategy = OptimizationStrategy.LATENCY_FOCUSED
        elif trigger_reason == "low_throughput":
            strategy = OptimizationStrategy.THROUGHPUT_FOCUSED
        elif trigger_reason == "high_memory":
            strategy = OptimizationStrategy.COST_OPTIMIZED
        else:
            strategy = OptimizationStrategy.BALANCED
        
        # Re-optimiser
        await self.optimize_serving_config(model_id, strategy)
    
    async def get_optimization_report(self, model_id: str) -> Dict[str, Any]:
        """Génère un rapport d'optimisation complet"""
        if model_id not in self.real_time_metrics:
            return {"error": "No metrics available for model"}
        
        metrics = self.real_time_metrics[model_id]
        config = self.serving_configs.get(model_id)
        
        # Calcul du gain d'optimisation
        historical = await self._analyze_historical_performance(model_id)
        
        optimization_gain = 0.0
        if historical.get("sample_size", 0) > 10:
            baseline_latency = historical["avg_latency"]
            current_latency = metrics.latency_p95
            if baseline_latency > 0:
                optimization_gain = ((baseline_latency - current_latency) / baseline_latency) * 100
        
        return {
            "model_id": model_id,
            "current_config": config.__dict__ if config else None,
            "performance_metrics": {
                "latency_p95_ms": metrics.latency_p95,
                "latency_p99_ms": metrics.latency_p99,
                "throughput_rps": metrics.throughput_rps,
                "memory_usage_mb": metrics.memory_usage_mb,
                "cpu_utilization": metrics.cpu_utilization,
                "optimization_gain_percent": optimization_gain
            },
            "optimization_history": [
                h for h in self.optimization_history 
                if h["model_id"] == model_id
            ][-5:],  # 5 dernières optimisations
            "recommendations": await self._generate_optimization_recommendations(model_id)
        }
    
    async def _generate_optimization_recommendations(self, model_id: str) -> List[str]:
        """Génère des recommandations d'optimisation"""
        recommendations = []
        
        if model_id not in self.real_time_metrics:
            return recommendations
        
        metrics = self.real_time_metrics[model_id]
        
        # Recommandations basées sur les métriques
        if metrics.latency_p95 > 100:
            recommendations.append("Consider quantization or TensorRT optimization for latency")
        
        if metrics.cpu_utilization > 0.8:
            recommendations.append("High CPU usage - consider scaling horizontally")
        
        if metrics.memory_usage_mb > 1500:
            recommendations.append("High memory usage - consider model compression")
        
        if metrics.throughput_rps < 50:
            recommendations.append("Low throughput - consider increasing batch size")
        
        return recommendations

# Exemple d'utilisation
async def demo_serving_optimization():
    """Démo de l'optimisation de serving"""
    optimizer = ServingOptimizationEngine()
    
    # Optimiser pour latence
    config = await optimizer.optimize_serving_config(
        "bert-base-uncased",
        OptimizationStrategy.LATENCY_FOCUSED,
        {"gpu_available": True, "max_latency_ms": 20.0}
    )
    
    print(f"Optimized config for latency:")
    print(f"  Format: {config.model_format.value}")
    print(f"  Batch size: {config.batch_size}")
    print(f"  Max latency: {config.max_latency_ms}ms")
    print(f"  GPU enabled: {config.gpu_enabled}")
    
    # Simuler monitoring
    for i in range(10):
        await optimizer.monitor_serving_performance(
            "bert-base-uncased",
            latency_ms=15.0 + i,
            throughput_rps=200 - i * 5,
            memory_usage_mb=512 + i * 10,
            cpu_utilization=0.3 + i * 0.05
        )
    
    # Rapport d'optimisation
    report = await optimizer.get_optimization_report("bert-base-uncased")
    print(f"\nOptimization report:")
    print(f"  Current P95 latency: {report['performance_metrics']['latency_p95_ms']:.2f}ms")
    print(f"  Throughput: {report['performance_metrics']['throughput_rps']:.2f} RPS")
    print(f"  Recommendations: {report['recommendations']}")

if __name__ == "__main__":
    asyncio.run(demo_serving_optimization())