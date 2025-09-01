"""Automated Load Testing Orchestrator
Implements production-ready automated load testing with continuous monitoring
"""

import asyncio
import json
import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import aiohttp
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class LoadTestType(Enum):
    """Types of load tests"""
    SMOKE_TEST = "smoke"  # Minimal load to verify basic functionality
    LOAD_TEST = "load"    # Expected normal load
    STRESS_TEST = "stress"  # High load to find breaking point
    SPIKE_TEST = "spike"   # Sudden load increase
    VOLUME_TEST = "volume"  # Large amounts of data
    ENDURANCE_TEST = "endurance"  # Extended duration


class TestPattern(Enum):
    """Load test execution patterns"""
    CONSTANT = "constant"    # Constant load
    RAMP_UP = "ramp_up"     # Gradual increase
    STEP_UP = "step_up"     # Step increases
    PYRAMID = "pyramid"     # Ramp up then down
    SPIKE = "spike"         # Quick spikes


@dataclass
class LoadTestConfig:
    """Configuration for load testing"""
    name: str
    test_type: LoadTestType
    pattern: TestPattern
    target_urls: List[str]
    
    # Load parameters
    max_users: int = 100
    duration_seconds: int = 300
    ramp_up_seconds: int = 60
    
    # Request parameters
    requests_per_second: int = 10
    timeout_seconds: int = 30
    
    # Test scenarios
    scenarios: List[Dict[str, Any]] = field(default_factory=list)
    
    # Success criteria
    max_response_time_ms: int = 2000
    max_error_rate_percent: float = 1.0
    min_throughput_rps: int = 8
    
    # Monitoring
    monitor_endpoints: List[str] = field(default_factory=list)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    
    # Scheduling
    schedule_cron: str = None  # For automated runs
    auto_stop_on_failure: bool = True


@dataclass
class RequestMetric:
    """Individual request metrics"""
    timestamp: datetime
    url: str
    method: str
    response_time_ms: float
    status_code: int
    success: bool
    error_message: str = None
    request_size_bytes: int = 0
    response_size_bytes: int = 0


@dataclass
class LoadTestResult:
    """Load test execution result"""
    test_id: str
    config: LoadTestConfig
    start_time: datetime
    end_time: datetime = None
    status: str = "running"  # "running", "completed", "failed", "stopped"
    
    # Performance metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_rate_percent: float = 0.0
    
    # Response time metrics
    avg_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    
    # Throughput metrics
    requests_per_second: float = 0.0
    peak_rps: float = 0.0
    
    # Resource metrics
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    
    # Raw metrics
    request_metrics: List[RequestMetric] = field(default_factory=list)
    
    # Test results
    success_criteria_met: bool = False
    failed_criteria: List[str] = field(default_factory=list)
    
    # Report
    detailed_report: Dict[str, Any] = field(default_factory=dict)


class LoadTestOrchestrator:
    """
    Orchestrator for automated load testing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_tests: Dict[str, LoadTestResult] = {}
        self.test_history: List[LoadTestResult] = []
        self.session: aiohttp.ClientSession = None
        self.executor = ThreadPoolExecutor(max_workers=100)
        
    async def initialize(self) -> bool:
        """Initialize load testing system"""
        try:
            # Create HTTP session with optimized settings
            connector = aiohttp.TCPConnector(
                limit=200,
                limit_per_host=100,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=60
            )
            
            timeout = aiohttp.ClientTimeout(total=300, connect=30)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Ainflue-LoadTester/1.0',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate'
                }
            )
            
            self.logger.info("Load testing orchestrator initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize load testing: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        self.executor.shutdown(wait=True)
    
    async def start_load_test(self, config: LoadTestConfig) -> str:
        """Start a new load test"""
        test_id = f"loadtest_{config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            self.logger.info(f"Starting load test: {test_id}")
            
            # Create test result
            result = LoadTestResult(
                test_id=test_id,
                config=config,
                start_time=datetime.now()
            )
            
            self.active_tests[test_id] = result
            
            # Start test execution in background
            asyncio.create_task(self._execute_load_test(test_id))
            
            return test_id
            
        except Exception as e:
            self.logger.error(f"Error starting load test: {e}")
            raise
    
    async def _execute_load_test(self, test_id: str):
        """Execute the load test"""
        result = self.active_tests[test_id]
        config = result.config
        
        try:
            self.logger.info(f"Executing load test {test_id}")
            result.status = "running"
            
            # Generate load based on pattern
            if config.pattern == TestPattern.CONSTANT:
                await self._execute_constant_load(result)
            elif config.pattern == TestPattern.RAMP_UP:
                await self._execute_ramp_up_load(result)
            elif config.pattern == TestPattern.SPIKE:
                await self._execute_spike_load(result)
            else:
                await self._execute_constant_load(result)  # Default
            
            # Calculate final metrics
            await self._calculate_final_metrics(result)
            
            # Check success criteria
            self._evaluate_success_criteria(result)
            
            result.status = "completed"
            result.end_time = datetime.now()
            
            # Move to history
            self.test_history.append(result)
            del self.active_tests[test_id]
            
            self.logger.info(f"Load test {test_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error executing load test {test_id}: {e}")
            result.status = "failed"
            result.end_time = datetime.now()
            if test_id in self.active_tests:
                self.test_history.append(result)
                del self.active_tests[test_id]
    
    async def _execute_constant_load(self, result: LoadTestResult):
        """Execute constant load pattern"""
        config = result.config
        end_time = result.start_time + timedelta(seconds=config.duration_seconds)
        
        # Calculate interval between requests
        interval = 1.0 / config.requests_per_second
        
        tasks = []
        request_count = 0
        
        while datetime.now() < end_time and result.status == "running":
            # Create batch of concurrent requests
            batch_size = min(config.requests_per_second, 50)  # Limit batch size
            
            for _ in range(batch_size):
                if datetime.now() >= end_time:
                    break
                
                # Select target URL (round-robin)
                url = config.target_urls[request_count % len(config.target_urls)]
                
                # Create request task
                task = asyncio.create_task(self._make_request(url, result))
                tasks.append(task)
                request_count += 1
                
                # Small delay to distribute requests
                await asyncio.sleep(interval / batch_size)
            
            # Wait for batch completion
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                tasks.clear()
            
            # Monitor system resources
            await self._monitor_system_resources(result)
            
            # Check for early termination
            if (config.auto_stop_on_failure and 
                result.error_rate_percent > config.max_error_rate_percent * 2):
                self.logger.warning(f"Stopping test {result.test_id} due to high error rate")
                break
    
    async def _execute_ramp_up_load(self, result: LoadTestResult):
        """Execute ramp-up load pattern"""
        config = result.config
        
        # Phase 1: Ramp up
        ramp_duration = config.ramp_up_seconds
        steady_duration = config.duration_seconds - ramp_duration
        
        self.logger.info(f"Ramp-up phase: {ramp_duration}s to {config.max_users} users")
        
        end_ramp = result.start_time + timedelta(seconds=ramp_duration)
        current_rps = 1
        
        while datetime.now() < end_ramp and result.status == "running":
            # Calculate current RPS based on ramp-up progress
            progress = (datetime.now() - result.start_time).total_seconds() / ramp_duration
            current_rps = int(1 + (config.requests_per_second - 1) * progress)
            
            # Execute requests for current interval
            await self._execute_requests_for_interval(result, current_rps, 1.0)
            
            await self._monitor_system_resources(result)
        
        # Phase 2: Steady load
        if steady_duration > 0:
            self.logger.info(f"Steady load phase: {steady_duration}s at {config.requests_per_second} RPS")
            end_steady = datetime.now() + timedelta(seconds=steady_duration)
            
            while datetime.now() < end_steady and result.status == "running":
                await self._execute_requests_for_interval(result, config.requests_per_second, 1.0)
                await self._monitor_system_resources(result)
    
    async def _execute_spike_load(self, result: LoadTestResult):
        """Execute spike load pattern"""
        config = result.config
        
        # Normal load for 30% of time
        normal_duration = config.duration_seconds * 0.3
        spike_duration = config.duration_seconds * 0.4
        recovery_duration = config.duration_seconds * 0.3
        
        normal_rps = config.requests_per_second
        spike_rps = config.requests_per_second * 3  # 3x spike
        
        # Phase 1: Normal load
        await self._execute_load_phase(result, normal_rps, normal_duration, "Normal")
        
        # Phase 2: Spike
        await self._execute_load_phase(result, spike_rps, spike_duration, "Spike")
        
        # Phase 3: Recovery
        await self._execute_load_phase(result, normal_rps, recovery_duration, "Recovery")
    
    async def _execute_load_phase(self, result: LoadTestResult, rps: int, duration: float, phase_name: str):
        """Execute a specific phase of load testing"""
        self.logger.info(f"{phase_name} phase: {duration}s at {rps} RPS")
        
        end_time = datetime.now() + timedelta(seconds=duration)
        
        while datetime.now() < end_time and result.status == "running":
            await self._execute_requests_for_interval(result, rps, 1.0)
            await self._monitor_system_resources(result)
    
    async def _execute_requests_for_interval(self, result: LoadTestResult, rps: int, interval: float):
        """Execute requests for a specific interval"""
        tasks = []
        request_interval = interval / rps if rps > 0 else 1.0
        
        for i in range(int(rps)):
            url = result.config.target_urls[i % len(result.config.target_urls)]
            task = asyncio.create_task(self._make_request(url, result))
            tasks.append(task)
            
            if i < rps - 1:  # Don't sleep after last request
                await asyncio.sleep(request_interval)
        
        # Wait for all requests to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _make_request(self, url: str, result: LoadTestResult) -> RequestMetric:
        """Make a single HTTP request and record metrics"""
        start_time = time.time()
        timestamp = datetime.now()
        
        try:
            async with self.session.get(url) as response:
                await response.read()  # Ensure response body is consumed
                
                response_time_ms = (time.time() - start_time) * 1000
                success = response.status < 400
                
                metric = RequestMetric(
                    timestamp=timestamp,
                    url=url,
                    method="GET",
                    response_time_ms=response_time_ms,
                    status_code=response.status,
                    success=success,
                    request_size_bytes=0,  # Could be calculated
                    response_size_bytes=len(await response.read()) if hasattr(response, '_body') else 0
                )
                
                # Update result metrics
                result.total_requests += 1
                if success:
                    result.successful_requests += 1
                else:
                    result.failed_requests += 1
                
                result.request_metrics.append(metric)
                return metric
                
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            
            metric = RequestMetric(
                timestamp=timestamp,
                url=url,
                method="GET",
                response_time_ms=response_time_ms,
                status_code=0,
                success=False,
                error_message=str(e)
            )
            
            result.total_requests += 1
            result.failed_requests += 1
            result.request_metrics.append(metric)
            
            return metric
    
    async def _monitor_system_resources(self, result: LoadTestResult):
        """Monitor system resources during test"""
        try:
            import psutil
            
            # Update system metrics
            result.cpu_usage_percent = psutil.cpu_percent(interval=0.1)
            result.memory_usage_percent = psutil.virtual_memory().percent
            
        except ImportError:
            # psutil not available, skip monitoring
            pass
        except Exception as e:
            self.logger.warning(f"Error monitoring system resources: {e}")
    
    async def _calculate_final_metrics(self, result: LoadTestResult):
        """Calculate final performance metrics"""
        if not result.request_metrics:
            return
        
        # Response time metrics
        response_times = [m.response_time_ms for m in result.request_metrics if m.success]
        if response_times:
            result.avg_response_time_ms = statistics.mean(response_times)
            result.min_response_time_ms = min(response_times)
            result.max_response_time_ms = max(response_times)
            
            sorted_times = sorted(response_times)
            n = len(sorted_times)
            result.p50_response_time_ms = sorted_times[int(n * 0.5)]
            result.p95_response_time_ms = sorted_times[int(n * 0.95)]
            result.p99_response_time_ms = sorted_times[int(n * 0.99)]
        
        # Error rate
        if result.total_requests > 0:
            result.error_rate_percent = (result.failed_requests / result.total_requests) * 100
        
        # Throughput
        if result.end_time:
            duration = (result.end_time - result.start_time).total_seconds()
            if duration > 0:
                result.requests_per_second = result.total_requests / duration
        
        # Calculate peak RPS (in 1-second windows)
        self._calculate_peak_rps(result)
        
        # Generate detailed report
        result.detailed_report = {
            "test_summary": {
                "duration_seconds": (result.end_time - result.start_time).total_seconds() if result.end_time else 0,
                "total_requests": result.total_requests,
                "successful_requests": result.successful_requests,
                "failed_requests": result.failed_requests,
                "error_rate_percent": result.error_rate_percent
            },
            "performance": {
                "avg_response_time_ms": result.avg_response_time_ms,
                "p95_response_time_ms": result.p95_response_time_ms,
                "p99_response_time_ms": result.p99_response_time_ms,
                "requests_per_second": result.requests_per_second,
                "peak_rps": result.peak_rps
            },
            "system_resources": {
                "cpu_usage_percent": result.cpu_usage_percent,
                "memory_usage_percent": result.memory_usage_percent
            }
        }
    
    def _calculate_peak_rps(self, result: LoadTestResult):
        """Calculate peak requests per second in 1-second windows"""
        if not result.request_metrics:
            return
        
        # Group requests by second
        second_counts = {}
        for metric in result.request_metrics:
            second = metric.timestamp.replace(microsecond=0)
            second_counts[second] = second_counts.get(second, 0) + 1
        
        if second_counts:
            result.peak_rps = max(second_counts.values())
    
    def _evaluate_success_criteria(self, result: LoadTestResult):
        """Evaluate if test meets success criteria"""
        config = result.config
        failed_criteria = []
        
        # Check response time
        if result.p95_response_time_ms > config.max_response_time_ms:
            failed_criteria.append(f"P95 response time ({result.p95_response_time_ms:.1f}ms) exceeds limit ({config.max_response_time_ms}ms)")
        
        # Check error rate
        if result.error_rate_percent > config.max_error_rate_percent:
            failed_criteria.append(f"Error rate ({result.error_rate_percent:.2f}%) exceeds limit ({config.max_error_rate_percent}%)")
        
        # Check throughput
        if result.requests_per_second < config.min_throughput_rps:
            failed_criteria.append(f"Throughput ({result.requests_per_second:.1f} RPS) below minimum ({config.min_throughput_rps} RPS)")
        
        result.failed_criteria = failed_criteria
        result.success_criteria_met = len(failed_criteria) == 0
    
    async def stop_test(self, test_id: str) -> bool:
        """Stop a running test"""
        if test_id in self.active_tests:
            result = self.active_tests[test_id]
            result.status = "stopped"
            result.end_time = datetime.now()
            
            # Calculate metrics for stopped test
            await self._calculate_final_metrics(result)
            self._evaluate_success_criteria(result)
            
            # Move to history
            self.test_history.append(result)
            del self.active_tests[test_id]
            
            self.logger.info(f"Load test {test_id} stopped")
            return True
        
        return False
    
    async def get_test_status(self, test_id: str) -> Optional[LoadTestResult]:
        """Get status of a specific test"""
        if test_id in self.active_tests:
            return self.active_tests[test_id]
        
        # Check history
        for result in self.test_history:
            if result.test_id == test_id:
                return result
        
        return None
    
    async def get_active_tests(self) -> List[LoadTestResult]:
        """Get all active tests"""
        return list(self.active_tests.values())
    
    async def get_test_history(self, limit: int = 50) -> List[LoadTestResult]:
        """Get test history"""
        return sorted(self.test_history, key=lambda x: x.start_time, reverse=True)[:limit]
    
    async def generate_performance_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate performance report from recent tests"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_tests = [t for t in self.test_history if t.start_time >= cutoff_date]
        
        if not recent_tests:
            return {"message": "No recent tests found"}
        
        # Calculate aggregate metrics
        successful_tests = [t for t in recent_tests if t.success_criteria_met]
        
        avg_response_times = [t.avg_response_time_ms for t in recent_tests if t.avg_response_time_ms > 0]
        p95_response_times = [t.p95_response_time_ms for t in recent_tests if t.p95_response_time_ms > 0]
        error_rates = [t.error_rate_percent for t in recent_tests]
        throughputs = [t.requests_per_second for t in recent_tests if t.requests_per_second > 0]
        
        report = {
            "period": f"Last {days} days",
            "summary": {
                "total_tests": len(recent_tests),
                "successful_tests": len(successful_tests),
                "success_rate_percent": (len(successful_tests) / len(recent_tests)) * 100 if recent_tests else 0,
                "total_requests": sum(t.total_requests for t in recent_tests)
            },
            "performance_trends": {
                "avg_response_time_ms": statistics.mean(avg_response_times) if avg_response_times else 0,
                "avg_p95_response_time_ms": statistics.mean(p95_response_times) if p95_response_times else 0,
                "avg_error_rate_percent": statistics.mean(error_rates) if error_rates else 0,
                "avg_throughput_rps": statistics.mean(throughputs) if throughputs else 0
            },
            "test_types": {},
            "recommendations": []
        }
        
        # Group by test type
        for test_type in LoadTestType:
            type_tests = [t for t in recent_tests if t.config.test_type == test_type]
            if type_tests:
                report["test_types"][test_type.value] = {
                    "count": len(type_tests),
                    "success_rate": (len([t for t in type_tests if t.success_criteria_met]) / len(type_tests)) * 100
                }
        
        # Generate recommendations
        if report["performance_trends"]["avg_error_rate_percent"] > 2.0:
            report["recommendations"].append("High error rates detected - investigate application stability")
        
        if report["performance_trends"]["avg_p95_response_time_ms"] > 2000:
            report["recommendations"].append("Response times are high - consider performance optimization")
        
        if report["summary"]["success_rate_percent"] < 80:
            report["recommendations"].append("Low test success rate - review performance criteria and system capacity")
        
        return report


# Global load test orchestrator
load_test_orchestrator = LoadTestOrchestrator()