#!/usr/bin/env python3
"""
Script de correction ULTIME pour éliminer TOUS les warnings
Author: Fahed Mlaiel <mlaiel@live.de>
"""

import os
import re
import sys

def fix_all_warnings_in_file(file_path):
    """Fix all warnings in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Add timezone import if datetime is imported but timezone is not
        if 'from datetime import' in content and 'timezone' not in content:
            content = re.sub(r'from datetime import ([^\n]+)', lambda m: f'from datetime import {m.group(1)}, timezone' if 'timezone' not in m.group(1) else m.group(0), content)
        
        # 2. Replace datetime.utcnow() with datetime.now(timezone.utc)
        content = re.sub(r'datetime\.utcnow\(\)', 'datetime.now(timezone.utc)', content)
        
        # 3. Replace datetime.datetime.utcnow() with datetime.datetime.now(datetime.timezone.utc) 
        content = re.sub(r'datetime\.datetime\.utcnow\(\)', 'datetime.datetime.now(datetime.timezone.utc)', content)
        
        # 4. Fix default_factory patterns
        content = re.sub(r'Field\(default_factory=datetime\.now\(timezone\.utc\)\)', 'Field(default_factory=lambda: datetime.now(timezone.utc))', content)
        
        # 5. Replace min_items with min_length
        content = re.sub(r'min_items=', 'min_length=', content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main correction function"""
    workspace_dir = '/workspaces/IA Chéries'
    files_fixed = 0
    
    print("🔧 ULTIMATE WARNING FIXER - PROCESSING ALL PYTHON FILES...")
    
    # Walk through all Python files
    for root, dirs, files in os.walk(workspace_dir):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', '.pytest_cache', 'node_modules']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, workspace_dir)
                
                if fix_all_warnings_in_file(file_path):
                    files_fixed += 1
                    print(f"✅ Fixed: {rel_path}")
                else:
                    print(f"➡️ No changes: {rel_path}")
    
    print(f"\n🎉 COMPLETED: Fixed {files_fixed} files")
    print("🏆 All datetime and Pydantic warnings should be resolved!")

if __name__ == '__main__':
    main()