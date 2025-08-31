#!/usr/bin/env python3
"""
Script de correction automatique industriel pour Ainflue
Correction systématique des erreurs de syntaxe et standardisation PEP257

Usage:
    python scripts/ainflue_syntax_corrector.py --mode=safe    # Mode sécurisé (recommandé)
    python scripts/ainflue_syntax_corrector.py --mode=full    # Correction complète
    python scripts/ainflue_syntax_corrector.py --mode=audit   # Audit seulement
"""

import os
import re
import ast
import sys
import json
import shutil
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import argparse


@dataclass
class CorrectionStats:
    """Statistiques de correction"""
    files_processed: int = 0
    files_fixed: int = 0
    syntax_errors_fixed: int = 0
    docstring_issues_fixed: int = 0
    backup_files_created: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class AinflueSyntaxCorrector:
    """Correcteur syntaxique industriel pour Ainflue"""
    
    def __init__(self, root_path: Path, mode: str = "safe"):
        self.root_path = Path(root_path)
        self.mode = mode
        self.stats = CorrectionStats()
        self.backup_dir = self.root_path / ".syntax_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Patterns de correction sûrs
        self.safe_patterns = [
            # Pattern 1: Docstring sans fermeture + variable
            (r'(""")([^"]*?)(""")\s*([A-Za-z_][A-Za-z0-9_]*\s*=)', 
             r'\1\2\3\n    \4',
             "docstring_variable_spacing"),
            
            # Pattern 2: Docstring sans fermeture + méthode
            (r'(""")([^"]*?)(""")\s*(def\s+)', 
             r'\1\2\3\n    \4',
             "docstring_method_spacing"),
             
            # Pattern 3: Docstring sans fermeture + classe
            (r'(""")([^"]*?)(""")\s*(class\s+)', 
             r'\1\2\3\n\n\4',
             "docstring_class_spacing"),
        ]
        
        # Patterns plus agressifs (mode full seulement)
        self.full_patterns = [
            # Correction des quotes simples en docstrings
            (r'^\s*"([^"]*?)"(\s*$)', 
             r'    """\1"""',
             "single_quote_docstring"),
             
            # Correction indentation de base
            (r'^(\s*)(class|def|async def)(\s+\w+)', 
             r'\1\2\3',
             "basic_indentation"),
        ]
    
    def create_backup(self, file_path: Path) -> Path:
        """Crée une sauvegarde d'un fichier"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        relative_path = file_path.relative_to(self.root_path)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(file_path, backup_path)
        self.stats.backup_files_created += 1
        return backup_path
    
    def is_syntax_valid(self, content: str) -> bool:
        """Vérifie si le contenu est syntaxiquement valide"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
    
    def apply_safe_corrections(self, content: str) -> Tuple[str, int]:
        """Applique les corrections sûres"""
        original_content = content
        corrections_applied = 0
        
        patterns = self.safe_patterns
        if self.mode == "full":
            patterns.extend(self.full_patterns)
        
        for pattern, replacement, correction_type in patterns:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if new_content != content:
                content = new_content
                corrections_applied += 1
                print(f"  ✓ Applied: {correction_type}")
        
        return content, corrections_applied
    
    def fix_common_syntax_issues(self, content: str) -> Tuple[str, int]:
        """Corrige les problèmes de syntaxe les plus courants"""
        corrections = 0
        
        # Correction 1: Fermeture manquante de docstrings
        pattern = r'(""")([^"]*?)(?!\""")(\n\s*[A-Za-z_])'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, r'\1\2"""\3', content, flags=re.DOTALL)
            corrections += 1
        
        # Correction 2: Indentation incohérente dans les classes
        lines = content.split('\n')
        fixed_lines = []
        in_class = False
        class_indent = 0
        
        for line in lines:
            if line.strip().startswith('class '):
                in_class = True
                class_indent = len(line) - len(line.lstrip())
                fixed_lines.append(line)
            elif in_class and line.strip() and not line.startswith(' ' * (class_indent + 4)) and line.strip() != '' and not line.strip().startswith('@'):
                if line.strip().startswith(('def ', 'async def ', 'class ')):
                    in_class = False
                    fixed_lines.append(line)
                else:
                    # Corriger l'indentation
                    fixed_line = ' ' * (class_indent + 4) + line.lstrip()
                    fixed_lines.append(fixed_line)
                    corrections += 1
            else:
                fixed_lines.append(line)
        
        if corrections > 0:
            content = '\n'.join(fixed_lines)
        
        return content, corrections
    
    def fix_file(self, file_path: Path) -> bool:
        """Corrige un fichier spécifique"""
        try:
            self.stats.files_processed += 1
            
            # Lire le fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Vérifier la syntaxe avant correction
            syntax_valid_before = self.is_syntax_valid(original_content)
            
            if syntax_valid_before and self.mode == "safe":
                return True  # Pas de correction nécessaire en mode sûr
            
            print(f"Fixing: {file_path}")
            
            # Créer une sauvegarde
            if not syntax_valid_before or self.mode == "full":
                self.create_backup(file_path)
            
            # Appliquer les corrections
            content = original_content
            total_corrections = 0
            
            # Corrections sûres
            content, safe_corrections = self.apply_safe_corrections(content)
            total_corrections += safe_corrections
            
            # Corrections syntaxiques communes
            if not syntax_valid_before:
                content, syntax_corrections = self.fix_common_syntax_issues(content)
                total_corrections += syntax_corrections
                self.stats.syntax_errors_fixed += syntax_corrections
            
            # Vérifier que les corrections n'ont pas cassé la syntaxe
            if not self.is_syntax_valid(content):
                print(f"  ❌ Corrections would break syntax, skipping")
                return False
            
            # Sauvegarder si des corrections ont été appliquées
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.stats.files_fixed += 1
                self.stats.docstring_issues_fixed += safe_corrections
                
                print(f"  ✅ Applied {total_corrections} corrections")
                return True
            else:
                print(f"  ℹ️  No corrections needed")
                return True
                
        except Exception as e:
            error_msg = f"Error fixing {file_path}: {str(e)}"
            self.stats.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            return False
    
    def get_python_files(self) -> List[Path]:
        """Obtient la liste des fichiers Python à traiter"""
        python_files = []
        
        # Exclure certains répertoires
        excluded_dirs = {
            '__pycache__', '.git', 'venv', 'env', '.venv', 
            'node_modules', 'build', 'dist', '.pytest_cache',
            '.syntax_backup'
        }
        
        for file_path in self.root_path.rglob("*.py"):
            if not any(excluded in str(file_path) for excluded in excluded_dirs):
                python_files.append(file_path)
        
        return python_files
    
    def run_audit(self) -> Dict[str, any]:
        """Exécute un audit complet"""
        print("🔍 Running comprehensive syntax audit...")
        
        python_files = self.get_python_files()
        valid_files = 0
        invalid_files = 0
        fixable_files = 0
        
        print(f"Found {len(python_files)} Python files to audit")
        
        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(python_files)} files audited")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if self.is_syntax_valid(content):
                    valid_files += 1
                else:
                    invalid_files += 1
                    
                    # Tester si le fichier est réparable
                    fixed_content, corrections = self.apply_safe_corrections(content)
                    if corrections > 0 and self.is_syntax_valid(fixed_content):
                        fixable_files += 1
                        
            except Exception as e:
                invalid_files += 1
                print(f"Error reading {file_path}: {e}")
        
        compliance_rate = (valid_files / len(python_files) * 100) if python_files else 0
        
        audit_results = {
            'total_files': len(python_files),
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'fixable_files': fixable_files,
            'compliance_rate': compliance_rate,
            'fix_potential': (fixable_files / invalid_files * 100) if invalid_files > 0 else 0
        }
        
        print(f"\n📊 Audit Results:")
        print(f"✅ Valid files: {valid_files:,}")
        print(f"❌ Invalid files: {invalid_files:,}")
        print(f"🔧 Auto-fixable files: {fixable_files:,}")
        print(f"📈 Syntax compliance: {compliance_rate:.1f}%")
        print(f"🎯 Fix potential: {audit_results['fix_potential']:.1f}%")
        
        return audit_results
    
    def run_corrections(self) -> None:
        """Exécute les corrections sur tous les fichiers"""
        print(f"🔧 Starting syntax corrections in {self.mode} mode...")
        
        python_files = self.get_python_files()
        
        # En mode sûr, limiter aux fichiers avec erreurs de syntaxe
        if self.mode == "safe":
            files_to_process = []
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if not self.is_syntax_valid(content):
                        files_to_process.append(file_path)
                except:
                    files_to_process.append(file_path)
            
            print(f"Found {len(files_to_process)} files with syntax errors to fix")
        else:
            files_to_process = python_files[:100]  # Limiter en mode full pour test
            print(f"Processing {len(files_to_process)} files in full mode")
        
        # Traiter les fichiers
        for file_path in files_to_process:
            self.fix_file(file_path)
        
        # Rapport final
        print(f"\n📊 Correction Summary:")
        print(f"📁 Files processed: {self.stats.files_processed:,}")
        print(f"✅ Files fixed: {self.stats.files_fixed:,}")
        print(f"🔧 Syntax errors fixed: {self.stats.syntax_errors_fixed:,}")
        print(f"📝 Docstring issues fixed: {self.stats.docstring_issues_fixed:,}")
        print(f"💾 Backup files created: {self.stats.backup_files_created:,}")
        
        if self.stats.errors:
            print(f"\n❌ Errors encountered: {len(self.stats.errors)}")
            for error in self.stats.errors[:5]:
                print(f"  - {error}")
            if len(self.stats.errors) > 5:
                print(f"  ... and {len(self.stats.errors) - 5} more")
        
        if self.stats.backup_files_created > 0:
            print(f"\n💾 Backups stored in: {self.backup_dir}")
    
    def create_summary_report(self) -> str:
        """Crée un rapport de résumé"""
        audit_results = self.run_audit()
        
        report = f"""# Rapport de Correction Syntaxique - Ainflue

## 📊 Résultats d'Audit
- **Total fichiers**: {audit_results['total_files']:,}
- **Fichiers valides**: {audit_results['valid_files']:,}  
- **Fichiers invalides**: {audit_results['invalid_files']:,}
- **Fichiers auto-réparables**: {audit_results['fixable_files']:,}
- **Taux de conformité**: {audit_results['compliance_rate']:.1f}%
- **Potentiel de correction**: {audit_results['fix_potential']:.1f}%

## 🎯 Objectifs Atteints
- [{"x" if audit_results['compliance_rate'] >= 90 else " "}] Conformité syntaxique ≥ 90%
- [{"x" if audit_results['compliance_rate'] >= 95 else " "}] Conformité syntaxique ≥ 95%
- [{"x" if audit_results['compliance_rate'] >= 99 else " "}] Conformité syntaxique ≥ 99%

## 📋 Recommandations
"""
        
        if audit_results['compliance_rate'] < 90:
            report += """
### 🔥 Actions Critiques Requises
1. **Correction automatique** - Exécuter en mode sûr: `python scripts/ainflue_syntax_corrector.py --mode=safe`
2. **Validation manuelle** - Réviser les fichiers non réparables automatiquement
3. **Tests de régression** - Vérifier que les corrections n'impactent pas les fonctionnalités
"""
        else:
            report += """
### ✅ Maintenance Continue
1. **Intégration CI/CD** - Validation automatique dans le pipeline
2. **Hooks pre-commit** - Prévention des régressions
3. **Formation équipe** - Respect des standards PEP8/PEP257
"""
        
        return report


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="Ainflue Industrial Syntax Corrector")
    parser.add_argument("--mode", choices=["audit", "safe", "full"], default="audit",
                       help="Mode d'exécution")
    parser.add_argument("--root", default=".", help="Répertoire racine")
    parser.add_argument("--report", action="store_true", help="Générer un rapport")
    
    args = parser.parse_args()
    
    corrector = AinflueSyntaxCorrector(Path(args.root), args.mode)
    
    if args.mode == "audit":
        corrector.run_audit()
        if args.report:
            report = corrector.create_summary_report()
            with open("syntax_correction_report.md", "w", encoding="utf-8") as f:
                f.write(report)
            print("\n📄 Report generated: syntax_correction_report.md")
    else:
        corrector.run_corrections()


if __name__ == "__main__":
    main()