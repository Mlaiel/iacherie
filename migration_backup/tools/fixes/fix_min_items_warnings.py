#!/usr/bin/env python3
"""
Script pour corriger tous les min_items deprecated en min_length
Author: Fahed Mlaiel <mlaiel@live.de>
"""

import os
import re
import sys

def fix_min_items_warnings(file_path):
    """Fix min_items warnings in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace min_items with min_length
        content = re.sub(r'min_items=', 'min_length=', content)
        
        # Write back only if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"➡️ No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all Python files"""
    workspace_dir = '/workspaces/IA Chéries'
    files_fixed = 0
    
    # Files that contain min_items
    files_to_fix = [
        'microservices/content_services/content_processing_service.py',
        'api/routes/content_routes.py',
        'api/routes/seo_routes.py',
        'api/routes/analytics_routes.py',
        'api/routes/auth_routes.py',
        'api/routes/distribution_routes.py',
        'infrastructure/security_modules/auth.py',
        'backend/api/business_api.py'
    ]
    
    print("🔧 Fixing min_items deprecated warnings...")
    
    for file_path in files_to_fix:
        full_path = os.path.join(workspace_dir, file_path)
        if os.path.exists(full_path):
            if fix_min_items_warnings(full_path):
                files_fixed += 1
        else:
            print(f"⚠️ File not found: {full_path}")
    
    print(f"\n✅ Fixed {files_fixed} files")
    print("🎉 All min_items warnings should be resolved!")

if __name__ == '__main__':
    main()