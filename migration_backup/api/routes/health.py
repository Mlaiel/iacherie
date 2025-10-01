#!/usr/bin/env python3
"""
Global Health Check Endpoint - IA Chéries Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Role: Backend Senior + DevOps Engineer
Purpose: Enterprise health monitoring and system status
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class ServiceHealth(BaseModel):
    name: str
    status: str
    response_time_ms: float
    last_check: str
    details: Dict[str, Any] = {}

class SystemHealth(BaseModel):
    overall_status: str
    timestamp: str
    services: List[ServiceHealth]
    system_info: Dict[str, Any]
    uptime_seconds: float

class ApiResponse(BaseModel):
    success: bool
    data: Any
    message: str = ""
    timestamp: str

# Router setup
router = APIRouter(tags=["health"])

# System start time for uptime calculation
SYSTEM_START_TIME = time.time()

async def check_service_health(service_name: str, check_function=None) -> ServiceHealth:
    """Check health of individual service"""
    start_time = time.time()
    
    try:
        if check_function:
            await check_function()
        
        response_time = (time.time() - start_time) * 1000
        
        return ServiceHealth(
            name=service_name,
            status="healthy",
            response_time_ms=round(response_time, 2),
            last_check=datetime.now().isoformat(),
            details={"message": f"{service_name} is operational"}
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        
        return ServiceHealth(
            name=service_name,
            status="unhealthy",
            response_time_ms=round(response_time, 2),
            last_check=datetime.now().isoformat(),
            details={"error": str(e)}
        )

async def check_database_health():
    """Mock database health check"""
    # Simulate database connection check
    await asyncio.sleep(0.01)  # Simulate query time
    return True

async def check_redis_health():
    """Mock Redis health check"""
    # Simulate Redis ping
    await asyncio.sleep(0.005)
    return True

async def check_external_api_health():
    """Mock external API health check"""
    # Simulate external API call
    await asyncio.sleep(0.02)
    return True

@router.get("/health", response_model=ApiResponse)
async def system_health_check():
    """Comprehensive system health check"""
    try:
        # Check individual services
        services = []
        
        # Core services
        services.append(await check_service_health("database", check_database_health))
        services.append(await check_service_health("redis", check_redis_health))
        services.append(await check_service_health("external_apis", check_external_api_health))
        
        # Application services
        services.append(await check_service_health("authentication"))
        services.append(await check_service_health("analytics"))
        services.append(await check_service_health("websockets"))
        
        # Calculate overall status
        unhealthy_services = [s for s in services if s.status != "healthy"]
        overall_status = "healthy" if not unhealthy_services else "degraded" if len(unhealthy_services) < len(services) // 2 else "unhealthy"
        
        # System information
        system_info = {
            "version": "2.0.0",
            "environment": "development",
            "total_services": len(services),
            "healthy_services": len([s for s in services if s.status == "healthy"]),
            "unhealthy_services": len(unhealthy_services),
            "average_response_time_ms": round(sum(s.response_time_ms for s in services) / len(services), 2)
        }
        
        health_data = SystemHealth(
            overall_status=overall_status,
            timestamp=datetime.now().isoformat(),
            services=services,
            system_info=system_info,
            uptime_seconds=round(time.time() - SYSTEM_START_TIME, 2)
        )
        
        return ApiResponse(
            success=overall_status != "unhealthy",
            data=health_data.dict(),
            message=f"System is {overall_status}",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/health/simple")
async def simple_health_check():
    """Simple health check for load balancers"""
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "uptime": round(time.time() - SYSTEM_START_TIME, 2)
    }

@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Check if all critical services are ready
        critical_services = ["database", "redis"]
        
        for service in critical_services:
            if service == "database":
                await check_database_health()
            elif service == "redis":
                await check_redis_health()
        
        return {
            "ready": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat(),
        "uptime": round(time.time() - SYSTEM_START_TIME, 2)
    }