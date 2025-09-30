"""
🚀 Model Inference Performance Monitor - Enterprise AI/ML Performance Hub
========================================================================

Monitoring performance inférence modèles IA Creator Economy ultra-avancé.
Métriques latence temps réel, tracking throughput par type créateur,
monitoring utilisation ressources GPU/CPU, analyse performance modalité.

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

Architecture: monitoring/ai_ml_performance_hub/model_inference_performance_monitor.py
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import psutil
import threading
import json
from concurrent.futures import ThreadPoolExecutor
import uuid


class CreatorTier(Enum):
    """Niveaux créateurs Ainflue"""
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class ContentModality(Enum):
    """Modalités contenu créateur"""
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    IMAGE = "image"
    MULTIMODAL = "multimodal"


class InferenceType(Enum):
    """Types inférence IA"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    SCHEDULED = "scheduled"


@dataclass
class InferenceMetrics:
    """Métriques inférence détaillées"""
    inference_id: str
    model_id: str
    creator_id: str
    creator_tier: CreatorTier
    content_modality: ContentModality
    inference_type: InferenceType
    start_time: float
    end_time: float
    latency_ms: float
    preprocessing_time_ms: float
    model_execution_time_ms: float
    postprocessing_time_ms: float
    memory_peak_mb: float
    cpu_usage_percent: float
    gpu_usage_percent: Optional[float]
    gpu_memory_mb: Optional[float]
    input_size_bytes: int
    output_size_bytes: int
    prediction_confidence: float
    success: bool
    error_message: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ThroughputMetrics:
    """Métriques débit système"""
    requests_per_second: float
    concurrent_requests: int
    queue_length: int
    average_response_time: float
    success_rate: float
    error_rate: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourceUtilization:
    """Utilisation ressources système"""
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    gpu_usage_percent: Optional[float]
    gpu_memory_mb: Optional[float]
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ModelInferencePerformanceMonitor:
    """Monitoring performance inférence modèles IA Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Storage for metrics
        self.inference_metrics: deque = deque(maxlen=10000)
        self.throughput_history: deque = deque(maxlen=1000)
        self.resource_history: deque = deque(maxlen=1000)
        
        # Real-time tracking
        self.active_inferences: Dict[str, InferenceMetrics] = {}
        self.model_stats: Dict[str, Dict] = defaultdict(dict)
        self.creator_stats: Dict[str, Dict] = defaultdict(dict)
        
        # Performance thresholds per creator tier
        self.latency_thresholds = {
            CreatorTier.FREE: 2000,         # 2s for free tier
            CreatorTier.PREMIUM: 1000,      # 1s for premium
            CreatorTier.PROFESSIONAL: 500,  # 500ms for professional
            CreatorTier.ENTERPRISE: 200     # 200ms for enterprise
        }
        
        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # System monitoring
        self._last_disk_io = psutil.disk_io_counters()
        self._last_network_io = psutil.net_io_counters()
        self._last_timestamp = time.time()
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger(f"inference_monitor_{id(self)}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation monitoring inférence"""
        self.logger.info("🚀 Initialisation Model Inference Performance Monitor...")
        
        # Démarrer monitoring système
        await self._start_system_monitoring()
        
        # Initialiser métriques baseline
        await self._initialize_baseline_metrics()
        
        self.logger.info("✅ Model Inference Performance Monitor initialisé")
    
    async def _start_system_monitoring(self):
        """Démarrage monitoring système continu"""
        self.monitoring_active = True
        
        def monitor_system():
            while self.monitoring_active:
                try:
                    self._collect_system_metrics()
                    time.sleep(5)  # Collect every 5 seconds
                except Exception as e:
                    self.logger.error(f"System monitoring error: {e}")
        
        self.monitoring_thread = threading.Thread(target=monitor_system, daemon=True)
        self.monitoring_thread.start()
    
    def _collect_system_metrics(self):
        """Collecte métriques système"""
        try:
            # CPU et mémoire
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # GPU metrics (simulated - would use nvidia-ml-py in production)
            gpu_usage = None
            gpu_memory = None
            try:
                # Placeholder for GPU monitoring
                # In production: use nvidia-ml-py or similar
                gpu_usage = 0.0
                gpu_memory = 0.0
            except:
                pass
            
            # Disk I/O
            current_disk_io = psutil.disk_io_counters()
            current_time = time.time()
            time_delta = current_time - self._last_timestamp
            
            disk_read_mb = 0
            disk_write_mb = 0
            if self._last_disk_io and time_delta > 0:
                disk_read_mb = (current_disk_io.read_bytes - self._last_disk_io.read_bytes) / (1024*1024) / time_delta
                disk_write_mb = (current_disk_io.write_bytes - self._last_disk_io.write_bytes) / (1024*1024) / time_delta
            
            # Network I/O
            current_network_io = psutil.net_io_counters()
            network_sent_mb = 0
            network_recv_mb = 0
            if self._last_network_io and time_delta > 0:
                network_sent_mb = (current_network_io.bytes_sent - self._last_network_io.bytes_sent) / (1024*1024) / time_delta
                network_recv_mb = (current_network_io.bytes_recv - self._last_network_io.bytes_recv) / (1024*1024) / time_delta
            
            # Créer métrique ressource
            resource_metric = ResourceUtilization(
                cpu_usage_percent=cpu_percent,
                memory_usage_mb=memory.used / (1024*1024),
                memory_usage_percent=memory.percent,
                gpu_usage_percent=gpu_usage,
                gpu_memory_mb=gpu_memory,
                disk_io_read_mb=disk_read_mb,
                disk_io_write_mb=disk_write_mb,
                network_io_sent_mb=network_sent_mb,
                network_io_recv_mb=network_recv_mb
            )
            
            self.resource_history.append(resource_metric)
            
            # Update for next iteration
            self._last_disk_io = current_disk_io
            self._last_network_io = current_network_io
            self._last_timestamp = current_time
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    async def _initialize_baseline_metrics(self):
        """Initialisation métriques baseline"""
        # Create baseline metrics for different creator tiers and content types
        for tier in CreatorTier:
            for modality in ContentModality:
                key = f"{tier.value}_{modality.value}"
                self.model_stats[key] = {
                    'total_inferences': 0,
                    'avg_latency': 0.0,
                    'success_rate': 100.0,
                    'avg_confidence': 0.9,
                    'p95_latency': 0.0,
                    'p99_latency': 0.0
                }
    
    async def start_inference_tracking(
        self,
        model_id: str,
        creator_id: str,
        creator_tier: CreatorTier,
        content_modality: ContentModality,
        inference_type: InferenceType,
        input_size_bytes: int
    ) -> str:
        """Démarrage tracking inférence"""
        inference_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Metrics baseline
        inference_metric = InferenceMetrics(
            inference_id=inference_id,
            model_id=model_id,
            creator_id=creator_id,
            creator_tier=creator_tier,
            content_modality=content_modality,
            inference_type=inference_type,
            start_time=start_time,
            end_time=0.0,
            latency_ms=0.0,
            preprocessing_time_ms=0.0,
            model_execution_time_ms=0.0,
            postprocessing_time_ms=0.0,
            memory_peak_mb=0.0,
            cpu_usage_percent=0.0,
            gpu_usage_percent=None,
            gpu_memory_mb=None,
            input_size_bytes=input_size_bytes,
            output_size_bytes=0,
            prediction_confidence=0.0,
            success=True,
            error_message=None
        )
        
        self.active_inferences[inference_id] = inference_metric
        
        self.logger.debug(f"Started tracking inference {inference_id} for model {model_id}")
        return inference_id
    
    async def update_inference_stage(
        self,
        inference_id: str,
        stage: str,
        duration_ms: float,
        memory_usage_mb: Optional[float] = None
    ):
        """Mise à jour étape inférence"""
        if inference_id not in self.active_inferences:
            self.logger.warning(f"Inference {inference_id} not found for stage update")
            return
        
        metric = self.active_inferences[inference_id]
        
        if stage == "preprocessing":
            metric.preprocessing_time_ms = duration_ms
        elif stage == "model_execution":
            metric.model_execution_time_ms = duration_ms
        elif stage == "postprocessing":
            metric.postprocessing_time_ms = duration_ms
        
        if memory_usage_mb:
            metric.memory_peak_mb = max(metric.memory_peak_mb, memory_usage_mb)
        
        # Update CPU/GPU usage from current system metrics
        if self.resource_history:
            latest_resource = self.resource_history[-1]
            metric.cpu_usage_percent = latest_resource.cpu_usage_percent
            metric.gpu_usage_percent = latest_resource.gpu_usage_percent
            metric.gpu_memory_mb = latest_resource.gpu_memory_mb
    
    async def complete_inference_tracking(
        self,
        inference_id: str,
        output_size_bytes: int,
        prediction_confidence: float,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Finalisation tracking inférence"""
        if inference_id not in self.active_inferences:
            self.logger.warning(f"Inference {inference_id} not found for completion")
            return
        
        metric = self.active_inferences[inference_id]
        end_time = time.time()
        
        # Finaliser métriques
        metric.end_time = end_time
        metric.latency_ms = (end_time - metric.start_time) * 1000
        metric.output_size_bytes = output_size_bytes
        metric.prediction_confidence = prediction_confidence
        metric.success = success
        metric.error_message = error_message
        
        # Stocker métrique complète
        self.inference_metrics.append(metric)
        
        # Supprimer du tracking actif
        del self.active_inferences[inference_id]
        
        # Mettre à jour statistiques
        await self._update_model_statistics(metric)
        await self._update_creator_statistics(metric)
        
        # Vérifier violations SLA
        await self._check_sla_violations(metric)
        
        self.logger.debug(
            f"Completed inference {inference_id}: {metric.latency_ms:.1f}ms, "
            f"success={success}, confidence={prediction_confidence:.3f}"
        )
    
    async def _update_model_statistics(self, metric: InferenceMetrics):
        """Mise à jour statistiques modèle"""
        key = f"{metric.creator_tier.value}_{metric.content_modality.value}"
        stats = self.model_stats[key]
        
        # Update counters
        stats['total_inferences'] += 1
        
        # Calculate rolling averages
        alpha = 0.1  # Exponential moving average factor
        if stats['avg_latency'] == 0:
            stats['avg_latency'] = metric.latency_ms
        else:
            stats['avg_latency'] = alpha * metric.latency_ms + (1 - alpha) * stats['avg_latency']
        
        if metric.success:
            if stats['avg_confidence'] == 0:
                stats['avg_confidence'] = metric.prediction_confidence
            else:
                stats['avg_confidence'] = alpha * metric.prediction_confidence + (1 - alpha) * stats['avg_confidence']
        
        # Update success rate
        recent_metrics = [m for m in self.inference_metrics 
                         if m.creator_tier == metric.creator_tier 
                         and m.content_modality == metric.content_modality
                         and (datetime.utcnow() - m.timestamp).total_seconds() < 3600]  # Last hour
        
        if recent_metrics:
            stats['success_rate'] = (sum(1 for m in recent_metrics if m.success) / len(recent_metrics)) * 100
            
            # Calculate percentiles
            latencies = [m.latency_ms for m in recent_metrics if m.success]
            if latencies:
                latencies.sort()
                stats['p95_latency'] = latencies[int(0.95 * len(latencies))]
                stats['p99_latency'] = latencies[int(0.99 * len(latencies))]
    
    async def _update_creator_statistics(self, metric: InferenceMetrics):
        """Mise à jour statistiques créateur"""
        creator_stats = self.creator_stats[metric.creator_id]
        
        if 'total_inferences' not in creator_stats:
            creator_stats['total_inferences'] = 0
            creator_stats['avg_latency'] = 0.0
            creator_stats['success_rate'] = 100.0
            creator_stats['preferred_modality'] = metric.content_modality.value
        
        creator_stats['total_inferences'] += 1
        
        # Rolling average latency
        alpha = 0.1
        if creator_stats['avg_latency'] == 0:
            creator_stats['avg_latency'] = metric.latency_ms
        else:
            creator_stats['avg_latency'] = alpha * metric.latency_ms + (1 - alpha) * creator_stats['avg_latency']
        
        # Update preferred modality (most used)
        creator_metrics = [m for m in self.inference_metrics if m.creator_id == metric.creator_id]
        if creator_metrics:
            modality_counts = defaultdict(int)
            for m in creator_metrics[-100:]:  # Last 100 inferences
                modality_counts[m.content_modality.value] += 1
            creator_stats['preferred_modality'] = max(modality_counts, key=modality_counts.get)
    
    async def _check_sla_violations(self, metric: InferenceMetrics):
        """Vérification violations SLA"""
        threshold = self.latency_thresholds[metric.creator_tier]
        
        if metric.latency_ms > threshold:
            self.logger.warning(
                f"🚨 SLA Violation: {metric.model_id} for {metric.creator_tier.value} creator "
                f"({metric.latency_ms:.1f}ms > {threshold}ms)"
            )
            
            # In production, would trigger alerts/notifications
            await self._handle_sla_violation(metric, threshold)
    
    async def _handle_sla_violation(self, metric: InferenceMetrics, threshold: float):
        """Gestion violation SLA"""
        violation_data = {
            'inference_id': metric.inference_id,
            'model_id': metric.model_id,
            'creator_id': metric.creator_id,
            'creator_tier': metric.creator_tier.value,
            'actual_latency': metric.latency_ms,
            'threshold': threshold,
            'severity': 'high' if metric.latency_ms > threshold * 2 else 'medium',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log violation for monitoring systems
        self.logger.error(f"SLA Violation: {json.dumps(violation_data)}")
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Métriques temps réel"""
        current_time = datetime.utcnow()
        recent_window = timedelta(minutes=5)
        
        # Recent inferences
        recent_inferences = [
            m for m in self.inference_metrics 
            if (current_time - m.timestamp) <= recent_window
        ]
        
        # Current system metrics
        current_resource = self.resource_history[-1] if self.resource_history else None
        
        # Calculate throughput
        throughput_rps = len(recent_inferences) / (recent_window.total_seconds()) if recent_inferences else 0
        
        # Active inferences count
        active_count = len(self.active_inferences)
        
        # Success rate
        success_rate = (sum(1 for m in recent_inferences if m.success) / len(recent_inferences) * 100) if recent_inferences else 100
        
        # Average latency by tier
        tier_latencies = {}
        for tier in CreatorTier:
            tier_metrics = [m for m in recent_inferences if m.creator_tier == tier and m.success]
            if tier_metrics:
                tier_latencies[tier.value] = statistics.mean([m.latency_ms for m in tier_metrics])
            else:
                tier_latencies[tier.value] = 0
        
        return {
            'timestamp': current_time.isoformat(),
            'throughput': {
                'requests_per_second': throughput_rps,
                'active_inferences': active_count,
                'total_inferences_5min': len(recent_inferences)
            },
            'performance': {
                'success_rate_percent': success_rate,
                'average_latency_by_tier': tier_latencies,
                'total_models_active': len(set(m.model_id for m in recent_inferences))
            },
            'system_resources': {
                'cpu_usage_percent': current_resource.cpu_usage_percent if current_resource else 0,
                'memory_usage_percent': current_resource.memory_usage_percent if current_resource else 0,
                'gpu_usage_percent': current_resource.gpu_usage_percent if current_resource else None,
                'gpu_memory_mb': current_resource.gpu_memory_mb if current_resource else None
            }
        }
    
    async def get_model_performance_analysis(self, model_id: str, hours: int = 24) -> Dict[str, Any]:
        """Analyse performance modèle détaillée"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        model_metrics = [
            m for m in self.inference_metrics 
            if m.model_id == model_id and m.timestamp >= cutoff_time
        ]
        
        if not model_metrics:
            return {'model_id': model_id, 'error': 'No metrics found'}
        
        # Performance par modalité
        modality_performance = {}
        for modality in ContentModality:
            modality_metrics = [m for m in model_metrics if m.content_modality == modality and m.success]
            if modality_metrics:
                latencies = [m.latency_ms for m in modality_metrics]
                modality_performance[modality.value] = {
                    'total_inferences': len(modality_metrics),
                    'avg_latency_ms': statistics.mean(latencies),
                    'p50_latency_ms': statistics.median(latencies),
                    'p95_latency_ms': latencies[int(0.95 * len(latencies))],
                    'p99_latency_ms': latencies[int(0.99 * len(latencies))],
                    'avg_confidence': statistics.mean([m.prediction_confidence for m in modality_metrics])
                }
        
        # Performance par tier créateur
        tier_performance = {}
        for tier in CreatorTier:
            tier_metrics = [m for m in model_metrics if m.creator_tier == tier and m.success]
            if tier_metrics:
                latencies = [m.latency_ms for m in tier_metrics]
                tier_performance[tier.value] = {
                    'total_inferences': len(tier_metrics),
                    'avg_latency_ms': statistics.mean(latencies),
                    'sla_violations': len([m for m in tier_metrics if m.latency_ms > self.latency_thresholds[tier]]),
                    'success_rate_percent': (len(tier_metrics) / len([m for m in model_metrics if m.creator_tier == tier])) * 100
                }
        
        # Performance globale
        successful_metrics = [m for m in model_metrics if m.success]
        all_latencies = [m.latency_ms for m in successful_metrics]
        
        return {
            'model_id': model_id,
            'analysis_period_hours': hours,
            'total_inferences': len(model_metrics),
            'success_rate_percent': (len(successful_metrics) / len(model_metrics)) * 100,
            'overall_performance': {
                'avg_latency_ms': statistics.mean(all_latencies) if all_latencies else 0,
                'median_latency_ms': statistics.median(all_latencies) if all_latencies else 0,
                'p95_latency_ms': all_latencies[int(0.95 * len(all_latencies))] if all_latencies else 0,
                'p99_latency_ms': all_latencies[int(0.99 * len(all_latencies))] if all_latencies else 0,
                'avg_confidence': statistics.mean([m.prediction_confidence for m in successful_metrics]) if successful_metrics else 0
            },
            'performance_by_modality': modality_performance,
            'performance_by_creator_tier': tier_performance,
            'resource_utilization': {
                'avg_memory_peak_mb': statistics.mean([m.memory_peak_mb for m in successful_metrics]) if successful_metrics else 0,
                'avg_cpu_usage_percent': statistics.mean([m.cpu_usage_percent for m in successful_metrics]) if successful_metrics else 0
            }
        }
    
    async def get_creator_usage_insights(self, creator_id: str) -> Dict[str, Any]:
        """Insights utilisation créateur"""
        creator_metrics = [m for m in self.inference_metrics if m.creator_id == creator_id]
        
        if not creator_metrics:
            return {'creator_id': creator_id, 'error': 'No usage data found'}
        
        # Modalities distribution
        modality_usage = defaultdict(int)
        for m in creator_metrics:
            modality_usage[m.content_modality.value] += 1
        
        # Performance par modèle
        model_usage = defaultdict(list)
        for m in creator_metrics:
            model_usage[m.model_id].append(m)
        
        model_performance = {}
        for model_id, metrics in model_usage.items():
            successful = [m for m in metrics if m.success]
            if successful:
                model_performance[model_id] = {
                    'total_uses': len(metrics),
                    'success_rate_percent': (len(successful) / len(metrics)) * 100,
                    'avg_latency_ms': statistics.mean([m.latency_ms for m in successful]),
                    'avg_confidence': statistics.mean([m.prediction_confidence for m in successful])
                }
        
        return {
            'creator_id': creator_id,
            'creator_tier': creator_metrics[-1].creator_tier.value,
            'total_inferences': len(creator_metrics),
            'modality_distribution': dict(modality_usage),
            'preferred_modality': max(modality_usage, key=modality_usage.get),
            'model_performance': model_performance,
            'overall_performance': {
                'avg_latency_ms': statistics.mean([m.latency_ms for m in creator_metrics if m.success]),
                'success_rate_percent': (sum(1 for m in creator_metrics if m.success) / len(creator_metrics)) * 100
            }
        }
    
    async def shutdown(self):
        """Arrêt propre monitoring"""
        self.logger.info("⏹️ Arrêt Model Inference Performance Monitor...")
        
        # Arrêter monitoring système
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        # Arrêter executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("✅ Model Inference Performance Monitor arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_inference_monitor():
        config = {"debug": True}
        monitor = ModelInferencePerformanceMonitor(config)
        
        await monitor.initialize()
        
        # Test inference tracking
        inference_id = await monitor.start_inference_tracking(
            model_id="content_classifier_v1",
            creator_id="creator_123",
            creator_tier=CreatorTier.PREMIUM,
            content_modality=ContentModality.VIDEO,
            inference_type=InferenceType.REAL_TIME,
            input_size_bytes=1024000
        )
        
        # Simulate processing stages
        await monitor.update_inference_stage(inference_id, "preprocessing", 50.0, 100.0)
        await monitor.update_inference_stage(inference_id, "model_execution", 200.0, 150.0)
        await monitor.update_inference_stage(inference_id, "postprocessing", 30.0)
        
        # Complete inference
        await monitor.complete_inference_tracking(
            inference_id=inference_id,
            output_size_bytes=512000,
            prediction_confidence=0.92,
            success=True
        )
        
        # Get metrics
        real_time_metrics = await monitor.get_real_time_metrics()
        print(f"Real-time metrics: {json.dumps(real_time_metrics, indent=2)}")
        
        print("✅ Model Inference Performance Monitor test passed")
        await monitor.shutdown()
    
    asyncio.run(test_inference_monitor())