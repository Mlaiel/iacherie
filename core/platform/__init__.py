"""Ainflue Core Platform Services - Enterprise Platform Infrastructure
==================================================================

Core platform services providing API gateways, GraphQL federation,
WebSocket management, real-time synchronization, notification systems,
file storage, CDN management, search engines, and platform utilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any

# Platform service core files (all to be created)
try:
    from .api_gateway_core import APIGatewayCore
except ImportError:
    APIGatewayCore = None

try:
    from .graphql_federation_core import GraphQLFederationCore
except ImportError:
    GraphQLFederationCore = None

try:
    from .websocket_manager_core import WebSocketManagerCore
except ImportError:
    WebSocketManagerCore = None

try:
    from .real_time_sync_core import RealTimeSyncCore
except ImportError:
    RealTimeSyncCore = None

try:
    from .notification_system_core import NotificationSystemCore
except ImportError:
    NotificationSystemCore = None

try:
    from .email_service_core import EmailServiceCore
except ImportError:
    EmailServiceCore = None

try:
    from .sms_service_core import SMSServiceCore
except ImportError:
    SMSServiceCore = None

try:
    from .push_notification_core import PushNotificationCore
except ImportError:
    PushNotificationCore = None

try:
    from .file_storage_core import FileStorageCore
except ImportError:
    FileStorageCore = None

try:
    from .cdn_manager_core import CDNManagerCore
except ImportError:
    CDNManagerCore = None

try:
    from .media_transcoding_core import MediaTranscodingCore
except ImportError:
    MediaTranscodingCore = None

try:
    from .search_engine_core import SearchEngineCore
except ImportError:
    SearchEngineCore = None

try:
    from .indexing_service_core import IndexingServiceCore
except ImportError:
    IndexingServiceCore = None

try:
    from .geolocation_core import GeolocationCore
except ImportError:
    GeolocationCore = None

try:
    from .internationalization_core import InternationalizationCore
except ImportError:
    InternationalizationCore = None

try:
    from .localization_core import LocalizationCore
except ImportError:
    LocalizationCore = None

try:
    from .timezone_manager_core import TimezoneManagerCore
except ImportError:
    TimezoneManagerCore = None

try:
    from .feature_toggle_core import FeatureToggleCore
except ImportError:
    FeatureToggleCore = None

try:
    from .ab_testing_core import ABTestingCore
except ImportError:
    ABTestingCore = None

__all__ = [
    "APIGatewayCore", "GraphQLFederationCore", "WebSocketManagerCore",
    "RealTimeSyncCore", "NotificationSystemCore", "EmailServiceCore",
    "SMSServiceCore", "PushNotificationCore", "FileStorageCore",
    "CDNManagerCore", "MediaTranscodingCore", "SearchEngineCore",
    "IndexingServiceCore", "GeolocationCore", "InternationalizationCore",
    "LocalizationCore", "TimezoneManagerCore", "FeatureToggleCore",
    "ABTestingCore"
]