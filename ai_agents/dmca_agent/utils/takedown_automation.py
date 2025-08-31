"""
Takedown Automation - Enterprise DMCA Takedown Processing System
===============================================================

Advanced automated takedown system for multi-platform copyright enforcement
with intelligent escalation, response tracking, and legal compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import aiohttp
import time
from pathlib import Path
import backoff

from ..base import BaseAgent, AgentRequest, AgentResponse
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
from ...utils.email_sender import EmailSender
from ...utils.platform_api_client import PlatformAPIClient
from ...utils.web_scraper import WebScraper
from ...models.dmca import DMCACase, TakedownStatus, PlatformResponse

logger = logging.getLogger(__name__)

class TakedownMethod(Enum):
    """Takedown delivery methods"""
    API_CALL = "api_call"
    EMAIL_FORM = "email_form"
    WEB_FORM = "web_form"
    MANUAL_REVIEW = "manual_review"
    LEGAL_NOTICE = "legal_notice"

class ResponseType(Enum):
    """Platform response types"""
    AUTOMATED_ACK = "automated_acknowledgment"
    HUMAN_REVIEW = "human_review"
    CONTENT_REMOVED = "content_removed"
    COUNTER_NOTICE = "counter_notice"
    DISPUTE = "dispute"
    REJECTED = "rejected"
    NO_RESPONSE = "no_response"

class EscalationLevel(Enum):
    """Escalation levels for takedown processing"""
    STANDARD = "standard"
    PRIORITY = "priority"
    URGENT = "urgent"
    LEGAL_ACTION = "legal_action"

@dataclass
class PlatformConfig:
    """Platform-specific takedown configuration"""
    platform_name: str
    takedown_methods: List[TakedownMethod]
    api_endpoint: Optional[str]
    email_address: Optional[str]
    web_form_url: Optional[str]
    response_time_sla: int  # hours
    success_indicators: List[str]
    rate_limits: Dict[str, int]
    authentication: Dict[str, str]
    headers: Dict[str, str] = field(default_factory=dict)
    
@dataclass 
class TakedownAttempt:
    """Individual takedown attempt record"""
    attempt_id: str
    case_id: str
    platform: str
    method: TakedownMethod
    timestamp: datetime
    status: str
    response_data: Dict[str, Any]
    error_details: Optional[str]
    retry_count: int
    next_retry: Optional[datetime]

@dataclass
class TakedownResult:
    """Complete takedown operation result"""
    case_id: str
    platform: str
    success: bool
    attempts: List[TakedownAttempt]
    final_status: TakedownStatus
    response_received: bool
    compliance_achieved: bool
    escalation_required: bool
    next_actions: List[str]
    total_time: float
    cost_estimate: float

class TakedownAutomation:
    """
    Enterprise Takedown Automation System
    
    Handles automated DMCA takedown processing across multiple platforms
    with intelligent retry logic, escalation management, and compliance tracking.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.email_sender = EmailSender()
        self.api_client = PlatformAPIClient()
        self.web_scraper = WebScraper()
        
        # Platform configurations
        self.platform_configs = self._initialize_platform_configs()
        
        # Success rate tracking
        self.success_rates = {}
        self.response_time_stats = {}
        
        # Rate limiting
        self.rate_limiters = {}
        
        # Retry configurations
        self.max_retries = 5
        self.base_delay = 60  # 1 minute base delay
        self.max_delay = 3600  # 1 hour max delay
        
        self.logger.info("Takedown Automation initialized successfully")
    
    def _initialize_platform_configs(self) -> Dict[str, PlatformConfig]:
        """Initialize platform-specific configurations"""
        configs = {
            "youtube": PlatformConfig(
                platform_name="YouTube",
                takedown_methods=[TakedownMethod.API_CALL, TakedownMethod.WEB_FORM],
                api_endpoint="https://www.googleapis.com/youtube/v3/videos",
                email_address=None,
                web_form_url="https://www.youtube.com/copyright_complaint_form",
                response_time_sla=24,
                success_indicators=["video_removed", "content_disabled", "claim_created"],
                rate_limits={"requests_per_hour": 100, "requests_per_day": 1000},
                authentication={"api_key": "youtube_api_key", "oauth_token": "oauth_token"},
                headers={"User-Agent": "DMCA-Agent/1.0"}
            ),
            
            "tiktok": PlatformConfig(
                platform_name="TikTok",
                takedown_methods=[TakedownMethod.EMAIL_FORM, TakedownMethod.WEB_FORM],
                api_endpoint=None,
                email_address="ip@tiktok.com",
                web_form_url="https://www.tiktok.com/legal/report/copyright",
                response_time_sla=72,
                success_indicators=["content_removed", "account_warned"],
                rate_limits={"requests_per_hour": 20, "requests_per_day": 100},
                authentication={},
                headers={"User-Agent": "DMCA-Agent/1.0"}
            ),
            
            "instagram": PlatformConfig(
                platform_name="Instagram",
                takedown_methods=[TakedownMethod.API_CALL, TakedownMethod.WEB_FORM],
                api_endpoint="https://graph.facebook.com/v18.0",
                email_address=None,
                web_form_url="https://help.instagram.com/contact/372592039493026",
                response_time_sla=48,
                success_indicators=["post_removed", "story_removed", "account_action"],
                rate_limits={"requests_per_hour": 200, "requests_per_day": 2000},
                authentication={"access_token": "facebook_access_token"},
                headers={"User-Agent": "DMCA-Agent/1.0"}
            ),
            
            "twitter": PlatformConfig(
                platform_name="Twitter/X",
                takedown_methods=[TakedownMethod.API_CALL, TakedownMethod.WEB_FORM],
                api_endpoint="https://api.twitter.com/2",
                email_address="copyright@twitter.com",
                web_form_url="https://help.twitter.com/forms/dmca",
                response_time_sla=24,
                success_indicators=["tweet_removed", "account_suspended"],
                rate_limits={"requests_per_hour": 100, "requests_per_day": 500},
                authentication={"bearer_token": "twitter_bearer_token"},
                headers={"User-Agent": "DMCA-Agent/1.0"}
            ),
            
            "facebook": PlatformConfig(
                platform_name="Facebook",
                takedown_methods=[TakedownMethod.API_CALL, TakedownMethod.WEB_FORM],
                api_endpoint="https://graph.facebook.com/v18.0",
                email_address=None,
                web_form_url="https://www.facebook.com/help/contact/634636770043106",
                response_time_sla=48,
                success_indicators=["post_removed", "video_removed", "page_action"],
                rate_limits={"requests_per_hour": 200, "requests_per_day": 2000},
                authentication={"access_token": "facebook_access_token"},
                headers={"User-Agent": "DMCA-Agent/1.0"}
            ),
            
            "twitch": PlatformConfig(
                platform_name="Twitch",
                takedown_methods=[TakedownMethod.EMAIL_FORM, TakedownMethod.WEB_FORM],
                api_endpoint=None,
                email_address="dmca@twitch.tv",
                web_form_url="https://www.twitch.tv/p/en/legal/dmca-guidelines/",
                response_time_sla=72,
                success_indicators=["clip_removed", "vod_removed", "channel_action"],
                rate_limits={"requests_per_hour": 10, "requests_per_day": 50},
                authentication={},
                headers={"User-Agent": "DMCA-Agent/1.0"}
            )
        }
        
        return configs
    
    async def execute_takedown(
        self,
        case_data: Dict[str, Any],
        legal_notice: str,
        priority: EscalationLevel = EscalationLevel.STANDARD
    ) -> TakedownResult:
        """
        Execute automated takedown process
        
        Args:
            case_data: DMCA case information
            legal_notice: Generated legal notice
            priority: Escalation priority level
            
        Returns:
            TakedownResult with complete processing information
        """
        try:
            case_id = case_data.get('case_id', '')
            platform = case_data.get('platform', '').lower()
            
            self.logger.info(f"Starting takedown execution for case {case_id} on {platform}")
            
            # Initialize result
            result = TakedownResult(
                case_id=case_id,
                platform=platform,
                success=False,
                attempts=[],
                final_status=TakedownStatus.PENDING,
                response_received=False,
                compliance_achieved=False,
                escalation_required=False,
                next_actions=[],
                total_time=0.0,
                cost_estimate=0.0
            )
            
            start_time = time.time()
            
            # Get platform configuration
            platform_config = self.platform_configs.get(platform)
            if not platform_config:
                raise ValueError(f"Unsupported platform: {platform}")
            
            # Execute takedown attempts with retry logic
            success = await self._execute_takedown_attempts(
                case_data, legal_notice, platform_config, priority, result
            )
            
            # Check for response and compliance
            if success:
                result.response_received = await self._check_platform_response(
                    case_data, platform_config, result
                )
                
                if result.response_received:
                    result.compliance_achieved = await self._verify_compliance(
                        case_data, platform_config, result
                    )
            
            # Determine final status and next actions
            await self._finalize_takedown_result(result, platform_config, priority)
            
            result.total_time = time.time() - start_time
            result.cost_estimate = await self._calculate_cost_estimate(result)
            
            self.logger.info(f"Takedown execution completed: {result.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"Takedown execution failed: {str(e)}")
            raise
    
    async def _execute_takedown_attempts(
        self,
        case_data: Dict[str, Any],
        legal_notice: str,
        platform_config: PlatformConfig,
        priority: EscalationLevel,
        result: TakedownResult
    ) -> bool:
        """Execute takedown attempts with intelligent retry logic"""
        methods_to_try = self._prioritize_takedown_methods(platform_config, priority)
        
        for method in methods_to_try:
            attempt_success = await self._attempt_takedown_method(
                case_data, legal_notice, platform_config, method, result
            )
            
            if attempt_success:
                result.success = True
                return True
            
            # Wait between methods based on rate limits
            await self._wait_for_rate_limit(platform_config, method)
        
        return False
    
    def _prioritize_takedown_methods(
        self,
        platform_config: PlatformConfig,
        priority: EscalationLevel
    ) -> List[TakedownMethod]:
        """Prioritize takedown methods based on success rates and priority"""
        methods = platform_config.takedown_methods.copy()
        
        # Sort by historical success rate
        platform_name = platform_config.platform_name.lower()
        success_rates = self.success_rates.get(platform_name, {})
        
        methods.sort(
            key=lambda m: success_rates.get(m.value, 0.5),
            reverse=True
        )
        
        # Adjust for priority
        if priority in [EscalationLevel.URGENT, EscalationLevel.LEGAL_ACTION]:
            # Prefer faster methods for urgent cases
            api_methods = [m for m in methods if m == TakedownMethod.API_CALL]
            other_methods = [m for m in methods if m != TakedownMethod.API_CALL]
            methods = api_methods + other_methods
        
        return methods
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=5,
        max_time=3600
    )
    async def _attempt_takedown_method(
        self,
        case_data: Dict[str, Any],
        legal_notice: str,
        platform_config: PlatformConfig,
        method: TakedownMethod,
        result: TakedownResult
    ) -> bool:
        """Attempt takedown using specific method"""
        attempt = TakedownAttempt(
            attempt_id=f"{case_data.get('case_id', '')}_{method.value}_{int(time.time())}",
            case_id=case_data.get('case_id', ''),
            platform=platform_config.platform_name,
            method=method,
            timestamp=datetime.now(),
            status="attempting",
            response_data={},
            error_details=None,
            retry_count=0,
            next_retry=None
        )
        
        try:
            success = False
            
            if method == TakedownMethod.API_CALL:
                success = await self._send_api_takedown(
                    case_data, legal_notice, platform_config, attempt
                )
            elif method == TakedownMethod.EMAIL_FORM:
                success = await self._send_email_takedown(
                    case_data, legal_notice, platform_config, attempt
                )
            elif method == TakedownMethod.WEB_FORM:
                success = await self._send_web_form_takedown(
                    case_data, legal_notice, platform_config, attempt
                )
            
            attempt.status = "success" if success else "failed"
            result.attempts.append(attempt)
            
            # Update success rate statistics
            await self._update_success_statistics(platform_config.platform_name, method, success)
            
            return success
            
        except Exception as e:
            attempt.status = "error"
            attempt.error_details = str(e)
            result.attempts.append(attempt)
            
            self.logger.error(f"Takedown attempt failed: {str(e)}")
            return False
    
    async def _send_api_takedown(
        self,
        case_data: Dict[str, Any],
        legal_notice: str,
        platform_config: PlatformConfig,
        attempt: TakedownAttempt
    ) -> bool:
        """Send takedown via platform API"""
        try:
            if not platform_config.api_endpoint:
                return False
            
            # Prepare API payload
            payload = await self._prepare_api_payload(case_data, legal_notice, platform_config)
            
            # Send API request
            async with aiohttp.ClientSession() as session:
                headers = {**platform_config.headers}
                
                # Add authentication
                auth_headers = await self._get_auth_headers(platform_config)
                headers.update(auth_headers)
                
                async with session.post(
                    platform_config.api_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.json()
                    attempt.response_data = response_data
                    
                    # Check for success indicators
                    success = await self._check_api_success(
                        response_data, platform_config.success_indicators
                    )
                    
                    return success
                    
        except Exception as e:
            self.logger.error(f"API takedown failed: {str(e)}")
            return False
    
    async def _send_email_takedown(
        self,
        case_data: Dict[str, Any],
        legal_notice: str,
        platform_config: PlatformConfig,
        attempt: TakedownAttempt
    ) -> bool:
        """Send takedown via email"""
        try:
            if not platform_config.email_address:
                return False
            
            # Prepare email
            subject = f"DMCA Takedown Notice - {case_data.get('case_id', '')}"
            
            attachments = await self._prepare_email_attachments(case_data)
            
            # Send email
            email_sent = await self.email_sender.send_legal_notice(
                to_address=platform_config.email_address,
                subject=subject,
                body=legal_notice,
                attachments=attachments
            )
            
            attempt.response_data = {"email_sent": email_sent}
            
            return email_sent
            
        except Exception as e:
            self.logger.error(f"Email takedown failed: {str(e)}")
            return False
    
    async def _send_web_form_takedown(
        self,
        case_data: Dict[str, Any],
        legal_notice: str,
        platform_config: PlatformConfig,
        attempt: TakedownAttempt
    ) -> bool:
        """Send takedown via web form"""
        try:
            if not platform_config.web_form_url:
                return False
            
            # Prepare form data
            form_data = await self._prepare_form_data(case_data, legal_notice, platform_config)
            
            # Submit form using web scraper
            submission_result = await self.web_scraper.submit_dmca_form(
                platform_config.web_form_url,
                form_data,
                platform_config.headers
            )
            
            attempt.response_data = submission_result
            
            # Check if submission was successful
            success = submission_result.get("success", False)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Web form takedown failed: {str(e)}")
            return False
    
    async def _prepare_api_payload(
        self,
        case_data: Dict[str, Any],
        legal_notice: str,
        platform_config: PlatformConfig
    ) -> Dict[str, Any]:
        """Prepare API payload for specific platform"""
        platform_name = platform_config.platform_name.lower()
        
        if platform_name == "youtube":
            return {
                "contentId": case_data.get("content_id"),
                "reason": "copyright",
                "description": legal_notice[:1000],  # YouTube has character limits
                "urls": case_data.get("infringing_urls", [])
            }
        elif platform_name == "instagram" or platform_name == "facebook":
            return {
                "object_id": case_data.get("content_id"),
                "ip_report_category": "copyright",
                "description": legal_notice,
                "evidence_urls": case_data.get("evidence_urls", [])
            }
        elif platform_name == "twitter":
            return {
                "tweet_id": case_data.get("content_id"),
                "category": "copyright",
                "description": legal_notice[:280],  # Twitter character limit
                "media_urls": case_data.get("infringing_urls", [])
            }
        else:
            # Generic payload
            return {
                "content_id": case_data.get("content_id"),
                "type": "copyright_claim",
                "notice": legal_notice,
                "urls": case_data.get("infringing_urls", [])
            }
    
    async def _get_auth_headers(self, platform_config: PlatformConfig) -> Dict[str, str]:
        """Get authentication headers for platform API"""
        headers = {}
        auth = platform_config.authentication
        
        if "api_key" in auth:
            headers["X-API-Key"] = auth["api_key"]
        
        if "bearer_token" in auth:
            headers["Authorization"] = f"Bearer {auth['bearer_token']}"
        
        if "access_token" in auth:
            headers["Authorization"] = f"Bearer {auth['access_token']}"
        
        if "oauth_token" in auth:
            headers["Authorization"] = f"OAuth {auth['oauth_token']}"
        
        return headers
    
    async def _check_api_success(
        self,
        response_data: Dict[str, Any],
        success_indicators: List[str]
    ) -> bool:
        """Check if API response indicates success"""
        response_str = json.dumps(response_data).lower()
        
        for indicator in success_indicators:
            if indicator.lower() in response_str:
                return True
        
        # Also check common success patterns
        if response_data.get("success") is True:
            return True
        
        if response_data.get("status") in ["success", "accepted", "processed"]:
            return True
        
        return False
    
    async def _prepare_email_attachments(
        self,
        case_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prepare email attachments for DMCA notice"""
        attachments = []
        
        # Add evidence files if available
        evidence_files = case_data.get("evidence_files", [])
        for file_info in evidence_files:
            if isinstance(file_info, dict):
                attachments.append({
                    "filename": file_info.get("filename"),
                    "content": file_info.get("content"),
                    "content_type": file_info.get("content_type", "application/octet-stream")
                })
        
        return attachments
    
    async def _prepare_form_data(
        self,
        case_data: Dict[str, Any],
        legal_notice: str,
        platform_config: PlatformConfig
    ) -> Dict[str, str]:
        """Prepare form data for web form submission"""
        form_data = {
            "copyright_owner": case_data.get("copyright_owner_name", ""),
            "email": case_data.get("contact_email", ""),
            "description": case_data.get("copyrighted_work_identification", ""),
            "infringing_url": case_data.get("infringing_url", ""),
            "legal_notice": legal_notice
        }
        
        # Platform-specific form field mappings
        platform_name = platform_config.platform_name.lower()
        
        if platform_name == "youtube":
            form_data.update({
                "product": "youtube",
                "issue": "copyright_infringement"
            })
        elif platform_name == "tiktok":
            form_data.update({
                "report_type": "copyright",
                "content_type": "video"
            })
        
        return form_data
    
    async def _wait_for_rate_limit(
        self,
        platform_config: PlatformConfig,
        method: TakedownMethod
    ) -> None:
        """Wait for rate limit compliance"""
        platform_name = platform_config.platform_name.lower()
        rate_limits = platform_config.rate_limits
        
        # Calculate wait time based on rate limits
        if "requests_per_hour" in rate_limits:
            min_interval = 3600 / rate_limits["requests_per_hour"]
            await asyncio.sleep(min_interval)
    
    async def _check_platform_response(
        self,
        case_data: Dict[str, Any],
        platform_config: PlatformConfig,
        result: TakedownResult
    ) -> bool:
        """Check for platform response to takedown notice"""
        try:
            # Wait for expected response time
            await asyncio.sleep(min(300, platform_config.response_time_sla * 60))  # Max 5 min for test
            
            # Check various response channels
            response_found = False
            
            # Check email responses
            if platform_config.email_address:
                email_response = await self._check_email_responses(case_data["case_id"])
                if email_response:
                    result.response_received = True
                    response_found = True
            
            # Check API status
            if platform_config.api_endpoint:
                api_status = await self._check_api_status(case_data, platform_config)
                if api_status:
                    result.response_received = True
                    response_found = True
            
            # Check content status
            content_status = await self._check_content_status(case_data)
            if content_status.get("removed") or content_status.get("restricted"):
                result.response_received = True
                response_found = True
            
            return response_found
            
        except Exception as e:
            self.logger.error(f"Response check failed: {str(e)}")
            return False
    
    async def _verify_compliance(
        self,
        case_data: Dict[str, Any],
        platform_config: PlatformConfig,
        result: TakedownResult
    ) -> bool:
        """Verify if platform complied with takedown notice"""
        try:
            # Check if infringing content is still accessible
            infringing_urls = case_data.get("infringing_urls", [])
            if isinstance(infringing_urls, str):
                infringing_urls = [infringing_urls]
            
            compliance_count = 0
            total_urls = len(infringing_urls)
            
            for url in infringing_urls:
                is_removed = await self._check_url_accessibility(url)
                if not is_removed:  # Content is no longer accessible
                    compliance_count += 1
            
            # Consider compliant if majority of content is removed
            compliance_rate = compliance_count / total_urls if total_urls > 0 else 0
            
            return compliance_rate >= 0.8  # 80% compliance threshold
            
        except Exception as e:
            self.logger.error(f"Compliance verification failed: {str(e)}")
            return False
    
    async def _finalize_takedown_result(
        self,
        result: TakedownResult,
        platform_config: PlatformConfig,
        priority: EscalationLevel
    ) -> None:
        """Finalize takedown result and determine next actions"""
        if result.success and result.compliance_achieved:
            result.final_status = TakedownStatus.COMPLIED
            result.next_actions = ["Monitor for re-uploads", "Update success metrics"]
        
        elif result.success and result.response_received:
            result.final_status = TakedownStatus.ACKNOWLEDGED
            result.next_actions = ["Wait for compliance", "Follow up if needed"]
        
        elif result.success:
            result.final_status = TakedownStatus.SENT
            result.next_actions = ["Monitor for response", "Escalate if no response"]
        
        else:
            result.final_status = TakedownStatus.FAILED
            result.escalation_required = True
            
            if priority == EscalationLevel.STANDARD:
                result.next_actions = ["Retry with different method", "Escalate to priority"]
            else:
                result.next_actions = ["Manual review required", "Consider legal action"]
    
    async def _update_success_statistics(
        self,
        platform: str,
        method: TakedownMethod,
        success: bool
    ) -> None:
        """Update success rate statistics for platform/method combination"""
        platform_key = platform.lower()
        method_key = method.value
        
        if platform_key not in self.success_rates:
            self.success_rates[platform_key] = {}
        
        if method_key not in self.success_rates[platform_key]:
            self.success_rates[platform_key][method_key] = {"successes": 0, "attempts": 0}
        
        stats = self.success_rates[platform_key][method_key]
        stats["attempts"] += 1
        
        if success:
            stats["successes"] += 1
    
    async def _calculate_cost_estimate(self, result: TakedownResult) -> float:
        """Calculate cost estimate for takedown process"""
        base_cost = 10.0  # Base processing cost
        
        # Add costs per attempt
        attempt_cost = len(result.attempts) * 5.0
        
        # Add escalation costs
        if result.escalation_required:
            attempt_cost += 50.0
        
        # Add time-based costs
        time_cost = result.total_time / 3600 * 25.0  # $25 per hour
        
        return base_cost + attempt_cost + time_cost
    
    async def _check_email_responses(self, case_id: str) -> bool:
        """Check for email responses from platforms"""
        # Implement email checking logic
        return False  # Placeholder
    
    async def _check_api_status(
        self,
        case_data: Dict[str, Any],
        platform_config: PlatformConfig
    ) -> bool:
        """Check API status for takedown progress"""
        # Implement API status checking logic
        return False  # Placeholder
    
    async def _check_content_status(self, case_data: Dict[str, Any]) -> Dict[str, bool]:
        """Check if infringing content is still accessible"""
        # Implement content status checking logic
        return {"removed": False, "restricted": False}  # Placeholder
    
    async def _check_url_accessibility(self, url: str) -> bool:
        """Check if URL is still accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return response.status == 200
        except:
            return False  # Assume removed if not accessible
    
    async def get_platform_statistics(self) -> Dict[str, Any]:
        """Get comprehensive platform statistics"""
        stats = {}
        
        for platform, methods in self.success_rates.items():
            platform_stats = {
                "platform": platform,
                "methods": {},
                "overall_success_rate": 0.0,
                "total_attempts": 0
            }
            
            total_successes = 0
            total_attempts = 0
            
            for method, data in methods.items():
                successes = data["successes"]
                attempts = data["attempts"]
                success_rate = (successes / attempts) if attempts > 0 else 0.0
                
                platform_stats["methods"][method] = {
                    "success_rate": success_rate,
                    "attempts": attempts,
                    "successes": successes
                }
                
                total_successes += successes
                total_attempts += attempts
            
            platform_stats["overall_success_rate"] = (
                total_successes / total_attempts
            ) if total_attempts > 0 else 0.0
            platform_stats["total_attempts"] = total_attempts
            
            stats[platform] = platform_stats
        
        return stats
    
    async def batch_execute_takedowns(
        self,
        cases: List[Dict[str, Any]],
        legal_notices: List[str],
        priority: EscalationLevel = EscalationLevel.STANDARD
    ) -> List[TakedownResult]:
        """Execute multiple takedowns in batch with concurrency control"""
        max_concurrent = 5  # Limit concurrent executions
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single(case_data, legal_notice):
            async with semaphore:
                return await self.execute_takedown(case_data, legal_notice, priority)
        
        tasks = [
            execute_single(case, notice)
            for case, notice in zip(cases, legal_notices)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch execution failed for case {i}: {str(result)}")
            else:
                valid_results.append(result)
        
        return valid_results
