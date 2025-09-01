#!/usr/bin/env python3
"""
Documentation Coverage Validation for Ainflue Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Description: Automated documentation coverage analysis and validation
"""

import ast
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import subprocess


@dataclass
class DocCoverageResult:
    """Documentation coverage result data structure"""
    file_path: str
    total_items: int
    documented_items: int
    coverage_percentage: float
    missing_docs: List[str]
    doc_quality_score: float


class DocumentationAnalyzer:
    """Advanced documentation coverage analyzer"""
    
    def __init__(self, source_dirs: List[str] = None, min_coverage: float = 80.0):
        self.source_dirs = source_dirs or ['.']
        self.min_coverage = min_coverage
        self.results: List[DocCoverageResult] = []
        self.excluded_patterns = {
            '__pycache__',
            '.git',
            '.pytest_cache',
            'node_modules',
            'venv',
            'env',
            'dist',
            'build',
            'migrations',
            'test_',
            '_test',
            'conftest'
        }
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis"""
        file_str = str(file_path)
        return any(pattern in file_str for pattern in self.excluded_patterns)
    
    def extract_docstrings_and_items(self, file_path: Path) -> Tuple[Set[str], Set[str]]:
        """Extract documented and undocumented items from Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            documented_items = set()
            all_items = set()
            
            for node in ast.walk(tree):
                item_name = None
                has_docstring = False
                
                if isinstance(node, ast.FunctionDef):
                    item_name = f"function:{node.name}"
                    has_docstring = (ast.get_docstring(node) is not None)
                elif isinstance(node, ast.AsyncFunctionDef):
                    item_name = f"async_function:{node.name}"
                    has_docstring = (ast.get_docstring(node) is not None)
                elif isinstance(node, ast.ClassDef):
                    item_name = f"class:{node.name}"
                    has_docstring = (ast.get_docstring(node) is not None)
                elif isinstance(node, ast.Module):
                    item_name = "module"
                    has_docstring = (ast.get_docstring(node) is not None)
                
                if item_name:
                    all_items.add(item_name)
                    if has_docstring:
                        documented_items.add(item_name)
            
            return documented_items, all_items
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return set(), set()
    
    def analyze_docstring_quality(self, file_path: Path) -> float:
        """Analyze quality of docstrings in file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            quality_scores = []
            
            for node in ast.walk(tree):
                docstring = ast.get_docstring(node)
                if docstring:
                    score = self.score_docstring_quality(docstring)
                    quality_scores.append(score)
            
            return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
        except Exception:
            return 0.0
    
    def score_docstring_quality(self, docstring: str) -> float:
        """Score individual docstring quality (0-100)"""
        score = 0.0
        
        # Basic presence (20 points)
        if docstring.strip():
            score += 20
        
        # Length check (20 points)
        if len(docstring.strip()) >= 20:
            score += 20
        
        # Has parameters description (20 points)
        if re.search(r'(Args?|Parameters?|Param):', docstring, re.IGNORECASE):
            score += 20
        
        # Has return description (20 points)
        if re.search(r'(Returns?|Return):', docstring, re.IGNORECASE):
            score += 20
        
        # Has examples (20 points)
        if re.search(r'(Example|Examples):', docstring, re.IGNORECASE):
            score += 20
        
        return min(100.0, score)
    
    def analyze_file(self, file_path: Path) -> DocCoverageResult:
        """Analyze documentation coverage for a single file"""
        documented_items, all_items = self.extract_docstrings_and_items(file_path)
        
        total_items = len(all_items)
        documented_count = len(documented_items)
        coverage_percentage = (documented_count / total_items * 100) if total_items > 0 else 100.0
        missing_docs = list(all_items - documented_items)
        quality_score = self.analyze_docstring_quality(file_path)
        
        return DocCoverageResult(
            file_path=str(file_path),
            total_items=total_items,
            documented_items=documented_count,
            coverage_percentage=coverage_percentage,
            missing_docs=missing_docs,
            doc_quality_score=quality_score
        )
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files to analyze"""
        python_files = []
        
        for source_dir in self.source_dirs:
            source_path = Path(source_dir)
            if source_path.is_file() and source_path.suffix == '.py':
                if not self.should_exclude_file(source_path):
                    python_files.append(source_path)
            elif source_path.is_dir():
                for py_file in source_path.rglob('*.py'):
                    if not self.should_exclude_file(py_file):
                        python_files.append(py_file)
        
        return python_files
    
    def run_interrogate(self) -> Dict:
        """Run interrogate tool for additional analysis"""
        try:
            cmd = [
                'interrogate',
                '--verbose',
                '--ignore-init-method',
                '--ignore-init-module',
                '--ignore-magic',
                '--ignore-module',
                '--ignore-private',
                '--fail-under', str(self.min_coverage),
                '--generate-badge', 'docs-badge.svg',
                '--output', 'interrogate-report.txt',
                '.'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse interrogate output
            output_lines = result.stdout.split('\n')
            coverage_line = [line for line in output_lines if 'Overall coverage:' in line]
            
            if coverage_line:
                coverage_match = re.search(r'(\d+\.?\d*)%', coverage_line[0])
                overall_coverage = float(coverage_match.group(1)) if coverage_match else 0.0
            else:
                overall_coverage = 0.0
            
            return {
                'tool': 'interrogate',
                'overall_coverage': overall_coverage,
                'output': result.stdout,
                'success': result.returncode == 0
            }
            
        except Exception as e:
            return {
                'tool': 'interrogate',
                'overall_coverage': 0.0,
                'error': str(e),
                'success': False
            }
    
    def run_pydocstyle(self) -> Dict:
        """Run pydocstyle for docstring style checking"""
        try:
            cmd = [
                'pydocstyle',
                '--count',
                '--convention=google',
                '--add-ignore=D100,D104,D105',
                '.'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Count violations
            violation_count = len([line for line in result.stdout.split('\n') if line.strip()])
            
            return {
                'tool': 'pydocstyle',
                'violations': violation_count,
                'output': result.stdout,
                'success': result.returncode == 0 or violation_count < 50  # Allow some violations
            }
            
        except Exception as e:
            return {
                'tool': 'pydocstyle',
                'violations': 999,
                'error': str(e),
                'success': False
            }
    
    def analyze_all_files(self) -> Dict:
        """Analyze documentation coverage for all files"""
        print("🔍 Analyzing documentation coverage...")
        
        python_files = self.find_python_files()
        print(f"Found {len(python_files)} Python files to analyze")
        
        # Analyze each file
        for file_path in python_files:
            result = self.analyze_file(file_path)
            self.results.append(result)
        
        # Calculate overall statistics
        total_items = sum(r.total_items for r in self.results)
        total_documented = sum(r.documented_items for r in self.results)
        overall_coverage = (total_documented / total_items * 100) if total_items > 0 else 100.0
        average_quality = sum(r.doc_quality_score for r in self.results) / len(self.results) if self.results else 0.0
        
        # Find files below threshold
        low_coverage_files = [r for r in self.results if r.coverage_percentage < self.min_coverage]
        
        # Run external tools
        interrogate_result = self.run_interrogate()
        pydocstyle_result = self.run_pydocstyle()
        
        return {
            'summary': {
                'total_files': len(self.results),
                'total_items': total_items,
                'documented_items': total_documented,
                'overall_coverage': overall_coverage,
                'average_quality_score': average_quality,
                'files_below_threshold': len(low_coverage_files),
                'coverage_threshold': self.min_coverage
            },
            'file_results': [
                {
                    'file': r.file_path,
                    'coverage': r.coverage_percentage,
                    'quality': r.doc_quality_score,
                    'missing_count': len(r.missing_docs),
                    'missing_items': r.missing_docs[:5]  # Show first 5 missing items
                }
                for r in self.results
            ],
            'low_coverage_files': [
                {
                    'file': r.file_path,
                    'coverage': r.coverage_percentage,
                    'missing_items': r.missing_docs
                }
                for r in low_coverage_files
            ],
            'external_tools': {
                'interrogate': interrogate_result,
                'pydocstyle': pydocstyle_result
            }
        }
    
    def generate_report(self, output_file: str = "doc-coverage-report.json") -> Dict:
        """Generate comprehensive documentation coverage report"""
        analysis_result = self.analyze_all_files()
        
        # Add metadata
        report = {
            'timestamp': subprocess.run(['date', '-Iseconds'], capture_output=True, text=True).stdout.strip(),
            'analysis': analysis_result,
            'quality_gates': {
                'coverage_passed': analysis_result['summary']['overall_coverage'] >= self.min_coverage,
                'quality_score': analysis_result['summary']['average_quality_score'],
                'external_tools_passed': (
                    analysis_result['external_tools']['interrogate'].get('success', False) and
                    analysis_result['external_tools']['pydocstyle'].get('success', False)
                )
            },
            'recommendations': self.generate_recommendations(analysis_result)
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        overall_coverage = analysis['summary']['overall_coverage']
        quality_score = analysis['summary']['average_quality_score']
        
        if overall_coverage < self.min_coverage:
            recommendations.append(
                f"Increase documentation coverage from {overall_coverage:.1f}% to at least {self.min_coverage}%"
            )
        
        if quality_score < 60:
            recommendations.append(
                "Improve docstring quality by adding parameter descriptions, return values, and examples"
            )
        
        if analysis['summary']['files_below_threshold'] > 0:
            recommendations.append(
                f"Focus on {analysis['summary']['files_below_threshold']} files with low documentation coverage"
            )
        
        # Check external tools
        if not analysis['external_tools']['pydocstyle'].get('success', False):
            recommendations.append("Fix docstring style violations identified by pydocstyle")
        
        if not recommendations:
            recommendations.append("Documentation coverage meets quality standards! Consider adding more examples.")
        
        return recommendations
    
    def print_summary(self, report: Dict):
        """Print documentation coverage summary"""
        analysis = report['analysis']
        quality_gates = report['quality_gates']
        
        print("\n📚 Documentation Coverage Analysis Results")
        print("=" * 50)
        print(f"Overall Coverage: {analysis['summary']['overall_coverage']:.1f}%")
        print(f"Quality Score: {analysis['summary']['average_quality_score']:.1f}/100")
        print(f"Files Analyzed: {analysis['summary']['total_files']}")
        print(f"Items Documented: {analysis['summary']['documented_items']}/{analysis['summary']['total_items']}")
        print(f"Files Below Threshold: {analysis['summary']['files_below_threshold']}")
        
        # Quality gates status
        print(f"\n🚪 Quality Gates:")
        coverage_status = "✅ PASSED" if quality_gates['coverage_passed'] else "❌ FAILED"
        tools_status = "✅ PASSED" if quality_gates['external_tools_passed'] else "❌ FAILED"
        print(f"Coverage Threshold: {coverage_status}")
        print(f"External Tools: {tools_status}")
        
        # Recommendations
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # Low coverage files
        if analysis['low_coverage_files']:
            print(f"\n⚠️ Files needing documentation attention:")
            for file_info in analysis['low_coverage_files'][:5]:  # Show first 5
                print(f"  - {file_info['file']}: {file_info['coverage']:.1f}%")


def main():
    """Main documentation coverage analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Documentation Coverage Analysis")
    parser.add_argument('--min-coverage', type=float, default=80.0,
                       help='Minimum documentation coverage threshold (default: 80.0)')
    parser.add_argument('--source-dirs', nargs='+', default=['.'],
                       help='Source directories to analyze (default: current directory)')
    parser.add_argument('--output', default='doc-coverage-report.json',
                       help='Output report file (default: doc-coverage-report.json)')
    
    args = parser.parse_args()
    
    analyzer = DocumentationAnalyzer(
        source_dirs=args.source_dirs,
        min_coverage=args.min_coverage
    )
    
    try:
        report = analyzer.generate_report(args.output)
        analyzer.print_summary(report)
        
        # Determine exit code
        quality_gates = report['quality_gates']
        if quality_gates['coverage_passed'] and quality_gates['external_tools_passed']:
            print("\n✅ Documentation coverage validation PASSED")
            exit(0)
        else:
            print("\n❌ Documentation coverage validation FAILED")
            exit(1)
            
    except Exception as e:
        print(f"❌ Documentation analysis failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()