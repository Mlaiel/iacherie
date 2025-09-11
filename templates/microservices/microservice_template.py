"""{{microservice_name}} Microservice Template for Ainflue Platform
{{microservice_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel, Field
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest

from core.config import get_settings
from core.database import get_async_session
from utils.exceptions import ServiceError, ValidationError
from monitoring.microservice_metrics import MicroserviceMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class ServiceStatus(Enum):
    """Service status enumeration"""
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPING = "stopping"


class MessageType(Enum):
    """Inter-service message types"""
    EVENT = "event"
    COMMAND = "command"
    QUERY = "query"
    RESPONSE = "response"


class ServiceMessage(BaseModel):
    """Inter-service message"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message ID")
    type: MessageType = Field(..., description="Message type")
    source_service: str = Field(..., description="Source service name")
    target_service: Optional[str] = Field(default=None, description="Target service name")
    operation: str = Field(..., description="Operation or event name")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracing")
    reply_to: Optional[str] = Field(default=None, description="Reply queue/topic")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    ttl: Optional[int] = Field(default=300, description="Time to live in seconds")
    retry_count: int = Field(default=0, description="Retry attempt count")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class ServiceConfig(BaseModel):
    """Microservice configuration"""
    name: str = Field(..., description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    port: int = Field(default=8000, description="Service port")
    host: str = Field(default="0.0.0.0", description="Service host")
    debug: bool = Field(default=False, description="Debug mode")
    workers: int = Field(default=1, description="Number of workers")
    enable_cors: bool = Field(default=True, description="Enable CORS")
    enable_gzip: bool = Field(default=True, description="Enable gzip compression")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    circuit_breaker_threshold: int = Field(default=5, description="Circuit breaker failure threshold")
    rate_limit: int = Field(default=1000, description="Rate limit per minute")
    dependencies: List[str] = Field(default_factory=list, description="Service dependencies")


class HealthStatus(BaseModel):
    """Health check status"""
    status: ServiceStatus = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    uptime: float = Field(..., description="Service uptime in seconds")
    dependencies: Dict[str, ServiceStatus] = Field(default_factory=dict, description="Dependency health status")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Service metrics")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional health details")


class {{microservice_name}}Service:
    """{{microservice_description}}
    
    Comprehensive microservice template providing:
    - RESTful API with FastAPI framework
    - Inter-service communication patterns
    - Health checks and monitoring
    - Circuit breaker pattern implementation
    - Rate limiting and throttling
    - Distributed tracing support
    - Message queue integration
    - Database connection management
    - Configuration management
    - Error handling and recovery
    - Metrics collection and export
    - Service discovery integration
    """
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.app = FastAPI(
            title=config.name,
            version=config.version,
            debug=config.debug
        )
        
        # Service state
        self.status = ServiceStatus.STARTING
        self.start_time = datetime.utcnow()
        self.metrics_collector = MicroserviceMetricsCollector(config.name)
        
        # External connections
        self.redis_client: Optional[redis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.message_handlers: Dict[str, Callable] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
        self._setup_event_handlers()
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        if self.config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        if self.config.enable_gzip:
            self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Add custom middleware
        @self.app.middleware("http")
        async def metrics_middleware(request: Request, call_next):
            start_time = datetime.utcnow()
            
            try:
                response = await call_next(request)
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Record metrics
                await self.metrics_collector.record_request_metrics(
                    method=request.method,
                    endpoint=str(request.url.path),
                    status_code=response.status_code,
                    execution_time=execution_time
                )
                
                return response
                
            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                await self.metrics_collector.record_request_metrics(
                    method=request.method,
                    endpoint=str(request.url.path),
                    status_code=500,
                    execution_time=execution_time
                )
                
                raise e
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health", response_model=HealthStatus)
        async def health_check():
            """Health check endpoint"""
            return await self._get_health_status()
        
        @self.app.get("/ready")
        async def readiness_check():
            """Readiness check endpoint"""
            if self.status == ServiceStatus.HEALTHY:
                return {"status": "ready"}
            else:
                raise HTTPException(status_code=503, detail="Service not ready")
        
        @self.app.get("/metrics")
        async def metrics_endpoint():
            """Prometheus metrics endpoint"""
            if self.config.enable_metrics:
                return Response(
                    content=generate_latest(),
                    media_type="text/plain"
                )
            else:
                raise HTTPException(status_code=404, detail="Metrics disabled")
        
        @self.app.get("/info")
        async def service_info():
            """Service information endpoint"""
            return {
                "name": self.config.name,
                "version": self.config.version,
                "status": self.status.value,
                "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
                "dependencies": self.config.dependencies,
                "config": self.config.dict()
            }
        
        # Add custom business logic routes here
        @self.app.post("/api/v1/process")
        async def process_request(request_data: Dict[str, Any]):
            """Main processing endpoint"""
            try:
                result = await self._process_business_logic(request_data)
                return {"success": True, "data": result}
            except Exception as e:
                logger.error(f"Processing failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _setup_event_handlers(self):
        """Setup application event handlers"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Application startup event"""
            try:
                await self._initialize_connections()
                await self._register_service()
                self.status = ServiceStatus.HEALTHY
                logger.info(f"Service {self.config.name} started successfully")
            except Exception as e:
                logger.error(f"Service startup failed: {str(e)}")
                self.status = ServiceStatus.UNHEALTHY
                raise
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Application shutdown event"""
            self.status = ServiceStatus.STOPPING
            await self._cleanup_connections()
            await self._deregister_service()
            logger.info(f"Service {self.config.name} stopped")
    
    async def _initialize_connections(self):
        """Initialize external connections"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
            # Initialize HTTP client
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
            logger.info("HTTP client initialized")
            
            # Initialize message queue subscriptions
            await self._setup_message_subscriptions()
            
        except Exception as e:
            logger.error(f"Failed to initialize connections: {str(e)}")
            raise
    
    async def _cleanup_connections(self):
        """Cleanup external connections"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.http_client:
                await self.http_client.aclose()
                
            logger.info("Connections cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def _get_health_status(self) -> HealthStatus:
        """Get comprehensive health status"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Check dependencies
        dependency_status = {}
        for dep in self.config.dependencies:
            try:
                status = await self._check_dependency_health(dep)
                dependency_status[dep] = status
            except Exception:
                dependency_status[dep] = ServiceStatus.UNHEALTHY
        
        # Determine overall status
        overall_status = self.status
        if any(status == ServiceStatus.UNHEALTHY for status in dependency_status.values()):
            overall_status = ServiceStatus.DEGRADED
        
        # Get service metrics
        metrics = await self.metrics_collector.get_current_metrics()
        
        return HealthStatus(
            status=overall_status,
            service=self.config.name,
            version=self.config.version,
            uptime=uptime,
            dependencies=dependency_status,
            metrics=metrics
        )
    
    async def _check_dependency_health(self, service_name: str) -> ServiceStatus:
        """Check health of a dependency service"""
        try:
            # This would typically use service discovery to find the service
            service_url = await self._get_service_url(service_name)
            
            if self.http_client:
                response = await self.http_client.get(f"{service_url}/health", timeout=5.0)
                
                if response.status_code == 200:
                    health_data = response.json()
                    return ServiceStatus(health_data.get("status", "unknown"))
                else:
                    return ServiceStatus.UNHEALTHY
            
            return ServiceStatus.UNKNOWN
            
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {str(e)}")
            return ServiceStatus.UNHEALTHY
    
    async def send_message(self, message: ServiceMessage) -> bool:
        """Send message to another service"""
        try:
            # Implement circuit breaker pattern
            if not await self._check_circuit_breaker(message.target_service):
                logger.warning(f"Circuit breaker open for {message.target_service}")
                return False
            
            # Serialize message
            message_data = message.json()
            
            # Send via message queue (Redis Streams in this example)
            if self.redis_client:
                stream_key = f"service:{message.target_service}:messages"
                await self.redis_client.xadd(stream_key, message_data)
                
                # Record successful send
                await self._record_circuit_breaker_success(message.target_service)
                
                logger.info(f"Message sent to {message.target_service}: {message.operation}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            await self._record_circuit_breaker_failure(message.target_service)
            return False
    
    async def _setup_message_subscriptions(self):
        """Setup message queue subscriptions"""
        if not self.redis_client:
            return
        
        # Create consumer group for this service
        stream_key = f"service:{self.config.name}:messages"
        group_name = f"{self.config.name}_group"
        
        try:
            await self.redis_client.xgroup_create(stream_key, group_name, id="0", mkstream=True)
        except Exception:
            # Group might already exist
            pass
        
        # Start message processing task
        asyncio.create_task(self._process_messages())
    
    async def _process_messages(self):
        """Process incoming messages"""
        if not self.redis_client:
            return
        
        stream_key = f"service:{self.config.name}:messages"
        group_name = f"{self.config.name}_group"
        consumer_name = f"{self.config.name}_{uuid.uuid4().hex[:8]}"
        
        while self.status in [ServiceStatus.STARTING, ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
            try:
                # Read messages from stream
                messages = await self.redis_client.xreadgroup(
                    group_name,
                    consumer_name,
                    {stream_key: ">"},
                    count=10,
                    block=1000
                )
                
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        try:
                            # Parse message
                            message_data = json.loads(fields.get('message', '{}'))
                            message = ServiceMessage(**message_data)
                            
                            # Process message
                            await self._handle_message(message)
                            
                            # Acknowledge message
                            await self.redis_client.xack(stream_key, group_name, msg_id)
                            
                        except Exception as e:
                            logger.error(f"Error processing message {msg_id}: {str(e)}")
                            # Could implement dead letter queue here
                
            except Exception as e:
                logger.error(f"Error in message processing loop: {str(e)}")
                await asyncio.sleep(5)
    
    async def _handle_message(self, message: ServiceMessage):
        """Handle incoming message"""
        handler = self.message_handlers.get(message.operation)
        
        if handler:
            try:
                await handler(message)
                logger.info(f"Processed message: {message.operation}")
            except Exception as e:
                logger.error(f"Message handler failed for {message.operation}: {str(e)}")
                
                # Implement retry logic if needed
                if message.retry_count < message.max_retries:
                    message.retry_count += 1
                    await self._retry_message(message)
        else:
            logger.warning(f"No handler found for operation: {message.operation}")
    
    def register_message_handler(self, operation: str, handler: Callable):
        """Register message handler for specific operation"""
        self.message_handlers[operation] = handler
        logger.info(f"Registered handler for operation: {operation}")
    
    async def _check_circuit_breaker(self, service: str) -> bool:
        """Check if circuit breaker allows request"""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = {
                "failures": 0,
                "last_failure": None,
                "state": "closed"  # closed, open, half-open
            }
        
        cb = self.circuit_breakers[service]
        
        if cb["state"] == "open":
            # Check if enough time has passed to try again
            if cb["last_failure"]:
                time_since_failure = (datetime.utcnow() - cb["last_failure"]).total_seconds()
                if time_since_failure > 60:  # 1 minute timeout
                    cb["state"] = "half-open"
                    return True
            return False
        
        return True
    
    async def _record_circuit_breaker_failure(self, service: str):
        """Record circuit breaker failure"""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = {
                "failures": 0,
                "last_failure": None,
                "state": "closed"
            }
        
        cb = self.circuit_breakers[service]
        cb["failures"] += 1
        cb["last_failure"] = datetime.utcnow()
        
        if cb["failures"] >= self.config.circuit_breaker_threshold:
            cb["state"] = "open"
            logger.warning(f"Circuit breaker opened for service: {service}")
    
    async def _record_circuit_breaker_success(self, service: str):
        """Record circuit breaker success"""
        if service in self.circuit_breakers:
            cb = self.circuit_breakers[service]
            cb["failures"] = 0
            cb["state"] = "closed"
    
    async def _process_business_logic(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process business logic - override in concrete implementation"""
        # This is where you would implement your specific business logic
        
        # Example: Call another service
        message = ServiceMessage(
            type=MessageType.COMMAND,
            source_service=self.config.name,
            target_service="data-processing-service",
            operation="process_data",
            payload=request_data
        )
        
        success = await self.send_message(message)
        
        return {
            "processed": True,
            "message_sent": success,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _register_service(self):
        """Register service with service discovery"""
        # This would integrate with service discovery like Consul, etcd, etc.
        logger.info(f"Service {self.config.name} registered")
    
    async def _deregister_service(self):
        """Deregister service from service discovery"""
        logger.info(f"Service {self.config.name} deregistered")
    
    async def _get_service_url(self, service_name: str) -> str:
        """Get service URL from service discovery"""
        # This would query service discovery for the service URL
        # For now, return a mock URL
        return f"http://{service_name}:8000"
    
    async def _retry_message(self, message: ServiceMessage):
        """Retry failed message"""
        # Implement exponential backoff
        delay = min(2 ** message.retry_count, 60)  # Max 60 seconds
        await asyncio.sleep(delay)
        
        # Resend message
        await self.send_message(message)
    
    def run(self):
        """Run the microservice"""
        import uvicorn
        
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            workers=self.config.workers
        )


# Example usage and service factory

def create_{{microservice_name|lower}}_service() -> {{microservice_name}}Service:
    """Factory function to create {{microservice_name}} service"""
    config = ServiceConfig(
        name="{{microservice_name|lower}}-service",
        version="1.0.0",
        port=8000,
        dependencies=["user-service", "notification-service"]
    )
    
    service = {{microservice_name}}Service(config)
    
    # Register custom message handlers
    async def handle_user_created(message: ServiceMessage):
        """Handle user created event"""
        user_data = message.payload
        logger.info(f"User created: {user_data.get('user_id')}")
        # Add business logic here
    
    async def handle_process_request(message: ServiceMessage):
        """Handle process request command"""
        request_data = message.payload
        logger.info(f"Processing request: {request_data}")
        # Add business logic here
    
    service.register_message_handler("user_created", handle_user_created)
    service.register_message_handler("process_request", handle_process_request)
    
    return service


if __name__ == "__main__":
    # Run the service
    service = create_{{microservice_name|lower}}_service()
    service.run()