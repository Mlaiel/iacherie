"""Mobile Configuration Management
Platform-specific configs, feature flags, and environment management

Author: Fahed Mlaiel <mlaiel@live.de>
Business Logic: Flexible mobile platform configuration for multi-environment deployment
"""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid

# Internal imports
try:
    from core.config import get_settings
    from core.logging import get_logger
except ImportError:
    # Fallback for standalone operation
    def get_logger(name: str):
        return logging.getLogger(name)
    
    def get_settings():
        return {"environment": "development"}


class Environment(Enum):
    """Environment types."""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Platform(Enum):
    """Mobile platform types."""    ANDROID = "android"
    IOS = "ios"
    REACT_NATIVE = "react_native"


@dataclass
class FeatureFlag:
    """Feature flag configuration."""    flag_id: str
    name: str
    description: str
    enabled: bool
    rollout_percentage: float = 100.0
    target_platforms: List[Platform] = field(default_factory=lambda: list(Platform))
    target_environments: List[Environment] = field(default_factory=lambda: list(Environment))
    user_segments: List[str] = field(default_factory=list)
    expiry_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_enabled_for_user(
        self,
        user_id: str,
        platform: Platform,
        environment: Environment
    ) -> bool:
        """Check if feature is enabled for specific user/platform/environment."""        
        # Check if expired
        if self.expiry_date and datetime.utcnow() > self.expiry_date:
            return False
        
        # Check platform
        if self.target_platforms and platform not in self.target_platforms:
            return False
        
        # Check environment
        if self.target_environments and environment not in self.target_environments:
            return False
        
        # Check if globally enabled
        if not self.enabled:
            return False
        
        # Check rollout percentage
        if self.rollout_percentage < 100.0:
            # Simple hash-based rollout
            user_hash = hash(f"{user_id}:{self.flag_id}") % 100
            if user_hash >= self.rollout_percentage:
                return False
        
        return True


@dataclass
class PlatformSettings:
    """Platform-specific settings."""    platform: Platform
    app_version: str
    min_supported_version: str
    api_endpoints: Dict[str, str]
    upload_limits: Dict[str, Any]
    security_settings: Dict[str, Any]
    ui_settings: Dict[str, Any]
    performance_settings: Dict[str, Any]
    push_notification_config: Dict[str, Any]
    analytics_config: Dict[str, Any]
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MobileAppConfig:
    """Complete mobile application configuration."""    config_id: str
    environment: Environment
    app_name: str
    app_version: str
    api_base_url: str
    cdn_base_url: str
    features: Dict[str, Any]
    platform_settings: Dict[Platform, PlatformSettings]
    security_config: Dict[str, Any]
    analytics_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class MobileConfig:
    """Professional mobile configuration management system."""    
    def __init__(self):
        self.logger = get_logger("mobile.config")
        self.settings = get_settings()
        self.current_environment = Environment(
            self.settings.get("environment", "development")
        )
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self.platform_settings: Dict[Platform, PlatformSettings] = {}
        self.app_configs: Dict[str, MobileAppConfig] = {}
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default mobile configurations."""        
        # Default feature flags
        self._create_default_feature_flags()
        
        # Default platform settings
        self._create_default_platform_settings()
        
        # Default app config
        self._create_default_app_config()
    
    def _create_default_feature_flags(self):
        """Create default feature flags."""        
        default_flags = [
            {
                "name": "offline_sync",
                "description": "Enable offline synchronization functionality",
                "enabled": True,
                "rollout_percentage": 100.0
            },
            {
                "name": "biometric_auth",
                "description": "Enable biometric authentication",
                "enabled": True,
                "rollout_percentage": 100.0,
                "target_platforms": [Platform.ANDROID, Platform.IOS]
            },
            {
                "name": "collaboration_features",
                "description": "Enable collaboration features",
                "enabled": True,
                "rollout_percentage": 80.0
            },
            {
                "name": "ai_content_analysis",
                "description": "Enable AI-powered content analysis",
                "enabled": True,
                "rollout_percentage": 100.0
            },
            {
                "name": "push_notifications",
                "description": "Enable push notifications",
                "enabled": True,
                "rollout_percentage": 100.0
            },
            {
                "name": "advanced_analytics",
                "description": "Enable advanced analytics tracking",
                "enabled": self.current_environment != Environment.DEVELOPMENT,
                "rollout_percentage": 100.0
            },
            {
                "name": "premium_features",
                "description": "Enable premium subscription features",
                "enabled": True,
                "rollout_percentage": 50.0
            }
        ]
        
        for flag_data in default_flags:
            flag_id = str(uuid.uuid4())
            
            feature_flag = FeatureFlag(
                flag_id=flag_id,
                name=flag_data["name"],
                description=flag_data["description"],
                enabled=flag_data["enabled"],
                rollout_percentage=flag_data["rollout_percentage"],
                target_platforms=flag_data.get("target_platforms", list(Platform)),
                target_environments=flag_data.get("target_environments", list(Environment))
            )
            
            self.feature_flags[flag_data["name"]] = feature_flag
    
    def _create_default_platform_settings(self):
        """Create default platform-specific settings."""        
        # Android settings
        android_settings = PlatformSettings(
            platform=Platform.ANDROID,
            app_version="1.0.0",
            min_supported_version="7.0",
            api_endpoints={
                "base": "https://api.ainflue.com/mobile/v1",
                "upload": "https://upload.ainflue.com/mobile",
                "analytics": "https://analytics.ainflue.com/mobile"
            },
            upload_limits={
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "max_concurrent_uploads": 3,
                "supported_formats": ["mp3", "mp4", "jpg", "png", "wav"]
            },
            security_settings={
                "certificate_pinning": True,
                "root_detection": True,
                "app_integrity_check": True,
                "encrypted_storage": True
            },
            ui_settings={
                "theme": "adaptive",
                "animation_duration": 300,
                "gesture_navigation": True,
                "haptic_feedback": True
            },
            performance_settings={
                "image_cache_size": 50 * 1024 * 1024,  # 50MB
                "network_timeout": 30,
                "background_sync_interval": 300  # 5 minutes
            },
            push_notification_config={
                "fcm_enabled": True,
                "notification_channels": ["uploads", "collaborations", "revenue"]
            },
            analytics_config={
                "session_timeout": 1800,  # 30 minutes
                "event_batch_size": 50,
                "offline_events_limit": 1000
            }
        )
        
        # iOS settings
        ios_settings = PlatformSettings(
            platform=Platform.IOS,
            app_version="1.0.0",
            min_supported_version="13.0",
            api_endpoints={
                "base": "https://api.ainflue.com/mobile/v1",
                "upload": "https://upload.ainflue.com/mobile",
                "analytics": "https://analytics.ainflue.com/mobile"
            },
            upload_limits={
                "max_file_size": 80 * 1024 * 1024,  # 80MB (iOS limit consideration)
                "max_concurrent_uploads": 2,
                "supported_formats": ["mp3", "mp4", "jpg", "png", "m4a", "heic"]
            },
            security_settings={
                "certificate_pinning": True,
                "jailbreak_detection": True,
                "app_integrity_check": True,
                "keychain_storage": True
            },
            ui_settings={
                "theme": "system",
                "animation_duration": 250,
                "gesture_navigation": True,
                "haptic_feedback": True,
                "dark_mode_support": True
            },
            performance_settings={
                "image_cache_size": 40 * 1024 * 1024,  # 40MB
                "network_timeout": 30,
                "background_sync_interval": 600  # 10 minutes (iOS background limits)
            },
            push_notification_config={
                "apns_enabled": True,
                "notification_categories": ["uploads", "collaborations", "revenue"],
                "silent_push": True
            },
            analytics_config={
                "session_timeout": 1800,  # 30 minutes
                "event_batch_size": 30,
                "offline_events_limit": 500
            }
        )
        
        # React Native settings
        react_native_settings = PlatformSettings(
            platform=Platform.REACT_NATIVE,
            app_version="1.0.0",
            min_supported_version="0.68.0",
            api_endpoints={
                "base": "https://api.ainflue.com/mobile/v1",
                "upload": "https://upload.ainflue.com/mobile",
                "analytics": "https://analytics.ainflue.com/mobile"
            },
            upload_limits={
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "max_concurrent_uploads": 3,
                "supported_formats": ["mp3", "mp4", "jpg", "png", "wav", "m4a"]
            },
            security_settings={
                "certificate_pinning": False,  # More complex in RN
                "root_detection": False,
                "app_integrity_check": False,
                "encrypted_storage": True
            },
            ui_settings={
                "theme": "adaptive",
                "animation_duration": 300,
                "gesture_navigation": True,
                "haptic_feedback": False  # Platform-dependent
            },
            performance_settings={
                "image_cache_size": 45 * 1024 * 1024,  # 45MB
                "network_timeout": 30,
                "background_sync_interval": 300  # 5 minutes
            },
            push_notification_config={
                "cross_platform_enabled": True,
                "notification_channels": ["uploads", "collaborations", "revenue"]
            },
            analytics_config={
                "session_timeout": 1800,  # 30 minutes
                "event_batch_size": 40,
                "offline_events_limit": 750
            }
        )
        
        self.platform_settings[Platform.ANDROID] = android_settings
        self.platform_settings[Platform.IOS] = ios_settings
        self.platform_settings[Platform.REACT_NATIVE] = react_native_settings
    
    def _create_default_app_config(self):
        """Create default application configuration."""        
        config_id = str(uuid.uuid4())
        
        # Environment-specific URLs
        url_config = {
            Environment.DEVELOPMENT: {
                "api_base_url": "https://dev-api.ainflue.com",
                "cdn_base_url": "https://dev-cdn.ainflue.com"
            },
            Environment.STAGING: {
                "api_base_url": "https://staging-api.ainflue.com",
                "cdn_base_url": "https://staging-cdn.ainflue.com"
            },
            Environment.PRODUCTION: {
                "api_base_url": "https://api.ainflue.com",
                "cdn_base_url": "https://cdn.ainflue.com"
            }
        }
        
        urls = url_config.get(self.current_environment, url_config[Environment.DEVELOPMENT])
        
        app_config = MobileAppConfig(
            config_id=config_id,
            environment=self.current_environment,
            app_name="Ainflue Creator",
            app_version="1.0.0",
            api_base_url=urls["api_base_url"],
            cdn_base_url=urls["cdn_base_url"],
            features={
                "content_upload": True,
                "ai_processing": True,
                "collaboration": True,
                "monetization": True,
                "analytics": True,
                "push_notifications": True,
                "offline_support": True,
                "biometric_auth": True,
                "social_sharing": True,
                "premium_features": True
            },
            platform_settings=self.platform_settings,
            security_config={
                "api_key_required": True,
                "jwt_token_expiry": 3600,  # 1 hour
                "refresh_token_expiry": 604800,  # 7 days
                "max_login_attempts": 5,
                "account_lockout_duration": 900,  # 15 minutes
                "password_min_length": 8,
                "two_factor_auth": self.current_environment == Environment.PRODUCTION
            },
            analytics_config={
                "enabled": True,
                "crash_reporting": True,
                "performance_monitoring": True,
                "user_analytics": True,
                "business_analytics": True,
                "retention_days": 90
            },
            monitoring_config={
                "health_check_interval": 300,  # 5 minutes
                "error_reporting": True,
                "performance_alerts": True,
                "uptime_monitoring": True
            }
        )
        
        self.app_configs[self.current_environment.value] = app_config
    
    def get_feature_flags(
        self,
        user_id: str,
        platform: Platform,
        environment: Optional[Environment] = None
    ) -> Dict[str, bool]:
        """Get enabled feature flags for user/platform/environment."""        
        if environment is None:
            environment = self.current_environment
        
        enabled_flags = {}
        
        for flag_name, flag in self.feature_flags.items():
            enabled_flags[flag_name] = flag.is_enabled_for_user(
                user_id, platform, environment
            )
        
        self.logger.info(
            f"Feature flags retrieved for user {user_id} on {platform.value}: "
            f"{sum(enabled_flags.values())}/{len(enabled_flags)} enabled"
        )
        
        return enabled_flags
    
    def update_feature_flag(
        self,
        flag_name: str,
        **updates
    ) -> Optional[FeatureFlag]:
        """Update feature flag configuration."""        
        if flag_name not in self.feature_flags:
            return None
        
        flag = self.feature_flags[flag_name]
        
        for key, value in updates.items():
            if hasattr(flag, key):
                setattr(flag, key, value)
        
        flag.updated_at = datetime.utcnow()
        
        self.logger.info(f"Feature flag updated: {flag_name}")
        
        return flag
    
    def create_feature_flag(
        self,
        name: str,
        description: str,
        enabled: bool = False,
        **kwargs
    ) -> FeatureFlag:
        """Create new feature flag."""        
        flag_id = str(uuid.uuid4())
        
        feature_flag = FeatureFlag(
            flag_id=flag_id,
            name=name,
            description=description,
            enabled=enabled,
            **kwargs
        )
        
        self.feature_flags[name] = feature_flag
        
        self.logger.info(f"Feature flag created: {name}")
        
        return feature_flag
    
    def get_platform_settings(self, platform: Platform) -> Optional[PlatformSettings]:
        """Get platform-specific settings."""        
        return self.platform_settings.get(platform)
    
    def update_platform_settings(
        self,
        platform: Platform,
        **updates
    ) -> Optional[PlatformSettings]:
        """Update platform-specific settings."""        
        if platform not in self.platform_settings:
            return None
        
        settings = self.platform_settings[platform]
        
        for key, value in updates.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        settings.updated_at = datetime.utcnow()
        
        self.logger.info(f"Platform settings updated: {platform.value}")
        
        return settings
    
    def get_mobile_config(
        self,
        user_id: str,
        platform: Platform,
        app_version: str
    ) -> Dict[str, Any]:
        """Get complete mobile configuration for client."""        
        app_config = self.app_configs.get(self.current_environment.value)
        platform_settings = self.platform_settings.get(platform)
        feature_flags = self.get_feature_flags(user_id, platform)
        
        if not app_config or not platform_settings:
            raise ValueError(f"Configuration not found for {platform.value}")
        
        # Check version compatibility
        is_supported = self._check_version_compatibility(
            app_version, platform_settings.min_supported_version
        )
        
        mobile_config = {
            "app_info": {
                "name": app_config.app_name,
                "version": app_config.app_version,
                "environment": app_config.environment.value,
                "supported": is_supported,
                "update_required": not is_supported
            },
            "api_config": {
                "base_url": app_config.api_base_url,
                "cdn_url": app_config.cdn_base_url,
                "timeout": platform_settings.performance_settings.get("network_timeout", 30),
                "endpoints": platform_settings.api_endpoints
            },
            "features": feature_flags,
            "upload_config": platform_settings.upload_limits,
            "security_config": {
                key: value for key, value in platform_settings.security_settings.items()
                if key not in ["app_integrity_check"]  # Don't expose internal security details
            },
            "ui_config": platform_settings.ui_settings,
            "analytics_config": platform_settings.analytics_config,
            "push_config": platform_settings.push_notification_config,
            "limits": {
                "max_file_size": platform_settings.upload_limits.get("max_file_size"),
                "max_concurrent_uploads": platform_settings.upload_limits.get("max_concurrent_uploads")
            }
        }
        
        self.logger.info(
            f"Mobile config generated for user {user_id} on {platform.value} v{app_version}"
        )
        
        return mobile_config
    
    def _check_version_compatibility(
        self,
        client_version: str,
        min_supported_version: str
    ) -> bool:
        """Check if client version is supported."""        
        try:
            client_parts = [int(x) for x in client_version.split('.')]
            min_parts = [int(x) for x in min_supported_version.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(client_parts), len(min_parts))
            client_parts.extend([0] * (max_len - len(client_parts)))
            min_parts.extend([0] * (max_len - len(min_parts)))
            
            return client_parts >= min_parts
            
        except (ValueError, AttributeError):
            # If version parsing fails, assume unsupported
            return False
    
    def export_config(self, platform: Optional[Platform] = None) -> Dict[str, Any]:
        """Export configuration for backup or deployment."""        
        export_data = {
            "environment": self.current_environment.value,
            "feature_flags": {
                name: asdict(flag) for name, flag in self.feature_flags.items()
            },
            "app_configs": {
                env: asdict(config) for env, config in self.app_configs.items()
            }
        }
        
        if platform:
            if platform in self.platform_settings:
                export_data["platform_settings"] = {
                    platform.value: asdict(self.platform_settings[platform])
                }
        else:
            export_data["platform_settings"] = {
                p.value: asdict(settings) for p, settings in self.platform_settings.items()
            }
        
        return export_data
    
    def import_config(self, config_data: Dict[str, Any]) -> bool:
        """Import configuration from backup or deployment."""        
        try:
            # Import feature flags
            if "feature_flags" in config_data:
                for flag_name, flag_data in config_data["feature_flags"].items():
                    # Convert datetime strings back to datetime objects
                    if "created_at" in flag_data:
                        flag_data["created_at"] = datetime.fromisoformat(flag_data["created_at"])
                    if "updated_at" in flag_data:
                        flag_data["updated_at"] = datetime.fromisoformat(flag_data["updated_at"])
                    if "expiry_date" in flag_data and flag_data["expiry_date"]:
                        flag_data["expiry_date"] = datetime.fromisoformat(flag_data["expiry_date"])
                    
                    # Convert platform and environment lists
                    if "target_platforms" in flag_data:
                        flag_data["target_platforms"] = [
                            Platform(p) for p in flag_data["target_platforms"]
                        ]
                    if "target_environments" in flag_data:
                        flag_data["target_environments"] = [
                            Environment(e) for e in flag_data["target_environments"]
                        ]
                    
                    self.feature_flags[flag_name] = FeatureFlag(**flag_data)
            
            self.logger.info("Configuration imported successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration import failed: {str(e)}")
            return False


# Utility functions
def get_mobile_config() -> MobileConfig:
    """Get mobile configuration instance."""    return MobileConfig()


def load_platform_settings(platform: Platform) -> Optional[PlatformSettings]:
    """Load platform-specific settings."""    config = get_mobile_config()
    return config.get_platform_settings(platform)


def get_feature_flags_for_user(
    user_id: str,
    platform: Platform,
    environment: Optional[Environment] = None
) -> Dict[str, bool]:
    """Get feature flags for specific user and platform."""    config = get_mobile_config()
    return config.get_feature_flags(user_id, platform, environment)


# Main execution for testing
if __name__ == "__main__":
    # Test mobile configuration
    config = MobileConfig()
    
    # Test feature flags
    flags = config.get_feature_flags("user123", Platform.ANDROID)
    print(f"Feature flags for Android user: {flags}")
    
    # Test mobile config generation
    mobile_config = config.get_mobile_config("user123", Platform.IOS, "1.0.0")
    print(f"Mobile config: {json.dumps(mobile_config, indent=2, default=str)}")
    
    # Test configuration export
    export_data = config.export_config(Platform.ANDROID)
    print(f"Exported Android config: {len(export_data)} sections")
    
    print("Mobile configuration testing completed!")