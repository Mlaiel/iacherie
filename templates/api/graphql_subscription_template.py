"""
🔒 GRAPHQL SUBSCRIPTION TEMPLATE - REAL-TIME ENTERPRISE IMPLEMENTATION
======================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade GraphQL subscription template with:
- Real-time data streaming
- WebSocket connection management
- Event-driven notifications
- Creator economy live updates
- Security and authentication
- Performance optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, AsyncGenerator, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import asyncio
import json

import strawberry
from strawberry.types import Info
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL
import redis.asyncio as redis

from ..template_registry import TemplateInterface, TemplateMetadata, TemplateType, TemplateCategory, SecurityLevel

logger = logging.getLogger(__name__)


class SubscriptionEventType(Enum):
    """Types of subscription events."""
    CONTENT_UPLOADED = "content_uploaded"
    COLLABORATION_STARTED = "collaboration_started"
    MONETIZATION_UPDATE = "monetization_update"
    CREATOR_LIVE = "creator_live"
    ANALYTICS_UPDATE = "analytics_update"
    NOTIFICATION = "notification"
    MESSAGE = "message"
    STATUS_CHANGE = "status_change"


@dataclass
class SubscriptionConfig:
    """Configuration for GraphQL subscription."""
    name: str
    event_type: SubscriptionEventType
    description: str = ""
    
    # Security
    requires_auth: bool = True
    required_roles: List[str] = field(default_factory=list)
    creator_only: bool = False
    
    # Performance
    rate_limit: Optional[int] = None
    buffer_size: int = 100
    debounce_ms: int = 0
    
    # Filtering
    enable_filtering: bool = True
    filterable_fields: List[str] = field(default_factory=list)
    
    # Creator Economy
    creator_context: bool = False
    monetization_events: bool = False


class GraphQLSubscriptionConfig(BaseModel):
    """Configuration for GraphQL subscription generation."""
    
    subscription_name: str = Field(..., description="Name of the subscription")
    description: str = Field("", description="Subscription description")
    
    # WebSocket configuration
    websocket_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "protocol": "graphql-ws",
            "keep_alive_interval": 30,
            "connection_timeout": 60,
            "max_connections": 1000
        }
    )
    
    # Redis configuration
    redis_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "max_connections": 100,
            "subscription_pattern": "subscription:*"
        }
    )
    
    # Event configuration
    events: Dict[str, SubscriptionConfig] = Field(default_factory=dict)
    
    # Security configuration
    security_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "authentication_required": True,
            "connection_validation": True,
            "rate_limiting": True,
            "message_validation": True
        }
    )
    
    # Creator economy configuration
    creator_economy_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enable_creator_notifications": True,
            "content_upload_events": True,
            "collaboration_events": True,
            "monetization_events": True,
            "analytics_events": True
        }
    )


class GraphQLSubscriptionTemplate(TemplateInterface):
    """Enterprise GraphQL subscription template."""
    
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="graphql_subscription_template",
            template_type=TemplateType.GRAPHQL,
            category=TemplateCategory.ADVANCED,
            version="1.0.0",
            author="Fahed Mlaiel",
            description="Enterprise GraphQL subscription template with real-time events",
            security_level=SecurityLevel.ENTERPRISE,
            dependencies=["strawberry-graphql", "redis", "websockets", "pydantic"],
            tags=["graphql", "subscription", "realtime", "websocket"],
            compliance_standards=["SOC2", "GDPR"],
            enterprise_features=[
                "Real-time event streaming",
                "WebSocket management",
                "Redis pub/sub integration",
                "Creator economy events",
                "Security validation"
            ]
        )
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate GraphQL subscription based on configuration."""
        try:
            subscription_config = GraphQLSubscriptionConfig(**config)
            return self._generate_subscription_code(subscription_config)
        except Exception as e:
            logger.error(f"Failed to generate GraphQL subscription: {e}")
            raise
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate subscription configuration."""
        try:
            GraphQLSubscriptionConfig(**config)
            return True
        except Exception as e:
            logger.error(f"Invalid GraphQL subscription config: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration."""
        return GraphQLSubscriptionConfig.schema()
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example configurations."""
        return [
            {
                "subscription_name": "CreatorSubscriptions",
                "description": "Real-time subscriptions for creator economy events",
                "events": {
                    "content_uploaded": {
                        "name": "content_uploaded",
                        "event_type": "content_uploaded",
                        "description": "Subscribe to content upload events",
                        "requires_auth": True,
                        "creator_context": True,
                        "enable_filtering": True,
                        "filterable_fields": ["creator_id", "content_type"]
                    },
                    "collaboration_updates": {
                        "name": "collaboration_updates",
                        "event_type": "collaboration_started", 
                        "description": "Subscribe to collaboration events",
                        "requires_auth": True,
                        "creator_only": True,
                        "monetization_events": True
                    }
                }
            }
        ]
    
    def _generate_subscription_code(self, config: GraphQLSubscriptionConfig) -> str:
        """Generate the actual GraphQL subscription code."""
        
        # Generate imports
        imports = self._generate_imports(config)
        
        # Generate event types
        event_types = self._generate_event_types(config)
        
        # Generate Redis client setup
        redis_setup = self._generate_redis_setup(config)
        
        # Generate WebSocket manager
        websocket_manager = self._generate_websocket_manager(config)
        
        # Generate subscription resolvers
        subscriptions = self._generate_subscriptions(config)
        
        # Generate event publisher
        event_publisher = self._generate_event_publisher(config)
        
        # Generate configuration
        subscription_config = self._generate_subscription_config(config)
        
        code = f'''"""
{config.subscription_name} GraphQL Subscriptions
Generated by Ainflue GraphQL Subscription Template

{config.description}

🔒 PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

{imports}

{event_types}

{redis_setup}

{websocket_manager}

{subscriptions}

{event_publisher}

{subscription_config}

# Subscription factory
def create_subscription_manager() -> SubscriptionManager:
    """Create subscription manager with configuration."""
    manager = SubscriptionManager()
    
    # Apply security middleware
    manager = apply_security_middleware(manager)
    
    # Apply performance optimizations
    manager = apply_performance_optimizations(manager)
    
    # Apply monitoring
    manager = apply_monitoring(manager)
    
    return manager

# Export subscription manager
subscription_manager = create_subscription_manager()

if __name__ == "__main__":
    print(f"✅ {config.subscription_name} initialized successfully")
    print(f"📊 Subscription statistics:")
    print(f"   - Events: {len(config.events)}")
    print(f"   - Redis enabled: True")
    print(f"   - WebSocket protocol: {config.websocket_config['protocol']}")
    print(f"   - Max connections: {config.websocket_config['max_connections']}")
'''
        
        return code
    
    def _generate_imports(self, config: GraphQLSubscriptionConfig) -> str:
        """Generate import statements."""
        return '''from typing import Dict, List, Optional, Any, AsyncGenerator, Callable, Union
from datetime import datetime
import logging
import asyncio
import json
from contextlib import asynccontextmanager

import strawberry
from strawberry.types import Info
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL
from strawberry.subscriptions.protocols.graphql_ws.handlers import GraphQLWSHandler

import redis.asyncio as redis
import websockets
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Core imports
from core.auth import get_current_user, verify_permissions
from core.caching import cache_response
from core.rate_limiting import rate_limit
from monitoring.subscription_metrics import SubscriptionMetricsCollector
from utils.validation import validate_input
from utils.security import sanitize_input

logger = logging.getLogger(__name__)'''
    
    def _generate_event_types(self, config: GraphQLSubscriptionConfig) -> str:
        """Generate event type definitions."""
        event_types = ["# Event Types", ""]
        
        # Generate base event type
        event_types.extend([
            "@strawberry.type",
            "class SubscriptionEvent:",
            '    """Base subscription event."""',
            "    id: str",
            "    event_type: str",
            "    timestamp: datetime",
            "    creator_id: Optional[str] = None",
            "    data: Optional[str] = None",
            ""
        ])
        
        # Generate specific event types for each subscription
        for event_key, event_config in config.events.items():
            event_type_name = f"{event_key.title().replace('_', '')}Event"
            event_types.extend([
                f"@strawberry.type",
                f"class {event_type_name}(SubscriptionEvent):",
                f'    """{event_config.description}"""',
                f'    event_type: str = "{event_config.event_type.value}"',
                ""
            ])
        
        return "\n".join(event_types)
    
    def _generate_redis_setup(self, config: GraphQLSubscriptionConfig) -> str:
        """Generate Redis client setup."""
        redis_config = config.redis_config
        
        return f'''# Redis Setup

class RedisSubscriptionManager:
    """Redis-based subscription management."""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        self.config = {redis_config}
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.Redis(
                host=self.config['host'],
                port=self.config['port'],
                db=self.config['db'],
                max_connections=self.config['max_connections'],
                decode_responses=True
            )
            
            self.pubsub = self.redis_client.pubsub()
            await self.redis_client.ping()
            logger.info("Connected to Redis for subscriptions")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {{e}}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
    
    async def subscribe(self, channel: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe to Redis channel."""
        if not self.pubsub:
            await self.connect()
        
        await self.pubsub.subscribe(channel)
        
        try:
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message and message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        yield data
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in subscription message: {{message['data']}}")
                
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
        except asyncio.CancelledError:
            await self.pubsub.unsubscribe(channel)
            raise
    
    async def publish(self, channel: str, data: Dict[str, Any]):
        """Publish event to Redis channel."""
        if not self.redis_client:
            await self.connect()
        
        try:
            message = json.dumps(data, default=str)
            await self.redis_client.publish(channel, message)
            
        except Exception as e:
            logger.error(f"Failed to publish to channel {{channel}}: {{e}}")

# Global Redis manager
redis_manager = RedisSubscriptionManager()'''
    
    def _generate_websocket_manager(self, config: GraphQLSubscriptionConfig) -> str:
        """Generate WebSocket connection manager."""
        websocket_config = config.websocket_config
        
        return f'''# WebSocket Connection Manager

class WebSocketConnectionManager:
    """Manage WebSocket connections for subscriptions."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {{}}
        self.user_connections: Dict[str, List[str]] = {{}}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {{}}
        self.max_connections = {websocket_config['max_connections']}
        self.keep_alive_interval = {websocket_config['keep_alive_interval']}
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: Optional[str] = None):
        """Accept WebSocket connection."""
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008, reason="Max connections reached")
            return False
        
        await websocket.accept(subprotocol="{websocket_config['protocol']}")
        
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {{
            "user_id": user_id,
            "connected_at": datetime.now(),
            "subscriptions": set(),
            "last_activity": datetime.now()
        }}
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(connection_id)
        
        logger.info(f"WebSocket connection {{connection_id}} established for user {{user_id}}")
        return True
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection."""
        if connection_id in self.active_connections:
            metadata = self.connection_metadata.get(connection_id, {{}})
            user_id = metadata.get("user_id")
            
            # Remove from active connections
            del self.active_connections[connection_id]
            del self.connection_metadata[connection_id]
            
            # Remove from user connections
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id] = [
                    conn_id for conn_id in self.user_connections[user_id] 
                    if conn_id != connection_id
                ]
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            logger.info(f"WebSocket connection {{connection_id}} disconnected")
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
                self.connection_metadata[connection_id]["last_activity"] = datetime.now()
            except Exception as e:
                logger.error(f"Failed to send message to connection {{connection_id}}: {{e}}")
                self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections for a user."""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id].copy():
                await self.send_to_connection(connection_id, message)
    
    async def broadcast(self, message: Dict[str, Any], filter_func: Optional[Callable] = None):
        """Broadcast message to all connections."""
        for connection_id in list(self.active_connections.keys()):
            metadata = self.connection_metadata.get(connection_id)
            
            # Apply filter if provided
            if filter_func and not filter_func(metadata):
                continue
            
            await self.send_to_connection(connection_id, message)
    
    def add_subscription(self, connection_id: str, subscription_name: str):
        """Add subscription to connection."""
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["subscriptions"].add(subscription_name)
    
    def remove_subscription(self, connection_id: str, subscription_name: str):
        """Remove subscription from connection."""
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["subscriptions"].discard(subscription_name)

# Global connection manager
connection_manager = WebSocketConnectionManager()'''
    
    def _generate_subscriptions(self, config: GraphQLSubscriptionConfig) -> str:
        """Generate subscription resolvers."""
        subscription_name = config.subscription_name
        
        subscriptions_code = [
            f"# {subscription_name} Implementation",
            "",
            f"@strawberry.type",
            f"class {subscription_name}:",
            f'    """{config.description}"""',
            ""
        ]
        
        for event_key, event_config in config.events.items():
            subscription_method = self._generate_subscription_method(event_key, event_config)
            subscriptions_code.extend([f"    {line}" for line in subscription_method])
            subscriptions_code.append("")
        
        return "\n".join(subscriptions_code)
    
    def _generate_subscription_method(self, event_key: str, event_config: SubscriptionConfig) -> List[str]:
        """Generate individual subscription method."""
        method_name = event_config.name
        description = event_config.description
        
        lines = [
            f"@strawberry.subscription",
            f"async def {method_name}(",
            f"    self,",
            f"    info: Info,"
        ]
        
        # Add filtering parameters if enabled
        if event_config.enable_filtering and event_config.filterable_fields:
            for field in event_config.filterable_fields:
                lines.append(f"    {field}: Optional[str] = None,")
        
        lines[-1] = lines[-1].rstrip(',')  # Remove trailing comma
        lines.append(f") -> AsyncGenerator[SubscriptionEvent, None]:")
        lines.append(f'    """{description}"""')
        
        # Add authentication if required
        if event_config.requires_auth:
            lines.extend([
                "    # Validate authentication",
                "    user = info.context.get('user')",
                "    if not user:",
                "        raise GraphQLError('Authentication required')",
                ""
            ])
        
        # Add role-based authorization
        if event_config.required_roles:
            roles_str = str(event_config.required_roles)
            lines.extend([
                f"    # Validate authorization",
                f"    user_roles = getattr(user, 'roles', [])",
                f"    if not any(role in user_roles for role in {roles_str}):",
                f"        raise GraphQLError('Insufficient permissions')",
                ""
            ])
        
        # Add creator-only validation
        if event_config.creator_only:
            lines.extend([
                "    # Validate creator access",
                "    if not getattr(user, 'is_creator', False):",
                "        raise GraphQLError('Creator access required')",
                ""
            ])
        
        # Generate subscription logic
        lines.extend([
            f"    # Build channel name",
            f"    channel = 'subscription:{event_config.event_type.value}'",
            ""
        ])
        
        # Add filtering logic
        if event_config.enable_filtering and event_config.filterable_fields:
            lines.extend([
                "    # Apply filters",
                "    filters = {",
                f"        {', '.join([f''{field}': {field}' for field in event_config.filterable_fields])}",
                "    }",
                "    filters = {k: v for k, v in filters.items() if v is not None}",
                ""
            ])
        
        # Generate main subscription loop
        lines.extend([
            f"    # Subscribe to events",
            f"    try:",
            f"        async for event_data in redis_manager.subscribe(channel):",
            f"            # Validate event data",
            f"            if not self._validate_event(event_data, filters if 'filters' in locals() else {{}}):",
            f"                continue",
            f"            ",
            f"            # Apply rate limiting",
            f"            if not self._check_rate_limit(user.id if user else 'anonymous', '{method_name}'):",
            f"                continue",
            f"            ",
            f"            # Create event object",
            f"            event = SubscriptionEvent(",
            f"                id=event_data.get('id'),",
            f"                event_type=event_data.get('event_type'),",
            f"                timestamp=datetime.fromisoformat(event_data.get('timestamp')),",
            f"                creator_id=event_data.get('creator_id'),",
            f"                data=json.dumps(event_data.get('data')) if event_data.get('data') else None",
            f"            )",
            f"            ",
            f"            yield event",
            f"    except asyncio.CancelledError:",
            f"        logger.info(f'Subscription {method_name} cancelled for user {{user.id if user else \"anonymous\"}}')",
            f"        raise",
            f"    except Exception as e:",
            f"        logger.error(f'Error in subscription {method_name}: {{e}}')",
            f"        raise GraphQLError(f'Subscription error: {{str(e)}}')"
        ])
        
        return lines
    
    def _generate_event_publisher(self, config: GraphQLSubscriptionConfig) -> str:
        """Generate event publisher utility."""
        return '''# Event Publisher

class SubscriptionEventPublisher:
    """Publish events to subscriptions."""
    
    @staticmethod
    async def publish_content_uploaded(creator_id: str, content_data: Dict[str, Any]):
        """Publish content uploaded event."""
        event_data = {
            "id": f"content_{content_data.get('id')}_{int(datetime.now().timestamp())}",
            "event_type": "content_uploaded",
            "timestamp": datetime.now().isoformat(),
            "creator_id": creator_id,
            "data": content_data
        }
        
        await redis_manager.publish("subscription:content_uploaded", event_data)
    
    @staticmethod
    async def publish_collaboration_started(creator_id: str, collaboration_data: Dict[str, Any]):
        """Publish collaboration started event."""
        event_data = {
            "id": f"collab_{collaboration_data.get('id')}_{int(datetime.now().timestamp())}",
            "event_type": "collaboration_started", 
            "timestamp": datetime.now().isoformat(),
            "creator_id": creator_id,
            "data": collaboration_data
        }
        
        await redis_manager.publish("subscription:collaboration_started", event_data)
    
    @staticmethod
    async def publish_monetization_update(creator_id: str, monetization_data: Dict[str, Any]):
        """Publish monetization update event."""
        event_data = {
            "id": f"monetization_{creator_id}_{int(datetime.now().timestamp())}",
            "event_type": "monetization_update",
            "timestamp": datetime.now().isoformat(), 
            "creator_id": creator_id,
            "data": monetization_data
        }
        
        await redis_manager.publish("subscription:monetization_update", event_data)

# Global event publisher
event_publisher = SubscriptionEventPublisher()'''
    
    def _generate_subscription_config(self, config: GraphQLSubscriptionConfig) -> str:
        """Generate subscription configuration."""
        return f'''# Subscription Configuration

SUBSCRIPTION_CONFIG = {config.dict()}

def apply_security_middleware(manager: WebSocketConnectionManager) -> WebSocketConnectionManager:
    """Apply security middleware to subscription manager."""
    # Add connection validation
    # Add message sanitization
    # Add rate limiting
    return manager

def apply_performance_optimizations(manager: WebSocketConnectionManager) -> WebSocketConnectionManager:
    """Apply performance optimizations."""
    # Add connection pooling
    # Add message batching
    # Add compression
    return manager

def apply_monitoring(manager: WebSocketConnectionManager) -> WebSocketConnectionManager:
    """Apply monitoring to subscription manager."""
    # Add metrics collection
    # Add performance tracking
    # Add error tracking
    return manager

class SubscriptionManager:
    """Main subscription manager."""
    
    def __init__(self):
        self.connection_manager = connection_manager
        self.redis_manager = redis_manager
        self.event_publisher = event_publisher
    
    def _validate_event(self, event_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Validate event against filters."""
        for filter_key, filter_value in filters.items():
            if event_data.get(filter_key) != filter_value:
                return False
        return True
    
    def _check_rate_limit(self, user_id: str, subscription_name: str) -> bool:
        """Check rate limit for subscription."""
        return rate_limit(f"subscription:{{subscription_name}}:{{user_id}}", 100, 60)
    
    async def start(self):
        """Start subscription manager."""
        await self.redis_manager.connect()
        logger.info("Subscription manager started")
    
    async def stop(self):
        """Stop subscription manager."""
        await self.redis_manager.disconnect()
        logger.info("Subscription manager stopped")'''


# Register template
from .template_registry import register_template

register_template(
    GraphQLSubscriptionTemplate,
    GraphQLSubscriptionTemplate().metadata
)