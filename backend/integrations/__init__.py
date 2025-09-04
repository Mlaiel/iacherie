"""Backend Integrations Module
Integration services for external APIs and platforms

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .openai import OpenAIIntegration
from .elevenlabs import ElevenLabsIntegration
from .midjourney import MidjourneyIntegration
from .stripe_connect import StripeConnectIntegration
from .shopify import ShopifyIntegration

__all__ = [
    "OpenAIIntegration",
    "ElevenLabsIntegration", 
    "MidjourneyIntegration",
    "StripeConnectIntegration",
    "ShopifyIntegration"
]