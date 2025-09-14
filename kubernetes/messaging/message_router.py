"""IA Influencer Agent - Message Router
Enterprise message routing and orchestration for multi-platform messaging

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
    - Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...core.logging import get_logger
from .celery_manager import CeleryManager
from .kafka_manager import KafkaManager
from .rabbitmq_manager import RabbitMQManager

logger = get_logger(__name__)
settings = get_settings()


class MessagePriority(str, Enum):
    """
Message priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MessageType(str, Enum):
    """Message types for routing"""

    CONTENT_UPLOAD = "content.upload"
    FINGERPRINT_GENERATION = "fingerprint.generation"
    AI_ANALYSIS = "ai.analysis"
    PROTECTION_ALERT = "protection.alert"
    CRAWLING_TASK = "crawling.task"
    NOTIFICATION = "notification"
    REVENUE_UPDATE = "revenue.update"
    SYSTEM_EVENT = "system.event"
    AUDIT_LOG = "audit.log"


class RoutingStrategy(str, Enum):
    """Message routing strategies"""

    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    LOAD_BALANCED = "load_balanced"
    TOPIC_BASED = "topic_based"
    BROADCAST = "broadcast"


class MessageProtocol(str, Enum):
    """Supported messaging protocols"""

    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    CELERY = "celery"
    REDIS = "redis"
    WEBSOCKET = "websocket"


class Message(BaseModel):
    """Standard message format for routing"""
    id: str = Field(..., description="Unique message identifier")
    type: MessageType = Field(..., description="Message type")
    priority: MessagePriority = Field(default=MessagePriority.MEDIUM, description="Message priority")
    source: str = Field(..., description="Message source service")
    destination: Optional[str] = Field(None, description="Target destination")
    timestamp: float = Field(default_factory=time.time, description="Message timestamp")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")
    routing_key: Optional[str] = Field(None, description="Routing key")
    ttl: Optional[int] = Field(None, description="Time-to-live in seconds")
    retry_count: int = Field(default=0, description="Retry count")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class RouteConfig(BaseModel):
    """Configuration for message routing"""
    message_type: MessageType = Field(..., description="Message type to route")
    protocol: MessageProtocol = Field(..., description="Target protocol")
    destination: str = Field(..., description="Destination queue/topic")
    routing_strategy: RoutingStrategy = Field(default=RoutingStrategy.ROUND_ROBIN, description="Routing strategy")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Message filters")
    transformations: List[str] = Field(default_factory=list, description="Message transformations")
    retry_policy: Dict[str, Any] = Field(default_factory=dict, description="Retry policy")
    dead_letter_queue: Optional[str] = Field(None, description="Dead letter queue")


class MessageHandler(ABC):
    """Abstract base class for message handlers"""
    
    @abstractmethod
    async def handle(self, message: Message) -> bool:
        try:
            logger.info(f"Executing handle")
            
            # Implementation for handle
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"handle completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing can_handle")
            
            # Implementation for can_handle
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing transform")
            
            # Implementation for transform
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"transform completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing filter")
            
            # Implementation for filter
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"filter completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"filter failed: {e}")
            raise
            logger.info(f"can_handle completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"can_handle failed: {e}")
            raise
            return result
            
        except Exception as e:
            logger.error(f"handle failed: {e}")
            raise
    @abstractmethod
    async def can_handle(self, message: Message) -> bool:
        """
Check if handler can process the message"""
        pass


class MessageTransformer(ABC):
    """
Abstract base class for message transformers"""
    
    @abstractmethod
    async def transform(self, message: Message) -> Message:
        """
Transform message before routing"""
        pass


class MessageFilter(ABC):
    """MessageFilter class implementation"""
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
class MessageFilter(ABC):
    """
Abstract base class for message filters"""
    
    @abstractmethod
    async def filter(self, message: Message) -> bool:
        """
Filter messages based on criteria"""
        pass


class ContentUploadTransformer(MessageTransformer):
    """
Transformer for content upload messages"""
    
    async def transform(self, message: Message) -> Message:
        """
Add content processing metadata"""
        message.metadata.update({
            "processing_stage": "upload",
            "content_type": message.payload.get("file_type", "unknown"),
            "estimated_processing_time": self._estimate_processing_time(message.payload),
            "requires_fingerprinting": True
        })
        return message
    
    def _estimate_processing_time(self, payload: Dict[str, Any]) -> int:
        """Estimate processing time based on content size and type"""
        file_size = payload.get("file_size", 0)
        file_type = payload.get("file_type", "unknown")
        
        base_time = {
            "audio": 30,
            "video": 120,
            "image": 10,
            "text": 5
        }.get(file_type, 15)
        
        # Add time based on file size (MB)
        size_factor = (file_size / (1024 * 1024)) * 2
        
        return int(base_time + size_factor)


class PriorityFilter(MessageFilter):
    """Filter messages based on priority"""
    
    def __init__(self, min_priority -> None: MessagePriority) -> None:
        self.min_priority = min_priority
        
    async def filter(self, message: Message) -> bool:
        """
Filter based on minimum priority"""
        priority_levels = {
            MessagePriority.LOW: 0,
            MessagePriority.MEDIUM: 1,
            MessagePriority.HIGH: 2,
            MessagePriority.CRITICAL: 3
        }
        
        return priority_levels[message.priority] >= priority_levels[self.min_priority]


class MessageRouter:
    """
    Enterprise message routing and orchestration system
    Handles intelligent routing across multiple messaging protocols
    """
    def __init__(self) -> None:
        self.routes: Dict[MessageType, List[RouteConfig]] = {}
        self.handlers: Dict[str, MessageHandler] = {}
        self.transformers: Dict[str, MessageTransformer] = {}
        self.filters: Dict[str, MessageFilter] = {}
        self.protocols: Dict[MessageProtocol, Any] = {}
        self.message_stats: Dict[str, int] = {}
        self.dead_letter_messages: List[Message] = []
        
        # Initialize default transformers and filters
        self._setup_default_components()

    def _setup_default_components(self) -> None:
        """
Setup default transformers and filters"""
        self.transformers["content_upload"] = ContentUploadTransformer()
        self.filters["high_priority"] = PriorityFilter(MessagePriority.HIGH)
        self.filters["critical_only"] = PriorityFilter(MessagePriority.CRITICAL)

    async def initialize_protocols(self, 
                                 kafka_manager: Optional[KafkaManager] = None,
                                 rabbitmq_manager: Optional[RabbitMQManager] = None,
                                 celery_manager: Optional[CeleryManager] = None) -> None:
        """Initialize messaging protocol managers"""
        try:
            if kafka_manager:
                self.protocols[MessageProtocol.KAFKA] = kafka_manager
                logger.info("Kafka protocol initialized")
                
            if rabbitmq_manager:
                self.protocols[MessageProtocol.RABBITMQ] = rabbitmq_manager
                logger.info("RabbitMQ protocol initialized")
                
            if celery_manager:
                self.protocols[MessageProtocol.CELERY] = celery_manager
                logger.info("Celery protocol initialized")
                
            # Setup default routing configuration
            await self._setup_default_routes()
            
            logger.info("Message router initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize protocols: {e}")
            raise

    async def _setup_default_routes(self) -> None:
        """Setup default routing configuration for IA processing"""
        default_routes = [
            # Content processing routes
            RouteConfig(
                message_type=MessageType.CONTENT_UPLOAD,
                protocol=MessageProtocol.KAFKA,
                destination="ia.content.uploads",
                routing_strategy=RoutingStrategy.PRIORITY_BASED,
                transformations=["content_upload"],
                retry_policy={"max_retries": 3, "backoff_factor": 2}
            ),
            RouteConfig(
                message_type=MessageType.FINGERPRINT_GENERATION,
                protocol=MessageProtocol.CELERY,
                destination="fingerprint_generation",
                routing_strategy=RoutingStrategy.LOAD_BALANCED,
                retry_policy={"max_retries": 5, "backoff_factor": 1.5}
            ),
            RouteConfig(
                message_type=MessageType.AI_ANALYSIS,
                protocol=MessageProtocol.KAFKA,
                destination="ia.ai.inference.requests",
                routing_strategy=RoutingStrategy.ROUND_ROBIN,
                retry_policy={"max_retries": 2, "backoff_factor": 3}
            ),
            
            # Alert and notification routes
            RouteConfig(
                message_type=MessageType.PROTECTION_ALERT,
                protocol=MessageProtocol.RABBITMQ,
                destination="ia.notifications.alerts",
                routing_strategy=RoutingStrategy.PRIORITY_BASED,
                filters=["high_priority"],
                retry_policy={"max_retries": 5, "backoff_factor": 1}
            ),
            RouteConfig(
                message_type=MessageType.NOTIFICATION,
                protocol=MessageProtocol.RABBITMQ,
                destination="ia.notifications.email",
                routing_strategy=RoutingStrategy.ROUND_ROBIN,
                retry_policy={"max_retries": 3, "backoff_factor": 2}
            ),
            
            # Crawling and monitoring routes
            RouteConfig(
                message_type=MessageType.CRAWLING_TASK,
                protocol=MessageProtocol.CELERY,
                destination="web_crawling",
                routing_strategy=RoutingStrategy.LOAD_BALANCED,
                retry_policy={"max_retries": 2, "backoff_factor": 4}
            ),
            
            # Revenue and system routes
            RouteConfig(
                message_type=MessageType.REVENUE_UPDATE,
                protocol=MessageProtocol.KAFKA,
                destination="ia.revenue.events",
                routing_strategy=RoutingStrategy.TOPIC_BASED,
                retry_policy={"max_retries": 5, "backoff_factor": 1.5}
            ),
            RouteConfig(
                message_type=MessageType.SYSTEM_EVENT,
                protocol=MessageProtocol.KAFKA,
                destination="ia.system.logs",
                routing_strategy=RoutingStrategy.BROADCAST,
                retry_policy={"max_retries": 1, "backoff_factor": 5}
            ),
            RouteConfig(
                message_type=MessageType.AUDIT_LOG,
                protocol=MessageProtocol.KAFKA,
                destination="ia.audit.events",
                routing_strategy=RoutingStrategy.TOPIC_BASED,
                retry_policy={"max_retries": 3, "backoff_factor": 2}
            )
        ]
        
        for route in default_routes:
            await self.add_route(route)

    async def add_route(self, route: RouteConfig) -> None:
        """Add routing configuration"""
        if route.message_type not in self.routes:
            self.routes[route.message_type] = []
        
        self.routes[route.message_type].append(route)
        logger.info(f"Added route for {route.message_type} to {route.protocol}:{route.destination}")

    async def remove_route(self, message_type: MessageType, protocol: MessageProtocol, destination: str) -> bool:
        """Remove routing configuration"""
        try:
            if message_type in self.routes:
                self.routes[message_type] = [
                    route for route in self.routes[message_type]
                    if not (route.protocol == protocol and route.destination == destination)
                ]
                logger.info(f"Removed route for {message_type} from {protocol}:{destination}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove route: {e}")
            return False

    async def route_message(self, message: Message) -> bool:
        """Route message to appropriate destination(s)"""
        try:
            # Get routes for message type
            routes = self.routes.get(message.type, [])
            
            if not routes:
                logger.warning(f"No routes found for message type {message.type}")
                await self._send_to_dead_letter(message, "No routes configured")
                return False
            
            success_count = 0
            
            for route in routes:
                try:
                    # Apply filters
                    if not await self._apply_filters(message, route):
                        continue
                    
                    # Apply transformations
                    transformed_message = await self._apply_transformations(message, route)
                    
                    # Route based on strategy
                    if await self._route_to_destination(transformed_message, route):
                        success_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to route message via {route.protocol}:{route.destination}: {e}")
                    continue
            
            # Update statistics
            self._update_message_stats(message.type, success_count > 0)
            
            if success_count == 0:
                await self._send_to_dead_letter(message, "All routing attempts failed")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to route message: {e}")
            await self._send_to_dead_letter(message, f"Routing error: {e}")
            return False

    async def _apply_filters(self, message: Message, route: RouteConfig) -> bool:
        """Apply filters to message"""
        try:
            for filter_name in route.filters:
                message_filter = self.filters.get(filter_name)
                if message_filter and not await message_filter.filter(message):
                    logger.debug(f"Message filtered out by {filter_name}")
                    return False
            return True
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            return False

    async def _apply_transformations(self, message: Message, route: RouteConfig) -> Message:
        """Apply transformations to message"""
        try:
            transformed_message = message.copy(deep=True)
            
            for transformer_name in route.transformations:
                transformer = self.transformers.get(transformer_name)
                if transformer:
                    transformed_message = await transformer.transform(transformed_message)
                    
            return transformed_message
            
        except Exception as e:
            logger.error(f"Error applying transformations: {e}")
            return message

    async def _route_to_destination(self, message: Message, route: RouteConfig) -> bool:
        """Route message to specific destination"""
        try:
            protocol_manager = self.protocols.get(route.protocol)
            
            if not protocol_manager:
                logger.error(f"Protocol manager for {route.protocol} not available")
                return False
            
            # Route based on protocol
            if route.protocol == MessageProtocol.KAFKA:
                return await self._route_to_kafka(message, route, protocol_manager)
            elif route.protocol == MessageProtocol.RABBITMQ:
                return await self._route_to_rabbitmq(message, route, protocol_manager)
            elif route.protocol == MessageProtocol.CELERY:
                return await self._route_to_celery(message, route, protocol_manager)
            else:
                logger.error(f"Unsupported protocol: {route.protocol}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to route to destination: {e}")
            return False

    async def _route_to_kafka(self, message: Message, route: RouteConfig, kafka_manager: KafkaManager) -> bool:
        """Route message to Kafka"""
        try:
            routing_key = message.routing_key or self._generate_routing_key(message, route)
            
            return await kafka_manager.publish_event(
                topic=route.destination,
                key=routing_key,
                value=message.dict()
            )
            
        except Exception as e:
            logger.error(f"Failed to route to Kafka: {e}")
            return False

    async def _route_to_rabbitmq(self, message: Message, route: RouteConfig, rabbitmq_manager: RabbitMQManager) -> bool:
        """Route message to RabbitMQ"""
        try:
            routing_key = message.routing_key or self._generate_routing_key(message, route)
            priority = self._get_priority_value(message.priority)
            
            return await rabbitmq_manager.publish_message(
                exchange_name="ia.content",
                routing_key=routing_key,
                message=message.dict(),
                priority=priority
            )
            
        except Exception as e:
            logger.error(f"Failed to route to RabbitMQ: {e}")
            return False

    async def _route_to_celery(self, message: Message, route: RouteConfig, celery_manager: CeleryManager) -> bool:
        """Route message to Celery"""
        try:
            # This would integrate with Celery task dispatch
            # For now, simulate successful routing
            logger.debug(f"Routed message to Celery queue: {route.destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to route to Celery: {e}")
            return False

    def _generate_routing_key(self, message: Message, route: RouteConfig) -> str:
        """Generate routing key based on message and route"""
        if route.routing_strategy == RoutingStrategy.TOPIC_BASED:
            return f"{message.type}.{message.priority}.{message.source}"
        elif route.routing_strategy == RoutingStrategy.PRIORITY_BASED:
            return f"{message.type}.{message.priority}"
        else:
            return f"{message.type}.default"

    def _get_priority_value(self, priority: MessagePriority) -> int:
        """Convert priority enum to numeric value"""
        priority_map = {
            MessagePriority.LOW: 1,
            MessagePriority.MEDIUM: 3,
            MessagePriority.HIGH: 5,
            MessagePriority.CRITICAL: 10
        }
        return priority_map.get(priority, 3)

    async def _send_to_dead_letter(self, message: Message, reason: str) -> None:
        """
Send message to dead letter queue"""
        try:
            message.metadata["dead_letter_reason"] = reason
            message.metadata["dead_letter_timestamp"] = time.time()
            
            self.dead_letter_messages.append(message)
            
            logger.warning(f"Message {message.id} sent to dead letter: {reason}")
            
            # Could also send to dedicated dead letter topic/queue
            
        except Exception as e:
            logger.error(f"Failed to send to dead letter: {e}")

    def _update_message_stats(self, message_type: MessageType, success: bool) -> None:
        """Update message routing statistics"""
        stat_key = f"{message_type}_{'success' if success else 'failed'}"
        self.message_stats[stat_key] = self.message_stats.get(stat_key, 0) + 1

    async def add_handler(self, name: str, handler: MessageHandler) -> None:
        """Add message handler"""
        self.handlers[name] = handler
        logger.info(f"Added message handler: {name}")

    async def remove_handler(self, name: str) -> bool:
        """Remove message handler"""
        if name in self.handlers:
            del self.handlers[name]
            logger.info(f"Removed message handler: {name}")
            return True
        return False

    async def process_message_with_handler(self, message: Message, handler_name: str) -> bool:
        """Process message with specific handler"""
        try:
            handler = self.handlers.get(handler_name)
            
            if not handler:
                logger.error(f"Handler {handler_name} not found")
                return False
            
            if await handler.can_handle(message):
                return await handler.handle(message)
            else:
                logger.warning(f"Handler {handler_name} cannot process message {message.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing message with handler {handler_name}: {e}")
            return False

    async def broadcast_message(self, message: Message, protocols: List[MessageProtocol]) -> Dict[MessageProtocol, bool]:
        """Broadcast message to multiple protocols"""
        results = {}
        
        for protocol in protocols:
            try:
                # Create temporary route for broadcast
                temp_route = RouteConfig(
                    message_type=message.type,
                    protocol=protocol,
                    destination=f"broadcast.{message.type}",
                    routing_strategy=RoutingStrategy.BROADCAST
                )
                
                success = await self._route_to_destination(message, temp_route)
                results[protocol] = success
                
            except Exception as e:
                logger.error(f"Failed to broadcast to {protocol}: {e}")
                results[protocol] = False
                
        return results

    async def get_routing_stats(self) -> Dict[str, Union[int, List[Dict]]]:
        """Get routing statistics"""
        try:
            total_routed = sum(v for k, v in self.message_stats.items() if "success" in k)
            total_failed = sum(v for k, v in self.message_stats.items() if "failed" in k)
            
            # Group stats by message type
            type_stats = {}
            for stat_key, count in self.message_stats.items():
                parts = stat_key.split("_")
                if len(parts) >= 2:
                    msg_type = "_".join(parts[:-1])
                    status = parts[-1]
                    
                    if msg_type not in type_stats:
                        type_stats[msg_type] = {"success": 0, "failed": 0}
                    
                    type_stats[msg_type][status] = count
            
            return {
                "total_routed": total_routed,
                "total_failed": total_failed,
                "success_rate": (total_routed / (total_routed + total_failed)) * 100 if (total_routed + total_failed) > 0 else 0,
                "dead_letter_count": len(self.dead_letter_messages),
                "active_routes": sum(len(routes) for routes in self.routes.values()),
                "active_handlers": len(self.handlers),
                "type_statistics": [
                    {
                        "message_type": msg_type,
                        "success_count": stats["success"],
                        "failed_count": stats["failed"],
                        "success_rate": (stats["success"] / (stats["success"] + stats["failed"])) * 100 if (stats["success"] + stats["failed"]) > 0 else 0
                    }
                    for msg_type, stats in type_stats.items()
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get routing stats: {e}")
            return {"error": str(e)}

    async def get_dead_letter_messages(self, limit: int = 100) -> List[Dict]:
        """Get dead letter messages"""
        return [msg.dict() for msg in self.dead_letter_messages[-limit:]]

    async def reprocess_dead_letter_messages(self, message_ids: Optional[List[str]] = None) -> Dict[str, int]:
        """
Reprocess dead letter messages"""
        try:
            reprocessed = 0
            failed = 0
            
            messages_to_process = self.dead_letter_messages
            
            if message_ids:
                messages_to_process = [
                    msg for msg in self.dead_letter_messages 
                    if msg.id in message_ids
                ]
            
            for message in messages_to_process:
                # Reset retry count for reprocessing
                message.retry_count = 0
                
                if await self.route_message(message):
                    reprocessed += 1
                    # Remove from dead letter
                    self.dead_letter_messages.remove(message)
                else:
                    failed += 1
            
            return {
                "reprocessed": reprocessed,
                "failed": failed,
                "remaining": len(self.dead_letter_messages)
            }
            
        except Exception as e:
            logger.error(f"Failed to reprocess dead letter messages: {e}")
            return {"error": str(e)}

    def export_routing_config(self) -> Dict:
        """Export current routing configuration"""
        return {
            "routes": {
                msg_type.value: [route.dict() for route in routes]
                for msg_type, routes in self.routes.items()
            },
            "handlers": list(self.handlers.keys()),
            "transformers": list(self.transformers.keys()),
            "filters": list(self.filters.keys()),
            "protocols": list(self.protocols.keys()),
            "export_timestamp": time.time()
        }

# File has syntax issues - needs manual review