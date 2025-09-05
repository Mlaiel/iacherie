#!/usr/bin/env python3
"""
Simple Module Validation Script for Ainflue Platform
Validates modules according to the specific checklist requirements with practical approach

This script focuses on practical validation that works with the existing codebase structure.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import os
import sys
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple


class SimpleModuleValidator:
    """Simple validator for module compliance"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.results = []
        
    def validate_file_existence(self, file_path: Path) -> Tuple[bool, str]:
        """Validate file exists and is readable"""
        try:
            if not file_path.exists():
                return False, "File does not exist"
            
            if not file_path.is_file():
                return False, "Path is not a file"
            
            # Try to read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return True, f"File exists and readable ({len(content)} characters)"
        except Exception as e:
            return False, f"File access error: {str(e)}"
    
    def validate_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Validate Python syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to check syntax
            ast.parse(content, filename=str(file_path))
            return True, "Syntax is correct"
        
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Syntax validation error: {str(e)}"
    
    def validate_import_via_python(self, module_path: str) -> Tuple[bool, str]:
        """Validate module can be imported using subprocess"""
        try:
            # Use subprocess to avoid import conflicts
            cmd = [sys.executable, '-c', f'import {module_path}']
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                cwd=str(self.root_path)
            )
            
            if result.returncode == 0:
                return True, f"Module '{module_path}' imports successfully"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, f"Import failed: {error_msg}"
        
        except subprocess.TimeoutExpired:
            return False, "Import test timed out"
        except Exception as e:
            return False, f"Import test error: {str(e)}"
    
    def analyze_definitions(self, file_path: Path) -> Tuple[bool, str]:
        """Analyze functions and classes defined in file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.dump(node))
            
            details = f"Functions: {len(functions)}, Classes: {len(classes)}, Imports: {len(imports)}"
            
            if functions:
                details += f" (functions: {', '.join(functions[:3])}{'...' if len(functions) > 3 else ''})"
            if classes:
                details += f" (classes: {', '.join(classes[:3])}{'...' if len(classes) > 3 else ''})"
            
            return True, details
        
        except Exception as e:
            return False, f"Definition analysis error: {str(e)}"
    
    def validate_directory_structure(self, dir_path: Path) -> Tuple[bool, str]:
        """Validate directory has proper structure"""
        try:
            if not dir_path.is_dir():
                return False, "Path is not a directory"
            
            init_file = dir_path / "__init__.py"
            has_init = init_file.exists()
            
            python_files = list(dir_path.glob("*.py"))
            subdirs = [d for d in dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            
            details = f"Python files: {len(python_files)}, Subdirs: {len(subdirs)}, Has __init__.py: {has_init}"
            
            if python_files and not has_init:
                return False, f"Directory has Python files but no __init__.py. {details}"
            
            return True, details
        
        except Exception as e:
            return False, f"Directory validation error: {str(e)}"
    
    def validate_core_module(self) -> Dict[str, Any]:
        """Validate the core module specifically"""
        print("🚀 Validating Core Module")
        print("=" * 50)
        
        core_dir = self.root_path / "core"
        required_files = [
            "core/__init__.py",
            "core/logging.py", 
            "core/middleware.py",
            "core/security.py",
            "core/auth.py"
        ]
        
        results = {
            'module_name': 'core',
            'tests': {},
            'summary': {'passed': 0, 'failed': 0, 'total': 0}
        }
        
        # Test 1: Directory structure
        print("📁 Testing directory structure...")
        success, details = self.validate_directory_structure(core_dir)
        results['tests']['directory_structure'] = {'passed': success, 'details': details}
        print(f"  {'✅' if success else '❌'} Directory structure: {details}")
        
        # Test 2: File existence
        print("\n📋 Testing file existence...")
        file_tests = {}
        for file_path in required_files:
            full_path = self.root_path / file_path
            success, details = self.validate_file_existence(full_path)
            file_tests[file_path] = {'passed': success, 'details': details}
            print(f"  {'✅' if success else '❌'} {file_path}: {details}")
        
        results['tests']['file_existence'] = file_tests
        
        # Test 3: Syntax validation
        print("\n🔍 Testing syntax correctness...")
        syntax_tests = {}
        for file_path in required_files:
            full_path = self.root_path / file_path
            if full_path.exists():
                success, details = self.validate_syntax(full_path)
                syntax_tests[file_path] = {'passed': success, 'details': details}
                print(f"  {'✅' if success else '❌'} {file_path}: {details}")
            else:
                syntax_tests[file_path] = {'passed': False, 'details': 'File not found'}
                print(f"  ❌ {file_path}: File not found")
        
        results['tests']['syntax_validation'] = syntax_tests
        
        # Test 4: Import validation
        print("\n📦 Testing import capability...")
        import_tests = {}
        
        # Test main core module import
        success, details = self.validate_import_via_python('core')
        import_tests['core'] = {'passed': success, 'details': details}
        print(f"  {'✅' if success else '❌'} core: {details}")
        
        # Test individual submodules
        submodules = ['core.logging', 'core.middleware', 'core.security', 'core.auth']
        for module in submodules:
            success, details = self.validate_import_via_python(module)
            import_tests[module] = {'passed': success, 'details': details}
            print(f"  {'✅' if success else '❌'} {module}: {details}")
        
        results['tests']['import_validation'] = import_tests
        
        # Test 5: Definition analysis
        print("\n⚙️ Testing function/class definitions...")
        definition_tests = {}
        for file_path in required_files:
            full_path = self.root_path / file_path
            if full_path.exists():
                success, details = self.analyze_definitions(full_path)
                definition_tests[file_path] = {'passed': success, 'details': details}
                print(f"  {'✅' if success else '❌'} {file_path}: {details}")
            else:
                definition_tests[file_path] = {'passed': False, 'details': 'File not found'}
                print(f"  ❌ {file_path}: File not found")
        
        results['tests']['definition_analysis'] = definition_tests
        
        # Calculate summary
        total_tests = 0
        passed_tests = 0
        
        for test_category in results['tests'].values():
            if isinstance(test_category, dict):
                for test_result in test_category.values():
                    if isinstance(test_result, dict) and 'passed' in test_result:
                        total_tests += 1
                        if test_result['passed']:
                            passed_tests += 1
        
        results['summary'] = {
            'total': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'compliance_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        return results
    
    def print_final_report(self, results: Dict[str, Any]):
        """Print final validation report"""
        print("\n📊 CORE MODULE VALIDATION SUMMARY")
        print("=" * 50)
        
        summary = results['summary']
        print(f"📋 Total tests: {summary['total']}")
        print(f"✅ Passed tests: {summary['passed']}")
        print(f"❌ Failed tests: {summary['failed']}")
        print(f"📈 Compliance rate: {summary['compliance_rate']:.1f}%")
        
        print("\n🎯 CHECKLIST VALIDATION:")
        
        # Check each requirement
        all_files_exist = all(
            test['passed'] for test in results['tests']['file_existence'].values()
        )
        print(f"  {'✅' if all_files_exist else '❌'} All required files exist")
        
        all_syntax_correct = all(
            test['passed'] for test in results['tests']['syntax_validation'].values()
        )
        print(f"  {'✅' if all_syntax_correct else '❌'} All syntax is correct")
        
        all_imports_work = all(
            test['passed'] for test in results['tests']['import_validation'].values()
        )
        print(f"  {'✅' if all_imports_work else '❌'} All imports work without error")
        
        has_proper_structure = results['tests']['directory_structure']['passed']
        print(f"  {'✅' if has_proper_structure else '❌'} Directory has proper structure")
        
        all_definitions_analyzed = all(
            test['passed'] for test in results['tests']['definition_analysis'].values()
        )
        print(f"  {'✅' if all_definitions_analyzed else '❌'} All definitions analyzed successfully")
        
        # Final verdict
        is_fully_compliant = (
            all_files_exist and 
            all_syntax_correct and 
            all_imports_work and 
            has_proper_structure and
            all_definitions_analyzed
        )
        
        print(f"\n🏆 FINAL RESULT:")
        if is_fully_compliant:
            print("🎉 CORE MODULE IS FULLY COMPLIANT!")
            print("✅ Meets all checklist requirements")
            return True
        else:
            print("⚠️  CORE MODULE HAS COMPLIANCE ISSUES")
            print("❌ Some requirements not met - see details above")
            return False


def main():
    """Main validation function"""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = "."
    
    validator = SimpleModuleValidator(root_path)
    
    try:
        results = validator.validate_core_module()
        is_compliant = validator.print_final_report(results)
        
        return 0 if is_compliant else 1
        
    except Exception as e:
        print(f"\n💥 Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())