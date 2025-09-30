"""🚪 Pre-Commit Gate Orchestrator - Ainflue Platform
================================================================
Expert: QUALITY_ENGINEER + DEVOPS_ENGINEER + SECURITY_ENGINEER
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Orchestrates pre-commit quality gates to ensure code quality before commits.
Integrates with Git hooks, runs automated checks, and enforces quality standards.
================================================================
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class GateStatus(Enum):
    """Pre-commit gate status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"

class GateSeverity(Enum):
    """Gate failure severity"""
    BLOCKING = "blocking"      # Prevents commit
    WARNING = "warning"        # Allows commit with warning
    INFORMATIONAL = "info"     # Just logs information

class GateCategory(Enum):
    """Categories of pre-commit gates"""
    CODE_STYLE = "code_style"
    LINTING = "linting"
    TYPE_CHECKING = "type_checking"
    SECURITY = "security"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    DEPENDENCIES = "dependencies"
    COMMIT_MESSAGE = "commit_message"
    FILE_STRUCTURE = "file_structure"

@dataclass
class GateRule:
    """Pre-commit gate rule definition"""
    name: str
    category: GateCategory
    severity: GateSeverity
    command: str
    file_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    timeout_seconds: int = 60
    retry_count: int = 0
    depends_on: List[str] = field(default_factory=list)
    enabled: bool = True
    description: str = ""

@dataclass
class GateResult:
    """Result of a pre-commit gate execution"""
    gate_name: str
    status: GateStatus
    severity: GateSeverity
    category: GateCategory
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    files_checked: List[str] = field(default_factory=list)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PreCommitReport:
    """Pre-commit gate execution report"""
    total_gates: int
    passed_gates: int
    failed_gates: int
    warning_gates: int
    skipped_gates: int
    total_duration: float
    commit_allowed: bool
    gate_results: List[GateResult]
    file_summary: Dict[str, Any]
    overall_metrics: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class PreCommitGateOrchestrator:
    """
    Orchestrates pre-commit quality gates
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize pre-commit gate orchestrator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.gate_rules: Dict[str, GateRule] = {}
        self.execution_history: List[PreCommitReport] = []
        
        # Initialize default gate rules
        self._initialize_default_gates()

    def _initialize_default_gates(self):
        """Initialize default pre-commit gate rules"""
        
        # Code style gates
        self.gate_rules["black_formatter"] = GateRule(
            name="black_formatter",
            category=GateCategory.CODE_STYLE,
            severity=GateSeverity.BLOCKING,
            command="black --check --diff",
            file_patterns=["*.py"],
            description="Check Python code formatting with Black"
        )
        
        self.gate_rules["isort_imports"] = GateRule(
            name="isort_imports",
            category=GateCategory.CODE_STYLE,
            severity=GateSeverity.BLOCKING,
            command="isort --check-only --diff",
            file_patterns=["*.py"],
            description="Check import sorting with isort"
        )
        
        # Linting gates
        self.gate_rules["flake8_linting"] = GateRule(
            name="flake8_linting",
            category=GateCategory.LINTING,
            severity=GateSeverity.WARNING,
            command="flake8 --statistics",
            file_patterns=["*.py"],
            description="Check code with flake8 linter"
        )
        
        self.gate_rules["pylint_analysis"] = GateRule(
            name="pylint_analysis",
            category=GateCategory.LINTING,
            severity=GateSeverity.WARNING,
            command="pylint --score=yes --reports=yes",
            file_patterns=["*.py"],
            exclude_patterns=["**/tests/**", "**/test_*.py"],
            description="Analyze code with pylint"
        )
        
        # Type checking gates
        self.gate_rules["mypy_types"] = GateRule(
            name="mypy_types",
            category=GateCategory.TYPE_CHECKING,
            severity=GateSeverity.WARNING,
            command="mypy --strict",
            file_patterns=["*.py"],
            exclude_patterns=["**/tests/**"],
            description="Check types with mypy"
        )
        
        # Security gates
        self.gate_rules["bandit_security"] = GateRule(
            name="bandit_security",
            category=GateCategory.SECURITY,
            severity=GateSeverity.BLOCKING,
            command="bandit -f json",
            file_patterns=["*.py"],
            exclude_patterns=["**/tests/**"],
            description="Security analysis with bandit"
        )
        
        self.gate_rules["safety_dependencies"] = GateRule(
            name="safety_dependencies",
            category=GateCategory.SECURITY,
            severity=GateSeverity.WARNING,
            command="safety check --json",
            file_patterns=["requirements*.txt", "setup.py", "pyproject.toml"],
            description="Check dependencies for security vulnerabilities"
        )
        
        # Testing gates
        self.gate_rules["pytest_tests"] = GateRule(
            name="pytest_tests",
            category=GateCategory.TESTING,
            severity=GateSeverity.BLOCKING,
            command="pytest --tb=short -q",
            file_patterns=["test_*.py", "**/tests/**/*.py"],
            timeout_seconds=300,
            description="Run unit tests with pytest"
        )
        
        # Documentation gates
        self.gate_rules["docstring_coverage"] = GateRule(
            name="docstring_coverage",
            category=GateCategory.DOCUMENTATION,
            severity=GateSeverity.INFORMATIONAL,
            command="docstring-coverage --badge=svg",
            file_patterns=["*.py"],
            exclude_patterns=["**/tests/**"],
            description="Check docstring coverage"
        )
        
        # Commit message gate
        self.gate_rules["commit_message_format"] = GateRule(
            name="commit_message_format",
            category=GateCategory.COMMIT_MESSAGE,
            severity=GateSeverity.BLOCKING,
            command="internal_commit_message_check",
            description="Validate commit message format"
        )
        
        # File structure gates
        self.gate_rules["file_size_limit"] = GateRule(
            name="file_size_limit",
            category=GateCategory.FILE_STRUCTURE,
            severity=GateSeverity.WARNING,
            command="internal_file_size_check",
            description="Check file size limits"
        )
        
        self.gate_rules["filename_conventions"] = GateRule(
            name="filename_conventions",
            category=GateCategory.FILE_STRUCTURE,
            severity=GateSeverity.WARNING,
            command="internal_filename_check",
            description="Check filename conventions"
        )

    async def run_pre_commit_gates(
        self,
        staged_files: Optional[List[str]] = None,
        gate_filter: Optional[List[str]] = None,
        fail_fast: bool = True,
        commit_message: Optional[str] = None
    ) -> PreCommitReport:
        """Run pre-commit gates on staged files"""
        self.logger.info("Starting pre-commit gate execution")
        start_time = time.time()
        
        # Get staged files if not provided
        if staged_files is None:
            staged_files = await self._get_staged_files()
        
        # Filter applicable gates
        applicable_gates = self._filter_applicable_gates(staged_files, gate_filter)
        
        if not applicable_gates:
            self.logger.info("No applicable gates found for staged files")
            return PreCommitReport(
                total_gates=0,
                passed_gates=0,
                failed_gates=0,
                warning_gates=0,
                skipped_gates=0,
                total_duration=0.0,
                commit_allowed=True,
                gate_results=[],
                file_summary={"staged_files": len(staged_files)},
                overall_metrics={},
                recommendations=[]
            )
        
        try:
            # Execute gates
            gate_results = await self._execute_gates(
                applicable_gates, staged_files, fail_fast, commit_message
            )
            
            # Generate report
            report = self._generate_report(
                applicable_gates, gate_results, staged_files, time.time() - start_time
            )
            
            # Store in history
            self.execution_history.append(report)
            
            self.logger.info(
                f"Pre-commit gates completed. "
                f"Passed: {report.passed_gates}/{report.total_gates}, "
                f"Commit allowed: {report.commit_allowed}"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Pre-commit gate execution failed: {e}")
            raise

    async def _get_staged_files(self) -> List[str]:
        """Get list of staged files from git"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
                return files
            else:
                self.logger.warning("Could not get staged files, using empty list")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting staged files: {e}")
            return []

    def _filter_applicable_gates(
        self, 
        staged_files: List[str], 
        gate_filter: Optional[List[str]]
    ) -> List[str]:
        """Filter gates applicable to staged files"""
        applicable_gates = []
        
        for gate_name, gate_rule in self.gate_rules.items():
            # Skip disabled gates
            if not gate_rule.enabled:
                continue
            
            # Apply gate filter
            if gate_filter and gate_name not in gate_filter:
                continue
            
            # Check if gate applies to any staged files
            if self._gate_applies_to_files(gate_rule, staged_files):
                applicable_gates.append(gate_name)
        
        return applicable_gates

    def _gate_applies_to_files(self, gate_rule: GateRule, files: List[str]) -> bool:
        """Check if gate rule applies to any of the files"""
        # Special gates that always run
        if gate_rule.category in [GateCategory.COMMIT_MESSAGE, GateCategory.DEPENDENCIES]:
            return True
        
        # If no file patterns specified, apply to all files
        if not gate_rule.file_patterns:
            return len(files) > 0
        
        # Check file patterns
        for file_path in files:
            # Check exclude patterns first
            excluded = False
            for exclude_pattern in gate_rule.exclude_patterns:
                if self._matches_pattern(file_path, exclude_pattern):
                    excluded = True
                    break
            
            if excluded:
                continue
            
            # Check include patterns
            for include_pattern in gate_rule.file_patterns:
                if self._matches_pattern(file_path, include_pattern):
                    return True
        
        return False

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches pattern"""
        # Convert glob-like pattern to regex
        regex_pattern = pattern.replace("**", ".*").replace("*", "[^/]*")
        return re.search(regex_pattern, file_path) is not None

    async def _execute_gates(
        self,
        gate_names: List[str],
        staged_files: List[str],
        fail_fast: bool,
        commit_message: Optional[str]
    ) -> List[GateResult]:
        """Execute pre-commit gates"""
        results = []
        
        # Sort gates by dependencies
        sorted_gates = self._sort_gates_by_dependencies(gate_names)
        
        for gate_name in sorted_gates:
            gate_rule = self.gate_rules[gate_name]
            
            # Check dependencies
            dependency_failed = False
            for dep_name in gate_rule.depends_on:
                dep_result = next((r for r in results if r.gate_name == dep_name), None)
                if dep_result and dep_result.status == GateStatus.FAILED:
                    dependency_failed = True
                    break
            
            if dependency_failed:
                # Skip this gate due to dependency failure
                result = GateResult(
                    gate_name=gate_name,
                    status=GateStatus.SKIPPED,
                    severity=gate_rule.severity,
                    category=gate_rule.category,
                    start_time=datetime.utcnow()
                )
                results.append(result)
                continue
            
            # Execute the gate
            result = await self._execute_single_gate(gate_rule, staged_files, commit_message)
            results.append(result)
            
            # Check fail-fast condition
            if (fail_fast and 
                result.status == GateStatus.FAILED and 
                result.severity == GateSeverity.BLOCKING):
                self.logger.warning(f"Fail-fast triggered by blocking failure in {gate_name}")
                break
        
        return results

    def _sort_gates_by_dependencies(self, gate_names: List[str]) -> List[str]:
        """Sort gates by their dependencies"""
        # Simple topological sort
        sorted_gates = []
        remaining_gates = gate_names.copy()
        
        while remaining_gates:
            # Find gates with no unresolved dependencies
            ready_gates = []
            for gate_name in remaining_gates:
                gate_rule = self.gate_rules[gate_name]
                deps_satisfied = all(dep in sorted_gates for dep in gate_rule.depends_on)
                if deps_satisfied:
                    ready_gates.append(gate_name)
            
            if not ready_gates:
                # Circular dependency or missing dependency, add remaining gates
                ready_gates = remaining_gates
            
            # Add ready gates to sorted list
            for gate_name in ready_gates:
                sorted_gates.append(gate_name)
                remaining_gates.remove(gate_name)
        
        return sorted_gates

    async def _execute_single_gate(
        self,
        gate_rule: GateRule,
        staged_files: List[str],
        commit_message: Optional[str]
    ) -> GateResult:
        """Execute a single pre-commit gate"""
        result = GateResult(
            gate_name=gate_rule.name,
            status=GateStatus.RUNNING,
            severity=gate_rule.severity,
            category=gate_rule.category,
            start_time=datetime.utcnow()
        )
        
        try:
            self.logger.info(f"Executing gate: {gate_rule.name}")
            
            # Filter files for this gate
            applicable_files = self._get_applicable_files(gate_rule, staged_files)
            result.files_checked = applicable_files
            
            # Execute the gate command
            if gate_rule.command.startswith("internal_"):
                # Handle internal commands
                success = await self._execute_internal_command(
                    gate_rule.command, applicable_files, commit_message, result
                )
                result.status = GateStatus.PASSED if success else GateStatus.FAILED
            else:
                # Execute external command
                await self._execute_external_command(gate_rule, applicable_files, result)
            
        except Exception as e:
            result.status = GateStatus.FAILED
            result.stderr = str(e)
            self.logger.error(f"Gate {gate_rule.name} failed with exception: {e}")
        finally:
            result.end_time = datetime.utcnow()
            result.duration = (result.end_time - result.start_time).total_seconds()
        
        return result

    def _get_applicable_files(self, gate_rule: GateRule, staged_files: List[str]) -> List[str]:
        """Get files applicable to a specific gate"""
        applicable_files = []
        
        for file_path in staged_files:
            # Check exclude patterns
            excluded = False
            for exclude_pattern in gate_rule.exclude_patterns:
                if self._matches_pattern(file_path, exclude_pattern):
                    excluded = True
                    break
            
            if excluded:
                continue
            
            # Check include patterns
            if not gate_rule.file_patterns:
                # No patterns means all files
                applicable_files.append(file_path)
            else:
                for include_pattern in gate_rule.file_patterns:
                    if self._matches_pattern(file_path, include_pattern):
                        applicable_files.append(file_path)
                        break
        
        return applicable_files

    async def _execute_external_command(
        self,
        gate_rule: GateRule,
        applicable_files: List[str],
        result: GateResult
    ):
        """Execute external command for gate"""
        if not applicable_files and gate_rule.category not in [
            GateCategory.DEPENDENCIES, GateCategory.COMMIT_MESSAGE
        ]:
            result.status = GateStatus.SKIPPED
            return
        
        # Build command with file arguments
        cmd_parts = gate_rule.command.split()
        if applicable_files and gate_rule.category != GateCategory.DEPENDENCIES:
            cmd_parts.extend(applicable_files)
        
        try:
            process = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=gate_rule.timeout_seconds,
                cwd=self.project_root
            )
            
            result.exit_code = process.returncode
            result.stdout = process.stdout
            result.stderr = process.stderr
            
            # Parse violations based on tool
            result.violations = self._parse_tool_output(gate_rule.name, process.stdout, process.stderr)
            
            # Determine status
            if process.returncode == 0:
                result.status = GateStatus.PASSED
            else:
                if gate_rule.severity == GateSeverity.BLOCKING:
                    result.status = GateStatus.FAILED
                elif gate_rule.severity == GateSeverity.WARNING:
                    result.status = GateStatus.WARNING
                else:
                    result.status = GateStatus.PASSED  # Informational
            
        except subprocess.TimeoutExpired:
            result.status = GateStatus.FAILED
            result.stderr = f"Command timed out after {gate_rule.timeout_seconds} seconds"
        except FileNotFoundError:
            result.status = GateStatus.SKIPPED
            result.stderr = f"Command not found: {cmd_parts[0]}"

    async def _execute_internal_command(
        self,
        command: str,
        applicable_files: List[str],
        commit_message: Optional[str],
        result: GateResult
    ) -> bool:
        """Execute internal command"""
        
        if command == "internal_commit_message_check":
            return await self._check_commit_message(commit_message, result)
        elif command == "internal_file_size_check":
            return await self._check_file_sizes(applicable_files, result)
        elif command == "internal_filename_check":
            return await self._check_filename_conventions(applicable_files, result)
        else:
            result.stderr = f"Unknown internal command: {command}"
            return False

    async def _check_commit_message(self, commit_message: Optional[str], result: GateResult) -> bool:
        """Check commit message format"""
        if not commit_message:
            # Try to get commit message from git
            try:
                git_result = subprocess.run(
                    ["git", "log", "-1", "--pretty=%B"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                commit_message = git_result.stdout.strip()
            except:
                result.violations.append({
                    "type": "missing_message",
                    "message": "No commit message provided"
                })
                return False
        
        violations = []
        
        # Check message length
        if len(commit_message) < 10:
            violations.append({
                "type": "too_short",
                "message": "Commit message too short (minimum 10 characters)"
            })
        
        # Check for conventional commit format (optional)
        conventional_pattern = r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"
        if not re.match(conventional_pattern, commit_message):
            violations.append({
                "type": "format",
                "message": "Consider using conventional commit format: type(scope): description"
            })
        
        # Check for common bad patterns
        bad_patterns = ["wip", "tmp", "fix", "update", "change"]
        for pattern in bad_patterns:
            if commit_message.lower().strip() == pattern:
                violations.append({
                    "type": "vague_message",
                    "message": f"Commit message too vague: '{pattern}'"
                })
        
        result.violations = violations
        return len(violations) == 0

    async def _check_file_sizes(self, files: List[str], result: GateResult) -> bool:
        """Check file size limits"""
        violations = []
        max_size_mb = 10  # 10MB limit
        
        for file_path in files:
            full_path = self.project_root / file_path
            if full_path.exists():
                size_mb = full_path.stat().st_size / (1024 * 1024)
                if size_mb > max_size_mb:
                    violations.append({
                        "file": file_path,
                        "size_mb": round(size_mb, 2),
                        "max_size_mb": max_size_mb,
                        "message": f"File {file_path} is {size_mb:.2f}MB (limit: {max_size_mb}MB)"
                    })
        
        result.violations = violations
        return len(violations) == 0

    async def _check_filename_conventions(self, files: List[str], result: GateResult) -> bool:
        """Check filename conventions"""
        violations = []
        
        for file_path in files:
            filename = Path(file_path).name
            
            # Check for spaces in filename
            if ' ' in filename:
                violations.append({
                    "file": file_path,
                    "issue": "spaces_in_name",
                    "message": f"Filename '{filename}' contains spaces"
                })
            
            # Check for non-ASCII characters
            if not filename.isascii():
                violations.append({
                    "file": file_path,
                    "issue": "non_ascii",
                    "message": f"Filename '{filename}' contains non-ASCII characters"
                })
            
            # Check Python file naming conventions
            if filename.endswith('.py'):
                if not re.match(r'^[a-z_][a-z0-9_]*\.py$', filename):
                    violations.append({
                        "file": file_path,
                        "issue": "python_naming",
                        "message": f"Python file '{filename}' should use snake_case"
                    })
        
        result.violations = violations
        return len(violations) == 0

    def _parse_tool_output(self, tool_name: str, stdout: str, stderr: str) -> List[Dict[str, Any]]:
        """Parse tool output to extract violations"""
        violations = []
        
        if tool_name == "bandit_security":
            try:
                bandit_data = json.loads(stdout)
                for result in bandit_data.get("results", []):
                    violations.append({
                        "file": result.get("filename"),
                        "line": result.get("line_number"),
                        "severity": result.get("issue_severity"),
                        "message": result.get("issue_text"),
                        "rule": result.get("test_name")
                    })
            except:
                pass
        
        elif tool_name == "flake8_linting":
            # Parse flake8 output
            for line in stdout.split('\n'):
                if ':' in line and len(line.strip()) > 0:
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        violations.append({
                            "file": parts[0],
                            "line": parts[1],
                            "column": parts[2],
                            "message": parts[3].strip()
                        })
        
        # Add more parsers for other tools as needed
        
        return violations

    def _generate_report(
        self,
        gate_names: List[str],
        gate_results: List[GateResult],
        staged_files: List[str],
        total_duration: float
    ) -> PreCommitReport:
        """Generate pre-commit report"""
        
        passed_gates = len([r for r in gate_results if r.status == GateStatus.PASSED])
        failed_gates = len([r for r in gate_results if r.status == GateStatus.FAILED])
        warning_gates = len([r for r in gate_results if r.status == GateStatus.WARNING])
        skipped_gates = len([r for r in gate_results if r.status == GateStatus.SKIPPED])
        
        # Determine if commit should be allowed
        blocking_failures = [r for r in gate_results 
                           if r.status == GateStatus.FAILED and r.severity == GateSeverity.BLOCKING]
        commit_allowed = len(blocking_failures) == 0
        
        # Generate file summary
        file_summary = {
            "staged_files": len(staged_files),
            "files_analyzed": len(set(f for r in gate_results for f in r.files_checked)),
            "file_types": self._analyze_file_types(staged_files)
        }
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(gate_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(gate_results, commit_allowed)
        
        return PreCommitReport(
            total_gates=len(gate_names),
            passed_gates=passed_gates,
            failed_gates=failed_gates,
            warning_gates=warning_gates,
            skipped_gates=skipped_gates,
            total_duration=total_duration,
            commit_allowed=commit_allowed,
            gate_results=gate_results,
            file_summary=file_summary,
            overall_metrics=overall_metrics,
            recommendations=recommendations
        )

    def _analyze_file_types(self, files: List[str]) -> Dict[str, int]:
        """Analyze file types in staged files"""
        file_types = {}
        for file_path in files:
            extension = Path(file_path).suffix or "no_extension"
            file_types[extension] = file_types.get(extension, 0) + 1
        return file_types

    def _calculate_overall_metrics(self, gate_results: List[GateResult]) -> Dict[str, Any]:
        """Calculate overall quality metrics"""
        if not gate_results:
            return {}
        
        total_violations = sum(len(r.violations) for r in gate_results)
        durations = [r.duration for r in gate_results if r.duration > 0]
        
        return {
            "total_violations": total_violations,
            "average_gate_duration": sum(durations) / len(durations) if durations else 0,
            "max_gate_duration": max(durations) if durations else 0,
            "gate_success_rate": len([r for r in gate_results if r.status == GateStatus.PASSED]) / len(gate_results) * 100
        }

    def _generate_recommendations(self, gate_results: List[GateResult], commit_allowed: bool) -> List[str]:
        """Generate recommendations based on gate results"""
        recommendations = []
        
        if not commit_allowed:
            recommendations.append("Fix blocking issues before committing")
        
        failed_gates = [r for r in gate_results if r.status == GateStatus.FAILED]
        if failed_gates:
            recommendations.append(f"Address failures in: {', '.join(r.gate_name for r in failed_gates)}")
        
        warning_gates = [r for r in gate_results if r.status == GateStatus.WARNING]
        if warning_gates:
            recommendations.append(f"Consider fixing warnings in: {', '.join(r.gate_name for r in warning_gates)}")
        
        high_violation_gates = [r for r in gate_results if len(r.violations) > 10]
        if high_violation_gates:
            recommendations.append("Focus on gates with many violations for maximum impact")
        
        return recommendations

    def install_git_hooks(self):
        """Install Git pre-commit hooks"""
        hooks_dir = self.project_root / ".git" / "hooks"
        pre_commit_hook = hooks_dir / "pre-commit"
        
        hook_content = f"""#!/bin/sh
# Auto-generated pre-commit hook for Ainflue quality gates

cd "{self.project_root}"
python -c "
from quality.pre_commit_gate_orchestrator import pre_commit_gate_orchestrator
import asyncio
import sys

async def main():
    report = await pre_commit_gate_orchestrator.run_pre_commit_gates()
    if not report.commit_allowed:
        print('❌ Commit blocked by quality gates')
        for result in report.gate_results:
            if result.status.value == 'failed' and result.severity.value == 'blocking':
                print(f'  - {{result.gate_name}}: {{len(result.violations)}} issues')
        sys.exit(1)
    else:
        print('✅ All quality gates passed')
        
asyncio.run(main())
"
"""
        
        try:
            hooks_dir.mkdir(exist_ok=True)
            with open(pre_commit_hook, 'w') as f:
                f.write(hook_content)
            pre_commit_hook.chmod(0o755)
            self.logger.info("Installed Git pre-commit hook")
        except Exception as e:
            self.logger.error(f"Failed to install Git hook: {e}")

    def add_gate_rule(self, gate_rule: GateRule):
        """Add a new gate rule"""
        self.gate_rules[gate_rule.name] = gate_rule
        self.logger.info(f"Added gate rule: {gate_rule.name}")

    def remove_gate_rule(self, gate_name: str):
        """Remove a gate rule"""
        if gate_name in self.gate_rules:
            del self.gate_rules[gate_name]
            self.logger.info(f"Removed gate rule: {gate_name}")

    def enable_gate(self, gate_name: str):
        """Enable a gate"""
        if gate_name in self.gate_rules:
            self.gate_rules[gate_name].enabled = True

    def disable_gate(self, gate_name: str):
        """Disable a gate"""
        if gate_name in self.gate_rules:
            self.gate_rules[gate_name].enabled = False

# Global pre-commit gate orchestrator instance
pre_commit_gate_orchestrator = PreCommitGateOrchestrator()

__all__ = [
    "PreCommitGateOrchestrator",
    "GateRule",
    "GateResult",
    "PreCommitReport",
    "GateStatus",
    "GateSeverity", 
    "GateCategory",
    "pre_commit_gate_orchestrator"
]