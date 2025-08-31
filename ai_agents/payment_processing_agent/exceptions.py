"""Payment Processing Exceptions - Banking Direct Support

Custom exceptions for Banking Direct payment processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""


class PaymentProcessingError(Exception):
    """Base exception for payment processing errors."""
    pass


class InvalidPaymentMethodError(PaymentProcessingError):
    """Exception for invalid payment method errors."""
    pass


class BankingDirectError(PaymentProcessingError):
    """Base exception for Banking Direct errors."""
    pass


class PlaidError(BankingDirectError):
    """Exception for Plaid-specific errors."""
    pass


class OpenBankingError(BankingDirectError):
    """Exception for Open Banking-specific errors."""
    pass


class ACHDirectError(BankingDirectError):
    """Exception for ACH Direct-specific errors."""
    pass