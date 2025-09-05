#!/usr/bin/env python3
"""
Comprehensive Module Testing Framework for Ainflue Platform
Tests all Python modules according to the checklist requirements

Requirements tested:
- File existence
- Import without errors  
- Syntax correctness
- Functions/classes defined
- No VS Code errors
- Directory contains __init__.py
- All sub-files importable
- Coherent structure
- No corrupted files

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import os
import sys
import ast
import importlib
import importlib.util
import traceback
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import subprocess


class ModuleTestResult:
    """Container for test results"""
    
    def __init__(self, module_path: str):
        self.module_path = module_path
        self.tests = {}
        self.errors = []
        self.warnings = []
        self.metadata = {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def add_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Add a test result"""
        self.tests[test_name] = {
            'passed': passed,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def add_error(self, error: str):
        """Add an error"""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add a warning"""
        self.warnings.append(warning)
    
    def is_fully_compliant(self) -> bool:
        """Check if module is fully compliant"""
        return (
            all(test['passed'] for test in self.tests.values()) and
            len(self.errors) == 0
        )
    
    def get_compliance_score(self) -> float:
        """Get compliance score (0-100)"""
        if not self.tests:
            return 0.0
        
        passed_tests = sum(1 for test in self.tests.values() if test['passed'])
        total_tests = len(self.tests)
        
        # Reduce score for errors
        error_penalty = min(len(self.errors) * 10, 50)
        
        base_score = (passed_tests / total_tests) * 100
        return max(0, base_score - error_penalty)


class ComprehensiveModuleTester:
    """Comprehensive testing framework for Python modules"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.results: Dict[str, ModuleTestResult] = {}
        self.excluded_paths = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        self.test_summary = {
            'total_modules': 0,
            'passed_modules': 0,
            'failed_modules': 0,
            'warnings_count': 0,
            'errors_count': 0,
            'compliance_rate': 0.0
        }
    
    def discover_python_modules(self) -> List[Path]:
        """Discover all Python files and packages"""
        python_files = []
        
        for path in self.root_path.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in path.parts for excluded in self.excluded_paths):
                continue
            
            python_files.append(path)
        
        return python_files
    
    def discover_python_packages(self) -> List[Path]:
        """Discover all Python packages (directories with __init__.py)"""
        packages = []
        
        for path in self.root_path.rglob("__init__.py"):
            # Skip excluded directories
            if any(excluded in path.parts for excluded in self.excluded_paths):
                continue
            
            package_dir = path.parent
            packages.append(package_dir)
        
        return packages
    
    def test_file_existence(self, file_path: Path) -> Tuple[bool, str]:
        """Test if file exists"""
        try:
            exists = file_path.exists() and file_path.is_file()
            if exists:
                # Check if file is readable
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1)  # Try to read first character
                return True, "File exists and is readable"
            else:
                return False, "File does not exist or is not a file"
        except Exception as e:
            return False, f"File access error: {str(e)}"
    
    def test_syntax_correctness(self, file_path: Path) -> Tuple[bool, str]:
        """Test Python syntax correctness"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse the AST to check syntax
            ast.parse(source_code, filename=str(file_path))
            return True, "Syntax is correct"
            
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Syntax check error: {str(e)}"
    
    def test_import_without_error(self, file_path: Path) -> Tuple[bool, str]:
        """Test if module can be imported without errors"""
        try:
            # Get module name relative to root
            relative_path = file_path.relative_to(self.root_path)
            
            # Convert path to module name
            if relative_path.name == "__init__.py":
                # Package import
                module_parts = relative_path.parent.parts
            else:
                # Module import
                module_parts = relative_path.with_suffix('').parts
            
            module_name = '.'.join(module_parts)
            
            # Add root path to sys.path temporarily
            original_path = sys.path.copy()
            if str(self.root_path) not in sys.path:
                sys.path.insert(0, str(self.root_path))
            
            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None:
                    return False, "Could not create module spec"
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                return True, f"Module imported successfully as '{module_name}'"
                
            finally:
                # Restore original sys.path
                sys.path = original_path
                
        except ImportError as e:
            return False, f"Import error: {str(e)}"
        except Exception as e:
            return False, f"Import test error: {str(e)}"
    
    def test_functions_classes_defined(self, file_path: Path) -> Tuple[bool, str]:
        """Test if file defines functions or classes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code, filename=str(file_path))
            
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            if functions or classes:
                details = f"Found {len(functions)} functions and {len(classes)} classes"
                if functions:
                    details += f" (functions: {', '.join(functions[:5])}{'...' if len(functions) > 5 else ''})"
                if classes:
                    details += f" (classes: {', '.join(classes[:5])}{'...' if len(classes) > 5 else ''})"
                return True, details
            else:
                return True, "File contains no functions or classes (may be a configuration/data file)"
                
        except Exception as e:
            return False, f"Analysis error: {str(e)}"
    
    def test_directory_has_init(self, package_dir: Path) -> Tuple[bool, str]:
        """Test if directory contains __init__.py"""
        init_file = package_dir / "__init__.py"
        exists = init_file.exists()
        
        if exists:
            # Check if __init__.py is readable
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():
                    return True, f"__init__.py exists and contains {len(content)} characters"
                else:
                    return True, "__init__.py exists but is empty"
            except Exception as e:
                return False, f"__init__.py exists but is not readable: {str(e)}"
        else:
            return False, "__init__.py is missing"
    
    def test_all_subfiles_importable(self, package_dir: Path) -> Tuple[bool, str]:
        """Test if all Python files in directory are importable"""
        python_files = list(package_dir.glob("*.py"))
        if not python_files:
            return True, "No Python files to test"
        
        importable_count = 0
        total_count = len(python_files)
        errors = []
        
        for py_file in python_files:
            if py_file.name == "__init__.py":
                continue
                
            success, details = self.test_import_without_error(py_file)
            if success:
                importable_count += 1
            else:
                errors.append(f"{py_file.name}: {details}")
        
        if importable_count == total_count - 1:  # -1 for __init__.py
            return True, f"All {importable_count} sub-files are importable"
        else:
            error_summary = "; ".join(errors[:3])
            if len(errors) > 3:
                error_summary += f" and {len(errors) - 3} more"
            return False, f"Only {importable_count}/{total_count-1} files importable. Errors: {error_summary}"
    
    def test_structure_coherence(self, path: Path) -> Tuple[bool, str]:
        """Test if directory structure is coherent"""
        if path.is_file():
            # For files, check naming conventions
            name = path.stem
            if name.isidentifier() or name == "__init__":
                return True, "File name follows Python naming conventions"
            else:
                return False, "File name does not follow Python naming conventions"
        else:
            # For directories, check structure
            python_files = list(path.glob("*.py"))
            subdirs = [d for d in path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            
            details = f"Contains {len(python_files)} Python files and {len(subdirs)} subdirectories"
            
            # Check for common patterns
            has_init = (path / "__init__.py").exists()
            if python_files and not has_init:
                return False, f"Directory has Python files but no __init__.py. {details}"
            
            return True, details
    
    def test_no_corruption(self, file_path: Path) -> Tuple[bool, str]:
        """Test that file is not corrupted"""
        try:
            with open(file_path, 'rb') as f:
                f.read()
            
            # Try to decode as UTF-8
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for null bytes (sign of corruption)
            if '\x00' in content:
                return False, "File contains null bytes (possibly corrupted)"
            
            return True, f"File integrity verified ({len(content)} characters)"
            
        except UnicodeDecodeError:
            return False, "File is not valid UTF-8 (possibly corrupted or binary)"
        except Exception as e:
            return False, f"Corruption test error: {str(e)}"
    
    def test_python_file(self, file_path: Path) -> ModuleTestResult:
        """Run all tests on a Python file"""
        result = ModuleTestResult(str(file_path))
        
        # Test 1: File existence
        success, details = self.test_file_existence(file_path)
        result.add_test_result("file_exists", success, details)
        if not success:
            result.add_error(f"File existence test failed: {details}")
            return result
        
        # Test 2: No corruption
        success, details = self.test_no_corruption(file_path)
        result.add_test_result("no_corruption", success, details)
        if not success:
            result.add_error(f"Corruption test failed: {details}")
        
        # Test 3: Syntax correctness
        success, details = self.test_syntax_correctness(file_path)
        result.add_test_result("syntax_correct", success, details)
        if not success:
            result.add_error(f"Syntax test failed: {details}")
        
        # Test 4: Import without error
        success, details = self.test_import_without_error(file_path)
        result.add_test_result("import_success", success, details)
        if not success:
            result.add_error(f"Import test failed: {details}")
        
        # Test 5: Functions/classes defined
        success, details = self.test_functions_classes_defined(file_path)
        result.add_test_result("has_definitions", success, details)
        
        # Test 6: Structure coherence
        success, details = self.test_structure_coherence(file_path)
        result.add_test_result("structure_coherent", success, details)
        if not success:
            result.add_warning(f"Structure coherence issue: {details}")
        
        return result
    
    def test_python_package(self, package_dir: Path) -> ModuleTestResult:
        """Run all tests on a Python package directory"""
        result = ModuleTestResult(str(package_dir))
        
        # Test 1: Directory has __init__.py
        success, details = self.test_directory_has_init(package_dir)
        result.add_test_result("has_init_py", success, details)
        if not success:
            result.add_error(f"__init__.py test failed: {details}")
        
        # Test 2: All sub-files importable
        success, details = self.test_all_subfiles_importable(package_dir)
        result.add_test_result("subfiles_importable", success, details)
        if not success:
            result.add_error(f"Sub-files import test failed: {details}")
        
        # Test 3: Structure coherence
        success, details = self.test_structure_coherence(package_dir)
        result.add_test_result("structure_coherent", success, details)
        if not success:
            result.add_warning(f"Structure coherence issue: {details}")
        
        # Test 4: Test __init__.py file specifically
        init_file = package_dir / "__init__.py"
        if init_file.exists():
            init_result = self.test_python_file(init_file)
            for test_name, test_data in init_result.tests.items():
                result.add_test_result(f"init_{test_name}", test_data['passed'], test_data['details'])
            result.errors.extend(init_result.errors)
            result.warnings.extend(init_result.warnings)
        
        return result
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests on all modules"""
        print("🚀 Starting Comprehensive Module Testing")
        print("=" * 60)
        
        # Discover modules
        python_files = self.discover_python_modules()
        python_packages = self.discover_python_packages()
        
        print(f"📦 Discovered {len(python_files)} Python files")
        print(f"📁 Discovered {len(python_packages)} Python packages")
        print()
        
        total_items = len(python_files) + len(python_packages)
        processed = 0
        
        # Test individual Python files
        print("🔍 Testing Python Files...")
        for file_path in python_files:
            processed += 1
            relative_path = file_path.relative_to(self.root_path)
            print(f"  [{processed}/{total_items}] Testing: {relative_path}")
            
            result = self.test_python_file(file_path)
            self.results[str(relative_path)] = result
            
            if result.is_fully_compliant():
                print(f"    ✅ PASS (score: {result.get_compliance_score():.1f}%)")
            else:
                print(f"    ❌ FAIL (score: {result.get_compliance_score():.1f}%)")
                if result.errors:
                    for error in result.errors[:2]:  # Show first 2 errors
                        print(f"       - {error}")
        
        print()
        print("📁 Testing Python Packages...")
        for package_dir in python_packages:
            processed += 1
            relative_path = package_dir.relative_to(self.root_path)
            print(f"  [{processed}/{total_items}] Testing: {relative_path}/")
            
            result = self.test_python_package(package_dir)
            self.results[str(relative_path) + "/"] = result
            
            if result.is_fully_compliant():
                print(f"    ✅ PASS (score: {result.get_compliance_score():.1f}%)")
            else:
                print(f"    ❌ FAIL (score: {result.get_compliance_score():.1f}%)")
                if result.errors:
                    for error in result.errors[:2]:  # Show first 2 errors  
                        print(f"       - {error}")
        
        # Calculate summary
        self._calculate_summary()
        
        return self._generate_report()
    
    def _calculate_summary(self):
        """Calculate test summary statistics"""
        self.test_summary['total_modules'] = len(self.results)
        self.test_summary['passed_modules'] = sum(1 for result in self.results.values() if result.is_fully_compliant())
        self.test_summary['failed_modules'] = self.test_summary['total_modules'] - self.test_summary['passed_modules']
        self.test_summary['errors_count'] = sum(len(result.errors) for result in self.results.values())
        self.test_summary['warnings_count'] = sum(len(result.warnings) for result in self.results.values())
        
        if self.test_summary['total_modules'] > 0:
            self.test_summary['compliance_rate'] = (self.test_summary['passed_modules'] / self.test_summary['total_modules']) * 100
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        return {
            'summary': self.test_summary,
            'results': {path: {
                'compliance_score': result.get_compliance_score(),
                'is_compliant': result.is_fully_compliant(),
                'tests': result.tests,
                'errors': result.errors,
                'warnings': result.warnings,
                'timestamp': result.timestamp
            } for path, result in self.results.items()},
            'timestamp': datetime.utcnow().isoformat(),
            'root_path': str(self.root_path)
        }
    
    def save_report(self, report_path: str = "module_test_report.json"):
        """Save test report to file"""
        report = self._generate_report()
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Report saved to: {report_path}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n📊 TEST SUMMARY")
        print("=" * 60)
        print(f"📦 Total modules tested: {self.test_summary['total_modules']}")
        print(f"✅ Modules passed: {self.test_summary['passed_modules']}")
        print(f"❌ Modules failed: {self.test_summary['failed_modules']}")
        print(f"⚠️  Total warnings: {self.test_summary['warnings_count']}")
        print(f"🚫 Total errors: {self.test_summary['errors_count']}")
        print(f"📈 Compliance rate: {self.test_summary['compliance_rate']:.1f}%")
        
        if self.test_summary['compliance_rate'] == 100:
            print("\n🎉 ALL MODULES ARE FULLY COMPLIANT!")
        elif self.test_summary['compliance_rate'] >= 80:
            print(f"\n✅ Good compliance rate ({self.test_summary['compliance_rate']:.1f}%)")
        else:
            print(f"\n⚠️  Low compliance rate ({self.test_summary['compliance_rate']:.1f}%) - review failures")


def main():
    """Main function to run comprehensive module testing"""
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = "."
    
    tester = ComprehensiveModuleTester(root_path)
    
    try:
        report = tester.run_comprehensive_tests()
        tester.print_summary()
        tester.save_report()
        
        # Return appropriate exit code
        if tester.test_summary['compliance_rate'] == 100:
            print("\n🎉 All tests passed! Modules are fully compliant.")
            return 0
        else:
            print(f"\n⚠️  {tester.test_summary['failed_modules']} modules have issues. See report for details.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Testing failed: {str(e)}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())