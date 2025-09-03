"""📱 Notification System - Backend Services Layer

Enterprise notification service layer that organizes notification functionality
into clean, maintainable service modules.

This module provides a service layer abstraction over the core notification
infrastructure, organizing channels, templates, and preferences management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Architecture:
- channels/: Multi-channel notification delivery services
- templates/: Template management and rendering services  
- preferences/: User notification preferences management
"""

from .channels import (
    EmailSenderService,
    PushNotificationService, 
    SMSSenderService,
    InAppNotificationService
)

from .templates import TemplateManagerService

from .preferences import UserPreferencesService

__all__ = [
    # Channel services
    "EmailSenderService",
    "PushNotificationService", 
    "SMSSenderService",
    "InAppNotificationService",
    
    # Template services
    "TemplateManagerService",
    
    # Preferences services
    "UserPreferencesService"
]