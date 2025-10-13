"""🚀 Platform Core Billing System - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/platform_core/billing/
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE FACTURATION ENTERPRISE
Gestion complète de facturation et paiements pour plateforme IA
- Intégration Stripe/PayPal/Wise pour paiements globaux
- Facturation automatique et récurrente
- Gestion des taxes internationales (TVA/TPS/HST)
- Rapports financiers et comptabilité analytique
"""

# Existing modules (already implemented)
from .payment_processor import PaymentProcessor, StripeProcessor, PayPalProcessor
from .invoice_manager import InvoiceManager, Invoice, InvoiceItem
from .subscription_billing import SubscriptionBilling, BillingCycle
from .tax_calculator import TaxCalculator, TaxRule
from .financial_reporting import FinancialReporting, RevenueAnalytics
from .payment_methods import PaymentMethodManager, PaymentMethod
from .billing_alerts import BillingAlerts, AlertManager
from .refund_manager import RefundManager, RefundRequest

# New advanced modules (Enterprise Level 3)
from .payment_gateway_manager import (
    PaymentGatewayManager, 
    GatewayStatus, 
    PaymentGatewayType, 
    RoutingStrategy,
    GatewayMetrics,
    PaymentRouting
)
from .fraud_detection import (
    FraudDetectionEngine,
    MLFraudModel,
    RiskLevel,
    FraudType,
    ActionRecommendation,
    FraudAnalysisResult,
    ChurnPrediction
)
from .split_payments import (
    SplitPaymentManager,
    SplitPaymentCalculator,
    CreatorParticipant,
    SplitRule,
    SplitTransaction,
    EscrowAccount,
    SplitType,
    CollaborationType
)
from .revenue_recognition import (
    RevenueRecognitionEngine,
    RevenueContract,
    PerformanceObligation,
    RevenueScheduleEntry,
    JournalEntry,
    RevenueRecognitionStandard,
    ContractType,
    RecognitionMethod
)
from .subscription_analytics import (
    SubscriptionAnalyticsEngine,
    MLChurnPredictor,
    SubscriptionMetrics,
    CohortData,
    ChurnPrediction as SubscriptionChurnPrediction,
    SubscriptionStatus,
    SubscriptionTier
)
from .billing_notifications import (
    BillingNotificationManager,
    MLPersonalizationEngine,
    NotificationTemplate,
    NotificationPreferences,
    BillingEvent,
    NotificationMessage,
    NotificationChannel,
    BillingEventType
)
from .payment_reconciliation import (
    PaymentReconciliationEngine,
    MLReconciliationEngine,
    InternalTransaction,
    GatewayTransaction,
    ReconciliationMatch,
    ReconciliationReport,
    ReconciliationStatus,
    DiscrepancyType
)
from .billing_webhooks import (
    BillingWebhookManager,
    WebhookSignatureValidator,
    WebhookEventProcessor,
    WebhookEvent,
    WebhookEndpoint,
    WebhookDelivery,
    WebhookProvider,
    WebhookEventType,
    RetryStrategy
)
from .dunning_management import (
    DunningManagementEngine,
    MLDunningOptimizer,
    DunningCase,
    DunningRule,
    DunningExecution,
    CustomerDunningProfile,
    DunningStatus,
    DunningAction,
    RecoveryStatus
)

__all__ = [
    # Existing modules
    "PaymentProcessor",
    "StripeProcessor", 
    "PayPalProcessor",
    "InvoiceManager",
    "Invoice",
    "InvoiceItem",
    "SubscriptionBilling",
    "BillingCycle",
    "TaxCalculator",
    "TaxRule",
    "FinancialReporting",
    "RevenueAnalytics",
    "PaymentMethodManager",
    "PaymentMethod",
    "BillingAlerts",
    "AlertManager",
    "RefundManager",
    "RefundRequest",
    
    # Payment Gateway Manager
    "PaymentGatewayManager",
    "GatewayStatus",
    "PaymentGatewayType",
    "RoutingStrategy",
    "GatewayMetrics",
    "PaymentRouting",
    
    # Fraud Detection
    "FraudDetectionEngine",
    "MLFraudModel",
    "RiskLevel",
    "FraudType",
    "ActionRecommendation",
    "FraudAnalysisResult",
    "ChurnPrediction",
    
    # Split Payments
    "SplitPaymentManager",
    "SplitPaymentCalculator",
    "CreatorParticipant",
    "SplitRule",
    "SplitTransaction",
    "EscrowAccount",
    "SplitType",
    "CollaborationType",
    
    # Revenue Recognition
    "RevenueRecognitionEngine",
    "RevenueContract",
    "PerformanceObligation",
    "RevenueScheduleEntry",
    "JournalEntry",
    "RevenueRecognitionStandard",
    "ContractType",
    "RecognitionMethod",
    
    # Subscription Analytics
    "SubscriptionAnalyticsEngine",
    "MLChurnPredictor",
    "SubscriptionMetrics",
    "CohortData",
    "SubscriptionChurnPrediction",
    "SubscriptionStatus",
    "SubscriptionTier",
    
    # Billing Notifications
    "BillingNotificationManager",
    "MLPersonalizationEngine",
    "NotificationTemplate",
    "NotificationPreferences",
    "BillingEvent",
    "NotificationMessage",
    "NotificationChannel",
    "BillingEventType",
    
    # Payment Reconciliation
    "PaymentReconciliationEngine",
    "MLReconciliationEngine",
    "InternalTransaction",
    "GatewayTransaction",
    "ReconciliationMatch",
    "ReconciliationReport",
    "ReconciliationStatus",
    "DiscrepancyType",
    
    # Billing Webhooks
    "BillingWebhookManager",
    "WebhookSignatureValidator",
    "WebhookEventProcessor",
    "WebhookEvent",
    "WebhookEndpoint",
    "WebhookDelivery",
    "WebhookProvider",
    "WebhookEventType",
    "RetryStrategy",
    
    # Dunning Management
    "DunningManagementEngine",
    "MLDunningOptimizer",
    "DunningCase",
    "DunningRule",
    "DunningExecution",
    "CustomerDunningProfile",
    "DunningStatus",
    "DunningAction",
    "RecoveryStatus"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
