"""
⚡ Real-Time Inference Metrics Collector - Enterprise AI/ML Streaming Analytics
===========================================================================

Collecteur métriques inférence temps réel pour Creator Economy.
Streaming metrics collection, low-latency aggregation, hot path optimization.

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

Architecture: monitoring/ai_ml_performance_hub/real_time_inference_metrics_collector.py
Responsabilité: Collecte métriques inférence temps réel Creator Economy
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
from collections import deque, defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor
import queue


class MetricType(Enum):
    """Types de métriques"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    ACCURACY = "accuracy"
    CONFIDENCE = "confidence"
    RESOURCE_USAGE = "resource_usage"
    QUEUE_DEPTH = "queue_depth"
    CACHE_HIT_RATE = "cache_hit_rate"


class AggregationMethod(Enum):
    """Méthodes agrégation"""
    MEAN = "mean"
    MEDIAN = "median"
    P95 = "p95"
    P99 = "p99"
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    HISTOGRAM = "histogram"


class MetricPriority(Enum):
    """Priorités métriques"""
    CRITICAL = "critical"    # < 1ms processing
    HIGH = "high"           # < 5ms processing
    MEDIUM = "medium"       # < 10ms processing
    LOW = "low"            # < 50ms processing


class CreatorInteractionType(Enum):
    """Types interaction créateur"""
    CONTENT_UPLOAD = "content_upload"
    REAL_TIME_EDIT = "real_time_edit"
    LIVE_STREAM = "live_stream"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    ANALYTICS_VIEW = "analytics_view"


@dataclass
class InferenceMetric:
    """Métrique inférence temps réel"""
    metric_id: str
    model_id: str
    creator_id: str
    interaction_type: CreatorInteractionType
    metric_type: MetricType
    value: float
    unit: str
    priority: MetricPriority
    context: Dict[str, Any]
    timestamp: float  # High precision timestamp
    processing_time: float = 0.0  # Time taken to process this metric


@dataclass
class StreamingWindow:
    """Fenêtre streaming"""
    window_id: str
    model_id: str
    metric_type: MetricType
    window_size_seconds: int
    aggregation_method: AggregationMethod
    values: deque
    timestamps: deque
    current_aggregated_value: float
    last_updated: float


@dataclass
class HotPathMetrics:
    """Métriques chemin critique"""
    path_id: str
    model_id: str
    creator_tier: str
    avg_latency: float
    p95_latency: float
    p99_latency: float
    throughput_rps: float
    error_rate: float
    cache_hit_rate: float
    resource_efficiency: float
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EdgeInferenceMetrics:
    """Métriques inférence edge"""
    edge_node_id: str
    model_id: str
    location: str
    latency: float
    bandwidth_usage: float
    compute_utilization: float
    memory_usage: float
    cache_efficiency: float
    offline_capability: bool
    sync_status: str


@dataclass
class AlertThreshold:
    """Seuil alerte"""
    threshold_id: str
    metric_type: MetricType
    model_id: str
    operator: str  # "gt", "lt", "eq"
    value: float
    window_seconds: int
    callback: Optional[Callable[[InferenceMetric], None]]


class RealTimeInferenceMetricsCollector:
    """Collecteur métriques inférence temps réel enterprise"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # High-performance data structures
        self.metric_buffer = queue.Queue(maxsize=10000)  # Thread-safe buffer
        self.streaming_windows: Dict[str, StreamingWindow] = {}
        self.hot_path_metrics: Dict[str, HotPathMetrics] = {}
        self.edge_metrics: Dict[str, EdgeInferenceMetrics] = {}
        self.alert_thresholds: Dict[str, AlertThreshold] = {}
        
        # Performance tracking
        self.metrics_processed = 0
        self.processing_times = deque(maxlen=1000)
        self.error_count = 0
        
        # Streaming configuration
        self.streaming_config = {
            'buffer_size': 10000,
            'batch_size': 100,
            'processing_interval_ms': 10,
            'aggregation_window_sizes': [1, 5, 15, 60, 300],  # seconds
            'max_processing_latency_ms': 5.0
        }
        
        # Creator tier performance targets
        self.performance_targets = {
            'free': {'latency_ms': 500, 'throughput_rps': 10, 'error_rate': 0.05},
            'premium': {'latency_ms': 200, 'throughput_rps': 100, 'error_rate': 0.01},
            'enterprise': {'latency_ms': 50, 'throughput_rps': 1000, 'error_rate': 0.001}
        }
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Processing control
        self._collecting = False
        self._processing_tasks = []
        
        # Initialize streaming windows
        asyncio.create_task(self._initialize_streaming_windows())
    
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("realtime_inference_metrics")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def _initialize_streaming_windows(self):
        """Initialisation fenêtres streaming"""
        try:
            # Create default streaming windows for common metrics
            default_windows = [
                ('latency_1s', MetricType.LATENCY, 1, AggregationMethod.P95),
                ('latency_5s', MetricType.LATENCY, 5, AggregationMethod.P95),
                ('latency_60s', MetricType.LATENCY, 60, AggregationMethod.P95),
                ('throughput_1s', MetricType.THROUGHPUT, 1, AggregationMethod.SUM),
                ('throughput_5s', MetricType.THROUGHPUT, 5, AggregationMethod.SUM),
                ('error_rate_5s', MetricType.ERROR_RATE, 5, AggregationMethod.MEAN),
                ('error_rate_60s', MetricType.ERROR_RATE, 60, AggregationMethod.MEAN),
                ('accuracy_5s', MetricType.ACCURACY, 5, AggregationMethod.MEAN),
                ('resource_usage_1s', MetricType.RESOURCE_USAGE, 1, AggregationMethod.MEAN)
            ]
            
            for window_name, metric_type, window_size, agg_method in default_windows:
                window_id = f"global_{window_name}"
                self.streaming_windows[window_id] = StreamingWindow(
                    window_id=window_id,
                    model_id="*",  # Global window
                    metric_type=metric_type,
                    window_size_seconds=window_size,
                    aggregation_method=agg_method,
                    values=deque(maxlen=window_size * 1000),  # Assume max 1000 metrics/second
                    timestamps=deque(maxlen=window_size * 1000),
                    current_aggregated_value=0.0,
                    last_updated=time.time()
                )
            
            self.logger.info(f"✅ Initialized {len(self.streaming_windows)} streaming windows")
            
        except Exception as e:
            self.logger.error(f"Error initializing streaming windows: {e}")
    
    async def start_collection(self):
        """Démarrage collecte temps réel"""
        try:
            if self._collecting:
                await self.stop_collection()
            
            self._collecting = True
            
            # Start processing tasks
            self._processing_tasks = [
                asyncio.create_task(self._metric_ingestion_loop()),
                asyncio.create_task(self._streaming_aggregation_loop()),
                asyncio.create_task(self._hot_path_monitoring_loop()),
                asyncio.create_task(self._alert_monitoring_loop())
            ]
            
            self.logger.info("🚀 Real-time inference metrics collection started")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting collection: {e}")
            return False
    
    async def _metric_ingestion_loop(self):
        """Boucle ingestion métriques"""
        try:
            while self._collecting:
                metrics_batch = []
                
                # Collect batch of metrics from buffer
                try:
                    for _ in range(self.streaming_config['batch_size']):
                        metric = self.metric_buffer.get_nowait()
                        metrics_batch.append(metric)
                except queue.Empty:
                    pass
                
                if metrics_batch:
                    # Process batch in thread pool for performance
                    await asyncio.get_event_loop().run_in_executor(
                        self.thread_pool,
                        self._process_metrics_batch,
                        metrics_batch
                    )
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(self.streaming_config['processing_interval_ms'] / 1000.0)
                
        except Exception as e:
            self.logger.error(f"Error in metric ingestion loop: {e}")
    
    def _process_metrics_batch(self, metrics_batch: List[InferenceMetric]):
        """Traitement batch métriques"""
        try:
            start_time = time.time()
            
            for metric in metrics_batch:
                # Update streaming windows
                self._update_streaming_windows(metric)
                
                # Update hot path metrics
                self._update_hot_path_metrics(metric)
                
                # Check alert thresholds
                self._check_alert_thresholds(metric)
                
                # Track processing performance
                self.metrics_processed += 1
            
            processing_time = (time.time() - start_time) * 1000  # ms
            self.processing_times.append(processing_time)
            
            # Check if processing is too slow
            if processing_time > self.streaming_config['max_processing_latency_ms']:
                self.logger.warning(f"Slow batch processing: {processing_time:.2f}ms for {len(metrics_batch)} metrics")
            
        except Exception as e:
            self.logger.error(f"Error processing metrics batch: {e}")
            self.error_count += 1
    
    def _update_streaming_windows(self, metric: InferenceMetric):
        """Mise à jour fenêtres streaming"""
        try:
            current_time = metric.timestamp
            
            # Update global windows
            for window in self.streaming_windows.values():
                if (window.model_id == "*" or window.model_id == metric.model_id) and \
                   window.metric_type == metric.metric_type:
                    
                    # Add new value
                    window.values.append(metric.value)
                    window.timestamps.append(current_time)
                    
                    # Remove old values outside window
                    cutoff_time = current_time - window.window_size_seconds
                    while window.timestamps and window.timestamps[0] < cutoff_time:
                        window.timestamps.popleft()
                        window.values.popleft()
                    
                    # Update aggregated value
                    if window.values:
                        window.current_aggregated_value = self._calculate_aggregation(
                            list(window.values), window.aggregation_method
                        )
                    
                    window.last_updated = current_time
            
        except Exception as e:
            self.logger.error(f"Error updating streaming windows: {e}")
    
    def _calculate_aggregation(self, values: List[float], method: AggregationMethod) -> float:
        """Calcul agrégation"""
        try:
            if not values:
                return 0.0
            
            if method == AggregationMethod.MEAN:
                return statistics.mean(values)
            elif method == AggregationMethod.MEDIAN:
                return statistics.median(values)
            elif method == AggregationMethod.P95:
                return np.percentile(values, 95)
            elif method == AggregationMethod.P99:
                return np.percentile(values, 99)
            elif method == AggregationMethod.SUM:
                return sum(values)
            elif method == AggregationMethod.COUNT:
                return len(values)
            elif method == AggregationMethod.MIN:
                return min(values)
            elif method == AggregationMethod.MAX:
                return max(values)
            else:
                return statistics.mean(values)
                
        except Exception as e:
            self.logger.error(f"Error calculating aggregation: {e}")
            return 0.0
    
    def _update_hot_path_metrics(self, metric: InferenceMetric):
        """Mise à jour métriques chemin critique"""
        try:
            # Determine creator tier from context
            creator_tier = metric.context.get('creator_tier', 'free')
            path_id = f"{metric.model_id}_{creator_tier}"
            
            if path_id not in self.hot_path_metrics:
                self.hot_path_metrics[path_id] = HotPathMetrics(
                    path_id=path_id,
                    model_id=metric.model_id,
                    creator_tier=creator_tier,
                    avg_latency=0.0,
                    p95_latency=0.0,
                    p99_latency=0.0,
                    throughput_rps=0.0,
                    error_rate=0.0,
                    cache_hit_rate=0.0,
                    resource_efficiency=0.0
                )
            
            hot_path = self.hot_path_metrics[path_id]
            
            # Update metrics based on type
            if metric.metric_type == MetricType.LATENCY:
                # Use exponential moving average for real-time updates
                alpha = 0.3  # Smoothing factor
                hot_path.avg_latency = (alpha * metric.value) + ((1 - alpha) * hot_path.avg_latency)
                
                # Approximate percentiles (simplified for real-time)
                if metric.value > hot_path.p95_latency:
                    hot_path.p95_latency = (alpha * metric.value) + ((1 - alpha) * hot_path.p95_latency)
                if metric.value > hot_path.p99_latency:
                    hot_path.p99_latency = (alpha * metric.value) + ((1 - alpha) * hot_path.p99_latency)
            
            elif metric.metric_type == MetricType.THROUGHPUT:
                hot_path.throughput_rps = metric.value
            
            elif metric.metric_type == MetricType.ERROR_RATE:
                hot_path.error_rate = (alpha * metric.value) + ((1 - alpha) * hot_path.error_rate)
            
            elif metric.metric_type == MetricType.CACHE_HIT_RATE:
                hot_path.cache_hit_rate = (alpha * metric.value) + ((1 - alpha) * hot_path.cache_hit_rate)
            
            hot_path.last_updated = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Error updating hot path metrics: {e}")
    
    def _check_alert_thresholds(self, metric: InferenceMetric):
        """Vérification seuils alerte"""
        try:
            for threshold in self.alert_thresholds.values():
                if (threshold.metric_type == metric.metric_type and 
                    (threshold.model_id == "*" or threshold.model_id == metric.model_id)):
                    
                    # Check threshold condition
                    triggered = False
                    if threshold.operator == "gt" and metric.value > threshold.value:
                        triggered = True
                    elif threshold.operator == "lt" and metric.value < threshold.value:
                        triggered = True
                    elif threshold.operator == "eq" and abs(metric.value - threshold.value) < 0.001:
                        triggered = True
                    
                    if triggered and threshold.callback:
                        try:
                            threshold.callback(metric)
                        except Exception as e:
                            self.logger.error(f"Error in alert callback: {e}")
            
        except Exception as e:
            self.logger.error(f"Error checking alert thresholds: {e}")
    
    async def _streaming_aggregation_loop(self):
        """Boucle agrégation streaming"""
        try:
            while self._collecting:
                # Update model-specific windows based on recent activity
                active_models = set()
                
                # Collect active models from recent metrics
                temp_metrics = []
                try:
                    for _ in range(100):  # Sample recent metrics
                        metric = self.metric_buffer.get_nowait()
                        temp_metrics.append(metric)
                        active_models.add(metric.model_id)
                except queue.Empty:
                    pass
                
                # Put metrics back in buffer
                for metric in temp_metrics:
                    try:
                        self.metric_buffer.put_nowait(metric)
                    except queue.Full:
                        pass
                
                # Create model-specific windows for active models
                for model_id in active_models:
                    await self._ensure_model_windows(model_id)
                
                # Clean up old windows
                await self._cleanup_old_windows()
                
                await asyncio.sleep(5)  # Run every 5 seconds
                
        except Exception as e:
            self.logger.error(f"Error in streaming aggregation loop: {e}")
    
    async def _ensure_model_windows(self, model_id: str):
        """Assurer fenêtres modèle"""
        try:
            required_windows = [
                (MetricType.LATENCY, 5, AggregationMethod.P95),
                (MetricType.THROUGHPUT, 60, AggregationMethod.SUM),
                (MetricType.ERROR_RATE, 60, AggregationMethod.MEAN)
            ]
            
            for metric_type, window_size, agg_method in required_windows:
                window_id = f"{model_id}_{metric_type.value}_{window_size}s"
                
                if window_id not in self.streaming_windows:
                    self.streaming_windows[window_id] = StreamingWindow(
                        window_id=window_id,
                        model_id=model_id,
                        metric_type=metric_type,
                        window_size_seconds=window_size,
                        aggregation_method=agg_method,
                        values=deque(maxlen=window_size * 100),
                        timestamps=deque(maxlen=window_size * 100),
                        current_aggregated_value=0.0,
                        last_updated=time.time()
                    )
            
        except Exception as e:
            self.logger.error(f"Error ensuring model windows: {e}")
    
    async def _cleanup_old_windows(self):
        """Nettoyage anciennes fenêtres"""
        try:
            current_time = time.time()
            cleanup_threshold = 3600  # 1 hour of inactivity
            
            windows_to_remove = []
            for window_id, window in self.streaming_windows.items():
                if (current_time - window.last_updated) > cleanup_threshold and window.model_id != "*":
                    windows_to_remove.append(window_id)
            
            for window_id in windows_to_remove:
                del self.streaming_windows[window_id]
            
            if windows_to_remove:
                self.logger.info(f"Cleaned up {len(windows_to_remove)} inactive streaming windows")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old windows: {e}")
    
    async def _hot_path_monitoring_loop(self):
        """Boucle monitoring chemin critique"""
        try:
            while self._collecting:
                # Check performance against targets
                for hot_path in self.hot_path_metrics.values():
                    targets = self.performance_targets.get(hot_path.creator_tier, {})
                    
                    # Check latency target
                    if 'latency_ms' in targets and hot_path.avg_latency > targets['latency_ms']:
                        self.logger.warning(
                            f"🚨 Hot path {hot_path.path_id} latency exceeded: "
                            f"{hot_path.avg_latency:.1f}ms > {targets['latency_ms']}ms"
                        )
                    
                    # Check error rate target
                    if 'error_rate' in targets and hot_path.error_rate > targets['error_rate']:
                        self.logger.warning(
                            f"🚨 Hot path {hot_path.path_id} error rate exceeded: "
                            f"{hot_path.error_rate:.3f} > {targets['error_rate']}"
                        )
                
                # Clean up old hot path metrics
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                paths_to_remove = [
                    path_id for path_id, hot_path in self.hot_path_metrics.items()
                    if hot_path.last_updated < cutoff_time
                ]
                
                for path_id in paths_to_remove:
                    del self.hot_path_metrics[path_id]
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            self.logger.error(f"Error in hot path monitoring loop: {e}")
    
    async def _alert_monitoring_loop(self):
        """Boucle monitoring alertes"""
        try:
            while self._collecting:
                # Monitor system health
                if self.processing_times:
                    avg_processing_time = statistics.mean(list(self.processing_times)[-100:])
                    if avg_processing_time > self.streaming_config['max_processing_latency_ms']:
                        self.logger.warning(f"High processing latency: {avg_processing_time:.2f}ms")
                
                # Monitor error rate
                total_processed = max(1, self.metrics_processed)
                error_rate = self.error_count / total_processed
                if error_rate > 0.01:  # 1% error rate threshold
                    self.logger.warning(f"High error rate in metrics processing: {error_rate:.3f}")
                
                # Monitor buffer usage
                buffer_usage = self.metric_buffer.qsize() / self.streaming_config['buffer_size']
                if buffer_usage > 0.8:
                    self.logger.warning(f"High buffer usage: {buffer_usage:.1%}")
                
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            self.logger.error(f"Error in alert monitoring loop: {e}")
    
    def collect_metric(self, 
                      model_id: str,
                      creator_id: str,
                      interaction_type: CreatorInteractionType,
                      metric_type: MetricType,
                      value: float,
                      unit: str = "",
                      priority: MetricPriority = MetricPriority.MEDIUM,
                      context: Dict[str, Any] = None) -> bool:
        """Collecte métrique temps réel"""
        try:
            metric = InferenceMetric(
                metric_id=str(uuid.uuid4()),
                model_id=model_id,
                creator_id=creator_id,
                interaction_type=interaction_type,
                metric_type=metric_type,
                value=value,
                unit=unit,
                priority=priority,
                context=context or {},
                timestamp=time.time()
            )
            
            # Add to buffer (non-blocking)
            try:
                self.metric_buffer.put_nowait(metric)
                return True
            except queue.Full:
                # Buffer full - drop metric with warning
                self.logger.warning("Metric buffer full - dropping metric")
                return False
                
        except Exception as e:
            self.logger.error(f"Error collecting metric: {e}")
            return False
    
    def add_alert_threshold(self,
                          metric_type: MetricType,
                          model_id: str,
                          operator: str,
                          value: float,
                          callback: Callable[[InferenceMetric], None],
                          window_seconds: int = 60) -> str:
        """Ajout seuil alerte"""
        try:
            threshold_id = str(uuid.uuid4())
            
            threshold = AlertThreshold(
                threshold_id=threshold_id,
                metric_type=metric_type,
                model_id=model_id,
                operator=operator,
                value=value,
                window_seconds=window_seconds,
                callback=callback
            )
            
            self.alert_thresholds[threshold_id] = threshold
            
            self.logger.info(f"Added alert threshold: {metric_type.value} {operator} {value} for {model_id}")
            return threshold_id
            
        except Exception as e:
            self.logger.error(f"Error adding alert threshold: {e}")
            return ""
    
    def remove_alert_threshold(self, threshold_id: str) -> bool:
        """Suppression seuil alerte"""
        try:
            if threshold_id in self.alert_thresholds:
                del self.alert_thresholds[threshold_id]
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing alert threshold: {e}")
            return False
    
    async def get_real_time_metrics(self, 
                                  model_id: str = None,
                                  metric_types: List[MetricType] = None,
                                  window_seconds: int = 60) -> Dict[str, Any]:
        """Récupération métriques temps réel"""
        try:
            current_time = time.time()
            cutoff_time = current_time - window_seconds
            
            results = {
                'timestamp': datetime.utcnow().isoformat(),
                'window_seconds': window_seconds,
                'streaming_windows': {},
                'hot_path_metrics': {},
                'system_performance': {}
            }
            
            # Get streaming window data
            for window_id, window in self.streaming_windows.items():
                if model_id and window.model_id != "*" and window.model_id != model_id:
                    continue
                if metric_types and window.metric_type not in metric_types:
                    continue
                if window.last_updated < cutoff_time:
                    continue
                
                results['streaming_windows'][window_id] = {
                    'model_id': window.model_id,
                    'metric_type': window.metric_type.value,
                    'aggregation_method': window.aggregation_method.value,
                    'current_value': window.current_aggregated_value,
                    'sample_count': len(window.values),
                    'last_updated': window.last_updated
                }
            
            # Get hot path metrics
            for path_id, hot_path in self.hot_path_metrics.items():
                if model_id and hot_path.model_id != model_id:
                    continue
                
                time_since_update = (datetime.utcnow() - hot_path.last_updated).total_seconds()
                if time_since_update > window_seconds:
                    continue
                
                results['hot_path_metrics'][path_id] = {
                    'model_id': hot_path.model_id,
                    'creator_tier': hot_path.creator_tier,
                    'avg_latency': hot_path.avg_latency,
                    'p95_latency': hot_path.p95_latency,
                    'p99_latency': hot_path.p99_latency,
                    'throughput_rps': hot_path.throughput_rps,
                    'error_rate': hot_path.error_rate,
                    'cache_hit_rate': hot_path.cache_hit_rate,
                    'resource_efficiency': hot_path.resource_efficiency,
                    'last_updated': hot_path.last_updated.isoformat()
                }
            
            # System performance metrics
            results['system_performance'] = {
                'metrics_processed': self.metrics_processed,
                'error_count': self.error_count,
                'buffer_usage': self.metric_buffer.qsize(),
                'buffer_capacity': self.streaming_config['buffer_size'],
                'avg_processing_time_ms': statistics.mean(list(self.processing_times)[-100:]) if self.processing_times else 0,
                'active_windows': len(self.streaming_windows),
                'active_hot_paths': len(self.hot_path_metrics),
                'alert_thresholds': len(self.alert_thresholds)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return {}
    
    async def get_creator_interaction_analytics(self, creator_id: str, hours: int = 24) -> Dict[str, Any]:
        """Analytics interaction créateur"""
        try:
            # This would typically query a time-series database
            # For now, we'll simulate based on current hot path metrics
            
            creator_metrics = {
                'creator_id': creator_id,
                'analysis_period_hours': hours,
                'interaction_summary': {},
                'performance_metrics': {},
                'recommendations': []
            }
            
            # Simulate interaction summary
            interaction_types = [t.value for t in CreatorInteractionType]
            creator_metrics['interaction_summary'] = {
                interaction_type: {
                    'count': np.random.randint(10, 100),
                    'avg_latency': np.random.uniform(50, 300),
                    'success_rate': np.random.uniform(0.95, 0.99)
                }
                for interaction_type in interaction_types
            }
            
            # Performance metrics from hot paths
            creator_hot_paths = [
                hp for hp in self.hot_path_metrics.values()
                if hp.model_id in ['content_classifier', 'recommendation_engine']  # Common creator models
            ]
            
            if creator_hot_paths:
                avg_latency = statistics.mean([hp.avg_latency for hp in creator_hot_paths])
                avg_error_rate = statistics.mean([hp.error_rate for hp in creator_hot_paths])
                
                creator_metrics['performance_metrics'] = {
                    'average_latency': avg_latency,
                    'error_rate': avg_error_rate,
                    'cache_efficiency': statistics.mean([hp.cache_hit_rate for hp in creator_hot_paths])
                }
                
                # Generate recommendations
                if avg_latency > 200:
                    creator_metrics['recommendations'].append("Consider upgrading to premium tier for better latency")
                if avg_error_rate > 0.01:
                    creator_metrics['recommendations'].append("Review content quality to reduce processing errors")
            
            return creator_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting creator interaction analytics: {e}")
            return {}
    
    async def optimize_collection_performance(self) -> Dict[str, Any]:
        """Optimisation performance collecte"""
        try:
            optimization_results = {
                'timestamp': datetime.utcnow().isoformat(),
                'optimizations_applied': [],
                'performance_improvement': {},
                'recommendations': []
            }
            
            # Check buffer usage and resize if needed
            current_usage = self.metric_buffer.qsize()
            usage_ratio = current_usage / self.streaming_config['buffer_size']
            
            if usage_ratio > 0.8:
                # Increase buffer size
                new_size = int(self.streaming_config['buffer_size'] * 1.5)
                self.streaming_config['buffer_size'] = new_size
                optimization_results['optimizations_applied'].append(f"Increased buffer size to {new_size}")
            
            # Optimize processing interval based on load
            if self.processing_times:
                avg_processing_time = statistics.mean(list(self.processing_times)[-100:])
                if avg_processing_time > self.streaming_config['max_processing_latency_ms']:
                    # Decrease processing interval for more frequent processing
                    new_interval = max(5, self.streaming_config['processing_interval_ms'] - 2)
                    self.streaming_config['processing_interval_ms'] = new_interval
                    optimization_results['optimizations_applied'].append(f"Decreased processing interval to {new_interval}ms")
            
            # Optimize batch size
            if self.metrics_processed > 1000:
                # Increase batch size for better throughput
                new_batch_size = min(200, self.streaming_config['batch_size'] + 20)
                self.streaming_config['batch_size'] = new_batch_size
                optimization_results['optimizations_applied'].append(f"Increased batch size to {new_batch_size}")
            
            # Performance improvement calculation
            if self.processing_times and len(self.processing_times) > 50:
                recent_times = list(self.processing_times)[-25:]
                older_times = list(self.processing_times)[-50:-25]
                
                if older_times:
                    recent_avg = statistics.mean(recent_times)
                    older_avg = statistics.mean(older_times)
                    improvement = ((older_avg - recent_avg) / older_avg) * 100 if older_avg > 0 else 0
                    
                    optimization_results['performance_improvement'] = {
                        'processing_time_improvement_percent': improvement,
                        'current_avg_processing_time_ms': recent_avg,
                        'previous_avg_processing_time_ms': older_avg
                    }
            
            # Generate recommendations
            error_rate = self.error_count / max(1, self.metrics_processed)
            if error_rate > 0.005:
                optimization_results['recommendations'].append("High error rate detected - review metric validation")
            
            if len(self.streaming_windows) > 100:
                optimization_results['recommendations'].append("Consider implementing window lifecycle management")
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Error optimizing collection performance: {e}")
            return {}
    
    async def stop_collection(self):
        """Arrêt collecte"""
        try:
            self._collecting = False
            
            # Cancel processing tasks
            for task in self._processing_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self._processing_tasks.clear()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            self.logger.info("⏹️ Real-time inference metrics collection stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping collection: {e}")
    
    async def shutdown(self):
        """Arrêt propre du collecteur"""
        self.logger.info("⏹️ Arrêt Real-Time Inference Metrics Collector...")
        
        # Stop collection
        await self.stop_collection()
        
        # Clear data
        while not self.metric_buffer.empty():
            try:
                self.metric_buffer.get_nowait()
            except queue.Empty:
                break
        
        self.streaming_windows.clear()
        self.hot_path_metrics.clear()
        self.edge_metrics.clear()
        self.alert_thresholds.clear()
        
        self.logger.info("✅ Real-Time Inference Metrics Collector arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_realtime_collector():
        config = {
            'debug': True,
            'buffer_size': 1000
        }
        
        collector = RealTimeInferenceMetricsCollector(config)
        
        # Start collection
        success = await collector.start_collection()
        print(f"Collection started: {success}")
        
        # Add some alert thresholds
        def latency_alert(metric: InferenceMetric):
            print(f"⚠️ High latency alert: {metric.value}ms for model {metric.model_id}")
        
        threshold_id = collector.add_alert_threshold(
            MetricType.LATENCY, "*", "gt", 500.0, latency_alert
        )
        print(f"Alert threshold added: {threshold_id}")
        
        # Simulate collecting metrics
        for i in range(100):
            collector.collect_metric(
                model_id="test_model_001",
                creator_id="creator_001",
                interaction_type=CreatorInteractionType.CONTENT_UPLOAD,
                metric_type=MetricType.LATENCY,
                value=np.random.uniform(50, 600),
                unit="ms",
                priority=MetricPriority.HIGH,
                context={'creator_tier': 'premium'}
            )
            
            collector.collect_metric(
                model_id="test_model_001",
                creator_id="creator_001",
                interaction_type=CreatorInteractionType.CONTENT_UPLOAD,
                metric_type=MetricType.THROUGHPUT,
                value=np.random.uniform(10, 100),
                unit="rps"
            )
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Get real-time metrics
        metrics = await collector.get_real_time_metrics("test_model_001")
        print(f"Real-time metrics: {len(metrics['streaming_windows'])} windows, {len(metrics['hot_path_metrics'])} hot paths")
        
        # Get creator analytics
        analytics = await collector.get_creator_interaction_analytics("creator_001")
        print(f"Creator analytics: {len(analytics['interaction_summary'])} interaction types")
        
        # Optimize performance
        optimization = await collector.optimize_collection_performance()
        print(f"Optimization: {len(optimization['optimizations_applied'])} optimizations applied")
        
        print('✅ Real-Time Inference Metrics Collector test passed')
        await collector.shutdown()
    
    asyncio.run(test_realtime_collector())