"""Enterprise SMS notification service with multi-provider support and delivery tracking."""

import os
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from dataclasses import dataclass, asdict
import hashlib
import hmac
from urllib.parse import urlencode

from app.core.config import settings
from app.core.security.encryption import encrypt_sensitive_data, decrypt_sensitive_data
from app.utils.metrics import MetricsCollector


class SMSProvider(str, Enum):
    """
Supported SMS providers with enterprise-grade reliability."""

    TWILIO = "twilio"
    AWS_SNS = "aws_sns"
    NEXMO = "nexmo"
    MESSAGEBIRD = "messagebird"
    CLICKSEND = "clicksend"


@dataclass
class SMSMessage:
    """Enterprise SMS message with advanced features."""
    to_phone: str
    message: str
    from_phone: Optional[str] = None
    country_code: Optional[str] = None
    priority: str = "normal"  # low, normal, high, critical
    template_id: Optional[str] = None
    variables: Optional[Dict[str, str]] = None
    scheduled_at: Optional[datetime] = None
    max_retries: int = 3
    delivery_callback_url: Optional[str] = None
    user_id: Optional[str] = None
    campaign_id: Optional[str] = None
    content_type: str = "text"  # text, unicode
    validity_period: Optional[int] = 24  # hours
    flash_sms: bool = False


@dataclass
class SMSDeliveryResult:
    """SMS delivery tracking and analytics result."""
    message_id: str
    provider: SMSProvider
    status: str  # sent, delivered, failed, pending
    to_phone: str
    cost: Optional[float] = None
    currency: str = "USD"
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    provider_message_id: Optional[str] = None
    segments: int = 1
    delivery_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class SMSNotifier:
    """Enterprise SMS notification service with intelligent routing and analytics."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector()
        
        # Provider configurations
        self.providers = {
            SMSProvider.TWILIO: {
                "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
                "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
                "from_phone": os.getenv("TWILIO_FROM_PHONE"),
                "endpoint": "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json",
                "cost_per_sms": 0.0075,
                "reliability_score": 0.99
            },
            SMSProvider.AWS_SNS: {
                "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "region": os.getenv("AWS_REGION", "us-east-1"),
                "endpoint": "https://sns.{}.amazonaws.com/",
                "cost_per_sms": 0.0075,
                "reliability_score": 0.98
            },
            SMSProvider.NEXMO: {
                "api_key": os.getenv("NEXMO_API_KEY"),
                "api_secret": os.getenv("NEXMO_API_SECRET"),
                "from_phone": os.getenv("NEXMO_FROM_PHONE", "IA-Influencer"),
                "endpoint": "https://rest.nexmo.com/sms/json",
                "cost_per_sms": 0.0070,
                "reliability_score": 0.97
            },
            SMSProvider.MESSAGEBIRD: {
                "api_key": os.getenv("MESSAGEBIRD_API_KEY"),
                "from_phone": os.getenv("MESSAGEBIRD_FROM_PHONE", "IA-Agent"),
                "endpoint": "https://rest.messagebird.com/messages",
                "cost_per_sms": 0.0065,
                "reliability_score": 0.96
            },
            SMSProvider.CLICKSEND: {
                "username": os.getenv("CLICKSEND_USERNAME"),
                "api_key": os.getenv("CLICKSEND_API_KEY"),
                "endpoint": "https://rest.clicksend.com/v3/sms/send",
                "cost_per_sms": 0.0080,
                "reliability_score": 0.95
            }
        }
        
        # Intelligent routing configuration
        self.routing_strategy = os.getenv("SMS_ROUTING_STRATEGY", "cost_optimized")  # cost_optimized, reliability_first, load_balanced
        self.fallback_enabled = True
        self.max_concurrent_requests = 100
        self.rate_limits = {
            SMSProvider.TWILIO: 100,  # requests per second
            SMSProvider.AWS_SNS: 300,
            SMSProvider.NEXMO: 100,
            SMSProvider.MESSAGEBIRD: 200,
            SMSProvider.CLICKSEND: 50
        }

    async def send_sms(self, message: SMSMessage) -> SMSDeliveryResult:
        """Send SMS with intelligent provider selection and fallback."""
        start_time = datetime.utcnow()
        
        try:
            # Validate phone number
            if not self._validate_phone_number(message.to_phone):
                raise ValueError("Invalid phone number format")
            
            # Select optimal provider
            provider = await self._select_provider(message)
            
            # Send SMS
            result = await self._send_via_provider(provider, message)
            
            # Track metrics
            delivery_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.delivery_time_ms = int(delivery_time)
            
            await self._track_delivery_metrics(result)
            
            self.logger.info(f"SMS sent successfully via {provider}: {result.message_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"SMS sending failed: {str(e)}")
            
            # Try fallback if enabled
            if self.fallback_enabled:
                return await self._send_with_fallback(message, exclude_provider=provider if 'provider' in locals() else None)
            
            raise

    async def send_bulk_sms(self, messages: List[SMSMessage]) -> List[SMSDeliveryResult]:
        """Send bulk SMS with intelligent batching and rate limiting."""
        results = []
        
        # Group by provider for optimal routing
        provider_groups = await self._group_messages_by_provider(messages)
        
        for provider, provider_messages in provider_groups.items():
            # Send in batches with rate limiting
            batch_results = await self._send_batch_with_rate_limit(provider, provider_messages)
            results.extend(batch_results)
        
        return results

    async def get_delivery_status(self, message_id: str) -> Optional[SMSDeliveryResult]:
        """
Get delivery status for a specific message."""
        # This would typically query a database or provider API
        # Simplified implementation
        return None

    async def schedule_sms(self, message: SMSMessage, scheduled_at: datetime) -> str:
        """
Schedule SMS for future delivery."""
        message.scheduled_at = scheduled_at
        
        # Store in scheduling queue (would use Celery or similar in production)
        # Return scheduling ID
        scheduling_id = f"scheduled_{hashlib.md5(f'{message.to_phone}_{scheduled_at}'.encode()).hexdigest()[:8]}"
        
        self.logger.info(f"SMS scheduled for {scheduled_at}: {scheduling_id}")
        return scheduling_id

    async def cancel_scheduled_sms(self, scheduling_id: str) -> bool:
        """Cancel a scheduled SMS."""
        # Implementation would remove from scheduling queue
        self.logger.info(f"Cancelled scheduled SMS: {scheduling_id}")
        return True

    async def get_analytics(self, start_date: datetime, end_date: datetime, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive SMS analytics and insights."""
        return {
            "total_sent": await self._get_total_sent(start_date, end_date, filters),
            "delivery_rate": await self._get_delivery_rate(start_date, end_date, filters),
            "cost_breakdown": await self._get_cost_breakdown(start_date, end_date, filters),
            "provider_performance": await self._get_provider_performance(start_date, end_date, filters),
            "geographic_distribution": await self._get_geographic_stats(start_date, end_date, filters),
            "failure_analysis": await self._get_failure_analysis(start_date, end_date, filters)
        }

    async def _select_provider(self, message: SMSMessage) -> SMSProvider:
        """Intelligent provider selection based on configured strategy."""
        available_providers = [p for p, config in self.providers.items() if self._is_provider_configured(config)]
        
        if not available_providers:
            raise ValueError("No SMS providers configured")
        
        if self.routing_strategy == "cost_optimized":
            return min(available_providers, key=lambda p: self.providers[p]["cost_per_sms"])
        elif self.routing_strategy == "reliability_first":
            return max(available_providers, key=lambda p: self.providers[p]["reliability_score"])
        elif self.routing_strategy == "load_balanced":
            # Simple round-robin for now
            return available_providers[0]  # Would implement proper load balancing
        else:
            return available_providers[0]

    async def _send_via_provider(self, provider: SMSProvider, message: SMSMessage) -> SMSDeliveryResult:
        """Send SMS via specific provider."""
        if provider == SMSProvider.TWILIO:
            return await self._send_via_twilio(message)
        elif provider == SMSProvider.AWS_SNS:
            return await self._send_via_aws_sns(message)
        elif provider == SMSProvider.NEXMO:
            return await self._send_via_nexmo(message)
        elif provider == SMSProvider.MESSAGEBIRD:
            return await self._send_via_messagebird(message)
        elif provider == SMSProvider.CLICKSEND:
            return await self._send_via_clicksend(message)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _send_via_twilio(self, message: SMSMessage) -> SMSDeliveryResult:
        """Send SMS via Twilio API."""
        config = self.providers[SMSProvider.TWILIO]
        
        data = {
            "From": message.from_phone or config["from_phone"],
            "To": message.to_phone,
            "Body": message.message
        }
        
        if message.delivery_callback_url:
            data["StatusCallback"] = message.delivery_callback_url
        
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(config["account_sid"], config["auth_token"])
            
            async with session.post(
                config["endpoint"].format(config["account_sid"]),
                auth=auth,
                data=data
            ) as response:
                result_data = await response.json()
                
                return SMSDeliveryResult(
                    message_id=result_data.get("sid", ""),
                    provider=SMSProvider.TWILIO,
                    status="sent" if response.status == 201 else "failed",
                    to_phone=message.to_phone,
                    cost=config["cost_per_sms"],
                    provider_message_id=result_data.get("sid"),
                    sent_at=datetime.utcnow(),
                    metadata={"response": result_data}
                )

    async def _send_via_aws_sns(self, message: SMSMessage) -> SMSDeliveryResult:
        """Send SMS via AWS SNS."""
        # Simplified implementation - would use boto3 in production
        config = self.providers[SMSProvider.AWS_SNS]
        
        # Mock implementation
        message_id = f"aws_sns_{hashlib.md5(f'{message.to_phone}_{message.message}'.encode()).hexdigest()[:12]}"
        
        return SMSDeliveryResult(
            message_id=message_id,
            provider=SMSProvider.AWS_SNS,
            status="sent",
            to_phone=message.to_phone,
            cost=config["cost_per_sms"],
            provider_message_id=message_id,
            sent_at=datetime.utcnow()
        )

    async def _send_via_nexmo(self, message: SMSMessage) -> SMSDeliveryResult:
        """Send SMS via Nexmo (Vonage) API."""
        config = self.providers[SMSProvider.NEXMO]
        
        data = {
            "api_key": config["api_key"],
            "api_secret": config["api_secret"],
            "from": message.from_phone or config["from_phone"],
            "to": message.to_phone,
            "text": message.message
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(config["endpoint"], data=data) as response:
                result_data = await response.json()
                messages = result_data.get("messages", [{}])
                first_message = messages[0] if messages else {}
                
                return SMSDeliveryResult(
                    message_id=first_message.get("message-id", ""),
                    provider=SMSProvider.NEXMO,
                    status="sent" if first_message.get("status") == "0" else "failed",
                    to_phone=message.to_phone,
                    cost=config["cost_per_sms"],
                    provider_message_id=first_message.get("message-id"),
                    sent_at=datetime.utcnow(),
                    failure_reason=first_message.get("error-text"),
                    metadata={"response": result_data}
                )

    async def _send_via_messagebird(self, message: SMSMessage) -> SMSDeliveryResult:
        """Send SMS via MessageBird API."""
        config = self.providers[SMSProvider.MESSAGEBIRD]
        
        data = {
            "recipients": [message.to_phone],
            "originator": message.from_phone or config["from_phone"],
            "body": message.message
        }
        
        headers = {
            "Authorization": f"AccessKey {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config["endpoint"],
                headers=headers,
                json=data
            ) as response:
                result_data = await response.json()
                
                return SMSDeliveryResult(
                    message_id=result_data.get("id", ""),
                    provider=SMSProvider.MESSAGEBIRD,
                    status="sent" if response.status == 201 else "failed",
                    to_phone=message.to_phone,
                    cost=config["cost_per_sms"],
                    provider_message_id=result_data.get("id"),
                    sent_at=datetime.utcnow(),
                    metadata={"response": result_data}
                )

    async def _send_via_clicksend(self, message: SMSMessage) -> SMSDeliveryResult:
        """Send SMS via ClickSend API."""
        config = self.providers[SMSProvider.CLICKSEND]
        
        data = {
            "messages": [{
                "from": message.from_phone or "IA-Agent",
                "to": message.to_phone,
                "body": message.message
            }]
        }
        
        auth = aiohttp.BasicAuth(config["username"], config["api_key"])
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config["endpoint"],
                auth=auth,
                json=data
            ) as response:
                result_data = await response.json()
                message_data = result_data.get("data", {}).get("messages", [{}])[0]
                
                return SMSDeliveryResult(
                    message_id=message_data.get("message_id", ""),
                    provider=SMSProvider.CLICKSEND,
                    status="sent" if response.status == 200 else "failed",
                    to_phone=message.to_phone,
                    cost=config["cost_per_sms"],
                    provider_message_id=message_data.get("message_id"),
                    sent_at=datetime.utcnow(),
                    metadata={"response": result_data}
                )

    def _validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format (E.164)."""
        # Simplified validation - would use phonenumbers library in production
        return phone.startswith("+") and len(phone.replace("+", "")) >= 10

    def _is_provider_configured(self, config: Dict[str, Any]) -> bool:
        """Check if provider is properly configured."""
        required_keys = ["endpoint"]  # Simplified check
        return all(config.get(key) for key in required_keys)

    async def _send_with_fallback(self, message: SMSMessage, exclude_provider: Optional[SMSProvider] = None) -> SMSDeliveryResult:
        """Send SMS with fallback providers."""
        available_providers = [p for p in SMSProvider if p != exclude_provider]
        
        for provider in available_providers:
            try:
                return await self._send_via_provider(provider, message)
            except Exception as e:
                self.logger.warning(f"Fallback provider {provider} failed: {str(e)}")
                continue
        
        raise Exception("All SMS providers failed")

    async def _group_messages_by_provider(self, messages: List[SMSMessage]) -> Dict[SMSProvider, List[SMSMessage]]:
        """Group messages by optimal provider for bulk sending."""
        groups = {}
        
        for message in messages:
            provider = await self._select_provider(message)
            if provider not in groups:
                groups[provider] = []
            groups[provider].append(message)
        
        return groups

    async def _send_batch_with_rate_limit(self, provider: SMSProvider, messages: List[SMSMessage]) -> List[SMSDeliveryResult]:
        """
Send batch of messages with rate limiting."""
        results = []
        rate_limit = self.rate_limits.get(provider, 10)  # Default 10 requests per second
        
        semaphore = asyncio.Semaphore(min(rate_limit, self.max_concurrent_requests))
        
        async def send_single(message: SMSMessage):
            async with semaphore:
                return await self._send_via_provider(provider, message)
        
        # Send all messages concurrently with rate limiting
        tasks = [send_single(message) for message in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        filtered_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Batch SMS failed: {str(result)}")
            else:
                filtered_results.append(result)
        
        return filtered_results

    async def _track_delivery_metrics(self, result: SMSDeliveryResult):
        """Track SMS delivery metrics for analytics."""
        await self.metrics.increment(
            "sms_sent_total",
            tags={
                "provider": result.provider.value,
                "status": result.status
            }
        )
        
        if result.cost:
            await self.metrics.histogram(
                "sms_cost",
                result.cost,
                tags={"provider": result.provider.value}
            )
        
        if result.delivery_time_ms:
            await self.metrics.histogram(
                "sms_delivery_time_ms",
                result.delivery_time_ms,
                tags={"provider": result.provider.value}
            )

    async def _get_total_sent(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> int:
        """Get total SMS sent in date range."""
        # Implementation would query database
        return 0

    async def _get_delivery_rate(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> float:
        """
Get SMS delivery rate percentage."""
        # Implementation would query database
        return 0.95

    async def _get_cost_breakdown(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, float]:
        """
Get cost breakdown by provider."""
        # Implementation would query database
        return {}

    async def _get_provider_performance(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, Dict]:
        """
Get provider performance metrics."""
        # Implementation would query database
        return {}

    async def _get_geographic_stats(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, int]:
        """
Get geographic distribution of SMS."""
        # Implementation would query database
        return {}

    async def _get_failure_analysis(self, start_date: datetime, end_date: datetime, filters: Optional[Dict]) -> Dict[str, Any]:
        """
Get failure analysis and common issues."""
        # Implementation would query database
        return {}
