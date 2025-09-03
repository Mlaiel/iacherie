#!/usr/bin/env python3
"""
YAML Lint Fixer for CI/CD Workflows
Fixes common yamllint issues in GitHub Actions workflow files
"""

import os
import re
import yaml
from pathlib import Path

def fix_yaml_issues(file_path):
    """Fix common YAML linting issues"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: Add document start if missing
    if not content.startswith('---'):
        content = '---\n' + content
    
    # Fix 2: Remove trailing spaces
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    
    # Fix 3: Fix indentation issues (GitHub Actions standard is 2 spaces)
    fixed_lines = []
    for line in lines:
        # Fix common indentation issues in GitHub Actions
        if re.match(r'^    [a-zA-Z]', line) and not line.startswith('        '):
            # Convert 4-space to 2-space indentation for top-level job properties
            line = re.sub(r'^    ', '  ', line)
        fixed_lines.append(line)
    
    # Fix 4: Fix brackets spacing (remove extra spaces)
    content = '\n'.join(fixed_lines)
    content = re.sub(r'\[\s+([^\]]+)\s+\]', r'[\1]', content)
    
    # Fix 5: Fix truthy values
    content = re.sub(r'^(\s*on:\s*)$', r'\1', content, flags=re.MULTILINE)
    
    # Fix 6: Ensure file ends with newline
    if not content.endswith('\n'):
        content += '\n'
    
    # Fix 7: Handle long lines by wrapping them appropriately
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        if len(line) > 80 and '|' not in line and not line.strip().startswith('#'):
            # For long run commands, try to add line breaks
            if 'run:' in line and len(line) > 80:
                # Convert single-line run to multi-line
                parts = line.split('run:', 1)
                if len(parts) == 2:
                    prefix = parts[0] + 'run: |'
                    command = parts[1].strip()
                    fixed_lines.append(prefix)
                    # Indent the command properly
                    indent = '        '  # 8 spaces for run content
                    fixed_lines.append(indent + command)
                    continue
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to fix all workflow files"""
    
    workflows_dir = Path('.github/workflows')
    if not workflows_dir.exists():
        print("❌ .github/workflows directory not found")
        return
    
    fixed_files = []
    
    for workflow_file in workflows_dir.glob('*.yml'):
        try:
            if fix_yaml_issues(workflow_file):
                fixed_files.append(workflow_file.name)
                print(f"✅ Fixed: {workflow_file.name}")
            else:
                print(f"📋 No changes needed: {workflow_file.name}")
        except Exception as e:
            print(f"❌ Error fixing {workflow_file.name}: {e}")
    
    for workflow_file in workflows_dir.glob('*.yaml'):
        try:
            if fix_yaml_issues(workflow_file):
                fixed_files.append(workflow_file.name)
                print(f"✅ Fixed: {workflow_file.name}")
            else:
                print(f"📋 No changes needed: {workflow_file.name}")
        except Exception as e:
            print(f"❌ Error fixing {workflow_file.name}: {e}")
    
    print(f"\n🎯 Summary: Fixed {len(fixed_files)} workflow files")
    if fixed_files:
        print("Fixed files:")
        for file in fixed_files:
            print(f"  • {file}")

if __name__ == "__main__":
    main()