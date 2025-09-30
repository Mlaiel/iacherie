#!/usr/bin/env python3
"""
⚡ LOAD TEST TEMPLATE - PERFORMANCE AND SCALABILITY TESTING
==========================================================

High-performance load testing with concurrent users simulation,
throughput measurement, and scalability analysis.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    target_url: str
    concurrent_users: int = 100
    duration_seconds: int = 60
    requests_per_second: int = 1000
    timeout: int = 30

@dataclass
class LoadTestResults:
    """Load test results"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0

class LoadTestTemplate:
    """
    🚀 ENTERPRISE LOAD TEST TEMPLATE
    
    Comprehensive load testing with performance metrics and analysis.
    """
    
    def __init__(self, config: LoadTestConfig):
        """Initialize load test template"""
        self.config = config
        self.response_times: List[float] = []
        self.results = LoadTestResults()
    
    async def run_load_test(self) -> LoadTestResults:
        """Execute load test"""
        start_time = time.time()
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.config.concurrent_users)
        
        tasks = []
        for _ in range(self.config.requests_per_second * self.config.duration_seconds):
            task = asyncio.create_task(self._make_request(semaphore))
            tasks.append(task)
        
        # Execute all requests
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate results
        total_time = time.time() - start_time
        self._calculate_results(total_time)
        
        return self.results
    
    async def _make_request(self, semaphore: asyncio.Semaphore):
        """Make individual HTTP request"""
        async with semaphore:
            start = time.time()
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.config.target_url,
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                    ) as response:
                        response_time = (time.time() - start) * 1000
                        self.response_times.append(response_time)
                        
                        if response.status < 400:
                            self.results.successful_requests += 1
                        else:
                            self.results.failed_requests += 1
                            
            except Exception:
                self.results.failed_requests += 1
            
            self.results.total_requests += 1
    
    def _calculate_results(self, total_time: float):
        """Calculate test results and statistics"""
        if self.response_times:
            self.results.avg_response_time_ms = statistics.mean(self.response_times)
            self.results.min_response_time_ms = min(self.response_times)
            self.results.max_response_time_ms = max(self.response_times)
        
        if total_time > 0:
            self.results.requests_per_second = self.results.total_requests / total_time
        
        if self.results.total_requests > 0:
            self.results.error_rate = (self.results.failed_requests / self.results.total_requests) * 100
    
    def generate_report(self) -> str:
        """Generate load test report"""
        return f"""
=== LOAD TEST REPORT ===
Target URL: {self.config.target_url}
Concurrent Users: {self.config.concurrent_users}
Duration: {self.config.duration_seconds}s

RESULTS:
Total Requests: {self.results.total_requests}
Successful: {self.results.successful_requests}
Failed: {self.results.failed_requests}
Error Rate: {self.results.error_rate:.2f}%

PERFORMANCE:
Requests/Second: {self.results.requests_per_second:.2f}
Avg Response Time: {self.results.avg_response_time_ms:.2f}ms
Min Response Time: {self.results.min_response_time_ms:.2f}ms
Max Response Time: {self.results.max_response_time_ms:.2f}ms
"""

# Factory function
def create_load_test_template(**kwargs) -> LoadTestTemplate:
    """Create load test template"""
    config = LoadTestConfig(**kwargs)
    return LoadTestTemplate(config)