#!/usr/bin/env python3
"""
GitHub Actions Workflow Structure Fixer
Fixes indentation and structural issues in GitHub Actions workflow files
"""

import re
import yaml
from pathlib import Path

def fix_workflow_structure(file_path):
    """Fix GitHub Actions workflow structure"""
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    in_jobs_section = False
    current_job_indent = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Track if we're in the jobs section
        if stripped == 'jobs:':
            in_jobs_section = True
            fixed_lines.append(line)
            i += 1
            continue
        
        # If we're in jobs section, fix job definitions
        if in_jobs_section and stripped and not line.startswith(' '):
            # This indicates we've left the jobs section
            in_jobs_section = False
        
        if in_jobs_section:
            # Handle job definitions (should be indented 2 spaces)
            if re.match(r'^  [a-zA-Z0-9_-]+:$', stripped + ':') and not line.startswith('    '):
                # This is a job name, should be indented 2 spaces
                job_name = stripped.rstrip(':')
                fixed_lines.append(f'  {job_name}:\n')
                current_job_indent = 4  # Next properties should be indented 4 spaces
                i += 1
                continue
            
            # Handle job properties (name, runs-on, etc.)
            elif re.match(r'^(name|runs-on|needs|if|outputs|environment|strategy|env|defaults|permissions|timeout-minutes|continue-on-error):.*', stripped):
                # Job property, should be indented 4 spaces
                prop_match = re.match(r'^(.*?):\s*(.*)$', stripped)
                if prop_match:
                    prop_name = prop_match.group(1)
                    prop_value = prop_match.group(2)
                    if prop_value:
                        fixed_lines.append(f'    {prop_name}: {prop_value}\n')
                    else:
                        fixed_lines.append(f'    {prop_name}:\n')
                i += 1
                continue
            
            # Handle steps section
            elif stripped == 'steps:':
                fixed_lines.append('    steps:\n')
                i += 1
                continue
            
            # Handle matrix strategy
            elif stripped == 'matrix:':
                fixed_lines.append('      matrix:\n')
                i += 1
                continue
            
            # Handle step items
            elif stripped.startswith('- name:') or stripped.startswith('- uses:'):
                # Step items should be indented 6 spaces
                fixed_lines.append(f'      {stripped}\n')
                i += 1
                continue
            
            # Handle step properties (with:, run:, env:, etc.)
            elif re.match(r'^(with|run|env|if|id|continue-on-error|timeout-minutes|working-directory):.*', stripped):
                # Step properties should be indented 8 spaces
                fixed_lines.append(f'        {stripped}\n')
                i += 1
                continue
            
            # Handle nested properties under 'with' or 'env'
            elif line.startswith('  ') and re.match(r'^[a-zA-Z0-9_-]+:\s*', stripped):
                # Check if this looks like a nested property
                if i > 0 and ('with:' in fixed_lines[-1] or 'env:' in fixed_lines[-1] or any('with:' in fixed_lines[j] or 'env:' in fixed_lines[j] for j in range(max(0, len(fixed_lines)-3), len(fixed_lines)))):
                    # Nested property under with/env, should be indented 10 spaces
                    fixed_lines.append(f'          {stripped}\n')
                    i += 1
                    continue
        
        # Default: keep the line as is
        fixed_lines.append(line)
        i += 1
    
    # Write back the fixed content
    fixed_content = ''.join(fixed_lines)
    
    # Ensure document starts with ---
    if not fixed_content.startswith('---'):
        fixed_content = '---\n' + fixed_content
    
    # Ensure file ends with newline
    if not fixed_content.endswith('\n'):
        fixed_content += '\n'
    
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    return True

def validate_yaml_syntax(file_path):
    """Validate YAML syntax after fixing"""
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        return True
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error in {file_path}: {e}")
        return False

def main():
    """Main function to fix all workflow files"""
    
    workflows_dir = Path('.github/workflows')
    if not workflows_dir.exists():
        print("❌ .github/workflows directory not found")
        return
    
    fixed_files = []
    validated_files = []
    
    # Focus on the main workflow files first
    priority_files = ['ci.yml', 'production-deployment.yml', 'security-scan.yml']
    
    for filename in priority_files:
        file_path = workflows_dir / filename
        if file_path.exists():
            print(f"🔧 Fixing {filename}...")
            try:
                fix_workflow_structure(file_path)
                fixed_files.append(filename)
                
                if validate_yaml_syntax(file_path):
                    validated_files.append(filename)
                    print(f"✅ Fixed and validated: {filename}")
                else:
                    print(f"⚠️ Fixed but validation failed: {filename}")
                    
            except Exception as e:
                print(f"❌ Error fixing {filename}: {e}")
    
    print(f"\n🎯 Summary:")
    print(f"  • Fixed: {len(fixed_files)} files")
    print(f"  • Validated: {len(validated_files)} files")
    
    if validated_files:
        print("✅ Successfully fixed and validated:")
        for file in validated_files:
            print(f"  • {file}")

if __name__ == "__main__":
    main()