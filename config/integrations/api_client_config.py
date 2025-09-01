"""API Client Configuration Module for IA-Influencer Agent Platform
================================================================

Professional API client configuration for external service integrations.
Handles authentication, rate limiting, and error handling for content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission
is strictly prohibited and will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseSettings, Field, validator
from enum import Enum
import httpx
from dataclasses import dataclass


class APIProvider(str, Enum):
    """
Supported API providers for content platforms and services."""

    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SOUNDCLOUD = "soundcloud"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    
    # Content protection APIs
    SHAZAM = "shazam"
    AUDIBLE_MAGIC = "audible_magic"
    CONTENT_ID = "content_id"
    
    # Payment APIs
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    
    # Cloud storage APIs
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    
    # Vector/Search APIs
    PINECONE = "pinecone"
    ELASTICSEARCH = "elasticsearch"
    WEAVIATE = "weaviate"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration for API clients."""
    requests_per_second: float = 10.0
    requests_per_minute: int = 600
    requests_per_hour: int = 10000
    requests_per_day: int = 100000
    burst_capacity: int = 50
    backoff_factor: float = 1.5
    max_retry_attempts: int = 3


@dataclass
class TimeoutConfig:
    """
Timeout configuration for API clients."""
    connect_timeout: float = 30.0
    read_timeout: float = 60.0
    write_timeout: float = 30.0
    pool_timeout: float = 10.0


class APIClientConfig(BaseSettings):
    """
API client configuration for external service integrations."""
    
    # Spotify API
    spotify_base_url: str = Field(default="https://api.spotify.com/v1", env="SPOTIFY_BASE_URL")
    spotify_api_key: Optional[str] = Field(default=None, env="SPOTIFY_API_KEY")
    spotify_rate_limit: int = Field(default=100, env="SPOTIFY_RATE_LIMIT")
    
    # YouTube Data API
    youtube_base_url: str = Field(default="https://www.googleapis.com/youtube/v3", env="YOUTUBE_BASE_URL")
    youtube_api_key: str = Field(..., env="YOUTUBE_API_KEY")
    youtube_rate_limit: int = Field(default=10000, env="YOUTUBE_RATE_LIMIT")
    
    # Instagram Basic Display API
    instagram_base_url: str = Field(default="https://graph.instagram.com", env="INSTAGRAM_BASE_URL")
    instagram_api_version: str = Field(default="v18.0", env="INSTAGRAM_API_VERSION")
    instagram_rate_limit: int = Field(default=200, env="INSTAGRAM_RATE_LIMIT")
    
    # TikTok API
    tiktok_base_url: str = Field(default="https://open-api.tiktok.com", env="TIKTOK_BASE_URL")
    tiktok_api_version: str = Field(default="v1.3", env="TIKTOK_API_VERSION")
    tiktok_rate_limit: int = Field(default=1000, env="TIKTOK_RATE_LIMIT")
    
    # SoundCloud API
    soundcloud_base_url: str = Field(default="https://api.soundcloud.com", env="SOUNDCLOUD_BASE_URL")
    soundcloud_api_key: Optional[str] = Field(default=None, env="SOUNDCLOUD_API_KEY")
    soundcloud_rate_limit: int = Field(default=15000, env="SOUNDCLOUD_RATE_LIMIT")
    
    # Twitter API v2
    twitter_base_url: str = Field(default="https://api.twitter.com/2", env="TWITTER_BASE_URL")
    twitter_bearer_token: str = Field(..., env="TWITTER_BEARER_TOKEN")
    twitter_rate_limit: int = Field(default=300, env="TWITTER_RATE_LIMIT")
    
    # Facebook Graph API
    facebook_base_url: str = Field(default="https://graph.facebook.com", env="FACEBOOK_BASE_URL")
    facebook_api_version: str = Field(default="v18.0", env="FACEBOOK_API_VERSION")
    facebook_rate_limit: int = Field(default=200, env="FACEBOOK_RATE_LIMIT")
    
    # LinkedIn API
    linkedin_base_url: str = Field(default="https://api.linkedin.com/v2", env="LINKEDIN_BASE_URL")
    linkedin_rate_limit: int = Field(default=100, env="LINKEDIN_RATE_LIMIT")
    
    # GitHub API
    github_base_url: str = Field(default="https://api.github.com", env="GITHUB_BASE_URL")
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    github_rate_limit: int = Field(default=5000, env="GITHUB_RATE_LIMIT")
    
    # Content Protection APIs
    shazam_base_url: str = Field(default="https://shazam-core.p.rapidapi.com", env="SHAZAM_BASE_URL")
    shazam_api_key: str = Field(..., env="SHAZAM_API_KEY")
    shazam_rate_limit: int = Field(default=500, env="SHAZAM_RATE_LIMIT")
    
    audible_magic_base_url: str = Field(..., env="AUDIBLE_MAGIC_BASE_URL")
    audible_magic_api_key: str = Field(..., env="AUDIBLE_MAGIC_API_KEY")
    audible_magic_rate_limit: int = Field(default=1000, env="AUDIBLE_MAGIC_RATE_LIMIT")
    
    content_id_base_url: str = Field(..., env="CONTENT_ID_BASE_URL")
    content_id_api_key: str = Field(..., env="CONTENT_ID_API_KEY")
    content_id_rate_limit: int = Field(default=500, env="CONTENT_ID_RATE_LIMIT")
    
    # Payment APIs
    stripe_base_url: str = Field(default="https://api.stripe.com/v1", env="STRIPE_BASE_URL")
    stripe_secret_key: str = Field(..., env="STRIPE_SECRET_KEY")
    stripe_publishable_key: str = Field(..., env="STRIPE_PUBLISHABLE_KEY")
    stripe_rate_limit: int = Field(default=100, env="STRIPE_RATE_LIMIT")
    
    paypal_base_url: str = Field(..., env="PAYPAL_BASE_URL")  # sandbox or live
    paypal_client_id: str = Field(..., env="PAYPAL_CLIENT_ID")
    paypal_client_secret: str = Field(..., env="PAYPAL_CLIENT_SECRET")
    paypal_rate_limit: int = Field(default=500, env="PAYPAL_RATE_LIMIT")
    
    wise_base_url: str = Field(default="https://api.transferwise.com", env="WISE_BASE_URL")
    wise_api_token: str = Field(..., env="WISE_API_TOKEN")
    wise_rate_limit: int = Field(default=100, env="WISE_RATE_LIMIT")
    
    # Cloud Storage APIs
    aws_s3_region: str = Field(..., env="AWS_S3_REGION")
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    aws_s3_bucket: str = Field(..., env="AWS_S3_BUCKET")
    
    google_cloud_project_id: str = Field(..., env="GOOGLE_CLOUD_PROJECT_ID")
    google_cloud_credentials_path: str = Field(..., env="GOOGLE_CLOUD_CREDENTIALS_PATH")
    
    azure_storage_account: str = Field(..., env="AZURE_STORAGE_ACCOUNT")
    azure_storage_key: str = Field(..., env="AZURE_STORAGE_KEY")
    azure_container_name: str = Field(..., env="AZURE_CONTAINER_NAME")
    
    # Vector/Search APIs
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    pinecone_environment: str = Field(..., env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(..., env="PINECONE_INDEX_NAME")
    
    elasticsearch_host: str = Field(..., env="ELASTICSEARCH_HOST")
    elasticsearch_port: int = Field(default=9200, env="ELASTICSEARCH_PORT")
    elasticsearch_username: Optional[str] = Field(default=None, env="ELASTICSEARCH_USERNAME")
    elasticsearch_password: Optional[str] = Field(default=None, env="ELASTICSEARCH_PASSWORD")
    
    weaviate_url: str = Field(..., env="WEAVIATE_URL")
    weaviate_api_key: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")
    
    # General API settings
    default_timeout: float = Field(default=30.0, env="API_DEFAULT_TIMEOUT")
    max_retries: int = Field(default=3, env="API_MAX_RETRIES")
    retry_backoff_factor: float = Field(default=1.5, env="API_RETRY_BACKOFF_FACTOR")
    
    # User agent and headers
    user_agent: str = Field(
        default="IA-Influencer-Agent/2.0 (Content Protection Platform)",
        env="API_USER_AGENT"
    )
    
    # Request logging
    log_requests: bool = Field(default=True, env="API_LOG_REQUESTS")
    log_responses: bool = Field(default=False, env="API_LOG_RESPONSES")  # Sensitive data
    log_errors: bool = Field(default=True, env="API_LOG_ERRORS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class APIEndpoints:
    """API endpoints configuration for supported platforms."""

    
    ENDPOINTS = {
        APIProvider.SPOTIFY: {
            "me": "/me",
            "playlists": "/me/playlists",
            "tracks": "/me/tracks",
            "albums": "/me/albums",
            "artists": "/me/following",
            "search": "/search",
            "recommendations": "/recommendations"
        },
        APIProvider.YOUTUBE: {
            "channels": "/channels",
            "videos": "/videos",
            "playlists": "/playlists",
            "search": "/search",
            "activities": "/activities",
            "subscriptions": "/subscriptions"
        },
        APIProvider.INSTAGRAM: {
            "me": "/me",
            "media": "/me/media",
            "media_children": "/{media-id}/children"
        },
        APIProvider.TIKTOK: {
            "user_info": "/user/info/",
            "video_list": "/video/list/",
            "video_query": "/video/query/"
        },
        APIProvider.SOUNDCLOUD: {
            "me": "/me",
            "tracks": "/me/tracks",
            "playlists": "/me/playlists",
            "favorites": "/me/favorites"
        },
        APIProvider.TWITTER: {
            "me": "/users/me",
            "tweets": "/tweets",
            "users": "/users",
            "search": "/tweets/search/recent"
        },
        APIProvider.STRIPE: {
            "customers": "/customers",
            "payments": "/payment_intents",
            "subscriptions": "/subscriptions",
            "invoices": "/invoices"
        },
        APIProvider.PAYPAL: {
            "orders": "/v2/checkout/orders",
            "payments": "/v2/payments/captures",
            "webhooks": "/v1/notifications/webhooks"
        }
    }
    
    @classmethod
    def get_endpoints(cls, provider: APIProvider) -> Dict[str, str]:
        """Get API endpoints for a specific provider."""
        return cls.ENDPOINTS.get(provider, {})


class APIClientManager:
    """
API client manager for handling external service communications."""
    
    def __init__(self, config: APIClientConfig):
        self.config = config
        self.clients: Dict[APIProvider, httpx.AsyncClient] = {}
        
    def get_base_headers(self, provider: APIProvider) -> Dict[str, str]:
        """
Get base headers for API requests."""
        headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Add provider-specific headers
        if provider == APIProvider.SPOTIFY:
            headers["Authorization"] = f"Bearer {{}}"  # Token added at runtime
        elif provider == APIProvider.YOUTUBE:
            headers["Authorization"] = f"Bearer {{}}"  # Token added at runtime
            headers["X-Goog-Api-Key"] = self.config.youtube_api_key
        elif provider == APIProvider.TWITTER:
            headers["Authorization"] = f"Bearer {self.config.twitter_bearer_token}"
        elif provider == APIProvider.STRIPE:
            headers["Authorization"] = f"Bearer {self.config.stripe_secret_key}"
        elif provider == APIProvider.GITHUB and self.config.github_token:
            headers["Authorization"] = f"token {self.config.github_token}"
        elif provider == APIProvider.SHAZAM:
            headers["X-RapidAPI-Key"] = self.config.shazam_api_key
            headers["X-RapidAPI-Host"] = "shazam-core.p.rapidapi.com"
        
        return headers
    
    def get_rate_limit_config(self, provider: APIProvider) -> RateLimitConfig:
        """Get rate limiting configuration for a specific provider."""
        rate_limit_attr = f"{provider}_rate_limit"
        rate_limit = getattr(self.config, rate_limit_attr, 1000)
        
        return RateLimitConfig(
            requests_per_second=rate_limit / 3600,  # Distributed over an hour
            requests_per_minute=min(rate_limit // 60, 300),
            requests_per_hour=rate_limit,
            requests_per_day=rate_limit * 24
        )
    
    def get_timeout_config(self) -> TimeoutConfig:
        """Get timeout configuration for API clients."""
        return TimeoutConfig(
            connect_timeout=self.config.default_timeout,
            read_timeout=self.config.default_timeout * 2,
            write_timeout=self.config.default_timeout,
            pool_timeout=10.0
        )
    
    async def get_client(self, provider: APIProvider) -> httpx.AsyncClient:
        """
Get or create an async HTTP client for a specific provider."""
        if provider not in self.clients:
            base_url = getattr(self.config, f"{provider}_base_url", "")
            headers = self.get_base_headers(provider)
            timeout_config = self.get_timeout_config()
            
            timeout = httpx.Timeout(
                connect=timeout_config.connect_timeout,
                read=timeout_config.read_timeout,
                write=timeout_config.write_timeout,
                pool=timeout_config.pool_timeout
            )
            
            self.clients[provider] = httpx.AsyncClient(
                base_url=base_url,
                headers=headers,
                timeout=timeout,
                follow_redirects=True
            )
        
        return self.clients[provider]
    
    def get_provider_config(self, provider: APIProvider) -> Dict[str, Any]:
        """Get complete configuration for a specific provider."""
        base_url_attr = f"{provider}_base_url"
        rate_limit_attr = f"{provider}_rate_limit"
        
        return {
            "base_url": getattr(self.config, base_url_attr, ""),
            "rate_limit": getattr(self.config, rate_limit_attr, 1000),
            "endpoints": APIEndpoints.get_endpoints(provider),
            "headers": self.get_base_headers(provider),
            "timeout": self.get_timeout_config(),
            "rate_limit_config": self.get_rate_limit_config(provider)
        }
    
    async def close_all_clients(self):
        """Close all HTTP clients."""
        for client in self.clients.values():
            await client.aclose()
        self.clients.clear()


# Global API client configuration instance
api_client_config = APIClientConfig()
api_client_manager = APIClientManager(api_client_config)
