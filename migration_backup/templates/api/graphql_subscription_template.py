"""GraphQL Subscription Template for IA Chéries Platform
Enterprise-grade real-time GraphQL subscriptions with WebSocket support

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

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, AsyncIterator, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import weakref

import graphene
from graphene import ObjectType, Subscription, Field, String, Boolean, DateTime, Int, List as GrapheneList
from graphql import GraphQLResolveInfo, GraphQLError
from graphql.execution.executors.asyncio import AsyncioExecutor
import redis.asyncio as aioredis

from core.config import get_settings
from core.database import get_db_session
from core.auth import get_current_user, verify_permissions
from core.rate_limiting import subscription_rate_limit
from core.validation import validate_subscription_args
from core.logging import log_subscription_event
from utils.exceptions import SubscriptionException, AuthenticationException
from monitoring.api_metrics import SubscriptionMetrics

logger = logging.getLogger(__name__)
settings = get_settings()


class SubscriptionEventType(Enum):
    """Types of subscription events"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STATUS_CHANGED = "status_changed"
    COLLABORATION_INVITED = "collaboration_invited"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    MONETIZATION_EVENT = "monetization_event"
    ANALYTICS_UPDATE = "analytics_update"


@dataclass
class SubscriptionEvent:
    """Structured subscription event"""
    event_type: SubscriptionEventType
    entity_type: str
    entity_id: str
    data: Dict[str, Any]
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "event_type": self.event_type.value,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "data": self.data,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubscriptionEvent":
        """Create from dictionary"""
        return cls(
            event_type=SubscriptionEventType(data["event_type"]),
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            data=data["data"],
            user_id=data.get("user_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


class SubscriptionManager:
    """Manages GraphQL subscriptions with Redis pub/sub"""
    
    def __init__(self):
        self.redis_client = None
        self.subscribers: Dict[str, Set[str]] = {}  # channel -> set of subscription_ids
        self.subscription_contexts: Dict[str, Dict[str, Any]] = {}  # subscription_id -> context
        self.metrics = SubscriptionMetrics()
        self._cleanup_task = None
    
    async def initialize(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_subscriptions())
    
    async def cleanup(self):
        """Cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self.redis_client:
            await self.redis_client.close()
    
    async def subscribe(
        self, 
        channel: str, 
        subscription_id: str,
        user_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        ttl: int = 3600
    ):
        """Subscribe to a channel with optional filtering"""
        await self.initialize()
        
        # Store subscription context
        self.subscription_contexts[subscription_id] = {
            "channel": channel,
            "user_id": user_id,
            "filters": filters or {},
            "created_at": datetime.utcnow(),
            "ttl": ttl,
            "last_activity": datetime.utcnow()
        }
        
        # Add to subscribers
        if channel not in self.subscribers:
            self.subscribers[channel] = set()
        self.subscribers[channel].add(subscription_id)
        
        # Set TTL in Redis
        await self.redis_client.setex(
            f"subscription:{subscription_id}",
            ttl,
            json.dumps(self.subscription_contexts[subscription_id], default=str)
        )
        
        logger.info(f"Subscription {subscription_id} added to channel {channel}")
        self.metrics.record_subscription(channel, user_id)
    
    async def unsubscribe(self, subscription_id: str):
        """Unsubscribe from all channels"""
        if subscription_id in self.subscription_contexts:
            context = self.subscription_contexts[subscription_id]
            channel = context["channel"]
            
            # Remove from subscribers
            if channel in self.subscribers:
                self.subscribers[channel].discard(subscription_id)
                if not self.subscribers[channel]:
                    del self.subscribers[channel]
            
            # Clean up context
            del self.subscription_contexts[subscription_id]
            
            # Remove from Redis
            await self.redis_client.delete(f"subscription:{subscription_id}")
            
            logger.info(f"Subscription {subscription_id} removed from channel {channel}")
            self.metrics.record_unsubscription(channel, context.get("user_id"))
    
    async def publish_event(self, event: SubscriptionEvent):
        """Publish event to appropriate channels"""
        await self.initialize()
        
        # Determine channels to publish to
        channels = [
            f"{event.entity_type}:all",  # All events for entity type
            f"{event.entity_type}:{event.entity_id}",  # Specific entity events
            f"{event.entity_type}:{event.event_type.value}",  # Specific event type
        ]
        
        # Add user-specific channel if applicable
        if event.user_id:
            channels.append(f"user:{event.user_id}")
        
        # Publish to Redis
        event_data = event.to_dict()
        for channel in channels:
            await self.redis_client.publish(channel, json.dumps(event_data))
            self.metrics.record_published_event(channel, event.event_type.value)
        
        logger.debug(f"Published event {event.event_type.value} to {len(channels)} channels")
    
    async def listen_to_channel(self, channel: str) -> AsyncIterator[SubscriptionEvent]:
        """Listen to channel and yield filtered events"""
        await self.initialize()
        
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(channel)
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        event_data = json.loads(message["data"])
                        event = SubscriptionEvent.from_dict(event_data)
                        
                        # Apply filters for each subscriber
                        for subscription_id in self.subscribers.get(channel, set()).copy():
                            context = self.subscription_contexts.get(subscription_id)
                            if context and self._event_matches_filters(event, context["filters"]):
                                # Update last activity
                                context["last_activity"] = datetime.utcnow()
                                yield event
                                
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.error(f"Error processing subscription message: {e}")
                        continue
                        
        except asyncio.CancelledError:
            logger.info(f"Subscription listener for channel {channel} cancelled")
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
    
    def _event_matches_filters(self, event: SubscriptionEvent, filters: Dict[str, Any]) -> bool:
        """Check if event matches subscription filters"""
        if not filters:
            return True
        
        # Entity ID filter
        if "entity_ids" in filters:
            if event.entity_id not in filters["entity_ids"]:
                return False
        
        # Event type filter
        if "event_types" in filters:
            if event.event_type.value not in filters["event_types"]:
                return False
        
        # User filter
        if "user_ids" in filters:
            if event.user_id not in filters["user_ids"]:
                return False
        
        # Custom data filters
        if "data_filters" in filters:
            for key, expected_value in filters["data_filters"].items():
                if event.data.get(key) != expected_value:
                    return False
        
        return True
    
    async def _cleanup_expired_subscriptions(self):
        """Periodic cleanup of expired subscriptions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                now = datetime.utcnow()
                expired_subscriptions = []
                
                for subscription_id, context in self.subscription_contexts.items():
                    # Check TTL
                    age = (now - context["created_at"]).total_seconds()
                    if age > context["ttl"]:
                        expired_subscriptions.append(subscription_id)
                        continue
                    
                    # Check activity
                    inactive_time = (now - context["last_activity"]).total_seconds()
                    if inactive_time > 1800:  # 30 minutes of inactivity
                        expired_subscriptions.append(subscription_id)
                
                # Clean up expired subscriptions
                for subscription_id in expired_subscriptions:
                    await self.unsubscribe(subscription_id)
                
                if expired_subscriptions:
                    logger.info(f"Cleaned up {len(expired_subscriptions)} expired subscriptions")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in subscription cleanup: {e}")


# Global subscription manager
subscription_manager = SubscriptionManager()


class {{EntityName}}SubscriptionEvent(graphene.ObjectType):
    """GraphQL type for {{entity_description}} subscription events"""
    
    event_type = String(required=True, description="Type of event")
    entity_id = String(required=True, description="ID of affected entity")
    entity = Field("{{EntityName}}Type", description="The affected entity")
    timestamp = DateTime(required=True, description="Event timestamp")
    user_id = String(description="ID of user who triggered the event")
    metadata = graphene.JSONString(description="Additional event metadata")
    
    def resolve_entity(self, info):
        """Resolve the full entity object"""
        # This would typically load the entity from database
        # For this template, we'll return the data from the event
        return self.get("entity_data")


class {{EntityName}}Subscription(ObjectType):
    """GraphQL subscriptions for {{entity_description}}"""
    
    # Subscribe to all events for an entity
    {{entity_name}}_events = Field(
        {{EntityName}}SubscriptionEvent,
        entity_id=String(description="Filter by specific entity ID"),
        event_types=GrapheneList(String, description="Filter by event types"),
        description="Subscribe to {{entity_description}} events"
    )
    
    # Subscribe to user-specific events
    my_{{entity_name}}_events = Field(
        {{EntityName}}SubscriptionEvent,
        event_types=GrapheneList(String, description="Filter by event types"),
        description="Subscribe to your {{entity_description}} events"
    )
    
    # Subscribe to collaboration events
    {{entity_name}}_collaboration_events = Field(
        {{EntityName}}SubscriptionEvent,
        entity_id=String(required=True, description="Entity ID to monitor"),
        description="Subscribe to collaboration events for {{entity_description}}"
    )
    
    # Subscribe to monetization events
    {{entity_name}}_monetization_events = Field(
        {{EntityName}}SubscriptionEvent,
        entity_id=String(description="Filter by entity ID"),
        description="Subscribe to monetization events"
    )
    
    # Subscribe to analytics updates
    {{entity_name}}_analytics_updates = Field(
        {{EntityName}}SubscriptionEvent,
        entity_id=String(description="Filter by entity ID"),
        min_threshold=Int(description="Minimum analytics threshold for notifications"),
        description="Subscribe to analytics updates"
    )
    
    @log_subscription_event
    @subscription_rate_limit(calls=5, period=60)
    async def resolve_{{entity_name}}_events(
        self, 
        info: GraphQLResolveInfo,
        entity_id: Optional[str] = None,
        event_types: Optional[List[str]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to {{entity_description}} events"""
        
        # Authentication check
        user = await get_current_user(info.context["request"])
        if not user:
            raise GraphQLError("Authentication required")
        
        # Validate arguments
        validation_errors = await validate_subscription_args({
            "entity_id": entity_id,
            "event_types": event_types
        })
        if validation_errors:
            raise GraphQLError(f"Validation error: {', '.join(validation_errors)}")
        
        # Build channel and filters
        if entity_id:
            channel = f"{{entity_name}}:{entity_id}"
            # Check entity access permissions
            async with get_db_session() as session:
                entity = await {{EntityName}}Service.get_by_id(session, entity_id)
                if not entity or not await {{EntityName}}Service.can_read(entity, user):
                    raise GraphQLError("Entity not found or access denied")
        else:
            channel = "{{entity_name}}:all"
            # Check general subscription permissions
            if not await verify_permissions(user, "subscribe_{{entity_name}}"):
                raise GraphQLError("Insufficient permissions")
        
        filters = {}
        if entity_id:
            filters["entity_ids"] = [entity_id]
        if event_types:
            filters["event_types"] = event_types
        
        # Generate unique subscription ID
        subscription_id = f"{user.id}_{channel}_{datetime.utcnow().timestamp()}"
        
        try:
            # Subscribe to channel
            await subscription_manager.subscribe(
                channel=channel,
                subscription_id=subscription_id,
                user_id=user.id,
                filters=filters,
                ttl=3600  # 1 hour
            )
            
            # Listen for events
            async for event in subscription_manager.listen_to_channel(channel):
                # Additional permission check per event
                if await self._can_receive_event(event, user):
                    yield {
                        "event_type": event.event_type.value,
                        "entity_id": event.entity_id,
                        "entity_data": event.data,
                        "timestamp": event.timestamp,
                        "user_id": event.user_id,
                        "metadata": event.metadata
                    }
                    
        except asyncio.CancelledError:
            logger.info(f"Subscription {subscription_id} cancelled")
        except Exception as e:
            logger.error(f"Error in {{entity_name}} subscription: {e}")
            raise GraphQLError("Subscription error")
        finally:
            await subscription_manager.unsubscribe(subscription_id)
    
    @log_subscription_event
    @subscription_rate_limit(calls=3, period=60)
    async def resolve_my_{{entity_name}}_events(
        self, 
        info: GraphQLResolveInfo,
        event_types: Optional[List[str]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to user's own {{entity_description}} events"""
        
        user = await get_current_user(info.context["request"])
        if not user:
            raise GraphQLError("Authentication required")
        
        channel = f"user:{user.id}"
        filters = {"user_ids": [user.id]}
        if event_types:
            filters["event_types"] = event_types
        
        subscription_id = f"{user.id}_my_events_{datetime.utcnow().timestamp()}"
        
        try:
            await subscription_manager.subscribe(
                channel=channel,
                subscription_id=subscription_id,
                user_id=user.id,
                filters=filters,
                ttl=7200  # 2 hours for user subscriptions
            )
            
            async for event in subscription_manager.listen_to_channel(channel):
                yield {
                    "event_type": event.event_type.value,
                    "entity_id": event.entity_id,
                    "entity_data": event.data,
                    "timestamp": event.timestamp,
                    "user_id": event.user_id,
                    "metadata": event.metadata
                }
                
        except asyncio.CancelledError:
            logger.info(f"User subscription {subscription_id} cancelled")
        except Exception as e:
            logger.error(f"Error in user {{entity_name}} subscription: {e}")
            raise GraphQLError("Subscription error")
        finally:
            await subscription_manager.unsubscribe(subscription_id)
    
    @log_subscription_event
    async def resolve_{{entity_name}}_collaboration_events(
        self, 
        info: GraphQLResolveInfo,
        entity_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """Subscribe to collaboration events"""
        
        user = await get_current_user(info.context["request"])
        if not user:
            raise GraphQLError("Authentication required")
        
        # Verify collaboration access
        async with get_db_session() as session:
            entity = await {{EntityName}}Service.get_by_id(session, entity_id)
            if not entity:
                raise GraphQLError("Entity not found")
            
            # Check if user is collaborator or owner
            if not await {{EntityName}}Service.is_collaborator(entity, user):
                raise GraphQLError("Access denied - not a collaborator")
        
        channel = f"{{entity_name}}:collaboration:{entity_id}"
        filters = {
            "entity_ids": [entity_id],
            "event_types": [
                SubscriptionEventType.COLLABORATION_INVITED.value,
                SubscriptionEventType.COLLABORATION_ACCEPTED.value
            ]
        }
        
        subscription_id = f"{user.id}_collab_{entity_id}_{datetime.utcnow().timestamp()}"
        
        try:
            await subscription_manager.subscribe(
                channel=channel,
                subscription_id=subscription_id,
                user_id=user.id,
                filters=filters,
                ttl=3600
            )
            
            async for event in subscription_manager.listen_to_channel(channel):
                yield {
                    "event_type": event.event_type.value,
                    "entity_id": event.entity_id,
                    "entity_data": event.data,
                    "timestamp": event.timestamp,
                    "user_id": event.user_id,
                    "metadata": event.metadata
                }
                
        except asyncio.CancelledError:
            logger.info(f"Collaboration subscription {subscription_id} cancelled")
        finally:
            await subscription_manager.unsubscribe(subscription_id)
    
    async def _can_receive_event(self, event: SubscriptionEvent, user: Any) -> bool:
        """Check if user can receive this specific event"""
        
        # Owner always receives events
        if event.user_id == user.id:
            return True
        
        # Check entity-level permissions
        async with get_db_session() as session:
            entity = await {{EntityName}}Service.get_by_id(session, event.entity_id)
            if entity and await {{EntityName}}Service.can_read(entity, user):
                return True
        
        # Admin users receive all events
        if await verify_permissions(user, "admin_{{entity_name}}"):
            return True
        
        return False


# Event publishing helpers
async def publish_{{entity_name}}_created(entity: Any, user: Any):
    """Publish entity created event"""
    event = SubscriptionEvent(
        event_type=SubscriptionEventType.CREATED,
        entity_type="{{entity_name}}",
        entity_id=str(entity.id),
        data={
            "name": entity.name,
            "status": entity.status,
            "created_by": user.id
        },
        user_id=user.id,
        metadata={"action": "create"}
    )
    await subscription_manager.publish_event(event)


async def publish_{{entity_name}}_updated(entity: Any, user: Any, changes: Dict[str, Any]):
    """Publish entity updated event"""
    event = SubscriptionEvent(
        event_type=SubscriptionEventType.UPDATED,
        entity_type="{{entity_name}}",
        entity_id=str(entity.id),
        data={
            "name": entity.name,
            "status": entity.status,
            "changes": changes
        },
        user_id=user.id,
        metadata={"action": "update", "fields_changed": list(changes.keys())}
    )
    await subscription_manager.publish_event(event)


async def publish_{{entity_name}}_deleted(entity_id: str, user: Any):
    """Publish entity deleted event"""
    event = SubscriptionEvent(
        event_type=SubscriptionEventType.DELETED,
        entity_type="{{entity_name}}",
        entity_id=entity_id,
        data={"deleted": True},
        user_id=user.id,
        metadata={"action": "delete"}
    )
    await subscription_manager.publish_event(event)


async def publish_monetization_event(entity_id: str, amount: float, currency: str, user: Any):
    """Publish monetization event"""
    event = SubscriptionEvent(
        event_type=SubscriptionEventType.MONETIZATION_EVENT,
        entity_type="{{entity_name}}",
        entity_id=entity_id,
        data={
            "amount": amount,
            "currency": currency,
            "type": "revenue"
        },
        user_id=user.id,
        metadata={"category": "monetization"}
    )
    await subscription_manager.publish_event(event)


# Subscription schema
class Subscription(ObjectType):
    """Root subscription for all {{entity_description}} events"""
    
    {{entity_name}}_events = {{EntityName}}Subscription.{{entity_name}}_events
    my_{{entity_name}}_events = {{EntityName}}Subscription.my_{{entity_name}}_events
    {{entity_name}}_collaboration_events = {{EntityName}}Subscription.{{entity_name}}_collaboration_events
    {{entity_name}}_monetization_events = {{EntityName}}Subscription.{{entity_name}}_monetization_events
    {{entity_name}}_analytics_updates = {{EntityName}}Subscription.{{entity_name}}_analytics_updates


# Export for template system
__all__ = [
    "Subscription",
    "{{EntityName}}Subscription",
    "{{EntityName}}SubscriptionEvent",
    "SubscriptionManager",
    "SubscriptionEvent",
    "SubscriptionEventType",
    "subscription_manager",
    "publish_{{entity_name}}_created",
    "publish_{{entity_name}}_updated",
    "publish_{{entity_name}}_deleted",
    "publish_monetization_event"
]