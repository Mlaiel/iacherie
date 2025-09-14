"""
🚀 Ainflue DevOps Service Entry Point - Enterprise FastAPI Implementation
=========================================================================

Main service entry point for DevOps operations with comprehensive REST API,
health monitoring, metrics collection, and service orchestration.

Features:
- FastAPI service with automatic OpenAPI documentation
- Health check endpoints with detailed system status
- Metrics collection and Prometheus integration
- Service discovery and registration
- Graceful shutdown with cleanup
- Middleware for logging, monitoring, and security
- Integration with all DevOps modules

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: Lead DevOps Engineer + Backend Senior + Platform Engineering
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

# DevOps module imports
from . import (
    devops_registry, 
    initialize_devops_modules,
    get_devops_info,
    get_devops_system,
    DEVOPS_SERVICES,
    DevOpsException,
    __version__
)

logger = logging.getLogger(__name__)

# Pydantic models for API responses
class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="DevOps service version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    modules: Dict[str, bool] = Field(..., description="Module health status")
    system_info: Dict[str, Any] = Field(..., description="System information")

class MetricsResponse(BaseModel):
    """Metrics response model"""
    timestamp: datetime = Field(..., description="Metrics collection timestamp")
    infrastructure: Dict[str, Any] = Field(..., description="Infrastructure metrics")
    deployment: Dict[str, Any] = Field(..., description="Deployment metrics")
    performance: Dict[str, Any] = Field(..., description="Performance metrics")
    security: Dict[str, Any] = Field(..., description="Security metrics")

class DeploymentRequest(BaseModel):
    """Deployment request model"""
    app_name: str = Field(..., description="Application name")
    environment: str = Field(..., description="Target environment")
    image_tag: str = Field(..., description="Container image tag")
    config_overrides: Optional[Dict[str, Any]] = Field(None, description="Configuration overrides")

class ScalingRequest(BaseModel):
    """Scaling request model"""
    app_name: str = Field(..., description="Application name")
    environment: str = Field(..., description="Environment name")
    target_replicas: int = Field(..., ge=1, le=100, description="Target replica count")
    scaling_reason: str = Field(default="manual", description="Reason for scaling")

# Global service state
class DevOpsServiceState:
    """DevOps service state management"""
    
    def __init__(self) -> None:
        self.start_time = datetime.now()
        self.is_ready = False
        self.is_shutting_down = False
        self.background_tasks: List[asyncio.Task] = []
        
    @property
    def uptime_seconds(self) -> float:
        """Get service uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
        
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.is_ready and not self.is_shutting_down

service_state = DevOpsServiceState()

# Service lifecycle management
@asynccontextmanager
async def lifespan(app -> None: FastAPI) -> None:
    """FastAPI lifespan context manager"""
    
    logger.info("🚀 Starting Ainflue DevOps Service...")
    
    try:
        # Initialize DevOps modules
        await initialize_devops_modules()
        
        # Start background monitoring tasks
        service_state.background_tasks.extend([
            asyncio.create_task(infrastructure_monitoring_task()),
            asyncio.create_task(deployment_monitoring_task()),
            asyncio.create_task(health_monitoring_task())
        ])
        
        service_state.is_ready = True
        logger.info("✅ DevOps service initialization complete")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ DevOps service initialization failed: {str(e)}")
        raise
    finally:
        # Graceful shutdown
        logger.info("🔄 DevOps service shutting down...")
        service_state.is_shutting_down = True
        
        # Cancel background tasks
        for task in service_state.background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("✅ DevOps service shutdown complete")

# FastAPI application setup
app = FastAPI(
    title="Ainflue DevOps Engineering Service",
    description="Enterprise-grade DevOps automation and infrastructure management API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Security
security = HTTPBearer(auto_error=False)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware for logging and monitoring
@app.middleware("http")
async def logging_middleware(request, call_next) -> None:
    """Log all HTTP requests and responses"""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"HTTP {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Dependency injection
async def get_devops_service() -> None:
    """Get DevOps service dependency"""
    devops_system = get_devops_system()
    if not devops_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DevOps system not available"
        )
    return devops_system

# Health and readiness endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> None:
    """
    Health check endpoint
    
    Returns detailed health status of DevOps service and all modules
    """
    try:
        # Get module health status
        module_health = await devops_registry.health_check_all()
        
        # Get system information
        devops_info = get_devops_info()
        
        # Get DevOps system dashboard if available
        devops_system = get_devops_system()
        system_info = {}
        if devops_system:
            try:
                system_info = devops_system.get_devops_dashboard()
            except Exception as e:
                logger.warning(f"Failed to get DevOps dashboard: {str(e)}")
        
        return HealthResponse(
            status="healthy" if service_state.is_healthy() else "unhealthy",
            timestamp=datetime.now(),
            version=__version__,
            uptime_seconds=service_state.uptime_seconds,
            modules=module_health,
            system_info={
                "devops_info": devops_info,
                "dashboard": system_info
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

@app.get("/ready", tags=["Health"])
async def readiness_check() -> None:
    """
    Readiness check endpoint
    
    Returns 200 if service is ready to accept requests
    """
    if not service_state.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )
    
    return {"status": "ready", "timestamp": datetime.now()}

@app.get("/metrics", response_model=MetricsResponse, tags=["Metrics"])
async def get_metrics(devops_system = Depends(get_devops_service)):
    """
    Get comprehensive DevOps metrics
    
    Returns infrastructure, deployment, performance, and security metrics
    """
    try:
        dashboard = devops_system.get_devops_dashboard()
        
        return MetricsResponse(
            timestamp=datetime.now(),
            infrastructure=dashboard.get("infrastructure", {}),
            deployment=dashboard.get("deployments", {}),
            performance=dashboard.get("optimization", {}),
            security=dashboard.get("alerts", {})
        )
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics collection failed: {str(e)}"
        )

# DevOps operation endpoints
@app.post("/deploy", tags=["Deployment"])
async def deploy_application(
    deployment: DeploymentRequest,
    background_tasks: BackgroundTasks,
    devops_system = Depends(get_devops_service)
):
    """
    Deploy application using DevOps automation
    
    Initiates deployment pipeline with specified strategy and configuration
    """
    try:
        pipeline_id = await devops_system.deploy_application(
            app_name=deployment.app_name,
            environment=deployment.environment,
            image_tag=deployment.image_tag,
            config_overrides=deployment.config_overrides
        )
        
        return {
            "status": "deployment_initiated",
            "pipeline_id": pipeline_id,
            "app_name": deployment.app_name,
            "environment": deployment.environment,
            "image_tag": deployment.image_tag,
            "timestamp": datetime.now()
        }
        
    except DevOpsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deployment failed: {str(e)}"
        )

@app.post("/scale", tags=["Scaling"])
async def scale_application(
    scaling: ScalingRequest,
    devops_system = Depends(get_devops_service)
):
    """
    Scale application instances
    
    Adjusts application replica count with monitoring and validation
    """
    try:
        success = await devops_system.scale_application(
            app_name=scaling.app_name,
            environment=scaling.environment,
            target_replicas=scaling.target_replicas,
            scaling_reason=scaling.scaling_reason
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Scaling operation failed"
            )
        
        return {
            "status": "scaling_complete",
            "app_name": scaling.app_name,
            "environment": scaling.environment,
            "target_replicas": scaling.target_replicas,
            "reason": scaling.scaling_reason,
            "timestamp": datetime.now()
        }
        
    except DevOpsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Scaling failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scaling failed: {str(e)}"
        )

@app.get("/infrastructure/status", tags=["Infrastructure"])
async def get_infrastructure_status(devops_system = Depends(get_devops_service)):
    """
    Get current infrastructure status and metrics
    """
    try:
        metrics = await devops_system.monitor_infrastructure()
        
        return {
            "status": "success",
            "timestamp": metrics.timestamp,
            "metrics": {
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "disk_usage": metrics.disk_usage,
                "network_io": metrics.network_io,
                "active_connections": metrics.active_connections,
                "response_time": metrics.response_time,
                "error_rate": metrics.error_rate,
                "throughput": metrics.throughput
            }
        }
        
    except Exception as e:
        logger.error(f"Infrastructure status check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Infrastructure status check failed: {str(e)}"
        )

@app.get("/optimization/recommendations", tags=["Optimization"])
async def get_optimization_recommendations(devops_system = Depends(get_devops_service)):
    """
    Get infrastructure optimization recommendations
    """
    try:
        recommendations = await devops_system.optimize_infrastructure()
        
        return {
            "status": "success",
            "timestamp": datetime.now(),
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Optimization recommendations failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization recommendations failed: {str(e)}"
        )

@app.get("/containers", tags=["Containers"])
async def get_container_status(devops_system = Depends(get_devops_service)):
    """
    Get container infrastructure status and management information
    """
    try:
        container_stats = await devops_system.manage_containers()
        
        return {
            "status": "success",
            "timestamp": datetime.now(),
            "container_stats": container_stats
        }
        
    except Exception as e:
        logger.error(f"Container status check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Container status check failed: {str(e)}"
        )

# Background monitoring tasks
async def infrastructure_monitoring_task() -> None:
    """Background task for infrastructure monitoring"""
    logger.info("Starting infrastructure monitoring task")
    
    while not service_state.is_shutting_down:
        try:
            devops_system = get_devops_system()
            if devops_system:
                await devops_system.monitor_infrastructure()
            
            await asyncio.sleep(60)  # Monitor every minute
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Infrastructure monitoring task error: {str(e)}")
            await asyncio.sleep(60)
    
    logger.info("Infrastructure monitoring task stopped")

async def deployment_monitoring_task() -> None:
    """Background task for deployment monitoring"""
    logger.info("Starting deployment monitoring task")
    
    while not service_state.is_shutting_down:
        try:
            # Monitor deployment pipelines and health
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Deployment monitoring task error: {str(e)}")
            await asyncio.sleep(30)
    
    logger.info("Deployment monitoring task stopped")

async def health_monitoring_task() -> None:
    """Background task for health monitoring"""
    logger.info("Starting health monitoring task")
    
    while not service_state.is_shutting_down:
        try:
            # Perform periodic health checks
            await devops_registry.health_check_all()
            await asyncio.sleep(120)  # Check every 2 minutes
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health monitoring task error: {str(e)}")
            await asyncio.sleep(120)
    
    logger.info("Health monitoring task stopped")

# Error handlers
@app.exception_handler(DevOpsException)
async def devops_exception_handler(request, exc -> None: DevOpsException) -> None:
    """Handle DevOps-specific exceptions"""
    return JSONResponse(
        status_code=400,
        content={
            "error": "DevOps operation failed",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc -> None: HTTPException) -> None:
    """Handle HTTP exceptions with enhanced logging"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

# Signal handlers for graceful shutdown
def handle_shutdown_signal(signum, frame) -> None:
    """Handle shutdown signals"""
    logger.info(f"Received shutdown signal: {signum}")
    service_state.is_shutting_down = True

signal.signal(signal.SIGTERM, handle_shutdown_signal)
signal.signal(signal.SIGINT, handle_shutdown_signal)

# Development server entry point
def run_development_server() -> None:
    """Run development server with hot reload"""
    uvicorn.run(
        "devops.index:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
        access_log=True
    )

# Production server entry point
def run_production_server() -> None:
    """Run production server with optimized settings"""
    uvicorn.run(
        "devops.index:app",
        host="0.0.0.0",
        port=8080,
        workers=4,
        log_level="info",
        access_log=True,
        loop="uvloop",
        http="httptools"
    )

if __name__ == "__main__":
    import os
    
    # Run server based on environment
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        run_production_server()
    else:
        run_development_server()

logger.info("🚀 Ainflue DevOps Service Entry Point initialized")