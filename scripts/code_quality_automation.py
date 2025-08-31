#!/usr/bin/env python3
"""
Code Quality Automation Script
=============================

Industrial-grade Python code quality automation system for the Ainflue platform.
Provides comprehensive syntax checking, style correction, and docstring standardization
according to PEP257 standards.

Author: Infrastructure Automation System
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
import ast
import re
import argparse
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CodeQualityResult:
    """Result of code quality analysis for a single file."""
    file_path: str
    syntax_errors: List[str]
    style_issues: List[str]
    docstring_issues: List[str]
    fixed_issues: List[str]
    status: str  # 'success', 'warning', 'error'


class SyntaxValidator:
    """Validates Python syntax and identifies common errors."""
    
    @staticmethod
    def check_syntax(file_path: str) -> List[str]:
        """Check Python file for syntax errors."""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                ast.parse(content)
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
        return errors


class StyleCorrector:
    """Corrects common Python style issues according to PEP8."""
    
    @staticmethod
    def fix_whitespace_issues(content: str) -> Tuple[str, List[str]]:
        """Fix common whitespace issues."""
        fixes = []
        lines = content.splitlines()
        fixed_lines = []
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Remove trailing whitespace
            line = line.rstrip()
            if line != original_line and original_line.strip():
                fixes.append(f"Line {i+1}: Removed trailing whitespace")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines) + '\n', fixes
    
    @staticmethod
    def fix_import_order(content: str) -> Tuple[str, List[str]]:
        """Fix import ordering issues."""
        fixes = []
        lines = content.splitlines()
        
        # Simple fix: ensure module-level imports are at the top
        # This is a basic implementation - for production, use isort
        import_lines = []
        other_lines = []
        imports_started = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                if not imports_started:
                    imports_started = True
                import_lines.append(line)
            elif imports_started and stripped and not stripped.startswith('#'):
                # Non-import, non-comment line after imports started
                other_lines.extend(import_lines)
                other_lines.append(line)
                other_lines.extend(lines[i+1:])
                break
            else:
                if imports_started:
                    import_lines.append(line)
                else:
                    other_lines.append(line)
        else:
            other_lines.extend(import_lines)
        
        if import_lines:
            fixes.append("Reorganized imports")
        
        return '\n'.join(other_lines) + '\n', fixes
    
    @staticmethod
    def fix_blank_lines(content: str) -> Tuple[str, List[str]]:
        """Fix blank line issues according to PEP8."""
        fixes = []
        lines = content.splitlines()
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            
            # Add blank line before class definitions (if not already present)
            if (line.strip().startswith('class ') and 
                i > 0 and 
                lines[i-1].strip() and 
                not lines[i-1].strip().startswith(('@', 'class ', 'def '))):
                fixed_lines.insert(-1, '')
                fixes.append(f"Line {i+1}: Added blank line before class definition")
        
        return '\n'.join(fixed_lines) + '\n', fixes


class DocstringStandardizer:
    """Standardizes docstrings according to PEP257."""
    
    @staticmethod
    def extract_docstring_info(node) -> Optional[Dict]:
        """Extract docstring information from AST node."""
        if (isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and
            node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            return {
                'content': node.body[0].value.value,
                'lineno': node.body[0].lineno,
                'type': type(node).__name__
            }
        return None
    
    @staticmethod
    def standardize_docstring(docstring: str, element_type: str) -> str:
        """Standardize a docstring according to PEP257."""
        if not docstring:
            return docstring
            
        lines = docstring.split('\n')
        
        # Remove leading/trailing empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        if not lines:
            return docstring
        
        # Ensure first line ends with period
        if lines[0].strip() and not lines[0].strip().endswith('.'):
            lines[0] = lines[0].strip() + '.'
        
        # For multi-line docstrings, ensure blank line after summary
        if len(lines) > 1 and lines[1].strip():
            lines.insert(1, '')
        
        return '\n'.join(lines)
    
    @staticmethod
    def check_docstring_compliance(file_path: str) -> List[str]:
        """Check docstring compliance with PEP257."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if not DocstringStandardizer.extract_docstring_info(node):
                        issues.append(f"Missing docstring for {type(node).__name__.lower()} '{node.name}' at line {node.lineno}")
                    
        except Exception as e:
            issues.append(f"Error parsing file: {str(e)}")
        
        return issues


class CodeQualityAutomation:
    """Main automation system for code quality improvement."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.syntax_validator = SyntaxValidator()
        self.style_corrector = StyleCorrector()
        self.docstring_standardizer = DocstringStandardizer()
        
    def find_python_files(self, exclude_patterns: Optional[List[str]] = None) -> List[Path]:
        """Find all Python files in the repository."""
        if exclude_patterns is None:
            exclude_patterns = [
                '.git', '__pycache__', '.pytest_cache', '.venv', 'venv',
                'env', '.env', 'node_modules', 'dist', 'build'
            ]
        
        python_files = []
        for file_path in self.root_path.rglob("*.py"):
            # Skip excluded directories
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue
            python_files.append(file_path)
        
        return python_files
    
    def analyze_file(self, file_path: Path) -> CodeQualityResult:
        """Analyze a single Python file for quality issues."""
        str_path = str(file_path)
        
        # Check syntax
        syntax_errors = self.syntax_validator.check_syntax(str_path)
        
        # Check style issues using subprocess for flake8
        style_issues = []
        try:
            result = subprocess.run(
                ['flake8', '--max-line-length=120', '--select=E,W', str_path],
                capture_output=True, text=True, timeout=30
            )
            if result.stdout:
                style_issues = result.stdout.strip().split('\n')
        except Exception as e:
            style_issues.append(f"Style check error: {str(e)}")
        
        # Check docstring issues
        docstring_issues = self.docstring_standardizer.check_docstring_compliance(str_path)
        
        # Determine status
        if syntax_errors:
            status = 'error'
        elif style_issues or docstring_issues:
            status = 'warning'
        else:
            status = 'success'
        
        return CodeQualityResult(
            file_path=str_path,
            syntax_errors=syntax_errors,
            style_issues=style_issues,
            docstring_issues=docstring_issues,
            fixed_issues=[],
            status=status
        )
    
    def fix_file(self, file_path: Path, fix_style: bool = True, fix_docstrings: bool = True) -> CodeQualityResult:
        """Fix issues in a single Python file."""
        str_path = str(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            fixed_issues = []
            
            if fix_style:
                # Fix whitespace issues
                content, whitespace_fixes = self.style_corrector.fix_whitespace_issues(content)
                fixed_issues.extend(whitespace_fixes)
                
                # Fix blank line issues
                content, blank_line_fixes = self.style_corrector.fix_blank_lines(content)
                fixed_issues.extend(blank_line_fixes)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Re-analyze to get current status
            result = self.analyze_file(file_path)
            result.fixed_issues = fixed_issues
            
            return result
            
        except Exception as e:
            return CodeQualityResult(
                file_path=str_path,
                syntax_errors=[f"Fix error: {str(e)}"],
                style_issues=[],
                docstring_issues=[],
                fixed_issues=[],
                status='error'
            )
    
    def run_comprehensive_audit(self, max_workers: int = None) -> Dict[str, List[CodeQualityResult]]:
        """Run comprehensive audit of all Python files."""
        if max_workers is None:
            max_workers = min(32, multiprocessing.cpu_count() * 2)
        
        python_files = self.find_python_files()
        logger.info(f"Found {len(python_files)} Python files to analyze")
        
        results = {
            'success': [],
            'warning': [],
            'error': []
        }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.analyze_file, file_path) for file_path in python_files]
            
            for i, future in enumerate(futures):
                try:
                    result = future.result(timeout=60)
                    results[result.status].append(result)
                    
                    if (i + 1) % 100 == 0:
                        logger.info(f"Analyzed {i + 1}/{len(python_files)} files")
                        
                except Exception as e:
                    logger.error(f"Error analyzing file: {str(e)}")
        
        return results
    
    def generate_report(self, results: Dict[str, List[CodeQualityResult]]) -> str:
        """Generate a comprehensive quality report."""
        total_files = sum(len(file_list) for file_list in results.values())
        
        report = [
            "# Ainflue Platform - Code Quality Audit Report",
            "=" * 50,
            "",
            f"**Total Files Analyzed**: {total_files}",
            f"**Files with No Issues**: {len(results['success'])}",
            f"**Files with Warnings**: {len(results['warning'])}",
            f"**Files with Errors**: {len(results['error'])}",
            "",
            "## Summary Statistics",
            f"- Success Rate: {len(results['success'])/total_files*100:.1f}%",
            f"- Warning Rate: {len(results['warning'])/total_files*100:.1f}%",
            f"- Error Rate: {len(results['error'])/total_files*100:.1f}%",
            "",
        ]
        
        if results['error']:
            report.extend([
                "## Files with Errors",
                "```"
            ])
            for result in results['error'][:10]:  # Show first 10 errors
                report.append(f"{result.file_path}")
                for error in result.syntax_errors:
                    report.append(f"  - {error}")
            if len(results['error']) > 10:
                report.append(f"... and {len(results['error']) - 10} more files with errors")
            report.append("```")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main entry point for the code quality automation system."""
    parser = argparse.ArgumentParser(description="Ainflue Code Quality Automation")
    parser.add_argument("--audit", action="store_true", help="Run comprehensive audit")
    parser.add_argument("--fix", action="store_true", help="Fix common issues")
    parser.add_argument("--path", default=".", help="Path to analyze (default: current directory)")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--workers", type=int, help="Number of worker threads")
    
    args = parser.parse_args()
    
    automation = CodeQualityAutomation(args.path)
    
    if args.audit:
        logger.info("Starting comprehensive code quality audit...")
        results = automation.run_comprehensive_audit(max_workers=args.workers)
        
        report = automation.generate_report(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to {args.output}")
        else:
            print(report)
    
    elif args.fix:
        logger.info("Starting automated fixes...")
        python_files = automation.find_python_files()
        
        fixed_count = 0
        for file_path in python_files[:100]:  # Start with first 100 files
            result = automation.fix_file(file_path)
            if result.fixed_issues:
                fixed_count += 1
                logger.info(f"Fixed {len(result.fixed_issues)} issues in {file_path}")
        
        logger.info(f"Fixed issues in {fixed_count} files")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()