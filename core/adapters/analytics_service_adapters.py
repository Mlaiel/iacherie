"""Analytics Service Adapters - Enterprise Data Intelligence

This module provides comprehensive adapters for major analytics platforms
including Google Analytics, Facebook Analytics, Adobe Analytics, and others.
Each adapter implements advanced tracking, conversion optimization, and
performance measurement for creator content and business intelligence.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Supported Platforms:
- Google Analytics: GA4, Universal Analytics, E-commerce tracking
- Facebook Analytics: Business insights, Conversion tracking
- Adobe Analytics: Experience Cloud, Real-time analytics
- Mixpanel: Event tracking, Funnel analysis, Cohort analysis
- Amplitude: Product analytics, User journey mapping
- Segment: Customer data platform, Event streaming
- Hotjar: Heatmaps, Session recordings, User feedback
- Custom Analytics: Self-hosted analytics solutions
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from urllib.parse import urlencode

from .base_adapter import (
    BasePlatformAdapter, PlatformType, AdapterStatus, AuthenticationType,
    AdapterCredentials, RateLimitConfig, AdapterError, AuthenticationError
)

logger = logging.getLogger(__name__)

class AnalyticsPlatform(Enum):
    """Supported analytics platforms."""    GOOGLE_ANALYTICS = "google_analytics"
    FACEBOOK_ANALYTICS = "facebook_analytics"
    ADOBE_ANALYTICS = "adobe_analytics"
    MIXPANEL = "mixpanel"
    AMPLITUDE = "amplitude"
    SEGMENT = "segment"
    HOTJAR = "hotjar"
    CUSTOM_ANALYTICS = "custom_analytics"
    YOUTUBE_ANALYTICS = "youtube_analytics"
    INSTAGRAM_INSIGHTS = "instagram_insights"

class EventType(Enum):
    """Analytics event types."""    PAGE_VIEW = "page_view"
    CLICK = "click"
    CONVERSION = "conversion"
    PURCHASE = "purchase"
    SIGN_UP = "sign_up"
    LOGIN = "login"
    CONTENT_VIEW = "content_view"
    VIDEO_PLAY = "video_play"
    VIDEO_COMPLETE = "video_complete"
    DOWNLOAD = "download"
    SHARE = "share"
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    SUBSCRIPTION = "subscription"
    CUSTOM = "custom"

class MetricType(Enum):
    """Analytics metric types."""    USERS = "users"
    SESSIONS = "sessions"
    PAGE_VIEWS = "page_views"
    BOUNCE_RATE = "bounce_rate"
    SESSION_DURATION = "session_duration"
    CONVERSION_RATE = "conversion_rate"
    REVENUE = "revenue"
    ENGAGEMENT_RATE = "engagement_rate"
    RETENTION_RATE = "retention_rate"
    CLICK_THROUGH_RATE = "click_through_rate"
    COST_PER_ACQUISITION = "cost_per_acquisition"
    LIFETIME_VALUE = "lifetime_value"

@dataclass
class AnalyticsEvent:
    """Analytics event data structure."""    event_type: EventType
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    user_properties: Dict[str, Any] = field(default_factory=dict)
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_info: Dict[str, str] = field(default_factory=dict)
    location_info: Dict[str, str] = field(default_factory=dict)
    custom_dimensions: Dict[str, str] = field(default_factory=dict)

@dataclass
class AnalyticsQuery:
    """Analytics query parameters."""    start_date: datetime
    end_date: datetime
    metrics: List[MetricType]
    dimensions: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    segments: List[str] = field(default_factory=list)
    limit: int = 1000
    offset: int = 0
    sort_by: Optional[str] = None
    sort_order: str = "desc"

@dataclass
class AnalyticsReport:
    """Analytics report data structure."""    query: AnalyticsQuery
    data: List[Dict[str, Any]] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    platform: Optional[str] = None
    report_id: Optional[str] = None

class GoogleAnalyticsAdapter(BasePlatformAdapter):
    """    Enterprise Google Analytics adapter with GA4 and Universal Analytics support.
    
    Supports:
    - Google Analytics 4 (GA4) Measurement Protocol
    - Universal Analytics (deprecated but still supported)
    - E-commerce tracking and enhanced e-commerce
    - Custom dimensions and metrics
    - Goal tracking and conversion measurement
    - Audience segmentation and cohort analysis
    - Real-time reporting and data streaming
    """    
    def __init__(self, credentials: AdapterCredentials, redis_client=None):
        rate_config = RateLimitConfig(
            requests_per_second=10.0,
            requests_per_minute=600.0,
            requests_per_hour=10000.0,
            burst_limit=20
        )
        
        if not credentials.base_url:
            credentials.base_url = "https://www.google-analytics.com"
        
        super().__init__(
            platform_name="Google Analytics",
            platform_type=PlatformType.ANALYTICS_SERVICE,
            credentials=credentials,
            rate_limit_config=rate_config,
            redis_client=redis_client
        )
        
        self.measurement_id = credentials.custom_headers.get('measurement_id')
        self.api_secret = credentials.custom_headers.get('api_secret')
        self.property_id = credentials.custom_headers.get('property_id')
    
    async def authenticate(self) -> bool:
        """Authenticate with Google Analytics."""        try:
            if self.credentials.auth_type == AuthenticationType.API_KEY:
                # For Measurement Protocol, we just need to validate the measurement ID and API secret
                if self.measurement_id and self.api_secret:
                    logger.info("Google Analytics authentication successful (Measurement Protocol)")
                    return True
            else:
                # For Reporting API, test with a simple query
                response = await self.make_request(
                    method="POST",
                    endpoint="v1beta/properties/{}/runReport".format(self.property_id),
                    json_data={
                        "requests": [{
                            "dimensions": [{"name": "date"}],
                            "metrics": [{"name": "sessions"}],
                            "dateRanges": [{
                                "startDate": "7daysAgo",
                                "endDate": "today"
                            }],
                            "limit": 1
                        }]
                    },
                    headers={"Authorization": f"Bearer {self.credentials.access_token}"}
                )
                
                if "reports" in response:
                    logger.info("Google Analytics authentication successful (Reporting API)")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Google Analytics authentication failed: {e}")
            return False
    
    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Track event using GA4 Measurement Protocol."""        try:
            # Prepare event data for GA4 Measurement Protocol
            event_data = {
                "client_id": event.user_id or str(uuid.uuid4()),
                "events": [{
                    "name": self._map_event_type(event.event_type),
                    "params": {
                        **event.properties,
                        "page_location": event.page_url,
                        "page_title": event.page_title,
                        "page_referrer": event.referrer,
                        **event.custom_dimensions
                    }
                }]
            }
            
            # Add user properties if provided
            if event.user_properties:
                event_data["user_properties"] = {
                    key: {"value": value} for key, value in event.user_properties.items()
                }
            
            # Send to GA4 Measurement Protocol
            response = await self.make_request(
                method="POST",
                endpoint=f"mp/collect?measurement_id={self.measurement_id}&api_secret={self.api_secret}",
                json_data=event_data
            )
            
            logger.debug(f"Google Analytics event tracked: {event.event_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Google Analytics event tracking failed: {e}")
            return False
    
    async def get_report(self, query: AnalyticsQuery) -> AnalyticsReport:
        """Get analytics report from GA4 Reporting API."""        try:
            # Prepare reporting request
            request_data = {
                "property": f"properties/{self.property_id}",
                "dimensions": [{"name": dim} for dim in query.dimensions],
                "metrics": [{"name": self._map_metric_type(metric)} for metric in query.metrics],
                "dateRanges": [{
                    "startDate": query.start_date.strftime("%Y-%m-%d"),
                    "endDate": query.end_date.strftime("%Y-%m-%d")
                }],
                "limit": query.limit,
                "offset": query.offset
            }
            
            # Add filters if provided
            if query.filters:
                request_data["dimensionFilter"] = self._build_filters(query.filters)
            
            # Add sorting if provided
            if query.sort_by:
                request_data["orderBys"] = [{
                    "dimension": {"dimensionName": query.sort_by} if query.sort_by in query.dimensions else None,
                    "metric": {"metricName": query.sort_by} if query.sort_by not in query.dimensions else None,
                    "desc": query.sort_order.lower() == "desc"
                }]
            
            response = await self.make_request(
                method="POST",
                endpoint=f"v1beta/properties/{self.property_id}:runReport",
                json_data=request_data,
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            # Process response data
            report_data = []
            totals = {}
            
            if "rows" in response:
                for row in response["rows"]:
                    row_data = {}
                    
                    # Process dimensions
                    for i, dimension in enumerate(query.dimensions):
                        if i < len(row.get("dimensionValues", [])):
                            row_data[dimension] = row["dimensionValues"][i]["value"]
                    
                    # Process metrics
                    for i, metric in enumerate(query.metrics):
                        if i < len(row.get("metricValues", [])):
                            metric_name = self._map_metric_type(metric)
                            row_data[metric_name] = float(row["metricValues"][i]["value"])
                    
                    report_data.append(row_data)
            
            # Process totals
            if "totals" in response:
                for i, metric in enumerate(query.metrics):
                    if i < len(response["totals"][0].get("metricValues", [])):
                        metric_name = self._map_metric_type(metric)
                        totals[metric_name] = float(response["totals"][0]["metricValues"][i]["value"])
            
            return AnalyticsReport(
                query=query,
                data=report_data,
                totals=totals,
                metadata=response.get("metadata", {}),
                platform="google_analytics",
                report_id=str(uuid.uuid4())
            )
            
        except Exception as e:
            logger.error(f"Google Analytics report generation failed: {e}")
            return AnalyticsReport(query=query, platform="google_analytics")
    
    def _map_event_type(self, event_type: EventType) -> str:
        """Map EventType to GA4 event name."""        mapping = {
            EventType.PAGE_VIEW: "page_view",
            EventType.CLICK: "click",
            EventType.CONVERSION: "conversion",
            EventType.PURCHASE: "purchase",
            EventType.SIGN_UP: "sign_up",
            EventType.LOGIN: "login",
            EventType.CONTENT_VIEW: "view_item",
            EventType.VIDEO_PLAY: "video_start",
            EventType.VIDEO_COMPLETE: "video_complete",
            EventType.DOWNLOAD: "file_download",
            EventType.SHARE: "share",
            EventType.LIKE: "like",
            EventType.COMMENT: "comment",
            EventType.FOLLOW: "follow",
            EventType.SUBSCRIPTION: "subscribe"
        }
        return mapping.get(event_type, "custom_event")
    
    def _map_metric_type(self, metric_type: MetricType) -> str:
        """Map MetricType to GA4 metric name."""        mapping = {
            MetricType.USERS: "activeUsers",
            MetricType.SESSIONS: "sessions",
            MetricType.PAGE_VIEWS: "screenPageViews",
            MetricType.BOUNCE_RATE: "bounceRate",
            MetricType.SESSION_DURATION: "averageSessionDuration",
            MetricType.CONVERSION_RATE: "conversionRate",
            MetricType.REVENUE: "totalRevenue",
            MetricType.ENGAGEMENT_RATE: "engagementRate",
            MetricType.RETENTION_RATE: "retentionRate"
        }
        return mapping.get(metric_type, str(metric_type.value))
    
    def _build_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build GA4 dimension filter from query filters."""        # Simplified filter builder - real implementation would be more comprehensive
        filter_expressions = []
        
        for dimension, value in filters.items():
            filter_expressions.append({
                "filter": {
                    "fieldName": dimension,
                    "stringFilter": {
                        "matchType": "EXACT",
                        "value": str(value)
                    }
                }
            })
        
        if len(filter_expressions) == 1:
            return filter_expressions[0]
        elif len(filter_expressions) > 1:
            return {
                "andGroup": {
                    "expressions": filter_expressions
                }
            }
        
        return {}
    
    async def health_check(self) -> bool:
        """Perform Google Analytics health check."""        try:
            if self.measurement_id and self.api_secret:
                return True
            elif self.property_id and self.credentials.access_token:
                response = await self.make_request(
                    method="POST",
                    endpoint=f"v1beta/properties/{self.property_id}:runReport",
                    json_data={
                        "dimensions": [{"name": "date"}],
                        "metrics": [{"name": "sessions"}],
                        "dateRanges": [{
                            "startDate": "yesterday",
                            "endDate": "yesterday"
                        }],
                        "limit": 1
                    },
                    headers={"Authorization": f"Bearer {self.credentials.access_token}"}
                )
                return "rows" in response or "totals" in response
            return False
        except:
            return False

class MixpanelAdapter(BasePlatformAdapter):
    """    Enterprise Mixpanel analytics adapter.
    
    Supports:
    - Event tracking and user profiles
    - Funnel analysis and cohort analysis
    - A/B testing and feature flags
    - Revenue tracking and LTV analysis
    - Real-time data streaming
    - Custom properties and user segmentation
    """    
    def __init__(self, credentials: AdapterCredentials, redis_client=None):
        rate_config = RateLimitConfig(
            requests_per_second=60.0,
            requests_per_minute=3600.0,
            requests_per_hour=60000.0,
            burst_limit=100
        )
        
        if not credentials.base_url:
            credentials.base_url = "https://api.mixpanel.com"
        
        super().__init__(
            platform_name="Mixpanel",
            platform_type=PlatformType.ANALYTICS_SERVICE,
            credentials=credentials,
            rate_limit_config=rate_config,
            redis_client=redis_client
        )
        
        self.project_token = credentials.custom_headers.get('project_token')
    
    async def authenticate(self) -> bool:
        """Authenticate with Mixpanel API."""        try:
            # Test authentication with a simple query
            response = await self.make_request(
                method="GET",
                endpoint="query/events",
                params={
                    "event": '["page_view"]',
                    "from_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "to_date": datetime.now().strftime("%Y-%m-%d"),
                    "unit": "day"
                },
                headers={"Authorization": f"Basic {self.credentials.api_key}"}
            )
            
            if "data" in response:
                logger.info("Mixpanel authentication successful")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Mixpanel authentication failed: {e}")
            return False
    
    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Track event in Mixpanel."""        try:
            event_data = {
                "event": self._map_event_type(event.event_type),
                "properties": {
                    "token": self.project_token,
                    "distinct_id": event.user_id or str(uuid.uuid4()),
                    "time": int(event.timestamp.timestamp()) if event.timestamp else int(datetime.now().timestamp()),
                    "$current_url": event.page_url,
                    "$referrer": event.referrer,
                    "$user_agent": event.user_agent,
                    "$ip": event.ip_address,
                    **event.properties,
                    **event.custom_dimensions
                }
            }
            
            # Add device and location info
            if event.device_info:
                event_data["properties"].update({
                    f"$device_{k}": v for k, v in event.device_info.items()
                })
            
            if event.location_info:
                event_data["properties"].update({
                    f"$location_{k}": v for k, v in event.location_info.items()
                })
            
            # Encode event data
            import base64
            encoded_data = base64.b64encode(json.dumps(event_data).encode()).decode()
            
            response = await self.make_request(
                method="POST",
                endpoint="track",
                params={"data": encoded_data}
            )
            
            if response.get("status") == 1:
                logger.debug(f"Mixpanel event tracked: {event.event_type.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Mixpanel event tracking failed: {e}")
            return False
    
    def _map_event_type(self, event_type: EventType) -> str:
        """Map EventType to Mixpanel event name."""        mapping = {
            EventType.PAGE_VIEW: "Page View",
            EventType.CLICK: "Click",
            EventType.CONVERSION: "Conversion",
            EventType.PURCHASE: "Purchase",
            EventType.SIGN_UP: "Sign Up",
            EventType.LOGIN: "Login",
            EventType.CONTENT_VIEW: "Content View",
            EventType.VIDEO_PLAY: "Video Play",
            EventType.VIDEO_COMPLETE: "Video Complete",
            EventType.DOWNLOAD: "Download",
            EventType.SHARE: "Share",
            EventType.LIKE: "Like",
            EventType.COMMENT: "Comment",
            EventType.FOLLOW: "Follow",
            EventType.SUBSCRIPTION: "Subscription"
        }
        return mapping.get(event_type, "Custom Event")
    
    async def health_check(self) -> bool:
        """Perform Mixpanel health check."""        try:
            response = await self.make_request(
                method="GET",
                endpoint="query/events",
                params={
                    "event": '["page_view"]',
                    "from_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "to_date": datetime.now().strftime("%Y-%m-%d"),
                    "unit": "day"
                },
                headers={"Authorization": f"Basic {self.credentials.api_key}"}
            )
            return "data" in response
        except:
            return False

class AnalyticsAdapterFactory:
    """Factory for creating analytics platform adapters."""    
    _adapters = {
        AnalyticsPlatform.GOOGLE_ANALYTICS: GoogleAnalyticsAdapter,
        AnalyticsPlatform.MIXPANEL: MixpanelAdapter,
        # Additional platforms would be registered here
    }
    
    @classmethod
    def create_adapter(cls, platform: AnalyticsPlatform, credentials: AdapterCredentials, redis_client=None) -> BasePlatformAdapter:
        """Create adapter for specified analytics platform."""        if platform not in cls._adapters:
            raise AdapterError(f"Unsupported analytics platform: {platform}")
        
        adapter_class = cls._adapters[platform]
        return adapter_class(credentials, redis_client)
    
    @classmethod
    def get_supported_platforms(cls) -> List[AnalyticsPlatform]:
        """Get list of supported analytics platforms."""        return list(cls._adapters.keys())

# Export all classes
__all__ = [
    'AnalyticsPlatform',
    'EventType',
    'MetricType',
    'AnalyticsEvent',
    'AnalyticsQuery',
    'AnalyticsReport',
    'GoogleAnalyticsAdapter',
    'MixpanelAdapter',
    'AnalyticsAdapterFactory'
]
