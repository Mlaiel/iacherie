"""Ultra-Advanced User Activity Logs Module

Revolutionary enterprise-grade user activity logging for IA Influencer Agent platform.
Provides comprehensive tracking for all user interactions, content operations, behavioral
analytics, collaboration workflows, revenue activities, and AI-powered user insights
with real-time monitoring and predictive behavior analysis.

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Multi-Expert Lead AI Developer & User Analytics Specialist

⚠️ ULTRA-STRONG INTELLECTUAL PROPERTY WARNING ⚠️
This revolutionary user activity logging technology is the EXCLUSIVE property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or exploitation is STRICTLY PROHIBITED.
Legal action will be taken against violators under international IP law.
Contact: mlaiel@live.de for authorization.
"""from typing import List, Dict, Any, Optional, Union, Tuple, Callable, Set
import logging
from datetime import datetime, timezone, timedelta
from enum import Enum, IntEnum
import json
import asyncio
import threading
import hashlib
import hmac
import uuid
from dataclasses import dataclass, asdict, field
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, JSON, Float, Index, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Session
import geoip2.database
import user_agents
from pathlib import Path
import ipaddress
import re
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor

# AI and ML imports for behavioral analysis
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.anomaly import IsolationForest
import joblib

logger = logging.getLogger(__name__)

Base = declarative_base()


class UserActivityType(Enum):
    """Ultra-comprehensive user activity types for complete behavioral tracking."""    
    # Authentication & Security Activities
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    SESSION_TIMEOUT = "session_timeout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    TWO_FACTOR_SETUP = "two_factor_setup"
    TWO_FACTOR_VERIFY = "two_factor_verify"
    TWO_FACTOR_DISABLE = "two_factor_disable"
    ACCOUNT_VERIFICATION = "account_verification"
    ACCOUNT_SUSPENSION = "account_suspension"
    ACCOUNT_REACTIVATION = "account_reactivation"
    SECURITY_QUESTION_UPDATE = "security_question_update"
    API_KEY_GENERATION = "api_key_generation"
    API_KEY_REVOCATION = "api_key_revocation"
    
    # Profile & Account Management
    PROFILE_CREATE = "profile_create"
    PROFILE_UPDATE = "profile_update"
    PROFILE_VIEW = "profile_view"
    AVATAR_UPLOAD = "avatar_upload"
    AVATAR_CHANGE = "avatar_change"
    BIO_UPDATE = "bio_update"
    CONTACT_INFO_UPDATE = "contact_info_update"
    PRIVACY_SETTINGS_CHANGE = "privacy_settings_change"
    NOTIFICATION_PREFERENCES = "notification_preferences"
    LANGUAGE_PREFERENCE_CHANGE = "language_preference_change"
    TIMEZONE_CHANGE = "timezone_change"
    
    # Content Management Activities (Core Business Logic)
    CONTENT_UPLOAD_START = "content_upload_start"
    CONTENT_UPLOAD_PROGRESS = "content_upload_progress"
    CONTENT_UPLOAD_COMPLETE = "content_upload_complete"
    CONTENT_UPLOAD_FAILED = "content_upload_failed"
    CONTENT_EDIT = "content_edit"
    CONTENT_DELETE = "content_delete"
    CONTENT_RESTORE = "content_restore"
    CONTENT_PUBLISH = "content_publish"
    CONTENT_UNPUBLISH = "content_unpublish"
    CONTENT_SCHEDULE = "content_schedule"
    CONTENT_DRAFT_SAVE = "content_draft_save"
    CONTENT_DUPLICATE = "content_duplicate"
    CONTENT_EXPORT = "content_export"
    CONTENT_IMPORT = "content_import"
    
    # Multi-Format Content Specific (Business Logic)
    AUDIO_UPLOAD = "audio_upload"
    AUDIO_PROCESSING = "audio_processing"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    VIDEO_UPLOAD = "video_upload"
    VIDEO_PROCESSING = "video_processing"
    VIDEO_THUMBNAIL_GENERATE = "video_thumbnail_generate"
    IMAGE_UPLOAD = "image_upload"
    IMAGE_EDITING = "image_editing"
    IMAGE_FILTER_APPLY = "image_filter_apply"
    TEXT_CONTENT_CREATE = "text_content_create"
    TEXT_CONTENT_EDIT = "text_content_edit"
    BLOG_POST_CREATE = "blog_post_create"
    BLOG_POST_PUBLISH = "blog_post_publish"
    
    # AI Processing Activities (Business Logic)
    AI_ANALYSIS_REQUEST = "ai_analysis_request"
    AI_ANALYSIS_COMPLETE = "ai_analysis_complete"
    AI_RECOMMENDATION_VIEW = "ai_recommendation_view"
    AI_RECOMMENDATION_ACCEPT = "ai_recommendation_accept"
    AI_RECOMMENDATION_REJECT = "ai_recommendation_reject"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    CONTENT_PROTECTION_ENABLE = "content_protection_enable"
    CONTENT_PROTECTION_DISABLE = "content_protection_disable"
    COPYRIGHT_CHECK_REQUEST = "copyright_check_request"
    COPYRIGHT_CLAIM_RESPONSE = "copyright_claim_response"
    
    # SEO & Optimization Activities (Business Logic)
    SEO_ANALYSIS_REQUEST = "seo_analysis_request"
    SEO_OPTIMIZATION_APPLY = "seo_optimization_apply"
    HASHTAG_GENERATION = "hashtag_generation"
    KEYWORD_RESEARCH = "keyword_research"
    METADATA_OPTIMIZATION = "metadata_optimization"
    THUMBNAIL_OPTIMIZATION = "thumbnail_optimization"
    TITLE_OPTIMIZATION = "title_optimization"
    DESCRIPTION_OPTIMIZATION = "description_optimization"
    
    # Collaboration Activities (Business Logic)
    COLLABORATION_REQUEST_SEND = "collaboration_request_send"
    COLLABORATION_REQUEST_RECEIVE = "collaboration_request_receive"
    COLLABORATION_ACCEPT = "collaboration_accept"
    COLLABORATION_DECLINE = "collaboration_decline"
    COLLABORATION_COMPLETE = "collaboration_complete"
    COLLABORATION_RATE = "collaboration_rate"
    COLLABORATION_REVIEW = "collaboration_review"
    PARTNER_SEARCH = "partner_search"
    PARTNER_PROFILE_VIEW = "partner_profile_view"
    COLLABORATION_PORTFOLIO_VIEW = "collaboration_portfolio_view"
    
    # Monetization Activities (Business Logic)
    MONETIZATION_ENABLE = "monetization_enable"
    MONETIZATION_DISABLE = "monetization_disable"
    REVENUE_DASHBOARD_VIEW = "revenue_dashboard_view"
    PAYMENT_METHOD_ADD = "payment_method_add"
    PAYMENT_METHOD_UPDATE = "payment_method_update"
    PAYMENT_METHOD_REMOVE = "payment_method_remove"
    WITHDRAWAL_REQUEST = "withdrawal_request"
    WITHDRAWAL_COMPLETE = "withdrawal_complete"
    REVENUE_REPORT_GENERATE = "revenue_report_generate"
    PRICING_UPDATE = "pricing_update"
    LICENSING_TERMS_UPDATE = "licensing_terms_update"
    
    # Platform Distribution Activities (Business Logic)
    PLATFORM_CONNECT = "platform_connect"
    PLATFORM_DISCONNECT = "platform_disconnect"
    PLATFORM_SYNC = "platform_sync"
    CONTENT_DISTRIBUTE = "content_distribute"
    DISTRIBUTION_STATUS_CHECK = "distribution_status_check"
    PLATFORM_ANALYTICS_VIEW = "platform_analytics_view"
    CROSS_PLATFORM_CAMPAIGN = "cross_platform_campaign"
    
    # Analytics & Reporting Activities
    ANALYTICS_DASHBOARD_VIEW = "analytics_dashboard_view"
    PERFORMANCE_REPORT_VIEW = "performance_report_view"
    AUDIENCE_INSIGHTS_VIEW = "audience_insights_view"
    ENGAGEMENT_METRICS_VIEW = "engagement_metrics_view"
    REVENUE_ANALYTICS_VIEW = "revenue_analytics_view"
    TREND_ANALYSIS_VIEW = "trend_analysis_view"
    EXPORT_ANALYTICS_DATA = "export_analytics_data"
    
    # Social & Engagement Activities
    CONTENT_LIKE = "content_like"
    CONTENT_UNLIKE = "content_unlike"
    CONTENT_COMMENT = "content_comment"
    CONTENT_COMMENT_REPLY = "content_comment_reply"
    CONTENT_SHARE = "content_share"
    CONTENT_BOOKMARK = "content_bookmark"
    CONTENT_UNBOOKMARK = "content_unbookmark"
    FOLLOW_USER = "follow_user"
    UNFOLLOW_USER = "unfollow_user"
    BLOCK_USER = "block_user"
    UNBLOCK_USER = "unblock_user"
    REPORT_CONTENT = "report_content"
    REPORT_USER = "report_user"
    
    # Search & Discovery Activities
    SEARCH_CONTENT = "search_content"
    SEARCH_USERS = "search_users"
    SEARCH_COLLABORATORS = "search_collaborators"
    FILTER_APPLY = "filter_apply"
    SORT_CHANGE = "sort_change"
    CATEGORY_BROWSE = "category_browse"
    TAG_EXPLORE = "tag_explore"
    TRENDING_VIEW = "trending_view"
    RECOMMENDATION_FEED_VIEW = "recommendation_feed_view"
    
    # Subscription & Billing Activities
    SUBSCRIPTION_UPGRADE = "subscription_upgrade"
    SUBSCRIPTION_DOWNGRADE = "subscription_downgrade"
    SUBSCRIPTION_CANCEL = "subscription_cancel"
    SUBSCRIPTION_RENEW = "subscription_renew"
    BILLING_INFO_UPDATE = "billing_info_update"
    INVOICE_VIEW = "invoice_view"
    INVOICE_DOWNLOAD = "invoice_download"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    REFUND_REQUEST = "refund_request"
    
    # API & Integration Activities
    API_REQUEST = "api_request"
    API_AUTHENTICATION = "api_authentication"
    WEBHOOK_SETUP = "webhook_setup"
    WEBHOOK_TRIGGER = "webhook_trigger"
    THIRD_PARTY_INTEGRATION = "third_party_integration"
    EXTERNAL_LINK_CLICK = "external_link_click"
    MOBILE_APP_USAGE = "mobile_app_usage"
    DESKTOP_APP_USAGE = "desktop_app_usage"
    
    # Support & Help Activities
    SUPPORT_TICKET_CREATE = "support_ticket_create"
    SUPPORT_TICKET_UPDATE = "support_ticket_update"
    SUPPORT_TICKET_CLOSE = "support_ticket_close"
    HELP_ARTICLE_VIEW = "help_article_view"
    FAQ_VIEW = "faq_view"
    TUTORIAL_START = "tutorial_start"
    TUTORIAL_COMPLETE = "tutorial_complete"
    FEATURE_FEEDBACK = "feature_feedback"
    BUG_REPORT = "bug_report"
    
    # Admin & Moderation Activities
    CONTENT_MODERATE = "content_moderate"
    USER_MODERATE = "user_moderate"
    ADMIN_PANEL_ACCESS = "admin_panel_access"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    USER_IMPERSONATE = "user_impersonate"
    BULK_OPERATION = "bulk_operation"
    DATA_EXPORT_ADMIN = "data_export_admin"
    AUDIT_LOG_VIEW = "audit_log_view"
    
    # Creator Type Specific Activities
    MUSICIAN_STUDIO_ACCESS = "musician_studio_access"
    MUSICIAN_ALBUM_CREATE = "musician_album_create"
    MUSICIAN_TRACK_UPLOAD = "musician_track_upload"
    BLOGGER_POST_CREATE = "blogger_post_create"
    BLOGGER_CATEGORY_MANAGE = "blogger_category_manage"
    PHOTOGRAPHER_GALLERY_CREATE = "photographer_gallery_create"
    PHOTOGRAPHER_PORTFOLIO_UPDATE = "photographer_portfolio_update"
    INFLUENCER_CAMPAIGN_CREATE = "influencer_campaign_create"
    INFLUENCER_BRAND_PARTNERSHIP = "influencer_brand_partnership"
    COMEDIAN_SHOW_SCHEDULE = "comedian_show_schedule"
    COMEDIAN_JOKE_UPLOAD = "comedian_joke_upload"
    CONTENT_DOWNLOAD = "content_download"
    
    # Protection Activities
    FINGERPRINT_GENERATION = "fingerprint_generation"
    PROTECTION_ENABLE = "protection_enable"
    PROTECTION_DISABLE = "protection_disable"
    DMCA_REQUEST = "dmca_request"
    COPYRIGHT_CLAIM = "copyright_claim"
    
    # Collaboration Activities
    COLLABORATION_INVITE = "collaboration_invite"
    COLLABORATION_ACCEPT = "collaboration_accept"
    COLLABORATION_REJECT = "collaboration_reject"
    PROJECT_CREATE = "project_create"
    PROJECT_JOIN = "project_join"
    PROJECT_LEAVE = "project_leave"
    
    # Monetization Activities
    PAYMENT_SETUP = "payment_setup"
    REVENUE_CLAIM = "revenue_claim"
    SUBSCRIPTION_START = "subscription_start"
    SUBSCRIPTION_CANCEL = "subscription_cancel"
    PURCHASE_CONTENT = "purchase_content"
    
    # AI Activities
    AI_GENERATION = "ai_generation"
    AI_ENHANCEMENT = "ai_enhancement"
    AI_ANALYSIS = "ai_analysis"
    RECOMMENDATION_VIEW = "recommendation_view"
    
    # Platform Activities
    PROFILE_UPDATE = "profile_update"
    SETTINGS_CHANGE = "settings_change"
    SEARCH_QUERY = "search_query"
    PAGE_VIEW = "page_view"
    FEATURE_USE = "feature_use"
    
    # Social Activities
    FOLLOW_USER = "follow_user"
    UNFOLLOW_USER = "unfollow_user"
    LIKE_CONTENT = "like_content"
    COMMENT_POST = "comment_post"
    MESSAGE_SEND = "message_send"



class ActivityStatus(Enum):
    """Ultra-comprehensive activity status types with detailed granularity."""    
    # Success States
    SUCCESS = "success"
    SUCCESS_WITH_WARNINGS = "success_with_warnings"
    PARTIAL_SUCCESS = "partial_success"
    COMPLETED = "completed"
    APPROVED = "approved"
    VERIFIED = "verified"
    
    # Failure States
    FAILED = "failed"
    FAILED_VALIDATION = "failed_validation"
    FAILED_AUTHENTICATION = "failed_authentication"
    FAILED_AUTHORIZATION = "failed_authorization"
    FAILED_NETWORK = "failed_network"
    FAILED_TIMEOUT = "failed_timeout"
    FAILED_QUOTA_EXCEEDED = "failed_quota_exceeded"
    FAILED_MALFORMED_REQUEST = "failed_malformed_request"
    
    # Pending States
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"
    PENDING_VERIFICATION = "pending_verification"
    PENDING_PAYMENT = "pending_payment"
    PENDING_REVIEW = "pending_review"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    
    # Processing States
    IN_PROGRESS = "in_progress"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    CONVERTING = "converting"
    OPTIMIZING = "optimizing"
    
    # Cancelled/Aborted States
    CANCELLED = "cancelled"
    CANCELLED_BY_USER = "cancelled_by_user"
    CANCELLED_BY_SYSTEM = "cancelled_by_system"
    ABORTED = "aborted"
    INTERRUPTED = "interrupted"
    EXPIRED = "expired"
    
    # Error States
    ERROR = "error"
    ERROR_RECOVERABLE = "error_recoverable"
    ERROR_FATAL = "error_fatal"
    ERROR_SYSTEM = "error_system"
    ERROR_USER = "error_user"
    
    # Special States
    SKIPPED = "skipped"
    IGNORED = "ignored"
    DUPLICATE = "duplicate"
    BLOCKED = "blocked"
    SUSPENDED = "suspended"
    RESTRICTED = "restricted"


class DeviceType(Enum):
    """Ultra-detailed device types for comprehensive user activity tracking."""    
    # Desktop Devices
    DESKTOP_WINDOWS = "desktop_windows"
    DESKTOP_MACOS = "desktop_macos"
    DESKTOP_LINUX = "desktop_linux"
    DESKTOP_CHROMEOS = "desktop_chromeos"
    DESKTOP_UNKNOWN = "desktop_unknown"
    
    # Mobile Devices
    MOBILE_ANDROID = "mobile_android"
    MOBILE_IOS = "mobile_ios"
    MOBILE_WINDOWS = "mobile_windows"
    MOBILE_UNKNOWN = "mobile_unknown"
    
    # Tablet Devices
    TABLET_ANDROID = "tablet_android"
    TABLET_IOS = "tablet_ios"
    TABLET_WINDOWS = "tablet_windows"
    TABLET_UNKNOWN = "tablet_unknown"
    
    # Web Browsers
    WEB_CHROME = "web_chrome"
    WEB_FIREFOX = "web_firefox"
    WEB_SAFARI = "web_safari"
    WEB_EDGE = "web_edge"
    WEB_OPERA = "web_opera"
    WEB_INTERNET_EXPLORER = "web_internet_explorer"
    WEB_OTHER = "web_other"
    
    # Smart Devices
    SMART_TV = "smart_tv"
    SMART_WATCH = "smart_watch"
    SMART_SPEAKER = "smart_speaker"
    GAMING_CONSOLE = "gaming_console"
    
    # Development & API
    API_CLIENT = "api_client"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    CLI_TOOL = "cli_tool"
    WEBHOOK = "webhook"
    BOT = "bot"
    AUTOMATED_SYSTEM = "automated_system"
    
    # Unknown/Other
    UNKNOWN = "unknown"
    OTHER = "other"


class ActivityPriority(IntEnum):
    """Activity priority levels for user actions."""    
    CRITICAL = 1      # Critical business actions (payments, security)
    HIGH = 2          # High priority (content creation, collaboration)
    MEDIUM = 3        # Medium priority (general interactions)
    LOW = 4           # Low priority (browsing, viewing)
    BACKGROUND = 5    # Background activities (analytics, sync)


class ContentType(Enum):
    """Content types for IA Influencer platform (Business Logic)."""    
    # Audio Content
    AUDIO_MUSIC = "audio_music"
    AUDIO_PODCAST = "audio_podcast"
    AUDIO_VOICE_OVER = "audio_voice_over"
    AUDIO_SOUND_EFFECT = "audio_sound_effect"
    AUDIO_RECORDING = "audio_recording"
    
    # Video Content
    VIDEO_MOVIE = "video_movie"
    VIDEO_SHORT = "video_short"
    VIDEO_TUTORIAL = "video_tutorial"
    VIDEO_VLOG = "video_vlog"
    VIDEO_LIVE_STREAM = "video_live_stream"
    VIDEO_ANIMATION = "video_animation"
    
    # Image Content
    IMAGE_PHOTO = "image_photo"
    IMAGE_ARTWORK = "image_artwork"
    IMAGE_DESIGN = "image_design"
    IMAGE_MEME = "image_meme"
    IMAGE_INFOGRAPHIC = "image_infographic"
    IMAGE_SCREENSHOT = "image_screenshot"
    
    # Text Content
    TEXT_BLOG_POST = "text_blog_post"
    TEXT_ARTICLE = "text_article"
    TEXT_STORY = "text_story"
    TEXT_POEM = "text_poem"
    TEXT_SCRIPT = "text_script"
    TEXT_CAPTION = "text_caption"
    
    # Interactive Content
    INTERACTIVE_GAME = "interactive_game"
    INTERACTIVE_QUIZ = "interactive_quiz"
    INTERACTIVE_POLL = "interactive_poll"
    
    # Mixed Media
    MIXED_PRESENTATION = "mixed_presentation"
    MIXED_COURSE = "mixed_course"
    MIXED_PORTFOLIO = "mixed_portfolio"


class CreatorType(Enum):
    """Creator types for IA Influencer platform (Business Logic)."""    
    # Main Creator Categories
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    
    # Sub-categories for Musicians
    MUSICIAN_SINGER = "musician_singer"
    MUSICIAN_RAPPER = "musician_rapper"
    MUSICIAN_PRODUCER = "musician_producer"
    MUSICIAN_DJ = "musician_dj"
    MUSICIAN_COMPOSER = "musician_composer"
    MUSICIAN_INSTRUMENTALIST = "musician_instrumentalist"
    
    # Sub-categories for Bloggers
    BLOGGER_LIFESTYLE = "blogger_lifestyle"
    BLOGGER_TECH = "blogger_tech"
    BLOGGER_TRAVEL = "blogger_travel"
    BLOGGER_FOOD = "blogger_food"
    BLOGGER_FASHION = "blogger_fashion"
    BLOGGER_FITNESS = "blogger_fitness"
    
    # Sub-categories for Photographers
    PHOTOGRAPHER_PORTRAIT = "photographer_portrait"
    PHOTOGRAPHER_LANDSCAPE = "photographer_landscape"
    PHOTOGRAPHER_WEDDING = "photographer_wedding"
    PHOTOGRAPHER_EVENT = "photographer_event"
    PHOTOGRAPHER_COMMERCIAL = "photographer_commercial"
    PHOTOGRAPHER_ARTISTIC = "photographer_artistic"
    
    # Sub-categories for Influencers
    INFLUENCER_LIFESTYLE = "influencer_lifestyle"
    INFLUENCER_BEAUTY = "influencer_beauty"
    INFLUENCER_FITNESS = "influencer_fitness"
    INFLUENCER_GAMING = "influencer_gaming"
    INFLUENCER_BUSINESS = "influencer_business"
    INFLUENCER_EDUCATION = "influencer_education"
    
    # Sub-categories for Comedians
    COMEDIAN_STANDUP = "comedian_standup"
    COMEDIAN_SKETCH = "comedian_sketch"
    COMEDIAN_IMPROV = "comedian_improv"
    COMEDIAN_WRITER = "comedian_writer"
    
    # Multi-discipline
    MULTI_CREATOR = "multi_creator"
    CONTENT_CREATOR = "content_creator"
    ARTIST = "artist"
    ENTERTAINER = "entertainer"


class GeographicRegion(Enum):
    """Geographic regions for compliance and analytics."""    
    # Major Regions
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EUROPE = "europe"
    ASIA = "asia"
    AFRICA = "africa"
    OCEANIA = "oceania"
    
    # Regulatory Zones
    GDPR_REGION = "gdpr_region"  # EU + UK + Switzerland
    CCPA_REGION = "ccpa_region"  # California
    LGPD_REGION = "lgpd_region"  # Brazil
    
    # Major Markets
    USA = "usa"
    CANADA = "canada"
    UNITED_KINGDOM = "united_kingdom"
    GERMANY = "germany"
    FRANCE = "france"
    JAPAN = "japan"
    CHINA = "china"
    INDIA = "india"
    BRAZIL = "brazil"
    AUSTRALIA = "australia"
    
    UNKNOWN = "unknown"


@dataclass
class UserContext:
    """Ultra-comprehensive context information for user activities."""    
    # Core User Information
    user_id: str
    user_email: str
    user_username: Optional[str] = None
    user_role: str = "user"
    user_type: Optional[CreatorType] = None
    account_status: str = "active"
    subscription_tier: str = "free"
    
    # Session Information
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_duration_seconds: Optional[int] = None
    previous_session_id: Optional[str] = None
    
    # Network & Location
    ip_address: str = "0.0.0.0"
    user_agent: str = ""
    device_type: DeviceType = DeviceType.UNKNOWN
    device_id: Optional[str] = None
    device_fingerprint: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    operating_system: Optional[str] = None
    screen_resolution: Optional[str] = None
    
    # Geographic Information
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    geographic_region: GeographicRegion = GeographicRegion.UNKNOWN
    
    # Business Context
    tenant_id: Optional[str] = None
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    collaboration_id: Optional[str] = None
    
    # Content Context
    content_id: Optional[str] = None
    content_type: Optional[ContentType] = None
    content_category: Optional[str] = None
    content_format: Optional[str] = None
    content_size_bytes: Optional[int] = None
    
    # Feature & Experiment Context
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    experiment_variants: Dict[str, str] = field(default_factory=dict)
    ab_test_groups: List[str] = field(default_factory=list)
    
    # Security Context
    authentication_method: str = "password"
    two_factor_enabled: bool = False
    security_clearance: str = "standard"
    risk_score: float = 0.0
    threat_indicators: List[str] = field(default_factory=list)
    
    # Performance Context
    network_speed: Optional[str] = None  # "fast", "slow", "offline"
    connection_type: Optional[str] = None  # "wifi", "cellular", "ethernet"
    page_load_time_ms: Optional[int] = None
    api_response_time_ms: Optional[int] = None
    
    # Marketing & Attribution
    referrer_url: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None
    
    # Compliance & Privacy
    privacy_consent: bool = False
    marketing_consent: bool = False
    analytics_consent: bool = False
    data_processing_purpose: Optional[str] = None
    legal_basis: str = "legitimate_interest"
    
    # Additional Metadata
    tags: Dict[str, str] = field(default_factory=dict)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""        result = asdict(self)
        # Handle datetime serialization
        if isinstance(result.get('session_start_time'), datetime):
            result['session_start_time'] = result['session_start_time'].isoformat()
        return result
    
    def get_device_info(self) -> Dict[str, Any]:
        """Extract device information from user agent."""        if not self.user_agent:
            return {}
        
        try:
            parsed_ua = user_agents.parse(self.user_agent)
            return {
                "browser": f"{parsed_ua.browser.family} {parsed_ua.browser.version_string}",
                "os": f"{parsed_ua.os.family} {parsed_ua.os.version_string}",
                "device": parsed_ua.device.family,
                "is_mobile": parsed_ua.is_mobile,
                "is_tablet": parsed_ua.is_tablet,
                "is_pc": parsed_ua.is_pc,
                "is_bot": parsed_ua.is_bot
            }
        except Exception:
            return {"error": "Failed to parse user agent"}
    
    def get_geographic_info(self) -> Dict[str, Any]:
        """Get geographic information from IP address."""        if not self.ip_address or self.ip_address == "0.0.0.0":
            return {}
        
        try:
            # This would use a GeoIP database in production
            # For now, return basic info based on IP patterns
            if self.ip_address.startswith(("10.", "192.168.", "172.")):
                return {"type": "private", "location": "internal"}
            return {"type": "public", "location": "external"}
        except Exception:
            return {"error": "Failed to get geographic info"}
    
    def calculate_risk_score(self) -> float:
        """Calculate user risk score based on context."""        risk_score = 0.0
        
        # IP-based risk
        if self.ip_address.startswith(("10.", "192.168.")):
            risk_score += 0.1  # Internal network, lower risk
        else:
            risk_score += 0.3  # External network, higher risk
        
        # Device-based risk
        if self.device_type in [DeviceType.API_CLIENT, DeviceType.BOT]:
            risk_score += 0.4  # Automated access, higher risk
        
        # Authentication-based risk
        if not self.two_factor_enabled:
            risk_score += 0.2  # No 2FA, higher risk
        
        # Session-based risk
        if self.session_duration_seconds and self.session_duration_seconds > 86400:  # 24 hours
            risk_score += 0.1  # Very long session, slight risk increase
        
        self.risk_score = min(1.0, risk_score)
        return self.risk_score
    
    @classmethod
    def create_from_request(cls, user_id: str, user_email: str, ip_address: str, 
                           user_agent: str, **kwargs) -> 'UserContext':
        """Create context from HTTP request information."""        context = cls(
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            **kwargs
        )
        
        # Auto-detect device type from user agent
        device_info = context.get_device_info()
        if device_info.get("is_mobile"):
            context.device_type = DeviceType.MOBILE_UNKNOWN
        elif device_info.get("is_tablet"):
            context.device_type = DeviceType.TABLET_UNKNOWN
        elif device_info.get("is_pc"):
            context.device_type = DeviceType.DESKTOP_UNKNOWN
        elif device_info.get("is_bot"):
            context.device_type = DeviceType.BOT
        
        # Calculate initial risk score
        context.calculate_risk_score()
        
        return context
    user_agent: str
    device_type: DeviceType
    location: Optional[Dict[str, str]]
    referrer: Optional[str]
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]


class UserActivityLog(Base):
    """User activity log model."""    
    __tablename__ = "user_activity_logs"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_id = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(100), nullable=False, index=True)
    activity_name = Column(String(255), nullable=False)
    activity_description = Column(Text)
    status = Column(String(50), nullable=False, index=True)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    duration_ms = Column(Integer)  # Activity duration in milliseconds
    
    # User context
    user_email = Column(String(255), index=True)
    user_role = Column(String(100))
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    device_type = Column(String(50))
    
    # Location and tracking
    country = Column(String(2))  # ISO country code
    region = Column(String(100))
    city = Column(String(100))
    timezone_offset = Column(Integer)  # Minutes offset from UTC
    
    # Marketing attribution
    referrer = Column(String(500))
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    utm_term = Column(String(100))
    utm_content = Column(String(100))
    
    # Content context
    content_id = Column(UUID(as_uuid=True), index=True)
    content_type = Column(String(100))
    content_title = Column(String(500))
    content_size_bytes = Column(Integer)
    
    # Platform context
    platform = Column(String(100))  # web, mobile_app, api
    app_version = Column(String(50))
    api_version = Column(String(50))
    endpoint = Column(String(255))
    method = Column(String(10))  # HTTP method
    
    # Performance metrics
    response_time_ms = Column(Integer)
    cpu_usage_percent = Column(Float)
    memory_usage_mb = Column(Float)
    bandwidth_used_kb = Column(Integer)
    
    # Activity data
    before_state = Column(JSON)
    after_state = Column(JSON)
    activity_data = Column(JSON)
    metadata = Column(JSON)
    
    # Error handling
    error_code = Column(String(100))
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Privacy and compliance
    is_anonymized = Column(Boolean, default=False)
    anonymized_at = Column(DateTime(timezone=True))
    retention_until = Column(DateTime(timezone=True))
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_activity_type_timestamp', 'user_id', 'activity_type', 'timestamp'),
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_content_activity', 'content_id', 'activity_type'),
        Index('idx_status_timestamp', 'status', 'timestamp'),
        Index('idx_ip_timestamp', 'ip_address', 'timestamp'),
    )
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary."""        result = {
            "id": str(self.id),
            "activity_id": self.activity_id,
            "user_id": str(self.user_id),
            "session_id": self.session_id,
            "activity_type": self.activity_type,
            "activity_name": self.activity_name,
            "activity_description": self.activity_description,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "duration_ms": self.duration_ms,
            "user_role": self.user_role,
            "device_type": self.device_type,
            "country": self.country,
            "region": self.region,
            "city": self.city,
            "timezone_offset": self.timezone_offset,
            "referrer": self.referrer,
            "utm_source": self.utm_source,
            "utm_medium": self.utm_medium,
            "utm_campaign": self.utm_campaign,
            "utm_term": self.utm_term,
            "utm_content": self.utm_content,
            "content_id": str(self.content_id) if self.content_id else None,
            "content_type": self.content_type,
            "content_title": self.content_title,
            "content_size_bytes": self.content_size_bytes,
            "platform": self.platform,
            "app_version": self.app_version,
            "api_version": self.api_version,
            "endpoint": self.endpoint,
            "method": self.method,
            "response_time_ms": self.response_time_ms,
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "bandwidth_used_kb": self.bandwidth_used_kb,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "activity_data": self.activity_data,
            "metadata": self.metadata,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "is_anonymized": self.is_anonymized,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include sensitive data only if explicitly requested
        if include_sensitive:
            result.update({
                "user_email": self.user_email,
                "ip_address": self.ip_address,
                "user_agent": self.user_agent
            })
        
        return result


class UserActivityLogger:
    """Enterprise user activity logger."""    
    def __init__(self, db_session, service_name: str = "ia_influencer_agent"):
        """        Initialize user activity logger.
        
        Args:
            db_session: Database session
            service_name: Name of the service
        """        self.db_session = db_session
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
    
    def log_activity(
        self,
        user_context: UserContext,
        activity_type: UserActivityType,
        activity_name: str,
        status: ActivityStatus = ActivityStatus.SUCCESS,
        description: Optional[str] = None,
        content_id: Optional[str] = None,
        content_type: Optional[str] = None,
        content_title: Optional[str] = None,
        content_size_bytes: Optional[int] = None,
        platform: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        duration_ms: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        activity_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Log a user activity.
        
        Args:
            user_context: User context information
            activity_type: Type of activity
            activity_name: Name of the activity
            status: Activity status
            description: Activity description
            content_id: ID of content involved
            content_type: Type of content
            content_title: Title of content
            content_size_bytes: Size of content in bytes
            platform: Platform used
            endpoint: API endpoint if applicable
            method: HTTP method if applicable
            duration_ms: Activity duration
            response_time_ms: Response time
            before_state: State before activity
            after_state: State after activity
            activity_data: Additional activity data
            metadata: Additional metadata
            error_code: Error code if failed
            error_message: Error message if failed
            error_details: Error details if failed
            
        Returns:
            str: Generated activity ID
        """        try:
            activity_id = f"act_{uuid.uuid4().hex[:16]}"
            
            # Parse location from user context
            location = user_context.location or {}
            
            activity_log = UserActivityLog(
                activity_id=activity_id,
                user_id=user_context.user_id,
                session_id=user_context.session_id,
                activity_type=activity_type.value,
                activity_name=activity_name,
                activity_description=description,
                status=status.value,
                user_email=user_context.user_email,
                user_role=user_context.user_role,
                ip_address=user_context.ip_address,
                user_agent=user_context.user_agent,
                device_type=user_context.device_type.value,
                country=location.get('country'),
                region=location.get('region'),
                city=location.get('city'),
                timezone_offset=location.get('timezone_offset'),
                referrer=user_context.referrer,
                utm_source=user_context.utm_source,
                utm_medium=user_context.utm_medium,
                utm_campaign=user_context.utm_campaign,
                content_id=content_id,
                content_type=content_type,
                content_title=content_title,
                content_size_bytes=content_size_bytes,
                platform=platform,
                endpoint=endpoint,
                method=method,
                duration_ms=duration_ms,
                response_time_ms=response_time_ms,
                before_state=before_state,
                after_state=after_state,
                activity_data=activity_data,
                metadata=metadata,
                error_code=error_code,
                error_message=error_message,
                error_details=error_details
            )
            
            # Set retention period (default 2 years for user activities)
            activity_log.retention_until = datetime.now(timezone.utc) + timedelta(days=730)
            
            self.db_session.add(activity_log)
            self.db_session.commit()
            
            # Log to application logger
            log_message = f"User Activity: {activity_name} ({activity_type.value}) - Status: {status.value}"
            if status == ActivityStatus.FAILED:
                self.logger.error(log_message, extra={
                    "activity_id": activity_id,
                    "user_id": user_context.user_id,
                    "error_code": error_code
                })
            else:
                self.logger.info(log_message, extra={
                    "activity_id": activity_id,
                    "user_id": user_context.user_id
                })
            
            return activity_id
            
        except Exception as e:
            self.logger.error(f"Failed to log user activity: {str(e)}")
            self.db_session.rollback()
            raise
    
    def log_login(self, user_context: UserContext, success: bool = True, failure_reason: Optional[str] = None) -> str:
        """Log user login activity."""        status = ActivityStatus.SUCCESS if success else ActivityStatus.FAILED
        return self.log_activity(
            user_context=user_context,
            activity_type=UserActivityType.LOGIN,
            activity_name="User Login",
            status=status,
            description="User login attempt",
            error_message=failure_reason if not success else None,
            activity_data={
                "login_method": "email_password",  # Could be expanded
                "remember_me": False,  # Could be passed as parameter
                "login_time": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def log_logout(self, user_context: UserContext, session_duration_ms: Optional[int] = None) -> str:
        """Log user logout activity."""        return self.log_activity(
            user_context=user_context,
            activity_type=UserActivityType.LOGOUT,
            activity_name="User Logout",
            description="User logged out",
            duration_ms=session_duration_ms,
            activity_data={
                "logout_time": datetime.now(timezone.utc).isoformat(),
                "session_duration_ms": session_duration_ms
            }
        )
    
    def log_content_upload(
        self,
        user_context: UserContext,
        content_id: str,
        content_type: str,
        content_title: str,
        content_size_bytes: int,
        upload_duration_ms: int,
        success: bool = True,
        error_details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log content upload activity."""        status = ActivityStatus.SUCCESS if success else ActivityStatus.FAILED
        return self.log_activity(
            user_context=user_context,
            activity_type=UserActivityType.CONTENT_UPLOAD,
            activity_name="Content Upload",
            status=status,
            description=f"Uploaded {content_type} content: {content_title}",
            content_id=content_id,
            content_type=content_type,
            content_title=content_title,
            content_size_bytes=content_size_bytes,
            duration_ms=upload_duration_ms,
            error_details=error_details,
            activity_data={
                "upload_time": datetime.now(timezone.utc).isoformat(),
                "file_size_mb": round(content_size_bytes / (1024 * 1024), 2),
                "upload_speed_mbps": round((content_size_bytes / (1024 * 1024)) / (upload_duration_ms / 1000), 2) if upload_duration_ms > 0 else 0
            }
        )
    
    def log_ai_generation(
        self,
        user_context: UserContext,
        ai_model: str,
        generation_type: str,
        prompt: str,
        generation_time_ms: int,
        tokens_used: int,
        success: bool = True,
        result_content_id: Optional[str] = None
    ) -> str:
        """Log AI content generation activity."""        status = ActivityStatus.SUCCESS if success else ActivityStatus.FAILED
        return self.log_activity(
            user_context=user_context,
            activity_type=UserActivityType.AI_GENERATION,
            activity_name="AI Content Generation",
            status=status,
            description=f"Generated {generation_type} content using {ai_model}",
            content_id=result_content_id,
            content_type=generation_type,
            duration_ms=generation_time_ms,
            activity_data={
                "ai_model": ai_model,
                "generation_type": generation_type,
                "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],  # Hash for privacy
                "prompt_length": len(prompt),
                "tokens_used": tokens_used,
                "generation_time_ms": generation_time_ms,
                "tokens_per_second": round(tokens_used / (generation_time_ms / 1000), 2) if generation_time_ms > 0 else 0
            }
        )
    
    def log_search_query(
        self,
        user_context: UserContext,
        query: str,
        search_type: str,
        results_count: int,
        search_time_ms: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log search query activity."""        return self.log_activity(
            user_context=user_context,
            activity_type=UserActivityType.SEARCH_QUERY,
            activity_name="Search Query",
            description=f"Performed {search_type} search",
            duration_ms=search_time_ms,
            activity_data={
                "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16],  # Hash for privacy
                "query_length": len(query),
                "search_type": search_type,
                "results_count": results_count,
                "search_time_ms": search_time_ms,
                "filters": filters or {},
                "search_timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def log_collaboration_invite(
        self,
        user_context: UserContext,
        project_id: str,
        invited_user_id: str,
        collaboration_type: str,
        message: Optional[str] = None
    ) -> str:
        """Log collaboration invitation activity."""        return self.log_activity(
            user_context=user_context,
            activity_type=UserActivityType.COLLABORATION_INVITE,
            activity_name="Collaboration Invite",
            description=f"Invited user to {collaboration_type} collaboration",
            activity_data={
                "project_id": project_id,
                "invited_user_id": invited_user_id,
                "collaboration_type": collaboration_type,
                "has_message": bool(message),
                "message_length": len(message) if message else 0,
                "invite_time": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def get_user_activity_summary(
        self,
        user_id: str,
        days: int = 30,
        activity_types: Optional[List[UserActivityType]] = None
    ) -> Dict[str, Any]:
        """        Get user activity summary.
        
        Args:
            user_id: User ID to analyze
            days: Number of days to look back
            activity_types: Specific activity types to include
            
        Returns:
            Dict[str, Any]: Activity summary
        """        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            query = self.db_session.query(UserActivityLog).filter(
                UserActivityLog.user_id == user_id,
                UserActivityLog.timestamp >= start_date
            )
            
            if activity_types:
                activity_type_values = [at.value for at in activity_types]
                query = query.filter(UserActivityLog.activity_type.in_(activity_type_values))
            
            activities = query.all()
            
            # Calculate summary statistics
            total_activities = len(activities)
            activity_type_counts = {}
            status_counts = {}
            device_type_counts = {}
            daily_activity = {}
            
            for activity in activities:
                # Count by type
                activity_type_counts[activity.activity_type] = activity_type_counts.get(activity.activity_type, 0) + 1
                
                # Count by status
                status_counts[activity.status] = status_counts.get(activity.status, 0) + 1
                
                # Count by device
                if activity.device_type:
                    device_type_counts[activity.device_type] = device_type_counts.get(activity.device_type, 0) + 1
                
                # Count by day
                day_key = activity.timestamp.date().isoformat()
                daily_activity[day_key] = daily_activity.get(day_key, 0) + 1
            
            # Calculate average daily activity
            avg_daily_activity = total_activities / days if days > 0 else 0
            
            # Find most active day
            most_active_day = max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else None
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_activities": total_activities,
                "average_daily_activities": round(avg_daily_activity, 2),
                "activity_type_breakdown": activity_type_counts,
                "status_breakdown": status_counts,
                "device_breakdown": device_type_counts,
                "daily_activity": daily_activity,
                "most_active_day": {
                    "date": most_active_day[0] if most_active_day else None,
                    "count": most_active_day[1] if most_active_day else 0
                },
                "summary_generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user activity summary: {str(e)}")
            return {"error": str(e)}
    
    def anonymize_user_data(self, user_id: str, retention_days: int = 0) -> int:
        """        Anonymize user activity data for GDPR compliance.
        
        Args:
            user_id: User ID to anonymize
            retention_days: Days to retain before anonymization (0 = immediate)
            
        Returns:
            int: Number of records anonymized
        """        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
            
            activities = self.db_session.query(UserActivityLog).filter(
                UserActivityLog.user_id == user_id,
                UserActivityLog.timestamp <= cutoff_date,
                UserActivityLog.is_anonymized == False
            ).all()
            
            anonymized_count = 0
            for activity in activities:
                # Anonymize personally identifiable information
                activity.user_email = "anonymized@example.com"
                activity.ip_address = "0.0.0.0"
                activity.user_agent = "anonymized"
                
                # Keep only essential non-personal data
                if activity.activity_data:
                    # Remove potentially sensitive data from activity_data
                    sanitized_data = {}
                    safe_keys = ['generation_type', 'search_type', 'collaboration_type', 'content_type']
                    for key in safe_keys:
                        if key in activity.activity_data:
                            sanitized_data[key] = activity.activity_data[key]
                    activity.activity_data = sanitized_data
                
                activity.is_anonymized = True
                activity.anonymized_at = datetime.now(timezone.utc)
                anonymized_count += 1
            
            self.db_session.commit()
            
            self.logger.info(f"Anonymized {anonymized_count} activity records for user {user_id}")
            return anonymized_count
            
        except Exception as e:
            self.logger.error(f"Failed to anonymize user data: {str(e)}")
            self.db_session.rollback()
            return 0
    
    def cleanup_old_activities(self, days_to_keep: int = 730) -> int:
        """        Clean up old activity logs based on retention policy.
        
        Args:
            days_to_keep: Number of days to keep (default 2 years)
            
        Returns:
            int: Number of records deleted
        """        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            
            deleted_count = self.db_session.query(UserActivityLog).filter(
                UserActivityLog.timestamp <= cutoff_date
            ).delete()
            
            self.db_session.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} old activity records")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old activities: {str(e)}")
            self.db_session.rollback()
            return 0


def create_user_activity_logger(db_session, service_name: str = "ia_influencer_agent") -> UserActivityLogger:
    """    Factory function to create user activity logger.
    
    Args:
        db_session: Database session
        service_name: Name of the service
        
    Returns:
        UserActivityLogger: Configured user activity logger
    """    return UserActivityLogger(db_session, service_name)


# Export main classes and functions
__all__ = [
    "UserActivityLog",
    "UserActivityLogger",
    "UserActivityType",
    "ActivityStatus",
    "DeviceType",
    "UserContext",
    "create_user_activity_logger"
]
