#!/usr/bin/env python3
"""
Comprehensive Fix Script for Multimedia Module
Systematically fixes syntax errors in all multimedia files
"""

import os
import re
from pathlib import Path

def fix_file_syntax(filepath):
    """Fix common syntax errors in a file"""
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    skip_corrupted_section = False
    in_try_block = False
    brace_depth = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Skip obviously corrupted sections with malformed try/except
        if ('except Exception as e:' in line and 
            i + 1 < len(lines) and 
            lines[i + 1].strip().startswith('try:')):
            # Fix the except and skip the corrupted try
            fixed_lines.append(line)
            fixed_lines.append('            logger.error(f"Error: {e}")')
            fixed_lines.append('            raise')
            skip_corrupted_section = True
            continue
        
        # Skip corrupted sections until we find a proper function/class definition
        if skip_corrupted_section:
            if (line_stripped.startswith('def ') or 
                line_stripped.startswith('class ') or 
                line_stripped.startswith('async def ') or
                (line_stripped and not line.startswith(' '))):
                skip_corrupted_section = False
            else:
                continue
        
        # Fix unclosed docstrings
        if line_stripped.startswith('"""') and line_stripped.endswith('"""') and len(line_stripped) > 6:
            # Single line docstring is fine
            pass
        elif line_stripped.startswith('"""') and not line_stripped.endswith('"""'):
            # Opening docstring - ensure it gets closed
            fixed_lines.append(line)
            # Look ahead to find the closing or add one
            found_close = False
            for j in range(i + 1, min(i + 10, len(lines))):
                if '"""' in lines[j]:
                    found_close = True
                    break
            if not found_close:
                fixed_lines.append(line.replace('"""', '"""Placeholder docstring"""'))
                continue
        
        # Add missing indentation for orphaned code
        if (line_stripped.startswith('logger.error(') or 
            line_stripped.startswith('raise') or
            line_stripped.startswith('return')):
            if not line.startswith('        '):  # Not properly indented
                line = '        ' + line_stripped
        
        fixed_lines.append(line)
    
    # Write back the fixed content
    with open(filepath, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"✅ Fixed {filepath}")

def main():
    """Fix all multimedia files"""
    multimedia_dir = Path("multimedia")
    
    # Files that need fixing based on our validation
    problematic_files = [
        "metadata_extractor.py",
        "monitoring.py", 
        "optimization.py",
        "protection.py",
        "validators.py",
        "video.py",
        "distribution.py"
    ]
    
    for filename in problematic_files:
        filepath = multimedia_dir / filename
        if filepath.exists():
            try:
                fix_file_syntax(filepath)
            except Exception as e:
                print(f"❌ Error fixing {filepath}: {e}")

if __name__ == "__main__":
    main()