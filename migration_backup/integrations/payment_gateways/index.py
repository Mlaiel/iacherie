"""
Payment Gateways Module - IA Chéries Integrations
=============================================
Enterprise-grade payment processing providing comprehensive payment gateway
integrations, fraud detection, subscription management, and global
payment solutions across multiple currencies and regions.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations
Version: 1.0 Production
"""

# Import all payment gateway components
from .stripe_integration import *
from .paypal_integration import *
from .square_integration import *
from .braintree_integration import *
from .adyen_integration import *
from .razorpay_integration import *
from .mercadopago_integration import *
from .wise_integration import *
from .apple_pay_integration import *
from .google_pay_integration import *
from .cryptocurrency_gateways import *
from .fraud_detection import *
from .payment_aggregator import *
from .payout_manager import *
from .subscription_manager import *

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise payment processing infrastructure for global monetization"

# Configuration logique métier IA Chéries
IA CHÉRIES_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'payment_gateways': 15,
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}