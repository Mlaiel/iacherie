"""🔍 Enterprise Assertion Engine - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + BACKEND_SENIOR + ML_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Advanced assertion engine with custom assertions, smart validations,
and comprehensive error reporting for enterprise-grade testing.
================================================================
"""

import logging
import json
import re
import time
import inspect
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Type
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import difflib
import math

logger = logging.getLogger(__name__)

class AssertionType(Enum):
    """Types of assertions"""
    BASIC = "basic"
    NUMERIC = "numeric" 
    STRING = "string"
    COLLECTION = "collection"
    OBJECT = "object"
    API = "api"
    PERFORMANCE = "performance"
    BUSINESS_LOGIC = "business_logic"
    AI_MODEL = "ai_model"
    SECURITY = "security"

class AssertionSeverity(Enum):
    """Assertion failure severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class AssertionResult:
    """Result of an assertion"""
    assertion_type: AssertionType
    severity: AssertionSeverity
    passed: bool
    message: str
    expected: Any = None
    actual: Any = None
    details: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    stack_trace: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)

@dataclass
class AssertionContext:
    """Context for assertion execution"""
    test_name: str
    test_file: str
    line_number: int
    function_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    environment: str = "test"
    timestamp: datetime = field(default_factory=datetime.utcnow)

class AssertionError(Exception):
    """Enhanced assertion error with detailed information"""
    
    def __init__(self, result: AssertionResult, context: AssertionContext):
        self.result = result
        self.context = context
        super().__init__(result.message)

class EnterpriseAssertionEngine:
    """
    Advanced assertion engine for comprehensive testing
    """
    
    def __init__(self):
        """Initialize assertion engine"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.assertion_registry: Dict[str, Callable] = {}
        self.results_history: List[AssertionResult] = []
        self.custom_validators: Dict[str, Callable] = {}
        
        # Tolerance settings
        self.numeric_tolerance = 1e-10
        self.performance_tolerance = 0.1  # 10% tolerance for performance tests
        
        # Register built-in assertions
        self._register_builtin_assertions()

    def _register_builtin_assertions(self):
        """Register built-in assertion methods"""
        assertions = [
            # Basic assertions
            ("assert_true", self.assert_true),
            ("assert_false", self.assert_false),
            ("assert_equal", self.assert_equal),
            ("assert_not_equal", self.assert_not_equal),
            ("assert_none", self.assert_none),
            ("assert_not_none", self.assert_not_none),
            
            # Numeric assertions
            ("assert_greater", self.assert_greater),
            ("assert_greater_equal", self.assert_greater_equal),
            ("assert_less", self.assert_less),
            ("assert_less_equal", self.assert_less_equal),
            ("assert_almost_equal", self.assert_almost_equal),
            ("assert_in_range", self.assert_in_range),
            
            # String assertions
            ("assert_string_contains", self.assert_string_contains),
            ("assert_string_starts_with", self.assert_string_starts_with),
            ("assert_string_ends_with", self.assert_string_ends_with),
            ("assert_regex_match", self.assert_regex_match),
            ("assert_string_length", self.assert_string_length),
            
            # Collection assertions
            ("assert_in", self.assert_in),
            ("assert_not_in", self.assert_not_in),
            ("assert_empty", self.assert_empty),
            ("assert_not_empty", self.assert_not_empty),
            ("assert_length", self.assert_length),
            ("assert_contains_all", self.assert_contains_all),
            ("assert_subset", self.assert_subset),
            
            # Object assertions
            ("assert_instance", self.assert_instance),
            ("assert_has_attribute", self.assert_has_attribute),
            ("assert_callable", self.assert_callable),
            
            # API assertions
            ("assert_status_code", self.assert_status_code),
            ("assert_response_time", self.assert_response_time),
            ("assert_json_structure", self.assert_json_structure),
            ("assert_headers_contain", self.assert_headers_contain),
            
            # Performance assertions
            ("assert_execution_time", self.assert_execution_time),
            ("assert_memory_usage", self.assert_memory_usage),
            ("assert_cpu_usage", self.assert_cpu_usage),
            
            # Business logic assertions
            ("assert_business_rule", self.assert_business_rule),
            ("assert_data_consistency", self.assert_data_consistency),
            ("assert_state_transition", self.assert_state_transition),
            
            # AI/ML assertions
            ("assert_model_accuracy", self.assert_model_accuracy),
            ("assert_prediction_confidence", self.assert_prediction_confidence),
            ("assert_feature_importance", self.assert_feature_importance),
            
            # Security assertions
            ("assert_no_sql_injection", self.assert_no_sql_injection),
            ("assert_secure_headers", self.assert_secure_headers),
            ("assert_password_strength", self.assert_password_strength)
        ]
        
        for name, method in assertions:
            self.assertion_registry[name] = method

    def _get_context(self) -> AssertionContext:
        """Get current execution context"""
        frame = inspect.currentframe()
        
        # Go up the stack to find the test function
        test_frame = frame
        while test_frame:
            test_frame = test_frame.f_back
            if test_frame and test_frame.f_code.co_name.startswith('test_'):
                break
        
        if test_frame:
            return AssertionContext(
                test_name=test_frame.f_code.co_name,
                test_file=test_frame.f_code.co_filename,
                line_number=test_frame.f_lineno,
                function_name=test_frame.f_code.co_name,
                parameters=test_frame.f_locals.copy()
            )
        else:
            return AssertionContext(
                test_name="unknown",
                test_file="unknown",
                line_number=0,
                function_name="unknown"
            )

    def _create_result(
        self,
        assertion_type: AssertionType,
        passed: bool,
        message: str,
        expected: Any = None,
        actual: Any = None,
        severity: AssertionSeverity = AssertionSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ) -> AssertionResult:
        """Create assertion result"""
        return AssertionResult(
            assertion_type=assertion_type,
            severity=severity,
            passed=passed,
            message=message,
            expected=expected,
            actual=actual,
            details=details or {},
            suggestions=suggestions or []
        )

    def _handle_result(self, result: AssertionResult, raise_on_fail: bool = True):
        """Handle assertion result"""
        # Store result in history
        self.results_history.append(result)
        
        # Log result
        if result.passed:
            self.logger.debug(f"✓ {result.message}")
        else:
            self.logger.error(f"✗ {result.message}")
            if result.details:
                self.logger.error(f"  Details: {result.details}")
        
        # Raise exception if failed and required
        if not result.passed and raise_on_fail:
            context = self._get_context()
            raise AssertionError(result, context)

    # Basic Assertions
    def assert_true(self, value: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that value is True"""
        passed = bool(value) is True
        msg = message or f"Expected True, got {value}"
        
        result = self._create_result(
            AssertionType.BASIC, passed, msg, True, value, severity
        )
        self._handle_result(result)

    def assert_false(self, value: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that value is False"""
        passed = bool(value) is False
        msg = message or f"Expected False, got {value}"
        
        result = self._create_result(
            AssertionType.BASIC, passed, msg, False, value, severity
        )
        self._handle_result(result)

    def assert_equal(self, actual: Any, expected: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that two values are equal"""
        passed = actual == expected
        msg = message or f"Expected {expected}, got {actual}"
        
        suggestions = []
        if not passed:
            if isinstance(actual, str) and isinstance(expected, str):
                # Provide diff for strings
                diff = '\n'.join(difflib.unified_diff(
                    expected.splitlines(), actual.splitlines(),
                    lineterm='', fromfile='expected', tofile='actual'
                ))
                suggestions.append(f"String diff:\n{diff}")
        
        result = self._create_result(
            AssertionType.BASIC, passed, msg, expected, actual, severity,
            suggestions=suggestions
        )
        self._handle_result(result)

    def assert_not_equal(self, actual: Any, expected: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that two values are not equal"""
        passed = actual != expected
        msg = message or f"Expected values to be different, both are {actual}"
        
        result = self._create_result(
            AssertionType.BASIC, passed, msg, f"!= {expected}", actual, severity
        )
        self._handle_result(result)

    def assert_none(self, value: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that value is None"""
        passed = value is None
        msg = message or f"Expected None, got {value}"
        
        result = self._create_result(
            AssertionType.BASIC, passed, msg, None, value, severity
        )
        self._handle_result(result)

    def assert_not_none(self, value: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that value is not None"""
        passed = value is not None
        msg = message or "Expected non-None value, got None"
        
        result = self._create_result(
            AssertionType.BASIC, passed, msg, "not None", value, severity
        )
        self._handle_result(result)

    # Numeric Assertions
    def assert_greater(self, actual: Union[int, float], expected: Union[int, float], message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that actual > expected"""
        passed = actual > expected
        msg = message or f"Expected {actual} > {expected}"
        
        result = self._create_result(
            AssertionType.NUMERIC, passed, msg, f"> {expected}", actual, severity
        )
        self._handle_result(result)

    def assert_greater_equal(self, actual: Union[int, float], expected: Union[int, float], message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that actual >= expected"""
        passed = actual >= expected
        msg = message or f"Expected {actual} >= {expected}"
        
        result = self._create_result(
            AssertionType.NUMERIC, passed, msg, f">= {expected}", actual, severity
        )
        self._handle_result(result)

    def assert_less(self, actual: Union[int, float], expected: Union[int, float], message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that actual < expected"""
        passed = actual < expected
        msg = message or f"Expected {actual} < {expected}"
        
        result = self._create_result(
            AssertionType.NUMERIC, passed, msg, f"< {expected}", actual, severity
        )
        self._handle_result(result)

    def assert_less_equal(self, actual: Union[int, float], expected: Union[int, float], message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that actual <= expected"""
        passed = actual <= expected
        msg = message or f"Expected {actual} <= {expected}"
        
        result = self._create_result(
            AssertionType.NUMERIC, passed, msg, f"<= {expected}", actual, severity
        )
        self._handle_result(result)

    def assert_almost_equal(self, actual: Union[int, float], expected: Union[int, float], tolerance: Optional[float] = None, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that two numeric values are almost equal within tolerance"""
        tol = tolerance or self.numeric_tolerance
        passed = abs(actual - expected) <= tol
        msg = message or f"Expected {actual} ≈ {expected} (tolerance: {tol})"
        
        details = {
            "tolerance": tol,
            "difference": abs(actual - expected)
        }
        
        result = self._create_result(
            AssertionType.NUMERIC, passed, msg, expected, actual, severity, details
        )
        self._handle_result(result)

    def assert_in_range(self, actual: Union[int, float], min_val: Union[int, float], max_val: Union[int, float], message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that value is within range [min_val, max_val]"""
        passed = min_val <= actual <= max_val
        msg = message or f"Expected {actual} to be in range [{min_val}, {max_val}]"
        
        result = self._create_result(
            AssertionType.NUMERIC, passed, msg, f"[{min_val}, {max_val}]", actual, severity
        )
        self._handle_result(result)

    # String Assertions
    def assert_string_contains(self, haystack: str, needle: str, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that string contains substring"""
        passed = needle in haystack
        msg = message or f"Expected '{haystack}' to contain '{needle}'"
        
        result = self._create_result(
            AssertionType.STRING, passed, msg, f"contains '{needle}'", haystack, severity
        )
        self._handle_result(result)

    def assert_string_starts_with(self, text: str, prefix: str, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that string starts with prefix"""
        passed = text.startswith(prefix)
        msg = message or f"Expected '{text}' to start with '{prefix}'"
        
        result = self._create_result(
            AssertionType.STRING, passed, msg, f"starts with '{prefix}'", text, severity
        )
        self._handle_result(result)

    def assert_string_ends_with(self, text: str, suffix: str, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that string ends with suffix"""
        passed = text.endswith(suffix)
        msg = message or f"Expected '{text}' to end with '{suffix}'"
        
        result = self._create_result(
            AssertionType.STRING, passed, msg, f"ends with '{suffix}'", text, severity
        )
        self._handle_result(result)

    def assert_regex_match(self, text: str, pattern: str, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that string matches regex pattern"""
        passed = bool(re.search(pattern, text))
        msg = message or f"Expected '{text}' to match pattern '{pattern}'"
        
        result = self._create_result(
            AssertionType.STRING, passed, msg, f"matches /{pattern}/", text, severity
        )
        self._handle_result(result)

    def assert_string_length(self, text: str, expected_length: int, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert string has expected length"""
        actual_length = len(text)
        passed = actual_length == expected_length
        msg = message or f"Expected string length {expected_length}, got {actual_length}"
        
        result = self._create_result(
            AssertionType.STRING, passed, msg, expected_length, actual_length, severity
        )
        self._handle_result(result)

    # Collection Assertions
    def assert_in(self, item: Any, collection: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that item is in collection"""
        passed = item in collection
        msg = message or f"Expected {item} to be in {collection}"
        
        result = self._create_result(
            AssertionType.COLLECTION, passed, msg, f"in {collection}", item, severity
        )
        self._handle_result(result)

    def assert_not_in(self, item: Any, collection: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that item is not in collection"""
        passed = item not in collection
        msg = message or f"Expected {item} not to be in {collection}"
        
        result = self._create_result(
            AssertionType.COLLECTION, passed, msg, f"not in {collection}", item, severity
        )
        self._handle_result(result)

    def assert_empty(self, collection: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that collection is empty"""
        passed = len(collection) == 0
        msg = message or f"Expected empty collection, got {len(collection)} items"
        
        result = self._create_result(
            AssertionType.COLLECTION, passed, msg, "empty", len(collection), severity
        )
        self._handle_result(result)

    def assert_not_empty(self, collection: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that collection is not empty"""
        passed = len(collection) > 0
        msg = message or "Expected non-empty collection, got empty collection"
        
        result = self._create_result(
            AssertionType.COLLECTION, passed, msg, "not empty", len(collection), severity
        )
        self._handle_result(result)

    def assert_length(self, collection: Any, expected_length: int, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert collection has expected length"""
        actual_length = len(collection)
        passed = actual_length == expected_length
        msg = message or f"Expected length {expected_length}, got {actual_length}"
        
        result = self._create_result(
            AssertionType.COLLECTION, passed, msg, expected_length, actual_length, severity
        )
        self._handle_result(result)

    def assert_contains_all(self, collection: Any, items: List[Any], message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that collection contains all specified items"""
        missing_items = [item for item in items if item not in collection]
        passed = len(missing_items) == 0
        msg = message or f"Collection missing items: {missing_items}"
        
        result = self._create_result(
            AssertionType.COLLECTION, passed, msg, f"contains all {items}", collection, severity,
            details={"missing_items": missing_items}
        )
        self._handle_result(result)

    def assert_subset(self, subset: Any, superset: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that subset is a subset of superset"""
        passed = set(subset).issubset(set(superset))
        msg = message or f"Expected {subset} to be subset of {superset}"
        
        result = self._create_result(
            AssertionType.COLLECTION, passed, msg, f"subset of {superset}", subset, severity
        )
        self._handle_result(result)

    # Object Assertions
    def assert_instance(self, obj: Any, expected_type: Type, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that object is instance of expected type"""
        passed = isinstance(obj, expected_type)
        actual_type = type(obj).__name__
        expected_type_name = expected_type.__name__
        msg = message or f"Expected instance of {expected_type_name}, got {actual_type}"
        
        result = self._create_result(
            AssertionType.OBJECT, passed, msg, expected_type_name, actual_type, severity
        )
        self._handle_result(result)

    def assert_has_attribute(self, obj: Any, attribute: str, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that object has specified attribute"""
        passed = hasattr(obj, attribute)
        msg = message or f"Expected object to have attribute '{attribute}'"
        
        result = self._create_result(
            AssertionType.OBJECT, passed, msg, f"has attribute '{attribute}'", obj, severity
        )
        self._handle_result(result)

    def assert_callable(self, obj: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert that object is callable"""
        passed = callable(obj)
        msg = message or f"Expected {obj} to be callable"
        
        result = self._create_result(
            AssertionType.OBJECT, passed, msg, "callable", obj, severity
        )
        self._handle_result(result)

    # API Assertions
    def assert_status_code(self, response: Any, expected_status: int, message: str = "", severity: AssertionSeverity = AssertionSeverity.HIGH):
        """Assert HTTP response status code"""
        actual_status = getattr(response, 'status_code', None)
        passed = actual_status == expected_status
        msg = message or f"Expected status {expected_status}, got {actual_status}"
        
        result = self._create_result(
            AssertionType.API, passed, msg, expected_status, actual_status, severity
        )
        self._handle_result(result)

    def assert_response_time(self, response_time: float, max_time: float, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert API response time is within limit"""
        passed = response_time <= max_time
        msg = message or f"Response time {response_time:.3f}s exceeded limit {max_time}s"
        
        result = self._create_result(
            AssertionType.PERFORMANCE, passed, msg, f"<= {max_time}s", f"{response_time:.3f}s", severity
        )
        self._handle_result(result)

    def assert_json_structure(self, json_data: Dict[str, Any], expected_keys: List[str], message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert JSON contains expected keys"""
        missing_keys = [key for key in expected_keys if key not in json_data]
        passed = len(missing_keys) == 0
        msg = message or f"JSON missing keys: {missing_keys}"
        
        result = self._create_result(
            AssertionType.API, passed, msg, expected_keys, list(json_data.keys()), severity,
            details={"missing_keys": missing_keys}
        )
        self._handle_result(result)

    def assert_headers_contain(self, headers: Dict[str, str], expected_headers: Dict[str, str], message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert response headers contain expected values"""
        missing_headers = {}
        for key, value in expected_headers.items():
            if key not in headers or headers[key] != value:
                missing_headers[key] = value
        
        passed = len(missing_headers) == 0
        msg = message or f"Headers missing or incorrect: {missing_headers}"
        
        result = self._create_result(
            AssertionType.API, passed, msg, expected_headers, headers, severity,
            details={"missing_headers": missing_headers}
        )
        self._handle_result(result)

    # Performance Assertions
    def assert_execution_time(self, execution_time: float, max_time: float, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert execution time is within limit"""
        passed = execution_time <= max_time
        msg = message or f"Execution time {execution_time:.3f}s exceeded limit {max_time}s"
        
        result = self._create_result(
            AssertionType.PERFORMANCE, passed, msg, f"<= {max_time}s", f"{execution_time:.3f}s", severity
        )
        self._handle_result(result)

    def assert_memory_usage(self, memory_mb: float, max_memory_mb: float, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert memory usage is within limit"""
        passed = memory_mb <= max_memory_mb
        msg = message or f"Memory usage {memory_mb:.1f}MB exceeded limit {max_memory_mb}MB"
        
        result = self._create_result(
            AssertionType.PERFORMANCE, passed, msg, f"<= {max_memory_mb}MB", f"{memory_mb:.1f}MB", severity
        )
        self._handle_result(result)

    def assert_cpu_usage(self, cpu_percent: float, max_cpu_percent: float, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert CPU usage is within limit"""
        passed = cpu_percent <= max_cpu_percent
        msg = message or f"CPU usage {cpu_percent:.1f}% exceeded limit {max_cpu_percent}%"
        
        result = self._create_result(
            AssertionType.PERFORMANCE, passed, msg, f"<= {max_cpu_percent}%", f"{cpu_percent:.1f}%", severity
        )
        self._handle_result(result)

    # Business Logic Assertions
    def assert_business_rule(self, rule_func: Callable, data: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.HIGH):
        """Assert business rule is satisfied"""
        try:
            passed = rule_func(data)
            msg = message or f"Business rule validation: {rule_func.__name__}"
        except Exception as e:
            passed = False
            msg = message or f"Business rule failed: {e}"
        
        result = self._create_result(
            AssertionType.BUSINESS_LOGIC, passed, msg, "business rule satisfied", data, severity
        )
        self._handle_result(result)

    def assert_data_consistency(self, data1: Any, data2: Any, consistency_func: Callable, message: str = "", severity: AssertionSeverity = AssertionSeverity.HIGH):
        """Assert data consistency between two datasets"""
        try:
            passed = consistency_func(data1, data2)
            msg = message or "Data consistency check passed"
        except Exception as e:
            passed = False
            msg = message or f"Data consistency check failed: {e}"
        
        result = self._create_result(
            AssertionType.BUSINESS_LOGIC, passed, msg, "consistent data", [data1, data2], severity
        )
        self._handle_result(result)

    def assert_state_transition(self, from_state: str, to_state: str, valid_transitions: Dict[str, List[str]], message: str = "", severity: AssertionSeverity = AssertionSeverity.HIGH):
        """Assert state transition is valid"""
        passed = from_state in valid_transitions and to_state in valid_transitions[from_state]
        msg = message or f"Invalid state transition: {from_state} -> {to_state}"
        
        result = self._create_result(
            AssertionType.BUSINESS_LOGIC, passed, msg, f"{from_state} -> {to_state}", valid_transitions.get(from_state, []), severity
        )
        self._handle_result(result)

    # AI/ML Assertions
    def assert_model_accuracy(self, accuracy: float, min_accuracy: float, message: str = "", severity: AssertionSeverity = AssertionSeverity.HIGH):
        """Assert model accuracy meets minimum threshold"""
        passed = accuracy >= min_accuracy
        msg = message or f"Model accuracy {accuracy:.3f} below threshold {min_accuracy:.3f}"
        
        result = self._create_result(
            AssertionType.AI_MODEL, passed, msg, f">= {min_accuracy:.3f}", f"{accuracy:.3f}", severity
        )
        self._handle_result(result)

    def assert_prediction_confidence(self, confidence: float, min_confidence: float, message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert prediction confidence meets minimum threshold"""
        passed = confidence >= min_confidence
        msg = message or f"Prediction confidence {confidence:.3f} below threshold {min_confidence:.3f}"
        
        result = self._create_result(
            AssertionType.AI_MODEL, passed, msg, f">= {min_confidence:.3f}", f"{confidence:.3f}", severity
        )
        self._handle_result(result)

    def assert_feature_importance(self, feature_importance: Dict[str, float], expected_features: List[str], message: str = "", severity: AssertionSeverity = AssertionSeverity.MEDIUM):
        """Assert important features are present"""
        missing_features = [feature for feature in expected_features if feature not in feature_importance]
        passed = len(missing_features) == 0
        msg = message or f"Missing important features: {missing_features}"
        
        result = self._create_result(
            AssertionType.AI_MODEL, passed, msg, expected_features, list(feature_importance.keys()), severity,
            details={"missing_features": missing_features}
        )
        self._handle_result(result)

    # Security Assertions
    def assert_no_sql_injection(self, query: str, message: str = "", severity: AssertionSeverity = AssertionSeverity.CRITICAL):
        """Assert query doesn't contain SQL injection patterns"""
        injection_patterns = [
            r"'\s*OR\s+'",
            r"'\s*UNION\s+SELECT",
            r"'\s*DROP\s+TABLE",
            r"'\s*DELETE\s+FROM",
            r"'\s*INSERT\s+INTO",
            r"--\s*$",
            r"/\*.*\*/"
        ]
        
        passed = True
        found_patterns = []
        
        for pattern in injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                passed = False
                found_patterns.append(pattern)
        
        msg = message or f"SQL injection patterns detected: {found_patterns}"
        
        result = self._create_result(
            AssertionType.SECURITY, passed, msg, "no injection patterns", query, severity,
            details={"found_patterns": found_patterns}
        )
        self._handle_result(result)

    def assert_secure_headers(self, headers: Dict[str, str], message: str = "", severity: AssertionSeverity = AssertionSeverity.HIGH):
        """Assert security headers are present"""
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        missing_headers = [header for header in required_headers if header not in headers]
        passed = len(missing_headers) == 0
        msg = message or f"Missing security headers: {missing_headers}"
        
        result = self._create_result(
            AssertionType.SECURITY, passed, msg, required_headers, list(headers.keys()), severity,
            details={"missing_headers": missing_headers}
        )
        self._handle_result(result)

    def assert_password_strength(self, password: str, min_length: int = 8, message: str = "", severity: AssertionSeverity = AssertionSeverity.HIGH):
        """Assert password meets strength requirements"""
        issues = []
        
        if len(password) < min_length:
            issues.append(f"Too short (minimum {min_length} characters)")
        
        if not re.search(r'[A-Z]', password):
            issues.append("No uppercase letters")
        
        if not re.search(r'[a-z]', password):
            issues.append("No lowercase letters")
        
        if not re.search(r'\d', password):
            issues.append("No digits")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\?]', password):
            issues.append("No special characters")
        
        passed = len(issues) == 0
        msg = message or f"Password strength issues: {issues}"
        
        result = self._create_result(
            AssertionType.SECURITY, passed, msg, "strong password", "weak password", severity,
            details={"issues": issues}
        )
        self._handle_result(result)

    # Utility Methods
    def register_custom_assertion(self, name: str, assertion_func: Callable):
        """Register custom assertion function"""
        self.assertion_registry[name] = assertion_func
        self.logger.info(f"Registered custom assertion: {name}")

    def get_assertion_stats(self) -> Dict[str, Any]:
        """Get statistics about assertion results"""
        if not self.results_history:
            return {"total": 0}
        
        total = len(self.results_history)
        passed = len([r for r in self.results_history if r.passed])
        failed = total - passed
        
        by_type = {}
        by_severity = {}
        
        for result in self.results_history:
            # Count by type
            type_name = result.assertion_type.value
            if type_name not in by_type:
                by_type[type_name] = {"total": 0, "passed": 0, "failed": 0}
            by_type[type_name]["total"] += 1
            if result.passed:
                by_type[type_name]["passed"] += 1
            else:
                by_type[type_name]["failed"] += 1
            
            # Count by severity
            severity_name = result.severity.value
            if severity_name not in by_severity:
                by_severity[severity_name] = {"total": 0, "passed": 0, "failed": 0}
            by_severity[severity_name]["total"] += 1
            if result.passed:
                by_severity[severity_name]["passed"] += 1
            else:
                by_severity[severity_name]["failed"] += 1
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total) * 100 if total > 0 else 0,
            "by_type": by_type,
            "by_severity": by_severity
        }

# Global assertion engine instance
assertion_engine = EnterpriseAssertionEngine()

__all__ = [
    "EnterpriseAssertionEngine",
    "AssertionResult",
    "AssertionContext",
    "AssertionError",
    "AssertionType",
    "AssertionSeverity",
    "assertion_engine"
]