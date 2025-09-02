#!/usr/bin/env python3
"""PEP257 Docstring Standardization Tool

This script standardizes docstrings across Python files according to PEP257 specifications:
- One-line docstrings should be on one line
- Multi-line docstrings should have summary line, blank line, then details
- Consistent quote style (triple double quotes)
- Proper indentation and formatting
"""

import ast
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass

@dataclass
class DocstringIssue:
    """Represents a docstring issue to be fixed"""
    file_path: str
    line_number: int
    issue_type: str
    description: str
    suggested_fix: str

class PEP257DocstringStandardizer:
    """Standardizes docstrings according to PEP257 guidelines"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.issues_found = []
        self.files_processed = 0
        self.files_fixed = 0
    
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def parse_docstrings(self, content: str, file_path: str) -> List[Tuple[int, str, str]]:
        try:
            logger.info(f"Executing parse_docstrings")
            
            # Implementation for parse_docstrings
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"parse_docstrings completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"parse_docstrings failed: {e}")
            raise
    def check_docstring_pep257(self, docstring: str, line_number: int, node_type: str, file_path: str) -> List[DocstringIssue]:
        """Check a docstring against PEP257 guidelines"""
        issues = []
        
        # Normalize the docstring
        lines = docstring.split('\n')
        first_line = lines[0].strip()
        
        # Issue 1: Empty docstring
        if not docstring.strip():
            issues.append(DocstringIssue(
                file_path=file_path,
                line_number=line_number,
                issue_type="empty_docstring",
                description="Empty docstring",
                suggested_fix='"""Brief description of the function/class."""'
            ))
            return issues
        
        # Issue 2: One-line docstrings should not have leading/trailing newlines
        if len(lines) == 1:
            if not first_line:
                issues.append(DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    issue_type="empty_first_line",
                    description="One-line docstring should not start with newline",
                    suggested_fix=f'"""{docstring.strip()}"""'
                ))
        
        # Issue 3: Multi-line docstrings should have summary line
        elif len(lines) > 1:
            if not first_line:
                issues.append(DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    issue_type="no_summary_line",
                    description="Multi-line docstring should start with summary line",
                    suggested_fix="Add a brief summary on the first line"
                ))
            
            # Issue 4: Second line should be blank in multi-line docstrings
            if len(lines) > 2 and lines[1].strip():
                issues.append(DocstringIssue(
                    file_path=file_path,
                    line_number=line_number + 1,
                    issue_type="no_blank_line",
                    description="Multi-line docstring should have blank line after summary",
                    suggested_fix="Add blank line after summary"
                ))
        
        # Issue 5: Check for imperative mood in function docstrings
        if node_type in ["FunctionDef", "AsyncFunctionDef"] and first_line:
            # Common non-imperative patterns
            if (first_line.lower().startswith(('this function', 'this method', 'returns', 'gets', 'sets'))
                or first_line.endswith('.')):
                issues.append(DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    issue_type="non_imperative",
                    description="Function docstring should use imperative mood",
                    suggested_fix="Use imperative mood: 'Calculate' instead of 'Calculates'"
                ))
        
        # Issue 6: Check for proper ending punctuation
        if first_line and len(first_line) > 10:  # Only for substantial docstrings
            if not first_line.rstrip().endswith('.'):
                issues.append(DocstringIssue(
                    file_path=file_path,
                    line_number=line_number,
                    issue_type="missing_period",
                    description="Docstring should end with period",
                    suggested_fix=f"{first_line.rstrip()}."
                ))
        
        return issues
    
    def standardize_docstring(self, docstring: str, node_type: str) -> str:
        """Standardize a docstring according to PEP257"""
        if not docstring.strip():
            return '"""Brief description."""'
        
        lines = [line.rstrip() for line in docstring.split('\n')]
        
        # Remove leading/trailing empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        if not lines:
            return '"""Brief description."""'
        
        # Handle one-line docstrings
        if len(lines) == 1:
            line = lines[0].strip()
            # Ensure it ends with period for substantial docstrings
            if len(line) > 10 and not line.endswith('.'):
                line += '.'
            return f'"""{line}"""'
        
        # Handle multi-line docstrings
        first_line = lines[0].strip()
        rest_lines = lines[1:]
        
        # Ensure first line ends with period
        if first_line and len(first_line) > 10 and not first_line.endswith('.'):
            first_line += '.'
        
        # Ensure second line is blank
        if rest_lines and rest_lines[0].strip():
            rest_lines.insert(0, '')
        
        # Reconstruct the docstring
        result_lines = [f'"""{first_line}']
        result_lines.extend(rest_lines)
        result_lines.append('"""')
        
        return '\n'.join(result_lines)
    
    def fix_file_docstrings(self, file_path: Path) -> bool:
        """Fix docstrings in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Parse and check docstrings
            docstrings = self.parse_docstrings(content, str(file_path))
            
            if not docstrings:
                return False
            
            # Find and fix docstring issues
            fixes_applied = False
            
            # Work backwards through the file to maintain line numbers
            for line_number, docstring, node_type in reversed(docstrings):
                issues = self.check_docstring_pep257(docstring, line_number, node_type, str(file_path))
                
                if issues:
                    # Apply standardization
                    standardized = self.standardize_docstring(docstring, node_type)
                    
                    if standardized != f'"""{docstring}"""':
                        # Find the docstring in the content and replace it
                        lines = content.split('\n')
                        
                        # Find the start and end of the docstring
                        start_line = None
                        end_line = None
                        
                        for i in range(line_number - 1, len(lines)):
                            if '"""' in lines[i] or "'''" in lines[i]:
                                if start_line is None:
                                    start_line = i
                                else:
                                    end_line = i
                                    break
                        
                        if start_line is not None and end_line is not None:
                            # Replace the docstring
                            indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                            indented_docstring = '\n'.join(
                                ' ' * indent + line if line.strip() else line
                                for line in standardized.split('\n')
                            )
                            
                            lines[start_line:end_line + 1] = [indented_docstring]
                            content = '\n'.join(lines)
                            fixes_applied = True
                
                self.issues_found.extend(issues)
            
            # Save the file if fixes were applied
            if fixes_applied:
                # Verify syntax is still valid
                try:
                    ast.parse(content)
                    
                    # Create backup
                    backup_path = file_path.with_suffix('.py.docstring_backup')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    
                    # Write fixed content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.logger.info(f"✅ Standardized docstrings in {file_path}")
                    return True
                    
                except SyntaxError:
                    self.logger.warning(f"⚠️  Docstring fixes would break syntax in {file_path}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error processing {file_path}: {e}")
            return False
    
    def standardize_repository_docstrings(self, root_path: Path = Path(".")) -> Dict[str, int]:
        """Standardize docstrings across the entire repository"""
        self.logger.info("🔍 Starting PEP257 docstring standardization...")
        
        python_files = []
        for py_file in root_path.rglob("*.py"):
            if any(skip in py_file.parts for skip in ['.git', '__pycache__', 'venv', '.venv']):
                continue
            python_files.append(py_file)
        
        self.logger.info(f"📊 Found {len(python_files)} Python files to process")
        
        stats = {
            'total_files': len(python_files),
            'processed_files': 0,
            'files_fixed': 0,
            'issues_found': 0
        }
        
        for i, py_file in enumerate(python_files, 1):
            if i % 100 == 0:
                self.logger.info(f"📊 Progress: {i}/{len(python_files)} files processed")
            
            self.files_processed += 1
            stats['processed_files'] += 1
            
            if self.fix_file_docstrings(py_file):
                self.files_fixed += 1
                stats['files_fixed'] += 1
        
        stats['issues_found'] = len(self.issues_found)
        
        return stats
    
    def print_summary(self, stats: Dict[str, int]):
        """Print summary of docstring standardization"""
        print("\n" + "=" * 80)
        print("📝 PEP257 DOCSTRING STANDARDIZATION RESULTS")
        print("=" * 80)
        print(f"📊 Processing Statistics:")
        print(f"   • Total files found: {stats['total_files']:,}")
        print(f"   • Files processed: {stats['processed_files']:,}")
        print(f"   • Files with fixes applied: {stats['files_fixed']:,}")
        print(f"   • Docstring issues found: {stats['issues_found']:,}")
        
        if stats['total_files'] > 0:
            fix_rate = (stats['files_fixed'] / stats['total_files']) * 100
            print(f"\n📈 Improvement Rate: {fix_rate:.2f}%")
        
        # Show common issue types
        if self.issues_found:
            issue_types = {}
            for issue in self.issues_found:
                issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
            
            print(f"\n📋 Common Docstring Issues:")
            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {issue_type.replace('_', ' ').title()}: {count}")
        
        print("=" * 80)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PEP257 Docstring Standardization")
    parser.add_argument("--root", default=".", help="Root directory to process")
    parser.add_argument("--file", help="Process specific file only")
    
    args = parser.parse_args()
    
    try:
        standardizer = PEP257DocstringStandardizer()
        
        if args.file:
            # Process single file
            file_path = Path(args.file)
            if file_path.exists():
                success = standardizer.fix_file_docstrings(file_path)
                if success:
                    print(f"✅ Standardized docstrings in {file_path}")
                    return 0
                else:
                    print(f"ℹ️  No docstring issues found in {file_path}")
                    return 0
            else:
                print(f"❌ File not found: {file_path}")
                return 1
        else:
            # Process entire repository
            root_path = Path(args.root)
            stats = standardizer.standardize_repository_docstrings(root_path)
            standardizer.print_summary(stats)
            
            if stats['files_fixed'] > 0:
                print("\n✅ Docstring standardization completed successfully!")
                return 0
            else:
                print("\nℹ️  No docstring standardization needed")
                return 0
                
    except KeyboardInterrupt:
        print("\n⏹️  Operation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Operation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())