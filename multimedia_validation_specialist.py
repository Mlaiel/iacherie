#!/usr/bin/env python3
"""
DOSSIER MULTIMEDIA/ - Validator Spécialisé
==========================================

Validateur spécialisé pour tous les fichiers du dossier multimedia/
selon les exigences du cahier des charges:

POUR CHAQUE FICHIER PYTHON:
✅ Le fichier existe
✅ Import sans erreur : python -c "import nomfichier"
✅ Syntaxe correcte
✅ Fonctions/classes définies
✅ Pas d'erreurs dans VS Code

POUR CHAQUE DOSSIER:
✅ Contient __init__.py
✅ Tous les sous-fichiers importables
✅ Structure cohérente
✅ Pas de fichiers corrompus

VALIDATION FINALE - CHAQUE MODULE EST FONCTIONNEL QUAND:
✅ Import sans erreur
✅ Toutes les fonctions définies
✅ Intégration avec autres modules OK
✅ Aucune erreur dans les logs

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import os
import sys
import ast
import importlib
import subprocess
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FileValidationResult:
    """Résultat de validation pour un fichier Python"""
    file_path: str
    exists: bool = False
    syntax_valid: bool = False
    importable: bool = False
    has_functions: bool = False
    has_classes: bool = False
    function_count: int = 0
    class_count: int = 0
    error_message: Optional[str] = None
    import_error: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si le fichier respecte tous les critères"""
        return (self.exists and 
                self.syntax_valid and 
                self.importable and 
                (self.has_functions or self.has_classes))

@dataclass
class DirectoryValidationResult:
    """Résultat de validation pour un dossier"""
    directory_path: str
    has_init: bool = False
    all_files_importable: bool = False
    structure_coherent: bool = False
    no_corrupted_files: bool = False
    file_results: List[FileValidationResult] = None
    
    def __post_init__(self):
        if self.file_results is None:
            self.file_results = []
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si le dossier respecte tous les critères"""
        return (self.has_init and 
                self.all_files_importable and 
                self.structure_coherent and 
                self.no_corrupted_files)

class MultimediaModuleValidator:
    """Validateur spécialisé pour les modules multimedia"""
    
    def __init__(self, multimedia_path: Path):
        self.multimedia_path = multimedia_path
        self.results = {}
        
    def validate_python_syntax(self, file_path: Path) -> Tuple[bool, Optional[str], int, int]:
        """Valide la syntaxe Python et compte les définitions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Count functions and classes
            func_count = 0
            class_count = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_count += 1
                elif isinstance(node, ast.ClassDef):
                    class_count += 1
            
            return True, None, func_count, class_count
            
        except SyntaxError as e:
            return False, f"Erreur de syntaxe: {str(e)}", 0, 0
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}", 0, 0
    
    def test_import_capability(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Teste si le fichier peut être importé sans erreur"""
        try:
            # Get module name relative to multimedia directory
            relative_path = file_path.relative_to(self.multimedia_path.parent)
            module_name = str(relative_path).replace('/', '.').replace('.py', '')
            
            # Test import using subprocess to avoid affecting current process
            result = subprocess.run([
                sys.executable, '-c', 
                f'import sys; sys.path.insert(0, "{self.multimedia_path.parent}"); import {module_name}'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, None
            else:
                return False, f"Import error: {result.stderr.strip()}"
                
        except Exception as e:
            return False, f"Exception during import test: {str(e)}"
    
    def validate_file(self, file_path: Path) -> FileValidationResult:
        """Valide un fichier Python selon les critères"""
        result = FileValidationResult(file_path=str(file_path))
        
        # 1. Vérifier l'existence
        result.exists = file_path.exists()
        if not result.exists:
            result.error_message = "Fichier inexistant"
            return result
        
        # 2. Valider la syntaxe et compter les définitions
        syntax_valid, syntax_error, func_count, class_count = self.validate_python_syntax(file_path)
        result.syntax_valid = syntax_valid
        result.function_count = func_count
        result.class_count = class_count
        result.has_functions = func_count > 0
        result.has_classes = class_count > 0
        
        if not syntax_valid:
            result.error_message = syntax_error
            return result
        
        # 3. Tester l'import
        importable, import_error = self.test_import_capability(file_path)
        result.importable = importable
        
        if not importable:
            result.import_error = import_error
        
        return result
    
    def validate_directory(self) -> DirectoryValidationResult:
        """Valide le dossier multimedia selon les critères"""
        result = DirectoryValidationResult(directory_path=str(self.multimedia_path))
        
        # 1. Vérifier la présence d'__init__.py
        init_file = self.multimedia_path / "__init__.py"
        result.has_init = init_file.exists()
        
        # 2. Valider tous les fichiers Python
        python_files = list(self.multimedia_path.glob("*.py"))
        valid_files = 0
        
        for py_file in python_files:
            file_result = self.validate_file(py_file)
            result.file_results.append(file_result)
            
            if file_result.is_valid:
                valid_files += 1
        
        # 3. Vérifier que tous les fichiers sont importables
        result.all_files_importable = valid_files == len(python_files)
        
        # 4. Vérifier la structure cohérente
        result.structure_coherent = len(python_files) > 0 and result.has_init
        
        # 5. Vérifier qu'il n'y a pas de fichiers corrompus
        corrupted_files = [fr for fr in result.file_results if not fr.syntax_valid]
        result.no_corrupted_files = len(corrupted_files) == 0
        
        return result
    
    def generate_report(self) -> str:
        """Génère un rapport de validation complet"""
        directory_result = self.validate_directory()
        
        report = []
        report.append("="*80)
        report.append("DOSSIER MULTIMEDIA/ - RAPPORT DE VALIDATION")
        report.append("="*80)
        report.append("")
        
        # Résumé global
        report.append("RÉSUMÉ GLOBAL:")
        report.append(f"📁 Dossier: {directory_result.directory_path}")
        report.append(f"✅ __init__.py présent: {'OUI' if directory_result.has_init else 'NON'}")
        report.append(f"✅ Tous fichiers importables: {'OUI' if directory_result.all_files_importable else 'NON'}")
        report.append(f"✅ Structure cohérente: {'OUI' if directory_result.structure_coherent else 'NON'}")
        report.append(f"✅ Aucun fichier corrompu: {'OUI' if directory_result.no_corrupted_files else 'NON'}")
        report.append("")
        
        # Status final
        if directory_result.is_valid:
            report.append("🎉 VALIDATION FINALE: ✅ SUCCÈS")
        else:
            report.append("❌ VALIDATION FINALE: ❌ ÉCHEC")
        
        report.append("")
        report.append("DÉTAILS PAR FICHIER:")
        report.append("-" * 50)
        
        # Détails par fichier
        for file_result in directory_result.file_results:
            filename = Path(file_result.file_path).name
            status = "✅" if file_result.is_valid else "❌"
            
            report.append(f"{status} {filename}")
            report.append(f"   📁 Existe: {'OUI' if file_result.exists else 'NON'}")
            report.append(f"   🔍 Syntaxe valide: {'OUI' if file_result.syntax_valid else 'NON'}")
            report.append(f"   📦 Importable: {'OUI' if file_result.importable else 'NON'}")
            report.append(f"   🔧 Fonctions: {file_result.function_count}")
            report.append(f"   🏗️  Classes: {file_result.class_count}")
            
            if file_result.error_message:
                report.append(f"   ⚠️  Erreur: {file_result.error_message}")
            if file_result.import_error:
                report.append(f"   📦 Import Error: {file_result.import_error}")
            
            report.append("")
        
        # Recommandations
        report.append("RECOMMANDATIONS:")
        report.append("-" * 20)
        
        failing_files = [fr for fr in directory_result.file_results if not fr.is_valid]
        if failing_files:
            report.append("Fichiers à corriger:")
            for fr in failing_files:
                filename = Path(fr.file_path).name
                report.append(f"  • {filename}: {fr.error_message or fr.import_error}")
        else:
            report.append("✅ Tous les fichiers sont conformes!")
        
        return "\n".join(report)

def main():
    """Point d'entrée principal"""
    multimedia_path = Path(__file__).parent / "multimedia"
    
    if not multimedia_path.exists():
        print(f"❌ Erreur: Le dossier {multimedia_path} n'existe pas")
        sys.exit(1)
    
    # Créer le validateur
    validator = MultimediaModuleValidator(multimedia_path)
    
    # Générer le rapport
    report = validator.generate_report()
    
    # Afficher le rapport
    print(report)
    
    # Sauvegarder le rapport
    report_file = Path("multimedia_validation_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Rapport sauvegardé dans: {report_file}")
    
    # Déterminer le code de sortie
    directory_result = validator.validate_directory()
    sys.exit(0 if directory_result.is_valid else 1)

if __name__ == "__main__":
    main()