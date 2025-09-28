#!/usr/bin/env python3
"""Script pour supprimer tous les warnings Redis répétitifs"""

import os
import re

def suppress_redis_warnings_in_file(file_path):
    """Supprime les warnings Redis dans un fichier spécifique"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Remplacer les patterns de warnings Redis
        patterns_to_replace = [
            (r'logging\.warning\(f?"Using Redis compatibility layer: \{e\}"\)', 'pass  # Redis warning suppressed'),
            (r'logger\.warning\(f?"Using Redis compatibility layer: \{.*?\}"\)', 'pass  # Redis warning suppressed'),
            (r'print.*Redis compatibility.*', '# Redis warning suppressed')
        ]
        
        modified = False
        for pattern, replacement in patterns_to_replace:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                modified = True
        
        if modified:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Supprimé warnings Redis dans {file_path}")
        
    except Exception as e:
        print(f"❌ Erreur dans {file_path}: {e}")

# Liste des fichiers à modifier
files_to_modify = [
    "/workspaces/Ainfluencer/database/database_operations.py",
    "/workspaces/Ainfluencer/infrastructure/storage_modules/mongodb_adapter.py",
    "/workspaces/Ainfluencer/infrastructure/storage_modules/file_storage.py",
    "/workspaces/Ainfluencer/infrastructure/storage_modules/database_adapter.py",
    "/workspaces/Ainfluencer/infrastructure/storage_modules/redis_adapter.py",
    "/workspaces/Ainfluencer/infrastructure/compliance/compliance_alerting.py",
    "/workspaces/Ainfluencer/infrastructure/compliance/global_compliance_manager.py",
    "/workspaces/Ainfluencer/infrastructure/compliance/regulatory_compliance.py",
    "/workspaces/Ainfluencer/infrastructure/compliance/compliance_documentation.py",
    "/workspaces/Ainfluencer/infrastructure/compliance/data_protection_impact_assessment.py",
    "/workspaces/Ainfluencer/infrastructure/compliance/regional_compliance.py",
    "/workspaces/Ainfluencer/infrastructure/compliance/compliance_analytics.py",
]

for file_path in files_to_modify:
    if os.path.exists(file_path):
        suppress_redis_warnings_in_file(file_path)

print("\n✅ Suppression des warnings Redis terminée")