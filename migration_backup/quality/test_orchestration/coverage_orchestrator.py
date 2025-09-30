"""📈 Coverage Orchestrator - Ainflue Platform
================================================================
Expert: TESTING_ARCHITECT + QUALITY_ENGINEER + DEVOPS_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Comprehensive test coverage orchestration system that tracks code coverage,
test effectiveness, and coverage quality across the entire platform.
================================================================
"""

import asyncio
import json
import logging
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import coverage
import statistics
import concurrent.futures
import sqlite3
import tempfile

# Import quality components
try:
    from quality.unit_test_orchestrator import UnitTestOrchestrator, TestResult, TestStatus
    from quality.metrics_orchestrator import QualityMetricsOrchestrator
    HAS_QUALITY_DEPS = True
except ImportError:
    HAS_QUALITY_DEPS = False
    class TestStatus(Enum):
        PASSED = "passed"
        FAILED = "failed"
        SKIPPED = "skipped"

logger = logging.getLogger(__name__)

class CoverageType(Enum):
    """Types of coverage measurement"""
    LINE_COVERAGE = "line_coverage"
    BRANCH_COVERAGE = "branch_coverage"
    FUNCTION_COVERAGE = "function_coverage"
    CLASS_COVERAGE = "class_coverage"
    STATEMENT_COVERAGE = "statement_coverage"
    CONDITION_COVERAGE = "condition_coverage"
    PATH_COVERAGE = "path_coverage"

class CoverageLevel(Enum):
    """Coverage quality levels"""
    EXCELLENT = "excellent"    # 90-100%
    GOOD = "good"             # 80-89%
    ACCEPTABLE = "acceptable" # 70-79%
    POOR = "poor"            # 50-69%
    CRITICAL = "critical"     # <50%

class TestType(Enum):
    """Types of tests contributing to coverage"""
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    FUNCTIONAL_TEST = "functional_test"
    E2E_TEST = "e2e_test"
    MANUAL_TEST = "manual_test"

@dataclass
class CoverageMetric:
    """Individual coverage metric"""
    file_path: str
    line_coverage: float
    branch_coverage: float
    function_coverage: float
    statement_coverage: float
    total_lines: int
    covered_lines: int
    missed_lines: List[int] = field(default_factory=list)
    partial_lines: List[int] = field(default_factory=list)
    excluded_lines: List[int] = field(default_factory=list)
    complexity_score: float = 0.0
    test_types: Set[TestType] = field(default_factory=set)

@dataclass
class ModuleCoverage:
    """Coverage metrics for a module/package"""
    module_name: str
    module_path: str
    file_metrics: List[CoverageMetric]
    overall_coverage: float
    line_coverage: float
    branch_coverage: float
    function_coverage: float
    test_count: int
    critical_paths_covered: bool = False
    coverage_trend: Optional[str] = None
    risk_score: float = 0.0

@dataclass
class CoverageReport:
    """Comprehensive coverage report"""
    project_name: str
    report_timestamp: datetime
    overall_coverage: float
    line_coverage: float
    branch_coverage: float
    function_coverage: float
    total_lines: int
    covered_lines: int
    total_statements: int
    covered_statements: int
    total_branches: int
    covered_branches: int
    total_functions: int
    covered_functions: int
    module_coverages: List[ModuleCoverage]
    uncovered_hotspots: List[Dict[str, Any]]
    coverage_gaps: List[Dict[str, Any]]
    quality_score: float
    recommendations: List[str]
    execution_time: float
    test_execution_stats: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CoverageTrend:
    """Coverage trend tracking"""
    metric_name: str
    values: List[float]
    timestamps: List[datetime]
    trend_direction: str  # "improving", "declining", "stable"
    change_rate: float
    target_coverage: float

class CoverageOrchestrator:
    """
    Orchestrates comprehensive test coverage analysis and reporting
    """
    
    def __init__(self, project_root: Optional[str] = None, config_path: Optional[str] = None):
        """Initialize coverage orchestrator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.config_path = config_path or "config/coverage.json"
        self.config = self._load_config()
        
        # Coverage tracking
        self.coverage_data: Dict[str, CoverageMetric] = {}
        self.historical_data: List[CoverageReport] = []
        self.trends: Dict[str, CoverageTrend] = {}
        
        # Initialize coverage.py instance
        self.coverage_instance = coverage.Coverage(
            source=[str(self.project_root)],
            omit=self.config.get("omit_patterns", [
                "*/tests/*", "*/test_*", "*/__pycache__/*", 
                "*/migrations/*", "*/venv/*", "*/env/*"
            ]),
            config_file=self.config.get("coverage_config", ".coveragerc")
        )
        
        # Database for historical tracking
        self.db_path = self.project_root / ".coverage_history.db"
        self._init_database()
        
        # Initialize quality components
        if HAS_QUALITY_DEPS:
            try:
                self.unit_test_orchestrator = UnitTestOrchestrator(str(self.project_root))
                self.quality_orchestrator = QualityMetricsOrchestrator()
            except Exception as e:
                self.logger.warning(f"Could not initialize quality components: {e}")
                self.unit_test_orchestrator = None
                self.quality_orchestrator = None

    def _load_config(self) -> Dict[str, Any]:
        """Load coverage configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default coverage configuration"""
        return {
            "target_coverage": {
                "overall": 80.0,
                "line": 85.0,
                "branch": 75.0,
                "function": 90.0
            },
            "critical_paths": [
                "core/**/*.py",
                "api/**/*.py", 
                "security/**/*.py",
                "payment/**/*.py"
            ],
            "omit_patterns": [
                "*/tests/*",
                "*/test_*",
                "*/__pycache__/*",
                "*/migrations/*",
                "*/venv/*",
                "*/env/*",
                "*/build/*",
                "*/dist/*"
            ],
            "include_patterns": [
                "**/*.py"
            ],
            "fail_under": 80.0,
            "precision": 2,
            "skip_covered": False,
            "show_missing": True,
            "sort": "Cover",
            "report_formats": ["json", "xml", "html", "markdown"]
        }

    def _init_database(self):
        """Initialize SQLite database for historical tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS coverage_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        overall_coverage REAL,
                        line_coverage REAL,
                        branch_coverage REAL,
                        function_coverage REAL,
                        total_lines INTEGER,
                        covered_lines INTEGER,
                        module_count INTEGER,
                        test_count INTEGER,
                        execution_time REAL,
                        commit_hash TEXT,
                        branch_name TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error initializing coverage database: {e}")

    async def run_comprehensive_coverage_analysis(self, 
                                                 test_suites: Optional[List[str]] = None,
                                                 include_integration: bool = True,
                                                 generate_reports: bool = True) -> CoverageReport:
        """Run comprehensive coverage analysis"""
        start_time = time.time()
        self.logger.info("Starting comprehensive coverage analysis")
        
        try:
            # Start coverage measurement
            self.coverage_instance.start()
            
            # Run tests and collect coverage
            test_stats = await self._run_tests_with_coverage(test_suites, include_integration)
            
            # Stop coverage measurement
            self.coverage_instance.stop()
            self.coverage_instance.save()
            
            # Analyze coverage data
            coverage_data = await self._analyze_coverage_data()
            
            # Generate module-level metrics
            module_coverages = await self._analyze_module_coverage()
            
            # Identify coverage gaps and hotspots
            gaps, hotspots = await self._identify_coverage_issues(coverage_data)
            
            # Calculate quality metrics
            quality_score = self._calculate_coverage_quality_score(coverage_data, module_coverages)
            
            # Generate recommendations
            recommendations = self._generate_coverage_recommendations(coverage_data, gaps, hotspots)
            
            # Create comprehensive report
            report = CoverageReport(
                project_name=self.project_root.name,
                report_timestamp=datetime.utcnow(),
                overall_coverage=coverage_data.get("overall_coverage", 0.0),
                line_coverage=coverage_data.get("line_coverage", 0.0),
                branch_coverage=coverage_data.get("branch_coverage", 0.0),
                function_coverage=coverage_data.get("function_coverage", 0.0),
                total_lines=coverage_data.get("total_lines", 0),
                covered_lines=coverage_data.get("covered_lines", 0),
                total_statements=coverage_data.get("total_statements", 0),
                covered_statements=coverage_data.get("covered_statements", 0),
                total_branches=coverage_data.get("total_branches", 0),
                covered_branches=coverage_data.get("covered_branches", 0),
                total_functions=coverage_data.get("total_functions", 0),
                covered_functions=coverage_data.get("covered_functions", 0),
                module_coverages=module_coverages,
                uncovered_hotspots=hotspots,
                coverage_gaps=gaps,
                quality_score=quality_score,
                recommendations=recommendations,
                execution_time=time.time() - start_time,
                test_execution_stats=test_stats
            )
            
            # Store historical data
            await self._store_historical_data(report)
            
            # Generate reports if requested
            if generate_reports:
                await self._generate_coverage_reports(report)
            
            self.logger.info(
                f"Coverage analysis completed. "
                f"Overall: {report.overall_coverage:.1f}%, "
                f"Line: {report.line_coverage:.1f}%, "
                f"Branch: {report.branch_coverage:.1f}%"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Coverage analysis failed: {e}")
            raise
        finally:
            # Ensure coverage is stopped
            try:
                self.coverage_instance.stop()
            except:
                pass

    async def _run_tests_with_coverage(self, test_suites: Optional[List[str]], 
                                     include_integration: bool) -> Dict[str, Any]:
        """Run tests while collecting coverage data"""
        test_stats = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "execution_time": 0.0,
            "test_types": []
        }
        
        if self.unit_test_orchestrator:
            # Use orchestrator to run tests
            self.logger.info("Running tests through unit test orchestrator")
            test_report = await self.unit_test_orchestrator.orchestrate_all_tests(
                suite_names=test_suites,
                coverage_enabled=False  # We're handling coverage ourselves
            )
            
            test_stats.update({
                "total_tests": test_report.total_tests,
                "passed_tests": test_report.passed_tests,
                "failed_tests": test_report.failed_tests,
                "skipped_tests": test_report.skipped_tests,
                "execution_time": test_report.total_duration
            })
        else:
            # Run tests directly
            self.logger.info("Running tests directly with pytest")
            await self._run_pytest_with_coverage()
        
        return test_stats

    async def _run_pytest_with_coverage(self):
        """Run pytest directly with coverage"""
        cmd = [
            "python", "-m", "pytest",
            "--tb=short",
            "-v",
            "tests/"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.warning(f"Some tests failed during coverage analysis")
                
        except Exception as e:
            self.logger.error(f"Error running pytest: {e}")

    async def _analyze_coverage_data(self) -> Dict[str, Any]:
        """Analyze collected coverage data"""
        try:
            # Get coverage data
            coverage_data = self.coverage_instance.get_data()
            
            # Calculate overall metrics
            total_lines = 0
            covered_lines = 0
            total_statements = 0
            covered_statements = 0
            total_branches = 0
            covered_branches = 0
            total_functions = 0
            covered_functions = 0
            
            file_metrics = {}
            
            for filename in coverage_data.measured_files():
                try:
                    # Get file analysis
                    analysis = self.coverage_instance._analyze(filename)
                    
                    # Line coverage
                    file_total_lines = len(analysis.statements)
                    file_covered_lines = len(analysis.statements - analysis.missing)
                    
                    total_lines += file_total_lines
                    covered_lines += file_covered_lines
                    
                    # Statement coverage (same as line for most cases)
                    total_statements += file_total_lines
                    covered_statements += file_covered_lines
                    
                    # Branch coverage (if available)
                    if hasattr(analysis, 'branch_lines'):
                        file_total_branches = len(analysis.branch_lines())
                        file_covered_branches = len(analysis.branch_lines() - analysis.missing_branch_arcs())
                        total_branches += file_total_branches
                        covered_branches += file_covered_branches
                    
                    # Store file metrics
                    file_metrics[filename] = {
                        "total_lines": file_total_lines,
                        "covered_lines": file_covered_lines,
                        "missing_lines": list(analysis.missing),
                        "excluded_lines": list(analysis.excluded),
                        "line_coverage": (file_covered_lines / file_total_lines * 100) if file_total_lines > 0 else 0
                    }
                    
                except Exception as e:
                    self.logger.warning(f"Error analyzing file {filename}: {e}")
                    continue
            
            # Calculate overall percentages
            overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            line_coverage = overall_coverage
            branch_coverage = (covered_branches / total_branches * 100) if total_branches > 0 else 0
            
            return {
                "overall_coverage": overall_coverage,
                "line_coverage": line_coverage,
                "branch_coverage": branch_coverage,
                "function_coverage": 0.0,  # Would need AST analysis
                "total_lines": total_lines,
                "covered_lines": covered_lines,
                "total_statements": total_statements,
                "covered_statements": covered_statements,
                "total_branches": total_branches,
                "covered_branches": covered_branches,
                "total_functions": total_functions,
                "covered_functions": covered_functions,
                "file_metrics": file_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing coverage data: {e}")
            return {}

    async def _analyze_module_coverage(self) -> List[ModuleCoverage]:
        """Analyze coverage at module level"""
        module_coverages = []
        
        # Group files by module/package
        modules = {}
        
        for file_path in self.coverage_instance.get_data().measured_files():
            rel_path = Path(file_path).relative_to(self.project_root)
            
            # Determine module name
            if len(rel_path.parts) > 1:
                module_name = rel_path.parts[0]
            else:
                module_name = "root"
            
            if module_name not in modules:
                modules[module_name] = []
            modules[module_name].append(str(rel_path))
        
        # Calculate coverage for each module
        for module_name, files in modules.items():
            module_metrics = []
            total_lines = 0
            covered_lines = 0
            
            for file_path in files:
                try:
                    full_path = self.project_root / file_path
                    analysis = self.coverage_instance._analyze(str(full_path))
                    
                    file_total = len(analysis.statements)
                    file_covered = len(analysis.statements - analysis.missing)
                    
                    total_lines += file_total
                    covered_lines += file_covered
                    
                    metric = CoverageMetric(
                        file_path=file_path,
                        line_coverage=(file_covered / file_total * 100) if file_total > 0 else 0,
                        branch_coverage=0.0,  # Would need detailed analysis
                        function_coverage=0.0,
                        statement_coverage=(file_covered / file_total * 100) if file_total > 0 else 0,
                        total_lines=file_total,
                        covered_lines=file_covered,
                        missed_lines=list(analysis.missing),
                        excluded_lines=list(analysis.excluded)
                    )
                    module_metrics.append(metric)
                    
                except Exception as e:
                    self.logger.warning(f"Error analyzing file {file_path}: {e}")
                    continue
            
            overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            
            module_coverage = ModuleCoverage(
                module_name=module_name,
                module_path=module_name,
                file_metrics=module_metrics,
                overall_coverage=overall_coverage,
                line_coverage=overall_coverage,
                branch_coverage=0.0,
                function_coverage=0.0,
                test_count=0,  # Would need test discovery
                risk_score=self._calculate_module_risk_score(module_metrics, overall_coverage)
            )
            
            module_coverages.append(module_coverage)
        
        return module_coverages

    def _calculate_module_risk_score(self, metrics: List[CoverageMetric], 
                                   overall_coverage: float) -> float:
        """Calculate risk score for a module based on coverage and complexity"""
        # Base risk from low coverage
        coverage_risk = max(0, 100 - overall_coverage) / 100
        
        # Risk from large uncovered files
        large_uncovered_files = len([m for m in metrics 
                                   if m.total_lines > 100 and m.line_coverage < 50])
        size_risk = min(1.0, large_uncovered_files / 10)
        
        # Combined risk score (0-100)
        return (coverage_risk * 0.7 + size_risk * 0.3) * 100

    async def _identify_coverage_issues(self, coverage_data: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """Identify coverage gaps and uncovered hotspots"""
        gaps = []
        hotspots = []
        
        file_metrics = coverage_data.get("file_metrics", {})
        
        for file_path, metrics in file_metrics.items():
            coverage_pct = metrics["line_coverage"]
            total_lines = metrics["total_lines"]
            missing_lines = metrics["missing_lines"]
            
            # Identify gaps (low coverage files)
            if coverage_pct < self.config["target_coverage"]["line"] and total_lines > 10:
                gaps.append({
                    "file": file_path,
                    "coverage": coverage_pct,
                    "missing_lines": len(missing_lines),
                    "total_lines": total_lines,
                    "severity": "high" if coverage_pct < 50 else "medium"
                })
            
            # Identify hotspots (large uncovered sections)
            if len(missing_lines) > 20:
                hotspots.append({
                    "file": file_path,
                    "uncovered_lines": len(missing_lines),
                    "coverage": coverage_pct,
                    "priority": "high" if total_lines > 100 else "medium"
                })
        
        # Sort by severity/priority
        gaps.sort(key=lambda x: (x["severity"] == "high", -x["coverage"]))
        hotspots.sort(key=lambda x: -x["uncovered_lines"])
        
        return gaps[:10], hotspots[:10]  # Top 10 of each

    def _calculate_coverage_quality_score(self, coverage_data: Dict[str, Any], 
                                        module_coverages: List[ModuleCoverage]) -> float:
        """Calculate overall coverage quality score"""
        overall_coverage = coverage_data.get("overall_coverage", 0)
        line_coverage = coverage_data.get("line_coverage", 0)
        branch_coverage = coverage_data.get("branch_coverage", 0)
        
        # Base score from coverage percentages
        coverage_score = (
            overall_coverage * 0.4 +
            line_coverage * 0.3 +
            branch_coverage * 0.3
        )
        
        # Penalty for modules with very low coverage
        low_coverage_modules = len([m for m in module_coverages if m.overall_coverage < 50])
        module_penalty = min(20, low_coverage_modules * 5)
        
        # Bonus for high coverage across all modules
        high_coverage_modules = len([m for m in module_coverages if m.overall_coverage > 90])
        module_bonus = min(10, high_coverage_modules * 2)
        
        # Final quality score
        quality_score = max(0, min(100, coverage_score - module_penalty + module_bonus))
        
        return quality_score

    def _generate_coverage_recommendations(self, coverage_data: Dict[str, Any],
                                         gaps: List[Dict], hotspots: List[Dict]) -> List[str]:
        """Generate coverage improvement recommendations"""
        recommendations = []
        
        overall_coverage = coverage_data.get("overall_coverage", 0)
        target_coverage = self.config["target_coverage"]["overall"]
        
        # Overall coverage recommendations
        if overall_coverage < target_coverage:
            shortfall = target_coverage - overall_coverage
            recommendations.append(
                f"Increase overall coverage by {shortfall:.1f}% to reach target of {target_coverage}%"
            )
        
        # Gap-specific recommendations
        if gaps:
            high_priority_gaps = [g for g in gaps[:5] if g["severity"] == "high"]
            if high_priority_gaps:
                recommendations.append(
                    f"Prioritize testing for {len(high_priority_gaps)} files with critical coverage gaps"
                )
        
        # Hotspot recommendations
        if hotspots:
            large_hotspots = [h for h in hotspots[:3] if h["uncovered_lines"] > 50]
            if large_hotspots:
                recommendations.append(
                    f"Focus on {len(large_hotspots)} files with large uncovered sections"
                )
        
        # Branch coverage recommendations
        branch_coverage = coverage_data.get("branch_coverage", 0)
        if branch_coverage < 70:
            recommendations.append("Improve branch coverage by adding tests for edge cases and error conditions")
        
        # Module-specific recommendations
        if len(gaps) > 10:
            recommendations.append("Consider implementing coverage gates in CI/CD to prevent coverage regression")
        
        return recommendations

    async def _store_historical_data(self, report: CoverageReport):
        """Store coverage data for trend analysis"""
        try:
            # Get git info
            commit_hash = ""
            branch_name = ""
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"], 
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    commit_hash = result.stdout.strip()
                
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    branch_name = result.stdout.strip()
            except:
                pass
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO coverage_history (
                        timestamp, overall_coverage, line_coverage, branch_coverage,
                        function_coverage, total_lines, covered_lines, module_count,
                        test_count, execution_time, commit_hash, branch_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.report_timestamp.isoformat(),
                    report.overall_coverage,
                    report.line_coverage,
                    report.branch_coverage,
                    report.function_coverage,
                    report.total_lines,
                    report.covered_lines,
                    len(report.module_coverages),
                    report.test_execution_stats.get("total_tests", 0),
                    report.execution_time,
                    commit_hash,
                    branch_name
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing historical data: {e}")

    async def _generate_coverage_reports(self, report: CoverageReport):
        """Generate coverage reports in multiple formats"""
        reports_dir = self.project_root / "coverage_reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = report.report_timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Generate JSON report
        json_report = self.generate_report(report, "json")
        with open(reports_dir / f"coverage_report_{timestamp}.json", "w") as f:
            f.write(json_report)
        
        # Generate Markdown report
        md_report = self.generate_report(report, "markdown")
        with open(reports_dir / f"coverage_report_{timestamp}.md", "w") as f:
            f.write(md_report)
        
        # Generate HTML report using coverage.py
        try:
            html_dir = reports_dir / f"html_{timestamp}"
            self.coverage_instance.html_report(directory=str(html_dir))
        except Exception as e:
            self.logger.warning(f"Could not generate HTML report: {e}")
        
        # Generate XML report for CI/CD integration
        try:
            xml_file = reports_dir / f"coverage_{timestamp}.xml"
            self.coverage_instance.xml_report(outfile=str(xml_file))
        except Exception as e:
            self.logger.warning(f"Could not generate XML report: {e}")

    def generate_report(self, report: CoverageReport, format: str = "json") -> str:
        """Generate coverage report in specified format"""
        if format == "json":
            return self._generate_json_report(report)
        elif format == "markdown":
            return self._generate_markdown_report(report)
        elif format == "html":
            return self._generate_html_report(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_json_report(self, report: CoverageReport) -> str:
        """Generate JSON coverage report"""
        # Convert to serializable format
        data = {
            "project_name": report.project_name,
            "timestamp": report.report_timestamp.isoformat(),
            "summary": {
                "overall_coverage": report.overall_coverage,
                "line_coverage": report.line_coverage,
                "branch_coverage": report.branch_coverage,
                "function_coverage": report.function_coverage,
                "quality_score": report.quality_score,
                "execution_time": report.execution_time
            },
            "statistics": {
                "total_lines": report.total_lines,
                "covered_lines": report.covered_lines,
                "total_statements": report.total_statements,
                "covered_statements": report.covered_statements,
                "total_branches": report.total_branches,
                "covered_branches": report.covered_branches
            },
            "modules": [
                {
                    "name": module.module_name,
                    "coverage": module.overall_coverage,
                    "files": len(module.file_metrics),
                    "risk_score": module.risk_score
                }
                for module in report.module_coverages
            ],
            "coverage_gaps": report.coverage_gaps[:5],
            "hotspots": report.uncovered_hotspots[:5],
            "recommendations": report.recommendations,
            "test_stats": report.test_execution_stats
        }
        
        return json.dumps(data, indent=2)

    def _generate_markdown_report(self, report: CoverageReport) -> str:
        """Generate Markdown coverage report"""
        
        # Determine overall status
        if report.overall_coverage >= 90:
            status_emoji = "🟢"
            status_text = "Excellent"
        elif report.overall_coverage >= 80:
            status_emoji = "🟡"
            status_text = "Good"
        elif report.overall_coverage >= 70:
            status_emoji = "🟠"
            status_text = "Acceptable"
        else:
            status_emoji = "🔴"
            status_text = "Needs Improvement"
        
        md = f"""# Coverage Report - {report.project_name} {status_emoji}

**Status:** {status_text}  
**Generated:** {report.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Quality Score:** {report.quality_score:.1f}%  
**Execution Time:** {report.execution_time:.2f}s

## Summary

| Metric | Coverage | Target | Status |
|--------|----------|--------|--------|
| Overall | {report.overall_coverage:.1f}% | {self.config['target_coverage']['overall']}% | {'✅' if report.overall_coverage >= self.config['target_coverage']['overall'] else '❌'} |
| Lines | {report.line_coverage:.1f}% | {self.config['target_coverage']['line']}% | {'✅' if report.line_coverage >= self.config['target_coverage']['line'] else '❌'} |
| Branches | {report.branch_coverage:.1f}% | {self.config['target_coverage']['branch']}% | {'✅' if report.branch_coverage >= self.config['target_coverage']['branch'] else '❌'} |
| Functions | {report.function_coverage:.1f}% | {self.config['target_coverage']['function']}% | {'✅' if report.function_coverage >= self.config['target_coverage']['function'] else '❌'} |

## Statistics

| Metric | Count |
|--------|-------|
| Total Lines | {report.total_lines:,} |
| Covered Lines | {report.covered_lines:,} |
| Total Statements | {report.total_statements:,} |
| Covered Statements | {report.covered_statements:,} |
| Total Branches | {report.total_branches:,} |
| Covered Branches | {report.covered_branches:,} |

## Module Coverage

| Module | Coverage | Files | Risk Score |
|--------|----------|-------|------------|
"""
        
        for module in sorted(report.module_coverages, key=lambda m: m.overall_coverage):
            risk_emoji = "🔴" if module.risk_score > 70 else "🟡" if module.risk_score > 30 else "🟢"
            md += f"| {module.module_name} | {module.overall_coverage:.1f}% | {len(module.file_metrics)} | {risk_emoji} {module.risk_score:.1f} |\n"
        
        if report.coverage_gaps:
            md += "\n## Coverage Gaps\n\n"
            for gap in report.coverage_gaps[:5]:
                severity_emoji = "🔴" if gap["severity"] == "high" else "🟡"
                md += f"- {severity_emoji} **{gap['file']}**: {gap['coverage']:.1f}% coverage ({gap['missing_lines']} uncovered lines)\n"
        
        if report.uncovered_hotspots:
            md += "\n## Uncovered Hotspots\n\n"
            for hotspot in report.uncovered_hotspots[:5]:
                priority_emoji = "🔥" if hotspot["priority"] == "high" else "⚠️"
                md += f"- {priority_emoji} **{hotspot['file']}**: {hotspot['uncovered_lines']} uncovered lines\n"
        
        if report.recommendations:
            md += "\n## Recommendations\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                md += f"{i}. {rec}\n"
        
        return md

    def _generate_html_report(self, report: CoverageReport) -> str:
        """Generate HTML coverage report"""
        status_color = (
            "green" if report.overall_coverage >= 90 else
            "orange" if report.overall_coverage >= 70 else
            "red"
        )
        
        return f"""
        <html>
        <head>
            <title>Coverage Report - {report.project_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #{status_color}; color: white; padding: 10px; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Coverage Report - {report.project_name}</h1>
            <div class="summary">
                <h2>Overall Coverage: {report.overall_coverage:.1f}%</h2>
                <p>Quality Score: {report.quality_score:.1f}%</p>
                <p>Generated: {report.report_timestamp}</p>
            </div>
            
            <h3>Coverage Breakdown</h3>
            <table>
                <tr><th>Metric</th><th>Coverage</th><th>Count</th></tr>
                <tr><td>Lines</td><td>{report.line_coverage:.1f}%</td><td>{report.covered_lines:,} / {report.total_lines:,}</td></tr>
                <tr><td>Branches</td><td>{report.branch_coverage:.1f}%</td><td>{report.covered_branches:,} / {report.total_branches:,}</td></tr>
                <tr><td>Functions</td><td>{report.function_coverage:.1f}%</td><td>{report.covered_functions:,} / {report.total_functions:,}</td></tr>
            </table>
        </body>
        </html>
        """

    async def get_coverage_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get coverage trends over specified period"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, overall_coverage, line_coverage, branch_coverage
                    FROM coverage_history
                    WHERE timestamp > datetime('now', '-{} days')
                    ORDER BY timestamp
                """.format(days))
                
                rows = cursor.fetchall()
                
                if len(rows) < 2:
                    return {"status": "insufficient_data", "message": "Need more historical data"}
                
                # Calculate trends
                timestamps = [datetime.fromisoformat(row[0]) for row in rows]
                overall_values = [row[1] for row in rows]
                line_values = [row[2] for row in rows]
                branch_values = [row[3] for row in rows]
                
                trends = {
                    "overall_coverage": {
                        "current": overall_values[-1],
                        "previous": overall_values[0],
                        "change": overall_values[-1] - overall_values[0],
                        "trend": "improving" if overall_values[-1] > overall_values[0] else "declining"
                    },
                    "line_coverage": {
                        "current": line_values[-1],
                        "previous": line_values[0], 
                        "change": line_values[-1] - line_values[0],
                        "trend": "improving" if line_values[-1] > line_values[0] else "declining"
                    },
                    "branch_coverage": {
                        "current": branch_values[-1],
                        "previous": branch_values[0],
                        "change": branch_values[-1] - branch_values[0],
                        "trend": "improving" if branch_values[-1] > branch_values[0] else "declining"
                    }
                }
                
                return trends
                
        except Exception as e:
            self.logger.error(f"Error getting coverage trends: {e}")
            return {"status": "error", "message": str(e)}

    async def cleanup(self):
        """Cleanup resources"""
        try:
            self.coverage_instance.stop()
        except:
            pass

# Global coverage orchestrator instance
coverage_orchestrator = CoverageOrchestrator()

__all__ = [
    "CoverageOrchestrator",
    "CoverageMetric",
    "ModuleCoverage",
    "CoverageReport",
    "CoverageTrend",
    "CoverageType",
    "CoverageLevel",
    "TestType",
    "coverage_orchestrator"
]