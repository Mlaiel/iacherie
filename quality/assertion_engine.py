"""⚡ Assertion Engine - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + SOFTWARE_ARCHITECT + ML_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Enterprise Assertion-Engine mit Custom-Assertions - provides
advanced assertion capabilities for complex testing scenarios.
================================================================
"""

import asyncio
import inspect
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union, Type, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import functools

logger = logging.getLogger(__name__)

T = TypeVar('T')

class AssertionType(Enum):
    """Types of assertions"""
    EQUALITY = "equality"
    COMPARISON = "comparison"
    CONTAINMENT = "containment"
    TYPE_CHECK = "type_check"
    PATTERN_MATCH = "pattern_match"
    TEMPORAL = "temporal"
    COLLECTION = "collection"
    ASYNC_OPERATION = "async_operation"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class AssertionSeverity(Enum):
    """Assertion failure severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class AssertionContext:
    """Context information for assertions"""
    test_name: str
    test_file: str
    line_number: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AssertionResult:
    """Result of an assertion"""
    passed: bool
    assertion_type: AssertionType
    severity: AssertionSeverity
    message: str
    expected: Any
    actual: Any
    context: AssertionContext
    execution_time: float
    details: Dict[str, Any] = field(default_factory=dict)

class AssertionError(Exception):
    """Custom assertion error"""
    def __init__(self, result: AssertionResult):
        self.result = result
        super().__init__(result.message)

class BaseAssertion(ABC, Generic[T]):
    """Base class for all assertions"""
    
    def __init__(self, severity: AssertionSeverity = AssertionSeverity.HIGH):
        self.severity = severity
        self.context: Optional[AssertionContext] = None
    
    @abstractmethod
    def evaluate(self, actual: T, expected: T, **kwargs) -> AssertionResult:
        """Evaluate the assertion"""
        pass
    
    def with_context(self, context: AssertionContext) -> 'BaseAssertion[T]':
        """Set assertion context"""
        self.context = context
        return self
    
    def with_severity(self, severity: AssertionSeverity) -> 'BaseAssertion[T]':
        """Set assertion severity"""
        self.severity = severity
        return self

class EqualityAssertion(BaseAssertion[Any]):
    """Equality assertion with advanced comparison"""
    
    def __init__(self, tolerance: float = 0.0, deep_compare: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.tolerance = tolerance
        self.deep_compare = deep_compare
    
    def evaluate(self, actual: Any, expected: Any, **kwargs) -> AssertionResult:
        start_time = time.time()
        
        try:
            passed = self._compare_values(actual, expected)
            message = f"Expected {expected}, got {actual}"
            
            if passed:
                message = f"Values are equal: {actual}"
            
            return AssertionResult(
                passed=passed,
                assertion_type=AssertionType.EQUALITY,
                severity=self.severity,
                message=message,
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={
                    "tolerance": self.tolerance,
                    "deep_compare": self.deep_compare
                }
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.EQUALITY,
                severity=self.severity,
                message=f"Assertion evaluation failed: {e}",
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"error": str(e)}
            )
    
    def _compare_values(self, actual: Any, expected: Any) -> bool:
        """Compare values with tolerance and deep comparison"""
        if actual is expected:
            return True
        
        # Numeric comparison with tolerance
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            return abs(actual - expected) <= self.tolerance
        
        # String comparison
        if isinstance(actual, str) and isinstance(expected, str):
            return actual == expected
        
        # Collection comparison
        if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
            if len(actual) != len(expected):
                return False
            
            if self.deep_compare:
                return all(self._compare_values(a, e) for a, e in zip(actual, expected))
            else:
                return actual == expected
        
        # Dictionary comparison
        if isinstance(actual, dict) and isinstance(expected, dict):
            if set(actual.keys()) != set(expected.keys()):
                return False
            
            if self.deep_compare:
                return all(self._compare_values(actual[k], expected[k]) for k in actual.keys())
            else:
                return actual == expected
        
        # Default comparison
        return actual == expected

class ComparisonAssertion(BaseAssertion[Union[int, float]]):
    """Comparison assertions (greater than, less than, etc.)"""
    
    def __init__(self, operator: str, **kwargs):
        super().__init__(**kwargs)
        self.operator = operator
        self.operators = {
            'gt': lambda a, e: a > e,
            'gte': lambda a, e: a >= e,
            'lt': lambda a, e: a < e,
            'lte': lambda a, e: a <= e,
            'ne': lambda a, e: a != e
        }
    
    def evaluate(self, actual: Union[int, float], expected: Union[int, float], **kwargs) -> AssertionResult:
        start_time = time.time()
        
        if self.operator not in self.operators:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.COMPARISON,
                severity=self.severity,
                message=f"Unknown operator: {self.operator}",
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time
            )
        
        try:
            comparison_func = self.operators[self.operator]
            passed = comparison_func(actual, expected)
            
            message = f"Expected {actual} {self.operator} {expected}"
            if not passed:
                message = f"Assertion failed: {actual} {self.operator} {expected}"
            
            return AssertionResult(
                passed=passed,
                assertion_type=AssertionType.COMPARISON,
                severity=self.severity,
                message=message,
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"operator": self.operator}
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.COMPARISON,
                severity=self.severity,
                message=f"Comparison failed: {e}",
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"error": str(e)}
            )

class ContainmentAssertion(BaseAssertion[Any]):
    """Containment assertions (in, not in, contains, etc.)"""
    
    def __init__(self, contains: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.contains = contains
    
    def evaluate(self, actual: Any, expected: Any, **kwargs) -> AssertionResult:
        start_time = time.time()
        
        try:
            if self.contains:
                passed = expected in actual
                message = f"Expected {expected} to be in {actual}"
            else:
                passed = expected not in actual
                message = f"Expected {expected} to not be in {actual}"
            
            if not passed:
                message = f"Assertion failed: {message}"
            
            return AssertionResult(
                passed=passed,
                assertion_type=AssertionType.CONTAINMENT,
                severity=self.severity,
                message=message,
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"contains": self.contains}
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.CONTAINMENT,
                severity=self.severity,
                message=f"Containment check failed: {e}",
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"error": str(e)}
            )

class TypeAssertion(BaseAssertion[Any]):
    """Type checking assertions"""
    
    def __init__(self, strict: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.strict = strict
    
    def evaluate(self, actual: Any, expected: Type, **kwargs) -> AssertionResult:
        start_time = time.time()
        
        try:
            if self.strict:
                passed = type(actual) is expected
            else:
                passed = isinstance(actual, expected)
            
            actual_type = type(actual)
            message = f"Expected type {expected.__name__}, got {actual_type.__name__}"
            
            if passed:
                message = f"Type check passed: {actual_type.__name__}"
            
            return AssertionResult(
                passed=passed,
                assertion_type=AssertionType.TYPE_CHECK,
                severity=self.severity,
                message=message,
                expected=expected,
                actual=actual_type,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"strict": self.strict}
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.TYPE_CHECK,
                severity=self.severity,
                message=f"Type check failed: {e}",
                expected=expected,
                actual=type(actual),
                context=self.context,
                execution_time=time.time() - start_time,
                details={"error": str(e)}
            )

class PatternAssertion(BaseAssertion[str]):
    """Pattern matching assertions using regex"""
    
    def __init__(self, flags: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.flags = flags
    
    def evaluate(self, actual: str, expected: str, **kwargs) -> AssertionResult:
        start_time = time.time()
        
        try:
            pattern = re.compile(expected, self.flags)
            match = pattern.search(actual)
            passed = match is not None
            
            message = f"Pattern '{expected}' {'found' if passed else 'not found'} in '{actual}'"
            
            details = {"pattern": expected, "flags": self.flags}
            if match:
                details["match"] = {
                    "groups": match.groups(),
                    "start": match.start(),
                    "end": match.end()
                }
            
            return AssertionResult(
                passed=passed,
                assertion_type=AssertionType.PATTERN_MATCH,
                severity=self.severity,
                message=message,
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details=details
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.PATTERN_MATCH,
                severity=self.severity,
                message=f"Pattern matching failed: {e}",
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"error": str(e)}
            )

class PerformanceAssertion(BaseAssertion[Callable]):
    """Performance-based assertions"""
    
    def __init__(self, max_execution_time: float, **kwargs):
        super().__init__(**kwargs)
        self.max_execution_time = max_execution_time
    
    def evaluate(self, actual: Callable, expected: Any = None, **kwargs) -> AssertionResult:
        start_time = time.time()
        
        try:
            # Execute the function and measure time
            exec_start = time.time()
            if asyncio.iscoroutinefunction(actual):
                # Handle async functions
                import asyncio
                result = asyncio.run(actual())
            else:
                result = actual()
            exec_time = time.time() - exec_start
            
            passed = exec_time <= self.max_execution_time
            
            message = f"Execution time {exec_time:.3f}s ({'within' if passed else 'exceeded'} limit of {self.max_execution_time}s)"
            
            return AssertionResult(
                passed=passed,
                assertion_type=AssertionType.PERFORMANCE,
                severity=self.severity,
                message=message,
                expected=self.max_execution_time,
                actual=exec_time,
                context=self.context,
                execution_time=time.time() - start_time,
                details={
                    "max_execution_time": self.max_execution_time,
                    "actual_execution_time": exec_time,
                    "function_result": result
                }
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.PERFORMANCE,
                severity=self.severity,
                message=f"Performance assertion failed: {e}",
                expected=self.max_execution_time,
                actual=None,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"error": str(e)}
            )

class AsyncAssertion(BaseAssertion[Callable]):
    """Assertions for async operations"""
    
    def __init__(self, timeout: float = 30.0, **kwargs):
        super().__init__(**kwargs)
        self.timeout = timeout
    
    async def evaluate_async(self, actual: Callable, expected: Any, **kwargs) -> AssertionResult:
        """Async evaluation method"""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(actual):
                result = await asyncio.wait_for(actual(), timeout=self.timeout)
            else:
                result = actual()
            
            # Compare result with expected
            equality_assertion = EqualityAssertion()
            comparison_result = equality_assertion.evaluate(result, expected)
            
            return AssertionResult(
                passed=comparison_result.passed,
                assertion_type=AssertionType.ASYNC_OPERATION,
                severity=self.severity,
                message=f"Async operation {'succeeded' if comparison_result.passed else 'failed'}: {comparison_result.message}",
                expected=expected,
                actual=result,
                context=self.context,
                execution_time=time.time() - start_time,
                details={
                    "timeout": self.timeout,
                    "async_result": result
                }
            )
        except asyncio.TimeoutError:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.ASYNC_OPERATION,
                severity=self.severity,
                message=f"Async operation timed out after {self.timeout}s",
                expected=expected,
                actual=None,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"timeout": self.timeout}
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.ASYNC_OPERATION,
                severity=self.severity,
                message=f"Async assertion failed: {e}",
                expected=expected,
                actual=None,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"error": str(e)}
            )
    
    def evaluate(self, actual: Callable, expected: Any, **kwargs) -> AssertionResult:
        """Sync wrapper for async evaluation"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.evaluate_async(actual, expected, **kwargs))
                    return future.result()
            else:
                return asyncio.run(self.evaluate_async(actual, expected, **kwargs))
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.ASYNC_OPERATION,
                severity=self.severity,
                message=f"Async assertion evaluation failed: {e}",
                expected=expected,
                actual=None,
                context=self.context,
                execution_time=0.0,
                details={"error": str(e)}
            )

class CollectionAssertion(BaseAssertion[List]):
    """Assertions for collections (lists, sets, etc.)"""
    
    def __init__(self, check_order: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.check_order = check_order
    
    def evaluate(self, actual: List, expected: List, **kwargs) -> AssertionResult:
        start_time = time.time()
        
        try:
            if self.check_order:
                passed = actual == expected
                message = f"Collections {'match' if passed else 'do not match'} (order sensitive)"
            else:
                passed = set(actual) == set(expected)
                message = f"Collections {'match' if passed else 'do not match'} (order insensitive)"
            
            details = {
                "check_order": self.check_order,
                "actual_length": len(actual),
                "expected_length": len(expected)
            }
            
            if not passed:
                details["differences"] = self._find_differences(actual, expected)
            
            return AssertionResult(
                passed=passed,
                assertion_type=AssertionType.COLLECTION,
                severity=self.severity,
                message=message,
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details=details
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.COLLECTION,
                severity=self.severity,
                message=f"Collection assertion failed: {e}",
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"error": str(e)}
            )
    
    def _find_differences(self, actual: List, expected: List) -> Dict[str, Any]:
        """Find differences between collections"""
        actual_set = set(actual)
        expected_set = set(expected)
        
        return {
            "missing_from_actual": list(expected_set - actual_set),
            "extra_in_actual": list(actual_set - expected_set),
            "common_elements": list(actual_set & expected_set)
        }

class CustomAssertion(BaseAssertion[Any]):
    """Custom assertion with user-defined validation function"""
    
    def __init__(self, validation_func: Callable[[Any, Any], bool], description: str = "", **kwargs):
        super().__init__(**kwargs)
        self.validation_func = validation_func
        self.description = description
    
    def evaluate(self, actual: Any, expected: Any, **kwargs) -> AssertionResult:
        start_time = time.time()
        
        try:
            passed = self.validation_func(actual, expected)
            message = self.description or f"Custom assertion {'passed' if passed else 'failed'}"
            
            return AssertionResult(
                passed=passed,
                assertion_type=AssertionType.CUSTOM,
                severity=self.severity,
                message=message,
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={
                    "description": self.description,
                    "validation_function": self.validation_func.__name__
                }
            )
        except Exception as e:
            return AssertionResult(
                passed=False,
                assertion_type=AssertionType.CUSTOM,
                severity=self.severity,
                message=f"Custom assertion failed: {e}",
                expected=expected,
                actual=actual,
                context=self.context,
                execution_time=time.time() - start_time,
                details={"error": str(e)}
            )

class AssertionEngine:
    """
    Enterprise assertion engine with advanced capabilities
    """
    
    def __init__(self):
        """Initialize assertion engine"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.assertion_history: List[AssertionResult] = []
        self.custom_assertions: Dict[str, CustomAssertion] = {}
        self.global_context: Optional[AssertionContext] = None
        
        # Built-in assertion types
        self.assertion_types = {
            'equals': EqualityAssertion,
            'gt': lambda **kwargs: ComparisonAssertion('gt', **kwargs),
            'gte': lambda **kwargs: ComparisonAssertion('gte', **kwargs),
            'lt': lambda **kwargs: ComparisonAssertion('lt', **kwargs),
            'lte': lambda **kwargs: ComparisonAssertion('lte', **kwargs),
            'ne': lambda **kwargs: ComparisonAssertion('ne', **kwargs),
            'contains': ContainmentAssertion,
            'not_contains': lambda **kwargs: ContainmentAssertion(contains=False, **kwargs),
            'is_type': TypeAssertion,
            'matches': PatternAssertion,
            'performance': PerformanceAssertion,
            'async_op': AsyncAssertion,
            'collection': CollectionAssertion
        }
    
    def set_global_context(self, context: AssertionContext):
        """Set global context for all assertions"""
        self.global_context = context
    
    def register_custom_assertion(self, name: str, assertion: CustomAssertion):
        """Register a custom assertion type"""
        self.custom_assertions[name] = assertion
        self.logger.info(f"Registered custom assertion: {name}")
    
    def assert_that(self, actual: Any) -> 'AssertionBuilder':
        """Start building an assertion"""
        return AssertionBuilder(actual, self)
    
    def execute_assertion(self, assertion: BaseAssertion, actual: Any, expected: Any, **kwargs) -> AssertionResult:
        """Execute an assertion and store the result"""
        # Set context if available
        if self.global_context and not assertion.context:
            assertion.context = self.global_context
        
        # Execute the assertion
        result = assertion.evaluate(actual, expected, **kwargs)
        
        # Store in history
        self.assertion_history.append(result)
        
        # Log result
        if result.passed:
            self.logger.debug(f"Assertion passed: {result.message}")
        else:
            self.logger.warning(f"Assertion failed: {result.message}")
        
        return result
    
    def get_assertion_statistics(self) -> Dict[str, Any]:
        """Get statistics about assertion executions"""
        if not self.assertion_history:
            return {"total": 0, "passed": 0, "failed": 0, "success_rate": 0.0}
        
        total = len(self.assertion_history)
        passed = len([r for r in self.assertion_history if r.passed])
        failed = total - passed
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total) * 100.0,
            "by_type": self._get_statistics_by_type(),
            "by_severity": self._get_statistics_by_severity(),
            "average_execution_time": sum(r.execution_time for r in self.assertion_history) / total
        }
    
    def _get_statistics_by_type(self) -> Dict[str, Dict[str, int]]:
        """Get statistics grouped by assertion type"""
        stats = {}
        for result in self.assertion_history:
            type_name = result.assertion_type.value
            if type_name not in stats:
                stats[type_name] = {"total": 0, "passed": 0, "failed": 0}
            
            stats[type_name]["total"] += 1
            if result.passed:
                stats[type_name]["passed"] += 1
            else:
                stats[type_name]["failed"] += 1
        
        return stats
    
    def _get_statistics_by_severity(self) -> Dict[str, Dict[str, int]]:
        """Get statistics grouped by severity"""
        stats = {}
        for result in self.assertion_history:
            severity_name = result.severity.value
            if severity_name not in stats:
                stats[severity_name] = {"total": 0, "passed": 0, "failed": 0}
            
            stats[severity_name]["total"] += 1
            if result.passed:
                stats[severity_name]["passed"] += 1
            else:
                stats[severity_name]["failed"] += 1
        
        return stats
    
    def export_results(self, format: str = "json", filter_failed: bool = False) -> str:
        """Export assertion results"""
        results = self.assertion_history
        if filter_failed:
            results = [r for r in results if not r.passed]
        
        if format == "json":
            return self._export_json(results)
        elif format == "html":
            return self._export_html(results)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, results: List[AssertionResult]) -> str:
        """Export results as JSON"""
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": self.get_assertion_statistics(),
            "results": [
                {
                    "passed": r.passed,
                    "type": r.assertion_type.value,
                    "severity": r.severity.value,
                    "message": r.message,
                    "expected": str(r.expected),
                    "actual": str(r.actual),
                    "execution_time": r.execution_time,
                    "timestamp": r.context.timestamp.isoformat() if r.context else None
                }
                for r in results
            ]
        }
        return json.dumps(data, indent=2)
    
    def _export_html(self, results: List[AssertionResult]) -> str:
        """Export results as HTML"""
        stats = self.get_assertion_statistics()
        html = f"""
        <html>
        <head><title>Assertion Results</title></head>
        <body>
        <h1>Assertion Results</h1>
        <h2>Summary</h2>
        <ul>
        <li>Total: {stats['total']}</li>
        <li>Passed: {stats['passed']}</li>
        <li>Failed: {stats['failed']}</li>
        <li>Success Rate: {stats['success_rate']:.1f}%</li>
        </ul>
        </body>
        </html>
        """
        return html

class AssertionBuilder:
    """Fluent interface for building assertions"""
    
    def __init__(self, actual: Any, engine: AssertionEngine):
        self.actual = actual
        self.engine = engine
        self.assertion: Optional[BaseAssertion] = None
        self.severity = AssertionSeverity.HIGH
    
    def with_severity(self, severity: AssertionSeverity) -> 'AssertionBuilder':
        """Set assertion severity"""
        self.severity = severity
        return self
    
    def equals(self, expected: Any, tolerance: float = 0.0) -> AssertionResult:
        """Assert equality"""
        assertion = EqualityAssertion(tolerance=tolerance, severity=self.severity)
        return self.engine.execute_assertion(assertion, self.actual, expected)
    
    def is_greater_than(self, expected: Union[int, float]) -> AssertionResult:
        """Assert greater than"""
        assertion = ComparisonAssertion('gt', severity=self.severity)
        return self.engine.execute_assertion(assertion, self.actual, expected)
    
    def is_less_than(self, expected: Union[int, float]) -> AssertionResult:
        """Assert less than"""
        assertion = ComparisonAssertion('lt', severity=self.severity)
        return self.engine.execute_assertion(assertion, self.actual, expected)
    
    def contains(self, expected: Any) -> AssertionResult:
        """Assert containment"""
        assertion = ContainmentAssertion(severity=self.severity)
        return self.engine.execute_assertion(assertion, self.actual, expected)
    
    def is_type(self, expected_type: Type) -> AssertionResult:
        """Assert type"""
        assertion = TypeAssertion(severity=self.severity)
        return self.engine.execute_assertion(assertion, self.actual, expected_type)
    
    def matches(self, pattern: str) -> AssertionResult:
        """Assert pattern match"""
        assertion = PatternAssertion(severity=self.severity)
        return self.engine.execute_assertion(assertion, self.actual, pattern)
    
    def executes_within(self, max_time: float) -> AssertionResult:
        """Assert execution time"""
        assertion = PerformanceAssertion(max_time, severity=self.severity)
        return self.engine.execute_assertion(assertion, self.actual, None)
    
    def collection_equals(self, expected: List, check_order: bool = True) -> AssertionResult:
        """Assert collection equality"""
        assertion = CollectionAssertion(check_order=check_order, severity=self.severity)
        return self.engine.execute_assertion(assertion, self.actual, expected)

# Global assertion engine instance
assertion_engine = AssertionEngine()

# Convenience functions
def assert_that(actual: Any) -> AssertionBuilder:
    """Create an assertion builder"""
    return assertion_engine.assert_that(actual)

def set_assertion_context(test_name: str, test_file: str, line_number: int):
    """Set global assertion context"""
    context = AssertionContext(
        test_name=test_name,
        test_file=test_file,
        line_number=line_number
    )
    assertion_engine.set_global_context(context)

# Decorator for automatic context setting
def with_assertion_context(func):
    """Decorator to automatically set assertion context"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get caller information
        frame = inspect.currentframe().f_back
        test_file = frame.f_code.co_filename
        line_number = frame.f_lineno
        test_name = func.__name__
        
        # Set context
        set_assertion_context(test_name, test_file, line_number)
        
        try:
            return func(*args, **kwargs)
        finally:
            # Clear context
            assertion_engine.global_context = None
    
    return wrapper

__all__ = [
    "AssertionEngine",
    "AssertionBuilder",
    "BaseAssertion",
    "EqualityAssertion",
    "ComparisonAssertion",
    "ContainmentAssertion",
    "TypeAssertion",
    "PatternAssertion",
    "PerformanceAssertion",
    "AsyncAssertion",
    "CollectionAssertion",
    "CustomAssertion",
    "AssertionResult",
    "AssertionContext",
    "AssertionType",
    "AssertionSeverity",
    "AssertionError",
    "assertion_engine",
    "assert_that",
    "set_assertion_context",
    "with_assertion_context"
]