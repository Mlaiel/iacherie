#!/usr/bin/env python3
"""
IA Influencer Agent - Secrets Module Test Script
Quick validation script for the secrets management module

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_imports() -> Dict[str, Any]:
    """Test importing all module components."""
    test_results = {
        'imports': {},
        'errors': [],
        'summary': {}
    }
    
    try:
        print("🔍 Testing module imports...")
        
        # Test core imports
        core_imports = [
            'SecretsConfig',
            'VaultManager', 
            'SecretRotator',
            'EncryptionManager',
            'SecretInjector',
            'ComplianceAuditor',
            'CertificateManager'
        ]
        
        for component in core_imports:
            try:
                exec(f"from . import {component}")
                test_results['imports'][component] = '✅ Success'
                print(f"  ✅ {component}")
            except Exception as e:
                test_results['imports'][component] = f'❌ Error: {str(e)}'
                test_results['errors'].append(f"{component}: {str(e)}")
                print(f"  ❌ {component}: {str(e)}")
        
        # Test IA Influencer specialized imports
        influencer_imports = [
            'InfluencerVaultManager',
            'InfluencerSecretRotator',
            'ContentProtectionEncryption',
            'InfluencerSecretInjector',
            'InfluencerComplianceAuditor',
            'InfluencerCertificateManager',
            'InfluencerPlatformUtils'
        ]
        
        for component in influencer_imports:
            try:
                exec(f"from . import {component}")
                test_results['imports'][component] = '✅ Success'
                print(f"  ✅ {component}")
            except Exception as e:
                test_results['imports'][component] = f'❌ Error: {str(e)}'
                test_results['errors'].append(f"{component}: {str(e)}")
                print(f"  ❌ {component}: {str(e)}")
        
        # Test utility imports
        utility_imports = [
            'SecurityUtils',
            'ValidationUtils',
            'NotificationUtils',
            'InfluencerSecretsManager'
        ]
        
        for component in utility_imports:
            try:
                exec(f"from . import {component}")
                test_results['imports'][component] = '✅ Success'
                print(f"  ✅ {component}")
            except Exception as e:
                test_results['imports'][component] = f'❌ Error: {str(e)}'
                test_results['errors'].append(f"{component}: {str(e)}")
                print(f"  ❌ {component}: {str(e)}")
        
        # Test factory functions
        factory_imports = [
            'create_secrets_manager',
            'create_influencer_secrets_manager',
            'initialize_platform_secrets',
            'get_module_info',
            'validate_environment'
        ]
        
        for component in factory_imports:
            try:
                exec(f"from . import {component}")
                test_results['imports'][component] = '✅ Success'
                print(f"  ✅ {component}")
            except Exception as e:
                test_results['imports'][component] = f'❌ Error: {str(e)}'
                test_results['errors'].append(f"{component}: {str(e)}")
                print(f"  ❌ {component}: {str(e)}")
        
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

def test_module_info() -> Dict[str, Any]:
    """Test module information functions."""
    test_results = {
        'module_info': {},
        'environment_validation': {},
        'errors': []
    }
    
    try:
        print("\n📋 Testing module information...")
        
        # Test get_module_info
        try:
            from . import get_module_info
            info = get_module_info()
            test_results['module_info'] = info
            print(f"  ✅ Module info retrieved: {info.get('name', 'Unknown')}")
            print(f"     Version: {info.get('version', 'Unknown')}")
            print(f"     Author: {info.get('author', 'Unknown')}")
        except Exception as e:
            test_results['errors'].append(f"get_module_info error: {str(e)}")
            print(f"  ❌ get_module_info error: {str(e)}")
        
        # Test validate_environment
        try:
            from . import validate_environment
            validation = validate_environment()
            test_results['environment_validation'] = validation
            print(f"  ✅ Environment validation completed")
            
            if validation.get('errors'):
                print("     ⚠️  Environment errors:")
                for error in validation['errors']:
                    print(f"       - {error}")
            
            if validation.get('warnings'):
                print("     ⚠️  Environment warnings:")
                for warning in validation['warnings']:
                    print(f"       - {warning}")
                    
        except Exception as e:
            test_results['errors'].append(f"validate_environment error: {str(e)}")
            print(f"  ❌ validate_environment error: {str(e)}")
            
    except Exception as e:
        test_results['errors'].append(f"General module info error: {str(e)}")
        print(f"❌ General module info error: {str(e)}")
    
    return test_results

def test_basic_functionality() -> Dict[str, Any]:
    """Test basic functionality without requiring external dependencies."""
    test_results = {
        'config_test': {},
        'utils_test': {},
        'errors': []
    }
    
    try:
        print("\n⚙️  Testing basic functionality...")
        
        # Test SecretsConfig
        try:
            from . import SecretsConfig
            config = SecretsConfig()
            test_results['config_test'] = {
                'instantiation': '✅ Success',
                'vault_url': getattr(config, 'vault_url', 'Not set'),
                'vault_timeout': getattr(config, 'vault_timeout', 'Not set')
            }
            print("  ✅ SecretsConfig instantiated successfully")
        except Exception as e:
            test_results['errors'].append(f"SecretsConfig error: {str(e)}")
            print(f"  ❌ SecretsConfig error: {str(e)}")
        
        # Test SecurityUtils
        try:
            from . import SecurityUtils
            security = SecurityUtils()
            
            # Test key generation
            key = security.generate_encryption_key()
            hash_result = security.generate_secure_hash("test_data")
            
            test_results['utils_test'] = {
                'instantiation': '✅ Success',
                'key_generation': '✅ Success' if key else '❌ Failed',
                'hash_generation': '✅ Success' if hash_result else '❌ Failed'
            }
            print("  ✅ SecurityUtils basic functions working")
        except Exception as e:
            test_results['errors'].append(f"SecurityUtils error: {str(e)}")
            print(f"  ❌ SecurityUtils error: {str(e)}")
        
        # Test ValidationUtils
        try:
            from . import ValidationUtils
            validation = ValidationUtils()
            
            # Test basic validation
            path_valid = validation.validate_secret_path("test/path")
            json_valid = validation.validate_json('{"test": "data"}')
            
            test_results['utils_test'].update({
                'validation_utils': '✅ Success',
                'path_validation': '✅ Success' if path_valid else '❌ Failed',
                'json_validation': '✅ Success' if json_valid else '❌ Failed'
            })
            print("  ✅ ValidationUtils basic functions working")
        except Exception as e:
            test_results['errors'].append(f"ValidationUtils error: {str(e)}")
            print(f"  ❌ ValidationUtils error: {str(e)}")
            
    except Exception as e:
        test_results['errors'].append(f"General functionality error: {str(e)}")
        print(f"❌ General functionality error: {str(e)}")
    
    return test_results

def main():
    """Main test function."""
    print("🚀 IA Influencer Agent - Secrets Module Test")
    print("=" * 60)
    
    all_results = {}
    
    # Run import tests
    all_results['imports'] = test_module_imports()
    
    # Run module info tests
    all_results['module_info'] = test_module_info()
    
    # Run basic functionality tests
    all_results['functionality'] = test_basic_functionality()
    
    # Print summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    total_errors = 0
    for test_category, results in all_results.items():
        errors = results.get('errors', [])
        total_errors += len(errors)
        
        if test_category == 'imports':
            summary = results.get('summary', {})
            print(f"📦 Imports: {summary.get('successful_imports', 0)}/{summary.get('total_components', 0)} successful ({summary.get('success_rate', 0):.1f}%)")
        
        if errors:
            print(f"❌ {test_category.title()} Errors: {len(errors)}")
            for error in errors[:3]:  # Show only first 3 errors
                print(f"   - {error}")
            if len(errors) > 3:
                print(f"   ... and {len(errors) - 3} more")
    
    if total_errors == 0:
        print("\n🎉 ALL TESTS PASSED! The secrets module is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total_errors} errors found. Please check the module configuration.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n💥 Test script failed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
