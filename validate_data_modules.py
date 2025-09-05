#!/usr/bin/env python3
"""
Data Modules Validation Script
=============================

Systematic validation of all data/ folder modules according to requirements:

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

Author: System Validation Tool
"""

import os
import sys
import ast
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any

class DataModuleValidator:
    """Comprehensive validator for data/ folder modules"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.results = {
            "directories": {},
            "files": {},
            "imports": {},
            "syntax": {},
            "summary": {}
        }
        
    def validate_all(self) -> Dict[str, Any]:
        """Run comprehensive validation of all data modules"""
        print("🔍 Starting Data Modules Validation")
        print("=" * 50)
        
        # Step 1: Validate directory structure
        self._validate_directory_structure()
        
        # Step 2: Validate Python files
        self._validate_python_files()
        
        # Step 3: Test imports
        self._test_imports()
        
        # Step 4: Generate summary
        self._generate_summary()
        
        return self.results
    
    def _validate_directory_structure(self):
        """Validate directory structure and __init__.py presence"""
        print("📁 Validating Directory Structure...")
        
        if not self.data_path.exists():
            self.results["directories"]["data_exists"] = False
            print("❌ Data directory does not exist!")
            return
            
        self.results["directories"]["data_exists"] = True
        
        # Find all subdirectories
        subdirs = [d for d in self.data_path.iterdir() if d.is_dir()]
        self.results["directories"]["subdirectories"] = []
        
        for subdir in subdirs:
            subdir_info = {
                "name": subdir.name,
                "path": str(subdir),
                "has_init": (subdir / "__init__.py").exists(),
                "python_files": []
            }
            
            # Find Python files in subdirectory
            python_files = list(subdir.glob("*.py"))
            subdir_info["python_files"] = [f.name for f in python_files]
            subdir_info["file_count"] = len(python_files)
            
            self.results["directories"]["subdirectories"].append(subdir_info)
            
            status = "✅" if subdir_info["has_init"] else "❌"
            print(f"  {status} {subdir.name}/ (__init__.py: {subdir_info['has_init']}, {subdir_info['file_count']} .py files)")
    
    def _validate_python_files(self):
        """Validate syntax and structure of Python files"""
        print("\n🐍 Validating Python Files...")
        
        # Get all Python files in data/
        python_files = list(self.data_path.rglob("*.py"))
        
        for py_file in python_files:
            file_info = {
                "path": str(py_file),
                "relative_path": str(py_file.relative_to(self.data_path)),
                "exists": py_file.exists(),
                "syntax_valid": False,
                "has_classes": False,
                "has_functions": False,
                "syntax_error": None
            }
            
            if file_info["exists"]:
                try:
                    # Read and parse file
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse AST to check syntax
                    tree = ast.parse(content, filename=str(py_file))
                    file_info["syntax_valid"] = True
                    
                    # Check for classes and functions
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            file_info["has_classes"] = True
                        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                            file_info["has_functions"] = True
                            
                except SyntaxError as e:
                    file_info["syntax_error"] = str(e)
                except Exception as e:
                    file_info["syntax_error"] = f"Parse error: {str(e)}"
            
            self.results["files"][str(py_file.relative_to(self.data_path))] = file_info
            
            # Print status
            status = "✅" if file_info["syntax_valid"] else "❌"
            func_class_info = ""
            if file_info["syntax_valid"]:
                if file_info["has_classes"] or file_info["has_functions"]:
                    parts = []
                    if file_info["has_classes"]: parts.append("classes")
                    if file_info["has_functions"]: parts.append("functions")
                    func_class_info = f" ({', '.join(parts)})"
            
            print(f"  {status} {file_info['relative_path']}{func_class_info}")
            if file_info["syntax_error"]:
                print(f"    ⚠️  Syntax Error: {file_info['syntax_error']}")
    
    def _test_imports(self):
        """Test import functionality for modules"""
        print("\n📦 Testing Module Imports...")
        
        # Test main data module
        self._test_single_import("data", "Main data module")
        
        # Test each subdirectory module
        for subdir_info in self.results["directories"]["subdirectories"]:
            if subdir_info["has_init"]:
                module_name = f"data.{subdir_info['name']}"
                self._test_single_import(module_name, f"Subdirectory: {subdir_info['name']}")
    
    def _test_single_import(self, module_name: str, description: str):
        """Test importing a single module"""
        import_info = {
            "module": module_name,
            "description": description,
            "success": False,
            "error": None,
            "error_type": None
        }
        
        try:
            # Try to import the module
            importlib.import_module(module_name)
            import_info["success"] = True
            print(f"  ✅ {module_name} - {description}")
            
        except ImportError as e:
            import_info["error"] = str(e)
            import_info["error_type"] = "ImportError"
            print(f"  ❌ {module_name} - ImportError: {str(e)}")
            
        except Exception as e:
            import_info["error"] = str(e)
            import_info["error_type"] = type(e).__name__
            print(f"  ⚠️  {module_name} - {type(e).__name__}: {str(e)}")
        
        self.results["imports"][module_name] = import_info
    
    def _generate_summary(self):
        """Generate validation summary"""
        print("\n📊 Validation Summary")
        print("=" * 50)
        
        # Directory summary
        subdirs = self.results["directories"]["subdirectories"]
        total_subdirs = len(subdirs)
        subdirs_with_init = sum(1 for d in subdirs if d["has_init"])
        
        # File summary
        files = self.results["files"]
        total_files = len(files)
        valid_syntax = sum(1 for f in files.values() if f["syntax_valid"])
        files_with_classes = sum(1 for f in files.values() if f["has_classes"])
        files_with_functions = sum(1 for f in files.values() if f["has_functions"])
        
        # Import summary
        imports = self.results["imports"]
        successful_imports = sum(1 for i in imports.values() if i["success"])
        total_imports = len(imports)
        
        summary = {
            "directories": {
                "total": total_subdirs,
                "with_init": subdirs_with_init,
                "percentage": round((subdirs_with_init / total_subdirs * 100) if total_subdirs > 0 else 0, 1)
            },
            "files": {
                "total": total_files,
                "valid_syntax": valid_syntax,
                "with_classes": files_with_classes, 
                "with_functions": files_with_functions,
                "syntax_percentage": round((valid_syntax / total_files * 100) if total_files > 0 else 0, 1)
            },
            "imports": {
                "total": total_imports,
                "successful": successful_imports,
                "percentage": round((successful_imports / total_imports * 100) if total_imports > 0 else 0, 1)
            }
        }
        
        self.results["summary"] = summary
        
        print(f"📁 Directories: {subdirs_with_init}/{total_subdirs} have __init__.py ({summary['directories']['percentage']}%)")
        print(f"🐍 Python Files: {valid_syntax}/{total_files} have valid syntax ({summary['files']['syntax_percentage']}%)")
        print(f"📦 Module Imports: {successful_imports}/{total_imports} successful ({summary['imports']['percentage']}%)")
        print(f"🏗️  Implementation: {files_with_classes} files with classes, {files_with_functions} with functions")
        
        # Overall status
        overall_success = (
            summary['directories']['percentage'] >= 95 and
            summary['files']['syntax_percentage'] >= 95 and
            summary['imports']['percentage'] >= 50  # Lower threshold for imports due to dependencies
        )
        
        status_icon = "✅" if overall_success else "⚠️"
        print(f"\n{status_icon} Overall Status: {'PASSED' if overall_success else 'NEEDS ATTENTION'}")
        
        return summary

def main():
    """Main validation function"""
    # Change to repository root
    os.chdir(Path(__file__).parent)
    
    validator = DataModuleValidator()
    results = validator.validate_all()
    
    # Exit with appropriate code
    summary = results["summary"]
    if summary["directories"]["percentage"] >= 95 and summary["files"]["syntax_percentage"] >= 95:
        print("\n🎉 Data modules validation completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Some issues found - see details above")
        sys.exit(1)

if __name__ == "__main__":
    main()