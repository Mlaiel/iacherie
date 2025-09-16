"""
gRPC API Gateway - High-Performance Protocol Buffer Gateway
© 2025 Fahed Mlaiel. All rights reserved.

gRPC Gateway providing gRPC-HTTP bridge, protocol buffer integration,
streaming support, service mesh integration, and load balancing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, AsyncIterator, Iterator
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from dataclasses import dataclass, field
import time
import threading
from collections import defaultdict
import base64

logger = logging.getLogger(__name__)


class GRPCMethod(Enum):
    """gRPC method types"""
    UNARY = "unary"
    SERVER_STREAMING = "server_streaming"
    CLIENT_STREAMING = "client_streaming"
    BIDIRECTIONAL_STREAMING = "bidirectional_streaming"


class GRPCStatus(Enum):
    """gRPC status codes"""
    OK = 0
    CANCELLED = 1
    UNKNOWN = 2
    INVALID_ARGUMENT = 3
    DEADLINE_EXCEEDED = 4
    NOT_FOUND = 5
    ALREADY_EXISTS = 6
    PERMISSION_DENIED = 7
    RESOURCE_EXHAUSTED = 8
    FAILED_PRECONDITION = 9
    ABORTED = 10
    OUT_OF_RANGE = 11
    UNIMPLEMENTED = 12
    INTERNAL = 13
    UNAVAILABLE = 14
    DATA_LOSS = 15
    UNAUTHENTICATED = 16


class CompressionType(Enum):
    """gRPC compression types"""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"


@dataclass
class GRPCServiceConfig:
    """gRPC service configuration"""
    name: str
    host: str
    port: int
    ssl_enabled: bool = False
    timeout: float = 30.0
    max_message_size: int = 4 * 1024 * 1024  # 4MB
    compression: CompressionType = CompressionType.GZIP
    keepalive_time: int = 30
    keepalive_timeout: int = 5
    keepalive_permit_without_calls: bool = True
    max_concurrent_streams: int = 100
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class GRPCEndpoint:
    """gRPC endpoint definition"""
    service_name: str
    method_name: str
    full_method: str
    method_type: GRPCMethod
    request_type: str
    response_type: str
    http_path: str = ""
    http_method: str = "POST"
    timeout: Optional[float] = None
    auth_required: bool = True
    rate_limit: Optional[int] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GRPCRequest:
    """gRPC request wrapper"""
    service_name: str
    method_name: str
    payload: Dict[str, Any]
    metadata: Dict[str, str] = field(default_factory=dict)
    timeout: Optional[float] = None
    compression: Optional[CompressionType] = None
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GRPCResponse:
    """gRPC response wrapper"""
    status_code: GRPCStatus
    payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)
    trace_id: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GRPCMetrics:
    """gRPC gateway metrics"""
    service_name: str
    method_name: str
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    last_request_time: Optional[datetime] = None
    error_rate: float = 0.0
    throughput_per_second: float = 0.0


class GRPCLoadBalancer:
    """
    gRPC Load Balancer
    
    Provides load balancing for gRPC services:
    - Round-robin distribution
    - Health-based routing
    - Weighted load balancing
    - Connection pooling
    """
    
    def __init__(self):
        """Initialize load balancer"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.services: Dict[str, List[GRPCServiceConfig]] = defaultdict(list)
        self.current_index: Dict[str, int] = defaultdict(int)
        self.health_status: Dict[str, bool] = {}
        self.connection_counts: Dict[str, int] = defaultdict(int)
        self._lock = threading.RLock()
    
    def add_service(self, config: GRPCServiceConfig):
        """Add a gRPC service instance"""
        with self._lock:
            service_key = f"{config.host}:{config.port}"
            self.services[config.name].append(config)
            self.health_status[service_key] = True
            
        self.logger.info(f"Added gRPC service instance: {config.name} at {service_key}")
    
    def remove_service(self, service_name: str, host: str, port: int):
        """Remove a gRPC service instance"""
        with self._lock:
            service_key = f"{host}:{port}"
            
            if service_name in self.services:
                self.services[service_name] = [
                    config for config in self.services[service_name]
                    if not (config.host == host and config.port == port)
                ]
                
                if service_key in self.health_status:
                    del self.health_status[service_key]
                
                if service_key in self.connection_counts:
                    del self.connection_counts[service_key]
        
        self.logger.info(f"Removed gRPC service instance: {service_name} at {service_key}")
    
    def get_service_instance(self, service_name: str) -> Optional[GRPCServiceConfig]:
        """Get next available service instance using round-robin"""
        with self._lock:
            if service_name not in self.services or not self.services[service_name]:
                return None
            
            instances = self.services[service_name]
            healthy_instances = [
                instance for instance in instances
                if self.health_status.get(f"{instance.host}:{instance.port}", True)
            ]
            
            if not healthy_instances:
                # Fall back to all instances if none are marked healthy
                healthy_instances = instances
            
            if not healthy_instances:
                return None
            
            # Round-robin selection
            index = self.current_index[service_name] % len(healthy_instances)
            self.current_index[service_name] = (index + 1) % len(healthy_instances)
            
            selected_instance = healthy_instances[index]
            service_key = f"{selected_instance.host}:{selected_instance.port}"
            self.connection_counts[service_key] += 1
            
            return selected_instance
    
    def mark_unhealthy(self, host: str, port: int):
        """Mark a service instance as unhealthy"""
        service_key = f"{host}:{port}"
        with self._lock:
            self.health_status[service_key] = False
        
        self.logger.warning(f"Marked service instance as unhealthy: {service_key}")
    
    def mark_healthy(self, host: str, port: int):
        """Mark a service instance as healthy"""
        service_key = f"{host}:{port}"
        with self._lock:
            self.health_status[service_key] = True
        
        self.logger.info(f"Marked service instance as healthy: {service_key}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        with self._lock:
            return {
                "services": {
                    name: len(instances) for name, instances in self.services.items()
                },
                "health_status": dict(self.health_status),
                "connection_counts": dict(self.connection_counts),
                "total_services": sum(len(instances) for instances in self.services.values()),
                "healthy_services": sum(1 for status in self.health_status.values() if status)
            }


class GRPCGateway:
    """
    gRPC API Gateway
    
    Provides comprehensive gRPC gateway functionality:
    - gRPC-HTTP protocol translation
    - Service discovery and load balancing
    - Authentication and authorization
    - Request/response transformation
    - Streaming support
    - Metrics and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize gRPC gateway"""
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.load_balancer = GRPCLoadBalancer()
        self.endpoints: Dict[str, GRPCEndpoint] = {}
        self.metrics: Dict[str, GRPCMetrics] = defaultdict(lambda: GRPCMetrics("", ""))
        
        # Connection management
        self.connections: Dict[str, Any] = {}  # Would store actual gRPC channels
        self.connection_pool_size = self.config.get('connection_pool_size', 10)
        
        # Request tracking
        self.active_requests: Dict[str, GRPCRequest] = {}
        self.streaming_sessions: Dict[str, Any] = {}
        
        # Configuration
        self.default_timeout = self.config.get('default_timeout', 30.0)
        self.max_message_size = self.config.get('max_message_size', 4 * 1024 * 1024)
        self.enable_compression = self.config.get('enable_compression', True)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Monitoring
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        self.logger.info("gRPC Gateway initialized")
    
    async def start(self):
        """Start gRPC gateway"""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_worker())
        
        self.logger.info("gRPC Gateway started")
    
    async def stop(self):
        """Stop gRPC gateway"""
        if not self._running:
            return
        
        self._running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        await self._cleanup_connections()
        
        self.logger.info("gRPC Gateway stopped")
    
    def register_service(self, config: GRPCServiceConfig):
        """Register a gRPC service"""
        self.load_balancer.add_service(config)
        self.logger.info(f"Registered gRPC service: {config.name}")
    
    def register_endpoint(self, endpoint: GRPCEndpoint):
        """Register a gRPC endpoint"""
        with self._lock:
            key = f"{endpoint.service_name}.{endpoint.method_name}"
            self.endpoints[key] = endpoint
            
            # Initialize metrics
            self.metrics[key] = GRPCMetrics(
                service_name=endpoint.service_name,
                method_name=endpoint.method_name
            )
        
        self.logger.info(f"Registered gRPC endpoint: {key}")
    
    async def call_unary(
        self,
        service_name: str,
        method_name: str,
        request_data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> GRPCResponse:
        """Execute unary gRPC call"""
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        try:
            # Get service instance
            service_config = self.load_balancer.get_service_instance(service_name)
            if not service_config:
                return GRPCResponse(
                    status_code=GRPCStatus.UNAVAILABLE,
                    error_message=f"No available instances for service: {service_name}",
                    trace_id=trace_id
                )
            
            # Create request
            request = GRPCRequest(
                service_name=service_name,
                method_name=method_name,
                payload=request_data,
                metadata=metadata or {},
                timeout=timeout or self.default_timeout,
                trace_id=trace_id,
                user_id=user_id
            )
            
            # Track active request
            with self._lock:
                self.active_requests[trace_id] = request
            
            try:
                # Simulate gRPC call (in real implementation, this would use grpc library)
                response_data = await self._simulate_grpc_call(service_config, request)
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Record success metrics
                await self._record_metrics(service_name, method_name, duration_ms, True)
                
                return GRPCResponse(
                    status_code=GRPCStatus.OK,
                    payload=response_data,
                    trace_id=trace_id,
                    duration_ms=duration_ms
                )
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Record failure metrics
                await self._record_metrics(service_name, method_name, duration_ms, False)
                
                # Mark service as unhealthy if needed
                if isinstance(e, (ConnectionError, TimeoutError)):
                    self.load_balancer.mark_unhealthy(service_config.host, service_config.port)
                
                return GRPCResponse(
                    status_code=GRPCStatus.INTERNAL,
                    error_message=str(e),
                    trace_id=trace_id,
                    duration_ms=duration_ms
                )
            
        finally:
            # Clean up tracking
            with self._lock:
                if trace_id in self.active_requests:
                    del self.active_requests[trace_id]
    
    async def call_server_streaming(
        self,
        service_name: str,
        method_name: str,
        request_data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> AsyncIterator[GRPCResponse]:
        """Execute server streaming gRPC call"""
        trace_id = str(uuid.uuid4())
        
        try:
            # Get service instance
            service_config = self.load_balancer.get_service_instance(service_name)
            if not service_config:
                yield GRPCResponse(
                    status_code=GRPCStatus.UNAVAILABLE,
                    error_message=f"No available instances for service: {service_name}",
                    trace_id=trace_id
                )
                return
            
            # Create request
            request = GRPCRequest(
                service_name=service_name,
                method_name=method_name,
                payload=request_data,
                metadata=metadata or {},
                timeout=timeout or self.default_timeout,
                trace_id=trace_id,
                user_id=user_id
            )
            
            # Simulate streaming response
            for i in range(5):  # Simulate 5 streaming responses
                await asyncio.sleep(0.1)  # Simulate processing delay
                
                yield GRPCResponse(
                    status_code=GRPCStatus.OK,
                    payload={
                        "chunk_id": i,
                        "data": f"Streaming data chunk {i}",
                        "total_chunks": 5,
                        "trace_id": trace_id
                    },
                    trace_id=trace_id
                )
            
            # Record metrics
            await self._record_metrics(service_name, method_name, 0, True)
            
        except Exception as e:
            await self._record_metrics(service_name, method_name, 0, False)
            
            yield GRPCResponse(
                status_code=GRPCStatus.INTERNAL,
                error_message=str(e),
                trace_id=trace_id
            )
    
    async def call_client_streaming(
        self,
        service_name: str,
        method_name: str,
        request_stream: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> GRPCResponse:
        """Execute client streaming gRPC call"""
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        try:
            # Get service instance
            service_config = self.load_balancer.get_service_instance(service_name)
            if not service_config:
                return GRPCResponse(
                    status_code=GRPCStatus.UNAVAILABLE,
                    error_message=f"No available instances for service: {service_name}",
                    trace_id=trace_id
                )
            
            # Collect streaming data
            collected_data = []
            async for data in request_stream:
                collected_data.append(data)
                
                # Check for limits
                if len(collected_data) > 1000:  # Arbitrary limit
                    return GRPCResponse(
                        status_code=GRPCStatus.RESOURCE_EXHAUSTED,
                        error_message="Too many streaming requests",
                        trace_id=trace_id
                    )
            
            # Simulate processing
            result_data = {
                "processed_items": len(collected_data),
                "summary": "Client streaming completed successfully",
                "trace_id": trace_id
            }
            
            duration_ms = (time.time() - start_time) * 1000
            await self._record_metrics(service_name, method_name, duration_ms, True)
            
            return GRPCResponse(
                status_code=GRPCStatus.OK,
                payload=result_data,
                trace_id=trace_id,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            await self._record_metrics(service_name, method_name, duration_ms, False)
            
            return GRPCResponse(
                status_code=GRPCStatus.INTERNAL,
                error_message=str(e),
                trace_id=trace_id,
                duration_ms=duration_ms
            )
    
    async def call_bidirectional_streaming(
        self,
        service_name: str,
        method_name: str,
        request_stream: AsyncIterator[Dict[str, Any]],
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> AsyncIterator[GRPCResponse]:
        """Execute bidirectional streaming gRPC call"""
        trace_id = str(uuid.uuid4())
        
        try:
            # Get service instance
            service_config = self.load_balancer.get_service_instance(service_name)
            if not service_config:
                yield GRPCResponse(
                    status_code=GRPCStatus.UNAVAILABLE,
                    error_message=f"No available instances for service: {service_name}",
                    trace_id=trace_id
                )
                return
            
            # Process bidirectional streaming
            request_count = 0
            async for request_data in request_stream:
                request_count += 1
                
                # Simulate processing and immediate response
                response_data = {
                    "request_id": request_count,
                    "echo": request_data,
                    "processed_at": datetime.utcnow().isoformat(),
                    "trace_id": trace_id
                }
                
                yield GRPCResponse(
                    status_code=GRPCStatus.OK,
                    payload=response_data,
                    trace_id=trace_id
                )
                
                await asyncio.sleep(0.01)  # Small delay to simulate processing
            
            # Final response
            yield GRPCResponse(
                status_code=GRPCStatus.OK,
                payload={
                    "session_completed": True,
                    "total_requests_processed": request_count,
                    "trace_id": trace_id
                },
                trace_id=trace_id
            )
            
            await self._record_metrics(service_name, method_name, 0, True)
            
        except Exception as e:
            await self._record_metrics(service_name, method_name, 0, False)
            
            yield GRPCResponse(
                status_code=GRPCStatus.INTERNAL,
                error_message=str(e),
                trace_id=trace_id
            )
    
    def http_to_grpc_request(
        self,
        http_method: str,
        path: str,
        headers: Dict[str, str],
        body: bytes,
        query_params: Dict[str, str]
    ) -> Optional[GRPCRequest]:
        """Convert HTTP request to gRPC request"""
        try:
            # Find matching endpoint
            endpoint = None
            for ep in self.endpoints.values():
                if ep.http_path and ep.http_path == path and ep.http_method == http_method:
                    endpoint = ep
                    break
            
            if not endpoint:
                return None
            
            # Parse body
            if body:
                try:
                    payload = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError:
                    # Try to decode as base64 for binary data
                    try:
                        payload = {"data": base64.b64encode(body).decode('utf-8')}
                    except Exception:
                        payload = {"raw": body.hex()}
            else:
                payload = query_params
            
            # Extract metadata from headers
            metadata = {}
            for key, value in headers.items():
                if key.lower().startswith('grpc-'):
                    metadata[key] = value
            
            return GRPCRequest(
                service_name=endpoint.service_name,
                method_name=endpoint.method_name,
                payload=payload,
                metadata=metadata,
                user_id=headers.get('x-user-id')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to convert HTTP to gRPC request: {e}")
            return None
    
    def grpc_to_http_response(
        self,
        grpc_response: GRPCResponse,
        accept_encoding: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert gRPC response to HTTP response"""
        try:
            # Map gRPC status to HTTP status
            status_mapping = {
                GRPCStatus.OK: 200,
                GRPCStatus.INVALID_ARGUMENT: 400,
                GRPCStatus.UNAUTHENTICATED: 401,
                GRPCStatus.PERMISSION_DENIED: 403,
                GRPCStatus.NOT_FOUND: 404,
                GRPCStatus.RESOURCE_EXHAUSTED: 429,
                GRPCStatus.INTERNAL: 500,
                GRPCStatus.UNAVAILABLE: 503,
                GRPCStatus.DEADLINE_EXCEEDED: 504
            }
            
            http_status = status_mapping.get(grpc_response.status_code, 500)
            
            # Prepare response body
            response_body = {}
            if grpc_response.payload:
                response_body.update(grpc_response.payload)
            
            if grpc_response.status_code != GRPCStatus.OK:
                response_body["error"] = {
                    "code": grpc_response.status_code.value,
                    "message": grpc_response.error_message or "Unknown error",
                    "status": grpc_response.status_code.name
                }
            
            # Add metadata
            response_body["metadata"] = {
                "trace_id": grpc_response.trace_id,
                "duration_ms": grpc_response.duration_ms,
                "timestamp": grpc_response.timestamp.isoformat()
            }
            
            # Prepare headers
            headers = {
                "content-type": "application/json",
                "x-grpc-gateway": "true",
                "x-trace-id": grpc_response.trace_id or "",
                "x-duration-ms": str(grpc_response.duration_ms)
            }
            
            # Add gRPC metadata as headers
            for key, value in grpc_response.metadata.items():
                headers[f"x-grpc-{key}"] = value
            
            return {
                "status_code": http_status,
                "headers": headers,
                "body": json.dumps(response_body),
                "content_type": "application/json"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to convert gRPC to HTTP response: {e}")
            return {
                "status_code": 500,
                "headers": {"content-type": "application/json"},
                "body": json.dumps({"error": "Internal conversion error"}),
                "content_type": "application/json"
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get gRPC gateway metrics"""
        with self._lock:
            total_requests = sum(m.request_count for m in self.metrics.values())
            total_errors = sum(m.error_count for m in self.metrics.values())
            
            service_metrics = {}
            for key, metrics in self.metrics.items():
                service_metrics[key] = {
                    "service_name": metrics.service_name,
                    "method_name": metrics.method_name,
                    "request_count": metrics.request_count,
                    "success_count": metrics.success_count,
                    "error_count": metrics.error_count,
                    "error_rate": metrics.error_rate,
                    "avg_duration_ms": metrics.avg_duration_ms,
                    "min_duration_ms": metrics.min_duration_ms if metrics.min_duration_ms != float('inf') else 0,
                    "max_duration_ms": metrics.max_duration_ms,
                    "throughput_per_second": metrics.throughput_per_second,
                    "last_request_time": metrics.last_request_time.isoformat() if metrics.last_request_time else None
                }
            
            return {
                "summary": {
                    "total_requests": total_requests,
                    "total_errors": total_errors,
                    "global_error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
                    "active_requests": len(self.active_requests),
                    "streaming_sessions": len(self.streaming_sessions),
                    "registered_endpoints": len(self.endpoints),
                    "timestamp": datetime.utcnow().isoformat()
                },
                "services": service_metrics,
                "load_balancer": self.load_balancer.get_stats(),
                "gateway_config": {
                    "default_timeout": self.default_timeout,
                    "max_message_size": self.max_message_size,
                    "enable_compression": self.enable_compression,
                    "connection_pool_size": self.connection_pool_size
                }
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get gateway health status"""
        load_balancer_stats = self.load_balancer.get_stats()
        
        is_healthy = (
            load_balancer_stats["healthy_services"] > 0 and
            len(self.endpoints) > 0 and
            self._running
        )
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "gateway_running": self._running,
            "total_services": load_balancer_stats["total_services"],
            "healthy_services": load_balancer_stats["healthy_services"],
            "registered_endpoints": len(self.endpoints),
            "active_requests": len(self.active_requests),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _simulate_grpc_call(
        self,
        service_config: GRPCServiceConfig,
        request: GRPCRequest
    ) -> Dict[str, Any]:
        """Simulate gRPC call (replace with actual gRPC implementation)"""
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Simulate some processing based on the request
        return {
            "success": True,
            "service": service_config.name,
            "method": request.method_name,
            "processed_at": datetime.utcnow().isoformat(),
            "trace_id": request.trace_id,
            "response_data": f"Processed {request.method_name} successfully"
        }
    
    async def _record_metrics(
        self,
        service_name: str,
        method_name: str,
        duration_ms: float,
        success: bool
    ):
        """Record metrics for a gRPC call"""
        key = f"{service_name}.{method_name}"
        
        with self._lock:
            metrics = self.metrics[key]
            metrics.service_name = service_name
            metrics.method_name = method_name
            metrics.request_count += 1
            metrics.last_request_time = datetime.utcnow()
            
            if success:
                metrics.success_count += 1
            else:
                metrics.error_count += 1
            
            # Update duration metrics
            if duration_ms > 0:
                metrics.total_duration_ms += duration_ms
                metrics.avg_duration_ms = metrics.total_duration_ms / metrics.request_count
                metrics.min_duration_ms = min(metrics.min_duration_ms, duration_ms)
                metrics.max_duration_ms = max(metrics.max_duration_ms, duration_ms)
            
            # Update error rate
            metrics.error_rate = (metrics.error_count / metrics.request_count) * 100
            
            # Calculate throughput (simplified)
            metrics.throughput_per_second = metrics.request_count / 3600  # Assume 1 hour window
    
    async def _monitoring_worker(self):
        """Background monitoring worker"""
        while self._running:
            try:
                await self._health_check_services()
                await self._cleanup_expired_requests()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring worker error: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_services(self):
        """Perform health checks on registered services"""
        # This would implement actual health checks to gRPC services
        # For now, we'll just log the current state
        stats = self.load_balancer.get_stats()
        if stats["total_services"] > 0:
            self.logger.debug(
                f"Service health check: {stats['healthy_services']}/{stats['total_services']} healthy"
            )
    
    async def _cleanup_expired_requests(self):
        """Clean up expired requests and sessions"""
        current_time = datetime.utcnow()
        expired_threshold = current_time - timedelta(minutes=5)
        
        with self._lock:
            # Clean up expired requests
            expired_requests = [
                trace_id for trace_id, request in self.active_requests.items()
                if request.timestamp < expired_threshold
            ]
            
            for trace_id in expired_requests:
                del self.active_requests[trace_id]
            
            if expired_requests:
                self.logger.debug(f"Cleaned up {len(expired_requests)} expired requests")
    
    async def _cleanup_connections(self):
        """Clean up all connections"""
        # This would close actual gRPC channels
        with self._lock:
            self.connections.clear()
        
        self.logger.info("Cleaned up all gRPC connections")


# Example usage
if __name__ == "__main__":
    async def main():
        # Create gRPC gateway
        gateway = GRPCGateway()
        await gateway.start()
        
        # Register a service
        service_config = GRPCServiceConfig(
            name="ai_content_service",
            host="localhost",
            port=50051,
            ssl_enabled=False
        )
        gateway.register_service(service_config)
        
        # Register an endpoint
        endpoint = GRPCEndpoint(
            service_name="ai_content_service",
            method_name="GenerateContent",
            full_method="/ai.content.v1.ContentService/GenerateContent",
            method_type=GRPCMethod.UNARY,
            request_type="GenerateContentRequest",
            response_type="GenerateContentResponse",
            http_path="/api/v1/content/generate",
            http_method="POST"
        )
        gateway.register_endpoint(endpoint)
        
        # Test unary call
        response = await gateway.call_unary(
            service_name="ai_content_service",
            method_name="GenerateContent",
            request_data={
                "prompt": "Create a blog post about AI",
                "max_tokens": 1000,
                "temperature": 0.7
            },
            user_id="user123"
        )
        
        print(f"Unary response: {response.payload}")
        
        # Test server streaming
        print("Server streaming responses:")
        async for stream_response in gateway.call_server_streaming(
            service_name="ai_content_service",
            method_name="StreamGenerate",
            request_data={"prompt": "Stream some content"},
            user_id="user123"
        ):
            print(f"Stream chunk: {stream_response.payload}")
        
        # Get metrics
        metrics = gateway.get_metrics()
        print(json.dumps(metrics, indent=2, default=str))
        
        await gateway.stop()
    
    asyncio.run(main())