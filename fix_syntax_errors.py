#!/usr/bin/env python3
"""Syntax Error Fixer for Ainflue Platform
Systematically fixes common syntax errors caused by incomplete implementations.
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple

class SyntaxErrorFixer:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.fixed_files = []
        self.errors_found = 0
        self.errors_fixed = 0
        
    def fix_all_syntax_errors(self) -> Dict[str, int]:
        """Fix all syntax errors in Python files"""
        results = {"files_scanned": 0, "files_fixed": 0, "errors_fixed": 0}
        
        # Find all Python files
        python_files = list(self.root_dir.rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            results["files_scanned"] += 1
            
            try:
                if self._fix_file_syntax_errors(file_path):
                    results["files_fixed"] += 1
                    self.fixed_files.append(str(file_path))
                    
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
        
        results["errors_fixed"] = self.errors_fixed
        return results
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Skip certain directories and files"""
        skip_dirs = {".git", "__pycache__", ".pytest_cache", "venv", "env", "node_modules"}
        
        for part in file_path.parts:
            if part in skip_dirs:
                return True
        
        return False
    
    def _fix_file_syntax_errors(self, file_path: Path) -> bool:
        """Fix syntax errors in a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return False
        
        original_content = content
        
        # Fix common patterns
        content = self._fix_incomplete_try_blocks(content)
        content = self._fix_incomplete_for_loops(content)
        content = self._fix_incomplete_while_loops(content)
        content = self._fix_incomplete_if_blocks(content)
        content = self._fix_incomplete_method_definitions(content)
        content = self._fix_incomplete_class_definitions(content)
        
        # Check if anything was changed
        if content != original_content:
            try:
                # Verify the syntax is now valid
                ast.parse(content)
                
                # Write back the fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fixed syntax errors in {file_path}")
                return True
                
            except SyntaxError as e:
                print(f"⚠️  Could not fully fix {file_path}: {e}")
                return False
        
        return False
    
    def _fix_incomplete_try_blocks(self, content: str) -> str:
        """Fix incomplete try blocks"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)
            
            # Look for try blocks that are not properly closed
            if re.match(r'\s*try:\s*$', line):
                # Check if the next lines have proper try content
                j = i + 1
                has_except = False
                has_content = False
                
                while j < len(lines):
                    next_line = lines[j]
                    if re.match(r'\s*(except|finally):', next_line):
                        has_except = True
                        break
                    elif re.match(r'\s*\S', next_line) and not re.match(r'\s*#', next_line):
                        has_content = True
                    elif re.match(r'^\s*(def|class|if|for|while|try)', next_line):
                        break
                    j += 1
                
                # If no except block found, add a minimal implementation
                if not has_except and not has_content:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * (indent + 4) + 'pass')
                    fixed_lines.append(' ' * indent + 'except Exception as e:')
                    fixed_lines.append(' ' * (indent + 4) + 'logger.error(f"Error: {e}")')
                    fixed_lines.append(' ' * (indent + 4) + 'raise')
                    self.errors_fixed += 1
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _fix_incomplete_for_loops(self, content: str) -> str:
        """Fix incomplete for loops"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)
            
            # Look for for loops without content
            if re.match(r'\s*for\s+.*:\s*$', line):
                j = i + 1
                has_content = False
                
                while j < len(lines) and j < i + 5:  # Look ahead a few lines
                    next_line = lines[j]
                    if re.match(r'\s*\S', next_line) and not re.match(r'\s*#', next_line):
                        if len(next_line) - len(next_line.lstrip()) > len(line) - len(line.lstrip()):
                            has_content = True
                            break
                    elif re.match(r'^\s*(def|class|if|for|while|try)', next_line):
                        break
                    j += 1
                
                if not has_content:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * (indent + 4) + 'pass')
                    self.errors_fixed += 1
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _fix_incomplete_while_loops(self, content: str) -> str:
        """Fix incomplete while loops"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)
            
            # Look for while loops without content
            if re.match(r'\s*while\s+.*:\s*$', line):
                j = i + 1
                has_content = False
                
                while j < len(lines) and j < i + 5:
                    next_line = lines[j]
                    if re.match(r'\s*\S', next_line) and not re.match(r'\s*#', next_line):
                        if len(next_line) - len(next_line.lstrip()) > len(line) - len(line.lstrip()):
                            has_content = True
                            break
                    elif re.match(r'^\s*(def|class|if|for|while|try)', next_line):
                        break
                    j += 1
                
                if not has_content:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * (indent + 4) + 'pass')
                    self.errors_fixed += 1
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _fix_incomplete_if_blocks(self, content: str) -> str:
        """Fix incomplete if blocks"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)
            
            # Look for if statements without content
            if re.match(r'\s*(if|elif|else)\s*.*:\s*$', line):
                j = i + 1
                has_content = False
                
                while j < len(lines) and j < i + 5:
                    next_line = lines[j]
                    if re.match(r'\s*\S', next_line) and not re.match(r'\s*#', next_line):
                        if len(next_line) - len(next_line.lstrip()) > len(line) - len(line.lstrip()):
                            has_content = True
                            break
                    elif re.match(r'^\s*(def|class|if|elif|else|for|while|try)', next_line):
                        break
                    j += 1
                
                if not has_content:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * (indent + 4) + 'pass')
                    self.errors_fixed += 1
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _fix_incomplete_method_definitions(self, content: str) -> str:
        """Fix incomplete method definitions"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)
            
            # Look for method definitions without content
            if re.match(r'\s*def\s+\w+.*:\s*$', line):
                j = i + 1
                has_content = False
                
                while j < len(lines) and j < i + 10:
                    next_line = lines[j]
                    if re.match(r'\s*\S', next_line) and not re.match(r'\s*#', next_line):
                        if len(next_line) - len(next_line.lstrip()) > len(line) - len(line.lstrip()):
                            has_content = True
                            break
                    elif re.match(r'^\s*(def|class)', next_line):
                        break
                    j += 1
                
                if not has_content:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * (indent + 4) + 'pass')
                    self.errors_fixed += 1
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _fix_incomplete_class_definitions(self, content: str) -> str:
        """Fix incomplete class definitions"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)
            
            # Look for class definitions without content
            if re.match(r'\s*class\s+\w+.*:\s*$', line):
                j = i + 1
                has_content = False
                
                while j < len(lines) and j < i + 10:
                    next_line = lines[j]
                    if re.match(r'\s*\S', next_line) and not re.match(r'\s*#', next_line):
                        if len(next_line) - len(next_line.lstrip()) > len(line) - len(line.lstrip()):
                            has_content = True
                            break
                    elif re.match(r'^\s*class', next_line):
                        break
                    j += 1
                
                if not has_content:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * (indent + 4) + 'pass')
                    self.errors_fixed += 1
            
            i += 1
        
        return '\n'.join(fixed_lines)

def main():
    """Main execution function"""
    print("🔧 Starting Syntax Error Fixing...")
    
    fixer = SyntaxErrorFixer()
    results = fixer.fix_all_syntax_errors()
    
    print(f"\n📊 FIXING RESULTS:")
    print(f"Files scanned: {results['files_scanned']}")
    print(f"Files fixed: {results['files_fixed']}")
    print(f"Errors fixed: {results['errors_fixed']}")
    
    if results['files_fixed'] > 0:
        print(f"\n✅ Successfully fixed syntax errors in {results['files_fixed']} files!")
        print("\nFixed files:")
        for file_path in fixer.fixed_files[:10]:  # Show first 10
            print(f"  - {file_path}")
        if len(fixer.fixed_files) > 10:
            print(f"  ... and {len(fixer.fixed_files) - 10} more")

if __name__ == "__main__":
    main()