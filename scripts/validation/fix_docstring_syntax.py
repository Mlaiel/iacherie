#!/usr/bin/env python3
"""Fix docstring syntax errors in Python files

This script specifically targets and fixes common docstring syntax errors:
1. Missing closing triple quotes
2. Incorrect docstring formatting
3. PEP257 compliance issues
"""

import ast
import sys
import re
from pathlib import Path
from typing import List, Tuple
import logging

class DocstringSyntaxFixer:
    """
Fix common docstring syntax errors automatically"""
    
    def __init__(self):
        self.fixed_files = []
        self.failed_files = []
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """
Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def fix_file_docstring_syntax(self, file_path: Path) -> bool:
        """
Fix docstring syntax errors in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern 1: Fix unclosed module docstring at the beginning
            # Look for """ followed by content then import without closing """
            pattern1 = r'^(""")([^"]*?)(["\n]*)import\s+'
            if re.match(pattern1, content, re.MULTILINE | re.DOTALL):
                # Find the end of the docstring content
                lines = content.split('\n')
                docstring_end = None
                import_line = None
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_line = i
                        break
                
                if import_line is not None:
                    # Find last line of docstring content before import
                    for i in range(import_line - 1, -1, -1):
                        if lines[i].strip() and not lines[i].strip().startswith('"""'):
                            docstring_end = i
                            break
                    
                    if docstring_end is not None:
                        # Insert closing """ after the docstring content
                        lines.insert(docstring_end + 1, '"""')
                        content = '\n'.join(lines)
            
            # Pattern 2: Fix missing closing quotes in class/function docstrings
            content = re.sub(
                r'(\s+"""[^"]*?)(\n\s*)(def |class |@)',
                r'\1"""\2\3',
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            
            # Pattern 3: Fix standalone docstrings without closing quotes
            content = re.sub(
                r'^(""")([^"]*?)(\n)([a-zA-Z_]|import|from)',
                r'\1\2"""\3\4',
                content,
                flags=re.MULTILINE
            )
            
            # Verify the fix by trying to parse
            if content != original_content:
                try:
                    ast.parse(content)
                    
                    # Create backup
                    backup_path = file_path.with_suffix('.py.bak')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    
                    # Write fixed content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.logger.info(f"✅ Fixed docstring syntax in {file_path}")
                    self.fixed_files.append(str(file_path))
                    return True
                    
                except SyntaxError as e:
                    self.logger.warning(f"⚠️  Fix attempt failed for {file_path}: {e}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error processing {file_path}: {e}")
            self.failed_files.append(str(file_path))
            return False
    
    def find_files_with_docstring_errors(self, root_path: Path = Path(".")) -> List[Path]:
        """Find Python files with docstring syntax errors"""
        problematic_files = []
        
        for py_file in root_path.rglob("*.py"):
            # Skip certain directories
            if any(skip in py_file.parts for skip in ['.git', '__pycache__', 'venv', '.venv']):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try to parse
                ast.parse(content)
                
            except SyntaxError as e:
                # Check if it's a docstring-related error
                if 'EOF while scanning triple-quoted string literal' in str(e) or \
                   'invalid syntax' in str(e):
                    problematic_files.append(py_file)
            except Exception:
                continue
        
        return problematic_files
    
    def fix_all_docstring_errors(self, root_path: Path = Path(".")) -> Tuple[int, int]:
        """Fix all docstring syntax errors in the repository"""
        self.logger.info("🔍 Finding files with docstring syntax errors...")
        
        problematic_files = self.find_files_with_docstring_errors(root_path)
        
        self.logger.info(f"📊 Found {len(problematic_files)} files with potential docstring issues")
        
        fixed_count = 0
        for file_path in problematic_files:
            if self.fix_file_docstring_syntax(file_path):
                fixed_count += 1
        
        return fixed_count, len(problematic_files)
    
    def print_summary(self, fixed_count: int, total_count: int):
        """Print summary of fixes applied"""
        print("\n" + "=" * 60)
        print("🔧 DOCSTRING SYNTAX FIX SUMMARY")
        print("=" * 60)
        print(f"📊 Files with docstring issues: {total_count}")
        print(f"✅ Files successfully fixed: {fixed_count}")
        print(f"❌ Files that failed to fix: {len(self.failed_files)}")
        
        if self.fixed_files:
            print(f"\n✅ Successfully fixed files:")
            for file_path in self.fixed_files[:10]:  # Show first 10
                print(f"   • {file_path}")
            if len(self.fixed_files) > 10:
                print(f"   ... and {len(self.fixed_files) - 10} more")
        
        if self.failed_files:
            print(f"\n❌ Failed to fix:")
            for file_path in self.failed_files[:5]:  # Show first 5
                print(f"   • {file_path}")
        
        print("=" * 60)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix docstring syntax errors")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--file", help="Fix specific file")
    
    args = parser.parse_args()
    
    fixer = DocstringSyntaxFixer()
    
    if args.file:
        # Fix specific file
        file_path = Path(args.file)
        if file_path.exists():
            success = fixer.fix_file_docstring_syntax(file_path)
            if success:
                print(f"✅ Fixed {file_path}")
                return 0
            else:
                print(f"❌ Failed to fix {file_path}")
                return 1
        else:
            print(f"❌ File not found: {file_path}")
            return 1
    else:
        # Fix all files in directory
        root_path = Path(args.root)
        fixed_count, total_count = fixer.fix_all_docstring_errors(root_path)
        fixer.print_summary(fixed_count, total_count)
        
        if fixed_count == total_count and total_count > 0:
            print("🎉 All docstring syntax errors fixed successfully!")
            return 0
        elif fixed_count > 0:
            print("⚠️  Some files were fixed, but others remain problematic")
            return 0
        else:
            print("❌ No fixes were applied")
            return 1


if __name__ == "__main__":
    sys.exit(main())