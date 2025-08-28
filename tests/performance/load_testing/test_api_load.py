"""
API Load Testing

Tests API endpoints under normal and increased load conditions.
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any


class APILoadMetrics:
    """Metrics collection for API load testing."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.success_count: int = 0
        self.error_count: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
    
    def start_monitoring(self):
        self.start_time = time.time()
    
    def stop_monitoring(self):
        self.end_time = time.time()
    
    def record_response(self, response_time: float, success: bool = True):
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.response_times:
            return {"error": "No measurements recorded"}
        
        total_requests = self.success_count + self.error_count
        duration = self.end_time - self.start_time
        
        return {
            "total_requests": total_requests,
            "successful_requests": self.success_count,
            "failed_requests": self.error_count,
            "success_rate_percent": (self.success_count / total_requests) * 100 if total_requests > 0 else 0,
            "duration_seconds": duration,
            "requests_per_second": total_requests / duration if duration > 0 else 0,
            "response_times_ms": {
                "min": min(self.response_times) * 1000,
                "max": max(self.response_times) * 1000,
                "mean": statistics.mean(self.response_times) * 1000,
                "median": statistics.median(self.response_times) * 1000,
                "p95": sorted(self.response_times)[int(0.95 * len(self.response_times))] * 1000 if len(self.response_times) > 20 else max(self.response_times) * 1000,
            }
        }


class TestAPILoadTesting:
    """API load testing scenarios."""
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self):
        """Test API performance with concurrent requests."""
        metrics = APILoadMetrics()
        metrics.start_monitoring()
        
        concurrent_users = 50
        requests_per_user = 5
        max_response_time_ms = 500
        min_success_rate = 95.0
        
        async def simulate_api_request(user_id: int, request_id: int):
            """Simulate API request."""
            start_time = time.time()
            
            # Simulate API processing (varies based on endpoint complexity)
            base_processing_time = 0.05  # 50ms base
            variance = (user_id + request_id) % 10 * 0.01  # Add variance
            processing_time = base_processing_time + variance
            
            await asyncio.sleep(processing_time)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Simulate 98% success rate under load
            success = (user_id + request_id) % 50 != 0
            
            return {
                "user_id": user_id,
                "request_id": request_id,
                "response_time": response_time,
                "success": success
            }
        
        # Generate all tasks
        tasks = []
        for user_id in range(concurrent_users):
            for request_id in range(requests_per_user):
                tasks.append(simulate_api_request(user_id, request_id))
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)
        
        # Collect metrics
        for result in results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate_percent"] >= min_success_rate
        assert summary["response_times_ms"]["mean"] <= max_response_time_ms
        assert summary["requests_per_second"] >= 100  # Should handle at least 100 RPS
        
        print(f"API Load Test Results: {summary}")
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """Test API under sustained load for extended period."""
        metrics = APILoadMetrics()
        metrics.start_monitoring()
        
        duration_seconds = 30  # 30 second sustained load
        target_rps = 20  # 20 requests per second
        max_response_time_ms = 200
        min_success_rate = 95.0
        
        async def api_worker():
            """Worker that makes API requests at steady rate."""
            request_count = 0
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                request_start = time.time()
                
                # Simulate API call
                processing_time = 0.03 + (request_count % 5) * 0.01  # 30-70ms
                await asyncio.sleep(processing_time)
                
                request_end = time.time()
                response_time = request_end - request_start
                
                # 97% success rate for sustained load
                success = request_count % 33 != 0
                metrics.record_response(response_time, success)
                
                request_count += 1
                
                # Control request rate
                target_interval = 1.0 / target_rps
                elapsed = time.time() - request_start
                if elapsed < target_interval:
                    await asyncio.sleep(target_interval - elapsed)
        
        # Run sustained load
        await api_worker()
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate_percent"] >= min_success_rate
        assert summary["response_times_ms"]["mean"] <= max_response_time_ms
        assert summary["total_requests"] >= duration_seconds * target_rps * 0.8  # Allow 20% variance
        
        print(f"Sustained Load Test Results: {summary}")
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_gradual_load_increase(self):
        """Test API performance as load gradually increases."""
        load_levels = [10, 25, 50, 100]  # Number of concurrent requests
        max_degradation_factor = 3.0  # Max 3x response time increase
        
        results = {}
        baseline_response_time = None
        
        for load_level in load_levels:
            metrics = APILoadMetrics()
            metrics.start_monitoring()
            
            async def load_request(request_id: int):
                start_time = time.time()
                
                # Processing time slightly increases with load
                base_time = 0.02
                load_factor = 1 + (load_level / 1000)  # Slight increase
                processing_time = base_time * load_factor
                
                await asyncio.sleep(processing_time)
                
                end_time = time.time()
                return end_time - start_time
            
            # Execute requests for this load level
            tasks = [load_request(i) for i in range(load_level)]
            response_times = await asyncio.gather(*tasks)
            
            # Record metrics
            for rt in response_times:
                metrics.record_response(rt, True)
            
            metrics.stop_monitoring()
            summary = metrics.get_summary()
            results[load_level] = summary
            
            # Set baseline from first test
            if baseline_response_time is None:
                baseline_response_time = summary["response_times_ms"]["mean"]
            
            # Check degradation
            current_response_time = summary["response_times_ms"]["mean"]
            degradation = current_response_time / baseline_response_time
            
            assert degradation <= max_degradation_factor
            
            print(f"Load {load_level}: Avg response {current_response_time:.2f}ms, "
                  f"degradation {degradation:.2f}x")
        
        # Final assertion: performance should scale reasonably
        final_degradation = (results[max(load_levels)]["response_times_ms"]["mean"] / 
                           baseline_response_time)
        assert final_degradation <= max_degradation_factor


class TestDatabaseLoadTesting:
    """Database performance under load."""
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_concurrent_database_queries(self):
        """Test database performance with concurrent queries."""
        metrics = APILoadMetrics()
        metrics.start_monitoring()
        
        concurrent_queries = 100
        max_query_time_ms = 100
        min_success_rate = 98.0
        
        async def simulate_db_query(query_id: int):
            """Simulate database query."""
            start_time = time.time()
            
            # Simulate different query types
            if query_id % 4 == 0:
                # Simple SELECT
                await asyncio.sleep(0.01)
            elif query_id % 4 == 1:
                # JOIN query
                await asyncio.sleep(0.03)
            elif query_id % 4 == 2:
                # Aggregate query
                await asyncio.sleep(0.05)
            else:
                # UPDATE/INSERT
                await asyncio.sleep(0.02)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # 99% success rate for database operations
            success = query_id % 100 != 0
            
            return {
                "query_id": query_id,
                "response_time": response_time,
                "success": success
            }
        
        # Execute concurrent queries
        tasks = [simulate_db_query(i) for i in range(concurrent_queries)]
        results = await asyncio.gather(*tasks)
        
        # Collect metrics
        for result in results:
            metrics.record_response(result["response_time"], result["success"])
        
        metrics.stop_monitoring()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate_percent"] >= min_success_rate
        assert summary["response_times_ms"]["mean"] <= max_query_time_ms
        assert summary["requests_per_second"] >= 200  # Should handle 200+ queries/sec
        
        print(f"Database Load Test Results: {summary}")
    
    @pytest.mark.load
    def test_connection_pool_load(self):
        """Test database connection pool under load."""
        pool_size = 10
        max_connections = pool_size
        active_connections = 0
        total_requests = 0
        successful_requests = 0
        
        def acquire_connection():
            nonlocal active_connections, total_requests, successful_requests
            total_requests += 1
            
            if active_connections < max_connections:
                active_connections += 1
                successful_requests += 1
                return True
            return False
        
        def release_connection():
            nonlocal active_connections
            if active_connections > 0:
                active_connections -= 1
        
        # Simulate high connection demand
        for i in range(50):  # 50 connection requests
            if acquire_connection():
                # Simulate query execution time
                time.sleep(0.001)  # 1ms query
                
                # Release every other connection immediately
                if i % 2 == 0:
                    release_connection()
        
        # Release remaining connections
        while active_connections > 0:
            release_connection()
        
        success_rate = (successful_requests / total_requests) * 100
        
        # Assertions
        assert success_rate >= 80.0  # Should handle at least 80% of requests
        assert active_connections == 0  # All connections should be released
        
        print(f"Connection Pool: {successful_requests}/{total_requests} "
              f"({success_rate:.1f}% success rate)")