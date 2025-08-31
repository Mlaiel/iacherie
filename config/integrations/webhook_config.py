"""Webhook Configuration Module for IA-Influencer Agent Platform
=============================================================

Professional webhook configuration for real-time notifications and events.
Handles platform integrations, content protection alerts, and payment notifications.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission
is strictly prohibited and will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""import os
from typing import Dict, Any, Optional, List, Union, Callable
from pydantic import BaseSettings, Field, validator, HttpUrl
from enum import Enum
from dataclasses import dataclass
import hashlib
import hmac
import json


class WebhookProvider(str, Enum):
    """Supported webhook providers."""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    
    # Payment webhooks
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    
    # Content protection webhooks
    CONTENT_ID = "content_id"
    SHAZAM = "shazam"
    AUDIBLE_MAGIC = "audible_magic"
    
    # System webhooks
    GITHUB = "github"
    MONITORING = "monitoring"
    SECURITY = "security"


class WebhookEvent(str, Enum):
    """Supported webhook event types."""    # Content events
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_MATCHED = "content.matched"
    CONTENT_CLAIMED = "content.claimed"
    CONTENT_DISPUTED = "content.disputed"
    
    # User events
    USER_REGISTERED = "user.registered"
    USER_VERIFIED = "user.verified"
    USER_SUBSCRIPTION_CHANGED = "user.subscription.changed"
    
    # Platform events
    SPOTIFY_TRACK_ADDED = "spotify.track.added"
    YOUTUBE_VIDEO_UPLOADED = "youtube.video.uploaded"
    INSTAGRAM_MEDIA_POSTED = "instagram.media.posted"
    TIKTOK_VIDEO_PUBLISHED = "tiktok.video.published"
    
    # Payment events
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    INVOICE_CREATED = "invoice.created"
    
    # Protection events
    FINGERPRINT_MATCH = "fingerprint.match"
    COPYRIGHT_VIOLATION = "copyright.violation"
    TAKEDOWN_REQUEST = "takedown.request"
    REVENUE_DETECTED = "revenue.detected"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SECURITY_ALERT = "security.alert"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"


@dataclass
class WebhookSecurity:
    """Webhook security configuration."""    secret_key: str
    verify_signature: bool = True
    signature_header: str = "X-Webhook-Signature"
    timestamp_header: str = "X-Webhook-Timestamp"
    timestamp_tolerance: int = 300  # 5 minutes
    allowed_ips: Optional[List[str]] = None


@dataclass
class WebhookRetry:
    """Webhook retry configuration."""    max_attempts: int = 5
    initial_delay: float = 1.0
    max_delay: float = 300.0
    backoff_factor: float = 2.0
    timeout_seconds: float = 30.0


class WebhookConfig(BaseSettings):
    """Webhook configuration for external service integrations."""    
    # Base webhook settings
    webhook_base_url: HttpUrl = Field(..., env="WEBHOOK_BASE_URL")
    webhook_secret_key: str = Field(..., env="WEBHOOK_SECRET_KEY")
    webhook_verify_ssl: bool = Field(default=True, env="WEBHOOK_VERIFY_SSL")
    
    # Spotify webhooks
    spotify_webhook_enabled: bool = Field(default=True, env="SPOTIFY_WEBHOOK_ENABLED")
    spotify_webhook_endpoint: str = Field(default="/webhooks/spotify", env="SPOTIFY_WEBHOOK_ENDPOINT")
    spotify_webhook_secret: str = Field(..., env="SPOTIFY_WEBHOOK_SECRET")
    spotify_webhook_events: List[str] = Field(
        default_factory=lambda: ["user.subscription", "user.track.saved"],
        env="SPOTIFY_WEBHOOK_EVENTS"
    )
    
    # YouTube webhooks
    youtube_webhook_enabled: bool = Field(default=True, env="YOUTUBE_WEBHOOK_ENABLED")
    youtube_webhook_endpoint: str = Field(default="/webhooks/youtube", env="YOUTUBE_WEBHOOK_ENDPOINT")
    youtube_webhook_secret: str = Field(..., env="YOUTUBE_WEBHOOK_SECRET")
    youtube_webhook_verify_token: str = Field(..., env="YOUTUBE_WEBHOOK_VERIFY_TOKEN")
    youtube_webhook_events: List[str] = Field(
        default_factory=lambda: ["video.upload", "channel.update"],
        env="YOUTUBE_WEBHOOK_EVENTS"
    )
    
    # Instagram webhooks
    instagram_webhook_enabled: bool = Field(default=True, env="INSTAGRAM_WEBHOOK_ENABLED")
    instagram_webhook_endpoint: str = Field(default="/webhooks/instagram", env="INSTAGRAM_WEBHOOK_ENDPOINT")
    instagram_webhook_secret: str = Field(..., env="INSTAGRAM_WEBHOOK_SECRET")
    instagram_webhook_verify_token: str = Field(..., env="INSTAGRAM_WEBHOOK_VERIFY_TOKEN")
    instagram_webhook_events: List[str] = Field(
        default_factory=lambda: ["feed", "story"],
        env="INSTAGRAM_WEBHOOK_EVENTS"
    )
    
    # TikTok webhooks
    tiktok_webhook_enabled: bool = Field(default=True, env="TIKTOK_WEBHOOK_ENABLED")
    tiktok_webhook_endpoint: str = Field(default="/webhooks/tiktok", env="TIKTOK_WEBHOOK_ENDPOINT")
    tiktok_webhook_secret: str = Field(..., env="TIKTOK_WEBHOOK_SECRET")
    tiktok_webhook_events: List[str] = Field(
        default_factory=lambda: ["video.create", "video.delete"],
        env="TIKTOK_WEBHOOK_EVENTS"
    )
    
    # Twitter webhooks
    twitter_webhook_enabled: bool = Field(default=True, env="TWITTER_WEBHOOK_ENABLED")
    twitter_webhook_endpoint: str = Field(default="/webhooks/twitter", env="TWITTER_WEBHOOK_ENDPOINT")
    twitter_webhook_secret: str = Field(..., env="TWITTER_WEBHOOK_SECRET")
    twitter_webhook_events: List[str] = Field(
        default_factory=lambda: ["tweet.create", "user.follow"],
        env="TWITTER_WEBHOOK_EVENTS"
    )
    
    # Stripe webhooks
    stripe_webhook_enabled: bool = Field(default=True, env="STRIPE_WEBHOOK_ENABLED")
    stripe_webhook_endpoint: str = Field(default="/webhooks/stripe", env="STRIPE_WEBHOOK_ENDPOINT")
    stripe_webhook_secret: str = Field(..., env="STRIPE_WEBHOOK_SECRET")
    stripe_webhook_events: List[str] = Field(
        default_factory=lambda: [
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
            "customer.subscription.created",
            "customer.subscription.deleted",
            "invoice.payment_succeeded"
        ],
        env="STRIPE_WEBHOOK_EVENTS"
    )
    
    # PayPal webhooks
    paypal_webhook_enabled: bool = Field(default=True, env="PAYPAL_WEBHOOK_ENABLED")
    paypal_webhook_endpoint: str = Field(default="/webhooks/paypal", env="PAYPAL_WEBHOOK_ENDPOINT")
    paypal_webhook_id: str = Field(..., env="PAYPAL_WEBHOOK_ID")
    paypal_webhook_events: List[str] = Field(
        default_factory=lambda: [
            "PAYMENT.CAPTURE.COMPLETED",
            "PAYMENT.CAPTURE.DENIED",
            "BILLING.SUBSCRIPTION.CREATED",
            "BILLING.SUBSCRIPTION.CANCELLED"
        ],
        env="PAYPAL_WEBHOOK_EVENTS"
    )
    
    # Content protection webhooks
    content_id_webhook_enabled: bool = Field(default=True, env="CONTENT_ID_WEBHOOK_ENABLED")
    content_id_webhook_endpoint: str = Field(default="/webhooks/content-id", env="CONTENT_ID_WEBHOOK_ENDPOINT")
    content_id_webhook_secret: str = Field(..., env="CONTENT_ID_WEBHOOK_SECRET")
    
    shazam_webhook_enabled: bool = Field(default=True, env="SHAZAM_WEBHOOK_ENABLED")
    shazam_webhook_endpoint: str = Field(default="/webhooks/shazam", env="SHAZAM_WEBHOOK_ENDPOINT")
    shazam_webhook_secret: str = Field(..., env="SHAZAM_WEBHOOK_SECRET")
    
    # System webhooks
    github_webhook_enabled: bool = Field(default=True, env="GITHUB_WEBHOOK_ENABLED")
    github_webhook_endpoint: str = Field(default="/webhooks/github", env="GITHUB_WEBHOOK_ENDPOINT")
    github_webhook_secret: str = Field(..., env="GITHUB_WEBHOOK_SECRET")
    
    monitoring_webhook_enabled: bool = Field(default=True, env="MONITORING_WEBHOOK_ENABLED")
    monitoring_webhook_endpoint: str = Field(default="/webhooks/monitoring", env="MONITORING_WEBHOOK_ENDPOINT")
    monitoring_webhook_secret: str = Field(..., env="MONITORING_WEBHOOK_SECRET")
    
    # General webhook settings
    webhook_max_payload_size: int = Field(default=10485760, env="WEBHOOK_MAX_PAYLOAD_SIZE")  # 10MB
    webhook_timeout: float = Field(default=30.0, env="WEBHOOK_TIMEOUT")
    webhook_retry_attempts: int = Field(default=5, env="WEBHOOK_RETRY_ATTEMPTS")
    webhook_retry_delay: float = Field(default=1.0, env="WEBHOOK_RETRY_DELAY")
    webhook_queue_size: int = Field(default=1000, env="WEBHOOK_QUEUE_SIZE")
    
    # Security settings
    webhook_ip_whitelist: Optional[List[str]] = Field(default=None, env="WEBHOOK_IP_WHITELIST")
    webhook_rate_limit: int = Field(default=1000, env="WEBHOOK_RATE_LIMIT")  # per hour
    webhook_signature_required: bool = Field(default=True, env="WEBHOOK_SIGNATURE_REQUIRED")
    
    # Logging and monitoring
    webhook_log_payloads: bool = Field(default=False, env="WEBHOOK_LOG_PAYLOADS")  # Sensitive data
    webhook_log_headers: bool = Field(default=True, env="WEBHOOK_LOG_HEADERS")
    webhook_metrics_enabled: bool = Field(default=True, env="WEBHOOK_METRICS_ENABLED")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class WebhookEndpoints:
    """Webhook endpoints configuration."""    
    ENDPOINTS = {
        WebhookProvider.SPOTIFY: {
            "subscription": "/webhooks/spotify/subscription",
            "user": "/webhooks/spotify/user",
            "playlist": "/webhooks/spotify/playlist"
        },
        WebhookProvider.YOUTUBE: {
            "pubsub": "/webhooks/youtube/pubsub",
            "api": "/webhooks/youtube/api"
        },
        WebhookProvider.INSTAGRAM: {
            "feed": "/webhooks/instagram/feed",
            "story": "/webhooks/instagram/story"
        },
        WebhookProvider.TIKTOK: {
            "video": "/webhooks/tiktok/video",
            "user": "/webhooks/tiktok/user"
        },
        WebhookProvider.STRIPE: {
            "payments": "/webhooks/stripe/payments",
            "subscriptions": "/webhooks/stripe/subscriptions"
        },
        WebhookProvider.PAYPAL: {
            "payments": "/webhooks/paypal/payments",
            "subscriptions": "/webhooks/paypal/subscriptions"
        },
        WebhookProvider.CONTENT_ID: {
            "match": "/webhooks/content-id/match",
            "claim": "/webhooks/content-id/claim"
        },
        WebhookProvider.GITHUB: {
            "push": "/webhooks/github/push",
            "release": "/webhooks/github/release"
        }
    }
    
    @classmethod
    def get_endpoints(cls, provider: WebhookProvider) -> Dict[str, str]:
        """Get webhook endpoints for a specific provider."""        return cls.ENDPOINTS.get(provider, {})


class WebhookManager:
    """Webhook manager for handling external service notifications."""    
    def __init__(self, config: WebhookConfig):
        self.config = config
        self.handlers: Dict[str, Callable] = {}
        
    def get_security_config(self, provider: WebhookProvider) -> WebhookSecurity:
        """Get security configuration for a specific provider."""        secret_attr = f"{provider}_webhook_secret"
        secret_key = getattr(self.config, secret_attr, "")
        
        return WebhookSecurity(
            secret_key=secret_key,
            verify_signature=self.config.webhook_signature_required,
            allowed_ips=self.config.webhook_ip_whitelist
        )
    
    def get_retry_config(self) -> WebhookRetry:
        """Get retry configuration for webhook delivery."""        return WebhookRetry(
            max_attempts=self.config.webhook_retry_attempts,
            initial_delay=self.config.webhook_retry_delay,
            timeout_seconds=self.config.webhook_timeout
        )
    
    def verify_signature(
        self, 
        payload: bytes, 
        signature: str, 
        secret: str,
        algorithm: str = "sha256"
    ) -> bool:
        """Verify webhook signature."""        if not self.config.webhook_signature_required:
            return True
            
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            getattr(hashlib, algorithm)
        ).hexdigest()
        
        # Handle different signature formats
        if signature.startswith(f"{algorithm}="):
            signature = signature.split("=", 1)[1]
        
        return hmac.compare_digest(expected_signature, signature)
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a webhook event handler."""        self.handlers[event_type] = handler
    
    def get_handler(self, event_type: str) -> Optional[Callable]:
        """Get webhook event handler."""        return self.handlers.get(event_type)
    
    def get_provider_config(self, provider: WebhookProvider) -> Dict[str, Any]:
        """Get complete webhook configuration for a specific provider."""        enabled_attr = f"{provider}_webhook_enabled"
        endpoint_attr = f"{provider}_webhook_endpoint"
        events_attr = f"{provider}_webhook_events"
        
        return {
            "enabled": getattr(self.config, enabled_attr, False),
            "endpoint": getattr(self.config, endpoint_attr, ""),
            "events": getattr(self.config, events_attr, []),
            "security": self.get_security_config(provider),
            "retry": self.get_retry_config(),
            "endpoints": WebhookEndpoints.get_endpoints(provider)
        }
    
    def validate_webhook_payload(self, payload: dict, provider: WebhookProvider) -> bool:
        """Validate webhook payload structure."""        required_fields = ["type", "data", "timestamp"]
        
        # Provider-specific validations
        if provider == WebhookProvider.STRIPE:
            required_fields.extend(["id", "object", "livemode"])
        elif provider == WebhookProvider.PAYPAL:
            required_fields.extend(["id", "event_type", "resource"])
        elif provider in [WebhookProvider.YOUTUBE, WebhookProvider.INSTAGRAM]:
            required_fields.extend(["hub.challenge", "hub.verify_token"])
        
        return all(field in payload for field in required_fields)
    
    def format_webhook_url(self, provider: WebhookProvider, endpoint: str = "") -> str:
        """Format complete webhook URL."""        base_url = str(self.config.webhook_base_url).rstrip("/")
        provider_endpoint = getattr(self.config, f"{provider}_webhook_endpoint", "")
        
        if endpoint:
            return f"{base_url}{endpoint}"
        return f"{base_url}{provider_endpoint}"


# Global webhook configuration instance
webhook_config = WebhookConfig()
webhook_manager = WebhookManager(webhook_config)
