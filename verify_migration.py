#!/usr/bin/env python3
"""
🔍 VÉRIFICATEUR POST-MIGRATION - IA CHÉRIE
==========================================

Script pour vérifier que la migration vers IA Chérie est complète
et qu'il ne reste aucune référence à l'ancien nom.

Author: Fahed Mlaiel
Date: 1er Octobre 2025
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Patterns à rechercher (références restantes à l'ancien nom)
SEARCH_PATTERNS = [
    'Ainfluencer',
    'AINFLUENCER', 
    'ainfluencer',
    'AInfluencer',
    'Ainflue',
    'AINFLUE',
    'ainflue',
]

# Extensions de fichiers à vérifier
EXTENSIONS = {
    '.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md', '.txt',
    '.sh', '.yml', '.yaml', '.env', '.dockerfile', '.toml', '.ini',
    '.sql', '.html', '.css', '.scss'
}

# Fichiers et dossiers à exclure de la vérification
EXCLUDE_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv',
    '.next', 'dist', 'build', '.cache', '.pytest_cache',
    'logs', 'tmp', 'cache', 'fingerprints'
}

EXCLUDE_FILES = {
    'fix_ainfluencer_references.py',
    'fix_python_imports.py',
    'verify_migration.py',
    'rename_to_iacherie.py',
    'migrate_to_iacherie.py'
}

def find_files_to_check(root_dir: str) -> List[Path]:
    """Trouve tous les fichiers à vérifier"""
    files_to_check = []
    
    for ext in EXTENSIONS:
        pattern = f"**/*{ext}"
        for file_path in Path(root_dir).glob(pattern):
            if file_path.is_file():
                # Vérifier les exclusions
                if any(exclude_dir in str(file_path) for exclude_dir in EXCLUDE_DIRS):
                    continue
                if file_path.name in EXCLUDE_FILES:
                    continue
                    
                files_to_check.append(file_path)
    
    return files_to_check

def check_file_for_references(file_path: Path) -> List[Tuple[int, str, str]]:
    """Vérifie un fichier pour les références restantes"""
    references_found = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            for pattern in SEARCH_PATTERNS:
                if pattern.lower() in line_lower:
                    # Éviter les faux positifs dans les noms de fichiers de scripts
                    if 'ainfluencer_references' in line or 'migrate_to_iacherie' in line:
                        continue
                    
                    # Éviter les commentaires de migration
                    if '# Migration:' in line or '# Ancien:' in line:
                        continue
                    
                    references_found.append((line_num, pattern, line.strip()))
        
        return references_found
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la lecture de {file_path}: {e}")
        return []

def categorize_references(references: Dict[Path, List[Tuple[int, str, str]]]) -> Dict[str, List]:
    """Catégorise les références trouvées"""
    categories = {
        'critical': [],      # Dans le code principal
        'backup': [],        # Dans migration_backup
        'documentation': [], # Dans les fichiers de documentation
        'configuration': [], # Dans les fichiers de configuration
    }
    
    for file_path, file_references in references.items():
        file_str = str(file_path)
        
        for line_num, pattern, line in file_references:
            ref_info = {
                'file': file_path,
                'line': line_num,
                'pattern': pattern,
                'content': line
            }
            
            if 'migration_backup' in file_str:
                categories['backup'].append(ref_info)
            elif any(doc_ext in file_str for doc_ext in ['.md', '.txt', 'README', 'GUIDE']):
                categories['documentation'].append(ref_info)
            elif any(conf_ext in file_str for conf_ext in ['.env', '.yml', '.yaml', '.toml', '.ini']):
                categories['configuration'].append(ref_info)
            else:
                categories['critical'].append(ref_info)
    
    return categories

def main():
    """Fonction principale"""
    print("🔍 VÉRIFICATEUR POST-MIGRATION - IA CHÉRIE")
    print("==========================================")
    print()
    
    root_dir = "/workspaces/iacherie"
    
    # Trouver tous les fichiers à vérifier
    print("🔍 Recherche des fichiers à vérifier...")
    files_to_check = find_files_to_check(root_dir)
    print(f"📁 {len(files_to_check)} fichiers à vérifier")
    print()
    
    # Vérifier chaque fichier
    all_references = {}
    total_references = 0
    
    print("🔎 Recherche des références restantes...")
    for file_path in files_to_check:
        references = check_file_for_references(file_path)
        if references:
            all_references[file_path] = references
            total_references += len(references)
    
    print()
    
    # Catégoriser les résultats
    if all_references:
        categories = categorize_references(all_references)
        
        print("📊 RAPPORT DE VÉRIFICATION")
        print("==========================")
        print(f"📁 Fichiers vérifiés: {len(files_to_check)}")
        print(f"⚠️  Références trouvées: {total_references}")
        print()
        
        # Références critiques (dans le code principal)
        if categories['critical']:
            print("🚨 RÉFÉRENCES CRITIQUES (Code principal)")
            print("=======================================")
            for ref in categories['critical']:
                print(f"📄 {ref['file']}")
                print(f"   Ligne {ref['line']}: {ref['pattern']} dans '{ref['content']}'")
            print()
        
        # Références dans migration_backup (acceptable)
        if categories['backup']:
            print("📦 RÉFÉRENCES DANS MIGRATION_BACKUP (Acceptable)")
            print("==============================================")
            print(f"   {len(categories['backup'])} références trouvées dans les sauvegardes")
            print()
        
        # Références dans la documentation
        if categories['documentation']:
            print("📚 RÉFÉRENCES DANS DOCUMENTATION")
            print("===============================")
            for ref in categories['documentation']:
                print(f"📄 {ref['file']}")
                print(f"   Ligne {ref['line']}: {ref['pattern']} dans '{ref['content']}'")
            print()
        
        # Références dans la configuration
        if categories['configuration']:
            print("⚙️  RÉFÉRENCES DANS CONFIGURATION")
            print("=================================")
            for ref in categories['configuration']:
                print(f"📄 {ref['file']}")
                print(f"   Ligne {ref['line']}: {ref['pattern']} dans '{ref['content']}'")
            print()
        
        # Résumé
        critical_count = len(categories['critical'])
        if critical_count > 0:
            print("❌ MIGRATION INCOMPLÈTE!")
            print(f"Il reste {critical_count} références critiques à corriger.")
        else:
            print("✅ MIGRATION RÉUSSIE!")
            print("Aucune référence critique trouvée dans le code principal.")
            if categories['backup'] or categories['documentation'] or categories['configuration']:
                print("📝 Note: Quelques références non critiques persistent (documentation, backup, etc.)")
    
    else:
        print("📊 RAPPORT DE VÉRIFICATION")
        print("==========================")
        print(f"📁 Fichiers vérifiés: {len(files_to_check)}")
        print(f"✅ Références trouvées: 0")
        print()
        print("🎉 MIGRATION PARFAITEMENT COMPLÈTE!")
        print("Aucune référence à l'ancien nom trouvée.")
    
    print()
    print("🏁 Vérification terminée.")

if __name__ == "__main__":
    main()