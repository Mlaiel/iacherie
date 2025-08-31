# Banking Direct Integration - Usage Guide

This document provides examples of how to use the Banking Direct functionality in the Ainflue platform.

## Overview

Banking Direct provides three main payment processing options:

1. **Plaid** - US/EU bank account connections
2. **Open Banking** - European banking APIs (PSD2)
3. **ACH Direct** - Automatic direct debits (US)

## Basic Usage

### Plaid Integration

```python
from ai_agents.payment_processing_agent.core.banking_direct import PlaidProcessor

# Initialize Plaid processor
plaid = PlaidProcessor(
    client_id="your_plaid_client_id",
    client_secret="your_plaid_client_secret", 
    environment="production"  # or "sandbox"
)

# Connect a bank account
result = await plaid.connect_bank_account(
    user_id="user_123",
    institution_id="ins_bank_of_america"
)

if result.success and result.requires_verification:
    # User needs to complete Plaid Link flow
    redirect_to_link(result.verification_url)
else:
    # Connection complete, accounts available
    accounts = result.accounts
```

### Open Banking Integration

```python
from ai_agents.payment_processing_agent.core.banking_direct import OpenBankingProcessor

# Initialize Open Banking processor
open_banking = OpenBankingProcessor(
    client_id="your_ob_client_id",
    client_secret="your_ob_client_secret",
    api_key="your_api_key",
    environment="production"
)

# Connect European bank account
result = await open_banking.connect_bank_account(
    user_id="user_456",
    institution_id="lloyds_bank_gb",
    country_code="GB"
)

# Setup SEPA Direct Debit
debit_result = await open_banking.setup_direct_debit(
    user_id="user_456",
    account_id="account_789",
    amount=Decimal("29.99"),
    currency="EUR",
    frequency="monthly"
)
```

### ACH Direct Integration

```python
from ai_agents.payment_processing_agent.core.banking_direct import ACHDirectProcessor

# Initialize ACH processor
ach = ACHDirectProcessor(
    api_key="your_ach_api_key",
    routing_number="123456789",  # Your company routing number
    account_number="987654321",  # Your company account
    company_name="Ainflue Platform",
    company_id="AINFLUE01",
    environment="production"
)

# Connect customer bank account
result = await ach.connect_bank_account(
    user_id="user_789",
    institution_id="123456789",  # Customer's bank routing number
    account_number="111222333",  # Customer's account number
    account_type="checking",
    account_holder_name="John Doe"
)

# Verify with micro-deposits
verified = await ach.verify_bank_account(
    user_id="user_789",
    account_id="account_abc",
    verification_amounts=[Decimal("0.12"), Decimal("0.34")]
)
```

## Configuration

Add Banking Direct providers to your payment configuration:

```python
# config.py
BANKING_DIRECT_CONFIG = {
    "plaid": {
        "client_id": "your_plaid_client_id",
        "client_secret": "your_plaid_client_secret",
        "environment": "production",
        "supported_countries": ["US", "CA", "GB", "FR", "DE", "ES", "IT", "NL"]
    },
    "open_banking": {
        "client_id": "your_ob_client_id", 
        "client_secret": "your_ob_client_secret",
        "psd2_license": "PSD2_LICENSED",
        "redirect_uri": "https://yourapp.com/callback/openbanking"
    },
    "ach_direct": {
        "api_key": "your_ach_api_key",
        "routing_number": "123456789",
        "account_number": "987654321",
        "company_name": "Your Company",
        "company_id": "YOURCO01"
    }
}
```

## Error Handling

```python
from ai_agents.payment_processing_agent.exceptions import (
    BankingDirectError, PlaidError, OpenBankingError, ACHDirectError
)

try:
    result = await processor.connect_bank_account(user_id, **params)
except PlaidError as e:
    # Handle Plaid-specific errors
    logger.error(f"Plaid error: {e}")
except OpenBankingError as e:
    # Handle Open Banking errors
    logger.error(f"Open Banking error: {e}")
except ACHDirectError as e:
    # Handle ACH Direct errors  
    logger.error(f"ACH error: {e}")
except BankingDirectError as e:
    # Handle general Banking Direct errors
    logger.error(f"Banking Direct error: {e}")
```

## Security Considerations

1. **Credential Storage**: Store API keys and secrets securely using encryption
2. **Access Tokens**: Encrypt and securely store bank access tokens
3. **Account Numbers**: Always mask account numbers in logs and UI
4. **Compliance**: Ensure PCI DSS, PSD2, and NACHA compliance
5. **Audit Logs**: Log all banking operations for compliance

## Supported Features

### Plaid
- ✅ Bank account connection via Link
- ✅ Real-time balance checking
- ✅ Transaction history
- ✅ ACH payments
- ✅ US and EU bank support

### Open Banking  
- ✅ PSD2 compliant bank connections
- ✅ Account Information Service (AIS)
- ✅ Payment Initiation Service (PIS)
- ✅ SEPA Instant Payments
- ✅ SEPA Direct Debits
- ✅ Strong Customer Authentication (SCA)

### ACH Direct
- ✅ ACH origination and debits
- ✅ Micro-deposit verification
- ✅ NACHA compliant processing
- ✅ Recurring payment setup
- ✅ Real-time status tracking

## Integration with Existing Payment System

Banking Direct processors integrate seamlessly with the existing payment infrastructure:

```python
# Use with existing payment config
from ai_agents.payment_processing_agent.config.config import get_payment_config

config = get_payment_config()
plaid_config = config.get_provider_config("plaid")

if config.is_provider_enabled("plaid"):
    processor = PlaidProcessor(**plaid_config)
```

For more detailed API documentation, see the individual processor class documentation.