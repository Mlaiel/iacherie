#!/usr/bin/env python3
"""
Comprehensive Syntax Error Correction Script for Ainflue Platform
================================================================

This script performs systematic correction of Python syntax errors across
the entire codebase, focusing on:
- Syntax errors (missing newlines, incorrect indentation)
- PEP257 docstring compliance
- Common regex escape sequence issues
- Import statement validation

Part of the industrial infrastructure for automated code quality.
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import subprocess
import tempfile
import shutil


@dataclass
class SyntaxIssue:
    """Represents a syntax issue found in a file."""
    file_path: str
    line_number: int
    issue_type: str
    description: str
    auto_fixable: bool
    original_content: str = ""
    suggested_fix: str = ""


class ComprehensiveSyntaxFixer:
    """
    Industrial-grade syntax error correction system.
    
    Performs comprehensive audit and automatic correction of Python
    syntax errors across the entire Ainflue codebase.
    """
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.issues_found: List[SyntaxIssue] = []
        self.files_processed = 0
        self.files_fixed = 0
        self.backup_dir = None
        
        # Common problematic patterns and their fixes
        self.regex_fixes = [
            (r'\\\.', r'\.'),  # Fix invalid escape sequence \. 
            (r'\\s', r'\\\\s'),  # Fix invalid escape sequence \s
            (r'\\`', r'\\\\`'),  # Fix invalid escape sequence \`
            (r'\\d', r'\\\\d'),  # Fix invalid escape sequence \d if not properly escaped
            (r'\\w', r'\\\\w'),  # Fix invalid escape sequence \w if not properly escaped
        ]
        
        # Initialize backup directory
        self._setup_backup_directory()
    
    def _setup_backup_directory(self):
        """Setup backup directory for original files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.root_path / f"backups/syntax_fixes_{timestamp}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"🗂️  Backup directory created: {self.backup_dir}")
    
    def audit_all_files(self) -> Dict[str, int]:
        """
        Perform comprehensive audit of all Python files.
        
        Returns:
            Dict with audit statistics
        """
        print("🔍 Starting comprehensive syntax audit...")
        
        stats = {
            'total_files': 0,
            'syntax_errors': 0,
            'docstring_issues': 0,
            'regex_warnings': 0,
            'auto_fixable': 0
        }
        
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            stats['total_files'] += 1
            self.files_processed += 1
            
            # Check syntax errors
            syntax_valid, syntax_error = self._check_syntax(py_file)
            if not syntax_valid:
                stats['syntax_errors'] += 1
                issue = self._analyze_syntax_error(py_file, syntax_error)
                if issue:
                    self.issues_found.append(issue)
                    if issue.auto_fixable:
                        stats['auto_fixable'] += 1
            
            # Check docstring compliance
            docstring_issues = self._check_docstring_compliance(py_file)
            stats['docstring_issues'] += len(docstring_issues)
            self.issues_found.extend(docstring_issues)
            
            # Check regex patterns
            regex_issues = self._check_regex_patterns(py_file)
            stats['regex_warnings'] += len(regex_issues)
            self.issues_found.extend(regex_issues)
            
            if self.files_processed % 100 == 0:
                print(f"📊 Processed {self.files_processed} files...")
        
        return stats
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during processing."""
        skip_patterns = [
            '__pycache__',
            '.pyc',
            'migrations/',
            '.git/',
            'venv/',
            'env/',
            '.env',
            'backup'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _check_syntax(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Check if a Python file has valid syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to validate syntax
            ast.parse(content)
            return True, None
            
        except SyntaxError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error reading file: {e}"
    
    def _analyze_syntax_error(self, file_path: Path, error_msg: str) -> Optional[SyntaxIssue]:
        """Analyze syntax error and determine if it's auto-fixable."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return None
        
        # Extract line number from error message
        line_num = self._extract_line_number(error_msg)
        
        # Common auto-fixable patterns
        if "invalid syntax" in error_msg and line_num:
            if line_num <= len(lines):
                line_content = lines[line_num - 1] if line_num > 0 else ""
                
                # Check for missing newline after docstring
                if '"""' in line_content and not line_content.strip().endswith('"""'):
                    return SyntaxIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        issue_type="missing_newline_after_docstring",
                        description="Missing newline after docstring",
                        auto_fixable=True,
                        original_content=line_content,
                        suggested_fix=self._fix_docstring_newline(line_content)
                    )
        
        # Return non-fixable issue for manual review
        return SyntaxIssue(
            file_path=str(file_path),
            line_number=line_num or 0,
            issue_type="syntax_error",
            description=error_msg,
            auto_fixable=False,
            original_content="",
            suggested_fix=""
        )
    
    def _extract_line_number(self, error_msg: str) -> Optional[int]:
        """Extract line number from syntax error message."""
        import re
        match = re.search(r'line (\d+)', error_msg)
        return int(match.group(1)) if match else None
    
    def _fix_docstring_newline(self, line_content: str) -> str:
        """Fix missing newline after docstring."""
        # Find the position where docstring ends and code begins
        if '"""' in line_content:
            parts = line_content.split('"""')
            if len(parts) >= 3:
                # Triple quote, content, triple quote, then code on same line
                docstring_part = '"""'.join(parts[:2]) + '"""'
                code_part = '"""'.join(parts[2:]).strip()
                if code_part:
                    return docstring_part + '\n        ' + code_part
        return line_content
    
    def _check_docstring_compliance(self, file_path: Path) -> List[SyntaxIssue]:
        """Check PEP257 docstring compliance."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use pydocstyle to check compliance
            result = subprocess.run(
                ['pydocstyle', str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0 and result.stdout:
                for line in result.stdout.split('\n'):
                    if ':' in line and ('D' in line):  # pydocstyle error format
                        parts = line.split(':')
                        if len(parts) >= 3:
                            try:
                                line_num = int(parts[1])
                                description = ':'.join(parts[2:]).strip()
                                
                                issues.append(SyntaxIssue(
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    issue_type="docstring_pep257",
                                    description=description,
                                    auto_fixable=False,  # PEP257 fixes need manual review
                                    original_content="",
                                    suggested_fix=""
                                ))
                            except ValueError:
                                continue
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # pydocstyle not available or timeout
            pass
        except Exception:
            pass
        
        return issues
    
    def _check_regex_patterns(self, file_path: Path) -> List[SyntaxIssue]:
        """Check for invalid regex escape sequences."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Check for invalid escape sequences in strings
                if any(pattern in line for pattern in [r'\.', r'\s', r'\`', r'\d', r'\w']):
                    # Only flag if it's in a string and not properly escaped
                    if ('"' in line or "'" in line) and not r'\\' in line:
                        issues.append(SyntaxIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            issue_type="invalid_escape_sequence",
                            description="Potential invalid escape sequence in regex pattern",
                            auto_fixable=True,
                            original_content=line.strip(),
                            suggested_fix="Use raw string (r'') or double escape (\\\\)"
                        ))
        
        except Exception:
            pass
        
        return issues
    
    def apply_automatic_fixes(self) -> Dict[str, int]:
        """Apply automatic fixes to all auto-fixable issues."""
        print("🔧 Applying automatic fixes...")
        
        stats = {
            'files_fixed': 0,
            'issues_fixed': 0,
            'backup_created': 0
        }
        
        # Group issues by file
        files_to_fix = {}
        for issue in self.issues_found:
            if issue.auto_fixable:
                if issue.file_path not in files_to_fix:
                    files_to_fix[issue.file_path] = []
                files_to_fix[issue.file_path].append(issue)
        
        for file_path, file_issues in files_to_fix.items():
            if self._apply_file_fixes(file_path, file_issues):
                stats['files_fixed'] += 1
                stats['issues_fixed'] += len(file_issues)
                stats['backup_created'] += 1
        
        self.files_fixed = stats['files_fixed']
        return stats
    
    def _apply_file_fixes(self, file_path: str, issues: List[SyntaxIssue]) -> bool:
        """Apply fixes to a specific file."""
        try:
            # Create backup
            backup_path = self.backup_dir / Path(file_path).name
            backup_counter = 1
            while backup_path.exists():
                backup_path = self.backup_dir / f"{Path(file_path).stem}_{backup_counter}{Path(file_path).suffix}"
                backup_counter += 1
            
            shutil.copy2(file_path, backup_path)
            
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Apply fixes (in reverse line order to maintain line numbers)
            issues_sorted = sorted(issues, key=lambda x: x.line_number, reverse=True)
            
            for issue in issues_sorted:
                if issue.issue_type == "missing_newline_after_docstring":
                    if issue.line_number <= len(lines):
                        lines[issue.line_number - 1] = issue.suggested_fix
                
                elif issue.issue_type == "invalid_escape_sequence":
                    if issue.line_number <= len(lines):
                        # Apply regex fixes
                        line = lines[issue.line_number - 1]
                        for pattern, replacement in self.regex_fixes:
                            if pattern in line:
                                # Only apply if it's in a string context
                                if '"' in line or "'" in line:
                                    line = re.sub(pattern, replacement, line)
                        lines[issue.line_number - 1] = line
            
            # Write fixed content
            fixed_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            # Verify the fix didn't break syntax
            try:
                ast.parse(fixed_content)
                print(f"✅ Fixed: {file_path}")
                return True
            except SyntaxError:
                # Restore from backup if fix broke syntax
                shutil.copy2(backup_path, file_path)
                print(f"❌ Fix failed, restored: {file_path}")
                return False
        
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
            return False
    
    def generate_validation_script(self):
        """Generate CI/CD validation script."""
        script_content = """#!/usr/bin/env python3
'''
Automated syntax validation for CI/CD pipeline
==============================================

This script validates Python syntax across the entire codebase
and fails the build if syntax errors are found.
'''

import ast
import sys
from pathlib import Path

def validate_syntax():
    errors = 0
    total = 0
    
    for py_file in Path('.').rglob('*.py'):
        if '__pycache__' in str(py_file) or '.git' in str(py_file):
            continue
            
        total += 1
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
        except SyntaxError as e:
            print(f"SYNTAX ERROR: {py_file}:{e.lineno} - {e.msg}")
            errors += 1
        except Exception as e:
            print(f"ERROR: {py_file} - {e}")
            errors += 1
    
    print(f"\\nValidation complete: {total} files checked")
    if errors == 0:
        print("✅ All files have valid syntax")
        return 0
    else:
        print(f"❌ {errors} files have syntax errors")
        return 1

if __name__ == '__main__':
    sys.exit(validate_syntax())
"""
        
        script_path = self.root_path / "scripts/validation/ci_syntax_validator.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make executable
        script_path.chmod(0o755)
        print(f"📝 Created CI/CD validation script: {script_path}")
    
    def generate_report(self, stats: Dict[str, int]) -> str:
        """Generate comprehensive audit report."""
        report = f"""
🏭 INDUSTRIAL INFRASTRUCTURE - SYNTAX AUDIT REPORT
==================================================

📊 AUDIT STATISTICS:
   Total Python Files: {stats.get('total_files', 0):,}
   Files Processed: {self.files_processed:,}
   Files Fixed: {self.files_fixed:,}
   
🔍 ISSUES DETECTED:
   Syntax Errors: {stats.get('syntax_errors', 0):,}
   Docstring Issues: {stats.get('docstring_issues', 0):,}
   Regex Warnings: {stats.get('regex_warnings', 0):,}
   Auto-fixable Issues: {stats.get('auto_fixable', 0):,}

💾 BACKUP INFORMATION:
   Backup Directory: {self.backup_dir}
   Backups Created: {stats.get('backup_created', 0):,}

🎯 NEXT STEPS:
   1. Review remaining manual fix issues
   2. Run comprehensive tests
   3. Update CI/CD pipeline with validation
   4. Document coding standards

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Ainflue Platform - Industrial Quality Standards
        """
        
        return report.strip()
    
    def run_comprehensive_audit(self) -> int:
        """Run complete syntax audit and correction process."""
        print("🏭 AINFLUE INDUSTRIAL INFRASTRUCTURE")
        print("=" * 50)
        print("🔍 Comprehensive Syntax Error Correction")
        print()
        
        try:
            # Step 1: Audit all files
            stats = self.audit_all_files()
            
            # Step 2: Apply automatic fixes
            fix_stats = self.apply_automatic_fixes()
            stats.update(fix_stats)
            
            # Step 3: Generate CI/CD validation
            self.generate_validation_script()
            
            # Step 4: Generate report
            report = self.generate_report(stats)
            print(report)
            
            # Save detailed report
            report_path = self.root_path / f"syntax_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n📄 Detailed report saved: {report_path}")
            
            # Return success if major issues are resolved
            remaining_syntax_errors = stats.get('syntax_errors', 0) - stats.get('issues_fixed', 0)
            return 0 if remaining_syntax_errors < 50 else 1
            
        except Exception as e:
            print(f"❌ Critical error during audit: {e}")
            return 1


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = "."
    
    fixer = ComprehensiveSyntaxFixer(root_path)
    return fixer.run_comprehensive_audit()


if __name__ == "__main__":
    sys.exit(main())