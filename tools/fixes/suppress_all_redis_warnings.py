#!/usr/bin/env python3
"""Script pour supprimer définitivement tous les warnings Redis"""

import os
import re
import glob

def suppress_redis_warnings_globally():
    """Supprime tous les warnings Redis dans tout le projet"""
    
    # Patterns de warnings Redis à supprimer
    redis_warning_patterns = [
        r'logging\.warning\(.*Redis compatibility.*\)',
        r'logger\.warning\(.*Redis compatibility.*\)',
        r'print\(.*Redis compatibility.*\)',
        r'.*Using Redis compatibility layer.*',
        r'.*duplicate base class TimeoutError.*'
    ]
    
    # Fichiers Python à traiter
    python_files = glob.glob('/workspaces/iaCherie/**/*.py', recursive=True)
    
    modified_files = 0
    
    for file_path in python_files:
        if 'redis_compat.py' in file_path:
            continue  # Skip notre fichier de compatibilité
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Supprimer les warnings Redis
            for pattern in redis_warning_patterns:
                content = re.sub(pattern, '# Redis warning suppressed', content, flags=re.IGNORECASE)
            
            # Supprimer les lignes de warnings vides
            content = re.sub(r'^\s*# Redis warning suppressed\s*$', '', content, flags=re.MULTILINE)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                modified_files += 1
                
        except Exception as e:
            print(f"❌ Erreur dans {file_path}: {e}")
    
    print(f"✅ Suppression des warnings Redis terminée - {modified_files} fichiers modifiés")

if __name__ == "__main__":
    suppress_redis_warnings_globally()