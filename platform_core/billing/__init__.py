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

from .payment_processor import PaymentProcessor, StripeProcessor, PayPalProcessor
from .invoice_manager import InvoiceManager, Invoice, InvoiceItem
from .subscription_billing import SubscriptionBilling, BillingCycle
from .tax_calculator import TaxCalculator, TaxRule
from .financial_reporting import FinancialReporting, RevenueAnalytics
from .payment_methods import PaymentMethodManager, PaymentMethod
from .billing_alerts import BillingAlerts, AlertManager
from .refund_manager import RefundManager, RefundRequest

__all__ = [
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
    "RefundRequest"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
