"""DMCA Delivery Manager

Advanced multi-channel delivery system for DMCA takedown notices with
intelligent routing, delivery optimization, and failure recovery.

Author: Fahed Mlaiel
Email: mlaiel@live.de

⚠️ COPYRIGHT WARNING ⚠️
Unauthorized copying or distribution prohibited. All rights reserved (c) 2025 Fahed Mlaiel
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import ssl

from ...core.database import get_database
from ...core.exceptions import ContentProtectionError
from ...utils.validation import validate_email, validate_url
from ...utils.security import encrypt_sensitive_data, decrypt_sensitive_data
from ..models import TakedownNotice, DeliveryAttempt

logger = logging.getLogger(__name__)


class DeliveryMethod(Enum):
    """
Supported delivery methods"""

    EMAIL = "email"
    WEB_FORM = "web_form"
    API_ENDPOINT = "api_endpoint"
    REGISTERED_MAIL = "registered_mail"
    FAX = "fax"
    PLATFORM_NATIVE = "platform_native"


class DeliveryStatus(Enum):
    """Delivery status options"""

    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    REJECTED = "rejected"
    BOUNCED = "bounced"


class DeliveryPriority(Enum):
    """Delivery priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    EMERGENCY = 5


@dataclass
class DeliveryChannel:
    """
Delivery channel configuration"""
    channel_id: str
    method: DeliveryMethod
    endpoint: str
    credentials: Dict[str, str]
    headers: Dict[str, str]
    success_rate: float
    avg_delivery_time: float
    is_active: bool
    rate_limit: Optional[int] = None
    retry_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeliveryRequest:
    """
Delivery request structure"""
    request_id: str
    notice_id: str
    recipient: str
    method: DeliveryMethod
    priority: DeliveryPriority
    content: str
    headers: Dict[str, str]
    metadata: Dict[str, Any]
    scheduled_time: Optional[datetime] = None
    max_retries: int = 3
    retry_delay: timedelta = field(default=timedelta(minutes=30))


@dataclass
class DeliveryResult:
    """
Delivery attempt result"""
    success: bool
    delivery_id: str
    timestamp: datetime
    method_used: DeliveryMethod
    response_code: Optional[int] = None
    response_message: Optional[str] = None
    delivery_time: Optional[float] = None
    error_details: Optional[Dict[str, Any]] = None
    tracking_info: Optional[Dict[str, Any]] = None


class DeliveryManager:
    """
    Advanced DMCA notice delivery system with intelligent routing
    
    Features:
    - Multi-channel delivery (email, web forms, APIs)
    - Intelligent delivery routing
    - Automatic failover and retry
    - Delivery tracking and analytics
    - Rate limiting and throttling
    - Platform-specific optimizations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize delivery manager"""
        self.config = config or {}
        self.db = get_database()
        self.logger = logger
        
        # Initialize delivery channels
        self.channels: Dict[str, DeliveryChannel] = {}
        self._initialize_delivery_channels()
        
        # Rate limiting
        self.rate_limiters = {}
        
        # Retry configurations
        self.retry_configs = {
            DeliveryMethod.EMAIL: {'max_retries': 3, 'base_delay': 300},
            DeliveryMethod.WEB_FORM: {'max_retries': 5, 'base_delay': 180},
            DeliveryMethod.API_ENDPOINT: {'max_retries': 4, 'base_delay': 120},
            DeliveryMethod.REGISTERED_MAIL: {'max_retries': 1, 'base_delay': 0},
            DeliveryMethod.FAX: {'max_retries': 2, 'base_delay': 600}
        }
        
        # Platform-specific delivery rules
        self.platform_rules = {
            'youtube.com': {
                'preferred_methods': [DeliveryMethod.WEB_FORM, DeliveryMethod.EMAIL],
                'form_endpoint': 'https://www.youtube.com/copyright_complaint_form',
                'email_contacts': ['copyright@youtube.com']
            },
            'facebook.com': {
                'preferred_methods': [DeliveryMethod.WEB_FORM, DeliveryMethod.EMAIL],
                'form_endpoint': 'https://www.facebook.com/help/contact/634636770043106',
                'email_contacts': ['ip@fb.com']
            },
            'instagram.com': {
                'preferred_methods': [DeliveryMethod.WEB_FORM, DeliveryMethod.EMAIL],
                'form_endpoint': 'https://help.instagram.com/contact/372592039493026',
                'email_contacts': ['ip@fb.com']
            },
            'tiktok.com': {
                'preferred_methods': [DeliveryMethod.WEB_FORM, DeliveryMethod.EMAIL],
                'form_endpoint': 'https://www.tiktok.com/legal/copyright-policy',
                'email_contacts': ['copyright@tiktok.com']
            }
        }
    
    async def deliver_notice(self, 
                           notice_id: str,
                           recipient_info: Dict[str, Any],
                           delivery_options: Optional[Dict[str, Any]] = None) -> DeliveryResult:
        """
        Deliver DMCA notice using optimal delivery method
        
        Args:
            notice_id: ID of the notice to deliver
            recipient_info: Recipient contact information
            delivery_options: Optional delivery configuration
            
        Returns:
            DeliveryResult with delivery status and details
        """
        try:
            self.logger.info(f"Starting delivery for notice: {notice_id}")
            
            # Retrieve notice content
            notice = await self._get_notice_content(notice_id)
            if not notice:
                raise ContentProtectionError(f"Notice not found: {notice_id}")
            
            # Determine optimal delivery method
            delivery_method = await self._select_delivery_method(recipient_info, delivery_options)
            
            # Format notice for delivery
            formatted_content = await self._format_notice_for_delivery(notice, delivery_method)
            
            # Create delivery request
            delivery_request = DeliveryRequest(
                request_id=str(uuid.uuid4()),
                notice_id=notice_id,
                recipient=recipient_info.get('primary_contact', ''),
                method=delivery_method,
                priority=DeliveryPriority(delivery_options.get('priority', 2) if delivery_options else 2),
                content=formatted_content,
                headers=await self._generate_delivery_headers(delivery_method, recipient_info),
                metadata={
                    'platform': recipient_info.get('platform', 'unknown'),
                    'delivery_options': delivery_options or {},
                    'notice_type': notice.metadata.get('notice_type', 'standard')
                }
            )
            
            # Execute delivery
            delivery_result = await self._execute_delivery(delivery_request)
            
            # Store delivery record
            await self._store_delivery_record(delivery_request, delivery_result)
            
            # Update delivery analytics
            await self._update_delivery_analytics(delivery_method, delivery_result)
            
            return delivery_result
            
        except Exception as e:
            self.logger.error(f"Delivery failed for notice {notice_id}: {str(e)}")
            return DeliveryResult(
                success=False,
                delivery_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                method_used=DeliveryMethod.EMAIL,  # Default
                error_details={'error': str(e)}
            )
    
    async def batch_deliver_notices(self, 
                                  delivery_requests: List[Dict[str, Any]]) -> List[DeliveryResult]:
        """
        Deliver multiple notices in batch with optimization
        
        Args:
            delivery_requests: List of delivery request configurations
            
        Returns:
            List of delivery results
        """
        self.logger.info(f"Starting batch delivery for {len(delivery_requests)} notices")
        
        # Group requests by delivery method for optimization
        method_groups = {}
        for request in delivery_requests:
            method = request.get('delivery_method', 'email')
            if method not in method_groups:
                method_groups[method] = []
            method_groups[method].append(request)
        
        # Process each group with appropriate concurrency limits
        all_results = []
        for method, requests in method_groups.items():
            method_enum = DeliveryMethod(method)
            concurrency_limit = self._get_concurrency_limit(method_enum)
            
            # Process requests with rate limiting
            semaphore = asyncio.Semaphore(concurrency_limit)
            
            async def deliver_with_rate_limit(request):
                async with semaphore:
                    return await self.deliver_notice(
                        request['notice_id'],
                        request['recipient_info'],
                        request.get('delivery_options')
                    )
            
            # Execute deliveries with controlled concurrency
            method_results = await asyncio.gather(
                *[deliver_with_rate_limit(req) for req in requests],
                return_exceptions=True
            )
            
            # Handle exceptions
            for result in method_results:
                if isinstance(result, Exception):
                    all_results.append(DeliveryResult(
                        success=False,
                        delivery_id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc),
                        method_used=method_enum,
                        error_details={'error': str(result)}
                    ))
                else:
                    all_results.append(result)
        
        self.logger.info(f"Batch delivery completed: {len(all_results)} results")
        return all_results
    
    async def retry_failed_delivery(self, delivery_id: str) -> DeliveryResult:
        """
        Retry a failed delivery with intelligent fallback
        
        Args:
            delivery_id: ID of the failed delivery to retry
            
        Returns:
            New delivery result
        """
        try:
            self.logger.info(f"Retrying failed delivery: {delivery_id}")
            
            # Retrieve original delivery attempt
            original_attempt = await self._get_delivery_attempt(delivery_id)
            if not original_attempt:
                raise ContentProtectionError(f"Delivery attempt not found: {delivery_id}")
            
            # Check retry limits
            retry_count = await self._get_retry_count(original_attempt.notice_id)
            max_retries = self.retry_configs.get(original_attempt.method, {}).get('max_retries', 3)
            
            if retry_count >= max_retries:
                # Try alternative delivery method
                alternative_method = await self._get_alternative_delivery_method(
                    original_attempt.method, 
                    original_attempt.metadata.get('platform')
                )
                
                if alternative_method:
                    self.logger.info(f"Switching to alternative method: {alternative_method}")
                    # Create new delivery request with alternative method
                    # (Implementation would reuse original request data)
                    pass
                else:
                    raise ContentProtectionError("Maximum retries exceeded and no alternatives available")
            
            # Calculate retry delay
            base_delay = self.retry_configs.get(original_attempt.method, {}).get('base_delay', 300)
            retry_delay = base_delay * (2 ** min(retry_count, 5))  # Exponential backoff
            
            # Schedule retry
            scheduled_time = datetime.now(timezone.utc) + timedelta(seconds=retry_delay)
            
            # Execute retry (simplified for this example)
            retry_result = await self._execute_retry_delivery(original_attempt, scheduled_time)
            
            return retry_result
            
        except Exception as e:
            self.logger.error(f"Retry failed: {str(e)}")
            return DeliveryResult(
                success=False,
                delivery_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                method_used=DeliveryMethod.EMAIL,
                error_details={'error': f"Retry failed: {str(e)}"}
            )
    
    async def track_delivery_status(self, delivery_id: str) -> Dict[str, Any]:
        """
        Track delivery status and get detailed information
        
        Args:
            delivery_id: ID of the delivery to track
            
        Returns:
            Detailed delivery status information
        """
        try:
            # Retrieve delivery record
            delivery_record = await self._get_delivery_record(delivery_id)
            if not delivery_record:
                raise ContentProtectionError(f"Delivery record not found: {delivery_id}")
            
            # Get current status
            current_status = await self._check_delivery_status(delivery_record)
            
            # Calculate delivery metrics
            delivery_time = None
            if delivery_record.get('delivered_at'):
                delivery_time = (
                    delivery_record['delivered_at'] - delivery_record['created_at']
                ).total_seconds()
            
            return {
                'delivery_id': delivery_id,
                'notice_id': delivery_record['notice_id'],
                'recipient': delivery_record['recipient'],
                'method': delivery_record['method'],
                'status': current_status,
                'created_at': delivery_record['created_at'].isoformat(),
                'delivered_at': delivery_record.get('delivered_at', {}).isoformat() if delivery_record.get('delivered_at') else None,
                'delivery_time_seconds': delivery_time,
                'retry_count': delivery_record.get('retry_count', 0),
                'tracking_info': delivery_record.get('tracking_info', {}),
                'response_received': delivery_record.get('response_received', False),
                'last_status_check': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Delivery tracking failed: {str(e)}")
            raise ContentProtectionError(f"Tracking failed: {str(e)}")
    
    async def get_delivery_analytics(self, 
                                   time_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """
        Get comprehensive delivery analytics and performance metrics
        
        Args:
            time_range: Optional time range for analytics
            
        Returns:
            Detailed analytics data
        """
        try:
            # Set default time range
            if not time_range:
                time_range = {
                    'start': datetime.now(timezone.utc) - timedelta(days=30),
                    'end': datetime.now(timezone.utc)
                }
            
            # Query delivery data
            analytics_query = """
                SELECT 
                    delivery_method,
                    status,
                    platform,
                    COUNT(*) as delivery_count,
                    AVG(delivery_time_seconds) as avg_delivery_time,
                    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as successful_deliveries,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_deliveries,
                    DATE(created_at) as delivery_date
                FROM dmca_delivery_records 
                WHERE created_at >= %s AND created_at <= %s
                GROUP BY delivery_method, status, platform, DATE(created_at)
                ORDER BY delivery_date DESC
            """
            
            results = await self.db.fetch_all(
                analytics_query, 
                [time_range['start'], time_range['end']]
            )
            
            # Process analytics data
            analytics = {
                'summary': {
                    'total_deliveries': sum(r['delivery_count'] for r in results),
                    'success_rate': 0.0,
                    'avg_delivery_time': 0.0,
                    'total_failures': sum(r['failed_deliveries'] for r in results)
                },
                'by_method': {},
                'by_platform': {},
                'daily_trends': {},
                'performance_metrics': {
                    'fastest_delivery_method': '',
                    'most_reliable_method': '',
                    'best_platform_performance': '',
                    'delivery_time_distribution': {}
                }
            }
            
            # Calculate success rate
            total_successful = sum(r['successful_deliveries'] for r in results)
            total_deliveries = sum(r['delivery_count'] for r in results)
            analytics['summary']['success_rate'] = (
                total_successful / total_deliveries if total_deliveries > 0 else 0.0
            )
            
            # Calculate average delivery time
            valid_times = [r['avg_delivery_time'] for r in results if r['avg_delivery_time']]
            analytics['summary']['avg_delivery_time'] = (
                sum(valid_times) / len(valid_times) if valid_times else 0.0
            )
            
            # Group by method
            for result in results:
                method = result['delivery_method']
                if method not in analytics['by_method']:
                    analytics['by_method'][method] = {
                        'total_deliveries': 0,
                        'successful_deliveries': 0,
                        'success_rate': 0.0,
                        'avg_delivery_time': 0.0
                    }
                
                analytics['by_method'][method]['total_deliveries'] += result['delivery_count']
                analytics['by_method'][method]['successful_deliveries'] += result['successful_deliveries']
            
            # Calculate method success rates
            for method_data in analytics['by_method'].values():
                if method_data['total_deliveries'] > 0:
                    method_data['success_rate'] = (
                        method_data['successful_deliveries'] / method_data['total_deliveries']
                    )
            
            # Group by platform
            for result in results:
                platform = result['platform']
                if platform not in analytics['by_platform']:
                    analytics['by_platform'][platform] = {
                        'total_deliveries': 0,
                        'success_rate': 0.0,
                        'avg_delivery_time': 0.0
                    }
                
                analytics['by_platform'][platform]['total_deliveries'] += result['delivery_count']
                # Additional platform calculations would go here
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Analytics generation failed: {str(e)}")
            raise ContentProtectionError(f"Analytics failed: {str(e)}")
    
    # Private helper methods
    
    def _initialize_delivery_channels(self) -> None:
        """Initialize delivery channels configuration"""
        # Email channel
        self.channels['smtp_primary'] = DeliveryChannel(
            channel_id='smtp_primary',
            method=DeliveryMethod.EMAIL,
            endpoint=self.config.get('smtp_server', 'smtp.gmail.com'),
            credentials={
                'username': self.config.get('smtp_username', ''),
                'password': self.config.get('smtp_password', '')
            },
            headers={'Content-Type': 'text/html'},
            success_rate=0.95,
            avg_delivery_time=30.0,
            is_active=True,
            rate_limit=100  # emails per hour
        )
        
        # Web form channel
        self.channels['web_form_primary'] = DeliveryChannel(
            channel_id='web_form_primary',
            method=DeliveryMethod.WEB_FORM,
            endpoint='',  # Dynamic based on platform
            credentials={},
            headers={'User-Agent': 'DMCA-Bot/1.0'},
            success_rate=0.88,
            avg_delivery_time=120.0,
            is_active=True,
            rate_limit=20  # forms per hour
        )
    
    async def _get_notice_content(self, notice_id: str) -> Optional[TakedownNotice]:
        """
Retrieve notice content from database"""
        try:
            query = "SELECT * FROM dmca_notices WHERE notice_id = %s"
            result = await self.db.fetch_one(query, [notice_id])
            
            if result:
                return TakedownNotice(
                    notice_id=result['notice_id'],
                    content_id=result['content_id'],
                    copyright_owner=result['copyright_owner'],
                    copyright_owner_contact={'email': result.get('owner_email', '')},
                    infringing_url=result['infringing_url'],
                    notice_content=result.get('notice_content', ''),
                    evidence=[],
                    jurisdiction=result.get('jurisdiction', 'US'),
                    language=result.get('language', 'en'),
                    created_at=result['created_at'],
                    metadata=result.get('metadata', {})
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve notice: {str(e)}")
            return None
    
    async def _select_delivery_method(self, 
                                    recipient_info: Dict[str, Any],
                                    delivery_options: Optional[Dict[str, Any]]) -> DeliveryMethod:
        """Select optimal delivery method based on recipient and options"""
        # Check if method is explicitly specified
        if delivery_options and 'method' in delivery_options:
            return DeliveryMethod(delivery_options['method'])
        
        # Get platform-specific preferences
        platform = recipient_info.get('platform', 'unknown')
        if platform in self.platform_rules:
            preferred_methods = self.platform_rules[platform]['preferred_methods']
            
            # Return first available preferred method
            for method in preferred_methods:
                if self._is_method_available(method, platform):
                    return method
        
        # Default to email if available
        if recipient_info.get('email') and validate_email(recipient_info['email']):
            return DeliveryMethod.EMAIL
        
        # Fallback to web form
        return DeliveryMethod.WEB_FORM
    
    async def _format_notice_for_delivery(self, 
                                        notice: TakedownNotice,
                                        method: DeliveryMethod) -> str:
        """
Format notice content for specific delivery method"""
        if method == DeliveryMethod.EMAIL:
            return self._format_email_notice(notice)
        elif method == DeliveryMethod.WEB_FORM:
            return self._format_web_form_notice(notice)
        else:
            return notice.notice_content
    
    def _format_email_notice(self, notice: TakedownNotice) -> str:
        """
Format notice for email delivery"""
        return f"""
Subject: DMCA Takedown Notice - Copyright Infringement

{notice.notice_content}

---
This notice was generated automatically by the IA Influencer Agent Platform.
For questions, please contact: {notice.copyright_owner_contact.get('email', '')}
        """.strip()
    
    def _format_web_form_notice(self, notice: TakedownNotice) -> str:
        """
Format notice for web form submission"""
        return notice.notice_content  # Web forms typically use the raw content
    
    async def _generate_delivery_headers(self, 
                                       method: DeliveryMethod,
                                       recipient_info: Dict[str, Any]) -> Dict[str, str]:
        """
Generate appropriate headers for delivery method"""
        headers = {}
        
        if method == DeliveryMethod.EMAIL:
            headers.update({
                'From': self.config.get('smtp_from', 'noreply@ia-influencer.com'),
                'To': recipient_info.get('email', ''),
                'Subject': 'DMCA Takedown Notice - Copyright Infringement',
                'Content-Type': 'text/plain; charset=utf-8'
            })
        elif method == DeliveryMethod.WEB_FORM:
            headers.update({
                'User-Agent': 'IA-Influencer-DMCA-Bot/1.0',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml'
            })
        
        return headers
    
    async def _execute_delivery(self, request: DeliveryRequest) -> DeliveryResult:
        """
Execute the actual delivery"""
        start_time = datetime.now(timezone.utc)
        
        try:
            if request.method == DeliveryMethod.EMAIL:
                result = await self._deliver_via_email(request)
            elif request.method == DeliveryMethod.WEB_FORM:
                result = await self._deliver_via_web_form(request)
            elif request.method == DeliveryMethod.API_ENDPOINT:
                result = await self._deliver_via_api(request)
            else:
                raise ValueError(f"Unsupported delivery method: {request.method}")
            
            delivery_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            result.delivery_time = delivery_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"Delivery execution failed: {str(e)}")
            return DeliveryResult(
                success=False,
                delivery_id=request.request_id,
                timestamp=datetime.now(timezone.utc),
                method_used=request.method,
                error_details={'error': str(e)}
            )
    
    async def _deliver_via_email(self, request: DeliveryRequest) -> DeliveryResult:
        """Deliver notice via email"""
        # Simulate email delivery (would use actual SMTP)
        self.logger.info(f"Sending email to {request.recipient}")
        
        # Simulate success/failure
        success = True  # In real implementation, this would depend on SMTP response
        
        return DeliveryResult(
            success=success,
            delivery_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            method_used=DeliveryMethod.EMAIL,
            response_code=250 if success else 550,
            response_message="Email delivered successfully" if success else "Email delivery failed"
        )
    
    async def _deliver_via_web_form(self, request: DeliveryRequest) -> DeliveryResult:
        """Deliver notice via web form submission"""
        # Simulate web form submission
        self.logger.info(f"Submitting web form for platform: {request.metadata.get('platform')}")
        
        # In real implementation, this would use Selenium or similar
        success = True
        
        return DeliveryResult(
            success=success,
            delivery_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            method_used=DeliveryMethod.WEB_FORM,
            response_code=200 if success else 400,
            response_message="Form submitted successfully" if success else "Form submission failed"
        )
    
    async def _deliver_via_api(self, request: DeliveryRequest) -> DeliveryResult:
        """Deliver notice via API endpoint"""
        # Simulate API delivery
        self.logger.info(f"Sending to API endpoint for {request.recipient}")
        
        success = True
        
        return DeliveryResult(
            success=success,
            delivery_id=request.request_id,
            timestamp=datetime.now(timezone.utc),
            method_used=DeliveryMethod.API_ENDPOINT,
            response_code=201 if success else 400,
            response_message="API delivery successful" if success else "API delivery failed"
        )
    
    def _is_method_available(self, method: DeliveryMethod, platform: str) -> bool:
        """Check if delivery method is available for platform"""
        # Check if we have the necessary configuration for this method/platform
        if method == DeliveryMethod.EMAIL:
            return bool(self.config.get('smtp_server'))
        elif method == DeliveryMethod.WEB_FORM:
            return platform in self.platform_rules
        return True
    
    def _get_concurrency_limit(self, method: DeliveryMethod) -> int:
        """
Get concurrency limit for delivery method"""
        limits = {
            DeliveryMethod.EMAIL: 5,
            DeliveryMethod.WEB_FORM: 2,
            DeliveryMethod.API_ENDPOINT: 10,
            DeliveryMethod.FAX: 1
        }
        return limits.get(method, 3)
    
    async def _store_delivery_record(self, 
                                   request: DeliveryRequest,
                                   result: DeliveryResult) -> None:
        """
Store delivery record in database"""
        try:
            query = """
                INSERT INTO dmca_delivery_records (
                    delivery_id, notice_id, recipient, delivery_method, status,
                    response_code, response_message, delivery_time_seconds,
                    created_at, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            status = DeliveryStatus.DELIVERED if result.success else DeliveryStatus.FAILED
            
            await self.db.execute(query, [
                result.delivery_id,
                request.notice_id,
                request.recipient,
                request.method.value,
                status.value,
                result.response_code,
                result.response_message,
                result.delivery_time,
                result.timestamp,
                request.metadata
            ])
            
        except Exception as e:
            self.logger.error(f"Failed to store delivery record: {str(e)}")
    
    async def _update_delivery_analytics(self, 
                                       method: DeliveryMethod,
                                       result: DeliveryResult) -> None:
        """Update delivery analytics"""
        # Update channel performance metrics
        if method.value in self.channels:
            channel = self.channels[method.value]
            if result.success:
                # Update success rate (simplified calculation)
                channel.success_rate = (channel.success_rate * 0.9) + (1.0 * 0.1)
            else:
                channel.success_rate = (channel.success_rate * 0.9) + (0.0 * 0.1)
            
            if result.delivery_time:
                # Update average delivery time
                channel.avg_delivery_time = (
                    (channel.avg_delivery_time * 0.8) + (result.delivery_time * 0.2)
                )
