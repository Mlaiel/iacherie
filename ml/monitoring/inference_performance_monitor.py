"""🚀 Inference Performance Monitor - IA Influencer Agent Platform Enterprise
=========================================================================
Module: backend/ml/monitoring/inference_performance_monitor.py
Author: Fahed Mlaiel (mlaiel@live.de) - Backend Senior + ML Engineer
=========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MONITEUR DE PERFORMANCE D'INFÉRENCE
Monitoring temps réel des performances d'inférence ML
- Latency tracking (<100ms target)
- Throughput optimization
- Resource utilization monitoring
- Creator-specific performance analytics
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import deque, defaultdict

import numpy as np
import pandas as pd
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import redis
import psutil
import GPUtil

# Configuration
logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """Types de créateurs"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

class InferenceType(Enum):
    """Types d'inférence"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    EDGE = "edge"

class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class InferenceMetrics:
    """Métriques d'inférence"""
    request_id: str
    model_id: str
    creator_type: CreatorType
    inference_type: InferenceType
    
    # Timing metrics
    start_time: datetime
    end_time: datetime
    latency_ms: float
    
    # Resource metrics
    cpu_usage_percent: float
    memory_usage_mb: float
    gpu_usage_percent: Optional[float]
    gpu_memory_mb: Optional[float]
    
    # Request metrics
    input_size_bytes: int
    output_size_bytes: int
    batch_size: int
    
    # Quality metrics
    confidence_score: float
    error_occurred: bool
    error_message: Optional[str]
    
    # Business metrics
    creator_id: Optional[str] = None
    content_type: Optional[str] = None
    success: bool = True

@dataclass
class PerformanceThresholds:
    """Seuils de performance"""
    max_latency_ms: float
    max_cpu_usage_percent: float
    max_memory_usage_mb: float
    min_confidence_score: float
    max_error_rate_percent: float

class InferencePerformanceMonitor:
    """🔧 Moniteur de performance d'inférence ML"""
    
    def __init__(self, 
                 redis_url -> None: str = "redis -> None://localhost -> None:6379/0",
                 prometheus_port -> None: int = 8090) -> None:
        self.redis_url = redis_url
        self.prometheus_port = prometheus_port
        
        # Redis client pour stockage des métriques
        self.redis_client = None
        
        # Métriques en mémoire
        self.inference_history: deque = deque(maxlen=10000)
        self.performance_stats: Dict[str, Any] = {}
        
        # Métriques par créateur
        self.creator_metrics: Dict[CreatorType, List[InferenceMetrics]] = defaultdict(list)
        
        # Configuration des seuils
        self.thresholds = {
            CreatorType.MUSICIAN: PerformanceThresholds(
                max_latency_ms=100.0,
                max_cpu_usage_percent=80.0,
                max_memory_usage_mb=2048.0,
                min_confidence_score=0.85,
                max_error_rate_percent=1.0
            ),
            CreatorType.BLOGGER: PerformanceThresholds(
                max_latency_ms=150.0,
                max_cpu_usage_percent=70.0,
                max_memory_usage_mb=1024.0,
                min_confidence_score=0.80,
                max_error_rate_percent=2.0
            ),
            CreatorType.PHOTOGRAPHER: PerformanceThresholds(
                max_latency_ms=200.0,
                max_cpu_usage_percent=90.0,
                max_memory_usage_mb=4096.0,
                min_confidence_score=0.90,
                max_error_rate_percent=0.5
            ),
            CreatorType.INFLUENCER: PerformanceThresholds(
                max_latency_ms=120.0,
                max_cpu_usage_percent=75.0,
                max_memory_usage_mb=1536.0,
                min_confidence_score=0.88,
                max_error_rate_percent=1.5
            ),
            CreatorType.COMEDIAN: PerformanceThresholds(
                max_latency_ms=180.0,
                max_cpu_usage_percent=85.0,
                max_memory_usage_mb=2048.0,
                min_confidence_score=0.82,
                max_error_rate_percent=2.5
            )
        }
        
        # Métriques Prometheus
        self._setup_prometheus_metrics()
        
        # Alertes
        self.alert_callbacks: List[callable] = []
        self.alert_history: deque = deque(maxlen=1000)
        
        # Stats globales
        self.total_requests = 0
        self.total_errors = 0
        self.total_latency_sum = 0.0
        
    def _setup_prometheus_metrics(self) -> None:
        """Configure les métriques Prometheus"""
        # Counters
        self.request_counter = Counter(
            'ml_inference_requests_total',
            'Total inference requests',
            ['model_id', 'creator_type', 'inference_type', 'status']
        )
        
        self.error_counter = Counter(
            'ml_inference_errors_total',
            'Total inference errors',
            ['model_id', 'creator_type', 'error_type']
        )
        
        # Histograms
        self.latency_histogram = Histogram(
            'ml_inference_latency_seconds',
            'Inference latency in seconds',
            ['model_id', 'creator_type'],
            buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.batch_size_histogram = Histogram(
            'ml_inference_batch_size',
            'Inference batch size',
            ['model_id', 'creator_type'],
            buckets=[1, 5, 10, 25, 50, 100, 200, 500]
        )
        
        # Gauges
        self.cpu_usage_gauge = Gauge(
            'ml_inference_cpu_usage_percent',
            'CPU usage percentage during inference'
        )
        
        self.memory_usage_gauge = Gauge(
            'ml_inference_memory_usage_mb',
            'Memory usage in MB during inference'
        )
        
        self.gpu_usage_gauge = Gauge(
            'ml_inference_gpu_usage_percent',
            'GPU usage percentage during inference'
        )
        
        self.active_models_gauge = Gauge(
            'ml_active_models',
            'Number of active models'
        )
        
        self.confidence_score_gauge = Gauge(
            'ml_inference_confidence_score',
            'Average confidence score',
            ['model_id', 'creator_type']
        )
    
    async def initialize(self) -> None:
        """Initialise le moniteur"""
        try:
            # Redis connection
            self.redis_client = redis.from_url(self.redis_url)
            
            # Démarrer le serveur Prometheus
            start_http_server(self.prometheus_port)
            
            # Démarrer les tâches de monitoring
            asyncio.create_task(self._resource_monitoring_loop())
            asyncio.create_task(self._performance_analysis_loop())
            asyncio.create_task(self._alert_processing_loop())
            
            logger.info(f"InferencePerformanceMonitor initialized on port {self.prometheus_port}")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitor: {e}")
            raise
    
    async def record_inference(self, metrics -> None: InferenceMetrics) -> None:
        """Enregistre les métriques d'une inférence"""
        try:
            # Ajouter à l'historique
            self.inference_history.append(metrics)
            self.creator_metrics[metrics.creator_type].append(metrics)
            
            # Mettre à jour les stats globales
            self.total_requests += 1
            self.total_latency_sum += metrics.latency_ms
            
            if metrics.error_occurred:
                self.total_errors += 1
            
            # Métriques Prometheus
            status = "error" if metrics.error_occurred else "success"
            
            self.request_counter.labels(
                model_id=metrics.model_id,
                creator_type=metrics.creator_type.value,
                inference_type=metrics.inference_type.value,
                status=status
            ).inc()
            
            if metrics.error_occurred:
                self.error_counter.labels(
                    model_id=metrics.model_id,
                    creator_type=metrics.creator_type.value,
                    error_type="inference_error"
                ).inc()
            
            self.latency_histogram.labels(
                model_id=metrics.model_id,
                creator_type=metrics.creator_type.value
            ).observe(metrics.latency_ms / 1000.0)
            
            self.batch_size_histogram.labels(
                model_id=metrics.model_id,
                creator_type=metrics.creator_type.value
            ).observe(metrics.batch_size)
            
            self.confidence_score_gauge.labels(
                model_id=metrics.model_id,
                creator_type=metrics.creator_type.value
            ).set(metrics.confidence_score)
            
            # Stocker dans Redis pour analyse historique
            await self._store_metrics_redis(metrics)
            
            # Vérifier les seuils et déclencher des alertes
            await self._check_thresholds(metrics)
            
        except Exception as e:
            logger.error(f"Failed to record inference metrics: {e}")
    
    async def _store_metrics_redis(self, metrics -> None: InferenceMetrics) -> None:
        """Stocke les métriques dans Redis"""
        try:
            # Clé basée sur la date pour partitioning
            date_key = metrics.start_time.strftime("%Y-%m-%d")
            redis_key = f"inference_metrics:{date_key}:{metrics.request_id}"
            
            # Sérialiser les métriques
            metrics_dict = {
                "request_id": metrics.request_id,
                "model_id": metrics.model_id,
                "creator_type": metrics.creator_type.value,
                "inference_type": metrics.inference_type.value,
                "start_time": metrics.start_time.isoformat(),
                "end_time": metrics.end_time.isoformat(),
                "latency_ms": metrics.latency_ms,
                "cpu_usage_percent": metrics.cpu_usage_percent,
                "memory_usage_mb": metrics.memory_usage_mb,
                "gpu_usage_percent": metrics.gpu_usage_percent,
                "gpu_memory_mb": metrics.gpu_memory_mb,
                "input_size_bytes": metrics.input_size_bytes,
                "output_size_bytes": metrics.output_size_bytes,
                "batch_size": metrics.batch_size,
                "confidence_score": metrics.confidence_score,
                "error_occurred": metrics.error_occurred,
                "error_message": metrics.error_message,
                "creator_id": metrics.creator_id,
                "content_type": metrics.content_type,
                "success": metrics.success
            }
            
            # Stocker avec expiration (30 jours)
            self.redis_client.setex(
                redis_key,
                30 * 24 * 60 * 60,  # 30 jours
                json.dumps(metrics_dict)
            )
            
            # Ajouter à l'index par modèle
            model_index_key = f"model_metrics:{metrics.model_id}"
            self.redis_client.zadd(
                model_index_key,
                {redis_key: time.time()}
            )
            
            # Ajouter à l'index par créateur
            creator_index_key = f"creator_metrics:{metrics.creator_type.value}"
            self.redis_client.zadd(
                creator_index_key,
                {redis_key: time.time()}
            )
            
        except Exception as e:
            logger.error(f"Failed to store metrics in Redis: {e}")
    
    async def _check_thresholds(self, metrics -> None: InferenceMetrics) -> None:
        """Vérifie les seuils de performance et déclenche des alertes"""
        try:
            thresholds = self.thresholds.get(metrics.creator_type)
            if not thresholds:
                return
            
            alerts = []
            
            # Vérifier la latence
            if metrics.latency_ms > thresholds.max_latency_ms:
                alerts.append({
                    "level": AlertLevel.WARNING if metrics.latency_ms < thresholds.max_latency_ms * 1.5 else AlertLevel.CRITICAL,
                    "message": f"High latency: {metrics.latency_ms:.2f}ms > {thresholds.max_latency_ms}ms",
                    "metric": "latency",
                    "value": metrics.latency_ms,
                    "threshold": thresholds.max_latency_ms,
                    "model_id": metrics.model_id,
                    "creator_type": metrics.creator_type.value
                })
            
            # Vérifier l'utilisation CPU
            if metrics.cpu_usage_percent > thresholds.max_cpu_usage_percent:
                alerts.append({
                    "level": AlertLevel.WARNING,
                    "message": f"High CPU usage: {metrics.cpu_usage_percent:.1f}% > {thresholds.max_cpu_usage_percent}%",
                    "metric": "cpu_usage",
                    "value": metrics.cpu_usage_percent,
                    "threshold": thresholds.max_cpu_usage_percent,
                    "model_id": metrics.model_id,
                    "creator_type": metrics.creator_type.value
                })
            
            # Vérifier l'utilisation mémoire
            if metrics.memory_usage_mb > thresholds.max_memory_usage_mb:
                alerts.append({
                    "level": AlertLevel.CRITICAL,
                    "message": f"High memory usage: {metrics.memory_usage_mb:.1f}MB > {thresholds.max_memory_usage_mb}MB",
                    "metric": "memory_usage",
                    "value": metrics.memory_usage_mb,
                    "threshold": thresholds.max_memory_usage_mb,
                    "model_id": metrics.model_id,
                    "creator_type": metrics.creator_type.value
                })
            
            # Vérifier la confidence
            if metrics.confidence_score < thresholds.min_confidence_score:
                alerts.append({
                    "level": AlertLevel.WARNING,
                    "message": f"Low confidence: {metrics.confidence_score:.3f} < {thresholds.min_confidence_score}",
                    "metric": "confidence",
                    "value": metrics.confidence_score,
                    "threshold": thresholds.min_confidence_score,
                    "model_id": metrics.model_id,
                    "creator_type": metrics.creator_type.value
                })
            
            # Déclencher les alertes
            for alert in alerts:
                await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Failed to check thresholds: {e}")
    
    async def _trigger_alert(self, alert -> None: Dict[str, Any]) -> None:
        """Déclenche une alerte"""
        try:
            alert["timestamp"] = datetime.utcnow().isoformat()
            alert["alert_id"] = str(uuid.uuid4())
            
            # Ajouter à l'historique
            self.alert_history.append(alert)
            
            # Appeler les callbacks d'alerte
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
            
            # Log l'alerte
            level_map = {
                AlertLevel.INFO: logger.info,
                AlertLevel.WARNING: logger.warning,
                AlertLevel.CRITICAL: logger.error,
                AlertLevel.EMERGENCY: logger.critical
            }
            
            log_func = level_map.get(alert["level"], logger.info)
            log_func(f"ALERT: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    async def _resource_monitoring_loop(self) -> None:
        """Boucle de monitoring des ressources système"""
        while True:
            try:
                # CPU et mémoire système
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                self.cpu_usage_gauge.set(cpu_percent)
                self.memory_usage_gauge.set(memory.used / 1024 / 1024)  # MB
                
                # GPU si disponible
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # Premier GPU
                        self.gpu_usage_gauge.set(gpu.load * 100)
                except:
                    pass  # GPU monitoring optionnel
                
                await asyncio.sleep(5)  # Monitoring toutes les 5 secondes
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _performance_analysis_loop(self) -> None:
        """Boucle d'analyse des performances"""
        while True:
            try:
                await asyncio.sleep(60)  # Analyse chaque minute
                
                # Calculer les stats de performance
                await self._calculate_performance_stats()
                
            except Exception as e:
                logger.error(f"Performance analysis error: {e}")
    
    async def _alert_processing_loop(self) -> None:
        """Boucle de traitement des alertes"""
        while True:
            try:
                await asyncio.sleep(30)  # Vérifier les alertes toutes les 30 secondes
                
                # Vérifier les taux d'erreur globaux
                await self._check_global_error_rates()
                
            except Exception as e:
                logger.error(f"Alert processing error: {e}")
    
    async def _calculate_performance_stats(self) -> None:
        """Calcule les statistiques de performance"""
        try:
            if not self.inference_history:
                return
            
            # Stats globales
            recent_metrics = list(self.inference_history)[-100:]  # 100 dernières requêtes
            
            latencies = [m.latency_ms for m in recent_metrics]
            cpu_usages = [m.cpu_usage_percent for m in recent_metrics]
            memory_usages = [m.memory_usage_mb for m in recent_metrics]
            confidence_scores = [m.confidence_score for m in recent_metrics]
            
            self.performance_stats = {
                "global": {
                    "avg_latency_ms": statistics.mean(latencies),
                    "p95_latency_ms": np.percentile(latencies, 95),
                    "p99_latency_ms": np.percentile(latencies, 99),
                    "avg_cpu_usage": statistics.mean(cpu_usages),
                    "avg_memory_usage": statistics.mean(memory_usages),
                    "avg_confidence": statistics.mean(confidence_scores),
                    "error_rate": sum(1 for m in recent_metrics if m.error_occurred) / len(recent_metrics) * 100,
                    "throughput_rps": len(recent_metrics) / 60  # Approximation
                }
            }
            
            # Stats par créateur
            for creator_type in CreatorType:
                creator_metrics = [m for m in recent_metrics if m.creator_type == creator_type]
                
                if creator_metrics:
                    creator_latencies = [m.latency_ms for m in creator_metrics]
                    creator_confidences = [m.confidence_score for m in creator_metrics]
                    
                    self.performance_stats[creator_type.value] = {
                        "avg_latency_ms": statistics.mean(creator_latencies),
                        "p95_latency_ms": np.percentile(creator_latencies, 95),
                        "avg_confidence": statistics.mean(creator_confidences),
                        "error_rate": sum(1 for m in creator_metrics if m.error_occurred) / len(creator_metrics) * 100,
                        "request_count": len(creator_metrics)
                    }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance stats: {e}")
    
    async def _check_global_error_rates(self) -> None:
        """Vérifie les taux d'erreur globaux"""
        try:
            if not self.inference_history:
                return
            
            # Dernière heure
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_metrics = [
                m for m in self.inference_history 
                if m.start_time > one_hour_ago
            ]
            
            if len(recent_metrics) < 10:  # Pas assez de données
                return
            
            error_rate = sum(1 for m in recent_metrics if m.error_occurred) / len(recent_metrics) * 100
            
            # Alertes de taux d'erreur
            if error_rate > 10:  # 10% d'erreurs
                await self._trigger_alert({
                    "level": AlertLevel.CRITICAL,
                    "message": f"High global error rate: {error_rate:.1f}%",
                    "metric": "global_error_rate",
                    "value": error_rate,
                    "threshold": 10,
                    "timeframe": "1h"
                })
            elif error_rate > 5:  # 5% d'erreurs
                await self._trigger_alert({
                    "level": AlertLevel.WARNING,
                    "message": f"Elevated global error rate: {error_rate:.1f}%",
                    "metric": "global_error_rate",
                    "value": error_rate,
                    "threshold": 5,
                    "timeframe": "1h"
                })
            
        except Exception as e:
            logger.error(f"Failed to check global error rates: {e}")
    
    def add_alert_callback(self, callback -> None: callable) -> None:
        """Ajoute un callback d'alerte"""
        self.alert_callbacks.append(callback)
    
    async def get_performance_report(self, 
                                   creator_type: Optional[CreatorType] = None,
                                   time_range_hours: int = 24) -> Dict[str, Any]:
        """Génère un rapport de performance"""
        try:
            # Filtrer par période
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
            metrics = [
                m for m in self.inference_history 
                if m.start_time > cutoff_time
            ]
            
            if creator_type:
                metrics = [m for m in metrics if m.creator_type == creator_type]
            
            if not metrics:
                return {"error": "No data available for the specified criteria"}
            
            # Calculer les statistiques
            latencies = [m.latency_ms for m in metrics]
            cpu_usages = [m.cpu_usage_percent for m in metrics]
            memory_usages = [m.memory_usage_mb for m in metrics]
            confidence_scores = [m.confidence_score for m in metrics]
            
            errors = [m for m in metrics if m.error_occurred]
            successes = [m for m in metrics if not m.error_occurred]
            
            # Analyse par modèle
            models_stats = defaultdict(list)
            for metric in metrics:
                models_stats[metric.model_id].append(metric)
            
            model_performance = {}
            for model_id, model_metrics in models_stats.items():
                model_latencies = [m.latency_ms for m in model_metrics]
                model_performance[model_id] = {
                    "request_count": len(model_metrics),
                    "avg_latency_ms": statistics.mean(model_latencies),
                    "p95_latency_ms": np.percentile(model_latencies, 95),
                    "error_rate": sum(1 for m in model_metrics if m.error_occurred) / len(model_metrics) * 100
                }
            
            report = {
                "summary": {
                    "time_range_hours": time_range_hours,
                    "creator_type": creator_type.value if creator_type else "all",
                    "total_requests": len(metrics),
                    "total_errors": len(errors),
                    "error_rate_percent": len(errors) / len(metrics) * 100,
                    "avg_latency_ms": statistics.mean(latencies),
                    "median_latency_ms": statistics.median(latencies),
                    "p95_latency_ms": np.percentile(latencies, 95),
                    "p99_latency_ms": np.percentile(latencies, 99),
                    "max_latency_ms": max(latencies),
                    "avg_cpu_usage": statistics.mean(cpu_usages),
                    "avg_memory_usage_mb": statistics.mean(memory_usages),
                    "avg_confidence_score": statistics.mean(confidence_scores),
                    "throughput_rps": len(metrics) / (time_range_hours * 3600)
                },
                "model_performance": model_performance,
                "performance_stats": self.performance_stats,
                "recent_alerts": list(self.alert_history)[-20:]  # 20 dernières alertes
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {"error": str(e)}

# Usage example avec création de métriques simulées
async def demo_performance_monitor() -> None:
    """Démo du moniteur de performance"""
    monitor = InferencePerformanceMonitor()
    await monitor.initialize()
    
    # Ajouter un callback d'alerte
    async def alert_handler(alert) -> None:
        print(f"🚨 ALERT: {alert['message']}")
    
    monitor.add_alert_callback(alert_handler)
    
    # Simuler des métriques d'inférence
    for i in range(10):
        metrics = InferenceMetrics(
            request_id=f"req-{i}",
            model_id="musician-classifier",
            creator_type=CreatorType.MUSICIAN,
            inference_type=InferenceType.REAL_TIME,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(milliseconds=85),
            latency_ms=85.0 + i * 10,  # Latence croissante pour tester les alertes
            cpu_usage_percent=45.0 + i * 5,
            memory_usage_mb=512.0 + i * 100,
            gpu_usage_percent=60.0,
            gpu_memory_mb=1024.0,
            input_size_bytes=1024,
            output_size_bytes=256,
            batch_size=1,
            confidence_score=0.92 - i * 0.02,  # Confidence décroissante
            error_occurred=i > 8,  # Erreur sur les dernières requêtes
            error_message="Timeout" if i > 8 else None,
            creator_id="creator-123",
            content_type="audio"
        )
        
        await monitor.record_inference(metrics)
        await asyncio.sleep(0.1)
    
    # Attendre un peu pour que les analyses se fassent
    await asyncio.sleep(2)
    
    # Générer un rapport
    report = await monitor.get_performance_report(
        creator_type=CreatorType.MUSICIAN,
        time_range_hours=1
    )
    
    print("✅ Performance Report:")
    print(f"  Total requests: {report['summary']['total_requests']}")
    print(f"  Average latency: {report['summary']['avg_latency_ms']:.2f}ms")
    print(f"  Error rate: {report['summary']['error_rate_percent']:.1f}%")
    print(f"  Throughput: {report['summary']['throughput_rps']:.2f} RPS")

if __name__ == "__main__":
    asyncio.run(demo_performance_monitor())