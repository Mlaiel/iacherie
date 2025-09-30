"""Payment Gateways Integration Module
=====================================

Enterprise payment processing integrations for Ainflue platform.
Supports multiple payment providers for global creator monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .stripe_integration import StripePaymentProcessor
from .paypal_integration import PayPalPaymentProcessor  
from .wise_integration import WisePaymentProcessor
from .square_integration import SquarePaymentProcessor

try:
    from .adyen_integration import AdyenPaymentProcessor
except ImportError:
    AdyenPaymentProcessor = None

try:
    from .braintree_integration import BraintreePaymentProcessor
except ImportError:
    BraintreePaymentProcessor = None

try:
    from .razorpay_integration import RazorpayPaymentProcessor
except ImportError:
    RazorpayPaymentProcessor = None

try:
    from .cryptocurrency_gateways import CryptocurrencyPaymentProcessor
except ImportError:
    CryptocurrencyPaymentProcessor = None

try:
    from .apple_pay_integration import ApplePayIntegration
except ImportError:
    ApplePayIntegration = None

try:
    from .google_pay_integration import GooglePayIntegration
except ImportError:
    GooglePayIntegration = None

try:
    from .payment_aggregator import PaymentAggregator
except ImportError:
    PaymentAggregator = None

__all__ = [
    'StripePaymentProcessor',
    'PayPalPaymentProcessor', 
    'WisePaymentProcessor',
    'SquarePaymentProcessor',
    'AdyenPaymentProcessor',
    'BraintreePaymentProcessor',
    'RazorpayPaymentProcessor',
    'CryptocurrencyPaymentProcessor',
    'ApplePayIntegration',
    'GooglePayIntegration',
    'PaymentAggregator'
]

# Payment processor registry
PAYMENT_PROCESSORS = {
    'stripe': StripePaymentProcessor,
    'paypal': PayPalPaymentProcessor,
    'wise': WisePaymentProcessor,
    'square': SquarePaymentProcessor,
}

if AdyenPaymentProcessor:
    PAYMENT_PROCESSORS['adyen'] = AdyenPaymentProcessor
if BraintreePaymentProcessor:
    PAYMENT_PROCESSORS['braintree'] = BraintreePaymentProcessor
if RazorpayPaymentProcessor:
    PAYMENT_PROCESSORS['razorpay'] = RazorpayPaymentProcessor
if CryptocurrencyPaymentProcessor:
    PAYMENT_PROCESSORS['crypto'] = CryptocurrencyPaymentProcessor
