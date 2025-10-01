#!/usr/bin/env python3
"""
Script de renommage global de IA Chéries vers IA Chérie
Remplace tous les noms dans les fichiers du projet
"""

import os
import re
from pathlib import Path

# Mappings de renommage
REPLACEMENTS = {
    # Noms complets
    'IA Chéries': 'iacherie',
    'IA Chéries': 'iaCherie',
    'IA CHÉRIES': 'IACHERIE',
    'IA Chéries': 'iacherie',
    'ainflue': 'iacherie',
    'IA CHÉRIES': 'IACHERIE',
    
    # Noms dans les chemins
    '/ainflue': '/iacherie',
    'ainflue_': 'iacherie_',
    'iacheries': 'iacherie',
    'IA Chéries': 'iaCherie',
    
    # Twitter/Social
    '@IA ChériesAI': '@iaCherieAI',
    '@iacheries': '@iacherie',
    
    # Usernames
    'iacheries_demo': 'iacherie_demo',
    'iacheries_official': 'iacherie_official',
    'iacheries_channel': 'iacherie_channel',
}

# Extensions de fichiers à traiter
EXTENSIONS = {
    '.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md', '.txt',
    '.sh', '.yml', '.yaml', '.env', '.dockerfile', '.toml', '.ini',
    '.sql', '.html', '.css', '.scss', '.vue', '.svelte'
}

# Fichiers et dossiers à exclure
EXCLUDE_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv',
    '.next', 'dist', 'build', '.cache', '.pytest_cache',
    'migration_backup', 'logs', 'tmp', 'cache', 'fingerprints'
}

EXCLUDE_FILES = {
    'rename_to_iacherie.py', 'migrate_to_iacherie.py'
}

def should_process_file(file_path: Path) -> bool:
    """Vérifie si le fichier doit être traité"""
    # Vérifier les dossiers exclus
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False
    
    # Vérifier les fichiers exclus
    if file_path.name in EXCLUDE_FILES:
        return False
    
    # Vérifier l'extension
    if file_path.suffix in EXTENSIONS or file_path.name.startswith('Dockerfile'):
        return True
    
    # Fichiers sans extension spécifiques
    if file_path.name in ['.env', '.env.local', '.env.production', '.env.development', '.env.staging', '.env.testing']:
        return True
    
    return False

def replace_in_content(content: str) -> tuple[str, int]:
    """Remplace les occurrences dans le contenu"""
    new_content = content
    count = 0
    
    for old, new in REPLACEMENTS.items():
        if old in new_content:
            occurrences = new_content.count(old)
            new_content = new_content.replace(old, new)
            count += occurrences
    
    return new_content, count

def process_file(file_path: Path) -> tuple[bool, int]:
    """Traite un fichier et retourne (modifié, nombre de remplacements)"""
    try:
        # Lire le fichier
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Ignorer les fichiers binaires
            return False, 0
        
        # Remplacer
        new_content, count = replace_in_content(content)
        
        # Écrire si modifié
        if count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, count
        
        return False, 0
    
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {file_path}: {e}")
        return False, 0

def main():
    """Point d'entrée principal"""
    print("🔄 Renommage de IA Chéries vers IA Chérie")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    total_files = 0
    total_modified = 0
    total_replacements = 0
    
    # Parcourir tous les fichiers
    for file_path in project_root.rglob('*'):
        if not file_path.is_file():
            continue
        
        if not should_process_file(file_path):
            continue
        
        total_files += 1
        modified, count = process_file(file_path)
        
        if modified:
            total_modified += 1
            total_replacements += count
            print(f"✅ {file_path.relative_to(project_root)}: {count} remplacements")
    
    print("=" * 60)
    print(f"📊 Résumé:")
    print(f"   • Fichiers analysés: {total_files}")
    print(f"   • Fichiers modifiés: {total_modified}")
    print(f"   • Remplacements totaux: {total_replacements}")
    print("=" * 60)
    print("✅ Renommage terminé avec succès!")
    print("\n💡 N'oubliez pas de:")
    print("   1. Redémarrer les serveurs (backend et frontend)")
    print("   2. Vider les caches (npm cache clean --force)")
    print("   3. Reconstruire les images Docker si nécessaire")

if __name__ == '__main__':
    main()
