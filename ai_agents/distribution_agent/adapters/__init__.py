"""Platform Adapters Module - Multi-Platform Integration Framework

Enterprise-grade platform adapters for seamless integration with all major
content distribution platforms including social media, streaming, and monetization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from .base_adapter import (
    BasePlatformAdapter,
    PlatformCredentials,
    PublishRequest,
    PublishResponse,
    AnalyticsRequest,
    AnalyticsResponse,
    AdapterStatus,
    RequestMethod
)

__all__ = [
    "BasePlatformAdapter",
    "PlatformCredentials",
    "PublishRequest",
    "PublishResponse",
    "AnalyticsRequest",
    "AnalyticsResponse",
    "AdapterStatus",
    "RequestMethod"
]
