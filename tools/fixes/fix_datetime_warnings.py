#!/usr/bin/env python3
"""
Script pour corriger tous les datetime.utcnow() deprecated warnings
Author: Fahed Mlaiel <mlaiel@live.de>
"""

import os
import re
import sys

def fix_datetime_warnings(file_path):
    """Fix datetime.utcnow() warnings in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check if timezone is already imported
        has_timezone_import = re.search(r'from datetime import.*timezone', content)
        
        # Add timezone import if not present
        if not has_timezone_import:
            # Find existing datetime import
            datetime_import_match = re.search(r'from datetime import ([^\n]+)', content)
            if datetime_import_match:
                imports = datetime_import_match.group(1)
                if 'timezone' not in imports:
                    new_imports = imports.strip() + ', timezone'
                    content = content.replace(
                        f'from datetime import {imports}',
                        f'from datetime import {new_imports}'
                    )
        
        # Replace datetime.utcnow() with datetime.now(timezone.utc)
        content = re.sub(r'datetime\.utcnow\(\)', 'datetime.now(timezone.utc)', content)
        
        # Replace datetime.datetime.utcnow() with datetime.datetime.now(datetime.timezone.utc)
        content = re.sub(r'datetime\.datetime\.utcnow\(\)', 'datetime.datetime.now(datetime.timezone.utc)', content)
        
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
    workspace_dir = '/workspaces/iaCherie'
    files_fixed = 0
    
    # Files to fix
    files_to_fix = [
        'main.py',
        'core/ai/ai_model_core.py',
        'core/ai/ia_processing_core.py', 
        'core/ai/ml_pipeline_core.py',
        'database/models.py',
        'database/migrations.py',
        'database/analytics_engine.py',
        'database/monetization_models.py',
        'microservices/content_services/content_distribution_service.py',
        'microservices/monitoring_services/health_monitoring_service.py'
    ]
    
    print("🔧 Fixing datetime.utcnow() deprecated warnings...")
    
    for file_path in files_to_fix:
        full_path = os.path.join(workspace_dir, file_path)
        if os.path.exists(full_path):
            if fix_datetime_warnings(full_path):
                files_fixed += 1
        else:
            print(f"⚠️ File not found: {full_path}")
    
    print(f"\n✅ Fixed {files_fixed} files")
    print("🎉 All datetime.utcnow() warnings should be resolved!")

if __name__ == '__main__':
    main()