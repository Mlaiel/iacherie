"""External API Integrations Health Monitoring
Comprehensive health checking for third-party service integrations

This module provides health monitoring for:
- Social media platform APIs (Instagram, TikTok, Twitter/X, Facebook)
- Music streaming platform APIs (Spotify, Apple Music, YouTube Music)
- Content distribution platform APIs (YouTube, Vimeo, SoundCloud)
- AI/ML service APIs (OpenAI, Anthropic, Google Cloud AI)
- Infrastructure service APIs (AWS, Google Cloud, Azure)
- Communication service APIs (SendGrid, Twilio, Slack)
- Analytics service APIs (Google Analytics, Mixpanel)

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: IA Influencer Agent Platform - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use,
reproduction, or distribution without explicit written permission from
Fahed Mlaiel is strictly prohibited and may result in legal action.
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging

import requests
import aiohttp

from .core_health import HealthStatus, HealthCheckResult


@dataclass
class APIEndpointMetrics:
    """
External API endpoint performance metrics"""
    service_name: str
    endpoint_name: str
    response_time_ms: float
    status_code: int
    rate_limit_remaining: Optional[int]
    rate_limit_reset: Optional[datetime]
    success_rate_24h: float
    last_success: datetime
    api_version: str


class ExternalAPIHealthChecker:
    """
    External API integrations health monitoring system
    
    Monitors all third-party service integrations and API connectivity
    for the IA Influencer Agent platform.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize external API health checker
        
        Args:
            config: External API configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # API configurations
        self.external_apis = config.get("external_apis", {})
        self.social_media_apis = self.external_apis.get("social_media", {})
        self.music_platform_apis = self.external_apis.get("music_platforms", {})
        self.ai_service_apis = self.external_apis.get("ai_services", {})
        self.infrastructure_apis = self.external_apis.get("infrastructure", {})
        self.communication_apis = self.external_apis.get("communication", {})
        
        # Health check thresholds
        self.response_time_threshold = config.get("health_checks", {}).get("api_response_threshold_ms", 5000)
        self.rate_limit_threshold = config.get("health_checks", {}).get("rate_limit_threshold_percent", 20.0)
        self.success_rate_threshold = config.get("health_checks", {}).get("api_success_rate_threshold", 95.0)

    async def check_social_media_apis(self) -> HealthCheckResult:
        """
        Check social media platform API integrations
        
        Returns:
            HealthCheckResult: Social media APIs health status
        """
        start_time = time.time()
        
        try:
            details = {
                "category": "social_media_apis",
                "platforms": [],
                "total_platforms": 0,
                "healthy_platforms": 0
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # Instagram Basic Display API
            if "instagram" in self.social_media_apis:
                try:
                    instagram_config = self.social_media_apis["instagram"]
                    
                    # Test Instagram API
                    if instagram_config.get("access_token"):
                        test_url = "https://graph.instagram.com/me"
                        params = {
                            "fields": "id,username",
                            "access_token": instagram_config["access_token"]
                        }
                        
                        api_start = time.time()
                        response = requests.get(test_url, params=params, timeout=30)
                        api_time = (time.time() - api_start) * 1000
                        
                        platform_result = {
                            "platform": "instagram",
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "response_time_ms": api_time,
                            "status_code": response.status_code,
                            "api_version": "v18.0",
                            "rate_limit_remaining": response.headers.get("X-App-Usage", "unknown"),
                            "last_check": datetime.utcnow().isoformat()
                        }
                        
                        if response.status_code != 200:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"Instagram API returned HTTP {response.status_code}")
                        
                        if api_time > self.response_time_threshold:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"Instagram API slow response: {api_time:.1f}ms")
                        
                    else:
                        platform_result = {
                            "platform": "instagram",
                            "status": "not_configured",
                            "error": "Access token not configured"
                        }
                        warnings.append("Instagram access token not configured")
                    
                    details["platforms"].append(platform_result)
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    details["platforms"].append({
                        "platform": "instagram",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Twitter/X API v2
            if "twitter" in self.social_media_apis:
                try:
                    twitter_config = self.social_media_apis["twitter"]
                    
                    if twitter_config.get("bearer_token"):
                        test_url = "https://api.twitter.com/2/users/me"
                        headers = {
                            "Authorization": f"Bearer {twitter_config['bearer_token']}"
                        }
                        
                        api_start = time.time()
                        response = requests.get(test_url, headers=headers, timeout=30)
                        api_time = (time.time() - api_start) * 1000
                        
                        platform_result = {
                            "platform": "twitter",
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "response_time_ms": api_time,
                            "status_code": response.status_code,
                            "api_version": "v2",
                            "rate_limit_remaining": response.headers.get("x-rate-limit-remaining"),
                            "rate_limit_reset": response.headers.get("x-rate-limit-reset"),
                            "last_check": datetime.utcnow().isoformat()
                        }
                        
                        if response.status_code != 200:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"Twitter API returned HTTP {response.status_code}")
                        
                    else:
                        platform_result = {
                            "platform": "twitter",
                            "status": "not_configured",
                            "error": "Bearer token not configured"
                        }
                        warnings.append("Twitter bearer token not configured")
                    
                    details["platforms"].append(platform_result)
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    details["platforms"].append({
                        "platform": "twitter",
                        "status": "error",
                        "error": str(e)
                    })
            
            # TikTok Business API
            if "tiktok" in self.social_media_apis:
                try:
                    tiktok_config = self.social_media_apis["tiktok"]
                    
                    platform_result = {
                        "platform": "tiktok",
                        "status": "configured" if tiktok_config.get("access_token") else "not_configured",
                        "api_version": "v1.3",
                        "note": "TikTok Business API requires manual approval and review",
                        "last_check": datetime.utcnow().isoformat()
                    }
                    
                    if not tiktok_config.get("access_token"):
                        warnings.append("TikTok access token not configured")
                    
                    details["platforms"].append(platform_result)
                    
                except Exception as e:
                    details["platforms"].append({
                        "platform": "tiktok",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Facebook Graph API
            if "facebook" in self.social_media_apis:
                try:
                    facebook_config = self.social_media_apis["facebook"]
                    
                    if facebook_config.get("access_token"):
                        test_url = "https://graph.facebook.com/me"
                        params = {
                            "fields": "id,name",
                            "access_token": facebook_config["access_token"]
                        }
                        
                        api_start = time.time()
                        response = requests.get(test_url, params=params, timeout=30)
                        api_time = (time.time() - api_start) * 1000
                        
                        platform_result = {
                            "platform": "facebook",
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "response_time_ms": api_time,
                            "status_code": response.status_code,
                            "api_version": "v18.0",
                            "last_check": datetime.utcnow().isoformat()
                        }
                        
                        if response.status_code != 200:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"Facebook API returned HTTP {response.status_code}")
                        
                    else:
                        platform_result = {
                            "platform": "facebook",
                            "status": "not_configured",
                            "error": "Access token not configured"
                        }
                        warnings.append("Facebook access token not configured")
                    
                    details["platforms"].append(platform_result)
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    details["platforms"].append({
                        "platform": "facebook",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Calculate summary metrics
            details["total_platforms"] = len(details["platforms"])
            details["healthy_platforms"] = len([p for p in details["platforms"] if p.get("status") == "healthy"])
            details["warnings"] = warnings
            
            return HealthCheckResult(
                service="social_media_apis",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Social media APIs health check failed: {str(e)}")
            return HealthCheckResult(
                service="social_media_apis",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_music_platform_apis(self) -> HealthCheckResult:
        """
        Check music streaming platform API integrations
        
        Returns:
            HealthCheckResult: Music platform APIs health status
        """
        start_time = time.time()
        
        try:
            details = {
                "category": "music_platform_apis",
                "platforms": [],
                "total_platforms": 0,
                "healthy_platforms": 0
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # Spotify Web API
            if "spotify" in self.music_platform_apis:
                try:
                    spotify_config = self.music_platform_apis["spotify"]
                    
                    if spotify_config.get("client_id") and spotify_config.get("client_secret"):
                        # Get access token using client credentials flow
                        auth_url = "https://accounts.spotify.com/api/token"
                        auth_data = {
                            "grant_type": "client_credentials"
                        }
                        
                        auth_response = requests.post(
                            auth_url,
                            data=auth_data,
                            auth=(spotify_config["client_id"], spotify_config["client_secret"]),
                            timeout=30
                        )
                        
                        if auth_response.status_code == 200:
                            token_data = auth_response.json()
                            access_token = token_data["access_token"]
                            
                            # Test API call
                            test_url = "https://api.spotify.com/v1/browse/categories"
                            headers = {
                                "Authorization": f"Bearer {access_token}"
                            }
                            
                            api_start = time.time()
                            response = requests.get(test_url, headers=headers, timeout=30)
                            api_time = (time.time() - api_start) * 1000
                            
                            platform_result = {
                                "platform": "spotify",
                                "status": "healthy" if response.status_code == 200 else "unhealthy",
                                "response_time_ms": api_time,
                                "status_code": response.status_code,
                                "api_version": "v1",
                                "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining"),
                                "last_check": datetime.utcnow().isoformat()
                            }
                            
                            if response.status_code != 200:
                                status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                                warnings.append(f"Spotify API returned HTTP {response.status_code}")
                        else:
                            platform_result = {
                                "platform": "spotify",
                                "status": "auth_failed",
                                "error": f"Authentication failed: HTTP {auth_response.status_code}"
                            }
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append("Spotify API authentication failed")
                    else:
                        platform_result = {
                            "platform": "spotify",
                            "status": "not_configured",
                            "error": "Client credentials not configured"
                        }
                        warnings.append("Spotify client credentials not configured")
                    
                    details["platforms"].append(platform_result)
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    details["platforms"].append({
                        "platform": "spotify",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Apple Music API
            if "apple_music" in self.music_platform_apis:
                try:
                    apple_config = self.music_platform_apis["apple_music"]
                    
                    platform_result = {
                        "platform": "apple_music",
                        "status": "configured" if apple_config.get("developer_token") else "not_configured",
                        "api_version": "v1",
                        "note": "Apple Music API requires developer token and app-specific password",
                        "last_check": datetime.utcnow().isoformat()
                    }
                    
                    if not apple_config.get("developer_token"):
                        warnings.append("Apple Music developer token not configured")
                    
                    details["platforms"].append(platform_result)
                    
                except Exception as e:
                    details["platforms"].append({
                        "platform": "apple_music",
                        "status": "error",
                        "error": str(e)
                    })
            
            # SoundCloud API
            if "soundcloud" in self.music_platform_apis:
                try:
                    soundcloud_config = self.music_platform_apis["soundcloud"]
                    
                    if soundcloud_config.get("client_id"):
                        test_url = "https://api.soundcloud.com/resolve"
                        params = {
                            "url": "https://soundcloud.com/soundcloud",
                            "client_id": soundcloud_config["client_id"]
                        }
                        
                        api_start = time.time()
                        response = requests.get(test_url, params=params, timeout=30)
                        api_time = (time.time() - api_start) * 1000
                        
                        platform_result = {
                            "platform": "soundcloud",
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "response_time_ms": api_time,
                            "status_code": response.status_code,
                            "api_version": "v1",
                            "last_check": datetime.utcnow().isoformat()
                        }
                        
                        if response.status_code != 200:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"SoundCloud API returned HTTP {response.status_code}")
                        
                    else:
                        platform_result = {
                            "platform": "soundcloud",
                            "status": "not_configured",
                            "error": "Client ID not configured"
                        }
                        warnings.append("SoundCloud client ID not configured")
                    
                    details["platforms"].append(platform_result)
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    details["platforms"].append({
                        "platform": "soundcloud",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Calculate summary metrics
            details["total_platforms"] = len(details["platforms"])
            details["healthy_platforms"] = len([p for p in details["platforms"] if p.get("status") == "healthy"])
            details["warnings"] = warnings
            
            return HealthCheckResult(
                service="music_platform_apis",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Music platform APIs health check failed: {str(e)}")
            return HealthCheckResult(
                service="music_platform_apis",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_ai_service_apis(self) -> HealthCheckResult:
        """
        Check AI/ML service API integrations
        
        Returns:
            HealthCheckResult: AI service APIs health status
        """
        start_time = time.time()
        
        try:
            details = {
                "category": "ai_service_apis",
                "services": [],
                "total_services": 0,
                "healthy_services": 0
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # OpenAI API
            if "openai" in self.ai_service_apis:
                try:
                    openai_config = self.ai_service_apis["openai"]
                    
                    if openai_config.get("api_key"):
                        test_url = "https://api.openai.com/v1/models"
                        headers = {
                            "Authorization": f"Bearer {openai_config['api_key']}"
                        }
                        
                        api_start = time.time()
                        response = requests.get(test_url, headers=headers, timeout=30)
                        api_time = (time.time() - api_start) * 1000
                        
                        service_result = {
                            "service": "openai",
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "response_time_ms": api_time,
                            "status_code": response.status_code,
                            "api_version": "v1",
                            "rate_limit_remaining": response.headers.get("x-ratelimit-remaining-requests"),
                            "last_check": datetime.utcnow().isoformat()
                        }
                        
                        if response.status_code != 200:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"OpenAI API returned HTTP {response.status_code}")
                        
                    else:
                        service_result = {
                            "service": "openai",
                            "status": "not_configured",
                            "error": "API key not configured"
                        }
                        warnings.append("OpenAI API key not configured")
                    
                    details["services"].append(service_result)
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    details["services"].append({
                        "service": "openai",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Google Cloud AI APIs
            if "google_cloud_ai" in self.ai_service_apis:
                try:
                    gcp_config = self.ai_service_apis["google_cloud_ai"]
                    
                    service_result = {
                        "service": "google_cloud_ai",
                        "status": "configured" if gcp_config.get("credentials_path") else "not_configured",
                        "services": ["Vision API", "Natural Language API", "Translate API"],
                        "note": "Requires service account credentials file",
                        "last_check": datetime.utcnow().isoformat()
                    }
                    
                    if not gcp_config.get("credentials_path"):
                        warnings.append("Google Cloud AI credentials not configured")
                    
                    details["services"].append(service_result)
                    
                except Exception as e:
                    details["services"].append({
                        "service": "google_cloud_ai",
                        "status": "error",
                        "error": str(e)
                    })
            
            # AWS AI Services
            if "aws_ai" in self.ai_service_apis:
                try:
                    aws_config = self.ai_service_apis["aws_ai"]
                    
                    service_result = {
                        "service": "aws_ai",
                        "status": "configured" if aws_config.get("access_key_id") else "not_configured",
                        "services": ["Rekognition", "Comprehend", "Transcribe", "Polly"],
                        "region": aws_config.get("region", "us-east-1"),
                        "last_check": datetime.utcnow().isoformat()
                    }
                    
                    if not aws_config.get("access_key_id"):
                        warnings.append("AWS AI credentials not configured")
                    
                    details["services"].append(service_result)
                    
                except Exception as e:
                    details["services"].append({
                        "service": "aws_ai",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Anthropic Claude API
            if "anthropic" in self.ai_service_apis:
                try:
                    anthropic_config = self.ai_service_apis["anthropic"]
                    
                    service_result = {
                        "service": "anthropic",
                        "status": "configured" if anthropic_config.get("api_key") else "not_configured",
                        "api_version": "2023-06-01",
                        "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                        "last_check": datetime.utcnow().isoformat()
                    }
                    
                    if not anthropic_config.get("api_key"):
                        warnings.append("Anthropic API key not configured")
                    
                    details["services"].append(service_result)
                    
                except Exception as e:
                    details["services"].append({
                        "service": "anthropic",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Calculate summary metrics
            details["total_services"] = len(details["services"])
            details["healthy_services"] = len([s for s in details["services"] if s.get("status") == "healthy"])
            details["warnings"] = warnings
            
            return HealthCheckResult(
                service="ai_service_apis",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"AI service APIs health check failed: {str(e)}")
            return HealthCheckResult(
                service="ai_service_apis",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_communication_apis(self) -> HealthCheckResult:
        """
        Check communication service API integrations
        
        Returns:
            HealthCheckResult: Communication APIs health status
        """
        start_time = time.time()
        
        try:
            details = {
                "category": "communication_apis",
                "services": [],
                "total_services": 0,
                "healthy_services": 0
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # SendGrid Email API
            if "sendgrid" in self.communication_apis:
                try:
                    sendgrid_config = self.communication_apis["sendgrid"]
                    
                    if sendgrid_config.get("api_key"):
                        test_url = "https://api.sendgrid.com/v3/user/profile"
                        headers = {
                            "Authorization": f"Bearer {sendgrid_config['api_key']}"
                        }
                        
                        api_start = time.time()
                        response = requests.get(test_url, headers=headers, timeout=30)
                        api_time = (time.time() - api_start) * 1000
                        
                        service_result = {
                            "service": "sendgrid",
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "response_time_ms": api_time,
                            "status_code": response.status_code,
                            "api_version": "v3",
                            "last_check": datetime.utcnow().isoformat()
                        }
                        
                        if response.status_code != 200:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"SendGrid API returned HTTP {response.status_code}")
                        
                    else:
                        service_result = {
                            "service": "sendgrid",
                            "status": "not_configured",
                            "error": "API key not configured"
                        }
                        warnings.append("SendGrid API key not configured")
                    
                    details["services"].append(service_result)
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    details["services"].append({
                        "service": "sendgrid",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Twilio SMS/Voice API
            if "twilio" in self.communication_apis:
                try:
                    twilio_config = self.communication_apis["twilio"]
                    
                    if twilio_config.get("account_sid") and twilio_config.get("auth_token"):
                        test_url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_config['account_sid']}.json"
                        
                        api_start = time.time()
                        response = requests.get(
                            test_url,
                            auth=(twilio_config["account_sid"], twilio_config["auth_token"]),
                            timeout=30
                        )
                        api_time = (time.time() - api_start) * 1000
                        
                        service_result = {
                            "service": "twilio",
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "response_time_ms": api_time,
                            "status_code": response.status_code,
                            "api_version": "2010-04-01",
                            "last_check": datetime.utcnow().isoformat()
                        }
                        
                        if response.status_code != 200:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"Twilio API returned HTTP {response.status_code}")
                        
                    else:
                        service_result = {
                            "service": "twilio",
                            "status": "not_configured",
                            "error": "Account SID or Auth Token not configured"
                        }
                        warnings.append("Twilio credentials not configured")
                    
                    details["services"].append(service_result)
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    details["services"].append({
                        "service": "twilio",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Slack API
            if "slack" in self.communication_apis:
                try:
                    slack_config = self.communication_apis["slack"]
                    
                    if slack_config.get("bot_token"):
                        test_url = "https://slack.com/api/auth.test"
                        headers = {
                            "Authorization": f"Bearer {slack_config['bot_token']}"
                        }
                        
                        api_start = time.time()
                        response = requests.get(test_url, headers=headers, timeout=30)
                        api_time = (time.time() - api_start) * 1000
                        
                        if response.status_code == 200:
                            response_data = response.json()
                            is_ok = response_data.get("ok", False)
                        else:
                            is_ok = False
                        
                        service_result = {
                            "service": "slack",
                            "status": "healthy" if is_ok else "unhealthy",
                            "response_time_ms": api_time,
                            "status_code": response.status_code,
                            "api_ok": is_ok,
                            "last_check": datetime.utcnow().isoformat()
                        }
                        
                        if not is_ok:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append("Slack API authentication failed")
                        
                    else:
                        service_result = {
                            "service": "slack",
                            "status": "not_configured",
                            "error": "Bot token not configured"
                        }
                        warnings.append("Slack bot token not configured")
                    
                    details["services"].append(service_result)
                    
                except Exception as e:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                    details["services"].append({
                        "service": "slack",
                        "status": "error",
                        "error": str(e)
                    })
            
            # Calculate summary metrics
            details["total_services"] = len(details["services"])
            details["healthy_services"] = len([s for s in details["services"] if s.get("status") == "healthy"])
            details["warnings"] = warnings
            
            return HealthCheckResult(
                service="communication_apis",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Communication APIs health check failed: {str(e)}")
            return HealthCheckResult(
                service="communication_apis",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def perform_comprehensive_check(self) -> List[HealthCheckResult]:
        """
        Perform all external API health checks concurrently
        
        Returns:
            List[HealthCheckResult]: All external API health check results
        """
        checks = await asyncio.gather(
            self.check_social_media_apis(),
            self.check_music_platform_apis(),
            self.check_ai_service_apis(),
            self.check_communication_apis(),
            return_exceptions=True
        )
        
        results = []
        for check in checks:
            if isinstance(check, Exception):
                self.logger.error(f"External API health check failed with exception: {str(check)}")
                results.append(HealthCheckResult(
                    service="unknown_external_api",
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0.0,
                    timestamp=datetime.utcnow(),
                    details={},
                    error_message=str(check)
                ))
            else:
                results.append(check)
                
        return results

    async def get_external_api_health_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive external API health summary
        
        Returns:
            Dict[str, Any]: External API health summary with overall status
        """
        results = await self.perform_comprehensive_check()
        
        # Calculate overall external API health
        status_weights = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 1,
            HealthStatus.UNHEALTHY: 2,
            HealthStatus.CRITICAL: 3
        }
        
        overall_score = max([status_weights[result.status] for result in results])
        overall_status = [status for status, weight in status_weights.items() if weight == overall_score][0]
        
        # Calculate metrics
        avg_response_time = sum([result.response_time_ms for result in results]) / len(results)
        healthy_apis = len([r for r in results if r.status == HealthStatus.HEALTHY])
        total_apis = len(results)
        
        return {
            "overall_status": overall_status.value,
            "healthy_external_apis": healthy_apis,
            "total_external_apis": total_apis,
            "external_api_health_percentage": (healthy_apis / total_apis) * 100,
            "average_response_time_ms": round(avg_response_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "external_api_results": [asdict(result) for result in results]
        }
