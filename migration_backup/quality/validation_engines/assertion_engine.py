"""⚡ Assertion Engine - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + TESTING_ARCHITECT + SOFTWARE_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Enterprise-grade assertion engine with custom assertions, enhanced error reporting,
and intelligent test failure analysis for the AI content protection platform.
================================================================
"""

import inspect
import json
import logging
import re
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import traceback

logger = logging.getLogger(__name__)

class AssertionSeverity(Enum):
    """Assertion failure severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AssertionCategory(Enum):
    """Categories of assertions"""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DATA_INTEGRITY = "data_integrity"
    API_CONTRACT = "api_contract"
    BUSINESS_LOGIC = "business_logic"
    AI_MODEL = "ai_model"
    CONTENT_PROTECTION = "content_protection"

@dataclass
class AssertionResult:
    """Result of an assertion execution"""
    passed: bool
    assertion_name: str
    category: AssertionCategory
    severity: AssertionSeverity
    message: str
    expected: Any = None
    actual: Any = None
    execution_time: float = 0.0
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AssertionGroup:
    """Group of related assertions"""
    name: str
    description: str
    assertions: List[AssertionResult] = field(default_factory=list)
    setup_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None

class AssertionError(Exception):
    """Custom assertion error with enhanced information"""
    
    def __init__(self, message: str, result: AssertionResult):
        super().__init__(message)
        self.result = result

class AssertionEngine:
    """
    Enterprise assertion engine with enhanced capabilities
    """
    
    def __init__(self):
        """Initialize assertion engine"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.assertion_history: List[AssertionResult] = []
        self.assertion_groups: Dict[str, AssertionGroup] = {}
        self.custom_assertions: Dict[str, Callable] = {}
        self.context_stack: List[Dict[str, Any]] = []
        
        # Register built-in assertions
        self._register_builtin_assertions()

    def _register_builtin_assertions(self):
        """Register built-in assertion methods"""
        # Core assertions
        self.custom_assertions["assert_equal"] = self._assert_equal
        self.custom_assertions["assert_not_equal"] = self._assert_not_equal
        self.custom_assertions["assert_true"] = self._assert_true
        self.custom_assertions["assert_false"] = self._assert_false
        self.custom_assertions["assert_none"] = self._assert_none
        self.custom_assertions["assert_not_none"] = self._assert_not_none
        
        # Collection assertions
        self.custom_assertions["assert_in"] = self._assert_in
        self.custom_assertions["assert_not_in"] = self._assert_not_in
        self.custom_assertions["assert_contains"] = self._assert_contains
        self.custom_assertions["assert_length"] = self._assert_length
        self.custom_assertions["assert_empty"] = self._assert_empty
        self.custom_assertions["assert_not_empty"] = self._assert_not_empty
        
        # Numeric assertions
        self.custom_assertions["assert_greater"] = self._assert_greater
        self.custom_assertions["assert_greater_equal"] = self._assert_greater_equal
        self.custom_assertions["assert_less"] = self._assert_less
        self.custom_assertions["assert_less_equal"] = self._assert_less_equal
        self.custom_assertions["assert_between"] = self._assert_between
        
        # String assertions
        self.custom_assertions["assert_regex"] = self._assert_regex
        self.custom_assertions["assert_starts_with"] = self._assert_starts_with
        self.custom_assertions["assert_ends_with"] = self._assert_ends_with
        
        # Type assertions
        self.custom_assertions["assert_instance"] = self._assert_instance
        self.custom_assertions["assert_type"] = self._assert_type
        
        # Exception assertions
        self.custom_assertions["assert_raises"] = self._assert_raises
        self.custom_assertions["assert_not_raises"] = self._assert_not_raises
        
        # Performance assertions
        self.custom_assertions["assert_execution_time"] = self._assert_execution_time
        
        # API assertions
        self.custom_assertions["assert_http_status"] = self._assert_http_status
        self.custom_assertions["assert_json_schema"] = self._assert_json_schema
        
        # AI/Content protection specific assertions
        self.custom_assertions["assert_content_protected"] = self._assert_content_protected
        self.custom_assertions["assert_ai_confidence"] = self._assert_ai_confidence
        self.custom_assertions["assert_detection_accuracy"] = self._assert_detection_accuracy

    def create_assertion_group(
        self, 
        name: str, 
        description: str,
        setup_function: Optional[Callable] = None,
        teardown_function: Optional[Callable] = None
    ) -> AssertionGroup:
        """Create a new assertion group"""
        group = AssertionGroup(
            name=name,
            description=description,
            setup_function=setup_function,
            teardown_function=teardown_function
        )
        self.assertion_groups[name] = group
        return group

    def with_context(self, **context):
        """Context manager for adding context to assertions"""
        class ContextManager:
            def __init__(self, engine, context_data):
                self.engine = engine
                self.context_data = context_data
            
            def __enter__(self):
                self.engine.context_stack.append(self.context_data)
                return self.engine
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.engine.context_stack:
                    self.engine.context_stack.pop()
        
        return ContextManager(self, context)

    def _get_current_context(self) -> Dict[str, Any]:
        """Get current assertion context"""
        context = {}
        for ctx in self.context_stack:
            context.update(ctx)
        return context

    def _execute_assertion(
        self,
        assertion_func: Callable,
        assertion_name: str,
        category: AssertionCategory,
        severity: AssertionSeverity,
        *args,
        **kwargs
    ) -> AssertionResult:
        """Execute an assertion and capture result"""
        start_time = time.time()
        context = self._get_current_context()
        
        try:
            result = assertion_func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            assertion_result = AssertionResult(
                passed=True,
                assertion_name=assertion_name,
                category=category,
                severity=severity,
                message=f"Assertion '{assertion_name}' passed",
                execution_time=execution_time,
                context=context
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            assertion_result = AssertionResult(
                passed=False,
                assertion_name=assertion_name,
                category=category,
                severity=severity,
                message=str(e),
                execution_time=execution_time,
                stack_trace=traceback.format_exc(),
                context=context
            )
        
        # Store in history
        self.assertion_history.append(assertion_result)
        
        return assertion_result

    # Core assertion implementations
    def _assert_equal(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Assert that two values are equal"""
        if actual != expected:
            raise AssertionError(
                message or f"Expected {expected}, but got {actual}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_equal",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.HIGH,
                    message=message or f"Expected {expected}, but got {actual}",
                    expected=expected,
                    actual=actual
                )
            )
        return True

    def _assert_not_equal(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Assert that two values are not equal"""
        if actual == expected:
            raise AssertionError(
                message or f"Expected {actual} to not equal {expected}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_not_equal",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected {actual} to not equal {expected}",
                    expected=expected,
                    actual=actual
                )
            )
        return True

    def _assert_true(self, value: Any, message: str = "") -> bool:
        """Assert that value is True"""
        if not value:
            raise AssertionError(
                message or f"Expected True, but got {value}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_true",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.HIGH,
                    message=message or f"Expected True, but got {value}",
                    expected=True,
                    actual=value
                )
            )
        return True

    def _assert_false(self, value: Any, message: str = "") -> bool:
        """Assert that value is False"""
        if value:
            raise AssertionError(
                message or f"Expected False, but got {value}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_false",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.HIGH,
                    message=message or f"Expected False, but got {value}",
                    expected=False,
                    actual=value
                )
            )
        return True

    def _assert_none(self, value: Any, message: str = "") -> bool:
        """Assert that value is None"""
        if value is not None:
            raise AssertionError(
                message or f"Expected None, but got {value}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_none",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected None, but got {value}",
                    expected=None,
                    actual=value
                )
            )
        return True

    def _assert_not_none(self, value: Any, message: str = "") -> bool:
        """Assert that value is not None"""
        if value is None:
            raise AssertionError(
                message or "Expected value to not be None",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_not_none",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.HIGH,
                    message=message or "Expected value to not be None",
                    expected="not None",
                    actual=None
                )
            )
        return True

    def _assert_in(self, item: Any, container: Any, message: str = "") -> bool:
        """Assert that item is in container"""
        if item not in container:
            raise AssertionError(
                message or f"Expected {item} to be in {container}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_in",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected {item} to be in {container}",
                    expected=f"{item} in container",
                    actual=container
                )
            )
        return True

    def _assert_not_in(self, item: Any, container: Any, message: str = "") -> bool:
        """Assert that item is not in container"""
        if item in container:
            raise AssertionError(
                message or f"Expected {item} to not be in {container}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_not_in",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected {item} to not be in {container}",
                    expected=f"{item} not in container",
                    actual=container
                )
            )
        return True

    def _assert_contains(self, container: Any, item: Any, message: str = "") -> bool:
        """Assert that container contains item"""
        return self._assert_in(item, container, message)

    def _assert_length(self, container: Any, expected_length: int, message: str = "") -> bool:
        """Assert container has expected length"""
        actual_length = len(container)
        if actual_length != expected_length:
            raise AssertionError(
                message or f"Expected length {expected_length}, but got {actual_length}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_length",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected length {expected_length}, but got {actual_length}",
                    expected=expected_length,
                    actual=actual_length
                )
            )
        return True

    def _assert_empty(self, container: Any, message: str = "") -> bool:
        """Assert that container is empty"""
        if len(container) != 0:
            raise AssertionError(
                message or f"Expected empty container, but got {len(container)} items",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_empty",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected empty container, but got {len(container)} items",
                    expected=0,
                    actual=len(container)
                )
            )
        return True

    def _assert_not_empty(self, container: Any, message: str = "") -> bool:
        """Assert that container is not empty"""
        if len(container) == 0:
            raise AssertionError(
                message or "Expected non-empty container",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_not_empty",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or "Expected non-empty container",
                    expected="> 0",
                    actual=0
                )
            )
        return True

    def _assert_greater(self, actual: Union[int, float], expected: Union[int, float], message: str = "") -> bool:
        """Assert that actual > expected"""
        if not actual > expected:
            raise AssertionError(
                message or f"Expected {actual} > {expected}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_greater",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected {actual} > {expected}",
                    expected=f"> {expected}",
                    actual=actual
                )
            )
        return True

    def _assert_greater_equal(self, actual: Union[int, float], expected: Union[int, float], message: str = "") -> bool:
        """Assert that actual >= expected"""
        if not actual >= expected:
            raise AssertionError(
                message or f"Expected {actual} >= {expected}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_greater_equal",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected {actual} >= {expected}",
                    expected=f">= {expected}",
                    actual=actual
                )
            )
        return True

    def _assert_less(self, actual: Union[int, float], expected: Union[int, float], message: str = "") -> bool:
        """Assert that actual < expected"""
        if not actual < expected:
            raise AssertionError(
                message or f"Expected {actual} < {expected}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_less",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected {actual} < {expected}",
                    expected=f"< {expected}",
                    actual=actual
                )
            )
        return True

    def _assert_less_equal(self, actual: Union[int, float], expected: Union[int, float], message: str = "") -> bool:
        """Assert that actual <= expected"""
        if not actual <= expected:
            raise AssertionError(
                message or f"Expected {actual} <= {expected}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_less_equal",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected {actual} <= {expected}",
                    expected=f"<= {expected}",
                    actual=actual
                )
            )
        return True

    def _assert_between(self, actual: Union[int, float], min_val: Union[int, float], max_val: Union[int, float], message: str = "") -> bool:
        """Assert that min_val <= actual <= max_val"""
        if not (min_val <= actual <= max_val):
            raise AssertionError(
                message or f"Expected {actual} to be between {min_val} and {max_val}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_between",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected {actual} to be between {min_val} and {max_val}",
                    expected=f"between {min_val} and {max_val}",
                    actual=actual
                )
            )
        return True

    def _assert_regex(self, text: str, pattern: str, message: str = "") -> bool:
        """Assert that text matches regex pattern"""
        if not re.search(pattern, text):
            raise AssertionError(
                message or f"Expected text to match pattern '{pattern}'",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_regex",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.MEDIUM,
                    message=message or f"Expected text to match pattern '{pattern}'",
                    expected=pattern,
                    actual=text
                )
            )
        return True

    def _assert_starts_with(self, text: str, prefix: str, message: str = "") -> bool:
        """Assert that text starts with prefix"""
        if not text.startswith(prefix):
            raise AssertionError(
                message or f"Expected text to start with '{prefix}'",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_starts_with",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.LOW,
                    message=message or f"Expected text to start with '{prefix}'",
                    expected=f"starts with '{prefix}'",
                    actual=text
                )
            )
        return True

    def _assert_ends_with(self, text: str, suffix: str, message: str = "") -> bool:
        """Assert that text ends with suffix"""
        if not text.endswith(suffix):
            raise AssertionError(
                message or f"Expected text to end with '{suffix}'",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_ends_with",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.LOW,
                    message=message or f"Expected text to end with '{suffix}'",
                    expected=f"ends with '{suffix}'",
                    actual=text
                )
            )
        return True

    def _assert_instance(self, obj: Any, cls: Type, message: str = "") -> bool:
        """Assert that obj is instance of cls"""
        if not isinstance(obj, cls):
            raise AssertionError(
                message or f"Expected instance of {cls.__name__}, but got {type(obj).__name__}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_instance",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.HIGH,
                    message=message or f"Expected instance of {cls.__name__}, but got {type(obj).__name__}",
                    expected=cls.__name__,
                    actual=type(obj).__name__
                )
            )
        return True

    def _assert_type(self, obj: Any, expected_type: Type, message: str = "") -> bool:
        """Assert that obj is exactly of expected_type"""
        if type(obj) is not expected_type:
            raise AssertionError(
                message or f"Expected type {expected_type.__name__}, but got {type(obj).__name__}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_type",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.HIGH,
                    message=message or f"Expected type {expected_type.__name__}, but got {type(obj).__name__}",
                    expected=expected_type.__name__,
                    actual=type(obj).__name__
                )
            )
        return True

    def _assert_raises(self, exception_class: Type[Exception], func: Callable, *args, **kwargs) -> bool:
        """Assert that function raises specified exception"""
        try:
            func(*args, **kwargs)
            raise AssertionError(
                f"Expected {exception_class.__name__} to be raised",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_raises",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.HIGH,
                    message=f"Expected {exception_class.__name__} to be raised",
                    expected=exception_class.__name__,
                    actual="No exception raised"
                )
            )
        except exception_class:
            return True
        except Exception as e:
            raise AssertionError(
                f"Expected {exception_class.__name__}, but got {type(e).__name__}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_raises",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.HIGH,
                    message=f"Expected {exception_class.__name__}, but got {type(e).__name__}",
                    expected=exception_class.__name__,
                    actual=type(e).__name__
                )
            )

    def _assert_not_raises(self, exception_class: Type[Exception], func: Callable, *args, **kwargs) -> bool:
        """Assert that function does not raise specified exception"""
        try:
            func(*args, **kwargs)
            return True
        except exception_class as e:
            raise AssertionError(
                f"Did not expect {exception_class.__name__} to be raised",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_not_raises",
                    category=AssertionCategory.FUNCTIONAL,
                    severity=AssertionSeverity.HIGH,
                    message=f"Did not expect {exception_class.__name__} to be raised: {e}",
                    expected="No exception",
                    actual=exception_class.__name__
                )
            )

    def _assert_execution_time(self, func: Callable, max_time: float, *args, **kwargs) -> bool:
        """Assert that function executes within specified time"""
        start_time = time.time()
        func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > max_time:
            raise AssertionError(
                f"Expected execution time <= {max_time}s, but took {execution_time:.3f}s",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_execution_time",
                    category=AssertionCategory.PERFORMANCE,
                    severity=AssertionSeverity.MEDIUM,
                    message=f"Expected execution time <= {max_time}s, but took {execution_time:.3f}s",
                    expected=f"<= {max_time}s",
                    actual=f"{execution_time:.3f}s"
                )
            )
        return True

    def _assert_http_status(self, response: Any, expected_status: int, message: str = "") -> bool:
        """Assert HTTP response status code"""
        actual_status = getattr(response, 'status_code', None)
        if actual_status != expected_status:
            raise AssertionError(
                message or f"Expected HTTP status {expected_status}, but got {actual_status}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_http_status",
                    category=AssertionCategory.API_CONTRACT,
                    severity=AssertionSeverity.HIGH,
                    message=message or f"Expected HTTP status {expected_status}, but got {actual_status}",
                    expected=expected_status,
                    actual=actual_status
                )
            )
        return True

    def _assert_json_schema(self, data: Dict, schema: Dict, message: str = "") -> bool:
        """Assert that data conforms to JSON schema"""
        # Simplified schema validation - in production would use jsonschema library
        try:
            import jsonschema
            jsonschema.validate(data, schema)
            return True
        except ImportError:
            # Fallback to basic validation
            required_fields = schema.get('required', [])
            for field in required_fields:
                if field not in data:
                    raise AssertionError(
                        message or f"Required field '{field}' missing from data",
                        AssertionResult(
                            passed=False,
                            assertion_name="assert_json_schema",
                            category=AssertionCategory.API_CONTRACT,
                            severity=AssertionSeverity.HIGH,
                            message=message or f"Required field '{field}' missing from data",
                            expected=f"Field '{field}' present",
                            actual="Field missing"
                        )
                    )
            return True
        except Exception as e:
            raise AssertionError(
                message or f"Schema validation failed: {e}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_json_schema",
                    category=AssertionCategory.API_CONTRACT,
                    severity=AssertionSeverity.HIGH,
                    message=message or f"Schema validation failed: {e}",
                    expected="Valid schema",
                    actual=str(e)
                )
            )

    # AI/Content protection specific assertions
    def _assert_content_protected(self, content_id: str, protection_level: str, message: str = "") -> bool:
        """Assert that content has specified protection level"""
        # This would integrate with the actual content protection system
        # For now, it's a placeholder
        if not content_id or not protection_level:
            raise AssertionError(
                message or f"Content {content_id} not properly protected with level {protection_level}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_content_protected",
                    category=AssertionCategory.CONTENT_PROTECTION,
                    severity=AssertionSeverity.CRITICAL,
                    message=message or f"Content {content_id} not properly protected with level {protection_level}",
                    expected=protection_level,
                    actual="No protection"
                )
            )
        return True

    def _assert_ai_confidence(self, prediction: Dict, min_confidence: float, message: str = "") -> bool:
        """Assert that AI prediction meets minimum confidence threshold"""
        confidence = prediction.get('confidence', 0.0)
        if confidence < min_confidence:
            raise AssertionError(
                message or f"AI confidence {confidence:.3f} below threshold {min_confidence:.3f}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_ai_confidence",
                    category=AssertionCategory.AI_MODEL,
                    severity=AssertionSeverity.HIGH,
                    message=message or f"AI confidence {confidence:.3f} below threshold {min_confidence:.3f}",
                    expected=f">= {min_confidence:.3f}",
                    actual=f"{confidence:.3f}"
                )
            )
        return True

    def _assert_detection_accuracy(self, results: List[Dict], expected_accuracy: float, message: str = "") -> bool:
        """Assert that detection accuracy meets expected threshold"""
        if not results:
            accuracy = 0.0
        else:
            correct = sum(1 for r in results if r.get('correct', False))
            accuracy = correct / len(results)
        
        if accuracy < expected_accuracy:
            raise AssertionError(
                message or f"Detection accuracy {accuracy:.3f} below expected {expected_accuracy:.3f}",
                AssertionResult(
                    passed=False,
                    assertion_name="assert_detection_accuracy",
                    category=AssertionCategory.AI_MODEL,
                    severity=AssertionSeverity.HIGH,
                    message=message or f"Detection accuracy {accuracy:.3f} below expected {expected_accuracy:.3f}",
                    expected=f">= {expected_accuracy:.3f}",
                    actual=f"{accuracy:.3f}"
                )
            )
        return True

    # Public assertion methods that use the engine
    def assert_equal(self, actual: Any, expected: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.HIGH, category: AssertionCategory = AssertionCategory.FUNCTIONAL) -> AssertionResult:
        """Public assert_equal method"""
        return self._execute_assertion(
            self._assert_equal, "assert_equal", category, severity, actual, expected, message
        )

    def assert_true(self, value: Any, message: str = "", severity: AssertionSeverity = AssertionSeverity.HIGH, category: AssertionCategory = AssertionCategory.FUNCTIONAL) -> AssertionResult:
        """Public assert_true method"""
        return self._execute_assertion(
            self._assert_true, "assert_true", category, severity, value, message
        )

    def assert_performance_time(self, func: Callable, max_time: float, *args, **kwargs) -> AssertionResult:
        """Assert function execution time"""
        return self._execute_assertion(
            self._assert_execution_time, "assert_execution_time", 
            AssertionCategory.PERFORMANCE, AssertionSeverity.MEDIUM,
            func, max_time, *args, **kwargs
        )

    def assert_api_status(self, response: Any, expected_status: int, message: str = "") -> AssertionResult:
        """Assert API response status"""
        return self._execute_assertion(
            self._assert_http_status, "assert_http_status",
            AssertionCategory.API_CONTRACT, AssertionSeverity.HIGH,
            response, expected_status, message
        )

    def generate_report(self, format: str = "json") -> str:
        """Generate assertion execution report"""
        if format == "json":
            return self._generate_json_report()
        elif format == "markdown":
            return self._generate_markdown_report()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_json_report(self) -> str:
        """Generate JSON report"""
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_assertions": len(self.assertion_history),
            "passed_assertions": len([a for a in self.assertion_history if a.passed]),
            "failed_assertions": len([a for a in self.assertion_history if not a.passed]),
            "assertions": [
                {
                    "name": a.assertion_name,
                    "passed": a.passed,
                    "category": a.category.value,
                    "severity": a.severity.value,
                    "message": a.message,
                    "execution_time": a.execution_time,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in self.assertion_history
            ]
        }
        return json.dumps(data, indent=2)

    def _generate_markdown_report(self) -> str:
        """Generate Markdown report"""
        total = len(self.assertion_history)
        passed = len([a for a in self.assertion_history if a.passed])
        failed = total - passed
        
        md = f"""# Assertion Execution Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Total Assertions | {total} |
| Passed | {passed} |
| Failed | {failed} |
| Success Rate | {(passed / total * 100) if total > 0 else 0:.1f}% |

## Failed Assertions

"""
        
        failed_assertions = [a for a in self.assertion_history if not a.passed]
        for assertion in failed_assertions:
            md += f"### {assertion.assertion_name} ({assertion.severity.value})\n"
            md += f"- **Category:** {assertion.category.value}\n"
            md += f"- **Message:** {assertion.message}\n"
            md += f"- **Expected:** {assertion.expected}\n"
            md += f"- **Actual:** {assertion.actual}\n\n"

        return md

    def register_custom_assertion(self, name: str, assertion_func: Callable):
        """Register a custom assertion function"""
        self.custom_assertions[name] = assertion_func
        self.logger.info(f"Registered custom assertion: {name}")

    def clear_history(self):
        """Clear assertion history"""
        self.assertion_history.clear()
        self.logger.info("Cleared assertion history")

# Global assertion engine instance
assertion_engine = AssertionEngine()

__all__ = [
    "AssertionEngine",
    "AssertionResult",
    "AssertionGroup", 
    "AssertionError",
    "AssertionSeverity",
    "AssertionCategory",
    "assertion_engine"
]