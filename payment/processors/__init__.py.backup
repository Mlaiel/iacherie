"""💳 Payment Processors Module
============================

Comprehensive payment processing suite with specialized processors for
enterprise-grade payment handling, compliance, and financial operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

Available Processors:
- StripeConnectProcessor: Stripe Connect enterprise payment processing
- PayPalBusinessProcessor: PayPal Business complete payment handling  
- WiseMultiCurrencyProcessor: Wise multi-currency international transfers
- CryptoPaymentsProcessor: Cryptocurrency payments and blockchain integration
- RevenueRecoveryProcessor: Automated revenue recovery and dunning management
- AutomatedLicensingProcessor: Content licensing and royalty distribution
- TaxComplianceProcessor: Tax calculation, reporting, and compliance
- DisputeResolutionProcessor: Payment dispute and chargeback resolution
- PayoutSchedulerProcessor: Automated payout scheduling and batch processing
- FinancialReportingProcessor: Comprehensive financial reporting and analytics
"""
from .stripe import (
    StripeConnectProcessor,
    StripeConnectAccount,
    StripePaymentIntent,
    StripeAccountType,
    StripeCapability
)

from .paypal_business import (
    PayPalBusinessProcessor,
    PayPalMerchantAccount,
    PayPalOrder,
    PayPalPayout,
    PayPalEnvironment,
    PayPalAccountType,
    PayPalPaymentMethod
)

from .wise_multi_currency import (
    WiseMultiCurrencyProcessor,
    WiseProfile,
    WiseAccount,
    WiseExchangeRate,
    WiseTransfer,
    WiseCurrency,
    WiseEnvironment,
    WiseAccountType,
    TransferPurpose
)

from .crypto_payments import (
    CryptoPaymentsProcessor,
    CryptoWallet,
    CryptoTransaction,
    ExchangeRate as CryptoExchangeRate,
    CryptoCurrency,
    BlockchainNetwork,
    TransactionStatus,
    WalletType
)

from .revenue_recovery import (
    RevenueRecoveryProcessor,
    RecoveryCase,
    DunningCampaign,
    RecoveryAttempt,
    RecoveryType,
    RecoveryStatus,
    RecoveryStrategy,
    DunningLevel
)

from .automated_licensing import (
    AutomatedLicensingProcessor,
    LicenseAgreement,
    UsageReport,
    RoyaltyDistribution,
    RevenueShare,
    LicenseType,
    UsageType,
    RoyaltyType,
    LicenseStatus
)

from .tax_compliance import (
    TaxComplianceProcessor,
    TaxRate,
    TaxableTransaction,
    TaxCalculation,
    TaxRemittance,
    TaxType,
    TaxJurisdiction,
    TransactionCategory
)

from .dispute_resolution import (
    DisputeResolutionProcessor,
    DisputeCase,
    Evidence,
    DisputeMessage,
    DisputeType,
    DisputeStatus,
    DisputeResolution,
    EvidenceType
)

from .payout_scheduler import (
    PayoutSchedulerProcessor,
    PayoutSchedule,
    ScheduledPayout,
    PayoutBatch,
    PayoutFrequency,
    PayoutStatus,
    PayoutMethod
)

from .financial_reporting import (
    FinancialReportingProcessor,
    FinancialReport,
    ReportSchedule,
    FinancialMetric,
    ReportFilter,
    ReportType,
    ReportFormat,
    MetricType,
    ReportFrequency
)


# Processor registry for easy access
PAYMENT_PROCESSORS = {
    'stripe': StripeConnectProcessor,
    'paypal_business': PayPalBusinessProcessor,
    'wise_multi_currency': WiseMultiCurrencyProcessor,
    'crypto_payments': CryptoPaymentsProcessor,
    'revenue_recovery': RevenueRecoveryProcessor,
    'automated_licensing': AutomatedLicensingProcessor,
    'tax_compliance': TaxComplianceProcessor,
    'dispute_resolution': DisputeResolutionProcessor,
    'payout_scheduler': PayoutSchedulerProcessor,
    'financial_reporting': FinancialReportingProcessor
}


def get_processor(processor_name: str, **kwargs):
    """
    Factory function to get a payment processor instance
    
    Args:
        processor_name: Name of the processor to instantiate
        **kwargs: Processor-specific configuration parameters
        
    Returns:
        Configured processor instance
        
    Raises:
        ValueError: If processor name is not recognized
    """
    if processor_name not in PAYMENT_PROCESSORS:
        available = ', '.join(PAYMENT_PROCESSORS.keys())
        raise ValueError(f"Unknown processor '{processor_name}'. Available: {available}")
    
    processor_class = PAYMENT_PROCESSORS[processor_name]
    return processor_class(**kwargs)


def list_processors():
    """
    List all available payment processors
    
    Returns:
        List of available processor names
    """
    return list(PAYMENT_PROCESSORS.keys())


def get_processor_info(processor_name: str):
    """
    Get information about a specific processor
    
    Args:
        processor_name: Name of the processor
        
    Returns:
        Dictionary with processor information
        
    Raises:
        ValueError: If processor name is not recognized
    """
    if processor_name not in PAYMENT_PROCESSORS:
        raise ValueError(f"Unknown processor '{processor_name}'")
    
    processor_class = PAYMENT_PROCESSORS[processor_name]
    
    # Extract processor information from docstring
    info = {
        'name': processor_name,
        'class': processor_class.__name__,
        'description': processor_class.__doc__.split('\n')[1].strip() if processor_class.__doc__ else 'No description available',
        'module': processor_class.__module__
    }
    
    return info


# Export all processors and utilities
__all__ = [
    # Stripe Connect
    'StripeConnectProcessor',
    'StripeConnectAccount', 
    'StripePaymentIntent',
    'StripeAccountType',
    'StripeCapability',
    
    # PayPal Business
    'PayPalBusinessProcessor',
    'PayPalMerchantAccount',
    'PayPalOrder',
    'PayPalPayout',
    'PayPalEnvironment',
    'PayPalAccountType',
    'PayPalPaymentMethod',
    
    # Wise Multi-Currency
    'WiseMultiCurrencyProcessor',
    'WiseProfile',
    'WiseAccount',
    'WiseExchangeRate',
    'WiseTransfer',
    'WiseCurrency',
    'WiseEnvironment',
    'WiseAccountType',
    'TransferPurpose',
    
    # Cryptocurrency
    'CryptoPaymentsProcessor',
    'CryptoWallet',
    'CryptoTransaction',
    'CryptoExchangeRate',
    'CryptoCurrency',
    'BlockchainNetwork',
    'TransactionStatus',
    'WalletType',
    
    # Revenue Recovery
    'RevenueRecoveryProcessor',
    'RecoveryCase',
    'DunningCampaign',
    'RecoveryAttempt',
    'RecoveryType',
    'RecoveryStatus',
    'RecoveryStrategy',
    'DunningLevel',
    
    # Automated Licensing
    'AutomatedLicensingProcessor',
    'LicenseAgreement',
    'UsageReport',
    'RoyaltyDistribution',
    'RevenueShare',
    'LicenseType',
    'UsageType',
    'RoyaltyType',
    'LicenseStatus',
    
    # Tax Compliance
    'TaxComplianceProcessor',
    'TaxRate',
    'TaxableTransaction',
    'TaxCalculation',
    'TaxRemittance',
    'TaxType',
    'TaxJurisdiction',
    'TransactionCategory',
    
    # Dispute Resolution
    'DisputeResolutionProcessor',
    'DisputeCase',
    'Evidence',
    'DisputeMessage',
    'DisputeType',
    'DisputeStatus',
    'DisputeResolution',
    'EvidenceType',
    
    # Payout Scheduler
    'PayoutSchedulerProcessor',
    'PayoutSchedule',
    'ScheduledPayout',
    'PayoutBatch',
    'PayoutFrequency',
    'PayoutStatus',
    'PayoutMethod',
    
    # Financial Reporting
    'FinancialReportingProcessor',
    'FinancialReport',
    'ReportSchedule',
    'FinancialMetric',
    'ReportFilter',
    'ReportType',
    'ReportFormat',
    'MetricType',
    'ReportFrequency',
    
    # Utility functions
    'PAYMENT_PROCESSORS',
    'get_processor',
    'list_processors',
    'get_processor_info'
]


# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Enterprise payment processing suite for Ainflue platform"