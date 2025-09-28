#!/usr/bin/env python3
"""Script pour corriger les constructeurs des classes Core"""

import os
import re

def fix_constructor_in_file(filepath):
    """Corrige le constructeur d'une classe Core dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns to fix
        patterns = [
            # Simple __init__(self): -> __init__(self, level: str = "enterprise"):
            (r'def __init__\(self\):', r'def __init__(self, level: str = "enterprise"):'),
            
            # Add level parameter to existing parameters
            (r'def __init__\(self, ([^)]+)\):', r'def __init__(self, \1, level: str = "enterprise"):'),
        ]
        
        modified = False
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                break
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            print(f"⏭️  Skip: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Corrige tous les constructeurs problématiques"""
    
    # Files that need fixing based on error logs
    problem_files = [
        'core/business/monetization_business_core.py',
        'core/business/creator_matching_core.py', 
        'core/business/collaboration_business_core.py',
        'core/business/gamification_business_core.py',
        'core/business/achievement_engagement_core.py',
        'core/business/seo_business_core.py',
        'core/business/distribution_business_core.py',
        'core/business/multi_platform_distribution_core.py',
        'core/business/search_optimization_core.py',
        'core/security/protection_business_core.py',
        'core/security/rights_management_core.py',
    ]
    
    fixed_count = 0
    for file in problem_files:
        filepath = f'/workspaces/Ainfluencer/{file}'
        if os.path.exists(filepath):
            if fix_constructor_in_file(filepath):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {filepath}")
    
    print(f"\n🎉 Fixed {fixed_count} files")

if __name__ == "__main__":
    main()