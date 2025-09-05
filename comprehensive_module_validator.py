#!/usr/bin/env python3
"""Comprehensive Module Validation Script

Validates that all Python files and modules in the Ainflue repository meet
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
    """Result of validating a Python file or module"""
    file_path: str
    exists: bool = False
    syntax_valid: bool = False
    importable: bool = False
    has_definitions: bool = False
    error_message: Optional[str] = None
    functions_count: int = 0
    classes_count: int = 0

@dataclass
class DirectoryValidationResult:
    """Result of validating a directory"""
    directory_path: str
    has_init_py: bool = False
    all_files_importable: bool = False
    structure_coherent: bool = False
    corrupted_files: List[str] = None
    
    def __post_init__(self):
        if self.corrupted_files is None:
            self.corrupted_files = []

class ComprehensiveModuleValidator:
    """Comprehensive validation system for all Python modules"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.results: Dict[str, ValidationResult] = {}
        self.directory_results: Dict[str, DirectoryValidationResult] = {}
        self.excluded_patterns = {
            '__pycache__',
            '.git',
            '.env',
            'node_modules',
            'dist',
            'build',
            '*.pyc',
            '.pytest_cache',
            'alembic/versions'  # Skip alembic migration files
        }
    
    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from validation"""
        path_str = str(path)
        return any(pattern in path_str for pattern in self.excluded_patterns)
    
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
                return False, f"Import error: {result.stderr.strip()}"
                
        except subprocess.TimeoutExpired:
            return False, "Import timeout"
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
        
        return result
    
    def validate_directory(self, dir_path: Path) -> DirectoryValidationResult:
        """Validate a directory structure"""
        result = DirectoryValidationResult(directory_path=str(dir_path))
        
        # Check for __init__.py
        init_file = dir_path / '__init__.py'
        result.has_init_py = init_file.exists()
        
        # Check if all Python files in directory are importable
        python_files = list(dir_path.glob('*.py'))
        if python_files:
            all_importable = True
            for py_file in python_files:
                if self.should_exclude(py_file):
                    continue
                    
                file_result = self.validate_file(py_file)
                if not file_result.importable:
                    all_importable = False
                    result.corrupted_files.append(str(py_file))
            
            result.all_files_importable = all_importable
        else:
            result.all_files_importable = True  # No Python files to check
        
        # Structure coherence (basic check)
        result.structure_coherent = result.has_init_py or len(python_files) == 0
        
        return result
    
    def find_all_python_files(self) -> List[Path]:
        """Find all Python files in the repository"""
        python_files = []
        for path in self.root_path.rglob('*.py'):
            if not self.should_exclude(path):
                python_files.append(path)
        return python_files
    
    def find_all_python_directories(self) -> List[Path]:
        """Find all directories containing Python files"""
        directories = set()
        for py_file in self.find_all_python_files():
            directories.add(py_file.parent)
        return list(directories)
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation on all Python files and directories"""
        logger.info("Starting comprehensive module validation...")
        
        # Find all Python files
        python_files = self.find_all_python_files()
        logger.info(f"Found {len(python_files)} Python files to validate")
        
        # Validate each file
        failed_files = []
        passed_files = []
        
        for py_file in python_files:
            try:
                result = self.validate_file(py_file)
                self.results[str(py_file)] = result
                
                if result.syntax_valid and result.importable:
                    passed_files.append(str(py_file))
                    logger.info(f"✅ {py_file.relative_to(self.root_path)}")
                else:
                    failed_files.append(str(py_file))
                    logger.error(f"❌ {py_file.relative_to(self.root_path)}: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"❌ Error validating {py_file}: {e}")
                failed_files.append(str(py_file))
        
        # Validate directories
        directories = self.find_all_python_directories()
        logger.info(f"Found {len(directories)} directories to validate")
        
        missing_init_dirs = []
        for directory in directories:
            try:
                dir_result = self.validate_directory(directory)
                self.directory_results[str(directory)] = dir_result
                
                if not dir_result.has_init_py:
                    missing_init_dirs.append(str(directory))
                    logger.warning(f"⚠️  {directory.relative_to(self.root_path)}: Missing __init__.py")
                else:
                    logger.info(f"✅ {directory.relative_to(self.root_path)}: Has __init__.py")
                    
            except Exception as e:
                logger.error(f"❌ Error validating directory {directory}: {e}")
        
        # Generate summary
        summary = {
            'total_files': len(python_files),
            'passed_files': len(passed_files),
            'failed_files': len(failed_files),
            'total_directories': len(directories),
            'directories_with_init': len(directories) - len(missing_init_dirs),
            'directories_missing_init': len(missing_init_dirs),
            'failed_file_list': failed_files,
            'missing_init_dirs': missing_init_dirs,
            'success_rate': (len(passed_files) / len(python_files)) * 100 if python_files else 0
        }
        
        return summary
    
    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate a comprehensive validation report"""
        report = f"""
=== COMPREHENSIVE MODULE VALIDATION REPORT ===

📊 SUMMARY STATISTICS:
• Total Python files: {summary['total_files']}
• Files passed validation: {summary['passed_files']} ({summary['success_rate']:.1f}%)
• Files failed validation: {summary['failed_files']}
• Total directories: {summary['total_directories']}
• Directories with __init__.py: {summary['directories_with_init']}
• Directories missing __init__.py: {summary['directories_missing_init']}

"""
        
        if summary['failed_files'] > 0:
            report += f"""
❌ FAILED FILES ({summary['failed_files']}):
"""
            for file_path in summary['failed_file_list']:
                result = self.results.get(file_path)
                if result:
                    report += f"   • {file_path}: {result.error_message}\n"
        
        if summary['directories_missing_init']:
            report += f"""
⚠️  DIRECTORIES MISSING __init__.py ({summary['directories_missing_init']}):
"""
            for dir_path in summary['missing_init_dirs']:
                report += f"   • {dir_path}\n"
        
        # Special focus on distribution module as requested
        distribution_files = [f for f in self.results.keys() if 'distribution' in f]
        if distribution_files:
            report += f"""
📁 DISTRIBUTION MODULE VALIDATION:
"""
            for file_path in distribution_files:
                result = self.results[file_path]
                status = "✅" if (result.syntax_valid and result.importable) else "❌"
                report += f"   {status} {file_path}\n"
                if result.error_message:
                    report += f"      Error: {result.error_message}\n"
        
        return report

def main():
    """Main validation function"""
    validator = ComprehensiveModuleValidator()
    
    try:
        summary = validator.run_comprehensive_validation()
        report = validator.generate_report(summary)
        
        print(report)
        
        # Save report to file
        with open('module_validation_report.txt', 'w') as f:
            f.write(report)
        
        # Exit with appropriate code
        if summary['failed_files'] == 0 and summary['directories_missing_init'] == 0:
            logger.info("🎉 All modules passed validation!")
            return True
        else:
            logger.error("❌ Some modules failed validation. See report for details.")
            return False
            
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)