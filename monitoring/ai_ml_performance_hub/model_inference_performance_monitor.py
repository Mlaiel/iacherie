"""
🚀 Model Inference Performance Monitor - Enterprise AI/ML Performance
====================================================================

Système de monitoring ultra-avancé pour surveillance performance inférence modèles IA.
Surveillance temps réel, optimisation latence et tracking utilisation ressources Creator Economy.

Fonctionnalités:
- Monitoring latence inférence temps réel par type créateur
- Tracking throughput adaptatif selon tier Creator
- Surveillance utilisation ressources GPU/CPU/Mémoire
- Analyse performance par modalité (audio/video/texte/image)
- Différenciation performance selon Creator tier (Free/Pro/Enterprise)
- Détection goulots étranglement automatique
- Optimisation allocation ressources dynamique
- Analytics ROI performance par Creator

Architecture: monitoring/ai_ml_performance_hub/model_inference_performance_monitor.py
Responsabilité: Performance inférence, optimisation latence, resource tracking

© 2025 Fahed Mlaiel - Code propriétaire ultra-avancé production-ready
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
import threading
from collections import defaultdict, deque
import weakref


class CreatorTier(Enum):
    """Niveaux créateurs Ainflue"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class ContentModality(Enum):
    """Modalités contenu Creator Economy"""
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    IMAGE = "image"
    MIXED_MEDIA = "mixed_media"


class InferenceStatus(Enum):
    """États inférence modèle"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class InferenceRequest:
    """Requête inférence modèle"""
    request_id: str
    model_id: str
    creator_id: str
    creator_tier: CreatorTier
    content_modality: ContentModality
    input_size: int  # bytes
    priority: int  # 1-10, 10 highest
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceMetrics:
    """Métriques performance inférence"""
    request_id: str
    model_id: str
    creator_id: str
    creator_tier: CreatorTier
    content_modality: ContentModality
    
    # Performance metrics
    latency_ms: float
    throughput_rps: float
    queue_wait_time_ms: float
    processing_time_ms: float
    
    # Resource utilization
    cpu_usage_percent: float
    memory_usage_mb: float
    gpu_usage_percent: float
    gpu_memory_mb: float
    
    # Quality metrics
    confidence_score: float
    accuracy_estimate: float
    
    # Business metrics
    cost_estimate: float
    revenue_attribution: float
    
    # Status
    status: InferenceStatus
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ModelPerformanceStats:
    """Statistiques performance modèle"""
    model_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    
    # Latency statistics
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    
    # Throughput statistics
    avg_throughput_rps: float
    peak_throughput_rps: float
    
    # Resource utilization
    avg_cpu_usage: float
    avg_memory_usage: float
    avg_gpu_usage: float
    
    # Quality metrics
    avg_confidence: float
    avg_accuracy: float
    
    # Business metrics
    total_cost: float
    total_revenue: float
    roi_ratio: float
    
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ModelInferencePerformanceMonitor:
    """Monitoring performance inférence modèles IA Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Active monitoring
        self.active_requests: Dict[str, InferenceRequest] = {}
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.model_stats: Dict[str, ModelPerformanceStats] = {}
        
        # Performance tracking
        self.latency_buckets = defaultdict(list)  # By model_id
        self.throughput_tracker = defaultdict(deque)  # By model_id, maxlen=100
        self.resource_usage_tracker = defaultdict(deque)  # By model_id, maxlen=100
        
        # Creator tier performance tracking
        self.tier_performance: Dict[CreatorTier, Dict[str, List[float]]] = {
            tier: defaultdict(list) for tier in CreatorTier
        }
        
        # Modality performance tracking
        self.modality_performance: Dict[ContentModality, Dict[str, List[float]]] = {
            modality: defaultdict(list) for modality in ContentModality
        }
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = config.get('monitoring_interval', 1.0)  # seconds
        
        # Performance thresholds
        self.performance_thresholds = {
            'max_latency_ms': {
                CreatorTier.FREE: 2000,
                CreatorTier.PRO: 1000,
                CreatorTier.ENTERPRISE: 500,
                CreatorTier.PREMIUM: 200
            },
            'min_throughput_rps': {
                CreatorTier.FREE: 1,
                CreatorTier.PRO: 5,
                CreatorTier.ENTERPRISE: 20,
                CreatorTier.PREMIUM: 50
            },
            'max_resource_usage': {
                'cpu_percent': 80,
                'memory_mb': 2000,
                'gpu_percent': 90
            }
        }
        
        # Cost model (per request)
        self.cost_model = {
            'base_cost': 0.001,  # $0.001 base
            'cpu_cost_per_ms': 0.000001,
            'memory_cost_per_mb_ms': 0.0000001,
            'gpu_cost_per_ms': 0.00001
        }
        
        # Revenue attribution model
        self.revenue_attribution = {
            CreatorTier.FREE: 0.0,
            CreatorTier.PRO: 0.1,    # $0.1 per request
            CreatorTier.ENTERPRISE: 0.5,  # $0.5 per request
            CreatorTier.PREMIUM: 1.0     # $1.0 per request
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger("model_inference_monitor")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation monitoring performance inférence"""
        self.logger.info("🚀 Initialisation Model Inference Performance Monitor...")
        
        # Initialize performance tracking structures
        await self._initialize_performance_tracking()
        
        # Start real-time monitoring
        await self._start_real_time_monitoring()
        
        self.logger.info("✅ Model Inference Performance Monitor initialisé")
    
    async def _initialize_performance_tracking(self):
        """Initialisation structures tracking performance"""
        # Initialize model stats for common models
        common_models = [
            'content_classifier_v1',
            'collaboration_matcher_v2',
            'revenue_predictor_v1',
            'quality_assessor_v1',
            'audio_processor_v1',
            'image_enhancer_v1',
            'text_analyzer_v1',
            'trend_predictor_v1'
        ]
        
        for model_id in common_models:
            self.model_stats[model_id] = ModelPerformanceStats(
                model_id=model_id,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_latency_ms=0.0,
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                avg_throughput_rps=0.0,
                peak_throughput_rps=0.0,
                avg_cpu_usage=0.0,
                avg_memory_usage=0.0,
                avg_gpu_usage=0.0,
                avg_confidence=0.0,
                avg_accuracy=0.0,
                total_cost=0.0,
                total_revenue=0.0,
                roi_ratio=0.0
            )
    
    async def _start_real_time_monitoring(self):
        """Démarrage monitoring temps réel"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info("🔍 Real-time monitoring started")
    
    def _monitoring_loop(self):
        """Boucle monitoring temps réel"""
        while self.monitoring_active:
            try:
                # Update performance statistics
                self._update_performance_statistics()
                
                # Check performance thresholds
                self._check_performance_thresholds()
                
                # Cleanup old data
                self._cleanup_old_data()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Wait before retrying
    
    async def start_inference_tracking(self, request: InferenceRequest) -> str:
        """Démarrage tracking inférence"""
        self.active_requests[request.request_id] = request
        
        self.logger.debug(
            f"Started tracking inference {request.request_id} for model {request.model_id} "
            f"(Creator: {request.creator_tier.value}, Modality: {request.content_modality.value})"
        )
        
        return request.request_id
    
    async def complete_inference_tracking(
        self, 
        request_id: str,
        latency_ms: float,
        cpu_usage: float,
        memory_usage: float,
        gpu_usage: float,
        gpu_memory: float,
        confidence_score: float,
        status: InferenceStatus,
        error_message: Optional[str] = None
    ) -> InferenceMetrics:
        """Finalisation tracking inférence avec métriques"""
        
        if request_id not in self.active_requests:
            raise ValueError(f"Request {request_id} not found in active tracking")
        
        request = self.active_requests[request_id]
        
        # Calculate derived metrics
        processing_time = latency_ms
        queue_wait_time = 0.0  # Would be calculated from actual queue times
        throughput = 1000.0 / latency_ms if latency_ms > 0 else 0.0
        
        # Calculate costs
        cost = self._calculate_inference_cost(
            latency_ms, cpu_usage, memory_usage, gpu_usage
        )
        
        # Calculate revenue attribution
        revenue = self.revenue_attribution.get(request.creator_tier, 0.0)
        
        # Estimate accuracy (would use actual model predictions in production)
        accuracy_estimate = min(confidence_score + 0.1, 1.0)
        
        # Create metrics object
        metrics = InferenceMetrics(
            request_id=request_id,
            model_id=request.model_id,
            creator_id=request.creator_id,
            creator_tier=request.creator_tier,
            content_modality=request.content_modality,
            latency_ms=latency_ms,
            throughput_rps=throughput,
            queue_wait_time_ms=queue_wait_time,
            processing_time_ms=processing_time,
            cpu_usage_percent=cpu_usage,
            memory_usage_mb=memory_usage,
            gpu_usage_percent=gpu_usage,
            gpu_memory_mb=gpu_memory,
            confidence_score=confidence_score,
            accuracy_estimate=accuracy_estimate,
            cost_estimate=cost,
            revenue_attribution=revenue,
            status=status,
            error_message=error_message
        )
        
        # Store metrics
        await self._store_inference_metrics(metrics)
        
        # Update performance statistics
        await self._update_model_statistics(metrics)
        
        # Remove from active tracking
        del self.active_requests[request_id]
        
        self.logger.info(
            f"Completed inference tracking {request_id}: {latency_ms:.1f}ms, "
            f"Status: {status.value}, Cost: ${cost:.6f}, Revenue: ${revenue:.2f}"
        )
        
        return metrics
    
    def _calculate_inference_cost(
        self, 
        latency_ms: float, 
        cpu_usage: float, 
        memory_usage: float, 
        gpu_usage: float
    ) -> float:
        """Calcul coût inférence basé ressources utilisées"""
        base_cost = self.cost_model['base_cost']
        cpu_cost = (cpu_usage / 100.0) * latency_ms * self.cost_model['cpu_cost_per_ms']
        memory_cost = memory_usage * latency_ms * self.cost_model['memory_cost_per_mb_ms']
        gpu_cost = (gpu_usage / 100.0) * latency_ms * self.cost_model['gpu_cost_per_ms']
        
        total_cost = base_cost + cpu_cost + memory_cost + gpu_cost
        return round(total_cost, 6)
    
    async def _store_inference_metrics(self, metrics: InferenceMetrics):
        """Stockage métriques inférence"""
        # Store in metrics history
        self.metrics_history[metrics.model_id].append(metrics)
        
        # Update latency buckets
        self.latency_buckets[metrics.model_id].append(metrics.latency_ms)
        
        # Update throughput tracking
        current_time = time.time()
        self.throughput_tracker[metrics.model_id].append((current_time, metrics.throughput_rps))
        
        # Update resource usage tracking
        resource_usage = {
            'cpu': metrics.cpu_usage_percent,
            'memory': metrics.memory_usage_mb,
            'gpu': metrics.gpu_usage_percent,
            'timestamp': current_time
        }
        self.resource_usage_tracker[metrics.model_id].append(resource_usage)
        
        # Update tier-specific performance
        tier_metrics = self.tier_performance[metrics.creator_tier]
        tier_metrics['latency'].append(metrics.latency_ms)
        tier_metrics['throughput'].append(metrics.throughput_rps)
        tier_metrics['confidence'].append(metrics.confidence_score)
        
        # Update modality-specific performance
        modality_metrics = self.modality_performance[metrics.content_modality]
        modality_metrics['latency'].append(metrics.latency_ms)
        modality_metrics['throughput'].append(metrics.throughput_rps)
        modality_metrics['accuracy'].append(metrics.accuracy_estimate)
    
    async def _update_model_statistics(self, metrics: InferenceMetrics):
        """Mise à jour statistiques modèle"""
        model_id = metrics.model_id
        
        if model_id not in self.model_stats:
            self.model_stats[model_id] = ModelPerformanceStats(
                model_id=model_id,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_latency_ms=0.0,
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                avg_throughput_rps=0.0,
                peak_throughput_rps=0.0,
                avg_cpu_usage=0.0,
                avg_memory_usage=0.0,
                avg_gpu_usage=0.0,
                avg_confidence=0.0,
                avg_accuracy=0.0,
                total_cost=0.0,
                total_revenue=0.0,
                roi_ratio=0.0
            )
        
        stats = self.model_stats[model_id]
        
        # Update request counts
        stats.total_requests += 1
        if metrics.status == InferenceStatus.COMPLETED:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
        
        # Update costs and revenue
        stats.total_cost += metrics.cost_estimate
        stats.total_revenue += metrics.revenue_attribution
        stats.roi_ratio = (stats.total_revenue / stats.total_cost) if stats.total_cost > 0 else 0.0
        
        # Update averages using exponential moving average
        alpha = 0.1  # Smoothing factor
        
        stats.avg_latency_ms = alpha * metrics.latency_ms + (1 - alpha) * stats.avg_latency_ms
        stats.avg_throughput_rps = alpha * metrics.throughput_rps + (1 - alpha) * stats.avg_throughput_rps
        stats.avg_cpu_usage = alpha * metrics.cpu_usage_percent + (1 - alpha) * stats.avg_cpu_usage
        stats.avg_memory_usage = alpha * metrics.memory_usage_mb + (1 - alpha) * stats.avg_memory_usage
        stats.avg_gpu_usage = alpha * metrics.gpu_usage_percent + (1 - alpha) * stats.avg_gpu_usage
        stats.avg_confidence = alpha * metrics.confidence_score + (1 - alpha) * stats.avg_confidence
        stats.avg_accuracy = alpha * metrics.accuracy_estimate + (1 - alpha) * stats.avg_accuracy
        
        # Update peak throughput
        if metrics.throughput_rps > stats.peak_throughput_rps:
            stats.peak_throughput_rps = metrics.throughput_rps
        
        # Update percentile latencies
        await self._update_latency_percentiles(model_id)
        
        stats.last_updated = datetime.utcnow()
    
    async def _update_latency_percentiles(self, model_id: str):
        """Mise à jour percentiles latence"""
        if model_id not in self.latency_buckets or not self.latency_buckets[model_id]:
            return
        
        latencies = sorted(self.latency_buckets[model_id])
        n = len(latencies)
        
        if n > 0:
            stats = self.model_stats[model_id]
            stats.p50_latency_ms = latencies[int(n * 0.5)]
            stats.p95_latency_ms = latencies[int(n * 0.95)]
            stats.p99_latency_ms = latencies[int(n * 0.99)]
    
    def _update_performance_statistics(self):
        """Mise à jour statistiques performance temps réel"""
        try:
            current_time = time.time()
            
            # Calculate current throughput for each model
            for model_id, throughput_data in self.throughput_tracker.items():
                # Remove old data (older than 60 seconds)
                cutoff_time = current_time - 60
                while throughput_data and throughput_data[0][0] < cutoff_time:
                    throughput_data.popleft()
                
                # Calculate current throughput
                if throughput_data:
                    total_rps = sum(rps for _, rps in throughput_data)
                    avg_rps = total_rps / len(throughput_data)
                    
                    if model_id in self.model_stats:
                        self.model_stats[model_id].avg_throughput_rps = avg_rps
            
        except Exception as e:
            self.logger.error(f"Error updating performance statistics: {str(e)}")
    
    def _check_performance_thresholds(self):
        """Vérification seuils performance"""
        try:
            for model_id, stats in self.model_stats.items():
                # Check latency thresholds for each creator tier
                for tier, max_latency in self.performance_thresholds['max_latency_ms'].items():
                    if stats.avg_latency_ms > max_latency:
                        self.logger.warning(
                            f"🚨 Latency threshold exceeded for {model_id} ({tier.value}): "
                            f"{stats.avg_latency_ms:.1f}ms > {max_latency}ms"
                        )
                
                # Check resource usage thresholds
                max_cpu = self.performance_thresholds['max_resource_usage']['cpu_percent']
                if stats.avg_cpu_usage > max_cpu:
                    self.logger.warning(
                        f"🚨 CPU usage threshold exceeded for {model_id}: "
                        f"{stats.avg_cpu_usage:.1f}% > {max_cpu}%"
                    )
                
                max_memory = self.performance_thresholds['max_resource_usage']['memory_mb']
                if stats.avg_memory_usage > max_memory:
                    self.logger.warning(
                        f"🚨 Memory usage threshold exceeded for {model_id}: "
                        f"{stats.avg_memory_usage:.1f}MB > {max_memory}MB"
                    )
                
        except Exception as e:
            self.logger.error(f"Error checking performance thresholds: {str(e)}")
    
    def _cleanup_old_data(self):
        """Nettoyage données anciennes"""
        try:
            current_time = time.time()
            cutoff_time = current_time - 3600  # Keep 1 hour of data
            
            # Cleanup latency buckets - keep only recent data
            for model_id in list(self.latency_buckets.keys()):
                if len(self.latency_buckets[model_id]) > 500:
                    # Keep only the most recent 500 measurements
                    self.latency_buckets[model_id] = self.latency_buckets[model_id][-500:]
            
            # Cleanup tier and modality performance data
            for tier_data in self.tier_performance.values():
                for metric_list in tier_data.values():
                    if len(metric_list) > 200:
                        metric_list[:] = metric_list[-200:]
            
            for modality_data in self.modality_performance.values():
                for metric_list in modality_data.values():
                    if len(metric_list) > 200:
                        metric_list[:] = metric_list[-200:]
                        
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")
    
    async def get_model_performance_summary(self, model_id: str) -> Dict[str, Any]:
        """Résumé performance modèle"""
        if model_id not in self.model_stats:
            return {'error': f'Model {model_id} not found'}
        
        stats = self.model_stats[model_id]
        
        # Get recent metrics
        recent_metrics = list(self.metrics_history[model_id])[-10:] if model_id in self.metrics_history else []
        
        return {
            'model_id': model_id,
            'performance_summary': {
                'total_requests': stats.total_requests,
                'success_rate': (stats.successful_requests / stats.total_requests * 100) if stats.total_requests > 0 else 0,
                'avg_latency_ms': round(stats.avg_latency_ms, 2),
                'p95_latency_ms': round(stats.p95_latency_ms, 2),
                'p99_latency_ms': round(stats.p99_latency_ms, 2),
                'avg_throughput_rps': round(stats.avg_throughput_rps, 2),
                'peak_throughput_rps': round(stats.peak_throughput_rps, 2)
            },
            'resource_utilization': {
                'avg_cpu_usage': round(stats.avg_cpu_usage, 2),
                'avg_memory_usage': round(stats.avg_memory_usage, 2),
                'avg_gpu_usage': round(stats.avg_gpu_usage, 2)
            },
            'quality_metrics': {
                'avg_confidence': round(stats.avg_confidence, 3),
                'avg_accuracy': round(stats.avg_accuracy, 3)
            },
            'business_metrics': {
                'total_cost': round(stats.total_cost, 4),
                'total_revenue': round(stats.total_revenue, 2),
                'roi_ratio': round(stats.roi_ratio, 2)
            },
            'recent_activity': len(recent_metrics),
            'last_updated': stats.last_updated.isoformat()
        }
    
    async def get_creator_tier_performance(self, tier: CreatorTier) -> Dict[str, Any]:
        """Performance par tier créateur"""
        tier_data = self.tier_performance[tier]
        
        if not any(tier_data.values()):
            return {'tier': tier.value, 'status': 'No data available'}
        
        # Calculate statistics
        latencies = tier_data['latency']
        throughputs = tier_data['throughput']
        confidences = tier_data['confidence']
        
        return {
            'tier': tier.value,
            'performance_stats': {
                'avg_latency_ms': round(statistics.mean(latencies), 2) if latencies else 0,
                'median_latency_ms': round(statistics.median(latencies), 2) if latencies else 0,
                'avg_throughput_rps': round(statistics.mean(throughputs), 2) if throughputs else 0,
                'avg_confidence': round(statistics.mean(confidences), 3) if confidences else 0
            },
            'threshold_compliance': {
                'latency_sla': self.performance_thresholds['max_latency_ms'][tier],
                'throughput_sla': self.performance_thresholds['min_throughput_rps'][tier],
                'meets_latency_sla': all(l <= self.performance_thresholds['max_latency_ms'][tier] for l in latencies[-10:]) if latencies else True,
                'meets_throughput_sla': all(t >= self.performance_thresholds['min_throughput_rps'][tier] for t in throughputs[-10:]) if throughputs else True
            },
            'sample_count': len(latencies)
        }
    
    async def get_modality_performance(self, modality: ContentModality) -> Dict[str, Any]:
        """Performance par modalité contenu"""
        modality_data = self.modality_performance[modality]
        
        if not any(modality_data.values()):
            return {'modality': modality.value, 'status': 'No data available'}
        
        # Calculate statistics
        latencies = modality_data['latency']
        throughputs = modality_data['throughput']
        accuracies = modality_data['accuracy']
        
        return {
            'modality': modality.value,
            'performance_stats': {
                'avg_latency_ms': round(statistics.mean(latencies), 2) if latencies else 0,
                'min_latency_ms': round(min(latencies), 2) if latencies else 0,
                'max_latency_ms': round(max(latencies), 2) if latencies else 0,
                'avg_throughput_rps': round(statistics.mean(throughputs), 2) if throughputs else 0,
                'avg_accuracy': round(statistics.mean(accuracies), 3) if accuracies else 0
            },
            'optimization_opportunities': self._identify_modality_optimizations(modality, latencies, throughputs),
            'sample_count': len(latencies)
        }
    
    def _identify_modality_optimizations(
        self, 
        modality: ContentModality, 
        latencies: List[float], 
        throughputs: List[float]
    ) -> List[str]:
        """Identification opportunités optimisation par modalité"""
        opportunities = []
        
        if not latencies or not throughputs:
            return opportunities
        
        avg_latency = statistics.mean(latencies)
        avg_throughput = statistics.mean(throughputs)
        
        # Modality-specific optimizations
        if modality == ContentModality.AUDIO:
            if avg_latency > 1000:
                opportunities.append("Consider audio preprocessing optimization")
            if avg_throughput < 10:
                opportunities.append("Implement parallel audio processing")
                
        elif modality == ContentModality.VIDEO:
            if avg_latency > 2000:
                opportunities.append("Optimize video frame processing")
            if avg_throughput < 5:
                opportunities.append("Implement video streaming processing")
                
        elif modality == ContentModality.IMAGE:
            if avg_latency > 500:
                opportunities.append("Optimize image preprocessing pipeline")
            if avg_throughput < 20:
                opportunities.append("Implement batch image processing")
                
        elif modality == ContentModality.TEXT:
            if avg_latency > 200:
                opportunities.append("Optimize text tokenization")
            if avg_throughput < 50:
                opportunities.append("Implement text batch processing")
        
        return opportunities
    
    async def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Dashboard complet performance inférence"""
        # Overall statistics
        total_requests = sum(stats.total_requests for stats in self.model_stats.values())
        total_successful = sum(stats.successful_requests for stats in self.model_stats.values())
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        # Cost and revenue totals
        total_cost = sum(stats.total_cost for stats in self.model_stats.values())
        total_revenue = sum(stats.total_revenue for stats in self.model_stats.values())
        overall_roi = (total_revenue / total_cost) if total_cost > 0 else 0
        
        # Active requests
        active_count = len(self.active_requests)
        
        # Performance by tier
        tier_summaries = {}
        for tier in CreatorTier:
            tier_summary = await self.get_creator_tier_performance(tier)
            tier_summaries[tier.value] = tier_summary
        
        # Performance by modality
        modality_summaries = {}
        for modality in ContentModality:
            modality_summary = await self.get_modality_performance(modality)
            modality_summaries[modality.value] = modality_summary
        
        # Top performing models
        sorted_models = sorted(
            self.model_stats.values(),
            key=lambda x: x.roi_ratio,
            reverse=True
        )[:5]
        
        return {
            'overview': {
                'total_requests': total_requests,
                'overall_success_rate': round(overall_success_rate, 2),
                'active_requests': active_count,
                'models_tracked': len(self.model_stats),
                'total_cost': round(total_cost, 4),
                'total_revenue': round(total_revenue, 2),
                'overall_roi': round(overall_roi, 2)
            },
            'performance_by_tier': tier_summaries,
            'performance_by_modality': modality_summaries,
            'top_performing_models': [
                {
                    'model_id': stats.model_id,
                    'roi_ratio': round(stats.roi_ratio, 2),
                    'total_requests': stats.total_requests,
                    'avg_latency_ms': round(stats.avg_latency_ms, 2)
                }
                for stats in sorted_models
            ],
            'system_health': {
                'monitoring_active': self.monitoring_active,
                'last_update': datetime.utcnow().isoformat()
            }
        }
    
    async def shutdown(self):
        """Arrêt propre monitoring"""
        self.logger.info("⏹️ Shutting down Model Inference Performance Monitor...")
        
        # Stop monitoring
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        # Clear data structures
        self.active_requests.clear()
        self.metrics_history.clear()
        self.model_stats.clear()
        self.latency_buckets.clear()
        self.throughput_tracker.clear()
        self.resource_usage_tracker.clear()
        
        self.logger.info("✅ Model Inference Performance Monitor shutdown complete")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_inference_monitor():
        config = {
            'monitoring_interval': 0.1,  # Fast for testing
            'debug': True
        }
        
        monitor = ModelInferencePerformanceMonitor(config)
        await monitor.initialize()
        
        # Test inference tracking
        request = InferenceRequest(
            request_id=str(uuid.uuid4()),
            model_id='content_classifier_v1',
            creator_id='creator_123',
            creator_tier=CreatorTier.PRO,
            content_modality=ContentModality.VIDEO,
            input_size=1024000,  # 1MB
            priority=5
        )
        
        # Start tracking
        await monitor.start_inference_tracking(request)
        
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Complete tracking
        metrics = await monitor.complete_inference_tracking(
            request_id=request.request_id,
            latency_ms=250.5,
            cpu_usage=45.2,
            memory_usage=512.0,
            gpu_usage=67.8,
            gpu_memory=1024.0,
            confidence_score=0.89,
            status=InferenceStatus.COMPLETED
        )
        
        print(f"✅ Inference tracked: {metrics.latency_ms}ms, Cost: ${metrics.cost_estimate:.6f}")
        
        # Test multiple requests for statistics
        for i in range(5):
            req = InferenceRequest(
                request_id=str(uuid.uuid4()),
                model_id='content_classifier_v1',
                creator_id=f'creator_{i}',
                creator_tier=CreatorTier.FREE if i % 2 == 0 else CreatorTier.ENTERPRISE,
                content_modality=ContentModality.TEXT,
                input_size=1000,
                priority=i + 1
            )
            
            await monitor.start_inference_tracking(req)
            await monitor.complete_inference_tracking(
                request_id=req.request_id,
                latency_ms=100.0 + i * 50,
                cpu_usage=30.0 + i * 10,
                memory_usage=200.0 + i * 100,
                gpu_usage=40.0 + i * 15,
                gpu_memory=512.0,
                confidence_score=0.8 + i * 0.02,
                status=InferenceStatus.COMPLETED
            )
        
        # Get performance summary
        summary = await monitor.get_model_performance_summary('content_classifier_v1')
        print(f"✅ Model summary: {summary['performance_summary']['total_requests']} requests")
        
        # Get dashboard
        dashboard = await monitor.get_comprehensive_dashboard()
        print(f"✅ Dashboard: {dashboard['overview']['total_requests']} total requests")
        
        print("✅ Model Inference Performance Monitor test completed")
        await monitor.shutdown()
    
    asyncio.run(test_inference_monitor())