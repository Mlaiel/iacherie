"""Backend Integrations Module
Integration services for external APIs and platforms

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Existing integrations
from .openai import OpenAIIntegration
from .elevenlabs import ElevenLabsIntegration
from .midjourney import MidjourneyIntegration
from .stripe_connect import StripeConnectIntegration
from .shopify import ShopifyIntegration

# New comprehensive integrations
from .social_media_hub import SocialMediaHubIntegration
from .payment_gateways import PaymentGatewaysIntegration
from .communication_apis import CommunicationAPIsIntegration
from .audio_platforms import AudioPlatformsIntegration
from .security_compliance import SecurityComplianceIntegration
from .webhook_manager import WebhookManagerIntegration

__all__ = [
    # Existing integrations
    "OpenAIIntegration",
    "ElevenLabsIntegration", 
    "MidjourneyIntegration",
    "StripeConnectIntegration",
    "ShopifyIntegration",
    
    # New comprehensive integrations
    "SocialMediaHubIntegration",
    "PaymentGatewaysIntegration",
    "CommunicationAPIsIntegration",
    "AudioPlatformsIntegration",
    "SecurityComplianceIntegration",
    "WebhookManagerIntegration"
]