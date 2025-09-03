"""Notification Preferences Module

Service layer for managing user notification preferences.
Provides clean abstractions over the core preferences infrastructure.
"""

from .user_preferences import UserPreferencesService

__all__ = [
    "UserPreferencesService"
]