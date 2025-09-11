"""🧪 Unit Test Orchestrator - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + DEVOPS_ENGINEER + BACKEND_SENIOR
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Central orchestrator for unit testing across all microservices and modules.
Provides intelligent test discovery, execution, and reporting capabilities.
================================================================
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"

class TestType(Enum):
    """Types of unit tests"""
    UNIT = "unit"
    INTEGRATION = "integration"
    COMPONENT = "component"
    CONTRACT = "contract"
    MUTATION = "mutation"

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    test_file: str
    test_class: Optional[str]
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    assertions: int = 0
    coverage: float = 0.0
    tags: List[str] = field(default_factory=list)

@dataclass
class TestSuite:
    """Test suite definition"""
    name: str
    path: str
    test_type: TestType
    pattern: str
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    parallel: bool = True
    retry_count: int = 0

@dataclass
class TestExecution:
    """Test execution summary"""
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    coverage: float
    results: List[TestResult]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class UnitTestOrchestrator:
    """
    Central orchestrator for unit testing across the platform
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize unit test orchestrator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.test_suites: List[TestSuite] = []
        self.execution_history: List[TestExecution] = []
        
        # Test discovery patterns
        self.test_patterns = [
            "test_*.py",
            "*_test.py", 
            "tests/*.py",
            "test/**/*.py"
        ]
        
        # Initialize default test suites
        self._discover_test_suites()

    def _discover_test_suites(self):
        """Discover test suites in the project"""
        self.test_suites = [
            TestSuite(
                name="Core Unit Tests",
                path="tests/unit",
                test_type=TestType.UNIT,
                pattern="test_*.py",
                timeout=120,
                parallel=True
            ),
            TestSuite(
                name="API Unit Tests", 
                path="tests/api",
                test_type=TestType.UNIT,
                pattern="test_api_*.py",
                timeout=180,
                parallel=True
            ),
            TestSuite(
                name="Service Unit Tests",
                path="tests/services",
                test_type=TestType.UNIT,
                pattern="test_*_service.py",
                timeout=150,
                parallel=True
            ),
            TestSuite(
                name="Model Unit Tests",
                path="tests/models",
                test_type=TestType.UNIT,
                pattern="test_*_model.py",
                timeout=90,
                parallel=True
            ),
            TestSuite(
                name="Quality Module Tests",
                path="tests/quality",
                test_type=TestType.UNIT,
                pattern="test_quality_*.py",
                timeout=240,
                parallel=True
            )
        ]

    async def run_all_tests(
        self, 
        include_coverage: bool = True,
        parallel: bool = True,
        fail_fast: bool = False
    ) -> Dict[str, TestExecution]:
        """Run all test suites"""
        self.logger.info("Starting comprehensive test execution")
        start_time = time.time()
        
        executions = {}
        
        if parallel:
            # Run test suites in parallel
            tasks = []
            for suite in self.test_suites:
                if suite.parallel:
                    task = self.run_test_suite(suite, include_coverage)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                suite = self.test_suites[i]
                if isinstance(result, Exception):
                    self.logger.error(f"Test suite {suite.name} failed: {result}")
                    executions[suite.name] = self._create_error_execution(suite, str(result))
                else:
                    executions[suite.name] = result
                    
                # Check fail fast
                if fail_fast and result and result.failed > 0:
                    self.logger.warning("Stopping execution due to test failures (fail_fast=True)")
                    break
        else:
            # Run test suites sequentially
            for suite in self.test_suites:
                try:
                    execution = await self.run_test_suite(suite, include_coverage)
                    executions[suite.name] = execution
                    
                    if fail_fast and execution.failed > 0:
                        self.logger.warning("Stopping execution due to test failures (fail_fast=True)")
                        break
                        
                except Exception as e:
                    self.logger.error(f"Test suite {suite.name} failed: {e}")
                    executions[suite.name] = self._create_error_execution(suite, str(e))
        
        total_time = time.time() - start_time
        self.logger.info(f"Test execution completed in {total_time:.2f} seconds")
        
        # Store execution history
        for execution in executions.values():
            if execution:
                self.execution_history.append(execution)
        
        return executions

    async def run_test_suite(
        self, 
        suite: TestSuite, 
        include_coverage: bool = True
    ) -> TestExecution:
        """Run a specific test suite"""
        self.logger.info(f"Running test suite: {suite.name}")
        start_time = time.time()
        
        # Check if test path exists
        test_path = self.project_root / suite.path
        if not test_path.exists():
            self.logger.warning(f"Test path {test_path} does not exist, creating...")
            test_path.mkdir(parents=True, exist_ok=True)
            # Create a basic __init__.py file
            (test_path / "__init__.py").touch()
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        # Add test path and pattern
        if test_path.exists():
            cmd.extend([str(test_path), "-k", suite.pattern.replace("*.py", "")])
        
        # Add coverage if requested
        if include_coverage:
            cmd.extend([
                "--cov=.",
                "--cov-report=xml:coverage.xml",
                "--cov-report=json:coverage.json"
            ])
        
        # Add output format
        cmd.extend([
            "--tb=short",
            "-v",
            "--junitxml=test_results.xml"
        ])
        
        # Add timeout
        if suite.timeout:
            cmd.extend(["--timeout", str(suite.timeout)])
        
        try:
            # Execute tests
            result = await self._run_command(cmd, timeout=suite.timeout + 60)
            
            # Parse results
            test_results = await self._parse_test_results()
            coverage = await self._parse_coverage() if include_coverage else 0.0
            
            # Create execution summary
            execution = TestExecution(
                suite_name=suite.name,
                total_tests=len(test_results),
                passed=len([r for r in test_results if r.status == TestStatus.PASSED]),
                failed=len([r for r in test_results if r.status == TestStatus.FAILED]),
                skipped=len([r for r in test_results if r.status == TestStatus.SKIPPED]),
                errors=len([r for r in test_results if r.status == TestStatus.ERROR]),
                duration=time.time() - start_time,
                coverage=coverage,
                results=test_results
            )
            
            self.logger.info(
                f"Suite {suite.name} completed: "
                f"{execution.passed} passed, {execution.failed} failed, "
                f"{execution.skipped} skipped, {execution.errors} errors"
            )
            
            return execution
            
        except Exception as e:
            self.logger.error(f"Error running test suite {suite.name}: {e}")
            return self._create_error_execution(suite, str(e))

    async def _run_command(self, cmd: List[str], timeout: int = 300) -> subprocess.CompletedProcess:
        """Run command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=process.returncode,
                stdout=stdout.decode() if stdout else "",
                stderr=stderr.decode() if stderr else ""
            )
            
        except asyncio.TimeoutError:
            self.logger.error(f"Command timed out: {' '.join(cmd)}")
            return subprocess.CompletedProcess(
                args=cmd, returncode=1, stdout="", stderr="Timeout"
            )
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return subprocess.CompletedProcess(
                args=cmd, returncode=1, stdout="", stderr=str(e)
            )

    async def _parse_test_results(self) -> List[TestResult]:
        """Parse test results from JUnit XML"""
        results = []
        xml_file = self.project_root / "test_results.xml"
        
        if not xml_file.exists():
            return results
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            for testcase in root.findall(".//testcase"):
                test_name = testcase.get("name", "")
                test_file = testcase.get("file", "")
                test_class = testcase.get("classname", "")
                duration = float(testcase.get("time", "0"))
                
                # Determine status
                status = TestStatus.PASSED
                error_message = None
                traceback = None
                
                failure = testcase.find("failure")
                error = testcase.find("error")
                skipped = testcase.find("skipped")
                
                if failure is not None:
                    status = TestStatus.FAILED
                    error_message = failure.get("message", "")
                    traceback = failure.text
                elif error is not None:
                    status = TestStatus.ERROR
                    error_message = error.get("message", "")
                    traceback = error.text
                elif skipped is not None:
                    status = TestStatus.SKIPPED
                    error_message = skipped.get("message", "")
                
                results.append(TestResult(
                    test_name=test_name,
                    test_file=test_file,
                    test_class=test_class,
                    status=status,
                    duration=duration,
                    error_message=error_message,
                    traceback=traceback
                ))
                
        except Exception as e:
            self.logger.error(f"Error parsing test results: {e}")
        
        return results

    async def _parse_coverage(self) -> float:
        """Parse coverage from JSON report"""
        coverage_file = self.project_root / "coverage.json"
        
        if not coverage_file.exists():
            return 0.0
        
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            
            return coverage_data.get("totals", {}).get("percent_covered", 0.0)
            
        except Exception as e:
            self.logger.error(f"Error parsing coverage: {e}")
            return 0.0

    def _create_error_execution(self, suite: TestSuite, error: str) -> TestExecution:
        """Create error execution result"""
        return TestExecution(
            suite_name=suite.name,
            total_tests=0,
            passed=0,
            failed=0,
            skipped=0,
            errors=1,
            duration=0.0,
            coverage=0.0,
            results=[TestResult(
                test_name="Suite Execution",
                test_file=suite.path,
                test_class=None,
                status=TestStatus.ERROR,
                duration=0.0,
                error_message=error
            )]
        )

    async def run_targeted_tests(
        self, 
        test_files: List[str],
        include_coverage: bool = True
    ) -> TestExecution:
        """Run specific test files"""
        self.logger.info(f"Running targeted tests: {test_files}")
        
        cmd = ["python", "-m", "pytest"]
        cmd.extend(test_files)
        
        if include_coverage:
            cmd.extend(["--cov=.", "--cov-report=json:coverage.json"])
        
        cmd.extend(["--tb=short", "-v", "--junitxml=test_results.xml"])
        
        try:
            result = await self._run_command(cmd, timeout=300)
            test_results = await self._parse_test_results()
            coverage = await self._parse_coverage() if include_coverage else 0.0
            
            return TestExecution(
                suite_name="Targeted Tests",
                total_tests=len(test_results),
                passed=len([r for r in test_results if r.status == TestStatus.PASSED]),
                failed=len([r for r in test_results if r.status == TestStatus.FAILED]),
                skipped=len([r for r in test_results if r.status == TestStatus.SKIPPED]),
                errors=len([r for r in test_results if r.status == TestStatus.ERROR]),
                duration=0.0,
                coverage=coverage,
                results=test_results
            )
            
        except Exception as e:
            self.logger.error(f"Error running targeted tests: {e}")
            return self._create_error_execution(
                TestSuite("Targeted", "", TestType.UNIT, ""), str(e)
            )

    def generate_test_report(self, executions: Dict[str, TestExecution]) -> str:
        """Generate comprehensive test report"""
        total_tests = sum(ex.total_tests for ex in executions.values() if ex)
        total_passed = sum(ex.passed for ex in executions.values() if ex)
        total_failed = sum(ex.failed for ex in executions.values() if ex)
        total_skipped = sum(ex.skipped for ex in executions.values() if ex)
        total_errors = sum(ex.errors for ex in executions.values() if ex)
        
        avg_coverage = sum(ex.coverage for ex in executions.values() if ex) / len(executions) if executions else 0
        
        report = f"""# Unit Test Execution Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Tests:** {total_tests}
- **Passed:** {total_passed} ({(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%)
- **Failed:** {total_failed} ({(total_failed/total_tests*100) if total_tests > 0 else 0:.1f}%)
- **Skipped:** {total_skipped} ({(total_skipped/total_tests*100) if total_tests > 0 else 0:.1f}%)
- **Errors:** {total_errors} ({(total_errors/total_tests*100) if total_tests > 0 else 0:.1f}%)
- **Average Coverage:** {avg_coverage:.1f}%

## Test Suite Results

| Suite | Tests | Passed | Failed | Skipped | Errors | Coverage | Duration |
|-------|-------|--------|--------|---------|--------|----------|----------|
"""
        
        for suite_name, execution in executions.items():
            if execution:
                report += f"| {suite_name} | {execution.total_tests} | {execution.passed} | "
                report += f"{execution.failed} | {execution.skipped} | {execution.errors} | "
                report += f"{execution.coverage:.1f}% | {execution.duration:.2f}s |\n"
        
        # Add failed test details
        failed_tests = []
        for execution in executions.values():
            if execution:
                failed_tests.extend([r for r in execution.results if r.status == TestStatus.FAILED])
        
        if failed_tests:
            report += "\n## Failed Tests\n\n"
            for test in failed_tests:
                report += f"### {test.test_name}\n"
                report += f"- **File:** {test.test_file}\n"
                report += f"- **Error:** {test.error_message}\n\n"
        
        return report

    def get_test_metrics(self) -> Dict[str, Any]:
        """Get test metrics and trends"""
        if not self.execution_history:
            return {"status": "no_data"}
        
        recent_executions = self.execution_history[-10:]  # Last 10 executions
        
        return {
            "total_executions": len(self.execution_history),
            "average_coverage": sum(ex.coverage for ex in recent_executions) / len(recent_executions),
            "average_pass_rate": sum(ex.passed / (ex.total_tests or 1) for ex in recent_executions) / len(recent_executions) * 100,
            "test_trend": "improving" if len(recent_executions) >= 2 and recent_executions[-1].coverage > recent_executions[-2].coverage else "stable",
            "last_execution": recent_executions[-1].timestamp.isoformat(),
            "total_tests": recent_executions[-1].total_tests if recent_executions else 0
        }

# Global unit test orchestrator instance
unit_test_orchestrator = UnitTestOrchestrator()

__all__ = [
    "UnitTestOrchestrator",
    "TestResult",
    "TestSuite", 
    "TestExecution",
    "TestStatus",
    "TestType",
    "unit_test_orchestrator"
]