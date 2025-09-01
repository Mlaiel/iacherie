"""Analytics APIs Configuration - Analytics & Business Intelligence Services
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module configures analytics and business intelligence APIs including
Google Analytics, Mixpanel, Segment, and other tracking services for
comprehensive user behavior and business metrics analysis.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class AnalyticsServiceType(Enum):
    """
Analytics service types"""

    WEB_ANALYTICS = "web_analytics"
    EVENT_TRACKING = "event_tracking"
    USER_ANALYTICS = "user_analytics"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    PERFORMANCE_MONITORING = "performance_monitoring"
    CONVERSION_TRACKING = "conversion_tracking"

class DataRetentionPeriod(Enum):
    """Data retention periods"""

    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    MONTHS_6 = "6_months"
    YEAR_1 = "1_year"
    YEARS_2 = "2_years"
    UNLIMITED = "unlimited"

@dataclass
class AnalyticsAPIConfig:
    """Configuration class for analytics APIs"""
    service_name: str
    service_type: AnalyticsServiceType
    base_url: str
    api_version: str
    
    # Credentials (from environment)
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    tracking_id: Optional[str] = None
    property_id: Optional[str] = None
    project_id: Optional[str] = None
    
    # Data configuration
    data_retention: DataRetentionPeriod = DataRetentionPeriod.YEAR_1
    real_time_enabled: bool = True
    custom_events_enabled: bool = True
    user_identification_enabled: bool = True
    
    # Privacy & Compliance
    gdpr_compliant: bool = True
    ccpa_compliant: bool = True
    anonymize_ip: bool = True
    cookie_consent_required: bool = True
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 3600
    batch_size_limit: int = 500
    
    # Features
    supports_custom_dimensions: bool = True
    supports_goal_tracking: bool = True
    supports_ecommerce: bool = True
    supports_attribution: bool = True
    
    # Reporting capabilities
    supports_real_time_reports: bool = True
    supports_custom_reports: bool = True
    report_delay_minutes: int = 5
    
    # Cost structure
    monthly_events_included: int = 100000
    cost_per_additional_event: float = 0.0001
    
    # Environment configurations
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def get_environment_config(self, environment: str = "production") -> Dict[str, Any]:
        """Get configuration for specific environment"""
        base_config = self.__dict__.copy()
        env_config = self.environments.get(environment, {})
        base_config.update(env_config)
        return base_config

# Google Analytics 4 Configuration
GOOGLE_ANALYTICS_CONFIG = AnalyticsAPIConfig(
    service_name="google_analytics",
    service_type=AnalyticsServiceType.WEB_ANALYTICS,
    base_url="https://analyticsdata.googleapis.com",
    api_version="v1beta",
    api_key=os.getenv("GOOGLE_ANALYTICS_API_KEY"),
    tracking_id=os.getenv("GA4_MEASUREMENT_ID"),
    property_id=os.getenv("GA4_PROPERTY_ID"),
    data_retention=DataRetentionPeriod.YEARS_2,
    real_time_enabled=True,
    custom_events_enabled=True,
    user_identification_enabled=True,
    supports_custom_dimensions=True,
    supports_goal_tracking=True,
    supports_ecommerce=True,
    supports_attribution=True,
    supports_real_time_reports=True,
    supports_custom_reports=True,
    report_delay_minutes=5,
    monthly_events_included=100000000,  # GA4 generous limits
    cost_per_additional_event=0.0,
    environments={
        "development": {
            "tracking_id": os.getenv("GA4_DEV_MEASUREMENT_ID"),
            "property_id": os.getenv("GA4_DEV_PROPERTY_ID")
        },
        "staging": {
            "tracking_id": os.getenv("GA4_STAGING_MEASUREMENT_ID"),
            "property_id": os.getenv("GA4_STAGING_PROPERTY_ID")
        }
    }
)

# Mixpanel Configuration
MIXPANEL_CONFIG = AnalyticsAPIConfig(
    service_name="mixpanel",
    service_type=AnalyticsServiceType.EVENT_TRACKING,
    base_url="https://api.mixpanel.com",
    api_version="v2",
    api_key=os.getenv("MIXPANEL_API_KEY"),
    secret_key=os.getenv("MIXPANEL_API_SECRET"),
    project_id=os.getenv("MIXPANEL_PROJECT_ID"),
    data_retention=DataRetentionPeriod.UNLIMITED,
    real_time_enabled=True,
    custom_events_enabled=True,
    user_identification_enabled=True,
    supports_custom_dimensions=True,
    supports_goal_tracking=True,
    supports_attribution=True,
    supports_real_time_reports=True,
    supports_custom_reports=True,
    report_delay_minutes=1,  # Near real-time
    rate_limit_per_minute=1000,
    batch_size_limit=2000,
    monthly_events_included=100000,
    cost_per_additional_event=0.0005,
    environments={
        "development": {
            "project_id": os.getenv("MIXPANEL_DEV_PROJECT_ID"),
            "api_key": os.getenv("MIXPANEL_DEV_API_KEY")
        },
        "staging": {
            "project_id": os.getenv("MIXPANEL_STAGING_PROJECT_ID"),
            "api_key": os.getenv("MIXPANEL_STAGING_API_KEY")
        }
    }
)

# Segment Configuration (Customer Data Platform)
SEGMENT_CONFIG = AnalyticsAPIConfig(
    service_name="segment",
    service_type=AnalyticsServiceType.USER_ANALYTICS,
    base_url="https://api.segment.io",
    api_version="v1",
    api_key=os.getenv("SEGMENT_WRITE_KEY"),
    secret_key=os.getenv("SEGMENT_SECRET_KEY"),
    data_retention=DataRetentionPeriod.UNLIMITED,
    real_time_enabled=True,
    custom_events_enabled=True,
    user_identification_enabled=True,
    supports_custom_dimensions=True,
    supports_attribution=True,
    rate_limit_per_minute=500,
    batch_size_limit=500,
    monthly_events_included=10000,
    cost_per_additional_event=0.0012,
    environments={
        "development": {
            "api_key": os.getenv("SEGMENT_DEV_WRITE_KEY")
        },
        "staging": {
            "api_key": os.getenv("SEGMENT_STAGING_WRITE_KEY")
        }
    }
)

# Amplitude Configuration
AMPLITUDE_CONFIG = AnalyticsAPIConfig(
    service_name="amplitude",
    service_type=AnalyticsServiceType.USER_ANALYTICS,
    base_url="https://api2.amplitude.com",
    api_version="v2",
    api_key=os.getenv("AMPLITUDE_API_KEY"),
    secret_key=os.getenv("AMPLITUDE_SECRET_KEY"),
    data_retention=DataRetentionPeriod.UNLIMITED,
    real_time_enabled=True,
    custom_events_enabled=True,
    user_identification_enabled=True,
    supports_custom_dimensions=True,
    supports_goal_tracking=True,
    supports_attribution=True,
    supports_real_time_reports=True,
    supports_custom_reports=True,
    report_delay_minutes=2,
    rate_limit_per_minute=1000,
    batch_size_limit=1000,
    monthly_events_included=10000000,  # Generous free tier
    cost_per_additional_event=0.0001,
    environments={
        "development": {
            "api_key": os.getenv("AMPLITUDE_DEV_API_KEY")
        },
        "staging": {
            "api_key": os.getenv("AMPLITUDE_STAGING_API_KEY")
        }
    }
)

# Hotjar Configuration (User Behavior Analytics)
HOTJAR_CONFIG = AnalyticsAPIConfig(
    service_name="hotjar",
    service_type=AnalyticsServiceType.USER_ANALYTICS,
    base_url="https://insights.hotjar.com/api",
    api_version="v1",
    api_key=os.getenv("HOTJAR_API_KEY"),
    tracking_id=os.getenv("HOTJAR_SITE_ID"),
    data_retention=DataRetentionPeriod.YEAR_1,
    real_time_enabled=False,  # Hotjar processes data with delay
    report_delay_minutes=60,
    supports_custom_reports=True,
    monthly_events_included=35000,  # Page views
    cost_per_additional_event=0.01,
    environments={
        "development": {
            "tracking_id": os.getenv("HOTJAR_DEV_SITE_ID")
        },
        "staging": {
            "tracking_id": os.getenv("HOTJAR_STAGING_SITE_ID")
        }
    }
)

# PostHog Configuration (Product Analytics)
POSTHOG_CONFIG = AnalyticsAPIConfig(
    service_name="posthog",
    service_type=AnalyticsServiceType.USER_ANALYTICS,
    base_url=os.getenv("POSTHOG_HOST", "https://app.posthog.com"),
    api_version="v1",
    api_key=os.getenv("POSTHOG_API_KEY"),
    project_id=os.getenv("POSTHOG_PROJECT_ID"),
    data_retention=DataRetentionPeriod.UNLIMITED,
    real_time_enabled=True,
    custom_events_enabled=True,
    user_identification_enabled=True,
    supports_custom_dimensions=True,
    supports_goal_tracking=True,
    supports_attribution=True,
    supports_real_time_reports=True,
    supports_custom_reports=True,
    report_delay_minutes=1,
    rate_limit_per_minute=1000,
    batch_size_limit=500,
    monthly_events_included=1000000,
    cost_per_additional_event=0.0005,
    environments={
        "development": {
            "base_url": "https://app.posthog.com",
            "project_id": os.getenv("POSTHOG_DEV_PROJECT_ID")
        },
        "staging": {
            "base_url": "https://app.posthog.com",
            "project_id": os.getenv("POSTHOG_STAGING_PROJECT_ID")
        }
    }
)

# Adobe Analytics Configuration
ADOBE_ANALYTICS_CONFIG = AnalyticsAPIConfig(
    service_name="adobe_analytics",
    service_type=AnalyticsServiceType.WEB_ANALYTICS,
    base_url="https://analytics.adobe.io",
    api_version="v2.0",
    api_key=os.getenv("ADOBE_ANALYTICS_API_KEY"),
    secret_key=os.getenv("ADOBE_ANALYTICS_CLIENT_SECRET"),
    property_id=os.getenv("ADOBE_ANALYTICS_COMPANY_ID"),
    data_retention=DataRetentionPeriod.YEARS_2,
    supports_custom_dimensions=True,
    supports_goal_tracking=True,
    supports_ecommerce=True,
    supports_attribution=True,
    supports_custom_reports=True,
    report_delay_minutes=30,
    rate_limit_per_minute=60,
    monthly_events_included=10000000,
    cost_per_additional_event=0.001,
    environments={
        "development": {
            "property_id": os.getenv("ADOBE_ANALYTICS_DEV_COMPANY_ID")
        }
    }
)

# Custom Analytics Service Configuration
CUSTOM_ANALYTICS_CONFIG = AnalyticsAPIConfig(
    service_name="custom_analytics",
    service_type=AnalyticsServiceType.BUSINESS_INTELLIGENCE,
    base_url="https://api.ia-influencer.com/analytics",
    api_version="v1",
    api_key=os.getenv("CUSTOM_ANALYTICS_API_KEY"),
    data_retention=DataRetentionPeriod.UNLIMITED,
    real_time_enabled=True,
    custom_events_enabled=True,
    user_identification_enabled=True,
    supports_custom_dimensions=True,
    supports_goal_tracking=True,
    supports_ecommerce=True,
    supports_attribution=True,
    supports_real_time_reports=True,
    supports_custom_reports=True,
    report_delay_minutes=1,
    rate_limit_per_minute=2000,
    batch_size_limit=1000,
    monthly_events_included=50000000,  # High limits for internal service
    cost_per_additional_event=0.0,
    environments={
        "development": {
            "base_url": "http://localhost:8000/api/analytics",
            "monthly_events_included": 1000000
        },
        "staging": {
            "base_url": "https://staging-api.ia-influencer.com/analytics",
            "monthly_events_included": 10000000
        }
    }
)

# Performance Monitoring - New Relic Configuration
NEW_RELIC_CONFIG = AnalyticsAPIConfig(
    service_name="new_relic",
    service_type=AnalyticsServiceType.PERFORMANCE_MONITORING,
    base_url="https://api.newrelic.com",
    api_version="v2",
    api_key=os.getenv("NEW_RELIC_API_KEY"),
    project_id=os.getenv("NEW_RELIC_ACCOUNT_ID"),
    data_retention=DataRetentionPeriod.MONTHS_6,
    real_time_enabled=True,
    supports_custom_reports=True,
    report_delay_minutes=1,
    rate_limit_per_minute=3000,
    monthly_events_included=100000000,
    cost_per_additional_event=0.0001,
    environments={
        "development": {
            "project_id": os.getenv("NEW_RELIC_DEV_ACCOUNT_ID")
        },
        "staging": {
            "project_id": os.getenv("NEW_RELIC_STAGING_ACCOUNT_ID")
        }
    }
)

# Analytics configurations registry
ANALYTICS_CONFIGS: Dict[str, AnalyticsAPIConfig] = {
    "google_analytics": GOOGLE_ANALYTICS_CONFIG,
    "mixpanel": MIXPANEL_CONFIG,
    "segment": SEGMENT_CONFIG,
    "amplitude": AMPLITUDE_CONFIG,
    "hotjar": HOTJAR_CONFIG,
    "posthog": POSTHOG_CONFIG,
    "adobe_analytics": ADOBE_ANALYTICS_CONFIG,
    "custom_analytics": CUSTOM_ANALYTICS_CONFIG,
    "new_relic": NEW_RELIC_CONFIG
}

def get_analytics_config(service: str) -> Optional[AnalyticsAPIConfig]:
    """Get analytics service configuration by name"""
    return ANALYTICS_CONFIGS.get(service.lower())

def get_services_by_type(service_type: AnalyticsServiceType) -> List[AnalyticsAPIConfig]:
    """
Get all analytics services of specific type"""
    return [config for config in ANALYTICS_CONFIGS.values() 
            if config.service_type == service_type]

def get_real_time_services() -> List[AnalyticsAPIConfig]:
    """
Get services that support real-time analytics"""
    return [config for config in ANALYTICS_CONFIGS.values() 
            if config.real_time_enabled]

def get_custom_event_services() -> List[AnalyticsAPIConfig]:
    """
Get services that support custom events"""
    return [config for config in ANALYTICS_CONFIGS.values() 
            if config.custom_events_enabled]

def get_ecommerce_services() -> List[AnalyticsAPIConfig]:
    """
Get services that support ecommerce tracking"""
    return [config for config in ANALYTICS_CONFIGS.values() 
            if config.supports_ecommerce]
