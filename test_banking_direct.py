"""Banking Direct Implementation Test - Simple Validation

Simple test to validate Banking Direct processors can be imported and initialized.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import sys
import os
from decimal import Decimal
from datetime import datetime

# Add project root to path
sys.path.append('/home/runner/work/Ainflue/Ainflue')


def test_imports():
    """Test that Banking Direct modules can be imported."""
    print("=== Testing Banking Direct Imports ===")
    
    try:
        # Test individual module imports
        from ai_agents.payment_processing_agent.core.banking_direct.base_banking_processor import (
            BaseBankingProcessor, BankAccount, BankConnectionResult, DirectDebitResult
        )
        print("✓ Base Banking processor imported")
        
        from ai_agents.payment_processing_agent.core.banking_direct.plaid_processor import PlaidProcessor
        print("✓ Plaid processor imported")
        
        from ai_agents.payment_processing_agent.core.banking_direct.open_banking_processor import OpenBankingProcessor
        print("✓ Open Banking processor imported")
        
        from ai_agents.payment_processing_agent.core.banking_direct.ach_direct_processor import ACHDirectProcessor
        print("✓ ACH Direct processor imported")
        
        # Test package import
        from ai_agents.payment_processing_agent.core.banking_direct import (
            PlaidProcessor as PlaidPkg, OpenBankingProcessor as OpenBankingPkg, ACHDirectProcessor as ACHPkg
        )
        print("✓ Package imports working")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_initialization():
    """Test that processors can be initialized."""
    print("\n=== Testing Processor Initialization ===")
    
    try:
        from ai_agents.payment_processing_agent.core.banking_direct import (
            PlaidProcessor, OpenBankingProcessor, ACHDirectProcessor
        )
        
        # Test Plaid initialization
        plaid = PlaidProcessor(
            client_id="test_client",
            client_secret="test_secret",
            environment="sandbox"
        )
        assert plaid.name == "plaid"
        assert plaid.environment == "sandbox"
        print("✓ Plaid processor initialized")
        
        # Test Open Banking initialization
        open_banking = OpenBankingProcessor(
            client_id="test_ob_client",
            client_secret="test_ob_secret",
            environment="sandbox"
        )
        assert open_banking.name == "open_banking"
        assert open_banking.environment == "sandbox"
        print("✓ Open Banking processor initialized")
        
        # Test ACH Direct initialization
        ach = ACHDirectProcessor(
            api_key="test_key",
            routing_number="123456789",
            account_number="987654321",
            company_name="Test Company", 
            company_id="TEST01",
            environment="sandbox"
        )
        assert ach.name == "ach_direct"
        assert ach.company_name == "Test Company"
        print("✓ ACH Direct processor initialized")
        
        return True
        
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return False


def test_data_structures():
    """Test Banking Direct data structures."""
    print("\n=== Testing Data Structures ===")
    
    try:
        from ai_agents.payment_processing_agent.core.banking_direct.base_banking_processor import (
            BankAccount, BankConnectionResult, DirectDebitResult
        )
        
        # Test BankAccount
        account = BankAccount(
            account_id="test_123",
            account_name="Test Account",
            account_type="checking",
            routing_number="123456789",
            account_number_mask="****1234",
            institution_name="Test Bank",
            currency="USD"
        )
        assert account.account_id == "test_123"
        assert account.currency == "USD"
        print("✓ BankAccount structure working")
        
        # Test BankConnectionResult
        connection = BankConnectionResult(
            success=True,
            connection_id="conn_123",
            accounts=[account]
        )
        assert connection.success is True
        assert len(connection.accounts) == 1
        print("✓ BankConnectionResult structure working")
        
        # Test DirectDebitResult
        debit = DirectDebitResult(
            success=True,
            mandate_id="mandate_123",
            amount=Decimal("100.00"),
            currency="USD"
        )
        assert debit.success is True
        assert debit.amount == Decimal("100.00")
        print("✓ DirectDebitResult structure working")
        
        return True
        
    except Exception as e:
        print(f"✗ Data structure error: {e}")
        return False


def test_payment_models():
    """Test that payment models include Banking Direct providers."""
    print("\n=== Testing Payment Models ===")
    
    try:
        # Import the payment models
        sys.path.append('/home/runner/work/Ainflue/Ainflue/database/payment_processing')
        from models import PaymentProvider, PaymentMethodType
        
        # Check that Banking Direct providers are included
        providers = [provider.value for provider in PaymentProvider]
        assert "plaid" in providers, "Plaid not found in PaymentProvider enum"
        assert "open_banking" in providers, "Open Banking not found in PaymentProvider enum"
        assert "ach_direct" in providers, "ACH Direct not found in PaymentProvider enum"
        print("✓ Banking Direct providers in PaymentProvider enum")
        
        # Check that Banking Direct payment methods are included
        methods = [method.value for method in PaymentMethodType]
        assert "plaid_bank_account" in methods, "Plaid bank account not found in PaymentMethodType enum"
        assert "open_banking_instant" in methods, "Open Banking instant not found in PaymentMethodType enum" 
        assert "ach_direct_debit" in methods, "ACH direct debit not found in PaymentMethodType enum"
        print("✓ Banking Direct payment methods in PaymentMethodType enum")
        
        return True
        
    except Exception as e:
        print(f"✗ Payment models error: {e}")
        return False


def test_configuration():
    """Test Banking Direct configuration."""
    print("\n=== Testing Configuration ===")
    
    try:
        from ai_agents.payment_processing_agent.config.config import PaymentConfig
        
        # Create config instance
        config = PaymentConfig(encryption_key="test_key_123456789012345678901234")
        
        # Check Banking Direct providers are configured
        assert "plaid" in config.providers, "Plaid not configured"
        assert "open_banking" in config.providers, "Open Banking not configured"  
        assert "ach_direct" in config.providers, "ACH Direct not configured"
        print("✓ Banking Direct providers configured")
        
        # Test provider configuration access
        plaid_config = config.get_provider_config("plaid")
        assert plaid_config is not None, "Cannot get Plaid config"
        assert "client_id" in plaid_config, "Plaid config missing client_id"
        print("✓ Provider configuration access working")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def main():
    """Run all simple Banking Direct tests."""
    print("Banking Direct Implementation - Simple Test")
    print("=" * 50)
    
    test_results = []
    
    # Run tests
    test_results.append(test_imports())
    test_results.append(test_initialization()) 
    test_results.append(test_data_structures())
    test_results.append(test_payment_models())
    test_results.append(test_configuration())
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All Banking Direct tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)