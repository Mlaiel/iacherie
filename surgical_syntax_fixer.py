#!/usr/bin/env python3
"""
Surgical Syntax Error Fixer
Fixes critical syntax errors that block business logic implementation.
"""

import ast
import re
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SurgicalSyntaxFixer:
    """Fixes critical syntax errors with minimal changes"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.fixes_applied = []
    
    def fix_critical_files(self) -> Dict[str, int]:
        """Fix syntax errors in critical business files"""
        logger.info("🔧 Starting surgical syntax error fixing...")
        
        # Focus on files needed for business logic implementation
        critical_files = [
            "core/interfaces/platform_interfaces.py",
            "core/interfaces/monetization_interfaces.py",
            "tests/accessibility/test_wcag_compliance.py",
            "scripts/testing/simple_agents.py"
        ]
        
        results = {"fixed": 0, "failed": 0, "files_processed": 0}
        
        for file_path in critical_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                fixed = self._fix_file_syntax(full_path)
                results["files_processed"] += 1
                if fixed:
                    results["fixed"] += 1
                else:
                    results["failed"] += 1
        
        return results
    
    def _fix_file_syntax(self, file_path: Path) -> bool:
        """Fix syntax errors in a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Test if file already has valid syntax
            try:
                ast.parse(content)
                logger.info(f"✅ {file_path} already has valid syntax")
                return True
            except SyntaxError as e:
                logger.info(f"🔧 Fixing syntax error in {file_path}: {e}")
                
                # Apply targeted fixes based on error type
                fixed_content = self._apply_targeted_fixes(content, str(e), file_path)
                
                # Validate the fix
                try:
                    ast.parse(fixed_content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    logger.info(f"✅ Fixed syntax error in {file_path}")
                    return True
                except SyntaxError as validation_error:
                    logger.error(f"❌ Could not fix syntax error in {file_path}: {validation_error}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            return False
    
    def _apply_targeted_fixes(self, content: str, error_msg: str, file_path: Path) -> str:
        """Apply targeted fixes based on specific error patterns"""
        
        # Fix unmatched parentheses/brackets
        if "closing parenthesis ')' does not match opening parenthesis '{'" in error_msg:
            content = self._fix_mismatched_brackets(content)
        
        # Fix unmatched parentheses 
        elif "unmatched ')'" in error_msg:
            content = self._fix_unmatched_parentheses(content)
        
        # Fix incomplete try blocks
        elif "expected 'except' or 'finally' block" in error_msg:
            content = self._fix_incomplete_try_blocks(content)
        
        # Fix indentation errors
        elif "expected an indented block" in error_msg:
            content = self._fix_indentation_errors(content)
        
        # Fix unterminated strings
        elif "unterminated triple-quoted string" in error_msg:
            content = self._fix_unterminated_strings(content)
        
        return content
    
    def _fix_mismatched_brackets(self, content: str) -> str:
        """Fix mismatched brackets and parentheses"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Replace common mismatched bracket patterns
            if re.search(r'\{[^}]*\)', line):
                line = re.sub(r'\{([^}]*)\)', r'{\1}', line)
            elif re.search(r'\([^)]*\}', line):
                line = re.sub(r'\(([^)]*)\}', r'(\1)', line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_unmatched_parentheses(self, content: str) -> str:
        """Fix unmatched parentheses"""
        lines = content.split('\n')
        fixed_lines = []
        paren_stack = []
        
        for line_num, line in enumerate(lines):
            # Track parentheses balance
            for char in line:
                if char == '(':
                    paren_stack.append(line_num)
                elif char == ')':
                    if paren_stack:
                        paren_stack.pop()
                    else:
                        # Unmatched closing paren - remove it
                        line = line.replace(')', '', 1)
                        break
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_incomplete_try_blocks(self, content: str) -> str:
        """Fix incomplete try blocks by adding proper except clauses"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for try blocks
            if re.match(r'\s*try:\s*$', line):
                indent = len(line) - len(line.lstrip())
                base_indent = " " * indent
                
                # Look ahead to see if there's a proper except/finally
                has_except_or_finally = False
                j = i + 1
                while j < len(lines) and j < i + 20:  # Look ahead max 20 lines
                    next_line = lines[j]
                    if next_line.strip() == "":
                        j += 1
                        continue
                    
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent:
                        # End of try block scope
                        break
                    
                    if re.match(r'\s*(except|finally):', next_line):
                        has_except_or_finally = True
                        break
                    
                    j += 1
                
                # Add the try line
                fixed_lines.append(line)
                
                # If no except/finally found, add a generic except block
                if not has_except_or_finally:
                    # Add content until we need the except
                    k = i + 1
                    while k < len(lines) and k < j:
                        fixed_lines.append(lines[k])
                        k += 1
                    
                    # Add the except block
                    fixed_lines.append(f"{base_indent}except Exception as e:")
                    fixed_lines.append(f"{base_indent}    logger.error(f'Error: {{e}}')")
                    fixed_lines.append(f"{base_indent}    raise")
                    
                    i = k - 1  # Skip the lines we already processed
            else:
                fixed_lines.append(line)
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _fix_indentation_errors(self, content: str) -> str:
        """Fix indentation errors"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix common indentation patterns
            if i > 0:
                prev_line = lines[i-1].strip()
                
                # If previous line ends with colon and current line is not indented
                if prev_line.endswith(':') and line.strip() and not line.startswith(' '):
                    # Add 4 spaces indentation
                    line = "    " + line
                
                # If we have an except with no indented block
                elif prev_line.startswith('except') and prev_line.endswith(':'):
                    if not line.strip():
                        # Add a pass statement
                        base_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                        line = " " * (base_indent + 4) + "pass"
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_unterminated_strings(self, content: str) -> str:
        """Fix unterminated triple-quoted strings"""
        # Simple fix: close any open triple quotes
        if content.count('"""') % 2 != 0:
            content += '\n"""'
        if content.count("'''") % 2 != 0:
            content += "\n'''"
        
        return content

def main():
    """Main execution"""
    fixer = SurgicalSyntaxFixer()
    results = fixer.fix_critical_files()
    
    print(f"\n🔧 SYNTAX ERROR FIXING RESULTS:")
    print(f"✅ Fixed: {results['fixed']} files")
    print(f"❌ Failed: {results['failed']} files")
    print(f"📁 Files processed: {results['files_processed']}")

if __name__ == "__main__":
    main()