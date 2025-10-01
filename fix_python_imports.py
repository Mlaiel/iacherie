#!/usr/bin/env python3
"""
🔧 CORRECTEUR D'IMPORTS PYTHON - IA CHÉRIE
==========================================

Script spécialisé pour corriger les imports Python après la migration.

Author: Fahed Mlaiel
Date: 1er Octobre 2025
"""

import os
import re
from pathlib import Path
from typing import List, Dict

# Mappings spécifiques aux imports Python
IMPORT_MAPPINGS = {
    # Classes TTS
    'AinfluencerTTS': 'IaCheriesTTS',
    'tts_generate_for_ainfluencer': 'tts_generate_for_iacheries',
    
    # Classes API externes
    'AinfluencerFreesoundAPI': 'IaCheriesFreesoundAPI',
    'AinfluencerYouTubeAPI': 'IaCheriesYouTubeAPI',
    'AinfluencerTwitterAPI': 'IaCheriesTwitterAPI',
    'AinfluencerRedditAPI': 'IaCheriesRedditAPI',
    'AinfluencerLibreTranslate': 'IaCheriesLibreTranslate',
    'AinfluencerTextRazor': 'IaCheriesTextRazor',
    
    # Classes d'authentification
    'AinfluencerAuthenticationOrchestrator': 'IaCheriesAuthenticationOrchestrator',
    
    # Classes Kubernetes
    'IAInfluencerInfrastructureManager': 'IACheriesInfrastructureManager',
    'IAInfluencerInfrastructureConfig': 'IACheriesInfrastructureConfig',
    'IAInfluencerLoggingSystem': 'IACheriesLoggingSystem',
    'IAInfluencerCICDOrchestrator': 'IACheriesCICDOrchestrator',
    'IAInfluencerNetworkDemo': 'IACheriesNetworkDemo',
    'IAInfluencerNetworkEnterpriseIntegration': 'IACheriesNetworkEnterpriseIntegration',
    'IAInfluencerPipelineSystem': 'IACheriesPipelineSystem',
    
    # Classes Workflow
    'AinfluencerWorkflowEngine': 'IaCheriesWorkflowEngine',
    
    # Variables et fonctions
    'ainfluencer_metadata': 'iacheries_metadata',
    'track_ainfluencer_auth_success': 'track_iacheries_auth_success',
}

def find_python_files(root_dir: str) -> List[Path]:
    """Trouve tous les fichiers Python"""
    python_files = []
    for file_path in Path(root_dir).rglob("*.py"):
        if file_path.is_file():
            # Exclure certains dossiers
            exclude_dirs = {'__pycache__', '.venv', 'venv', '.git', 'node_modules'}
            if not any(exclude_dir in str(file_path) for exclude_dir in exclude_dirs):
                python_files.append(file_path)
    return python_files

def fix_imports_in_file(file_path: Path) -> int:
    """Corrige les imports dans un fichier Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_count = 0
        
        # Corriger les imports directs
        for old_name, new_name in IMPORT_MAPPINGS.items():
            # Pattern pour "from module import OldClass"
            import_pattern = rf'\bfrom\s+([^\s]+)\s+import\s+([^,\n]*\b{re.escape(old_name)}\b[^,\n]*)'
            matches = re.findall(import_pattern, content)
            
            for match in matches:
                module_name, import_list = match
                new_import_list = import_list.replace(old_name, new_name)
                old_import = f"from {module_name} import {import_list}"
                new_import = f"from {module_name} import {new_import_list}"
                
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    fixes_count += 1
                    print(f"  🔧 Import corrigé: {old_import} → {new_import}")
            
            # Pattern pour "import module.OldClass"
            direct_import_pattern = rf'\bimport\s+([^\s]*\.{re.escape(old_name)})\b'
            matches = re.findall(direct_import_pattern, content)
            
            for match in matches:
                old_full_import = match
                new_full_import = old_full_import.replace(old_name, new_name)
                old_import_stmt = f"import {old_full_import}"
                new_import_stmt = f"import {new_full_import}"
                
                if old_import_stmt in content:
                    content = content.replace(old_import_stmt, new_import_stmt)
                    fixes_count += 1
                    print(f"  🔧 Import direct corrigé: {old_import_stmt} → {new_import_stmt}")
            
            # Corriger les utilisations dans le code
            if old_name in content:
                # Éviter de remplacer dans les commentaires et chaînes de caractères
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    # Ignorer les commentaires
                    if line.strip().startswith('#'):
                        continue
                    
                    # Ignorer les chaînes de caractères (approximation simple)
                    if ('"' in line and old_name in line.split('"')[1::2]) or \
                       ("'" in line and old_name in line.split("'")[1::2]):
                        continue
                    
                    # Remplacer seulement les occurrences de mots entiers
                    pattern = rf'\b{re.escape(old_name)}\b'
                    if re.search(pattern, line):
                        new_line = re.sub(pattern, new_name, line)
                        if new_line != line:
                            lines[i] = new_line
                            fixes_count += 1
                            print(f"  🔧 Utilisation corrigée: {old_name} → {new_name}")
                
                content = '\n'.join(lines)
        
        # Sauvegarder si des changements ont été effectués
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return fixes_count
        
        return 0
        
    except Exception as e:
        print(f"  ❌ Erreur lors du traitement de {file_path}: {e}")
        return 0

def main():
    """Fonction principale"""
    print("🔧 CORRECTEUR D'IMPORTS PYTHON - IA CHÉRIE")
    print("==========================================")
    print()
    
    root_dir = "/workspaces/iacherie"
    
    # Trouver tous les fichiers Python
    print("🔍 Recherche des fichiers Python...")
    python_files = find_python_files(root_dir)
    print(f"🐍 {len(python_files)} fichiers Python trouvés")
    print()
    
    # Traiter chaque fichier
    total_fixes = 0
    files_modified = 0
    
    for file_path in python_files:
        print(f"📝 Traitement: {file_path}")
        fixes = fix_imports_in_file(file_path)
        
        if fixes > 0:
            files_modified += 1
            total_fixes += fixes
            print(f"  ✨ {fixes} corrections effectuées")
        else:
            print(f"  ⏭️  Aucune correction nécessaire")
        print()
    
    # Résumé
    print("📊 RÉSUMÉ DES CORRECTIONS D'IMPORTS")
    print("===================================")
    print(f"🐍 Fichiers Python analysés: {len(python_files)}")
    print(f"✏️  Fichiers modifiés: {files_modified}")
    print(f"🔧 Total corrections: {total_fixes}")
    print()
    
    if files_modified > 0:
        print("✅ CORRECTION D'IMPORTS TERMINÉE!")
        print("Tous les imports Python ont été mis à jour pour IA Chéries")
    else:
        print("ℹ️  Aucune correction d'import nécessaire")

if __name__ == "__main__":
    main()