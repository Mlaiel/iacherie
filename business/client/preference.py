"""Preference Manager - Client preferences and settings management.

Manages comprehensive user preferences including privacy settings, notification
preferences, content settings, and platform customization for creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Advanced Content Protection
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
import logging
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, validator

from ...core.database import get_db
from ...core.exceptions import (
    PreferenceServiceError,
    InvalidPreferenceError
)
from ...models.preference import (
    ClientPreference, PreferenceCategory, PreferenceType,
    NotificationSetting, PrivacySetting, ContentSetting
)
from ...services.notification.preferences import NotificationPreferenceService
from ...services.privacy.settings import PrivacySettingsService
from ...services.cache.redis_cache import RedisCache
from ...utils.validation import ValidationUtils


logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """
Available notification channels."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class PrivacyLevel(str, Enum):
    """Privacy levels for various settings."""

    PUBLIC = "public"
    FOLLOWERS = "followers"
    VERIFIED_ONLY = "verified_only"
    PRIVATE = "private"


class ContentVisibility(str, Enum):
    """Content visibility options."""

    PUBLIC = "public"
    UNLISTED = "unlisted"
    FOLLOWERS_ONLY = "followers_only"
    PRIVATE = "private"


class NotificationPreferenceData(BaseModel):
    """Notification preference settings."""
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    
    # Specific notification types
    content_interactions: bool = True
    collaboration_requests: bool = True
    security_alerts: bool = True
    marketing_updates: bool = False
    platform_updates: bool = True
    payment_notifications: bool = True
    content_protection_alerts: bool = True
    
    # Frequency settings
    digest_frequency: str = "daily"  # immediate, daily, weekly, never
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "08:00"
    timezone: str = "UTC"
    
    @validator('digest_frequency')
    def validate_digest_frequency(cls, v):
        allowed = ['immediate', 'daily', 'weekly', 'never']
        if v not in allowed:
            raise ValueError(f'Digest frequency must be one of: {", ".join(allowed)}')
        return v


class PrivacyPreferenceData(BaseModel):
    """Privacy preference settings."""
    profile_visibility: PrivacyLevel = PrivacyLevel.PUBLIC
    content_default_visibility: ContentVisibility = ContentVisibility.PUBLIC
    show_online_status: bool = True
    show_last_active: bool = True
    allow_direct_messages: PrivacyLevel = PrivacyLevel.PUBLIC
    allow_collaboration_requests: PrivacyLevel = PrivacyLevel.PUBLIC
    show_follower_count: bool = True
    show_following_count: bool = True
    show_analytics: bool = False
    allow_content_downloads: bool = True
    show_location: bool = False
    allow_tagging: PrivacyLevel = PrivacyLevel.FOLLOWERS
    data_sharing_consent: bool = False
    analytics_tracking_consent: bool = True
    
    @validator('profile_visibility', 'allow_direct_messages', 'allow_collaboration_requests', 'allow_tagging')
    def validate_privacy_level(cls, v):
        if isinstance(v, str):
            try:
                return PrivacyLevel(v)
            except ValueError:
                raise ValueError(f'Invalid privacy level: {v}')
        return v


class ContentPreferenceData(BaseModel):
    """
Content preference settings."""
    default_language: str = "en"
    content_quality: str = "high"  # low, medium, high, ultra
    auto_generate_thumbnails: bool = True
    auto_generate_captions: bool = True
    auto_seo_optimization: bool = True
    watermark_enabled: bool = False
    watermark_style: str = "subtle"  # subtle, prominent, custom
    auto_protection_enabled: bool = True
    allow_ai_analysis: bool = True
    enable_collaboration_features: bool = True
    default_licensing: str = "all_rights_reserved"
    content_categories: List[str] = []
    blocked_keywords: List[str] = []
    preferred_upload_format: Optional[str] = None
    
    @validator('content_quality')
    def validate_content_quality(cls, v):
        allowed = ['low', 'medium', 'high', 'ultra']
        if v not in allowed:
            raise ValueError(f'Content quality must be one of: {", ".join(allowed)}')
        return v
        
    @validator('watermark_style')
    def validate_watermark_style(cls, v):
        allowed = ['subtle', 'prominent', 'custom']
        if v not in allowed:
            raise ValueError(f'Watermark style must be one of: {", ".join(allowed)}')
        return v


class InterfacePreferenceData(BaseModel):
    """User interface preference settings."""
    theme: str = "system"  # light, dark, system
    language: str = "en"
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "24h"  # 12h, 24h
    currency: str = "USD"
    number_format: str = "1,234.56"
    dashboard_layout: str = "default"
    sidebar_collapsed: bool = False
    show_tooltips: bool = True
    enable_animations: bool = True
    keyboard_shortcuts_enabled: bool = True
    accessibility_mode: bool = False
    font_size: str = "medium"  # small, medium, large, x-large
    high_contrast: bool = False
    
    @validator('theme')
    def validate_theme(cls, v):
        allowed = ['light', 'dark', 'system']
        if v not in allowed:
            raise ValueError(f'Theme must be one of: {", ".join(allowed)}')
        return v
        
    @validator('time_format')
    def validate_time_format(cls, v):
        allowed = ['12h', '24h']
        if v not in allowed:
            raise ValueError(f'Time format must be one of: {", ".join(allowed)}')
        return v


class PreferenceManager:
    """
    Comprehensive preference management system for creators.
    
    Features:
    - Multi-category preference management
    - Real-time preference updates
    - Privacy and security settings
    - Notification customization
    - Content management preferences
    - Interface personalization
    - Preference validation and defaults
    - Caching for performance optimization
    """
    
    def __init__(
        self,
        db: Session,
        notification_service: NotificationPreferenceService,
        privacy_service: PrivacySettingsService,
        redis_cache: RedisCache
    ):
        self.db = db
        self.notification_service = notification_service
        self.privacy_service = privacy_service
        self.redis_cache = redis_cache
        self.validation_utils = ValidationUtils()
        
        # Default preferences for new clients
        self.default_preferences = {
            PreferenceCategory.NOTIFICATION: NotificationPreferenceData().dict(),
            PreferenceCategory.PRIVACY: PrivacyPreferenceData().dict(),
            PreferenceCategory.CONTENT: ContentPreferenceData().dict(),
            PreferenceCategory.INTERFACE: InterfacePreferenceData().dict()
        }
        
    async def initialize_client_preferences(self, client_id: UUID) -> Dict[str, Any]:
        """
        Initialize default preferences for new client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Initialized preferences
        """
        try:
            preferences_created = {}
            
            for category, default_values in self.default_preferences.items():
                preference = ClientPreference(
                    client_id=client_id,
                    category=category,
                    preferences=default_values,
                    is_active=True
                )
                
                self.db.add(preference)
                preferences_created[category.value] = default_values
                
            self.db.commit()
            
            # Cache preferences
            await self._cache_client_preferences(client_id, preferences_created)
            
            logger.info(f"Default preferences initialized for client: {client_id}")
            
            return preferences_created
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error initializing preferences: {e}")
            raise PreferenceServiceError("Failed to initialize preferences") from e
            
    async def get_client_preferences(
        self,
        client_id: UUID,
        category: Optional[PreferenceCategory] = None
    ) -> Dict[str, Any]:
        """
        Get client preferences by category or all preferences.
        
        Args:
            client_id: Client identifier
            category: Optional specific category
            
        Returns:
            Client preferences data
        """
        try:
            # Try cache first
            cache_key = f"preferences:{client_id}"
            cached_preferences = await self.redis_cache.get(cache_key)
            
            if cached_preferences:
                if category:
                    return cached_preferences.get(category.value, {})
                return cached_preferences
                
            # Fetch from database
            query = self.db.query(ClientPreference).filter(
                ClientPreference.client_id == client_id,
                ClientPreference.is_active == True
            )
            
            if category:
                query = query.filter(ClientPreference.category == category)
                
            preferences = query.all()
            
            # Format preferences
            formatted_preferences = {}
            for pref in preferences:
                formatted_preferences[pref.category.value] = pref.preferences
                
            # Cache for future requests
            if not category:  # Only cache full preference set
                await self._cache_client_preferences(client_id, formatted_preferences)
                
            if category:
                return formatted_preferences.get(category.value, {})
                
            return formatted_preferences
            
        except Exception as e:
            logger.error(f"Error retrieving preferences for client {client_id}: {e}")
            raise PreferenceServiceError("Failed to retrieve preferences") from e
            
    async def update_notification_preferences(
        self,
        client_id: UUID,
        notification_data: NotificationPreferenceData
    ) -> Dict[str, Any]:
        """
        Update notification preferences for client.
        
        Args:
            client_id: Client identifier
            notification_data: Updated notification preferences
            
        Returns:
            Updated preferences
        """
        try:
            # Get existing preference record
            preference = self.db.query(ClientPreference).filter(
                ClientPreference.client_id == client_id,
                ClientPreference.category == PreferenceCategory.NOTIFICATION,
                ClientPreference.is_active == True
            ).first()
            
            notification_dict = notification_data.dict()
            
            if preference:
                # Update existing preference
                preference.preferences = notification_dict
                preference.updated_at = datetime.utcnow()
            else:
                # Create new preference record
                preference = ClientPreference(
                    client_id=client_id,
                    category=PreferenceCategory.NOTIFICATION,
                    preferences=notification_dict,
                    is_active=True
                )
                self.db.add(preference)
                
            self.db.commit()
            
            # Update notification service
            await self.notification_service.update_client_preferences(
                client_id, notification_dict
            )
            
            # Clear cache to force refresh
            await self._clear_preference_cache(client_id)
            
            logger.info(f"Notification preferences updated for client: {client_id}")
            
            return notification_dict
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating notification preferences: {e}")
            raise PreferenceServiceError("Failed to update notification preferences") from e
            
    async def update_privacy_preferences(
        self,
        client_id: UUID,
        privacy_data: PrivacyPreferenceData
    ) -> Dict[str, Any]:
        """
        Update privacy preferences for client.
        
        Args:
            client_id: Client identifier
            privacy_data: Updated privacy preferences
            
        Returns:
            Updated preferences
        """
        try:
            # Get existing preference record
            preference = self.db.query(ClientPreference).filter(
                ClientPreference.client_id == client_id,
                ClientPreference.category == PreferenceCategory.PRIVACY,
                ClientPreference.is_active == True
            ).first()
            
            privacy_dict = privacy_data.dict()
            
            if preference:
                preference.preferences = privacy_dict
                preference.updated_at = datetime.utcnow()
            else:
                preference = ClientPreference(
                    client_id=client_id,
                    category=PreferenceCategory.PRIVACY,
                    preferences=privacy_dict,
                    is_active=True
                )
                self.db.add(preference)
                
            self.db.commit()
            
            # Update privacy service
            await self.privacy_service.update_client_settings(
                client_id, privacy_dict
            )
            
            # Clear cache
            await self._clear_preference_cache(client_id)
            
            logger.info(f"Privacy preferences updated for client: {client_id}")
            
            return privacy_dict
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating privacy preferences: {e}")
            raise PreferenceServiceError("Failed to update privacy preferences") from e
            
    async def update_content_preferences(
        self,
        client_id: UUID,
        content_data: ContentPreferenceData
    ) -> Dict[str, Any]:
        """
        Update content preferences for client.
        
        Args:
            client_id: Client identifier
            content_data: Updated content preferences
            
        Returns:
            Updated preferences
        """
        try:
            preference = self.db.query(ClientPreference).filter(
                ClientPreference.client_id == client_id,
                ClientPreference.category == PreferenceCategory.CONTENT,
                ClientPreference.is_active == True
            ).first()
            
            content_dict = content_data.dict()
            
            if preference:
                preference.preferences = content_dict
                preference.updated_at = datetime.utcnow()
            else:
                preference = ClientPreference(
                    client_id=client_id,
                    category=PreferenceCategory.CONTENT,
                    preferences=content_dict,
                    is_active=True
                )
                self.db.add(preference)
                
            self.db.commit()
            
            # Clear cache
            await self._clear_preference_cache(client_id)
            
            logger.info(f"Content preferences updated for client: {client_id}")
            
            return content_dict
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating content preferences: {e}")
            raise PreferenceServiceError("Failed to update content preferences") from e
            
    async def update_interface_preferences(
        self,
        client_id: UUID,
        interface_data: InterfacePreferenceData
    ) -> Dict[str, Any]:
        """
        Update interface preferences for client.
        
        Args:
            client_id: Client identifier
            interface_data: Updated interface preferences
            
        Returns:
            Updated preferences
        """
        try:
            preference = self.db.query(ClientPreference).filter(
                ClientPreference.client_id == client_id,
                ClientPreference.category == PreferenceCategory.INTERFACE,
                ClientPreference.is_active == True
            ).first()
            
            interface_dict = interface_data.dict()
            
            if preference:
                preference.preferences = interface_dict
                preference.updated_at = datetime.utcnow()
            else:
                preference = ClientPreference(
                    client_id=client_id,
                    category=PreferenceCategory.INTERFACE,
                    preferences=interface_dict,
                    is_active=True
                )
                self.db.add(preference)
                
            self.db.commit()
            
            # Clear cache
            await self._clear_preference_cache(client_id)
            
            logger.info(f"Interface preferences updated for client: {client_id}")
            
            return interface_dict
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating interface preferences: {e}")
            raise PreferenceServiceError("Failed to update interface preferences") from e
            
    async def update_specific_preference(
        self,
        client_id: UUID,
        category: PreferenceCategory,
        preference_key: str,
        preference_value: Any
    ) -> Dict[str, Any]:
        """
        Update a specific preference value.
        
        Args:
            client_id: Client identifier
            category: Preference category
            preference_key: Specific preference key
            preference_value: New preference value
            
        Returns:
            Updated preference data
        """
        try:
            # Get current preferences
            current_preferences = await self.get_client_preferences(client_id, category)
            
            # Validate preference key exists in category
            if preference_key not in current_preferences:
                raise InvalidPreferenceError(f"Unknown preference key: {preference_key}")
                
            # Update specific preference
            current_preferences[preference_key] = preference_value
            
            # Get preference record
            preference = self.db.query(ClientPreference).filter(
                ClientPreference.client_id == client_id,
                ClientPreference.category == category,
                ClientPreference.is_active == True
            ).first()
            
            if preference:
                preference.preferences = current_preferences
                preference.updated_at = datetime.utcnow()
                self.db.commit()
                
                # Clear cache
                await self._clear_preference_cache(client_id)
                
                logger.info(f"Preference {preference_key} updated for client: {client_id}")
                
                return current_preferences
            else:
                raise PreferenceServiceError("Preference record not found")
                
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating specific preference: {e}")
            raise PreferenceServiceError("Failed to update preference") from e
            
    async def reset_preferences(
        self,
        client_id: UUID,
        category: Optional[PreferenceCategory] = None
    ) -> Dict[str, Any]:
        """
        Reset preferences to defaults.
        
        Args:
            client_id: Client identifier
            category: Optional specific category to reset
            
        Returns:
            Reset preferences
        """
        try:
            if category:
                # Reset specific category
                preference = self.db.query(ClientPreference).filter(
                    ClientPreference.client_id == client_id,
                    ClientPreference.category == category,
                    ClientPreference.is_active == True
                ).first()
                
                if preference:
                    default_values = self.default_preferences[category]
                    preference.preferences = default_values
                    preference.updated_at = datetime.utcnow()
                    
                self.db.commit()
                
                result = {category.value: default_values}
            else:
                # Reset all preferences
                preferences = self.db.query(ClientPreference).filter(
                    ClientPreference.client_id == client_id,
                    ClientPreference.is_active == True
                ).all()
                
                result = {}
                for preference in preferences:
                    default_values = self.default_preferences[preference.category]
                    preference.preferences = default_values
                    preference.updated_at = datetime.utcnow()
                    result[preference.category.value] = default_values
                    
                self.db.commit()
                
            # Clear cache
            await self._clear_preference_cache(client_id)
            
            logger.info(f"Preferences reset for client: {client_id}")
            
            return result
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error resetting preferences: {e}")
            raise PreferenceServiceError("Failed to reset preferences") from e
            
    async def export_preferences(self, client_id: UUID) -> Dict[str, Any]:
        """
        Export all client preferences for backup/migration.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Exported preferences data
        """
        try:
            preferences = await self.get_client_preferences(client_id)
            
            export_data = {
                "client_id": str(client_id),
                "exported_at": datetime.utcnow().isoformat(),
                "preferences": preferences,
                "version": "2.1.0"
            }
            
            logger.info(f"Preferences exported for client: {client_id}")
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting preferences: {e}")
            raise PreferenceServiceError("Failed to export preferences") from e
            
    async def import_preferences(
        self,
        client_id: UUID,
        preferences_data: Dict[str, Any],
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Import preferences from exported data.
        
        Args:
            client_id: Client identifier
            preferences_data: Exported preferences data
            overwrite: Whether to overwrite existing preferences
            
        Returns:
            Import result
        """
        try:
            imported_categories = []
            
            for category_name, category_prefs in preferences_data.get("preferences", {}).items():
                try:
                    category = PreferenceCategory(category_name)
                except ValueError:
                    logger.warning(f"Unknown preference category: {category_name}")
                    continue
                    
                # Check if preference exists
                existing_pref = self.db.query(ClientPreference).filter(
                    ClientPreference.client_id == client_id,
                    ClientPreference.category == category,
                    ClientPreference.is_active == True
                ).first()
                
                if existing_pref and not overwrite:
                    logger.info(f"Skipping existing preference category: {category_name}")
                    continue
                    
                if existing_pref:
                    existing_pref.preferences = category_prefs
                    existing_pref.updated_at = datetime.utcnow()
                else:
                    preference = ClientPreference(
                        client_id=client_id,
                        category=category,
                        preferences=category_prefs,
                        is_active=True
                    )
                    self.db.add(preference)
                    
                imported_categories.append(category_name)
                
            self.db.commit()
            
            # Clear cache
            await self._clear_preference_cache(client_id)
            
            logger.info(f"Preferences imported for client: {client_id}")
            
            return {
                "success": True,
                "imported_categories": imported_categories,
                "imported_at": datetime.utcnow().isoformat()
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error importing preferences: {e}")
            raise PreferenceServiceError("Failed to import preferences") from e
            
    async def _cache_client_preferences(
        self,
        client_id: UUID,
        preferences: Dict[str, Any]
    ) -> None:
        """Cache client preferences for performance."""
        cache_key = f"preferences:{client_id}"
        await self.redis_cache.set(
            cache_key, preferences, expire_seconds=3600  # 1 hour
        )
        
    async def _clear_preference_cache(self, client_id: UUID) -> None:
        """Clear cached preferences for client."""
        cache_key = f"preferences:{client_id}"
        await self.redis_cache.delete(cache_key)
