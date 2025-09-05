#!/usr/bin/env python3
"""
Payment Module for Ainflue Platform
===================================

Enterprise-grade payment processing system supporting multiple providers,
currencies, and payment methods including traditional payments and cryptocurrencies.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

from .multi_provider_gateway import (
    MultiProviderPaymentGateway,
    PaymentRequest,
    PaymentResponse,
    PaymentType,
    PaymentProvider,
    PaymentStatus
)

from .processors import *

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Enterprise payment processing system for Ainflue platform"

__all__ = [
    # Main Gateway
    'MultiProviderPaymentGateway',
    'PaymentRequest',
    'PaymentResponse',
    'PaymentType',
    'PaymentProvider',
    'PaymentStatus',
    
    # All processor exports are included via processors import
]