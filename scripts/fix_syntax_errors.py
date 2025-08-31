#!/usr/bin/env python3
"""
Script automatisé pour corriger les erreurs de syntaxe systématiques
Projet Ainflue - Infrastructure Industrielle
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse


class SyntaxErrorFixer:
    """Correcteur d'erreurs de syntaxe automatisé"""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.fixed_files: List[Path] = []
        self.errors: List[str] = []
        self.syntax_patterns = [
            # Pattern principal: docstring sans fermeture suivie de code
            (r'"""([^"]*?)"""\s*([A-Z_][A-Z0-9_]*\s*=)', r'"""\1"""\n    \2'),
            (r"'''([^']*?)'''\s*([A-Z_][A-Z0-9_]*\s*=)", r"'''\1'''\n    \2"),
            
            # Docstring suivie directement par une définition de classe
            (r'"""([^"]*?)"""\s*(class\s+\w+)', r'"""\1"""\n\n\2'),
            (r"'''([^']*?)'''\s*(class\s+\w+)", r"'''\1'''\n\n\2"),
            
            # Docstring suivie directement par une définition de fonction
            (r'"""([^"]*?)"""\s*(def\s+\w+)', r'"""\1"""\n    \2'),
            (r"'''([^']*?)'''\s*(def\s+\w+)", r"'''\1'''\n    \2"),
            
            # Docstring suivie directement par une assignation de variable
            (r'"""([^"]*?)"""\s*(self\.\w+\s*=)', r'"""\1"""\n        \2'),
            (r"'''([^']*?)'''\s*(self\.\w+\s*=)", r"'''\1'''\n        \2"),
            
            # Autres patterns courrants
            (r'"""([^"]*?)"""\s*(@\w+)', r'"""\1"""\n    \2'),
            (r"'''([^']*?)'''\s*(@\w+)", r"'''\1'''\n    \2"),
        ]
        
    def scan_python_files(self) -> List[Path]:
        """Scan pour tous les fichiers Python"""
        python_files = []
        for file_path in self.root_path.rglob("*.py"):
            if not any(excluded in str(file_path) for excluded in [
                '__pycache__', '.git', 'venv', 'env', '.venv', 
                'node_modules', 'build', 'dist', '.pytest_cache'
            ]):
                python_files.append(file_path)
        return python_files
    
    def check_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Vérifie la syntaxe d'un fichier Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    def fix_docstring_patterns(self, content: str) -> Tuple[str, bool]:
        """Corrige les patterns de docstrings problématiques"""
        original_content = content
        fixed = False
        
        for pattern, replacement in self.syntax_patterns:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            if new_content != content:
                content = new_content
                fixed = True
        
        return content, fixed
    
    def fix_file(self, file_path: Path) -> bool:
        """Corrige un fichier spécifique"""
        try:
            # Lire le fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Vérifier la syntaxe avant correction
            is_valid_before, error_before = self.check_syntax(file_path)
            
            if is_valid_before:
                return True  # Pas besoin de correction
            
            # Appliquer les corrections
            fixed_content, was_fixed = self.fix_docstring_patterns(original_content)
            
            if not was_fixed:
                self.errors.append(f"{file_path}: No patterns matched for syntax error")
                return False
            
            # Vérifier que la correction a résolu le problème
            temp_file = file_path.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            is_valid_after, error_after = self.check_syntax(temp_file)
            
            if is_valid_after:
                # Sauvegarder le fichier corrigé
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                temp_file.unlink()
                self.fixed_files.append(file_path)
                return True
            else:
                temp_file.unlink()
                self.errors.append(f"{file_path}: Fix didn't resolve syntax error: {error_after}")
                return False
                
        except Exception as e:
            self.errors.append(f"{file_path}: Exception during fix: {str(e)}")
            return False
    
    def audit_repository(self) -> Dict[str, List[Path]]:
        """Effectue un audit complet du repository"""
        print("🔍 Scanning Python files...")
        python_files = self.scan_python_files()
        print(f"Found {len(python_files)} Python files")
        
        valid_files = []
        invalid_files = []
        
        print("🧪 Checking syntax for all files...")
        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(python_files)} files checked")
            
            is_valid, error = self.check_syntax(file_path)
            if is_valid:
                valid_files.append(file_path)
            else:
                invalid_files.append(file_path)
                print(f"❌ {file_path}: {error}")
        
        return {
            'valid': valid_files,
            'invalid': invalid_files,
            'total': python_files
        }
    
    def fix_repository(self) -> None:
        """Corrige tous les fichiers du repository"""
        audit_results = self.audit_repository()
        invalid_files = audit_results['invalid']
        
        if not invalid_files:
            print("✅ No syntax errors found!")
            return
        
        print(f"\n🔧 Fixing {len(invalid_files)} files with syntax errors...")
        
        for file_path in invalid_files:
            print(f"Fixing: {file_path}")
            success = self.fix_file(file_path)
            if success:
                print(f"  ✅ Fixed successfully")
            else:
                print(f"  ❌ Could not fix automatically")
        
        # Rapport final
        print(f"\n📊 Final Report:")
        print(f"✅ Files fixed: {len(self.fixed_files)}")
        print(f"❌ Files with errors: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ Remaining errors:")
            for error in self.errors[:10]:  # Afficher seulement les 10 premières
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
    
    def generate_report(self) -> str:
        """Génère un rapport détaillé"""
        audit_results = self.audit_repository()
        
        report = f"""
# Rapport d'Audit Syntaxique - Projet Ainflue

## 📊 Statistiques Globales
- **Total fichiers Python**: {len(audit_results['total'])}
- **Fichiers valides**: {len(audit_results['valid'])}
- **Fichiers avec erreurs**: {len(audit_results['invalid'])}
- **Taux de validité**: {len(audit_results['valid'])/len(audit_results['total'])*100:.1f}%

## ❌ Fichiers avec Erreurs de Syntaxe
"""
        
        for file_path in audit_results['invalid']:
            is_valid, error = self.check_syntax(file_path)
            report += f"- `{file_path}`: {error}\n"
        
        return report


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="Fix Python syntax errors in Ainflue repository")
    parser.add_argument("--audit", action="store_true", help="Audit only, don't fix")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--root", default=".", help="Repository root path")
    
    args = parser.parse_args()
    
    fixer = SyntaxErrorFixer(Path(args.root))
    
    if args.report:
        report = fixer.generate_report()
        with open("syntax_audit_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("📄 Report generated: syntax_audit_report.md")
    elif args.audit:
        fixer.audit_repository()
    else:
        fixer.fix_repository()


if __name__ == "__main__":
    main()