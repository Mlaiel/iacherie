"""🚀 Platform Core Notifications - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/platform_core/notifications/
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE NOTIFICATIONS MULTI-CANAL ENTERPRISE
Notifications intelligentes avec templates et targeting avancé
- Email/SMS/Push/In-app notifications
- Templates dynamiques avec personnalisation IA
- Scheduling et automation de campagnes
- Analytics et tracking des engagements
"""

from .notification_manager import (
    NotificationManager,
    TemplateManager,
    NotificationTemplate,
    NotificationRecipient,
    NotificationRequest,
    NotificationResult,
    NotificationType,
    NotificationPriority,
    NotificationStatus
)

__all__ = [
    "NotificationManager",
    "TemplateManager",
    "NotificationTemplate",
    "NotificationRecipient",
    "NotificationRequest",
    "NotificationResult",
    "NotificationType",
    "NotificationPriority",
    "NotificationStatus"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
