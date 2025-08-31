#!/usr/bin/env python3
"""Universal Python syntax error fixer

Automatically fixes common syntax errors in Python files:
1. Missing newlines after docstrings
2. Missing closing quotes in docstrings  
3. Invalid characters in docstrings
4. Common spacing issues
"""

import ast
import sys
import re
from pathlib import Path
from typing import List, Tuple
import logging

class UniversalSyntaxFixer:
    """Universal fixer for common Python syntax errors"""
    
    def __init__(self):
        self.fixed_files = []
        self.failed_files = []
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def fix_file_syntax(self, file_path: Path) -> bool:
        """Fix syntax errors in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: Replace problematic unicode characters
            content = content.replace('©', '(c)')
            content = content.replace('®', '(R)')
            content = content.replace('™', '(TM)')
            
            # Fix 2: Add newlines after docstrings that are immediately followed by code
            # Pattern: """docstring"""    code -> """docstring"""\n    code
            content = re.sub(
                r'("""[^"]*?""")(\s+)([A-Z_][A-Z0-9_]*\s*=)',
                r'\1\n    \3',
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            
            # Fix 3: Add newlines after single-line docstrings in functions/methods
            content = re.sub(
                r'("""[^"]*?""")([a-zA-Z_])',
                r'\1\n        \2',
                content
            )
            
            # Fix 4: Fix docstrings that end with content instead of quotes
            # Look for lines that start with """ but don't end properly
            lines = content.split('\n')
            for i, line in enumerate(lines):
                stripped = line.strip()
                # If line starts with """ but doesn't end with """ and has content after
                if stripped.startswith('"""') and not stripped.endswith('"""') and len(stripped) > 3:
                    # Check if it contains closing quotes
                    if '"""' in stripped[3:]:
                        # Find the position of the closing quotes
                        closing_pos = stripped.find('"""', 3)
                        if closing_pos > 0:
                            # Split at the closing quotes
                            before = stripped[:closing_pos + 3]
                            after = stripped[closing_pos + 3:].strip()
                            if after:
                                # Reconstruct the line with proper spacing
                                indent = line[:len(line) - len(line.lstrip())]
                                lines[i] = indent + before
                                if after:
                                    lines.insert(i + 1, indent + after)
                        
            content = '\n'.join(lines)
            
            # Fix 5: Ensure proper spacing around imports
            content = re.sub(r'"""\nimport', '"""\n\nimport', content)
            content = re.sub(r'"""import', '"""\nimport', content)
            
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
                    
                    self.logger.info(f"✅ Fixed syntax in {file_path}")
                    self.fixed_files.append(str(file_path))
                    return True
                    
                except SyntaxError as e:
                    self.logger.warning(f"⚠️  Fix attempt failed for {file_path}: {e}")
                    return False
            else:
                # Try to parse original content to see if it already works
                try:
                    ast.parse(content)
                    self.logger.info(f"✅ {file_path} already has valid syntax")
                    return True
                except SyntaxError:
                    self.logger.warning(f"⚠️  No fixes applied to {file_path}, still has syntax errors")
                    return False
            
        except Exception as e:
            self.logger.error(f"❌ Error processing {file_path}: {e}")
            self.failed_files.append(str(file_path))
            return False
    
    def fix_multiple_files(self, file_paths: List[Path]) -> Tuple[int, int]:
        """Fix syntax errors in multiple files"""
        fixed_count = 0
        for file_path in file_paths:
            if self.fix_file_syntax(file_path):
                fixed_count += 1
        
        return fixed_count, len(file_paths)
    
    def print_summary(self, fixed_count: int, total_count: int):
        """Print summary of fixes applied"""
        print("\n" + "=" * 60)
        print("🔧 UNIVERSAL SYNTAX FIX SUMMARY")
        print("=" * 60)
        print(f"📊 Files processed: {total_count}")
        print(f"✅ Files successfully fixed: {fixed_count}")
        print(f"❌ Files that failed to fix: {len(self.failed_files)}")
        
        if self.fixed_files:
            print(f"\n✅ Successfully fixed files:")
            for file_path in self.fixed_files:
                print(f"   • {file_path}")
        
        if self.failed_files:
            print(f"\n❌ Failed to fix:")
            for file_path in self.failed_files:
                print(f"   • {file_path}")
        
        print("=" * 60)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix Python syntax errors")
    parser.add_argument("files", nargs="*", help="Files to fix")
    parser.add_argument("--all", action="store_true", help="Fix all Python files with syntax errors")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    
    args = parser.parse_args()
    
    fixer = UniversalSyntaxFixer()
    
    if args.files:
        # Fix specific files
        file_paths = [Path(f) for f in args.files]
        fixed_count, total_count = fixer.fix_multiple_files(file_paths)
        fixer.print_summary(fixed_count, total_count)
        return 0 if fixed_count == total_count else 1
    
    elif args.all:
        # Find and fix all files with syntax errors
        root_path = Path(args.root)
        problematic_files = []
        
        for py_file in root_path.rglob("*.py"):
            if any(skip in py_file.parts for skip in ['.git', '__pycache__', 'venv', '.venv']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except:
                problematic_files.append(py_file)
        
        print(f"Found {len(problematic_files)} files with syntax errors")
        fixed_count, total_count = fixer.fix_multiple_files(problematic_files)
        fixer.print_summary(fixed_count, total_count)
        return 0 if fixed_count > 0 else 1
    
    else:
        print("Please specify files to fix or use --all flag")
        return 1


if __name__ == "__main__":
    sys.exit(main())