"""Webhook Handler Template for IA Chéries Platform
Enterprise-grade webhook processing with security, validation, and retry mechanisms

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
"""

import logging
import asyncio
import hmac
import hashlib
import json
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator, Field
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB

from core.config import get_settings
from core.database import get_db_session, Base
from core.auth import verify_webhook_signature, get_webhook_token
from core.rate_limiting import webhook_rate_limit
from core.logging import log_webhook_operation
from utils.exceptions import WebhookException, SecurityException
from monitoring.api_metrics import WebhookMetrics
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)
settings = get_settings()


class WebhookEventType(str, Enum):
    """Webhook event types supported by the platform"""
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_PROCESSED = "content.processed"
    COLLABORATION_CREATED = "collaboration.created"
    COLLABORATION_UPDATED = "collaboration.updated"
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_FAILED = "payment.failed"
    USER_REGISTERED = "user.registered"
    USER_VERIFIED = "user.verified"
    CREATOR_VERIFIED = "creator.verified"
    MONETIZATION_EVENT = "monetization.event"
    SECURITY_ALERT = "security.alert"
    SYSTEM_MAINTENANCE = "system.maintenance"


class WebhookStatus(str, Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class WebhookConfig:
    """Webhook configuration settings"""
    secret_key: str
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 5
    verify_ssl: bool = True
    signature_header: str = "X-IA Chéries-Signature"
    timestamp_header: str = "X-IA Chéries-Timestamp"
    event_types: List[WebhookEventType] = field(default_factory=list)


class WebhookPayload(BaseModel):
    """Webhook payload model"""
    event_id: str = Field(..., description="Unique event identifier")
    event_type: WebhookEventType = Field(..., description="Type of webhook event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data payload")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    source: str = Field(default="ainflue", description="Event source system")
    version: str = Field(default="1.0", description="Payload version")

    @validator('event_id')
    def validate_event_id(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Event ID must be at least 10 characters long')
        return v

    @validator('data')
    def validate_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Data must be a dictionary')
        return v


class WebhookEndpoint(Base):
    """Database model for webhook endpoints"""
    __tablename__ = "webhook_endpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String(2048), nullable=False, index=True)
    secret_key = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    event_types = Column(JSONB, default=list, nullable=False)
    headers = Column(JSONB, default=dict, nullable=True)
    timeout_seconds = Column(Integer, default=30, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    retry_delay_seconds = Column(Integer, default=5, nullable=False)
    verify_ssl = Column(Boolean, default=True, nullable=False)
    meta_data = Column(JSONB, default=dict, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_delivery_at = Column(DateTime, nullable=True)
    total_deliveries = Column(Integer, default=0, nullable=False)
    successful_deliveries = Column(Integer, default=0, nullable=False)
    failed_deliveries = Column(Integer, default=0, nullable=False)


class WebhookDelivery(Base):
    """Database model for webhook delivery attempts"""
    __tablename__ = "webhook_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSONB, nullable=False)
    status = Column(String(50), default=WebhookStatus.PENDING, nullable=False)
    response_status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_headers = Column(JSONB, nullable=True)
    attempt_count = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivered_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)


class WebhookHandler:
    """Enterprise webhook handler with comprehensive features"""

    def __init__(self, config: Optional[WebhookConfig] = None):
        self.config = config or WebhookConfig(
            secret_key=settings.WEBHOOK_SECRET_KEY,
            timeout_seconds=settings.WEBHOOK_TIMEOUT,
            max_retries=settings.WEBHOOK_MAX_RETRIES,
            retry_delay_seconds=settings.WEBHOOK_RETRY_DELAY
        )
        self.redis = None
        self.metrics = WebhookMetrics()
        self.notification_service = NotificationService()
        self._event_handlers: Dict[WebhookEventType, List[Callable]] = {}

    async def initialize(self):
        """Initialize webhook handler with Redis connection"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Webhook handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize webhook handler: {e}")
            raise

    def register_event_handler(self, event_type: WebhookEventType, handler: Callable):
        """Register an event handler for specific webhook events"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")

    async def create_webhook_endpoint(
        self,
        url: str,
        secret_key: str,
        event_types: List[WebhookEventType],
        session: AsyncSession,
        **kwargs
    ) -> WebhookEndpoint:
        """Create a new webhook endpoint"""
        try:
            endpoint = WebhookEndpoint(
                url=url,
                secret_key=secret_key,
                event_types=[et.value for et in event_types],
                **kwargs
            )
            session.add(endpoint)
            await session.commit()
            await session.refresh(endpoint)
            
            logger.info(f"Created webhook endpoint: {endpoint.id}")
            return endpoint
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create webhook endpoint: {e}")
            raise WebhookException(f"Failed to create webhook endpoint: {e}")

    async def generate_signature(self, payload: str, secret_key: str) -> str:
        """Generate HMAC signature for webhook payload"""
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    async def verify_webhook_signature(
        self,
        payload: str,
        signature: str,
        secret_key: str,
        timestamp: Optional[str] = None
    ) -> bool:
        """Verify webhook signature with timestamp validation"""
        try:
            # Verify timestamp if provided (prevent replay attacks)
            if timestamp:
                timestamp_dt = datetime.fromtimestamp(int(timestamp))
                if datetime.utcnow() - timestamp_dt > timedelta(minutes=5):
                    logger.warning("Webhook timestamp too old, potential replay attack")
                    return False

            # Generate expected signature
            expected_signature = await self.generate_signature(payload, secret_key)
            
            # Compare signatures securely
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    async def process_webhook_event(
        self,
        event_type: WebhookEventType,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> WebhookPayload:
        """Process incoming webhook event"""
        try:
            # Create webhook payload
            payload = WebhookPayload(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                data=data,
                metadata=metadata or {}
            )

            # Execute registered handlers
            if event_type in self._event_handlers:
                for handler in self._event_handlers[event_type]:
                    try:
                        await handler(payload)
                    except Exception as e:
                        logger.error(f"Handler failed for {event_type}: {e}")

            # Store in Redis for processing
            await self.redis.lpush(
                "webhook_events",
                json.dumps(payload.dict(), default=str)
            )

            # Update metrics
            await self.metrics.increment_webhook_events(event_type.value)
            
            logger.info(f"Processed webhook event: {payload.event_id}")
            return payload
            
        except Exception as e:
            logger.error(f"Failed to process webhook event: {e}")
            raise WebhookException(f"Failed to process webhook event: {e}")

    async def deliver_webhook(
        self,
        endpoint: WebhookEndpoint,
        payload: WebhookPayload,
        session: AsyncSession
    ) -> WebhookDelivery:
        """Deliver webhook to endpoint with retry logic"""
        delivery = WebhookDelivery(
            endpoint_id=endpoint.id,
            event_id=payload.event_id,
            event_type=payload.event_type.value,
            payload=payload.dict(),
            max_attempts=endpoint.max_retries
        )
        session.add(delivery)
        await session.commit()

        try:
            # Prepare request payload
            request_payload = json.dumps(payload.dict(), default=str)
            
            # Generate signature
            signature = await self.generate_signature(request_payload, endpoint.secret_key)
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "IA Chéries-Webhooks/1.0",
                endpoint.signature_header or "X-IA Chéries-Signature": signature,
                endpoint.timestamp_header or "X-IA Chéries-Timestamp": str(int(datetime.utcnow().timestamp()))
            }
            headers.update(endpoint.headers or {})

            # Make HTTP request
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=endpoint.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as client:
                async with client.post(
                    endpoint.url,
                    data=request_payload,
                    headers=headers,
                    ssl=endpoint.verify_ssl
                ) as response:
                    delivery.response_status_code = response.status
                    delivery.response_body = await response.text()
                    delivery.response_headers = dict(response.headers)
                    
                    if 200 <= response.status < 300:
                        delivery.status = WebhookStatus.DELIVERED
                        delivery.delivered_at = datetime.utcnow()
                        endpoint.successful_deliveries += 1
                        await self.metrics.increment_webhook_deliveries("success")
                    else:
                        delivery.status = WebhookStatus.FAILED
                        delivery.error_message = f"HTTP {response.status}: {await response.text()}"
                        endpoint.failed_deliveries += 1
                        await self.metrics.increment_webhook_deliveries("failed")

        except Exception as e:
            delivery.status = WebhookStatus.FAILED
            delivery.error_message = str(e)
            endpoint.failed_deliveries += 1
            await self.metrics.increment_webhook_deliveries("error")
            logger.error(f"Webhook delivery failed: {e}")

        finally:
            delivery.attempt_count += 1
            endpoint.total_deliveries += 1
            endpoint.last_delivery_at = datetime.utcnow()
            
            # Schedule retry if needed
            if (delivery.status == WebhookStatus.FAILED and 
                delivery.attempt_count < delivery.max_attempts):
                delivery.status = WebhookStatus.RETRYING
                delivery.next_retry_at = datetime.utcnow() + timedelta(
                    seconds=endpoint.retry_delay_seconds * (2 ** delivery.attempt_count)
                )

            await session.commit()
            return delivery

    async def process_webhook_queue(self, session: AsyncSession):
        """Process pending webhook deliveries from queue"""
        try:
            # Get webhook events from Redis queue
            event_data = await self.redis.brpop("webhook_events", timeout=1)
            if not event_data:
                return

            event_json = event_data[1]
            payload_data = json.loads(event_json)
            payload = WebhookPayload(**payload_data)

            # Get active endpoints for this event type
            from sqlalchemy import select
            stmt = select(WebhookEndpoint).where(
                WebhookEndpoint.is_active == True,
                WebhookEndpoint.event_types.contains([payload.event_type.value])
            )
            result = await session.execute(stmt)
            endpoints = result.scalars().all()

            # Deliver to all matching endpoints
            for endpoint in endpoints:
                await self.deliver_webhook(endpoint, payload, session)

        except Exception as e:
            logger.error(f"Failed to process webhook queue: {e}")

    async def retry_failed_webhooks(self, session: AsyncSession):
        """Retry failed webhook deliveries"""
        try:
            from sqlalchemy import select
            
            # Get deliveries ready for retry
            stmt = select(WebhookDelivery).where(
                WebhookDelivery.status == WebhookStatus.RETRYING,
                WebhookDelivery.next_retry_at <= datetime.utcnow(),
                WebhookDelivery.attempt_count < WebhookDelivery.max_attempts
            )
            result = await session.execute(stmt)
            deliveries = result.scalars().all()

            for delivery in deliveries:
                # Get endpoint
                endpoint_stmt = select(WebhookEndpoint).where(
                    WebhookEndpoint.id == delivery.endpoint_id
                )
                endpoint_result = await session.execute(endpoint_stmt)
                endpoint = endpoint_result.scalar_one_or_none()
                
                if endpoint and endpoint.is_active:
                    payload = WebhookPayload(**delivery.payload)
                    await self.deliver_webhook(endpoint, payload, session)

        except Exception as e:
            logger.error(f"Failed to retry webhooks: {e}")


# FastAPI Integration
webhook_handler = WebhookHandler()

async def get_webhook_handler() -> WebhookHandler:
    """Dependency to get webhook handler instance"""
    return webhook_handler


@log_webhook_operation
@webhook_rate_limit
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    handler: WebhookHandler = Depends(get_webhook_handler),
    session: AsyncSession = Depends(get_db_session)
):
    """Receive and process incoming webhook"""
    try:
        # Get request data
        payload_bytes = await request.body()
        payload_str = payload_bytes.decode('utf-8')
        
        # Get headers
        signature = request.headers.get('X-IA Chéries-Signature')
        timestamp = request.headers.get('X-IA Chéries-Timestamp')
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature header")
        
        # Verify signature
        if not await handler.verify_webhook_signature(
            payload_str, signature, settings.WEBHOOK_SECRET_KEY, timestamp
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        try:
            payload_data = json.loads(payload_str)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Validate payload
        try:
            webhook_payload = WebhookPayload(**payload_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
        
        # Process webhook in background
        background_tasks.add_task(
            handler.process_webhook_event,
            webhook_payload.event_type,
            webhook_payload.data,
            webhook_payload.metadata
        )
        
        return JSONResponse({
            "status": "received",
            "event_id": webhook_payload.event_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def create_webhook_router() -> FastAPI:
    """Create FastAPI router for webhook endpoints"""
    app = FastAPI(
        title="IA Chéries Webhook Handler",
        description="Enterprise webhook processing system",
        version="1.0.0"
    )
    
    @app.post("/webhooks/receive")
    async def webhook_endpoint(
        request: Request,
        background_tasks: BackgroundTasks,
        handler: WebhookHandler = Depends(get_webhook_handler),
        session: AsyncSession = Depends(get_db_session)
    ):
        """Main webhook receiving endpoint"""
        return await receive_webhook(request, background_tasks, handler, session)
    
    @app.get("/webhooks/health")
    async def webhook_health():
        """Webhook system health check"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    return app


# Background task for processing webhook queue
async def webhook_queue_processor():
    """Background task to process webhook queue"""
    await webhook_handler.initialize()
    
    while True:
        try:
            async with get_db_session() as session:
                await webhook_handler.process_webhook_queue(session)
                await webhook_handler.retry_failed_webhooks(session)
        except Exception as e:
            logger.error(f"Webhook queue processor error: {e}")
        
        await asyncio.sleep(1)


# Example usage
if __name__ == "__main__":
    import uvicorn
    
    app = create_webhook_router()
    
    # Start background processor
    asyncio.create_task(webhook_queue_processor())
    
    uvicorn.run(app, host="0.0.0.0", port=8001)