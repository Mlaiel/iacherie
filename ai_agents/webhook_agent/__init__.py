"""
Webhook Agent Module - Industrial-Grade Real-Time Event Processing System

Enterprise webhook management system for real-time platform integrations, event processing,
and automated notification handling across multi-platform content protection ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written 
permission from Fahed Mlaiel <mlaiel@live.de> is strictly prohibited and will result
in immediate legal action under German and international copyright law.

Project: IA-Influencer-Agent Multi-Platform Content Protection System
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

from .webhook_agent import WebhookAgent
from .webhook_manager import WebhookManager
from .event_processor import EventProcessor
from .signature_validator import SignatureValidator
from .notification_dispatcher import NotificationDispatcher
from .webhook_registry import WebhookRegistry
from .payload_transformer import PayloadTransformer
from .webhook_analytics import WebhookAnalytics
from .retry_handler import RetryHandler
from .webhook_security import WebhookSecurity

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "WebhookAgent",
    "WebhookManager", 
    "EventProcessor",
    "SignatureValidator",
    "NotificationDispatcher",
    "WebhookRegistry",
    "PayloadTransformer",
    "WebhookAnalytics",
    "RetryHandler",
    "WebhookSecurity"
]
