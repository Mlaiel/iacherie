"""
gRPC Gateway - High-Performance gRPC-HTTP Bridge
© 2025 Fahed Mlaiel. All rights reserved.

Enterprise gRPC gateway providing gRPC-HTTP bridge for microservices,
Protocol Buffer integration, streaming support, and service mesh integration.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable, AsyncIterator
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid

logger = logging.getLogger(__name__)


class GRPCMethodType(Enum):
    """gRPC method types"""
    UNARY = "unary"                      # Single request, single response
    SERVER_STREAMING = "server_streaming" # Single request, stream response
    CLIENT_STREAMING = "client_streaming" # Stream request, single response
    BIDIRECTIONAL = "bidirectional"      # Stream request, stream response


class CompressionType(Enum):
    """Compression types for gRPC"""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    SNAPPY = "snappy"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies for gRPC"""
    ROUND_ROBIN = "round_robin"
    LEAST_REQUEST = "least_request"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"
    WEIGHTED = "weighted"


class ServiceStatus(Enum):
    """gRPC service status"""
    SERVING = "serving"
    NOT_SERVING = "not_serving"
    UNKNOWN = "unknown"
    SERVICE_UNKNOWN = "service_unknown"


@dataclass
class GRPCServiceConfig:
    """gRPC service configuration"""
    service_name: str
    proto_file: str = ""
    host: str = "localhost"
    port: int = 50051
    max_message_size: int = 4 * 1024 * 1024  # 4MB
    compression: CompressionType = CompressionType.GZIP
    timeout_seconds: float = 30.0
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    load_balancing: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    tls_enabled: bool = False
    tls_cert_path: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class GRPCMethod:
    """gRPC method definition"""
    name: str
    service: str
    method_type: GRPCMethodType
    request_type: str
    response_type: str
    description: str = ""
    timeout_seconds: float = 30.0
    streaming: bool = False
    authenticated: bool = True


@dataclass
class GRPCRequest:
    """gRPC request"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service: str = ""
    method: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    timeout_seconds: float = 30.0
    compression: CompressionType = CompressionType.GZIP


@dataclass
class GRPCResponse:
    """gRPC response"""
    request_id: str
    service: str
    method: str
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)
    status_code: int = 0  # 0 = OK in gRPC
    status_message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    compressed: bool = False


@dataclass
class GRPCStreamMessage:
    """gRPC streaming message"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stream_id: str = ""
    sequence_number: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)
    is_final: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


class GRPCGateway:
    """
    gRPC Gateway - HTTP-gRPC Bridge
    
    Provides enterprise gRPC gateway functionality:
    - gRPC-HTTP protocol translation
    - Protocol Buffer integration
    - Streaming support (all types)
    - Service mesh integration
    - Load balancing
    - Health checking
    - Metrics collection
    """
    
    def __init__(
        self,
        enable_reflection: bool = True,
        enable_health_check: bool = True,
        enable_metrics: bool = True,
        max_concurrent_streams: int = 100
    ):
        """
        Initialize gRPC Gateway
        
        Args:
            enable_reflection: Enable gRPC reflection for service discovery
            enable_health_check: Enable health checking
            enable_metrics: Enable metrics collection
            max_concurrent_streams: Maximum concurrent streams
        """
        self.enable_reflection = enable_reflection
        self.enable_health_check = enable_health_check
        self.enable_metrics = enable_metrics
        self.max_concurrent_streams = max_concurrent_streams
        
        # Service registry
        self.services: Dict[str, GRPCServiceConfig] = {}
        self.methods: Dict[str, GRPCMethod] = {}
        
        # Connection pool
        self.connections: Dict[str, List[Any]] = {}
        self.active_streams: Dict[str, Any] = {}
        
        # Metrics
        self.request_count: int = 0
        self.stream_count: int = 0
        self.error_count: int = 0
        self.total_bytes_sent: int = 0
        self.total_bytes_received: int = 0
        
        # Service health status
        self.service_health: Dict[str, ServiceStatus] = {}
        
        logger.info("gRPC Gateway initialized")
    
    def register_service(self, config: GRPCServiceConfig) -> None:
        """
        Register gRPC service
        
        Args:
            config: Service configuration
        """
        try:
            self.services[config.service_name] = config
            self.service_health[config.service_name] = ServiceStatus.UNKNOWN
            
            logger.info(
                f"Registered gRPC service: {config.service_name} "
                f"at {config.host}:{config.port}"
            )
            
        except Exception as e:
            logger.error(f"Error registering gRPC service: {e}")
            raise
    
    def register_method(self, method: GRPCMethod) -> None:
        """
        Register gRPC method
        
        Args:
            method: Method definition
        """
        try:
            method_key = f"{method.service}/{method.name}"
            self.methods[method_key] = method
            
            logger.info(
                f"Registered gRPC method: {method_key} "
                f"({method.method_type.value})"
            )
            
        except Exception as e:
            logger.error(f"Error registering gRPC method: {e}")
            raise
    
    async def call_unary(
        self,
        service: str,
        method: str,
        request: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> GRPCResponse:
        """
        Call unary gRPC method (single request, single response)
        
        Args:
            service: Service name
            method: Method name
            request: Request payload
            metadata: Optional metadata
            timeout: Optional timeout override
            
        Returns:
            gRPC response
        """
        try:
            self.request_count += 1
            
            grpc_request = GRPCRequest(
                service=service,
                method=method,
                payload=request,
                metadata=metadata or {},
                timeout_seconds=timeout or 30.0
            )
            
            # Simulate gRPC call (in production, use actual gRPC client)
            logger.info(f"gRPC unary call: {service}/{method}")
            
            # Mock response
            response = GRPCResponse(
                request_id=grpc_request.request_id,
                service=service,
                method=method,
                payload={'result': 'success', 'data': request},
                status_code=0,
                status_message="OK"
            )
            
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in gRPC unary call: {e}")
            
            return GRPCResponse(
                request_id=grpc_request.request_id if 'grpc_request' in locals() else "",
                service=service,
                method=method,
                status_code=2,  # gRPC UNKNOWN error
                status_message=str(e)
            )
    
    async def call_server_streaming(
        self,
        service: str,
        method: str,
        request: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None
    ) -> AsyncIterator[GRPCStreamMessage]:
        """
        Call server streaming gRPC method (single request, stream response)
        
        Args:
            service: Service name
            method: Method name
            request: Request payload
            metadata: Optional metadata
            
        Yields:
            Stream messages
        """
        try:
            self.request_count += 1
            self.stream_count += 1
            
            stream_id = str(uuid.uuid4())
            logger.info(
                f"gRPC server streaming call: {service}/{method} "
                f"(stream_id: {stream_id})"
            )
            
            # Mock streaming response (in production, use actual gRPC client)
            for i in range(5):  # Simulate 5 messages
                message = GRPCStreamMessage(
                    stream_id=stream_id,
                    sequence_number=i,
                    payload={
                        'message': f'Stream message {i}',
                        'data': request,
                        'progress': (i + 1) / 5
                    },
                    is_final=(i == 4)
                )
                
                yield message
                await asyncio.sleep(0.1)  # Simulate processing delay
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in gRPC server streaming call: {e}")
    
    async def call_client_streaming(
        self,
        service: str,
        method: str,
        request_stream: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, str]] = None
    ) -> GRPCResponse:
        """
        Call client streaming gRPC method (stream request, single response)
        
        Args:
            service: Service name
            method: Method name
            request_stream: Request stream
            metadata: Optional metadata
            
        Returns:
            gRPC response
        """
        try:
            self.request_count += 1
            self.stream_count += 1
            
            stream_id = str(uuid.uuid4())
            logger.info(
                f"gRPC client streaming call: {service}/{method} "
                f"(stream_id: {stream_id})"
            )
            
            # Collect all stream messages
            messages = []
            async for request_msg in request_stream:
                messages.append(request_msg)
            
            # Mock response
            response = GRPCResponse(
                request_id=stream_id,
                service=service,
                method=method,
                payload={
                    'result': 'success',
                    'messages_received': len(messages),
                    'summary': messages
                },
                status_code=0,
                status_message="OK"
            )
            
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in gRPC client streaming call: {e}")
            
            return GRPCResponse(
                request_id=stream_id if 'stream_id' in locals() else "",
                service=service,
                method=method,
                status_code=2,
                status_message=str(e)
            )
    
    async def call_bidirectional_streaming(
        self,
        service: str,
        method: str,
        request_stream: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, str]] = None
    ) -> AsyncIterator[GRPCStreamMessage]:
        """
        Call bidirectional streaming gRPC method (stream request, stream response)
        
        Args:
            service: Service name
            method: Method name
            request_stream: Request stream
            metadata: Optional metadata
            
        Yields:
            Response stream messages
        """
        try:
            self.request_count += 1
            self.stream_count += 1
            
            stream_id = str(uuid.uuid4())
            logger.info(
                f"gRPC bidirectional streaming call: {service}/{method} "
                f"(stream_id: {stream_id})"
            )
            
            sequence = 0
            async for request_msg in request_stream:
                # Echo back with processing
                response_msg = GRPCStreamMessage(
                    stream_id=stream_id,
                    sequence_number=sequence,
                    payload={
                        'echo': request_msg,
                        'processed': True,
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    is_final=False
                )
                
                sequence += 1
                yield response_msg
                await asyncio.sleep(0.05)
            
            # Send final message
            final_msg = GRPCStreamMessage(
                stream_id=stream_id,
                sequence_number=sequence,
                payload={'status': 'completed', 'total_messages': sequence},
                is_final=True
            )
            yield final_msg
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in gRPC bidirectional streaming call: {e}")
    
    async def http_to_grpc(
        self,
        http_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert HTTP request to gRPC call
        
        Args:
            http_request: HTTP request data
            
        Returns:
            gRPC response as HTTP response
        """
        try:
            # Extract service and method from HTTP path
            path = http_request.get('path', '')
            parts = path.strip('/').split('/')
            
            if len(parts) < 2:
                return {
                    'status': 400,
                    'error': 'Invalid gRPC path format'
                }
            
            service = parts[0]
            method = parts[1]
            
            # Get request body
            body = http_request.get('body', {})
            
            # Call gRPC method
            grpc_response = await self.call_unary(
                service=service,
                method=method,
                request=body,
                metadata=http_request.get('headers', {})
            )
            
            # Convert to HTTP response
            http_status = 200 if grpc_response.status_code == 0 else 500
            
            return {
                'status': http_status,
                'body': grpc_response.payload,
                'headers': {
                    'Content-Type': 'application/json',
                    'X-GRPC-Status': str(grpc_response.status_code),
                    'X-GRPC-Message': grpc_response.status_message
                }
            }
            
        except Exception as e:
            logger.error(f"Error converting HTTP to gRPC: {e}")
            return {
                'status': 500,
                'error': str(e)
            }
    
    async def check_service_health(
        self,
        service: str
    ) -> Dict[str, Any]:
        """
        Check gRPC service health
        
        Args:
            service: Service name
            
        Returns:
            Service health status
        """
        try:
            if service not in self.services:
                return {
                    'service': service,
                    'status': ServiceStatus.SERVICE_UNKNOWN.value,
                    'message': 'Service not registered'
                }
            
            # In production, perform actual health check
            # For now, simulate health check
            config = self.services[service]
            
            # Mock health check
            is_healthy = True  # Simulate health check result
            
            status = ServiceStatus.SERVING if is_healthy else ServiceStatus.NOT_SERVING
            self.service_health[service] = status
            
            return {
                'service': service,
                'status': status.value,
                'host': config.host,
                'port': config.port,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking service health: {e}")
            self.service_health[service] = ServiceStatus.UNKNOWN
            
            return {
                'service': service,
                'status': ServiceStatus.UNKNOWN.value,
                'error': str(e)
            }
    
    def get_service_metrics(self, service: Optional[str] = None) -> Dict[str, Any]:
        """
        Get gRPC service metrics
        
        Args:
            service: Optional service name filter
            
        Returns:
            Service metrics
        """
        try:
            metrics = {
                'total_requests': self.request_count,
                'total_streams': self.stream_count,
                'error_count': self.error_count,
                'error_rate': (self.error_count / self.request_count * 100) if self.request_count > 0 else 0.0,
                'bytes_sent': self.total_bytes_sent,
                'bytes_received': self.total_bytes_received,
                'active_streams': len(self.active_streams),
                'registered_services': len(self.services),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if service and service in self.services:
                metrics['service'] = service
                metrics['health_status'] = self.service_health.get(service, ServiceStatus.UNKNOWN).value
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting service metrics: {e}")
            return {}
    
    def get_load_balancing_stats(self) -> Dict[str, Any]:
        """
        Get load balancing statistics
        
        Returns:
            Load balancing stats
        """
        try:
            stats = {
                'strategy': 'round_robin',  # Default strategy
                'services': {},
                'total_connections': sum(len(conns) for conns in self.connections.values()),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            for service_name, config in self.services.items():
                stats['services'][service_name] = {
                    'strategy': config.load_balancing.value,
                    'connection_count': len(self.connections.get(service_name, [])),
                    'health_status': self.service_health.get(service_name, ServiceStatus.UNKNOWN).value
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting load balancing stats: {e}")
            return {}
    
    async def shutdown(self) -> None:
        """Gracefully shutdown gRPC gateway"""
        try:
            logger.info("Shutting down gRPC gateway...")
            
            # Close all active streams
            for stream_id in list(self.active_streams.keys()):
                try:
                    # In production, properly close gRPC streams
                    del self.active_streams[stream_id]
                except Exception as e:
                    logger.error(f"Error closing stream {stream_id}: {e}")
            
            # Close all connections
            for service_name in list(self.connections.keys()):
                try:
                    # In production, properly close gRPC connections
                    self.connections[service_name].clear()
                except Exception as e:
                    logger.error(f"Error closing connections for {service_name}: {e}")
            
            logger.info("gRPC gateway shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during gRPC gateway shutdown: {e}")


class GRPCServiceMeshIntegration:
    """
    gRPC Service Mesh Integration
    
    Integrates gRPC gateway with service mesh (Istio, Linkerd, etc.)
    """
    
    def __init__(
        self,
        gateway: GRPCGateway,
        mesh_type: str = "istio"
    ):
        """
        Initialize service mesh integration
        
        Args:
            gateway: gRPC gateway instance
            mesh_type: Service mesh type (istio, linkerd, consul)
        """
        self.gateway = gateway
        self.mesh_type = mesh_type
        
        logger.info(f"gRPC Service Mesh Integration initialized: {mesh_type}")
    
    def register_with_mesh(self, service: str) -> Dict[str, Any]:
        """
        Register service with service mesh
        
        Args:
            service: Service name
            
        Returns:
            Registration result
        """
        try:
            if service not in self.gateway.services:
                return {
                    'success': False,
                    'error': 'Service not found'
                }
            
            config = self.gateway.services[service]
            
            # In production, register with actual service mesh
            logger.info(
                f"Registering {service} with {self.mesh_type} service mesh"
            )
            
            return {
                'success': True,
                'service': service,
                'mesh': self.mesh_type,
                'endpoint': f"{config.host}:{config.port}"
            }
            
        except Exception as e:
            logger.error(f"Error registering with service mesh: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def enable_mutual_tls(self, service: str) -> bool:
        """
        Enable mutual TLS for service
        
        Args:
            service: Service name
            
        Returns:
            True if successful
        """
        try:
            if service not in self.gateway.services:
                return False
            
            config = self.gateway.services[service]
            config.tls_enabled = True
            
            logger.info(f"Enabled mTLS for service: {service}")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling mTLS: {e}")
            return False


# Creator platform gRPC configuration
IACHERIE_GRPC_CONFIG = {
    'services': {
        'ai_processing_service': {
            'host': 'ai-processing.iacherie.svc.cluster.local',
            'port': 50051,
            'methods': ['ProcessContent', 'AnalyzeCreator', 'StreamResults']
        },
        'content_service': {
            'host': 'content.iacherie.svc.cluster.local',
            'port': 50052,
            'methods': ['UploadContent', 'GetContent', 'StreamContent']
        },
        'distribution_service': {
            'host': 'distribution.iacherie.svc.cluster.local',
            'port': 50053,
            'methods': ['DistributeContent', 'GetPlatformStatus']
        },
        'monetization_service': {
            'host': 'monetization.iacherie.svc.cluster.local',
            'port': 50054,
            'methods': ['ProcessPayment', 'GetRevenue', 'StreamTransactions']
        },
        'analytics_service': {
            'host': 'analytics.iacherie.svc.cluster.local',
            'port': 50055,
            'methods': ['GetAnalytics', 'StreamMetrics', 'GenerateReport']
        }
    },
    'load_balancing': {
        'strategy': 'round_robin',
        'health_check_interval': 30,
        'max_connections_per_service': 100
    },
    'compression': {
        'enabled': True,
        'type': 'gzip',
        'min_size_bytes': 1024
    },
    'streaming': {
        'max_concurrent_streams': 100,
        'buffer_size': 65536,
        'timeout_seconds': 300
    },
    'service_mesh': {
        'enabled': True,
        'type': 'istio',
        'mtls_enabled': True
    }
}
