"""📊 Code Complexity Analyzer - Ainflue Platform
================================================================
Expert: SOFTWARE_ARCHITECT + QUALITY_ENGINEER + TECHNICAL_LEAD
Created: 2025-01-XX
Author: Fahed Mlaiel (mlaiel@live.de)

Advanced code complexity analysis engine that measures cyclomatic complexity,
cognitive complexity, maintainability index, and technical debt indicators.
================================================================
"""

import ast
import asyncio
import json
import logging
import math
import statistics
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import subprocess
import concurrent.futures
import radon.complexity as radon_cc
import radon.metrics as radon_metrics
from radon.visitors import ComplexityVisitor

logger = logging.getLogger(__name__)

class ComplexityType(Enum):
    """Types of complexity metrics"""
    CYCLOMATIC = "cyclomatic"
    COGNITIVE = "cognitive"
    HALSTEAD = "halstead"
    MAINTAINABILITY_INDEX = "maintainability_index"
    NESTING_DEPTH = "nesting_depth"
    CLASS_COUPLING = "class_coupling"
    INHERITANCE_DEPTH = "inheritance_depth"
    LINES_OF_CODE = "lines_of_code"

class ComplexityLevel(Enum):
    """Complexity severity levels"""
    SIMPLE = "simple"           # 1-5
    MODERATE = "moderate"       # 6-10
    COMPLEX = "complex"         # 11-20
    VERY_COMPLEX = "very_complex" # 21-50
    EXTREMELY_COMPLEX = "extremely_complex" # 50+

@dataclass
class ComplexityMetric:
    """Individual complexity metric"""
    name: str
    complexity_type: ComplexityType
    value: float
    level: ComplexityLevel
    threshold: float
    file_path: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    line_number: int = 0
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)

@dataclass
class FileComplexity:
    """Complexity metrics for a single file"""
    file_path: str
    total_complexity: float
    average_complexity: float
    max_complexity: float
    function_count: int
    class_count: int
    lines_of_code: int
    metrics: List[ComplexityMetric] = field(default_factory=list)
    maintainability_index: float = 0.0
    technical_debt_ratio: float = 0.0
    refactoring_candidates: List[str] = field(default_factory=list)

@dataclass
class ProjectComplexity:
    """Overall project complexity analysis"""
    project_name: str
    total_files: int
    analyzed_files: int
    total_functions: int
    total_classes: int
    total_lines: int
    overall_complexity: float
    average_complexity: float
    complexity_distribution: Dict[ComplexityLevel, int]
    file_complexities: List[FileComplexity]
    hotspots: List[ComplexityMetric]
    recommendations: List[str]
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)

class PythonComplexityVisitor(ast.NodeVisitor):
    """Custom AST visitor for detailed complexity analysis"""
    
    def __init__(self) -> None:
        self.complexity_data = []
        self.current_function = None
        self.current_class = None
        self.nesting_depth = 0
        self.max_nesting_depth = 0

    def visit_FunctionDef(self, node) -> None:
        """Visit function definition"""
        old_function = self.current_function
        self.current_function = node.name
        
        # Calculate cyclomatic complexity for this function
        complexity = self._calculate_cyclomatic_complexity(node)
        cognitive_complexity = self._calculate_cognitive_complexity(node)
        
        self.complexity_data.append({
            'type': 'function',
            'name': node.name,
            'class': self.current_class,
            'line': node.lineno,
            'cyclomatic_complexity': complexity,
            'cognitive_complexity': cognitive_complexity,
            'nesting_depth': self._calculate_max_nesting_depth(node)
        })
        
        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node) -> None:
        """Visit async function definition"""
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node) -> None:
        """Visit class definition"""
        old_class = self.current_class
        self.current_class = node.name
        
        # Calculate class complexity metrics
        method_count = len([n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
        inheritance_depth = len(node.bases)
        
        self.complexity_data.append({
            'type': 'class',
            'name': node.name,
            'line': node.lineno,
            'method_count': method_count,
            'inheritance_depth': inheritance_depth,
            'coupling': self._calculate_class_coupling(node)
        })
        
        self.generic_visit(node)
        self.current_class = old_class

    def visit_If(self, node) -> None:
        """Visit if statement"""
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_For(self, node) -> None:
        """Visit for loop"""
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_While(self, node) -> None:
        """Visit while loop"""
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def _calculate_cyclomatic_complexity(self, node) -> None:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
        
        return complexity

    def _calculate_cognitive_complexity(self, node) -> None:
        """Calculate cognitive complexity (more intuitive than cyclomatic)"""
        complexity = 0
        nesting_level = 0
        
        def calculate_recursive(node, nesting) -> None:
            nonlocal complexity
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1 + nesting
                    calculate_recursive(child, nesting + 1)
                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1
                elif isinstance(child, (ast.ExceptHandler, ast.With, ast.AsyncWith)):
                    complexity += 1 + nesting
                else:
                    calculate_recursive(child, nesting)
        
        calculate_recursive(node, 0)
        return complexity

    def _calculate_max_nesting_depth(self, node) -> None:
        """Calculate maximum nesting depth in a function"""
        max_depth = 0
        
        def calculate_depth(node, current_depth=0) -> None:
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith)):
                    calculate_depth(child, current_depth + 1)
                else:
                    calculate_depth(child, current_depth)
        
        calculate_depth(node)
        return max_depth

    def _calculate_class_coupling(self, node) -> None:
        """Calculate coupling between classes (simplified)"""
        coupling = 0
        
        # Count external class references
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                if child.id.istitle():  # Likely a class name
                    coupling += 1
        
        return coupling

class CodeComplexityAnalyzer:
    """
    Advanced code complexity analyzer for Python projects
    """
    
    def __init__(self, project_root -> None: Optional[str] = None) -> None:
        """Initialize complexity analyzer"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.project_root = Path(project_root or ".")
        self.complexity_thresholds = self._get_default_thresholds()
        self.exclude_patterns = [
            "**/test_*",
            "**/tests/**",
            "**/__pycache__/**",
            "**/migrations/**",
            "**/venv/**",
            "**/env/**",
            "**/.git/**"
        ]

    def _get_default_thresholds(self) -> Dict[str, float]:
        """Get default complexity thresholds"""
        return {
            "cyclomatic_complexity": {
                "simple": 5,
                "moderate": 10,
                "complex": 20,
                "very_complex": 50
            },
            "cognitive_complexity": {
                "simple": 5,
                "moderate": 10,
                "complex": 15,
                "very_complex": 25
            },
            "maintainability_index": {
                "excellent": 85,
                "good": 70,
                "moderate": 50,
                "poor": 25
            },
            "lines_per_function": 50,
            "max_nesting_depth": 4,
            "class_coupling": 10,
            "inheritance_depth": 5
        }

    async def analyze_project(self, include_patterns: Optional[List[str]] = None) -> ProjectComplexity:
        """Analyze complexity of entire project"""
        start_time = time.time()
        self.logger.info("Starting project complexity analysis")
        
        # Find Python files to analyze
        python_files = self._find_python_files(include_patterns)
        self.logger.info(f"Found {len(python_files)} Python files to analyze")
        
        # Analyze files in parallel
        file_complexities = await self._analyze_files_parallel(python_files)
        
        # Calculate project-level metrics
        project_complexity = self._calculate_project_metrics(file_complexities)
        
        execution_time = time.time() - start_time
        self.logger.info(f"Complexity analysis completed in {execution_time:.2f}s")
        
        return project_complexity

    def _find_python_files(self, include_patterns: Optional[List[str]] = None) -> List[Path]:
        """Find Python files to analyze"""
        patterns = include_patterns or ["**/*.py"]
        python_files = []
        
        for pattern in patterns:
            found_files = list(self.project_root.glob(pattern))
            python_files.extend(found_files)
        
        # Filter out excluded files
        filtered_files = []
        for file_path in python_files:
            if not any(file_path.match(exclude) for exclude in self.exclude_patterns):
                filtered_files.append(file_path)
        
        return sorted(set(filtered_files))

    async def _analyze_files_parallel(self, files: List[Path]) -> List[FileComplexity]:
        """Analyze files in parallel for better performance"""
        max_workers = min(8, len(files))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, self._analyze_file, file_path)
                for file_path in files
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        file_complexities = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Error analyzing {files[i]}: {result}")
            elif result is not None:
                file_complexities.append(result)
        
        return file_complexities

    def _analyze_file(self, file_path: Path) -> Optional[FileComplexity]:
        """Analyze complexity of a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                self.logger.warning(f"Syntax error in {file_path}: {e}")
                return None
            
            # Use custom visitor
            visitor = PythonComplexityVisitor()
            visitor.visit(tree)
            
            # Use radon for additional metrics
            radon_result = radon_cc.cc_visit(content)
            halstead_result = radon_metrics.h_visit(content)
            
            # Calculate metrics
            metrics = self._calculate_file_metrics(
                file_path, content, visitor.complexity_data, radon_result, halstead_result
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            return None

    def _calculate_file_metrics(self, file_path: Path, content: str, 
                               visitor_data: List[Dict], radon_result: List,
                               halstead_result: Any) -> FileComplexity:
        """Calculate comprehensive metrics for a file"""
        
        # Basic file statistics
        lines_of_code = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
        function_count = len([item for item in visitor_data if item['type'] == 'function'])
        class_count = len([item for item in visitor_data if item['type'] == 'class'])
        
        # Complexity metrics
        complexity_metrics = []
        total_complexity = 0
        max_complexity = 0
        
        # Process function complexities
        for item in visitor_data:
            if item['type'] == 'function':
                cyclomatic = item['cyclomatic_complexity']
                cognitive = item['cognitive_complexity']
                nesting = item['nesting_depth']
                
                total_complexity += cyclomatic
                max_complexity = max(max_complexity, cyclomatic)
                
                # Create complexity metrics
                complexity_metrics.append(ComplexityMetric(
                    name=item['name'],
                    complexity_type=ComplexityType.CYCLOMATIC,
                    value=cyclomatic,
                    level=self._get_complexity_level(cyclomatic, 'cyclomatic_complexity'),
                    threshold=self.complexity_thresholds['cyclomatic_complexity']['complex'],
                    file_path=str(file_path),
                    function_name=item['name'],
                    class_name=item.get('class'),
                    line_number=item['line'],
                    details={'cognitive_complexity': cognitive, 'nesting_depth': nesting},
                    suggestions=self._generate_complexity_suggestions(cyclomatic, cognitive, nesting)
                ))
        
        # Calculate averages
        average_complexity = total_complexity / function_count if function_count > 0 else 0
        
        # Calculate maintainability index
        maintainability_index = self._calculate_maintainability_index(
            lines_of_code, average_complexity, halstead_result
        )
        
        # Calculate technical debt ratio
        technical_debt_ratio = self._calculate_technical_debt_ratio(complexity_metrics)
        
        # Identify refactoring candidates
        refactoring_candidates = self._identify_refactoring_candidates(complexity_metrics)
        
        return FileComplexity(
            file_path=str(file_path.relative_to(self.project_root)),
            total_complexity=total_complexity,
            average_complexity=average_complexity,
            max_complexity=max_complexity,
            function_count=function_count,
            class_count=class_count,
            lines_of_code=lines_of_code,
            metrics=complexity_metrics,
            maintainability_index=maintainability_index,
            technical_debt_ratio=technical_debt_ratio,
            refactoring_candidates=refactoring_candidates
        )

    def _get_complexity_level(self, value: float, complexity_type: str) -> ComplexityLevel:
        """Determine complexity level based on value and type"""
        thresholds = self.complexity_thresholds.get(complexity_type, {})
        
        if value <= thresholds.get('simple', 5):
            return ComplexityLevel.SIMPLE
        elif value <= thresholds.get('moderate', 10):
            return ComplexityLevel.MODERATE
        elif value <= thresholds.get('complex', 20):
            return ComplexityLevel.COMPLEX
        elif value <= thresholds.get('very_complex', 50):
            return ComplexityLevel.VERY_COMPLEX
        else:
            return ComplexityLevel.EXTREMELY_COMPLEX

    def _calculate_maintainability_index(self, lines_of_code: int, 
                                       avg_complexity: float, halstead: Any) -> float:
        """Calculate maintainability index using Halstead metrics"""
        try:
            # Simplified maintainability index calculation
            # MI = 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code)
            
            if hasattr(halstead, 'volume') and halstead.volume > 0:
                volume = halstead.volume
            else:
                volume = lines_of_code * 10  # Fallback estimation
            
            if volume <= 0 or lines_of_code <= 0:
                return 50.0  # Default moderate value
            
            mi = 171 - 5.2 * math.log(volume) - 0.23 * avg_complexity - 16.2 * math.log(lines_of_code)
            
            # Normalize to 0-100 scale
            return max(0, min(100, mi))
            
        except (ValueError, ZeroDivisionError, AttributeError):
            return 50.0  # Default moderate value

    def _calculate_technical_debt_ratio(self, metrics: List[ComplexityMetric]) -> float:
        """Calculate technical debt ratio based on complexity violations"""
        if not metrics:
            return 0.0
        
        complex_functions = len([m for m in metrics 
                               if m.level in [ComplexityLevel.COMPLEX, 
                                            ComplexityLevel.VERY_COMPLEX, 
                                            ComplexityLevel.EXTREMELY_COMPLEX]])
        
        return (complex_functions / len(metrics)) * 100

    def _identify_refactoring_candidates(self, metrics: List[ComplexityMetric]) -> List[str]:
        """Identify functions that are candidates for refactoring"""
        candidates = []
        
        for metric in metrics:
            if metric.level in [ComplexityLevel.VERY_COMPLEX, ComplexityLevel.EXTREMELY_COMPLEX]:
                candidates.append(f"{metric.function_name} (complexity: {metric.value})")
            elif metric.level == ComplexityLevel.COMPLEX and metric.value > 15:
                candidates.append(f"{metric.function_name} (complexity: {metric.value})")
        
        return candidates

    def _generate_complexity_suggestions(self, cyclomatic: float, 
                                       cognitive: float, nesting: int) -> List[str]:
        """Generate suggestions for reducing complexity"""
        suggestions = []
        
        if cyclomatic > 20:
            suggestions.append("Break this function into smaller, more focused functions")
            suggestions.append("Consider using the Strategy pattern to handle different cases")
        elif cyclomatic > 10:
            suggestions.append("Extract some logic into helper functions")
        
        if cognitive > 15:
            suggestions.append("Reduce cognitive load by simplifying conditional logic")
            suggestions.append("Consider using early returns to reduce nesting")
        
        if nesting > 4:
            suggestions.append("Reduce nesting depth by extracting nested blocks into functions")
            suggestions.append("Use guard clauses to reduce indentation levels")
        
        return suggestions

    def _calculate_project_metrics(self, file_complexities: List[FileComplexity]) -> ProjectComplexity:
        """Calculate project-level complexity metrics"""
        
        if not file_complexities:
            return ProjectComplexity(
                project_name=self.project_root.name,
                total_files=0,
                analyzed_files=0,
                total_functions=0,
                total_classes=0,
                total_lines=0,
                overall_complexity=0.0,
                average_complexity=0.0,
                complexity_distribution={level: 0 for level in ComplexityLevel},
                file_complexities=[],
                hotspots=[],
                recommendations=[]
            )
        
        # Aggregate statistics
        total_functions = sum(fc.function_count for fc in file_complexities)
        total_classes = sum(fc.class_count for fc in file_complexities)
        total_lines = sum(fc.lines_of_code for fc in file_complexities)
        total_complexity = sum(fc.total_complexity for fc in file_complexities)
        
        # Calculate averages
        average_complexity = total_complexity / total_functions if total_functions > 0 else 0
        
        # Calculate complexity distribution
        all_metrics = []
        for fc in file_complexities:
            all_metrics.extend(fc.metrics)
        
        complexity_distribution = {level: 0 for level in ComplexityLevel}
        for metric in all_metrics:
            complexity_distribution[metric.level] += 1
        
        # Identify hotspots (most complex functions)
        hotspots = sorted(all_metrics, key=lambda m: m.value, reverse=True)[:10]
        
        # Generate recommendations
        recommendations = self._generate_project_recommendations(file_complexities, complexity_distribution)
        
        return ProjectComplexity(
            project_name=self.project_root.name,
            total_files=len(list(self.project_root.rglob("*.py"))),
            analyzed_files=len(file_complexities),
            total_functions=total_functions,
            total_classes=total_classes,
            total_lines=total_lines,
            overall_complexity=total_complexity,
            average_complexity=average_complexity,
            complexity_distribution=complexity_distribution,
            file_complexities=file_complexities,
            hotspots=hotspots,
            recommendations=recommendations
        )

    def _generate_project_recommendations(self, file_complexities: List[FileComplexity],
                                        distribution: Dict[ComplexityLevel, int]) -> List[str]:
        """Generate project-level recommendations"""
        recommendations = []
        
        # Check overall complexity
        very_complex = distribution.get(ComplexityLevel.VERY_COMPLEX, 0)
        extremely_complex = distribution.get(ComplexityLevel.EXTREMELY_COMPLEX, 0)
        total_functions = sum(distribution.values())
        
        if total_functions > 0:
            complex_ratio = (very_complex + extremely_complex) / total_functions
            
            if complex_ratio > 0.2:
                recommendations.append("Consider major refactoring - 20%+ of functions are highly complex")
            elif complex_ratio > 0.1:
                recommendations.append("Focus on reducing complexity in the most complex functions")
        
        # Check maintainability
        low_maintainability = [fc for fc in file_complexities if fc.maintainability_index < 50]
        if len(low_maintainability) > len(file_complexities) * 0.3:
            recommendations.append("Improve maintainability by reducing complexity and improving documentation")
        
        # Check technical debt
        high_debt_files = [fc for fc in file_complexities if fc.technical_debt_ratio > 30]
        if high_debt_files:
            recommendations.append(f"Address technical debt in {len(high_debt_files)} files with high complexity ratios")
        
        # File-specific recommendations
        large_files = [fc for fc in file_complexities if fc.lines_of_code > 500]
        if large_files:
            recommendations.append(f"Consider splitting {len(large_files)} large files (>500 LOC) into smaller modules")
        
        return recommendations

    def generate_report(self, analysis: ProjectComplexity, format: str = "json") -> str:
        """Generate complexity analysis report"""
        if format == "json":
            return self._generate_json_report(analysis)
        elif format == "markdown":
            return self._generate_markdown_report(analysis)
        elif format == "html":
            return self._generate_html_report(analysis)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_json_report(self, analysis: ProjectComplexity) -> str:
        """Generate JSON report"""
        # Convert to serializable format
        data = {
            "project_name": analysis.project_name,
            "analysis_timestamp": analysis.analysis_timestamp.isoformat(),
            "summary": {
                "total_files": analysis.total_files,
                "analyzed_files": analysis.analyzed_files,
                "total_functions": analysis.total_functions,
                "total_classes": analysis.total_classes,
                "total_lines": analysis.total_lines,
                "overall_complexity": analysis.overall_complexity,
                "average_complexity": analysis.average_complexity
            },
            "complexity_distribution": {
                level.value: count for level, count in analysis.complexity_distribution.items()
            },
            "hotspots": [
                {
                    "function": hotspot.function_name,
                    "file": hotspot.file_path,
                    "complexity": hotspot.value,
                    "level": hotspot.level.value,
                    "line": hotspot.line_number
                }
                for hotspot in analysis.hotspots[:5]
            ],
            "recommendations": analysis.recommendations
        }
        
        return json.dumps(data, indent=2)

    def _generate_markdown_report(self, analysis: ProjectComplexity) -> str:
        """Generate Markdown report"""
        total_functions = analysis.total_functions
        complex_functions = (
            analysis.complexity_distribution.get(ComplexityLevel.COMPLEX, 0) +
            analysis.complexity_distribution.get(ComplexityLevel.VERY_COMPLEX, 0) +
            analysis.complexity_distribution.get(ComplexityLevel.EXTREMELY_COMPLEX, 0)
        )
        
        complexity_percentage = (complex_functions / total_functions * 100) if total_functions > 0 else 0
        
        md = f"""# Code Complexity Analysis - {analysis.project_name}

**Generated:** {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Total Files | {analysis.total_files} |
| Analyzed Files | {analysis.analyzed_files} |
| Total Functions | {analysis.total_functions} |
| Total Classes | {analysis.total_classes} |
| Total Lines | {analysis.total_lines:,} |
| Average Complexity | {analysis.average_complexity:.1f} |
| Complex Functions | {complex_functions} ({complexity_percentage:.1f}%) |

## Complexity Distribution

| Level | Count | Percentage |
|-------|-------|------------|
"""
        
        for level, count in analysis.complexity_distribution.items():
            percentage = (count / total_functions * 100) if total_functions > 0 else 0
            md += f"| {level.value.title()} | {count} | {percentage:.1f}% |\n"
        
        if analysis.hotspots:
            md += "\n## Complexity Hotspots\n\n"
            for i, hotspot in enumerate(analysis.hotspots[:5], 1):
                md += f"{i}. **{hotspot.function_name}** in `{hotspot.file_path}` (complexity: {hotspot.value})\n"
        
        if analysis.recommendations:
            md += "\n## Recommendations\n\n"
            for i, rec in enumerate(analysis.recommendations, 1):
                md += f"{i}. {rec}\n"
        
        return md

    def _generate_html_report(self, analysis: ProjectComplexity) -> str:
        """Generate HTML report"""
        return f"""
        <html>
        <head><title>Code Complexity Analysis - {analysis.project_name}</title></head>
        <body>
        <h1>Code Complexity Analysis - {analysis.project_name}</h1>
        <p><strong>Generated:</strong> {analysis.analysis_timestamp}</p>
        <p><strong>Average Complexity:</strong> {analysis.average_complexity:.1f}</p>
        <p><strong>Total Functions:</strong> {analysis.total_functions}</p>
        </body>
        </html>
        """

    async def monitor_complexity_trends(self, days: int = 30) -> Dict[str, Any]:
        """Monitor complexity trends over time"""
        # This would integrate with historical data storage
        # For now, return current analysis
        current_analysis = await self.analyze_project()
        
        return {
            "current_complexity": current_analysis.average_complexity,
            "trend": "stable",  # Would calculate from historical data
            "hotspots_trend": len(current_analysis.hotspots),
            "recommendations": current_analysis.recommendations
        }

# Global code complexity analyzer instance
code_complexity_analyzer = CodeComplexityAnalyzer()

__all__ = [
    "CodeComplexityAnalyzer",
    "ComplexityMetric",
    "FileComplexity", 
    "ProjectComplexity",
    "ComplexityType",
    "ComplexityLevel",
    "code_complexity_analyzer"
]