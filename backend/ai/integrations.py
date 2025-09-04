"""
External Services Integration Module
==================================

Consolidated integration functionality from conversational/ and other modules.
Provides comprehensive external services integration and API management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use is strictly prohibited. Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import aiohttp
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import base64
import hashlib

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Types of external services"""
    SOCIAL_MEDIA = "social_media"
    PAYMENT_PROCESSOR = "payment_processor"
    ANALYTICS_PLATFORM = "analytics_platform"
    AI_SERVICE = "ai_service"
    CONTENT_DELIVERY = "content_delivery"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    STORAGE_SERVICE = "storage_service"
    MONITORING_SERVICE = "monitoring_service"
    NOTIFICATION_SERVICE = "notification_service"

class IntegrationStatus(Enum):
    """Status of service integrations"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    AUTHENTICATING = "authenticating"
    RATE_LIMITED = "rate_limited"

class AuthenticationType(Enum):
    """Types of authentication methods"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    WEBHOOK_SIGNATURE = "webhook_signature"
    CUSTOM = "custom"

@dataclass
class ServiceCredentials:
    """Credentials for external service"""
    service_id: str
    auth_type: AuthenticationType
    credentials: Dict[str, Any]
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    scopes: List[str] = field(default_factory=list)

@dataclass
class IntegrationConfig:
    """Configuration for service integration"""
    service_id: str
    service_type: ServiceType
    name: str
    base_url: str
    credentials: ServiceCredentials
    rate_limits: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    retry_attempts: int = 3
    webhook_endpoints: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class APIResponse:
    """Response from external API"""
    service_id: str
    endpoint: str
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None

@dataclass
class WebhookEvent:
    """Webhook event from external service"""
    service_id: str
    event_type: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: datetime
    signature: Optional[str] = None
    verified: bool = False

class BaseServiceIntegration(ABC):
    """Base class for service integrations"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.status = IntegrationStatus.INACTIVE
        self.last_activity = datetime.now()
        self.error_count = 0
        self.logger = logging.getLogger(f"{__name__}.{config.service_id}")
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the service"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to the service"""
        pass
    
    @abstractmethod
    async def refresh_authentication(self) -> bool:
        """Refresh authentication if needed"""
        pass
    
    async def make_request(self, method: str, endpoint: str, data: Any = None, 
                          headers: Dict[str, str] = None) -> APIResponse:
        """Make authenticated request to service"""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Prepare headers
        request_headers = self.config.custom_headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Add authentication headers
        auth_headers = await self._get_auth_headers()
        request_headers.update(auth_headers)
        
        start_time = datetime.now()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data if method.upper() in ['POST', 'PUT', 'PATCH'] else None,
                    params=data if method.upper() == 'GET' else None,
                    headers=request_headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
                ) as response:
                    response_time = (datetime.now() - start_time).total_seconds()
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                    
                    self.last_activity = datetime.now()
                    
                    return APIResponse(
                        service_id=self.config.service_id,
                        endpoint=endpoint,
                        status_code=response.status,
                        data=response_data,
                        headers=dict(response.headers),
                        response_time=response_time
                    )
                    
        except Exception as e:
            self.error_count += 1
            response_time = (datetime.now() - start_time).total_seconds()
            
            return APIResponse(
                service_id=self.config.service_id,
                endpoint=endpoint,
                status_code=0,
                data=None,
                headers={},
                response_time=response_time,
                error_message=str(e)
            )
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on auth type"""
        auth_type = self.config.credentials.auth_type
        creds = self.config.credentials.credentials
        
        if auth_type == AuthenticationType.API_KEY:
            return {"X-API-Key": creds.get("api_key", "")}
        elif auth_type == AuthenticationType.BEARER_TOKEN:
            return {"Authorization": f"Bearer {creds.get('token', '')}"}
        elif auth_type == AuthenticationType.BASIC_AUTH:
            username = creds.get("username", "")
            password = creds.get("password", "")
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            return {"Authorization": f"Basic {credentials}"}
        else:
            return {}

class SocialMediaIntegration(BaseServiceIntegration):
    """Integration for social media platforms"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.supported_platforms = ["youtube", "instagram", "twitter", "tiktok", "facebook", "linkedin"]
    
    async def authenticate(self) -> bool:
        """Authenticate with social media platform"""
        try:
            # Test authentication with a simple API call
            response = await self.make_request("GET", "/me")
            
            if response.status_code == 200:
                self.status = IntegrationStatus.CONNECTED
                return True
            else:
                self.status = IntegrationStatus.ERROR
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            self.status = IntegrationStatus.ERROR
            return False
    
    async def test_connection(self) -> bool:
        """Test connection to social media platform"""
        response = await self.make_request("GET", "/health")
        return response.status_code == 200
    
    async def refresh_authentication(self) -> bool:
        """Refresh OAuth2 token if needed"""
        if self.config.credentials.auth_type != AuthenticationType.OAUTH2:
            return True
        
        if self.config.credentials.expires_at and self.config.credentials.expires_at > datetime.now():
            return True  # Token still valid
        
        if not self.config.credentials.refresh_token:
            return False
        
        # Refresh token logic (platform-specific)
        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": self.config.credentials.refresh_token
        }
        
        response = await self.make_request("POST", "/oauth/token", refresh_data)
        
        if response.status_code == 200 and response.data:
            # Update credentials
            new_token = response.data.get("access_token")
            expires_in = response.data.get("expires_in", 3600)
            
            self.config.credentials.credentials["token"] = new_token
            self.config.credentials.expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            return True
        
        return False
    
    async def post_content(self, content: Dict[str, Any]) -> APIResponse:
        """Post content to social media platform"""
        return await self.make_request("POST", "/posts", content)
    
    async def get_analytics(self, content_id: str = None) -> APIResponse:
        """Get analytics data"""
        endpoint = f"/analytics/{content_id}" if content_id else "/analytics"
        return await self.make_request("GET", endpoint)
    
    async def get_audience_insights(self) -> APIResponse:
        """Get audience insights"""
        return await self.make_request("GET", "/insights/audience")

class PaymentProcessorIntegration(BaseServiceIntegration):
    """Integration for payment processors"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.supported_processors = ["stripe", "paypal", "square", "razorpay"]
    
    async def authenticate(self) -> bool:
        """Authenticate with payment processor"""
        response = await self.make_request("GET", "/account")
        
        if response.status_code == 200:
            self.status = IntegrationStatus.CONNECTED
            return True
        else:
            self.status = IntegrationStatus.ERROR
            return False
    
    async def test_connection(self) -> bool:
        """Test connection to payment processor"""
        response = await self.make_request("GET", "/balance")
        return response.status_code == 200
    
    async def refresh_authentication(self) -> bool:
        """Payment processors typically use API keys that don't expire"""
        return True
    
    async def create_payment_intent(self, amount: float, currency: str, metadata: Dict[str, Any] = None) -> APIResponse:
        """Create payment intent"""
        payment_data = {
            "amount": int(amount * 100),  # Convert to cents
            "currency": currency,
            "metadata": metadata or {}
        }
        
        return await self.make_request("POST", "/payment_intents", payment_data)
    
    async def capture_payment(self, payment_intent_id: str) -> APIResponse:
        """Capture payment"""
        return await self.make_request("POST", f"/payment_intents/{payment_intent_id}/capture")
    
    async def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> APIResponse:
        """Refund payment"""
        refund_data = {"payment_intent": payment_id}
        if amount:
            refund_data["amount"] = int(amount * 100)
        
        return await self.make_request("POST", "/refunds", refund_data)
    
    async def get_transaction_history(self, limit: int = 100) -> APIResponse:
        """Get transaction history"""
        return await self.make_request("GET", "/charges", {"limit": limit})

class AIServiceIntegration(BaseServiceIntegration):
    """Integration for AI services (OpenAI, Google AI, etc.)"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.supported_services = ["openai", "google_ai", "anthropic", "cohere"]
    
    async def authenticate(self) -> bool:
        """Authenticate with AI service"""
        # Most AI services use API keys, test with a simple request
        response = await self.make_request("GET", "/models")
        
        if response.status_code == 200:
            self.status = IntegrationStatus.CONNECTED
            return True
        else:
            self.status = IntegrationStatus.ERROR
            return False
    
    async def test_connection(self) -> bool:
        """Test connection to AI service"""
        response = await self.make_request("GET", "/models")
        return response.status_code == 200
    
    async def refresh_authentication(self) -> bool:
        """AI services typically use API keys that don't expire"""
        return True
    
    async def generate_text(self, prompt: str, model: str = "gpt-3.5-turbo", 
                          max_tokens: int = 150) -> APIResponse:
        """Generate text using AI service"""
        request_data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }
        
        return await self.make_request("POST", "/chat/completions", request_data)
    
    async def analyze_sentiment(self, text: str) -> APIResponse:
        """Analyze sentiment of text"""
        request_data = {"text": text}
        return await self.make_request("POST", "/sentiment", request_data)
    
    async def extract_entities(self, text: str) -> APIResponse:
        """Extract entities from text"""
        request_data = {"text": text}
        return await self.make_request("POST", "/entities", request_data)

class EmailServiceIntegration(BaseServiceIntegration):
    """Integration for email services"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.supported_services = ["sendgrid", "mailgun", "ses", "mailchimp"]
    
    async def authenticate(self) -> bool:
        """Authenticate with email service"""
        response = await self.make_request("GET", "/user")
        
        if response.status_code == 200:
            self.status = IntegrationStatus.CONNECTED
            return True
        else:
            self.status = IntegrationStatus.ERROR
            return False
    
    async def test_connection(self) -> bool:
        """Test connection to email service"""
        response = await self.make_request("GET", "/stats")
        return response.status_code == 200
    
    async def refresh_authentication(self) -> bool:
        """Email services typically use API keys that don't expire"""
        return True
    
    async def send_email(self, to_email: str, subject: str, content: str, 
                        from_email: str = None, html_content: str = None) -> APIResponse:
        """Send email"""
        email_data = {
            "to": [{"email": to_email}],
            "subject": subject,
            "content": [{"type": "text/plain", "value": content}]
        }
        
        if html_content:
            email_data["content"].append({"type": "text/html", "value": html_content})
        
        if from_email:
            email_data["from"] = {"email": from_email}
        
        return await self.make_request("POST", "/mail/send", email_data)
    
    async def create_email_list(self, list_name: str) -> APIResponse:
        """Create email list"""
        list_data = {"name": list_name}
        return await self.make_request("POST", "/lists", list_data)
    
    async def add_subscriber(self, list_id: str, email: str, metadata: Dict[str, Any] = None) -> APIResponse:
        """Add subscriber to email list"""
        subscriber_data = {
            "email": email,
            "metadata": metadata or {}
        }
        
        return await self.make_request("POST", f"/lists/{list_id}/subscribers", subscriber_data)

class AnalyticsIntegration(BaseServiceIntegration):
    """Integration for analytics platforms"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.supported_platforms = ["google_analytics", "mixpanel", "amplitude", "segment"]
    
    async def authenticate(self) -> bool:
        """Authenticate with analytics platform"""
        response = await self.make_request("GET", "/account")
        
        if response.status_code == 200:
            self.status = IntegrationStatus.CONNECTED
            return True
        else:
            self.status = IntegrationStatus.ERROR
            return False
    
    async def test_connection(self) -> bool:
        """Test connection to analytics platform"""
        response = await self.make_request("GET", "/properties")
        return response.status_code == 200
    
    async def refresh_authentication(self) -> bool:
        """Refresh authentication if needed"""
        return await self.refresh_authentication()
    
    async def track_event(self, event_name: str, properties: Dict[str, Any], 
                         user_id: str = None) -> APIResponse:
        """Track analytics event"""
        event_data = {
            "event": event_name,
            "properties": properties
        }
        
        if user_id:
            event_data["user_id"] = user_id
        
        return await self.make_request("POST", "/track", event_data)
    
    async def get_metrics(self, start_date: str, end_date: str, 
                         metrics: List[str] = None) -> APIResponse:
        """Get analytics metrics"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        if metrics:
            params["metrics"] = ",".join(metrics)
        
        return await self.make_request("GET", "/reports", params)

class WebhookManager:
    """Manages webhook events from external services"""
    
    def __init__(self):
        self.webhook_handlers: Dict[str, Callable] = {}
        self.webhook_events: List[WebhookEvent] = []
        self.signature_validators: Dict[str, Callable] = {}
    
    def register_webhook_handler(self, service_id: str, handler: Callable):
        """Register webhook handler for service"""
        self.webhook_handlers[service_id] = handler
        
    def register_signature_validator(self, service_id: str, validator: Callable):
        """Register signature validator for service"""
        self.signature_validators[service_id] = validator
    
    async def process_webhook(self, service_id: str, event_type: str, payload: Dict[str, Any], 
                            headers: Dict[str, str]) -> Dict[str, Any]:
        """Process incoming webhook"""
        # Create webhook event
        event = WebhookEvent(
            service_id=service_id,
            event_type=event_type,
            payload=payload,
            headers=headers,
            timestamp=datetime.now(),
            signature=headers.get("X-Signature") or headers.get("X-Hub-Signature")
        )
        
        # Verify signature if validator exists
        if service_id in self.signature_validators:
            validator = self.signature_validators[service_id]
            event.verified = await validator(payload, event.signature, headers)
        else:
            event.verified = True  # No signature validation
        
        # Store event
        self.webhook_events.append(event)
        
        # Limit stored events
        if len(self.webhook_events) > 1000:
            self.webhook_events = self.webhook_events[-1000:]
        
        # Process with handler if available
        if service_id in self.webhook_handlers and event.verified:
            handler = self.webhook_handlers[service_id]
            result = await handler(event)
            return {"status": "processed", "result": result}
        elif not event.verified:
            return {"status": "error", "message": "Signature verification failed"}
        else:
            return {"status": "no_handler", "message": f"No handler registered for {service_id}"}
    
    async def get_webhook_events(self, service_id: str = None, 
                               limit: int = 100) -> List[WebhookEvent]:
        """Get webhook events"""
        events = self.webhook_events
        
        if service_id:
            events = [e for e in events if e.service_id == service_id]
        
        return events[-limit:]

class IntegrationManager:
    """Main manager for all external service integrations"""
    
    def __init__(self):
        self.integrations: Dict[str, BaseServiceIntegration] = {}
        self.webhook_manager = WebhookManager()
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
    
    async def add_integration(self, config: IntegrationConfig) -> bool:
        """Add new service integration"""
        service_type = config.service_type
        
        # Create appropriate integration instance
        if service_type == ServiceType.SOCIAL_MEDIA:
            integration = SocialMediaIntegration(config)
        elif service_type == ServiceType.PAYMENT_PROCESSOR:
            integration = PaymentProcessorIntegration(config)
        elif service_type == ServiceType.AI_SERVICE:
            integration = AIServiceIntegration(config)
        elif service_type == ServiceType.EMAIL_SERVICE:
            integration = EmailServiceIntegration(config)
        elif service_type == ServiceType.ANALYTICS_PLATFORM:
            integration = AnalyticsIntegration(config)
        else:
            integration = BaseServiceIntegration(config)
        
        # Test authentication
        authenticated = await integration.authenticate()
        
        if authenticated:
            self.integrations[config.service_id] = integration
            logger.info(f"Successfully added integration for {config.service_id}")
            return True
        else:
            logger.error(f"Failed to authenticate integration for {config.service_id}")
            return False
    
    async def remove_integration(self, service_id: str) -> bool:
        """Remove service integration"""
        if service_id in self.integrations:
            del self.integrations[service_id]
            logger.info(f"Removed integration for {service_id}")
            return True
        return False
    
    async def get_integration(self, service_id: str) -> Optional[BaseServiceIntegration]:
        """Get integration by service ID"""
        return self.integrations.get(service_id)
    
    async def test_all_integrations(self) -> Dict[str, bool]:
        """Test all integrations"""
        results = {}
        
        for service_id, integration in self.integrations.items():
            try:
                results[service_id] = await integration.test_connection()
            except Exception as e:
                logger.error(f"Integration test failed for {service_id}: {e}")
                results[service_id] = False
        
        return results
    
    async def refresh_all_authentications(self) -> Dict[str, bool]:
        """Refresh authentication for all integrations"""
        results = {}
        
        for service_id, integration in self.integrations.items():
            try:
                results[service_id] = await integration.refresh_authentication()
            except Exception as e:
                logger.error(f"Authentication refresh failed for {service_id}: {e}")
                results[service_id] = False
        
        return results
    
    async def get_integration_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all integrations"""
        status = {}
        
        for service_id, integration in self.integrations.items():
            status[service_id] = {
                "status": integration.status.value,
                "service_type": integration.config.service_type.value,
                "last_activity": integration.last_activity.isoformat(),
                "error_count": integration.error_count
            }
        
        return status
    
    async def execute_bulk_operation(self, service_ids: List[str], operation: str, 
                                   parameters: Dict[str, Any]) -> Dict[str, APIResponse]:
        """Execute operation across multiple integrations"""
        results = {}
        
        for service_id in service_ids:
            if service_id not in self.integrations:
                continue
            
            integration = self.integrations[service_id]
            
            try:
                if hasattr(integration, operation):
                    method = getattr(integration, operation)
                    result = await method(**parameters)
                    results[service_id] = result
                else:
                    results[service_id] = APIResponse(
                        service_id=service_id,
                        endpoint=operation,
                        status_code=404,
                        data=None,
                        headers={},
                        response_time=0.0,
                        error_message=f"Operation {operation} not supported"
                    )
            except Exception as e:
                results[service_id] = APIResponse(
                    service_id=service_id,
                    endpoint=operation,
                    status_code=500,
                    data=None,
                    headers={},
                    response_time=0.0,
                    error_message=str(e)
                )
        
        return results

# Factory functions
def create_integration_manager() -> IntegrationManager:
    """Create integration manager instance"""
    return IntegrationManager()

def create_webhook_manager() -> WebhookManager:
    """Create webhook manager instance"""
    return WebhookManager()

def create_social_media_integration(config: IntegrationConfig) -> SocialMediaIntegration:
    """Create social media integration"""
    return SocialMediaIntegration(config)

def create_payment_processor_integration(config: IntegrationConfig) -> PaymentProcessorIntegration:
    """Create payment processor integration"""
    return PaymentProcessorIntegration(config)

def create_ai_service_integration(config: IntegrationConfig) -> AIServiceIntegration:
    """Create AI service integration"""
    return AIServiceIntegration(config)

def create_email_service_integration(config: IntegrationConfig) -> EmailServiceIntegration:
    """Create email service integration"""
    return EmailServiceIntegration(config)

def create_analytics_integration(config: IntegrationConfig) -> AnalyticsIntegration:
    """Create analytics integration"""
    return AnalyticsIntegration(config)

# Export all classes and functions
__all__ = [
    # Core classes
    "IntegrationManager",
    "WebhookManager",
    "BaseServiceIntegration",
    
    # Specific integrations
    "SocialMediaIntegration",
    "PaymentProcessorIntegration",
    "AIServiceIntegration",
    "EmailServiceIntegration",
    "AnalyticsIntegration",
    
    # Data structures
    "ServiceCredentials",
    "IntegrationConfig",
    "APIResponse",
    "WebhookEvent",
    "ServiceType",
    "IntegrationStatus",
    "AuthenticationType",
    
    # Factory functions
    "create_integration_manager",
    "create_webhook_manager",
    "create_social_media_integration",
    "create_payment_processor_integration",
    "create_ai_service_integration",
    "create_email_service_integration",
    "create_analytics_integration"
]