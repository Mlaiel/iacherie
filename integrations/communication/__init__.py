"""Communication Services Module - Multi-Channel Communication Platform
====================================================================

Enterprise communication services for notifications, campaigns, and messaging
across multiple channels and platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .notification_manager import NotificationManager, NotificationChannel, NotificationPriority
from .push_notification import PushNotificationService, PushNotificationType
from .email_campaigns import EmailCampaignManager, EmailTemplate, CampaignStatus
from .sms_campaigns import SMSCampaignManager, SMSTemplate, SMSProvider
from .chat_integration import ChatIntegration, ChatPlatform, ChatMessage
from .video_conferencing import VideoConferencingService, ConferenceProvider
from .voice_services import VoiceService, VoiceProvider, VoiceCallType
from .collaboration_tools import CollaborationManager, CollaborationPlatform

__all__ = [
    'NotificationManager',
    'NotificationChannel', 
    'NotificationPriority',
    'PushNotificationService',
    'PushNotificationType',
    'EmailCampaignManager',
    'EmailTemplate',
    'CampaignStatus',
    'SMSCampaignManager',
    'SMSTemplate',
    'SMSProvider',
    'ChatIntegration',
    'ChatPlatform',
    'ChatMessage',
    'VideoConferencingService',
    'ConferenceProvider',
    'VoiceService',
    'VoiceProvider',
    'VoiceCallType',
    'CollaborationManager',
    'CollaborationPlatform'
]

# Module version
__version__ = "1.0.0"

# Module metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."