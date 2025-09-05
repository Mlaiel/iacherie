#!/usr/bin/env python3
"""Infrastructure Module Validation Script

Validates that all Python files and modules in the infrastructure/ directory meet
the requirements specified in the problem statement:

POUR CHAQUE FICHIER PYTHON:
- Le fichier existe
- Import sans erreur: python -c "import nomfichier"
- Syntaxe correcte
- Fonctions/classes définies
- Pas d'erreurs dans VS Code

POUR CHAQUE DOSSIER:
- Contient __init__.py
- Tous les sous-fichiers importables
- Structure cohérente
- Pas de fichiers corrompus

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
class ValidationResult:
    """Result of validating a Python file"""
    file_path: str
    exists: bool = False
    syntax_valid: bool = False
    importable: bool = False
    has_definitions: bool = False
    functions_count: int = 0
    classes_count: int = 0
    error_message: Optional[str] = None

class InfrastructureValidator:
    """Validator specifically for infrastructure/ directory modules"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        self.infrastructure_path = self.root_path / "infrastructure"
    
    def validate_syntax(self, file_path: Path) -> Tuple[bool, Optional[str], int, int]:
        """Validate Python syntax and count definitions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            # Count function and class definitions
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            return True, None, len(functions), len(classes)
            
        except SyntaxError as e:
            return False, f"Syntax error line {e.lineno}: {e.msg}", 0, 0
        except Exception as e:
            return False, f"Parse error: {e}", 0, 0
    
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
            cmd = [sys.executable, '-c', f'import {module_name}']
            result = subprocess.run(
                cmd, 
                cwd=self.root_path,
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return True, None
            else:
                # Clean up error message
                error_msg = result.stderr.strip()
                if "WARNING:" in error_msg:
                    # Extract only the actual error, not warnings
                    lines = error_msg.split('\n')
                    error_lines = [line for line in lines if not line.startswith('WARNING:')]
                    error_msg = '\n'.join(error_lines).strip()
                return False, f"Import error: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Import timeout"
        except Exception as e:
            return False, f"Import test failed: {e}"
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single Python file"""
        result = ValidationResult(file_path=str(file_path.relative_to(self.root_path)))
        
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
        
        return result
    
    def validate_directory_structure(self, directory: Path) -> Dict[str, Any]:
        """Validate directory structure requirements"""
        result = {
            'path': str(directory.relative_to(self.root_path)),
            'has_init_py': False,
            'python_files': [],
            'subdirectories': [],
            'all_files_importable': True,
            'structure_coherent': True,
            'errors': []
        }
        
        # Check for __init__.py
        init_file = directory / "__init__.py"
        result['has_init_py'] = init_file.exists()
        
        if not result['has_init_py']:
            result['errors'].append("Missing __init__.py file")
            result['structure_coherent'] = False
        
        # Find Python files
        python_files = list(directory.glob("*.py"))
        result['python_files'] = [f.name for f in python_files]
        
        # Find subdirectories
        subdirs = [d for d in directory.iterdir() if d.is_dir() and not d.name.startswith('.')]
        result['subdirectories'] = [d.name for d in subdirs]
        
        # Test if all Python files are importable
        importable_files = 0
        for py_file in python_files:
            file_result = self.validate_file(py_file)
            if not file_result.importable:
                result['all_files_importable'] = False
                result['errors'].append(f"{py_file.name}: {file_result.error_message}")
            else:
                importable_files += 1
        
        result['importable_files_count'] = importable_files
        result['total_files_count'] = len(python_files)
        
        return result
    
    def run_infrastructure_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation on infrastructure directory"""
        logger.info("🚀 Starting Infrastructure Module Validation")
        logger.info("=" * 60)
        
        if not self.infrastructure_path.exists():
            return {
                "status": "error",
                "message": "Infrastructure directory not found",
                "path": str(self.infrastructure_path)
            }
        
        results = {
            "status": "success",
            "infrastructure_path": str(self.infrastructure_path.relative_to(self.root_path)),
            "files": {},
            "directories": {},
            "summary": {
                "total_files": 0,
                "valid_files": 0,
                "importable_files": 0,
                "files_with_definitions": 0,
                "directories_with_init": 0,
                "total_directories": 0
            }
        }
        
        # Find all Python files in infrastructure directory
        python_files = list(self.infrastructure_path.rglob("*.py"))
        results["summary"]["total_files"] = len(python_files)
        
        logger.info(f"📦 Found {len(python_files)} Python files in infrastructure/")
        
        # Validate each file
        for i, py_file in enumerate(python_files, 1):
            logger.info(f"  [{i}/{len(python_files)}] {py_file.relative_to(self.infrastructure_path)}")
            
            file_result = self.validate_file(py_file)
            relative_path = str(py_file.relative_to(self.infrastructure_path))
            results["files"][relative_path] = {
                "exists": file_result.exists,
                "syntax_valid": file_result.syntax_valid,
                "importable": file_result.importable,
                "has_definitions": file_result.has_definitions,
                "functions_count": file_result.functions_count,
                "classes_count": file_result.classes_count,
                "error_message": file_result.error_message
            }
            
            # Update summary
            if file_result.syntax_valid:
                results["summary"]["valid_files"] += 1
            if file_result.importable:
                results["summary"]["importable_files"] += 1
            if file_result.has_definitions:
                results["summary"]["files_with_definitions"] += 1
        
        # Find all directories in infrastructure
        directories = [d for d in self.infrastructure_path.rglob("*") if d.is_dir() and not d.name.startswith('.')]
        results["summary"]["total_directories"] = len(directories)
        
        logger.info(f"📁 Found {len(directories)} directories in infrastructure/")
        
        # Validate each directory
        for directory in directories:
            dir_result = self.validate_directory_structure(directory)
            relative_path = str(directory.relative_to(self.infrastructure_path))
            results["directories"][relative_path] = dir_result
            
            if dir_result['has_init_py']:
                results["summary"]["directories_with_init"] += 1
        
        # Calculate overall status
        total_files = results["summary"]["total_files"]
        valid_files = results["summary"]["valid_files"]
        importable_files = results["summary"]["importable_files"]
        
        success_rate = (importable_files / total_files) * 100 if total_files > 0 else 0
        
        logger.info("\n📊 INFRASTRUCTURE VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Files with valid syntax: {valid_files}/{total_files}")
        logger.info(f"✅ Importable files: {importable_files}/{total_files}")
        logger.info(f"✅ Files with definitions: {results['summary']['files_with_definitions']}/{total_files}")
        logger.info(f"✅ Directories with __init__.py: {results['summary']['directories_with_init']}/{results['summary']['total_directories']}")
        logger.info(f"📈 Overall success rate: {success_rate:.1f}%")
        
        results["summary"]["success_rate"] = success_rate
        
        if success_rate >= 90:
            logger.info("🎉 INFRASTRUCTURE VALIDATION PASSED!")
            results["status"] = "passed"
        elif success_rate >= 70:
            logger.info("⚠️  INFRASTRUCTURE VALIDATION NEEDS ATTENTION")
            results["status"] = "warning"
        else:
            logger.info("❌ INFRASTRUCTURE VALIDATION FAILED")
            results["status"] = "failed"
        
        return results

def main():
    """Main validation function"""
    try:
        root_path = Path(__file__).parent
        validator = InfrastructureValidator(root_path)
        
        results = validator.run_infrastructure_validation()
        
        # Save results to file
        import json
        output_file = root_path / "infrastructure_validation_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 Detailed report saved to: {output_file}")
        
        # Return exit code based on results
        if results["status"] == "passed":
            return 0
        elif results["status"] == "warning":
            return 1
        else:
            return 2
            
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    sys.exit(main())