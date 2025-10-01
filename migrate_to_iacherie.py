#!/usr/bin/env python3
"""🚀 MIGRATION DIRECTE : IA Chérie → IA Chérie 💕"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def migrate_iacheries_to_iacherie():
    """Migration directe et professionnelle."""
    
    print("🌟" * 60)
    print("🚀 MIGRATION AUTOMATIQUE")
    print("💕 IA Chérie → IA Chérie (iacherie.com)")
    print("🌟" * 60)
    
    workspace = Path("/workspaces/IACherie")
    
    # Mappings de migration
    migrations = {
        "IA Chérie": "IA Chérie",
        "iacherie": "iacherie", 
        "IACHERIE": "IACHERIE",
        "IA Chérie": "IA Chérie",
        "iacherie": "iacherie",
        "IACHERIE": "IACHERIE",
        "iacherie.com": "iacherie.com",
        "www.iacherie.com": "www.iacherie.com",
        "IACherieBackend": "IACherieBackend",
        "IACherieAPI": "IACherieAPI", 
        "IACherieCore": "IACherieCore",
        "IACheriePlatform": "IACheriePlatform",
        "iacherie_backend": "iacherie_backend",
        "iacherie_api": "iacherie_api",
        "iacherie_core": "iacherie_core",
        "iacherie_platform": "iacherie_platform",
        "iacherie-backend": "iacherie-backend",
        "iacherie-api": "iacherie-api",
        "iacherie-core": "iacherie-core",
        "Backend IA Chérie": "Backend IA Chérie",
        "IA Chérie Backend": "IA Chérie Backend",
        "Backend IA Chérie": "Backend IA Chérie",
        "IA Chérie Backend": "IA Chérie Backend",
        "plateforme IA Chérie": "plateforme IA Chérie",
        "Plateforme IA Chérie": "Plateforme IA Chérie",
        "la plateforme IA Chérie": "la plateforme IA Chérie",
        "platform IA Chérie": "platform IA Chérie",
        "Platform IA Chérie": "Platform IA Chérie",
        "workspaces/IACherie": "workspaces/IACherie",
        "/workspaces/IACherie": "/workspaces/IACherie"
    }
    
    # Extensions à traiter
    extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.txt',
        '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.env',
        '.html', '.css', '.scss', '.sass', '.vue', '.php', '.rb',
        '.go', '.rs', '.cpp', '.h', '.c', '.java', '.kt', '.swift',
        '.sql', '.sh', '.bash', '.zsh', '.dockerfile'
    }
    
    # Dossiers à ignorer
    ignore_dirs = {
        '.git', '__pycache__', 'node_modules', '.vscode', '.idea',
        'venv', 'env', '.env', 'dist', 'build', '.cache', '.tmp',
        'migration_backup'
    }
    
    changes_made = []
    files_processed = 0
    
    print("🔍 Scan en cours...")
    
    # Traiter tous les fichiers
    for file_path in workspace.rglob('*'):
        if not file_path.is_file():
            continue
            
        # Vérifier extension
        if file_path.suffix.lower() not in extensions:
            continue
            
        # Vérifier si dans dossier ignoré
        skip = False
        for parent in file_path.parents:
            if parent.name in ignore_dirs:
                skip = True
                break
        if skip:
            continue
            
        try:
            # Lire le fichier
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            file_changes = []
            
            # Appliquer toutes les migrations
            for old_text, new_text in migrations.items():
                if old_text in content:
                    content = content.replace(old_text, new_text)
                    file_changes.append(f"{old_text} → {new_text}")
            
            # Si changements, sauvegarder
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                changes_made.append({
                    "file": str(file_path.relative_to(workspace)),
                    "changes": file_changes
                })
                
                print(f"✅ {file_path.name}: {len(file_changes)} changements")
            
            files_processed += 1
            
            # Affichage du progrès
            if files_processed % 100 == 0:
                print(f"📊 {files_processed} fichiers traités...")
                
        except Exception as e:
            print(f"❌ Erreur {file_path.name}: {e}")
            continue
    
    # Générer le rapport
    report = {
        "migration_info": {
            "timestamp": datetime.now().isoformat(),
            "new_brand": "IA Chérie (iacherie.com)",
            "old_brand": "IA Chérie"
        },
        "statistics": {
            "files_processed": files_processed,
            "files_changed": len(changes_made),
            "total_changes": sum(len(change["changes"]) for change in changes_made)
        },
        "changes_by_file": changes_made
    }
    
    # Sauvegarder le rapport
    with open(workspace / "migration_report_iacherie.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Résumé final
    print("\n🎉 MIGRATION TERMINÉE!")
    print(f"📊 Statistiques:")
    print(f"   📁 Fichiers traités: {report['statistics']['files_processed']}")
    print(f"   ✏️ Fichiers modifiés: {report['statistics']['files_changed']}")
    print(f"   🔄 Total changements: {report['statistics']['total_changes']}")
    print("\n💕 Votre plateforme s'appelle maintenant 'IA Chérie'!")
    print("🌐 Nouveau domaine: iacherie.com")
    print("📄 Rapport détaillé: migration_report_iacherie.json")
    
    return True

if __name__ == "__main__":
    migrate_iacheries_to_iacherie()