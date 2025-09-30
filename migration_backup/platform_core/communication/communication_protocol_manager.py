#!/usr/bin/env python3
"""
Communication Protocol Manager - Enterprise Core Component
Protocol abstraction and switching system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive communication protocol management including:
- Protocol abstraction and switching
- gRPC, HTTP, WebSocket coordination
- Protocol-specific optimizations
- Cross-protocol communication
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolType(Enum):
    """Communication protocol types"""
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    WEBSOCKET_SECURE = "websocket_secure"
    GRPC = "grpc"
    TCP = "tcp"
    UDP = "udp"
    MQTT = "mqtt"
    AMQP = "amqp"
    CUSTOM = "custom"


class CompressionType(Enum):
    """Compression types"""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "brotli"
    LZ4 = "lz4"


class SerializationType(Enum):
    """Serialization types"""
    JSON = "json"
    PROTOBUF = "protobuf"
    AVRO = "avro"
    MSGPACK = "msgpack"
    XML = "xml"
    BINARY = "binary"


@dataclass
class ProtocolConfig:
    """Protocol configuration"""
    protocol_id: str
    protocol_type: ProtocolType
    name: str
    endpoint: str
    port: int
    compression: CompressionType = CompressionType.NONE
    serialization: SerializationType = SerializationType.JSON
    timeout: int = 30
    max_connections: int = 100
    keep_alive: bool = True
    ssl_enabled: bool = False
    custom_headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommunicationMessage:
    """Communication message structure"""
    message_id: str
    protocol_id: str
    source: str
    destination: str
    method: Optional[str] = None
    path: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommunicationResponse:
    """Communication response structure"""
    response_id: str
    message_id: str
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProtocolMetrics:
    """Protocol performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency: float = 0.0
    peak_latency: float = 0.0
    throughput: float = 0.0
    active_connections: int = 0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    last_activity: Optional[datetime] = None


class ProtocolAdapter(ABC):
    """Abstract base class for protocol adapters"""
    
    @abstractmethod
    async def initialize(self, config: ProtocolConfig) -> bool:
        """Initialize the protocol adapter"""
        pass
    
    @abstractmethod
    async def send_message(self, message: CommunicationMessage) -> CommunicationResponse:
        """Send message using this protocol"""
        pass
    
    @abstractmethod
    async def receive_message(self) -> Optional[CommunicationMessage]:
        """Receive message using this protocol"""
        pass
    
    @abstractmethod
    async def close(self) -> bool:
        """Close protocol connections"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> ProtocolMetrics:
        """Get protocol metrics"""
        pass


class HTTPAdapter(ProtocolAdapter):
    """HTTP/HTTPS protocol adapter"""
    
    def __init__(self):
        self.session = None
        self.metrics = ProtocolMetrics()
        self.config = None
    
    async def initialize(self, config: ProtocolConfig) -> bool:
        """Initialize HTTP adapter"""
        try:
            self.config = config
            # In a real implementation, would initialize aiohttp session
            logger.info(f"HTTP adapter initialized for {config.endpoint}:{config.port}")
            return True
        except Exception as e:
            logger.error(f"HTTP adapter initialization failed: {e}")
            return False
    
    async def send_message(self, message: CommunicationMessage) -> CommunicationResponse:
        """Send HTTP message"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate HTTP request
            await asyncio.sleep(0.1)  # Simulate network delay
            
            response = CommunicationResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                status_code=200,
                headers={"content-type": "application/json"},
                body={"status": "success", "data": "response"}
            )
            
            # Update metrics
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            response.latency_ms = latency
            self._update_metrics(True, latency)
            
            return response
            
        except Exception as e:
            self._update_metrics(False, 0)
            return CommunicationResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                status_code=500,
                error=str(e)
            )
    
    async def receive_message(self) -> Optional[CommunicationMessage]:
        """Receive HTTP message (for server mode)"""
        # HTTP is typically request-response, not good for receiving
        return None
    
    async def close(self) -> bool:
        """Close HTTP connections"""
        if self.session:
            # await self.session.close()
            pass
        return True
    
    def get_metrics(self) -> ProtocolMetrics:
        """Get HTTP metrics"""
        return self.metrics
    
    def _update_metrics(self, success: bool, latency: float):
        """Update adapter metrics"""
        self.metrics.total_requests += 1
        self.metrics.last_activity = datetime.utcnow()
        
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        if latency > 0:
            # Update average latency
            total_successful = self.metrics.successful_requests
            if total_successful > 1:
                self.metrics.average_latency = (
                    (self.metrics.average_latency * (total_successful - 1) + latency) / total_successful
                )
            else:
                self.metrics.average_latency = latency
            
            self.metrics.peak_latency = max(self.metrics.peak_latency, latency)


class WebSocketAdapter(ProtocolAdapter):
    """WebSocket protocol adapter"""
    
    def __init__(self):
        self.connection = None
        self.metrics = ProtocolMetrics()
        self.config = None
        self.message_queue = asyncio.Queue()
    
    async def initialize(self, config: ProtocolConfig) -> bool:
        """Initialize WebSocket adapter"""
        try:
            self.config = config
            # In a real implementation, would establish WebSocket connection
            logger.info(f"WebSocket adapter initialized for {config.endpoint}:{config.port}")
            return True
        except Exception as e:
            logger.error(f"WebSocket adapter initialization failed: {e}")
            return False
    
    async def send_message(self, message: CommunicationMessage) -> CommunicationResponse:
        """Send WebSocket message"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate WebSocket send
            await asyncio.sleep(0.05)  # Simulate send delay
            
            response = CommunicationResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                status_code=0,  # WebSocket doesn't use HTTP status codes
                body={"acknowledged": True}
            )
            
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            response.latency_ms = latency
            self._update_metrics(True, latency)
            
            return response
            
        except Exception as e:
            self._update_metrics(False, 0)
            return CommunicationResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                status_code=-1,
                error=str(e)
            )
    
    async def receive_message(self) -> Optional[CommunicationMessage]:
        """Receive WebSocket message"""
        try:
            # Simulate message reception
            if not self.message_queue.empty():
                return await self.message_queue.get()
            return None
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")
            return None
    
    async def close(self) -> bool:
        """Close WebSocket connection"""
        if self.connection:
            # await self.connection.close()
            pass
        return True
    
    def get_metrics(self) -> ProtocolMetrics:
        """Get WebSocket metrics"""
        return self.metrics
    
    def _update_metrics(self, success: bool, latency: float):
        """Update adapter metrics"""
        self.metrics.total_requests += 1
        self.metrics.last_activity = datetime.utcnow()
        
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        if latency > 0:
            total_successful = self.metrics.successful_requests
            if total_successful > 1:
                self.metrics.average_latency = (
                    (self.metrics.average_latency * (total_successful - 1) + latency) / total_successful
                )
            else:
                self.metrics.average_latency = latency
            
            self.metrics.peak_latency = max(self.metrics.peak_latency, latency)


class GRPCAdapter(ProtocolAdapter):
    """gRPC protocol adapter"""
    
    def __init__(self):
        self.channel = None
        self.metrics = ProtocolMetrics()
        self.config = None
    
    async def initialize(self, config: ProtocolConfig) -> bool:
        """Initialize gRPC adapter"""
        try:
            self.config = config
            # In a real implementation, would create gRPC channel
            logger.info(f"gRPC adapter initialized for {config.endpoint}:{config.port}")
            return True
        except Exception as e:
            logger.error(f"gRPC adapter initialization failed: {e}")
            return False
    
    async def send_message(self, message: CommunicationMessage) -> CommunicationResponse:
        """Send gRPC message"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate gRPC call
            await asyncio.sleep(0.08)  # Simulate RPC delay
            
            response = CommunicationResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                status_code=0,  # gRPC uses status codes differently
                body={"result": "success", "data": "grpc_response"}
            )
            
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            response.latency_ms = latency
            self._update_metrics(True, latency)
            
            return response
            
        except Exception as e:
            self._update_metrics(False, 0)
            return CommunicationResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                status_code=-1,
                error=str(e)
            )
    
    async def receive_message(self) -> Optional[CommunicationMessage]:
        """Receive gRPC message (for streaming)"""
        # Would implement gRPC streaming here
        return None
    
    async def close(self) -> bool:
        """Close gRPC channel"""
        if self.channel:
            # await self.channel.close()
            pass
        return True
    
    def get_metrics(self) -> ProtocolMetrics:
        """Get gRPC metrics"""
        return self.metrics
    
    def _update_metrics(self, success: bool, latency: float):
        """Update adapter metrics"""
        self.metrics.total_requests += 1
        self.metrics.last_activity = datetime.utcnow()
        
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        if latency > 0:
            total_successful = self.metrics.successful_requests
            if total_successful > 1:
                self.metrics.average_latency = (
                    (self.metrics.average_latency * (total_successful - 1) + latency) / total_successful
                )
            else:
                self.metrics.average_latency = latency
            
            self.metrics.peak_latency = max(self.metrics.peak_latency, latency)


class CommunicationProtocolManager:
    """
    Enterprise Communication Protocol Manager
    
    Manages multiple communication protocols with automatic switching,
    optimization, and cross-protocol coordination capabilities.
    """
    
    def __init__(self):
        self.protocols: Dict[str, ProtocolConfig] = {}
        self.adapters: Dict[str, ProtocolAdapter] = {}
        self.active_connections: Dict[str, List[str]] = {}
        self.protocol_routes: Dict[str, str] = {}  # service -> protocol mapping
        
        # Protocol type to adapter class mapping
        self.adapter_classes = {
            ProtocolType.HTTP: HTTPAdapter,
            ProtocolType.HTTPS: HTTPAdapter,
            ProtocolType.WEBSOCKET: WebSocketAdapter,
            ProtocolType.WEBSOCKET_SECURE: WebSocketAdapter,
            ProtocolType.GRPC: GRPCAdapter
        }
        
        # Message transformation functions
        self.transformers: Dict[str, Callable] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "protocol_registered": [],
            "protocol_connected": [],
            "protocol_disconnected": [],
            "message_sent": [],
            "message_received": [],
            "protocol_error": [],
            "failover_triggered": []
        }
        
        # Configuration
        self.auto_failover_enabled = True
        self.load_balancing_enabled = True
        self.compression_threshold = 1024  # bytes
        self.retry_attempts = 3
        self.circuit_breaker_threshold = 5  # failures before circuit opens
        
        # Circuit breaker state
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Communication Protocol Manager initialized")
    
    async def register_protocol(self, config: ProtocolConfig) -> bool:
        """Register a communication protocol"""
        try:
            # Validate configuration
            if not self._validate_config(config):
                logger.error(f"Invalid protocol configuration: {config.protocol_id}")
                return False
            
            self.protocols[config.protocol_id] = config
            
            # Create and initialize adapter
            adapter_class = self.adapter_classes.get(config.protocol_type)
            if adapter_class:
                adapter = adapter_class()
                success = await adapter.initialize(config)
                
                if success:
                    self.adapters[config.protocol_id] = adapter
                    await self._trigger_event("protocol_registered", config.protocol_id)
                    logger.info(f"Protocol registered: {config.protocol_id}")
                    return True
                else:
                    logger.error(f"Failed to initialize adapter for {config.protocol_id}")
                    return False
            else:
                logger.error(f"No adapter found for protocol type: {config.protocol_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to register protocol {config.protocol_id}: {e}")
            return False
    
    async def send_message(
        self,
        message: CommunicationMessage,
        preferred_protocol: Optional[str] = None
    ) -> CommunicationResponse:
        """Send message using appropriate protocol"""
        try:
            # Determine protocol to use
            protocol_id = preferred_protocol or self._select_protocol(message)
            
            if not protocol_id:
                return CommunicationResponse(
                    response_id=str(uuid.uuid4()),
                    message_id=message.message_id,
                    status_code=500,
                    error="No suitable protocol found"
                )
            
            # Check circuit breaker
            if not self._check_circuit_breaker(protocol_id):
                # Try failover
                if self.auto_failover_enabled:
                    protocol_id = await self._find_failover_protocol(protocol_id, message)
                    if not protocol_id:
                        return CommunicationResponse(
                            response_id=str(uuid.uuid4()),
                            message_id=message.message_id,
                            status_code=503,
                            error="Service unavailable - circuit breaker open"
                        )
            
            # Get adapter
            adapter = self.adapters.get(protocol_id)
            if not adapter:
                return CommunicationResponse(
                    response_id=str(uuid.uuid4()),
                    message_id=message.message_id,
                    status_code=500,
                    error=f"Adapter not found for protocol: {protocol_id}"
                )
            
            # Apply optimizations
            optimized_message = await self._optimize_message(message, protocol_id)
            
            # Send message with retry logic
            response = await self._send_with_retry(adapter, optimized_message, protocol_id)
            
            # Update circuit breaker
            self._update_circuit_breaker(protocol_id, response.status_code < 400)
            
            await self._trigger_event("message_sent", message.message_id)
            return response
            
        except Exception as e:
            logger.error(f"Failed to send message {message.message_id}: {e}")
            return CommunicationResponse(
                response_id=str(uuid.uuid4()),
                message_id=message.message_id,
                status_code=500,
                error=str(e)
            )
    
    async def broadcast_message(
        self,
        message: CommunicationMessage,
        protocols: Optional[List[str]] = None
    ) -> List[CommunicationResponse]:
        """Broadcast message to multiple protocols"""
        target_protocols = protocols or list(self.adapters.keys())
        responses = []
        
        # Send to all protocols concurrently
        tasks = []
        for protocol_id in target_protocols:
            task = asyncio.create_task(
                self.send_message(
                    CommunicationMessage(
                        message_id=str(uuid.uuid4()),
                        protocol_id=protocol_id,
                        source=message.source,
                        destination=message.destination,
                        method=message.method,
                        path=message.path,
                        headers=message.headers.copy(),
                        body=message.body,
                        metadata=message.metadata.copy()
                    ),
                    protocol_id
                )
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_responses = [
            r for r in responses 
            if isinstance(r, CommunicationResponse)
        ]
        
        return valid_responses
    
    async def receive_messages(
        self,
        protocol_id: str,
        timeout: Optional[float] = None
    ) -> List[CommunicationMessage]:
        """Receive messages from a protocol"""
        adapter = self.adapters.get(protocol_id)
        if not adapter:
            return []
        
        messages = []
        start_time = datetime.utcnow()
        
        while True:
            try:
                message = await adapter.receive_message()
                if message:
                    messages.append(message)
                    await self._trigger_event("message_received", message.message_id)
                else:
                    await asyncio.sleep(0.1)
                
                # Check timeout
                if timeout and (datetime.utcnow() - start_time).total_seconds() > timeout:
                    break
                    
            except Exception as e:
                logger.error(f"Error receiving messages from {protocol_id}: {e}")
                break
        
        return messages
    
    async def set_protocol_route(self, service_pattern: str, protocol_id: str) -> bool:
        """Set protocol routing for service"""
        try:
            if protocol_id not in self.protocols:
                logger.error(f"Protocol not found: {protocol_id}")
                return False
            
            self.protocol_routes[service_pattern] = protocol_id
            logger.info(f"Protocol route set: {service_pattern} -> {protocol_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set protocol route: {e}")
            return False
    
    async def get_protocol_metrics(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """Get protocol metrics"""
        adapter = self.adapters.get(protocol_id)
        if not adapter:
            return None
        
        metrics = adapter.get_metrics()
        config = self.protocols[protocol_id]
        
        return {
            "protocol_id": protocol_id,
            "protocol_type": config.protocol_type.value,
            "name": config.name,
            "endpoint": config.endpoint,
            "metrics": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "success_rate": (metrics.successful_requests / max(metrics.total_requests, 1)) * 100,
                "average_latency_ms": metrics.average_latency,
                "peak_latency_ms": metrics.peak_latency,
                "throughput": metrics.throughput,
                "active_connections": metrics.active_connections,
                "total_bytes_sent": metrics.total_bytes_sent,
                "total_bytes_received": metrics.total_bytes_received,
                "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None
            },
            "circuit_breaker": self.circuit_breakers.get(protocol_id, {"state": "closed"})
        }
    
    async def get_all_protocol_metrics(self) -> Dict[str, Any]:
        """Get metrics for all protocols"""
        all_metrics = {}
        
        for protocol_id in self.adapters.keys():
            metrics = await self.get_protocol_metrics(protocol_id)
            if metrics:
                all_metrics[protocol_id] = metrics
        
        return all_metrics
    
    async def optimize_protocol_selection(self, destination: str) -> Optional[str]:
        """Optimize protocol selection for destination"""
        best_protocol = None
        best_score = 0
        
        for protocol_id, adapter in self.adapters.items():
            metrics = adapter.get_metrics()
            
            # Calculate score based on multiple factors
            success_rate = (metrics.successful_requests / max(metrics.total_requests, 1)) * 100
            latency_score = 1000 / max(metrics.average_latency, 1)  # Lower latency = higher score
            availability_score = 100 if self._check_circuit_breaker(protocol_id) else 0
            
            # Weighted score
            total_score = (success_rate * 0.4) + (latency_score * 0.4) + (availability_score * 0.2)
            
            if total_score > best_score:
                best_score = total_score
                best_protocol = protocol_id
        
        return best_protocol
    
    async def add_message_transformer(
        self,
        protocol_id: str,
        transformer: Callable[[CommunicationMessage], CommunicationMessage]
    ) -> bool:
        """Add message transformer for protocol"""
        try:
            transformer_key = f"{protocol_id}_transformer"
            self.transformers[transformer_key] = transformer
            logger.info(f"Message transformer added for protocol: {protocol_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add transformer for {protocol_id}: {e}")
            return False
    
    async def disconnect_protocol(self, protocol_id: str) -> bool:
        """Disconnect a protocol"""
        try:
            adapter = self.adapters.get(protocol_id)
            if adapter:
                await adapter.close()
                del self.adapters[protocol_id]
                await self._trigger_event("protocol_disconnected", protocol_id)
                logger.info(f"Protocol disconnected: {protocol_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to disconnect protocol {protocol_id}: {e}")
            return False
    
    # Private methods
    
    def _validate_config(self, config: ProtocolConfig) -> bool:
        """Validate protocol configuration"""
        if not config.protocol_id or not config.name:
            return False
        
        if not config.endpoint or config.port <= 0:
            return False
        
        if config.protocol_type not in self.adapter_classes:
            logger.warning(f"No adapter available for protocol type: {config.protocol_type}")
        
        return True
    
    def _select_protocol(self, message: CommunicationMessage) -> Optional[str]:
        """Select appropriate protocol for message"""
        # Check if protocol is specified in message
        if message.protocol_id and message.protocol_id in self.adapters:
            return message.protocol_id
        
        # Check routing rules
        for pattern, protocol_id in self.protocol_routes.items():
            if pattern in message.destination:
                return protocol_id
        
        # Default selection based on message characteristics
        if message.method in ["GET", "POST", "PUT", "DELETE"]:
            # Prefer HTTP for REST-like operations
            for protocol_id, config in self.protocols.items():
                if config.protocol_type in [ProtocolType.HTTP, ProtocolType.HTTPS]:
                    return protocol_id
        
        # Fallback to first available protocol
        return next(iter(self.adapters.keys())) if self.adapters else None
    
    async def _optimize_message(self, message: CommunicationMessage, protocol_id: str) -> CommunicationMessage:
        """Apply optimizations to message"""
        optimized_message = CommunicationMessage(
            message_id=message.message_id,
            protocol_id=protocol_id,
            source=message.source,
            destination=message.destination,
            method=message.method,
            path=message.path,
            headers=message.headers.copy(),
            body=message.body,
            timestamp=message.timestamp,
            metadata=message.metadata.copy()
        )
        
        # Apply compression if message is large
        if message.body and len(str(message.body)) > self.compression_threshold:
            config = self.protocols[protocol_id]
            if config.compression != CompressionType.NONE:
                optimized_message.headers["content-encoding"] = config.compression.value
        
        # Apply message transformer if available
        transformer_key = f"{protocol_id}_transformer"
        if transformer_key in self.transformers:
            transformer = self.transformers[transformer_key]
            optimized_message = transformer(optimized_message)
        
        return optimized_message
    
    async def _send_with_retry(
        self,
        adapter: ProtocolAdapter,
        message: CommunicationMessage,
        protocol_id: str
    ) -> CommunicationResponse:
        """Send message with retry logic"""
        last_error = None
        
        for attempt in range(self.retry_attempts):
            try:
                response = await adapter.send_message(message)
                
                # Consider 5xx errors as retryable
                if response.status_code < 500 or not response.error:
                    return response
                
                last_error = response.error
                
                # Exponential backoff
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)
                    
            except Exception as e:
                last_error = str(e)
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)
        
        # All retries failed
        return CommunicationResponse(
            response_id=str(uuid.uuid4()),
            message_id=message.message_id,
            status_code=500,
            error=f"All retry attempts failed. Last error: {last_error}"
        )
    
    def _check_circuit_breaker(self, protocol_id: str) -> bool:
        """Check if circuit breaker allows requests"""
        if protocol_id not in self.circuit_breakers:
            return True
        
        breaker = self.circuit_breakers[protocol_id]
        
        if breaker["state"] == "open":
            # Check if we should try to close the circuit
            if datetime.utcnow() > breaker["open_until"]:
                breaker["state"] = "half_open"
                breaker["failures"] = 0
                return True
            return False
        
        return True
    
    def _update_circuit_breaker(self, protocol_id: str, success: bool):
        """Update circuit breaker state"""
        if protocol_id not in self.circuit_breakers:
            self.circuit_breakers[protocol_id] = {
                "state": "closed",
                "failures": 0,
                "open_until": None
            }
        
        breaker = self.circuit_breakers[protocol_id]
        
        if success:
            if breaker["state"] == "half_open":
                # Success in half-open state closes the circuit
                breaker["state"] = "closed"
            breaker["failures"] = 0
        else:
            breaker["failures"] += 1
            
            if breaker["failures"] >= self.circuit_breaker_threshold:
                breaker["state"] = "open"
                breaker["open_until"] = datetime.utcnow() + timedelta(minutes=5)
                logger.warning(f"Circuit breaker opened for protocol: {protocol_id}")
    
    async def _find_failover_protocol(self, failed_protocol: str, message: CommunicationMessage) -> Optional[str]:
        """Find failover protocol"""
        # Get original protocol config
        failed_config = self.protocols.get(failed_protocol)
        if not failed_config:
            return None
        
        # Find protocols of the same type
        for protocol_id, config in self.protocols.items():
            if (protocol_id != failed_protocol and 
                config.protocol_type == failed_config.protocol_type and
                self._check_circuit_breaker(protocol_id)):
                
                await self._trigger_event("failover_triggered", f"{failed_protocol}->{protocol_id}")
                return protocol_id
        
        return None
    
    async def _trigger_event(self, event_type: str, event_data: str):
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# Global instance
communication_protocol_manager = CommunicationProtocolManager()


# Convenience functions
async def register_http_protocol(
    protocol_id: str,
    endpoint: str,
    port: int = 80,
    ssl_enabled: bool = False
) -> bool:
    """Register HTTP protocol"""
    config = ProtocolConfig(
        protocol_id=protocol_id,
        protocol_type=ProtocolType.HTTPS if ssl_enabled else ProtocolType.HTTP,
        name=f"HTTP {'(SSL)' if ssl_enabled else ''} Protocol",
        endpoint=endpoint,
        port=port,
        ssl_enabled=ssl_enabled
    )
    return await communication_protocol_manager.register_protocol(config)


async def register_websocket_protocol(
    protocol_id: str,
    endpoint: str,
    port: int = 80,
    ssl_enabled: bool = False
) -> bool:
    """Register WebSocket protocol"""
    config = ProtocolConfig(
        protocol_id=protocol_id,
        protocol_type=ProtocolType.WEBSOCKET_SECURE if ssl_enabled else ProtocolType.WEBSOCKET,
        name=f"WebSocket {'(SSL)' if ssl_enabled else ''} Protocol",
        endpoint=endpoint,
        port=port,
        ssl_enabled=ssl_enabled
    )
    return await communication_protocol_manager.register_protocol(config)


async def register_grpc_protocol(
    protocol_id: str,
    endpoint: str,
    port: int = 50051
) -> bool:
    """Register gRPC protocol"""
    config = ProtocolConfig(
        protocol_id=protocol_id,
        protocol_type=ProtocolType.GRPC,
        name="gRPC Protocol",
        endpoint=endpoint,
        port=port,
        serialization=SerializationType.PROTOBUF
    )
    return await communication_protocol_manager.register_protocol(config)


async def send_simple_message(
    source: str,
    destination: str,
    body: Any,
    method: str = "POST",
    protocol_id: Optional[str] = None
) -> CommunicationResponse:
    """Send a simple message"""
    message = CommunicationMessage(
        message_id=str(uuid.uuid4()),
        protocol_id=protocol_id or "",
        source=source,
        destination=destination,
        method=method,
        body=body
    )
    return await communication_protocol_manager.send_message(message, protocol_id)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Register protocols
        await register_http_protocol("http1", "api.example.com", 80)
        await register_websocket_protocol("ws1", "ws.example.com", 80)
        await register_grpc_protocol("grpc1", "grpc.example.com", 50051)
        
        # Set routing
        await communication_protocol_manager.set_protocol_route("api.", "http1")
        await communication_protocol_manager.set_protocol_route("ws.", "ws1")
        
        # Send messages
        response1 = await send_simple_message(
            "client", "api.example.com/users", 
            {"name": "test"}, "POST"
        )
        print(f"HTTP Response: {response1.status_code}")
        
        response2 = await send_simple_message(
            "client", "ws.example.com", 
            {"type": "ping"}, protocol_id="ws1"
        )
        print(f"WebSocket Response: {response2.status_code}")
        
        # Get metrics
        metrics = await communication_protocol_manager.get_all_protocol_metrics()
        for protocol_id, metric_data in metrics.items():
            print(f"Protocol {protocol_id}: {metric_data['metrics']['success_rate']:.1f}% success rate")
    
    asyncio.run(main())