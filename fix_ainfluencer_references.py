#!/usr/bin/env python3
"""
🔧 CORRECTEUR POST-MIGRATION IA CHÉRIE
=====================================

Script pour corriger automatiquement toutes les références
"Ainfluencer" restantes après la migration vers "IA Chérie".

Author: Fahed Mlaiel
Date: 1er Octobre 2025
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, List

# Mappings de renommage détaillés
REPLACEMENTS = {
    # Classes et noms de modules
    'AinfluencerTTS': 'IaCheriesTTS',
    'AinfluencerFreesoundAPI': 'IaCheriesFreesoundAPI',
    'AinfluencerYouTubeAPI': 'IaCheriesYouTubeAPI',
    'AinfluencerTwitterAPI': 'IaCheriesTwitterAPI',
    'AinfluencerRedditAPI': 'IaCheriesRedditAPI',
    'AinfluencerLibreTranslate': 'IaCheriesLibreTranslate',
    'AinfluencerTextRazor': 'IaCheriesTextRazor',
    'AinfluencerAuthenticationOrchestrator': 'IaCheriesAuthenticationOrchestrator',
    'AinfluencerWorkflowEngine': 'IaCheriesWorkflowEngine',
    
    # Fonctions et variables
    'tts_generate_for_ainfluencer': 'tts_generate_for_iacheries',
    'track_ainfluencer_auth_success': 'track_iacheries_auth_success',
    'ainfluencer_metadata': 'iacheries_metadata',
    
    # Noms de projet et plateformes
    'Ainfluencer': 'IA Chéries',
    'AINFLUENCER': 'IA CHÉRIES',
    'ainfluencer': 'iacheries',
    'AInfluencer': 'IA Chéries',
    
    # URLs et chemins
    '/workspaces/Ainfluencer/': '/workspaces/iacherie/',
    'Ainfluencer-Platform': 'IA-Cheries-Platform',
    
    # Descriptions et commentaires
    'plateforme Ainfluencer': 'plateforme IA Chéries',
    'pour Ainfluencer': 'pour IA Chéries',
    'Moteur.*pour Ainfluencer': 'Moteur pour IA Chéries',
    
    # Noms de bases de données
    '"ainfluencer"': '"iacheries"',
    "'ainfluencer'": "'iacheries'",
    'database": "ainfluencer"': 'database": "iacheries"',
    
    # User agents et identifiants
    'Ainfluencer AI': 'IA Chéries AI',
    '@ainfluencer': '@iacheries',
    'ainfluencer_demo': 'iacheries_demo',
    'ainfluencer_official': 'iacheries_official',
    'ainfluencer_channel': 'iacheries_channel',
    
    # Fichiers et noms de fichiers
    'ainfluencer_': 'iacheries_',
    'Ainflue': 'IA Chéries',
    'AINFLUE': 'IA CHÉRIES',
    
    # Classes Kubernetes
    'IAInfluencer': 'IACheries',
    'IAInfluencerInfrastructureManager': 'IACheriesInfrastructureManager',
    'IAInfluencerInfrastructureConfig': 'IACheriesInfrastructureConfig',
    'IAInfluencerLoggingSystem': 'IACheriesLoggingSystem',
    'IAInfluencerCICDOrchestrator': 'IACheriesCICDOrchestrator',
    'IAInfluencerNetworkDemo': 'IACheriesNetworkDemo',
    'IAInfluencerNetworkEnterpriseIntegration': 'IACheriesNetworkEnterpriseIntegration',
    'IAInfluencerPipelineSystem': 'IACheriesPipelineSystem',
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
    'logs', 'tmp', 'cache', 'fingerprints'
}

EXCLUDE_FILES = {
    'fix_ainfluencer_references.py'
}

def find_files_to_process(root_dir: str) -> List[Path]:
    """Trouve tous les fichiers à traiter"""
    files_to_process = []
    
    for ext in EXTENSIONS:
        pattern = f"**/*{ext}"
        for file_path in Path(root_dir).glob(pattern):
            if file_path.is_file():
                # Vérifier les exclusions
                if any(exclude_dir in str(file_path) for exclude_dir in EXCLUDE_DIRS):
                    continue
                if file_path.name in EXCLUDE_FILES:
                    continue
                    
                files_to_process.append(file_path)
    
    return files_to_process

def process_file(file_path: Path) -> int:
    """Traite un fichier et retourne le nombre de remplacements effectués"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements_count = 0
        
        # Appliquer tous les remplacements
        for old_text, new_text in REPLACEMENTS.items():
            if old_text in content:
                # Remplacement simple pour la plupart des cas
                if not old_text.startswith('Moteur.*'):
                    new_content = content.replace(old_text, new_text)
                else:
                    # Remplacement par regex pour les patterns complexes
                    pattern = old_text
                    new_content = re.sub(pattern, new_text, content, flags=re.IGNORECASE)
                
                if new_content != content:
                    replacements_made = content.count(old_text)
                    replacements_count += replacements_made
                    content = new_content
                    print(f"  ✅ Remplacé '{old_text}' par '{new_text}' ({replacements_made} fois)")
        
        # Réécrire le fichier s'il y a eu des changements
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return replacements_count
        
        return 0
        
    except Exception as e:
        print(f"  ❌ Erreur lors du traitement de {file_path}: {e}")
        return 0

def main():
    """Fonction principale"""
    print("🔧 CORRECTEUR POST-MIGRATION IA CHÉRIE")
    print("=====================================")
    print()
    
    root_dir = "/workspaces/iacherie"
    
    # Trouver tous les fichiers à traiter
    print("🔍 Recherche des fichiers à traiter...")
    files_to_process = find_files_to_process(root_dir)
    print(f"📁 {len(files_to_process)} fichiers trouvés")
    print()
    
    # Traiter chaque fichier
    total_replacements = 0
    files_modified = 0
    
    for file_path in files_to_process:
        print(f"📝 Traitement: {file_path}")
        replacements = process_file(file_path)
        
        if replacements > 0:
            files_modified += 1
            total_replacements += replacements
            print(f"  ✨ {replacements} remplacements effectués")
        else:
            print(f"  ⏭️  Aucun changement nécessaire")
        print()
    
    # Résumé final
    print("📊 RÉSUMÉ DE LA CORRECTION")
    print("==========================")
    print(f"📁 Fichiers analysés: {len(files_to_process)}")
    print(f"✏️  Fichiers modifiés: {files_modified}")
    print(f"🔄 Total remplacements: {total_replacements}")
    print()
    
    if files_modified > 0:
        print("✅ CORRECTION TERMINÉE AVEC SUCCÈS!")
        print("Les références à 'Ainfluencer' ont été corrigées vers 'IA Chéries'")
    else:
        print("ℹ️  Aucune correction nécessaire - Migration déjà complète!")

if __name__ == "__main__":
    main()