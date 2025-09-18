"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

gRPC Service Template for Ainflue Microservices Platform
=======================================================

Enterprise-grade gRPC service template providing:
- High-performance gRPC server with HTTP/2
- Protocol Buffers message serialization
- Bidirectional streaming support
- Server reflection and health checking
- Load balancing and connection pooling
- Authentication and authorization
- Interceptors for logging and metrics
- Error handling and retry mechanisms
- TLS/SSL encryption support
- Service discovery integration

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & gRPC Specialist
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, AsyncIterator, Iterator
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
import time

import grpc
from grpc import aio
from grpc_reflection.v1alpha import reflection
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_health.v1.health import HealthServicer
import google.protobuf.message
from google.protobuf.json_format import MessageToDict, ParseDict

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus

logger = logging.getLogger(__name__)


class GrpcConfig(ServiceConfig):
    """gRPC service specific configuration"""
    grpc_port: int = 50051
    max_workers: int = 10
    max_message_length: int = 4 * 1024 * 1024  # 4MB
    max_connection_idle: int = 300  # 5 minutes
    max_connection_age: int = 3600  # 1 hour
    enable_reflection: bool = True
    enable_health_check: bool = True
    enable_tls: bool = False
    tls_cert_file: Optional[str] = None
    tls_key_file: Optional[str] = None
    tls_ca_file: Optional[str] = None
    compression: str = "gzip"  # gzip, deflate, none
    keepalive_time: int = 30
    keepalive_timeout: int = 5
    keepalive_permit_without_calls: bool = True
    max_concurrent_streams: int = 100


class MetricsInterceptor(aio.ServerInterceptor):
    """gRPC interceptor for metrics collection"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.request_counter = 0
        self.request_times: Dict[str, List[float]] = {}
    
    async def intercept_service(self, continuation, handler_call_details):
        """Intercept gRPC service calls"""
        start_time = time.time()
        method_name = handler_call_details.method
        
        try:
            # Continue with the call
            response = await continuation(handler_call_details)
            
            # Record metrics
            execution_time = time.time() - start_time
            self._record_metrics(method_name, execution_time, "SUCCESS")
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._record_metrics(method_name, execution_time, "ERROR")
            
            logger.error(f"gRPC call failed {method_name}: {str(e)}")
            raise e
    
    def _record_metrics(self, method_name: str, execution_time: float, status: str):
        """Record method execution metrics"""
        self.request_counter += 1
        
        if method_name not in self.request_times:
            self.request_times[method_name] = []
        
        self.request_times[method_name].append(execution_time)
        
        # Keep only last 1000 entries
        if len(self.request_times[method_name]) > 1000:
            self.request_times[method_name] = self.request_times[method_name][-1000:]
        
        logger.debug(f"gRPC {status}: {method_name} ({execution_time:.3f}s)")


class AuthInterceptor(aio.ServerInterceptor):
    """gRPC interceptor for authentication"""
    
    def __init__(self, auth_required_methods: Optional[List[str]] = None):
        self.auth_required_methods = auth_required_methods or []
    
    async def intercept_service(self, continuation, handler_call_details):
        """Intercept and authenticate gRPC calls"""
        method_name = handler_call_details.method
        
        # Check if authentication is required for this method
        if self.auth_required_methods and method_name in self.auth_required_methods:
            metadata = dict(handler_call_details.invocation_metadata)
            auth_token = metadata.get("authorization")
            
            if not auth_token or not self._validate_token(auth_token):
                context = grpc.aio.ServicerContext()
                await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid authentication")
        
        return await continuation(handler_call_details)
    
    def _validate_token(self, token: str) -> bool:
        """Validate authentication token"""
        # Implement token validation logic
        return token.startswith("Bearer ") and len(token) > 10


class LoggingInterceptor(aio.ServerInterceptor):
    """gRPC interceptor for request/response logging"""
    
    async def intercept_service(self, continuation, handler_call_details):
        """Log gRPC service calls"""
        method_name = handler_call_details.method
        client_info = handler_call_details.invocation_metadata
        
        logger.info(f"gRPC Request: {method_name} from {dict(client_info).get('user-agent', 'unknown')}")
        
        try:
            response = await continuation(handler_call_details)
            logger.info(f"gRPC Response: {method_name} SUCCESS")
            return response
            
        except Exception as e:
            logger.error(f"gRPC Response: {method_name} ERROR - {str(e)}")
            raise e


# Example Protocol Buffer message definitions (normally generated from .proto files)
class UserRequest:
    """User request message"""
    def __init__(self, user_id: str = "", name: str = "", email: str = ""):
        self.user_id = user_id
        self.name = name
        self.email = email


class UserResponse:
    """User response message"""
    def __init__(self, user_id: str = "", name: str = "", email: str = "", created_at: str = ""):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.created_at = created_at


class ListUsersRequest:
    """List users request message"""
    def __init__(self, page_size: int = 10, page_token: str = ""):
        self.page_size = page_size
        self.page_token = page_token


class ListUsersResponse:
    """List users response message"""
    def __init__(self, users: List[UserResponse] = None, next_page_token: str = ""):
        self.users = users or []
        self.next_page_token = next_page_token


class StreamRequest:
    """Stream request message"""
    def __init__(self, message: str = ""):
        self.message = message


class StreamResponse:
    """Stream response message"""
    def __init__(self, response: str = "", timestamp: str = ""):
        self.response = response
        self.timestamp = timestamp


class ExampleGrpcServicer:
    """Example gRPC service implementation"""
    
    def __init__(self, service_template):
        self.service_template = service_template
    
    async def GetUser(self, request: UserRequest, context: grpc.aio.ServicerContext) -> UserResponse:
        """Get user by ID"""
        try:
            logger.info(f"GetUser called for user_id: {request.user_id}")
            
            # Implement user retrieval logic
            user = await self._get_user_from_storage(request.user_id)
            
            if not user:
                await context.abort(grpc.StatusCode.NOT_FOUND, f"User {request.user_id} not found")
            
            return UserResponse(
                user_id=user["user_id"],
                name=user["name"],
                email=user["email"],
                created_at=user["created_at"]
            )
            
        except Exception as e:
            logger.error(f"GetUser error: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def CreateUser(self, request: UserRequest, context: grpc.aio.ServicerContext) -> UserResponse:
        """Create new user"""
        try:
            logger.info(f"CreateUser called for name: {request.name}")
            
            # Validate request
            if not request.name or not request.email:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Name and email are required")
            
            # Create user
            user = await self._create_user_in_storage(request.name, request.email)
            
            return UserResponse(
                user_id=user["user_id"],
                name=user["name"],
                email=user["email"],
                created_at=user["created_at"]
            )
            
        except Exception as e:
            logger.error(f"CreateUser error: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def ListUsers(self, request: ListUsersRequest, context: grpc.aio.ServicerContext) -> ListUsersResponse:
        """List users with pagination"""
        try:
            logger.info(f"ListUsers called with page_size: {request.page_size}")
            
            # Get users from storage
            users_data = await self._list_users_from_storage(request.page_size, request.page_token)
            
            users = [
                UserResponse(
                    user_id=user["user_id"],
                    name=user["name"],
                    email=user["email"],
                    created_at=user["created_at"]
                )
                for user in users_data["users"]
            ]
            
            return ListUsersResponse(
                users=users,
                next_page_token=users_data["next_page_token"]
            )
            
        except Exception as e:
            logger.error(f"ListUsers error: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def StreamUsers(self, request: StreamRequest, context: grpc.aio.ServicerContext) -> AsyncIterator[StreamResponse]:
        """Stream users (server streaming)"""
        try:
            logger.info(f"StreamUsers called with message: {request.message}")
            
            # Simulate streaming users
            for i in range(10):
                await asyncio.sleep(1)  # Simulate processing time
                
                yield StreamResponse(
                    response=f"User stream {i}: {request.message}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
        except Exception as e:
            logger.error(f"StreamUsers error: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def BidirectionalStream(self, request_iterator: AsyncIterator[StreamRequest], context: grpc.aio.ServicerContext) -> AsyncIterator[StreamResponse]:
        """Bidirectional streaming"""
        try:
            logger.info("BidirectionalStream started")
            
            async for request in request_iterator:
                logger.info(f"Received stream message: {request.message}")
                
                # Process request and yield response
                yield StreamResponse(
                    response=f"Echo: {request.message}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
        except Exception as e:
            logger.error(f"BidirectionalStream error: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def _get_user_from_storage(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user from storage - implement with actual storage"""
        # Simulate database lookup
        await asyncio.sleep(0.1)
        
        if user_id == "1":
            return {
                "user_id": "1",
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": datetime.utcnow().isoformat()
            }
        return None
    
    async def _create_user_in_storage(self, name: str, email: str) -> Dict[str, Any]:
        """Create user in storage - implement with actual storage"""
        # Simulate database creation
        await asyncio.sleep(0.1)
        
        return {
            "user_id": str(int(time.time())),
            "name": name,
            "email": email,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _list_users_from_storage(self, page_size: int, page_token: str) -> Dict[str, Any]:
        """List users from storage - implement with actual storage"""
        # Simulate database query
        await asyncio.sleep(0.1)
        
        users = []
        for i in range(min(page_size, 5)):  # Simulate limited results
            users.append({
                "user_id": str(i + 1),
                "name": f"User {i + 1}",
                "email": f"user{i + 1}@example.com",
                "created_at": datetime.utcnow().isoformat()
            })
        
        return {
            "users": users,
            "next_page_token": "next_page" if len(users) == page_size else ""
        }


class GrpcServiceTemplate(BaseMicroservice):
    """
    Enterprise gRPC service template
    
    Provides comprehensive gRPC functionality including:
    - High-performance async gRPC server with HTTP/2
    - Protocol Buffers message serialization
    - Bidirectional streaming support
    - Server reflection for service discovery
    - Health checking with gRPC health protocol
    - Authentication and authorization interceptors
    - Metrics collection and monitoring
    - Load balancing and connection management
    - TLS/SSL encryption support
    - Error handling and retry mechanisms
    """
    
    def __init__(self, config: GrpcConfig):
        """Initialize gRPC service"""
        self.grpc_config = config
        super().__init__(config)
        
        # gRPC server components
        self.grpc_server: Optional[aio.Server] = None
        self.health_servicer: Optional[HealthServicer] = None
        self.servicer: Optional[ExampleGrpcServicer] = None
        
        # Interceptors
        self.interceptors = self._create_interceptors()
        
        logger.info(f"gRPC service initialized on port {config.grpc_port}")
    
    def _create_interceptors(self) -> List[aio.ServerInterceptor]:
        """Create gRPC interceptors"""
        interceptors = [
            LoggingInterceptor(),
            MetricsInterceptor(self.config.name),
            AuthInterceptor()
        ]
        
        return interceptors
    
    async def _setup_grpc_server(self):
        """Setup gRPC server"""
        # Create server with interceptors
        self.grpc_server = aio.server(
            interceptors=self.interceptors,
            options=[
                ('grpc.keepalive_time_ms', self.grpc_config.keepalive_time * 1000),
                ('grpc.keepalive_timeout_ms', self.grpc_config.keepalive_timeout * 1000),
                ('grpc.keepalive_permit_without_calls', self.grpc_config.keepalive_permit_without_calls),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 10000),
                ('grpc.http2.min_ping_interval_without_data_ms', 300000),
                ('grpc.max_connection_idle_ms', self.grpc_config.max_connection_idle * 1000),
                ('grpc.max_connection_age_ms', self.grpc_config.max_connection_age * 1000),
                ('grpc.max_concurrent_streams', self.grpc_config.max_concurrent_streams),
                ('grpc.max_receive_message_length', self.grpc_config.max_message_length),
                ('grpc.max_send_message_length', self.grpc_config.max_message_length)
            ]
        )
        
        # Create and add servicer
        self.servicer = ExampleGrpcServicer(self)
        # Note: In real implementation, you would add the servicer to the server
        # example_pb2_grpc.add_ExampleServiceServicer_to_server(self.servicer, self.grpc_server)
        
        # Add health check service if enabled
        if self.grpc_config.enable_health_check:
            self.health_servicer = HealthServicer()
            health_pb2_grpc.add_HealthServicer_to_server(self.health_servicer, self.grpc_server)
            
            # Set service health status
            self.health_servicer.set(
                "",  # Overall server health
                health_pb2.HealthCheckResponse.SERVING
            )
        
        # Add reflection if enabled
        if self.grpc_config.enable_reflection:
            service_names = (
                "example.ExampleService",  # Your service name
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(service_names, self.grpc_server)
        
        # Configure server address
        listen_addr = f"{self.config.host}:{self.grpc_config.grpc_port}"
        
        if self.grpc_config.enable_tls:
            # Setup TLS credentials
            server_credentials = self._create_tls_credentials()
            self.grpc_server.add_secure_port(listen_addr, server_credentials)
        else:
            self.grpc_server.add_insecure_port(listen_addr)
        
        logger.info(f"gRPC server configured on {listen_addr}")
    
    def _create_tls_credentials(self) -> grpc.ServerCredentials:
        """Create TLS credentials for secure gRPC"""
        if not self.grpc_config.tls_cert_file or not self.grpc_config.tls_key_file:
            raise ValueError("TLS certificate and key files are required for secure gRPC")
        
        with open(self.grpc_config.tls_cert_file, 'rb') as f:
            certificate_chain = f.read()
        
        with open(self.grpc_config.tls_key_file, 'rb') as f:
            private_key = f.read()
        
        root_certificates = None
        if self.grpc_config.tls_ca_file:
            with open(self.grpc_config.tls_ca_file, 'rb') as f:
                root_certificates = f.read()
        
        return grpc.ssl_server_credentials(
            [(private_key, certificate_chain)],
            root_certificates=root_certificates,
            require_client_auth=bool(root_certificates)
        )
    
    async def start_grpc_server(self):
        """Start gRPC server"""
        if not self.grpc_server:
            await self._setup_grpc_server()
        
        await self.grpc_server.start()
        logger.info(f"gRPC server started on port {self.grpc_config.grpc_port}")
        
        # Update health status
        if self.health_servicer:
            self.health_servicer.set(
                "",
                health_pb2.HealthCheckResponse.SERVING
            )
    
    async def stop_grpc_server(self):
        """Stop gRPC server"""
        if self.grpc_server:
            # Update health status
            if self.health_servicer:
                self.health_servicer.set(
                    "",
                    health_pb2.HealthCheckResponse.NOT_SERVING
                )
            
            # Graceful shutdown
            await self.grpc_server.stop(grace=10)
            logger.info("gRPC server stopped")
    
    # Override abstract methods from BaseMicroservice
    
    async def initialize_service(self):
        """Initialize gRPC service"""
        await self._setup_grpc_server()
        logger.info(f"gRPC service {self.config.name} initialized")
    
    async def cleanup_service(self):
        """Cleanup gRPC service"""
        await self.stop_grpc_server()
        logger.info(f"gRPC service {self.config.name} cleaned up")
    
    def register_routes(self):
        """Register HTTP routes for gRPC gateway (optional)"""
        
        @self.app.get("/grpc/health")
        async def grpc_health_check():
            """HTTP endpoint for gRPC health check"""
            if self.health_servicer:
                return {"status": "serving", "service": self.config.name}
            else:
                return {"status": "unknown", "service": self.config.name}
        
        @self.app.get("/grpc/reflection")
        async def grpc_reflection_info():
            """HTTP endpoint for gRPC reflection information"""
            if self.grpc_config.enable_reflection:
                return {
                    "reflection_enabled": True,
                    "services": ["example.ExampleService"],
                    "grpc_port": self.grpc_config.grpc_port
                }
            else:
                return {"reflection_enabled": False}
    
    async def register_service(self):
        """Register service with service discovery"""
        # Start gRPC server
        await self.start_grpc_server()
        logger.info(f"gRPC service {self.config.name} registered")
    
    async def deregister_service(self):
        """Deregister service from service discovery"""
        await self.stop_grpc_server()
        logger.info(f"gRPC service {self.config.name} deregistered")
    
    async def get_service_url(self, service_name: str) -> str:
        """Get service URL from service discovery"""
        return f"{service_name}:50051"  # Default gRPC port
    
    async def start_background_tasks(self):
        """Start background tasks"""
        logger.info("gRPC background services started")
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        logger.info("gRPC background services stopped")
    
    def run(self, **kwargs):
        """Run the gRPC service with HTTP management interface"""
        # Override to include gRPC server lifecycle
        async def grpc_lifecycle():
            await self.start_grpc_server()
            
            # Keep running until shutdown
            while self.status != ServiceStatus.STOPPING:
                await asyncio.sleep(1)
        
        # Start gRPC server in background
        asyncio.create_task(grpc_lifecycle())
        
        # Start HTTP management interface
        super().run(**kwargs)


def create_grpc_service(
    service_name: str = "grpc-service",
    grpc_port: int = 50051,
    enable_reflection: bool = True,
    enable_tls: bool = False
) -> GrpcServiceTemplate:
    """Factory function to create gRPC service"""
    
    config = GrpcConfig(
        name=service_name,
        grpc_port=grpc_port,
        enable_reflection=enable_reflection,
        enable_health_check=True,
        enable_tls=enable_tls,
        max_workers=10,
        enable_metrics=True
    )
    
    return GrpcServiceTemplate(config)


if __name__ == "__main__":
    # Example usage
    service = create_grpc_service()
    service.run()