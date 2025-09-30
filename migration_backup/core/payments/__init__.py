"""Ainflue Core Payments - Enterprise Payment & Financial Systems
============================================================

Core payment systems providing payment gateways, cryptocurrency processing,
subscription management, billing engines, revenue tracking, fraud detection,
blockchain integration, and financial reporting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any

# Payment core imports (existing files to be moved here)
try:
    from .payment_gateway_core import PaymentGatewayCore
except ImportError:
    PaymentGatewayCore = None

try:
    from .crypto_payment_core import CryptoPaymentCore
except ImportError:
    CryptoPaymentCore = None

try:
    from .subscription_management_core import SubscriptionManagementCore
except ImportError:
    SubscriptionManagementCore = None

# New payment core files (to be created)
try:
    from .billing_engine_core import BillingEngineCore
except ImportError:
    BillingEngineCore = None

try:
    from .invoice_generator_core import InvoiceGeneratorCore
except ImportError:
    InvoiceGeneratorCore = None

try:
    from .tax_calculator_core import TaxCalculatorCore
except ImportError:
    TaxCalculatorCore = None

try:
    from .revenue_tracking_core import RevenueTrackingCore
except ImportError:
    RevenueTrackingCore = None

try:
    from .payout_system_core import PayoutSystemCore
except ImportError:
    PayoutSystemCore = None

try:
    from .escrow_service_core import EscrowServiceCore
except ImportError:
    EscrowServiceCore = None

try:
    from .fraud_detection_core import FraudDetectionCore
except ImportError:
    FraudDetectionCore = None

try:
    from .refund_processor_core import RefundProcessorCore
except ImportError:
    RefundProcessorCore = None

try:
    from .wallet_management_core import WalletManagementCore
except ImportError:
    WalletManagementCore = None

try:
    from .blockchain_integration_core import BlockchainIntegrationCore
except ImportError:
    BlockchainIntegrationCore = None

try:
    from .smart_contract_core import SmartContractCore
except ImportError:
    SmartContractCore = None

try:
    from .defi_protocols_core import DeFiProtocolsCore
except ImportError:
    DeFiProtocolsCore = None

try:
    from .stablecoin_core import StablecoinCore
except ImportError:
    StablecoinCore = None

try:
    from .payment_routing_core import PaymentRoutingCore
except ImportError:
    PaymentRoutingCore = None

try:
    from .financial_reporting_core import FinancialReportingCore
except ImportError:
    FinancialReportingCore = None

__all__ = [
    "PaymentGatewayCore", "CryptoPaymentCore", "SubscriptionManagementCore",
    "BillingEngineCore", "InvoiceGeneratorCore", "TaxCalculatorCore",
    "RevenueTrackingCore", "PayoutSystemCore", "EscrowServiceCore",
    "FraudDetectionCore", "RefundProcessorCore", "WalletManagementCore",
    "BlockchainIntegrationCore", "SmartContractCore", "DeFiProtocolsCore",
    "StablecoinCore", "PaymentRoutingCore", "FinancialReportingCore"
]