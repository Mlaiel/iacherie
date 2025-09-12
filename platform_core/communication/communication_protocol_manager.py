"""
Communication Protocol Manager - Platform Core Enterprise Architecture
Protocol abstraction and switching for Ainflue AI Creator Platform

© 2025 Fahed Mlaiel. All rights reserved.
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import aiohttp
import websockets
from abc import ABC, abstractmethod

# Platform Core Imports
from ..utils.base_classes import EnterpriseComponent
from ..utils.exceptions import ProtocolError, ValidationError
from ..utils.metrics import MetricsCollector
from ..security.auth_manager import AuthenticationManager

logger = logging.getLogger(__name__)

class ProtocolType(Enum):
    """Communication protocol types."""
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    WEBSOCKET_SECURE = "websocket_secure"
    GRPC = "grpc"
    TCP = "tcp"
    UDP = "udp"
    MQTT = "mqtt"
    AMQP = "amqp"
    GRAPHQL = "graphql"

class CompressionType(Enum):
    """Message compression types."""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "brotli"
    LZ4 = "lz4"

class SerializationType(Enum):
    """Message serialization types."""
    JSON = "json"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"
    AVRO = "avro"
    XML = "xml"
    YAML = "yaml"

@dataclass
class ProtocolConfig:
    """Protocol configuration."""
    name: str
    protocol_type: ProtocolType
    endpoint: str
    port: int
    compression: CompressionType = CompressionType.NONE
    serialization: SerializationType = SerializationType.JSON
    timeout: int = 30
    max_connections: int = 100
    keepalive: bool = True
    ssl_enabled: bool = False
    authentication_required: bool = True
    rate_limit: int = 1000  # requests per minute
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MessageFrame:
    """Protocol-agnostic message frame."""
    id: str
    protocol: ProtocolType
    headers: Dict[str, str]
    payload: Any
    timestamp: datetime = field(default_factory=datetime.now)
    compression: CompressionType = CompressionType.NONE
    serialization: SerializationType = SerializationType.JSON
    priority: int = 1
    correlation_id: Optional[str] = None

@dataclass
class ProtocolStats:
    """Protocol usage statistics."""
    protocol_name: str
    messages_sent: int = 0
    messages_received: int = 0
    bytes_transferred: int = 0
    errors: int = 0
    average_latency: float = 0.0
    connections_active: int = 0
    last_activity: datetime = field(default_factory=datetime.now)

class ProtocolAdapter(ABC):
    """Abstract protocol adapter interface."""
    
    @abstractmethod
    async def initialize(self, config: ProtocolConfig) -> bool:
        """Initialize the protocol adapter."""
        pass
    
    @abstractmethod
    async def send_message(self, message: MessageFrame) -> bool:
        """Send a message using this protocol."""
        pass
    
    @abstractmethod
    async def receive_message(self) -> Optional[MessageFrame]:
        """Receive a message using this protocol."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the protocol connection."""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get protocol adapter status."""
        pass

class HTTPProtocolAdapter(ProtocolAdapter):
    """HTTP/HTTPS protocol adapter."""
    
    def __init__(self):
        self.config: Optional[ProtocolConfig] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self, config: ProtocolConfig) -> bool:
        """Initialize HTTP adapter."""
        try:
            self.config = config
            
            # Create session with appropriate settings
            timeout = aiohttp.ClientTimeout(total=config.timeout)
            connector = aiohttp.TCPConnector(
                limit=config.max_connections,
                keepalive_timeout=30 if config.keepalive else 0
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
            
            logger.info(f"HTTP adapter initialized for {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize HTTP adapter: {str(e)}")
            return False
    
    async def send_message(self, message: MessageFrame) -> bool:
        """Send HTTP message."""
        try:
            if not self.session or not self.config:
                return False
            
            # Prepare URL
            url = f"{self.config.endpoint}:{self.config.port}"
            if self.config.protocol_type == ProtocolType.HTTPS:
                url = url.replace("http://", "https://")
            
            # Prepare headers
            headers = message.headers.copy()
            headers["Content-Type"] = "application/json"
            
            # Serialize payload
            payload_data = await self._serialize_payload(message.payload, message.serialization)
            
            # Compress if needed
            if message.compression != CompressionType.NONE:
                payload_data = await self._compress_data(payload_data, message.compression)
                headers["Content-Encoding"] = message.compression.value
            
            # Send request
            async with self.session.post(url, data=payload_data, headers=headers) as response:
                return response.status < 400
                
        except Exception as e:
            logger.error(f"HTTP send failed: {str(e)}")
            return False
    
    async def receive_message(self) -> Optional[MessageFrame]:
        """HTTP doesn't receive messages in traditional sense."""
        # HTTP is typically request-response, so this would be used for webhooks
        return None
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get HTTP adapter status."""
        return {
            "protocol": "HTTP",
            "initialized": self.session is not None,
            "endpoint": self.config.endpoint if self.config else None,
            "max_connections": self.config.max_connections if self.config else 0
        }
    
    async def _serialize_payload(self, payload: Any, serialization: SerializationType) -> bytes:
        """Serialize payload based on type."""
        if serialization == SerializationType.JSON:
            return json.dumps(payload).encode('utf-8')
        else:
            # Default to JSON for now
            return json.dumps(payload).encode('utf-8')
    
    async def _compress_data(self, data: bytes, compression: CompressionType) -> bytes:
        """Compress data based on compression type."""
        if compression == CompressionType.GZIP:
            import gzip
            return gzip.compress(data)
        else:
            return data

class WebSocketProtocolAdapter(ProtocolAdapter):
    """WebSocket protocol adapter."""
    
    def __init__(self):
        self.config: Optional[ProtocolConfig] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        
    async def initialize(self, config: ProtocolConfig) -> bool:
        """Initialize WebSocket adapter."""
        try:
            self.config = config
            
            # Create WebSocket URL
            protocol = "wss" if config.ssl_enabled else "ws"
            url = f"{protocol}://{config.endpoint}:{config.port}"
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(url)
            self.connected = True
            
            logger.info(f"WebSocket adapter initialized for {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebSocket adapter: {str(e)}")
            return False
    
    async def send_message(self, message: MessageFrame) -> bool:
        """Send WebSocket message."""
        try:
            if not self.websocket or not self.connected:
                return False
            
            # Prepare message data
            message_data = {
                "id": message.id,
                "headers": message.headers,
                "payload": message.payload,
                "timestamp": message.timestamp.isoformat(),
                "correlation_id": message.correlation_id
            }
            
            # Serialize
            serialized_data = json.dumps(message_data)
            
            # Send via WebSocket
            await self.websocket.send(serialized_data)
            return True
            
        except Exception as e:
            logger.error(f"WebSocket send failed: {str(e)}")
            self.connected = False
            return False
    
    async def receive_message(self) -> Optional[MessageFrame]:
        """Receive WebSocket message."""
        try:
            if not self.websocket or not self.connected:
                return None
            
            # Receive message
            message_data = await self.websocket.recv()
            
            # Parse message
            parsed_data = json.loads(message_data)
            
            # Create MessageFrame
            message = MessageFrame(
                id=parsed_data.get("id", ""),
                protocol=ProtocolType.WEBSOCKET,
                headers=parsed_data.get("headers", {}),
                payload=parsed_data.get("payload", {}),
                correlation_id=parsed_data.get("correlation_id")
            )
            
            return message
            
        except Exception as e:
            logger.error(f"WebSocket receive failed: {str(e)}")
            self.connected = False
            return None
    
    async def close(self) -> None:
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.connected = False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get WebSocket adapter status."""
        return {
            "protocol": "WebSocket",
            "connected": self.connected,
            "endpoint": self.config.endpoint if self.config else None,
            "ssl_enabled": self.config.ssl_enabled if self.config else False
        }

class GRPCProtocolAdapter(ProtocolAdapter):
    """gRPC protocol adapter."""
    
    def __init__(self):
        self.config: Optional[ProtocolConfig] = None
        self.channel = None
        
    async def initialize(self, config: ProtocolConfig) -> bool:
        """Initialize gRPC adapter."""
        try:
            self.config = config
            
            # For simulation, just mark as initialized
            logger.info(f"gRPC adapter initialized for {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize gRPC adapter: {str(e)}")
            return False
    
    async def send_message(self, message: MessageFrame) -> bool:
        """Send gRPC message."""
        try:
            # Simulate gRPC call
            await asyncio.sleep(0.01)
            logger.debug(f"gRPC message sent: {message.id}")
            return True
            
        except Exception as e:
            logger.error(f"gRPC send failed: {str(e)}")
            return False
    
    async def receive_message(self) -> Optional[MessageFrame]:
        """Receive gRPC message."""
        # gRPC is typically request-response or streaming
        return None
    
    async def close(self) -> None:
        """Close gRPC channel."""
        if self.channel:
            self.channel = None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get gRPC adapter status."""
        return {
            "protocol": "gRPC",
            "initialized": self.config is not None,
            "endpoint": self.config.endpoint if self.config else None
        }

class CommunicationProtocolManager(EnterpriseComponent):
    """
    Enterprise communication protocol management and coordination system.
    
    Features:
    - Protocol abstraction and switching
    - gRPC, HTTP, WebSocket coordination
    - Protocol-specific optimizations
    - Cross-protocol communication
    - Dynamic protocol selection
    - Message format transformation
    - Compression and encryption
    - Performance monitoring
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.protocol_adapters: Dict[str, ProtocolAdapter] = {}
        self.protocol_configs: Dict[str, ProtocolConfig] = {}
        self.protocol_stats: Dict[str, ProtocolStats] = {}
        self.active_connections: Dict[str, List[str]] = {}
        self.message_routes: Dict[str, List[str]] = {}  # destination -> protocols
        self.protocol_preferences: Dict[str, ProtocolType] = {}
        self.metrics_collector = MetricsCollector("communication_protocol_manager")
        self.auth_manager = AuthenticationManager()
        
        # Configuration
        self.auto_failover = config.get("auto_failover", True)
        self.health_check_interval = config.get("health_check_interval", 60)
        self.default_protocol = ProtocolType.HTTP
        self.max_retry_attempts = config.get("max_retry_attempts", 3)
        
        # Protocol selection weights
        self.protocol_weights = {
            ProtocolType.GRPC: 1.0,
            ProtocolType.WEBSOCKET: 0.9,
            ProtocolType.HTTPS: 0.8,
            ProtocolType.HTTP: 0.7
        }
        
        logger.info("CommunicationProtocolManager initialized successfully")

    async def register_protocol(
        self,
        config: ProtocolConfig,
        user_id: str = None
    ) -> str:
        """Register a communication protocol."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_protocol_management(user_id):
                raise ValidationError(f"User {user_id} not authorized for protocol management")
            
            # Validate configuration
            await self._validate_protocol_config(config)
            
            # Create appropriate adapter
            adapter = await self._create_protocol_adapter(config.protocol_type)
            
            # Initialize adapter
            if not await adapter.initialize(config):
                raise ProtocolError(f"Failed to initialize protocol adapter for {config.name}")
            
            # Store protocol
            self.protocol_adapters[config.name] = adapter
            self.protocol_configs[config.name] = config
            
            # Initialize stats
            self.protocol_stats[config.name] = ProtocolStats(protocol_name=config.name)
            
            # Start health monitoring
            asyncio.create_task(self._monitor_protocol_health(config.name))
            
            self.metrics_collector.increment("protocols_registered")
            logger.info(f"Protocol registered: {config.name} ({config.protocol_type.value})")
            
            return config.name
            
        except Exception as e:
            logger.error(f"Failed to register protocol: {str(e)}")
            raise ProtocolError(f"Protocol registration failed: {str(e)}")

    async def send_message(
        self,
        destination: str,
        message: MessageFrame,
        protocol_preference: ProtocolType = None,
        user_id: str = None
    ) -> bool:
        """Send a message using optimal protocol."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_message_send(user_id, destination):
                raise ValidationError(f"User {user_id} not authorized to send messages to {destination}")
            
            # Select optimal protocol
            selected_protocol = await self._select_optimal_protocol(
                destination, protocol_preference, message
            )
            
            if not selected_protocol:
                raise ProtocolError("No suitable protocol available for message")
            
            # Get adapter
            adapter = self.protocol_adapters[selected_protocol]
            
            # Set protocol in message
            message.protocol = self.protocol_configs[selected_protocol].protocol_type
            
            # Send message with retries
            success = await self._send_with_retries(selected_protocol, message)
            
            # Update stats
            if selected_protocol in self.protocol_stats:
                stats = self.protocol_stats[selected_protocol]
                if success:
                    stats.messages_sent += 1
                else:
                    stats.errors += 1
                stats.last_activity = datetime.now()
            
            if success:
                self.metrics_collector.increment("messages_sent")
                logger.debug(f"Message sent via {selected_protocol} to {destination}")
            else:
                self.metrics_collector.increment("messages_failed")
                logger.error(f"Failed to send message via {selected_protocol} to {destination}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            self.metrics_collector.increment("messages_failed")
            raise ProtocolError(f"Message sending failed: {str(e)}")

    async def receive_message(
        self,
        protocol_name: str,
        timeout: int = None
    ) -> Optional[MessageFrame]:
        """Receive a message from a specific protocol."""
        try:
            if protocol_name not in self.protocol_adapters:
                raise ProtocolError(f"Protocol {protocol_name} not found")
            
            adapter = self.protocol_adapters[protocol_name]
            
            # Receive message with timeout
            if timeout:
                try:
                    message = await asyncio.wait_for(
                        adapter.receive_message(),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    return None
            else:
                message = await adapter.receive_message()
            
            # Update stats
            if message and protocol_name in self.protocol_stats:
                stats = self.protocol_stats[protocol_name]
                stats.messages_received += 1
                stats.last_activity = datetime.now()
            
            if message:
                self.metrics_collector.increment("messages_received")
                logger.debug(f"Message received via {protocol_name}")
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to receive message: {str(e)}")
            raise ProtocolError(f"Message receiving failed: {str(e)}")

    async def broadcast_message(
        self,
        message: MessageFrame,
        protocols: List[str] = None,
        user_id: str = None
    ) -> Dict[str, bool]:
        """Broadcast a message across multiple protocols."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_message_broadcast(user_id):
                raise ValidationError(f"User {user_id} not authorized for message broadcasting")
            
            # Use all protocols if none specified
            if not protocols:
                protocols = list(self.protocol_adapters.keys())
            
            # Send to each protocol
            results = {}
            tasks = []
            
            for protocol_name in protocols:
                if protocol_name in self.protocol_adapters:
                    task = self._send_via_protocol(protocol_name, message)
                    tasks.append((protocol_name, task))
            
            # Wait for all sends to complete
            for protocol_name, task in tasks:
                try:
                    result = await task
                    results[protocol_name] = result
                except Exception as e:
                    logger.error(f"Broadcast failed for protocol {protocol_name}: {str(e)}")
                    results[protocol_name] = False
            
            successful_sends = sum(1 for success in results.values() if success)
            
            self.metrics_collector.record("broadcast_success_rate", 
                                        successful_sends / len(results) if results else 0)
            
            logger.info(f"Broadcast completed: {successful_sends}/{len(results)} successful")
            return results
            
        except Exception as e:
            logger.error(f"Failed to broadcast message: {str(e)}")
            raise ProtocolError(f"Message broadcasting failed: {str(e)}")

    async def set_protocol_preference(
        self,
        destination: str,
        protocol_type: ProtocolType,
        user_id: str = None
    ) -> None:
        """Set protocol preference for a destination."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_protocol_preference(user_id):
                raise ValidationError(f"User {user_id} not authorized to set protocol preferences")
            
            self.protocol_preferences[destination] = protocol_type
            logger.info(f"Protocol preference set for {destination}: {protocol_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to set protocol preference: {str(e)}")
            raise ProtocolError(f"Protocol preference setting failed: {str(e)}")

    async def add_message_route(
        self,
        destination: str,
        protocols: List[str],
        user_id: str = None
    ) -> None:
        """Add a message route for a destination."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_route_management(user_id):
                raise ValidationError(f"User {user_id} not authorized for route management")
            
            # Validate protocols exist
            for protocol_name in protocols:
                if protocol_name not in self.protocol_adapters:
                    raise ProtocolError(f"Protocol {protocol_name} not found")
            
            self.message_routes[destination] = protocols
            logger.info(f"Message route added for {destination}: {protocols}")
            
        except Exception as e:
            logger.error(f"Failed to add message route: {str(e)}")
            raise ProtocolError(f"Message route addition failed: {str(e)}")

    async def transform_message_protocol(
        self,
        message: MessageFrame,
        target_protocol: ProtocolType
    ) -> MessageFrame:
        """Transform message for different protocol."""
        try:
            # Create new message frame for target protocol
            transformed_message = MessageFrame(
                id=message.id,
                protocol=target_protocol,
                headers=message.headers.copy(),
                payload=message.payload,
                timestamp=message.timestamp,
                correlation_id=message.correlation_id
            )
            
            # Apply protocol-specific transformations
            await self._apply_protocol_transformations(transformed_message, target_protocol)
            
            logger.debug(f"Message transformed from {message.protocol.value} to {target_protocol.value}")
            return transformed_message
            
        except Exception as e:
            logger.error(f"Failed to transform message protocol: {str(e)}")
            raise ProtocolError(f"Message protocol transformation failed: {str(e)}")

    async def get_protocol_status(self, protocol_name: str) -> Dict[str, Any]:
        """Get status of a specific protocol."""
        try:
            if protocol_name not in self.protocol_adapters:
                raise ProtocolError(f"Protocol {protocol_name} not found")
            
            adapter = self.protocol_adapters[protocol_name]
            config = self.protocol_configs[protocol_name]
            stats = self.protocol_stats.get(protocol_name, ProtocolStats(protocol_name=protocol_name))
            
            adapter_status = await adapter.get_status()
            
            return {
                "name": protocol_name,
                "type": config.protocol_type.value,
                "endpoint": config.endpoint,
                "port": config.port,
                "status": adapter_status,
                "stats": {
                    "messages_sent": stats.messages_sent,
                    "messages_received": stats.messages_received,
                    "bytes_transferred": stats.bytes_transferred,
                    "errors": stats.errors,
                    "average_latency": stats.average_latency,
                    "connections_active": stats.connections_active,
                    "last_activity": stats.last_activity.isoformat()
                },
                "health": await self._check_protocol_health(protocol_name)
            }
            
        except Exception as e:
            logger.error(f"Failed to get protocol status: {str(e)}")
            raise ProtocolError(f"Protocol status retrieval failed: {str(e)}")

    async def get_manager_status(self) -> Dict[str, Any]:
        """Get manager status and metrics."""
        try:
            protocol_health = {}
            for protocol_name in self.protocol_adapters:
                protocol_health[protocol_name] = await self._check_protocol_health(protocol_name)
            
            total_messages_sent = sum(stats.messages_sent for stats in self.protocol_stats.values())
            total_messages_received = sum(stats.messages_received for stats in self.protocol_stats.values())
            total_errors = sum(stats.errors for stats in self.protocol_stats.values())
            
            return {
                "registered_protocols": len(self.protocol_adapters),
                "active_routes": len(self.message_routes),
                "protocol_preferences": len(self.protocol_preferences),
                "protocol_health": protocol_health,
                "total_messages_sent": total_messages_sent,
                "total_messages_received": total_messages_received,
                "total_errors": total_errors,
                "error_rate": total_errors / (total_messages_sent + total_messages_received) 
                             if (total_messages_sent + total_messages_received) > 0 else 0,
                "metrics": await self.metrics_collector.get_summary()
            }
            
        except Exception as e:
            logger.error(f"Failed to get manager status: {str(e)}")
            raise ProtocolError(f"Manager status retrieval failed: {str(e)}")

    # Private Methods
    
    async def _validate_protocol_config(self, config: ProtocolConfig) -> None:
        """Validate protocol configuration."""
        if not config.name:
            raise ValidationError("Protocol name is required")
        
        if not config.endpoint:
            raise ValidationError("Protocol endpoint is required")
        
        if config.port <= 0 or config.port > 65535:
            raise ValidationError("Protocol port must be between 1 and 65535")
        
        if config.timeout <= 0:
            raise ValidationError("Protocol timeout must be positive")

    async def _create_protocol_adapter(self, protocol_type: ProtocolType) -> ProtocolAdapter:
        """Create appropriate protocol adapter."""
        if protocol_type in [ProtocolType.HTTP, ProtocolType.HTTPS]:
            return HTTPProtocolAdapter()
        elif protocol_type in [ProtocolType.WEBSOCKET, ProtocolType.WEBSOCKET_SECURE]:
            return WebSocketProtocolAdapter()
        elif protocol_type == ProtocolType.GRPC:
            return GRPCProtocolAdapter()
        else:
            # Default to HTTP
            return HTTPProtocolAdapter()

    async def _select_optimal_protocol(
        self,
        destination: str,
        preference: ProtocolType = None,
        message: MessageFrame = None
    ) -> Optional[str]:
        """Select optimal protocol for destination."""
        available_protocols = []
        
        # Check if destination has specific routes
        if destination in self.message_routes:
            available_protocols = self.message_routes[destination]
        else:
            # Use all available protocols
            available_protocols = list(self.protocol_adapters.keys())
        
        # Filter healthy protocols
        healthy_protocols = []
        for protocol_name in available_protocols:
            if await self._check_protocol_health(protocol_name):
                healthy_protocols.append(protocol_name)
        
        if not healthy_protocols:
            return None
        
        # Apply preference if specified
        if preference:
            for protocol_name in healthy_protocols:
                config = self.protocol_configs[protocol_name]
                if config.protocol_type == preference:
                    return protocol_name
        
        # Check destination preference
        if destination in self.protocol_preferences:
            preferred_type = self.protocol_preferences[destination]
            for protocol_name in healthy_protocols:
                config = self.protocol_configs[protocol_name]
                if config.protocol_type == preferred_type:
                    return protocol_name
        
        # Select based on protocol weights and performance
        best_protocol = None
        best_score = 0
        
        for protocol_name in healthy_protocols:
            config = self.protocol_configs[protocol_name]
            stats = self.protocol_stats.get(protocol_name, ProtocolStats(protocol_name=protocol_name))
            
            # Calculate score based on weights and performance
            base_weight = self.protocol_weights.get(config.protocol_type, 0.5)
            error_rate = stats.errors / max(stats.messages_sent, 1)
            performance_factor = max(0.1, 1.0 - error_rate)
            
            score = base_weight * performance_factor
            
            if score > best_score:
                best_score = score
                best_protocol = protocol_name
        
        return best_protocol

    async def _send_with_retries(
        self,
        protocol_name: str,
        message: MessageFrame
    ) -> bool:
        """Send message with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retry_attempts):
            try:
                success = await self._send_via_protocol(protocol_name, message)
                if success:
                    return True
                
                # Wait before retry
                if attempt < self.max_retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                last_exception = e
                logger.warning(f"Send attempt {attempt + 1} failed for protocol {protocol_name}: {str(e)}")
                
                if attempt < self.max_retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)
        
        if last_exception:
            logger.error(f"All send attempts failed for protocol {protocol_name}: {str(last_exception)}")
        
        return False

    async def _send_via_protocol(
        self,
        protocol_name: str,
        message: MessageFrame
    ) -> bool:
        """Send message via specific protocol."""
        if protocol_name not in self.protocol_adapters:
            return False
        
        adapter = self.protocol_adapters[protocol_name]
        return await adapter.send_message(message)

    async def _apply_protocol_transformations(
        self,
        message: MessageFrame,
        target_protocol: ProtocolType
    ) -> None:
        """Apply protocol-specific transformations."""
        # Adjust headers based on protocol
        if target_protocol in [ProtocolType.HTTP, ProtocolType.HTTPS]:
            message.headers["User-Agent"] = "Ainflue-Platform/1.0"
            message.headers["Accept"] = "application/json"
        
        elif target_protocol == ProtocolType.GRPC:
            # gRPC specific headers
            message.headers["grpc-encoding"] = "gzip"
            message.headers["grpc-accept-encoding"] = "gzip"
        
        elif target_protocol in [ProtocolType.WEBSOCKET, ProtocolType.WEBSOCKET_SECURE]:
            # WebSocket specific headers
            message.headers["Sec-WebSocket-Version"] = "13"

    async def _monitor_protocol_health(self, protocol_name: str) -> None:
        """Monitor protocol health continuously."""
        while protocol_name in self.protocol_adapters:
            try:
                health_status = await self._check_protocol_health(protocol_name)
                
                if not health_status and self.auto_failover:
                    logger.warning(f"Protocol {protocol_name} health check failed, considering failover")
                    # Could implement failover logic here
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error for protocol {protocol_name}: {str(e)}")
                await asyncio.sleep(self.health_check_interval)

    async def _check_protocol_health(self, protocol_name: str) -> bool:
        """Check if a protocol is healthy."""
        try:
            if protocol_name not in self.protocol_adapters:
                return False
            
            adapter = self.protocol_adapters[protocol_name]
            status = await adapter.get_status()
            
            # Simple health check - could be enhanced
            return status.get("initialized", False) or status.get("connected", False)
            
        except Exception as e:
            logger.error(f"Health check failed for protocol {protocol_name}: {str(e)}")
            return False

    async def get_health_status(self) -> Dict[str, Any]:
        """Get manager health status."""
        healthy_protocols = sum(1 for protocol_name in self.protocol_adapters 
                               if await self._check_protocol_health(protocol_name))
        
        return {
            "status": "healthy" if healthy_protocols > 0 else "unhealthy",
            "total_protocols": len(self.protocol_adapters),
            "healthy_protocols": healthy_protocols,
            "active_routes": len(self.message_routes),
            "protocol_preferences": len(self.protocol_preferences),
            "metrics": await self.metrics_collector.get_summary()
        }

    async def cleanup(self) -> None:
        """Cleanup manager resources."""
        try:
            # Close all protocol adapters
            for protocol_name, adapter in self.protocol_adapters.items():
                await adapter.close()
            
            logger.info("CommunicationProtocolManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")