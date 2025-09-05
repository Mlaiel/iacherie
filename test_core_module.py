#!/usr/bin/env python3
"""
Core Module Specific Test Script for Ainflue Platform
Validates the core module according to checklist requirements

Tests:
- core/__init__.py
- core/logging.py  
- core/middleware.py
- core/security.py
- core/auth.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import sys
import os
import traceback
from typing import Dict, Any, List

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_core_module_imports() -> Dict[str, Any]:
    """Test importing all core module components"""
    test_results = {
        'imports': {},
        'errors': [],
        'summary': {}
    }
    
    try:
        print("🔍 Testing core module imports...")
        
        # Test core module import
        try:
            import core
            test_results['imports']['core'] = '✅ Success'
            print("  ✅ core")
        except Exception as e:
            test_results['imports']['core'] = f'❌ Error: {str(e)}'
            test_results['errors'].append(f"core: {str(e)}")
            print(f"  ❌ core: {str(e)}")
        
        # Test individual module imports
        modules_to_test = [
            'core.logging',
            'core.middleware', 
            'core.security',
            'core.auth'
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                test_results['imports'][module_name] = '✅ Success'
                print(f"  ✅ {module_name}")
            except Exception as e:
                test_results['imports'][module_name] = f'❌ Error: {str(e)}'
                test_results['errors'].append(f"{module_name}: {str(e)}")
                print(f"  ❌ {module_name}: {str(e)}")
        
        # Test importing specific components from core
        core_components = [
            ('logger', 'core'),
            ('get_logger', 'core'),
            ('set_log_level', 'core'),
            ('RequestLoggingMiddleware', 'core'),
            ('CORSMiddleware', 'core'),
            ('SecurityManager', 'core'),
            ('TokenManager', 'core'),
            ('User', 'core'),
            ('AuthenticationManager', 'core')
        ]
        
        for component, module in core_components:
            try:
                exec(f"from {module} import {component}")
                test_results['imports'][f'{module}.{component}'] = '✅ Success'
                print(f"  ✅ from {module} import {component}")
            except Exception as e:
                test_results['imports'][f'{module}.{component}'] = f'❌ Error: {str(e)}'
                test_results['errors'].append(f"{module}.{component}: {str(e)}")
                print(f"  ❌ from {module} import {component}: {str(e)}")
        
    except Exception as e:
        test_results['errors'].append(f"General import error: {str(e)}")
        print(f"❌ General import error: {str(e)}")
    
    # Calculate summary
    total_components = len(test_results['imports'])
    successful_imports = sum(1 for result in test_results['imports'].values() if result.startswith('✅'))
    failed_imports = total_components - successful_imports
    
    test_results['summary'] = {
        'total_components': total_components,
        'successful_imports': successful_imports,
        'failed_imports': failed_imports,
        'success_rate': (successful_imports / total_components * 100) if total_components > 0 else 0
    }
    
    return test_results


def test_core_file_existence() -> Dict[str, Any]:
    """Test that all required core files exist"""
    test_results = {
        'files': {},
        'errors': [],
        'summary': {}
    }
    
    try:
        print("\n📋 Testing core file existence...")
        
        required_files = [
            'core/__init__.py',
            'core/logging.py',
            'core/middleware.py',
            'core/security.py',
            'core/auth.py'
        ]
        
        for file_path in required_files:
            try:
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    # Check if file is readable
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    test_results['files'][file_path] = f'✅ Exists ({len(content)} chars)'
                    print(f"  ✅ {file_path} ({len(content)} characters)")
                else:
                    test_results['files'][file_path] = '❌ Missing'
                    test_results['errors'].append(f"{file_path}: File missing")
                    print(f"  ❌ {file_path}: Missing")
                    
            except Exception as e:
                test_results['files'][file_path] = f'❌ Error: {str(e)}'
                test_results['errors'].append(f"{file_path}: {str(e)}")
                print(f"  ❌ {file_path}: {str(e)}")
        
        # Calculate summary
        total_files = len(required_files)
        existing_files = sum(1 for result in test_results['files'].values() if result.startswith('✅'))
        
        test_results['summary'] = {
            'total_files': total_files,
            'existing_files': existing_files,
            'missing_files': total_files - existing_files,
            'existence_rate': (existing_files / total_files * 100) if total_files > 0 else 0
        }
        
    except Exception as e:
        test_results['errors'].append(f"General file existence error: {str(e)}")
        print(f"❌ General file existence error: {str(e)}")
    
    return test_results


def test_core_functionality() -> Dict[str, Any]:
    """Test basic functionality of core components"""
    test_results = {
        'functionality': {},
        'errors': [],
        'summary': {}
    }
    
    try:
        print("\n⚙️  Testing core functionality...")
        
        # Test logging functionality
        try:
            from core import logger, get_logger, set_log_level
            
            # Test logger
            logger.info("Test log message")
            
            # Test get_logger
            custom_logger = get_logger("test")
            custom_logger.info("Custom logger test")
            
            # Test set_log_level
            set_log_level("INFO")
            
            test_results['functionality']['logging'] = '✅ All logging functions work'
            print("  ✅ Logging functionality")
            
        except Exception as e:
            test_results['functionality']['logging'] = f'❌ Error: {str(e)}'
            test_results['errors'].append(f"Logging functionality: {str(e)}")
            print(f"  ❌ Logging functionality: {str(e)}")
        
        # Test middleware functionality
        try:
            from core import RequestLoggingMiddleware, CORSMiddleware, SecurityHeadersMiddleware
            
            # Test instantiation
            logging_middleware = RequestLoggingMiddleware()
            cors_middleware = CORSMiddleware()
            security_middleware = SecurityHeadersMiddleware()
            
            test_results['functionality']['middleware'] = '✅ All middleware classes instantiate'
            print("  ✅ Middleware functionality")
            
        except Exception as e:
            test_results['functionality']['middleware'] = f'❌ Error: {str(e)}'
            test_results['errors'].append(f"Middleware functionality: {str(e)}")
            print(f"  ❌ Middleware functionality: {str(e)}")
        
        # Test security functionality
        try:
            from core import SecurityManager, TokenManager, SecurityValidator
            
            # Test SecurityManager
            security_manager = SecurityManager()
            test_hash = security_manager.generate_secure_hash("test_data")
            test_verify = security_manager.verify_hash("test_data", test_hash)
            
            if not test_verify:
                raise Exception("Hash verification failed")
            
            # Test TokenManager
            token_manager = TokenManager()
            test_token = token_manager.generate_token("test_user")
            token_data = token_manager.validate_token(test_token)
            
            if not token_data:
                raise Exception("Token validation failed")
            
            # Test SecurityValidator
            validator = SecurityValidator()
            password_result = validator.validate_password_strength("TestPass123!")
            
            test_results['functionality']['security'] = '✅ All security functions work'
            print("  ✅ Security functionality")
            
        except Exception as e:
            test_results['functionality']['security'] = f'❌ Error: {str(e)}'
            test_results['errors'].append(f"Security functionality: {str(e)}")
            print(f"  ❌ Security functionality: {str(e)}")
        
        # Test authentication functionality
        try:
            from core import User, AuthenticationManager, AuthorizationManager
            
            # Test User class
            test_user = User("test123", "test@example.com", "testuser")
            user_dict = test_user.to_dict()
            
            # Test AuthenticationManager
            auth_manager = AuthenticationManager()
            created_user = auth_manager.create_user("test@example.com", "testuser", "TestPass123!")
            
            if not created_user:
                raise Exception("User creation failed")
            
            # Test authentication
            token = auth_manager.authenticate_user("testuser", "TestPass123!")
            
            if not token:
                raise Exception("Authentication failed")
            
            # Test AuthorizationManager
            authz_manager = AuthorizationManager()
            permission_check = authz_manager.check_permission(created_user, "read")
            
            test_results['functionality']['authentication'] = '✅ All authentication functions work'
            print("  ✅ Authentication functionality")
            
        except Exception as e:
            test_results['functionality']['authentication'] = f'❌ Error: {str(e)}'
            test_results['errors'].append(f"Authentication functionality: {str(e)}")
            print(f"  ❌ Authentication functionality: {str(e)}")
        
        # Calculate summary
        total_components = len(test_results['functionality'])
        working_components = sum(1 for result in test_results['functionality'].values() if result.startswith('✅'))
        
        test_results['summary'] = {
            'total_components': total_components,
            'working_components': working_components,
            'failed_components': total_components - working_components,
            'functionality_rate': (working_components / total_components * 100) if total_components > 0 else 0
        }
        
    except Exception as e:
        test_results['errors'].append(f"General functionality error: {str(e)}")
        print(f"❌ General functionality error: {str(e)}")
    
    return test_results


def test_core_syntax() -> Dict[str, Any]:
    """Test syntax correctness of all core files"""
    test_results = {
        'syntax': {},
        'errors': [],
        'summary': {}
    }
    
    try:
        print("\n🔍 Testing core syntax correctness...")
        
        files_to_test = [
            'core/__init__.py',
            'core/logging.py',
            'core/middleware.py',
            'core/security.py',
            'core/auth.py'
        ]
        
        for file_path in files_to_test:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    
                    # Try to compile the code
                    compile(source_code, file_path, 'exec')
                    
                    test_results['syntax'][file_path] = '✅ Syntax correct'
                    print(f"  ✅ {file_path}")
                else:
                    test_results['syntax'][file_path] = '❌ File missing'
                    test_results['errors'].append(f"{file_path}: File missing")
                    print(f"  ❌ {file_path}: File missing")
                    
            except SyntaxError as e:
                test_results['syntax'][file_path] = f'❌ Syntax error: {str(e)}'
                test_results['errors'].append(f"{file_path}: Syntax error at line {e.lineno}: {e.msg}")
                print(f"  ❌ {file_path}: Syntax error at line {e.lineno}: {e.msg}")
            except Exception as e:
                test_results['syntax'][file_path] = f'❌ Error: {str(e)}'
                test_results['errors'].append(f"{file_path}: {str(e)}")
                print(f"  ❌ {file_path}: {str(e)}")
        
        # Calculate summary
        total_files = len(files_to_test)
        correct_files = sum(1 for result in test_results['syntax'].values() if result.startswith('✅'))
        
        test_results['summary'] = {
            'total_files': total_files,
            'correct_files': correct_files,
            'incorrect_files': total_files - correct_files,
            'syntax_rate': (correct_files / total_files * 100) if total_files > 0 else 0
        }
        
    except Exception as e:
        test_results['errors'].append(f"General syntax error: {str(e)}")
        print(f"❌ General syntax error: {str(e)}")
    
    return test_results


def main():
    """Main test function for core module"""
    print("🚀 Core Module Comprehensive Test")
    print("=" * 60)
    
    all_results = {}
    
    # Run all tests
    all_results['file_existence'] = test_core_file_existence()
    all_results['syntax'] = test_core_syntax()
    all_results['imports'] = test_core_module_imports()
    all_results['functionality'] = test_core_functionality()
    
    # Print detailed summary
    print("\n📊 CORE MODULE TEST SUMMARY")
    print("=" * 60)
    
    total_errors = 0
    overall_success = True
    
    for test_category, results in all_results.items():
        errors = results.get('errors', [])
        total_errors += len(errors)
        summary = results.get('summary', {})
        
        if test_category == 'file_existence':
            rate = summary.get('existence_rate', 0)
            print(f"📁 File Existence: {summary.get('existing_files', 0)}/{summary.get('total_files', 0)} files ({rate:.1f}%)")
            if rate < 100:
                overall_success = False
        
        elif test_category == 'syntax':
            rate = summary.get('syntax_rate', 0)
            print(f"🔍 Syntax Correctness: {summary.get('correct_files', 0)}/{summary.get('total_files', 0)} files ({rate:.1f}%)")
            if rate < 100:
                overall_success = False
        
        elif test_category == 'imports':
            rate = summary.get('success_rate', 0)
            print(f"📦 Import Success: {summary.get('successful_imports', 0)}/{summary.get('total_components', 0)} components ({rate:.1f}%)")
            if rate < 100:
                overall_success = False
        
        elif test_category == 'functionality':
            rate = summary.get('functionality_rate', 0)
            print(f"⚙️  Functionality: {summary.get('working_components', 0)}/{summary.get('total_components', 0)} components ({rate:.1f}%)")
            if rate < 100:
                overall_success = False
        
        if errors:
            print(f"   ❌ Errors in {test_category}: {len(errors)}")
            for error in errors[:2]:  # Show first 2 errors
                print(f"      - {error}")
            if len(errors) > 2:
                print(f"      ... and {len(errors) - 2} more")
    
    print(f"\n🚫 Total Errors: {total_errors}")
    
    # Final verdict
    if overall_success and total_errors == 0:
        print("\n🎉 CORE MODULE IS FULLY COMPLIANT!")
        print("✅ All files exist")
        print("✅ All syntax is correct") 
        print("✅ All imports work")
        print("✅ All functionality works")
        print("✅ Core module meets all checklist requirements")
        return 0
    else:
        print(f"\n⚠️  CORE MODULE HAS ISSUES")
        print("❌ Some tests failed - review errors above")
        print("🔧 Fix the issues and re-run the test")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n💥 Core module test failed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)