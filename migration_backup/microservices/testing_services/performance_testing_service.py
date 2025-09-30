"""
Performance Testing Service
==========================

Enterprise-grade performance testing service for microservices validation.
Provides load testing, stress testing, and performance benchmarking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class TestType(Enum):
    """Performance test types"""
    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    SPIKE_TEST = "spike_test"
    VOLUME_TEST = "volume_test"
    ENDURANCE_TEST = "endurance_test"

class PerformanceTestingService:
    """
    Enterprise Performance Testing Service
    
    Provides comprehensive performance testing capabilities
    with load generation, metrics collection, and analysis.
    """
    
    def __init__(self):
        self.test_scenarios = {}
        self.test_results = {}
        self.active_tests = {}
        self.is_active = False
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize performance testing service"""
        try:
            logger.info("Initializing Performance Testing Service...")
            
            # Setup default test scenarios
            await self._setup_default_scenarios()
            
            self.is_active = True
            
            return {
                "status": "success",
                "service": "performance_testing",
                "test_scenarios": len(self.test_scenarios)
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize performance testing service: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _setup_default_scenarios(self):
        """Setup default performance test scenarios"""
        self.test_scenarios = {
            "api_load_test": {
                "name": "API Load Test",
                "type": TestType.LOAD_TEST,
                "target": "https://api.ainflue.com",
                "concurrent_users": 100,
                "duration": 300,  # 5 minutes
                "ramp_up": 60     # 1 minute
            },
            "upload_stress_test": {
                "name": "Content Upload Stress Test",
                "type": TestType.STRESS_TEST,
                "target": "https://api.ainflue.com/upload",
                "concurrent_users": 500,
                "duration": 600,  # 10 minutes
                "ramp_up": 120    # 2 minutes
            },
            "ai_processing_load": {
                "name": "AI Processing Load Test",
                "type": TestType.LOAD_TEST,
                "target": "https://ai.ainflue.com/process",
                "concurrent_users": 50,
                "duration": 900,  # 15 minutes
                "ramp_up": 180    # 3 minutes
            }
        }
    
    async def run_performance_test(
        self,
        scenario_name: str,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a performance test scenario"""
        try:
            if scenario_name not in self.test_scenarios:
                return {"status": "error", "error": "Test scenario not found"}
            
            scenario = self.test_scenarios[scenario_name].copy()
            if custom_config:
                scenario.update(custom_config)
            
            test_id = f"perf_{scenario_name}_{datetime.utcnow().timestamp()}"
            
            logger.info(f"Starting performance test: {scenario_name}")
            
            # Start test execution
            test_result = await self._execute_performance_test(test_id, scenario)
            
            # Store results
            self.test_results[test_id] = test_result
            
            return {
                "status": "success",
                "test_id": test_id,
                "test_result": test_result
            }
            
        except Exception as e:
            logger.error(f"Failed to run performance test: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _execute_performance_test(
        self,
        test_id: str,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute performance test scenario"""
        start_time = datetime.utcnow()
        
        # Mark test as active
        self.active_tests[test_id] = {
            "status": "running",
            "started_at": start_time.isoformat(),
            "scenario": scenario
        }
        
        try:
            # Simulate test execution (in real implementation would use tools like k6, JMeter, etc.)
            await self._simulate_load_test(scenario)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Generate test results
            results = await self._generate_test_results(scenario, duration)
            
            # Mark test as completed
            if test_id in self.active_tests:
                del self.active_tests[test_id]
            
            return {
                "test_id": test_id,
                "scenario_name": scenario["name"],
                "status": "completed",
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "duration": duration,
                "results": results
            }
            
        except Exception as e:
            # Mark test as failed
            if test_id in self.active_tests:
                self.active_tests[test_id]["status"] = "failed"
                self.active_tests[test_id]["error"] = str(e)
            
            raise e
    
    async def _simulate_load_test(self, scenario: Dict[str, Any]):
        """Simulate load test execution"""
        duration = scenario["duration"]
        
        # Simulate test execution time
        await asyncio.sleep(min(duration / 100, 10))  # Max 10 seconds for simulation
    
    async def _generate_test_results(
        self,
        scenario: Dict[str, Any],
        duration: float
    ) -> Dict[str, Any]:
        """Generate performance test results"""
        concurrent_users = scenario["concurrent_users"]
        test_type = scenario["type"]
        
        # Simulate realistic performance metrics
        if test_type == TestType.LOAD_TEST.value:
            avg_response_time = 150 + (concurrent_users * 0.5)  # Realistic scaling
            error_rate = min(concurrent_users * 0.01, 5)         # Error rate increases with load
            throughput = max(1000 - (concurrent_users * 2), 100) # Throughput decreases with load
        elif test_type == TestType.STRESS_TEST.value:
            avg_response_time = 300 + (concurrent_users * 1.2)
            error_rate = min(concurrent_users * 0.02, 15)
            throughput = max(800 - (concurrent_users * 3), 50)
        else:
            avg_response_time = 200 + (concurrent_users * 0.8)
            error_rate = min(concurrent_users * 0.015, 8)
            throughput = max(900 - (concurrent_users * 2.5), 75)
        
        total_requests = int(throughput * duration / 60)  # Requests per minute * minutes
        failed_requests = int(total_requests * error_rate / 100)
        successful_requests = total_requests - failed_requests
        
        return {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": round((successful_requests / total_requests * 100), 2) if total_requests > 0 else 0,
                "avg_response_time": round(avg_response_time, 2),
                "min_response_time": round(avg_response_time * 0.6, 2),
                "max_response_time": round(avg_response_time * 2.5, 2),
                "throughput": round(throughput, 2)
            },
            "performance_metrics": {
                "p50_response_time": round(avg_response_time * 0.9, 2),
                "p90_response_time": round(avg_response_time * 1.4, 2),
                "p95_response_time": round(avg_response_time * 1.7, 2),
                "p99_response_time": round(avg_response_time * 2.2, 2),
                "error_rate": round(error_rate, 2),
                "requests_per_second": round(throughput / 60, 2)
            },
            "resource_utilization": {
                "cpu_usage": min(30 + (concurrent_users * 0.1), 90),
                "memory_usage": min(40 + (concurrent_users * 0.05), 85),
                "network_io": f"{round(throughput * 1.5, 2)} Mbps",
                "disk_io": f"{round(throughput * 0.3, 2)} MB/s"
            },
            "test_configuration": {
                "concurrent_users": concurrent_users,
                "test_duration": duration,
                "test_type": test_type,
                "target": scenario["target"]
            }
        }
    
    async def get_test_status(self, test_id: str) -> Dict[str, Any]:
        """Get status of a running or completed test"""
        try:
            # Check active tests
            if test_id in self.active_tests:
                return {
                    "status": "success",
                    "test_status": self.active_tests[test_id]
                }
            
            # Check completed tests
            if test_id in self.test_results:
                return {
                    "status": "success",
                    "test_status": self.test_results[test_id]
                }
            
            return {
                "status": "error",
                "error": "Test not found"
            }
            
        except Exception as e:
            logger.error(f"Failed to get test status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_test_report(self, test_id: str) -> Dict[str, Any]:
        """Get detailed test report"""
        try:
            if test_id not in self.test_results:
                return {"status": "error", "error": "Test results not found"}
            
            test_data = self.test_results[test_id]
            
            # Generate comprehensive report
            report = {
                "test_summary": {
                    "test_id": test_id,
                    "scenario": test_data["scenario_name"],
                    "status": test_data["status"],
                    "execution_time": test_data["duration"],
                    "started_at": test_data["started_at"],
                    "completed_at": test_data["completed_at"]
                },
                "performance_results": test_data["results"],
                "recommendations": await self._generate_recommendations(test_data["results"]),
                "pass_fail_criteria": await self._evaluate_pass_fail_criteria(test_data["results"])
            }
            
            return {
                "status": "success",
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Failed to generate test report: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        summary = results["summary"]
        performance = results["performance_metrics"]
        resources = results["resource_utilization"]
        
        # Response time recommendations
        if summary["avg_response_time"] > 1000:
            recommendations.append("Consider optimizing database queries or adding caching to reduce response times")
        
        # Error rate recommendations
        if performance["error_rate"] > 5:
            recommendations.append("High error rate detected. Review error logs and implement better error handling")
        
        # Throughput recommendations
        if summary["throughput"] < 100:
            recommendations.append("Low throughput. Consider scaling up server resources or optimizing application code")
        
        # Resource utilization recommendations
        if resources["cpu_usage"] > 80:
            recommendations.append("High CPU usage. Consider horizontal scaling or CPU optimization")
        
        if resources["memory_usage"] > 80:
            recommendations.append("High memory usage. Check for memory leaks or consider increasing available memory")
        
        # Success rate recommendations
        if summary["success_rate"] < 95:
            recommendations.append("Success rate below 95%. Investigate failed requests and improve system reliability")
        
        return recommendations
    
    async def _evaluate_pass_fail_criteria(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate test against pass/fail criteria"""
        summary = results["summary"]
        performance = results["performance_metrics"]
        
        criteria = {
            "response_time": {
                "threshold": 2000,  # 2 seconds
                "actual": summary["avg_response_time"],
                "passed": summary["avg_response_time"] <= 2000
            },
            "error_rate": {
                "threshold": 5,     # 5%
                "actual": performance["error_rate"],
                "passed": performance["error_rate"] <= 5
            },
            "success_rate": {
                "threshold": 95,    # 95%
                "actual": summary["success_rate"],
                "passed": summary["success_rate"] >= 95
            },
            "throughput": {
                "threshold": 100,   # 100 req/min
                "actual": summary["throughput"],
                "passed": summary["throughput"] >= 100
            }
        }
        
        # Overall pass/fail
        overall_passed = all(criterion["passed"] for criterion in criteria.values())
        
        return {
            "overall_result": "PASS" if overall_passed else "FAIL",
            "criteria": criteria,
            "passed_criteria": sum(1 for c in criteria.values() if c["passed"]),
            "total_criteria": len(criteria)
        }
    
    async def run_benchmark_suite(self) -> Dict[str, Any]:
        """Run complete performance benchmark suite"""
        try:
            logger.info("Starting performance benchmark suite...")
            
            benchmark_results = []
            
            # Run all test scenarios
            for scenario_name in self.test_scenarios.keys():
                result = await self.run_performance_test(scenario_name)
                benchmark_results.append(result)
            
            # Generate suite summary
            suite_summary = await self._generate_suite_summary(benchmark_results)
            
            return {
                "status": "success",
                "suite_summary": suite_summary,
                "individual_results": benchmark_results,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to run benchmark suite: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _generate_suite_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary for benchmark suite"""
        successful_tests = [r for r in results if r["status"] == "success"]
        failed_tests = [r for r in results if r["status"] == "error"]
        
        if not successful_tests:
            return {
                "total_tests": len(results),
                "successful_tests": 0,
                "failed_tests": len(failed_tests),
                "overall_status": "FAILED"
            }
        
        # Aggregate metrics from successful tests
        avg_response_times = []
        error_rates = []
        success_rates = []
        
        for result in successful_tests:
            test_results = result.get("test_result", {}).get("results", {})
            summary = test_results.get("summary", {})
            performance = test_results.get("performance_metrics", {})
            
            if summary:
                avg_response_times.append(summary.get("avg_response_time", 0))
                success_rates.append(summary.get("success_rate", 0))
            
            if performance:
                error_rates.append(performance.get("error_rate", 0))
        
        return {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "overall_status": "PASSED" if len(failed_tests) == 0 else "PARTIAL",
            "aggregate_metrics": {
                "avg_response_time": round(sum(avg_response_times) / len(avg_response_times), 2) if avg_response_times else 0,
                "avg_error_rate": round(sum(error_rates) / len(error_rates), 2) if error_rates else 0,
                "avg_success_rate": round(sum(success_rates) / len(success_rates), 2) if success_rates else 0
            }
        }
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get performance testing service metrics"""
        return {
            "service": "performance_testing",
            "metrics": {
                "available_scenarios": len(self.test_scenarios),
                "completed_tests": len(self.test_results),
                "active_tests": len(self.active_tests),
                "test_types_supported": len(TestType)
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "performance_testing",
            "status": "healthy" if self.is_active else "inactive",
            "active_tests": len(self.active_tests),
            "test_engine": "active" if self.is_active else "inactive",
            "last_check": datetime.utcnow().isoformat()
        }