"""🧪 Unit Test Orchestrator - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + TESTING_ARCHITECT + DEVOPS_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Central orchestrator for unit testing across all microservices and modules.
Provides unified test execution, reporting, and quality metrics collection.
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
import statistics
import concurrent.futures
import coverage

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running" 
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestSeverity(Enum):
    """Test failure severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TestResult:
    """Individual test result"""
    test_id: str
    test_name: str
    module_path: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    assertion_count: int = 0
    coverage_percentage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass 
class TestSuite:
    """Test suite definition"""
    suite_name: str
    test_patterns: List[str]
    module_patterns: List[str]
    dependencies: List[str] = field(default_factory=list)
    setup_commands: List[str] = field(default_factory=list)
    teardown_commands: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    parallel: bool = True
    retry_count: int = 0

@dataclass
class TestOrchestrationReport:
    """Comprehensive test orchestration report"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_duration: float
    average_duration: float
    coverage_percentage: float
    test_results: List[TestResult]
    suite_results: Dict[str, Dict[str, Any]]
    quality_metrics: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class UnitTestOrchestrator:
    """
    Central orchestrator for unit testing across the entire platform
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize unit test orchestrator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_results: List[TestResult] = []
        self.coverage_data: Dict[str, Any] = {}
        
        # Initialize test suites
        self._initialize_default_suites()
        
        # Coverage tracking
        self.coverage_tracker = coverage.Coverage(
            source=[str(self.project_root)],
            omit=["*/tests/*", "*/test_*", "*/__pycache__/*", "*/venv/*"]
        )

    def _initialize_default_suites(self):
        """Initialize default test suites for the platform"""
        
        # Core API Tests
        self.test_suites["api_core"] = TestSuite(
            suite_name="API Core Tests",
            test_patterns=["tests/api/test_*.py", "tests/core/test_*.py"],
            module_patterns=["api/**/*.py", "core/**/*.py"],
            setup_commands=["pip install -e .", "export TESTING=true"],
            timeout_seconds=300,
            parallel=True
        )
        
        # Database Tests  
        self.test_suites["database"] = TestSuite(
            suite_name="Database Tests",
            test_patterns=["tests/database/test_*.py", "tests/mongodb/test_*.py"],
            module_patterns=["database/**/*.py", "mongodb/**/*.py"],
            dependencies=["mongodb", "redis"],
            setup_commands=["docker-compose up -d mongodb redis"],
            teardown_commands=["docker-compose down"],
            timeout_seconds=600,
            parallel=False  # Database tests should run sequentially
        )
        
        # Security Tests
        self.test_suites["security"] = TestSuite(
            suite_name="Security Tests", 
            test_patterns=["tests/security/test_*.py", "tests/protection/test_*.py"],
            module_patterns=["security/**/*.py", "protection/**/*.py"],
            timeout_seconds=900,
            parallel=True
        )
        
        # AI/ML Tests
        self.test_suites["ai_ml"] = TestSuite(
            suite_name="AI/ML Tests",
            test_patterns=["tests/ai_models/test_*.py", "tests/ml/test_*.py"],
            module_patterns=["ai_models/**/*.py", "ml/**/*.py"],
            setup_commands=["pip install torch transformers", "export CUDA_VISIBLE_DEVICES="],
            timeout_seconds=1200,
            parallel=True
        )
        
        # Integration Tests
        self.test_suites["integration"] = TestSuite(
            suite_name="Integration Tests",
            test_patterns=["tests/integration/test_*.py"],
            module_patterns=["**/*.py"],
            dependencies=["api_core", "database", "security"],
            timeout_seconds=1800,
            parallel=False
        )
        
        # Quality Module Tests
        self.test_suites["quality"] = TestSuite(
            suite_name="Quality Module Tests",
            test_patterns=["tests/quality/test_*.py"],
            module_patterns=["quality/**/*.py"],
            timeout_seconds=300,
            parallel=True
        )

    async def orchestrate_all_tests(
        self, 
        suite_names: Optional[List[str]] = None,
        fail_fast: bool = False,
        coverage_enabled: bool = True
    ) -> TestOrchestrationReport:
        """Orchestrate execution of all or specified test suites"""
        self.logger.info("Starting comprehensive test orchestration")
        start_time = time.time()
        
        # Determine which suites to run
        suites_to_run = suite_names or list(self.test_suites.keys())
        
        # Start coverage tracking
        if coverage_enabled:
            self.coverage_tracker.start()
        
        try:
            # Execute test suites
            suite_results = {}
            for suite_name in suites_to_run:
                if suite_name not in self.test_suites:
                    self.logger.warning(f"Test suite '{suite_name}' not found")
                    continue
                
                self.logger.info(f"Executing test suite: {suite_name}")
                suite_result = await self._execute_test_suite(self.test_suites[suite_name])
                suite_results[suite_name] = suite_result
                
                # Check for fail-fast
                if fail_fast and suite_result.get("failed_tests", 0) > 0:
                    self.logger.warning(f"Fail-fast enabled, stopping due to failures in {suite_name}")
                    break
            
            # Stop coverage tracking
            if coverage_enabled:
                self.coverage_tracker.stop()
                self.coverage_tracker.save()
                
            # Generate comprehensive report
            report = await self._generate_orchestration_report(
                suite_results, 
                time.time() - start_time,
                coverage_enabled
            )
            
            self.logger.info(
                f"Test orchestration completed. "
                f"Passed: {report.passed_tests}, Failed: {report.failed_tests}, "
                f"Coverage: {report.coverage_percentage:.1f}%"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Test orchestration failed: {e}")
            raise
        finally:
            if coverage_enabled:
                self.coverage_tracker.stop()

    async def _execute_test_suite(self, suite: TestSuite) -> Dict[str, Any]:
        """Execute a single test suite"""
        suite_start_time = time.time()
        
        try:
            # Run setup commands
            await self._run_setup_commands(suite.setup_commands)
            
            # Check dependencies
            await self._check_dependencies(suite.dependencies)
            
            # Find test files
            test_files = await self._find_test_files(suite.test_patterns)
            
            if not test_files:
                self.logger.warning(f"No test files found for suite {suite.suite_name}")
                return {
                    "status": "skipped",
                    "reason": "no_tests_found",
                    "duration": 0,
                    "test_results": []
                }
            
            # Execute tests
            if suite.parallel:
                test_results = await self._run_tests_parallel(test_files, suite)
            else:
                test_results = await self._run_tests_sequential(test_files, suite)
            
            # Calculate suite metrics
            suite_metrics = self._calculate_suite_metrics(test_results)
            
            return {
                "status": "completed",
                "duration": time.time() - suite_start_time,
                "test_count": len(test_results),
                "passed_tests": len([r for r in test_results if r.status == TestStatus.PASSED]),
                "failed_tests": len([r for r in test_results if r.status == TestStatus.FAILED]),
                "skipped_tests": len([r for r in test_results if r.status == TestStatus.SKIPPED]),
                "error_tests": len([r for r in test_results if r.status == TestStatus.ERROR]),
                "test_results": test_results,
                "metrics": suite_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error executing test suite {suite.suite_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "duration": time.time() - suite_start_time,
                "test_results": []
            }
        finally:
            # Run teardown commands
            await self._run_teardown_commands(suite.teardown_commands)

    async def _run_tests_parallel(self, test_files: List[Path], suite: TestSuite) -> List[TestResult]:
        """Run tests in parallel"""
        results = []
        
        # Use thread pool for parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self._run_single_test_file, test_file, suite): test_file
                for test_file in test_files
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                test_file = future_to_file[future]
                try:
                    file_results = future.result(timeout=suite.timeout_seconds)
                    results.extend(file_results)
                except Exception as e:
                    self.logger.error(f"Error running test file {test_file}: {e}")
                    results.append(TestResult(
                        test_id=f"error_{test_file.stem}",
                        test_name=f"Test file: {test_file.name}",
                        module_path=str(test_file),
                        status=TestStatus.ERROR,
                        duration=0.0,
                        error_message=str(e)
                    ))
        
        return results

    async def _run_tests_sequential(self, test_files: List[Path], suite: TestSuite) -> List[TestResult]:
        """Run tests sequentially"""
        results = []
        
        for test_file in test_files:
            try:
                file_results = self._run_single_test_file(test_file, suite)
                results.extend(file_results)
            except Exception as e:
                self.logger.error(f"Error running test file {test_file}: {e}")
                results.append(TestResult(
                    test_id=f"error_{test_file.stem}",
                    test_name=f"Test file: {test_file.name}",
                    module_path=str(test_file),
                    status=TestStatus.ERROR,
                    duration=0.0,
                    error_message=str(e)
                ))
        
        return results

    def _run_single_test_file(self, test_file: Path, suite: TestSuite) -> List[TestResult]:
        """Run a single test file and parse results"""
        cmd = [
            "python", "-m", "pytest", 
            str(test_file),
            "-v", "--tb=short", 
            "--json-report", f"--json-report-file=/tmp/test_report_{test_file.stem}.json"
        ]
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=suite.timeout_seconds,
                cwd=str(self.project_root)
            )
            duration = time.time() - start_time
            
            # Parse pytest JSON report
            report_file = Path(f"/tmp/test_report_{test_file.stem}.json")
            if report_file.exists():
                return self._parse_pytest_json_report(report_file, duration)
            else:
                # Fallback: parse from stdout/stderr
                return self._parse_pytest_output(result.stdout, result.stderr, str(test_file), duration)
                
        except subprocess.TimeoutExpired:
            return [TestResult(
                test_id=f"timeout_{test_file.stem}",
                test_name=f"Test file: {test_file.name}",
                module_path=str(test_file),
                status=TestStatus.ERROR,
                duration=suite.timeout_seconds,
                error_message="Test execution timed out"
            )]
        except Exception as e:
            return [TestResult(
                test_id=f"error_{test_file.stem}",
                test_name=f"Test file: {test_file.name}",
                module_path=str(test_file),
                status=TestStatus.ERROR,
                duration=0.0,
                error_message=str(e)
            )]

    def _parse_pytest_json_report(self, report_file: Path, total_duration: float) -> List[TestResult]:
        """Parse pytest JSON report"""
        results = []
        
        try:
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            tests = report_data.get("tests", [])
            for test_data in tests:
                status_map = {
                    "PASSED": TestStatus.PASSED,
                    "FAILED": TestStatus.FAILED,
                    "SKIPPED": TestStatus.SKIPPED,
                    "ERROR": TestStatus.ERROR
                }
                
                status = status_map.get(test_data.get("outcome", "ERROR"), TestStatus.ERROR)
                
                result = TestResult(
                    test_id=test_data.get("nodeid", "unknown"),
                    test_name=test_data.get("name", "unknown"),
                    module_path=test_data.get("file", "unknown"),
                    status=status,
                    duration=test_data.get("duration", 0.0),
                    error_message=test_data.get("call", {}).get("longrepr") if status in [TestStatus.FAILED, TestStatus.ERROR] else None,
                    metadata={
                        "keywords": test_data.get("keywords", []),
                        "markers": test_data.get("markers", [])
                    }
                )
                results.append(result)
            
            # Clean up report file
            report_file.unlink(missing_ok=True)
            
        except Exception as e:
            self.logger.error(f"Error parsing pytest JSON report: {e}")
            # Return minimal result
            results.append(TestResult(
                test_id="parse_error",
                test_name="JSON Report Parse Error",
                module_path=str(report_file),
                status=TestStatus.ERROR,
                duration=total_duration,
                error_message=str(e)
            ))
        
        return results

    def _parse_pytest_output(self, stdout: str, stderr: str, test_file: str, duration: float) -> List[TestResult]:
        """Parse pytest output as fallback"""
        # Simple parsing - in real implementation, this would be more sophisticated
        if "FAILED" in stdout or "ERROR" in stderr:
            status = TestStatus.FAILED
            error_message = stderr or "Test failed (see logs)"
        elif "PASSED" in stdout:
            status = TestStatus.PASSED
            error_message = None
        else:
            status = TestStatus.SKIPPED
            error_message = None
        
        return [TestResult(
            test_id=f"fallback_{Path(test_file).stem}",
            test_name=f"Test file: {Path(test_file).name}",
            module_path=test_file,
            status=status,
            duration=duration,
            error_message=error_message
        )]

    async def _find_test_files(self, patterns: List[str]) -> List[Path]:
        """Find test files matching patterns"""
        test_files = []
        
        for pattern in patterns:
            found_files = list(self.project_root.glob(pattern))
            test_files.extend(found_files)
        
        # Remove duplicates and sort
        unique_files = list(set(test_files))
        unique_files.sort()
        
        return unique_files

    async def _run_setup_commands(self, commands: List[str]):
        """Run setup commands before test execution"""
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, check=True, cwd=str(self.project_root))
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Setup command failed: {cmd}, error: {e}")

    async def _run_teardown_commands(self, commands: List[str]):
        """Run teardown commands after test execution"""
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, check=False, cwd=str(self.project_root))
            except Exception as e:
                self.logger.warning(f"Teardown command failed: {cmd}, error: {e}")

    async def _check_dependencies(self, dependencies: List[str]):
        """Check if test dependencies are available"""
        for dep in dependencies:
            if dep in self.test_suites:
                # Suite dependency - would need to track execution order
                continue
            else:
                # External dependency - could check if service is running
                pass

    def _calculate_suite_metrics(self, test_results: List[TestResult]) -> Dict[str, float]:
        """Calculate metrics for a test suite"""
        if not test_results:
            return {}
        
        durations = [r.duration for r in test_results if r.duration > 0]
        
        return {
            "average_duration": statistics.mean(durations) if durations else 0.0,
            "median_duration": statistics.median(durations) if durations else 0.0,
            "max_duration": max(durations) if durations else 0.0,
            "min_duration": min(durations) if durations else 0.0,
            "pass_rate": len([r for r in test_results if r.status == TestStatus.PASSED]) / len(test_results) * 100,
            "failure_rate": len([r for r in test_results if r.status == TestStatus.FAILED]) / len(test_results) * 100
        }

    async def _generate_orchestration_report(
        self, 
        suite_results: Dict[str, Dict[str, Any]], 
        total_duration: float,
        coverage_enabled: bool
    ) -> TestOrchestrationReport:
        """Generate comprehensive orchestration report"""
        
        # Aggregate results
        all_test_results = []
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        error_tests = 0
        
        for suite_name, suite_result in suite_results.items():
            suite_test_results = suite_result.get("test_results", [])
            all_test_results.extend(suite_test_results)
            
            total_tests += suite_result.get("test_count", 0)
            passed_tests += suite_result.get("passed_tests", 0)
            failed_tests += suite_result.get("failed_tests", 0)
            skipped_tests += suite_result.get("skipped_tests", 0)
            error_tests += suite_result.get("error_tests", 0)
        
        # Calculate coverage
        coverage_percentage = 0.0
        if coverage_enabled:
            try:
                coverage_percentage = self.coverage_tracker.report(show_missing=False)
            except:
                coverage_percentage = 0.0
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(all_test_results, coverage_percentage)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(suite_results, quality_metrics)
        
        # Calculate average duration
        durations = [r.duration for r in all_test_results if r.duration > 0]
        average_duration = statistics.mean(durations) if durations else 0.0
        
        return TestOrchestrationReport(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            error_tests=error_tests,
            total_duration=total_duration,
            average_duration=average_duration,
            coverage_percentage=coverage_percentage,
            test_results=all_test_results,
            suite_results=suite_results,
            quality_metrics=quality_metrics,
            recommendations=recommendations
        )

    def _calculate_quality_metrics(self, test_results: List[TestResult], coverage: float) -> Dict[str, float]:
        """Calculate overall quality metrics"""
        if not test_results:
            return {"overall_quality_score": 0.0}
        
        # Pass rate
        pass_rate = len([r for r in test_results if r.status == TestStatus.PASSED]) / len(test_results) * 100
        
        # Test stability (consistent execution times)
        durations = [r.duration for r in test_results if r.duration > 0]
        stability_score = 100.0
        if len(durations) > 1:
            cv = statistics.stdev(durations) / statistics.mean(durations) if statistics.mean(durations) > 0 else 0
            stability_score = max(0, 100 - cv * 100)
        
        # Overall quality score (weighted average)
        overall_score = (pass_rate * 0.4) + (coverage * 0.3) + (stability_score * 0.3)
        
        return {
            "pass_rate": pass_rate,
            "coverage_score": coverage,
            "test_stability_score": stability_score,
            "overall_quality_score": overall_score
        }

    def _generate_recommendations(
        self, 
        suite_results: Dict[str, Dict[str, Any]], 
        quality_metrics: Dict[str, float]
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Coverage recommendations
        coverage = quality_metrics.get("coverage_score", 0)
        if coverage < 80:
            recommendations.append(f"Increase test coverage from {coverage:.1f}% to at least 80%")
        
        # Pass rate recommendations
        pass_rate = quality_metrics.get("pass_rate", 0)
        if pass_rate < 95:
            recommendations.append(f"Improve test pass rate from {pass_rate:.1f}% to at least 95%")
        
        # Suite-specific recommendations
        for suite_name, suite_result in suite_results.items():
            failed_tests = suite_result.get("failed_tests", 0)
            if failed_tests > 0:
                recommendations.append(f"Fix {failed_tests} failing tests in {suite_name} suite")
            
            metrics = suite_result.get("metrics", {})
            avg_duration = metrics.get("average_duration", 0)
            if avg_duration > 30:  # 30 seconds
                recommendations.append(f"Optimize {suite_name} tests - average duration is {avg_duration:.1f}s")
        
        return recommendations

    def export_report(self, report: TestOrchestrationReport, format: str = "json") -> str:
        """Export test orchestration report"""
        if format == "json":
            return self._export_json_report(report)
        elif format == "html":
            return self._export_html_report(report)
        elif format == "markdown":
            return self._export_markdown_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json_report(self, report: TestOrchestrationReport) -> str:
        """Export report as JSON"""
        # Convert to serializable format
        data = {
            "timestamp": report.timestamp.isoformat(),
            "summary": {
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "skipped_tests": report.skipped_tests,
                "error_tests": report.error_tests,
                "total_duration": report.total_duration,
                "average_duration": report.average_duration,
                "coverage_percentage": report.coverage_percentage
            },
            "quality_metrics": report.quality_metrics,
            "recommendations": report.recommendations,
            "suite_results": report.suite_results
        }
        
        return json.dumps(data, indent=2)

    def _export_markdown_report(self, report: TestOrchestrationReport) -> str:
        """Export report as Markdown"""
        md = f"""# Unit Test Orchestration Report

**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Total Duration:** {report.total_duration:.2f}s

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {report.total_tests} |
| Passed | {report.passed_tests} |
| Failed | {report.failed_tests} |
| Skipped | {report.skipped_tests} |
| Errors | {report.error_tests} |
| Pass Rate | {report.quality_metrics.get('pass_rate', 0):.1f}% |
| Coverage | {report.coverage_percentage:.1f}% |
| Overall Quality Score | {report.quality_metrics.get('overall_quality_score', 0):.1f}% |

## Recommendations

"""
        for i, rec in enumerate(report.recommendations, 1):
            md += f"{i}. {rec}\n"

        return md

    def _export_html_report(self, report: TestOrchestrationReport) -> str:
        """Export report as HTML"""
        # Simplified HTML report
        return f"""
        <html>
        <head><title>Unit Test Orchestration Report</title></head>
        <body>
        <h1>Unit Test Orchestration Report</h1>
        <p><strong>Generated:</strong> {report.timestamp}</p>
        <p><strong>Total Tests:</strong> {report.total_tests}</p>
        <p><strong>Pass Rate:</strong> {report.quality_metrics.get('pass_rate', 0):.1f}%</p>
        <p><strong>Coverage:</strong> {report.coverage_percentage:.1f}%</p>
        </body>
        </html>
        """

# Global unit test orchestrator instance
unit_test_orchestrator = UnitTestOrchestrator()

__all__ = [
    "UnitTestOrchestrator",
    "TestResult",
    "TestSuite", 
    "TestOrchestrationReport",
    "TestStatus",
    "TestSeverity",
    "unit_test_orchestrator"
]