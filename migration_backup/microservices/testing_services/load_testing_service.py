"""
Load Testing Service - Enterprise High-Volume Testing
Ainflue Platform - Microservices Architecture

© FAHED MLAIEL 2024-2025 - CONFIDENTIAL ENTERPRISE MODULE
"""

import asyncio
import aiohttp
import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging
import psutil
import json
from datetime import datetime

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    target_service: str
    endpoint: str
    concurrent_users: int
    duration_minutes: int
    ramp_up_seconds: int
    think_time_seconds: float
    request_timeout: int
    max_retries: int

@dataclass
class LoadTestResult:
    """Load test execution result"""
    test_id: str
    config: LoadTestConfig
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput_rps: float
    error_rate: float
    cpu_usage: Dict[str, float]
    memory_usage: Dict[str, float]
    test_duration: float
    start_time: datetime
    end_time: datetime

class LoadTestingService:
    """
    Enterprise Load Testing Service
    
    Provides high-volume load testing capabilities for microservices
    with comprehensive performance metrics and resource monitoring.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=1000)
        self.active_tests = {}
        self.test_results = {}
        
    async def initialize(self) -> bool:
        """Initialize load testing service"""
        try:
            self.logger.info("Initializing Load Testing Service...")
            
            # Initialize performance monitoring
            self._init_performance_monitoring()
            
            # Setup test data management
            await self._setup_test_data()
            
            self.logger.info("Load Testing Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Load Testing Service: {e}")
            return False
    
    def _init_performance_monitoring(self):
        """Initialize performance monitoring"""
        self.cpu_monitor = psutil.cpu_percent(interval=1)
        self.memory_monitor = psutil.virtual_memory()
        
    async def _setup_test_data(self):
        """Setup test data for load testing"""
        self.test_payloads = {
            "api_gateway": {
                "content_upload": {"file": "test_content.mp4", "type": "video"},
                "user_auth": {"username": "test_user", "password": "test_pass"},
                "analytics": {"event": "page_view", "timestamp": int(time.time())}
            },
            "ai_services": {
                "inference": {"input": "test content", "model": "classification"},
                "training": {"dataset": "test_dataset", "epochs": 5},
                "validation": {"model_id": "test_model", "validation_set": "test_val"}
            },
            "content_services": {
                "upload": {"content": "test_content", "format": "mp4"},
                "processing": {"content_id": "test_123", "operation": "transcode"},
                "optimization": {"content_id": "test_123", "quality": "HD"}
            }
        }
    
    async def run_load_test(self, config: LoadTestConfig) -> LoadTestResult:
        """
        Execute comprehensive load test
        
        Args:
            config: Load test configuration
            
        Returns:
            LoadTestResult: Complete test results with metrics
        """
        test_id = f"load_test_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting load test {test_id} for {config.target_service}")
            self.active_tests[test_id] = config
            
            # Initialize result tracking
            response_times = []
            successful_requests = 0
            failed_requests = 0
            cpu_usage = []
            memory_usage = []
            
            # Calculate test parameters
            total_duration = config.duration_minutes * 60
            ramp_up_interval = config.ramp_up_seconds / config.concurrent_users
            
            # Start performance monitoring
            monitor_task = asyncio.create_task(
                self._monitor_system_resources(test_id, cpu_usage, memory_usage)
            )
            
            # Execute load test with ramp-up
            semaphore = asyncio.Semaphore(config.concurrent_users)
            tasks = []
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=config.request_timeout)
            ) as session:
                
                # Ramp-up phase
                for i in range(config.concurrent_users):
                    task = asyncio.create_task(
                        self._execute_user_simulation(
                            session, config, semaphore, total_duration,
                            response_times, successful_requests, failed_requests
                        )
                    )
                    tasks.append(task)
                    
                    # Ramp-up delay
                    if i < config.concurrent_users - 1:
                        await asyncio.sleep(ramp_up_interval)
                
                # Wait for all tasks to complete
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Stop monitoring
            monitor_task.cancel()
            
            end_time = datetime.now()
            test_duration = (end_time - start_time).total_seconds()
            
            # Calculate metrics
            result = self._calculate_test_metrics(
                test_id, config, response_times, successful_requests, 
                failed_requests, cpu_usage, memory_usage, 
                test_duration, start_time, end_time
            )
            
            self.test_results[test_id] = result
            del self.active_tests[test_id]
            
            self.logger.info(f"Load test {test_id} completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Load test {test_id} failed: {e}")
            if test_id in self.active_tests:
                del self.active_tests[test_id]
            raise
    
    async def _execute_user_simulation(
        self, session: aiohttp.ClientSession, config: LoadTestConfig,
        semaphore: asyncio.Semaphore, duration: float,
        response_times: List[float], successful_requests: int, failed_requests: int
    ):
        """Simulate individual user load"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            async with semaphore:
                try:
                    # Get test payload for service
                    payload = self._get_test_payload(config.target_service)
                    
                    # Execute request with timing
                    request_start = time.time()
                    
                    async with session.post(
                        f"http://localhost:8000{config.endpoint}",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        await response.read()
                        request_time = time.time() - request_start
                        
                        if response.status < 400:
                            response_times.append(request_time * 1000)  # Convert to ms
                            successful_requests += 1
                        else:
                            failed_requests += 1
                            self.logger.warning(f"Request failed with status {response.status}")
                
                except Exception as e:
                    failed_requests += 1
                    self.logger.error(f"Request exception: {e}")
                
                # Think time between requests
                if config.think_time_seconds > 0:
                    await asyncio.sleep(config.think_time_seconds)
    
    def _get_test_payload(self, service: str) -> Dict[str, Any]:
        """Get appropriate test payload for service"""
        if service in self.test_payloads:
            payloads = self.test_payloads[service]
            # Rotate through different payload types
            return list(payloads.values())[int(time.time()) % len(payloads)]
        return {"test": "data", "timestamp": time.time()}
    
    async def _monitor_system_resources(
        self, test_id: str, cpu_usage: List[float], memory_usage: List[float]
    ):
        """Monitor system resources during test"""
        try:
            while test_id in self.active_tests:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                cpu_usage.append(cpu_percent)
                memory_usage.append(memory_percent)
                
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
        except asyncio.CancelledError:
            pass
    
    def _calculate_test_metrics(
        self, test_id: str, config: LoadTestConfig, response_times: List[float],
        successful_requests: int, failed_requests: int, 
        cpu_usage: List[float], memory_usage: List[float],
        test_duration: float, start_time: datetime, end_time: datetime
    ) -> LoadTestResult:
        """Calculate comprehensive test metrics"""
        
        total_requests = successful_requests + failed_requests
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = self._calculate_percentile(response_times, 95)
            p99_response_time = self._calculate_percentile(response_times, 99)
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        throughput_rps = total_requests / test_duration if test_duration > 0 else 0
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        cpu_stats = {
            "avg": statistics.mean(cpu_usage) if cpu_usage else 0,
            "max": max(cpu_usage) if cpu_usage else 0,
            "min": min(cpu_usage) if cpu_usage else 0
        }
        
        memory_stats = {
            "avg": statistics.mean(memory_usage) if memory_usage else 0,
            "max": max(memory_usage) if memory_usage else 0,
            "min": min(memory_usage) if memory_usage else 0
        }
        
        return LoadTestResult(
            test_id=test_id,
            config=config,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            throughput_rps=throughput_rps,
            error_rate=error_rate,
            cpu_usage=cpu_stats,
            memory_usage=memory_stats,
            test_duration=test_duration,
            start_time=start_time,
            end_time=end_time
        )
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile from response time data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def run_spike_test(self, base_config: LoadTestConfig, spike_multiplier: int = 5) -> LoadTestResult:
        """Execute spike testing with sudden load increase"""
        spike_config = LoadTestConfig(
            target_service=base_config.target_service,
            endpoint=base_config.endpoint,
            concurrent_users=base_config.concurrent_users * spike_multiplier,
            duration_minutes=2,  # Short spike duration
            ramp_up_seconds=5,   # Very fast ramp-up
            think_time_seconds=base_config.think_time_seconds,
            request_timeout=base_config.request_timeout,
            max_retries=base_config.max_retries
        )
        
        return await self.run_load_test(spike_config)
    
    async def run_endurance_test(self, base_config: LoadTestConfig, duration_hours: int = 2) -> LoadTestResult:
        """Execute endurance testing for extended periods"""
        endurance_config = LoadTestConfig(
            target_service=base_config.target_service,
            endpoint=base_config.endpoint,
            concurrent_users=base_config.concurrent_users,
            duration_minutes=duration_hours * 60,  # Convert to minutes
            ramp_up_seconds=base_config.ramp_up_seconds,
            think_time_seconds=base_config.think_time_seconds,
            request_timeout=base_config.request_timeout,
            max_retries=base_config.max_retries
        )
        
        return await self.run_load_test(endurance_config)
    
    def get_test_results(self, test_id: Optional[str] = None) -> Dict[str, LoadTestResult]:
        """Get test results"""
        if test_id:
            return {test_id: self.test_results.get(test_id)}
        return self.test_results
    
    def get_active_tests(self) -> Dict[str, LoadTestConfig]:
        """Get currently running tests"""
        return self.active_tests
    
    async def generate_load_test_report(self, test_id: str) -> Dict[str, Any]:
        """Generate comprehensive load test report"""
        if test_id not in self.test_results:
            raise ValueError(f"Test result not found: {test_id}")
        
        result = self.test_results[test_id]
        
        report = {
            "test_summary": {
                "test_id": result.test_id,
                "target_service": result.config.target_service,
                "test_duration": f"{result.test_duration:.2f} seconds",
                "concurrent_users": result.config.concurrent_users,
                "total_requests": result.total_requests
            },
            "performance_metrics": {
                "avg_response_time": f"{result.avg_response_time:.2f} ms",
                "p95_response_time": f"{result.p95_response_time:.2f} ms",
                "p99_response_time": f"{result.p99_response_time:.2f} ms",
                "throughput": f"{result.throughput_rps:.2f} requests/sec",
                "error_rate": f"{result.error_rate:.2f}%"
            },
            "system_resources": {
                "cpu_usage": result.cpu_usage,
                "memory_usage": result.memory_usage
            },
            "test_verdict": self._generate_test_verdict(result),
            "recommendations": self._generate_recommendations(result)
        }
        
        return report
    
    def _generate_test_verdict(self, result: LoadTestResult) -> str:
        """Generate test verdict based on results"""
        if result.error_rate > 5:
            return "FAIL - High error rate"
        elif result.avg_response_time > 1000:  # 1 second
            return "FAIL - Poor response time"
        elif result.cpu_usage["avg"] > 90:
            return "WARNING - High CPU usage"
        elif result.memory_usage["avg"] > 90:
            return "WARNING - High memory usage"
        else:
            return "PASS - Performance within acceptable limits"
    
    def _generate_recommendations(self, result: LoadTestResult) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if result.avg_response_time > 500:
            recommendations.append("Consider optimizing service response time")
        
        if result.error_rate > 1:
            recommendations.append("Investigate and fix service errors")
        
        if result.cpu_usage["avg"] > 80:
            recommendations.append("Consider scaling CPU resources")
        
        if result.memory_usage["avg"] > 80:
            recommendations.append("Consider scaling memory resources")
        
        if result.throughput_rps < 100:
            recommendations.append("Investigate throughput bottlenecks")
        
        if not recommendations:
            recommendations.append("Performance is within acceptable limits")
        
        return recommendations

# Service instance
load_testing_service = LoadTestingService()