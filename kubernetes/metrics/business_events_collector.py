"""
IA Influencer Agent - Business Events Metrics Collector
Enterprise business metrics collection for content protection and monetization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

  AVERTISSEMENT LÉGAL STRICT 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Content protection business events tracking
- Revenue generation metrics collection
- User engagement analytics
- Platform-specific performance tracking
- Licensing transaction monitoring
- Collaboration opportunity metrics
- Creator success measurement
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal

from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager
from backend.utils.database import get_database_session
from .config import get_metrics_config

logger = get_logger(__name__)
metrics_config = get_metrics_config()


class BusinessEventType(Enum):
    """Business event types for metrics collection"""
    # Content Protection Events
    CONTENT_UPLOADED = "content_uploaded"
    FINGERPRINT_CREATED = "fingerprint_created"
    VIOLATION_DETECTED = "violation_detected"
    TAKEDOWN_REQUESTED = "takedown_requested"
    TAKEDOWN_COMPLETED = "takedown_completed"
    
    # Revenue Events
    REVENUE_GENERATED = "revenue_generated"
    PAYMENT_PROCESSED = "payment_processed"
    LICENSING_DEAL_CREATED = "licensing_deal_created"
    ROYALTY_DISTRIBUTED = "royalty_distributed"
    
    # User Engagement Events
    USER_REGISTERED = "user_registered"
    USER_VERIFIED = "user_verified"
    PROFILE_COMPLETED = "profile_completed"
    CONTENT_SHARED = "content_shared"
    COLLABORATION_INITIATED = "collaboration_initiated"
    
    # Platform Events
    PLATFORM_CONNECTED = "platform_connected"
    ANALYTICS_GENERATED = "analytics_generated"
    RECOMMENDATION_PROVIDED = "recommendation_provided"
    AI_MODEL_TRAINED = "ai_model_trained"


@dataclass
class BusinessEvent:
    """Business event data structure"""
    event_type: BusinessEventType
    tenant_id: str
    user_id: Optional[str]
    timestamp: datetime
    event_data: Dict[str, Any]
    platform: Optional[str] = None
    content_type: Optional[str] = None
    revenue_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BusinessEventsCollector:
    """
    Enterprise business events metrics collector
    
    Tracks all business-critical events for the IA Influencer platform
    including content protection, revenue generation, and user engagement
    """
    
    def __init__(self):
        self.redis_manager = RedisManager()
        self.logger = logger
        self.event_buffer: List[BusinessEvent] = []
        self.buffer_lock = asyncio.Lock()
        self.processing_enabled = True
        
        # Event processing intervals
        self.buffer_flush_interval = 30  # seconds
        self.metrics_calculation_interval = 300  # 5 minutes
        
        # Start background processing
        asyncio.create_task(self._start_background_processing())
    
    async def track_content_upload(
        self,
        tenant_id: str,
        user_id: str,
        content_type: str,
        file_size: int,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track content upload event"""
        event = BusinessEvent(
            event_type=BusinessEventType.CONTENT_UPLOADED,
            tenant_id=tenant_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            content_type=content_type,
            event_data={
                "file_size": file_size,
                "duration": duration,
                "upload_success": True
            },
            metadata=metadata
        )
        await self._add_event(event)
    
    async def track_fingerprint_creation(
        self,
        tenant_id: str,
        user_id: str,
        content_type: str,
        algorithm: str,
        processing_time: float,
        fingerprint_quality: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track fingerprint creation event"""
        event = BusinessEvent(
            event_type=BusinessEventType.FINGERPRINT_CREATED,
            tenant_id=tenant_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            content_type=content_type,
            event_data={
                "algorithm": algorithm,
                "processing_time": processing_time,
                "fingerprint_quality": fingerprint_quality,
                "success": True
            },
            metadata=metadata
        )
        await self._add_event(event)
    
    async def track_violation_detection(
        self,
        tenant_id: str,
        user_id: str,
        platform: str,
        content_type: str,
        similarity_score: float,
        detected_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track content violation detection"""
        event = BusinessEvent(
            event_type=BusinessEventType.VIOLATION_DETECTED,
            tenant_id=tenant_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            platform=platform,
            content_type=content_type,
            event_data={
                "similarity_score": similarity_score,
                "detected_url": detected_url,
                "detection_accuracy": similarity_score >= 0.8
            },
            metadata=metadata
        )
        await self._add_event(event)
    
    async def track_revenue_generation(
        self,
        tenant_id: str,
        user_id: str,
        platform: str,
        content_type: str,
        amount: Decimal,
        currency: str,
        revenue_source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track revenue generation event"""
        event = BusinessEvent(
            event_type=BusinessEventType.REVENUE_GENERATED,
            tenant_id=tenant_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            platform=platform,
            content_type=content_type,
            revenue_amount=amount,
            currency=currency,
            event_data={
                "revenue_source": revenue_source,
                "amount_usd": float(amount),  # Convert to USD for comparison
                "is_recurring": revenue_source in ["subscription", "licensing"]
            },
            metadata=metadata
        )
        await self._add_event(event)
    
    async def track_licensing_deal(
        self,
        tenant_id: str,
        user_id: str,
        licensee_id: str,
        content_type: str,
        deal_value: Decimal,
        currency: str,
        license_type: str,
        duration_months: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track licensing deal creation"""
        event = BusinessEvent(
            event_type=BusinessEventType.LICENSING_DEAL_CREATED,
            tenant_id=tenant_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            content_type=content_type,
            revenue_amount=deal_value,
            currency=currency,
            event_data={
                "licensee_id": licensee_id,
                "license_type": license_type,
                "duration_months": duration_months,
                "deal_value": float(deal_value),
                "is_exclusive": license_type == "exclusive"
            },
            metadata=metadata
        )
        await self._add_event(event)
    
    async def track_user_engagement(
        self,
        tenant_id: str,
        user_id: str,
        action: str,
        platform: Optional[str] = None,
        engagement_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track user engagement event"""
        event_type_map = {
            "register": BusinessEventType.USER_REGISTERED,
            "verify": BusinessEventType.USER_VERIFIED,
            "complete_profile": BusinessEventType.PROFILE_COMPLETED,
            "share": BusinessEventType.CONTENT_SHARED,
            "collaborate": BusinessEventType.COLLABORATION_INITIATED
        }
        
        event = BusinessEvent(
            event_type=event_type_map.get(action, BusinessEventType.USER_REGISTERED),
            tenant_id=tenant_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            platform=platform,
            event_data={
                "action": action,
                "engagement_score": engagement_score,
                "platform_specific": platform is not None
            },
            metadata=metadata
        )
        await self._add_event(event)
    
    async def track_ai_model_performance(
        self,
        tenant_id: str,
        model_name: str,
        model_version: str,
        accuracy: float,
        inference_time: float,
        prediction_count: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track AI model performance metrics"""
        event = BusinessEvent(
            event_type=BusinessEventType.AI_MODEL_TRAINED,
            tenant_id=tenant_id,
            user_id=None,
            timestamp=datetime.now(timezone.utc),
            event_data={
                "model_name": model_name,
                "model_version": model_version,
                "accuracy": accuracy,
                "inference_time": inference_time,
                "prediction_count": prediction_count,
                "performance_score": accuracy * (1.0 / max(inference_time, 0.001))
            },
            metadata=metadata
        )
        await self._add_event(event)
    
    async def _add_event(self, event: BusinessEvent) -> None:
        """Add event to processing buffer"""
        async with self.buffer_lock:
            self.event_buffer.append(event)
            
            # Flush buffer if it gets too large
            if len(self.event_buffer) >= 100:
                await self._flush_events()
    
    async def _flush_events(self) -> None:
        """Flush events buffer to storage and processing"""
        if not self.event_buffer:
            return
        
        events_to_process = self.event_buffer.copy()
        self.event_buffer.clear()
        
        try:
            # Store events in database
            await self._store_events(events_to_process)
            
            # Process real-time metrics
            await self._process_realtime_metrics(events_to_process)
            
            # Cache events for aggregation
            await self._cache_events_for_aggregation(events_to_process)
            
        except Exception as e:
            self.logger.error(f"Error flushing events: {e}")
    
    async def _store_events(self, events: List[BusinessEvent]) -> None:
        """Store events in database"""



        try:
            async with get_database_session() as session:
                for event in events:
                    # Store in events table
                    await session.execute(
                        """
                        INSERT INTO business_events 
                        (tenant_id, user_id, event_type, timestamp, event_data, 
                         platform, content_type, revenue_amount, currency, metadata)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        """,
                        event.tenant_id,
                        event.user_id,
                        event.event_type.value,
                        event.timestamp,
                        json.dumps(event.event_data),
                        event.platform,
                        event.content_type,
                        float(event.revenue_amount) if event.revenue_amount else None,
                        event.currency,
                        json.dumps(event.metadata) if event.metadata else None
                    )
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing events in database: {e}")
    
    async def _process_realtime_metrics(self, events: List[BusinessEvent]) -> None:
        """Process real-time metrics from events"""



        try:
            # Group events by type and tenant
            event_groups = defaultdict(lambda: defaultdict(list))
            for event in events:
                event_groups[event.tenant_id][event.event_type].append(event)
            
            for tenant_id, tenant_events in event_groups.items():
                # Calculate real-time metrics
                metrics = await self._calculate_realtime_metrics(tenant_id, tenant_events)
                
                # Store in Redis for immediate access
                await self.redis_manager.set_json(
                    f"realtime_metrics:{tenant_id}",
                    metrics,
                    expire=300  # 5 minutes
                )
                
        except Exception as e:
            self.logger.error(f"Error processing real-time metrics: {e}")
    
    async def _calculate_realtime_metrics(
        self,
        tenant_id: str,
        events_by_type: Dict[BusinessEventType, List[BusinessEvent]]
    ) -> Dict[str, Any]:
        """Calculate real-time metrics from events"""
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id,
            "period": "realtime"
        }
        
        # Content protection metrics
        if BusinessEventType.VIOLATION_DETECTED in events_by_type:
            violations = events_by_type[BusinessEventType.VIOLATION_DETECTED]
            metrics["violations_detected"] = len(violations)
            metrics["avg_similarity_score"] = sum(
                v.event_data["similarity_score"] for v in violations
            ) / len(violations)
        
        # Revenue metrics
        revenue_events = events_by_type.get(BusinessEventType.REVENUE_GENERATED, [])
        if revenue_events:
            total_revenue = sum(
                float(event.revenue_amount) for event in revenue_events
                if event.revenue_amount
            )
            metrics["revenue_generated"] = total_revenue
            metrics["revenue_transactions"] = len(revenue_events)
        
        # User engagement metrics
        engagement_events = [
            event for event_type, events in events_by_type.items()
            for event in events
            if event_type in [
                BusinessEventType.USER_REGISTERED,
                BusinessEventType.CONTENT_SHARED,
                BusinessEventType.COLLABORATION_INITIATED
            ]
        ]
        metrics["user_engagement_events"] = len(engagement_events)
        
        return metrics
    
    async def _cache_events_for_aggregation(self, events: List[BusinessEvent]) -> None:
        """Cache events for later aggregation"""



        try:
            # Group events by hour for aggregation
            current_hour = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            
            for event in events:
                cache_key = f"events_aggregation:{current_hour.isoformat()}:{event.tenant_id}"
                
                # Add event to hourly aggregation cache
                await self.redis_manager.list_push(
                    cache_key,
                    json.dumps(asdict(event), default=str),
                    expire=86400  # 24 hours
                )
                
        except Exception as e:
            self.logger.error(f"Error caching events for aggregation: {e}")
    
    async def get_business_metrics_summary(
        self,
        tenant_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get business metrics summary for tenant"""



        try:
            # Parse time range
            if time_range == "1h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=1)
            elif time_range == "24h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            elif time_range == "7d":
                start_time = datetime.now(timezone.utc) - timedelta(days=7)
            elif time_range == "30d":
                start_time = datetime.now(timezone.utc) - timedelta(days=30)
            else:
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            async with get_database_session() as session:
                # Get business metrics from database
                result = await session.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_events,
                        COUNT(CASE WHEN event_type = 'content_uploaded' THEN 1 END) as content_uploads,
                        COUNT(CASE WHEN event_type = 'violation_detected' THEN 1 END) as violations_detected,
                        COALESCE(SUM(revenue_amount), 0) as total_revenue,
                        COUNT(DISTINCT user_id) as active_users,
                        COUNT(CASE WHEN event_type = 'licensing_deal_created' THEN 1 END) as licensing_deals
                    FROM business_events 
                    WHERE tenant_id = $1 AND timestamp >= $2
                    """,
                    tenant_id,
                    start_time
                )
                
                return {
                    "time_range": time_range,
                    "total_events": result["total_events"],
                    "content_uploads": result["content_uploads"],
                    "violations_detected": result["violations_detected"],
                    "total_revenue": float(result["total_revenue"]),
                    "active_users": result["active_users"],
                    "licensing_deals": result["licensing_deals"],
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting business metrics summary: {e}")
            return {}
    
    async def get_platform_performance_metrics(
        self,
        tenant_id: str,
        platform: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get platform-specific performance metrics"""



        try:
            if time_range == "1h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=1)
            elif time_range == "24h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            elif time_range == "7d":
                start_time = datetime.now(timezone.utc) - timedelta(days=7)
            else:
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            async with get_database_session() as session:
                result = await session.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_events,
                        COUNT(CASE WHEN event_type = 'violation_detected' THEN 1 END) as violations,
                        COALESCE(SUM(revenue_amount), 0) as revenue,
                        COUNT(DISTINCT user_id) as active_users
                    FROM business_events 
                    WHERE tenant_id = $1 AND platform = $2 AND timestamp >= $3
                    """,
                    tenant_id,
                    platform,
                    start_time
                )
                
                return {
                    "platform": platform,
                    "time_range": time_range,
                    "total_events": result["total_events"],
                    "violations_detected": result["violations"],
                    "revenue_generated": float(result["revenue"]),
                    "active_users": result["active_users"],
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting platform performance metrics: {e}")
            return {}
    
    async def _start_background_processing(self) -> None:
        """Start background event processing"""
        while self.processing_enabled:
            try:
                # Flush events buffer periodically
                await asyncio.sleep(self.buffer_flush_interval)
                async with self.buffer_lock:
                    if self.event_buffer:
                        await self._flush_events()
                        
            except Exception as e:
                self.logger.error(f"Error in background processing: {e}")
                await asyncio.sleep(5)
    
    async def stop_processing(self) -> None:
        """Stop background processing and flush remaining events"""
        self.processing_enabled = False
        async with self.buffer_lock:
            if self.event_buffer:
                await self._flush_events()
