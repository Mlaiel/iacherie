"""Business Billing Module - IA Influencer Agent
==============================================

Module de facturation et paiement industriel pour créateurs multi-format
avec intégration IA, protection contenu et monétisation automatisée.

Architecture: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
             Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""# Core billing services
from .invoice_generator import InvoiceGeneratorEngine, InvoiceData
from .payment_processor import PaymentProcessorEngine, PaymentData, BulkPayoutResult
from .commission_calculator import CommissionCalculatorEngine, CommissionData, TierLevel
from .subscription_billing import SubscriptionBillingEngine, SubscriptionData, BillingCycle
from .royalty_distributor import RoyaltyDistributorEngine, RoyaltyData, RoyaltyType
from .tax_compliance import TaxComplianceEngine, TaxCalculation, TaxType
from .billing_analytics import BillingAnalyticsEngine, AnalyticsType, TimeFrame
from .payment_gateway import PaymentGatewayEngine, PaymentRequest, PaymentResult, GatewayProvider
from .dispute_manager import DisputeManagerEngine, DisputeData, DisputeType, DisputeStatus
from .billing_aggregator import BillingAggregatorEngine, BillingWorkflow, BillingWorkflowType

# Export main classes
__all__ = [
    # Core Engines
    'InvoiceGeneratorEngine',
    'PaymentProcessorEngine', 
    'CommissionCalculatorEngine',
    'SubscriptionBillingEngine',
    'RoyaltyDistributorEngine',
    'TaxComplianceEngine',
    'BillingAnalyticsEngine',
    'PaymentGatewayEngine',
    'DisputeManagerEngine',
    'BillingAggregatorEngine',
    
    # Data Classes
    'InvoiceData',
    'PaymentData',
    'CommissionData',
    'SubscriptionData',
    'RoyaltyData',
    'TaxCalculation',
    'PaymentRequest',
    'PaymentResult',
    'DisputeData',
    'BillingWorkflow',
    
    # Results & Collections
    'BulkPayoutResult',
    
    # Enums
    'TierLevel',
    'BillingCycle',
    'RoyaltyType',
    'TaxType',
    'AnalyticsType',
    'TimeFrame',
    'GatewayProvider',
    'DisputeType',
    'DisputeStatus',
    'BillingWorkflowType'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Industrial billing system for multi-format content creators"
