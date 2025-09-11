"""Training Metrics Collector for Ainflue ML Platform

Comprehensive training metrics collection and real-time monitoring for ML models
with creator-specific metrics and enterprise-grade analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import time
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
import psutil
import threading
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric type enumeration."""
    LOSS = "loss"
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    LEARNING_RATE = "learning_rate"
    GRADIENT_NORM = "gradient_norm"
    WEIGHT_NORM = "weight_norm"
    BATCH_TIME = "batch_time"
    DATA_LOADING_TIME = "data_loading_time"
    GPU_UTILIZATION = "gpu_utilization"
    MEMORY_USAGE = "memory_usage"
    CREATOR_ENGAGEMENT = "creator_engagement"
    CONTENT_QUALITY = "content_quality"


class AggregationType(Enum):
    """Aggregation type enumeration."""
    MEAN = "mean"
    SUM = "sum"
    MIN = "min"
    MAX = "max"
    STD = "std"
    MEDIAN = "median"
    PERCENTILE_95 = "percentile_95"
    PERCENTILE_99 = "percentile_99"
    LAST = "last"
    FIRST = "first"


@dataclass
class MetricConfig:
    """Configuration for metric collection."""
    # Basic settings
    collect_interval: float = 1.0  # seconds
    buffer_size: int = 10000
    auto_save_interval: int = 100  # batches
    
    # Metric categories
    collect_training_metrics: bool = True
    collect_validation_metrics: bool = True
    collect_system_metrics: bool = True
    collect_creator_metrics: bool = True
    
    # Storage settings
    save_to_disk: bool = True
    metrics_dir: str = "metrics"
    export_formats: List[str] = field(default_factory=lambda: ["json", "csv"])
    
    # Visualization settings
    enable_real_time_plots: bool = False
    plot_update_interval: int = 10  # batches
    
    # Creator-specific settings
    creator_specific_tracking: bool = True
    engagement_metrics: bool = True
    content_quality_metrics: bool = True
    
    # Alert settings
    enable_alerts: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "loss_spike": 2.0,  # Alert if loss increases by this factor
        "gradient_explosion": 10.0,  # Alert if gradient norm exceeds this
        "memory_usage": 0.9,  # Alert if memory usage exceeds 90%
        "accuracy_drop": 0.1  # Alert if accuracy drops by this amount
    })


@dataclass
class MetricData:
    """Data structure for a single metric."""
    name: str
    value: Union[float, int, str]
    timestamp: datetime
    epoch: int
    batch: int
    phase: str  # train, validation, test
    creator_id: Optional[str] = None
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetrics:
    """Aggregated metrics over a time period."""
    metric_name: str
    aggregation_type: AggregationType
    value: float
    count: int
    start_time: datetime
    end_time: datetime
    creator_id: Optional[str] = None


class MetricBuffer:
    """Thread-safe buffer for storing metrics."""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.Lock()
        
    def add(self, metric: MetricData):
        """Add metric to buffer."""
        with self.lock:
            self.buffer.append(metric)
    
    def get_all(self) -> List[MetricData]:
        """Get all metrics from buffer."""
        with self.lock:
            return list(self.buffer)
    
    def get_recent(self, n: int) -> List[MetricData]:
        """Get n most recent metrics."""
        with self.lock:
            return list(self.buffer)[-n:] if len(self.buffer) >= n else list(self.buffer)
    
    def clear(self):
        """Clear buffer."""
        with self.lock:
            self.buffer.clear()
    
    def size(self) -> int:
        """Get buffer size."""
        with self.lock:
            return len(self.buffer)


class SystemMetricsCollector:
    """Collects system metrics like GPU, memory, CPU usage."""
    
    def __init__(self):
        self.gpu_available = torch.cuda.is_available()
        self.device_count = torch.cuda.device_count() if self.gpu_available else 0
        
    async def collect_metrics(self) -> Dict[str, float]:
        """Collect current system metrics."""
        metrics = {}
        
        # CPU metrics
        metrics['cpu_percent'] = psutil.cpu_percent(interval=0.1)
        metrics['cpu_count'] = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics['memory_percent'] = memory.percent
        metrics['memory_available_gb'] = memory.available / (1024**3)
        metrics['memory_used_gb'] = memory.used / (1024**3)
        
        # GPU metrics
        if self.gpu_available:
            for i in range(self.device_count):
                try:
                    # GPU memory
                    gpu_memory = torch.cuda.memory_stats(i)
                    allocated = gpu_memory.get('allocated_bytes.all.current', 0) / (1024**3)
                    cached = gpu_memory.get('reserved_bytes.all.current', 0) / (1024**3)
                    
                    metrics[f'gpu_{i}_memory_allocated_gb'] = allocated
                    metrics[f'gpu_{i}_memory_cached_gb'] = cached
                    
                    # GPU utilization (approximation)
                    metrics[f'gpu_{i}_utilization'] = torch.cuda.utilization(i) if hasattr(torch.cuda, 'utilization') else 0.0
                    
                except Exception as e:
                    logger.warning(f"Failed to collect GPU {i} metrics: {e}")
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics['disk_percent'] = (disk.used / disk.total) * 100
        metrics['disk_free_gb'] = disk.free / (1024**3)
        
        return metrics


class ModelMetricsExtractor:
    """Extracts metrics from PyTorch models."""
    
    def __init__(self):
        pass
    
    async def extract_model_metrics(
        self,
        model: nn.Module,
        loss: Optional[torch.Tensor] = None,
        optimizer: Optional[torch.optim.Optimizer] = None
    ) -> Dict[str, float]:
        """Extract metrics from model, loss, and optimizer."""
        metrics = {}
        
        # Model parameter metrics
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        metrics['total_parameters'] = total_params
        metrics['trainable_parameters'] = trainable_params
        
        # Weight statistics
        weight_norms = []
        gradient_norms = []
        
        for name, param in model.named_parameters():
            if param.requires_grad:
                # Weight norm
                weight_norm = torch.norm(param.data).item()
                weight_norms.append(weight_norm)
                metrics[f'weight_norm_{name}'] = weight_norm
                
                # Gradient norm
                if param.grad is not None:
                    grad_norm = torch.norm(param.grad.data).item()
                    gradient_norms.append(grad_norm)
                    metrics[f'gradient_norm_{name}'] = grad_norm
        
        # Aggregate norms
        if weight_norms:
            metrics['avg_weight_norm'] = np.mean(weight_norms)
            metrics['max_weight_norm'] = np.max(weight_norms)
            metrics['total_weight_norm'] = np.sum(weight_norms)
        
        if gradient_norms:
            metrics['avg_gradient_norm'] = np.mean(gradient_norms)
            metrics['max_gradient_norm'] = np.max(gradient_norms)
            metrics['total_gradient_norm'] = np.sum(gradient_norms)
        
        # Loss metrics
        if loss is not None:
            metrics['loss_value'] = loss.item()
        
        # Optimizer metrics
        if optimizer is not None:
            for group_idx, param_group in enumerate(optimizer.param_groups):
                lr = param_group.get('lr', 0.0)
                metrics[f'learning_rate_group_{group_idx}'] = lr
                
                # Momentum if available
                if 'momentum' in param_group:
                    metrics[f'momentum_group_{group_idx}'] = param_group['momentum']
                
                # Weight decay if available
                if 'weight_decay' in param_group:
                    metrics[f'weight_decay_group_{group_idx}'] = param_group['weight_decay']
        
        return metrics


class CreatorMetricsCalculator:
    """Calculates creator-specific metrics."""
    
    def __init__(self):
        self.creator_histories = defaultdict(list)
        
    async def calculate_creator_metrics(
        self,
        creator_id: str,
        content_type: str,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        engagement_data: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """Calculate creator-specific metrics."""
        metrics = {}
        
        # Basic performance metrics
        with torch.no_grad():
            if predictions.dim() > 1 and predictions.size(1) > 1:
                # Classification metrics
                pred_classes = torch.argmax(predictions, dim=1)
                accuracy = (pred_classes == targets).float().mean().item()
                metrics['creator_accuracy'] = accuracy
                
                # Confidence metrics
                confidence = torch.max(torch.softmax(predictions, dim=1), dim=1)[0]
                metrics['avg_confidence'] = confidence.mean().item()
                metrics['min_confidence'] = confidence.min().item()
                metrics['max_confidence'] = confidence.max().item()
            else:
                # Regression metrics
                mse = torch.mean((predictions - targets) ** 2).item()
                mae = torch.mean(torch.abs(predictions - targets)).item()
                metrics['creator_mse'] = mse
                metrics['creator_mae'] = mae
        
        # Content-type specific metrics
        if content_type == "audio":
            metrics.update(await self._calculate_audio_metrics(predictions, targets))
        elif content_type == "image":
            metrics.update(await self._calculate_image_metrics(predictions, targets))
        elif content_type == "text":
            metrics.update(await self._calculate_text_metrics(predictions, targets))
        
        # Engagement metrics
        if engagement_data:
            metrics.update(self._calculate_engagement_metrics(engagement_data))
        
        # Historical comparison
        self.creator_histories[creator_id].append(metrics.copy())
        if len(self.creator_histories[creator_id]) > 1:
            historical_metrics = self._calculate_historical_metrics(creator_id)
            metrics.update(historical_metrics)
        
        return metrics
    
    async def _calculate_audio_metrics(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor
    ) -> Dict[str, float]:
        """Calculate audio-specific metrics."""
        metrics = {}
        
        # Audio quality metrics (simplified)
        if predictions.dim() > 1:
            # Spectral metrics
            spectral_centroid = torch.mean(predictions * torch.arange(predictions.size(-1), dtype=torch.float32), dim=-1)
            metrics['spectral_centroid'] = spectral_centroid.mean().item()
            
            # Dynamic range
            dynamic_range = torch.max(predictions, dim=-1)[0] - torch.min(predictions, dim=-1)[0]
            metrics['dynamic_range'] = dynamic_range.mean().item()
        
        return metrics
    
    async def _calculate_image_metrics(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor
    ) -> Dict[str, float]:
        """Calculate image-specific metrics."""
        metrics = {}
        
        # Visual quality metrics (simplified)
        if predictions.dim() > 2:
            # Contrast metrics
            std_dev = torch.std(predictions, dim=(-2, -1))
            metrics['avg_contrast'] = std_dev.mean().item()
            
            # Brightness metrics
            brightness = torch.mean(predictions, dim=(-2, -1))
            metrics['avg_brightness'] = brightness.mean().item()
        
        return metrics
    
    async def _calculate_text_metrics(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor
    ) -> Dict[str, float]:
        """Calculate text-specific metrics."""
        metrics = {}
        
        # Text quality metrics (simplified)
        if predictions.dim() > 1:
            # Vocabulary diversity
            entropy = -torch.sum(torch.softmax(predictions, dim=-1) * torch.log_softmax(predictions, dim=-1), dim=-1)
            metrics['text_entropy'] = entropy.mean().item()
            
            # Perplexity
            perplexity = torch.exp(entropy)
            metrics['perplexity'] = perplexity.mean().item()
        
        return metrics
    
    def _calculate_engagement_metrics(self, engagement_data: Dict[str, float]) -> Dict[str, float]:
        """Calculate engagement-based metrics."""
        metrics = {}
        
        # Normalize engagement scores
        engagement_weights = {
            'likes': 1.0,
            'comments': 2.0,
            'shares': 3.0,
            'saves': 2.5,
            'view_time': 1.5
        }
        
        total_engagement = 0.0
        total_weight = 0.0
        
        for metric, value in engagement_data.items():
            weight = engagement_weights.get(metric, 1.0)
            total_engagement += value * weight
            total_weight += weight
        
        if total_weight > 0:
            metrics['weighted_engagement_score'] = total_engagement / total_weight
        
        # Individual engagement metrics
        metrics.update({f'engagement_{k}': v for k, v in engagement_data.items()})
        
        return metrics
    
    def _calculate_historical_metrics(self, creator_id: str) -> Dict[str, float]:
        """Calculate metrics comparing to historical performance."""
        history = self.creator_histories[creator_id]
        if len(history) < 2:
            return {}
        
        metrics = {}
        current = history[-1]
        previous = history[-2]
        
        # Calculate trends
        for metric_name, current_value in current.items():
            if metric_name in previous and isinstance(current_value, (int, float)):
                previous_value = previous[metric_name]
                if previous_value != 0:
                    change_percent = ((current_value - previous_value) / previous_value) * 100
                    metrics[f'{metric_name}_trend_percent'] = change_percent
        
        # Calculate moving averages
        if len(history) >= 5:
            for metric_name in current.keys():
                if isinstance(current[metric_name], (int, float)):
                    recent_values = [h[metric_name] for h in history[-5:] if metric_name in h and isinstance(h[metric_name], (int, float))]
                    if recent_values:
                        metrics[f'{metric_name}_ma5'] = np.mean(recent_values)
        
        return metrics


class AlertManager:
    """Manages alerts based on metric thresholds."""
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.alert_history = []
        
    async def check_alerts(self, metrics: List[MetricData]) -> List[Dict[str, Any]]:
        """Check metrics against alert thresholds."""
        alerts = []
        
        if not self.config.enable_alerts:
            return alerts
        
        for metric in metrics:
            alert = await self._check_metric_alert(metric)
            if alert:
                alerts.append(alert)
        
        return alerts
    
    async def _check_metric_alert(self, metric: MetricData) -> Optional[Dict[str, Any]]:
        """Check individual metric for alerts."""
        if not isinstance(metric.value, (int, float)):
            return None
        
        alert = None
        
        # Loss spike detection
        if 'loss' in metric.name.lower():
            threshold = self.config.alert_thresholds.get('loss_spike', 2.0)
            if self._is_spike(metric.name, metric.value, threshold):
                alert = {
                    'type': 'loss_spike',
                    'metric': metric.name,
                    'value': metric.value,
                    'threshold': threshold,
                    'timestamp': metric.timestamp,
                    'severity': 'high'
                }
        
        # Gradient explosion detection
        elif 'gradient_norm' in metric.name.lower():
            threshold = self.config.alert_thresholds.get('gradient_explosion', 10.0)
            if metric.value > threshold:
                alert = {
                    'type': 'gradient_explosion',
                    'metric': metric.name,
                    'value': metric.value,
                    'threshold': threshold,
                    'timestamp': metric.timestamp,
                    'severity': 'critical'
                }
        
        # Memory usage alert
        elif 'memory_percent' in metric.name.lower():
            threshold = self.config.alert_thresholds.get('memory_usage', 0.9) * 100
            if metric.value > threshold:
                alert = {
                    'type': 'high_memory_usage',
                    'metric': metric.name,
                    'value': metric.value,
                    'threshold': threshold,
                    'timestamp': metric.timestamp,
                    'severity': 'medium'
                }
        
        # Accuracy drop detection
        elif 'accuracy' in metric.name.lower():
            threshold = self.config.alert_thresholds.get('accuracy_drop', 0.1)
            if self._is_drop(metric.name, metric.value, threshold):
                alert = {
                    'type': 'accuracy_drop',
                    'metric': metric.name,
                    'value': metric.value,
                    'threshold': threshold,
                    'timestamp': metric.timestamp,
                    'severity': 'high'
                }
        
        if alert:
            self.alert_history.append(alert)
            logger.warning(f"Alert triggered: {alert['type']} - {alert['metric']}: {alert['value']}")
        
        return alert
    
    def _is_spike(self, metric_name: str, current_value: float, threshold: float) -> bool:
        """Check if current value is a spike compared to recent history."""
        # Get recent values for this metric
        recent_alerts = [a for a in self.alert_history[-10:] if a['metric'] == metric_name]
        if not recent_alerts:
            return False
        
        recent_values = [a['value'] for a in recent_alerts]
        avg_recent = np.mean(recent_values)
        
        return current_value > avg_recent * threshold
    
    def _is_drop(self, metric_name: str, current_value: float, threshold: float) -> bool:
        """Check if current value is a significant drop."""
        recent_alerts = [a for a in self.alert_history[-10:] if a['metric'] == metric_name]
        if not recent_alerts:
            return False
        
        recent_values = [a['value'] for a in recent_alerts]
        max_recent = max(recent_values)
        
        return (max_recent - current_value) > threshold


class MetricsVisualizer:
    """Creates real-time visualizations of training metrics."""
    
    def __init__(self, config: MetricConfig):
        self.config = config
        self.plots = {}
        
    async def create_real_time_plot(self, metrics: List[MetricData], metric_name: str):
        """Create real-time plot for a specific metric."""
        if not self.config.enable_real_time_plots:
            return
        
        # Filter metrics by name
        filtered_metrics = [m for m in metrics if m.name == metric_name]
        if not filtered_metrics:
            return
        
        # Extract values and timestamps
        values = [m.value for m in filtered_metrics if isinstance(m.value, (int, float))]
        timestamps = [m.timestamp for m in filtered_metrics if isinstance(m.value, (int, float))]
        
        if not values:
            return
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, values, label=metric_name)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title(f'Real-time {metric_name}')
        plt.legend()
        plt.grid(True)
        
        # Save plot
        plot_path = Path(self.config.metrics_dir) / f"{metric_name}_realtime.png"
        plot_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(plot_path)
        plt.close()
    
    async def create_comparison_plot(
        self,
        metrics: List[MetricData],
        metric_names: List[str],
        group_by: str = "phase"
    ):
        """Create comparison plot for multiple metrics."""
        plt.figure(figsize=(12, 8))
        
        for metric_name in metric_names:
            # Filter metrics by name
            filtered_metrics = [m for m in metrics if m.name == metric_name]
            
            if group_by == "phase":
                phases = set(m.phase for m in filtered_metrics)
                for phase in phases:
                    phase_metrics = [m for m in filtered_metrics if m.phase == phase]
                    values = [m.value for m in phase_metrics if isinstance(m.value, (int, float))]
                    timestamps = [m.timestamp for m in phase_metrics if isinstance(m.value, (int, float))]
                    
                    if values:
                        plt.plot(timestamps, values, label=f"{metric_name} ({phase})")
        
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title('Metrics Comparison')
        plt.legend()
        plt.grid(True)
        
        # Save plot
        plot_path = Path(self.config.metrics_dir) / "comparison_plot.png"
        plot_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(plot_path)
        plt.close()


class TrainingMetricsCollector:
    """Main training metrics collector."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        self.config = config or MetricConfig()
        
        # Initialize components
        self.metric_buffer = MetricBuffer(self.config.buffer_size)
        self.system_collector = SystemMetricsCollector()
        self.model_extractor = ModelMetricsExtractor()
        self.creator_calculator = CreatorMetricsCalculator()
        self.alert_manager = AlertManager(self.config)
        self.visualizer = MetricsVisualizer(self.config)
        
        # State tracking
        self.current_epoch = 0
        self.current_batch = 0
        self.collection_active = False
        self.last_save_batch = 0
        
        # Aggregation state
        self.aggregated_metrics: Dict[str, List[float]] = defaultdict(list)
        
        logger.info("Initialized TrainingMetricsCollector")
    
    async def start_collection(self):
        """Start metrics collection."""
        self.collection_active = True
        logger.info("Started metrics collection")
    
    async def stop_collection(self):
        """Stop metrics collection."""
        self.collection_active = False
        await self.save_metrics()
        logger.info("Stopped metrics collection")
    
    async def collect_batch_metrics(
        self,
        model: nn.Module,
        loss: torch.Tensor,
        optimizer: torch.optim.Optimizer,
        phase: str = "train",
        creator_id: Optional[str] = None,
        content_type: Optional[str] = None,
        predictions: Optional[torch.Tensor] = None,
        targets: Optional[torch.Tensor] = None,
        engagement_data: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """Collect metrics for a training batch."""
        if not self.collection_active:
            return
        
        timestamp = datetime.now()
        metrics_collected = []
        
        try:
            # Model metrics
            if self.config.collect_training_metrics:
                model_metrics = await self.model_extractor.extract_model_metrics(
                    model, loss, optimizer
                )
                
                for name, value in model_metrics.items():
                    metric = MetricData(
                        name=name,
                        value=value,
                        timestamp=timestamp,
                        epoch=self.current_epoch,
                        batch=self.current_batch,
                        phase=phase,
                        creator_id=creator_id,
                        content_type=content_type
                    )
                    self.metric_buffer.add(metric)
                    metrics_collected.append(metric)
            
            # System metrics
            if self.config.collect_system_metrics:
                system_metrics = await self.system_collector.collect_metrics()
                
                for name, value in system_metrics.items():
                    metric = MetricData(
                        name=name,
                        value=value,
                        timestamp=timestamp,
                        epoch=self.current_epoch,
                        batch=self.current_batch,
                        phase=phase,
                        creator_id=creator_id,
                        content_type=content_type
                    )
                    self.metric_buffer.add(metric)
                    metrics_collected.append(metric)
            
            # Creator-specific metrics
            if (self.config.collect_creator_metrics and 
                creator_id and predictions is not None and targets is not None):
                creator_metrics = await self.creator_calculator.calculate_creator_metrics(
                    creator_id, content_type or "general", predictions, targets, engagement_data
                )
                
                for name, value in creator_metrics.items():
                    metric = MetricData(
                        name=f"creator_{name}",
                        value=value,
                        timestamp=timestamp,
                        epoch=self.current_epoch,
                        batch=self.current_batch,
                        phase=phase,
                        creator_id=creator_id,
                        content_type=content_type
                    )
                    self.metric_buffer.add(metric)
                    metrics_collected.append(metric)
            
            # Custom metrics from kwargs
            for name, value in kwargs.items():
                if isinstance(value, (int, float, str)):
                    metric = MetricData(
                        name=f"custom_{name}",
                        value=value,
                        timestamp=timestamp,
                        epoch=self.current_epoch,
                        batch=self.current_batch,
                        phase=phase,
                        creator_id=creator_id,
                        content_type=content_type
                    )
                    self.metric_buffer.add(metric)
                    metrics_collected.append(metric)
            
            # Check alerts
            alerts = await self.alert_manager.check_alerts(metrics_collected)
            if alerts:
                logger.warning(f"Generated {len(alerts)} alerts for batch {self.current_batch}")
            
            # Auto-save
            if (self.current_batch - self.last_save_batch) >= self.config.auto_save_interval:
                await self.save_metrics()
                self.last_save_batch = self.current_batch
            
            # Update aggregations
            self._update_aggregations(metrics_collected)
            
            self.current_batch += 1
            
        except Exception as e:
            logger.error(f"Error collecting batch metrics: {e}")
    
    async def collect_epoch_metrics(
        self,
        validation_metrics: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        """Collect metrics at the end of an epoch."""
        timestamp = datetime.now()
        
        # Validation metrics
        if validation_metrics and self.config.collect_validation_metrics:
            for name, value in validation_metrics.items():
                metric = MetricData(
                    name=f"epoch_{name}",
                    value=value,
                    timestamp=timestamp,
                    epoch=self.current_epoch,
                    batch=self.current_batch,
                    phase="validation",
                    metadata={"epoch_summary": True}
                )
                self.metric_buffer.add(metric)
        
        # Custom epoch metrics
        for name, value in kwargs.items():
            if isinstance(value, (int, float, str)):
                metric = MetricData(
                    name=f"epoch_{name}",
                    value=value,
                    timestamp=timestamp,
                    epoch=self.current_epoch,
                    batch=self.current_batch,
                    phase="validation",
                    metadata={"epoch_summary": True}
                )
                self.metric_buffer.add(metric)
        
        self.current_epoch += 1
        logger.info(f"Collected epoch {self.current_epoch} metrics")
    
    def _update_aggregations(self, metrics: List[MetricData]):
        """Update metric aggregations."""
        for metric in metrics:
            if isinstance(metric.value, (int, float)):
                self.aggregated_metrics[metric.name].append(metric.value)
                
                # Keep only recent values
                if len(self.aggregated_metrics[metric.name]) > 1000:
                    self.aggregated_metrics[metric.name] = self.aggregated_metrics[metric.name][-500:]
    
    async def get_aggregated_metrics(
        self,
        metric_name: str,
        aggregation_type: AggregationType = AggregationType.MEAN,
        lookback_batches: Optional[int] = None
    ) -> Optional[AggregatedMetrics]:
        """Get aggregated metrics."""
        if metric_name not in self.aggregated_metrics:
            return None
        
        values = self.aggregated_metrics[metric_name]
        if lookback_batches:
            values = values[-lookback_batches:]
        
        if not values:
            return None
        
        # Calculate aggregation
        if aggregation_type == AggregationType.MEAN:
            result = np.mean(values)
        elif aggregation_type == AggregationType.SUM:
            result = np.sum(values)
        elif aggregation_type == AggregationType.MIN:
            result = np.min(values)
        elif aggregation_type == AggregationType.MAX:
            result = np.max(values)
        elif aggregation_type == AggregationType.STD:
            result = np.std(values)
        elif aggregation_type == AggregationType.MEDIAN:
            result = np.median(values)
        elif aggregation_type == AggregationType.PERCENTILE_95:
            result = np.percentile(values, 95)
        elif aggregation_type == AggregationType.PERCENTILE_99:
            result = np.percentile(values, 99)
        elif aggregation_type == AggregationType.LAST:
            result = values[-1]
        elif aggregation_type == AggregationType.FIRST:
            result = values[0]
        else:
            result = np.mean(values)
        
        return AggregatedMetrics(
            metric_name=metric_name,
            aggregation_type=aggregation_type,
            value=float(result),
            count=len(values),
            start_time=datetime.now() - timedelta(seconds=len(values)),
            end_time=datetime.now()
        )
    
    async def save_metrics(self):
        """Save metrics to disk."""
        if not self.config.save_to_disk:
            return
        
        metrics = self.metric_buffer.get_all()
        if not metrics:
            return
        
        # Create metrics directory
        metrics_dir = Path(self.config.metrics_dir)
        metrics_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save in requested formats
        if "json" in self.config.export_formats:
            await self._save_json(metrics, metrics_dir / f"metrics_{timestamp}.json")
        
        if "csv" in self.config.export_formats:
            await self._save_csv(metrics, metrics_dir / f"metrics_{timestamp}.csv")
        
        logger.info(f"Saved {len(metrics)} metrics to {metrics_dir}")
    
    async def _save_json(self, metrics: List[MetricData], filepath: Path):
        """Save metrics as JSON."""
        data = []
        for metric in metrics:
            data.append({
                'name': metric.name,
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'epoch': metric.epoch,
                'batch': metric.batch,
                'phase': metric.phase,
                'creator_id': metric.creator_id,
                'content_type': metric.content_type,
                'metadata': metric.metadata
            })
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def _save_csv(self, metrics: List[MetricData], filepath: Path):
        """Save metrics as CSV."""
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'name', 'value', 'timestamp', 'epoch', 'batch', 'phase',
                'creator_id', 'content_type', 'metadata'
            ])
            
            # Data
            for metric in metrics:
                writer.writerow([
                    metric.name,
                    metric.value,
                    metric.timestamp.isoformat(),
                    metric.epoch,
                    metric.batch,
                    metric.phase,
                    metric.creator_id or '',
                    metric.content_type or '',
                    json.dumps(metric.metadata) if metric.metadata else ''
                ])
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        metrics = self.metric_buffer.get_all()
        
        summary = {
            'total_metrics': len(metrics),
            'current_epoch': self.current_epoch,
            'current_batch': self.current_batch,
            'collection_active': self.collection_active,
            'buffer_utilization': self.metric_buffer.size() / self.config.buffer_size,
            'metrics_by_type': defaultdict(int),
            'metrics_by_phase': defaultdict(int),
            'creators_tracked': set(),
            'recent_alerts': len(self.alert_manager.alert_history[-10:])
        }
        
        for metric in metrics:
            summary['metrics_by_type'][metric.name.split('_')[0]] += 1
            summary['metrics_by_phase'][metric.phase] += 1
            if metric.creator_id:
                summary['creators_tracked'].add(metric.creator_id)
        
        summary['creators_tracked'] = len(summary['creators_tracked'])
        
        return summary


# Factory function for easy instantiation
def create_metrics_collector(
    collect_interval: float = 1.0,
    buffer_size: int = 10000,
    **kwargs
) -> TrainingMetricsCollector:
    """Factory function to create training metrics collector."""
    config = MetricConfig(
        collect_interval=collect_interval,
        buffer_size=buffer_size,
        **kwargs
    )
    return TrainingMetricsCollector(config)


# Example usage for Ainflue creators
async def example_metrics_collection():
    """Example of metrics collection for creator training."""
    
    # Create metrics collector
    collector = create_metrics_collector(
        collect_interval=1.0,
        buffer_size=5000,
        collect_creator_metrics=True,
        enable_alerts=True,
        save_to_disk=True
    )
    
    await collector.start_collection()
    
    logger.info("Training metrics collector ready for creator model monitoring")
    
    return collector


if __name__ == "__main__":
    # Run example
    asyncio.run(example_metrics_collection())