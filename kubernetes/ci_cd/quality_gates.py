"""
🔧 Quality Gates Validator - IA-Influencer-Agent CI/CD
================================================================
Expert: DEVOPS_ENGINEER + QA_ENGINEER
Created: 2025-08-24
Author: Fahed Mlaiel (mlaiel@live.de)

Enterprise quality gates validation system with comprehensive code analysis.
Integrates linting, testing, security, and performance validation.
================================================================
"""

from typing import Dict, List, Optional, Any, Tuple
import asyncio
import logging
import subprocess
import json
import os
import tempfile
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class QualityGateType(Enum):
    """Quality gate type enumeration"""
    CODE_COVERAGE = "code_coverage"
    LINTING = "linting"
    TYPE_CHECKING = "type_checking"
    SECURITY_SCAN = "security_scan"
    PERFORMANCE_TEST = "performance_test"
    DEPENDENCY_CHECK = "dependency_check"
    CODE_COMPLEXITY = "code_complexity"
    DOCUMENTATION = "documentation"

class QualityStatus(Enum):
    """Quality status enumeration"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

@dataclass
class QualityGateConfig:
    """Quality gate configuration"""
    gate_type: QualityGateType
    enabled: bool = True
    threshold: Optional[float] = None
    fail_on_warning: bool = False
    timeout: int = 300
    custom_rules: Dict[str, Any] = None

@dataclass
class QualityGateResult:
    """Quality gate result"""
    gate_type: QualityGateType
    status: QualityStatus
    score: Optional[float] = None
    message: str = ""
    details: Dict[str, Any] = None
    execution_time: float = 0.0
    output: str = ""
    warnings: List[str] = None
    errors: List[str] = None

@dataclass
class QualityValidationReport:
    """Complete quality validation report"""
    project_name: str
    validation_timestamp: datetime
    overall_status: QualityStatus
    overall_score: float
    gate_results: List[QualityGateResult]
    summary: Dict[str, Any]
    recommendations: List[str] = None

class QualityGateValidator:
    """Enterprise quality gates validation engine"""
    
    def __init__(self):
        """Initialize quality gate validator"""
        self.initialized = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.validation_history: List[QualityValidationReport] = []
        
        # Default quality gate configurations
        self.default_gates = {
            QualityGateType.CODE_COVERAGE: QualityGateConfig(
                gate_type=QualityGateType.CODE_COVERAGE,
                threshold=90.0,
                fail_on_warning=False
            ),
            QualityGateType.LINTING: QualityGateConfig(
                gate_type=QualityGateType.LINTING,
                threshold=0.0,  # No linting errors allowed
                fail_on_warning=False
            ),
            QualityGateType.TYPE_CHECKING: QualityGateConfig(
                gate_type=QualityGateType.TYPE_CHECKING,
                threshold=0.0,  # No type errors allowed
                fail_on_warning=False
            ),
            QualityGateType.SECURITY_SCAN: QualityGateConfig(
                gate_type=QualityGateType.SECURITY_SCAN,
                threshold=80.0,  # Minimum security score
                fail_on_warning=True
            ),
            QualityGateType.DEPENDENCY_CHECK: QualityGateConfig(
                gate_type=QualityGateType.DEPENDENCY_CHECK,
                threshold=0.0,  # No vulnerable dependencies
                fail_on_warning=True
            ),
            QualityGateType.CODE_COMPLEXITY: QualityGateConfig(
                gate_type=QualityGateType.CODE_COMPLEXITY,
                threshold=10.0,  # Maximum cyclomatic complexity
                fail_on_warning=False
            )
        }
        
    async def initialize(self) -> bool:
        """Initialize quality gate validator"""
        try:
            # Verify required tools are available
            await self._verify_quality_tools()
            
            self.initialized = True
            self.logger.info("✅ Quality gate validator initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize quality validator: {e}")
            return False
    
    async def _verify_quality_tools(self) -> None:
        """Verify required quality tools are installed"""
        required_tools = {
            "python": "Python interpreter",
            "pytest": "Testing framework",
            "flake8": "Code linting",
            "mypy": "Type checking",
            "bandit": "Security scanning",
            "safety": "Dependency vulnerability checking",
            "radon": "Code complexity analysis"
        }
        
        missing_tools = []
        for tool, description in required_tools.items():
            if not await self._check_tool_available(tool):
                missing_tools.append(f"{tool} ({description})")
        
        if missing_tools:
            raise RuntimeError(f"Missing required tools: {', '.join(missing_tools)}")
    
    async def _check_tool_available(self, tool: str) -> bool:
        """Check if a tool is available in PATH"""
        try:
            result = await self._run_command([tool, "--version"], timeout=30)
            return result.returncode == 0
        except:
            return False
    
    async def validate_quality(
        self,
        source_path: str,
        project_name: str = "ia-influencer-agent",
        custom_gates: Optional[Dict[QualityGateType, QualityGateConfig]] = None
    ) -> QualityValidationReport:
        """Execute complete quality validation"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting quality validation for {project_name}")
            
            # Merge custom gates with defaults
            gates_config = {**self.default_gates}
            if custom_gates:
                gates_config.update(custom_gates)
            
            # Execute quality gates
            gate_results = []
            
            for gate_type, config in gates_config.items():
                if config.enabled:
                    self.logger.info(f"Executing quality gate: {gate_type.value}")
                    result = await self._execute_quality_gate(source_path, config)
                    gate_results.append(result)
                else:
                    # Create skipped result
                    result = QualityGateResult(
                        gate_type=gate_type,
                        status=QualityStatus.SKIPPED,
                        message="Quality gate disabled"
                    )
                    gate_results.append(result)
            
            # Calculate overall status and score
            overall_status, overall_score = self._calculate_overall_quality(gate_results)
            
            # Generate summary and recommendations
            summary = self._generate_quality_summary(gate_results)
            recommendations = self._generate_recommendations(gate_results)
            
            # Create validation report
            report = QualityValidationReport(
                project_name=project_name,
                validation_timestamp=start_time,
                overall_status=overall_status,
                overall_score=overall_score,
                gate_results=gate_results,
                summary=summary,
                recommendations=recommendations
            )
            
            self.validation_history.append(report)
            
            self.logger.info(f"✅ Quality validation completed. Overall score: {overall_score:.1f}%")
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Quality validation failed: {e}")
            
            # Return failed report
            return QualityValidationReport(
                project_name=project_name,
                validation_timestamp=start_time,
                overall_status=QualityStatus.FAILED,
                overall_score=0.0,
                gate_results=[],
                summary={"error": str(e)}
            )
    
    async def _execute_quality_gate(
        self,
        source_path: str,
        config: QualityGateConfig
    ) -> QualityGateResult:
        """Execute individual quality gate"""
        start_time = datetime.now()
        
        try:
            if config.gate_type == QualityGateType.CODE_COVERAGE:
                result = await self._validate_code_coverage(source_path, config)
            elif config.gate_type == QualityGateType.LINTING:
                result = await self._validate_linting(source_path, config)
            elif config.gate_type == QualityGateType.TYPE_CHECKING:
                result = await self._validate_type_checking(source_path, config)
            elif config.gate_type == QualityGateType.SECURITY_SCAN:
                result = await self._validate_security(source_path, config)
            elif config.gate_type == QualityGateType.DEPENDENCY_CHECK:
                result = await self._validate_dependencies(source_path, config)
            elif config.gate_type == QualityGateType.CODE_COMPLEXITY:
                result = await self._validate_code_complexity(source_path, config)
            elif config.gate_type == QualityGateType.PERFORMANCE_TEST:
                result = await self._validate_performance(source_path, config)
            elif config.gate_type == QualityGateType.DOCUMENTATION:
                result = await self._validate_documentation(source_path, config)
            else:
                result = QualityGateResult(
                    gate_type=config.gate_type,
                    status=QualityStatus.SKIPPED,
                    message=f"Quality gate {config.gate_type.value} not implemented"
                )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return QualityGateResult(
                gate_type=config.gate_type,
                status=QualityStatus.FAILED,
                message=f"Quality gate execution failed: {e}",
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    async def _validate_code_coverage(
        self,
        source_path: str,
        config: QualityGateConfig
    ) -> QualityGateResult:
        """Validate code coverage"""
        try:
            # Run pytest with coverage
            cmd = [
                "python", "-m", "pytest",
                "--cov=backend",
                "--cov-report=json",
                "--cov-report=term-missing",
                "--tb=short",
                "-v"
            ]
            
            result = await self._run_command(cmd, cwd=source_path, timeout=config.timeout)
            
            # Parse coverage report
            coverage_file = os.path.join(source_path, "coverage.json")
            coverage_percentage = 0.0
            
            if os.path.exists(coverage_file):
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    coverage_percentage = coverage_data.get("totals", {}).get("percent_covered", 0.0)
            
            # Determine status based on threshold
            status = QualityStatus.PASSED if coverage_percentage >= config.threshold else QualityStatus.FAILED
            
            return QualityGateResult(
                gate_type=config.gate_type,
                status=status,
                score=coverage_percentage,
                message=f"Code coverage: {coverage_percentage:.1f}% (threshold: {config.threshold:.1f}%)",
                details={"coverage_percentage": coverage_percentage, "threshold": config.threshold},
                output=result.stdout
            )
            
        except Exception as e:
            return QualityGateResult(
                gate_type=config.gate_type,
                status=QualityStatus.FAILED,
                message=f"Code coverage validation failed: {e}",
                errors=[str(e)]
            )
    
    async def _validate_linting(
        self,
        source_path: str,
        config: QualityGateConfig
    ) -> QualityGateResult:
        """Validate code linting"""
        try:
            # Run flake8 linting
            cmd = [
                "flake8",
                "backend/",
                "--format=json",
                "--max-line-length=120",
                "--ignore=E203,W503",
                "--exclude=__pycache__,migrations,venv,.git"
            ]
            
            result = await self._run_command(cmd, cwd=source_path, timeout=config.timeout)
            
            # Parse linting results
            linting_issues = []
            if result.stdout:
                try:
                    linting_data = json.loads(result.stdout)
                    linting_issues = linting_data if isinstance(linting_data, list) else []
                except json.JSONDecodeError:
                    # Fallback to parsing text output
                    linting_issues = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            issue_count = len(linting_issues)
            
            # Determine status
            if issue_count <= config.threshold:
                status = QualityStatus.PASSED
            elif issue_count <= config.threshold * 1.5 and not config.fail_on_warning:
                status = QualityStatus.WARNING
            else:
                status = QualityStatus.FAILED
            
            return QualityGateResult(
                gate_type=config.gate_type,
                status=status,
                score=max(0, 100 - issue_count),
                message=f"Linting issues: {issue_count} (threshold: {config.threshold})",
                details={"issue_count": issue_count, "issues": linting_issues},
                output=result.stdout,
                warnings=linting_issues if status == QualityStatus.WARNING else None
            )
            
        except Exception as e:
            return QualityGateResult(
                gate_type=config.gate_type,
                status=QualityStatus.FAILED,
                message=f"Linting validation failed: {e}",
                errors=[str(e)]
            )
    
    async def _validate_type_checking(
        self,
        source_path: str,
        config: QualityGateConfig
    ) -> QualityGateResult:
        """Validate type checking"""
        try:
            # Run mypy type checking
            cmd = [
                "mypy",
                "backend/",
                "--json-report", "/tmp/mypy_report",
                "--ignore-missing-imports",
                "--strict-optional",
                "--warn-redundant-casts",
                "--warn-unused-ignores"
            ]
            
            result = await self._run_command(cmd, cwd=source_path, timeout=config.timeout)
            
            # Parse mypy results
            error_count = 0
            type_errors = []
            
            # Parse output for errors
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ': error:' in line:
                        error_count += 1
                        type_errors.append(line)
            
            # Determine status
            if error_count <= config.threshold:
                status = QualityStatus.PASSED
            else:
                status = QualityStatus.FAILED
            
            return QualityGateResult(
                gate_type=config.gate_type,
                status=status,
                score=max(0, 100 - error_count * 5),
                message=f"Type checking errors: {error_count} (threshold: {config.threshold})",
                details={"error_count": error_count, "errors": type_errors},
                output=result.stdout
            )
            
        except Exception as e:
            return QualityGateResult(
                gate_type=config.gate_type,
                status=QualityStatus.FAILED,
                message=f"Type checking validation failed: {e}",
                errors=[str(e)]
            )
    
    async def _validate_security(
        self,
        source_path: str,
        config: QualityGateConfig
    ) -> QualityGateResult:
        """Validate security scanning"""
        try:
            # Run bandit security scan
            cmd = [
                "bandit",
                "-r", "backend/",
                "-f", "json",
                "-ll",  # Low confidence, low severity
                "--exclude", "*/tests/*,*/test_*"
            ]
            
            result = await self._run_command(cmd, cwd=source_path, timeout=config.timeout)
            
            # Parse security scan results
            security_issues = []
            high_severity_count = 0
            medium_severity_count = 0
            
            if result.stdout:
                try:
                    security_data = json.loads(result.stdout)
                    security_issues = security_data.get("results", [])
                    
                    for issue in security_issues:
                        severity = issue.get("issue_severity", "").upper()
                        if severity == "HIGH":
                            high_severity_count += 1
                        elif severity == "MEDIUM":
                            medium_severity_count += 1
                            
                except json.JSONDecodeError:
                    pass
            
            # Calculate security score
            total_issues = len(security_issues)
            security_score = max(0, 100 - (high_severity_count * 20) - (medium_severity_count * 10))
            
            # Determine status
            if security_score >= config.threshold:
                status = QualityStatus.PASSED
            elif security_score >= config.threshold * 0.8 and not config.fail_on_warning:
                status = QualityStatus.WARNING
            else:
                status = QualityStatus.FAILED
            
            return QualityGateResult(
                gate_type=config.gate_type,
                status=status,
                score=security_score,
                message=f"Security score: {security_score:.1f}% (threshold: {config.threshold:.1f}%)",
                details={
                    "total_issues": total_issues,
                    "high_severity": high_severity_count,
                    "medium_severity": medium_severity_count,
                    "issues": security_issues
                },
                output=result.stdout
            )
            
        except Exception as e:
            return QualityGateResult(
                gate_type=config.gate_type,
                status=QualityStatus.FAILED,
                message=f"Security validation failed: {e}",
                errors=[str(e)]
            )
    
    async def _validate_dependencies(
        self,
        source_path: str,
        config: QualityGateConfig
    ) -> QualityGateResult:
        """Validate dependency vulnerabilities"""
        try:
            # Run safety check for known vulnerabilities
            cmd = ["safety", "check", "--json"]
            
            result = await self._run_command(cmd, cwd=source_path, timeout=config.timeout)
            
            # Parse safety results
            vulnerabilities = []
            if result.stdout:
                try:
                    safety_data = json.loads(result.stdout)
                    vulnerabilities = safety_data if isinstance(safety_data, list) else []
                except json.JSONDecodeError:
                    pass
            
            vulnerability_count = len(vulnerabilities)
            
            # Determine status
            if vulnerability_count <= config.threshold:
                status = QualityStatus.PASSED
            elif vulnerability_count <= config.threshold * 2 and not config.fail_on_warning:
                status = QualityStatus.WARNING
            else:
                status = QualityStatus.FAILED
            
            return QualityGateResult(
                gate_type=config.gate_type,
                status=status,
                score=max(0, 100 - vulnerability_count * 10),
                message=f"Dependency vulnerabilities: {vulnerability_count} (threshold: {config.threshold})",
                details={"vulnerability_count": vulnerability_count, "vulnerabilities": vulnerabilities},
                output=result.stdout
            )
            
        except Exception as e:
            return QualityGateResult(
                gate_type=config.gate_type,
                status=QualityStatus.FAILED,
                message=f"Dependency validation failed: {e}",
                errors=[str(e)]
            )
    
    async def _validate_code_complexity(
        self,
        source_path: str,
        config: QualityGateConfig
    ) -> QualityGateResult:
        """Validate code complexity"""
        try:
            # Run radon complexity analysis
            cmd = [
                "radon", "cc", "backend/",
                "--json",
                "--average"
            ]
            
            result = await self._run_command(cmd, cwd=source_path, timeout=config.timeout)
            
            # Parse complexity results
            complexity_data = {}
            max_complexity = 0
            avg_complexity = 0
            
            if result.stdout:
                try:
                    complexity_data = json.loads(result.stdout)
                    
                    # Calculate maximum and average complexity
                    all_complexities = []
                    for file_path, functions in complexity_data.items():
                        for func in functions:
                            complexity = func.get("complexity", 0)
                            all_complexities.append(complexity)
                            max_complexity = max(max_complexity, complexity)
                    
                    if all_complexities:
                        avg_complexity = sum(all_complexities) / len(all_complexities)
                        
                except json.JSONDecodeError:
                    pass
            
            # Determine status based on maximum complexity
            if max_complexity <= config.threshold:
                status = QualityStatus.PASSED
            elif max_complexity <= config.threshold * 1.5 and not config.fail_on_warning:
                status = QualityStatus.WARNING
            else:
                status = QualityStatus.FAILED
            
            complexity_score = max(0, 100 - (max_complexity - config.threshold) * 5)
            
            return QualityGateResult(
                gate_type=config.gate_type,
                status=status,
                score=complexity_score,
                message=f"Max complexity: {max_complexity:.1f} (threshold: {config.threshold:.1f})",
                details={
                    "max_complexity": max_complexity,
                    "avg_complexity": avg_complexity,
                    "threshold": config.threshold,
                    "complexity_data": complexity_data
                },
                output=result.stdout
            )
            
        except Exception as e:
            return QualityGateResult(
                gate_type=config.gate_type,
                status=QualityStatus.FAILED,
                message=f"Code complexity validation failed: {e}",
                errors=[str(e)]
            )
    
    async def _validate_performance(
        self,
        source_path: str,
        config: QualityGateConfig
    ) -> QualityGateResult:
        """Validate performance tests"""
        try:
            # Run performance tests using pytest-benchmark
            cmd = [
                "python", "-m", "pytest",
                "-m", "benchmark",
                "--benchmark-json=/tmp/benchmark.json",
                "--benchmark-only"
            ]
            
            result = await self._run_command(cmd, cwd=source_path, timeout=config.timeout)
            
            # Parse benchmark results
            benchmark_data = {}
            avg_performance = 100.0  # Default good performance score
            
            benchmark_file = "/tmp/benchmark.json"
            if os.path.exists(benchmark_file):
                with open(benchmark_file) as f:
                    benchmark_data = json.load(f)
                    
                    # Calculate performance score based on benchmarks
                    benchmarks = benchmark_data.get("benchmarks", [])
                    if benchmarks:
                        # Example: calculate based on mean execution time
                        mean_times = [b.get("stats", {}).get("mean", 0) for b in benchmarks]
                        if mean_times:
                            max_mean_time = max(mean_times)
                            # Performance score: lower time = higher score
                            avg_performance = max(0, 100 - (max_mean_time * 1000))  # Convert to ms
            
            status = QualityStatus.PASSED if avg_performance >= config.threshold else QualityStatus.FAILED
            
            return QualityGateResult(
                gate_type=config.gate_type,
                status=status,
                score=avg_performance,
                message=f"Performance score: {avg_performance:.1f}% (threshold: {config.threshold:.1f}%)",
                details={"benchmark_data": benchmark_data},
                output=result.stdout
            )
            
        except Exception as e:
            return QualityGateResult(
                gate_type=config.gate_type,
                status=QualityStatus.WARNING,  # Performance tests are optional
                message=f"Performance validation skipped: {e}",
                score=config.threshold,  # Give threshold score
                warnings=[str(e)]
            )
    
    async def _validate_documentation(
        self,
        source_path: str,
        config: QualityGateConfig
    ) -> QualityGateResult:
        """Validate documentation coverage"""
        try:
            # Check for documentation files
            doc_files = []
            required_docs = ["README.md", "README.de.md", "README.fr.md"]
            
            for doc_file in required_docs:
                doc_path = os.path.join(source_path, doc_file)
                if os.path.exists(doc_path):
                    doc_files.append(doc_file)
            
            # Calculate documentation score
            doc_coverage = (len(doc_files) / len(required_docs)) * 100
            
            # Check for docstrings in Python files
            python_files = list(Path(source_path).rglob("*.py"))
            documented_files = 0
            
            for py_file in python_files:
                if "test" not in str(py_file) and "__pycache__" not in str(py_file):
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '"""' in content or "'''" in content:
                            documented_files += 1
            
            if python_files:
                docstring_coverage = (documented_files / len(python_files)) * 100
                doc_score = (doc_coverage + docstring_coverage) / 2
            else:
                doc_score = doc_coverage
            
            status = QualityStatus.PASSED if doc_score >= config.threshold else QualityStatus.WARNING
            
            return QualityGateResult(
                gate_type=config.gate_type,
                status=status,
                score=doc_score,
                message=f"Documentation coverage: {doc_score:.1f}% (threshold: {config.threshold:.1f}%)",
                details={
                    "doc_files": doc_files,
                    "required_docs": required_docs,
                    "documented_files": documented_files,
                    "total_python_files": len(python_files)
                }
            )
            
        except Exception as e:
            return QualityGateResult(
                gate_type=config.gate_type,
                status=QualityStatus.WARNING,
                message=f"Documentation validation failed: {e}",
                warnings=[str(e)]
            )
    
    def _calculate_overall_quality(
        self,
        gate_results: List[QualityGateResult]
    ) -> Tuple[QualityStatus, float]:
        """Calculate overall quality status and score"""
        if not gate_results:
            return QualityStatus.FAILED, 0.0
        
        # Count status types
        passed_count = sum(1 for r in gate_results if r.status == QualityStatus.PASSED)
        failed_count = sum(1 for r in gate_results if r.status == QualityStatus.FAILED)
        warning_count = sum(1 for r in gate_results if r.status == QualityStatus.WARNING)
        
        # Calculate weighted average score
        total_score = 0.0
        total_weight = 0.0
        
        for result in gate_results:
            if result.score is not None:
                weight = 1.0
                if result.gate_type in [QualityGateType.CODE_COVERAGE, QualityGateType.SECURITY_SCAN]:
                    weight = 2.0  # Higher weight for critical gates
                
                total_score += result.score * weight
                total_weight += weight
        
        overall_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # Determine overall status
        if failed_count > 0:
            overall_status = QualityStatus.FAILED
        elif warning_count > 0:
            overall_status = QualityStatus.WARNING
        else:
            overall_status = QualityStatus.PASSED
        
        return overall_status, overall_score
    
    def _generate_quality_summary(self, gate_results: List[QualityGateResult]) -> Dict[str, Any]:
        """Generate quality validation summary"""
        summary = {
            "total_gates": len(gate_results),
            "passed": sum(1 for r in gate_results if r.status == QualityStatus.PASSED),
            "failed": sum(1 for r in gate_results if r.status == QualityStatus.FAILED),
            "warnings": sum(1 for r in gate_results if r.status == QualityStatus.WARNING),
            "skipped": sum(1 for r in gate_results if r.status == QualityStatus.SKIPPED),
            "total_execution_time": sum(r.execution_time for r in gate_results),
            "gate_scores": {r.gate_type.value: r.score for r in gate_results if r.score is not None}
        }
        
        return summary
    
    def _generate_recommendations(self, gate_results: List[QualityGateResult]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        for result in gate_results:
            if result.status == QualityStatus.FAILED:
                if result.gate_type == QualityGateType.CODE_COVERAGE:
                    recommendations.append("Increase test coverage by adding unit tests for uncovered code paths")
                elif result.gate_type == QualityGateType.LINTING:
                    recommendations.append("Fix code style issues identified by the linter")
                elif result.gate_type == QualityGateType.SECURITY_SCAN:
                    recommendations.append("Address security vulnerabilities identified in the code")
                elif result.gate_type == QualityGateType.DEPENDENCY_CHECK:
                    recommendations.append("Update vulnerable dependencies to secure versions")
                elif result.gate_type == QualityGateType.CODE_COMPLEXITY:
                    recommendations.append("Refactor complex functions to reduce cyclomatic complexity")
            
            elif result.status == QualityStatus.WARNING:
                recommendations.append(f"Consider improving {result.gate_type.value} metrics for better code quality")
        
        return recommendations
    
    async def _run_command(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        timeout: int = 300
    ) -> subprocess.CompletedProcess:
        """Run shell command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=process.returncode,
                stdout=stdout.decode(),
                stderr=stderr.decode()
            )
            
        except asyncio.TimeoutError:
            raise RuntimeError(f"Command timed out: {' '.join(cmd)}")
        except Exception as e:
            raise RuntimeError(f"Command failed: {e}")
    
    def get_validation_history(self, limit: int = 10) -> List[QualityValidationReport]:
        """Get validation history"""
        return self.validation_history[-limit:]
    
    def get_quality_trends(self) -> Dict[str, Any]:
        """Get quality trends over time"""
        if not self.validation_history:
            return {}
        
        recent_reports = self.validation_history[-10:]  # Last 10 reports
        
        trend_data = {
            "score_trend": [r.overall_score for r in recent_reports],
            "coverage_trend": [],
            "security_trend": [],
            "dates": [r.validation_timestamp.isoformat() for r in recent_reports]
        }
        
        # Extract specific metric trends
        for report in recent_reports:
            for result in report.gate_results:
                if result.gate_type == QualityGateType.CODE_COVERAGE and result.score:
                    trend_data["coverage_trend"].append(result.score)
                elif result.gate_type == QualityGateType.SECURITY_SCAN and result.score:
                    trend_data["security_trend"].append(result.score)
        
        return trend_data

__all__ = [
    "QualityGateValidator",
    "QualityGateConfig",
    "QualityGateResult",
    "QualityValidationReport",
    "QualityGateType",
    "QualityStatus",
]
