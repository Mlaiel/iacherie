#!/usr/bin/env python3
"""
Repository-Wide Module Validation Script for Ainflue Platform
Validates ALL Python modules according to the checklist requirements

This script validates the entire repository systematically:
- File existence for all Python files
- Import capability via subprocess (avoiding conflicts)
- Syntax correctness 
- Directory structure compliance
- Function/class definitions analysis
- Generate comprehensive reports

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import os
import sys
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
from collections import defaultdict


class RepositoryValidator:
    """Repository-wide validation for all Python modules"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.results = {}
        self.summary = defaultdict(int)
        self.excluded_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', 'dist', 'build'}
        
    def discover_all_modules(self) -> Dict[str, List[Path]]:
        """Discover all Python modules in the repository"""
        discovered = {
            'python_files': [],
            'python_packages': [],
            'directories': []
        }
        
        print("🔍 Discovering Python modules...")
        
        # Find all Python files
        for py_file in self.root_path.rglob("*.py"):
            if any(excluded in py_file.parts for excluded in self.excluded_dirs):
                continue
            discovered['python_files'].append(py_file)
        
        # Find all Python packages (directories with __init__.py)
        for init_file in self.root_path.rglob("__init__.py"):
            if any(excluded in init_file.parts for excluded in self.excluded_dirs):
                continue
            package_dir = init_file.parent
            discovered['python_packages'].append(package_dir)
        
        # Find all directories that might contain Python code
        for directory in self.root_path.rglob("*"):
            if directory.is_dir() and not any(excluded in directory.parts for excluded in self.excluded_dirs):
                if any(directory.glob("*.py")):
                    discovered['directories'].append(directory)
        
        print(f"  📦 Found {len(discovered['python_files'])} Python files")
        print(f"  📁 Found {len(discovered['python_packages'])} Python packages")
        print(f"  🗂️  Found {len(discovered['directories'])} directories with Python code")
        
        return discovered
    
    def validate_file_existence(self, file_path: Path) -> Tuple[bool, str]:
        """Validate file exists and is accessible"""
        try:
            if not file_path.exists():
                return False, "File does not exist"
            
            if not file_path.is_file():
                return False, "Path is not a file"
            
            # Check if readable
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for obvious corruption
            if '\x00' in content:
                return False, "File contains null bytes (possibly corrupted)"
            
            return True, f"File exists and readable ({len(content)} chars)"
        
        except UnicodeDecodeError:
            return False, "File is not valid UTF-8"
        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, f"Access error: {str(e)}"
    
    def validate_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Validate Python syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to check syntax
            tree = ast.parse(content, filename=str(file_path))
            return True, "Syntax correct"
        
        except SyntaxError as e:
            return False, f"Syntax error line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Syntax check error: {str(e)}"
    
    def validate_import_capability(self, file_path: Path) -> Tuple[bool, str]:
        """Test if file can be imported using subprocess"""
        try:
            # Calculate module path relative to root
            relative_path = file_path.relative_to(self.root_path)
            
            # Convert to module path
            if relative_path.name == "__init__.py":
                module_parts = relative_path.parent.parts
            else:
                module_parts = relative_path.with_suffix('').parts
            
            if not module_parts:
                return False, "Cannot determine module path"
            
            module_name = '.'.join(module_parts)
            
            # Use subprocess to test import
            cmd = [sys.executable, '-c', f'import {module_name}']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.root_path)
            )
            
            if result.returncode == 0:
                return True, f"'{module_name}' imports successfully"
            else:
                error_msg = (result.stderr or result.stdout or "Unknown error").strip()
                # Truncate very long error messages
                if len(error_msg) > 200:
                    error_msg = error_msg[:200] + "..."
                return False, f"Import failed: {error_msg}"
        
        except subprocess.TimeoutExpired:
            return False, "Import test timed out"
        except Exception as e:
            return False, f"Import test error: {str(e)}"
    
    def analyze_definitions(self, file_path: Path) -> Tuple[bool, str]:
        """Analyze functions, classes, and imports in file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            functions = []
            classes = []
            imports = []
            variables = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append("import")
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append(target.id)
            
            details = f"Functions: {len(functions)}, Classes: {len(classes)}, Imports: {len(imports)}"
            
            if functions:
                example_functions = functions[:3]
                details += f" (functions: {', '.join(example_functions)}{'...' if len(functions) > 3 else ''})"
            
            if classes:
                example_classes = classes[:3]
                details += f" (classes: {', '.join(example_classes)}{'...' if len(classes) > 3 else ''})"
            
            return True, details
        
        except Exception as e:
            return False, f"Definition analysis error: {str(e)}"
    
    def validate_directory_structure(self, dir_path: Path) -> Tuple[bool, str]:
        """Validate directory structure"""
        try:
            if not dir_path.is_dir():
                return False, "Not a directory"
            
            python_files = list(dir_path.glob("*.py"))
            init_file = dir_path / "__init__.py"
            has_init = init_file.exists()
            subdirs = [d for d in dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            
            details = f"{len(python_files)} .py files, {len(subdirs)} subdirs, __init__.py: {has_init}"
            
            # Check naming conventions
            if not dir_path.name.replace('_', '').replace('-', '').isalnum():
                return False, f"Directory name doesn't follow conventions. {details}"
            
            # If has Python files, should have __init__.py for packages
            if len(python_files) > 1 and not has_init:
                return False, f"Multiple .py files but no __init__.py. {details}"
            
            return True, details
        
        except Exception as e:
            return False, f"Directory validation error: {str(e)}"
    
    def validate_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single Python file"""
        result = {
            'file_path': str(file_path.relative_to(self.root_path)),
            'tests': {},
            'score': 0,
            'passed': False
        }
        
        tests_passed = 0
        total_tests = 5
        
        # Test 1: File existence
        success, details = self.validate_file_existence(file_path)
        result['tests']['file_existence'] = {'passed': success, 'details': details}
        if success:
            tests_passed += 1
        
        # Test 2: Syntax validation (only if file exists)
        if success:
            success, details = self.validate_syntax(file_path)
            result['tests']['syntax'] = {'passed': success, 'details': details}
            if success:
                tests_passed += 1
        else:
            result['tests']['syntax'] = {'passed': False, 'details': 'File not accessible'}
        
        # Test 3: Import capability (only if syntax is correct)
        if result['tests']['syntax']['passed']:
            success, details = self.validate_import_capability(file_path)
            result['tests']['import'] = {'passed': success, 'details': details}
            if success:
                tests_passed += 1
        else:
            result['tests']['import'] = {'passed': False, 'details': 'Syntax errors prevent import test'}
        
        # Test 4: Definition analysis (only if file exists)
        if result['tests']['file_existence']['passed']:
            success, details = self.analyze_definitions(file_path)
            result['tests']['definitions'] = {'passed': success, 'details': details}
            if success:
                tests_passed += 1
        else:
            result['tests']['definitions'] = {'passed': False, 'details': 'File not accessible'}
        
        # Test 5: Name conventions
        name_valid = file_path.stem.replace('_', '').replace('-', '').isalnum() or file_path.stem == "__init__"
        result['tests']['naming'] = {
            'passed': name_valid,
            'details': f"File name {'follows' if name_valid else 'violates'} Python conventions"
        }
        if name_valid:
            tests_passed += 1
        
        result['score'] = (tests_passed / total_tests) * 100
        result['passed'] = tests_passed == total_tests
        
        return result
    
    def validate_single_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Validate a single directory"""
        result = {
            'dir_path': str(dir_path.relative_to(self.root_path)),
            'tests': {},
            'score': 0,
            'passed': False
        }
        
        tests_passed = 0
        total_tests = 3
        
        # Test 1: Directory structure
        success, details = self.validate_directory_structure(dir_path)
        result['tests']['structure'] = {'passed': success, 'details': details}
        if success:
            tests_passed += 1
        
        # Test 2: __init__.py presence (if has Python files)
        python_files = list(dir_path.glob("*.py"))
        init_file = dir_path / "__init__.py"
        
        if python_files:
            has_init = init_file.exists()
            result['tests']['init_file'] = {
                'passed': has_init,
                'details': f"{'Has' if has_init else 'Missing'} __init__.py with {len(python_files)} .py files"
            }
            if has_init:
                tests_passed += 1
        else:
            result['tests']['init_file'] = {'passed': True, 'details': 'No Python files - __init__.py not required'}
            tests_passed += 1
        
        # Test 3: Naming conventions
        name_valid = dir_path.name.replace('_', '').replace('-', '').replace('.', '').isalnum()
        result['tests']['naming'] = {
            'passed': name_valid,
            'details': f"Directory name {'follows' if name_valid else 'violates'} conventions"
        }
        if name_valid:
            tests_passed += 1
        
        result['score'] = (tests_passed / total_tests) * 100
        result['passed'] = tests_passed == total_tests
        
        return result
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run validation on entire repository"""
        print("🚀 Starting Repository-Wide Module Validation")
        print("=" * 60)
        
        # Discover all modules
        discovered = self.discover_all_modules()
        
        validation_results = {
            'files': {},
            'directories': {},
            'packages': {},
            'summary': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        total_items = (
            len(discovered['python_files']) + 
            len(discovered['python_packages']) + 
            len(discovered['directories'])
        )
        
        processed = 0
        
        # Validate Python files
        print(f"\n📋 Validating {len(discovered['python_files'])} Python files...")
        for file_path in discovered['python_files']:
            processed += 1
            relative_path = str(file_path.relative_to(self.root_path))
            
            if processed % 10 == 0 or processed <= 10:
                print(f"  [{processed}/{total_items}] {relative_path}")
            
            result = self.validate_single_file(file_path)
            validation_results['files'][relative_path] = result
            
            # Update summary
            if result['passed']:
                self.summary['files_passed'] += 1
            else:
                self.summary['files_failed'] += 1
        
        # Validate directories
        print(f"\n📁 Validating {len(discovered['directories'])} directories...")
        for dir_path in discovered['directories']:
            processed += 1
            relative_path = str(dir_path.relative_to(self.root_path))
            
            if processed % 10 == 0:
                print(f"  [{processed}/{total_items}] {relative_path}/")
            
            result = self.validate_single_directory(dir_path)
            validation_results['directories'][relative_path] = result
            
            # Update summary
            if result['passed']:
                self.summary['dirs_passed'] += 1
            else:
                self.summary['dirs_failed'] += 1
        
        # Validate packages specifically
        print(f"\n📦 Validating {len(discovered['python_packages'])} Python packages...")
        for package_dir in discovered['python_packages']:
            processed += 1
            relative_path = str(package_dir.relative_to(self.root_path))
            
            if processed % 10 == 0:
                print(f"  [{processed}/{total_items}] {relative_path}/ (package)")
            
            result = self.validate_single_directory(package_dir)
            validation_results['packages'][relative_path] = result
            
            # Update summary
            if result['passed']:
                self.summary['packages_passed'] += 1
            else:
                self.summary['packages_failed'] += 1
        
        # Calculate overall summary
        total_files = len(validation_results['files'])
        total_dirs = len(validation_results['directories'])
        total_packages = len(validation_results['packages'])
        
        passed_files = self.summary['files_passed']
        passed_dirs = self.summary['dirs_passed'] 
        passed_packages = self.summary['packages_passed']
        
        validation_results['summary'] = {
            'total_files': total_files,
            'total_directories': total_dirs,
            'total_packages': total_packages,
            'total_items': total_files + total_dirs + total_packages,
            'passed_files': passed_files,
            'passed_directories': passed_dirs,
            'passed_packages': passed_packages,
            'failed_files': total_files - passed_files,
            'failed_directories': total_dirs - passed_dirs,
            'failed_packages': total_packages - passed_packages,
            'overall_compliance_rate': (
                (passed_files + passed_dirs + passed_packages) / 
                (total_files + total_dirs + total_packages) * 100
            ) if (total_files + total_dirs + total_packages) > 0 else 0
        }
        
        return validation_results
    
    def print_summary_report(self, results: Dict[str, Any]):
        """Print summary report"""
        print("\n📊 REPOSITORY VALIDATION SUMMARY")
        print("=" * 60)
        
        summary = results['summary']
        
        print(f"📋 Files tested: {summary['total_files']}")
        print(f"  ✅ Passed: {summary['passed_files']}")
        print(f"  ❌ Failed: {summary['failed_files']}")
        
        print(f"\n📁 Directories tested: {summary['total_directories']}")
        print(f"  ✅ Passed: {summary['passed_directories']}")
        print(f"  ❌ Failed: {summary['failed_directories']}")
        
        print(f"\n📦 Packages tested: {summary['total_packages']}")
        print(f"  ✅ Passed: {summary['passed_packages']}")
        print(f"  ❌ Failed: {summary['failed_packages']}")
        
        print(f"\n🎯 Overall Compliance Rate: {summary['overall_compliance_rate']:.1f}%")
        
        # Show top failures if any
        if summary['failed_files'] > 0:
            print(f"\n⚠️  Top File Failures:")
            failed_files = [
                (path, result) for path, result in results['files'].items()
                if not result['passed']
            ]
            for i, (path, result) in enumerate(failed_files[:5]):
                print(f"  {i+1}. {path} (score: {result['score']:.1f}%)")
        
        if summary['overall_compliance_rate'] >= 90:
            print(f"\n🎉 Excellent compliance! Repository is in great shape.")
        elif summary['overall_compliance_rate'] >= 70:
            print(f"\n✅ Good compliance rate. Some modules need attention.")
        else:
            print(f"\n⚠️  Low compliance rate. Many modules need fixes.")
    
    def save_detailed_report(self, results: Dict[str, Any], filename: str = "repository_validation_report.json"):
        """Save detailed report to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Detailed report saved to: {filename}")


def main():
    """Main validation function"""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = "."
    
    validator = RepositoryValidator(root_path)
    
    try:
        results = validator.run_full_validation()
        validator.print_summary_report(results)
        validator.save_detailed_report(results)
        
        # Return exit code based on compliance rate
        compliance_rate = results['summary']['overall_compliance_rate']
        if compliance_rate >= 90:
            print("\n🎉 Repository validation successful!")
            return 0
        elif compliance_rate >= 70:
            print("\n⚠️  Repository has some issues but is mostly compliant.")
            return 1
        else:
            print("\n❌ Repository has significant compliance issues.")
            return 2
        
    except KeyboardInterrupt:
        print("\n⏹️  Validation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())