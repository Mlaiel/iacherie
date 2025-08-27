"""
Payment Processing Agent - Industrial Payment Ecosystem

Complete payment processing system for content monetization, revenue tracking,
creator payments, licensing fees, and multi-currency support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

"""
Payment Processing Agent - Industrial Payment Ecosystem

Complete payment processing system for content monetization, revenue tracking,
creator payments, licensing fees, and multi-currency support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .payment_agent import PaymentProcessingAgent
from .index import (
    PaymentProcessingService,
    get_service,
    get_payment_agent,
    shutdown_service,
    create_fraud_engine,
    create_compliance_manager,
    create_analytics_engine,
    create_currency_converter
)
from .models import (
    PaymentTransaction,
    PayoutSchedule,
    PaymentMethod,
    RevenueAllocation,
    TaxConfiguration,
    PaymentProvider,
    FraudAnalysis,
    ComplianceCheck
)
from .validators import PaymentValidator
from .schedulers import PayoutScheduler
from .analytics import PaymentAnalytics
from .compliance import ComplianceManager
from .fraud_detection import FraudDetectionEngine
from .cache import PerformanceCache
from .currency import CurrencyConverter
from .exceptions import (
    PaymentProcessingError,
    InsufficientFundsError,
    InvalidPaymentMethodError,
    FraudDetectedError,
    ComplianceError,
    PaymentDeclinedError,
    PayoutFailedError
)
from .config import PaymentConfig

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Main service and agent
    "PaymentProcessingService",
    "PaymentProcessingAgent",
    
    # Service factory functions
    "get_service",
    "get_payment_agent", 
    "shutdown_service",
    "create_fraud_engine",
    "create_compliance_manager",
    "create_analytics_engine",
    "create_currency_converter",
    
    # Data models
    "PaymentTransaction",
    "PayoutSchedule", 
    "PaymentMethod",
    "RevenueAllocation",
    "TaxConfiguration",
    "PaymentProvider",
    "FraudAnalysis",
    "ComplianceCheck",
    
    # Core components
    "PaymentValidator",
    "PayoutScheduler",
    "PaymentAnalytics", 
    "ComplianceManager",
    "FraudDetectionEngine",
    "PerformanceCache",
    "CurrencyConverter",
    
    # Configuration
    "PaymentConfig",
    
    # Exceptions
    "PaymentProcessingError",
    "InsufficientFundsError",
    "InvalidPaymentMethodError",
    "FraudDetectedError",
    "ComplianceError",
    "PaymentDeclinedError",
    "PayoutFailedError",
]
