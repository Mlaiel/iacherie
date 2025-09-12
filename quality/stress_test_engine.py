#!/usr/bin/env python3
"""
Stress Test Engine - Ainflue Quality Platform
===========================================

Enterprise-grade stress testing engine for performance validation under extreme load.
Demonstrates DevOps + Backend Senior + ML Engineer expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import threading
import multiprocessing
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import psutil
import aiohttp
import aiofiles
import numpy as np
from collections import defaultdict, deque
import statistics
import gc
import resource
import platform
import subprocess
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StressTestType(Enum):
    """Types of stress tests"""
    CPU_INTENSIVE = "cpu_intensive"
    MEMORY_INTENSIVE = "memory_intensive"
    IO_INTENSIVE = "io_intensive"
    NETWORK_INTENSIVE = "network_intensive"
    CONCURRENT_USERS = "concurrent_users"
    DATA_PROCESSING = "data_processing"
    API_ENDPOINT = "api_endpoint"
    DATABASE_LOAD = "database_load"
    MIXED_WORKLOAD = "mixed_workload"


class StressLevel(Enum):
    """Stress test intensity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"
    DESTRUCTIVE = "destructive"


class StressTestStatus(Enum):
    """Stress test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    TIMEOUT = "timeout"


@dataclass
class StressTestConfig:
    """Stress test configuration"""
    test_name: str
    test_type: StressTestType
    stress_level: StressLevel
    duration_seconds: int = 300
    max_workers: int = 100
    ramp_up_time: int = 30
    target_host: str = "localhost"
    target_port: int = 8000
    request_rate: int = 100  # requests per second
    memory_limit_mb: int = 1000
    cpu_threshold: float = 90.0
    timeout_seconds: int = 600
    metrics_interval: float = 1.0
    failure_threshold: float = 5.0  # percentage
    custom_payloads: List[Dict] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)


@dataclass
class ResourceMetrics:
    """System resource metrics during stress test"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_available: int
    disk_io_read: int
    disk_io_write: int
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    error_rate: float
    throughput: float


@dataclass
class StressTestResult:
    """Stress test execution result"""
    test_name: str
    test_type: StressTestType
    status: StressTestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_rate: float = 0.0
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    max_response_time: float = 0.0
    min_response_time: float = 0.0
    throughput_per_second: float = 0.0
    peak_cpu_usage: float = 0.0
    peak_memory_usage: float = 0.0
    system_degradation: float = 0.0
    breaking_point_reached: bool = False
    recovery_time_seconds: float = 0.0
    metrics_timeline: List[ResourceMetrics] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class StressTestEngine:
    """
    Enterprise stress testing engine
    
    Demonstrates expertise in:
    - DevOps: Infrastructure stress testing and monitoring
    - Backend Senior: System performance analysis and optimization
    - ML Engineer: Performance prediction and data analysis
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.active_tests = {}
        self.test_history = []
        self.metrics_collectors = []
        self.baseline_metrics = None
        self.worker_pool = None
        self.abort_flags = {}
        
        # Initialize directories
        self.reports_dir = Path("reports/stress_tests")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("StressTestEngine initialized")
    
    async def run_stress_test(self, config: StressTestConfig) -> StressTestResult:
        """
        Execute a comprehensive stress test
        
        DevOps expertise: Infrastructure monitoring and stress testing
        Backend expertise: Performance analysis and bottleneck identification
        ML expertise: Predictive analysis and pattern recognition
        """
        logger.info(f"Starting stress test: {config.test_name}")
        
        result = StressTestResult(
            test_name=config.test_name,
            test_type=config.test_type,
            status=StressTestStatus.RUNNING,
            start_time=datetime.now()
        )
        
        self.active_tests[config.test_name] = result
        self.abort_flags[config.test_name] = False
        
        try:
            # Pre-test system baseline
            await self._establish_baseline()
            
            # Execute stress test based on type
            if config.test_type == StressTestType.CPU_INTENSIVE:
                await self._run_cpu_stress_test(config, result)
            elif config.test_type == StressTestType.MEMORY_INTENSIVE:
                await self._run_memory_stress_test(config, result)
            elif config.test_type == StressTestType.IO_INTENSIVE:
                await self._run_io_stress_test(config, result)
            elif config.test_type == StressTestType.NETWORK_INTENSIVE:
                await self._run_network_stress_test(config, result)
            elif config.test_type == StressTestType.API_ENDPOINT:
                await self._run_api_stress_test(config, result)
            elif config.test_type == StressTestType.MIXED_WORKLOAD:
                await self._run_mixed_stress_test(config, result)
            else:
                raise ValueError(f"Unsupported stress test type: {config.test_type}")
            
            result.status = StressTestStatus.COMPLETED
            
        except asyncio.TimeoutError:
            result.status = StressTestStatus.TIMEOUT
            result.errors.append(f"Test timed out after {config.timeout_seconds} seconds")
        except Exception as e:
            result.status = StressTestStatus.FAILED
            result.errors.append(str(e))
            logger.error(f"Stress test failed: {e}")
        finally:
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            # Clean up
            self.abort_flags.pop(config.test_name, None)
            
            # Post-test analysis
            await self._analyze_results(result)
            await self._generate_recommendations(result)
            
            # Save results
            await self._save_test_results(result)
            
            self.test_history.append(result)
            
        logger.info(f"Stress test completed: {config.test_name}")
        return result
    
    async def _establish_baseline(self):
        """Establish system performance baseline"""
        logger.info("Establishing performance baseline")
        
        baseline_samples = []
        for _ in range(10):
            metrics = await self._collect_system_metrics()
            baseline_samples.append(metrics)
            await asyncio.sleep(0.5)
        
        self.baseline_metrics = {
            'cpu_avg': statistics.mean([m.cpu_usage for m in baseline_samples]),
            'memory_avg': statistics.mean([m.memory_usage for m in baseline_samples]),
            'network_baseline': statistics.mean([m.network_bytes_sent + m.network_bytes_recv for m in baseline_samples])
        }
        
        logger.info(f"Baseline established: CPU={self.baseline_metrics['cpu_avg']:.1f}%, Memory={self.baseline_metrics['memory_avg']:.1f}%")
    
    async def _run_cpu_stress_test(self, config: StressTestConfig, result: StressTestResult):
        """Run CPU-intensive stress test (DevOps + Backend expertise)"""
        logger.info("Starting CPU stress test")
        
        def cpu_intensive_task():
            """CPU-intensive computation task"""
            start_time = time.time()
            iterations = 0
            
            while (time.time() - start_time) < config.duration_seconds:
                if self.abort_flags.get(config.test_name, False):
                    break
                
                # Mathematical computations to stress CPU
                for i in range(10000):
                    _ = sum(x ** 2 for x in range(100))
                iterations += 1
            
            return iterations
        
        # Launch CPU stress workers
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            tasks = []
            
            # Ramp up workers gradually
            for i in range(config.max_workers):
                tasks.append(executor.submit(cpu_intensive_task))
                if i % 10 == 0:  # Add delay for gradual ramp-up
                    await asyncio.sleep(config.ramp_up_time / (config.max_workers / 10))
            
            # Monitor system during stress test
            await self._monitor_system_during_test(config, result)
            
            # Wait for all tasks to complete
            total_iterations = sum(task.result() for task in as_completed(tasks))
            result.total_requests = total_iterations
            result.successful_requests = total_iterations
    
    async def _run_memory_stress_test(self, config: StressTestConfig, result: StressTestResult):
        """Run memory-intensive stress test (Backend + ML Engineer expertise)"""
        logger.info("Starting memory stress test")
        
        def memory_intensive_task():
            """Memory allocation and manipulation task"""
            allocated_memory = []
            start_time = time.time()
            
            try:
                while (time.time() - start_time) < config.duration_seconds:
                    if self.abort_flags.get(config.test_name, False):
                        break
                    
                    # Allocate large arrays
                    data = np.random.random((1000, 1000)).astype(np.float64)
                    allocated_memory.append(data)
                    
                    # Perform operations on data
                    np.linalg.norm(data)
                    
                    # Occasionally free memory to simulate real workload
                    if len(allocated_memory) > 100:
                        allocated_memory.pop(0)
                        gc.collect()
                
                return len(allocated_memory)
                
            except MemoryError:
                logger.warning("Memory limit reached during stress test")
                return len(allocated_memory)
        
        # Launch memory stress workers
        with ThreadPoolExecutor(max_workers=min(config.max_workers, 20)) as executor:
            tasks = []
            
            for i in range(min(config.max_workers, 20)):
                tasks.append(executor.submit(memory_intensive_task))
                await asyncio.sleep(0.1)  # Gradual ramp-up
            
            # Monitor system during stress test
            await self._monitor_system_during_test(config, result)
            
            # Wait for completion
            total_allocations = sum(task.result() for task in as_completed(tasks))
            result.total_requests = total_allocations
            result.successful_requests = total_allocations
    
    async def _run_api_stress_test(self, config: StressTestConfig, result: StressTestResult):
        """Run API endpoint stress test (DevOps + Backend + Microservices expertise)"""
        logger.info("Starting API stress test")
        
        base_url = f"http://{config.target_host}:{config.target_port}"
        request_count = 0
        success_count = 0
        response_times = []
        
        async def make_request(session, payload=None):
            """Make HTTP request with timing"""
            nonlocal request_count, success_count
            
            start_time = time.time()
            try:
                if payload:
                    async with session.post(f"{base_url}/api/test", json=payload) as response:
                        await response.text()
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                        
                        if response.status < 400:
                            success_count += 1
                        request_count += 1
                        
                else:
                    async with session.get(f"{base_url}/api/health") as response:
                        await response.text()
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                        
                        if response.status < 400:
                            success_count += 1
                        request_count += 1
                        
            except Exception as e:
                request_count += 1
                logger.debug(f"Request failed: {e}")
        
        # Create HTTP session with connection pooling
        connector = aiohttp.TCPConnector(limit=config.max_workers, limit_per_host=config.max_workers)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            start_time = time.time()
            tasks = []
            
            # Launch concurrent requests
            while (time.time() - start_time) < config.duration_seconds:
                if self.abort_flags.get(config.test_name, False):
                    break
                
                # Create batch of requests
                batch_size = min(config.request_rate, config.max_workers)
                
                for _ in range(batch_size):
                    payload = config.custom_payloads[0] if config.custom_payloads else None
                    task = asyncio.create_task(make_request(session, payload))
                    tasks.append(task)
                
                # Wait for batch completion or continue
                if len(tasks) >= config.max_workers:
                    done, pending = await asyncio.wait(tasks[:batch_size], timeout=1.0)
                    tasks = list(pending) + tasks[batch_size:]
                
                await asyncio.sleep(1.0 / config.request_rate)
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.wait(tasks, timeout=30)
        
        # Calculate metrics
        result.total_requests = request_count
        result.successful_requests = success_count
        result.failed_requests = request_count - success_count
        result.error_rate = (result.failed_requests / max(request_count, 1)) * 100
        
        if response_times:
            result.average_response_time = statistics.mean(response_times)
            result.p95_response_time = np.percentile(response_times, 95)
            result.p99_response_time = np.percentile(response_times, 99)
            result.max_response_time = max(response_times)
            result.min_response_time = min(response_times)
        
        result.throughput_per_second = request_count / config.duration_seconds
    
    async def _run_mixed_stress_test(self, config: StressTestConfig, result: StressTestResult):
        """Run mixed workload stress test (Full-stack expertise)"""
        logger.info("Starting mixed workload stress test")
        
        # Run multiple stress tests concurrently
        cpu_config = StressTestConfig(
            test_name=f"{config.test_name}_cpu",
            test_type=StressTestType.CPU_INTENSIVE,
            stress_level=config.stress_level,
            duration_seconds=config.duration_seconds,
            max_workers=config.max_workers // 3
        )
        
        memory_config = StressTestConfig(
            test_name=f"{config.test_name}_memory",
            test_type=StressTestType.MEMORY_INTENSIVE,
            stress_level=config.stress_level,
            duration_seconds=config.duration_seconds,
            max_workers=config.max_workers // 3
        )
        
        api_config = StressTestConfig(
            test_name=f"{config.test_name}_api",
            test_type=StressTestType.API_ENDPOINT,
            stress_level=config.stress_level,
            duration_seconds=config.duration_seconds,
            max_workers=config.max_workers // 3,
            target_host=config.target_host,
            target_port=config.target_port
        )
        
        # Run tests concurrently
        tasks = [
            asyncio.create_task(self._run_cpu_stress_test(cpu_config, result)),
            asyncio.create_task(self._run_memory_stress_test(memory_config, result)),
            asyncio.create_task(self._run_api_stress_test(api_config, result))
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _monitor_system_during_test(self, config: StressTestConfig, result: StressTestResult):
        """Monitor system metrics during stress test (DevOps expertise)"""
        monitoring_start = time.time()
        
        while (time.time() - monitoring_start) < config.duration_seconds:
            if self.abort_flags.get(config.test_name, False):
                break
            
            metrics = await self._collect_system_metrics()
            result.metrics_timeline.append(metrics)
            
            # Track peak values
            result.peak_cpu_usage = max(result.peak_cpu_usage, metrics.cpu_usage)
            result.peak_memory_usage = max(result.peak_memory_usage, metrics.memory_usage)
            
            # Check for system degradation
            if metrics.cpu_usage > config.cpu_threshold:
                result.warnings.append(f"CPU usage exceeded threshold: {metrics.cpu_usage:.1f}%")
            
            if metrics.memory_usage > 95:
                result.warnings.append(f"Memory usage critical: {metrics.memory_usage:.1f}%")
                result.breaking_point_reached = True
            
            await asyncio.sleep(config.metrics_interval)
    
    async def _collect_system_metrics(self) -> ResourceMetrics:
        """Collect current system metrics (DevOps + Backend expertise)"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()
        
        # Get network connections count
        try:
            connections = len(psutil.net_connections())
        except:
            connections = 0
        
        return ResourceMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            memory_available=memory.available,
            disk_io_read=disk_io.read_bytes if disk_io else 0,
            disk_io_write=disk_io.write_bytes if disk_io else 0,
            network_bytes_sent=network_io.bytes_sent if network_io else 0,
            network_bytes_recv=network_io.bytes_recv if network_io else 0,
            active_connections=connections,
            response_time_avg=0.0,  # Will be filled by specific tests
            response_time_p95=0.0,
            response_time_p99=0.0,
            error_rate=0.0,
            throughput=0.0
        )
    
    async def _analyze_results(self, result: StressTestResult):
        """Analyze stress test results (ML Engineer expertise)"""
        if not result.metrics_timeline:
            return
        
        # Calculate system degradation
        baseline_cpu = self.baseline_metrics.get('cpu_avg', 0) if self.baseline_metrics else 0
        baseline_memory = self.baseline_metrics.get('memory_avg', 0) if self.baseline_metrics else 0
        
        avg_cpu_during_test = statistics.mean([m.cpu_usage for m in result.metrics_timeline])
        avg_memory_during_test = statistics.mean([m.memory_usage for m in result.metrics_timeline])
        
        cpu_degradation = max(0, avg_cpu_during_test - baseline_cpu)
        memory_degradation = max(0, avg_memory_during_test - baseline_memory)
        
        result.system_degradation = (cpu_degradation + memory_degradation) / 2
        
        # Analyze recovery time
        if result.breaking_point_reached:
            recovery_start = None
            for i, metrics in enumerate(reversed(result.metrics_timeline)):
                if metrics.cpu_usage < 50 and metrics.memory_usage < 80:
                    recovery_start = len(result.metrics_timeline) - i
                    break
            
            if recovery_start:
                result.recovery_time_seconds = (len(result.metrics_timeline) - recovery_start) * 1.0
    
    async def _generate_recommendations(self, result: StressTestResult):
        """Generate performance recommendations (Backend + ML expertise)"""
        recommendations = []
        
        # CPU analysis
        if result.peak_cpu_usage > 90:
            recommendations.append("Consider CPU scaling or optimization for high CPU usage")
        
        # Memory analysis
        if result.peak_memory_usage > 85:
            recommendations.append("Memory usage is high - consider memory optimization or scaling")
        
        # Error rate analysis
        if result.error_rate > 5:
            recommendations.append(f"High error rate ({result.error_rate:.1f}%) indicates system instability")
        
        # Performance analysis
        if result.average_response_time > 1000:  # 1 second
            recommendations.append("Response times are high - investigate bottlenecks")
        
        # Breaking point analysis
        if result.breaking_point_reached:
            recommendations.append("System breaking point reached - immediate scaling recommended")
        
        # Throughput analysis
        expected_throughput = 100  # baseline expectation
        if result.throughput_per_second < expected_throughput * 0.7:
            recommendations.append("Throughput below expected levels - performance tuning needed")
        
        result.recommendations = recommendations
    
    async def _save_test_results(self, result: StressTestResult):
        """Save test results to file (DevOps expertise)"""
        timestamp = result.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_{result.test_name}_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Convert result to dict for JSON serialization
        result_dict = {
            'test_name': result.test_name,
            'test_type': result.test_type.value,
            'status': result.status.value,
            'start_time': result.start_time.isoformat(),
            'end_time': result.end_time.isoformat() if result.end_time else None,
            'duration_seconds': result.duration_seconds,
            'total_requests': result.total_requests,
            'successful_requests': result.successful_requests,
            'failed_requests': result.failed_requests,
            'error_rate': result.error_rate,
            'average_response_time': result.average_response_time,
            'p95_response_time': result.p95_response_time,
            'p99_response_time': result.p99_response_time,
            'throughput_per_second': result.throughput_per_second,
            'peak_cpu_usage': result.peak_cpu_usage,
            'peak_memory_usage': result.peak_memory_usage,
            'system_degradation': result.system_degradation,
            'breaking_point_reached': result.breaking_point_reached,
            'recovery_time_seconds': result.recovery_time_seconds,
            'errors': result.errors,
            'warnings': result.warnings,
            'recommendations': result.recommendations,
            'metrics_count': len(result.metrics_timeline)
        }
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(result_dict, indent=2))
        
        logger.info(f"Stress test results saved to: {filepath}")
    
    async def abort_test(self, test_name: str):
        """Abort running stress test"""
        if test_name in self.abort_flags:
            self.abort_flags[test_name] = True
            logger.info(f"Aborting stress test: {test_name}")
    
    async def get_test_status(self, test_name: str) -> Optional[StressTestResult]:
        """Get current test status"""
        return self.active_tests.get(test_name)
    
    async def generate_stress_test_report(self, test_results: List[StressTestResult]) -> str:
        """Generate comprehensive stress test report (DevOps + Backend expertise)"""
        report = []
        report.append("# Stress Test Analysis Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary statistics
        total_tests = len(test_results)
        successful_tests = len([r for r in test_results if r.status == StressTestStatus.COMPLETED])
        
        report.append("## Summary")
        report.append(f"- Total Tests: {total_tests}")
        report.append(f"- Successful: {successful_tests}")
        report.append(f"- Success Rate: {(successful_tests/max(total_tests,1)*100):.1f}%")
        report.append("")
        
        # Individual test results
        for result in test_results:
            report.append(f"## Test: {result.test_name}")
            report.append(f"- Type: {result.test_type.value}")
            report.append(f"- Status: {result.status.value}")
            report.append(f"- Duration: {result.duration_seconds:.1f}s")
            report.append(f"- Peak CPU: {result.peak_cpu_usage:.1f}%")
            report.append(f"- Peak Memory: {result.peak_memory_usage:.1f}%")
            report.append(f"- Error Rate: {result.error_rate:.2f}%")
            
            if result.recommendations:
                report.append("### Recommendations:")
                for rec in result.recommendations:
                    report.append(f"- {rec}")
            
            report.append("")
        
        return "\n".join(report)


# Global instance
stress_test_engine = StressTestEngine()


async def run_stress_test(config: StressTestConfig) -> StressTestResult:
    """Convenience function to run stress test"""
    return await stress_test_engine.run_stress_test(config)


async def run_cpu_stress_test(duration: int = 300, workers: int = None) -> StressTestResult:
    """Quick CPU stress test"""
    workers = workers or multiprocessing.cpu_count()
    config = StressTestConfig(
        test_name="quick_cpu_stress",
        test_type=StressTestType.CPU_INTENSIVE,
        stress_level=StressLevel.HIGH,
        duration_seconds=duration,
        max_workers=workers
    )
    return await run_stress_test(config)


async def run_api_stress_test(host: str = "localhost", port: int = 8000, 
                             duration: int = 300, rps: int = 100) -> StressTestResult:
    """Quick API stress test"""
    config = StressTestConfig(
        test_name="quick_api_stress",
        test_type=StressTestType.API_ENDPOINT,
        stress_level=StressLevel.HIGH,
        duration_seconds=duration,
        target_host=host,
        target_port=port,
        request_rate=rps,
        max_workers=min(rps, 100)
    )
    return await run_stress_test(config)


if __name__ == "__main__":
    # Example usage
    async def main():
        # CPU stress test
        cpu_config = StressTestConfig(
            test_name="cpu_stress_demo",
            test_type=StressTestType.CPU_INTENSIVE,
            stress_level=StressLevel.HIGH,
            duration_seconds=60,
            max_workers=multiprocessing.cpu_count()
        )
        
        result = await run_stress_test(cpu_config)
        print(f"Stress test completed: {result.status.value}")
        print(f"Peak CPU: {result.peak_cpu_usage:.1f}%")
        print(f"Peak Memory: {result.peak_memory_usage:.1f}%")
        
        if result.recommendations:
            print("Recommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")
    
    asyncio.run(main())