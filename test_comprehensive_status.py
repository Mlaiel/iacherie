#!/usr/bin/env python3
"""Comprehensive status test for Ainflue platform after syntax fixes."""

import sys
import traceback
from pathlib import Path

def test_core_imports():
    """Test critical module imports."""
    print("🧪 Testing Core Module Imports...")
    results = {}
    
    # Test 1: Business logic core
    try:
        import business_logic_core
        from business_logic_core import CreatorType
        results['business_logic_core'] = '✅ SUCCESS'
    except Exception as e:
        results['business_logic_core'] = f'❌ {str(e)[:100]}'
    
    # Test 2: Simple agents
    try:
        import simple_agents
        results['simple_agents'] = '✅ SUCCESS'
    except Exception as e:
        results['simple_agents'] = f'❌ {str(e)[:100]}'
    
    # Test 3: Data management validation
    try:
        from data_management.validation import ValidationManager
        vm = ValidationManager()
        results['validation_manager'] = '✅ SUCCESS'
    except Exception as e:
        results['validation_manager'] = f'❌ {str(e)[:100]}'
    
    # Test 4: Data management transformers
    try:
        from data_management.transformers import TransformationManager  
        tm = TransformationManager()
        results['transformation_manager'] = '✅ SUCCESS'
    except Exception as e:
        results['transformation_manager'] = f'❌ {str(e)[:100]}'
    
    # Test 5: Fingerprinting
    try:
        from data_management.fingerprinting import FingerprintingEngine
        fe = FingerprintingEngine()
        results['fingerprinting_engine'] = '✅ SUCCESS'
    except Exception as e:
        results['fingerprinting_engine'] = f'❌ {str(e)[:100]}'
    
    return results

def test_syntax_health():
    """Test overall syntax health."""
    print("🔍 Testing Syntax Health...")
    import ast
    import glob
    
    total_files = 0
    valid_files = 0
    errors = []
    
    # Test a sample of files
    for py_file in glob.glob('**/*.py', recursive=True)[:200]:  # Test 200 files
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            valid_files += 1
        except Exception as e:
            errors.append((py_file, str(e)[:100]))
        total_files += 1
    
    success_rate = (valid_files / total_files * 100) if total_files > 0 else 0
    
    return {
        'total_files_tested': total_files,
        'valid_files': valid_files,
        'syntax_errors': len(errors),
        'success_rate': f"{success_rate:.1f}%",
        'sample_errors': errors[:5]  # Show first 5 errors
    }

def test_pytest_readiness():
    """Test if pytest can collect tests."""
    print("🧪 Testing PyTest Readiness...")
    import subprocess
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', '--collect-only', '--quiet'
        ], capture_output=True, text=True, timeout=60)
        
        output = result.stdout + result.stderr
        
        # Extract key metrics
        if 'collected' in output:
            # Parse collected tests and errors
            lines = output.split('\n')
            for line in lines:
                if 'collected' in line and ('error' in line or 'warning' in line):
                    return {
                        'status': '⚠️ PARTIAL',
                        'details': line.strip(),
                        'exit_code': result.returncode
                    }
                elif 'collected' in line:
                    return {
                        'status': '✅ SUCCESS',
                        'details': line.strip(),
                        'exit_code': result.returncode
                    }
        
        return {
            'status': '❌ FAILED',
            'details': f"Exit code: {result.returncode}",
            'exit_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            'status': '⏱️ TIMEOUT',
            'details': 'Test collection took too long',
            'exit_code': 124
        }
    except Exception as e:
        return {
            'status': '❌ ERROR',
            'details': str(e)[:100],
            'exit_code': 1
        }

def main():
    """Main test runner."""
    print("🚀 COMPREHENSIVE AINFLUE STATUS TEST")
    print("=" * 50)
    
    # Test 1: Core imports
    print("\n1️⃣ CORE MODULE IMPORTS")
    import_results = test_core_imports()
    for module, status in import_results.items():
        print(f"   {module}: {status}")
    
    # Test 2: Syntax health
    print("\n2️⃣ SYNTAX HEALTH CHECK")
    syntax_results = test_syntax_health()
    print(f"   Files tested: {syntax_results['total_files_tested']}")
    print(f"   Valid files: {syntax_results['valid_files']}")
    print(f"   Success rate: {syntax_results['success_rate']}")
    print(f"   Syntax errors: {syntax_results['syntax_errors']}")
    
    if syntax_results['sample_errors']:
        print("   Sample errors:")
        for file, error in syntax_results['sample_errors']:
            print(f"     • {file}: {error}")
    
    # Test 3: PyTest readiness
    print("\n3️⃣ PYTEST READINESS")
    pytest_results = test_pytest_readiness()
    print(f"   Status: {pytest_results['status']}")
    print(f"   Details: {pytest_results['details']}")
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 50)
    
    success_modules = sum(1 for status in import_results.values() if '✅' in status)
    total_modules = len(import_results)
    
    print(f"Core modules working: {success_modules}/{total_modules}")
    print(f"Syntax health: {syntax_results['success_rate']}")
    print(f"PyTest status: {pytest_results['status']}")
    
    overall_health = "🟢 GOOD" if success_modules >= 3 and float(syntax_results['success_rate'].rstrip('%')) >= 90 else "🟡 NEEDS WORK"
    print(f"Overall health: {overall_health}")
    
    return 0 if overall_health == "🟢 GOOD" else 1

if __name__ == "__main__":
    sys.exit(main())