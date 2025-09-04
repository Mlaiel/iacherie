"""Backend API Module
Consolidated API routes for the Ainflue platform.

This module consolidates all API routes into three main categories:
- Core API: Authentication, content management, analytics, monitoring, platform integration, GDPR
- Business API: Monetization, payments, collaboration, fingerprinting, protection, licensing, webhooks, alerts, AI agents
- Public API: Public-facing API for developers, SDK integration, and testing sandbox

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .core_api import core_router
from .business_api import business_router
from .public import public_router

__all__ = [
    "core_router", 
    "business_router",
    "public_router"
]