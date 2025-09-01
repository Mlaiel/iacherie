"""🎯 Quality Metrics Orchestrator - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + DEVOPS_ENGINEER  
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Comprehensive quality metrics orchestration system that coordinates
all quality gates, metrics collection, and reporting for the platform.
================================================================
"""

import asyncio
import logging
import json
import yaml
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import statistics

# Import existing quality components
try:
    from kubernetes.ci_cd.quality_gates import QualityGateValidator, QualityGateType, QualityStatus
    from kubernetes.ci_cd.security_scanner import SecurityScanEngine, ScanType
    from monitoring.documentation.api_validator import APIDocumentationValidator
except ImportError:
    # Fallback for testing
    logging.warning("Could not import existing quality components")

logger = logging.getLogger(__name__)

class QualityMetricType(Enum):
    """Quality metric types"""
    CODE_COVERAGE = "code_coverage"
    CODE_QUALITY = "code_quality" 
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    TECHNICAL_DEBT = "technical_debt"
    DEPENDENCY_HEALTH = "dependency_health"
    API_STABILITY = "api_stability"
    COMPLEXITY = "complexity"

class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 80-89%
    ACCEPTABLE = "acceptable" # 70-79%
    POOR = "poor"           # 60-69%
    CRITICAL = "critical"   # <60%

@dataclass
class QualityMetric:
    """Individual quality metric"""
    name: str
    type: QualityMetricType
    value: float
    threshold: float
    status: QualityLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    trend: Optional[str] = None  # "improving", "stable", "declining"

@dataclass
class QualityReport:
    """Comprehensive quality report"""
    project_name: str
    version: str
    timestamp: datetime
    overall_score: float
    overall_level: QualityLevel
    metrics: List[QualityMetric]
    recommendations: List[str]
    trend_analysis: Dict[str, Any]
    execution_time: float
    environment: str = "development"

@dataclass
class QualityTrend:
    """Quality trend tracking"""
    metric_name: str
    values: List[float]
    timestamps: List[datetime]
    trend_direction: str  # "up", "down", "stable"
    change_rate: float
    variance: float

class QualityMetricsOrchestrator:
    """
    Master orchestrator for all quality metrics and gates
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize quality metrics orchestrator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config_path = config_path or "config/quality_metrics.yaml"
        self.config = self._load_config()
        self.project_root = Path.cwd()
        self.trends: Dict[str, QualityTrend] = {}
        self.history: List[QualityReport] = []
        
        # Initialize component validators
        self.quality_gate_validator = None
        self.security_scanner = None
        self.doc_validator = None
        
        try:
            self.quality_gate_validator = QualityGateValidator()
            self.security_scanner = SecurityScanEngine()
            self.doc_validator = APIDocumentationValidator()
        except Exception as e:
            self.logger.warning(f"Could not initialize some quality components: {e}")

    def _load_config(self) -> Dict[str, Any]:
        """Load quality metrics configuration"""
        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                self.logger.warning(f"Config file {config_path} not found, using defaults")
                return self._get_default_config()
            
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "quality_gates": {
                "code_coverage": {"enabled": True, "thresholds": {"minimum_coverage": 90.0}},
                "security": {"enabled": True, "vulnerability_thresholds": {"critical": 0, "high": 0}},
                "performance": {"enabled": True, "benchmarks": {"response_time": {"p99_threshold_ms": 1000}}},
                "documentation": {"enabled": True, "thresholds": {"api_documentation": 100.0}},
                "technical_debt": {"enabled": True, "metrics": {"code_duplication": {"max_percentage": 5.0}}},
                "code_complexity": {"enabled": True, "thresholds": {"cyclomatic_complexity": 10}}
            }
        }

    async def run_comprehensive_analysis(
        self, 
        project_path: Optional[str] = None,
        environment: str = "development"
    ) -> QualityReport:
        """Run comprehensive quality analysis"""
        start_time = time.time()
        self.logger.info("Starting comprehensive quality analysis")
        
        project_path = project_path or str(self.project_root)
        metrics = []
        
        try:
            # Run all quality checks in parallel for efficiency
            tasks = []
            
            if self._is_enabled("code_coverage"):
                tasks.append(self._measure_code_coverage(project_path))
            
            if self._is_enabled("security"):
                tasks.append(self._analyze_security_metrics(project_path))
            
            if self._is_enabled("performance"):
                tasks.append(self._benchmark_performance(project_path))
            
            if self._is_enabled("documentation"):
                tasks.append(self._analyze_documentation_coverage(project_path))
            
            if self._is_enabled("technical_debt"):
                tasks.append(self._track_technical_debt(project_path))
            
            if self._is_enabled("code_complexity"):
                tasks.append(self._analyze_code_complexity(project_path))
            
            if self._is_enabled("dependency_scanning"):
                tasks.append(self._scan_dependencies(project_path))
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect metrics from results
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Quality check failed: {result}")
                    continue
                
                if isinstance(result, list):
                    metrics.extend(result)
                elif isinstance(result, QualityMetric):
                    metrics.append(result)
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_score(metrics)
            overall_level = self._determine_quality_level(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics)
            
            # Analyze trends
            trend_analysis = self._analyze_trends(metrics)
            
            # Create comprehensive report
            report = QualityReport(
                project_name="Ainflue",
                version=self._get_project_version(),
                timestamp=datetime.utcnow(),
                overall_score=overall_score,
                overall_level=overall_level,
                metrics=metrics,
                recommendations=recommendations,
                trend_analysis=trend_analysis,
                execution_time=time.time() - start_time,
                environment=environment
            )
            
            # Store report for trend analysis
            self.history.append(report)
            self._update_trends(metrics)
            
            self.logger.info(f"Quality analysis completed. Overall score: {overall_score:.1f}%")
            return report
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")
            raise

    async def _measure_code_coverage(self, project_path: str) -> List[QualityMetric]:
        """Measure code coverage metrics"""
        metrics = []
        
        try:
            # Run pytest with coverage
            cmd = [
                "python", "-m", "pytest", 
                "--cov=.", 
                "--cov-report=json:coverage.json",
                "--cov-report=term-missing",
                "tests/", "--tb=short", "-v"
            ]
            
            result = await self._run_command(cmd, cwd=project_path, timeout=300)
            
            # Parse coverage report
            coverage_file = Path(project_path) / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0.0)
                threshold = self.config["quality_gates"]["code_coverage"]["thresholds"]["minimum_coverage"]
                
                metrics.append(QualityMetric(
                    name="Code Coverage",
                    type=QualityMetricType.CODE_COVERAGE,
                    value=total_coverage,
                    threshold=threshold,
                    status=self._determine_quality_level(total_coverage),
                    message=f"Code coverage: {total_coverage:.1f}% (threshold: {threshold}%)",
                    details=coverage_data
                ))
                
        except Exception as e:
            self.logger.error(f"Code coverage measurement failed: {e}")
            metrics.append(QualityMetric(
                name="Code Coverage",
                type=QualityMetricType.CODE_COVERAGE,
                value=0.0,
                threshold=90.0,
                status=QualityLevel.CRITICAL,
                message=f"Coverage measurement failed: {e}"
            ))
        
        return metrics

    async def _analyze_security_metrics(self, project_path: str) -> List[QualityMetric]:
        """Analyze security metrics"""
        metrics = []
        
        try:
            # Run bandit security scan
            cmd = ["bandit", "-r", ".", "-f", "json", "--exclude", "*/tests/*,*/test_*"]
            result = await self._run_command(cmd, cwd=project_path, timeout=180)
            
            if result.stdout:
                security_data = json.loads(result.stdout)
                issues = security_data.get("results", [])
                
                # Count severity levels
                severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
                for issue in issues:
                    severity = issue.get("issue_severity", "").upper()
                    if severity in severity_counts:
                        severity_counts[severity] += 1
                
                # Calculate security score
                total_issues = sum(severity_counts.values())
                security_score = max(0, 100 - (severity_counts["HIGH"] * 20) - 
                                   (severity_counts["MEDIUM"] * 10) - (severity_counts["LOW"] * 2))
                
                metrics.append(QualityMetric(
                    name="Security Scan",
                    type=QualityMetricType.SECURITY,
                    value=security_score,
                    threshold=80.0,
                    status=self._determine_quality_level(security_score),
                    message=f"Security score: {security_score:.1f}% ({total_issues} issues)",
                    details={"severity_counts": severity_counts, "issues": issues}
                ))
                
        except Exception as e:
            self.logger.error(f"Security analysis failed: {e}")
        
        return metrics

    async def _analyze_code_complexity(self, project_path: str) -> List[QualityMetric]:
        """Analyze code complexity metrics"""
        metrics = []
        
        try:
            # Run radon complexity analysis
            cmd = ["radon", "cc", ".", "--json", "--average"]
            result = await self._run_command(cmd, cwd=project_path, timeout=120)
            
            if result.stdout:
                complexity_data = json.loads(result.stdout)
                
                # Calculate average complexity
                all_complexities = []
                for file_path, functions in complexity_data.items():
                    for func in functions:
                        complexity = func.get("complexity", 0)
                        all_complexities.append(complexity)
                
                if all_complexities:
                    avg_complexity = statistics.mean(all_complexities)
                    max_complexity = max(all_complexities)
                    threshold = self.config["quality_gates"]["code_complexity"]["thresholds"]["cyclomatic_complexity"]
                    
                    # Score based on average complexity (lower is better)
                    complexity_score = max(0, 100 - (avg_complexity - 5) * 10)
                    
                    metrics.append(QualityMetric(
                        name="Code Complexity",
                        type=QualityMetricType.COMPLEXITY,
                        value=complexity_score,
                        threshold=70.0,
                        status=self._determine_quality_level(complexity_score),
                        message=f"Average complexity: {avg_complexity:.1f}, Max: {max_complexity}",
                        details={"avg_complexity": avg_complexity, "max_complexity": max_complexity}
                    ))
                    
        except Exception as e:
            self.logger.error(f"Complexity analysis failed: {e}")
        
        return metrics

    async def _track_technical_debt(self, project_path: str) -> List[QualityMetric]:
        """Track technical debt metrics"""
        metrics = []
        
        try:
            # Count TODO/FIXME/XXX comments
            debt_keywords = ["TODO", "FIXME", "XXX", "HACK"]
            debt_count = 0
            
            for py_file in Path(project_path).rglob("*.py"):
                if "test" in str(py_file) or "__pycache__" in str(py_file):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for keyword in debt_keywords:
                            debt_count += content.upper().count(keyword)
                except:
                    continue
            
            max_debt = self.config["quality_gates"]["technical_debt"]["metrics"]["todo_comments"]["max_count"]
            debt_score = max(0, 100 - (debt_count / max_debt) * 100)
            
            metrics.append(QualityMetric(
                name="Technical Debt",
                type=QualityMetricType.TECHNICAL_DEBT,
                value=debt_score,
                threshold=80.0,
                status=self._determine_quality_level(debt_score),
                message=f"Technical debt items: {debt_count} (max: {max_debt})",
                details={"debt_count": debt_count, "debt_keywords": debt_keywords}
            ))
            
        except Exception as e:
            self.logger.error(f"Technical debt tracking failed: {e}")
        
        return metrics

    async def _scan_dependencies(self, project_path: str) -> List[QualityMetric]:
        """Scan dependencies for vulnerabilities"""
        metrics = []
        
        try:
            # Run safety check
            cmd = ["safety", "check", "--json"]
            result = await self._run_command(cmd, cwd=project_path, timeout=120)
            
            vulnerabilities = 0
            if result.stdout:
                try:
                    safety_data = json.loads(result.stdout)
                    vulnerabilities = len(safety_data)
                except:
                    pass
            
            # Score based on vulnerabilities found
            dependency_score = max(0, 100 - vulnerabilities * 10)
            
            metrics.append(QualityMetric(
                name="Dependency Security",
                type=QualityMetricType.DEPENDENCY_HEALTH,
                value=dependency_score,
                threshold=90.0,
                status=self._determine_quality_level(dependency_score),
                message=f"Dependency vulnerabilities: {vulnerabilities}",
                details={"vulnerability_count": vulnerabilities}
            ))
            
        except Exception as e:
            self.logger.error(f"Dependency scanning failed: {e}")
        
        return metrics

    async def _benchmark_performance(self, project_path: str) -> List[QualityMetric]:
        """Benchmark performance metrics"""
        metrics = []
        
        # For now, create a placeholder metric
        # In a real implementation, this would run actual performance tests
        metrics.append(QualityMetric(
            name="Performance Score",
            type=QualityMetricType.PERFORMANCE,
            value=85.0,
            threshold=80.0,
            status=QualityLevel.GOOD,
            message="Performance benchmarking placeholder",
            details={"note": "Actual performance testing would be implemented here"}
        ))
        
        return metrics

    async def _analyze_documentation_coverage(self, project_path: str) -> List[QualityMetric]:
        """Analyze documentation coverage"""
        metrics = []
        
        try:
            if self.doc_validator:
                report = await self.doc_validator.scan_api_documentation()
                
                metrics.append(QualityMetric(
                    name="API Documentation",
                    type=QualityMetricType.DOCUMENTATION,
                    value=report.coverage_percentage,
                    threshold=100.0,
                    status=self._determine_quality_level(report.coverage_percentage),
                    message=f"API documentation: {report.coverage_percentage:.1f}%",
                    details=asdict(report)
                ))
            else:
                # Fallback: count Python files with docstrings
                total_files = 0
                documented_files = 0
                
                for py_file in Path(project_path).rglob("*.py"):
                    if "test" in str(py_file) or "__pycache__" in str(py_file):
                        continue
                    
                    total_files += 1
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if '"""' in content or "'''" in content:
                                documented_files += 1
                    except:
                        continue
                
                doc_coverage = (documented_files / total_files * 100) if total_files > 0 else 100.0
                
                metrics.append(QualityMetric(
                    name="Code Documentation",
                    type=QualityMetricType.DOCUMENTATION,
                    value=doc_coverage,
                    threshold=80.0,
                    status=self._determine_quality_level(doc_coverage),
                    message=f"Code documentation: {doc_coverage:.1f}%",
                    details={"documented_files": documented_files, "total_files": total_files}
                ))
                
        except Exception as e:
            self.logger.error(f"Documentation analysis failed: {e}")
        
        return metrics

    def _is_enabled(self, gate_name: str) -> bool:
        """Check if quality gate is enabled"""
        return self.config.get("quality_gates", {}).get(gate_name, {}).get("enabled", True)

    def _calculate_overall_score(self, metrics: List[QualityMetric]) -> float:
        """Calculate overall quality score"""
        if not metrics:
            return 0.0
        
        total_score = sum(metric.value for metric in metrics)
        return total_score / len(metrics)

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 80:
            return QualityLevel.GOOD
        elif score >= 70:
            return QualityLevel.ACCEPTABLE
        elif score >= 60:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL

    def _generate_recommendations(self, metrics: List[QualityMetric]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for metric in metrics:
            if metric.status in [QualityLevel.POOR, QualityLevel.CRITICAL]:
                if metric.type == QualityMetricType.CODE_COVERAGE:
                    recommendations.append(f"Increase test coverage for {metric.name} (current: {metric.value:.1f}%)")
                elif metric.type == QualityMetricType.SECURITY:
                    recommendations.append(f"Address security vulnerabilities in {metric.name}")
                elif metric.type == QualityMetricType.COMPLEXITY:
                    recommendations.append(f"Refactor complex code to reduce {metric.name}")
                elif metric.type == QualityMetricType.TECHNICAL_DEBT:
                    recommendations.append(f"Address technical debt items in {metric.name}")
        
        return recommendations

    def _analyze_trends(self, metrics: List[QualityMetric]) -> Dict[str, Any]:
        """Analyze quality trends"""
        if len(self.history) < 2:
            return {"status": "insufficient_data", "message": "Need more data points for trend analysis"}
        
        trends = {}
        for metric in metrics:
            if metric.name in self.trends:
                trend = self.trends[metric.name]
                if len(trend.values) >= 2:
                    recent_change = trend.values[-1] - trend.values[-2]
                    trends[metric.name] = {
                        "direction": "improving" if recent_change > 0 else "declining" if recent_change < 0 else "stable",
                        "change": recent_change,
                        "trend_direction": trend.trend_direction
                    }
        
        return trends

    def _update_trends(self, metrics: List[QualityMetric]):
        """Update trend tracking with new metrics"""
        for metric in metrics:
            if metric.name not in self.trends:
                self.trends[metric.name] = QualityTrend(
                    metric_name=metric.name,
                    values=[],
                    timestamps=[],
                    trend_direction="stable",
                    change_rate=0.0,
                    variance=0.0
                )
            
            trend = self.trends[metric.name]
            trend.values.append(metric.value)
            trend.timestamps.append(metric.timestamp)
            
            # Keep only last 30 data points
            if len(trend.values) > 30:
                trend.values = trend.values[-30:]
                trend.timestamps = trend.timestamps[-30:]
            
            # Calculate trend direction
            if len(trend.values) >= 3:
                recent_values = trend.values[-3:]
                if all(recent_values[i] <= recent_values[i+1] for i in range(len(recent_values)-1)):
                    trend.trend_direction = "up"
                elif all(recent_values[i] >= recent_values[i+1] for i in range(len(recent_values)-1)):
                    trend.trend_direction = "down"
                else:
                    trend.trend_direction = "stable"

    def _get_project_version(self) -> str:
        """Get project version"""
        try:
            # Try to get from git tag
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return "1.0.0"

    async def _run_command(self, cmd: List[str], cwd: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Run command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
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
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="Timeout")
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr=str(e))

    async def generate_report(self, report: QualityReport, format: str = "json") -> str:
        """Generate quality report in specified format"""
        if format == "json":
            return json.dumps(asdict(report), indent=2, default=str)
        elif format == "markdown":
            return self._generate_markdown_report(report)
        elif format == "html":
            return self._generate_html_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_report(self, report: QualityReport) -> str:
        """Generate markdown quality report"""
        md = f"""# Quality Report - {report.project_name} v{report.version}

**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Environment:** {report.environment}  
**Execution Time:** {report.execution_time:.2f}s

## Overall Quality Score: {report.overall_score:.1f}% ({report.overall_level.value.title()})

## Quality Metrics

| Metric | Score | Status | Threshold | Details |
|--------|-------|--------|-----------|---------|
"""
        
        for metric in report.metrics:
            md += f"| {metric.name} | {metric.value:.1f}% | {metric.status.value.title()} | {metric.threshold:.1f}% | {metric.message} |\n"
        
        if report.recommendations:
            md += "\n## Recommendations\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                md += f"{i}. {rec}\n"
        
        return md

    def _generate_html_report(self, report: QualityReport) -> str:
        """Generate HTML quality report"""
        # Simplified HTML report
        return f"""
        <html>
        <head><title>Quality Report - {report.project_name}</title></head>
        <body>
        <h1>Quality Report - {report.project_name} v{report.version}</h1>
        <p><strong>Overall Score:</strong> {report.overall_score:.1f}% ({report.overall_level.value.title()})</p>
        <p><strong>Generated:</strong> {report.timestamp}</p>
        </body>
        </html>
        """

# Global orchestrator instance
quality_orchestrator = QualityMetricsOrchestrator()

__all__ = [
    "QualityMetricsOrchestrator",
    "QualityMetric", 
    "QualityReport",
    "QualityMetricType",
    "QualityLevel",
    "quality_orchestrator"
]