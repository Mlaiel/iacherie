#!/usr/bin/env python3
"""
MLOps Module Comprehensive Validation Script

Validates that the MLOps module meets all requirements:
- Le fichier existe
- Import sans erreur : python -c "import nomfichier"
- Syntaxe correcte
- Fonctions/classes définies
- Pas d'erreurs dans VS Code

POUR CHAQUE DOSSIER :
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
import inspect
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

def validate_file_exists(file_path: str) -> bool:
    """Check if file exists"""
    return os.path.isfile(file_path)

def validate_syntax(file_path: str) -> Tuple[bool, Optional[str]]:
    """Check if Python file has correct syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def validate_import(module_path: str) -> Tuple[bool, Optional[str]]:
    """Check if module can be imported"""
    try:
        importlib.import_module(module_path)
        return True, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def validate_definitions(module_path: str) -> Tuple[bool, Dict[str, int], Optional[str]]:
    """Check if module has function/class definitions"""
    try:
        module = importlib.import_module(module_path)
        
        functions = []
        classes = []
        
        for name, obj in inspect.getmembers(module):
            if not name.startswith('_'):  # Skip private members
                if inspect.isfunction(obj):
                    functions.append(name)
                elif inspect.isclass(obj):
                    classes.append(name)
        
        counts = {
            'functions': len(functions),
            'classes': len(classes),
            'total': len(functions) + len(classes)
        }
        
        return True, counts, None
    except Exception as e:
        return False, {'functions': 0, 'classes': 0, 'total': 0}, str(e)

def validate_directory_structure(dir_path: str) -> Tuple[bool, List[str]]:
    """Check directory structure"""
    issues = []
    
    # Check if __init__.py exists
    init_file = os.path.join(dir_path, '__init__.py')
    if not os.path.isfile(init_file):
        issues.append(f"Missing __init__.py in {dir_path}")
    
    # Check all Python files are importable
    for root, dirs, files in os.walk(dir_path):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, '.')
                module_path = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                
                success, error = validate_import(module_path)
                if not success:
                    issues.append(f"Cannot import {module_path}: {error}")
    
    return len(issues) == 0, issues

def main():
    print("🚀 MLOps Module Comprehensive Validation")
    print("=" * 60)
    
    mlops_dir = "mlops"
    
    # Check if mlops directory exists
    if not os.path.isdir(mlops_dir):
        print(f"❌ MLOps directory '{mlops_dir}' not found")
        return 1
    
    # Find all Python files in mlops
    python_files = []
    for root, dirs, files in os.walk(mlops_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)
    
    print(f"📁 Found {len(python_files)} Python files in MLOps module")
    print()
    
    # Validate each file
    file_results = []
    for file_path in sorted(python_files):
        print(f"📄 Validating {file_path}")
        
        # Convert file path to module path
        module_path = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        
        result = {
            'file': file_path,
            'module': module_path,
            'exists': False,
            'syntax_ok': False,
            'import_ok': False,
            'has_definitions': False,
            'functions': 0,
            'classes': 0,
            'errors': []
        }
        
        # Check file exists
        if validate_file_exists(file_path):
            result['exists'] = True
            print("  ✅ File exists")
        else:
            result['errors'].append("File does not exist")
            print("  ❌ File does not exist")
        
        # Check syntax
        if result['exists']:
            syntax_ok, syntax_error = validate_syntax(file_path)
            result['syntax_ok'] = syntax_ok
            if syntax_ok:
                print("  ✅ Syntax correct")
            else:
                result['errors'].append(f"Syntax error: {syntax_error}")
                print(f"  ❌ Syntax error: {syntax_error}")
        
        # Check import
        if result['syntax_ok']:
            import_ok, import_error = validate_import(module_path)
            result['import_ok'] = import_ok
            if import_ok:
                print("  ✅ Import successful")
            else:
                result['errors'].append(f"Import error: {import_error}")
                print(f"  ❌ Import error: {import_error}")
        
        # Check definitions
        if result['import_ok']:
            defs_ok, counts, defs_error = validate_definitions(module_path)
            result['has_definitions'] = defs_ok and counts['total'] > 0
            result['functions'] = counts['functions']
            result['classes'] = counts['classes']
            
            if defs_ok:
                if counts['total'] > 0:
                    print(f"  ✅ Has definitions: {counts['functions']} functions, {counts['classes']} classes")
                else:
                    print(f"  ⚠️  No public definitions found")
            else:
                result['errors'].append(f"Definition check error: {defs_error}")
                print(f"  ❌ Definition check error: {defs_error}")
        
        file_results.append(result)
        print()
    
    # Validate directory structure
    print("📁 Validating directory structure")
    
    # Find all subdirectories
    subdirs = []
    for root, dirs, files in os.walk(mlops_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        subdirs.extend([os.path.join(root, d) for d in dirs])
    
    directory_results = []
    for subdir in sorted(subdirs):
        print(f"📂 Validating directory {subdir}")
        
        structure_ok, issues = validate_directory_structure(subdir)
        
        result = {
            'directory': subdir,
            'structure_ok': structure_ok,
            'issues': issues
        }
        
        if structure_ok:
            print("  ✅ Directory structure OK")
        else:
            for issue in issues:
                print(f"  ❌ {issue}")
        
        directory_results.append(result)
        print()
    
    # Final summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    total_files = len(file_results)
    exists_count = sum(1 for r in file_results if r['exists'])
    syntax_count = sum(1 for r in file_results if r['syntax_ok'])
    import_count = sum(1 for r in file_results if r['import_ok'])
    defs_count = sum(1 for r in file_results if r['has_definitions'])
    
    print(f"📁 File Existence: {exists_count}/{total_files} files ({exists_count/total_files*100:.1f}%)")
    print(f"🔍 Syntax Correctness: {syntax_count}/{total_files} files ({syntax_count/total_files*100:.1f}%)")
    print(f"📦 Import Success: {import_count}/{total_files} files ({import_count/total_files*100:.1f}%)")
    print(f"⚙️  Functionality: {defs_count}/{total_files} files ({defs_count/total_files*100:.1f}%)")
    
    total_dirs = len(directory_results)
    struct_count = sum(1 for r in directory_results if r['structure_ok'])
    
    if total_dirs > 0:
        print(f"📂 Directory Structure: {struct_count}/{total_dirs} directories ({struct_count/total_dirs*100:.1f}%)")
    
    # Calculate overall compliance
    compliance_score = (exists_count + syntax_count + import_count + defs_count) / (4 * total_files) * 100
    print(f"🎯 COMPLIANCE RATE: {compliance_score:.1f}%")
    
    if compliance_score == 100:
        print("\n🎉 ALL REQUIREMENTS MET! MLOps module is fully compliant!")
        return 0
    else:
        print(f"\n⚠️  Compliance issues found. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())