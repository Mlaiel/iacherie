#!/usr/bin/env python3
"""
Payment Module Validation Script
================================

Validates all files in the payment/ directory according to the requirements:

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
class PaymentFileValidationResult:
    """Result of validating a Python file in payment directory"""
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
        """Check if file meets all criteria"""
        # For __init__.py files, having definitions is not required
        is_init_file = Path(self.file_path).name == "__init__.py"
        definitions_requirement = True if is_init_file else (self.has_functions or self.has_classes)
        
        return (self.exists and 
                self.syntax_valid and 
                self.importable and 
                definitions_requirement)

@dataclass
class DirectoryValidationResult:
    """Result of validating a directory structure"""
    directory_path: str
    has_init: bool = False
    all_files_importable: bool = False
    structure_coherent: bool = False
    no_corrupted_files: bool = False
    file_results: List[PaymentFileValidationResult] = None
    
    def __post_init__(self):
        if self.file_results is None:
            self.file_results = []

class PaymentModuleValidator:
    """Specialized validator for payment directory modules"""
    
    def __init__(self, payment_dir: str = "/home/runner/work/Ainflue/Ainflue/payment"):
        self.payment_dir = Path(payment_dir)
        self.validation_results = {}
        
    def validate_python_syntax(self, file_path: Path) -> Tuple[bool, Optional[str], int, int]:
        """Validate Python syntax and count definitions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Count functions and classes
            func_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            
            return True, None, func_count, class_count
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}", 0, 0
        except Exception as e:
            return False, f"Error during validation: {str(e)}", 0, 0
    
    def test_import_capability(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Test if file can be imported"""
        try:
            # Convert path to module name
            relative_path = file_path.relative_to(Path("/home/runner/work/Ainflue/Ainflue"))
            if relative_path.suffix == '.py':
                relative_path = relative_path.with_suffix('')
            
            module_name = str(relative_path).replace(os.sep, '.')
            
            # Test import
            result = subprocess.run([
                sys.executable, '-c', f'import {module_name}'
            ], capture_output=True, text=True, cwd="/home/runner/work/Ainflue/Ainflue")
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr.strip()
                
        except Exception as e:
            return False, f"Import test failed: {str(e)}"
    
    def validate_file(self, file_path: Path) -> PaymentFileValidationResult:
        """Validate a single Python file according to criteria"""
        result = PaymentFileValidationResult(file_path=str(file_path))
        
        # 1. Check existence
        result.exists = file_path.exists()
        if not result.exists:
            result.error_message = "File does not exist"
            return result
        
        # 2. Validate syntax and count definitions
        syntax_valid, syntax_error, func_count, class_count = self.validate_python_syntax(file_path)
        result.syntax_valid = syntax_valid
        result.function_count = func_count
        result.class_count = class_count
        result.has_functions = func_count > 0
        result.has_classes = class_count > 0
        
        if not syntax_valid:
            result.error_message = syntax_error
            return result
        
        # 3. Test import
        importable, import_error = self.test_import_capability(file_path)
        result.importable = importable
        result.import_error = import_error
        
        if not importable:
            result.error_message = import_error
        
        return result
    
    def validate_directory(self, dir_path: Path) -> DirectoryValidationResult:
        """Validate directory structure and all Python files"""
        result = DirectoryValidationResult(directory_path=str(dir_path))
        
        # Check for __init__.py
        init_file = dir_path / "__init__.py"
        result.has_init = init_file.exists()
        
        # Find all Python files
        python_files = list(dir_path.glob("*.py"))
        
        # Validate each Python file
        all_importable = True
        all_syntax_valid = True
        
        for py_file in python_files:
            file_result = self.validate_file(py_file)
            result.file_results.append(file_result)
            
            if not file_result.importable:
                all_importable = False
            if not file_result.syntax_valid:
                all_syntax_valid = False
        
        result.all_files_importable = all_importable
        result.no_corrupted_files = all_syntax_valid
        result.structure_coherent = result.has_init and all_syntax_valid
        
        return result
    
    def validate_payment_module(self) -> Dict[str, Any]:
        """Validate the entire payment module"""
        logger.info("Starting payment module validation...")
        
        validation_summary = {
            "main_directory": {},
            "processors_directory": {},
            "all_files": [],
            "summary": {}
        }
        
        # Validate main payment directory
        main_result = self.validate_directory(self.payment_dir)
        validation_summary["main_directory"] = {
            "path": str(self.payment_dir),
            "has_init": main_result.has_init,
            "structure_coherent": main_result.structure_coherent,
            "files": [
                {
                    "file": str(Path(fr.file_path).name),
                    "exists": fr.exists,
                    "syntax_valid": fr.syntax_valid,
                    "importable": fr.importable,
                    "has_definitions": fr.has_functions or fr.has_classes,
                    "functions": fr.function_count,
                    "classes": fr.class_count,
                    "error": fr.error_message or fr.import_error
                }
                for fr in main_result.file_results
            ]
        }
        
        # Validate processors subdirectory
        processors_dir = self.payment_dir / "processors"
        if processors_dir.exists():
            processors_result = self.validate_directory(processors_dir)
            validation_summary["processors_directory"] = {
                "path": str(processors_dir),
                "has_init": processors_result.has_init,
                "structure_coherent": processors_result.structure_coherent,
                "files": [
                    {
                        "file": str(Path(fr.file_path).name),
                        "exists": fr.exists,
                        "syntax_valid": fr.syntax_valid,
                        "importable": fr.importable,
                        "has_definitions": fr.has_functions or fr.has_classes,
                        "functions": fr.function_count,
                        "classes": fr.class_count,
                        "error": fr.error_message or fr.import_error
                    }
                    for fr in processors_result.file_results
                ]
            }
            
            # Add processors files to all_files list
            validation_summary["all_files"].extend(processors_result.file_results)
        
        # Add main directory files to all_files list
        validation_summary["all_files"].extend(main_result.file_results)
        
        # Calculate summary statistics
        total_files = len(validation_summary["all_files"])
        valid_files = sum(1 for fr in validation_summary["all_files"] if fr.is_valid)
        syntax_valid_files = sum(1 for fr in validation_summary["all_files"] if fr.syntax_valid)
        importable_files = sum(1 for fr in validation_summary["all_files"] if fr.importable)
        files_with_definitions = sum(1 for fr in validation_summary["all_files"] if fr.has_functions or fr.has_classes)
        
        validation_summary["summary"] = {
            "total_files": total_files,
            "valid_files": valid_files,
            "syntax_valid_files": syntax_valid_files,
            "importable_files": importable_files,
            "files_with_definitions": files_with_definitions,
            "all_requirements_met": (
                main_result.has_init and
                (not processors_dir.exists() or processors_result.has_init) and
                valid_files == total_files
            )
        }
        
        return validation_summary
    
    def print_validation_report(self, validation_summary: Dict[str, Any]):
        """Print detailed validation report"""
        print("\n" + "="*80)
        print("🔍 PAYMENT MODULE VALIDATION REPORT")
        print("="*80)
        
        # Main directory
        main_dir = validation_summary["main_directory"]
        print(f"\n📁 MAIN DIRECTORY: {main_dir['path']}")
        print(f"   ✅ Has __init__.py: {main_dir['has_init']}")
        print(f"   ✅ Structure coherent: {main_dir['structure_coherent']}")
        
        for file_info in main_dir["files"]:
            status = "✅" if all([file_info["exists"], file_info["syntax_valid"], 
                                file_info["importable"], file_info["has_definitions"]]) else "❌"
            print(f"   {status} {file_info['file']}")
            print(f"      - Exists: {file_info['exists']}")
            print(f"      - Syntax valid: {file_info['syntax_valid']}")
            print(f"      - Importable: {file_info['importable']}")
            print(f"      - Has definitions: {file_info['has_definitions']} ({file_info['functions']} functions, {file_info['classes']} classes)")
            if file_info["error"]:
                print(f"      - Error: {file_info['error']}")
        
        # Processors directory
        if "processors_directory" in validation_summary:
            proc_dir = validation_summary["processors_directory"]
            print(f"\n📁 PROCESSORS DIRECTORY: {proc_dir['path']}")
            print(f"   ✅ Has __init__.py: {proc_dir['has_init']}")
            print(f"   ✅ Structure coherent: {proc_dir['structure_coherent']}")
            
            for file_info in proc_dir["files"]:
                status = "✅" if all([file_info["exists"], file_info["syntax_valid"], 
                                    file_info["importable"], file_info["has_definitions"]]) else "❌"
                print(f"   {status} {file_info['file']}")
                print(f"      - Exists: {file_info['exists']}")
                print(f"      - Syntax valid: {file_info['syntax_valid']}")
                print(f"      - Importable: {file_info['importable']}")
                print(f"      - Has definitions: {file_info['has_definitions']} ({file_info['functions']} functions, {file_info['classes']} classes)")
                if file_info["error"]:
                    print(f"      - Error: {file_info['error']}")
        
        # Summary
        summary = validation_summary["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   Total files: {summary['total_files']}")
        print(f"   Valid files: {summary['valid_files']}")
        print(f"   Syntax valid: {summary['syntax_valid_files']}")
        print(f"   Importable: {summary['importable_files']}")
        print(f"   With definitions: {summary['files_with_definitions']}")
        print(f"   All requirements met: {'✅ YES' if summary['all_requirements_met'] else '❌ NO'}")
        
        print("\n" + "="*80)

def main():
    """Run payment module validation"""
    validator = PaymentModuleValidator()
    validation_summary = validator.validate_payment_module()
    validator.print_validation_report(validation_summary)
    
    # Return exit code based on validation result
    return 0 if validation_summary["summary"]["all_requirements_met"] else 1

if __name__ == "__main__":
    sys.exit(main())