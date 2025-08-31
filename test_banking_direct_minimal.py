"""Banking Direct Minimal Test - Code Structure Validation

Validates Banking Direct implementation without external dependencies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path('/home/runner/work/Ainflue/Ainflue')
sys.path.insert(0, str(project_root))

def test_file_structure():
    """Test that Banking Direct files are created correctly."""
    print("=== Testing File Structure ===")
    
    base_path = project_root / 'ai_agents' / 'payment_processing_agent' / 'core' / 'banking_direct'
    
    required_files = [
        '__init__.py',
        'base_banking_processor.py',
        'plaid_processor.py',
        'open_banking_processor.py',
        'ach_direct_processor.py'
    ]
    
    for file_name in required_files:
        file_path = base_path / file_name
        if file_path.exists():
            print(f"✓ {file_name} exists")
        else:
            print(f"✗ {file_name} missing")
            return False
    
    return True


def test_code_syntax():
    """Test that Banking Direct code has valid Python syntax."""
    print("\n=== Testing Code Syntax ===")
    
    base_path = project_root / 'ai_agents' / 'payment_processing_agent' / 'core' / 'banking_direct'
    
    python_files = [
        'base_banking_processor.py',
        'plaid_processor.py', 
        'open_banking_processor.py',
        'ach_direct_processor.py'
    ]
    
    for file_name in python_files:
        file_path = base_path / file_name
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            compile(code, str(file_path), 'exec')
            print(f"✓ {file_name} syntax valid")
        except SyntaxError as e:
            print(f"✗ {file_name} syntax error: {e}")
            return False
        except Exception as e:
            print(f"✗ {file_name} error: {e}")
            return False
    
    return True


def test_class_definitions():
    """Test that classes are defined with expected names."""
    print("\n=== Testing Class Definitions ===")
    
    base_path = project_root / 'ai_agents' / 'payment_processing_agent' / 'core' / 'banking_direct'
    
    expected_classes = {
        'base_banking_processor.py': ['BaseBankingProcessor', 'BankAccount', 'BankConnectionResult', 'DirectDebitResult'],
        'plaid_processor.py': ['PlaidProcessor'],
        'open_banking_processor.py': ['OpenBankingProcessor'],
        'ach_direct_processor.py': ['ACHDirectProcessor']
    }
    
    for file_name, classes in expected_classes.items():
        file_path = base_path / file_name
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            for class_name in classes:
                if f"class {class_name}" in content:
                    print(f"✓ {class_name} defined in {file_name}")
                else:
                    print(f"✗ {class_name} missing in {file_name}")
                    return False
                    
        except Exception as e:
            print(f"✗ Error reading {file_name}: {e}")
            return False
    
    return True


def test_payment_models_update():
    """Test that payment models include Banking Direct providers."""
    print("\n=== Testing Payment Models Update ===")
    
    models_path = project_root / 'database' / 'payment_processing' / 'models.py'
    
    try:
        with open(models_path, 'r') as f:
            content = f.read()
        
        # Check for Banking Direct providers
        banking_providers = ['PLAID = "plaid"', 'OPEN_BANKING = "open_banking"', 'ACH_DIRECT = "ach_direct"']
        for provider in banking_providers:
            if provider in content:
                print(f"✓ {provider} found in PaymentProvider enum")
            else:
                print(f"✗ {provider} missing from PaymentProvider enum")
                return False
        
        # Check for Banking Direct payment methods
        banking_methods = ['PLAID_BANK_ACCOUNT = "plaid_bank_account"', 
                          'OPEN_BANKING_INSTANT = "open_banking_instant"',
                          'ACH_DIRECT_DEBIT = "ach_direct_debit"']
        for method in banking_methods:
            if method in content:
                print(f"✓ {method} found in PaymentMethodType enum")
            else:
                print(f"✗ {method} missing from PaymentMethodType enum")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error reading payment models: {e}")
        return False


def test_configuration_update():
    """Test that configuration includes Banking Direct providers."""
    print("\n=== Testing Configuration Update ===")
    
    config_path = project_root / 'ai_agents' / 'payment_processing_agent' / 'config' / 'config.py'
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Check for Banking Direct provider configs
        banking_configs = ['"plaid":', '"open_banking":', '"ach_direct":']
        for config in banking_configs:
            if config in content:
                print(f"✓ {config} configuration found")
            else:
                print(f"✗ {config} configuration missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error reading configuration: {e}")
        return False


def test_exceptions_module():
    """Test that exceptions module exists."""
    print("\n=== Testing Exceptions Module ===")
    
    exceptions_path = project_root / 'ai_agents' / 'payment_processing_agent' / 'exceptions.py'
    
    try:
        if exceptions_path.exists():
            print("✓ exceptions.py exists")
            
            with open(exceptions_path, 'r') as f:
                content = f.read()
            
            expected_exceptions = ['PaymentProcessingError', 'BankingDirectError', 'PlaidError', 
                                 'OpenBankingError', 'ACHDirectError']
            for exception in expected_exceptions:
                if f"class {exception}" in content:
                    print(f"✓ {exception} defined")
                else:
                    print(f"✗ {exception} missing")
                    return False
            
            return True
        else:
            print("✗ exceptions.py missing")
            return False
            
    except Exception as e:
        print(f"✗ Error checking exceptions: {e}")
        return False


def main():
    """Run all minimal Banking Direct tests."""
    print("Banking Direct Implementation - Minimal Test")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(test_file_structure())
    test_results.append(test_code_syntax())
    test_results.append(test_class_definitions())
    test_results.append(test_payment_models_update())
    test_results.append(test_configuration_update())
    test_results.append(test_exceptions_module())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All Banking Direct structural tests passed!")
        print("\nBanking Direct implementation is ready for integration!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)