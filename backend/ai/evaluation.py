"""
Performance Metrics and Testing Module
=====================================

Consolidated evaluation functionality from various conversational and AI modules.
Provides comprehensive performance metrics, testing frameworks, and quality assurance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import statistics

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of evaluation metrics"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    QUALITY_SCORE = "quality_score"
    USER_SATISFACTION = "user_satisfaction"
    ENGAGEMENT_RATE = "engagement_rate"
    CONVERSATION_COMPLETION = "conversation_completion"
    INTENT_ACCURACY = "intent_accuracy"
    ENTITY_EXTRACTION_ACCURACY = "entity_extraction_accuracy"
    SENTIMENT_ACCURACY = "sentiment_accuracy"
    PERSONALIZATION_SCORE = "personalization_score"

class TestType(Enum):
    """Types of tests that can be performed"""
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    PERFORMANCE_TEST = "performance_test"
    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    USER_ACCEPTANCE_TEST = "user_acceptance_test"
    A_B_TEST = "a_b_test"
    CONVERSATION_FLOW_TEST = "conversation_flow_test"
    NLP_ACCURACY_TEST = "nlp_accuracy_test"
    RESPONSE_QUALITY_TEST = "response_quality_test"

class EvaluationStatus(Enum):
    """Status of evaluation tasks"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class MetricResult:
    """Individual metric result"""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: Optional[float] = None

@dataclass
class TestCase:
    """Test case definition"""
    test_id: str
    test_type: TestType
    description: str
    input_data: Any
    expected_output: Any
    test_parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30

@dataclass
class TestResult:
    """Test execution result"""
    test_case: TestCase
    passed: bool
    actual_output: Any
    execution_time: float
    error_message: Optional[str] = None
    metrics: List[MetricResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class EvaluationSuite:
    """Collection of related test cases"""
    suite_id: str
    name: str
    description: str
    test_cases: List[TestCase]
    setup_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None

@dataclass
class EvaluationReport:
    """Comprehensive evaluation report"""
    evaluation_id: str
    suite_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: EvaluationStatus = EvaluationStatus.PENDING
    test_results: List[TestResult] = field(default_factory=list)
    overall_metrics: List[MetricResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

class MetricsCalculator:
    """Calculates various performance metrics"""
    
    def __init__(self) -> None:
        self.calculation_cache: Dict[str, Any] = {}
    
    async def calculate_accuracy(self, predictions: List[Any], ground_truth: List[Any]) -> float:
        """Calculate accuracy metric"""
        if len(predictions) != len(ground_truth):
            raise ValueError("Predictions and ground truth must have same length")
        
        correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
        return correct / len(predictions) if predictions else 0.0
    
    async def calculate_precision_recall_f1(self, predictions: List[Any], ground_truth: List[Any], 
                                          positive_class: Any = 1) -> Tuple[float, float, float]:
        """Calculate precision, recall, and F1 score"""
        true_positives = sum(1 for p, g in zip(predictions, ground_truth) 
                           if p == positive_class and g == positive_class)
        false_positives = sum(1 for p, g in zip(predictions, ground_truth) 
                            if p == positive_class and g != positive_class)
        false_negatives = sum(1 for p, g in zip(predictions, ground_truth) 
                            if p != positive_class and g == positive_class)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return precision, recall, f1
    
    async def calculate_response_time_metrics(self, response_times: List[float]) -> Dict[str, float]:
        """Calculate response time statistics"""
        if not response_times:
            return {"mean": 0.0, "median": 0.0, "p95": 0.0, "p99": 0.0}
        
        sorted_times = sorted(response_times)
        n = len(sorted_times)
        
        return {
            "mean": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "min": min(response_times),
            "max": max(response_times),
            "p95": sorted_times[int(0.95 * n)] if n > 0 else 0.0,
            "p99": sorted_times[int(0.99 * n)] if n > 0 else 0.0,
            "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0.0
        }
    
    async def calculate_engagement_metrics(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate engagement metrics"""
        if not interactions:
            return {"engagement_rate": 0.0, "average_session_length": 0.0, "bounce_rate": 0.0}
        
        total_interactions = len(interactions)
        engaged_interactions = sum(1 for i in interactions if i.get("engaged", False))
        session_lengths = [i.get("session_length", 0) for i in interactions]
        bounced_sessions = sum(1 for i in interactions if i.get("session_length", 0) < 30)  # Less than 30 seconds
        
        return {
            "engagement_rate": engaged_interactions / total_interactions,
            "average_session_length": statistics.mean(session_lengths),
            "bounce_rate": bounced_sessions / total_interactions
        }
    
    async def calculate_conversation_quality_score(self, conversation_data: Dict[str, Any]) -> float:
        """Calculate conversation quality score"""
        # Factors that contribute to conversation quality
        factors = {
            "relevance": conversation_data.get("relevance_score", 0.5),
            "coherence": conversation_data.get("coherence_score", 0.5),
            "helpfulness": conversation_data.get("helpfulness_score", 0.5),
            "naturalness": conversation_data.get("naturalness_score", 0.5),
            "completeness": conversation_data.get("completeness_score", 0.5)
        }
        
        # Weighted average
        weights = {
            "relevance": 0.25,
            "coherence": 0.20,
            "helpfulness": 0.25,
            "naturalness": 0.15,
            "completeness": 0.15
        }
        
        quality_score = sum(factors[key] * weights[key] for key in factors)
        return min(1.0, max(0.0, quality_score))

class TestExecutor:
    """Executes test cases and collects results"""
    
    def __init__(self) -> None:
        self.active_tests: Dict[str, TestResult] = {}
        self.metrics_calculator = MetricsCalculator()
    
    async def execute_test_case(self, test_case: TestCase, target_function: Callable) -> TestResult:
        """Execute a single test case"""
        start_time = time.time()
        
        try:
            # Execute the test
            actual_output = await self._run_test_with_timeout(
                target_function, 
                test_case.input_data, 
                test_case.timeout_seconds
            )
            
            execution_time = time.time() - start_time
            
            # Compare with expected output
            passed = await self._compare_outputs(actual_output, test_case.expected_output)
            
            # Calculate metrics
            metrics = await self._calculate_test_metrics(test_case, actual_output, execution_time)
            
            return TestResult(
                test_case=test_case,
                passed=passed,
                actual_output=actual_output,
                execution_time=execution_time,
                metrics=metrics
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_case=test_case,
                passed=False,
                actual_output=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def _run_test_with_timeout(self, target_function: Callable, input_data: Any, timeout: int) -> Any:
        """Run test function with timeout"""
        try:
            result = await asyncio.wait_for(
                target_function(input_data),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Test timed out after {timeout} seconds")
    
    async def _compare_outputs(self, actual: Any, expected: Any) -> bool:
        """Compare actual output with expected output"""
        if isinstance(expected, dict) and isinstance(actual, dict):
            return await self._compare_dict_outputs(actual, expected)
        elif isinstance(expected, list) and isinstance(actual, list):
            return await self._compare_list_outputs(actual, expected)
        else:
            return actual == expected
    
    async def _compare_dict_outputs(self, actual: Dict, expected: Dict) -> bool:
        """Compare dictionary outputs with tolerance for floating point numbers"""
        if set(actual.keys()) != set(expected.keys()):
            return False
        
        for key in expected:
            if isinstance(expected[key], float) and isinstance(actual[key], (int, float)):
                if abs(actual[key] - expected[key]) > 0.001:  # Tolerance for floating point
                    return False
            elif actual[key] != expected[key]:
                return False
        
        return True
    
    async def _compare_list_outputs(self, actual: List, expected: List) -> bool:
        """Compare list outputs"""
        if len(actual) != len(expected):
            return False
        
        for a, e in zip(actual, expected):
            if not await self._compare_outputs(a, e):
                return False
        
        return True
    
    async def _calculate_test_metrics(self, test_case: TestCase, output: Any, execution_time: float) -> List[MetricResult]:
        """Calculate metrics for test execution"""
        metrics = []
        
        # Response time metric
        metrics.append(MetricResult(
            metric_type=MetricType.RESPONSE_TIME,
            value=execution_time,
            unit="seconds",
            timestamp=datetime.now()
        ))
        
        # Test-specific metrics based on test type
        if test_case.test_type == TestType.NLP_ACCURACY_TEST:
            # Mock NLP accuracy calculation
            accuracy = 0.85 + (hash(str(output)) % 20) / 100  # Simulated accuracy
            metrics.append(MetricResult(
                metric_type=MetricType.INTENT_ACCURACY,
                value=accuracy,
                unit="percentage",
                timestamp=datetime.now()
            ))
        
        elif test_case.test_type == TestType.RESPONSE_QUALITY_TEST:
            # Mock quality score calculation
            quality = 0.8 + (hash(str(output)) % 25) / 100  # Simulated quality
            metrics.append(MetricResult(
                metric_type=MetricType.QUALITY_SCORE,
                value=quality,
                unit="score",
                timestamp=datetime.now()
            ))
        
        return metrics

class EvaluationEngine:
    """Main evaluation engine that orchestrates testing and metrics collection"""
    
    def __init__(self) -> None:
        self.test_executor = TestExecutor()
        self.metrics_calculator = MetricsCalculator()
        self.evaluation_suites: Dict[str, EvaluationSuite] = {}
        self.evaluation_reports: Dict[str, EvaluationReport] = {}
    
    async def register_evaluation_suite(self, suite -> None: EvaluationSuite) -> None:
        """Register an evaluation suite"""
        self.evaluation_suites[suite.suite_id] = suite
        logger.info(f"Registered evaluation suite: {suite.suite_id}")
    
    async def run_evaluation(self, suite_id: str, target_system: Any) -> str:
        """Run evaluation suite and return evaluation ID"""
        if suite_id not in self.evaluation_suites:
            raise ValueError(f"Evaluation suite {suite_id} not found")
        
        suite = self.evaluation_suites[suite_id]
        evaluation_id = f"eval_{suite_id}_{datetime.now().timestamp()}"
        
        report = EvaluationReport(
            evaluation_id=evaluation_id,
            suite_id=suite_id,
            started_at=datetime.now(),
            status=EvaluationStatus.RUNNING
        )
        
        self.evaluation_reports[evaluation_id] = report
        
        try:
            # Run setup if available
            if suite.setup_function:
                await suite.setup_function()
            
            # Execute all test cases
            for test_case in suite.test_cases:
                test_result = await self.test_executor.execute_test_case(
                    test_case, 
                    target_system
                )
                report.test_results.append(test_result)
            
            # Calculate overall metrics
            report.overall_metrics = await self._calculate_overall_metrics(report.test_results)
            
            # Generate summary
            report.summary = await self._generate_evaluation_summary(report)
            
            # Run teardown if available
            if suite.teardown_function:
                await suite.teardown_function()
            
            report.status = EvaluationStatus.COMPLETED
            report.completed_at = datetime.now()
            
            logger.info(f"Evaluation {evaluation_id} completed successfully")
            
        except Exception as e:
            report.status = EvaluationStatus.FAILED
            report.summary = {"error": str(e)}
            logger.error(f"Evaluation {evaluation_id} failed: {e}")
        
        return evaluation_id
    
    async def _calculate_overall_metrics(self, test_results: List[TestResult]) -> List[MetricResult]:
        """Calculate overall metrics from test results"""
        overall_metrics = []
        
        # Calculate pass rate
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result.passed)
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        
        overall_metrics.append(MetricResult(
            metric_type=MetricType.ACCURACY,
            value=pass_rate,
            unit="percentage",
            timestamp=datetime.now(),
            context={"total_tests": total_tests, "passed_tests": passed_tests}
        ))
        
        # Calculate average response time
        response_times = [result.execution_time for result in test_results]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            overall_metrics.append(MetricResult(
                metric_type=MetricType.RESPONSE_TIME,
                value=avg_response_time,
                unit="seconds",
                timestamp=datetime.now()
            ))
        
        # Calculate throughput (tests per second)
        if response_times:
            throughput = 1.0 / statistics.mean(response_times)
            overall_metrics.append(MetricResult(
                metric_type=MetricType.THROUGHPUT,
                value=throughput,
                unit="tests_per_second",
                timestamp=datetime.now()
            ))
        
        return overall_metrics
    
    async def _generate_evaluation_summary(self, report: EvaluationReport) -> Dict[str, Any]:
        """Generate evaluation summary"""
        total_tests = len(report.test_results)
        passed_tests = sum(1 for result in report.test_results if result.passed)
        failed_tests = total_tests - passed_tests
        
        # Group results by test type
        test_type_summary = {}
        for result in report.test_results:
            test_type = result.test_case.test_type.value
            if test_type not in test_type_summary:
                test_type_summary[test_type] = {"total": 0, "passed": 0, "failed": 0}
            
            test_type_summary[test_type]["total"] += 1
            if result.passed:
                test_type_summary[test_type]["passed"] += 1
            else:
                test_type_summary[test_type]["failed"] += 1
        
        # Calculate execution statistics
        execution_times = [result.execution_time for result in report.test_results]
        duration = (report.completed_at - report.started_at).total_seconds() if report.completed_at else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "test_type_breakdown": test_type_summary,
            "execution_statistics": {
                "total_duration": duration,
                "average_test_time": statistics.mean(execution_times) if execution_times else 0,
                "min_test_time": min(execution_times) if execution_times else 0,
                "max_test_time": max(execution_times) if execution_times else 0
            }
        }
    
    async def get_evaluation_report(self, evaluation_id: str) -> Optional[EvaluationReport]:
        """Get evaluation report by ID"""
        return self.evaluation_reports.get(evaluation_id)
    
    async def list_evaluations(self, status_filter: Optional[EvaluationStatus] = None) -> List[Dict[str, Any]]:
        """List evaluations with optional status filter"""
        evaluations = list(self.evaluation_reports.values())
        
        if status_filter:
            evaluations = [eval for eval in evaluations if eval.status == status_filter]
        
        return [
            {
                "evaluation_id": eval.evaluation_id,
                "suite_id": eval.suite_id,
                "status": eval.status.value,
                "started_at": eval.started_at.isoformat(),
                "completed_at": eval.completed_at.isoformat() if eval.completed_at else None,
                "total_tests": len(eval.test_results),
                "pass_rate": eval.summary.get("pass_rate", 0.0)
            }
            for eval in evaluations
        ]

class PerformanceBenchmark:
    """Performance benchmarking utilities"""
    
    def __init__(self) -> None:
        self.benchmark_results: Dict[str, List[float]] = {}
    
    async def benchmark_function(self, function: Callable, input_data: Any, 
                                iterations: int = 100) -> Dict[str, float]:
        """Benchmark a function's performance"""
        execution_times = []
        
        for _ in range(iterations):
            start_time = time.time()
            try:
                await function(input_data)
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
            except Exception as e:
                logger.warning(f"Benchmark iteration failed: {e}")
        
        if not execution_times:
            return {"error": "All benchmark iterations failed"}
        
        return await self.metrics_calculator.calculate_response_time_metrics(execution_times)
    
    async def compare_implementations(self, implementations: Dict[str, Callable], 
                                    input_data: Any, iterations: int = 100) -> Dict[str, Dict[str, float]]:
        """Compare performance of multiple implementations"""
        results = {}
        
        for name, implementation in implementations.items():
            results[name] = await self.benchmark_function(implementation, input_data, iterations)
        
        return results

# Factory functions
def create_evaluation_engine() -> EvaluationEngine:
    """Create evaluation engine instance"""
    return EvaluationEngine()

def create_metrics_calculator() -> MetricsCalculator:
    """Create metrics calculator instance"""
    return MetricsCalculator()

def create_test_executor() -> TestExecutor:
    """Create test executor instance"""
    return TestExecutor()

def create_performance_benchmark() -> PerformanceBenchmark:
    """Create performance benchmark instance"""
    return PerformanceBenchmark()

# Export all classes and functions
__all__ = [
    # Core classes
    "EvaluationEngine",
    "MetricsCalculator",
    "TestExecutor", 
    "PerformanceBenchmark",
    
    # Data structures
    "MetricResult",
    "TestCase",
    "TestResult",
    "EvaluationSuite",
    "EvaluationReport",
    "MetricType",
    "TestType",
    "EvaluationStatus",
    
    # Factory functions
    "create_evaluation_engine",
    "create_metrics_calculator",
    "create_test_executor",
    "create_performance_benchmark"
]