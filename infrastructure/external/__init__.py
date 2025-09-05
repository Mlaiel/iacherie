"""Infrastructure External Integrations - IA-Influencer-Agent Platform
=====================================================================
External service integrations for the infrastructure module

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved

This module provides integrations with external services:
- AI Services (OpenAI, Anthropic, etc.)
- Blockchain Networks (Ethereum, Polygon, etc.)
- Payment Gateways (Stripe, PayPal, etc.)
- Social Media APIs (Twitter, Instagram, etc.)
"""

# Import all external integration modules
try:
    from .ai_services import *
except ImportError:
    pass

try:
    from .blockchain_networks import *
except ImportError:
    pass

try:
    from .payment_gateways import *
except ImportError:
    pass

try:
    from .social_media_apis import *
except ImportError:
    pass

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Collect all exports from submodules
__all__ = []

# Add exports from each submodule if they exist
try:
    from . import ai_services
    if hasattr(ai_services, '__all__'):
        __all__.extend(ai_services.__all__)
except ImportError:
    pass

try:
    from . import blockchain_networks
    if hasattr(blockchain_networks, '__all__'):
        __all__.extend(blockchain_networks.__all__)
except ImportError:
    pass

try:
    from . import payment_gateways
    if hasattr(payment_gateways, '__all__'):
        __all__.extend(payment_gateways.__all__)
except ImportError:
    pass

try:
    from . import social_media_apis
    if hasattr(social_media_apis, '__all__'):
        __all__.extend(social_media_apis.__all__)
except ImportError:
    pass