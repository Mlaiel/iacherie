"""Infrastructure External Services Module - IA-Influencer-Agent Platform
=========================================================================
External integrations and third-party service connectors

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved

This module consolidates external service integrations:
- AI services integration
- Blockchain networks connectivity  
- Payment gateways integration
- Social media APIs connectivity
"""

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Import external service modules with error handling
import logging

logger = logging.getLogger(__name__)

# Import modules with graceful error handling
try:
    from .ai_services import *
except ImportError as e:
    logger.warning(f"Failed to import ai_services: {e}")

try:
    from .blockchain_networks import *
except ImportError as e:
    logger.warning(f"Failed to import blockchain_networks: {e}")

try:
    from .payment_gateways import *
except ImportError as e:
    logger.warning(f"Failed to import payment_gateways: {e}")

try:
    from .social_media_apis import *
except ImportError as e:
    logger.warning(f"Failed to import social_media_apis: {e}")

__all__ = [
    # AI Services
    "AIServiceManager",
    "OpenAIConnector",
    "AnthropicConnector",
    "HuggingFaceConnector",
    
    # Blockchain Networks
    "BlockchainManager",
    "EthereumConnector",
    "PolygonConnector",
    "SolanaConnector",
    
    # Payment Gateways
    "PaymentManager",
    "StripeConnector",
    "PayPalConnector",
    "CryptoPaymentConnector",
    
    # Social Media APIs
    "SocialMediaManager",
    "TwitterAPIConnector",
    "InstagramAPIConnector",
    "TikTokAPIConnector",
    "YouTubeAPIConnector"
]