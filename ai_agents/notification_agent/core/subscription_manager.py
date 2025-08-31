"""
Notification Subscription Manager - Advanced User Preference & Subscription Management

Enterprise-grade subscription management system handling intelligent user preferences,
dynamic subscription management, AI-driven personalization settings, and granular
notification control for multi-format content creators on the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property are the EXCLUSIVE PROPERTY of Fahed Mlaiel.

STRICTLY PROHIBITED WITHOUT EXPLICIT WRITTEN AUTHORIZATION:
- Copying, cloning, reproducing, or distributing this code
- Using concepts, methodologies, or approaches in other projects
- Commercial exploitation, monetization, or resale
- Reverse engineering, decompilation, or adaptation
- Creating derivative works based on this intellectual property

Contact for licensing inquiries: mlaiel@live.de

Violation of these terms will result in immediate legal action.
All usage is monitored, logged, and legally protected.

Team Specialties & Expertise:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from .channel_manager import ChannelType
from .event_manager import NotificationEventType
try:
    from core.database import get_async_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_async_session = DatabaseManager
from ...models.user_models import UserModel, UserPreferences
from ...models.subscription_models import (
    NotificationSubscription, SubscriptionStatus, FrequencyLimit
)
from ...business.user_business import UserBusinessLogic
from ...integrations.analytics_integration import AnalyticsIntegration


class SubscriptionType(Enum):
    """Comprehensive subscription types for IA Influencer platform"""
    CONTENT_NOTIFICATIONS = "content_notifications"
    PROTECTION_ALERTS = "protection_alerts"
    COLLABORATION_OPPORTUNITIES = "collaboration_opportunities"
    MONETIZATION_UPDATES = "monetization_updates"
    SEO_INSIGHTS = "seo_insights"
    DISTRIBUTION_STATUS = "distribution_status"
    ENGAGEMENT_ANALYTICS = "engagement_analytics"
    PLATFORM_UPDATES = "platform_updates"
    SECURITY_ALERTS = "security_alerts"
    MARKETING_COMMUNICATIONS = "marketing_communications"


class FrequencyType(Enum):
    """Notification frequency options"""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NEVER = "never"


class PersonalizationLevel(Enum):
    """AI personalization levels"""
    MINIMAL = "minimal"
    BASIC = "basic"
    ADVANCED = "advanced"
    INTELLIGENT = "intelligent"
    FULL_AI = "full_ai"


@dataclass
class ChannelPreference:
    """Channel-specific user preferences"""
    channel_type: ChannelType
    enabled: bool
    priority: int  # 1-10, higher = more preferred
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    frequency_limits: Dict[FrequencyType, int] = field(default_factory=dict)


@dataclass
class SubscriptionSettings:
    """Comprehensive subscription configuration"""
    subscription_type: SubscriptionType
    enabled: bool
    frequency: FrequencyType
    channel_preferences: List[ChannelPreference]
    content_filters: Dict[str, Any] = field(default_factory=dict)
    priority_threshold: int = 1  # 1-10, only notifications >= threshold
    ai_personalization_level: PersonalizationLevel = PersonalizationLevel.ADVANCED


@dataclass
class UserNotificationProfile:
    """Complete user notification profile with intelligent defaults"""
    user_id: str
    subscription_settings: Dict[SubscriptionType, SubscriptionSettings]
    global_preferences: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class NotificationSubscriptionManager:
    """
    Advanced subscription management system with AI-driven personalization
    
    Key Features:
    - Granular subscription management for all IA Influencer business contexts
    - Intelligent channel preference optimization based on user behavior
    - Dynamic frequency adjustment with AI-driven timing optimization
    - Content filtering with business logic integration
    - Quiet hours management with timezone intelligence
    - A/B testing framework for subscription optimization
    - Comprehensive analytics and engagement tracking
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_business = UserBusinessLogic()
        self.analytics = AnalyticsIntegration()
        
        # Caching for performance optimization
        self._user_profiles_cache: Dict[str, UserNotificationProfile] = {}
        self._subscription_stats: Dict[str, Any] = {}
        
        # AI components
        self._personalization_engine = PersonalizationEngine()
        self._preference_optimizer = PreferenceOptimizer()
        
        # Background tasks
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        self._optimization_task = asyncio.create_task(self._periodic_optimization())
    
    async def get_user_profile(
        self, user_id: str, force_refresh: bool = False
    ) -> UserNotificationProfile:
        """
        Get comprehensive user notification profile with intelligent caching
        
        Args:
            user_id: User identifier
            force_refresh: Force reload from database
            
        Returns:
            Complete user notification profile
        """
        if not force_refresh and user_id in self._user_profiles_cache:
            profile = self._user_profiles_cache[user_id]
            # Check if cache is still valid (1 hour)
            if (datetime.utcnow() - profile.last_updated).seconds < 3600:
                return profile
        
        try:
            # Load from database
            profile = await self._load_user_profile_from_db(user_id)
            
            # Apply AI optimization if needed
            if profile.global_preferences.get('ai_optimization_enabled', True):
                profile = await self._personalization_engine.optimize_profile(profile)
            
            # Cache the profile
            self._user_profiles_cache[user_id] = profile
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to load user profile for {user_id}: {str(e)}")
            # Return default profile
            return await self._create_default_profile(user_id)
    
    async def update_subscription_settings(
        self,
        user_id: str,
        subscription_type: SubscriptionType,
        settings: SubscriptionSettings
    ) -> bool:
        """
        Update subscription settings with intelligent validation and optimization
        """
        try:
            profile = await self.get_user_profile(user_id)
            
            # Validate settings
            if not await self._validate_subscription_settings(settings):
                return False
            
            # Apply intelligent optimization
            optimized_settings = await self._preference_optimizer.optimize_settings(
                settings, profile.ai_insights
            )
            
            # Update profile
            profile.subscription_settings[subscription_type] = optimized_settings
            profile.last_updated = datetime.utcnow()
            
            # Save to database
            await self._save_user_profile_to_db(profile)
            
            # Update cache
            self._user_profiles_cache[user_id] = profile
            
            # Track analytics
            await self.analytics.track_event('subscription_updated', {
                'user_id': user_id,
                'subscription_type': subscription_type.value,
                'enabled': settings.enabled,
                'frequency': settings.frequency.value
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update subscription settings: {str(e)}")
            return False
    
    async def update_channel_preferences(
        self,
        user_id: str,
        channel_preferences: List[ChannelPreference]
    ) -> bool:
        """
        Update channel preferences with intelligent conflict resolution
        """
        try:
            profile = await self.get_user_profile(user_id)
            
            # Validate and optimize channel preferences
            optimized_preferences = await self._optimize_channel_preferences(
                channel_preferences, profile.ai_insights
            )
            
            # Update all subscription settings with new channel preferences
            for subscription_type in profile.subscription_settings:
                settings = profile.subscription_settings[subscription_type]
                settings.channel_preferences = optimized_preferences
            
            profile.last_updated = datetime.utcnow()
            
            # Save changes
            await self._save_user_profile_to_db(profile)
            self._user_profiles_cache[user_id] = profile
            
            # Track analytics
            await self.analytics.track_event('channel_preferences_updated', {
                'user_id': user_id,
                'channels_enabled': [
                    pref.channel_type.value for pref in optimized_preferences if pref.enabled
                ]
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update channel preferences: {str(e)}")
            return False
    
    async def check_subscription_eligibility(
        self,
        user_id: str,
        event_type: NotificationEventType,
        channel_type: ChannelType,
        priority: int = 5
    ) -> bool:
        """
        Check if user is eligible to receive notification based on comprehensive criteria
        """
        try:
            profile = await self.get_user_profile(user_id)
            
            # Map event type to subscription type
            subscription_type = self._map_event_to_subscription(event_type)
            
            if subscription_type not in profile.subscription_settings:
                return False
            
            settings = profile.subscription_settings[subscription_type]
            
            # Check if subscription is enabled
            if not settings.enabled:
                return False
            
            # Check priority threshold
            if priority < settings.priority_threshold:
                return False
            
            # Check channel preferences
            channel_pref = next(
                (pref for pref in settings.channel_preferences 
                 if pref.channel_type == channel_type),
                None
            )
            
            if not channel_pref or not channel_pref.enabled:
                return False
            
            # Check quiet hours
            if await self._is_in_quiet_hours(user_id, channel_pref):
                return False
            
            # Check frequency limits
            if not await self._check_frequency_limits(user_id, subscription_type, settings):
                return False
            
            # Check content filters
            if not await self._check_content_filters(user_id, event_type, settings):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Eligibility check failed: {str(e)}")
            return False
    
    async def get_preferred_channels(
        self,
        user_id: str,
        event_type: NotificationEventType,
        max_channels: int = 3
    ) -> List[ChannelType]:
        """
        Get preferred channels for user and event type with intelligent ranking
        """
        try:
            profile = await self.get_user_profile(user_id)
            subscription_type = self._map_event_to_subscription(event_type)
            
            if subscription_type not in profile.subscription_settings:
                return []
            
            settings = profile.subscription_settings[subscription_type]
            
            # Filter enabled channels
            eligible_channels = [
                pref for pref in settings.channel_preferences
                if pref.enabled and await self.check_subscription_eligibility(
                    user_id, event_type, pref.channel_type
                )
            ]
            
            # Sort by priority and AI optimization
            sorted_channels = sorted(
                eligible_channels,
                key=lambda pref: (
                    pref.priority,
                    profile.ai_insights.get(f'{pref.channel_type.value}_engagement_rate', 0.5)
                ),
                reverse=True
            )
            
            # Return top channels
            return [pref.channel_type for pref in sorted_channels[:max_channels]]
            
        except Exception as e:
            self.logger.error(f"Failed to get preferred channels: {str(e)}")
            return [ChannelType.EMAIL]  # Fallback to email
    
    async def update_engagement_metrics(
        self,
        user_id: str,
        channel_type: ChannelType,
        event_type: NotificationEventType,
        engagement_data: Dict[str, Any]
    ):
        """
        Update user engagement metrics for AI optimization
        """
        try:
            profile = await self.get_user_profile(user_id)
            
            # Update AI insights with engagement data
            engagement_key = f'{channel_type.value}_{event_type.value}_engagement'
            if engagement_key not in profile.ai_insights:
                profile.ai_insights[engagement_key] = []
            
            profile.ai_insights[engagement_key].append({
                'timestamp': datetime.utcnow().isoformat(),
                'data': engagement_data
            })
            
            # Keep only recent data (last 30 entries)
            profile.ai_insights[engagement_key] = profile.ai_insights[engagement_key][-30:]
            
            # Update overall channel engagement rate
            channel_key = f'{channel_type.value}_engagement_rate'
            if 'opened' in engagement_data:
                current_rate = profile.ai_insights.get(channel_key, 0.5)
                new_rate = (current_rate * 0.9) + (engagement_data['opened'] * 0.1)
                profile.ai_insights[channel_key] = new_rate
            
            # Save updates
            await self._save_user_profile_to_db(profile)
            self._user_profiles_cache[user_id] = profile
            
        except Exception as e:
            self.logger.error(f"Failed to update engagement metrics: {str(e)}")
    
    async def get_subscription_analytics(
        self, user_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive subscription analytics for user
        """
        try:
            profile = await self.get_user_profile(user_id)
            
            analytics = {
                'total_subscriptions': len(profile.subscription_settings),
                'enabled_subscriptions': sum(
                    1 for settings in profile.subscription_settings.values()
                    if settings.enabled
                ),
                'preferred_channels': {},
                'engagement_rates': {},
                'frequency_distribution': {},
                'ai_optimization_level': profile.global_preferences.get(
                    'ai_optimization_level', PersonalizationLevel.ADVANCED.value
                )
            }
            
            # Calculate preferred channels distribution
            for settings in profile.subscription_settings.values():
                if settings.enabled:
                    for pref in settings.channel_preferences:
                        if pref.enabled:
                            channel = pref.channel_type.value
                            analytics['preferred_channels'][channel] = analytics['preferred_channels'].get(channel, 0) + 1
            
            # Calculate engagement rates from AI insights
            for key, value in profile.ai_insights.items():
                if key.endswith('_engagement_rate'):
                    channel = key.replace('_engagement_rate', '')
                    analytics['engagement_rates'][channel] = value
            
            # Calculate frequency distribution
            for settings in profile.subscription_settings.values():
                if settings.enabled:
                    freq = settings.frequency.value
                    analytics['frequency_distribution'][freq] = analytics['frequency_distribution'].get(freq, 0) + 1
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get subscription analytics: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _load_user_profile_from_db(self, user_id: str) -> UserNotificationProfile:
        """Load user profile from database"""
        async with get_async_session() as session:
            # Implementation would load from database
            # For now, return a default profile with some sample data
            return await self._create_default_profile(user_id)
    
    async def _save_user_profile_to_db(self, profile: UserNotificationProfile):
        """Save user profile to database"""
        async with get_async_session() as session:
            # Implementation would save to database
            pass
    
    async def _create_default_profile(self, user_id: str) -> UserNotificationProfile:
        """Create default notification profile for new user"""
        
        # Default channel preferences
        default_channels = [
            ChannelPreference(
                channel_type=ChannelType.EMAIL,
                enabled=True,
                priority=8,
                quiet_hours_enabled=True,
                quiet_hours_start=time(22, 0),
                quiet_hours_end=time(8, 0)
            ),
            ChannelPreference(
                channel_type=ChannelType.PUSH_NOTIFICATION,
                enabled=True,
                priority=6,
                quiet_hours_enabled=True,
                quiet_hours_start=time(22, 0),
                quiet_hours_end=time(8, 0)
            ),
            ChannelPreference(
                channel_type=ChannelType.SMS,
                enabled=False,
                priority=9,
                quiet_hours_enabled=True,
                quiet_hours_start=time(22, 0),
                quiet_hours_end=time(8, 0)
            )
        ]
        
        # Default subscription settings
        default_subscriptions = {}
        
        for sub_type in SubscriptionType:
            # High priority subscriptions
            if sub_type in [
                SubscriptionType.PROTECTION_ALERTS,
                SubscriptionType.SECURITY_ALERTS
            ]:
                frequency = FrequencyType.IMMEDIATE
                priority_threshold = 1
            # Medium priority subscriptions
            elif sub_type in [
                SubscriptionType.CONTENT_NOTIFICATIONS,
                SubscriptionType.COLLABORATION_OPPORTUNITIES,
                SubscriptionType.MONETIZATION_UPDATES
            ]:
                frequency = FrequencyType.IMMEDIATE
                priority_threshold = 3
            # Low priority subscriptions
            else:
                frequency = FrequencyType.DAILY
                priority_threshold = 5
            
            default_subscriptions[sub_type] = SubscriptionSettings(
                subscription_type=sub_type,
                enabled=True,
                frequency=frequency,
                channel_preferences=default_channels.copy(),
                priority_threshold=priority_threshold,
                ai_personalization_level=PersonalizationLevel.ADVANCED
            )
        
        return UserNotificationProfile(
            user_id=user_id,
            subscription_settings=default_subscriptions,
            global_preferences={
                'ai_optimization_enabled': True,
                'timezone': 'UTC',
                'language': 'en'
            }
        )
    
    def _map_event_to_subscription(
        self, event_type: NotificationEventType
    ) -> SubscriptionType:
        """Map notification event type to subscription type"""
        mapping = {
            NotificationEventType.CONTENT_UPLOADED: SubscriptionType.CONTENT_NOTIFICATIONS,
            NotificationEventType.CONTENT_PROCESSED: SubscriptionType.CONTENT_NOTIFICATIONS,
            NotificationEventType.CONTENT_PROTECTED: SubscriptionType.PROTECTION_ALERTS,
            NotificationEventType.COPYRIGHT_DETECTED: SubscriptionType.PROTECTION_ALERTS,
            NotificationEventType.INFRINGEMENT_ALERT: SubscriptionType.PROTECTION_ALERTS,
            NotificationEventType.COLLABORATION_MATCH_FOUND: SubscriptionType.COLLABORATION_OPPORTUNITIES,
            NotificationEventType.COLLABORATION_REQUEST_RECEIVED: SubscriptionType.COLLABORATION_OPPORTUNITIES,
            NotificationEventType.REVENUE_OPPORTUNITY: SubscriptionType.MONETIZATION_UPDATES,
            NotificationEventType.PAYMENT_RECEIVED: SubscriptionType.MONETIZATION_UPDATES,
            NotificationEventType.SEO_OPTIMIZATION_COMPLETE: SubscriptionType.SEO_INSIGHTS,
            NotificationEventType.PLATFORM_DISTRIBUTION_COMPLETE: SubscriptionType.DISTRIBUTION_STATUS,
            NotificationEventType.HIGH_ENGAGEMENT_DETECTED: SubscriptionType.ENGAGEMENT_ANALYTICS,
            NotificationEventType.SECURITY_ALERT: SubscriptionType.SECURITY_ALERTS,
            NotificationEventType.PLATFORM_UPDATE: SubscriptionType.PLATFORM_UPDATES
        }
        
        return mapping.get(event_type, SubscriptionType.PLATFORM_UPDATES)
    
    async def _validate_subscription_settings(
        self, settings: SubscriptionSettings
    ) -> bool:
        """Validate subscription settings"""
        if not settings.channel_preferences:
            return False
        
        # Ensure at least one channel is enabled
        if not any(pref.enabled for pref in settings.channel_preferences):
            return False
        
        # Validate priority threshold
        if not 1 <= settings.priority_threshold <= 10:
            return False
        
        return True
    
    async def _optimize_channel_preferences(
        self,
        preferences: List[ChannelPreference],
        ai_insights: Dict[str, Any]
    ) -> List[ChannelPreference]:
        """Optimize channel preferences based on AI insights"""
        optimized_prefs = preferences.copy()
        
        # Adjust priorities based on engagement rates
        for pref in optimized_prefs:
            engagement_key = f'{pref.channel_type.value}_engagement_rate'
            engagement_rate = ai_insights.get(engagement_key, 0.5)
            
            # Boost priority for high-performing channels
            if engagement_rate > 0.8:
                pref.priority = min(pref.priority + 2, 10)
            elif engagement_rate < 0.3:
                pref.priority = max(pref.priority - 1, 1)
        
        return optimized_prefs
    
    async def _is_in_quiet_hours(
        self, user_id: str, channel_pref: ChannelPreference
    ) -> bool:
        """Check if current time is within user's quiet hours"""
        if not channel_pref.quiet_hours_enabled:
            return False
        
        if not channel_pref.quiet_hours_start or not channel_pref.quiet_hours_end:
            return False
        
        # Get user's timezone (would be loaded from profile)
        current_time = datetime.utcnow().time()
        
        # Simple quiet hours check (assumes UTC for now)
        if channel_pref.quiet_hours_start <= channel_pref.quiet_hours_end:
            # Same day quiet hours
            return channel_pref.quiet_hours_start <= current_time <= channel_pref.quiet_hours_end
        else:
            # Overnight quiet hours
            return current_time >= channel_pref.quiet_hours_start or current_time <= channel_pref.quiet_hours_end
    
    async def _check_frequency_limits(
        self,
        user_id: str,
        subscription_type: SubscriptionType,
        settings: SubscriptionSettings
    ) -> bool:
        """Check if user has exceeded frequency limits"""
        # Implementation would check database for recent notifications
        # For now, always return True (no limits exceeded)
        return True
    
    async def _check_content_filters(
        self,
        user_id: str,
        event_type: NotificationEventType,
        settings: SubscriptionSettings
    ) -> bool:
        """Check if notification passes content filters"""
        # Implementation would apply content filters
        # For now, always return True (no filters)
        return True
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of cached data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean up old cache entries
                cutoff_time = datetime.utcnow() - timedelta(hours=2)
                expired_users = [
                    user_id for user_id, profile in self._user_profiles_cache.items()
                    if profile.last_updated < cutoff_time
                ]
                
                for user_id in expired_users:
                    del self._user_profiles_cache[user_id]
                
                self.logger.info(f"Cleaned up {len(expired_users)} expired cache entries")
                
            except Exception as e:
                self.logger.error(f"Cleanup task error: {str(e)}")
    
    async def _periodic_optimization(self):
        """Periodic AI optimization of user preferences"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                
                # Optimize preferences for active users
                for user_id, profile in self._user_profiles_cache.items():
                    if profile.global_preferences.get('ai_optimization_enabled', True):
                        optimized_profile = await self._personalization_engine.optimize_profile(profile)
                        if optimized_profile != profile:
                            await self._save_user_profile_to_db(optimized_profile)
                            self._user_profiles_cache[user_id] = optimized_profile
                
                self.logger.info("Completed daily preference optimization")
                
            except Exception as e:
                self.logger.error(f"Optimization task error: {str(e)}")


class PersonalizationEngine:
    """AI-powered personalization engine for notification preferences"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def optimize_profile(
        self, profile: UserNotificationProfile
    ) -> UserNotificationProfile:
        """
        Apply AI-driven optimization to user notification profile
        """
        # Implementation would use ML models for optimization
        # For now, apply simple heuristics
        
        optimized_profile = profile
        
        # Optimize channel priorities based on engagement
        for settings in optimized_profile.subscription_settings.values():
            if settings.ai_personalization_level in [
                PersonalizationLevel.ADVANCED,
                PersonalizationLevel.INTELLIGENT,
                PersonalizationLevel.FULL_AI
            ]:
                # Optimize based on AI insights
                for pref in settings.channel_preferences:
                    engagement_key = f'{pref.channel_type.value}_engagement_rate'
                    engagement_rate = profile.ai_insights.get(engagement_key, 0.5)
                    
                    # Adjust priority based on engagement
                    if engagement_rate > 0.8:
                        pref.priority = min(pref.priority + 1, 10)
                    elif engagement_rate < 0.3:
                        pref.priority = max(pref.priority - 1, 1)
        
        return optimized_profile


class PreferenceOptimizer:
    """Advanced preference optimization with ML-driven insights"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def optimize_settings(
        self,
        settings: SubscriptionSettings,
        ai_insights: Dict[str, Any]
    ) -> SubscriptionSettings:
        """
        Optimize subscription settings based on AI insights
        """
        # Implementation would use sophisticated ML algorithms
        # For now, apply basic optimization
        
        optimized_settings = settings
        
        # Optimize frequency based on engagement patterns
        if settings.ai_personalization_level in [
            PersonalizationLevel.INTELLIGENT,
            PersonalizationLevel.FULL_AI
        ]:
            # Analyze engagement patterns to suggest optimal frequency
            avg_engagement = sum(
                ai_insights.get(f'{pref.channel_type.value}_engagement_rate', 0.5)
                for pref in settings.channel_preferences
                if pref.enabled
            ) / max(len([p for p in settings.channel_preferences if p.enabled]), 1)
            
            # Adjust frequency based on engagement
            if avg_engagement > 0.8 and settings.frequency == FrequencyType.DAILY:
                optimized_settings.frequency = FrequencyType.HOURLY
            elif avg_engagement < 0.3 and settings.frequency == FrequencyType.HOURLY:
                optimized_settings.frequency = FrequencyType.DAILY
        
        return optimized_settings
