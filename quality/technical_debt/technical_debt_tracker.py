"""🔧 Technical Debt Tracker - Ainflue Platform
import asyncio

================================================================
Expert: QUALITY_ENGINEER + SOFTWARE_ARCHITECT
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Comprehensive technical debt tracking and analysis system.
Monitors code quality degradation, design smells, and refactoring opportunities.
================================================================
"""

import ast
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)

class DebtType(Enum):
    """Types of technical debt"""
    CODE_DUPLICATION = "code_duplication"
    TODO_COMMENTS = "todo_comments"
    DEPRECATED_USAGE = "deprecated_usage"
    DESIGN_SMELLS = "design_smells"
    COMPLEX_METHODS = "complex_methods"
    LARGE_CLASSES = "large_classes"
    LONG_PARAMETER_LISTS = "long_parameter_lists"
    DEAD_CODE = "dead_code"
    MISSING_TESTS = "missing_tests"
    HARDCODED_VALUES = "hardcoded_values"

class DebtSeverity(Enum):
    """Severity levels for technical debt"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class DebtItem:
    """Individual technical debt item"""
    debt_type: DebtType
    severity: DebtSeverity
    description: str
    file_path: str
    line_number: Optional[int] = None
    method_name: Optional[str] = None
    class_name: Optional[str] = None
    effort_estimate: int = 1  # Story points or hours
    impact_score: float = 1.0  # 1-10 scale
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DebtSummary:
    """Technical debt summary"""
    total_items: int
    total_effort: int
    severity_breakdown: Dict[DebtSeverity, int]
    type_breakdown: Dict[DebtType, int]
    debt_ratio: float  # Technical debt / total code ratio
    trend: str  # "increasing", "stable", "decreasing"
    hotspots: List[str]  # Files with most debt
    recommendations: List[str]

class TechnicalDebtTracker:
    """
    Comprehensive technical debt tracking system
    """
    
    def __init__(self, project_root -> None: Optional[str] = None) -> None:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise

    async def analyze_technical_debt(self) -> DebtSummary:
        """Analyze technical debt across the project"""
        self.logger.info("Starting technical debt analysis")
        self.debt_items = []
        
        # Analyze Python files
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._is_excluded(f)]
        
        for file_path in python_files:
            try:
                await self._analyze_file(file_path)
            except Exception as e:
                self.logger.warning(f"Error analyzing {file_path}: {e}")
        
        # Generate summary
        summary = self._generate_summary()
        self.logger.info(f"Technical debt analysis completed. Found {summary.total_items} debt items")
        
        return summary

    async def _analyze_file(self, file_path -> None: Path) -> None:
        """Analyze a single file for technical debt"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Parse AST for structural analysis
            try:
                tree = ast.parse(content)
                await self._analyze_ast(tree, file_path, lines)
            except SyntaxError:
                self.logger.warning(f"Syntax error in {file_path}, skipping AST analysis")
            
            # Analyze line by line
            await self._analyze_lines(lines, file_path)
            
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")

    async def _analyze_ast(self, tree -> None: ast.AST, file_path -> None: Path, lines -> None: List[str]) -> None:
        """Analyze AST for structural debt"""
        
        class DebtVisitor(ast.NodeVisitor):
    """DebtVisitor class implementation"""
            def __init__(self, tracker, file_path, lines) -> None:
                self.tracker = tracker
                self.file_path = file_path
                self.lines = lines
                self.current_class = None
                self.current_method = None
            
            def visit_ClassDef(self, node) -> None:
                old_class = self.current_class
                self.current_class = node.name
                
                # Check for large classes (God class anti-pattern)
                class_lines = self._count_code_lines(node)
                if class_lines > 500:
                    self.tracker._add_debt_item(
                        DebtType.LARGE_CLASSES,
                        DebtSeverity.HIGH,
                        f"Large class '{node.name}' with {class_lines} lines",
                        self.file_path,
                        node.lineno,
                        class_name=node.name,
                        effort_estimate=8,
                        impact_score=7.0
                    )
                
                # Check for too many methods
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 30:
                    self.tracker._add_debt_item(
                        DebtType.DESIGN_SMELLS,
                        DebtSeverity.MEDIUM,
                        f"Class '{node.name}' has {len(methods)} methods (too many responsibilities)",
                        self.file_path,
                        node.lineno,
                        class_name=node.name,
                        effort_estimate=5,
                        impact_score=6.0
                    )
                
                self.generic_visit(node)
                self.current_class = old_class
            
            def visit_FunctionDef(self, node) -> None:
                old_method = self.current_method
                self.current_method = node.name
                
                # Check for long methods
                method_lines = self._count_code_lines(node)
                if method_lines > 50:
                    self.tracker._add_debt_item(
                        DebtType.COMPLEX_METHODS,
                        DebtSeverity.MEDIUM,
                        f"Long method '{node.name}' with {method_lines} lines",
                        self.file_path,
                        node.lineno,
                        method_name=node.name,
                        class_name=self.current_class,
                        effort_estimate=3,
                        impact_score=5.0
                    )
                
                # Check for long parameter lists
                param_count = len(node.args.args)
                if param_count > 6:
                    self.tracker._add_debt_item(
                        DebtType.LONG_PARAMETER_LISTS,
                        DebtSeverity.LOW,
                        f"Method '{node.name}' has {param_count} parameters",
                        self.file_path,
                        node.lineno,
                        method_name=node.name,
                        class_name=self.current_class,
                        effort_estimate=2,
                        impact_score=3.0
                    )
                
                # Check for high cyclomatic complexity
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    self.tracker._add_debt_item(
                        DebtType.COMPLEX_METHODS,
                        DebtSeverity.HIGH,
                        f"Method '{node.name}' has high complexity ({complexity})",
                        self.file_path,
                        node.lineno,
                        method_name=node.name,
                        class_name=self.current_class,
                        effort_estimate=5,
                        impact_score=8.0
                    )
                
                self.generic_visit(node)
                self.current_method = old_method
            
            def _count_code_lines(self, node) -> None:
                """Count non-empty, non-comment lines in a node"""
                start_line = node.lineno - 1
                end_line = getattr(node, 'end_lineno', len(self.lines)) or len(self.lines)
                
                count = 0
                for i in range(start_line, min(end_line, len(self.lines))):
                    line = self.lines[i].strip()
                    if line and not line.startswith('#'):
                        count += 1
                return count
            
            def _calculate_complexity(self, node) -> None:
                """Calculate cyclomatic complexity"""
                complexity = 1  # Base complexity
                
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                        complexity += 1
                    elif isinstance(child, ast.ExceptHandler):
                        complexity += 1
                    elif isinstance(child, (ast.And, ast.Or)):
                        complexity += 1
                
                return complexity
        
        visitor = DebtVisitor(self, file_path, lines)
        visitor.visit(tree)

    async def _analyze_lines(self, lines -> None: List[str], file_path -> None: Path) -> None:
        """Analyze file line by line for debt patterns"""
        
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # Check for TODO/FIXME comments
            for pattern in self.todo_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    comment_text = match.group(1) if match.groups() else stripped_line
                    severity = self._determine_todo_severity(stripped_line)
                    
                    self._add_debt_item(
                        DebtType.TODO_COMMENTS,
                        severity,
                        f"TODO comment: {comment_text}",
                        file_path,
                        line_num,
                        effort_estimate=self._estimate_todo_effort(comment_text),
                        impact_score=3.0
                    )
            
            # Check for deprecated usage
            for pattern in self.deprecated_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_debt_item(
                        DebtType.DEPRECATED_USAGE,
                        DebtSeverity.MEDIUM,
                        f"Deprecated usage detected: {stripped_line[:100]}",
                        file_path,
                        line_num,
                        effort_estimate=2,
                        impact_score=5.0
                    )
            
            # Check for hardcoded values (magic numbers/strings)
            if self._has_magic_numbers(stripped_line):
                self._add_debt_item(
                    DebtType.HARDCODED_VALUES,
                    DebtSeverity.LOW,
                    f"Magic number/string detected: {stripped_line[:100]}",
                    file_path,
                    line_num,
                    effort_estimate=1,
                    impact_score=2.0
                )

    def _add_debt_item(
        self, 
        debt_type -> None: DebtType, 
        severity -> None: DebtSeverity, 
        description -> None: str,
        file_path -> None: Path,
        line_number -> None: Optional[int] = None,
        method_name -> None: Optional[str] = None,
        class_name -> None: Optional[str] = None,
        effort_estimate -> None: int = 1,
        impact_score -> None: float = 1.0,
        metadata -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a technical debt item"""
        item = DebtItem(
            debt_type=debt_type,
            severity=severity,
            description=description,
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=line_number,
            method_name=method_name,
            class_name=class_name,
            effort_estimate=effort_estimate,
            impact_score=impact_score,
            metadata=metadata or {}
        )
        self.debt_items.append(item)

    def _determine_todo_severity(self, line: str) -> DebtSeverity:
        """Determine severity of TODO comments"""
        line_upper = line.upper()
        if any(word in line_upper for word in ["CRITICAL", "URGENT", "FIXME", "BUG"]):
            return DebtSeverity.HIGH
        elif any(word in line_upper for word in ["IMPORTANT", "XXX"]):
            return DebtSeverity.MEDIUM
        else:
            return DebtSeverity.LOW

    def _estimate_todo_effort(self, line: str) -> int:
        """Estimate effort for TODO items"""
        comment_lower = line.lower()
        if any(word in comment_lower for word in ["refactor", "rewrite", "redesign"]):
            return 8
        elif any(word in comment_lower for word in ["implement", "add", "create"]):
            return 5
        elif any(word in comment_lower for word in ["fix", "update", "change"]):
            return 3
        else:
            return 1

    def _has_magic_numbers(self, line: str) -> bool:
        """Check for magic numbers (excluding common ones)"""
        # Skip comments and strings
        if line.strip().startswith('#') or '"""' in line or "'''" in line:
            return False
        
        # Common acceptable numbers
        acceptable_numbers = {0, 1, 2, 10, 100, 1000, -1}
        
        # Find numbers in the line
        numbers = re.findall(r'\b\d+\.?\d*\b', line)
        for num_str in numbers:
            try:
                num = float(num_str)
                if num not in acceptable_numbers and num > 2:
                    return True
            except ValueError:
                continue
        
        return False

    def _is_excluded(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis"""
        file_str = str(file_path)
        for exclusion in self.exclusions:
            if exclusion.replace("*", "") in file_str:
                return True
        return False

    def _generate_summary(self) -> DebtSummary:
        """Generate technical debt summary"""
        total_items = len(self.debt_items)
        total_effort = sum(item.effort_estimate for item in self.debt_items)
        
        # Severity breakdown
        severity_breakdown = {}
        for severity in DebtSeverity:
            severity_breakdown[severity] = len([
                item for item in self.debt_items if item.severity == severity
            ])
        
        # Type breakdown
        type_breakdown = {}
        for debt_type in DebtType:
            type_breakdown[debt_type] = len([
                item for item in self.debt_items if item.debt_type == debt_type
            ])
        
        # Calculate debt ratio (rough estimate)
        total_lines = self._count_total_lines()
        debt_ratio = (total_items / max(total_lines, 1)) * 100
        
        # Find hotspots (files with most debt)
        file_debt_counts = {}
        for item in self.debt_items:
            file_debt_counts[item.file_path] = file_debt_counts.get(item.file_path, 0) + 1
        
        hotspots = sorted(file_debt_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        hotspot_files = [file_path for file_path, _ in hotspots]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(severity_breakdown, type_breakdown)
        
        return DebtSummary(
            total_items=total_items,
            total_effort=total_effort,
            severity_breakdown=severity_breakdown,
            type_breakdown=type_breakdown,
            debt_ratio=debt_ratio,
            trend="stable",  # Would need historical data for trend
            hotspots=hotspot_files,
            recommendations=recommendations
        )

    def _count_total_lines(self) -> int:
        """Count total lines of code in the project"""
        total_lines = 0
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._is_excluded(f)]
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                continue
        
        return total_lines

    def _generate_recommendations(
        self, 
        severity_breakdown: Dict[DebtSeverity, int],
        type_breakdown: Dict[DebtType, int]
    ) -> List[str]:
        """Generate recommendations based on debt analysis"""
        recommendations = []
        
        if severity_breakdown.get(DebtSeverity.CRITICAL, 0) > 0:
            recommendations.append("Address critical technical debt items immediately")
        
        if severity_breakdown.get(DebtSeverity.HIGH, 0) > 5:
            recommendations.append("High priority: Reduce high-severity debt items")
        
        if type_breakdown.get(DebtType.TODO_COMMENTS, 0) > 20:
            recommendations.append("Create issues for TODO comments and track them properly")
        
        if type_breakdown.get(DebtType.COMPLEX_METHODS, 0) > 10:
            recommendations.append("Refactor complex methods to improve maintainability")
        
        if type_breakdown.get(DebtType.LARGE_CLASSES, 0) > 0:
            recommendations.append("Break down large classes following Single Responsibility Principle")
        
        if type_breakdown.get(DebtType.DEPRECATED_USAGE, 0) > 0:
            recommendations.append("Update deprecated API usage to current alternatives")
        
        return recommendations

    def export_debt_report(self, format: str = "json") -> str:
        """Export technical debt report"""
        if format == "json":
            return self._export_json()
        elif format == "csv":
            return self._export_csv()
        elif format == "markdown":
            return self._export_markdown()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json(self) -> str:
        """Export debt report as JSON"""
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_items": len(self.debt_items),
                "total_effort": sum(item.effort_estimate for item in self.debt_items)
            },
            "debt_items": [
                {
                    "type": item.debt_type.value,
                    "severity": item.severity.value,
                    "description": item.description,
                    "file_path": item.file_path,
                    "line_number": item.line_number,
                    "effort_estimate": item.effort_estimate,
                    "impact_score": item.impact_score
                }
                for item in self.debt_items
            ]
        }
        return json.dumps(data, indent=2)

    def _export_csv(self) -> str:
        """Export debt report as CSV"""
        lines = ["Type,Severity,Description,File,Line,Effort,Impact"]
        for item in self.debt_items:
            lines.append(
                f"{item.debt_type.value},{item.severity.value},"
                f"\"{item.description}\",{item.file_path},{item.line_number or ''},"
                f"{item.effort_estimate},{item.impact_score}"
            )
        return "\n".join(lines)

    def _export_markdown(self) -> str:
        """Export debt report as Markdown"""
        summary = self._generate_summary()
        
        md = f"""# Technical Debt Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Items:** {summary.total_items}
- **Total Effort:** {summary.total_effort} story points
- **Debt Ratio:** {summary.debt_ratio:.2f}%

## Severity Breakdown
"""
        for severity, count in summary.severity_breakdown.items():
            if count > 0:
                md += f"- **{severity.value.title()}:** {count}\n"
        
        md += "\n## Type Breakdown\n"
        for debt_type, count in summary.type_breakdown.items():
            if count > 0:
                md += f"- **{debt_type.value.replace('_', ' ').title()}:** {count}\n"
        
        if summary.recommendations:
            md += "\n## Recommendations\n"
            for i, rec in enumerate(summary.recommendations, 1):
                md += f"{i}. {rec}\n"
        
        return md

# Global technical debt tracker instance
technical_debt_tracker = TechnicalDebtTracker()

__all__ = [
    "TechnicalDebtTracker",
    "DebtItem",
    "DebtSummary", 
    "DebtType",
    "DebtSeverity",
    "technical_debt_tracker"
]