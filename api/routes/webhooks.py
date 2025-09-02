"""Webhooks API Routes
Platform webhooks and external integrations endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import hmac
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import aiohttp

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...integrations.platform_apis.youtube_api import YouTubeAPI
from ...integrations.platform_apis.instagram_api import InstagramAPI
from ...integrations.platform_apis.tiktok_api import TikTokAPI
from ...integrations.platform_apis.spotify_api import SpotifyAPI


# Enums
class PlatformType(str, Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    DISCORD = "discord"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"


class WebhookEvent(str, Enum):
    CONTENT_PUBLISHED = "content.published"
    CONTENT_UPDATED = "content.updated"
    CONTENT_DELETED = "content.deleted"
    REVENUE_RECEIVED = "revenue.received"
    VIOLATION_DETECTED = "violation.detected"
    COPYRIGHT_CLAIM = "copyright.claim"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    USER_FOLLOWED = "user.followed"
    USER_UNFOLLOWED = "user.unfollowed"
    COLLABORATION_REQUEST = "collaboration.request"
    COLLABORATION_ACCEPTED = "collaboration.accepted"


class WebhookStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    PENDING = "pending"


# Pydantic models
class WebhookEndpoint(BaseModel):
    webhook_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str = Field(..., regex=r'^https?://.+')
    platform: PlatformType
    events: List[WebhookEvent]
    secret: Optional[str] = None
    is_active: bool = Field(default=True)
    retry_policy: Dict[str, int] = Field(default={"max_retries": 3, "retry_delay": 60})
    filters: Optional[Dict[str, Any]] = None
    custom_headers: Optional[Dict[str, str]] = None


class WebhookDelivery(BaseModel):
    delivery_id: str
    webhook_id: str
    event_type: WebhookEvent
    payload: Dict[str, Any]
    status: WebhookStatus
    attempts: int
    last_attempt_at: Optional[datetime]
    next_retry_at: Optional[datetime]
    response_status: Optional[int]
    response_body: Optional[str]
    created_at: datetime


class IncomingWebhook(BaseModel):
    platform: PlatformType
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    signature: Optional[str] = None


class WebhookLog(BaseModel):
    log_id: str
    webhook_id: str
    event_type: str
    payload_size: int
    response_time_ms: int
    status_code: int
    error_message: Optional[str]
    created_at: datetime


class WebhookStats(BaseModel):
    webhook_id: str
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    average_response_time: float
    success_rate: float
    last_delivery: Optional[datetime]
    period: str


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize platform APIs
youtube_api = YouTubeAPI()
instagram_api = InstagramAPI()
tiktok_api = TikTokAPI()
spotify_api = SpotifyAPI()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


@router.post("/endpoints", response_model=Dict[str, str])
async def create_webhook_endpoint(
    webhook: WebhookEndpoint,
    user: dict = Depends(get_current_user)
):
    """Create a new webhook endpoint"""
    try:
        # Validate URL accessibility
        url_validation = await _validate_webhook_url(webhook.url)
        if not url_validation['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid webhook URL: {url_validation['error']}"
            )
        
        # Generate secret if not provided
        if not webhook.secret:
            webhook.secret = security_manager.generate_webhook_secret()
        
        # Create webhook endpoint
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO webhook_endpoints (webhook_id, user_id, url, platform, events,
                                             secret_hash, is_active, retry_policy, filters,
                                             custom_headers, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                webhook.webhook_id, user['user_id'], webhook.url, webhook.platform.value,
                [event.value for event in webhook.events],
                security_manager.hash_webhook_secret(webhook.secret),
                webhook.is_active, webhook.retry_policy, webhook.filters,
                webhook.custom_headers, datetime.utcnow()
            ))
            await session.commit()
        
        # Register webhook with platform if needed
        if webhook.platform in [PlatformType.YOUTUBE, PlatformType.INSTAGRAM, PlatformType.TIKTOK]:
            await _register_platform_webhook(webhook, user)
        
        logger.info(f"Webhook endpoint created: {webhook.webhook_id} by user {user['user_id']}")
        
        return {
            "webhook_id": webhook.webhook_id,
            "secret": webhook.secret,
            "status": "active" if webhook.is_active else "inactive",
            "message": "Webhook endpoint created successfully"
        }
        
    except Exception as e:
        logger.error(f"Create webhook endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create webhook endpoint"
        )


@router.get("/endpoints", response_model=List[Dict[str, Any]])
async def get_webhook_endpoints(
    platform: Optional[PlatformType] = None,
    is_active: Optional[bool] = None,
    user: dict = Depends(get_current_user)
):
    """Get user's webhook endpoints"""
    try:
        query = """
            SELECT webhook_id, url, platform, events, is_active, retry_policy,
                   filters, custom_headers, created_at, updated_at
            FROM webhook_endpoints
            WHERE user_id = %s
        """
        params = [user['user_id']]
        
        if platform:
            query += " AND platform = %s"
            params.append(platform.value)
        
        if is_active is not None:
            query += " AND is_active = %s"
            params.append(is_active)
            
        query += " ORDER BY created_at DESC"
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            webhooks = result.fetchall()
        
        webhook_list = []
        for webhook in webhooks:
            # Get recent delivery stats
            stats = await _get_webhook_stats(webhook[0])
            
            webhook_list.append({
                "webhook_id": webhook[0],
                "url": webhook[1],
                "platform": webhook[2],
                "events": webhook[3],
                "is_active": webhook[4],
                "retry_policy": webhook[5],
                "filters": webhook[6],
                "custom_headers": webhook[7],
                "created_at": webhook[8],
                "updated_at": webhook[9],
                "stats": stats
            })
        
        return webhook_list
        
    except Exception as e:
        logger.error(f"Get webhook endpoints failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get webhook endpoints"
        )


@router.post("/receive/{platform}")
async def receive_platform_webhook(
    platform: PlatformType,
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: Optional[str] = Header(None),
    x_hub_signature: Optional[str] = Header(None)
):
    """Receive webhook from external platform"""
    try:
        # Get raw body
        raw_body = await request.body()
        
        # Parse JSON payload
        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # Verify webhook signature
        signature = x_signature or x_hub_signature
        if not await _verify_platform_signature(platform, raw_body, signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Create incoming webhook record
        webhook_id = str(uuid.uuid4())
        incoming_webhook = IncomingWebhook(
            platform=platform,
            event_type=payload.get('event_type', 'unknown'),
            data=payload,
            timestamp=datetime.utcnow(),
            signature=signature
        )
        
        # Store incoming webhook
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO incoming_webhooks (webhook_id, platform, event_type, payload,
                                             signature, received_at, processed)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                webhook_id, platform.value, incoming_webhook.event_type,
                incoming_webhook.data, signature, datetime.utcnow(), False
            ))
            await session.commit()
        
        # Process webhook in background
        background_tasks.add_task(
            _process_incoming_webhook, webhook_id, incoming_webhook
        )
        
        logger.info(f"Webhook received from {platform.value}: {incoming_webhook.event_type}")
        
        return {"status": "received", "webhook_id": webhook_id}
        
    except Exception as e:
        logger.error(f"Receive platform webhook failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@router.post("/send", response_model=Dict[str, str])
async def send_webhook(
    event_type: WebhookEvent,
    payload: Dict[str, Any],
    target_platforms: List[PlatformType],
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Send webhook to registered endpoints"""
    try:
        # Get matching webhook endpoints
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT webhook_id, url, platform, secret_hash, custom_headers, retry_policy
                FROM webhook_endpoints
                WHERE user_id = %s AND is_active = true
                  AND platform = ANY(%s) AND %s = ANY(events)
            """, (user['user_id'], [p.value for p in target_platforms], event_type.value))
            
            endpoints = result.fetchall()
        
        if not endpoints:
            return {
                "message": "No active webhook endpoints found for specified platforms and event",
                "endpoints_notified": 0
            }
        
        delivery_id = str(uuid.uuid4())
        
        # Create delivery records and schedule sending
        async with database_manager.get_postgres_session() as session:
            for endpoint in endpoints:
                webhook_id, url, platform, secret_hash, custom_headers, retry_policy = endpoint
                
                await session.execute("""
                    INSERT INTO webhook_deliveries (delivery_id, webhook_id, user_id, event_type,
                                                   payload, status, attempts, created_at, next_retry_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"{delivery_id}_{webhook_id}", webhook_id, user['user_id'],
                    event_type.value, payload, WebhookStatus.PENDING.value,
                    0, datetime.utcnow(), datetime.utcnow()
                ))
                
                # Schedule webhook delivery
                background_tasks.add_task(
                    _deliver_webhook, f"{delivery_id}_{webhook_id}", url, event_type.value,
                    payload, secret_hash, custom_headers, retry_policy
                )
            
            await session.commit()
        
        logger.info(f"Webhook delivery scheduled: {delivery_id} to {len(endpoints)} endpoints")
        
        return {
            "delivery_id": delivery_id,
            "endpoints_notified": len(endpoints),
            "message": "Webhook delivery scheduled"
        }
        
    except Exception as e:
        logger.error(f"Send webhook failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send webhook"
        )


@router.get("/deliveries", response_model=List[WebhookDelivery])
async def get_webhook_deliveries(
    webhook_id: Optional[str] = None,
    event_type: Optional[WebhookEvent] = None,
    status: Optional[WebhookStatus] = None,
    days: int = Field(default=7, ge=1, le=30),
    limit: int = Field(default=50, ge=1, le=200),
    user: dict = Depends(get_current_user)
):
    """Get webhook delivery history"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = """
            SELECT wd.delivery_id, wd.webhook_id, wd.event_type, wd.payload, wd.status,
                   wd.attempts, wd.last_attempt_at, wd.next_retry_at, wd.response_status,
                   wd.response_body, wd.created_at
            FROM webhook_deliveries wd
            JOIN webhook_endpoints we ON wd.webhook_id = we.webhook_id
            WHERE wd.user_id = %s AND wd.created_at >= %s
        """
        params = [user['user_id'], start_date]
        
        if webhook_id:
            query += " AND wd.webhook_id = %s"
            params.append(webhook_id)
        
        if event_type:
            query += " AND wd.event_type = %s"
            params.append(event_type.value)
        
        if status:
            query += " AND wd.status = %s"
            params.append(status.value)
            
        query += " ORDER BY wd.created_at DESC LIMIT %s"
        params.append(limit)
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            deliveries = result.fetchall()
        
        delivery_list = []
        for delivery in deliveries:
            delivery_list.append(WebhookDelivery(
                delivery_id=delivery[0],
                webhook_id=delivery[1],
                event_type=WebhookEvent(delivery[2]),
                payload=delivery[3],
                status=WebhookStatus(delivery[4]),
                attempts=delivery[5],
                last_attempt_at=delivery[6],
                next_retry_at=delivery[7],
                response_status=delivery[8],
                response_body=delivery[9],
                created_at=delivery[10]
            ))
        
        return delivery_list
        
    except Exception as e:
        logger.error(f"Get webhook deliveries failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get webhook deliveries"
        )


@router.post("/test/{webhook_id}", response_model=Dict[str, str])
async def test_webhook(
    webhook_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Test a webhook endpoint"""
    try:
        # Get webhook details
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT url, platform, secret_hash, custom_headers, retry_policy
                FROM webhook_endpoints
                WHERE webhook_id = %s AND user_id = %s
            """, (webhook_id, user['user_id']))
            
            webhook_info = result.fetchone()
            if not webhook_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Webhook not found or access denied"
                )
        
        url, platform, secret_hash, custom_headers, retry_policy = webhook_info
        
        # Create test payload
        test_payload = {
            "event_type": "webhook.test",
            "data": {
                "test_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "message": "This is a test webhook from Ainflue platform"
            },
            "webhook_id": webhook_id,
            "platform": platform
        }
        
        test_delivery_id = f"test_{webhook_id}_{int(datetime.utcnow().timestamp())}"
        
        # Record test delivery
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO webhook_deliveries (delivery_id, webhook_id, user_id, event_type,
                                               payload, status, attempts, created_at, next_retry_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                test_delivery_id, webhook_id, user['user_id'], "webhook.test",
                test_payload, WebhookStatus.PENDING.value, 0, datetime.utcnow(), datetime.utcnow()
            ))
            await session.commit()
        
        # Send test webhook
        background_tasks.add_task(
            _deliver_webhook, test_delivery_id, url, "webhook.test",
            test_payload, secret_hash, custom_headers, retry_policy
        )
        
        logger.info(f"Test webhook sent: {webhook_id}")
        
        return {
            "test_id": test_delivery_id,
            "message": "Test webhook sent successfully",
            "status": "sent"
        }
        
    except Exception as e:
        logger.error(f"Test webhook failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test webhook"
        )


@router.get("/stats/{webhook_id}", response_model=WebhookStats)
async def get_webhook_statistics(
    webhook_id: str,
    days: int = Field(default=30, ge=1, le=90),
    user: dict = Depends(get_current_user)
):
    """Get webhook statistics"""
    try:
        # Verify webhook ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT webhook_id FROM webhook_endpoints
                WHERE webhook_id = %s AND user_id = %s
            """, (webhook_id, user['user_id']))
            
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Webhook not found or access denied"
                )
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get delivery statistics
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT 
                    COUNT(*) as total_deliveries,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as successful_deliveries,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_deliveries,
                    AVG(response_time_ms) as avg_response_time,
                    MAX(created_at) as last_delivery
                FROM webhook_deliveries
                WHERE webhook_id = %s AND created_at >= %s
            """, (webhook_id, start_date))
            
            stats = result.fetchone()
        
        total_deliveries = stats[0]
        successful_deliveries = stats[1] or 0
        failed_deliveries = stats[2] or 0
        avg_response_time = float(stats[3] or 0)
        last_delivery = stats[4]
        
        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        webhook_stats = WebhookStats(
            webhook_id=webhook_id,
            total_deliveries=total_deliveries,
            successful_deliveries=successful_deliveries,
            failed_deliveries=failed_deliveries,
            average_response_time=avg_response_time,
            success_rate=success_rate,
            last_delivery=last_delivery,
            period=f"{days}d"
        )
        
        return webhook_stats
        
    except Exception as e:
        logger.error(f"Get webhook statistics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get webhook statistics"
        )


@router.put("/endpoints/{webhook_id}", response_model=Dict[str, str])
async def update_webhook_endpoint(
    webhook_id: str,
    webhook_update: WebhookEndpoint,
    user: dict = Depends(get_current_user)
):
    """Update webhook endpoint"""
    try:
        # Verify ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT webhook_id FROM webhook_endpoints
                WHERE webhook_id = %s AND user_id = %s
            """, (webhook_id, user['user_id']))
            
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Webhook not found or access denied"
                )
            
            # Update webhook
            await session.execute("""
                UPDATE webhook_endpoints 
                SET url = %s, platform = %s, events = %s, is_active = %s,
                    retry_policy = %s, filters = %s, custom_headers = %s, updated_at = %s
                WHERE webhook_id = %s
            """, (
                webhook_update.url, webhook_update.platform.value,
                [event.value for event in webhook_update.events], webhook_update.is_active,
                webhook_update.retry_policy, webhook_update.filters,
                webhook_update.custom_headers, datetime.utcnow(), webhook_id
            ))
            await session.commit()
        
        logger.info(f"Webhook endpoint updated: {webhook_id}")
        
        return {
            "webhook_id": webhook_id,
            "message": "Webhook endpoint updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Update webhook endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update webhook endpoint"
        )


@router.delete("/endpoints/{webhook_id}")
async def delete_webhook_endpoint(
    webhook_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete webhook endpoint"""
    try:
        async with database_manager.get_postgres_session() as session:
            # Verify ownership
            result = await session.execute("""
                SELECT platform FROM webhook_endpoints
                WHERE webhook_id = %s AND user_id = %s
            """, (webhook_id, user['user_id']))
            
            webhook_info = result.fetchone()
            if not webhook_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Webhook not found or access denied"
                )
            
            platform = webhook_info[0]
            
            # Delete webhook
            await session.execute("""
                DELETE FROM webhook_endpoints WHERE webhook_id = %s
            """, (webhook_id,))
            await session.commit()
        
        # Unregister from platform if needed
        if platform in ["youtube", "instagram", "tiktok"]:
            await _unregister_platform_webhook(webhook_id, platform)
        
        logger.info(f"Webhook endpoint deleted: {webhook_id}")
        
        return {"message": "Webhook endpoint deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete webhook endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete webhook endpoint"
        )


# Helper functions
async def _validate_webhook_url(url: str) -> Dict[str, Any]:
    """Validate webhook URL accessibility"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return {
                    "valid": response.status < 400,
                    "status_code": response.status
                }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


async def _verify_platform_signature(platform: PlatformType, body: bytes, signature: Optional[str]) -> bool:
    """Verify webhook signature from platform"""
    if not signature:
        return False
    
    try:
        # Get platform webhook secret
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT webhook_secret FROM platform_integrations
                WHERE platform = %s AND is_active = true
            """, (platform.value,))
            
            secret_info = result.fetchone()
            if not secret_info:
                return False
            
            secret = secret_info[0]
        
        # Verify signature based on platform
        if platform == PlatformType.STRIPE:
            # Stripe uses HMAC-SHA256
            expected_signature = hmac.new(
                secret.encode('utf-8'), body, hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
        
        elif platform == PlatformType.YOUTUBE:
            # YouTube uses HMAC-SHA1
            expected_signature = hmac.new(
                secret.encode('utf-8'), body, hashlib.sha1
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature.replace('sha1=', ''))
        
        # Add other platform signature verification logic here
        
        return True
        
    except Exception as e:
        logger.error(f"Signature verification failed: {e}")
        return False


async def _get_webhook_stats(webhook_id: str) -> Dict[str, Any]:
    """Get basic webhook statistics"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT 
                    COUNT(*) as total_deliveries,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as successful_deliveries,
                    MAX(created_at) as last_delivery
                FROM webhook_deliveries
                WHERE webhook_id = %s AND created_at >= %s
            """, (webhook_id, datetime.utcnow() - timedelta(days=7)))
            
            stats = result.fetchone()
            
            return {
                "total_deliveries": stats[0],
                "successful_deliveries": stats[1] or 0,
                "last_delivery": stats[2]
            }
    except Exception as e:
        logger.error(f"Get webhook stats failed: {e}")
        return {"total_deliveries": 0, "successful_deliveries": 0, "last_delivery": None}


# Background task functions
async def _process_incoming_webhook(webhook_id: str, incoming_webhook: IncomingWebhook):
    """Process incoming webhook from external platform"""
    try:
        # Determine event type and extract relevant data
        event_handlers = {
            PlatformType.YOUTUBE: _process_youtube_webhook,
            PlatformType.INSTAGRAM: _process_instagram_webhook,
            PlatformType.TIKTOK: _process_tiktok_webhook,
            PlatformType.SPOTIFY: _process_spotify_webhook,
            PlatformType.STRIPE: _process_stripe_webhook,
        }
        
        handler = event_handlers.get(incoming_webhook.platform)
        if handler:
            await handler(webhook_id, incoming_webhook)
        
        # Mark as processed
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE incoming_webhooks 
                SET processed = true, processed_at = %s
                WHERE webhook_id = %s
            """, (datetime.utcnow(), webhook_id))
            await session.commit()
        
        logger.info(f"Incoming webhook processed: {webhook_id}")
        
    except Exception as e:
        logger.error(f"Process incoming webhook failed: {e}")


async def _deliver_webhook(delivery_id: str, url: str, event_type: str, payload: Dict[str, Any],
                          secret_hash: str, custom_headers: Optional[Dict[str, str]],
                          retry_policy: Dict[str, int]):
    """Deliver webhook to endpoint"""
    try:
        start_time = datetime.utcnow()
        
        # Update status to attempting
        await _update_delivery_status(delivery_id, WebhookStatus.PENDING, attempts=1)
        
        # Prepare payload
        webhook_payload = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload,
            "delivery_id": delivery_id
        }
        
        # Generate signature
        payload_bytes = json.dumps(webhook_payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret_hash.encode('utf-8'), payload_bytes, hashlib.sha256
        ).hexdigest()
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Ainflue-Signature": f"sha256={signature}",
            "X-Ainflue-Event": event_type,
            "X-Ainflue-Delivery": delivery_id
        }
        
        if custom_headers:
            headers.update(custom_headers)
        
        # Send webhook
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                json=webhook_payload, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                response_text = await response.text()
                
                if 200 <= response.status < 300:
                    await _update_delivery_status(
                        delivery_id, WebhookStatus.ACTIVE, response.status,
                        response_text, response_time
                    )
                    logger.info(f"Webhook delivered successfully: {delivery_id}")
                else:
                    await _update_delivery_status(
                        delivery_id, WebhookStatus.FAILED, response.status,
                        response_text, response_time
                    )
                    logger.warning(f"Webhook delivery failed: {delivery_id}, status: {response.status}")
        
    except Exception as e:
        logger.error(f"Webhook delivery failed: {e}")
        await _update_delivery_status(delivery_id, WebhookStatus.FAILED, error_message=str(e))


async def _update_delivery_status(delivery_id: str, status: WebhookStatus, 
                                 response_status: Optional[int] = None,
                                 response_body: Optional[str] = None,
                                 response_time: Optional[float] = None,
                                 attempts: Optional[int] = None,
                                 error_message: Optional[str] = None):
    """Update webhook delivery status"""
    try:
        async with database_manager.get_postgres_session() as session:
            update_fields = ["status = %s", "last_attempt_at = %s"]
            params = [status.value, datetime.utcnow()]
            
            if response_status is not None:
                update_fields.append("response_status = %s")
                params.append(response_status)
            
            if response_body is not None:
                update_fields.append("response_body = %s")
                params.append(response_body)
            
            if response_time is not None:
                update_fields.append("response_time_ms = %s")
                params.append(int(response_time))
            
            if attempts is not None:
                update_fields.append("attempts = %s")
                params.append(attempts)
            
            if error_message is not None:
                update_fields.append("error_message = %s")
                params.append(error_message)
            
            params.append(delivery_id)
            
            query = f"""
                UPDATE webhook_deliveries 
                SET {', '.join(update_fields)}
                WHERE delivery_id = %s
            """
            
            await session.execute(query, params)
            await session.commit()
    except Exception as e:
        logger.error(f"Update delivery status failed: {e}")


# Platform-specific webhook processors
async def _process_youtube_webhook(webhook_id: str, webhook: IncomingWebhook):
    """Process YouTube webhook"""
    try:
        logger.info(f"Processing YouTube webhook {webhook_id} for event {webhook.event}")
        
        # Parse YouTube webhook data
        data = webhook.data
        
        if webhook.event == WebhookEvent.CONTENT_PUBLISHED:
            # Handle new content publication
            video_id = data.get('video_id')
            channel_id = data.get('channel_id') 
            title = data.get('title', '')
            
            if video_id and channel_id:
                # Update content database
                await database_manager.execute(
                    "INSERT INTO platform_content (platform, external_id, channel_id, title, status, webhook_id) VALUES (?, ?, ?, ?, ?, ?)",
                    ("youtube", video_id, channel_id, title, "published", webhook_id)
                )
                
                # Trigger content analysis
                await _analyze_new_content("youtube", video_id, title)
                
        elif webhook.event == WebhookEvent.CONTENT_UPDATED:
            # Handle content updates
            video_id = data.get('video_id')
            if video_id:
                await database_manager.execute(
                    "UPDATE platform_content SET updated_at = ? WHERE platform = ? AND external_id = ?",
                    (datetime.utcnow(), "youtube", video_id)
                )
                
        elif webhook.event == WebhookEvent.CONTENT_DELETED:
            # Handle content deletion
            video_id = data.get('video_id')
            if video_id:
                await database_manager.execute(
                    "UPDATE platform_content SET status = ? WHERE platform = ? AND external_id = ?",
                    ("deleted", "youtube", video_id)
                )
        
        # Update analytics
        await _update_platform_analytics("youtube", webhook.event, data)
        
        logger.info(f"Successfully processed YouTube webhook {webhook_id}")
        
    except Exception as e:
        logger.error(f"Error processing YouTube webhook {webhook_id}: {str(e)}")
        raise


async def _process_instagram_webhook(webhook_id: str, webhook: IncomingWebhook):
    """Process Instagram webhook"""
    try:
        logger.info(f"Processing Instagram webhook {webhook_id} for event {webhook.event}")
        
        data = webhook.data
        
        if webhook.event == WebhookEvent.CONTENT_PUBLISHED:
            # Handle new Instagram post/story/reel
            media_id = data.get('media_id')
            user_id = data.get('user_id')
            media_type = data.get('media_type', 'photo')  # photo, video, carousel, story
            caption = data.get('caption', '')
            
            if media_id and user_id:
                # Store Instagram content
                await database_manager.execute(
                    """INSERT INTO platform_content 
                       (platform, external_id, user_id, media_type, caption, status, webhook_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    ("instagram", media_id, user_id, media_type, caption, "published", webhook_id)
                )
                
                # Analyze engagement potential
                await _analyze_instagram_engagement(media_id, media_type, caption)
                
        elif webhook.event == WebhookEvent.CONTENT_UPDATED:
            # Handle Instagram content updates (edited captions, etc.)
            media_id = data.get('media_id')
            new_caption = data.get('caption')
            
            if media_id and new_caption:
                await database_manager.execute(
                    "UPDATE platform_content SET caption = ?, updated_at = ? WHERE platform = ? AND external_id = ?",
                    (new_caption, datetime.utcnow(), "instagram", media_id)
                )
                
        elif webhook.event == WebhookEvent.CONTENT_DELETED:
            # Handle Instagram content deletion
            media_id = data.get('media_id')
            if media_id:
                await database_manager.execute(
                    "UPDATE platform_content SET status = ? WHERE platform = ? AND external_id = ?",
                    ("deleted", "instagram", media_id)
                )
        
        # Update Instagram-specific metrics
        await _update_instagram_metrics(webhook.event, data)
        
        logger.info(f"Successfully processed Instagram webhook {webhook_id}")
        
    except Exception as e:
        logger.error(f"Error processing Instagram webhook {webhook_id}: {str(e)}")
        raise


async def _process_tiktok_webhook(webhook_id: str, webhook: IncomingWebhook):
    """Process TikTok webhook"""
    try:
        logger.info(f"Processing TikTok webhook {webhook_id} for event {webhook.event}")
        
        data = webhook.data
        
        if webhook.event == WebhookEvent.CONTENT_PUBLISHED:
            # Handle new TikTok video
            video_id = data.get('video_id')
            user_id = data.get('user_id')
            title = data.get('title', '')
            description = data.get('description', '')
            hashtags = data.get('hashtags', [])
            
            if video_id and user_id:
                # Store TikTok content
                await database_manager.execute(
                    """INSERT INTO platform_content 
                       (platform, external_id, user_id, title, description, hashtags, status, webhook_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    ("tiktok", video_id, user_id, title, description, json.dumps(hashtags), "published", webhook_id)
                )
                
                # Analyze TikTok trend potential
                await _analyze_tiktok_trends(video_id, hashtags, title)
                
        elif webhook.event == WebhookEvent.CONTENT_UPDATED:
            # Handle TikTok video updates
            video_id = data.get('video_id')
            new_description = data.get('description')
            new_hashtags = data.get('hashtags', [])
            
            if video_id:
                update_fields = {}
                if new_description:
                    update_fields['description'] = new_description
                if new_hashtags:
                    update_fields['hashtags'] = json.dumps(new_hashtags)
                
                if update_fields:
                    # Build dynamic update query
                    set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
                    values = list(update_fields.values()) + [datetime.utcnow(), "tiktok", video_id]
                    
                    await database_manager.execute(
                        f"UPDATE platform_content SET {set_clause}, updated_at = ? WHERE platform = ? AND external_id = ?",
                        tuple(values)
                    )
                    
        elif webhook.event == WebhookEvent.CONTENT_DELETED:
            # Handle TikTok video deletion
            video_id = data.get('video_id')
            if video_id:
                await database_manager.execute(
                    "UPDATE platform_content SET status = ? WHERE platform = ? AND external_id = ?",
                    ("deleted", "tiktok", video_id)
                )
        
        # Update TikTok analytics and trending data
        await _update_tiktok_analytics(webhook.event, data)
        
        logger.info(f"Successfully processed TikTok webhook {webhook_id}")
        
    except Exception as e:
        logger.error(f"Error processing TikTok webhook {webhook_id}: {str(e)}")
        raise


async def _process_spotify_webhook(webhook_id: str, webhook: IncomingWebhook):
    """Process Spotify webhook"""
    try:
        logger.info(f"Processing Spotify webhook {webhook_id} for event {webhook.event}")
        
        data = webhook.data
        
        if webhook.event == WebhookEvent.CONTENT_PUBLISHED:
            # Handle new track/album/playlist release
            content_id = data.get('content_id')  # track_id, album_id, or playlist_id
            artist_id = data.get('artist_id')
            content_type = data.get('content_type', 'track')  # track, album, playlist
            name = data.get('name', '')
            artists = data.get('artists', [])
            
            if content_id and artist_id:
                # Store Spotify content
                await database_manager.execute(
                    """INSERT INTO platform_content 
                       (platform, external_id, user_id, title, content_type, artists, status, webhook_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    ("spotify", content_id, artist_id, name, content_type, json.dumps(artists), "published", webhook_id)
                )
                
                # Analyze music metadata and trends
                await _analyze_spotify_track(content_id, content_type, artists)
                
        elif webhook.event == WebhookEvent.CONTENT_UPDATED:
            # Handle metadata updates (title, artist info, etc.)
            content_id = data.get('content_id')
            new_name = data.get('name')
            
            if content_id and new_name:
                await database_manager.execute(
                    "UPDATE platform_content SET title = ?, updated_at = ? WHERE platform = ? AND external_id = ?",
                    (new_name, datetime.utcnow(), "spotify", content_id)
                )
                
        elif webhook.event == WebhookEvent.CONTENT_DELETED:
            # Handle content removal from Spotify
            content_id = data.get('content_id')
            if content_id:
                await database_manager.execute(
                    "UPDATE platform_content SET status = ? WHERE platform = ? AND external_id = ?",
                    ("deleted", "spotify", content_id)
                )
        
        # Update Spotify analytics and streaming data
        await _update_spotify_analytics(webhook.event, data)
        
        logger.info(f"Successfully processed Spotify webhook {webhook_id}")
        
    except Exception as e:
        logger.error(f"Error processing Spotify webhook {webhook_id}: {str(e)}")
        raise


async def _process_stripe_webhook(webhook_id: str, webhook: IncomingWebhook):
    """Process Stripe webhook"""
    try:
        logger.info(f"Processing Stripe webhook {webhook_id} for event {webhook.event}")
        
        data = webhook.data
        event_type = data.get('type', '')
        
        # Handle payment-related events
        if event_type == 'payment_intent.succeeded':
            payment_data = data.get('data', {}).get('object', {})
            payment_id = payment_data.get('id')
            amount = payment_data.get('amount', 0) / 100  # Convert from cents
            currency = payment_data.get('currency', 'usd').upper()
            customer_id = payment_data.get('customer')
            
            if payment_id:
                # Record successful payment
                await database_manager.execute(
                    """INSERT INTO payments 
                       (platform, external_id, customer_id, amount, currency, status, webhook_id) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    ("stripe", payment_id, customer_id, amount, currency, "completed", webhook_id)
                )
                
                # Trigger revenue processing
                await _process_revenue_update(customer_id, amount, currency)
                
        elif event_type == 'payment_intent.payment_failed':
            payment_data = data.get('data', {}).get('object', {})
            payment_id = payment_data.get('id')
            failure_reason = payment_data.get('last_payment_error', {}).get('message', 'Unknown error')
            
            if payment_id:
                # Record failed payment
                await database_manager.execute(
                    """INSERT INTO payments 
                       (platform, external_id, status, failure_reason, webhook_id) 
                       VALUES (?, ?, ?, ?, ?)""",
                    ("stripe", payment_id, "failed", failure_reason, webhook_id)
                )
                
        elif event_type == 'invoice.payment_succeeded':
            invoice_data = data.get('data', {}).get('object', {})
            invoice_id = invoice_data.get('id')
            subscription_id = invoice_data.get('subscription')
            amount_paid = invoice_data.get('amount_paid', 0) / 100
            
            if invoice_id:
                # Record subscription payment
                await database_manager.execute(
                    """INSERT INTO subscription_payments 
                       (platform, invoice_id, subscription_id, amount, status, webhook_id) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    ("stripe", invoice_id, subscription_id, amount_paid, "paid", webhook_id)
                )
        
        # Update payment analytics
        await _update_payment_analytics("stripe", event_type, data)
        
        logger.info(f"Successfully processed Stripe webhook {webhook_id}")
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook {webhook_id}: {str(e)}")
        raise


async def _register_platform_webhook(webhook: WebhookEndpoint, user: dict):
    """Register webhook with external platform"""
    try:
        platform = webhook.platform
        logger.info(f"Registering webhook for platform {platform}")
        
        # Platform-specific webhook registration URLs and methods
        registration_configs = {
            PlatformType.YOUTUBE: {
                'url': 'https://www.googleapis.com/youtube/v3/subscriptions',
                'method': 'POST',
                'headers': {'Authorization': f'Bearer {user.get("youtube_token")}'}
            },
            PlatformType.INSTAGRAM: {
                'url': 'https://graph.facebook.com/v18.0/subscriptions',
                'method': 'POST',
                'headers': {'Authorization': f'Bearer {user.get("instagram_token")}'}
            },
            PlatformType.STRIPE: {
                'url': 'https://api.stripe.com/v1/webhook_endpoints',
                'method': 'POST',
                'headers': {'Authorization': f'Bearer {user.get("stripe_secret_key")}'}
            },
            PlatformType.SPOTIFY: {
                'url': 'https://api.spotify.com/v1/webhooks',
                'method': 'POST',
                'headers': {'Authorization': f'Bearer {user.get("spotify_token")}'}
            }
        }
        
        config = registration_configs.get(platform)
        if not config:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        # Prepare webhook registration payload
        payload = {
            'url': webhook.url,
            'events': webhook.events,
            'description': f'Ainflue webhook for {platform}',
            'active': True
        }
        
        # Add platform-specific payload fields
        if platform == PlatformType.STRIPE:
            payload['enabled_events'] = webhook.events
            
        elif platform == PlatformType.YOUTUBE:
            payload['type'] = 'web_hook'
            payload['address'] = webhook.url
            
        # Make registration request
        async with aiohttp.ClientSession() as session:
            async with session.request(
                config['method'],
                config['url'],
                headers=config['headers'],
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    registration_data = await response.json()
                    external_webhook_id = registration_data.get('id')
                    
                    # Store webhook registration in database
                    await database_manager.execute(
                        """INSERT INTO platform_webhooks 
                           (platform, external_id, url, events, user_id, status) 
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (platform, external_webhook_id, webhook.url, json.dumps(webhook.events), user['id'], 'active')
                    )
                    
                    logger.info(f"Successfully registered webhook {external_webhook_id} for platform {platform}")
                    return external_webhook_id
                else:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Failed to register webhook with {platform}: {error_text}"
                    )
                    
    except Exception as e:
        logger.error(f"Error registering webhook for platform {platform}: {str(e)}")
        raise


async def _unregister_platform_webhook(webhook_id: str, platform: str):
    """Unregister webhook from external platform"""
    try:
        logger.info(f"Unregistering webhook {webhook_id} from platform {platform}")
        
        # Get webhook details from database
        webhook_data = await database_manager.fetch_one(
            "SELECT external_id, user_id FROM platform_webhooks WHERE id = ? AND platform = ?",
            (webhook_id, platform)
        )
        
        if not webhook_data:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        external_id = webhook_data['external_id']
        user_id = webhook_data['user_id']
        
        # Get user credentials for platform API
        user_data = await database_manager.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Platform-specific unregistration URLs and methods
        unregistration_configs = {
            PlatformType.YOUTUBE: {
                'url': f'https://www.googleapis.com/youtube/v3/subscriptions/{external_id}',
                'method': 'DELETE',
                'headers': {'Authorization': f'Bearer {user_data.get("youtube_token")}'}
            },
            PlatformType.INSTAGRAM: {
                'url': f'https://graph.facebook.com/v18.0/{external_id}',
                'method': 'DELETE',
                'headers': {'Authorization': f'Bearer {user_data.get("instagram_token")}'}
            },
            PlatformType.STRIPE: {
                'url': f'https://api.stripe.com/v1/webhook_endpoints/{external_id}',
                'method': 'DELETE',
                'headers': {'Authorization': f'Bearer {user_data.get("stripe_secret_key")}'}
            },
            PlatformType.SPOTIFY: {
                'url': f'https://api.spotify.com/v1/webhooks/{external_id}',
                'method': 'DELETE',
                'headers': {'Authorization': f'Bearer {user_data.get("spotify_token")}'}
            }
        }
        
        config = unregistration_configs.get(platform)
        if not config:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        # Make unregistration request
        async with aiohttp.ClientSession() as session:
            async with session.request(
                config['method'],
                config['url'],
                headers=config['headers']
            ) as response:
                if response.status in [200, 204]:
                    # Update webhook status in database
                    await database_manager.execute(
                        "UPDATE platform_webhooks SET status = ? WHERE id = ?",
                        ('inactive', webhook_id)
                    )
                    
                    logger.info(f"Successfully unregistered webhook {webhook_id} from platform {platform}")
                    return True
                else:
                    error_text = await response.text()
                    logger.warning(f"Failed to unregister webhook from {platform}: {error_text}")
                    
                    # Still mark as inactive in our database even if platform API fails
                    await database_manager.execute(
                        "UPDATE platform_webhooks SET status = ? WHERE id = ?",
                        ('inactive', webhook_id)
                    )
                    return False
                    
    except Exception as e:
        logger.error(f"Error unregistering webhook {webhook_id} from platform {platform}: {str(e)}")
        raise