"""🚀 Notification Preference Manager - Enterprise User Control System
======================================================================
Module: platform_core/notifications/notification_preference_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 NOTIFICATION PREFERENCE MANAGER - ENTERPRISE USER CONTROL
- Gestion préférences utilisateurs granulaire
- Compliance GDPR/CCPA avec opt-in/opt-out
- Intelligent preference learning from behavior
- Frequency capping et quiet hours
- Multi-channel preference orchestration
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, timedelta, time
from dataclasses import dataclass, field
from enum import Enum
import pytz
import redis.asyncio as redis
from collections import defaultdict

logger = logging.getLogger(__name__)


class ChannelType(Enum):
    """Notification channel types."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationCategory(Enum):
    """Notification categories."""
    MARKETING = "marketing"
    TRANSACTIONAL = "transactional"
    SYSTEM = "system"
    SECURITY = "security"
    PRODUCT_UPDATES = "product_updates"
    SOCIAL = "social"
    CONTENT = "content"
    BILLING = "billing"
    SUPPORT = "support"


class FrequencyLimit(Enum):
    """Frequency limiting options."""
    UNLIMITED = "unlimited"
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class PreferenceScope(Enum):
    """Preference scope levels."""
    GLOBAL = "global"
    CHANNEL = "channel"
    CATEGORY = "category"
    TEMPLATE = "template"
    CAMPAIGN = "campaign"


class OptInStatus(Enum):
    """Opt-in status options."""
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"
    PENDING = "pending"
    UNKNOWN = "unknown"


@dataclass
class QuietHours:
    """Quiet hours configuration."""
    enabled: bool = False
    start_time: time = time(22, 0)  # 10 PM
    end_time: time = time(8, 0)     # 8 AM
    timezone: str = "UTC"
    days_of_week: List[int] = field(default_factory=lambda: list(range(7)))  # All days
    
    def is_quiet_time(self, check_time: datetime) -> bool:
        """Check if given time is within quiet hours."""
        try:
            if not self.enabled:
                return False
            
            # Convert to user timezone
            tz = pytz.timezone(self.timezone)
            user_time = check_time.astimezone(tz)
            
            # Check day of week
            if user_time.weekday() not in self.days_of_week:
                return False
            
            current_time = user_time.time()
            
            # Handle overnight quiet hours (e.g., 22:00 to 08:00)
            if self.start_time > self.end_time:
                return current_time >= self.start_time or current_time <= self.end_time
            else:
                return self.start_time <= current_time <= self.end_time
                
        except Exception as e:
            logger.error(f"Quiet hours check failed: {e}")
            return False


@dataclass
class FrequencySettings:
    """Frequency limiting settings."""
    channel: ChannelType
    category: NotificationCategory
    limit: FrequencyLimit
    max_count: int = 1
    time_window_hours: int = 24
    current_count: int = 0
    reset_at: Optional[datetime] = None


@dataclass
class ChannelPreference:
    """Channel-specific preferences."""
    channel: ChannelType
    enabled: bool = True
    opt_in_status: OptInStatus = OptInStatus.UNKNOWN
    opt_in_date: Optional[datetime] = None
    opt_out_date: Optional[datetime] = None
    frequency_settings: Dict[NotificationCategory, FrequencySettings] = field(default_factory=dict)
    quiet_hours: Optional[QuietHours] = None
    device_tokens: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CategoryPreference:
    """Category-specific preferences."""
    category: NotificationCategory
    enabled: bool = True
    opt_in_status: OptInStatus = OptInStatus.UNKNOWN
    priority_threshold: int = 1  # Minimum priority to receive notifications
    frequency_limit: FrequencyLimit = FrequencyLimit.UNLIMITED
    max_per_day: int = 10
    channels: Set[ChannelType] = field(default_factory=set)
    keywords_include: List[str] = field(default_factory=list)
    keywords_exclude: List[str] = field(default_factory=list)


@dataclass
class GlobalPreferences:
    """Global notification preferences."""
    user_id: str
    enabled: bool = True
    global_opt_in: OptInStatus = OptInStatus.UNKNOWN
    default_channels: Set[ChannelType] = field(default_factory=lambda: {ChannelType.EMAIL})
    timezone: str = "UTC"
    language: str = "en"
    quiet_hours: Optional[QuietHours] = None
    marketing_consent: bool = False
    marketing_consent_date: Optional[datetime] = None
    data_processing_consent: bool = False
    data_processing_consent_date: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserNotificationPreferences:
    """Complete user notification preferences."""
    user_id: str
    global_preferences: GlobalPreferences
    channel_preferences: Dict[ChannelType, ChannelPreference] = field(default_factory=dict)
    category_preferences: Dict[NotificationCategory, CategoryPreference] = field(default_factory=dict)
    template_preferences: Dict[str, bool] = field(default_factory=dict)  # template_id -> enabled
    campaign_preferences: Dict[str, bool] = field(default_factory=dict)  # campaign_id -> enabled
    suppression_list: Set[str] = field(default_factory=set)  # suppressed template/campaign IDs
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PreferenceUpdate:
    """Preference update request."""
    user_id: str
    scope: PreferenceScope
    target_id: str  # channel, category, template, or campaign ID
    property_name: str
    property_value: Any
    updated_at: datetime = field(default_factory=datetime.utcnow)
    source: str = "user"  # user, system, admin, api


@dataclass
class ConsentRecord:
    """Consent tracking record."""
    user_id: str
    consent_type: str
    status: bool
    timestamp: datetime
    source: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    legal_basis: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PreferenceLearningEngine:
    """AI-powered preference learning from user behavior."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def learn_from_behavior(self, user_id: str, behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Learn preferences from user behavior."""
        try:
            suggestions = {}
            
            # Analyze open rates by channel
            channel_engagement = behavioral_data.get('channel_engagement', {})
            for channel, metrics in channel_engagement.items():
                open_rate = metrics.get('open_rate', 0)
                click_rate = metrics.get('click_rate', 0)
                
                if open_rate < 0.1 and click_rate < 0.02:  # Very low engagement
                    suggestions[f'disable_{channel}'] = {
                        'action': 'suggest_disable',
                        'channel': channel,
                        'reason': 'Low engagement detected',
                        'confidence': 0.8
                    }
                elif open_rate > 0.5 and click_rate > 0.1:  # High engagement
                    suggestions[f'prioritize_{channel}'] = {
                        'action': 'suggest_prioritize',
                        'channel': channel,
                        'reason': 'High engagement detected',
                        'confidence': 0.9
                    }
            
            # Analyze category preferences
            category_engagement = behavioral_data.get('category_engagement', {})
            for category, metrics in category_engagement.items():
                engagement_score = metrics.get('engagement_score', 0)
                
                if engagement_score < 0.2:
                    suggestions[f'reduce_{category}'] = {
                        'action': 'suggest_reduce_frequency',
                        'category': category,
                        'reason': 'Low category engagement',
                        'confidence': 0.7
                    }
            
            # Analyze time-based patterns
            time_patterns = behavioral_data.get('time_patterns', {})
            inactive_hours = time_patterns.get('inactive_hours', [])
            if len(inactive_hours) > 8:  # More than 8 hours of inactivity
                suggested_quiet_hours = self._suggest_quiet_hours(inactive_hours)
                suggestions['quiet_hours'] = {
                    'action': 'suggest_quiet_hours',
                    'quiet_hours': suggested_quiet_hours,
                    'reason': 'Consistent inactivity pattern detected',
                    'confidence': 0.6
                }
            
            # Store learning insights
            await self._store_learning_insights(user_id, suggestions)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Preference learning failed: {e}")
            return {}
    
    def _suggest_quiet_hours(self, inactive_hours: List[int]) -> Dict[str, Any]:
        """Suggest quiet hours based on inactive hours."""
        try:
            # Find the longest consecutive sequence of inactive hours
            inactive_hours.sort()
            
            longest_start = inactive_hours[0]
            longest_end = inactive_hours[0]
            current_start = inactive_hours[0]
            current_end = inactive_hours[0]
            
            for i in range(1, len(inactive_hours)):
                if inactive_hours[i] == inactive_hours[i-1] + 1:
                    current_end = inactive_hours[i]
                else:
                    if current_end - current_start > longest_end - longest_start:
                        longest_start = current_start
                        longest_end = current_end
                    current_start = current_end = inactive_hours[i]
            
            # Final check
            if current_end - current_start > longest_end - longest_start:
                longest_start = current_start
                longest_end = current_end
            
            return {
                'start_hour': longest_start,
                'end_hour': (longest_end + 1) % 24,
                'confidence': min(0.9, (longest_end - longest_start) / 12)
            }
            
        except Exception as e:
            logger.error(f"Quiet hours suggestion failed: {e}")
            return {'start_hour': 22, 'end_hour': 8, 'confidence': 0.3}
    
    async def _store_learning_insights(self, user_id: str, insights: Dict[str, Any]) -> None:
        """Store learning insights for user."""
        try:
            insight_data = {
                'user_id': user_id,
                'insights': json.dumps(insights),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            await self.redis.hset(f"preference_insights:{user_id}", mapping=insight_data)
            await self.redis.expire(f"preference_insights:{user_id}", 30 * 24 * 3600)  # 30 days
            
        except Exception as e:
            logger.error(f"Failed to store learning insights: {e}")


class NotificationPreferenceManager:
    """Enterprise notification preference management system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis = redis.Redis(**config.get('redis', {}))
        self.learning_engine = PreferenceLearningEngine(self.redis)
        
        # Default preferences
        self.default_global_preferences = GlobalPreferences(
            user_id="",
            enabled=True,
            global_opt_in=OptInStatus.UNKNOWN,
            default_channels={ChannelType.EMAIL, ChannelType.IN_APP},
            timezone="UTC",
            language="en"
        )
        
        # Compliance settings
        self.require_explicit_consent = config.get('require_explicit_consent', True)
        self.gdpr_enabled = config.get('gdpr_enabled', True)
        self.ccpa_enabled = config.get('ccpa_enabled', True)
        
        # Preference cache
        self.preference_cache: Dict[str, UserNotificationPreferences] = {}
        self.cache_ttl = config.get('cache_ttl', 3600)  # 1 hour
    
    async def get_user_preferences(self, user_id: str) -> UserNotificationPreferences:
        """Get complete user notification preferences."""
        try:
            # Check cache first
            if user_id in self.preference_cache:
                return self.preference_cache[user_id]
            
            # Load from storage
            preferences = await self._load_user_preferences(user_id)
            
            if not preferences:
                # Create default preferences
                preferences = await self._create_default_preferences(user_id)
            
            # Cache preferences
            self.preference_cache[user_id] = preferences
            
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return await self._create_default_preferences(user_id)
    
    async def update_global_preferences(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update global notification preferences."""
        try:
            preferences = await self.get_user_preferences(user_id)
            
            # Track consent changes
            consent_updates = {}
            if 'marketing_consent' in updates:
                consent_updates['marketing'] = updates['marketing_consent']
            if 'data_processing_consent' in updates:
                consent_updates['data_processing'] = updates['data_processing_consent']
            
            # Update global preferences
            for key, value in updates.items():
                if hasattr(preferences.global_preferences, key):
                    setattr(preferences.global_preferences, key, value)
                    
                    # Special handling for consent fields
                    if key == 'marketing_consent':
                        preferences.global_preferences.marketing_consent_date = datetime.utcnow()
                    elif key == 'data_processing_consent':
                        preferences.global_preferences.data_processing_consent_date = datetime.utcnow()
            
            preferences.global_preferences.last_updated = datetime.utcnow()
            preferences.last_updated = datetime.utcnow()
            
            # Record consent changes
            for consent_type, status in consent_updates.items():
                await self._record_consent(user_id, consent_type, status, "user_update")
            
            # Save preferences
            await self._save_user_preferences(preferences)
            
            # Clear cache
            if user_id in self.preference_cache:
                del self.preference_cache[user_id]
            
            logger.info(f"Global preferences updated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update global preferences: {e}")
            return False
    
    async def update_channel_preferences(self, user_id: str, channel: ChannelType, 
                                       updates: Dict[str, Any]) -> bool:
        """Update channel-specific preferences."""
        try:
            preferences = await self.get_user_preferences(user_id)
            
            # Get or create channel preference
            if channel not in preferences.channel_preferences:
                preferences.channel_preferences[channel] = ChannelPreference(channel=channel)
            
            channel_pref = preferences.channel_preferences[channel]
            
            # Track opt-in/out changes
            if 'enabled' in updates:
                old_status = channel_pref.opt_in_status
                new_enabled = updates['enabled']
                
                if new_enabled and old_status != OptInStatus.OPT_IN:
                    channel_pref.opt_in_status = OptInStatus.OPT_IN
                    channel_pref.opt_in_date = datetime.utcnow()
                    await self._record_consent(user_id, f"{channel.value}_notifications", True, "user_update")
                elif not new_enabled and old_status != OptInStatus.OPT_OUT:
                    channel_pref.opt_in_status = OptInStatus.OPT_OUT
                    channel_pref.opt_out_date = datetime.utcnow()
                    await self._record_consent(user_id, f"{channel.value}_notifications", False, "user_update")
            
            # Update channel preferences
            for key, value in updates.items():
                if hasattr(channel_pref, key):
                    if key == 'quiet_hours' and isinstance(value, dict):
                        channel_pref.quiet_hours = QuietHours(**value)
                    else:
                        setattr(channel_pref, key, value)
            
            preferences.last_updated = datetime.utcnow()
            
            # Save preferences
            await self._save_user_preferences(preferences)
            
            # Clear cache
            if user_id in self.preference_cache:
                del self.preference_cache[user_id]
            
            logger.info(f"Channel preferences updated for user {user_id}, channel {channel.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update channel preferences: {e}")
            return False
    
    async def update_category_preferences(self, user_id: str, category: NotificationCategory,
                                        updates: Dict[str, Any]) -> bool:
        """Update category-specific preferences."""
        try:
            preferences = await self.get_user_preferences(user_id)
            
            # Get or create category preference
            if category not in preferences.category_preferences:
                preferences.category_preferences[category] = CategoryPreference(category=category)
            
            category_pref = preferences.category_preferences[category]
            
            # Track opt-in/out changes
            if 'enabled' in updates:
                if updates['enabled'] and category_pref.opt_in_status != OptInStatus.OPT_IN:
                    category_pref.opt_in_status = OptInStatus.OPT_IN
                    await self._record_consent(user_id, f"{category.value}_notifications", True, "user_update")
                elif not updates['enabled'] and category_pref.opt_in_status != OptInStatus.OPT_OUT:
                    category_pref.opt_in_status = OptInStatus.OPT_OUT
                    await self._record_consent(user_id, f"{category.value}_notifications", False, "user_update")
            
            # Update category preferences
            for key, value in updates.items():
                if hasattr(category_pref, key):
                    if key == 'channels' and isinstance(value, list):
                        category_pref.channels = set(ChannelType(c) for c in value)
                    else:
                        setattr(category_pref, key, value)
            
            preferences.last_updated = datetime.utcnow()
            
            # Save preferences
            await self._save_user_preferences(preferences)
            
            # Clear cache
            if user_id in self.preference_cache:
                del self.preference_cache[user_id]
            
            logger.info(f"Category preferences updated for user {user_id}, category {category.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update category preferences: {e}")
            return False
    
    async def can_send_notification(self, user_id: str, channel: ChannelType,
                                  category: NotificationCategory, template_id: str = None,
                                  campaign_id: str = None, priority: int = 1) -> Tuple[bool, str]:
        """Check if notification can be sent to user."""
        try:
            preferences = await self.get_user_preferences(user_id)
            
            # Check global preferences
            if not preferences.global_preferences.enabled:
                return False, "Global notifications disabled"
            
            if preferences.global_preferences.global_opt_in == OptInStatus.OPT_OUT:
                return False, "User globally opted out"
            
            # Check channel preferences
            if channel in preferences.channel_preferences:
                channel_pref = preferences.channel_preferences[channel]
                
                if not channel_pref.enabled:
                    return False, f"{channel.value} notifications disabled"
                
                if channel_pref.opt_in_status == OptInStatus.OPT_OUT:
                    return False, f"User opted out of {channel.value}"
                
                # Check quiet hours
                if channel_pref.quiet_hours:
                    if channel_pref.quiet_hours.is_quiet_time(datetime.utcnow()):
                        return False, "Within user's quiet hours"
            
            # Check category preferences
            if category in preferences.category_preferences:
                category_pref = preferences.category_preferences[category]
                
                if not category_pref.enabled:
                    return False, f"{category.value} notifications disabled"
                
                if category_pref.opt_in_status == OptInStatus.OPT_OUT:
                    return False, f"User opted out of {category.value}"
                
                if priority < category_pref.priority_threshold:
                    return False, f"Priority {priority} below threshold {category_pref.priority_threshold}"
                
                if channel not in category_pref.channels and category_pref.channels:
                    return False, f"{channel.value} not allowed for {category.value}"
            
            # Check template preferences
            if template_id and template_id in preferences.template_preferences:
                if not preferences.template_preferences[template_id]:
                    return False, f"Template {template_id} disabled"
            
            # Check campaign preferences
            if campaign_id and campaign_id in preferences.campaign_preferences:
                if not preferences.campaign_preferences[campaign_id]:
                    return False, f"Campaign {campaign_id} disabled"
            
            # Check suppression list
            if template_id and template_id in preferences.suppression_list:
                return False, f"Template {template_id} suppressed"
            
            if campaign_id and campaign_id in preferences.suppression_list:
                return False, f"Campaign {campaign_id} suppressed"
            
            # Check frequency limits
            frequency_check = await self._check_frequency_limits(user_id, channel, category)
            if not frequency_check[0]:
                return False, frequency_check[1]
            
            # Check compliance requirements
            compliance_check = await self._check_compliance_requirements(
                user_id, channel, category, preferences
            )
            if not compliance_check[0]:
                return False, compliance_check[1]
            
            return True, "Notification allowed"
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False, f"Permission check error: {str(e)}"
    
    async def record_notification_sent(self, user_id: str, channel: ChannelType,
                                     category: NotificationCategory, notification_id: str) -> None:
        """Record that a notification was sent to update frequency counters."""
        try:
            # Update frequency counters
            await self._update_frequency_counters(user_id, channel, category)
            
            # Store notification history
            notification_record = {
                'notification_id': notification_id,
                'user_id': user_id,
                'channel': channel.value,
                'category': category.value,
                'sent_at': datetime.utcnow().isoformat()
            }
            
            await self.redis.lpush(f"notification_history:{user_id}", json.dumps(notification_record))
            await self.redis.ltrim(f"notification_history:{user_id}", 0, 999)  # Keep last 1000
            
        except Exception as e:
            logger.error(f"Failed to record notification sent: {e}")
    
    async def get_unsubscribe_link(self, user_id: str, channel: ChannelType = None,
                                 category: NotificationCategory = None, 
                                 campaign_id: str = None) -> str:
        """Generate unsubscribe link for user."""
        try:
            # Create unsubscribe token
            unsubscribe_data = {
                'user_id': user_id,
                'channel': channel.value if channel else None,
                'category': category.value if category else None,
                'campaign_id': campaign_id,
                'created_at': datetime.utcnow().isoformat()
            }
            
            token = str(uuid.uuid4())
            await self.redis.setex(f"unsubscribe_token:{token}", 7 * 24 * 3600, json.dumps(unsubscribe_data))
            
            base_url = self.config.get('unsubscribe_base_url', 'https://app.ainflue.com/unsubscribe')
            return f"{base_url}?token={token}"
            
        except Exception as e:
            logger.error(f"Failed to generate unsubscribe link: {e}")
            return ""
    
    async def process_unsubscribe(self, token: str) -> bool:
        """Process unsubscribe request."""
        try:
            # Get unsubscribe data
            unsubscribe_data_str = await self.redis.get(f"unsubscribe_token:{token}")
            if not unsubscribe_data_str:
                return False
            
            unsubscribe_data = json.loads(unsubscribe_data_str)
            user_id = unsubscribe_data['user_id']
            channel = ChannelType(unsubscribe_data['channel']) if unsubscribe_data.get('channel') else None
            category = NotificationCategory(unsubscribe_data['category']) if unsubscribe_data.get('category') else None
            campaign_id = unsubscribe_data.get('campaign_id')
            
            # Process unsubscribe
            if campaign_id:
                # Unsubscribe from specific campaign
                preferences = await self.get_user_preferences(user_id)
                preferences.campaign_preferences[campaign_id] = False
                await self._save_user_preferences(preferences)
                
            elif category:
                # Unsubscribe from category
                await self.update_category_preferences(user_id, category, {'enabled': False})
                
            elif channel:
                # Unsubscribe from channel
                await self.update_channel_preferences(user_id, channel, {'enabled': False})
                
            else:
                # Global unsubscribe
                await self.update_global_preferences(user_id, {'enabled': False})
            
            # Record unsubscribe event
            await self._record_consent(user_id, "unsubscribe", False, "unsubscribe_link")
            
            # Delete token
            await self.redis.delete(f"unsubscribe_token:{token}")
            
            logger.info(f"Unsubscribe processed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process unsubscribe: {e}")
            return False
    
    async def get_preference_insights(self, user_id: str) -> Dict[str, Any]:
        """Get AI-powered preference insights for user."""
        try:
            # Get behavioral data
            behavioral_data = await self._get_user_behavioral_data(user_id)
            
            # Generate insights
            insights = await self.learning_engine.learn_from_behavior(user_id, behavioral_data)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get preference insights: {e}")
            return {}
    
    async def bulk_preference_update(self, updates: List[PreferenceUpdate]) -> Dict[str, bool]:
        """Process bulk preference updates."""
        try:
            results = {}
            
            for update in updates:
                try:
                    if update.scope == PreferenceScope.GLOBAL:
                        success = await self.update_global_preferences(
                            update.user_id, {update.property_name: update.property_value}
                        )
                    elif update.scope == PreferenceScope.CHANNEL:
                        channel = ChannelType(update.target_id)
                        success = await self.update_channel_preferences(
                            update.user_id, channel, {update.property_name: update.property_value}
                        )
                    elif update.scope == PreferenceScope.CATEGORY:
                        category = NotificationCategory(update.target_id)
                        success = await self.update_category_preferences(
                            update.user_id, category, {update.property_name: update.property_value}
                        )
                    else:
                        success = False
                    
                    results[f"{update.user_id}_{update.scope.value}_{update.target_id}"] = success
                    
                except Exception as e:
                    logger.error(f"Bulk update failed for {update.user_id}: {e}")
                    results[f"{update.user_id}_{update.scope.value}_{update.target_id}"] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Bulk preference update failed: {e}")
            return {}
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export user preference data for GDPR compliance."""
        try:
            preferences = await self.get_user_preferences(user_id)
            consent_history = await self._get_consent_history(user_id)
            notification_history = await self._get_notification_history(user_id)
            
            export_data = {
                'user_id': user_id,
                'preferences': self._serialize_preferences(preferences),
                'consent_history': consent_history,
                'notification_history': notification_history,
                'export_date': datetime.utcnow().isoformat()
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export user data: {e}")
            return {}
    
    async def delete_user_data(self, user_id: str) -> bool:
        """Delete user preference data for GDPR compliance."""
        try:
            # Delete preferences
            await self.redis.delete(f"user_preferences:{user_id}")
            
            # Delete consent history
            await self.redis.delete(f"consent_history:{user_id}")
            
            # Delete notification history
            await self.redis.delete(f"notification_history:{user_id}")
            
            # Delete frequency counters
            await self.redis.delete(f"frequency_counters:{user_id}")
            
            # Delete learning insights
            await self.redis.delete(f"preference_insights:{user_id}")
            
            # Clear cache
            if user_id in self.preference_cache:
                del self.preference_cache[user_id]
            
            logger.info(f"User data deleted for {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user data: {e}")
            return False
    
    async def _load_user_preferences(self, user_id: str) -> Optional[UserNotificationPreferences]:
        """Load user preferences from storage."""
        try:
            preferences_data = await self.redis.hgetall(f"user_preferences:{user_id}")
            if not preferences_data:
                return None
            
            return self._deserialize_preferences(preferences_data)
            
        except Exception as e:
            logger.error(f"Failed to load user preferences: {e}")
            return None
    
    async def _save_user_preferences(self, preferences: UserNotificationPreferences) -> None:
        """Save user preferences to storage."""
        try:
            preferences_data = self._serialize_preferences(preferences)
            await self.redis.hset(f"user_preferences:{preferences.user_id}", mapping=preferences_data)
            
        except Exception as e:
            logger.error(f"Failed to save user preferences: {e}")
            raise
    
    async def _create_default_preferences(self, user_id: str) -> UserNotificationPreferences:
        """Create default preferences for new user."""
        try:
            global_prefs = GlobalPreferences(user_id=user_id)
            
            preferences = UserNotificationPreferences(
                user_id=user_id,
                global_preferences=global_prefs
            )
            
            # Create default channel preferences
            for channel in ChannelType:
                preferences.channel_preferences[channel] = ChannelPreference(channel=channel)
            
            # Create default category preferences
            for category in NotificationCategory:
                preferences.category_preferences[category] = CategoryPreference(category=category)
            
            # Save preferences
            await self._save_user_preferences(preferences)
            
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to create default preferences: {e}")
            raise
    
    def _serialize_preferences(self, preferences: UserNotificationPreferences) -> Dict[str, str]:
        """Serialize preferences for storage."""
        try:
            data = {
                'user_id': preferences.user_id,
                'global_preferences': json.dumps({
                    'user_id': preferences.global_preferences.user_id,
                    'enabled': preferences.global_preferences.enabled,
                    'global_opt_in': preferences.global_preferences.global_opt_in.value,
                    'default_channels': [c.value for c in preferences.global_preferences.default_channels],
                    'timezone': preferences.global_preferences.timezone,
                    'language': preferences.global_preferences.language,
                    'quiet_hours': {
                        'enabled': preferences.global_preferences.quiet_hours.enabled,
                        'start_time': preferences.global_preferences.quiet_hours.start_time.strftime('%H:%M'),
                        'end_time': preferences.global_preferences.quiet_hours.end_time.strftime('%H:%M'),
                        'timezone': preferences.global_preferences.quiet_hours.timezone,
                        'days_of_week': preferences.global_preferences.quiet_hours.days_of_week
                    } if preferences.global_preferences.quiet_hours else None,
                    'marketing_consent': preferences.global_preferences.marketing_consent,
                    'marketing_consent_date': preferences.global_preferences.marketing_consent_date.isoformat() if preferences.global_preferences.marketing_consent_date else None,
                    'data_processing_consent': preferences.global_preferences.data_processing_consent,
                    'data_processing_consent_date': preferences.global_preferences.data_processing_consent_date.isoformat() if preferences.global_preferences.data_processing_consent_date else None,
                    'last_updated': preferences.global_preferences.last_updated.isoformat(),
                    'created_at': preferences.global_preferences.created_at.isoformat()
                }),
                'channel_preferences': json.dumps({
                    channel.value: {
                        'channel': channel_pref.channel.value,
                        'enabled': channel_pref.enabled,
                        'opt_in_status': channel_pref.opt_in_status.value,
                        'opt_in_date': channel_pref.opt_in_date.isoformat() if channel_pref.opt_in_date else None,
                        'opt_out_date': channel_pref.opt_out_date.isoformat() if channel_pref.opt_out_date else None,
                        'quiet_hours': {
                            'enabled': channel_pref.quiet_hours.enabled,
                            'start_time': channel_pref.quiet_hours.start_time.strftime('%H:%M'),
                            'end_time': channel_pref.quiet_hours.end_time.strftime('%H:%M'),
                            'timezone': channel_pref.quiet_hours.timezone,
                            'days_of_week': channel_pref.quiet_hours.days_of_week
                        } if channel_pref.quiet_hours else None,
                        'device_tokens': channel_pref.device_tokens,
                        'metadata': channel_pref.metadata
                    } for channel, channel_pref in preferences.channel_preferences.items()
                }),
                'category_preferences': json.dumps({
                    category.value: {
                        'category': category_pref.category.value,
                        'enabled': category_pref.enabled,
                        'opt_in_status': category_pref.opt_in_status.value,
                        'priority_threshold': category_pref.priority_threshold,
                        'frequency_limit': category_pref.frequency_limit.value,
                        'max_per_day': category_pref.max_per_day,
                        'channels': [c.value for c in category_pref.channels],
                        'keywords_include': category_pref.keywords_include,
                        'keywords_exclude': category_pref.keywords_exclude
                    } for category, category_pref in preferences.category_preferences.items()
                }),
                'template_preferences': json.dumps(preferences.template_preferences),
                'campaign_preferences': json.dumps(preferences.campaign_preferences),
                'suppression_list': json.dumps(list(preferences.suppression_list)),
                'last_updated': preferences.last_updated.isoformat()
            }
            
            return {k: str(v) for k, v in data.items()}
            
        except Exception as e:
            logger.error(f"Preference serialization failed: {e}")
            return {}
    
    def _deserialize_preferences(self, data: Dict[str, str]) -> UserNotificationPreferences:
        """Deserialize preferences from storage."""
        try:
            # Parse global preferences
            global_data = json.loads(data['global_preferences'])
            
            quiet_hours = None
            if global_data.get('quiet_hours'):
                qh_data = global_data['quiet_hours']
                quiet_hours = QuietHours(
                    enabled=qh_data['enabled'],
                    start_time=time.fromisoformat(qh_data['start_time']),
                    end_time=time.fromisoformat(qh_data['end_time']),
                    timezone=qh_data['timezone'],
                    days_of_week=qh_data['days_of_week']
                )
            
            global_prefs = GlobalPreferences(
                user_id=global_data['user_id'],
                enabled=global_data['enabled'],
                global_opt_in=OptInStatus(global_data['global_opt_in']),
                default_channels={ChannelType(c) for c in global_data['default_channels']},
                timezone=global_data['timezone'],
                language=global_data['language'],
                quiet_hours=quiet_hours,
                marketing_consent=global_data['marketing_consent'],
                marketing_consent_date=datetime.fromisoformat(global_data['marketing_consent_date']) if global_data.get('marketing_consent_date') else None,
                data_processing_consent=global_data['data_processing_consent'],
                data_processing_consent_date=datetime.fromisoformat(global_data['data_processing_consent_date']) if global_data.get('data_processing_consent_date') else None,
                last_updated=datetime.fromisoformat(global_data['last_updated']),
                created_at=datetime.fromisoformat(global_data['created_at'])
            )
            
            # Parse channel preferences
            channel_prefs = {}
            channel_data = json.loads(data.get('channel_preferences', '{}'))
            for channel_str, pref_data in channel_data.items():
                channel = ChannelType(channel_str)
                
                quiet_hours = None
                if pref_data.get('quiet_hours'):
                    qh_data = pref_data['quiet_hours']
                    quiet_hours = QuietHours(
                        enabled=qh_data['enabled'],
                        start_time=time.fromisoformat(qh_data['start_time']),
                        end_time=time.fromisoformat(qh_data['end_time']),
                        timezone=qh_data['timezone'],
                        days_of_week=qh_data['days_of_week']
                    )
                
                channel_prefs[channel] = ChannelPreference(
                    channel=ChannelType(pref_data['channel']),
                    enabled=pref_data['enabled'],
                    opt_in_status=OptInStatus(pref_data['opt_in_status']),
                    opt_in_date=datetime.fromisoformat(pref_data['opt_in_date']) if pref_data.get('opt_in_date') else None,
                    opt_out_date=datetime.fromisoformat(pref_data['opt_out_date']) if pref_data.get('opt_out_date') else None,
                    quiet_hours=quiet_hours,
                    device_tokens=pref_data['device_tokens'],
                    metadata=pref_data['metadata']
                )
            
            # Parse category preferences
            category_prefs = {}
            category_data = json.loads(data.get('category_preferences', '{}'))
            for category_str, pref_data in category_data.items():
                category = NotificationCategory(category_str)
                
                category_prefs[category] = CategoryPreference(
                    category=NotificationCategory(pref_data['category']),
                    enabled=pref_data['enabled'],
                    opt_in_status=OptInStatus(pref_data['opt_in_status']),
                    priority_threshold=pref_data['priority_threshold'],
                    frequency_limit=FrequencyLimit(pref_data['frequency_limit']),
                    max_per_day=pref_data['max_per_day'],
                    channels={ChannelType(c) for c in pref_data['channels']},
                    keywords_include=pref_data['keywords_include'],
                    keywords_exclude=pref_data['keywords_exclude']
                )
            
            return UserNotificationPreferences(
                user_id=data['user_id'],
                global_preferences=global_prefs,
                channel_preferences=channel_prefs,
                category_preferences=category_prefs,
                template_preferences=json.loads(data.get('template_preferences', '{}')),
                campaign_preferences=json.loads(data.get('campaign_preferences', '{}')),
                suppression_list=set(json.loads(data.get('suppression_list', '[]'))),
                last_updated=datetime.fromisoformat(data['last_updated'])
            )
            
        except Exception as e:
            logger.error(f"Preference deserialization failed: {e}")
            raise
    
    async def _record_consent(self, user_id: str, consent_type: str, status: bool, source: str) -> None:
        """Record consent change."""
        try:
            consent_record = ConsentRecord(
                user_id=user_id,
                consent_type=consent_type,
                status=status,
                timestamp=datetime.utcnow(),
                source=source
            )
            
            consent_data = {
                'user_id': consent_record.user_id,
                'consent_type': consent_record.consent_type,
                'status': str(consent_record.status),
                'timestamp': consent_record.timestamp.isoformat(),
                'source': consent_record.source,
                'ip_address': consent_record.ip_address or '',
                'user_agent': consent_record.user_agent or '',
                'legal_basis': consent_record.legal_basis or '',
                'metadata': json.dumps(consent_record.metadata)
            }
            
            await self.redis.lpush(f"consent_history:{user_id}", json.dumps(consent_data))
            
        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
    
    async def _check_frequency_limits(self, user_id: str, channel: ChannelType,
                                    category: NotificationCategory) -> Tuple[bool, str]:
        """Check frequency limits for user."""
        try:
            # Get current frequency counters
            counter_key = f"frequency_counters:{user_id}:{channel.value}:{category.value}"
            current_count = await self.redis.get(counter_key) or 0
            current_count = int(current_count)
            
            # Get user preferences
            preferences = await self.get_user_preferences(user_id)
            
            # Check category frequency limits
            if category in preferences.category_preferences:
                category_pref = preferences.category_preferences[category]
                
                if category_pref.frequency_limit != FrequencyLimit.UNLIMITED:
                    if current_count >= category_pref.max_per_day:
                        return False, f"Daily limit exceeded for {category.value}"
            
            return True, "Frequency limit check passed"
            
        except Exception as e:
            logger.error(f"Frequency limit check failed: {e}")
            return True, "Frequency limit check error - allowing"
    
    async def _update_frequency_counters(self, user_id: str, channel: ChannelType,
                                       category: NotificationCategory) -> None:
        """Update frequency counters."""
        try:
            counter_key = f"frequency_counters:{user_id}:{channel.value}:{category.value}"
            
            # Increment counter
            await self.redis.incr(counter_key)
            
            # Set expiration to reset at midnight
            now = datetime.utcnow()
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            seconds_until_midnight = int((midnight - now).total_seconds())
            
            await self.redis.expire(counter_key, seconds_until_midnight)
            
        except Exception as e:
            logger.error(f"Failed to update frequency counters: {e}")
    
    async def _check_compliance_requirements(self, user_id: str, channel: ChannelType,
                                          category: NotificationCategory,
                                          preferences: UserNotificationPreferences) -> Tuple[bool, str]:
        """Check compliance requirements (GDPR, CCPA, etc.)."""
        try:
            # Check marketing consent for marketing messages
            if category == NotificationCategory.MARKETING:
                if self.require_explicit_consent and not preferences.global_preferences.marketing_consent:
                    return False, "Marketing consent required"
            
            # Check data processing consent
            if self.gdpr_enabled and not preferences.global_preferences.data_processing_consent:
                if category in [NotificationCategory.MARKETING, NotificationCategory.PRODUCT_UPDATES]:
                    return False, "Data processing consent required"
            
            # Check explicit opt-in for channels if required
            if channel in preferences.channel_preferences:
                channel_pref = preferences.channel_preferences[channel]
                if self.require_explicit_consent and channel_pref.opt_in_status == OptInStatus.UNKNOWN:
                    return False, f"Explicit opt-in required for {channel.value}"
            
            return True, "Compliance check passed"
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return True, "Compliance check error - allowing"
    
    async def _get_user_behavioral_data(self, user_id: str) -> Dict[str, Any]:
        """Get user behavioral data for learning."""
        try:
            # This would integrate with analytics system
            # For now, return placeholder data
            return {
                'channel_engagement': {
                    'email': {'open_rate': 0.45, 'click_rate': 0.08},
                    'push': {'open_rate': 0.32, 'click_rate': 0.05},
                    'sms': {'open_rate': 0.78, 'click_rate': 0.12}
                },
                'category_engagement': {
                    'marketing': {'engagement_score': 0.3},
                    'product_updates': {'engagement_score': 0.7},
                    'social': {'engagement_score': 0.2}
                },
                'time_patterns': {
                    'inactive_hours': [22, 23, 0, 1, 2, 3, 4, 5, 6, 7]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get behavioral data: {e}")
            return {}
    
    async def _get_consent_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get consent history for user."""
        try:
            consent_records = await self.redis.lrange(f"consent_history:{user_id}", 0, -1)
            return [json.loads(record) for record in consent_records]
        except Exception as e:
            logger.error(f"Failed to get consent history: {e}")
            return []
    
    async def _get_notification_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get notification history for user."""
        try:
            notification_records = await self.redis.lrange(f"notification_history:{user_id}", 0, 99)
            return [json.loads(record) for record in notification_records]
        except Exception as e:
            logger.error(f"Failed to get notification history: {e}")
            return []


# Factory function for creating service instance
def create_preference_manager(config: Dict[str, Any]) -> NotificationPreferenceManager:
    """Create and configure notification preference manager."""
    return NotificationPreferenceManager(config)


# Export main classes and functions
__all__ = [
    'NotificationPreferenceManager',
    'UserNotificationPreferences',
    'GlobalPreferences',
    'ChannelPreference',
    'CategoryPreference',
    'QuietHours',
    'FrequencySettings',
    'PreferenceUpdate',
    'ConsentRecord',
    'ChannelType',
    'NotificationCategory',
    'FrequencyLimit',
    'PreferenceScope',
    'OptInStatus',
    'PreferenceLearningEngine',
    'create_preference_manager'
]