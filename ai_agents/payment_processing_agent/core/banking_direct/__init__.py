"""Banking Direct Processors - US/EU Bank Account Integration

Banking Direct payment processors for direct bank account connections,
Open Banking APIs, and ACH direct debits.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .base_banking_processor import BaseBankingProcessor
from .plaid_processor import PlaidProcessor
from .open_banking_processor import OpenBankingProcessor
from .ach_direct_processor import ACHDirectProcessor

__all__ = [
    'BaseBankingProcessor',
    'PlaidProcessor', 
    'OpenBankingProcessor',
    'ACHDirectProcessor'
]