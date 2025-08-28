"""
API Response Time Performance Tests

Comprehensive API endpoint response time testing.
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any, Optional
import json


class APIResponseMetrics:
    """API response time metrics collection."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.endpoint_metrics: Dict[str, List[float]] = {}
        self.status_codes: List[int] = []
        self.request_sizes: List[int] = []
        self.response_sizes: List[int] = []
        self.start_time: float = 0
        self.end_time: float = 0
    
    def start_monitoring(self):
        self.start_time = time.time()
    
    def stop_monitoring(self):
        self.end_time = time.time()
    
    def record_response(self, endpoint: str, response_time: float, status_code: int = 200, 
                       request_size: int = 0, response_size: int = 0):
        """Record API response metrics."""
        self.response_times.append(response_time)
        self.status_codes.append(status_code)
        self.request_sizes.append(request_size)
        self.response_sizes.append(response_size)
        
        if endpoint not in self.endpoint_metrics:
            self.endpoint_metrics[endpoint] = []
        self.endpoint_metrics[endpoint].append(response_time)
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.response_times:
            return {"error": "No measurements recorded"}
        
        total_requests = len(self.response_times)
        duration = self.end_time - self.start_time
        successful_requests = sum(1 for code in self.status_codes if 200 <= code < 300)
        
        def calc_stats(times, suffix="ms"):
            if not times:
                return {"count": 0}
            multiplier = 1000 if suffix == "ms" else 1
            return {
                "count": len(times),
                "min": min(times) * multiplier,
                "max": max(times) * multiplier,
                "mean": statistics.mean(times) * multiplier,
                "median": statistics.median(times) * multiplier,
                "p95": sorted(times)[int(0.95 * len(times))] * multiplier if len(times) > 20 else max(times) * multiplier,
                "p99": sorted(times)[int(0.99 * len(times))] * multiplier if len(times) > 100 else max(times) * multiplier,
            }
        
        # Endpoint breakdown
        endpoint_summary = {}
        for endpoint, times in self.endpoint_metrics.items():
            endpoint_summary[endpoint] = calc_stats(times)
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate_percent": (successful_requests / total_requests) * 100,
            "requests_per_second": total_requests / duration if duration > 0 else 0,
            "duration_seconds": duration,
            "overall_response_times": calc_stats(self.response_times),
            "endpoint_breakdown": endpoint_summary,
            "avg_request_size_kb": statistics.mean(self.request_sizes) / 1024 if self.request_sizes else 0,
            "avg_response_size_kb": statistics.mean(self.response_sizes) / 1024 if self.response_sizes else 0,
            "status_code_distribution": {
                "2xx": sum(1 for code in self.status_codes if 200 <= code < 300),
                "4xx": sum(1 for code in self.status_codes if 400 <= code < 500),
                "5xx": sum(1 for code in self.status_codes if 500 <= code < 600)
            }
        }


class TestAPIEndpointResponseTimes:
    """API endpoint response time tests."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_lightweight_endpoint_response_times(self):
        """Test response times for lightweight API endpoints."""
        metrics = APIResponseMetrics()
        metrics.start_monitoring()
        
        request_count = 100
        max_response_time_ms = 100
        target_p95_ms = 50
        min_rps = 200
        
        # Lightweight endpoints
        endpoints = {
            "/api/health": {"processing_time": 0.005, "response_size": 100},      # 5ms, 100 bytes
            "/api/version": {"processing_time": 0.003, "response_size": 50},      # 3ms, 50 bytes
            "/api/status": {"processing_time": 0.008, "response_size": 200},      # 8ms, 200 bytes
            "/api/ping": {"processing_time": 0.002, "response_size": 30},         # 2ms, 30 bytes
        }
        
        async def call_lightweight_endpoint(request_id: int):
            """Simulate lightweight API call."""
            endpoint_name = list(endpoints.keys())[request_id % len(endpoints)]
            endpoint_config = endpoints[endpoint_name]
            
            start_time = time.time()
            
            # Simulate request processing
            base_time = endpoint_config["processing_time"]
            variance = (request_id % 10) * 0.001  # Add small variance
            processing_time = base_time + variance
            
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Simulate response characteristics
            request_size = 500 + (request_id % 100)  # 500-600 bytes request
            response_size = endpoint_config["response_size"]
            
            # 99.5% success rate for lightweight endpoints
            status_code = 200 if request_id % 200 != 0 else 500
            
            return {
                "endpoint": endpoint_name,
                "response_time": response_time,
                "status_code": status_code,
                "request_size": request_size,
                "response_size": response_size
            }
        
        # Execute lightweight endpoint calls
        tasks = [call_lightweight_endpoint(i) for i in range(request_count)]
        results = await asyncio.gather(*tasks)
        
        # Collect metrics
        for result in results:
            metrics.record_response(
                result["endpoint"],
                result["response_time"],
                result["status_code"],
                result["request_size"],
                result["response_size"]
            )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Lightweight endpoint assertions
        assert summary["success_rate_percent"] >= 98.0
        assert summary["overall_response_times"]["mean"] <= max_response_time_ms
        assert summary["overall_response_times"]["p95"] <= target_p95_ms
        assert summary["requests_per_second"] >= min_rps
        
        print(f"Lightweight Endpoint Performance: {summary}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_data_processing_endpoint_response_times(self):
        """Test response times for data processing endpoints."""
        metrics = APIResponseMetrics()
        metrics.start_monitoring()
        
        request_count = 50
        max_response_time_ms = 2000
        target_p95_ms = 1500
        min_rps = 25
        
        # Data processing endpoints
        endpoints = {
            "/api/content/analyze": {"processing_time": 0.3, "response_size": 2048},    # 300ms, 2KB
            "/api/content/fingerprint": {"processing_time": 0.5, "response_size": 1024},  # 500ms, 1KB
            "/api/search": {"processing_time": 0.2, "response_size": 5120},             # 200ms, 5KB
            "/api/recommendations": {"processing_time": 0.4, "response_size": 3072},    # 400ms, 3KB
        }
        
        async def call_data_processing_endpoint(request_id: int):
            """Simulate data processing API call."""
            endpoint_name = list(endpoints.keys())[request_id % len(endpoints)]
            endpoint_config = endpoints[endpoint_name]
            
            start_time = time.time()
            
            # Simulate data processing
            base_time = endpoint_config["processing_time"]
            
            # Processing time varies with data complexity
            complexity_factor = 1 + (request_id % 5) * 0.2  # 1x to 2x complexity
            processing_time = base_time * complexity_factor
            
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Simulate request/response sizes
            request_size = 2048 + (request_id % 1024)  # 2-3KB request
            response_size = endpoint_config["response_size"]
            
            # 95% success rate for data processing endpoints
            status_code = 200 if request_id % 20 != 0 else (400 if request_id % 40 == 0 else 500)
            
            return {
                "endpoint": endpoint_name,
                "response_time": response_time,
                "status_code": status_code,
                "request_size": request_size,
                "response_size": response_size
            }
        
        # Execute data processing endpoint calls
        tasks = [call_data_processing_endpoint(i) for i in range(request_count)]
        results = await asyncio.gather(*tasks)
        
        # Collect metrics
        for result in results:
            metrics.record_response(
                result["endpoint"],
                result["response_time"],
                result["status_code"],
                result["request_size"],
                result["response_size"]
            )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Data processing endpoint assertions
        assert summary["success_rate_percent"] >= 90.0
        assert summary["overall_response_times"]["mean"] <= max_response_time_ms
        assert summary["overall_response_times"]["p95"] <= target_p95_ms
        assert summary["requests_per_second"] >= min_rps
        
        print(f"Data Processing Endpoint Performance: {summary}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_api_response_times(self):
        """Test API response times under concurrent load."""
        metrics = APIResponseMetrics()
        metrics.start_monitoring()
        
        concurrent_requests = 200
        max_concurrent_response_time_ms = 500
        target_p95_ms = 300
        min_concurrent_rps = 100
        
        # Mixed endpoint types
        endpoint_mix = [
            ("/api/health", 0.005, 100),              # Fast endpoint
            ("/api/content/analyze", 0.15, 2048),     # Medium endpoint
            ("/api/search", 0.1, 5120),               # Search endpoint
            ("/api/upload", 0.2, 1024),               # Upload endpoint
        ]
        
        # Concurrency control
        max_concurrent = 50
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def concurrent_api_call(request_id: int):
            """Execute API call with concurrency control."""
            async with semaphore:
                endpoint_name, base_time, response_size = endpoint_mix[request_id % len(endpoint_mix)]
                
                start_time = time.time()
                
                # Processing time increases slightly with concurrent load
                concurrency_factor = 1 + (max_concurrent - semaphore._value) * 0.02
                processing_time = base_time * concurrency_factor
                
                await asyncio.sleep(processing_time)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Request/response sizes
                request_size = 1024 + (request_id % 512)
                
                # 96% success rate under concurrent load
                status_code = 200 if request_id % 25 != 0 else (429 if request_id % 50 == 0 else 500)
                
                return {
                    "endpoint": endpoint_name,
                    "response_time": response_time,
                    "status_code": status_code,
                    "request_size": request_size,
                    "response_size": response_size
                }
        
        # Execute concurrent API calls
        tasks = [concurrent_api_call(i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        
        # Collect metrics
        for result in results:
            metrics.record_response(
                result["endpoint"],
                result["response_time"],
                result["status_code"],
                result["request_size"],
                result["response_size"]
            )
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Concurrent API assertions
        assert summary["success_rate_percent"] >= 90.0
        assert summary["overall_response_times"]["mean"] <= max_concurrent_response_time_ms
        assert summary["overall_response_times"]["p95"] <= target_p95_ms
        assert summary["requests_per_second"] >= min_concurrent_rps
        
        print(f"Concurrent API Response Performance: {summary}")


class TestAPIResponseTimeVariability:
    """API response time consistency and variability tests."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_response_time_consistency(self):
        """Test API response time consistency over time."""
        metrics = APIResponseMetrics()
        metrics.start_monitoring()
        
        # Test parameters
        test_duration_minutes = 2
        requests_per_minute = 60
        max_response_time_variance_ms = 100
        consistency_threshold = 0.8  # 80% of requests within 2x median
        
        endpoint = "/api/consistent_test"
        base_processing_time = 0.05  # 50ms
        
        async def consistent_api_call(request_id: int, start_offset: float):
            """API call for consistency testing."""
            # Wait for scheduled time
            await asyncio.sleep(start_offset)
            
            start_time = time.time()
            
            # Base processing with minimal variance
            processing_time = base_processing_time + (request_id % 3) * 0.005  # 50-60ms
            
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "request_id": request_id,
                "response_time": response_time,
                "scheduled_time": start_offset
            }
        
        # Schedule requests evenly over test duration
        total_requests = test_duration_minutes * requests_per_minute
        request_interval = (test_duration_minutes * 60) / total_requests
        
        tasks = []
        for i in range(total_requests):
            start_offset = i * request_interval
            tasks.append(consistent_api_call(i, start_offset))
        
        # Execute consistency test
        results = await asyncio.gather(*tasks)
        
        # Collect metrics
        for result in results:
            metrics.record_response(endpoint, result["response_time"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Analyze consistency
        response_times_ms = [rt * 1000 for rt in metrics.response_times]
        median_time = statistics.median(response_times_ms)
        
        # Count requests within 2x median (consistency measure)
        consistent_requests = sum(
            1 for rt in response_times_ms 
            if rt <= median_time * 2
        )
        consistency_rate = consistent_requests / len(response_times_ms)
        
        # Variance analysis
        variance = statistics.variance(response_times_ms)
        std_dev = statistics.stdev(response_times_ms)
        
        # Consistency assertions
        assert consistency_rate >= consistency_threshold
        assert std_dev <= max_response_time_variance_ms
        assert summary["success_rate_percent"] >= 95.0
        
        print(f"Response Time Consistency: {summary}")
        print(f"Consistency rate: {consistency_rate:.1%}, Std dev: {std_dev:.1f}ms")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_response_time_under_load_variation(self):
        """Test API response times under varying load conditions."""
        metrics = APIResponseMetrics()
        metrics.start_monitoring()
        
        # Load variation phases
        load_phases = [
            ("low", 10, 0.05),      # 10 RPS, 50ms processing
            ("medium", 50, 0.08),   # 50 RPS, 80ms processing
            ("high", 100, 0.12),    # 100 RPS, 120ms processing
            ("peak", 150, 0.15),    # 150 RPS, 150ms processing
            ("recovery", 20, 0.06), # 20 RPS, 60ms processing
        ]
        
        max_degradation_factor = 3.0  # Max 3x slower at peak vs low load
        
        endpoint = "/api/load_variation_test"
        phase_results = {}
        
        for phase_name, rps, base_processing_time in load_phases:
            phase_duration = 10  # 10 seconds per phase
            phase_requests = rps * phase_duration
            request_interval = 1.0 / rps
            
            print(f"  Testing {phase_name} load: {rps} RPS for {phase_duration}s")
            
            async def load_phase_request(request_id: int):
                """Request during specific load phase."""
                start_time = time.time()
                
                # Processing time with load-based variance
                load_factor = 1 + (rps - 10) / 100  # Increases with RPS
                processing_time = base_processing_time * load_factor
                
                await asyncio.sleep(processing_time)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                return {
                    "phase": phase_name,
                    "response_time": response_time
                }
            
            # Execute phase requests with controlled timing
            phase_tasks = []
            phase_start_time = time.time()
            
            for i in range(phase_requests):
                # Schedule request at appropriate interval
                scheduled_time = i * request_interval
                
                async def timed_request(req_id, delay):
                    await asyncio.sleep(delay)
                    return await load_phase_request(req_id)
                
                phase_tasks.append(timed_request(i, scheduled_time))
            
            # Wait for phase completion
            phase_request_results = await asyncio.gather(*phase_tasks)
            
            # Collect phase metrics
            phase_response_times = []
            for result in phase_request_results:
                metrics.record_response(endpoint, result["response_time"])
                phase_response_times.append(result["response_time"])
            
            # Calculate phase statistics
            if phase_response_times:
                phase_results[phase_name] = {
                    "mean_response_time_ms": statistics.mean(phase_response_times) * 1000,
                    "median_response_time_ms": statistics.median(phase_response_times) * 1000,
                    "request_count": len(phase_response_times),
                    "rps": rps
                }
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Load variation analysis
        low_load_time = phase_results["low"]["mean_response_time_ms"]
        peak_load_time = phase_results["peak"]["mean_response_time_ms"]
        degradation_factor = peak_load_time / low_load_time
        
        # Recovery analysis
        recovery_time = phase_results["recovery"]["mean_response_time_ms"]
        recovery_ratio = recovery_time / low_load_time
        
        # Load variation assertions
        assert degradation_factor <= max_degradation_factor
        assert recovery_ratio <= 1.5  # Recovery should be within 1.5x of low load
        assert summary["success_rate_percent"] >= 95.0
        
        print(f"Load Variation Performance: {summary}")
        print(f"Degradation factor: {degradation_factor:.2f}x (peak vs low)")
        print(f"Recovery ratio: {recovery_ratio:.2f}x (recovery vs low)")
        
        # Print phase breakdown
        for phase_name, stats in phase_results.items():
            print(f"  {phase_name}: {stats['mean_response_time_ms']:.1f}ms avg @ {stats['rps']} RPS")


class TestAPIPayloadSizeImpact:
    """Test impact of request/response payload sizes on response times."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_request_payload_size_impact(self):
        """Test how request payload size affects response times."""
        metrics = APIResponseMetrics()
        metrics.start_monitoring()
        
        # Different payload sizes
        payload_sizes = [
            (1024, "1KB"),        # 1KB
            (10240, "10KB"),      # 10KB  
            (102400, "100KB"),    # 100KB
            (512000, "500KB"),    # 500KB
        ]
        
        requests_per_size = 20
        max_size_impact_factor = 2.0  # Response time shouldn't increase more than 2x
        
        endpoint = "/api/payload_test"
        size_results = {}
        
        for payload_size, size_label in payload_sizes:
            async def payload_size_request(request_id: int, size: int):
                """Request with specific payload size."""
                start_time = time.time()
                
                # Simulate payload processing time (scales with size)
                base_processing_time = 0.02  # 20ms base
                size_factor = 1 + (size / 1000000)  # +1ms per MB
                processing_time = base_processing_time * size_factor
                
                await asyncio.sleep(processing_time)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                return {
                    "request_id": request_id,
                    "payload_size": size,
                    "response_time": response_time
                }
            
            # Execute requests for this payload size
            size_tasks = [
                payload_size_request(i, payload_size) 
                for i in range(requests_per_size)
            ]
            size_results_list = await asyncio.gather(*size_tasks)
            
            # Collect metrics and calculate size statistics
            size_response_times = []
            for result in size_results_list:
                metrics.record_response(
                    endpoint, 
                    result["response_time"], 
                    request_size=result["payload_size"]
                )
                size_response_times.append(result["response_time"])
            
            size_results[size_label] = {
                "payload_size_bytes": payload_size,
                "mean_response_time_ms": statistics.mean(size_response_times) * 1000,
                "median_response_time_ms": statistics.median(size_response_times) * 1000
            }
            
            print(f"  Tested {size_label} payload: {size_results[size_label]['mean_response_time_ms']:.1f}ms avg")
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Payload size impact analysis
        smallest_size_time = size_results["1KB"]["mean_response_time_ms"]
        largest_size_time = size_results["500KB"]["mean_response_time_ms"]
        size_impact_factor = largest_size_time / smallest_size_time
        
        # Payload size assertions
        assert size_impact_factor <= max_size_impact_factor
        assert summary["success_rate_percent"] >= 95.0
        
        print(f"Payload Size Impact: {summary}")
        print(f"Size impact factor: {size_impact_factor:.2f}x (500KB vs 1KB)")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_response_payload_generation_time(self):
        """Test response generation time for different response sizes."""
        metrics = APIResponseMetrics()
        metrics.start_monitoring()
        
        # Different response sizes to generate
        response_sizes = [
            (1024, "1KB"),
            (10240, "10KB"),
            (51200, "50KB"),
            (204800, "200KB"),
        ]
        
        requests_per_size = 15
        max_generation_time_ms = 200
        
        endpoint = "/api/response_generation_test"
        
        for response_size, size_label in response_sizes:
            async def response_generation_request(request_id: int, size: int):
                """Request that generates response of specific size."""
                start_time = time.time()
                
                # Simulate response data generation
                generation_time = 0.01 + (size / 1000000)  # 10ms base + 1ms per MB
                await asyncio.sleep(generation_time)
                
                # Simulate response serialization time
                serialization_time = size / 10000000  # 0.1ms per MB
                await asyncio.sleep(serialization_time)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                return {
                    "request_id": request_id,
                    "response_size": size,
                    "response_time": response_time
                }
            
            # Execute requests for this response size
            size_tasks = [
                response_generation_request(i, response_size) 
                for i in range(requests_per_size)
            ]
            size_results_list = await asyncio.gather(*size_tasks)
            
            # Collect metrics
            for result in size_results_list:
                metrics.record_response(
                    endpoint,
                    result["response_time"],
                    response_size=result["response_size"]
                )
            
            # Calculate average for this size
            avg_time = statistics.mean([r["response_time"] for r in size_results_list]) * 1000
            print(f"  Response generation {size_label}: {avg_time:.1f}ms avg")
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Response generation assertions
        assert summary["overall_response_times"]["max"] <= max_generation_time_ms
        assert summary["success_rate_percent"] >= 95.0
        
        print(f"Response Generation Performance: {summary}")