"""Reports Module Index
===================

Central entry point and orchestration layer for the ultra-advanced enterprise reporting
system of the IA Influencer Agent platform. Provides intelligent routing, service discovery,
and comprehensive API management for all reporting operations with enterprise-grade
reliability, security, and performance optimization.

Core Responsibilities:
- Service orchestration and dependency injection for reporting components
- Central configuration management with environment-specific settings
- API gateway and routing for all reporting endpoints
- Performance monitoring and metrics collection with real-time analytics
- Security enforcement and access control for all reporting operations
- Error handling and circuit breaker patterns for system resilience
- Caching layer management for optimized performance
- Background task coordination and queue management
- Health checks and system diagnostics for operational excellence

Advanced Features:
- Intelligent service mesh integration with automatic load balancing
- Real-time monitoring with Prometheus metrics and Grafana dashboards
- Advanced caching strategies with Redis cluster and CDN integration
- Comprehensive logging and tracing with structured logging and APM
- Circuit breaker patterns with automatic failover and recovery
- Rate limiting and throttling for API protection and fair usage
- Multi-tenant isolation with namespace-based resource allocation
- Automated scaling based on demand patterns and resource utilization
- Security scanning and vulnerability assessment with real-time alerts
- Compliance monitoring and audit trail management for regulatory requirements

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Legal Warning: This code and concept are the exclusive property of Fahed Mlaiel.
Any unauthorized use without explicit written permission will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

import asyncio
import logging
import warnings
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import threading
from contextlib import asynccontextmanager
from functools import wraps, lru_cache

# FastAPI and ASGI
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

# Database and ORM
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncSessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select

# Monitoring and Observability
try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server, generate_latest
    from prometheus_fastapi_instrumentator import Instrumentator
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    warnings.warn("Monitoring libraries not available. Install prometheus_client for metrics.")

# Caching
try:
    import redis.asyncio as redis
    from cachetools import TTLCache, LRUCache
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False
    warnings.warn("Caching libraries not available. Install redis for advanced caching.")

# Rate Limiting
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    warnings.warn("Rate limiting library not available. Install slowapi for API protection.")

# Circuit Breaker
try:
    from circuitbreaker import circuit
    CIRCUIT_BREAKER_AVAILABLE = True
except ImportError:
    CIRCUIT_BREAKER_AVAILABLE = False
    warnings.warn("Circuit breaker library not available. Install circuitbreaker for resilience.")

# Configuration Management
from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings as PydanticSettings

# Import reporting modules
from .generators import (
    ReportGenerator, PerformanceReportGenerator, ContentReportGenerator,
    ProtectionReportGenerator, RevenueReportGenerator, ComplianceReportGenerator,
    create_report_generator, ReportType, ReportConfiguration
)
from .analytics import (
    AnalyticsEngine, PerformanceAnalytics, ContentAnalytics,
    ProtectionAnalytics, PlatformAnalytics, RevenueAnalytics
)
from .formatters import (
    ReportFormatter, PDFFormatter, ExcelFormatter, JSONFormatter,
    CSVFormatter, HTMLFormatter
)
from .schedulers import (
    ReportScheduler, AutomatedReportScheduler, CronReportScheduler,
    RealTimeReportScheduler, ScheduleType, ScheduleConfiguration
)
from .aggregators import (
    DataAggregator, PerformanceAggregator, ContentAggregator,
    RevenueAggregator, MetricsAggregator
)
from .visualizers import (
    ChartGenerator, GraphVisualizer, DashboardVisualizer,
    MetricsVisualizer, TrendVisualizer
)
from .exporters import (
    ReportExporter, EmailExporter, CloudStorageExporter,
    APIExporter, DatabaseExporter
)
from .templates import (
    ReportTemplate, ExecutiveTemplate, TechnicalTemplate,
    ComplianceTemplate, FinancialTemplate
)
from .processors import (
    ReportProcessor, DataProcessor, MetricsProcessor,
    InsightsProcessor, IntelligenceProcessor
)

logger = logging.getLogger(__name__)

# Prometheus Metrics (if available)
if MONITORING_AVAILABLE:
    request_count = Counter('reports_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
    request_duration = Histogram('reports_request_duration_seconds', 'HTTP request duration')
    active_reports = Gauge('reports_active_generations', 'Number of active report generations')
    error_count = Counter('reports_errors_total', 'Total errors', ['error_type', 'component'])
    cache_hits = Counter('reports_cache_hits_total', 'Cache hits', ['cache_type'])
    cache_misses = Counter('reports_cache_misses_total', 'Cache misses', ['cache_type'])


class ServiceStatus(Enum):
    """Service status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


class ComponentType(Enum):
    """Component type enumeration."""

    GENERATOR = "generator"
    ANALYTICS = "analytics"
    FORMATTER = "formatter"
    SCHEDULER = "scheduler"
    AGGREGATOR = "aggregator"
    VISUALIZER = "visualizer"
    EXPORTER = "exporter"
    TEMPLATE = "template"
    PROCESSOR = "processor"


@dataclass
class ServiceConfig:
    """Service configuration dataclass."""
    name: str
    version: str = "2.0.0"
    environment: str = "production"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    database_url: str = ""
    redis_url: str = ""
    secret_key: str = ""
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit: str = "1000/minute"
    cache_ttl: int = 3600
    monitoring_enabled: bool = True
    security_enabled: bool = True


class ReportsSettings(PydanticSettings):
    """Reports service settings with environment variable support."""
    
    # Basic Settings
    app_name: str = Field(default="IA Influencer Agent - Reports Service", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    environment: str = Field(default="production", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # Database Settings
    database_url: str = Field(default="postgresql+asyncpg://localhost/reports", env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")
    
    # Security Settings
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=1440, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS Settings
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Rate Limiting
    rate_limit_default: str = Field(default="1000/minute", env="RATE_LIMIT_DEFAULT")
    rate_limit_burst: str = Field(default="2000/minute", env="RATE_LIMIT_BURST")
    
    # Caching
    cache_default_ttl: int = Field(default=3600, env="CACHE_DEFAULT_TTL")
    cache_max_size: int = Field(default=10000, env="CACHE_MAX_SIZE")
    
    # Monitoring
    monitoring_enabled: bool = Field(default=True, env="MONITORING_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class ReportsServiceManager:
    """
    Central service manager for the reports module.
    
    Manages all reporting components, handles service lifecycle,
    provides dependency injection, and ensures system reliability.
    """
    
    def __init__(self, settings: ReportsSettings):
        self.settings = settings
        self.status = ServiceStatus.HEALTHY
        self.components: Dict[str, Any] = {}
        self.health_checks: Dict[str, Callable] = {}
        self.startup_tasks: List[Callable] = []
        self.shutdown_tasks: List[Callable] = []
        
        # Initialize components
        self._redis_pool: Optional[redis.Redis] = None
        self._db_engine = None
        self._session_maker = None
        self._cache: Optional[Union[TTLCache, LRUCache]] = None
        
        # Service registry
        self._service_registry: Dict[str, Any] = {}
        
        # Performance metrics
        self._metrics = {
            "requests_processed": 0,
            "errors_encountered": 0,
            "avg_response_time": 0.0,
            "active_sessions": 0,
            "cache_hit_rate": 0.0
        }
        
        logger.info(f"ReportsServiceManager initialized for environment: {settings.environment}")
    
    async def initialize(self) -> None:
        """Initialize all service components."""
        try:
            logger.info("Initializing Reports Service components...")
            
            # Initialize database
            await self._initialize_database()
            
            # Initialize cache
            await self._initialize_cache()
            
            # Initialize Redis
            if CACHING_AVAILABLE:
                await self._initialize_redis()
            
            # Initialize monitoring
            if MONITORING_AVAILABLE and self.settings.monitoring_enabled:
                await self._initialize_monitoring()
            
            # Register components
            await self._register_components()
            
            # Run startup tasks
            await self._run_startup_tasks()
            
            self.status = ServiceStatus.HEALTHY
            logger.info("Reports Service initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Reports Service: {e}")
            self.status = ServiceStatus.UNHEALTHY
            raise
    
    async def _initialize_database(self) -> None:
        """Initialize database connection and session factory."""
        try:
            self._db_engine = create_async_engine(
                self.settings.database_url,
                pool_size=self.settings.database_pool_size,
                max_overflow=self.settings.database_max_overflow,
                echo=self.settings.debug
            )
            
            self._session_maker = AsyncSessionmaker(
                self._db_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self._session_maker() as session:
                await session.execute(text("SELECT 1"))
            
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _initialize_cache(self) -> None:
        """Initialize local caching system."""
        try:
            self._cache = TTLCache(
                maxsize=self.settings.cache_max_size,
                ttl=self.settings.cache_default_ttl
            )
            
            logger.info("Local cache initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection pool."""
        try:
            self._redis_pool = redis.from_url(
                self.settings.redis_url,
                max_connections=self.settings.redis_pool_size,
                decode_responses=True
            )
            
            # Test connection
            await self._redis_pool.ping()
            
            logger.info("Redis connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def _initialize_monitoring(self) -> None:
        """Initialize monitoring and metrics collection."""
        try:
            # Start Prometheus metrics server
            start_http_server(self.settings.metrics_port)
            
            logger.info(f"Monitoring initialized on port {self.settings.metrics_port}")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {e}")
            raise
    
    async def _register_components(self) -> None:
        """Register all reporting components in the service registry."""
        try:
            # Register generators
            self._service_registry["generators"] = {
                "performance": PerformanceReportGenerator,
                "content": ContentReportGenerator,
                "protection": ProtectionReportGenerator,
                "revenue": RevenueReportGenerator,
                "compliance": ComplianceReportGenerator
            }
            
            # Register analytics engines
            self._service_registry["analytics"] = {
                "performance": PerformanceAnalytics,
                "content": ContentAnalytics,
                "protection": ProtectionAnalytics,
                "platform": PlatformAnalytics,
                "revenue": RevenueAnalytics
            }
            
            # Register formatters
            self._service_registry["formatters"] = {
                "pdf": PDFFormatter,
                "excel": ExcelFormatter,
                "json": JSONFormatter,
                "csv": CSVFormatter,
                "html": HTMLFormatter
            }
            
            # Register schedulers
            self._service_registry["schedulers"] = {
                "automated": AutomatedReportScheduler,
                "cron": CronReportScheduler,
                "realtime": RealTimeReportScheduler
            }
            
            # Register aggregators
            self._service_registry["aggregators"] = {
                "performance": PerformanceAggregator,
                "content": ContentAggregator,
                "revenue": RevenueAggregator,
                "metrics": MetricsAggregator
            }
            
            # Register visualizers
            self._service_registry["visualizers"] = {
                "chart": ChartGenerator,
                "graph": GraphVisualizer,
                "dashboard": DashboardVisualizer,
                "metrics": MetricsVisualizer,
                "trend": TrendVisualizer
            }
            
            # Register exporters
            self._service_registry["exporters"] = {
                "email": EmailExporter,
                "cloud": CloudStorageExporter,
                "api": APIExporter,
                "database": DatabaseExporter
            }
            
            # Register templates
            self._service_registry["templates"] = {
                "executive": ExecutiveTemplate,
                "technical": TechnicalTemplate,
                "compliance": ComplianceTemplate,
                "financial": FinancialTemplate
            }
            
            # Register processors
            self._service_registry["processors"] = {
                "data": DataProcessor,
                "metrics": MetricsProcessor,
                "insights": InsightsProcessor,
                "intelligence": IntelligenceProcessor
            }
            
            logger.info("All components registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register components: {e}")
            raise
    
    async def _run_startup_tasks(self) -> None:
        """Run all startup tasks."""
        for task in self.startup_tasks:
            try:
                await task()
            except Exception as e:
                logger.error(f"Startup task failed: {e}")
    
    async def get_database_session(self) -> AsyncSession:
        """Get database session for dependency injection."""
        if not self._session_maker:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
        
        session = self._session_maker()
        try:
            yield session
        finally:
            await session.close()
    
    async def get_redis_client(self) -> redis.Redis:
        """Get Redis client for dependency injection."""
        if not self._redis_pool:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis not available"
            )
        
        return self._redis_pool
    
    def get_component(self, component_type: str, component_name: str) -> Any:
        """Get registered component by type and name."""
        components = self._service_registry.get(component_type, {})
        component_class = components.get(component_name)
        
        if not component_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Component {component_type}.{component_name} not found"
            )
        
        return component_class
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "status": self.status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": self.settings.app_version,
            "environment": self.settings.environment,
            "components": {},
            "metrics": self._metrics
        }
        
        # Check database
        try:
            async with self._session_maker() as session:
                await session.execute(text("SELECT 1"))
            health_status["components"]["database"] = "healthy"
        except Exception as e:
            health_status["components"]["database"] = f"unhealthy: {str(e)}"
            self.status = ServiceStatus.DEGRADED
        
        # Check Redis
        if self._redis_pool:
            try:
                await self._redis_pool.ping()
                health_status["components"]["redis"] = "healthy"
            except Exception as e:
                health_status["components"]["redis"] = f"unhealthy: {str(e)}"
                self.status = ServiceStatus.DEGRADED
        
        # Check cache
        health_status["components"]["cache"] = "healthy" if self._cache else "not_configured"
        
        # Run custom health checks
        for name, check_func in self.health_checks.items():
            try:
                result = await check_func()
                health_status["components"][name] = result
            except Exception as e:
                health_status["components"][name] = f"unhealthy: {str(e)}"
                self.status = ServiceStatus.DEGRADED
        
        health_status["status"] = self.status.value
        return health_status
    
    async def shutdown(self) -> None:
        """Graceful shutdown of all service components."""
        try:
            logger.info("Shutting down Reports Service...")
            
            # Run shutdown tasks
            for task in self.shutdown_tasks:
                try:
                    await task()
                except Exception as e:
                    logger.error(f"Shutdown task failed: {e}")
            
            # Close database connections
            if self._db_engine:
                await self._db_engine.dispose()
            
            # Close Redis connections
            if self._redis_pool:
                await self._redis_pool.close()
            
            self.status = ServiceStatus.MAINTENANCE
            logger.info("Reports Service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            raise


# Global service manager instance
service_manager: Optional[ReportsServiceManager] = None


def get_service_manager() -> ReportsServiceManager:
    """Get the global service manager instance."""
    global service_manager
    if not service_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service manager not initialized"
        )
    return service_manager


def create_fastapi_app(settings: ReportsSettings) -> FastAPI:
    """Create and configure FastAPI application."""
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        global service_manager
        service_manager = ReportsServiceManager(settings)
        await service_manager.initialize()
        
        yield
        
        # Shutdown
        if service_manager:
            await service_manager.shutdown()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Ultra-advanced enterprise reporting system for IA Influencer Agent platform",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add rate limiting
    if RATE_LIMITING_AVAILABLE:
        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add monitoring
    if MONITORING_AVAILABLE and settings.monitoring_enabled:
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app)
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Comprehensive health check endpoint."""
        manager = get_service_manager()
        return await manager.health_check()
    
    # Service info endpoint
    @app.get("/info", tags=["Info"])
    async def service_info():
        """Service information endpoint."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": list(get_service_manager()._service_registry.keys())
        }
    
    # Metrics endpoint
    if MONITORING_AVAILABLE:
        @app.get("/metrics", tags=["Monitoring"])
        async def metrics():
            """Prometheus metrics endpoint."""
            return Response(
                generate_latest(),
                media_type="text/plain; version=0.0.4; charset=utf-8"
            )
    
    return app


def run_service(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1
) -> None:
    """Run the reports service."""
    
    # Load settings
    settings = ReportsSettings()
    
    # Create FastAPI app
    app = create_fastapi_app(settings)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run server
    uvicorn.run(
        app,
        host=host or settings.host,
        port=port or settings.port,
        reload=reload,
        workers=workers if not reload else 1,
        access_log=settings.debug,
        log_level=settings.log_level.lower()
    )


# Dependency injection functions
async def get_db_session() -> AsyncSession:
    """
Database session dependency."""
    manager = get_service_manager()
    async for session in manager.get_database_session():
        yield session


async def get_redis_client() -> redis.Redis:
    """
Redis client dependency."""
    manager = get_service_manager()
    return await manager.get_redis_client()


def get_component_factory(component_type: str):
    """
Component factory dependency."""
    def _get_component(component_name: str):
        manager = get_service_manager()
        return manager.get_component(component_type, component_name)
    
    return _get_component


# Authentication and authorization
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
Verify JWT token and return user info."""
    
    try:
        import jwt
        from datetime import datetime, timezone
        
        token = credentials.credentials
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get settings for JWT verification
        manager = get_service_manager()
        secret_key = manager.settings.secret_key
        
        try:
            # Decode and verify the JWT token
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=["HS256"],
                options={"require_exp": True}
            )
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Extract user information
            user_data = {
                "user_id": payload.get("sub"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", []),
                "issued_at": payload.get("iat"),
                "expires_at": payload.get("exp")
            }
            
            # Validate required fields
            if not user_data["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.debug(f"Token verified for user: {user_data['username']}")
            return user_data
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except ImportError:
        logger.warning("JWT library not available, using mock authentication")
        
        # Fallback to mock authentication for development
        token = credentials.credentials
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Mock user data for development
        if token == "dev-token":
            return {
                "user_id": "dev-user-123",
                "username": "developer",
                "email": "dev@example.com",
                "roles": ["admin", "reports_access"],
                "permissions": ["read", "write", "admin"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid development token",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Rate limiting decorator
def rate_limit(limit: str = "100/minute"):
    """Rate limiting decorator."""
    def decorator(func):
        if RATE_LIMITING_AVAILABLE:
            return limiter.limit(limit)(func)
        return func
    return decorator


# Circuit breaker decorator
def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 30):
    """
Circuit breaker decorator."""
    def decorator(func):
        if CIRCUIT_BREAKER_AVAILABLE:
            return circuit(failure_threshold=failure_threshold, recovery_timeout=recovery_timeout)(func)
        return func
    return decorator


# Caching decorator
def cache_result(ttl: int = 3600, key_prefix: str = "reports"):
    """Caching decorator for expensive operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            manager = get_service_manager()
            
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            if manager._cache:
                cached_result = manager._cache.get(cache_key)
                if cached_result is not None:
                    if MONITORING_AVAILABLE:
                        cache_hits.labels(cache_type="local").inc()
                    return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            if manager._cache:
                manager._cache[cache_key] = result
                if MONITORING_AVAILABLE:
                    cache_misses.labels(cache_type="local").inc()
            
            return result
        
        return wrapper
    return decorator


# Export main components for external use
__all__ = [
    "ReportsServiceManager",
    "ReportsSettings",
    "ServiceStatus",
    "ComponentType",
    "create_fastapi_app",
    "run_service",
    "get_service_manager",
    "get_db_session",
    "get_redis_client",
    "get_component_factory",
    "verify_token",
    "rate_limit",
    "circuit_breaker",
    "cache_result"
]


if __name__ == "__main__":
    # Run the service if executed directly
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "dev":
            run_service(reload=True, workers=1)
        elif sys.argv[1] == "prod":
            run_service(workers=4)
        else:
            print("Usage: python index.py [dev|prod]")
    else:
        run_service()
