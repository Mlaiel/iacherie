"""⚡ AI Model Performance Profiler
====================================

Advanced profiling system for AI/ML models in the Creator Economy platform.
Provides real-time monitoring of model inference, GPU utilization, and batch processing optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import gc
import tracemalloc

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """AI Model types for specialized profiling"""
    
    TRANSFORMER = "transformer"
    CNN = "cnn"
    RNN = "rnn"
    GAN = "gan"
    DIFFUSION = "diffusion"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    AUDIO_PROCESSING = "audio_processing"


class InferenceMode(Enum):
    """Model inference execution modes"""
    
    SINGLE = "single"
    BATCH = "batch"
    STREAMING = "streaming"
    ASYNC_BATCH = "async_batch"


@dataclass
class GPUMetrics:
    """GPU performance metrics"""
    
    gpu_id: int
    utilization: float  # 0-100%
    memory_used: int  # MB
    memory_total: int  # MB
    temperature: float  # Celsius
    power_draw: float  # Watts
    compute_capability: str
    driver_version: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def memory_utilization(self) -> float:
        """Memory utilization percentage"""
        return (self.memory_used / self.memory_total) * 100 if self.memory_total > 0 else 0


@dataclass
class ModelInferenceMetrics:
    """AI Model inference performance metrics"""
    
    model_name: str
    model_type: ModelType
    inference_mode: InferenceMode
    batch_size: int
    input_shape: tuple
    output_shape: tuple
    inference_time: float  # seconds
    preprocessing_time: float  # seconds
    postprocessing_time: float  # seconds
    total_time: float  # seconds
    memory_peak: int  # MB
    gpu_metrics: Optional[GPUMetrics] = None
    accuracy_score: Optional[float] = None
    throughput: float = 0.0  # samples/second
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.batch_size > 0:
            self.throughput = self.batch_size / self.total_time if self.total_time > 0 else 0


@dataclass
class ModelBottleneck:
    """AI Model performance bottleneck detection"""
    
    bottleneck_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_component: str
    performance_impact: float  # percentage
    optimization_suggestions: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class AIModelProfiler:
    """
    Advanced AI Model Performance Profiler
    
    Provides comprehensive profiling for AI/ML models with focus on:
    - Real-time inference monitoring
    - GPU utilization tracking
    - Batch processing optimization
    - Memory usage analysis
    - Performance bottleneck detection
    """
    
    def __init__(
        self,
        enable_gpu_monitoring: bool = True,
        enable_memory_tracking: bool = True,
        sampling_interval: float = 0.1,
        max_history_size: int = 10000
    ):
        """
        Initialize AI Model Profiler
        
        Args:
            enable_gpu_monitoring: Enable GPU metrics collection
            enable_memory_tracking: Enable memory profiling
            sampling_interval: Metrics collection interval in seconds
            max_history_size: Maximum number of metrics to keep in memory
        """
        self.enable_gpu_monitoring = enable_gpu_monitoring
        self.enable_memory_tracking = enable_memory_tracking
        self.sampling_interval = sampling_interval
        self.max_history_size = max_history_size
        
        # Metrics storage
        self.inference_metrics: deque = deque(maxlen=max_history_size)
        self.gpu_metrics_history: deque = deque(maxlen=max_history_size)
        self.bottlenecks: deque = deque(maxlen=max_history_size)
        
        # Active profiling sessions
        self.active_sessions: Dict[str, Dict] = {}
        self.session_lock = threading.Lock()
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # GPU availability check
        self.gpu_available = self._check_gpu_availability()
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        logger.info("AIModelProfiler initialized with GPU monitoring: %s", 
                   self.gpu_available and self.enable_gpu_monitoring)
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""
        
        self.inference_time_histogram = Histogram(
            'ai_model_inference_time_seconds',
            'AI model inference time',
            ['model_name', 'model_type', 'inference_mode', 'batch_size']
        )
        
        self.throughput_gauge = Gauge(
            'ai_model_throughput_samples_per_second',
            'AI model throughput in samples per second',
            ['model_name', 'model_type']
        )
        
        self.gpu_utilization_gauge = Gauge(
            'ai_model_gpu_utilization_percent',
            'GPU utilization percentage',
            ['gpu_id']
        )
        
        self.memory_usage_gauge = Gauge(
            'ai_model_memory_usage_mb',
            'AI model memory usage in MB',
            ['model_name', 'memory_type']
        )
        
        self.bottleneck_counter = Counter(
            'ai_model_bottlenecks_total',
            'Total number of AI model bottlenecks detected',
            ['bottleneck_type', 'severity']
        )
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available for monitoring"""
        try:
            # Try importing GPU monitoring libraries
            import pynvml
            pynvml.nvmlInit()
            return True
        except ImportError:
            logger.warning("pynvml not available, GPU monitoring disabled")
            return False
        except Exception as e:
            logger.warning("GPU not available: %s", e)
            return False
    
    def _get_gpu_metrics(self) -> List[GPUMetrics]:
        """Collect current GPU metrics"""
        if not self.gpu_available:
            return []
        
        try:
            import pynvml
            
            gpu_metrics = []
            device_count = pynvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                # Get utilization
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                
                # Get memory info
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Get temperature
                try:
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except:
                    temp = 0.0
                
                # Get power draw
                try:
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                except:
                    power = 0.0
                
                # Get compute capability
                try:
                    major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                    compute_cap = f"{major}.{minor}"
                except:
                    compute_cap = "unknown"
                
                # Get driver version
                try:
                    driver_version = pynvml.nvmlSystemGetDriverVersion()
                except:
                    driver_version = "unknown"
                
                gpu_metric = GPUMetrics(
                    gpu_id=i,
                    utilization=util.gpu,
                    memory_used=memory_info.used // (1024 * 1024),  # Convert to MB
                    memory_total=memory_info.total // (1024 * 1024),  # Convert to MB
                    temperature=temp,
                    power_draw=power,
                    compute_capability=compute_cap,
                    driver_version=driver_version
                )
                
                gpu_metrics.append(gpu_metric)
                
                # Update Prometheus metrics
                self.gpu_utilization_gauge.labels(gpu_id=i).set(util.gpu)
            
            return gpu_metrics
            
        except Exception as e:
            logger.error("Error collecting GPU metrics: %s", e)
            return []
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("AI Model background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("AI Model background monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect GPU metrics
                if self.enable_gpu_monitoring:
                    gpu_metrics = self._get_gpu_metrics()
                    if gpu_metrics:
                        self.gpu_metrics_history.extend(gpu_metrics)
                
                # Analyze for bottlenecks
                self._detect_bottlenecks()
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error("Error in monitoring loop: %s", e)
                time.sleep(1.0)
    
    def start_inference_profiling(
        self,
        model_name: str,
        model_type: ModelType,
        inference_mode: InferenceMode,
        batch_size: int = 1,
        input_shape: Optional[tuple] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Start profiling an AI model inference session
        
        Args:
            model_name: Name of the model being profiled
            model_type: Type of AI model
            inference_mode: Mode of inference execution
            batch_size: Size of the batch being processed
            input_shape: Shape of input tensors
            session_id: Optional session identifier
        
        Returns:
            session_id: Unique identifier for this profiling session
        """
        if session_id is None:
            session_id = f"{model_name}_{int(time.time() * 1000)}"
        
        # Start memory tracking if enabled
        if self.enable_memory_tracking:
            tracemalloc.start()
        
        session_data = {
            'model_name': model_name,
            'model_type': model_type,
            'inference_mode': inference_mode,
            'batch_size': batch_size,
            'input_shape': input_shape,
            'start_time': time.time(),
            'preprocessing_start': None,
            'inference_start': None,
            'postprocessing_start': None,
            'memory_peak': 0,
            'initial_gpu_metrics': self._get_gpu_metrics() if self.enable_gpu_monitoring else None
        }
        
        with self.session_lock:
            self.active_sessions[session_id] = session_data
        
        logger.debug("Started inference profiling session: %s", session_id)
        return session_id
    
    def mark_preprocessing_start(self, session_id: str):
        """Mark the start of preprocessing phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['preprocessing_start'] = time.time()
    
    def mark_inference_start(self, session_id: str):
        """Mark the start of inference phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['inference_start'] = time.time()
    
    def mark_postprocessing_start(self, session_id: str):
        """Mark the start of postprocessing phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['postprocessing_start'] = time.time()
    
    def end_inference_profiling(
        self,
        session_id: str,
        output_shape: Optional[tuple] = None,
        accuracy_score: Optional[float] = None
    ) -> ModelInferenceMetrics:
        """
        End profiling session and return metrics
        
        Args:
            session_id: Session identifier
            output_shape: Shape of output tensors
            accuracy_score: Model accuracy if available
        
        Returns:
            ModelInferenceMetrics: Complete inference metrics
        """
        with self.session_lock:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session_data = self.active_sessions.pop(session_id)
        
        end_time = time.time()
        
        # Calculate timing metrics
        total_time = end_time - session_data['start_time']
        
        preprocessing_time = 0.0
        inference_time = 0.0
        postprocessing_time = 0.0
        
        if session_data['preprocessing_start']:
            if session_data['inference_start']:
                preprocessing_time = session_data['inference_start'] - session_data['preprocessing_start']
            else:
                preprocessing_time = end_time - session_data['preprocessing_start']
        
        if session_data['inference_start']:
            if session_data['postprocessing_start']:
                inference_time = session_data['postprocessing_start'] - session_data['inference_start']
            else:
                inference_time = end_time - session_data['inference_start']
        
        if session_data['postprocessing_start']:
            postprocessing_time = end_time - session_data['postprocessing_start']
        
        # Get memory peak
        memory_peak = 0
        if self.enable_memory_tracking:
            try:
                current, peak = tracemalloc.get_traced_memory()
                memory_peak = peak // (1024 * 1024)  # Convert to MB
                tracemalloc.stop()
            except:
                pass
        
        # Get final GPU metrics
        final_gpu_metrics = None
        if self.enable_gpu_monitoring:
            gpu_metrics_list = self._get_gpu_metrics()
            if gpu_metrics_list:
                final_gpu_metrics = gpu_metrics_list[0]  # Use first GPU
        
        # Create metrics object
        metrics = ModelInferenceMetrics(
            model_name=session_data['model_name'],
            model_type=session_data['model_type'],
            inference_mode=session_data['inference_mode'],
            batch_size=session_data['batch_size'],
            input_shape=session_data['input_shape'] or (),
            output_shape=output_shape or (),
            inference_time=inference_time,
            preprocessing_time=preprocessing_time,
            postprocessing_time=postprocessing_time,
            total_time=total_time,
            memory_peak=memory_peak,
            gpu_metrics=final_gpu_metrics,
            accuracy_score=accuracy_score
        )
        
        # Store metrics
        self.inference_metrics.append(metrics)
        
        # Update Prometheus metrics
        self.inference_time_histogram.labels(
            model_name=metrics.model_name,
            model_type=metrics.model_type.value,
            inference_mode=metrics.inference_mode.value,
            batch_size=str(metrics.batch_size)
        ).observe(metrics.total_time)
        
        self.throughput_gauge.labels(
            model_name=metrics.model_name,
            model_type=metrics.model_type.value
        ).set(metrics.throughput)
        
        self.memory_usage_gauge.labels(
            model_name=metrics.model_name,
            memory_type='peak'
        ).set(metrics.memory_peak)
        
        logger.info("Inference profiling completed for %s: %.3fs total, %.1f samples/sec",
                   metrics.model_name, metrics.total_time, metrics.throughput)
        
        return metrics
    
    def _detect_bottlenecks(self):
        """Detect performance bottlenecks in AI model execution"""
        if len(self.inference_metrics) < 2:
            return
        
        recent_metrics = list(self.inference_metrics)[-10:]  # Last 10 inferences
        
        # Analyze inference time trends
        inference_times = [m.inference_time for m in recent_metrics]
        avg_inference_time = statistics.mean(inference_times)
        
        # Check for slow inference
        if avg_inference_time > 5.0:  # 5 seconds threshold
            bottleneck = ModelBottleneck(
                bottleneck_type="slow_inference",
                severity="high" if avg_inference_time > 10.0 else "medium",
                description=f"Average inference time is {avg_inference_time:.2f}s",
                affected_component="model_inference",
                performance_impact=min(100, (avg_inference_time / 1.0) * 10),
                optimization_suggestions=[
                    "Consider model quantization",
                    "Optimize batch size",
                    "Use model distillation",
                    "Implement tensor parallelism"
                ]
            )
            self._record_bottleneck(bottleneck)
        
        # Check GPU utilization if available
        if self.gpu_metrics_history:
            recent_gpu = list(self.gpu_metrics_history)[-5:]
            avg_gpu_util = statistics.mean([g.utilization for g in recent_gpu])
            
            if avg_gpu_util < 30:  # Low GPU utilization
                bottleneck = ModelBottleneck(
                    bottleneck_type="low_gpu_utilization",
                    severity="medium",
                    description=f"GPU utilization is only {avg_gpu_util:.1f}%",
                    affected_component="gpu_compute",
                    performance_impact=100 - avg_gpu_util,
                    optimization_suggestions=[
                        "Increase batch size",
                        "Use mixed precision training",
                        "Optimize data loading pipeline",
                        "Reduce CPU-GPU data transfer"
                    ]
                )
                self._record_bottleneck(bottleneck)
        
        # Check memory usage patterns
        memory_peaks = [m.memory_peak for m in recent_metrics if m.memory_peak > 0]
        if memory_peaks:
            avg_memory = statistics.mean(memory_peaks)
            if avg_memory > 8000:  # 8GB threshold
                bottleneck = ModelBottleneck(
                    bottleneck_type="high_memory_usage",
                    severity="high" if avg_memory > 16000 else "medium",
                    description=f"Average memory usage is {avg_memory:.0f}MB",
                    affected_component="memory",
                    performance_impact=min(100, (avg_memory / 1000) * 5),
                    optimization_suggestions=[
                        "Implement gradient checkpointing",
                        "Use memory-efficient attention",
                        "Reduce model precision",
                        "Optimize data loading"
                    ]
                )
                self._record_bottleneck(bottleneck)
    
    def _record_bottleneck(self, bottleneck: ModelBottleneck):
        """Record a detected bottleneck"""
        self.bottlenecks.append(bottleneck)
        
        # Update Prometheus counter
        self.bottleneck_counter.labels(
            bottleneck_type=bottleneck.bottleneck_type,
            severity=bottleneck.severity
        ).inc()
        
        logger.warning("AI Model bottleneck detected: %s (%s severity)",
                      bottleneck.description, bottleneck.severity)
    
    def get_optimization_recommendations(
        self,
        model_name: Optional[str] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """
        Get AI model optimization recommendations
        
        Args:
            model_name: Specific model to analyze (None for all)
            time_window: Time window for analysis
        
        Returns:
            List of optimization recommendations
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.inference_metrics
            if m.timestamp >= cutoff_time and (model_name is None or m.model_name == model_name)
        ]
        
        if not recent_metrics:
            return []
        
        recommendations = []
        
        # Analyze throughput
        throughputs = [m.throughput for m in recent_metrics if m.throughput > 0]
        if throughputs:
            avg_throughput = statistics.mean(throughputs)
            
            if avg_throughput < 10:  # Low throughput threshold
                recommendations.append({
                    'type': 'throughput_optimization',
                    'priority': 'high',
                    'description': f'Low throughput detected: {avg_throughput:.1f} samples/sec',
                    'suggestions': [
                        'Increase batch size for batch inference',
                        'Use tensor parallelism for large models',
                        'Implement asynchronous inference pipeline',
                        'Consider model quantization'
                    ],
                    'expected_improvement': '50-200% throughput increase'
                })
        
        # Analyze batch size efficiency
        batch_sizes = [m.batch_size for m in recent_metrics]
        batch_times = [m.total_time for m in recent_metrics]
        
        if len(batch_sizes) > 1:
            # Find optimal batch size
            batch_efficiency = {}
            for bs, bt in zip(batch_sizes, batch_times):
                if bs > 0 and bt > 0:
                    efficiency = bs / bt  # samples per second
                    if bs not in batch_efficiency:
                        batch_efficiency[bs] = []
                    batch_efficiency[bs].append(efficiency)
            
            if len(batch_efficiency) > 1:
                avg_efficiency = {bs: statistics.mean(effs) for bs, effs in batch_efficiency.items()}
                optimal_batch = max(avg_efficiency.keys(), key=lambda x: avg_efficiency[x])
                current_batch = statistics.mode(batch_sizes)
                
                if optimal_batch != current_batch:
                    recommendations.append({
                        'type': 'batch_size_optimization',
                        'priority': 'medium',
                        'description': f'Suboptimal batch size: {current_batch} vs optimal {optimal_batch}',
                        'suggestions': [
                            f'Use batch size {optimal_batch} for better efficiency',
                            'Implement dynamic batching',
                            'Monitor memory usage with larger batches'
                        ],
                        'expected_improvement': f'{((avg_efficiency[optimal_batch] / avg_efficiency[current_batch] - 1) * 100):.1f}% efficiency gain'
                    })
        
        return recommendations
    
    def get_performance_summary(
        self,
        model_name: Optional[str] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        Get performance summary for AI models
        
        Args:
            model_name: Specific model to analyze (None for all)
            time_window: Time window for analysis
        
        Returns:
            Performance summary dictionary
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.inference_metrics
            if m.timestamp >= cutoff_time and (model_name is None or m.model_name == model_name)
        ]
        
        if not recent_metrics:
            return {'error': 'No metrics available'}
        
        # Calculate statistics
        inference_times = [m.inference_time for m in recent_metrics]
        total_times = [m.total_time for m in recent_metrics]
        throughputs = [m.throughput for m in recent_metrics if m.throughput > 0]
        memory_peaks = [m.memory_peak for m in recent_metrics if m.memory_peak > 0]
        
        summary = {
            'time_window': str(time_window),
            'total_inferences': len(recent_metrics),
            'models_analyzed': len(set(m.model_name for m in recent_metrics)),
            'performance_metrics': {
                'avg_inference_time': statistics.mean(inference_times),
                'p95_inference_time': statistics.quantiles(inference_times, n=20)[18] if len(inference_times) >= 20 else max(inference_times),
                'avg_total_time': statistics.mean(total_times),
                'p95_total_time': statistics.quantiles(total_times, n=20)[18] if len(total_times) >= 20 else max(total_times),
            }
        }
        
        if throughputs:
            summary['performance_metrics'].update({
                'avg_throughput': statistics.mean(throughputs),
                'max_throughput': max(throughputs)
            })
        
        if memory_peaks:
            summary['performance_metrics'].update({
                'avg_memory_peak': statistics.mean(memory_peaks),
                'max_memory_peak': max(memory_peaks)
            })
        
        # GPU metrics if available
        if self.gpu_metrics_history:
            recent_gpu = [g for g in self.gpu_metrics_history if g.timestamp >= cutoff_time]
            if recent_gpu:
                summary['gpu_metrics'] = {
                    'avg_utilization': statistics.mean([g.utilization for g in recent_gpu]),
                    'avg_memory_utilization': statistics.mean([g.memory_utilization for g in recent_gpu]),
                    'max_temperature': max([g.temperature for g in recent_gpu if g.temperature > 0], default=0)
                }
        
        # Recent bottlenecks
        recent_bottlenecks = [b for b in self.bottlenecks if b.timestamp >= cutoff_time]
        summary['bottlenecks'] = {
            'total_count': len(recent_bottlenecks),
            'by_severity': {
                severity: len([b for b in recent_bottlenecks if b.severity == severity])
                for severity in ['low', 'medium', 'high', 'critical']
            }
        }
        
        return summary
    
    def export_metrics(self, format_type: str = 'json') -> str:
        """
        Export profiling metrics in specified format
        
        Args:
            format_type: Export format ('json', 'csv')
        
        Returns:
            Formatted metrics data
        """
        if format_type.lower() == 'json':
            data = {
                'inference_metrics': [
                    {
                        'model_name': m.model_name,
                        'model_type': m.model_type.value,
                        'inference_mode': m.inference_mode.value,
                        'batch_size': m.batch_size,
                        'inference_time': m.inference_time,
                        'total_time': m.total_time,
                        'throughput': m.throughput,
                        'memory_peak': m.memory_peak,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in self.inference_metrics
                ],
                'bottlenecks': [
                    {
                        'type': b.bottleneck_type,
                        'severity': b.severity,
                        'description': b.description,
                        'affected_component': b.affected_component,
                        'performance_impact': b.performance_impact,
                        'timestamp': b.timestamp.isoformat()
                    }
                    for b in self.bottlenecks
                ]
            }
            return json.dumps(data, indent=2)
        
        elif format_type.lower() == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow([
                'timestamp', 'model_name', 'model_type', 'inference_mode',
                'batch_size', 'inference_time', 'total_time', 'throughput',
                'memory_peak'
            ])
            
            # Write data
            for m in self.inference_metrics:
                writer.writerow([
                    m.timestamp.isoformat(),
                    m.model_name,
                    m.model_type.value,
                    m.inference_mode.value,
                    m.batch_size,
                    m.inference_time,
                    m.total_time,
                    m.throughput,
                    m.memory_peak
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")


# Context manager for easy profiling
class InferenceProfiler:
    """Context manager for AI model inference profiling"""
    
    def __init__(
        self,
        profiler: AIModelProfiler,
        model_name: str,
        model_type: ModelType,
        inference_mode: InferenceMode = InferenceMode.SINGLE,
        batch_size: int = 1,
        input_shape: Optional[tuple] = None
    ):
        self.profiler = profiler
        self.model_name = model_name
        self.model_type = model_type
        self.inference_mode = inference_mode
        self.batch_size = batch_size
        self.input_shape = input_shape
        self.session_id: Optional[str] = None
    
    def __enter__(self):
        self.session_id = self.profiler.start_inference_profiling(
            model_name=self.model_name,
            model_type=self.model_type,
            inference_mode=self.inference_mode,
            batch_size=self.batch_size,
            input_shape=self.input_shape
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session_id:
            return self.profiler.end_inference_profiling(self.session_id)
        return None
    
    def mark_preprocessing_start(self):
        if self.session_id:
            self.profiler.mark_preprocessing_start(self.session_id)
    
    def mark_inference_start(self):
        if self.session_id:
            self.profiler.mark_inference_start(self.session_id)
    
    def mark_postprocessing_start(self):
        if self.session_id:
            self.profiler.mark_postprocessing_start(self.session_id)


# Factory function for creating profiler instances
def create_ai_model_profiler(
    enable_gpu_monitoring: bool = True,
    enable_memory_tracking: bool = True,
    start_monitoring: bool = True
) -> AIModelProfiler:
    """
    Factory function to create and configure AI Model Profiler
    
    Args:
        enable_gpu_monitoring: Enable GPU metrics collection
        enable_memory_tracking: Enable memory profiling
        start_monitoring: Start background monitoring immediately
    
    Returns:
        Configured AIModelProfiler instance
    """
    profiler = AIModelProfiler(
        enable_gpu_monitoring=enable_gpu_monitoring,
        enable_memory_tracking=enable_memory_tracking
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


if __name__ == "__main__":
    # Example usage
    import numpy as np
    
    # Create profiler
    profiler = create_ai_model_profiler()
    
    # Example: Profile a transformer model inference
    with InferenceProfiler(
        profiler=profiler,
        model_name="gpt-3.5-turbo",
        model_type=ModelType.TRANSFORMER,
        inference_mode=InferenceMode.BATCH,
        batch_size=8,
        input_shape=(8, 512)
    ) as session:
        
        # Simulate preprocessing
        session.mark_preprocessing_start()
        time.sleep(0.1)  # Simulate preprocessing time
        
        # Simulate inference
        session.mark_inference_start()
        time.sleep(0.5)  # Simulate inference time
        
        # Simulate postprocessing
        session.mark_postprocessing_start()
        time.sleep(0.05)  # Simulate postprocessing time
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print("Performance Summary:", json.dumps(summary, indent=2))
    
    # Get optimization recommendations
    recommendations = profiler.get_optimization_recommendations()
    print("Optimization Recommendations:", json.dumps(recommendations, indent=2))
    
    # Stop monitoring
    profiler.stop_monitoring()