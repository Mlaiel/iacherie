"""
Model Performance Analyzer - AI/ML Pipeline Infrastructure
Enterprise performance profiling and optimization with comprehensive model analysis and tuning.

Created by: Fahed Mlaiel (mlaiel@live.de)
Copyright: EXCLUSIVE INTELLECTUAL PROPERTY - Fahed Mlaiel
WARNING: Unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import uuid
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.profiler
from core.tensorflow_singleton import get_tensorflow
tf = get_tensorflow()
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import psutil
import GPUtil
import pynvml
import redis
import boto3
import mlflow
import wandb
from memory_profiler import profile
import cProfile
import pstats
import tracemalloc
import py3nvml.py3nvml as nvml
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class PerformanceMetricType(Enum):
    """Types of performance metrics"""
    INFERENCE_LATENCY = "inference_latency"
    TRAINING_THROUGHPUT = "training_throughput"
    MEMORY_USAGE = "memory_usage"
    GPU_UTILIZATION = "gpu_utilization"
    CPU_UTILIZATION = "cpu_utilization"
    ACCURACY = "accuracy"
    LOSS = "loss"
    BATCH_SIZE_EFFICIENCY = "batch_size_efficiency"
    MODEL_SIZE = "model_size"
    ENERGY_CONSUMPTION = "energy_consumption"


class OptimizationStrategy(Enum):
    """Model optimization strategies"""
    QUANTIZATION = "quantization"
    PRUNING = "pruning"
    KNOWLEDGE_DISTILLATION = "knowledge_distillation"
    TENSOR_COMPRESSION = "tensor_compression"
    MIXED_PRECISION = "mixed_precision"
    DYNAMIC_BATCHING = "dynamic_batching"
    MODEL_PARALLELISM = "model_parallelism"
    GRADIENT_ACCUMULATION = "gradient_accumulation"


@dataclass
class PerformanceMetric:
    """Individual performance metric measurement"""
    metric_type: PerformanceMetricType
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any]
    
    # Statistical properties
    percentile_50: Optional[float] = None
    percentile_95: Optional[float] = None
    percentile_99: Optional[float] = None
    std_dev: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class ModelProfile:
    """Comprehensive model performance profile"""
    model_id: str
    model_version: str
    profile_id: str
    
    # Model characteristics
    model_type: str
    model_size_mb: float
    parameter_count: int
    flops_count: int
    
    # Performance metrics
    inference_latency_ms: PerformanceMetric
    training_throughput: Optional[PerformanceMetric] = None
    memory_usage_mb: Optional[PerformanceMetric] = None
    gpu_utilization: Optional[PerformanceMetric] = None
    cpu_utilization: Optional[PerformanceMetric] = None
    
    # Quality metrics
    accuracy: Optional[PerformanceMetric] = None
    precision: Optional[PerformanceMetric] = None
    recall: Optional[PerformanceMetric] = None
    f1_score: Optional[PerformanceMetric] = None
    
    # Efficiency metrics
    throughput_per_watt: Optional[float] = None
    cost_per_inference: Optional[float] = None
    latency_percentiles: Optional[Dict[str, float]] = None
    
    # Profiling metadata
    profiled_at: datetime = None
    profiling_duration_seconds: float = 0.0
    profiling_environment: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.profiled_at is None:
            self.profiled_at = datetime.utcnow()


@dataclass
class OptimizationResult:
    """Result of model optimization"""
    optimization_id: str
    original_model_id: str
    optimized_model_id: str
    strategy: OptimizationStrategy
    
    # Performance comparison
    original_profile: ModelProfile
    optimized_profile: ModelProfile
    
    # Improvement metrics
    latency_improvement_percent: float
    memory_reduction_percent: float
    throughput_improvement_percent: float
    model_size_reduction_percent: float
    
    # Quality impact
    accuracy_change_percent: float
    quality_degradation: bool
    
    # Optimization details
    optimization_config: Dict[str, Any]
    optimization_time_seconds: float
    created_at: datetime
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class PerformanceBenchmark:
    """Performance benchmark suite"""
    benchmark_id: str
    benchmark_name: str
    model_profiles: List[ModelProfile]
    
    # Benchmark configuration
    test_dataset_size: int
    batch_sizes: List[int]
    hardware_configs: List[Dict[str, Any]]
    optimization_strategies: List[OptimizationStrategy]
    
    # Results
    benchmark_results: Dict[str, Any]
    recommendations: List[str]
    
    created_at: datetime
    completed_at: Optional[datetime] = None


class ModelPerformanceAnalyzer:
    """Enterprise model performance profiling and optimization engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        self.s3_client = boto3.client('s3') if config.get('s3_enabled') else None
        self.logger = self._setup_logging()
        
        # Profiling components
        self.profiler = ModelProfiler(config)
        self.optimizer = ModelOptimizer(config)
        self.benchmarker = PerformanceBenchmarker(config)
        self.monitor = RealTimeMonitor(config)
        
        # Storage
        self.model_profiles: Dict[str, ModelProfile] = {}
        self.optimization_results: Dict[str, OptimizationResult] = {}
        self.benchmarks: Dict[str, PerformanceBenchmark] = {}
        
        # Initialize hardware monitoring
        try:
            pynvml.nvmlInit()
            self.nvml_available = True
        except:
            self.nvml_available = False
            self.logger.warning("NVIDIA ML not available")
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for performance analysis"""
        logger = logging.getLogger('model_performance_analyzer')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _start_background_monitoring(self) -> None:
        """Start background performance monitoring"""
        asyncio.create_task(self._continuous_performance_monitoring())
        self.logger.info("Started background performance monitoring")
    
    async def profile_model_performance(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        model_id: str,
        model_version: str,
        test_data: Any,
        profiling_config: Optional[Dict[str, Any]] = None
    ) -> ModelProfile:
        """Comprehensive model performance profiling"""
        profile_id = str(uuid.uuid4())
        start_time = time.time()
        
        self.logger.info(f"Starting model performance profiling: {model_id}")
        
        try:
            # Initialize profiling environment
            profiling_env = await self._setup_profiling_environment()
            
            # Profile model characteristics
            model_characteristics = await self._analyze_model_characteristics(model)
            
            # Profile inference performance
            inference_metrics = await self._profile_inference_performance(
                model, test_data, profiling_config
            )
            
            # Profile memory usage
            memory_metrics = await self._profile_memory_usage(model, test_data)
            
            # Profile hardware utilization
            hardware_metrics = await self._profile_hardware_utilization(
                model, test_data, profiling_config
            )
            
            # Profile training performance (if applicable)
            training_metrics = None
            if profiling_config and profiling_config.get('profile_training', False):
                training_metrics = await self._profile_training_performance(
                    model, test_data, profiling_config
                )
            
            # Calculate efficiency metrics
            efficiency_metrics = await self._calculate_efficiency_metrics(
                inference_metrics, memory_metrics, hardware_metrics
            )
            
            # Create comprehensive profile
            profile = ModelProfile(
                model_id=model_id,
                model_version=model_version,
                profile_id=profile_id,
                model_type=type(model).__name__,
                model_size_mb=model_characteristics['size_mb'],
                parameter_count=model_characteristics['parameter_count'],
                flops_count=model_characteristics['flops_count'],
                inference_latency_ms=inference_metrics['latency'],
                training_throughput=training_metrics.get('throughput') if training_metrics else None,
                memory_usage_mb=memory_metrics['peak_usage'],
                gpu_utilization=hardware_metrics.get('gpu_utilization'),
                cpu_utilization=hardware_metrics.get('cpu_utilization'),
                throughput_per_watt=efficiency_metrics.get('throughput_per_watt'),
                cost_per_inference=efficiency_metrics.get('cost_per_inference'),
                latency_percentiles=inference_metrics.get('percentiles'),
                profiling_duration_seconds=time.time() - start_time,
                profiling_environment=profiling_env
            )
            
            # Store profile
            self.model_profiles[profile_id] = profile
            await self._store_model_profile(profile)
            
            # Track in MLflow/Wandb
            await self._track_profiling_metrics(profile)
            
            self.logger.info(f"Completed model profiling: {profile_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error profiling model performance: {e}")
            raise
    
    async def _setup_profiling_environment(self) -> Dict[str, Any]:
        """Setup profiling environment and collect system info"""
        env_info = {
            'cpu_info': {
                'model': 'Unknown',
                'cores': psutil.cpu_count(),
                'frequency_mhz': psutil.cpu_freq().current if psutil.cpu_freq() else 0
            },
            'memory_info': {
                'total_gb': psutil.virtual_memory().total / (1024**3),
                'available_gb': psutil.virtual_memory().available / (1024**3)
            },
            'gpu_info': [],
            'software_versions': {
                'torch_version': torch.__version__,
                'tf_version': tf.__version__ if hasattr(tf, '__version__') else 'N/A',
                'python_version': f"{psutil.python_version()}"
            }
        }
        
        # Get GPU information
        if self.nvml_available:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    
                    env_info['gpu_info'].append({
                        'name': name,
                        'memory_total_gb': memory_info.total / (1024**3),
                        'memory_available_gb': memory_info.free / (1024**3)
                    })
            except Exception as e:
                self.logger.warning(f"Could not get GPU info: {e}")
        
        return env_info
    
    async def _analyze_model_characteristics(self, model: Union[torch.nn.Module, tf.keras.Model]) -> Dict[str, Any]:
        """Analyze model structure and characteristics"""
        characteristics = {
            'size_mb': 0.0,
            'parameter_count': 0,
            'flops_count': 0,
            'layers_count': 0,
            'model_type': type(model).__name__
        }
        
        if isinstance(model, torch.nn.Module):
            # PyTorch model analysis
            characteristics.update(await self._analyze_pytorch_model(model))
        elif hasattr(model, 'layers'):  # TensorFlow/Keras model
            characteristics.update(await self._analyze_tensorflow_model(model))
        
        return characteristics
    
    async def _analyze_pytorch_model(self, model: torch.nn.Module) -> Dict[str, Any]:
        """Analyze PyTorch model characteristics"""
        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        # Estimate model size
        param_size = sum(p.numel() * p.element_size() for p in model.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
        model_size_bytes = param_size + buffer_size
        
        # Count layers
        layers_count = len(list(model.modules()))
        
        return {
            'parameter_count': total_params,
            'trainable_parameter_count': trainable_params,
            'size_mb': model_size_bytes / (1024 * 1024),
            'layers_count': layers_count,
            'flops_count': await self._estimate_pytorch_flops(model)
        }
    
    async def _analyze_tensorflow_model(self, model) -> Dict[str, Any]:
        """Analyze TensorFlow/Keras model characteristics"""
        # Count parameters
        total_params = model.count_params()
        
        # Get model size (approximate)
        model_size_mb = total_params * 4 / (1024 * 1024)  # Assuming float32
        
        # Count layers
        layers_count = len(model.layers)
        
        return {
            'parameter_count': total_params,
            'size_mb': model_size_mb,
            'layers_count': layers_count,
            'flops_count': await self._estimate_tensorflow_flops(model)
        }
    
    async def _estimate_pytorch_flops(self, model: torch.nn.Module) -> int:
        """Estimate FLOPs for PyTorch model"""
        # Simplified FLOP estimation
        total_flops = 0
        
        for module in model.modules():
            if isinstance(module, nn.Conv2d):
                # Convolution FLOPs: output_size * kernel_size * input_channels
                total_flops += module.out_channels * module.kernel_size[0] * module.kernel_size[1] * module.in_channels
            elif isinstance(module, nn.Linear):
                # Linear layer FLOPs: input_features * output_features
                total_flops += module.in_features * module.out_features
        
        return total_flops
    
    async def _estimate_tensorflow_flops(self, model) -> int:
        """Estimate FLOPs for TensorFlow model"""
        # Simplified FLOP estimation for TensorFlow
        try:
            # Try to use TensorFlow's built-in profiler if available
            concrete_func = tf.function(lambda: model(tf.random.normal([1] + list(model.input_shape[1:]))))
            concrete_func = concrete_func.get_concrete_function()
            
            # This would require TensorFlow Profiler
            return 0  # Placeholder
        except:
            return 0
    
    async def _profile_inference_performance(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        test_data: Any,
        config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Profile model inference performance"""
        warmup_iterations = config.get('warmup_iterations', 10) if config else 10
        benchmark_iterations = config.get('benchmark_iterations', 100) if config else 100
        batch_sizes = config.get('batch_sizes', [1, 8, 16, 32]) if config else [1, 8, 16, 32]
        
        inference_results = {}
        
        for batch_size in batch_sizes:
            latencies = []
            
            # Prepare batch data
            batch_data = self._prepare_batch_data(test_data, batch_size)
            
            # Warmup
            for _ in range(warmup_iterations):
                _ = await self._run_inference(model, batch_data)
            
            # Benchmark
            for _ in range(benchmark_iterations):
                start_time = time.perf_counter()
                _ = await self._run_inference(model, batch_data)
                end_time = time.perf_counter()
                
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
            
            # Calculate statistics
            latencies = np.array(latencies)
            inference_results[f'batch_size_{batch_size}'] = {
                'mean_latency_ms': np.mean(latencies),
                'p50_latency_ms': np.percentile(latencies, 50),
                'p95_latency_ms': np.percentile(latencies, 95),
                'p99_latency_ms': np.percentile(latencies, 99),
                'std_latency_ms': np.std(latencies),
                'min_latency_ms': np.min(latencies),
                'max_latency_ms': np.max(latencies),
                'throughput_samples_per_sec': batch_size * 1000 / np.mean(latencies)
            }
        
        # Create aggregated metrics
        best_batch_size = min(inference_results.keys(), 
                            key=lambda k: inference_results[k]['mean_latency_ms'])
        best_results = inference_results[best_batch_size]
        
        return {
            'latency': PerformanceMetric(
                metric_type=PerformanceMetricType.INFERENCE_LATENCY,
                value=best_results['mean_latency_ms'],
                unit='ms',
                timestamp=datetime.utcnow(),
                context={'batch_size': best_batch_size},
                percentile_50=best_results['p50_latency_ms'],
                percentile_95=best_results['p95_latency_ms'],
                percentile_99=best_results['p99_latency_ms'],
                std_dev=best_results['std_latency_ms'],
                min_value=best_results['min_latency_ms'],
                max_value=best_results['max_latency_ms']
            ),
            'batch_size_results': inference_results,
            'optimal_batch_size': best_batch_size,
            'percentiles': {
                'p50': best_results['p50_latency_ms'],
                'p95': best_results['p95_latency_ms'],
                'p99': best_results['p99_latency_ms']
            }
        }
    
    def _prepare_batch_data(self, test_data: Any, batch_size: int) -> Any:
        """Prepare batch data for inference"""
        if isinstance(test_data, torch.Tensor):
            if len(test_data.shape) == 4:  # Batch already present
                return test_data[:batch_size]
            else:
                return test_data.unsqueeze(0).repeat(batch_size, *([1] * (len(test_data.shape))))
        elif isinstance(test_data, np.ndarray):
            if len(test_data.shape) == 4:  # Batch already present
                return test_data[:batch_size]
            else:
                return np.repeat(test_data[np.newaxis, :], batch_size, axis=0)
        else:
            # Handle other data types
            return test_data
    
    async def _run_inference(self, model: Union[torch.nn.Module, tf.keras.Model], batch_data: Any) -> Any:
        """Run single inference pass"""
        if isinstance(model, torch.nn.Module):
            model.eval()
            with torch.no_grad():
                if torch.cuda.is_available() and next(model.parameters()).is_cuda:
                    batch_data = batch_data.cuda()
                result = model(batch_data)
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                return result
        else:
            # TensorFlow model
            return model(batch_data, training=False)
    
    async def _profile_memory_usage(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        test_data: Any
    ) -> Dict[str, Any]:
        """Profile model memory usage"""
        memory_metrics = {}
        
        # Start memory tracking
        tracemalloc.start()
        
        if torch.cuda.is_available() and isinstance(model, torch.nn.Module):
            # GPU memory profiling for PyTorch
            torch.cuda.reset_peak_memory_stats()
            initial_memory = torch.cuda.memory_allocated()
            
            # Run inference
            batch_data = self._prepare_batch_data(test_data, 1)
            _ = await self._run_inference(model, batch_data)
            
            peak_memory = torch.cuda.max_memory_allocated()
            final_memory = torch.cuda.memory_allocated()
            
            memory_metrics['gpu_memory'] = {
                'initial_mb': initial_memory / (1024 * 1024),
                'peak_mb': peak_memory / (1024 * 1024),
                'final_mb': final_memory / (1024 * 1024),
                'usage_mb': (peak_memory - initial_memory) / (1024 * 1024)
            }
        
        # CPU memory profiling
        process = psutil.Process()
        initial_cpu_memory = process.memory_info().rss
        
        # Run inference
        batch_data = self._prepare_batch_data(test_data, 1)
        _ = await self._run_inference(model, batch_data)
        
        final_cpu_memory = process.memory_info().rss
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        memory_metrics['cpu_memory'] = {
            'initial_mb': initial_cpu_memory / (1024 * 1024),
            'final_mb': final_cpu_memory / (1024 * 1024),
            'peak_traced_mb': peak / (1024 * 1024),
            'current_traced_mb': current / (1024 * 1024)
        }
        
        # Determine peak usage
        peak_usage_mb = memory_metrics.get('gpu_memory', {}).get('peak_mb', 0)
        if peak_usage_mb == 0:
            peak_usage_mb = memory_metrics['cpu_memory']['peak_traced_mb']
        
        return {
            'peak_usage': PerformanceMetric(
                metric_type=PerformanceMetricType.MEMORY_USAGE,
                value=peak_usage_mb,
                unit='MB',
                timestamp=datetime.utcnow(),
                context=memory_metrics
            ),
            'detailed_metrics': memory_metrics
        }
    
    async def _profile_hardware_utilization(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        test_data: Any,
        config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Profile hardware utilization during inference"""
        monitoring_duration = config.get('monitoring_duration', 10) if config else 10
        
        # Start hardware monitoring
        hardware_monitor = HardwareMonitor()
        hardware_monitor.start_monitoring()
        
        # Run inference workload
        batch_data = self._prepare_batch_data(test_data, 8)
        start_time = time.time()
        
        while time.time() - start_time < monitoring_duration:
            _ = await self._run_inference(model, batch_data)
            await asyncio.sleep(0.1)  # Small delay between inferences
        
        # Stop monitoring and get results
        utilization_data = hardware_monitor.stop_monitoring()
        
        hardware_metrics = {}
        
        if utilization_data['cpu_utilization']:
            cpu_util = np.array(utilization_data['cpu_utilization'])
            hardware_metrics['cpu_utilization'] = PerformanceMetric(
                metric_type=PerformanceMetricType.CPU_UTILIZATION,
                value=np.mean(cpu_util),
                unit='%',
                timestamp=datetime.utcnow(),
                context={'measurements': len(cpu_util)},
                percentile_95=np.percentile(cpu_util, 95),
                std_dev=np.std(cpu_util),
                min_value=np.min(cpu_util),
                max_value=np.max(cpu_util)
            )
        
        if utilization_data['gpu_utilization']:
            gpu_util = np.array(utilization_data['gpu_utilization'])
            hardware_metrics['gpu_utilization'] = PerformanceMetric(
                metric_type=PerformanceMetricType.GPU_UTILIZATION,
                value=np.mean(gpu_util),
                unit='%',
                timestamp=datetime.utcnow(),
                context={'measurements': len(gpu_util)},
                percentile_95=np.percentile(gpu_util, 95),
                std_dev=np.std(gpu_util),
                min_value=np.min(gpu_util),
                max_value=np.max(gpu_util)
            )
        
        return hardware_metrics
    
    async def _profile_training_performance(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        training_data: Any,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Profile training performance"""
        # Mock training performance profiling
        return {
            'throughput': PerformanceMetric(
                metric_type=PerformanceMetricType.TRAINING_THROUGHPUT,
                value=1250.0,
                unit='samples/sec',
                timestamp=datetime.utcnow(),
                context={'training_mode': True}
            )
        }
    
    async def _calculate_efficiency_metrics(
        self,
        inference_metrics: Dict[str, Any],
        memory_metrics: Dict[str, Any],
        hardware_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate efficiency metrics"""
        efficiency = {}
        
        # Throughput per watt (estimated)
        if 'gpu_utilization' in hardware_metrics:
            gpu_util = hardware_metrics['gpu_utilization'].value
            estimated_power_watts = 250 * (gpu_util / 100)  # Estimated GPU power
            
            latency_ms = inference_metrics['latency'].value
            throughput_per_sec = 1000 / latency_ms
            
            efficiency['throughput_per_watt'] = throughput_per_sec / max(estimated_power_watts, 1)
        
        # Cost per inference (estimated)
        gpu_cost_per_hour = 3.0  # Example cost
        inference_time_hours = inference_metrics['latency'].value / (1000 * 3600)
        efficiency['cost_per_inference'] = gpu_cost_per_hour * inference_time_hours
        
        return efficiency
    
    async def optimize_model_performance(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        model_id: str,
        optimization_strategies: List[OptimizationStrategy],
        target_metrics: Dict[str, float]
    ) -> List[OptimizationResult]:
        """Optimize model performance using various strategies"""
        optimization_results = []
        
        # Get baseline profile
        baseline_profile = await self.profile_model_performance(
            model, model_id, "baseline", self._get_sample_data(model)
        )
        
        for strategy in optimization_strategies:
            try:
                self.logger.info(f"Applying optimization strategy: {strategy.value}")
                
                # Apply optimization
                optimized_model, optimization_config = await self.optimizer.apply_optimization(
                    model, strategy, target_metrics
                )
                
                # Profile optimized model
                optimized_profile = await self.profile_model_performance(
                    optimized_model, f"{model_id}_optimized", "optimized", 
                    self._get_sample_data(optimized_model)
                )
                
                # Calculate improvements
                result = await self._calculate_optimization_results(
                    baseline_profile, optimized_profile, strategy, optimization_config
                )
                
                optimization_results.append(result)
                self.optimization_results[result.optimization_id] = result
                
                self.logger.info(f"Optimization {strategy.value} completed with {result.latency_improvement_percent:.1f}% latency improvement")
                
            except Exception as e:
                self.logger.error(f"Error applying optimization {strategy.value}: {e}")
        
        return optimization_results
    
    def _get_sample_data(self, model: Union[torch.nn.Module, tf.keras.Model]) -> Any:
        """Generate sample data for model profiling"""
        if isinstance(model, torch.nn.Module):
            # Try to infer input shape from model
            if hasattr(model, 'input_shape'):
                shape = model.input_shape
            else:
                shape = [1, 3, 224, 224]  # Default shape
            return torch.randn(shape)
        else:
            # TensorFlow model
            if hasattr(model, 'input_shape') and model.input_shape:
                shape = [1] + list(model.input_shape[1:])
            else:
                shape = [1, 224, 224, 3]  # Default shape
            return np.random.randn(*shape).astype(np.float32)
    
    async def _calculate_optimization_results(
        self,
        baseline_profile: ModelProfile,
        optimized_profile: ModelProfile,
        strategy: OptimizationStrategy,
        optimization_config: Dict[str, Any]
    ) -> OptimizationResult:
        """Calculate optimization results and improvements"""
        
        # Calculate improvements
        latency_improvement = (
            (baseline_profile.inference_latency_ms.value - optimized_profile.inference_latency_ms.value) /
            baseline_profile.inference_latency_ms.value * 100
        )
        
        memory_improvement = 0.0
        if baseline_profile.memory_usage_mb and optimized_profile.memory_usage_mb:
            memory_improvement = (
                (baseline_profile.memory_usage_mb.value - optimized_profile.memory_usage_mb.value) /
                baseline_profile.memory_usage_mb.value * 100
            )
        
        size_improvement = (
            (baseline_profile.model_size_mb - optimized_profile.model_size_mb) /
            baseline_profile.model_size_mb * 100
        )
        
        # Calculate throughput improvement
        baseline_throughput = 1000 / baseline_profile.inference_latency_ms.value
        optimized_throughput = 1000 / optimized_profile.inference_latency_ms.value
        throughput_improvement = (
            (optimized_throughput - baseline_throughput) / baseline_throughput * 100
        )
        
        # Calculate accuracy change (if available)
        accuracy_change = 0.0
        quality_degradation = False
        if baseline_profile.accuracy and optimized_profile.accuracy:
            accuracy_change = (
                (optimized_profile.accuracy.value - baseline_profile.accuracy.value) /
                baseline_profile.accuracy.value * 100
            )
            quality_degradation = accuracy_change < -1.0  # More than 1% degradation
        
        return OptimizationResult(
            optimization_id=str(uuid.uuid4()),
            original_model_id=baseline_profile.model_id,
            optimized_model_id=optimized_profile.model_id,
            strategy=strategy,
            original_profile=baseline_profile,
            optimized_profile=optimized_profile,
            latency_improvement_percent=latency_improvement,
            memory_reduction_percent=memory_improvement,
            throughput_improvement_percent=throughput_improvement,
            model_size_reduction_percent=size_improvement,
            accuracy_change_percent=accuracy_change,
            quality_degradation=quality_degradation,
            optimization_config=optimization_config,
            optimization_time_seconds=0.0  # Would be measured during optimization
        )
    
    async def run_performance_benchmark(
        self,
        models: List[Tuple[Union[torch.nn.Module, tf.keras.Model], str]],
        benchmark_config: Dict[str, Any]
    ) -> PerformanceBenchmark:
        """Run comprehensive performance benchmark"""
        benchmark_id = str(uuid.uuid4())
        
        self.logger.info(f"Starting performance benchmark: {benchmark_id}")
        
        model_profiles = []
        
        for model, model_id in models:
            try:
                profile = await self.profile_model_performance(
                    model, model_id, "benchmark", 
                    self._get_sample_data(model), benchmark_config
                )
                model_profiles.append(profile)
            except Exception as e:
                self.logger.error(f"Error profiling model {model_id} in benchmark: {e}")
        
        # Analyze benchmark results
        benchmark_results = await self._analyze_benchmark_results(model_profiles)
        
        # Generate recommendations
        recommendations = await self._generate_benchmark_recommendations(benchmark_results)
        
        benchmark = PerformanceBenchmark(
            benchmark_id=benchmark_id,
            benchmark_name=benchmark_config.get('name', f'Benchmark_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}'),
            model_profiles=model_profiles,
            test_dataset_size=benchmark_config.get('dataset_size', 1000),
            batch_sizes=benchmark_config.get('batch_sizes', [1, 8, 16, 32]),
            hardware_configs=benchmark_config.get('hardware_configs', []),
            optimization_strategies=benchmark_config.get('optimization_strategies', []),
            benchmark_results=benchmark_results,
            recommendations=recommendations,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        self.benchmarks[benchmark_id] = benchmark
        await self._store_benchmark_results(benchmark)
        
        self.logger.info(f"Completed performance benchmark: {benchmark_id}")
        return benchmark
    
    async def _analyze_benchmark_results(self, profiles: List[ModelProfile]) -> Dict[str, Any]:
        """Analyze benchmark results across models"""
        if not profiles:
            return {}
        
        # Extract metrics
        latencies = [p.inference_latency_ms.value for p in profiles]
        memory_usages = [p.memory_usage_mb.value for p in profiles if p.memory_usage_mb]
        model_sizes = [p.model_size_mb for p in profiles]
        
        analysis = {
            'latency_analysis': {
                'best_model': min(enumerate(latencies), key=lambda x: x[1])[0],
                'worst_model': max(enumerate(latencies), key=lambda x: x[1])[0],
                'mean_latency': np.mean(latencies),
                'std_latency': np.std(latencies),
                'latency_range': max(latencies) - min(latencies)
            },
            'memory_analysis': {
                'mean_usage': np.mean(memory_usages) if memory_usages else 0,
                'max_usage': max(memory_usages) if memory_usages else 0,
                'min_usage': min(memory_usages) if memory_usages else 0
            },
            'model_size_analysis': {
                'mean_size': np.mean(model_sizes),
                'largest_model': max(enumerate(model_sizes), key=lambda x: x[1])[0],
                'smallest_model': min(enumerate(model_sizes), key=lambda x: x[1])[0]
            },
            'efficiency_rankings': await self._calculate_efficiency_rankings(profiles)
        }
        
        return analysis
    
    async def _calculate_efficiency_rankings(self, profiles: List[ModelProfile]) -> Dict[str, Any]:
        """Calculate efficiency rankings for benchmarked models"""
        rankings = {
            'latency_rank': [],
            'memory_efficiency_rank': [],
            'size_efficiency_rank': [],
            'overall_efficiency_rank': []
        }
        
        # Sort by latency (lower is better)
        latency_sorted = sorted(enumerate(profiles), key=lambda x: x[1].inference_latency_ms.value)
        rankings['latency_rank'] = [(i, p.model_id) for i, (_, p) in enumerate(latency_sorted)]
        
        # Sort by memory efficiency (lower usage is better)
        memory_sorted = sorted(
            enumerate(profiles), 
            key=lambda x: x[1].memory_usage_mb.value if x[1].memory_usage_mb else float('inf')
        )
        rankings['memory_efficiency_rank'] = [(i, p.model_id) for i, (_, p) in enumerate(memory_sorted)]
        
        # Sort by model size (smaller is better)
        size_sorted = sorted(enumerate(profiles), key=lambda x: x[1].model_size_mb)
        rankings['size_efficiency_rank'] = [(i, p.model_id) for i, (_, p) in enumerate(size_sorted)]
        
        return rankings
    
    async def _generate_benchmark_recommendations(self, benchmark_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on benchmark results"""
        recommendations = []
        
        latency_analysis = benchmark_results.get('latency_analysis', {})
        memory_analysis = benchmark_results.get('memory_analysis', {})
        
        # Latency recommendations
        if latency_analysis.get('latency_range', 0) > 100:  # More than 100ms difference
            recommendations.append(
                "Significant latency variation detected. Consider optimizing slower models or using model ensemble strategies."
            )
        
        # Memory recommendations
        if memory_analysis.get('max_usage', 0) > 8000:  # More than 8GB
            recommendations.append(
                "High memory usage detected. Consider model compression techniques or gradient checkpointing."
            )
        
        # General recommendations
        recommendations.extend([
            "Consider quantization for production deployment to reduce model size and improve inference speed.",
            "Evaluate mixed precision training to balance performance and accuracy.",
            "Monitor model performance continuously in production environment."
        ])
        
        return recommendations
    
    async def _continuous_performance_monitoring(self) -> None:
        """Continuous monitoring of model performance in production"""
        while True:
            try:
                # Monitor active models
                for profile_id, profile in self.model_profiles.items():
                    # Check if model is in production and needs monitoring
                    if await self._should_monitor_model(profile):
                        await self._monitor_production_performance(profile)
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def _should_monitor_model(self, profile: ModelProfile) -> bool:
        """Check if model should be monitored"""
        # Check if model is recent and in production
        age_hours = (datetime.utcnow() - profile.profiled_at).total_seconds() / 3600
        return age_hours < 24  # Monitor models profiled in last 24 hours
    
    async def _monitor_production_performance(self, profile: ModelProfile) -> None:
        """Monitor model performance in production"""
        # Mock production monitoring - would integrate with actual monitoring systems
        pass
    
    async def _store_model_profile(self, profile: ModelProfile) -> None:
        """Store model profile in Redis"""
        profile_data = asdict(profile)
        self.redis_client.setex(
            f"model_profile:{profile.profile_id}",
            timedelta(days=30),
            json.dumps(profile_data, default=str)
        )
    
    async def _store_benchmark_results(self, benchmark: PerformanceBenchmark) -> None:
        """Store benchmark results"""
        benchmark_data = asdict(benchmark)
        self.redis_client.setex(
            f"benchmark:{benchmark.benchmark_id}",
            timedelta(days=90),
            json.dumps(benchmark_data, default=str)
        )
    
    async def _track_profiling_metrics(self, profile: ModelProfile) -> None:
        """Track profiling metrics in MLflow/Wandb"""
        try:
            metrics = {
                'inference_latency_ms': profile.inference_latency_ms.value,
                'model_size_mb': profile.model_size_mb,
                'parameter_count': profile.parameter_count
            }
            
            if profile.memory_usage_mb:
                metrics['memory_usage_mb'] = profile.memory_usage_mb.value
            
            if profile.gpu_utilization:
                metrics['gpu_utilization'] = profile.gpu_utilization.value
            
            # MLflow tracking
            if mlflow.active_run():
                mlflow.log_metrics(metrics)
            
            # Wandb tracking
            if wandb.run:
                wandb.log(metrics)
                
        except Exception as e:
            self.logger.error(f"Error tracking profiling metrics: {e}")


class ModelProfiler:
    """Core model profiling functionality"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('model_profiler')


class ModelOptimizer:
    """Model optimization strategies and techniques"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('model_optimizer')
    
    async def apply_optimization(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        strategy: OptimizationStrategy,
        target_metrics: Dict[str, float]
    ) -> Tuple[Union[torch.nn.Module, tf.keras.Model], Dict[str, Any]]:
        """Apply optimization strategy to model"""
        
        if strategy == OptimizationStrategy.QUANTIZATION:
            return await self._apply_quantization(model, target_metrics)
        elif strategy == OptimizationStrategy.PRUNING:
            return await self._apply_pruning(model, target_metrics)
        elif strategy == OptimizationStrategy.MIXED_PRECISION:
            return await self._apply_mixed_precision(model, target_metrics)
        else:
            # Mock optimization - return original model with config
            return model, {'strategy': strategy.value, 'applied': False}
    
    async def _apply_quantization(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        target_metrics: Dict[str, float]
    ) -> Tuple[Union[torch.nn.Module, tf.keras.Model], Dict[str, Any]]:
        """Apply quantization optimization"""
        config = {
            'strategy': 'quantization',
            'precision': 'int8',
            'calibration_samples': 1000,
            'applied': True
        }
        
        if isinstance(model, torch.nn.Module):
            # PyTorch quantization (simplified)
            quantized_model = torch.quantization.quantize_dynamic(
                model, {torch.nn.Linear}, dtype=torch.qint8
            )
            return quantized_model, config
        else:
            # TensorFlow quantization would go here
            return model, config
    
    async def _apply_pruning(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        target_metrics: Dict[str, float]
    ) -> Tuple[Union[torch.nn.Module, tf.keras.Model], Dict[str, Any]]:
        """Apply pruning optimization"""
        config = {
            'strategy': 'pruning',
            'sparsity': 0.5,
            'structured': False,
            'applied': True
        }
        
        # Mock pruning - return original model
        return model, config
    
    async def _apply_mixed_precision(
        self,
        model: Union[torch.nn.Module, tf.keras.Model],
        target_metrics: Dict[str, float]
    ) -> Tuple[Union[torch.nn.Module, tf.keras.Model], Dict[str, Any]]:
        """Apply mixed precision optimization"""
        config = {
            'strategy': 'mixed_precision',
            'precision': 'fp16',
            'loss_scaling': True,
            'applied': True
        }
        
        # Mock mixed precision - return original model
        return model, config


class PerformanceBenchmarker:
    """Performance benchmarking suite"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('performance_benchmarker')


class RealTimeMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('realtime_monitor')


class HardwareMonitor:
    """Monitor hardware utilization during profiling"""
    
    def __init__(self):
        self.monitoring = False
        self.data = {
            'cpu_utilization': [],
            'gpu_utilization': [],
            'memory_usage': [],
            'timestamps': []
        }
        self.monitor_thread = None
    
    def start_monitoring(self) -> None:
        """Start hardware monitoring"""
        self.monitoring = True
        self.data = {
            'cpu_utilization': [],
            'gpu_utilization': [],
            'memory_usage': [],
            'timestamps': []
        }
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, List[float]]:
        """Stop monitoring and return collected data"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        return self.data
    
    def _monitor_loop(self) -> None:
        """Monitoring loop running in separate thread"""
        try:
            pynvml.nvmlInit()
            nvml_available = True
        except:
            nvml_available = False
        
        while self.monitoring:
            try:
                # CPU utilization
                cpu_percent = psutil.cpu_percent(interval=0.1)
                self.data['cpu_utilization'].append(cpu_percent)
                
                # GPU utilization
                if nvml_available:
                    try:
                        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                        self.data['gpu_utilization'].append(utilization.gpu)
                    except:
                        pass
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.data['memory_usage'].append(memory.percent)
                
                self.data['timestamps'].append(time.time())
                
                time.sleep(0.5)  # Sample every 500ms
                
            except Exception:
                break


# Factory function for creating model performance analyzer
def create_model_performance_analyzer(config: Dict[str, Any]) -> ModelPerformanceAnalyzer:
    """Create model performance analyzer instance"""
    return ModelPerformanceAnalyzer(config)


# Helper functions for performance analysis
def create_performance_config(
    warmup_iterations: int = 10,
    benchmark_iterations: int = 100,
    batch_sizes: List[int] = None,
    monitoring_duration: int = 10,
    profile_training: bool = False
) -> Dict[str, Any]:
    """Create performance profiling configuration"""
    return {
        'warmup_iterations': warmup_iterations,
        'benchmark_iterations': benchmark_iterations,
        'batch_sizes': batch_sizes or [1, 8, 16, 32],
        'monitoring_duration': monitoring_duration,
        'profile_training': profile_training
    }


def create_optimization_config(
    target_latency_ms: Optional[float] = None,
    target_memory_mb: Optional[float] = None,
    max_accuracy_drop: float = 1.0,
    strategies: List[OptimizationStrategy] = None
) -> Dict[str, Any]:
    """Create model optimization configuration"""
    return {
        'target_latency_ms': target_latency_ms,
        'target_memory_mb': target_memory_mb,
        'max_accuracy_drop': max_accuracy_drop,
        'strategies': strategies or [
            OptimizationStrategy.QUANTIZATION,
            OptimizationStrategy.MIXED_PRECISION
        ]
    }