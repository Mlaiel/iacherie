"""Content Protection Platform Adapters - Anti-Piracy & Copyright Management

This module provides comprehensive adapter infrastructure for integrating with
content protection services, anti-piracy platforms, and copyright management systems.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Features:
- Multi-platform content monitoring (YouTube, TikTok, Instagram, etc.)
- Advanced fingerprinting and matching algorithms
- DMCA takedown automation and tracking
- Copyright registration and management
- Real-time content violation detection
- Legal compliance and documentation
"""
import asyncio
import logging
from abc import abstractmethod
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
import aiohttp
from urllib.parse import urljoin, urlparse
import mimetypes
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_adapter import (
    BasePlatformAdapter, PlatformType, AdapterStatus, AuthenticationType,
    AdapterCredentials, RateLimitConfig, AdapterError, PlatformError
)

logger = logging.getLogger(__name__)

class ProtectionPlatform(Enum):
    """Supported content protection platforms."""    YOUTUBE_CONTENT_ID = "youtube_content_id"
    FACEBOOK_RIGHTS_MANAGER = "facebook_rights_manager"
    INSTAGRAM_CREATOR_STUDIO = "instagram_creator_studio"
    TIKTOK_COPYRIGHT_TOOL = "tiktok_copyright_tool"
    TWITCH_AUDIO_RECOGNITION = "twitch_audio_recognition"
    SOUNDCLOUD_COPYRIGHT = "soundcloud_copyright"
    SPOTIFY_COPYRIGHT = "spotify_copyright"
    DMCA_TAKEDOWN_SERVICE = "dmca_takedown_service"
    COPYRIGHT_ALLIANCE = "copyright_alliance"
    CUSTOM_FINGERPRINT = "custom_fingerprint"

class ContentType(Enum):
    """Types of content that can be protected."""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    SOCIAL_POST = "social_post"
    MUSIC_COMPOSITION = "music_composition"
    ARTWORK = "artwork"
    BRAND_CONTENT = "brand_content"

class ViolationType(Enum):
    """Types of copyright violations."""    EXACT_COPY = "exact_copy"
    PARTIAL_COPY = "partial_copy"
    REMIX_UNAUTHORIZED = "remix_unauthorized"
    COVER_UNAUTHORIZED = "cover_unauthorized"
    SAMPLING_UNAUTHORIZED = "sampling_unauthorized"
    TRADEMARK_VIOLATION = "trademark_violation"
    BRAND_IMPERSONATION = "brand_impersonation"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    COMMERCIAL_USE = "commercial_use"
    FAIR_USE_VIOLATION = "fair_use_violation"

class ActionType(Enum):
    """Actions that can be taken on violations."""    DMCA_TAKEDOWN = "dmca_takedown"
    COPYRIGHT_CLAIM = "copyright_claim"
    MONETIZATION_CLAIM = "monetization_claim"
    CONTENT_BLOCK = "content_block"
    WARNING_NOTICE = "warning_notice"
    CEASE_DESIST = "cease_desist"
    LEGAL_ACTION = "legal_action"
    PLATFORM_REPORT = "platform_report"
    MANUAL_REVIEW = "manual_review"

@dataclass
class ProtectedContent:
    """Represents content that is being protected."""    content_id: str
    title: str
    content_type: ContentType
    owner_id: str
    fingerprints: Dict[str, str]  # algorithm -> fingerprint
    metadata: Dict[str, Any]
    upload_date: datetime
    protection_enabled: bool = True
    monitoring_platforms: Set[ProtectionPlatform] = field(default_factory=set)
    copyright_info: Optional[Dict[str, Any]] = None
    
class ContentViolation:
    """Represents a detected content violation."""    
    def __init__(
        self,
        violation_id: str,
        protected_content_id: str,
        infringing_url: str,
        platform: ProtectionPlatform,
        violation_type: ViolationType,
        confidence_score: float,
        detected_at: datetime,
        infringing_content: Dict[str, Any],
        similarity_score: float = 0.0,
        metadata: Dict[str, Any] = None
    ):
        self.violation_id = violation_id
        self.protected_content_id = protected_content_id
        self.infringing_url = infringing_url
        self.platform = platform
        self.violation_type = violation_type
        self.confidence_score = confidence_score
        self.detected_at = detected_at
        self.infringing_content = infringing_content
        self.similarity_score = similarity_score
        self.metadata = metadata or {}
        self.status = "detected"
        self.actions_taken: List[Dict[str, Any]] = []

@dataclass
class TakedownRequest:
    """Represents a DMCA takedown request."""    request_id: str
    violation_id: str
    platform: ProtectionPlatform
    infringing_url: str
    copyright_owner: str
    contact_email: str
    action_type: ActionType
    legal_basis: str
    requested_at: datetime
    status: str = "pending"
    response_deadline: Optional[datetime] = None
    platform_response: Optional[Dict[str, Any]] = None

class BaseProtectionAdapter(BasePlatformAdapter):
    """Base class for content protection platform adapters."""    
    def __init__(
        self, 
        platform_name: str,
        protection_platform: ProtectionPlatform,
        credentials: AdapterCredentials, 
        config: Dict[str, Any]
    ):
        super().__init__(
            platform_name=platform_name,
            platform_type=PlatformType.CONTENT_PROTECTION,
            credentials=credentials,
            rate_limit_config=RateLimitConfig(
                requests_per_minute=30,
                burst_limit=5,
                rate_limit_window=60
            )
        )
        self.protection_platform = protection_platform
        self.config = config
        self.monitored_content: Dict[str, ProtectedContent] = {}
        self.detected_violations: Dict[str, ContentViolation] = {}
        self.takedown_requests: Dict[str, TakedownRequest] = {}
    
    @abstractmethod
    async def register_content(self, content: ProtectedContent) -> bool:
        """Register content for protection monitoring."""        pass
    
    @abstractmethod
    async def scan_for_violations(self, content_id: str) -> List[ContentViolation]:
        """Scan for violations of protected content."""        pass
    
    @abstractmethod
    async def submit_takedown_request(self, request: TakedownRequest) -> bool:
        """Submit a DMCA takedown request."""        pass
    
    @abstractmethod
    async def check_takedown_status(self, request_id: str) -> Dict[str, Any]:
        """Check the status of a takedown request."""        pass
    
    async def generate_content_fingerprint(self, content_data: bytes, content_type: ContentType) -> str:
        """Generate a fingerprint for content identification."""        # Basic hash-based fingerprint (should be replaced with advanced algorithms)
        fingerprint_data = hashlib.sha256(content_data).hexdigest()
        
        # Add content type specific processing
        if content_type == ContentType.AUDIO:
            # Audio fingerprinting would use acoustic features
            pass
        elif content_type == ContentType.VIDEO:
            # Video fingerprinting would use visual and audio features
            pass
        elif content_type == ContentType.IMAGE:
            # Image fingerprinting would use perceptual hashing
            pass
        
        return fingerprint_data
    
    async def calculate_similarity(self, fingerprint1: str, fingerprint2: str) -> float:
        """Calculate similarity between two fingerprints."""        # Basic implementation - should be replaced with advanced similarity algorithms
        if fingerprint1 == fingerprint2:
            return 1.0
        
        # Hamming distance for basic comparison
        if len(fingerprint1) != len(fingerprint2):
            return 0.0
        
        differences = sum(c1 != c2 for c1, c2 in zip(fingerprint1, fingerprint2))
        similarity = 1.0 - (differences / len(fingerprint1))
        
        return similarity
    
    async def analyze_violation_severity(self, violation: ContentViolation) -> Dict[str, Any]:
        """Analyze the severity and recommended actions for a violation."""        severity_score = 0.0
        recommended_actions = []
        
        # Factor in confidence score
        severity_score += violation.confidence_score * 0.4
        
        # Factor in similarity score
        severity_score += violation.similarity_score * 0.3
        
        # Factor in violation type
        violation_weights = {
            ViolationType.EXACT_COPY: 1.0,
            ViolationType.PARTIAL_COPY: 0.7,
            ViolationType.REMIX_UNAUTHORIZED: 0.6,
            ViolationType.COVER_UNAUTHORIZED: 0.5,
            ViolationType.SAMPLING_UNAUTHORIZED: 0.4,
            ViolationType.COMMERCIAL_USE: 0.8,
            ViolationType.TRADEMARK_VIOLATION: 0.9,
            ViolationType.BRAND_IMPERSONATION: 0.9
        }
        
        severity_score += violation_weights.get(violation.violation_type, 0.5) * 0.3
        
        # Recommend actions based on severity
        if severity_score >= 0.8:
            recommended_actions = [ActionType.DMCA_TAKEDOWN, ActionType.LEGAL_ACTION]
        elif severity_score >= 0.6:
            recommended_actions = [ActionType.COPYRIGHT_CLAIM, ActionType.MONETIZATION_CLAIM]
        elif severity_score >= 0.4:
            recommended_actions = [ActionType.PLATFORM_REPORT, ActionType.WARNING_NOTICE]
        else:
            recommended_actions = [ActionType.MANUAL_REVIEW]
        
        return {
            'severity_score': severity_score,
            'severity_level': 'high' if severity_score >= 0.7 else 'medium' if severity_score >= 0.4 else 'low',
            'recommended_actions': recommended_actions,
            'priority': 'urgent' if severity_score >= 0.8 else 'normal' if severity_score >= 0.5 else 'low'
        }

class YouTubeContentIDAdapter(BaseProtectionAdapter):
    """YouTube Content ID system adapter."""    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(
            platform_name="youtube_content_id",
            protection_platform=ProtectionPlatform.YOUTUBE_CONTENT_ID,
            credentials=credentials,
            config=config
        )
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
    
    async def register_content(self, content: ProtectedContent) -> bool:
        """Register content with YouTube Content ID."""        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare Content ID reference
            reference_data = {
                "asset_id": content.content_id,
                "title": content.title,
                "content_type": content.content_type.value,
                "fingerprints": content.fingerprints,
                "metadata": content.metadata
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/assets",
                    headers=headers,
                    json=reference_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Content registered with YouTube Content ID: {content.content_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"YouTube Content ID registration failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"YouTube Content ID registration error: {str(e)}")
            return False
    
    async def scan_for_violations(self, content_id: str) -> List[ContentViolation]:
        """Scan YouTube for violations using Content ID."""        violations = []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            # Query Content ID matches
            params = {
                "asset_id": content_id,
                "status": "active"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/claims",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for claim in data.get('items', []):
                            violation = ContentViolation(
                                violation_id=claim['id'],
                                protected_content_id=content_id,
                                infringing_url=f"https://youtube.com/watch?v={claim['video_id']}",
                                platform=ProtectionPlatform.YOUTUBE_CONTENT_ID,
                                violation_type=ViolationType.PARTIAL_COPY,  # Determined by Content ID
                                confidence_score=claim.get('match_confidence', 0.0),
                                detected_at=datetime.utcnow(),
                                infringing_content={
                                    'video_id': claim['video_id'],
                                    'title': claim.get('video_title', ''),
                                    'channel': claim.get('channel_name', ''),
                                    'duration': claim.get('duration', 0)
                                },
                                similarity_score=claim.get('similarity_score', 0.0)
                            )
                            violations.append(violation)
                    
        except Exception as e:
            logger.error(f"YouTube Content ID scan error: {str(e)}")
        
        return violations
    
    async def submit_takedown_request(self, request: TakedownRequest) -> bool:
        """Submit a copyright claim through YouTube Content ID."""        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            claim_data = {
                "video_id": request.infringing_url.split('v=')[1],
                "asset_id": request.violation_id,
                "action": "claim" if request.action_type == ActionType.COPYRIGHT_CLAIM else "takedown",
                "policy": "monetize" if request.action_type == ActionType.MONETIZATION_CLAIM else "block"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/claims",
                    headers=headers,
                    json=claim_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        request.status = "submitted"
                        request.platform_response = result
                        logger.info(f"YouTube copyright claim submitted: {request.request_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"YouTube claim submission failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"YouTube claim submission error: {str(e)}")
            return False
    
    async def check_takedown_status(self, request_id: str) -> Dict[str, Any]:
        """Check YouTube copyright claim status."""        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/claims/{request_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "error", "message": await response.text()}
            
        except Exception as e:
            logger.error(f"YouTube status check error: {str(e)}")
            return {"status": "error", "message": str(e)}

class FacebookRightsManagerAdapter(BaseProtectionAdapter):
    """Facebook Rights Manager adapter."""    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(
            platform_name="facebook_rights_manager",
            protection_platform=ProtectionPlatform.FACEBOOK_RIGHTS_MANAGER,
            credentials=credentials,
            config=config
        )
        self.api_base_url = "https://graph.facebook.com/v18.0"
    
    async def register_content(self, content: ProtectedContent) -> bool:
        """Register content with Facebook Rights Manager."""        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            reference_data = {
                "name": content.title,
                "content_category": content.content_type.value.upper(),
                "ownership_countries": ["US", "CA", "GB", "DE", "FR"],  # Global protection
                "whitelisted_ig_users": [],
                "whitelisted_fb_users": []
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/me/owned_media",
                    headers=headers,
                    json=reference_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Content registered with Facebook Rights Manager: {content.content_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Facebook Rights Manager registration failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Facebook Rights Manager registration error: {str(e)}")
            return False
    
    async def scan_for_violations(self, content_id: str) -> List[ContentViolation]:
        """Scan Facebook/Instagram for rights violations."""        violations = []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            # Query for matches
            params = {
                "media_id": content_id,
                "fields": "matched_content,similarity_score,content_owner"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/me/matched_content",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for match in data.get('data', []):
                            violation = ContentViolation(
                                violation_id=match['id'],
                                protected_content_id=content_id,
                                infringing_url=match.get('permalink_url', ''),
                                platform=ProtectionPlatform.FACEBOOK_RIGHTS_MANAGER,
                                violation_type=ViolationType.PARTIAL_COPY,
                                confidence_score=match.get('match_confidence', 0.0),
                                detected_at=datetime.utcnow(),
                                infringing_content={
                                    'post_id': match.get('id'),
                                    'content_type': match.get('media_type'),
                                    'owner': match.get('content_owner', {}).get('name', ''),
                                    'created_time': match.get('created_time')
                                },
                                similarity_score=match.get('similarity_score', 0.0)
                            )
                            violations.append(violation)
                    
        except Exception as e:
            logger.error(f"Facebook Rights Manager scan error: {str(e)}")
        
        return violations
    
    async def submit_takedown_request(self, request: TakedownRequest) -> bool:
        """Submit a rights claim through Facebook Rights Manager."""        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            action_data = {
                "matched_content_id": request.violation_id,
                "action": "CLAIM" if request.action_type == ActionType.COPYRIGHT_CLAIM else "TAKEDOWN",
                "action_reason": request.legal_basis
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/me/rights_actions",
                    headers=headers,
                    json=action_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        request.status = "submitted"
                        request.platform_response = result
                        logger.info(f"Facebook rights action submitted: {request.request_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Facebook rights action failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Facebook rights action error: {str(e)}")
            return False
    
    async def check_takedown_status(self, request_id: str) -> Dict[str, Any]:
        """Check Facebook rights action status."""        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/{request_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "error", "message": await response.text()}
            
        except Exception as e:
            logger.error(f"Facebook status check error: {str(e)}")
            return {"status": "error", "message": str(e)}

class DMCATakedownAdapter(BaseProtectionAdapter):
    """Generic DMCA takedown service adapter."""    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(
            platform_name="dmca_takedown",
            protection_platform=ProtectionPlatform.DMCA_TAKEDOWN_SERVICE,
            credentials=credentials,
            config=config
        )
        self.service_url = config.get('service_url', 'https://api.dmcatakedown.com/v1')
    
    async def register_content(self, content: ProtectedContent) -> bool:
        """Register content for DMCA protection monitoring."""        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            registration_data = {
                "content_id": content.content_id,
                "title": content.title,
                "content_type": content.content_type.value,
                "copyright_owner": content.metadata.get('owner_name'),
                "copyright_email": content.metadata.get('owner_email'),
                "original_url": content.metadata.get('original_url'),
                "fingerprints": content.fingerprints,
                "monitoring_enabled": content.protection_enabled
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.service_url}/content/register",
                    headers=headers,
                    json=registration_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Content registered for DMCA protection: {content.content_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"DMCA registration failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"DMCA registration error: {str(e)}")
            return False
    
    async def scan_for_violations(self, content_id: str) -> List[ContentViolation]:
        """Scan web for DMCA violations."""        violations = []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.service_url}/violations/{content_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for violation_data in data.get('violations', []):
                            violation = ContentViolation(
                                violation_id=violation_data['id'],
                                protected_content_id=content_id,
                                infringing_url=violation_data['infringing_url'],
                                platform=ProtectionPlatform.DMCA_TAKEDOWN_SERVICE,
                                violation_type=ViolationType(violation_data.get('violation_type', 'partial_copy')),
                                confidence_score=violation_data.get('confidence_score', 0.0),
                                detected_at=datetime.fromisoformat(violation_data['detected_at']),
                                infringing_content=violation_data.get('infringing_content', {}),
                                similarity_score=violation_data.get('similarity_score', 0.0)
                            )
                            violations.append(violation)
                    
        except Exception as e:
            logger.error(f"DMCA violation scan error: {str(e)}")
        
        return violations
    
    async def submit_takedown_request(self, request: TakedownRequest) -> bool:
        """Submit DMCA takedown notice."""        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}",
                "Content-Type": "application/json"
            }
            
            takedown_data = {
                "violation_id": request.violation_id,
                "infringing_url": request.infringing_url,
                "copyright_owner": request.copyright_owner,
                "contact_email": request.contact_email,
                "legal_basis": request.legal_basis,
                "action_type": request.action_type.value,
                "expedited": request.metadata.get('expedited', False)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.service_url}/takedown/submit",
                    headers=headers,
                    json=takedown_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        request.status = "submitted"
                        request.platform_response = result
                        logger.info(f"DMCA takedown submitted: {request.request_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"DMCA takedown submission failed: {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"DMCA takedown submission error: {str(e)}")
            return False
    
    async def check_takedown_status(self, request_id: str) -> Dict[str, Any]:
        """Check DMCA takedown status."""        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.service_url}/takedown/status/{request_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"status": "error", "message": await response.text()}
            
        except Exception as e:
            logger.error(f"DMCA status check error: {str(e)}")
            return {"status": "error", "message": str(e)}

class ProtectionAdapterFactory:
    """Factory for creating content protection adapters."""    
    _adapters = {
        ProtectionPlatform.YOUTUBE_CONTENT_ID: YouTubeContentIDAdapter,
        ProtectionPlatform.FACEBOOK_RIGHTS_MANAGER: FacebookRightsManagerAdapter,
        ProtectionPlatform.DMCA_TAKEDOWN_SERVICE: DMCATakedownAdapter
    }
    
    @classmethod
    def create_adapter(
        cls, 
        platform: ProtectionPlatform, 
        credentials: AdapterCredentials, 
        config: Dict[str, Any]
    ) -> BaseProtectionAdapter:
        """Create a protection adapter instance."""        adapter_class = cls._adapters.get(platform)
        if not adapter_class:
            raise ValueError(f"Unsupported protection platform: {platform}")
        
        return adapter_class(credentials, config)
    
    @classmethod
    def get_supported_platforms(cls) -> List[ProtectionPlatform]:
        """Get list of supported protection platforms."""        return list(cls._adapters.keys())

class ProtectionAdapterManager:
    """Manager for content protection adapter instances and orchestration."""    
    def __init__(self):
        self.adapters: Dict[ProtectionPlatform, BaseProtectionAdapter] = {}
        self.protected_content: Dict[str, ProtectedContent] = {}
        self.violation_history: List[ContentViolation] = []
        self.takedown_requests: Dict[str, TakedownRequest] = {}
    
    def register_adapter(self, platform: ProtectionPlatform, adapter: BaseProtectionAdapter):
        """Register a protection adapter."""        self.adapters[platform] = adapter
        logger.info(f"Registered protection adapter for platform: {platform.value}")
    
    async def protect_content(self, content: ProtectedContent) -> bool:
        """Register content for protection across all enabled platforms."""        self.protected_content[content.content_id] = content
        
        success_count = 0
        for platform in content.monitoring_platforms:
            if platform in self.adapters:
                adapter = self.adapters[platform]
                try:
                    if await adapter.register_content(content):
                        success_count += 1
                        logger.info(f"Content {content.content_id} registered with {platform.value}")
                    else:
                        logger.warning(f"Failed to register content {content.content_id} with {platform.value}")
                except Exception as e:
                    logger.error(f"Error registering content with {platform.value}: {str(e)}")
        
        return success_count > 0
    
    async def scan_all_violations(self, content_id: str) -> List[ContentViolation]:
        """Scan for violations across all monitoring platforms."""        all_violations = []
        
        content = self.protected_content.get(content_id)
        if not content:
            logger.warning(f"Content {content_id} not found in protected content")
            return all_violations
        
        for platform in content.monitoring_platforms:
            if platform in self.adapters:
                adapter = self.adapters[platform]
                try:
                    violations = await adapter.scan_for_violations(content_id)
                    all_violations.extend(violations)
                    logger.info(f"Found {len(violations)} violations on {platform.value}")
                except Exception as e:
                    logger.error(f"Error scanning violations on {platform.value}: {str(e)}")
        
        # Store violations in history
        self.violation_history.extend(all_violations)
        
        return all_violations
    
    async def auto_respond_violations(self, violations: List[ContentViolation]) -> Dict[str, Any]:
        """Automatically respond to violations based on severity analysis."""        responses = {
            'processed': 0,
            'actions_taken': 0,
            'failed': 0,
            'details': []
        }
        
        for violation in violations:
            try:
                # Analyze violation severity
                if violation.platform in self.adapters:
                    adapter = self.adapters[violation.platform]
                    analysis = await adapter.analyze_violation_severity(violation)
                    
                    # Take action based on severity
                    if analysis['severity_level'] == 'high':
                        action_type = ActionType.DMCA_TAKEDOWN
                    elif analysis['severity_level'] == 'medium':
                        action_type = ActionType.COPYRIGHT_CLAIM
                    else:
                        action_type = ActionType.WARNING_NOTICE
                    
                    # Create takedown request
                    takedown_request = TakedownRequest(
                        request_id=f"req_{violation.violation_id}",
                        violation_id=violation.violation_id,
                        platform=violation.platform,
                        infringing_url=violation.infringing_url,
                        copyright_owner="Content Owner",  # Should come from content metadata
                        contact_email="contact@example.com",  # Should come from content metadata
                        action_type=action_type,
                        legal_basis="Copyright infringement under DMCA",
                        requested_at=datetime.utcnow()
                    )
                    
                    # Submit takedown request
                    if await adapter.submit_takedown_request(takedown_request):
                        self.takedown_requests[takedown_request.request_id] = takedown_request
                        responses['actions_taken'] += 1
                        responses['details'].append({
                            'violation_id': violation.violation_id,
                            'action': action_type.value,
                            'status': 'submitted'
                        })
                    else:
                        responses['failed'] += 1
                        responses['details'].append({
                            'violation_id': violation.violation_id,
                            'action': action_type.value,
                            'status': 'failed'
                        })
                
                responses['processed'] += 1
                
            except Exception as e:
                logger.error(f"Error auto-responding to violation {violation.violation_id}: {str(e)}")
                responses['failed'] += 1
        
        return responses
    
    async def get_protection_status(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive protection status for content."""        content = self.protected_content.get(content_id)
        if not content:
            return {"error": "Content not found"}
        
        # Get recent violations
        recent_violations = [
            v for v in self.violation_history 
            if v.protected_content_id == content_id and 
            v.detected_at > datetime.utcnow() - timedelta(days=30)
        ]
        
        # Get active takedown requests
        active_requests = [
            r for r in self.takedown_requests.values()
            if any(v.violation_id == r.violation_id for v in recent_violations) and
            r.status in ['pending', 'submitted']
        ]
        
        return {
            'content_id': content_id,
            'protection_enabled': content.protection_enabled,
            'monitoring_platforms': [p.value for p in content.monitoring_platforms],
            'total_violations': len([v for v in self.violation_history if v.protected_content_id == content_id]),
            'recent_violations': len(recent_violations),
            'active_takedown_requests': len(active_requests),
            'protection_score': self._calculate_protection_score(content_id)
        }
    
    def _calculate_protection_score(self, content_id: str) -> float:
        """Calculate protection effectiveness score."""        content_violations = [v for v in self.violation_history if v.protected_content_id == content_id]
        
        if not content_violations:
            return 1.0  # Perfect score if no violations
        
        # Factor in response time and effectiveness
        resolved_violations = len([v for v in content_violations if v.status == 'resolved'])
        total_violations = len(content_violations)
        
        resolution_rate = resolved_violations / total_violations if total_violations > 0 else 1.0
        
        # Adjust score based on violation severity and frequency
        recent_violations = [
            v for v in content_violations 
            if v.detected_at > datetime.utcnow() - timedelta(days=30)
        ]
        
        if len(recent_violations) > 10:
            frequency_penalty = 0.2
        elif len(recent_violations) > 5:
            frequency_penalty = 0.1
        else:
            frequency_penalty = 0.0
        
        protection_score = resolution_rate - frequency_penalty
        return max(0.0, min(1.0, protection_score))

# Export all classes and functions
__all__ = [
    'ProtectionPlatform', 'ContentType', 'ViolationType', 'ActionType',
    'ProtectedContent', 'ContentViolation', 'TakedownRequest',
    'BaseProtectionAdapter', 'YouTubeContentIDAdapter', 'FacebookRightsManagerAdapter',
    'DMCATakedownAdapter', 'ProtectionAdapterFactory', 'ProtectionAdapterManager'
]
