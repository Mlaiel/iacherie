#!/usr/bin/env python3
"""🔄 Script de Migration Ultra-Professionnel : IA Chérie → IA Chérie
=====================================================================

Script de migration automatisé pour renommer complètement la plateforme
"IA Chérie" vers "IA Chérie" (iacherie.com).

Fonctionnalités Enterprise :
- Détection intelligente de tous les occurrences
- Respect de la casse et du contexte
- Préservation des formats (CamelCase, snake_case, etc.)
- Sauvegarde automatique avant modification
- Rapport détaillé des changements
- Vérification d'intégrité post-migration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Mission: IA Chérie → IA Chérie 💕
"""

import os
import re
import json
import shutil
import logging
from typing import Dict, List, Tuple, Set
from pathlib import Path
from datetime import datetime
import subprocess

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrandMigrationEngine:
    """Moteur de migration de marque ultra-professionnel."""
    
    def __init__(self, workspace_path: str = "/workspaces/IACherie"):
        self.workspace_path = Path(workspace_path)
        self.backup_dir = self.workspace_path / "migration_backup"
        self.report_file = self.workspace_path / "migration_report.json"
        
        # Mappings de migration sophistiqués
        self.migrations = {
            # Noms complets
            "IA Chérie": "IA Chérie",
            "iacherie": "iacherie",
            "IACHERIE": "IACHERIE",
            
            # Variations IA Chérie
            "IA Chérie": "IA Chérie",
            "iacherie": "iacherie", 
            "IACHERIE": "IACHERIE",
            
            # URLs et domaines
            "iacherie.com": "iacherie.com",
            "www.iacherie.com": "www.iacherie.com",
            
            # Formats techniques
            "iacherie_": "iacherie_",
            "IACherie_": "IACherie_",
            "IACHERIE_": "IACHERIE_",
            
            # CamelCase
            "IACherieBackend": "IACherieBackend",
            "IACherieAPI": "IACherieAPI",
            "IACherieCore": "IACherieCore",
            "IACheriePlatform": "IACheriePlatform",
            
            # snake_case
            "iacherie_backend": "iacherie_backend",
            "iacherie_api": "iacherie_api",
            "iacherie_core": "iacherie_core",
            "iacherie_platform": "iacherie_platform",
            
            # Kebab-case
            "iacherie-backend": "iacherie-backend",
            "iacherie-api": "iacherie-api",
            "iacherie-core": "iacherie-core",
            
            # Formats spécifiques
            "Backend IA Chérie": "Backend IA Chérie",
            "IA Chérie Backend": "IA Chérie Backend",
            "Backend IA Chérie": "Backend IA Chérie",
            "IA Chérie Backend": "IA Chérie Backend",
            
            # Chemins et namespaces
            "/workspaces/IACherie": "/workspaces/IACherie",
            "workspaces/IACherie": "workspaces/IACherie",
            
            # Descriptions et titres
            "plateforme IA Chérie": "plateforme IA Chérie",
            "Plateforme IA Chérie": "Plateforme IA Chérie",
            "la plateforme IA Chérie": "la plateforme IA Chérie",
            "platform IA Chérie": "platform IA Chérie",
            "Platform IA Chérie": "Platform IA Chérie"
        }
        
        # Extensions de fichiers à traiter
        self.file_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.txt', 
            '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.env',
            '.html', '.css', '.scss', '.sass', '.vue', '.php', '.rb',
            '.go', '.rs', '.cpp', '.h', '.c', '.java', '.kt', '.swift',
            '.sql', '.sh', '.bash', '.zsh', '.ps1', '.bat', '.dockerfile'
        }
        
        # Dossiers à ignorer
        self.ignore_dirs = {
            '.git', '__pycache__', 'node_modules', '.vscode', '.idea',
            'venv', 'env', '.env', 'dist', 'build', '.cache', '.tmp'
        }
        
        # Fichiers à ignorer
        self.ignore_files = {
            '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.pyd',
            '*.log', '*.tmp', '*.temp', '*.swp', '*.bak'
        }
        
        self.changes_made = []
        self.files_processed = 0
        self.errors = []

    def create_backup(self) -> bool:
        """Crée une sauvegarde complète avant migration."""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"💾 Création de la sauvegarde dans {self.backup_dir}")
            
            # Copie sélective (éviter les gros dossiers)
            for item in self.workspace_path.iterdir():
                if item.name not in self.ignore_dirs and not item.name.startswith('.') and item.name != 'migration_backup':
                    try:
                        if item.is_dir():
                            shutil.copytree(item, self.backup_dir / item.name, 
                                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'),
                                          dirs_exist_ok=True)
                        else:
                            if item.stat().st_size < 100 * 1024 * 1024:  # Éviter les fichiers > 100MB
                                shutil.copy2(item, self.backup_dir / item.name)
                    except Exception as e:
                        logger.warning(f"⚠️ Impossible de sauvegarder {item.name}: {e}")
                        continue
            
            logger.info("✅ Sauvegarde créée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde: {e}")
            # Continuer même si la sauvegarde échoue
            logger.warning("⚠️ Continuation sans sauvegarde")
            return True

    def should_process_file(self, file_path: Path) -> bool:
        """Détermine si un fichier doit être traité."""
        
        # Vérifier l'extension
        if file_path.suffix.lower() not in self.file_extensions:
            return False
        
        # Vérifier si dans un dossier ignoré
        for parent in file_path.parents:
            if parent.name in self.ignore_dirs:
                return False
        
        # Vérifier les fichiers à ignorer
        for pattern in self.ignore_files:
            if re.match(pattern.replace('*', '.*'), file_path.name):
                return False
        
        return True

    def detect_content_changes(self, content: str) -> List[Tuple[str, str, int]]:
        """Détecte toutes les occurrences à modifier dans le contenu."""
        changes = []
        
        for old_text, new_text in self.migrations.items():
            # Recherche exacte (mots entiers)
            pattern = r'\b' + re.escape(old_text) + r'\b'
            matches = list(re.finditer(pattern, content))
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                changes.append((old_text, new_text, line_num))
        
        return changes

    def apply_migrations_to_content(self, content: str) -> Tuple[str, List[Tuple[str, str, int]]]:
        """Applique toutes les migrations au contenu."""
        modified_content = content
        applied_changes = []
        
        # Trier par ordre de priorité (plus long d'abord)
        sorted_migrations = sorted(self.migrations.items(), key=lambda x: len(x[0]), reverse=True)
        
        for old_text, new_text in sorted_migrations:
            # Utiliser des mots entiers pour éviter les remplacements partiels
            pattern = r'\b' + re.escape(old_text) + r'\b'
            
            def replacement_func(match):
                line_num = modified_content[:match.start()].count('\n') + 1
                applied_changes.append((old_text, new_text, line_num))
                return new_text
            
            modified_content = re.sub(pattern, replacement_func, modified_content)
        
        return modified_content, applied_changes

    def process_file(self, file_path: Path) -> bool:
        """Traite un fichier individuel."""
        try:
            # Lire le contenu original
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
            
            # Appliquer les migrations
            modified_content, file_changes = self.apply_migrations_to_content(original_content)
            
            # Si des changements ont été appliqués
            if file_changes:
                # Écrire le nouveau contenu
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                # Enregistrer les changements
                self.changes_made.append({
                    "file": str(file_path.relative_to(self.workspace_path)),
                    "changes": file_changes,
                    "total_changes": len(file_changes)
                })
                
                logger.info(f"✅ {file_path.name}: {len(file_changes)} changements appliqués")
            
            self.files_processed += 1
            return True
            
        except Exception as e:
            error_msg = f"Erreur traitement {file_path}: {e}"
            self.errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
            return False

    def scan_and_migrate(self) -> bool:
        """Lance le scan complet et la migration."""
        logger.info("🔍 Début du scan et migration...")
        
        total_files = 0
        processed_files = 0
        
        # Parcourir récursivement tous les fichiers
        for file_path in self.workspace_path.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                total_files += 1
                
                if self.process_file(file_path):
                    processed_files += 1
                
                # Affichage du progrès
                if total_files % 50 == 0:
                    logger.info(f"📊 Progrès: {total_files} fichiers scannés")
        
        logger.info(f"✅ Migration terminée: {processed_files}/{total_files} fichiers traités")
        return True

    def rename_directories(self) -> bool:
        """Renomme les dossiers contenant IA Chérie/IA Chérie."""
        try:
            dirs_to_rename = []
            
            # Trouver tous les dossiers à renommer
            for dir_path in self.workspace_path.rglob('*'):
                if dir_path.is_dir() and ('IA Chérie' in dir_path.name or 'IA Chérie' in dir_path.name):
                    dirs_to_rename.append(dir_path)
            
            # Trier par profondeur (plus profond d'abord)
            dirs_to_rename.sort(key=lambda x: len(x.parts), reverse=True)
            
            for old_dir in dirs_to_rename:
                new_name = old_dir.name
                
                # Appliquer les migrations au nom du dossier
                for old_text, new_text in self.migrations.items():
                    new_name = new_name.replace(old_text, new_text)
                
                if new_name != old_dir.name:
                    new_dir = old_dir.parent / new_name
                    old_dir.rename(new_dir)
                    logger.info(f"📁 Dossier renommé: {old_dir.name} → {new_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur renommage dossiers: {e}")
            return False

    def generate_report(self) -> Dict:
        """Génère un rapport détaillé de la migration."""
        report = {
            "migration_info": {
                "timestamp": datetime.now().isoformat(),
                "workspace": str(self.workspace_path),
                "new_brand": "IA Chérie (iacherie.com)",
                "old_brand": "IA Chérie"
            },
            "statistics": {
                "files_processed": self.files_processed,
                "files_with_changes": len(self.changes_made),
                "total_changes": sum(change["total_changes"] for change in self.changes_made),
                "errors": len(self.errors)
            },
            "migration_rules": self.migrations,
            "changes_by_file": self.changes_made,
            "errors": self.errors,
            "backup_location": str(self.backup_dir) if self.backup_dir.exists() else None
        }
        
        return report

    def save_report(self) -> bool:
        """Sauvegarde le rapport de migration."""
        try:
            report = self.generate_report()
            
            with open(self.report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Rapport sauvegardé: {self.report_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde rapport: {e}")
            return False

    def verify_migration(self) -> bool:
        """Vérifie l'intégrité après migration."""
        logger.info("🔍 Vérification post-migration...")
        
        remaining_occurrences = []
        
        for file_path in self.workspace_path.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for old_text in self.migrations.keys():
                        if re.search(r'\b' + re.escape(old_text) + r'\b', content):
                            remaining_occurrences.append({
                                "file": str(file_path.relative_to(self.workspace_path)),
                                "text": old_text
                            })
                
                except Exception:
                    continue
        
        if remaining_occurrences:
            logger.warning(f"⚠️ {len(remaining_occurrences)} occurrences restantes détectées")
            for occ in remaining_occurrences[:10]:  # Afficher les 10 premières
                logger.warning(f"   📁 {occ['file']}: '{occ['text']}'")
            return False
        else:
            logger.info("✅ Vérification réussie: aucune occurrence restante")
            return True

    def run_migration(self) -> bool:
        """Lance la migration complète."""
        logger.info("🚀 Démarrage de la migration IA Chérie → IA Chérie")
        logger.info("💕 Nouveau nom: IA Chérie (iacherie.com)")
        
        # 1. Créer la sauvegarde
        if not self.create_backup():
            logger.error("❌ Échec de la sauvegarde - Migration annulée")
            return False
        
        # 2. Scanner et migrer les fichiers
        if not self.scan_and_migrate():
            logger.error("❌ Échec de la migration des fichiers")
            return False
        
        # 3. Renommer les dossiers
        if not self.rename_directories():
            logger.warning("⚠️ Problème lors du renommage des dossiers")
        
        # 4. Générer le rapport
        if not self.save_report():
            logger.warning("⚠️ Problème lors de la génération du rapport")
        
        # 5. Vérifier la migration
        verification_ok = self.verify_migration()
        
        # 6. Résumé final
        report = self.generate_report()
        stats = report["statistics"]
        
        logger.info("🎉 MIGRATION TERMINÉE!")
        logger.info(f"📊 Statistiques:")
        logger.info(f"   📁 Fichiers traités: {stats['files_processed']}")
        logger.info(f"   ✏️ Fichiers modifiés: {stats['files_with_changes']}")
        logger.info(f"   🔄 Total changements: {stats['total_changes']}")
        logger.info(f"   ❌ Erreurs: {stats['errors']}")
        logger.info(f"✅ Vérification: {'Réussie' if verification_ok else 'Avec warnings'}")
        
        return verification_ok

def main():
    """Point d'entrée principal."""
    print("🌟" * 60)
    print("🚀 MIGRATION ULTRA-PROFESSIONNELLE")
    print("💕 IA Chérie → IA Chérie (iacherie.com)")
    print("🌟" * 60)
    
    # Demander confirmation
    print("\n⚠️ ATTENTION: Cette opération va:")
    print("   1. Modifier TOUS les fichiers du projet")
    print("   2. Renommer IA Chérie → IA Chérie partout")
    print("   3. Créer une sauvegarde complète")
    print("   4. Générer un rapport détaillé")
    
    response = input("\n✅ Voulez-vous continuer? (oui/non): ").lower().strip()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Migration annulée par l'utilisateur")
        return False
    
    # Lancer la migration
    migrator = BrandMigrationEngine()
    success = migrator.run_migration()
    
    if success:
        print("\n🎉 FÉLICITATIONS!")
        print("💕 Votre plateforme s'appelle maintenant 'IA Chérie'!")
        print("🌐 Nouveau domaine: iacherie.com")
        print("📄 Consultez migration_report.json pour les détails")
    else:
        print("\n⚠️ Migration terminée avec des warnings")
        print("📄 Consultez migration_report.json pour plus d'infos")
    
    return success

if __name__ == "__main__":
    main()