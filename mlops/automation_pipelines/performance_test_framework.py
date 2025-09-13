"""
Enterprise Performance Test Framework for MLOps
ML Engineer + DevOps implementation with comprehensive benchmarking and optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import time
import numpy as np
import pandas as pd
import psutil
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import statistics
import uuid
from pathlib import Path
import pickle
import warnings
from abc import ABC, abstractmethod
import gc
import tracemalloc

logger = logging.getLogger(__name__)


class PerformanceTestType(Enum):
    """Types of performance tests"""
    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    SPIKE_TEST = "spike_test"
    ENDURANCE_TEST = "endurance_test"
    VOLUME_TEST = "volume_test"
    LATENCY_TEST = "latency_test"
    THROUGHPUT_TEST = "throughput_test"
    RESOURCE_TEST = "resource_test"
    SCALABILITY_TEST = "scalability_test"
    BASELINE_TEST = "baseline_test"


class TestPhase(Enum):
    """Performance test phases"""
    RAMP_UP = "ramp_up"
    STEADY_STATE = "steady_state"
    RAMP_DOWN = "ramp_down"
    SPIKE = "spike"
    RECOVERY = "recovery"


class MetricType(Enum):
    """Performance metric types"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    GPU_USAGE = "gpu_usage"
    CUSTOM = "custom"


@dataclass
class PerformanceTarget:
    """Performance target definition"""
    metric_name: str
    metric_type: MetricType
    target_value: float
    threshold_type: str = "max"  # max, min, avg
    tolerance_percent: float = 10.0
    critical: bool = True


@dataclass
class LoadPattern:
    """Load pattern configuration"""
    pattern_type: str = "constant"  # constant, ramp, spike, step
    initial_load: int = 1
    target_load: int = 100
    ramp_duration_seconds: int = 60
    steady_duration_seconds: int = 300
    ramp_down_duration_seconds: int = 60


@dataclass
class ResourceMetrics:
    """System resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    gpu_percent: float = 0.0
    gpu_memory_mb: float = 0.0


@dataclass
class PerformanceMetrics:
    """Performance test metrics"""
    test_id: str
    metric_type: MetricType
    values: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    
    # Statistical metrics
    min_value: float = 0.0
    max_value: float = 0.0
    mean_value: float = 0.0
    median_value: float = 0.0
    p95_value: float = 0.0
    p99_value: float = 0.0
    std_deviation: float = 0.0
    
    # Additional metrics
    total_samples: int = 0
    errors_count: int = 0
    success_rate: float = 100.0


@dataclass
class PerformanceTestCase:
    """Performance test case definition"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    test_type: PerformanceTestType = PerformanceTestType.LOAD_TEST
    
    # Load configuration
    load_pattern: LoadPattern = field(default_factory=LoadPattern)
    max_concurrent_users: int = 100
    total_requests: Optional[int] = None
    test_duration_seconds: int = 300
    
    # Performance targets
    performance_targets: List[PerformanceTarget] = field(default_factory=list)
    
    # Test configuration
    warmup_requests: int = 10
    cooldown_seconds: int = 30
    data_collection_interval: float = 1.0
    
    # Test functions
    test_function: Optional[Callable] = None
    data_generator: Optional[Callable] = None
    validator: Optional[Callable] = None
    
    # Environment
    environment_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceTestResult:
    """Performance test result"""
    test_case_id: str
    test_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Test status
    status: str = "completed"
    error_message: Optional[str] = None
    
    # Performance metrics
    metrics: Dict[str, PerformanceMetrics] = field(default_factory=dict)
    resource_metrics: List[ResourceMetrics] = field(default_factory=list)
    
    # Summary statistics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    requests_per_second: float = 0.0
    avg_response_time: float = 0.0
    
    # Target compliance
    targets_met: Dict[str, bool] = field(default_factory=dict)
    performance_score: float = 0.0
    
    # Additional data
    artifacts: Dict[str, str] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class ResourceMonitor:
    """System resource monitoring during tests"""
    
    def __init__(self, collection_interval: float = 1.0):
        self.collection_interval = collection_interval
        self.monitoring = False
        self.metrics: List[ResourceMetrics] = []
        self.monitor_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.metrics.clear()
        self.monitor_thread = threading.Thread(target=self._collect_metrics)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Resource monitoring stopped")
    
    def _collect_metrics(self):
        """Collect system metrics"""
        try:
            # Get initial network stats
            net_io_start = psutil.net_io_counters()
            disk_io_start = psutil.disk_io_counters()
            
            while self.monitoring:
                try:
                    # CPU and memory
                    cpu_percent = psutil.cpu_percent(interval=None)
                    memory = psutil.virtual_memory()
                    
                    # Disk I/O
                    disk_io_current = psutil.disk_io_counters()
                    disk_read_mb = (disk_io_current.read_bytes - disk_io_start.read_bytes) / (1024 * 1024)
                    disk_write_mb = (disk_io_current.write_bytes - disk_io_start.write_bytes) / (1024 * 1024)
                    
                    # Network I/O
                    net_io_current = psutil.net_io_counters()
                    net_sent_mb = (net_io_current.bytes_sent - net_io_start.bytes_sent) / (1024 * 1024)
                    net_recv_mb = (net_io_current.bytes_recv - net_io_start.bytes_recv) / (1024 * 1024)
                    
                    # GPU metrics (mock for now)
                    gpu_percent = 0.0
                    gpu_memory_mb = 0.0
                    
                    # Try to get GPU metrics if available
                    try:
                        # This would integrate with nvidia-ml-py or similar
                        pass
                    except:
                        pass
                    
                    metrics = ResourceMetrics(
                        timestamp=datetime.utcnow(),
                        cpu_percent=cpu_percent,
                        memory_percent=memory.percent,
                        memory_mb=memory.used / (1024 * 1024),
                        disk_io_read_mb=disk_read_mb,
                        disk_io_write_mb=disk_write_mb,
                        network_sent_mb=net_sent_mb,
                        network_recv_mb=net_recv_mb,
                        gpu_percent=gpu_percent,
                        gpu_memory_mb=gpu_memory_mb
                    )
                    
                    self.metrics.append(metrics)
                    
                except Exception as e:
                    logger.warning(f"Failed to collect metrics: {e}")
                
                time.sleep(self.collection_interval)
                
        except Exception as e:
            logger.error(f"Resource monitoring failed: {e}")
    
    def get_metrics(self) -> List[ResourceMetrics]:
        """Get collected metrics"""
        return self.metrics.copy()


class LoadGenerator:
    """Generate load for performance testing"""
    
    def __init__(self):
        self.active_workers = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times: List[float] = []
        self.error_messages: List[str] = []
        
    async def generate_load(
        self,
        test_function: Callable,
        load_pattern: LoadPattern,
        test_duration_seconds: int,
        data_generator: Optional[Callable] = None,
        max_concurrent: int = 100
    ) -> Dict[str, Any]:
        """Generate load according to pattern"""
        try:
            logger.info(f"Starting load generation with pattern: {load_pattern.pattern_type}")
            
            start_time = time.time()
            end_time = start_time + test_duration_seconds
            
            # Reset counters
            self.total_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.response_times.clear()
            self.error_messages.clear()
            
            if load_pattern.pattern_type == "constant":
                await self._generate_constant_load(
                    test_function, load_pattern.target_load, end_time, 
                    data_generator, max_concurrent
                )
            elif load_pattern.pattern_type == "ramp":
                await self._generate_ramp_load(
                    test_function, load_pattern, end_time, 
                    data_generator, max_concurrent
                )
            elif load_pattern.pattern_type == "spike":
                await self._generate_spike_load(
                    test_function, load_pattern, end_time, 
                    data_generator, max_concurrent
                )
            else:
                await self._generate_constant_load(
                    test_function, load_pattern.target_load, end_time, 
                    data_generator, max_concurrent
                )
            
            total_duration = time.time() - start_time
            
            return {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
                "requests_per_second": self.total_requests / total_duration if total_duration > 0 else 0,
                "avg_response_time": statistics.mean(self.response_times) if self.response_times else 0,
                "response_times": self.response_times.copy(),
                "error_messages": self.error_messages.copy()
            }
            
        except Exception as e:
            logger.error(f"Load generation failed: {e}")
            raise

    async def _generate_constant_load(
        self,
        test_function: Callable,
        target_load: int,
        end_time: float,
        data_generator: Optional[Callable],
        max_concurrent: int
    ):
        """Generate constant load"""
        semaphore = asyncio.Semaphore(min(target_load, max_concurrent))
        
        async def worker():
            async with semaphore:
                await self._execute_single_request(test_function, data_generator)
        
        while time.time() < end_time:
            # Create batch of requests
            batch_size = min(target_load, max_concurrent)
            tasks = [worker() for _ in range(batch_size)]
            
            # Execute batch
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Small delay to control rate
            await asyncio.sleep(0.1)

    async def _generate_ramp_load(
        self,
        test_function: Callable,
        load_pattern: LoadPattern,
        end_time: float,
        data_generator: Optional[Callable],
        max_concurrent: int
    ):
        """Generate ramping load"""
        start_time = time.time()
        ramp_duration = load_pattern.ramp_duration_seconds
        steady_duration = load_pattern.steady_duration_seconds
        
        while time.time() < end_time:
            current_time = time.time()
            elapsed = current_time - start_time
            
            if elapsed < ramp_duration:
                # Ramp up phase
                progress = elapsed / ramp_duration
                current_load = int(load_pattern.initial_load + 
                                 (load_pattern.target_load - load_pattern.initial_load) * progress)
            elif elapsed < ramp_duration + steady_duration:
                # Steady state phase
                current_load = load_pattern.target_load
            else:
                # Ramp down phase
                ramp_down_start = ramp_duration + steady_duration
                ramp_down_elapsed = elapsed - ramp_down_start
                ramp_down_duration = load_pattern.ramp_down_duration_seconds
                
                if ramp_down_elapsed < ramp_down_duration:
                    progress = 1.0 - (ramp_down_elapsed / ramp_down_duration)
                    current_load = int(load_pattern.target_load * progress)
                else:
                    break
            
            # Execute requests for current load
            semaphore = asyncio.Semaphore(min(current_load, max_concurrent))
            
            async def worker():
                async with semaphore:
                    await self._execute_single_request(test_function, data_generator)
            
            tasks = [worker() for _ in range(min(current_load, max_concurrent))]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.sleep(0.1)

    async def _generate_spike_load(
        self,
        test_function: Callable,
        load_pattern: LoadPattern,
        end_time: float,
        data_generator: Optional[Callable],
        max_concurrent: int
    ):
        """Generate spike load"""
        start_time = time.time()
        spike_duration = 30  # 30 second spike
        
        while time.time() < end_time:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Determine if in spike period (every 2 minutes)
            cycle_time = elapsed % 120  # 2 minute cycles
            
            if cycle_time < spike_duration:
                # Spike phase
                current_load = load_pattern.target_load
            else:
                # Normal phase
                current_load = load_pattern.initial_load
            
            # Execute requests
            semaphore = asyncio.Semaphore(min(current_load, max_concurrent))
            
            async def worker():
                async with semaphore:
                    await self._execute_single_request(test_function, data_generator)
            
            tasks = [worker() for _ in range(min(current_load, max_concurrent))]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            await asyncio.sleep(0.1)

    async def _execute_single_request(
        self,
        test_function: Callable,
        data_generator: Optional[Callable]
    ):
        """Execute a single request"""
        try:
            start_time = time.time()
            
            # Generate test data if data generator provided
            test_data = None
            if data_generator:
                test_data = data_generator()
            
            # Execute test function
            if asyncio.iscoroutinefunction(test_function):
                if test_data is not None:
                    result = await test_function(test_data)
                else:
                    result = await test_function()
            else:
                if test_data is not None:
                    result = test_function(test_data)
                else:
                    result = test_function()
            
            response_time = time.time() - start_time
            
            self.total_requests += 1
            self.successful_requests += 1
            self.response_times.append(response_time)
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self.total_requests += 1
            self.failed_requests += 1
            self.response_times.append(response_time)
            self.error_messages.append(str(e))
            logger.debug(f"Request failed: {e}")


class PerformanceTestFramework:
    """
    Enterprise performance test framework for MLOps
    """
    
    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.load_generator = LoadGenerator()
        self.test_results: Dict[str, PerformanceTestResult] = {}
        
    async def run_performance_test(
        self,
        test_case: PerformanceTestCase
    ) -> PerformanceTestResult:
        """Run a performance test case"""
        result = PerformanceTestResult(
            test_case_id=test_case.id,
            test_name=test_case.name,
            start_time=datetime.utcnow()
        )
        
        try:
            logger.info(f"Starting performance test: {test_case.name}")
            
            # Validate test case
            if not test_case.test_function:
                raise ValueError("Test function is required")
            
            # Setup phase
            await self._setup_test_environment(test_case, result)
            
            # Warmup phase
            if test_case.warmup_requests > 0:
                logger.info(f"Running warmup with {test_case.warmup_requests} requests")
                await self._run_warmup(test_case)
            
            # Start resource monitoring
            self.resource_monitor.start_monitoring()
            
            try:
                # Execute performance test
                test_start_time = time.time()
                
                load_results = await self.load_generator.generate_load(
                    test_function=test_case.test_function,
                    load_pattern=test_case.load_pattern,
                    test_duration_seconds=test_case.test_duration_seconds,
                    data_generator=test_case.data_generator,
                    max_concurrent=test_case.max_concurrent_users
                )
                
                test_duration = time.time() - test_start_time
                
                # Stop resource monitoring
                self.resource_monitor.stop_monitoring()
                resource_metrics = self.resource_monitor.get_metrics()
                
                # Process results
                await self._process_test_results(test_case, result, load_results, resource_metrics)
                
                # Validate performance targets
                await self._validate_performance_targets(test_case, result)
                
                result.status = "completed"
                logger.info(f"Performance test completed: {test_case.name}")
                
            except Exception as e:
                self.resource_monitor.stop_monitoring()
                raise e
            
            # Cooldown phase
            if test_case.cooldown_seconds > 0:
                logger.info(f"Cooldown period: {test_case.cooldown_seconds}s")
                await asyncio.sleep(test_case.cooldown_seconds)
            
        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)
            logger.error(f"Performance test failed: {test_case.name} - {e}")
        
        finally:
            result.end_time = datetime.utcnow()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            # Store result
            self.test_results[test_case.id] = result
        
        return result

    async def _setup_test_environment(
        self,
        test_case: PerformanceTestCase,
        result: PerformanceTestResult
    ):
        """Setup test environment"""
        try:
            # Enable memory tracking if needed
            if test_case.test_type in [PerformanceTestType.RESOURCE_TEST, PerformanceTestType.ENDURANCE_TEST]:
                tracemalloc.start()
            
            # Setup environment variables
            for key, value in test_case.environment_config.items():
                result.artifacts[f"env_{key}"] = str(value)
            
        except Exception as e:
            logger.error(f"Environment setup failed: {e}")
            raise

    async def _run_warmup(self, test_case: PerformanceTestCase):
        """Run warmup requests"""
        try:
            warmup_generator = LoadGenerator()
            
            # Create simple load pattern for warmup
            warmup_pattern = LoadPattern(
                pattern_type="constant",
                target_load=min(10, test_case.max_concurrent_users),
                steady_duration_seconds=30
            )
            
            await warmup_generator.generate_load(
                test_function=test_case.test_function,
                load_pattern=warmup_pattern,
                test_duration_seconds=30,
                data_generator=test_case.data_generator,
                max_concurrent=10
            )
            
            # Force garbage collection after warmup
            gc.collect()
            
        except Exception as e:
            logger.warning(f"Warmup failed: {e}")

    async def _process_test_results(
        self,
        test_case: PerformanceTestCase,
        result: PerformanceTestResult,
        load_results: Dict[str, Any],
        resource_metrics: List[ResourceMetrics]
    ):
        """Process and analyze test results"""
        try:
            # Basic statistics
            result.total_requests = load_results["total_requests"]
            result.successful_requests = load_results["successful_requests"]
            result.failed_requests = load_results["failed_requests"]
            result.requests_per_second = load_results["requests_per_second"]
            result.avg_response_time = load_results["avg_response_time"]
            result.resource_metrics = resource_metrics
            
            # Process response time metrics
            response_times = load_results["response_times"]
            if response_times:
                latency_metrics = PerformanceMetrics(
                    test_id=test_case.id,
                    metric_type=MetricType.LATENCY,
                    values=response_times,
                    timestamps=[datetime.utcnow()] * len(response_times)  # Simplified
                )
                
                # Calculate statistics
                latency_metrics.total_samples = len(response_times)
                latency_metrics.min_value = min(response_times)
                latency_metrics.max_value = max(response_times)
                latency_metrics.mean_value = statistics.mean(response_times)
                latency_metrics.median_value = statistics.median(response_times)
                latency_metrics.std_deviation = statistics.stdev(response_times) if len(response_times) > 1 else 0
                
                # Calculate percentiles
                sorted_times = sorted(response_times)
                latency_metrics.p95_value = sorted_times[int(0.95 * len(sorted_times))]
                latency_metrics.p99_value = sorted_times[int(0.99 * len(sorted_times))]
                
                # Error rate
                latency_metrics.errors_count = load_results["failed_requests"]
                latency_metrics.success_rate = load_results["success_rate"]
                
                result.metrics["latency"] = latency_metrics
            
            # Process throughput metrics
            throughput_metrics = PerformanceMetrics(
                test_id=test_case.id,
                metric_type=MetricType.THROUGHPUT,
                values=[result.requests_per_second],
                timestamps=[datetime.utcnow()]
            )
            throughput_metrics.mean_value = result.requests_per_second
            result.metrics["throughput"] = throughput_metrics
            
            # Process resource metrics
            if resource_metrics:
                cpu_values = [m.cpu_percent for m in resource_metrics]
                memory_values = [m.memory_percent for m in resource_metrics]
                
                # CPU metrics
                cpu_metrics = PerformanceMetrics(
                    test_id=test_case.id,
                    metric_type=MetricType.CPU_USAGE,
                    values=cpu_values,
                    timestamps=[m.timestamp for m in resource_metrics]
                )
                cpu_metrics.min_value = min(cpu_values)
                cpu_metrics.max_value = max(cpu_values)
                cpu_metrics.mean_value = statistics.mean(cpu_values)
                cpu_metrics.median_value = statistics.median(cpu_values)
                result.metrics["cpu_usage"] = cpu_metrics
                
                # Memory metrics
                memory_metrics = PerformanceMetrics(
                    test_id=test_case.id,
                    metric_type=MetricType.MEMORY_USAGE,
                    values=memory_values,
                    timestamps=[m.timestamp for m in resource_metrics]
                )
                memory_metrics.min_value = min(memory_values)
                memory_metrics.max_value = max(memory_values)
                memory_metrics.mean_value = statistics.mean(memory_values)
                memory_metrics.median_value = statistics.median(memory_values)
                result.metrics["memory_usage"] = memory_metrics
            
        except Exception as e:
            logger.error(f"Results processing failed: {e}")
            raise

    async def _validate_performance_targets(
        self,
        test_case: PerformanceTestCase,
        result: PerformanceTestResult
    ):
        """Validate performance against targets"""
        try:
            targets_met = 0
            total_targets = len(test_case.performance_targets)
            
            for target in test_case.performance_targets:
                target_met = await self._check_performance_target(target, result)
                result.targets_met[target.metric_name] = target_met
                
                if target_met:
                    targets_met += 1
            
            # Calculate performance score
            if total_targets > 0:
                result.performance_score = (targets_met / total_targets) * 100
            else:
                result.performance_score = 100.0
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(test_case, result)
            
        except Exception as e:
            logger.error(f"Performance validation failed: {e}")
            raise

    async def _check_performance_target(
        self,
        target: PerformanceTarget,
        result: PerformanceTestResult
    ) -> bool:
        """Check if performance target is met"""
        try:
            # Get the relevant metric
            metric = None
            
            if target.metric_type == MetricType.LATENCY:
                metric = result.metrics.get("latency")
            elif target.metric_type == MetricType.THROUGHPUT:
                metric = result.metrics.get("throughput")
            elif target.metric_type == MetricType.CPU_USAGE:
                metric = result.metrics.get("cpu_usage")
            elif target.metric_type == MetricType.MEMORY_USAGE:
                metric = result.metrics.get("memory_usage")
            elif target.metric_type == MetricType.ERROR_RATE:
                error_rate = (result.failed_requests / result.total_requests * 100) if result.total_requests > 0 else 0
                return error_rate <= target.target_value
            
            if not metric:
                return False
            
            # Get value based on threshold type
            if target.threshold_type == "max":
                test_value = metric.max_value
            elif target.threshold_type == "min":
                test_value = metric.min_value
            elif target.threshold_type == "avg":
                test_value = metric.mean_value
            elif target.threshold_type == "p95":
                test_value = metric.p95_value
            elif target.threshold_type == "p99":
                test_value = metric.p99_value
            else:
                test_value = metric.mean_value
            
            # Check if target is met within tolerance
            tolerance = target.target_value * (target.tolerance_percent / 100)
            
            if target.threshold_type in ["max", "p95", "p99"]:
                # For max values, test value should be <= target
                return test_value <= (target.target_value + tolerance)
            else:
                # For min/avg values, test value should be >= target
                return test_value >= (target.target_value - tolerance)
            
        except Exception as e:
            logger.error(f"Target validation failed: {e}")
            return False

    async def _generate_recommendations(
        self,
        test_case: PerformanceTestCase,
        result: PerformanceTestResult
    ) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        try:
            # Latency recommendations
            if "latency" in result.metrics:
                latency = result.metrics["latency"]
                if latency.p95_value > 1.0:  # > 1 second
                    recommendations.append("Consider optimizing response time - P95 latency is high")
                if latency.std_deviation > latency.mean_value * 0.5:
                    recommendations.append("High latency variance detected - investigate inconsistent performance")
            
            # Throughput recommendations
            if "throughput" in result.metrics:
                if result.requests_per_second < test_case.max_concurrent_users * 0.5:
                    recommendations.append("Low throughput detected - consider performance optimization")
            
            # Resource recommendations
            if "cpu_usage" in result.metrics:
                cpu = result.metrics["cpu_usage"]
                if cpu.mean_value > 80:
                    recommendations.append("High CPU usage - consider scaling or optimization")
                elif cpu.mean_value < 20:
                    recommendations.append("Low CPU usage - system may be underutilized")
            
            if "memory_usage" in result.metrics:
                memory = result.metrics["memory_usage"]
                if memory.max_value > 85:
                    recommendations.append("High memory usage detected - monitor for memory leaks")
            
            # Error rate recommendations
            error_rate = (result.failed_requests / result.total_requests * 100) if result.total_requests > 0 else 0
            if error_rate > 1:
                recommendations.append(f"Error rate is {error_rate:.1f}% - investigate failures")
            
            # Scalability recommendations
            if test_case.test_type == PerformanceTestType.SCALABILITY_TEST:
                if result.performance_score < 80:
                    recommendations.append("Scalability issues detected - review architecture")
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
        
        return recommendations

    async def run_test_suite(
        self,
        test_cases: List[PerformanceTestCase],
        parallel: bool = False
    ) -> Dict[str, Any]:
        """Run a suite of performance tests"""
        try:
            logger.info(f"Running performance test suite with {len(test_cases)} tests")
            start_time = datetime.utcnow()
            
            if parallel:
                # Run tests in parallel (be careful with resource contention)
                results = await asyncio.gather(
                    *[self.run_performance_test(tc) for tc in test_cases],
                    return_exceptions=True
                )
            else:
                # Run tests sequentially
                results = []
                for test_case in test_cases:
                    result = await self.run_performance_test(test_case)
                    results.append(result)
            
            # Process suite results
            valid_results = [r for r in results if isinstance(r, PerformanceTestResult)]
            error_results = [r for r in results if isinstance(r, Exception)]
            
            # Calculate summary
            total_tests = len(test_cases)
            completed_tests = len([r for r in valid_results if r.status == "completed"])
            failed_tests = len([r for r in valid_results if r.status == "failed"]) + len(error_results)
            
            end_time = datetime.utcnow()
            total_duration = (end_time - start_time).total_seconds()
            
            # Calculate overall performance score
            performance_scores = [r.performance_score for r in valid_results if r.performance_score > 0]
            overall_score = statistics.mean(performance_scores) if performance_scores else 0
            
            summary = {
                "total_tests": total_tests,
                "completed": completed_tests,
                "failed": failed_tests,
                "success_rate": (completed_tests / total_tests * 100) if total_tests > 0 else 0,
                "overall_performance_score": overall_score,
                "total_duration_seconds": total_duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "parallel_execution": parallel,
                "results": valid_results
            }
            
            logger.info(f"Performance test suite completed: {completed_tests}/{total_tests} passed")
            return summary
            
        except Exception as e:
            logger.error(f"Performance test suite execution failed: {e}")
            raise

    async def generate_performance_report(
        self,
        suite_results: Dict[str, Any],
        output_path: Path
    ) -> str:
        """Generate comprehensive performance test report"""
        try:
            results = suite_results["results"]
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .test-result {{ margin: 15px 0; padding: 15px; border-left: 4px solid #ddd; }}
        .completed {{ border-left-color: #4CAF50; }}
        .failed {{ border-left-color: #f44336; }}
        .metrics {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; }}
        .recommendations {{ background-color: #fff3cd; padding: 10px; margin: 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .chart {{ width: 100%; height: 300px; margin: 20px 0; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="header">
        <h1>Performance Test Report</h1>
        <p>Generated: {datetime.utcnow().isoformat()}</p>
        <p>Overall Performance Score: {suite_results['overall_performance_score']:.1f}%</p>
    </div>
    
    <div class="summary">
        <h3>Summary</h3>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Tests</td><td>{suite_results['total_tests']}</td></tr>
            <tr><td>Completed</td><td>{suite_results['completed']}</td></tr>
            <tr><td>Failed</td><td>{suite_results['failed']}</td></tr>
            <tr><td>Success Rate</td><td>{suite_results['success_rate']:.1f}%</td></tr>
            <tr><td>Total Duration</td><td>{suite_results['total_duration_seconds']:.1f}s</td></tr>
        </table>
    </div>
    
    <div class="results">
        <h3>Test Results</h3>
"""
            
            for result in results:
                status_class = result.status
                
                html_content += f"""
        <div class="test-result {status_class}">
            <h4>{result.test_name}</h4>
            <p><strong>Status:</strong> {result.status.upper()}</p>
            <p><strong>Duration:</strong> {result.duration_seconds:.1f}s</p>
            <p><strong>Performance Score:</strong> {result.performance_score:.1f}%</p>
            
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Requests</td><td>{result.total_requests}</td></tr>
                <tr><td>Successful Requests</td><td>{result.successful_requests}</td></tr>
                <tr><td>Failed Requests</td><td>{result.failed_requests}</td></tr>
                <tr><td>Requests/Second</td><td>{result.requests_per_second:.2f}</td></tr>
                <tr><td>Avg Response Time</td><td>{result.avg_response_time:.3f}s</td></tr>
            </table>
"""
                
                if result.error_message:
                    html_content += f"<p><strong>Error:</strong> {result.error_message}</p>"
                
                # Performance metrics
                if result.metrics:
                    html_content += '<div class="metrics"><strong>Performance Metrics:</strong><ul>'
                    for metric_name, metric in result.metrics.items():
                        html_content += f"""
                <li>{metric_name.title()}: 
                    Min={metric.min_value:.3f}, 
                    Max={metric.max_value:.3f}, 
                    Avg={metric.mean_value:.3f}, 
                    P95={metric.p95_value:.3f}
                </li>"""
                    html_content += '</ul></div>'
                
                # Recommendations
                if result.recommendations:
                    html_content += '<div class="recommendations"><strong>Recommendations:</strong><ul>'
                    for rec in result.recommendations:
                        html_content += f'<li>{rec}</li>'
                    html_content += '</ul></div>'
                
                html_content += "</div>"
            
            html_content += """
    </div>
</body>
</html>
"""
            
            # Write report
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html_content, encoding='utf-8')
            
            logger.info(f"Performance test report generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate performance test report: {e}")
            raise

    async def benchmark_model_performance(
        self,
        model_function: Callable,
        test_data_generator: Callable,
        benchmark_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Benchmark ML model performance"""
        try:
            logger.info("Starting ML model performance benchmark")
            
            # Create benchmark test cases
            test_cases = []
            
            # Latency benchmark
            latency_test = PerformanceTestCase(
                name="model_latency_benchmark",
                description="Benchmark model inference latency",
                test_type=PerformanceTestType.LATENCY_TEST,
                load_pattern=LoadPattern(
                    pattern_type="constant",
                    target_load=1,
                    steady_duration_seconds=60
                ),
                test_duration_seconds=60,
                test_function=model_function,
                data_generator=test_data_generator,
                performance_targets=[
                    PerformanceTarget(
                        metric_name="inference_latency",
                        metric_type=MetricType.LATENCY,
                        target_value=0.1,  # 100ms
                        threshold_type="p95"
                    )
                ]
            )
            test_cases.append(latency_test)
            
            # Throughput benchmark
            throughput_test = PerformanceTestCase(
                name="model_throughput_benchmark",
                description="Benchmark model throughput",
                test_type=PerformanceTestType.THROUGHPUT_TEST,
                load_pattern=LoadPattern(
                    pattern_type="constant",
                    target_load=50,
                    steady_duration_seconds=120
                ),
                test_duration_seconds=120,
                max_concurrent_users=50,
                test_function=model_function,
                data_generator=test_data_generator,
                performance_targets=[
                    PerformanceTarget(
                        metric_name="throughput",
                        metric_type=MetricType.THROUGHPUT,
                        target_value=100,  # 100 requests/second
                        threshold_type="avg"
                    )
                ]
            )
            test_cases.append(throughput_test)
            
            # Stress test
            stress_test = PerformanceTestCase(
                name="model_stress_test",
                description="Stress test model under high load",
                test_type=PerformanceTestType.STRESS_TEST,
                load_pattern=LoadPattern(
                    pattern_type="ramp",
                    initial_load=10,
                    target_load=200,
                    ramp_duration_seconds=60,
                    steady_duration_seconds=180,
                    ramp_down_duration_seconds=60
                ),
                test_duration_seconds=300,
                max_concurrent_users=200,
                test_function=model_function,
                data_generator=test_data_generator,
                performance_targets=[
                    PerformanceTarget(
                        metric_name="error_rate",
                        metric_type=MetricType.ERROR_RATE,
                        target_value=5.0,  # 5% max error rate
                        threshold_type="max"
                    )
                ]
            )
            test_cases.append(stress_test)
            
            # Run benchmark suite
            results = await self.run_test_suite(test_cases, parallel=False)
            
            return results
            
        except Exception as e:
            logger.error(f"Model performance benchmark failed: {e}")
            raise


# Factory functions
def create_performance_test_framework() -> PerformanceTestFramework:
    """Create a new performance test framework instance"""
    return PerformanceTestFramework()


def create_performance_target(
    metric_name: str,
    metric_type: MetricType,
    target_value: float,
    threshold_type: str = "max"
) -> PerformanceTarget:
    """Create a performance target"""
    return PerformanceTarget(
        metric_name=metric_name,
        metric_type=metric_type,
        target_value=target_value,
        threshold_type=threshold_type
    )


def create_load_pattern(
    pattern_type: str = "constant",
    target_load: int = 100,
    duration_seconds: int = 300
) -> LoadPattern:
    """Create a load pattern"""
    return LoadPattern(
        pattern_type=pattern_type,
        target_load=target_load,
        steady_duration_seconds=duration_seconds
    )


# Example usage
if __name__ == "__main__":
    async def main():
        # Create framework
        framework = create_performance_test_framework()
        
        # Mock ML model function
        async def mock_ml_model(data=None):
            # Simulate model inference
            await asyncio.sleep(0.05)  # 50ms inference time
            return {"prediction": np.random.random(), "confidence": 0.95}
        
        # Mock data generator
        def mock_data_generator():
            return {
                "features": np.random.random(10).tolist(),
                "metadata": {"timestamp": datetime.utcnow().isoformat()}
            }
        
        # Create performance test
        test_case = PerformanceTestCase(
            name="ml_model_performance_test",
            description="Test ML model performance under load",
            test_type=PerformanceTestType.LOAD_TEST,
            load_pattern=create_load_pattern("constant", 50, 60),
            test_duration_seconds=60,
            max_concurrent_users=50,
            test_function=mock_ml_model,
            data_generator=mock_data_generator,
            performance_targets=[
                create_performance_target(
                    "response_time", MetricType.LATENCY, 0.1, "p95"
                ),
                create_performance_target(
                    "throughput", MetricType.THROUGHPUT, 40, "avg"
                )
            ]
        )
        
        print("Running performance test...")
        
        # Run test
        result = await framework.run_performance_test(test_case)
        
        print(f"Performance test completed:")
        print(f"- Status: {result.status}")
        print(f"- Duration: {result.duration_seconds:.1f}s")
        print(f"- Total requests: {result.total_requests}")
        print(f"- Success rate: {(result.successful_requests/result.total_requests*100):.1f}%")
        print(f"- Requests/second: {result.requests_per_second:.2f}")
        print(f"- Avg response time: {result.avg_response_time:.3f}s")
        print(f"- Performance score: {result.performance_score:.1f}%")
        
        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"- {rec}")
        
        # Generate report
        suite_results = {
            "total_tests": 1,
            "completed": 1 if result.status == "completed" else 0,
            "failed": 1 if result.status == "failed" else 0,
            "success_rate": 100 if result.status == "completed" else 0,
            "overall_performance_score": result.performance_score,
            "total_duration_seconds": result.duration_seconds,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat(),
            "parallel_execution": False,
            "results": [result]
        }
        
        report_path = Path("performance_test_report.html")
        await framework.generate_performance_report(suite_results, report_path)
        print(f"\nReport generated: {report_path}")
    
    asyncio.run(main())