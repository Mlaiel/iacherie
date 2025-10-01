"""💳 Payment Processors Enterprise Module - Consolidated Architecture
=====================================================================

Enterprise-grade payment processing suite with consolidated processors for
high-performance, multi-role expert payment handling and creator monetization.

Multi-Role Expert Implementation:
- Lead Dev IA: Advanced ML orchestration & predictive modeling
- Backend Senior: High-performance async processing architecture
- ML Engineer: Revenue optimization algorithms & fraud detection  
- DBA: Optimized data aggregation & comprehensive analytics
- Security: PCI DSS compliance & ML-powered fraud prevention
- Microservices: Event-driven distributed payment workflows
- Audio Engineer: Audio content payment optimization
- DevOps: Performance monitoring & validation automation
- IA Prompt Engineer: Intelligent workflow automation

Architecture: Consolidated from 35+ modules to 18 max (enterprise compliance)
Performance: <100ms Stripe, <150ms PayPal, <200ms Wise, <500ms Crypto, <50ms Creator

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Violation = Poursuites judiciaires automatiques

=================================================================
ENTERPRISE CONSOLIDATED PROCESSORS (8 Core Processors)
=================================================================
"""

# ============================================================
# ENTERPRISE CONSOLIDATED PROCESSORS  
# ============================================================

from .stripe_enterprise_processor import (
    StripeEnterpriseProcessor,
    StripeConnectAccount,
    PaymentIntent,
    Subscription,
    Dispute,
    StripeAccountType,
    PaymentIntentStatus,
    SubscriptionStatus,
    DisputeStatus
)

from .paypal_enterprise_processor import (
    PayPalEnterpriseProcessor,
    PayPalMerchantAccount,
    PayPalOrder,
    PayPalPayout,
    PayPalSubscription,
    PayPalEnvironment,
    PayPalOrderStatus,
    PayPalPayoutStatus,
    RiskLevel
)

from .wise_enterprise_processor import (
    WiseEnterpriseProcessor,
    WiseProfile,
    WiseAccount,
    ExchangeRate,
    WiseTransfer,
    WiseEnvironment,
    TransferStatus,
    AccountType,
    CurrencyCode,
    ComplianceStatus
)

from .crypto_blockchain_processor import (
    CryptoBlockchainProcessor,
    CryptoWallet,
    BlockchainTransaction,
    NFTAsset,
    SmartContract,
    BlockchainNetwork,
    CryptoCurrency,
    TransactionStatus as CryptoTransactionStatus,
    WalletType,
    NFTType,
    SmartContractType
)

from .creator_monetization_processor import (
    CreatorMonetizationProcessor,
    CreatorProfile,
    CreatorContent,
    RevenueTransaction,
    CreatorAnalytics,
    CreatorType,
    RevenueStream,
    PaymentStatus as CreatorPaymentStatus,
    ContentType
)

from .marketplace_orchestrator import (
    MarketplaceOrchestrator,
    MarketplaceParticipant,
    MarketplaceTransaction,
    EscrowAccount,
    MarketplaceDispute,
    MarketplaceType,
    TransactionType as MarketplaceTransactionType,
    EscrowStatus,
    DisputeStatus as MarketplaceDisputeStatus
)

from .payment_workflow_engine import (
    PaymentWorkflowEngine,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStep,
    WorkflowStatus,
    WorkflowStepType
)

from .fraud_prevention_processor import (
    FraudPreventionProcessor,
    FraudAnalysis,
    FraudPattern,
    ThreatIntelligence,
    FraudRiskLevel,
    FraudType,
    FraudAction
)

# ============================================================
# ADDITIONAL SPECIALIZED PROCESSORS  
# ============================================================

from .revenue_recovery import (
    RevenueRecoveryProcessor,
    DunningCampaign,
    RecoveryStrategy,
    PaymentRetry
)

from .automated_licensing import (
    AutomatedLicensingProcessor,
    LicenseAgreement,
    RoyaltyDistribution,
    ContentLicense
)

from .tax_compliance import (
    TaxComplianceProcessor,
    TaxCalculation,
    TaxReporting,
    ComplianceCheck
)

from .dispute_resolution import (
    DisputeResolutionProcessor,
    PaymentDispute,
    DisputeEvidence,
    ResolutionOutcome
)

from .payout_scheduler import (
    PayoutSchedulerProcessor,
    PayoutSchedule,
    BatchPayout,
    PayoutBatch
)

from .financial_reporting import (
    FinancialReportingProcessor,
    FinancialReport,
    RevenueAnalytics,
    PaymentMetrics
)

# =================================================================
# ENTERPRISE PROCESSOR FACTORY & UTILITIES
# =================================================================

class ProcessorFactory:
    """Factory for creating enterprise payment processors"""
    
    @staticmethod
    def create_stripe_processor(api_key: str, webhook_secret: str, **kwargs) -> StripeEnterpriseProcessor:
        """Create Stripe Enterprise processor"""
        return StripeEnterpriseProcessor(api_key, webhook_secret, **kwargs)
    
    @staticmethod
    def create_paypal_processor(client_id: str, client_secret: str, **kwargs) -> PayPalEnterpriseProcessor:
        """Create PayPal Enterprise processor"""
        return PayPalEnterpriseProcessor(client_id, client_secret, **kwargs)
    
    @staticmethod
    def create_wise_processor(api_token: str, **kwargs) -> WiseEnterpriseProcessor:
        """Create Wise Enterprise processor"""
        return WiseEnterpriseProcessor(api_token, **kwargs)
    
    @staticmethod
    def create_crypto_processor(**kwargs) -> CryptoBlockchainProcessor:
        """Create Crypto Blockchain processor"""
        return CryptoBlockchainProcessor(**kwargs)
    
    @staticmethod
    def create_creator_processor(**kwargs) -> CreatorMonetizationProcessor:
        """Create Creator Monetization processor"""
        return CreatorMonetizationProcessor(**kwargs)
    
    @staticmethod
    def create_marketplace_orchestrator(**kwargs) -> MarketplaceOrchestrator:
        """Create Marketplace Orchestrator"""
        return MarketplaceOrchestrator(**kwargs)
    
    @staticmethod
    def create_workflow_engine(**kwargs) -> PaymentWorkflowEngine:
        """Create Payment Workflow Engine"""
        return PaymentWorkflowEngine(**kwargs)
    
    @staticmethod
    def create_fraud_processor(**kwargs) -> FraudPreventionProcessor:
        """Create Fraud Prevention processor"""
        return FraudPreventionProcessor(**kwargs)

# =================================================================
# MODULE EXPORTS
# =================================================================

__all__ = [
    # Enterprise Consolidated Processors
    'StripeEnterpriseProcessor',
    'PayPalEnterpriseProcessor', 
    'WiseEnterpriseProcessor',
    'CryptoBlockchainProcessor',
    'CreatorMonetizationProcessor',
    'MarketplaceOrchestrator',
    'PaymentWorkflowEngine',
    'FraudPreventionProcessor',
    
    # Enterprise Types - Stripe
    'StripeConnectAccount',
    'PaymentIntent',
    'Subscription',
    'Dispute',
    'StripeAccountType',
    'PaymentIntentStatus',
    'SubscriptionStatus',
    'DisputeStatus',
    
    # Enterprise Types - PayPal
    'PayPalMerchantAccount',
    'PayPalOrder',
    'PayPalPayout',
    'PayPalSubscription',
    'PayPalEnvironment',
    'PayPalOrderStatus',
    'PayPalPayoutStatus',
    'RiskLevel',
    
    # Enterprise Types - Wise
    'WiseProfile',
    'WiseAccount',
    'ExchangeRate',
    'WiseTransfer',
    'WiseEnvironment',
    'TransferStatus',
    'AccountType',
    'CurrencyCode',
    'ComplianceStatus',
    
    # Enterprise Types - Crypto
    'CryptoWallet',
    'BlockchainTransaction',
    'NFTAsset',
    'SmartContract',
    'BlockchainNetwork',
    'CryptoCurrency',
    'CryptoTransactionStatus',
    'WalletType',
    'NFTType',
    'SmartContractType',
    
    # Enterprise Types - Creator
    'CreatorProfile',
    'CreatorContent',
    'RevenueTransaction',
    'CreatorAnalytics',
    'CreatorType',
    'RevenueStream',
    'CreatorPaymentStatus',
    'ContentType',
    
    # Enterprise Types - Marketplace
    'MarketplaceParticipant',
    'MarketplaceTransaction',
    'EscrowAccount',
    'MarketplaceDispute',
    'MarketplaceType',
    'MarketplaceTransactionType',
    'EscrowStatus',
    'MarketplaceDisputeStatus',
    
    # Enterprise Types - Workflow
    'WorkflowDefinition',
    'WorkflowExecution',
    'WorkflowStep',
    'WorkflowStatus',
    'WorkflowStepType',
    
    # Enterprise Types - Fraud
    'FraudAnalysis',
    'FraudPattern',
    'ThreatIntelligence',
    'FraudRiskLevel',
    'FraudType',
    'FraudAction',
    
    # Legacy Processors (Backward Compatibility)
    'StripeConnectProcessor',
    'PayPalBusinessProcessor',
    'WiseMultiCurrencyProcessor',
    'CryptoPaymentsProcessor',
    'RevenueRecoveryProcessor',
    'AutomatedLicensingProcessor',
    'TaxComplianceProcessor',
    'DisputeResolutionProcessor',
    'PayoutSchedulerProcessor',
    'FinancialReportingProcessor',
    
    # Factory & Utilities
    'ProcessorFactory'
]

# =================================================================
# MODULE METADATA
# =================================================================

__version__ = '2.0.0'
__author__ = 'Fahed Mlaiel <mlaiel@live.de>'
__description__ = 'Enterprise Payment Processors - Consolidated Architecture'
__license__ = 'Proprietary - All Rights Reserved'
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
    # Enterprise Consolidated Processors
    'StripeEnterpriseProcessor',
    'PayPalEnterpriseProcessor', 
    'WiseEnterpriseProcessor',
    'CryptoBlockchainProcessor',
    'CreatorMonetizationProcessor',
    'MarketplaceOrchestrator',
    'PaymentWorkflowEngine',
    'FraudPreventionProcessor',
    
    # Stripe Enterprise Types
    'StripeConnectAccount',
    'PaymentIntent',
    'Subscription',
    'Dispute',
    'StripeAccountType',
    'PaymentIntentStatus',
    'SubscriptionStatus',
    'DisputeStatus',
    
    # PayPal Enterprise Types
    'PayPalMerchantAccount',
    'PayPalOrder',
    'PayPalPayout',
    'PayPalSubscription',
    'PayPalEnvironment',
    'PayPalOrderStatus',
    'PayPalPayoutStatus',
    'RiskLevel',
    
    # Wise Enterprise Types
    'WiseProfile',
    'WiseAccount',
    'ExchangeRate',
    'WiseTransfer',
    'WiseEnvironment',
    'TransferStatus',
    'AccountType',
    'CurrencyCode',
    'ComplianceStatus',
    
    # Crypto Blockchain Types
    'CryptoWallet',
    'BlockchainTransaction',
    'NFTAsset',
    'SmartContract',
    'BlockchainNetwork',
    'CryptoCurrency',
    'WalletType',
    'NFTType',
    'SmartContractType',
    
    # Creator Monetization Types
    'CreatorProfile',
    'CreatorContent',
    'RevenueTransaction',
    'CreatorAnalytics',
    'CreatorType',
    'RevenueStream',
    'ContentType',
    
    # Marketplace Types
    'MarketplaceParticipant',
    'MarketplaceTransaction',
    'EscrowAccount',
    'MarketplaceDispute',
    'MarketplaceType',
    'EscrowStatus',
    
    # Workflow Types
    'WorkflowDefinition',
    'WorkflowExecution',
    'WorkflowStep',
    'WorkflowStatus',
    'WorkflowStepType',
    
    # Fraud Prevention Types
    'FraudAnalysis',
    'FraudPattern',
    'ThreatIntelligence',
    'FraudRiskLevel',
    'FraudType',
    'FraudAction',
    
    # Specialized Processors
    'RevenueRecoveryProcessor',
    'AutomatedLicensingProcessor',
    'TaxComplianceProcessor',
    'DisputeResolutionProcessor',
    'PayoutSchedulerProcessor',
    'FinancialReportingProcessor',
    
    # Utilities
    'ProcessorFactory'
]


# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Enterprise payment processing suite for IA Chéries platform"