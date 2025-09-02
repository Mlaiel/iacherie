"""🌐 Multi-Platform Integration Engine
=====================================

Enterprise-grade platform integration system for automated DMCA submission across major content platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

This module provides:
- Multi-platform API integration
- Automated form submission
- Platform-specific adapters
- Rate limiting and retry logic
- Real-time status tracking
"""

import asyncio
import logging
import aiohttp
import secrets
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import hashlib
from urllib.parse import urljoin, urlparse
import base64

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """
Supported platform types for DMCA integration"""

    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    GENERIC_WEB = "generic_web"


class SubmissionMethod(Enum):
    """Available submission methods"""

    API_REST = "api_rest"
    API_GRAPHQL = "api_graphql"
    WEB_FORM = "web_form"
    EMAIL = "email"
    WEBHOOK = "webhook"


class SubmissionStatus(Enum):
    """Submission status tracking"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    RETRY_SCHEDULED = "retry_scheduled"
    RATE_LIMITED = "rate_limited"


@dataclass
class PlatformCredentials:
    """Platform API credentials"""
    platform: PlatformType
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    additional_params: Dict[str, Any] = None
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
            self.additional_params = {}


@dataclass
class SubmissionResult:
    """
Platform submission result"""
    platform: PlatformType
    method: SubmissionMethod
    status: SubmissionStatus
    submission_id: Optional[str] = None
    platform_reference: Optional[str] = None
    response_data: Dict[str, Any] = None
    error_message: Optional[str] = None
    submitted_at: datetime = None
    response_received_at: Optional[datetime] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.response_data is None:
            self.response_data = {}
        if self.submitted_at is None:
            self.submitted_at = datetime.utcnow()


class PlatformAdapter:
    """
Base platform adapter interface"""
    
    def __init__(self, platform: PlatformType, credentials: PlatformCredentials):
        self.platform = platform
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimiter(platform)
        
    async def initialize(self) -> bool:
        """
Initialize platform connection"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),
                headers=await self._get_default_headers()
            )
            
            # Authenticate if required
            auth_success = await self._authenticate()
            if not auth_success:
                logger.error(f"Authentication failed for {self.platform.value}")
                return False
            
            logger.info(f"Platform adapter initialized for {self.platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing {self.platform.value} adapter: {e}")
            return False
    
    async def submit_dmca_notice(self, notice_data: Dict[str, Any]) -> SubmissionResult:
        """Submit DMCA notice to platform"""
        # Default implementation for platforms without specific DMCA support
        logger.warning(f"DMCA submission not implemented for {self.platform.value}")
        
        return SubmissionResult(
            submission_id=f"unsupported_{uuid.uuid4().hex[:8]}",
            platform=self.platform,
            status=SubmissionStatus.FAILED,
            message=f"DMCA submission not supported for {self.platform.value}",
            submitted_at=datetime.now(timezone.utc),
            reference_number=None,
            tracking_url=None
        )
    
    async def check_submission_status(self, submission_id: str) -> SubmissionStatus:
        """Check status of submitted DMCA notice"""
        # Default implementation for platforms without status checking
        logger.warning(f"DMCA status checking not implemented for {self.platform.value}")
        return SubmissionStatus.UNKNOWN
    
    async def _authenticate(self) -> bool:
        """Authenticate with platform"""
        return True  # Default implementation
    
    async def _get_default_headers(self) -> Dict[str, str]:
        """
Get default HTTP headers"""
        return {
            'User-Agent': 'IA-Influencer-Agent DMCA System v2.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    async def cleanup(self):
        """
Clean up resources"""
        if self.session:
            await self.session.close()


class YouTubeAdapter(PlatformAdapter):
    """
YouTube platform adapter"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(PlatformType.YOUTUBE, credentials)
        self.api_base = "https://www.googleapis.com/youtube/v3"
        self.copyright_api = "https://youtubei.googleapis.com/youtubei/v1"
    
    async def submit_dmca_notice(self, notice_data: Dict[str, Any]) -> SubmissionResult:
        """Submit DMCA notice to YouTube"""
        
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Prepare YouTube-specific payload
            payload = await self._prepare_youtube_payload(notice_data)
            
            # Submit via Copyright Management API
            url = f"{self.copyright_api}/copyright/claim"
            headers = await self._get_auth_headers()
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    return SubmissionResult(
                        platform=self.platform,
                        method=SubmissionMethod.API_REST,
                        status=SubmissionStatus.SUBMITTED,
                        submission_id=response_data.get('id'),
                        platform_reference=response_data.get('claimId'),
                        response_data=response_data
                    )
                else:
                    return SubmissionResult(
                        platform=self.platform,
                        method=SubmissionMethod.API_REST,
                        status=SubmissionStatus.FAILED,
                        error_message=f"API error: {response.status}",
                        response_data=response_data
                    )
                    
        except Exception as e:
            logger.error(f"YouTube DMCA submission error: {e}")
            return SubmissionResult(
                platform=self.platform,
                method=SubmissionMethod.API_REST,
                status=SubmissionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _prepare_youtube_payload(self, notice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare YouTube-specific DMCA payload"""
        return {
            'videoId': self._extract_video_id(notice_data['infringing_url']),
            'copyrightOwner': notice_data['copyright_owner']['name'],
            'contactEmail': notice_data['copyright_owner']['email'],
            'workDescription': notice_data['original_work']['description'],
            'claimType': 'copyright',
            'policy': 'takedown',
            'evidence': {
                'originalWork': notice_data['original_work']['url'],
                'similarityScore': notice_data['similarity_score'],
                'fingerprintMatch': notice_data['fingerprint_match']
            }
        }
    
    def _extract_video_id(self, url: str) -> str:
        """
Extract YouTube video ID from URL"""
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:v\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authenticated headers for YouTube API"""
        headers = await self._get_default_headers()
        if self.credentials.access_token:
            headers['Authorization'] = f"Bearer {self.credentials.access_token}"
        elif self.credentials.api_key:
            headers['X-API-Key'] = self.credentials.api_key
        return headers


class SpotifyAdapter(PlatformAdapter):
    """Spotify platform adapter"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(PlatformType.SPOTIFY, credentials)
        self.api_base = "https://api.spotify.com/v1"
        self.copyright_email = "copyright@spotify.com"
    
    async def submit_dmca_notice(self, notice_data: Dict[str, Any]) -> SubmissionResult:
        """Submit DMCA notice to Spotify via email"""
        
        try:
            # Spotify primarily uses email for DMCA notices
            from ..email_service import EmailService
            
            email_service = EmailService()
            email_content = await self._prepare_spotify_email(notice_data)
            
            success = await email_service.send_dmca_email(
                to=self.copyright_email,
                subject=f"DMCA Takedown Notice - {notice_data['notice_id']}",
                content=email_content,
                attachments=notice_data.get('evidence_files', [])
            )
            
            if success:
                return SubmissionResult(
                    platform=self.platform,
                    method=SubmissionMethod.EMAIL,
                    status=SubmissionStatus.SUBMITTED,
                    submission_id=f"spotify-{secrets.token_hex(8)}",
                    platform_reference=self.copyright_email
                )
            else:
                return SubmissionResult(
                    platform=self.platform,
                    method=SubmissionMethod.EMAIL,
                    status=SubmissionStatus.FAILED,
                    error_message="Email delivery failed"
                )
                
        except Exception as e:
            logger.error(f"Spotify DMCA submission error: {e}")
            return SubmissionResult(
                platform=self.platform,
                method=SubmissionMethod.EMAIL,
                status=SubmissionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _prepare_spotify_email(self, notice_data: Dict[str, Any]) -> str:
        """Prepare Spotify-specific DMCA email content"""
        
        track_id = self._extract_spotify_track_id(notice_data['infringing_url'])
        
        return f"""
Subject: DMCA Takedown Notice - Track ID: {track_id}

Dear Spotify Copyright Team,

I am submitting this DMCA takedown notice pursuant to the Digital Millennium Copyright Act.

NOTICE DETAILS:
- Notice ID: {notice_data['notice_id']}
- Infringing Track: {notice_data['infringing_url']}
- Track ID: {track_id}
- Original Work: {notice_data['original_work']['url']}
- Similarity: {notice_data['similarity_score']}%

COPYRIGHT OWNER:
{notice_data['copyright_owner']['name']}
{notice_data['copyright_owner']['email']}

Please remove the infringing content expeditiously.

Best regards,
{notice_data['authorized_agent']['name']}
        """
    
    def _extract_spotify_track_id(self, url: str) -> str:
        """
Extract Spotify track ID from URL"""
        import re
        match = re.search(r'track/([a-zA-Z0-9]{22})', url)
        if match:
            return match.group(1)
        raise ValueError(f"Could not extract track ID from URL: {url}")


class InstagramAdapter(PlatformAdapter):
    """Instagram/Meta platform adapter"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(PlatformType.INSTAGRAM, credentials)
        self.api_base = "https://graph.facebook.com/v18.0"
        self.copyright_form_url = "https://help.instagram.com/contact/372592039493026"
    
    async def submit_dmca_notice(self, notice_data: Dict[str, Any]) -> SubmissionResult:
        """Submit DMCA notice to Instagram via web form"""
        
        try:
            # Instagram requires web form submission
            form_submitter = WebFormSubmitter()
            
            form_data = await self._prepare_instagram_form_data(notice_data)
            
            result = await form_submitter.submit_form(
                url=self.copyright_form_url,
                form_data=form_data,
                platform=self.platform
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Instagram DMCA submission error: {e}")
            return SubmissionResult(
                platform=self.platform,
                method=SubmissionMethod.WEB_FORM,
                status=SubmissionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _prepare_instagram_form_data(self, notice_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare Instagram form data"""
        return {
            'full_name': notice_data['copyright_owner']['name'],
            'email': notice_data['copyright_owner']['email'],
            'work_description': notice_data['original_work']['description'],
            'infringing_url': notice_data['infringing_url'],
            'original_work_url': notice_data['original_work']['url'],
            'additional_info': f"Similarity: {notice_data['similarity_score']}%"
        }


class TikTokAdapter(PlatformAdapter):
    """TikTok platform adapter"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(PlatformType.TIKTOK, credentials)
        self.api_base = "https://open-api.tiktok.com/platform/oauth/connect"
        self.copyright_form_url = "https://www.tiktok.com/legal/copyright-policy"
    
    async def submit_dmca_notice(self, notice_data: Dict[str, Any]) -> SubmissionResult:
        """Submit DMCA notice to TikTok"""
        
        try:
            # TikTok uses a combination of API and form submission
            if self.credentials.api_key:
                return await self._submit_via_api(notice_data)
            else:
                return await self._submit_via_form(notice_data)
                
        except Exception as e:
            logger.error(f"TikTok DMCA submission error: {e}")
            return SubmissionResult(
                platform=self.platform,
                method=SubmissionMethod.API_REST,
                status=SubmissionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _submit_via_api(self, notice_data: Dict[str, Any]) -> SubmissionResult:
        """Submit via TikTok API"""
        
        payload = {
            'video_id': self._extract_tiktok_video_id(notice_data['infringing_url']),
            'copyright_owner': notice_data['copyright_owner']['name'],
            'contact_email': notice_data['copyright_owner']['email'],
            'work_description': notice_data['original_work']['description'],
            'claim_type': 'copyright_infringement'
        }
        
        headers = await self._get_auth_headers()
        url = f"{self.api_base}/copyright/report"
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            response_data = await response.json()
            
            if response.status == 200:
                return SubmissionResult(
                    platform=self.platform,
                    method=SubmissionMethod.API_REST,
                    status=SubmissionStatus.SUBMITTED,
                    submission_id=response_data.get('report_id'),
                    response_data=response_data
                )
            else:
                return SubmissionResult(
                    platform=self.platform,
                    method=SubmissionMethod.API_REST,
                    status=SubmissionStatus.FAILED,
                    error_message=f"API error: {response.status}",
                    response_data=response_data
                )
    
    def _extract_tiktok_video_id(self, url: str) -> str:
        """Extract TikTok video ID from URL"""
        import re
        match = re.search(r'/video/(\d+)', url)
        if match:
            return match.group(1)
        raise ValueError(f"Could not extract video ID from URL: {url}")


class WebFormSubmitter:
    """Automated web form submission using Selenium"""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
    
    async def submit_form(self, url: str, form_data: Dict[str, str], 
                         platform: PlatformType) -> SubmissionResult:
        """
Submit DMCA form on web platform"""
        
        try:
            await self._setup_driver()
            
            # Navigate to form
            self.driver.get(url)
            await asyncio.sleep(2)
            
            # Fill form based on platform
            success = await self._fill_platform_form(platform, form_data)
            
            if success:
                return SubmissionResult(
                    platform=platform,
                    method=SubmissionMethod.WEB_FORM,
                    status=SubmissionStatus.SUBMITTED,
                    submission_id=f"form-{secrets.token_hex(8)}",
                    platform_reference=url
                )
            else:
                return SubmissionResult(
                    platform=platform,
                    method=SubmissionMethod.WEB_FORM,
                    status=SubmissionStatus.FAILED,
                    error_message="Form submission failed"
                )
                
        except Exception as e:
            logger.error(f"Web form submission error: {e}")
            return SubmissionResult(
                platform=platform,
                method=SubmissionMethod.WEB_FORM,
                status=SubmissionStatus.FAILED,
                error_message=str(e)
            )
        finally:
            await self._cleanup_driver()
    
    async def _setup_driver(self):
        """Setup Chrome WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 30)
    
    async def _fill_platform_form(self, platform: PlatformType, 
                                 form_data: Dict[str, str]) -> bool:
        """
Fill platform-specific form"""
        
        try:
            if platform == PlatformType.INSTAGRAM:
                return await self._fill_instagram_form(form_data)
            elif platform == PlatformType.TIKTOK:
                return await self._fill_tiktok_form(form_data)
            elif platform == PlatformType.TWITTER:
                return await self._fill_twitter_form(form_data)
            else:
                return await self._fill_generic_form(form_data)
                
        except TimeoutException:
            logger.error(f"Timeout filling {platform.value} form")
            return False
        except WebDriverException as e:
            logger.error(f"WebDriver error filling {platform.value} form: {e}")
            return False
    
    async def _fill_instagram_form(self, form_data: Dict[str, str]) -> bool:
        """Fill Instagram copyright form"""
        
        # Wait for form to load
        name_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, "full_name"))
        )
        
        # Fill form fields
        name_field.send_keys(form_data['full_name'])
        
        email_field = self.driver.find_element(By.NAME, "email")
        email_field.send_keys(form_data['email'])
        
        work_desc = self.driver.find_element(By.NAME, "work_description")
        work_desc.send_keys(form_data['work_description'])
        
        infringing_url = self.driver.find_element(By.NAME, "infringing_url")
        infringing_url.send_keys(form_data['infringing_url'])
        
        # Submit form
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        # Wait for confirmation
        await asyncio.sleep(3)
        
        # Check for success indicators
        success_indicators = [
            "Thank you for your report",
            "Report submitted successfully",
            "We have received your report"
        ]
        
        page_text = self.driver.page_source.lower()
        return any(indicator.lower() in page_text for indicator in success_indicators)
    
    async def _cleanup_driver(self):
        """Clean up WebDriver resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None


class RateLimiter:
    """
Platform-specific rate limiting"""
    
    def __init__(self, platform: PlatformType):
        self.platform = platform
        self.last_request_time: Optional[datetime] = None
        self.request_count = 0
        self.rate_limits = self._get_platform_limits()
    
    def _get_platform_limits(self) -> Dict[str, Any]:
        """
Get platform-specific rate limits"""
        limits = {
            PlatformType.YOUTUBE: {
                'requests_per_minute': 30,
                'requests_per_hour': 1000,
                'min_interval_seconds': 2
            },
            PlatformType.SPOTIFY: {
                'requests_per_minute': 10,
                'requests_per_hour': 100,
                'min_interval_seconds': 6
            },
            PlatformType.INSTAGRAM: {
                'requests_per_minute': 5,
                'requests_per_hour': 50,
                'min_interval_seconds': 12
            },
            PlatformType.TIKTOK: {
                'requests_per_minute': 15,
                'requests_per_hour': 200,
                'min_interval_seconds': 4
            }
        }
        
        return limits.get(self.platform, {
            'requests_per_minute': 10,
            'requests_per_hour': 100,
            'min_interval_seconds': 6
        })
    
    async def wait_if_needed(self):
        """
Wait if rate limit requires it"""
        
        now = datetime.utcnow()
        min_interval = self.rate_limits['min_interval_seconds']
        
        if self.last_request_time:
            time_since_last = (now - self.last_request_time).total_seconds()
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                logger.info(f"Rate limiting: waiting {wait_time:.1f}s for {self.platform.value}")
                await asyncio.sleep(wait_time)
        
        self.last_request_time = datetime.utcnow()
        self.request_count += 1


class MultiPlatformIntegrationEngine:
    """Main engine for multi-platform DMCA submissions"""
    
    def __init__(self):
        self.adapters: Dict[PlatformType, PlatformAdapter] = {}
        self.credentials: Dict[PlatformType, PlatformCredentials] = {}
        self.submission_history: List[SubmissionResult] = []
        
    async def initialize(self, platform_credentials: Dict[PlatformType, PlatformCredentials]):
        """
Initialize all platform adapters"""
        
        self.credentials = platform_credentials
        
        for platform, creds in platform_credentials.items():
            adapter = self._create_adapter(platform, creds)
            
            if adapter and await adapter.initialize():
                self.adapters[platform] = adapter
                logger.info(f"Initialized adapter for {platform.value}")
            else:
                logger.error(f"Failed to initialize adapter for {platform.value}")
    
    def _create_adapter(self, platform: PlatformType, 
                       credentials: PlatformCredentials) -> Optional[PlatformAdapter]:
        """Create platform-specific adapter"""
        
        adapter_map = {
            PlatformType.YOUTUBE: YouTubeAdapter,
            PlatformType.SPOTIFY: SpotifyAdapter,
            PlatformType.INSTAGRAM: InstagramAdapter,
            PlatformType.TIKTOK: TikTokAdapter
        }
        
        adapter_class = adapter_map.get(platform)
        if adapter_class:
            return adapter_class(credentials)
        else:
            logger.warning(f"No adapter available for {platform.value}")
            return None
    
    async def submit_to_platform(self, platform: PlatformType, 
                                notice_data: Dict[str, Any]) -> SubmissionResult:
        """Submit DMCA notice to specific platform"""
        
        adapter = self.adapters.get(platform)
        if not adapter:
            return SubmissionResult(
                platform=platform,
                method=SubmissionMethod.API_REST,
                status=SubmissionStatus.FAILED,
                error_message=f"No adapter available for {platform.value}"
            )
        
        try:
            result = await adapter.submit_dmca_notice(notice_data)
            self.submission_history.append(result)
            
            logger.info(f"DMCA submission to {platform.value}: {result.status.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error submitting to {platform.value}: {e}")
            result = SubmissionResult(
                platform=platform,
                method=SubmissionMethod.API_REST,
                status=SubmissionStatus.FAILED,
                error_message=str(e)
            )
            self.submission_history.append(result)
            return result
    
    async def submit_to_multiple_platforms(self, 
                                         platforms: List[PlatformType],
                                         notice_data: Dict[str, Any]) -> List[SubmissionResult]:
        """Submit DMCA notice to multiple platforms simultaneously"""
        
        tasks = [
            self.submit_to_platform(platform, notice_data)
            for platform in platforms
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(SubmissionResult(
                    platform=platforms[i],
                    method=SubmissionMethod.API_REST,
                    status=SubmissionStatus.FAILED,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def check_submission_status(self, submission_result: SubmissionResult) -> SubmissionStatus:
        """
Check status of a submitted notice"""
        
        adapter = self.adapters.get(submission_result.platform)
        if not adapter or not submission_result.submission_id:
            return SubmissionStatus.FAILED
        
        try:
            return await adapter.check_submission_status(submission_result.submission_id)
        except Exception as e:
            logger.error(f"Error checking status for {submission_result.platform.value}: {e}")
            return SubmissionStatus.FAILED
    
    async def get_submission_statistics(self) -> Dict[str, Any]:
        """Get submission statistics across all platforms"""
        
        if not self.submission_history:
            return {}
        
        stats = {
            'total_submissions': len(self.submission_history),
            'by_platform': {},
            'by_status': {},
            'success_rate': 0.0,
            'average_response_time': None
        }
        
        # Platform statistics
        for result in self.submission_history:
            platform_name = result.platform.value
            if platform_name not in stats['by_platform']:
                stats['by_platform'][platform_name] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0
                }
            
            stats['by_platform'][platform_name]['total'] += 1
            
            if result.status in [SubmissionStatus.SUBMITTED, SubmissionStatus.ACKNOWLEDGED]:
                stats['by_platform'][platform_name]['successful'] += 1
            else:
                stats['by_platform'][platform_name]['failed'] += 1
        
        # Status statistics
        for result in self.submission_history:
            status = result.status.value
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Success rate
        successful = stats['by_status'].get('submitted', 0) + stats['by_status'].get('acknowledged', 0)
        stats['success_rate'] = (successful / len(self.submission_history)) * 100
        
        return stats
    
    async def cleanup(self):
        """
Clean up all adapter resources"""
        
        cleanup_tasks = [
            adapter.cleanup() 
            for adapter in self.adapters.values()
        ]
        
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        self.adapters.clear()
        
        logger.info("Multi-platform integration engine cleaned up")


# Factory functions
def create_platform_credentials(platform: PlatformType, **kwargs) -> PlatformCredentials:
    """Create platform credentials"""
    return PlatformCredentials(platform=platform, **kwargs)


def create_integration_engine() -> MultiPlatformIntegrationEngine:
    """
Create new multi-platform integration engine"""
    return MultiPlatformIntegrationEngine()


__all__ = [
    'MultiPlatformIntegrationEngine',
    'PlatformAdapter',
    'YouTubeAdapter',
    'SpotifyAdapter',
    'InstagramAdapter',
    'TikTokAdapter',
    'WebFormSubmitter',
    'PlatformCredentials',
    'SubmissionResult',
    'PlatformType',
    'SubmissionMethod',
    'SubmissionStatus',
    'RateLimiter',
    'create_platform_credentials',
    'create_integration_engine'
]
