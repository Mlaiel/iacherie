#!/usr/bin/env python3
"""Comprehensive syntax audit and correction for all Python files in the repository

This script performs:
1. Syntax validation for all Python files
2. PEP257 docstring standardization
3. Automated correction of common syntax errors
4. Detailed reporting and logging
"""

import ast
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import re
import os


@dataclass
class SyntaxIssue:
    """
Represents a syntax issue found in a file"""
    file_path: str
    line_number: int
    column: int
    error_type: str
    message: str
    severity: str  # 'error', 'warning', 'info'


@dataclass
class AuditResult:
    """
Results from the comprehensive audit"""
    total_files: int
    checked_files: int
    files_with_errors: int
    files_fixed: int
    syntax_errors: List[SyntaxIssue]
    docstring_issues: List[SyntaxIssue]
    fixed_issues: List[SyntaxIssue]
    skipped_files: List[str]


class ComprehensiveSyntaxAuditor:
    """
Advanced syntax auditor for industrial-scale Python code validation"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.logger = self._setup_logging()
        self.audit_result = AuditResult(
            total_files=0,
            checked_files=0,
            files_with_errors=0,
            files_fixed=0,
            syntax_errors=[],
            docstring_issues=[],
            fixed_issues=[],
            skipped_files=[]
        )
        
        # Common syntax error patterns and their fixes
        self.syntax_fixes = [
            # Missing newlines between docstrings and code
            (r'"""([^"]+)"""([a-zA-Z_])', r'"""\1"""\n\2'),
            (r"'''([^']+)'''([a-zA-Z_])", r"'''\1'''\n\2"),
            
            # Fix missing spaces after colons in function definitions  
            (r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\):([a-zA-Z_])', r'def \1():\n    \2'),
            
            # Fix imports without proper spacing
            (r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)\n([a-zA-Z_])', r'import \1\n\n\2'),
        ]
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the audit process"""
        logger = logging.getLogger("syntax_auditor")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = self.root_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"syntax_audit_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the repository"""
        self.logger.info("🔍 Scanning for Python files...")
        
        # Directories to exclude from scanning
        exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            'venv', '.venv', 'env', '.env', 'dist', 'build',
            '.tox', '.coverage', 'htmlcov'
        }
        
        python_files = []
        
        for py_file in self.root_path.rglob("*.py"):
            # Skip if in excluded directory
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue
            
            # Skip if file is too large (>1MB)
            try:
                if py_file.stat().st_size > 1024 * 1024:
                    self.audit_result.skipped_files.append(str(py_file))
                    continue
            except OSError:
                continue
                
            python_files.append(py_file)
        
        self.audit_result.total_files = len(python_files)
        self.logger.info(f"📊 Found {len(python_files)} Python files")
        return python_files
    
    def check_syntax(self, file_path: Path) -> Tuple[bool, List[SyntaxIssue]]:
        """Check syntax of a Python file"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to check syntax
            ast.parse(content)
            return True, issues
            
        except SyntaxError as e:
            issue = SyntaxIssue(
                file_path=str(file_path),
                line_number=e.lineno or 0,
                column=e.offset or 0,
                error_type="SyntaxError",
                message=str(e.msg),
                severity="error"
            )
            issues.append(issue)
            return False, issues
            
        except UnicodeDecodeError as e:
            issue = SyntaxIssue(
                file_path=str(file_path),
                line_number=0,
                column=0,
                error_type="EncodingError",
                message=f"Cannot decode file: {e}",
                severity="error"
            )
            issues.append(issue)
            return False, issues
            
        except Exception as e:
            issue = SyntaxIssue(
                file_path=str(file_path),
                line_number=0,
                column=0,
                error_type="UnknownError",
                message=f"Unexpected error: {e}",
                severity="error"
            )
            issues.append(issue)
            return False, issues
    
    def check_docstrings_pep257(self, file_path: Path) -> List[SyntaxIssue]:
        """Check docstring compliance with PEP257"""
        issues = []
        
        try:
            # Use pydocstyle to check PEP257 compliance
            result = subprocess.run(
                ['pydocstyle', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line and 'D' in line:
                        # Parse pydocstyle output
                        parts = line.split(':')
                        if len(parts) >= 3:
                            try:
                                line_num = int(parts[1])
                                message = ':'.join(parts[2:]).strip()
                                
                                issue = SyntaxIssue(
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    column=0,
                                    error_type="DocstringError",
                                    message=message,
                                    severity="warning"
                                )
                                issues.append(issue)
                            except ValueError:
                                continue
                                
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout checking docstrings for {file_path}")
        except Exception as e:
            self.logger.debug(f"Error checking docstrings for {file_path}: {e}")
        
        return issues
    
    def attempt_auto_fix(self, file_path: Path) -> bool:
        """Attempt to automatically fix common syntax errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            fixed = False
            
            # Apply automatic fixes
            for pattern, replacement in self.syntax_fixes:
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    content = new_content
                    fixed = True
            
            # If we made changes, verify syntax and save
            if fixed:
                try:
                    ast.parse(content)
                    
                    # Create backup
                    backup_path = file_path.with_suffix('.py.bak')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    
                    # Save fixed content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.logger.info(f"✅ Auto-fixed {file_path}")
                    return True
                    
                except SyntaxError:
                    # If fix introduced new errors, revert
                    self.logger.warning(f"⚠️  Auto-fix failed for {file_path}, reverting")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error auto-fixing {file_path}: {e}")
            return False
    
    def run_comprehensive_audit(self) -> AuditResult:
        """Run comprehensive syntax audit on all Python files"""
        self.logger.info("🚀 Starting comprehensive syntax audit...")
        
        python_files = self.find_python_files()
        
        for i, file_path in enumerate(python_files, 1):
            if i % 100 == 0:
                self.logger.info(f"📊 Progress: {i}/{len(python_files)} files processed")
            
            # Check syntax
            syntax_ok, syntax_issues = self.check_syntax(file_path)
            
            if not syntax_ok:
                self.audit_result.files_with_errors += 1
                self.audit_result.syntax_errors.extend(syntax_issues)
                
                # Attempt auto-fix
                if self.attempt_auto_fix(file_path):
                    self.audit_result.files_fixed += 1
                    self.audit_result.fixed_issues.extend(syntax_issues)
                    
                    # Re-check syntax after fix
                    syntax_ok, _ = self.check_syntax(file_path)
            
            # Check docstrings (only for files with valid syntax)
            if syntax_ok:
                docstring_issues = self.check_docstrings_pep257(file_path)
                self.audit_result.docstring_issues.extend(docstring_issues)
            
            self.audit_result.checked_files += 1
        
        return self.audit_result
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        report = {
            "audit_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": self.audit_result.total_files,
                "checked_files": self.audit_result.checked_files,
                "files_with_errors": self.audit_result.files_with_errors,
                "files_fixed": self.audit_result.files_fixed,
                "syntax_errors_count": len(self.audit_result.syntax_errors),
                "docstring_issues_count": len(self.audit_result.docstring_issues),
                "skipped_files_count": len(self.audit_result.skipped_files)
            },
            "syntax_errors": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "column": issue.column,
                    "type": issue.error_type,
                    "message": issue.message,
                    "severity": issue.severity
                }
                for issue in self.audit_result.syntax_errors
            ],
            "docstring_issues": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "type": issue.error_type,
                    "message": issue.message,
                    "severity": issue.severity
                }
                for issue in self.audit_result.docstring_issues
            ],
            "fixed_issues": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "type": issue.error_type,
                    "message": issue.message,
                    "severity": issue.severity
                }
                for issue in self.audit_result.fixed_issues
            ],
            "skipped_files": self.audit_result.skipped_files
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any]) -> Path:
        """Save audit report to JSON file"""
        reports_dir = self.root_path / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"syntax_audit_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def print_summary(self, report: Dict[str, Any]):
        """Print audit summary to console"""
        summary = report["summary"]
        
        print("\n" + "=" * 80)
        print("🏭 COMPREHENSIVE SYNTAX AUDIT RESULTS")
        print("=" * 80)
        print(f"📊 Files Statistics:")
        print(f"   • Total Python files found: {summary['total_files']:,}")
        print(f"   • Files checked: {summary['checked_files']:,}")
        print(f"   • Files with syntax errors: {summary['files_with_errors']:,}")
        print(f"   • Files automatically fixed: {summary['files_fixed']:,}")
        print(f"   • Files skipped: {summary['skipped_files_count']:,}")
        
        print(f"\n🔍 Issues Found:")
        print(f"   • Syntax errors: {summary['syntax_errors_count']:,}")
        print(f"   • Docstring issues (PEP257): {summary['docstring_issues_count']:,}")
        
        if summary['files_fixed'] > 0:
            print(f"\n✅ Auto-Fixes Applied:")
            print(f"   • {summary['files_fixed']:,} files automatically corrected")
        
        # Show top error types
        if report["syntax_errors"]:
            error_types = {}
            for error in report["syntax_errors"]:
                error_type = error["type"]
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            print(f"\n🚨 Top Syntax Error Types:")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   • {error_type}: {count}")
        
        # Calculate success rate
        if summary['checked_files'] > 0:
            success_rate = ((summary['checked_files'] - summary['files_with_errors']) / summary['checked_files']) * 100
            print(f"\n📈 Syntax Validation Success Rate: {success_rate:.2f}%")
        
        print("=" * 80)


def main():
    """Main function to run comprehensive syntax audit"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Python syntax audit and correction")
    parser.add_argument("--root", default=".", help="Root directory to scan (default: current directory)")
    parser.add_argument("--fix", action="store_true", help="Attempt to auto-fix syntax errors")
    parser.add_argument("--report-only", action="store_true", help="Generate report only, no fixes")
    
    args = parser.parse_args()
    
    try:
        auditor = ComprehensiveSyntaxAuditor(args.root)
        
        # Run audit
        result = auditor.run_comprehensive_audit()
        
        # Generate and save report
        report = auditor.generate_report()
        report_file = auditor.save_report(report)
        
        # Print summary
        auditor.print_summary(report)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Return appropriate exit code
        if result.files_with_errors > 0 and result.files_fixed < result.files_with_errors:
            print("\n⚠️  Some syntax errors remain unresolved")
            return 1
        else:
            print("\n🎉 Syntax audit completed successfully!")
            return 0
            
    except KeyboardInterrupt:
        print("\n⏹️  Audit interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())