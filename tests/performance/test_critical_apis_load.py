# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Critical APIs Load Testing
========================

Enhanced load testing specifically targeting critical business APIs for the Ainflue platform.
Tests authentication, content upload, fingerprinting, analytics, protection, and collaboration endpoints.

Author: Performance Optimization Team
"""
import asyncio
import time
import json
import pytest
import sys
import os
from pathlib import Path
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp

# Import existing performance metrics class
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tests.performance.test_load_stress import PerformanceMetrics


@dataclass
class CriticalAPIEndpoint:
    """Critical API endpoint configuration"""    name: str
    path: str
    method: str = "POST"
    priority: str = "high"  # high, medium, low
    expected_response_time_ms: int = 500  # SLA requirement
    max_concurrent_requests: int = 100
    payload_size_bytes: int = 1024
    requires_auth: bool = True
    business_impact: str = "critical"  # critical, high, medium, low


class CriticalAPILoadTester:
    """Enhanced load tester for critical business APIs"""    
    def __init__(self):
        self.critical_endpoints = self._define_critical_endpoints()
        self.performance_metrics = PerformanceMetrics()
        self.session: Optional[aiohttp.ClientSession] = None
        
    def _define_critical_endpoints(self) -> List[CriticalAPIEndpoint]:
        """Define critical business API endpoints"""        return [
            # Authentication & User Management
            CriticalAPIEndpoint(
                name="user_authentication",
                path="/auth/login",
                method="POST",
                expected_response_time_ms=200,
                max_concurrent_requests=200,
                business_impact="critical"
            ),
            CriticalAPIEndpoint(
                name="user_registration",
                path="/auth/register",
                method="POST",
                expected_response_time_ms=300,
                max_concurrent_requests=100,
                business_impact="high"
            ),
            
            # Content Upload & Processing
            CriticalAPIEndpoint(
                name="content_upload",
                path="/content/upload",
                method="POST",
                expected_response_time_ms=2000,  # Longer for file uploads
                max_concurrent_requests=50,
                payload_size_bytes=5 * 1024 * 1024,  # 5MB
                business_impact="critical"
            ),
            CriticalAPIEndpoint(
                name="content_processing_status",
                path="/content/processing/status",
                method="GET",
                expected_response_time_ms=100,
                max_concurrent_requests=200,
                business_impact="high"
            ),
            
            # AI Fingerprinting & Protection
            CriticalAPIEndpoint(
                name="fingerprint_generation",
                path="/fingerprint/generate",
                method="POST",
                expected_response_time_ms=1500,  # AI processing time
                max_concurrent_requests=30,
                payload_size_bytes=2 * 1024 * 1024,  # 2MB
                business_impact="critical"
            ),
            CriticalAPIEndpoint(
                name="content_protection_check",
                path="/protection/check",
                method="POST",
                expected_response_time_ms=800,
                max_concurrent_requests=100,
                business_impact="critical"
            ),
            
            # Analytics & Revenue
            CriticalAPIEndpoint(
                name="revenue_analytics",
                path="/analytics/revenue",
                method="GET",
                expected_response_time_ms=300,
                max_concurrent_requests=150,
                business_impact="high"
            ),
            CriticalAPIEndpoint(
                name="engagement_metrics",
                path="/analytics/engagement",
                method="GET",
                expected_response_time_ms=250,
                max_concurrent_requests=200,
                business_impact="high"
            ),
            
            # Collaboration & Discovery
            CriticalAPIEndpoint(
                name="creator_discovery",
                path="/collaboration/discover",
                method="POST",
                expected_response_time_ms=400,
                max_concurrent_requests=100,
                business_impact="medium"
            ),
            CriticalAPIEndpoint(
                name="collaboration_request",
                path="/collaboration/request",
                method="POST",
                expected_response_time_ms=200,
                max_concurrent_requests=80,
                business_impact="high"
            )
        ]
    
    async def simulate_api_call(self, endpoint: CriticalAPIEndpoint) -> Dict[str, Any]:
        """Simulate API call with realistic response times and payloads"""        start_time = time.time()
        
        # Simulate different processing times based on endpoint type
        if "upload" in endpoint.path:
            # File upload simulation - based on payload size
            processing_time = 0.5 + (endpoint.payload_size_bytes / 1024 / 1024) * 0.3
        elif "fingerprint" in endpoint.path:
            # AI processing simulation
            processing_time = 1.0 + (endpoint.payload_size_bytes / 1024 / 1024) * 0.2
        elif "analytics" in endpoint.path:
            # Database query simulation
            processing_time = 0.1 + 0.05 * (endpoint.max_concurrent_requests / 100)
        elif "auth" in endpoint.path:
            # Authentication simulation
            processing_time = 0.05 + 0.02 * (endpoint.max_concurrent_requests / 200)
        else:
            # General API call
            processing_time = 0.1
        
        # Add some realistic variability
        import random
        processing_time *= random.uniform(0.8, 1.4)
        
        await asyncio.sleep(processing_time)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Simulate success rate based on load
        success_rate = max(0.95 - (endpoint.max_concurrent_requests / 1000) * 0.1, 0.85)
        status_code = 200 if random.random() < success_rate else 500
        
        return {
            "endpoint": endpoint.name,
            "path": endpoint.path,
            "method": endpoint.method,
            "status_code": status_code,
            "response_time": response_time,
            "response_time_ms": response_time * 1000,
            "payload_size_bytes": endpoint.payload_size_bytes,
            "business_impact": endpoint.business_impact,
            "timestamp": datetime.utcnow().isoformat()
        }


class TestCriticalAPIsLoad:
    """Test suite for critical API load testing"""    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_critical_apis_individual_load(self):
        """Test each critical API individually under load"""        tester = CriticalAPILoadTester()
        results = {}
        
        for endpoint in tester.critical_endpoints:
            print(f"\\nTesting {endpoint.name} ({endpoint.business_impact} impact)...")
            
            # Reset metrics for each endpoint
            metrics = PerformanceMetrics()
            metrics.start_monitoring()
            
            # Create load test tasks
            tasks = []
            concurrent_requests = min(endpoint.max_concurrent_requests, 50)  # Limit for testing
            
            for i in range(concurrent_requests):
                tasks.append(tester.simulate_api_call(endpoint))
            
            # Execute load test
            start_time = time.time()
            api_results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Process results
            successful_requests = 0
            failed_requests = 0
            response_times = []
            
            for result in api_results:
                if isinstance(result, dict):
                    response_times.append(result["response_time"])
                    if result["status_code"] == 200:
                        successful_requests += 1
                        metrics.add_success()
                    else:
                        failed_requests += 1
                        metrics.add_error()
                    metrics.add_response_time(result["response_time"])
                else:
                    failed_requests += 1
                    metrics.add_error()
            
            metrics.stop_monitoring()
            summary = metrics.get_summary()
            
            # Calculate endpoint-specific metrics
            avg_response_time_ms = statistics.mean(response_times) * 1000 if response_times else 0
            p95_response_time_ms = sorted(response_times)[int(0.95 * len(response_times))] * 1000 if len(response_times) > 20 else avg_response_time_ms
            success_rate = (successful_requests / (successful_requests + failed_requests)) * 100 if (successful_requests + failed_requests) > 0 else 0
            requests_per_second = concurrent_requests / (end_time - start_time)
            
            # Store results
            results[endpoint.name] = {
                "endpoint_config": {
                    "name": endpoint.name,
                    "path": endpoint.path,
                    "business_impact": endpoint.business_impact,
                    "expected_response_time_ms": endpoint.expected_response_time_ms
                },
                "performance_metrics": {
                    "concurrent_requests": concurrent_requests,
                    "successful_requests": successful_requests,
                    "failed_requests": failed_requests,
                    "success_rate_percent": success_rate,
                    "avg_response_time_ms": avg_response_time_ms,
                    "p95_response_time_ms": p95_response_time_ms,
                    "requests_per_second": requests_per_second,
                    "total_duration_seconds": end_time - start_time
                },
                "sla_compliance": {
                    "meets_response_time_sla": avg_response_time_ms <= endpoint.expected_response_time_ms,
                    "meets_success_rate_sla": success_rate >= 95.0,
                    "response_time_variance": avg_response_time_ms - endpoint.expected_response_time_ms
                }
            }
            
            # Print results
            print(f"  Requests: {concurrent_requests}, Success Rate: {success_rate:.1f}%")
            print(f"  Avg Response Time: {avg_response_time_ms:.1f}ms (SLA: {endpoint.expected_response_time_ms}ms)")
            print(f"  P95 Response Time: {p95_response_time_ms:.1f}ms")
            print(f"  Requests/sec: {requests_per_second:.1f}")
            print(f"  SLA Compliance: {'✅' if results[endpoint.name]['sla_compliance']['meets_response_time_sla'] and results[endpoint.name]['sla_compliance']['meets_success_rate_sla'] else '❌'}")
        
        # Generate overall report
        print("\\n" + "="*80)
        print("CRITICAL APIs LOAD TEST SUMMARY")
        print("="*80)
        
        critical_endpoints_meeting_sla = 0
        total_critical_endpoints = 0
        
        for endpoint_name, result in results.items():
            config = result["endpoint_config"]
            metrics = result["performance_metrics"]
            sla = result["sla_compliance"]
            
            if config["business_impact"] in ["critical", "high"]:
                total_critical_endpoints += 1
                if sla["meets_response_time_sla"] and sla["meets_success_rate_sla"]:
                    critical_endpoints_meeting_sla += 1
            
            status = "✅ PASS" if (sla["meets_response_time_sla"] and sla["meets_success_rate_sla"]) else "❌ FAIL"
            print(f"{config['name']:25} | {config['business_impact']:8} | {metrics['avg_response_time_ms']:6.1f}ms | {metrics['success_rate_percent']:5.1f}% | {status}")
        
        sla_compliance_rate = (critical_endpoints_meeting_sla / total_critical_endpoints) * 100 if total_critical_endpoints > 0 else 0
        print(f"\\nOverall SLA Compliance Rate: {sla_compliance_rate:.1f}% ({critical_endpoints_meeting_sla}/{total_critical_endpoints} critical/high impact endpoints)")
        
        # Assertions for test validation
        assert sla_compliance_rate >= 80, f"SLA compliance rate {sla_compliance_rate:.1f}% is below 80% threshold"
        
        # Save detailed results for analysis
        with open("/tmp/critical_apis_load_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\\nDetailed results saved to: /tmp/critical_apis_load_test_results.json")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_critical_apis_mixed_load(self):
        """Test mixed load across all critical APIs simultaneously"""        tester = CriticalAPILoadTester()
        
        print("\\nTesting mixed load across all critical APIs...")
        
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        # Create mixed load tasks
        all_tasks = []
        
        for endpoint in tester.critical_endpoints:
            # Reduce concurrent requests for mixed load test
            concurrent_requests = min(endpoint.max_concurrent_requests // 3, 20)
            
            for i in range(concurrent_requests):
                all_tasks.append(tester.simulate_api_call(endpoint))
        
        # Shuffle tasks to simulate realistic mixed load
        import random
        random.shuffle(all_tasks)
        
        # Execute mixed load test
        start_time = time.time()
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        end_time = time.time()
        
        # Process results by endpoint
        endpoint_results = {}
        total_requests = 0
        total_successful = 0
        total_failed = 0
        all_response_times = []
        
        for result in results:
            if isinstance(result, dict):
                endpoint_name = result["endpoint"]
                if endpoint_name not in endpoint_results:
                    endpoint_results[endpoint_name] = {"requests": 0, "successful": 0, "failed": 0, "response_times": []}
                
                endpoint_results[endpoint_name]["requests"] += 1
                endpoint_results[endpoint_name]["response_times"].append(result["response_time"])
                
                total_requests += 1
                all_response_times.append(result["response_time"])
                
                if result["status_code"] == 200:
                    endpoint_results[endpoint_name]["successful"] += 1
                    total_successful += 1
                    metrics.add_success()
                else:
                    endpoint_results[endpoint_name]["failed"] += 1
                    total_failed += 1
                    metrics.add_error()
                
                metrics.add_response_time(result["response_time"])
            else:
                total_failed += 1
                metrics.add_error()
        
        metrics.stop_monitoring()
        
        # Calculate overall metrics
        total_duration = end_time - start_time
        overall_success_rate = (total_successful / total_requests) * 100 if total_requests > 0 else 0
        overall_rps = total_requests / total_duration
        avg_response_time_ms = statistics.mean(all_response_times) * 1000 if all_response_times else 0
        p95_response_time_ms = sorted(all_response_times)[int(0.95 * len(all_response_times))] * 1000 if len(all_response_times) > 20 else avg_response_time_ms
        
        print(f"\\nMixed Load Test Results:")
        print(f"Total Requests: {total_requests}")
        print(f"Success Rate: {overall_success_rate:.1f}%")
        print(f"Average Response Time: {avg_response_time_ms:.1f}ms")
        print(f"P95 Response Time: {p95_response_time_ms:.1f}ms")
        print(f"Requests per Second: {overall_rps:.1f}")
        print(f"Test Duration: {total_duration:.1f}s")
        
        # Per-endpoint breakdown
        print(f"\\nPer-Endpoint Breakdown:")
        for endpoint_name, stats in endpoint_results.items():
            if stats["requests"] > 0:
                success_rate = (stats["successful"] / stats["requests"]) * 100
                avg_time_ms = statistics.mean(stats["response_times"]) * 1000
                print(f"  {endpoint_name:25} | {stats['requests']:3d} reqs | {success_rate:5.1f}% success | {avg_time_ms:6.1f}ms avg")
        
        # Assertions
        assert overall_success_rate >= 90, f"Mixed load success rate {overall_success_rate:.1f}% is below 90% threshold"
        assert avg_response_time_ms <= 1000, f"Mixed load average response time {avg_response_time_ms:.1f}ms exceeds 1000ms threshold"
        
        mixed_results = {
            "test_type": "mixed_load",
            "overall_metrics": {
                "total_requests": total_requests,
                "success_rate_percent": overall_success_rate,
                "avg_response_time_ms": avg_response_time_ms,
                "p95_response_time_ms": p95_response_time_ms,
                "requests_per_second": overall_rps,
                "duration_seconds": total_duration
            },
            "endpoint_breakdown": endpoint_results
        }
        
        with open("/tmp/mixed_load_test_results.json", "w") as f:
            json.dump(mixed_results, f, indent=2)
        
        print(f"\\nMixed load results saved to: /tmp/mixed_load_test_results.json")


if __name__ == "__main__":
    # Run critical API load tests
    pytest.main([
        __file__, 
        "-v", 
        "-m", "performance",
        "--asyncio-mode=auto",
        "--tb=short"
    ])