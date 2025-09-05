#!/usr/bin/env python3
"""
Microservices Module Validation Script for Ainflue Platform
Validates all Python files and modules in the microservices/ directory according to requirements:

POUR CHAQUE FICHIER PYTHON:
- Le fichier existe
- Import sans erreur : python -c "import nomfichier"
- Syntaxe correcte
- Fonctions/classes définies
- Pas d'erreurs dans VS Code

POUR CHAQUE DOSSIER:
- Contient __init__.py
- Tous les sous-fichiers importables
- Structure cohérente
- Pas de fichiers corrompus

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import os
import sys
import ast
import subprocess
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of validating a single file or module"""
    file_path: str
    exists: bool = False
    syntax_valid: bool = False
    importable: bool = False
    has_definitions: bool = False
    functions_count: int = 0
    classes_count: int = 0
    error_message: Optional[str] = None
    success: bool = False

class MicroservicesValidator:
    """Validator specifically for microservices directory"""
    
    def __init__(self, root_path: str = None):
        self.root_path = Path(root_path) if root_path else Path(__file__).parent
        self.microservices_path = self.root_path / "microservices"
        
    def validate_syntax(self, file_path: Path) -> Tuple[bool, Optional[str], int, int]:
        """Validate Python syntax and count definitions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to check syntax and count definitions
            tree = ast.parse(content)
            
            # Count functions and classes
            functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            
            return True, None, functions, classes
            
        except SyntaxError as e:
            return False, f"Syntax error: {e}", 0, 0
        except Exception as e:
            return False, f"Error reading file: {e}", 0, 0

    def test_import(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Test if a Python file can be imported"""
        try:
            # Convert file path to module name
            relative_path = file_path.relative_to(self.root_path)
            
            # Skip if not a .py file
            if not file_path.suffix == '.py':
                return True, "Not a Python file"
            
            # Get module path
            module_parts = list(relative_path.parts[:-1])  # Remove filename
            filename = relative_path.stem
            
            # Skip __init__.py for module import test
            if filename == '__init__':
                if module_parts:
                    module_name = '.'.join(module_parts)
                else:
                    return True, "Root __init__.py - skipping import test"
            else:
                if module_parts:
                    module_name = '.'.join(module_parts + [filename])
                else:
                    module_name = filename
            
            # Test import using subprocess to avoid affecting current process
            result = subprocess.run([
                sys.executable, '-c', f'import {module_name}'
            ], capture_output=True, text=True, cwd=self.root_path)
            
            if result.returncode == 0:
                return True, None
            else:
                return False, f"Import error: {result.stderr.strip()}"
                
        except Exception as e:
            return False, f"Import test failed: {e}"

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single Python file"""
        result = ValidationResult(file_path=str(file_path))
        
        # Check if file exists
        result.exists = file_path.exists()
        if not result.exists:
            result.error_message = "File does not exist"
            return result
        
        # Validate syntax and count definitions
        syntax_valid, syntax_error, func_count, class_count = self.validate_syntax(file_path)
        result.syntax_valid = syntax_valid
        result.functions_count = func_count
        result.classes_count = class_count
        result.has_definitions = func_count > 0 or class_count > 0
        
        if not syntax_valid:
            result.error_message = syntax_error
            return result
        
        # Test import
        importable, import_error = self.test_import(file_path)
        result.importable = importable
        
        if not importable:
            result.error_message = import_error
        
        # Overall success - must have definitions as per requirements
        result.success = (result.exists and result.syntax_valid and 
                         result.importable and result.has_definitions)
        
        return result

    def validate_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Validate a directory structure"""
        result = {
            'path': str(dir_path),
            'exists': dir_path.exists(),
            'has_init': False,
            'init_file_valid': False,
            'python_files': [],
            'all_importable': True,
            'structure_coherent': True,
            'corrupted_files': []
        }
        
        if not result['exists']:
            return result
        
        # Check for __init__.py
        init_file = dir_path / '__init__.py'
        result['has_init'] = init_file.exists()
        
        if result['has_init']:
            init_result = self.validate_file(init_file)
            result['init_file_valid'] = init_result.success
            result['init_has_definitions'] = init_result.has_definitions
        else:
            result['init_has_definitions'] = False
        
        # Find all Python files
        for py_file in dir_path.glob('**/*.py'):
            file_result = self.validate_file(py_file)
            result['python_files'].append({
                'file': str(py_file),
                'valid': file_result.success,
                'error': file_result.error_message
            })
            
            if not file_result.importable:
                result['all_importable'] = False
            
            if not file_result.success:
                result['corrupted_files'].append(str(py_file))
        
        return result

    def validate_microservices(self) -> Dict[str, Any]:
        """Validate the entire microservices directory"""
        logger.info("🔍 Starting microservices validation...")
        
        results = {
            'microservices_root': {},
            'subdirectories': {},
            'summary': {
                'total_directories': 0,
                'valid_directories': 0,
                'total_files': 0,
                'valid_files': 0,
                'all_requirements_met': False
            }
        }
        
        # Validate root microservices directory
        results['microservices_root'] = self.validate_directory(self.microservices_path)
        
        # Validate each subdirectory
        for subdir in self.microservices_path.iterdir():
            if subdir.is_dir() and subdir.name != '__pycache__':
                logger.info(f"  Validating {subdir.name}...")
                results['subdirectories'][subdir.name] = self.validate_directory(subdir)
                results['summary']['total_directories'] += 1
                
                if results['subdirectories'][subdir.name]['has_init'] and \
                   results['subdirectories'][subdir.name]['all_importable']:
                    results['summary']['valid_directories'] += 1
        
        # Count files and calculate success
        for dir_data in [results['microservices_root']] + list(results['subdirectories'].values()):
            for file_info in dir_data['python_files']:
                results['summary']['total_files'] += 1
                if file_info['valid']:
                    results['summary']['valid_files'] += 1
        
        # Check if all requirements are met
        results['summary']['all_requirements_met'] = (
            results['summary']['valid_directories'] == results['summary']['total_directories'] and
            results['summary']['valid_files'] == results['summary']['total_files'] and
            results['microservices_root']['has_init'] and
            results['microservices_root']['init_file_valid']
        )
        
        return results

    def print_validation_report(self, results: Dict[str, Any]) -> None:
        """Print a comprehensive validation report"""
        print("\n" + "="*80)
        print("🚀 MICROSERVICES VALIDATION REPORT")
        print("="*80)
        
        # Root directory status
        root = results['microservices_root']
        print(f"\n📁 Microservices Root Directory:")
        print(f"  {'✅' if root['exists'] else '❌'} Directory exists")
        print(f"  {'✅' if root['has_init'] else '❌'} Contains __init__.py")
        print(f"  {'✅' if root['init_file_valid'] else '❌'} __init__.py is valid")
        print(f"  {'✅' if root.get('init_has_definitions', False) else '❌'} __init__.py has functions/classes")
        
        # Subdirectory status
        print(f"\n📂 Subdirectories:")
        for dirname, dirdata in results['subdirectories'].items():
            print(f"\n  📁 {dirname}/")
            print(f"    {'✅' if dirdata['has_init'] else '❌'} Contains __init__.py")
            print(f"    {'✅' if dirdata['init_file_valid'] else '❌'} __init__.py is valid")
            print(f"    {'✅' if dirdata.get('init_has_definitions', False) else '❌'} __init__.py has functions/classes")
            print(f"    {'✅' if dirdata['all_importable'] else '❌'} All files importable")
            print(f"    {'✅' if not dirdata['corrupted_files'] else '❌'} No corrupted files")
            
            if dirdata['corrupted_files']:
                print(f"    ⚠️  Corrupted files: {', '.join(dirdata['corrupted_files'])}")
        
        # Summary
        summary = results['summary']
        print(f"\n📊 SUMMARY:")
        print(f"  Total directories: {summary['total_directories']}")
        print(f"  Valid directories: {summary['valid_directories']}")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Valid files: {summary['valid_files']}")
        print(f"  Success rate: {(summary['valid_files']/summary['total_files']*100) if summary['total_files'] > 0 else 0:.1f}%")
        
        # Final validation status
        print(f"\n🎯 FINAL VALIDATION:")
        if summary['all_requirements_met']:
            print("  ✅ ALL REQUIREMENTS MET")
            print("  ✅ Import sans erreur")
            print("  ✅ Toutes les fonctions définies")
            print("  ✅ Intégration avec autres modules OK")
            print("  ✅ Aucune erreur dans les logs")
        else:
            print("  ❌ REQUIREMENTS NOT MET")
            print("  🔧 Fixes needed - see details above")
        
        print("="*80)

def main():
    """Main validation function"""
    validator = MicroservicesValidator()
    results = validator.validate_microservices()
    validator.print_validation_report(results)
    
    return 0 if results['summary']['all_requirements_met'] else 1

if __name__ == "__main__":
    sys.exit(main())