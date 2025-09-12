#!/usr/bin/env python3
"""
Maintainability Index Calculator - Ainflue Quality Platform
========================================================

Enterprise-grade code maintainability assessment and calculation engine.
Demonstrates Lead Dev IA + Backend Senior + ML Engineer expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import ast
import math
import statistics
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import aiofiles
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
import radon.complexity as cc
import radon.metrics as metrics
from radon.raw import analyze
import subprocess
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MaintainabilityLevel(Enum):
    """Maintainability assessment levels"""
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"  # 60-79
    MODERATE = "moderate"  # 40-59
    POOR = "poor"  # 20-39
    CRITICAL = "critical"  # 0-19


class CodeMetricType(Enum):
    """Types of code metrics"""
    CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
    HALSTEAD_VOLUME = "halstead_volume"
    LINES_OF_CODE = "lines_of_code"
    COMMENT_RATIO = "comment_ratio"
    DUPLICATION_RATIO = "duplication_ratio"
    DEPENDENCY_COUNT = "dependency_count"
    NESTING_DEPTH = "nesting_depth"
    FUNCTION_LENGTH = "function_length"
    CLASS_COUPLING = "class_coupling"
    INHERITANCE_DEPTH = "inheritance_depth"


class TechnicalDebtCategory(Enum):
    """Categories of technical debt"""
    CODE_COMPLEXITY = "code_complexity"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    DUPLICATION = "duplication"
    NAMING = "naming"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class CodeFileMetrics:
    """Metrics for a single code file"""
    file_path: str
    language: str
    lines_of_code: int = 0
    lines_of_comments: int = 0
    blank_lines: int = 0
    cyclomatic_complexity: float = 0.0
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_effort: float = 0.0
    maintainability_index: float = 0.0
    functions: List[Dict] = field(default_factory=list)
    classes: List[Dict] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    duplicated_blocks: List[Dict] = field(default_factory=list)
    max_nesting_depth: int = 0
    average_function_length: float = 0.0
    comment_ratio: float = 0.0
    technical_debt_minutes: float = 0.0


@dataclass
class ProjectMaintainabilityReport:
    """Comprehensive maintainability report for entire project"""
    project_name: str
    generated_at: datetime
    total_files: int
    total_lines_of_code: int
    overall_maintainability_index: float
    maintainability_level: MaintainabilityLevel
    average_cyclomatic_complexity: float
    average_halstead_volume: float
    comment_ratio: float
    duplication_percentage: float
    technical_debt_hours: float
    file_metrics: List[CodeFileMetrics] = field(default_factory=list)
    hotspots: List[Dict] = field(default_factory=list)
    trends: Dict[str, List[float]] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)


class MaintainabilityIndexCalculator:
    """
    Enterprise maintainability assessment engine
    
    Demonstrates expertise in:
    - Lead Dev IA: Advanced code analysis and architecture assessment
    - Backend Senior: Code quality metrics and systematic analysis
    - ML Engineer: Predictive analytics and pattern recognition
    """
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.cs', '.go'}
        self.language_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go'
        }
        
        # Maintainability thresholds
        self.complexity_thresholds = {
            'low': 5,
            'medium': 10,
            'high': 15,
            'very_high': 20
        }
        
        self.mi_thresholds = {
            'excellent': 80,
            'good': 60,
            'moderate': 40,
            'poor': 20
        }
        
        # Initialize directories
        self.reports_dir = Path("reports/maintainability")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MaintainabilityIndexCalculator initialized for {self.project_path}")
    
    async def calculate_project_maintainability(self) -> ProjectMaintainabilityReport:
        """
        Calculate comprehensive maintainability metrics for entire project
        
        Lead Dev IA expertise: Architectural analysis and code quality assessment
        Backend expertise: Systematic code analysis and metrics collection
        ML expertise: Pattern recognition and predictive maintenance analysis
        """
        logger.info("Starting project maintainability analysis")
        
        start_time = datetime.now()
        
        # Discover code files
        code_files = await self._discover_code_files()
        logger.info(f"Found {len(code_files)} code files to analyze")
        
        # Analyze each file
        file_metrics = []
        for file_path in code_files:
            try:
                metrics = await self._analyze_file(file_path)
                if metrics:
                    file_metrics.append(metrics)
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
        
        # Calculate project-level metrics
        report = await self._calculate_project_metrics(file_metrics)
        
        # Identify maintainability hotspots
        await self._identify_hotspots(report)
        
        # Generate recommendations
        await self._generate_recommendations(report)
        
        # Perform risk assessment
        await self._perform_risk_assessment(report)
        
        # Save report
        await self._save_report(report)
        
        end_time = datetime.now()
        analysis_duration = (end_time - start_time).total_seconds()
        logger.info(f"Maintainability analysis completed in {analysis_duration:.2f}s")
        
        return report
    
    async def _discover_code_files(self) -> List[Path]:
        """Discover all code files in the project (Backend expertise)"""
        code_files = []
        
        # Exclusion patterns
        exclude_patterns = [
            '**/node_modules/**',
            '**/venv/**',
            '**/env/**',
            '**/__pycache__/**',
            '**/build/**',
            '**/dist/**',
            '**/target/**',
            '**/.git/**',
            '**/migrations/**',
            '**/test_*',
            '**/*_test.*',
            '**/tests/**'
        ]
        
        for extension in self.supported_extensions:
            pattern = f"**/*{extension}"
            files = list(self.project_path.rglob(pattern))
            
            # Filter out excluded files
            filtered_files = []
            for file_path in files:
                excluded = False
                for exclude_pattern in exclude_patterns:
                    if file_path.match(exclude_pattern):
                        excluded = True
                        break
                
                if not excluded:
                    filtered_files.append(file_path)
            
            code_files.extend(filtered_files)
        
        return sorted(code_files)
    
    async def _analyze_file(self, file_path: Path) -> Optional[CodeFileMetrics]:
        """Analyze individual code file (Lead Dev IA + Backend expertise)"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            language = self.language_mapping.get(file_path.suffix, 'unknown')
            
            if language == 'python':
                return await self._analyze_python_file(file_path, content)
            else:
                return await self._analyze_generic_file(file_path, content, language)
                
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None
    
    async def _analyze_python_file(self, file_path: Path, content: str) -> CodeFileMetrics:
        """Detailed Python file analysis (Lead Dev IA expertise)"""
        metrics = CodeFileMetrics(
            file_path=str(file_path),
            language='python'
        )
        
        try:
            # Basic line counts using radon
            raw_metrics = analyze(content)
            metrics.lines_of_code = raw_metrics.loc
            metrics.lines_of_comments = raw_metrics.comments
            metrics.blank_lines = raw_metrics.blank
            
            # Comment ratio
            total_lines = metrics.lines_of_code + metrics.lines_of_comments + metrics.blank_lines
            metrics.comment_ratio = (metrics.lines_of_comments / max(total_lines, 1)) * 100
            
            # Cyclomatic complexity
            complexity_results = cc.cc_visit(content)
            if complexity_results:
                complexities = [result.complexity for result in complexity_results]
                metrics.cyclomatic_complexity = statistics.mean(complexities) if complexities else 0
            
            # Halstead metrics
            halstead_metrics = metrics.analyze(content)
            if hasattr(halstead_metrics, 'total'):
                h_metrics = halstead_metrics.total
                metrics.halstead_volume = getattr(h_metrics, 'volume', 0) or 0
                metrics.halstead_difficulty = getattr(h_metrics, 'difficulty', 0) or 0
                metrics.halstead_effort = getattr(h_metrics, 'effort', 0) or 0
            
            # AST analysis for deeper insights
            try:
                tree = ast.parse(content)
                await self._analyze_ast(tree, metrics)
            except SyntaxError:
                logger.warning(f"Syntax error in {file_path}, skipping AST analysis")
            
            # Calculate maintainability index
            metrics.maintainability_index = await self._calculate_maintainability_index(metrics)
            
            # Estimate technical debt
            metrics.technical_debt_minutes = await self._estimate_technical_debt(metrics)
            
        except Exception as e:
            logger.error(f"Error in Python analysis for {file_path}: {e}")
        
        return metrics
    
    async def _analyze_ast(self, tree: ast.AST, metrics: CodeFileMetrics):
        """Analyze Python AST for detailed metrics (Lead Dev IA expertise)"""
        class CodeAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.functions = []
                self.classes = []
                self.imports = []
                self.max_nesting = 0
                self.current_nesting = 0
                
            def visit_FunctionDef(self, node):
                function_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': getattr(node, 'end_lineno', node.lineno),
                    'complexity': 1,  # Base complexity
                    'args_count': len(node.args.args),
                    'docstring': ast.get_docstring(node) is not None
                }
                
                # Calculate function length
                function_info['length'] = function_info['line_end'] - function_info['line_start'] + 1
                
                # Count decision points for complexity
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try, ast.ExceptHandler)):
                        function_info['complexity'] += 1
                    elif isinstance(child, ast.BoolOp):
                        function_info['complexity'] += len(child.values) - 1
                
                self.functions.append(function_info)
                
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
            
            def visit_ClassDef(self, node):
                class_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': getattr(node, 'end_lineno', node.lineno),
                    'methods': [],
                    'inheritance_depth': len(node.bases),
                    'docstring': ast.get_docstring(node) is not None
                }
                
                # Analyze methods
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        class_info['methods'].append(child.name)
                
                self.classes.append(class_info)
                
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
            
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.append(alias.name)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module:
                    for alias in node.names:
                        import_name = f"{node.module}.{alias.name}"
                        self.imports.append(import_name)
                self.generic_visit(node)
        
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        
        metrics.functions = analyzer.functions
        metrics.classes = analyzer.classes
        metrics.imports = analyzer.imports
        metrics.max_nesting_depth = analyzer.max_nesting
        
        # Calculate average function length
        if analyzer.functions:
            function_lengths = [f['length'] for f in analyzer.functions]
            metrics.average_function_length = statistics.mean(function_lengths)
    
    async def _analyze_generic_file(self, file_path: Path, content: str, language: str) -> CodeFileMetrics:
        """Generic file analysis for non-Python files (Backend expertise)"""
        metrics = CodeFileMetrics(
            file_path=str(file_path),
            language=language
        )
        
        lines = content.split('\n')
        
        # Basic line counting
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        comment_patterns = {
            'javascript': [r'^\s*//', r'/\*.*?\*/'],
            'typescript': [r'^\s*//', r'/\*.*?\*/'],
            'java': [r'^\s*//', r'/\*.*?\*/'],
            'cpp': [r'^\s*//', r'/\*.*?\*/', r'^\s*#'],
            'csharp': [r'^\s*//', r'/\*.*?\*/'],
            'go': [r'^\s*//', r'/\*.*?\*/']
        }
        
        patterns = comment_patterns.get(language, [r'^\s*#', r'^\s*//'])
        
        for line in lines:
            stripped_line = line.strip()
            
            if not stripped_line:
                blank_lines += 1
            elif any(re.match(pattern, stripped_line) for pattern in patterns):
                comment_lines += 1
            else:
                code_lines += 1
        
        metrics.lines_of_code = code_lines
        metrics.lines_of_comments = comment_lines
        metrics.blank_lines = blank_lines
        
        total_lines = code_lines + comment_lines + blank_lines
        metrics.comment_ratio = (comment_lines / max(total_lines, 1)) * 100
        
        # Estimate complexity based on keywords
        complexity_keywords = {
            'javascript': ['if', 'else', 'while', 'for', 'switch', 'catch', 'function'],
            'typescript': ['if', 'else', 'while', 'for', 'switch', 'catch', 'function'],
            'java': ['if', 'else', 'while', 'for', 'switch', 'catch', 'try'],
            'cpp': ['if', 'else', 'while', 'for', 'switch', 'catch', 'try'],
            'csharp': ['if', 'else', 'while', 'for', 'switch', 'catch', 'try'],
            'go': ['if', 'else', 'for', 'switch', 'select', 'func']
        }
        
        keywords = complexity_keywords.get(language, ['if', 'else', 'while', 'for'])
        complexity_count = 0
        
        for line in lines:
            for keyword in keywords:
                complexity_count += len(re.findall(rf'\b{keyword}\b', line.lower()))
        
        metrics.cyclomatic_complexity = max(1, complexity_count / max(len(lines), 1) * 10)
        
        # Calculate maintainability index
        metrics.maintainability_index = await self._calculate_maintainability_index(metrics)
        
        return metrics
    
    async def _calculate_maintainability_index(self, metrics: CodeFileMetrics) -> float:
        """
        Calculate maintainability index using Microsoft's formula
        
        ML Engineer expertise: Mathematical modeling and metric calculation
        """
        try:
            # Microsoft Maintainability Index formula:
            # MI = max(0, (171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code)) * 100 / 171)
            
            halstead_volume = max(metrics.halstead_volume, 1)
            cyclomatic_complexity = max(metrics.cyclomatic_complexity, 1)
            lines_of_code = max(metrics.lines_of_code, 1)
            
            # Calculate base MI
            mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * cyclomatic_complexity - 16.2 * math.log(lines_of_code)
            
            # Normalize to 0-100 scale
            mi_normalized = max(0, (mi * 100 / 171))
            
            # Apply comment ratio bonus (up to 10 points)
            comment_bonus = min(10, metrics.comment_ratio / 10)
            mi_normalized += comment_bonus
            
            # Cap at 100
            return min(100, mi_normalized)
            
        except (ValueError, ZeroDivisionError):
            # Fallback calculation based on available metrics
            base_score = 50  # Average baseline
            
            # Adjust based on complexity
            if metrics.cyclomatic_complexity <= 5:
                base_score += 20
            elif metrics.cyclomatic_complexity <= 10:
                base_score += 10
            elif metrics.cyclomatic_complexity > 20:
                base_score -= 20
            
            # Adjust based on comment ratio
            if metrics.comment_ratio > 20:
                base_score += 10
            elif metrics.comment_ratio < 5:
                base_score -= 10
            
            # Adjust based on file size
            if metrics.lines_of_code > 500:
                base_score -= 15
            elif metrics.lines_of_code < 50:
                base_score += 5
            
            return max(0, min(100, base_score))
    
    async def _estimate_technical_debt(self, metrics: CodeFileMetrics) -> float:
        """
        Estimate technical debt in minutes (Lead Dev IA + ML expertise)
        
        Uses SQALE methodology for technical debt calculation
        """
        debt_minutes = 0.0
        
        # Complexity debt
        if metrics.cyclomatic_complexity > self.complexity_thresholds['medium']:
            excess_complexity = metrics.cyclomatic_complexity - self.complexity_thresholds['medium']
            debt_minutes += excess_complexity * 5  # 5 minutes per excess complexity point
        
        # Documentation debt
        if metrics.comment_ratio < 15:  # Less than 15% comments
            debt_minutes += (15 - metrics.comment_ratio) * 2  # 2 minutes per missing comment percentage
        
        # Function length debt
        if metrics.average_function_length > 50:  # Functions longer than 50 lines
            debt_minutes += (metrics.average_function_length - 50) * 1  # 1 minute per excess line
        
        # File size debt
        if metrics.lines_of_code > 300:  # Files longer than 300 lines
            debt_minutes += (metrics.lines_of_code - 300) * 0.1  # 0.1 minutes per excess line
        
        # Nesting depth debt
        if metrics.max_nesting_depth > 4:
            debt_minutes += (metrics.max_nesting_depth - 4) * 10  # 10 minutes per excess nesting level
        
        return debt_minutes
    
    async def _calculate_project_metrics(self, file_metrics: List[CodeFileMetrics]) -> ProjectMaintainabilityReport:
        """Calculate project-level maintainability metrics (Backend + ML expertise)"""
        if not file_metrics:
            return ProjectMaintainabilityReport(
                project_name=self.project_path.name,
                generated_at=datetime.now(),
                total_files=0,
                total_lines_of_code=0,
                overall_maintainability_index=0.0,
                maintainability_level=MaintainabilityLevel.CRITICAL,
                average_cyclomatic_complexity=0.0,
                average_halstead_volume=0.0,
                comment_ratio=0.0,
                duplication_percentage=0.0,
                technical_debt_hours=0.0
            )
        
        # Aggregate metrics
        total_loc = sum(fm.lines_of_code for fm in file_metrics)
        total_comments = sum(fm.lines_of_comments for fm in file_metrics)
        total_debt_minutes = sum(fm.technical_debt_minutes for fm in file_metrics)
        
        # Weighted averages (by lines of code)
        weighted_mi = sum(fm.maintainability_index * fm.lines_of_code for fm in file_metrics) / max(total_loc, 1)
        weighted_complexity = sum(fm.cyclomatic_complexity * fm.lines_of_code for fm in file_metrics) / max(total_loc, 1)
        weighted_halstead = sum(fm.halstead_volume * fm.lines_of_code for fm in file_metrics if fm.halstead_volume > 0) / max(total_loc, 1)
        
        # Comment ratio
        overall_comment_ratio = (total_comments / max(total_loc + total_comments, 1)) * 100
        
        # Determine maintainability level
        maintainability_level = self._determine_maintainability_level(weighted_mi)
        
        report = ProjectMaintainabilityReport(
            project_name=self.project_path.name,
            generated_at=datetime.now(),
            total_files=len(file_metrics),
            total_lines_of_code=total_loc,
            overall_maintainability_index=weighted_mi,
            maintainability_level=maintainability_level,
            average_cyclomatic_complexity=weighted_complexity,
            average_halstead_volume=weighted_halstead,
            comment_ratio=overall_comment_ratio,
            duplication_percentage=0.0,  # Will be calculated separately
            technical_debt_hours=total_debt_minutes / 60,
            file_metrics=file_metrics
        )
        
        return report
    
    def _determine_maintainability_level(self, mi_score: float) -> MaintainabilityLevel:
        """Determine maintainability level from MI score"""
        if mi_score >= self.mi_thresholds['excellent']:
            return MaintainabilityLevel.EXCELLENT
        elif mi_score >= self.mi_thresholds['good']:
            return MaintainabilityLevel.GOOD
        elif mi_score >= self.mi_thresholds['moderate']:
            return MaintainabilityLevel.MODERATE
        elif mi_score >= self.mi_thresholds['poor']:
            return MaintainabilityLevel.POOR
        else:
            return MaintainabilityLevel.CRITICAL
    
    async def _identify_hotspots(self, report: ProjectMaintainabilityReport):
        """Identify maintainability hotspots (ML Engineer expertise)"""
        hotspots = []
        
        # Sort files by maintainability issues
        sorted_files = sorted(report.file_metrics, key=lambda x: x.maintainability_index)
        
        # Top 10 worst files
        worst_files = sorted_files[:10]
        
        for file_metrics in worst_files:
            hotspot = {
                'file_path': file_metrics.file_path,
                'maintainability_index': file_metrics.maintainability_index,
                'cyclomatic_complexity': file_metrics.cyclomatic_complexity,
                'technical_debt_minutes': file_metrics.technical_debt_minutes,
                'lines_of_code': file_metrics.lines_of_code,
                'issues': []
            }
            
            # Identify specific issues
            if file_metrics.cyclomatic_complexity > self.complexity_thresholds['high']:
                hotspot['issues'].append('High cyclomatic complexity')
            
            if file_metrics.comment_ratio < 10:
                hotspot['issues'].append('Low comment ratio')
            
            if file_metrics.lines_of_code > 500:
                hotspot['issues'].append('Large file size')
            
            if file_metrics.average_function_length > 50:
                hotspot['issues'].append('Long functions')
            
            if file_metrics.max_nesting_depth > 5:
                hotspot['issues'].append('Deep nesting')
            
            hotspots.append(hotspot)
        
        report.hotspots = hotspots
    
    async def _generate_recommendations(self, report: ProjectMaintainabilityReport):
        """Generate maintainability recommendations (Lead Dev IA expertise)"""
        recommendations = []
        
        # Overall project recommendations
        if report.overall_maintainability_index < 40:
            recommendations.append("CRITICAL: Overall maintainability is poor. Consider major refactoring.")
        elif report.overall_maintainability_index < 60:
            recommendations.append("Project maintainability needs improvement. Focus on reducing complexity.")
        
        # Complexity recommendations
        if report.average_cyclomatic_complexity > 10:
            recommendations.append("High average complexity detected. Break down complex functions.")
        
        # Documentation recommendations
        if report.comment_ratio < 15:
            recommendations.append("Low comment ratio. Improve code documentation and inline comments.")
        
        # Technical debt recommendations
        if report.technical_debt_hours > 40:
            recommendations.append(f"High technical debt ({report.technical_debt_hours:.1f} hours). Prioritize refactoring.")
        
        # File-specific recommendations
        large_files = [fm for fm in report.file_metrics if fm.lines_of_code > 500]
        if large_files:
            recommendations.append(f"{len(large_files)} files are too large (>500 LOC). Consider splitting them.")
        
        complex_files = [fm for fm in report.file_metrics if fm.cyclomatic_complexity > 15]
        if complex_files:
            recommendations.append(f"{len(complex_files)} files have high complexity. Refactor to reduce complexity.")
        
        # Priority recommendations
        if report.hotspots:
            recommendations.append(f"Focus on top {min(5, len(report.hotspots))} maintainability hotspots first.")
        
        report.recommendations = recommendations
    
    async def _perform_risk_assessment(self, report: ProjectMaintainabilityReport):
        """Perform maintainability risk assessment (ML Engineer + Lead Dev expertise)"""
        risk_factors = {}
        
        # Calculate risk scores (0-100)
        complexity_risk = min(100, (report.average_cyclomatic_complexity / 20) * 100)
        size_risk = min(100, (report.total_lines_of_code / 50000) * 100)
        debt_risk = min(100, (report.technical_debt_hours / 100) * 100)
        documentation_risk = max(0, (20 - report.comment_ratio) * 5)
        
        # Hotspot concentration risk
        if report.file_metrics:
            bottom_20_percent = int(len(report.file_metrics) * 0.2)
            worst_files = sorted(report.file_metrics, key=lambda x: x.maintainability_index)[:bottom_20_percent]
            worst_files_loc = sum(fm.lines_of_code for fm in worst_files)
            hotspot_concentration = (worst_files_loc / max(report.total_lines_of_code, 1)) * 100
        else:
            hotspot_concentration = 0
        
        # Overall risk calculation
        overall_risk = (complexity_risk + size_risk + debt_risk + documentation_risk) / 4
        
        risk_factors = {
            'overall_risk_score': overall_risk,
            'complexity_risk': complexity_risk,
            'size_risk': size_risk,
            'technical_debt_risk': debt_risk,
            'documentation_risk': documentation_risk,
            'hotspot_concentration': hotspot_concentration,
            'risk_level': self._categorize_risk(overall_risk),
            'maintainability_trend': 'stable',  # Would require historical data
            'estimated_maintenance_effort': report.technical_debt_hours * 1.5  # Include overhead
        }
        
        report.risk_assessment = risk_factors
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level based on score"""
        if risk_score >= 80:
            return 'CRITICAL'
        elif risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        elif risk_score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    async def _save_report(self, report: ProjectMaintainabilityReport):
        """Save maintainability report (Backend expertise)"""
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        filename = f"maintainability_report_{report.project_name}_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Convert report to dict for JSON serialization
        report_dict = {
            'project_name': report.project_name,
            'generated_at': report.generated_at.isoformat(),
            'total_files': report.total_files,
            'total_lines_of_code': report.total_lines_of_code,
            'overall_maintainability_index': report.overall_maintainability_index,
            'maintainability_level': report.maintainability_level.value,
            'average_cyclomatic_complexity': report.average_cyclomatic_complexity,
            'average_halstead_volume': report.average_halstead_volume,
            'comment_ratio': report.comment_ratio,
            'duplication_percentage': report.duplication_percentage,
            'technical_debt_hours': report.technical_debt_hours,
            'recommendations': report.recommendations,
            'risk_assessment': report.risk_assessment,
            'hotspots': report.hotspots,
            'file_metrics': []
        }
        
        # Add file metrics (truncate for large projects)
        for fm in report.file_metrics[:100]:  # Limit to top 100 files
            file_dict = {
                'file_path': fm.file_path,
                'language': fm.language,
                'lines_of_code': fm.lines_of_code,
                'lines_of_comments': fm.lines_of_comments,
                'cyclomatic_complexity': fm.cyclomatic_complexity,
                'maintainability_index': fm.maintainability_index,
                'comment_ratio': fm.comment_ratio,
                'technical_debt_minutes': fm.technical_debt_minutes,
                'average_function_length': fm.average_function_length,
                'max_nesting_depth': fm.max_nesting_depth
            }
            report_dict['file_metrics'].append(file_dict)
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(report_dict, indent=2))
        
        logger.info(f"Maintainability report saved to: {filepath}")
    
    async def generate_maintainability_dashboard(self, report: ProjectMaintainabilityReport) -> str:
        """Generate HTML dashboard for maintainability report (Frontend + Backend expertise)"""
        
        # Create visualizations
        await self._create_maintainability_charts(report)
        
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Maintainability Dashboard - {report.project_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: #2c3e50; color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                .score {{ font-size: 64px; font-weight: bold; margin: 20px 0; }}
                .level-{report.maintainability_level.value} {{ 
                    color: {'#27ae60' if report.maintainability_level.value in ['excellent', 'good'] else 
                           '#f39c12' if report.maintainability_level.value == 'moderate' else 
                           '#e74c3c'}; 
                }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .metric-value {{ font-size: 32px; font-weight: bold; color: #2c3e50; }}
                .metric-label {{ color: #7f8c8d; font-size: 14px; }}
                .recommendations {{ background: white; padding: 30px; border-radius: 10px; margin: 30px 0; }}
                .hotspots {{ background: white; padding: 30px; border-radius: 10px; margin: 30px 0; }}
                .hotspot-item {{ padding: 15px; border-left: 4px solid #e74c3c; margin: 10px 0; background: #fff5f5; }}
                .risk-assessment {{ background: white; padding: 30px; border-radius: 10px; margin: 30px 0; }}
                .chart-container {{ text-align: center; margin: 30px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Maintainability Assessment</h1>
                    <h2>{report.project_name}</h2>
                    <div class="score level-{report.maintainability_level.value}">{report.overall_maintainability_index:.1f}</div>
                    <p>Maintainability Level: {report.maintainability_level.value.title()}</p>
                    <p>Generated: {report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">{report.total_files}</div>
                        <div class="metric-label">Total Files</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{report.total_lines_of_code:,}</div>
                        <div class="metric-label">Lines of Code</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{report.average_cyclomatic_complexity:.1f}</div>
                        <div class="metric-label">Avg Complexity</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{report.comment_ratio:.1f}%</div>
                        <div class="metric-label">Comment Ratio</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{report.technical_debt_hours:.1f}h</div>
                        <div class="metric-label">Technical Debt</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{report.risk_assessment.get('risk_level', 'UNKNOWN')}</div>
                        <div class="metric-label">Risk Level</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>Maintainability Distribution</h3>
                    <img src="maintainability_distribution.png" alt="Maintainability Distribution" style="max-width: 100%;">
                </div>
                
                <div class="recommendations">
                    <h3>🎯 Recommendations</h3>
                    <ul>
        """
        
        for recommendation in report.recommendations:
            dashboard_html += f"<li>{recommendation}</li>"
        
        dashboard_html += """
                    </ul>
                </div>
                
                <div class="hotspots">
                    <h3>🔥 Maintainability Hotspots</h3>
        """
        
        for hotspot in report.hotspots[:10]:
            dashboard_html += f"""
                    <div class="hotspot-item">
                        <h4>{hotspot['file_path']}</h4>
                        <p>MI: {hotspot['maintainability_index']:.1f} | 
                           Complexity: {hotspot['cyclomatic_complexity']:.1f} | 
                           Debt: {hotspot['technical_debt_minutes']:.1f}min</p>
                        <p>Issues: {', '.join(hotspot['issues'])}</p>
                    </div>
            """
        
        dashboard_html += f"""
                </div>
                
                <div class="risk-assessment">
                    <h3>⚠️ Risk Assessment</h3>
                    <p><strong>Overall Risk Score:</strong> {report.risk_assessment.get('overall_risk_score', 0):.1f}/100</p>
                    <p><strong>Risk Level:</strong> {report.risk_assessment.get('risk_level', 'UNKNOWN')}</p>
                    <p><strong>Estimated Maintenance Effort:</strong> {report.risk_assessment.get('estimated_maintenance_effort', 0):.1f} hours</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return dashboard_html
    
    async def _create_maintainability_charts(self, report: ProjectMaintainabilityReport):
        """Create visualization charts for maintainability data (ML Engineer expertise)"""
        if not report.file_metrics:
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Maintainability Analysis - {report.project_name}', fontsize=16, fontweight='bold')
        
        # 1. Maintainability Index Distribution
        mi_scores = [fm.maintainability_index for fm in report.file_metrics]
        ax1.hist(mi_scores, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        ax1.axvline(report.overall_maintainability_index, color='red', linestyle='--', 
                   label=f'Average: {report.overall_maintainability_index:.1f}')
        ax1.set_xlabel('Maintainability Index')
        ax1.set_ylabel('Number of Files')
        ax1.set_title('Maintainability Index Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Complexity vs File Size
        complexities = [fm.cyclomatic_complexity for fm in report.file_metrics]
        file_sizes = [fm.lines_of_code for fm in report.file_metrics]
        scatter = ax2.scatter(file_sizes, complexities, alpha=0.6, c=mi_scores, cmap='RdYlGn')
        ax2.set_xlabel('Lines of Code')
        ax2.set_ylabel('Cyclomatic Complexity')
        ax2.set_title('Complexity vs File Size')
        plt.colorbar(scatter, ax=ax2, label='Maintainability Index')
        ax2.grid(True, alpha=0.3)
        
        # 3. Technical Debt by File
        debt_data = [(fm.file_path.split('/')[-1], fm.technical_debt_minutes) 
                    for fm in sorted(report.file_metrics, key=lambda x: x.technical_debt_minutes, reverse=True)[:10]]
        
        if debt_data:
            files, debts = zip(*debt_data)
            ax3.barh(range(len(files)), debts, color='coral')
            ax3.set_yticks(range(len(files)))
            ax3.set_yticklabels([f[:20] + '...' if len(f) > 20 else f for f in files])
            ax3.set_xlabel('Technical Debt (minutes)')
            ax3.set_title('Top 10 Files by Technical Debt')
            ax3.grid(True, alpha=0.3)
        
        # 4. Language Distribution
        language_counts = {}
        language_debt = {}
        
        for fm in report.file_metrics:
            language = fm.language
            language_counts[language] = language_counts.get(language, 0) + 1
            language_debt[language] = language_debt.get(language, 0) + fm.technical_debt_minutes
        
        if language_counts:
            languages = list(language_counts.keys())
            counts = list(language_counts.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(languages)))
            
            wedges, texts, autotexts = ax4.pie(counts, labels=languages, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            ax4.set_title('Files by Language')
        
        plt.tight_layout()
        
        # Save the chart
        chart_path = self.reports_dir / "maintainability_distribution.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Maintainability charts saved to: {chart_path}")


# Global instance
maintainability_calculator = MaintainabilityIndexCalculator()


async def calculate_project_maintainability(project_path: str = ".") -> ProjectMaintainabilityReport:
    """Convenience function to calculate project maintainability"""
    calculator = MaintainabilityIndexCalculator(project_path)
    return await calculator.calculate_project_maintainability()


async def quick_maintainability_check(file_path: str) -> float:
    """Quick maintainability check for single file"""
    calculator = MaintainabilityIndexCalculator()
    file_metrics = await calculator._analyze_file(Path(file_path))
    return file_metrics.maintainability_index if file_metrics else 0.0


if __name__ == "__main__":
    # Example usage
    async def main():
        # Calculate maintainability for current project
        report = await calculate_project_maintainability(".")
        
        print(f"Project: {report.project_name}")
        print(f"Overall Maintainability Index: {report.overall_maintainability_index:.1f}")
        print(f"Maintainability Level: {report.maintainability_level.value}")
        print(f"Technical Debt: {report.technical_debt_hours:.1f} hours")
        print(f"Average Complexity: {report.average_cyclomatic_complexity:.1f}")
        
        if report.recommendations:
            print("\nRecommendations:")
            for rec in report.recommendations[:5]:
                print(f"  - {rec}")
        
        if report.hotspots:
            print(f"\nTop 3 Hotspots:")
            for hotspot in report.hotspots[:3]:
                print(f"  - {hotspot['file_path']}: MI={hotspot['maintainability_index']:.1f}")
    
    asyncio.run(main())