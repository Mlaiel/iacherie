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

Base Microservice Class for IA Chérie Platform
===========================================

Enterprise-grade base microservice providing foundational patterns for:
- Service lifecycle management
- Health monitoring and readiness checks
- Metrics collection and observability
- Inter-service communication
- Configuration management
- Security integration
- Error handling and recovery
- Graceful shutdown handling

Author: Fahed Mlaiel (mlaiel@live.de)
Microservices Architect & Technical Lead
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Type
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import uuid
import signal
import sys

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import httpx
from pydantic import BaseModel, Field
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest

from .microservice_template import (
    ServiceStatus, 
    MessageType, 
    ServiceMessage, 
    ServiceConfig, 
    HealthStatus
)

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """Base service error"""
    pass


class ConfigurationError(ServiceError):
    """Configuration error"""
    pass


class CommunicationError(ServiceError):
    """Inter-service communication error"""
    pass


class HealthCheckError(ServiceError):
    """Health check error"""
    pass


class ServiceMetrics(BaseModel):
    """Service metrics model"""
    requests_total: int = 0
    requests_success: int = 0
    requests_failed: int = 0
    response_time_avg: float = 0.0
    response_time_p95: float = 0.0
    response_time_p99: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    circuit_breaker_trips: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class BaseMicroservice(ABC):
    """
    Abstract base class for all microservices in IA Chérie platform
    
    Provides enterprise-grade foundations including:
    - FastAPI application setup and configuration
    - Health monitoring and readiness checks
    - Metrics collection with Prometheus integration
    - Inter-service communication patterns
    - Circuit breaker implementation
    - Graceful shutdown handling
    - Security middleware integration
    - Configuration management
    - Error handling and recovery
    - Service discovery integration
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize base microservice"""
        self.config = config
        self.service_id = str(uuid.uuid4())
        self.start_time = datetime.utcnow()
        self.status = ServiceStatus.STARTING
        
        # Initialize FastAPI application
        self.app = FastAPI(
            title=config.name,
            version=config.version,
            debug=config.debug,
            description=f"Enterprise microservice: {config.name}"
        )
        
        # External connections
        self.redis_client: Optional[redis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        
        # Service state
        self.metrics = ServiceMetrics()
        self.message_handlers: Dict[str, Callable] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.shutdown_handlers: List[Callable] = []
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Setup application
        self._setup_middleware()
        self._setup_routes()
        self._setup_event_handlers()
        self._setup_signal_handlers()
        
        logger.info(f"Initialized {config.name} service with ID: {self.service_id}")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics collectors"""
        service_name = self.config.name.replace("-", "_")
        
        self.request_counter = Counter(
            f"{service_name}_requests_total",
            "Total requests processed",
            ["method", "endpoint", "status"]
        )
        
        self.request_histogram = Histogram(
            f"{service_name}_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"]
        )
        
        self.active_connections_gauge = Gauge(
            f"{service_name}_active_connections",
            "Active connections"
        )
        
        self.circuit_breaker_gauge = Gauge(
            f"{service_name}_circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=open, 2=half-open)",
            ["target_service"]
        )
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS middleware
        if self.config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # GZip compression
        if self.config.enable_gzip:
            self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Metrics and request tracking middleware
        @self.app.middleware("http")
        async def metrics_middleware(request: Request, call_next):
            start_time = datetime.utcnow()
            
            # Increment active connections
            self.active_connections_gauge.inc()
            
            try:
                response = await call_next(request)
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Record metrics
                self.request_counter.labels(
                    method=request.method,
                    endpoint=str(request.url.path),
                    status=response.status_code
                ).inc()
                
                self.request_histogram.labels(
                    method=request.method,
                    endpoint=str(request.url.path)
                ).observe(execution_time)
                
                # Update service metrics
                await self._update_service_metrics(
                    success=200 <= response.status_code < 400,
                    execution_time=execution_time
                )
                
                return response
                
            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                self.request_counter.labels(
                    method=request.method,
                    endpoint=str(request.url.path),
                    status=500
                ).inc()
                
                await self._update_service_metrics(
                    success=False,
                    execution_time=execution_time
                )
                
                raise e
            finally:
                # Decrement active connections
                self.active_connections_gauge.dec()
    
    def _setup_routes(self):
        """Setup standard microservice routes"""
        
        @self.app.get("/health", response_model=HealthStatus)
        async def health_check():
            """Comprehensive health check endpoint"""
            return await self.get_health_status()
        
        @self.app.get("/ready")
        async def readiness_check():
            """Kubernetes readiness probe endpoint"""
            if self.status == ServiceStatus.HEALTHY:
                return {"status": "ready", "service": self.config.name}
            else:
                raise HTTPException(status_code=503, detail="Service not ready")
        
        @self.app.get("/live")
        async def liveness_check():
            """Kubernetes liveness probe endpoint"""
            if self.status != ServiceStatus.STOPPING:
                return {"status": "alive", "service": self.config.name}
            else:
                raise HTTPException(status_code=503, detail="Service shutting down")
        
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
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            
            return {
                "service": self.config.name,
                "version": self.config.version,
                "service_id": self.service_id,
                "status": self.status.value,
                "uptime_seconds": uptime,
                "dependencies": self.config.dependencies,
                "metrics": self.metrics.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Register custom routes
        self.register_routes()
    
    def _setup_event_handlers(self):
        """Setup FastAPI event handlers"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Application startup event"""
            try:
                logger.info(f"Starting {self.config.name} service...")
                
                # Initialize connections
                await self.initialize_connections()
                
                # Initialize service-specific components
                await self.initialize_service()
                
                # Register with service discovery
                await self.register_service()
                
                # Start background tasks
                await self.start_background_tasks()
                
                self.status = ServiceStatus.HEALTHY
                logger.info(f"Service {self.config.name} started successfully")
                
            except Exception as e:
                logger.error(f"Service startup failed: {str(e)}")
                self.status = ServiceStatus.UNHEALTHY
                raise
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Application shutdown event"""
            logger.info(f"Shutting down {self.config.name} service...")
            self.status = ServiceStatus.STOPPING
            
            try:
                # Execute custom shutdown handlers
                for handler in self.shutdown_handlers:
                    try:
                        await handler()
                    except Exception as e:
                        logger.error(f"Shutdown handler failed: {str(e)}")
                
                # Stop background tasks
                await self.stop_background_tasks()
                
                # Cleanup service-specific components
                await self.cleanup_service()
                
                # Deregister from service discovery
                await self.deregister_service()
                
                # Cleanup connections
                await self.cleanup_connections()
                
                logger.info(f"Service {self.config.name} stopped successfully")
                
            except Exception as e:
                logger.error(f"Service shutdown error: {str(e)}")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self._graceful_shutdown())
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def _graceful_shutdown(self):
        """Handle graceful shutdown"""
        self.status = ServiceStatus.STOPPING
        
        # Allow current requests to complete
        await asyncio.sleep(5)
        
        # Force shutdown if needed
        sys.exit(0)
    
    async def initialize_connections(self):
        """Initialize external connections"""
        try:
            # Initialize Redis connection
            if hasattr(self, '_redis_config'):
                self.redis_client = redis.Redis(
                    host=self._redis_config.get('host', 'localhost'),
                    port=self._redis_config.get('port', 6379),
                    password=self._redis_config.get('password'),
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info("Redis connection established")
            
            # Initialize HTTP client
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(
                    max_keepalive_connections=20, 
                    max_connections=100
                )
            )
            logger.info("HTTP client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize connections: {str(e)}")
            raise CommunicationError(f"Connection initialization failed: {str(e)}")
    
    async def cleanup_connections(self):
        """Cleanup external connections"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            
            if self.http_client:
                await self.http_client.aclose()
                logger.info("HTTP client closed")
                
        except Exception as e:
            logger.error(f"Error during connection cleanup: {str(e)}")
    
    async def get_health_status(self) -> HealthStatus:
        """Get comprehensive health status"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Check dependencies
        dependency_status = {}
        for dep in self.config.dependencies:
            try:
                status = await self.check_dependency_health(dep)
                dependency_status[dep] = status
            except Exception:
                dependency_status[dep] = ServiceStatus.UNHEALTHY
        
        # Determine overall status
        overall_status = self.status
        unhealthy_deps = [
            dep for dep, status in dependency_status.items() 
            if status == ServiceStatus.UNHEALTHY
        ]
        
        if unhealthy_deps:
            overall_status = ServiceStatus.DEGRADED
            logger.warning(f"Unhealthy dependencies: {unhealthy_deps}")
        
        return HealthStatus(
            status=overall_status,
            service=self.config.name,
            version=self.config.version,
            uptime=uptime,
            dependencies=dependency_status,
            metrics=self.metrics.dict(),
            details={
                "service_id": self.service_id,
                "circuit_breakers": self._get_circuit_breaker_status(),
                "memory_info": await self._get_memory_info(),
                "active_tasks": len([t for t in asyncio.all_tasks() if not t.done()])
            }
        )
    
    async def check_dependency_health(self, service_name: str) -> ServiceStatus:
        """Check health of a dependency service"""
        try:
            service_url = await self.get_service_url(service_name)
            
            if self.http_client:
                response = await self.http_client.get(
                    f"{service_url}/health", 
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    health_data = response.json()
                    return ServiceStatus(health_data.get("status", "unknown"))
                else:
                    return ServiceStatus.UNHEALTHY
            
            return ServiceStatus.UNHEALTHY
            
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {str(e)}")
            return ServiceStatus.UNHEALTHY
    
    async def _update_service_metrics(self, success: bool, execution_time: float):
        """Update internal service metrics"""
        self.metrics.requests_total += 1
        
        if success:
            self.metrics.requests_success += 1
        else:
            self.metrics.requests_failed += 1
        
        # Update response time averages (simple moving average)
        current_avg = self.metrics.response_time_avg
        total_requests = self.metrics.requests_total
        
        self.metrics.response_time_avg = (
            (current_avg * (total_requests - 1) + execution_time) / total_requests
        )
        
        self.metrics.last_updated = datetime.utcnow()
    
    def _get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for all services"""
        return {
            service: {
                "state": cb["state"],
                "failures": cb["failures"],
                "last_failure": cb["last_failure"].isoformat() if cb["last_failure"] else None
            }
            for service, cb in self.circuit_breakers.items()
        }
    
    async def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def add_shutdown_handler(self, handler: Callable):
        """Add custom shutdown handler"""
        self.shutdown_handlers.append(handler)
        logger.info(f"Added shutdown handler: {handler.__name__}")
    
    # Abstract methods to be implemented by concrete services
    
    @abstractmethod
    async def initialize_service(self):
        """Initialize service-specific components"""
        pass
    
    @abstractmethod
    async def cleanup_service(self):
        """Cleanup service-specific components"""
        pass
    
    @abstractmethod
    def register_routes(self):
        """Register service-specific routes"""
        pass
    
    @abstractmethod
    async def register_service(self):
        """Register service with service discovery"""
        pass
    
    @abstractmethod
    async def deregister_service(self):
        """Deregister service from service discovery"""
        pass
    
    @abstractmethod
    async def get_service_url(self, service_name: str) -> str:
        """Get service URL from service discovery"""
        pass
    
    @abstractmethod
    async def start_background_tasks(self):
        """Start service-specific background tasks"""
        pass
    
    @abstractmethod
    async def stop_background_tasks(self):
        """Stop service-specific background tasks"""
        pass
    
    def run(self, **kwargs):
        """Run the microservice"""
        import uvicorn
        
        run_config = {
            "app": self.app,
            "host": self.config.host,
            "port": self.config.port,
            "workers": 1,  # Use 1 worker for async services
            "loop": "asyncio",
            "access_log": True,
            "log_level": "info" if not self.config.debug else "debug"
        }
        
        run_config.update(kwargs)
        
        logger.info(f"Starting {self.config.name} on {self.config.host}:{self.config.port}")
        uvicorn.run(**run_config)


class SimpleBaseMicroservice(BaseMicroservice):
    """
    Simple implementation of BaseMicroservice for basic services
    """
    
    async def initialize_service(self):
        """Default service initialization"""
        logger.info(f"Initializing {self.config.name} service")
    
    async def cleanup_service(self):
        """Default service cleanup"""
        logger.info(f"Cleaning up {self.config.name} service")
    
    def register_routes(self):
        """Default route registration"""
        # No additional routes by default
        pass
    
    async def register_service(self):
        """Default service registration"""
        logger.info(f"Registering {self.config.name} with service discovery")
    
    async def deregister_service(self):
        """Default service deregistration"""
        logger.info(f"Deregistering {self.config.name} from service discovery")
    
    async def get_service_url(self, service_name: str) -> str:
        """Default service URL resolution"""
        # Simple hostname-based resolution
        return f"http://{service_name}:8000"
    
    async def start_background_tasks(self):
        """Default background tasks start"""
        logger.info(f"Starting background tasks for {self.config.name}")
    
    async def stop_background_tasks(self):
        """Default background tasks stop"""
        logger.info(f"Stopping background tasks for {self.config.name}")