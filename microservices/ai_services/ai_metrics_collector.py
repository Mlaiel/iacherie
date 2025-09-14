"""
AI Metrics Collector Service - Enterprise AI Performance Monitoring
Ainflue Platform - Microservices Architecture

© FAHED MLAIEL 2024-2025 - CONFIDENTIAL ENTERPRISE MODULE
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import json

@dataclass
class AIMetric:
    """AI metric data point"""
    metric_name: str
    value: float
    timestamp: datetime
    service_name: str
    model_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None

@dataclass
class AIPerformanceMetrics:
    """AI service performance metrics"""
    service_name: str
    model_id: str
    inference_latency_ms: float
    throughput_rps: float
    accuracy_score: float
    memory_usage_mb: float
    gpu_utilization_percent: float
    error_rate_percent: float
    availability_percent: float
    total_requests: int
    timestamp: datetime

@dataclass
class AIResourceMetrics:
    """AI resource utilization metrics"""
    cpu_usage_percent: float
    memory_usage_mb: float
    gpu_memory_mb: float
    gpu_utilization_percent: float
    disk_io_mbps: float
    network_io_mbps: float
    active_models: int
    queue_length: int
    timestamp: datetime

class AIMetricsCollector:
    """
    Enterprise AI Metrics Collector Service
    
    Collects, aggregates, and provides real-time metrics for AI services
    including performance, resource utilization, model accuracy, and
    system health across distributed AI infrastructure.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.performance_metrics = {}
        self.resource_metrics = {}
        self.aggregated_metrics = {}
        self.collection_interval = 5  # seconds
        self.is_collecting = False
        
    async def initialize(self) -> bool:
        """Initialize AI metrics collector"""
        try:
            self.logger.info("Initializing AI Metrics Collector Service...")
            
            # Initialize metric storage
            await self._initialize_metric_storage()
            
            # Setup metric collection
            await self._setup_metric_collection()
            
            # Start background collection
            self.collection_task = asyncio.create_task(self._start_collection())
            
            self.logger.info("AI Metrics Collector Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Metrics Collector: {e}")
            return False
    
    async def _initialize_metric_storage(self):
        """Initialize metric storage systems"""
        self.metric_types = {
            'performance': ['latency', 'throughput', 'accuracy', 'error_rate'],
            'resource': ['cpu_usage', 'memory_usage', 'gpu_usage', 'disk_io'],
            'model': ['inference_time', 'prediction_confidence', 'model_size'],
            'business': ['total_requests', 'active_users', 'revenue_impact']
        }
        
        # Initialize metric buffers
        for metric_type in self.metric_types:
            for metric_name in self.metric_types[metric_type]:
                self.metrics_buffer[f"{metric_type}.{metric_name}"] = deque(maxlen=1000)
    
    async def _setup_metric_collection(self):
        """Setup metric collection configuration"""
        self.collection_config = {
            'ai_inference_service': {
                'enabled': True,
                'metrics': ['latency', 'throughput', 'accuracy'],
                'interval': 5
            },
            'ai_training_service': {
                'enabled': True,
                'metrics': ['training_loss', 'validation_accuracy', 'epoch_time'],
                'interval': 30
            },
            'ai_model_serving': {
                'enabled': True,
                'metrics': ['serving_latency', 'requests_per_second', 'error_rate'],
                'interval': 10
            },
            'ai_orchestration_service': {
                'enabled': True,
                'metrics': ['pipeline_duration', 'step_success_rate', 'resource_usage'],
                'interval': 15
            }
        }
    
    async def _start_collection(self):
        """Start continuous metric collection"""
        self.is_collecting = True
        
        try:
            while self.is_collecting:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect AI service metrics
                await self._collect_ai_service_metrics()
                
                # Collect model performance metrics
                await self._collect_model_metrics()
                
                # Update aggregated metrics
                await self._update_aggregated_metrics()
                
                await asyncio.sleep(self.collection_interval)
                
        except asyncio.CancelledError:
            self.is_collecting = False
        except Exception as e:
            self.logger.error(f"Metric collection error: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system resource metrics"""
        try:
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            self.add_metric('resource.cpu_usage', cpu_usage, 'system')
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage_mb = memory.used / (1024 * 1024)
            self.add_metric('resource.memory_usage', memory_usage_mb, 'system')
            
            # GPU metrics (simulated - would use nvidia-ml-py in production)
            gpu_usage = await self._get_gpu_metrics()
            self.add_metric('resource.gpu_usage', gpu_usage['utilization'], 'system')
            self.add_metric('resource.gpu_memory', gpu_usage['memory_used'], 'system')
            
            # Disk I/O metrics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_io_mbps = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)
                self.add_metric('resource.disk_io', disk_io_mbps, 'system')
            
            # Network I/O metrics
            network_io = psutil.net_io_counters()
            if network_io:
                network_io_mbps = (network_io.bytes_sent + network_io.bytes_recv) / (1024 * 1024)
                self.add_metric('resource.network_io', network_io_mbps, 'system')
                
        except Exception as e:
            self.logger.error(f"System metrics collection error: {e}")
    
    async def _get_gpu_metrics(self) -> Dict[str, float]:
        """Get GPU metrics (simulated)"""
        # In production, would use nvidia-ml-py or similar
        return {
            'utilization': 45.5,  # GPU utilization percentage
            'memory_used': 2048,  # GPU memory in MB
            'temperature': 65,    # GPU temperature in Celsius
            'power_usage': 180    # Power usage in watts
        }
    
    async def _collect_ai_service_metrics(self):
        """Collect AI service specific metrics"""
        for service_name, config in self.collection_config.items():
            if not config['enabled']:
                continue
                
            try:
                # Simulate AI service metrics collection
                metrics = await self._get_ai_service_metrics(service_name)
                
                for metric_name, value in metrics.items():
                    self.add_metric(f"performance.{metric_name}", value, service_name)
                    
            except Exception as e:
                self.logger.error(f"AI service metrics collection error for {service_name}: {e}")
    
    async def _get_ai_service_metrics(self, service_name: str) -> Dict[str, float]:
        """Get metrics for specific AI service"""
        # Simulate different metrics based on service
        base_metrics = {
            'ai_inference_service': {
                'latency': 45.2,           # milliseconds
                'throughput': 120.5,       # requests per second
                'accuracy': 0.945,         # accuracy score
                'error_rate': 0.02         # error rate percentage
            },
            'ai_training_service': {
                'training_loss': 0.123,    # training loss
                'validation_accuracy': 0.89, # validation accuracy
                'epoch_time': 345.6,       # epoch time in seconds
                'learning_rate': 0.001     # current learning rate
            },
            'ai_model_serving': {
                'serving_latency': 25.8,   # serving latency ms
                'requests_per_second': 85.3, # RPS
                'cache_hit_rate': 0.78,    # cache hit rate
                'model_load_time': 2.5     # model load time seconds
            },
            'ai_orchestration_service': {
                'pipeline_duration': 125.4, # pipeline duration seconds
                'step_success_rate': 0.98,  # step success rate
                'active_pipelines': 15,     # number of active pipelines
                'queue_depth': 8            # pipeline queue depth
            }
        }
        
        return base_metrics.get(service_name, {})
    
    async def _collect_model_metrics(self):
        """Collect individual model performance metrics"""
        # Simulate model metrics for different models
        models = [
            'content_classifier_v2',
            'text_sentiment_analyzer',
            'image_quality_detector',
            'audio_transcription_model',
            'video_content_analyzer'
        ]
        
        for model_id in models:
            try:
                metrics = await self._get_model_performance_metrics(model_id)
                
                performance_metrics = AIPerformanceMetrics(
                    service_name='ai_inference_service',
                    model_id=model_id,
                    inference_latency_ms=metrics['latency'],
                    throughput_rps=metrics['throughput'],
                    accuracy_score=metrics['accuracy'],
                    memory_usage_mb=metrics['memory_usage'],
                    gpu_utilization_percent=metrics['gpu_usage'],
                    error_rate_percent=metrics['error_rate'],
                    availability_percent=metrics['availability'],
                    total_requests=metrics['total_requests'],
                    timestamp=datetime.now()
                )
                
                self.performance_metrics[model_id] = performance_metrics
                
            except Exception as e:
                self.logger.error(f"Model metrics collection error for {model_id}: {e}")
    
    async def _get_model_performance_metrics(self, model_id: str) -> Dict[str, float]:
        """Get performance metrics for specific model"""
        # Simulate model-specific metrics
        base_performance = {
            'latency': 35.0 + hash(model_id) % 20,  # 35-55ms
            'throughput': 50.0 + hash(model_id) % 30,  # 50-80 RPS
            'accuracy': 0.85 + (hash(model_id) % 15) / 100,  # 0.85-1.00
            'memory_usage': 512 + hash(model_id) % 1024,  # 512-1536 MB
            'gpu_usage': 30.0 + hash(model_id) % 40,  # 30-70%
            'error_rate': (hash(model_id) % 5) / 100,  # 0-5%
            'availability': 95.0 + (hash(model_id) % 5),  # 95-99%
            'total_requests': 1000 + hash(model_id) % 5000  # 1000-6000
        }
        
        return base_performance
    
    async def _update_aggregated_metrics(self):
        """Update aggregated metrics"""
        try:
            current_time = datetime.now()
            
            # Aggregate performance metrics
            if self.performance_metrics:
                total_latency = sum(m.inference_latency_ms for m in self.performance_metrics.values())
                avg_latency = total_latency / len(self.performance_metrics)
                
                total_throughput = sum(m.throughput_rps for m in self.performance_metrics.values())
                
                avg_accuracy = sum(m.accuracy_score for m in self.performance_metrics.values()) / len(self.performance_metrics)
                
                self.aggregated_metrics['ai_performance'] = {
                    'avg_latency_ms': avg_latency,
                    'total_throughput_rps': total_throughput,
                    'avg_accuracy': avg_accuracy,
                    'active_models': len(self.performance_metrics),
                    'timestamp': current_time.isoformat()
                }
            
            # Aggregate resource metrics
            resource_metrics = AIResourceMetrics(
                cpu_usage_percent=self._get_latest_metric('resource.cpu_usage'),
                memory_usage_mb=self._get_latest_metric('resource.memory_usage'),
                gpu_memory_mb=self._get_latest_metric('resource.gpu_memory'),
                gpu_utilization_percent=self._get_latest_metric('resource.gpu_usage'),
                disk_io_mbps=self._get_latest_metric('resource.disk_io'),
                network_io_mbps=self._get_latest_metric('resource.network_io'),
                active_models=len(self.performance_metrics),
                queue_length=self._get_latest_metric('performance.queue_depth'),
                timestamp=current_time
            )
            
            self.resource_metrics = resource_metrics
            
        except Exception as e:
            self.logger.error(f"Aggregated metrics update error: {e}")
    
    def add_metric(self, metric_name: str, value: float, service_name: str, 
                   model_id: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        """Add a metric data point"""
        try:
            metric = AIMetric(
                metric_name=metric_name,
                value=value,
                timestamp=datetime.now(),
                service_name=service_name,
                model_id=model_id,
                tags=tags
            )
            
            self.metrics_buffer[metric_name].append(metric)
            
        except Exception as e:
            self.logger.error(f"Error adding metric {metric_name}: {e}")
    
    def _get_latest_metric(self, metric_name: str) -> float:
        """Get latest value for a metric"""
        buffer = self.metrics_buffer.get(metric_name)
        if buffer and len(buffer) > 0:
            return buffer[-1].value
        return 0.0
    
    def get_metrics_summary(self, time_window_minutes: int = 5) -> Dict[str, Any]:
        """Get metrics summary for time window"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
            summary = {}
            
            for metric_name, buffer in self.metrics_buffer.items():
                recent_metrics = [m for m in buffer if m.timestamp >= cutoff_time]
                
                if recent_metrics:
                    values = [m.value for m in recent_metrics]
                    summary[metric_name] = {
                        'count': len(values),
                        'avg': statistics.mean(values),
                        'min': min(values),
                        'max': max(values),
                        'latest': values[-1] if values else 0
                    }
            
            return {
                'time_window_minutes': time_window_minutes,
                'metrics': summary,
                'aggregated': self.aggregated_metrics,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating metrics summary: {e}")
            return {}
    
    def get_performance_metrics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for specific model or all models"""
        if model_id:
            return asdict(self.performance_metrics.get(model_id, {}))
        
        return {model_id: asdict(metrics) for model_id, metrics in self.performance_metrics.items()}
    
    def get_resource_metrics(self) -> Dict[str, Any]:
        """Get current resource metrics"""
        if self.resource_metrics:
            return asdict(self.resource_metrics)
        return {}
    
    def get_model_health_status(self) -> Dict[str, Any]:
        """Get health status for all models"""
        health_status = {}
        
        for model_id, metrics in self.performance_metrics.items():
            # Determine health based on thresholds
            health = "healthy"
            issues = []
            
            if metrics.inference_latency_ms > 100:
                health = "degraded"
                issues.append("High latency")
            
            if metrics.error_rate_percent > 5:
                health = "degraded"
                issues.append("High error rate")
            
            if metrics.availability_percent < 95:
                health = "unhealthy"
                issues.append("Low availability")
            
            if metrics.accuracy_score < 0.8:
                health = "degraded"
                issues.append("Low accuracy")
            
            health_status[model_id] = {
                'status': health,
                'issues': issues,
                'last_updated': metrics.timestamp.isoformat()
            }
        
        return health_status
    
    async def export_metrics(self, format_type: str = 'json') -> str:
        """Export metrics in specified format"""
        try:
            metrics_data = {
                'performance_metrics': self.get_performance_metrics(),
                'resource_metrics': self.get_resource_metrics(),
                'metrics_summary': self.get_metrics_summary(),
                'health_status': self.get_model_health_status(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            if format_type.lower() == 'json':
                return json.dumps(metrics_data, indent=2, default=str)
            elif format_type.lower() == 'prometheus':
                return self._format_prometheus_metrics(metrics_data)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return ""
    
    def _format_prometheus_metrics(self, metrics_data: Dict[str, Any]) -> str:
        """Format metrics for Prometheus"""
        prometheus_metrics = []
        
        # Add performance metrics
        for model_id, metrics in metrics_data['performance_metrics'].items():
            prometheus_metrics.append(f'ai_inference_latency_ms{{model="{model_id}"}} {metrics.get("inference_latency_ms", 0)}')
            prometheus_metrics.append(f'ai_throughput_rps{{model="{model_id}"}} {metrics.get("throughput_rps", 0)}')
            prometheus_metrics.append(f'ai_accuracy_score{{model="{model_id}"}} {metrics.get("accuracy_score", 0)}')
        
        # Add resource metrics
        resource_metrics = metrics_data['resource_metrics']
        if resource_metrics:
            prometheus_metrics.append(f'ai_cpu_usage_percent {resource_metrics.get("cpu_usage_percent", 0)}')
            prometheus_metrics.append(f'ai_memory_usage_mb {resource_metrics.get("memory_usage_mb", 0)}')
            prometheus_metrics.append(f'ai_gpu_utilization_percent {resource_metrics.get("gpu_utilization_percent", 0)}')
        
        return '\n'.join(prometheus_metrics)
    
    async def stop_collection(self):
        """Stop metric collection"""
        self.is_collecting = False
        if hasattr(self, 'collection_task'):
            self.collection_task.cancel()
        
        self.logger.info("AI Metrics Collector stopped")

# Service instance
ai_metrics_collector = AIMetricsCollector()