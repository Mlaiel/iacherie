"""🧪 Unit Test Orchestrator - Ainflue Platform
================================================================
Expert: LEAD_DEV_IA + QUALITY_ENGINEER + DEVOPS_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Central Unit-Test-Orchestrator für Mikroservices - coordinates
and manages unit testing across all platform microservices.
================================================================
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import importlib.util

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestPriority(Enum):
    """Test priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TestCase:
    """Individual test case definition"""
    name: str
    module: str
    file_path: str
    function_name: str
    priority: TestPriority
    tags: List[str]
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 30
    retry_count: int = 0
    status: TestStatus = TestStatus.PENDING
    execution_time: float = 0.0
    error_message: Optional[str] = None
    last_run: Optional[datetime] = None

@dataclass
class TestSuite:
    """Test suite containing multiple test cases"""
    name: str
    description: str
    test_cases: List[TestCase]
    setup_script: Optional[str] = None
    teardown_script: Optional[str] = None
    parallel_execution: bool = True
    max_workers: int = 4

@dataclass
class TestResult:
    """Test execution result"""
    test_case: TestCase
    status: TestStatus
    execution_time: float
    output: str
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    coverage_data: Optional[Dict[str, Any]] = None

@dataclass
class TestReport:
    """Comprehensive test report"""
    test_suite: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_time: float
    coverage_percentage: float
    results: List[TestResult]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class UnitTestOrchestrator:
    """
    Central orchestrator for unit testing across microservices
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize unit test orchestrator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_results: List[TestResult] = []
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        config_path = self.project_root / "config" / "testing.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load test config: {e}")
        
        return {
            "parallel_execution": True,
            "max_workers": 4,
            "default_timeout": 30,
            "coverage_threshold": 80.0,
            "retry_failed_tests": True,
            "test_patterns": ["test_*.py", "*_test.py"],
            "exclude_patterns": ["__pycache__", "*.pyc", ".pytest_cache"]
        }

    async def discover_tests(self, test_directory: Optional[str] = None) -> Dict[str, TestSuite]:
        """Discover all test cases in the project"""
        self.logger.info("Starting test discovery")
        test_dir = Path(test_directory or self.project_root / "tests")
        
        if not test_dir.exists():
            self.logger.warning(f"Test directory {test_dir} does not exist")
            return {}
        
        discovered_suites = {}
        
        # Find all test files
        test_files = []
        for pattern in self.config["test_patterns"]:
            test_files.extend(test_dir.rglob(pattern))
        
        # Filter out excluded files
        for exclude_pattern in self.config["exclude_patterns"]:
            test_files = [f for f in test_files if exclude_pattern not in str(f)]
        
        # Group test files by module/service
        for test_file in test_files:
            try:
                test_cases = await self._extract_test_cases(test_file)
                if test_cases:
                    # Determine suite name from file structure
                    relative_path = test_file.relative_to(test_dir)
                    suite_name = str(relative_path.parent).replace("/", "_") or "root"
                    
                    if suite_name not in discovered_suites:
                        discovered_suites[suite_name] = TestSuite(
                            name=suite_name,
                            description=f"Test suite for {suite_name}",
                            test_cases=[],
                            parallel_execution=self.config["parallel_execution"],
                            max_workers=self.config["max_workers"]
                        )
                    
                    discovered_suites[suite_name].test_cases.extend(test_cases)
                    
            except Exception as e:
                self.logger.error(f"Error discovering tests in {test_file}: {e}")
        
        self.test_suites.update(discovered_suites)
        total_tests = sum(len(suite.test_cases) for suite in discovered_suites.values())
        self.logger.info(f"Discovered {total_tests} tests in {len(discovered_suites)} suites")
        
        return discovered_suites

    async def _extract_test_cases(self, test_file: Path) -> List[TestCase]:
        """Extract test cases from a test file"""
        test_cases = []
        
        try:
            # Import the test module
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find test functions
                for name in dir(module):
                    if name.startswith('test_'):
                        func = getattr(module, name)
                        if callable(func):
                            test_case = TestCase(
                                name=name,
                                module=str(test_file.relative_to(self.project_root)),
                                file_path=str(test_file),
                                function_name=name,
                                priority=self._determine_test_priority(func),
                                tags=self._extract_test_tags(func),
                                timeout=self.config["default_timeout"]
                            )
                            test_cases.append(test_case)
                            
        except Exception as e:
            self.logger.error(f"Error extracting test cases from {test_file}: {e}")
        
        return test_cases

    def _determine_test_priority(self, test_func) -> TestPriority:
        """Determine test priority from function metadata"""
        # Check for priority markers in docstring or decorators
        if hasattr(test_func, '__doc__') and test_func.__doc__:
            doc = test_func.__doc__.lower()
            if 'critical' in doc or 'priority:critical' in doc:
                return TestPriority.CRITICAL
            elif 'high' in doc or 'priority:high' in doc:
                return TestPriority.HIGH
            elif 'low' in doc or 'priority:low' in doc:
                return TestPriority.LOW
        
        # Check function name for priority indicators
        func_name = test_func.__name__.lower()
        if 'critical' in func_name or 'essential' in func_name:
            return TestPriority.CRITICAL
        elif 'integration' in func_name or 'smoke' in func_name:
            return TestPriority.HIGH
        
        return TestPriority.MEDIUM

    def _extract_test_tags(self, test_func) -> List[str]:
        """Extract tags from test function"""
        tags = []
        
        # Check for pytest markers
        if hasattr(test_func, 'pytestmark'):
            for marker in test_func.pytestmark:
                tags.append(marker.name)
        
        # Check docstring for tags
        if hasattr(test_func, '__doc__') and test_func.__doc__:
            doc = test_func.__doc__
            import re
            tag_matches = re.findall(r'@tag\s*:\s*(\w+)', doc)
            tags.extend(tag_matches)
        
        return tags

    async def run_test_suite(self, suite_name: str, filters: Optional[Dict[str, Any]] = None) -> TestReport:
        """Run a specific test suite"""
        if suite_name not in self.test_suites:
            raise ValueError(f"Test suite '{suite_name}' not found")
        
        suite = self.test_suites[suite_name]
        self.logger.info(f"Running test suite: {suite_name}")
        
        # Filter test cases if filters provided
        test_cases = suite.test_cases
        if filters:
            test_cases = self._filter_test_cases(test_cases, filters)
        
        start_time = time.time()
        results = []
        
        # Run setup script if provided
        if suite.setup_script:
            await self._run_setup_script(suite.setup_script)
        
        try:
            if suite.parallel_execution and len(test_cases) > 1:
                # Run tests in parallel
                results = await self._run_tests_parallel(test_cases, suite.max_workers)
            else:
                # Run tests sequentially
                results = await self._run_tests_sequential(test_cases)
                
        finally:
            # Run teardown script if provided
            if suite.teardown_script:
                await self._run_teardown_script(suite.teardown_script)
        
        total_time = time.time() - start_time
        
        # Generate test report
        report = self._generate_test_report(suite_name, results, total_time)
        
        # Store results
        self.test_results.extend(results)
        
        self.logger.info(f"Test suite {suite_name} completed: {report.passed}/{report.total_tests} passed")
        return report

    async def _run_tests_parallel(self, test_cases: List[TestCase], max_workers: int) -> List[TestResult]:
        """Run test cases in parallel"""
        semaphore = asyncio.Semaphore(max_workers)
        
        async def run_single_test(test_case: TestCase) -> TestResult:
            async with semaphore:
                return await self._execute_test_case(test_case)
        
        tasks = [run_single_test(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error result
                error_result = TestResult(
                    test_case=test_cases[i],
                    status=TestStatus.ERROR,
                    execution_time=0.0,
                    output="",
                    error_message=str(result)
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
        
        return final_results

    async def _run_tests_sequential(self, test_cases: List[TestCase]) -> List[TestResult]:
        """Run test cases sequentially"""
        results = []
        for test_case in test_cases:
            result = await self._execute_test_case(test_case)
            results.append(result)
        
        return results

    async def _execute_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case"""
        self.logger.debug(f"Executing test: {test_case.name}")
        
        start_time = time.time()
        test_case.status = TestStatus.RUNNING
        test_case.last_run = datetime.utcnow()
        
        try:
            # Build pytest command
            cmd = [
                "python", "-m", "pytest",
                f"{test_case.file_path}::{test_case.function_name}",
                "-v", "--tb=short",
                f"--timeout={test_case.timeout}"
            ]
            
            # Add coverage if enabled
            if self.config.get("enable_coverage", True):
                cmd.extend(["--cov=.", "--cov-report=term-missing"])
            
            # Execute test
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=test_case.timeout + 10
            )
            
            execution_time = time.time() - start_time
            output = stdout.decode() + stderr.decode()
            
            # Determine test status
            if process.returncode == 0:
                status = TestStatus.PASSED
                error_message = None
            else:
                status = TestStatus.FAILED
                error_message = stderr.decode() if stderr else "Test failed"
            
            test_case.status = status
            test_case.execution_time = execution_time
            test_case.error_message = error_message
            
            return TestResult(
                test_case=test_case,
                status=status,
                execution_time=execution_time,
                output=output,
                error_message=error_message
            )
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            test_case.status = TestStatus.ERROR
            error_message = f"Test timed out after {test_case.timeout} seconds"
            
            return TestResult(
                test_case=test_case,
                status=TestStatus.ERROR,
                execution_time=execution_time,
                output="",
                error_message=error_message
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            test_case.status = TestStatus.ERROR
            error_message = str(e)
            
            return TestResult(
                test_case=test_case,
                status=TestStatus.ERROR,
                execution_time=execution_time,
                output="",
                error_message=error_message
            )

    def _filter_test_cases(self, test_cases: List[TestCase], filters: Dict[str, Any]) -> List[TestCase]:
        """Filter test cases based on criteria"""
        filtered = test_cases
        
        if 'priority' in filters:
            priority_filter = filters['priority']
            if isinstance(priority_filter, str):
                priority_filter = TestPriority(priority_filter)
            filtered = [tc for tc in filtered if tc.priority == priority_filter]
        
        if 'tags' in filters:
            required_tags = filters['tags']
            if isinstance(required_tags, str):
                required_tags = [required_tags]
            filtered = [tc for tc in filtered if any(tag in tc.tags for tag in required_tags)]
        
        if 'module' in filters:
            module_filter = filters['module']
            filtered = [tc for tc in filtered if module_filter in tc.module]
        
        return filtered

    async def _run_setup_script(self, script_path: str):
        """Run setup script before test execution"""
        try:
            self.logger.debug(f"Running setup script: {script_path}")
            result = await asyncio.create_subprocess_exec(
                "python", script_path,
                cwd=str(self.project_root)
            )
            await result.wait()
        except Exception as e:
            self.logger.error(f"Setup script failed: {e}")
            raise

    async def _run_teardown_script(self, script_path: str):
        """Run teardown script after test execution"""
        try:
            self.logger.debug(f"Running teardown script: {script_path}")
            result = await asyncio.create_subprocess_exec(
                "python", script_path,
                cwd=str(self.project_root)
            )
            await result.wait()
        except Exception as e:
            self.logger.warning(f"Teardown script failed: {e}")

    def _generate_test_report(self, suite_name: str, results: List[TestResult], total_time: float) -> TestReport:
        """Generate comprehensive test report"""
        total_tests = len(results)
        passed = len([r for r in results if r.status == TestStatus.PASSED])
        failed = len([r for r in results if r.status == TestStatus.FAILED])
        skipped = len([r for r in results if r.status == TestStatus.SKIPPED])
        errors = len([r for r in results if r.status == TestStatus.ERROR])
        
        # Calculate coverage (simplified)
        coverage_percentage = self._calculate_coverage(results)
        
        return TestReport(
            test_suite=suite_name,
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total_time=total_time,
            coverage_percentage=coverage_percentage,
            results=results
        )

    def _calculate_coverage(self, results: List[TestResult]) -> float:
        """Calculate test coverage percentage"""
        # Simplified coverage calculation
        # In a real implementation, this would parse coverage reports
        if not results:
            return 0.0
        
        passed_tests = len([r for r in results if r.status == TestStatus.PASSED])
        total_tests = len(results)
        
        return (passed_tests / total_tests) * 100.0 if total_tests > 0 else 0.0

    async def run_all_tests(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, TestReport]:
        """Run all discovered test suites"""
        self.logger.info("Running all test suites")
        
        if not self.test_suites:
            await self.discover_tests()
        
        reports = {}
        for suite_name in self.test_suites.keys():
            try:
                report = await self.run_test_suite(suite_name, filters)
                reports[suite_name] = report
            except Exception as e:
                self.logger.error(f"Error running test suite {suite_name}: {e}")
        
        return reports

    def export_report(self, reports: Dict[str, TestReport], format: str = "json") -> str:
        """Export test reports in specified format"""
        if format == "json":
            return self._export_json(reports)
        elif format == "html":
            return self._export_html(reports)
        elif format == "junit":
            return self._export_junit(reports)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_json(self, reports: Dict[str, TestReport]) -> str:
        """Export reports as JSON"""
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_suites": len(reports),
                "total_tests": sum(r.total_tests for r in reports.values()),
                "total_passed": sum(r.passed for r in reports.values()),
                "total_failed": sum(r.failed for r in reports.values()),
                "overall_success_rate": self._calculate_overall_success_rate(reports)
            },
            "suites": {
                name: {
                    "total_tests": report.total_tests,
                    "passed": report.passed,
                    "failed": report.failed,
                    "skipped": report.skipped,
                    "errors": report.errors,
                    "total_time": report.total_time,
                    "coverage_percentage": report.coverage_percentage,
                    "timestamp": report.timestamp.isoformat()
                }
                for name, report in reports.items()
            }
        }
        return json.dumps(data, indent=2)

    def _export_html(self, reports: Dict[str, TestReport]) -> str:
        """Export reports as HTML"""
        html = f"""
        <html>
        <head><title>Unit Test Report</title></head>
        <body>
        <h1>Unit Test Report</h1>
        <p><strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <h2>Summary</h2>
        <ul>
        <li>Total Suites: {len(reports)}</li>
        <li>Total Tests: {sum(r.total_tests for r in reports.values())}</li>
        <li>Success Rate: {self._calculate_overall_success_rate(reports):.1f}%</li>
        </ul>
        </body>
        </html>
        """
        return html

    def _export_junit(self, reports: Dict[str, TestReport]) -> str:
        """Export reports as JUnit XML"""
        # Simplified JUnit XML format
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<testsuites>\n'
        
        for name, report in reports.items():
            xml += f'  <testsuite name="{name}" tests="{report.total_tests}" '
            xml += f'failures="{report.failed}" errors="{report.errors}" '
            xml += f'time="{report.total_time:.2f}">\n'
            xml += '  </testsuite>\n'
        
        xml += '</testsuites>'
        return xml

    def _calculate_overall_success_rate(self, reports: Dict[str, TestReport]) -> float:
        """Calculate overall success rate across all suites"""
        total_tests = sum(r.total_tests for r in reports.values())
        total_passed = sum(r.passed for r in reports.values())
        
        return (total_passed / total_tests * 100.0) if total_tests > 0 else 0.0

# Global unit test orchestrator instance
unit_test_orchestrator = UnitTestOrchestrator()

__all__ = [
    "UnitTestOrchestrator",
    "TestCase",
    "TestSuite", 
    "TestResult",
    "TestReport",
    "TestStatus",
    "TestPriority",
    "unit_test_orchestrator"
]