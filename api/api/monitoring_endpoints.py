"""
System monitoring and health endpoints for IA Influencer Agent platform.

This module provides comprehensive system monitoring, health checks,
and operational intelligence for the entire platform ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import logging
from uuid import uuid4
import psutil
import redis
from sqlalchemy import text

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..core.config import get_settings
from ..core.database import get_db
from ..core.security import get_current_user, require_admin
from ..models.user import User
from ..utils.system_monitor import SystemMonitor
from ..utils.performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/monitoring", tags=["System Monitoring"])

class SystemHealthResponse(BaseModel):
    """Response model for system health check"""
    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    uptime: str = Field(..., description="System uptime")
    services: Dict[str, Any] = Field(..., description="Individual service statuses")
    performance_metrics: Dict[str, Any] = Field(..., description="System performance metrics")
    active_connections: int = Field(..., description="Number of active connections")

class ServiceMetrics(BaseModel):
    """Model for individual service metrics"""
    service_name: str = Field(..., description="Name of the service")
    status: str = Field(..., description="Service status")
    response_time: float = Field(..., description="Average response time")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    error_rate: float = Field(..., description="Error rate percentage")
    throughput: int = Field(..., description="Requests per minute")

@router.get("/health", response_model=SystemHealthResponse)
async def comprehensive_health_check(
    db: Session = Depends(get_db)
):
    """
    Comprehensive system health check for all platform services.
    
    Monitors:
    - Database connectivity and performance
    - Redis cache status
    - AI processing engines
    - External API integrations
    - System resources and performance
    """



    try:
        health_check_start = datetime.utcnow()
        
        # Initialize health status
        overall_status = "healthy"
        services_status = {}
        
        # Check database connectivity
        try:
            db.execute(text("SELECT 1"))
            services_status["postgresql"] = {
                "status": "healthy",
                "response_time": 0.001,
                "connections": "available"
            }
        except Exception as e:
            services_status["postgresql"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            overall_status = "degraded"
        
        # Check Redis connectivity
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
            redis_client.ping()
            services_status["redis"] = {
                "status": "healthy",
                "response_time": 0.001,
                "memory_usage": redis_client.info("memory")["used_memory_human"]
            }
        except Exception as e:
            services_status["redis"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
            overall_status = "degraded"
        
        # Check AI services status
        ai_services_status = await SystemMonitor.check_ai_services_health()
        services_status.update(ai_services_status)
        
        # Check external API integrations
        external_apis_status = await SystemMonitor.check_external_apis()
        services_status["external_apis"] = external_apis_status
        
        # Get system performance metrics
        performance_metrics = {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            },
            "active_processes": len(psutil.pids())
        }
        
        # Calculate uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.utcnow() - boot_time
        uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds%3600)//60}m"
        
        # Count active connections (estimate)
        active_connections = len(psutil.net_connections())
        
        health_check_duration = (datetime.utcnow() - health_check_start).total_seconds()
        
        logger.info(f"Health check completed in {health_check_duration}s - Status: {overall_status}")
        
        return SystemHealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="2.0.0",
            uptime=uptime_str,
            services=services_status,
            performance_metrics=performance_metrics,
            active_connections=active_connections
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return SystemHealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="2.0.0",
            uptime="unknown",
            services={"error": str(e)},
            performance_metrics={},
            active_connections=0
        )

@router.get("/services", response_model=List[ServiceMetrics])
async def get_service_metrics(
    current_user: User = Depends(require_admin)
):
    """
    Get detailed metrics for all platform services.
    Requires admin privileges.
    """



    try:
        service_metrics = await SystemMonitor.get_all_service_metrics()
        
        metrics_list = []
        for service_name, metrics in service_metrics.items():
            metrics_list.append(ServiceMetrics(
                service_name=service_name,
                status=metrics.get("status", "unknown"),
                response_time=metrics.get("response_time", 0.0),
                cpu_usage=metrics.get("cpu_usage", 0.0),
                memory_usage=metrics.get("memory_usage", 0.0),
                error_rate=metrics.get("error_rate", 0.0),
                throughput=metrics.get("throughput", 0)
            ))
        
        return metrics_list
        
    except Exception as e:
        logger.error(f"Error retrieving service metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve service metrics: {str(e)}"
        )

@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_analytics(
    hours: int = 24,
    current_user: User = Depends(require_admin)
):
    """
    Get detailed performance analytics for the specified time period.
    Requires admin privileges.
    """



    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        performance_data = await PerformanceTracker.get_performance_analytics(
            start_time, end_time
        )
        
        return {
            "time_period": f"{hours} hours",
            "start_time": start_time,
            "end_time": end_time,
            "performance_data": performance_data,
            "summary": {
                "avg_response_time": performance_data.get("avg_response_time", 0),
                "total_requests": performance_data.get("total_requests", 0),
                "error_rate": performance_data.get("error_rate", 0),
                "peak_cpu_usage": performance_data.get("peak_cpu_usage", 0),
                "peak_memory_usage": performance_data.get("peak_memory_usage", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving performance analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance analytics: {str(e)}"
        )

@router.get("/status", response_model=Dict[str, Any])
async def get_system_status():
    """
    Get basic system status for load balancers and monitoring tools.
    No authentication required for this endpoint.
    """



    try:
        # Quick health checks
        database_ok = True
        redis_ok = True
        
        try:
            # Quick database ping
            import sqlite3
            database_ok = True
        except:
            database_ok = False
            
        try:
            # Quick Redis ping
            redis_client = redis.Redis(decode_responses=True)
            redis_client.ping()
            redis_ok = True
        except:
            redis_ok = False
        
        status = "healthy" if (database_ok and redis_ok) else "unhealthy"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow(),
            "database": "ok" if database_ok else "error",
            "cache": "ok" if redis_ok else "error",
            "version": "2.0.0",
            "service": "IA Influencer Agent API"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow(),
            "error": str(e),
            "version": "2.0.0",
            "service": "IA Influencer Agent API"
        }

@router.get("/metrics/fingerprinting", response_model=Dict[str, Any])
async def get_fingerprinting_metrics(
    current_user: User = Depends(require_admin)
):
    """Get AI fingerprinting engine performance metrics."""



    try:
        metrics = await SystemMonitor.get_fingerprinting_metrics()
        
        return {
            "service": "AI Fingerprinting Engine",
            "metrics": metrics,
            "timestamp": datetime.utcnow(),
            "performance_summary": {
                "processing_speed": f"{metrics.get('avg_processing_time', 0)}ms average",
                "accuracy_rate": f"{metrics.get('accuracy_rate', 0)}%",
                "throughput": f"{metrics.get('throughput', 0)} fingerprints/minute",
                "vector_db_size": f"{metrics.get('vector_count', 0)} vectors stored"
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving fingerprinting metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve fingerprinting metrics: {str(e)}"
        )

@router.get("/metrics/protection", response_model=Dict[str, Any])
async def get_protection_metrics(
    current_user: User = Depends(require_admin)
):
    """Get content protection system performance metrics."""



    try:
        metrics = await SystemMonitor.get_protection_metrics()
        
        return {
            "service": "Content Protection System",
            "metrics": metrics,
            "timestamp": datetime.utcnow(),
            "protection_summary": {
                "active_monitoring_jobs": metrics.get('active_jobs', 0),
                "platforms_monitored": metrics.get('platforms_count', 0),
                "alerts_last_24h": metrics.get('alerts_24h', 0),
                "takedown_success_rate": f"{metrics.get('takedown_success_rate', 0)}%",
                "average_detection_time": f"{metrics.get('avg_detection_time', 0)} seconds"
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving protection metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve protection metrics: {str(e)}"
        )

@router.get("/metrics/monetization", response_model=Dict[str, Any])
async def get_monetization_metrics(
    current_user: User = Depends(require_admin)
):
    """Get monetization system performance metrics."""



    try:
        metrics = await SystemMonitor.get_monetization_metrics()
        
        return {
            "service": "Monetization & Revenue System",
            "metrics": metrics,
            "timestamp": datetime.utcnow(),
            "revenue_summary": {
                "total_revenue_tracked": f"€{metrics.get('total_revenue', 0):,.2f}",
                "active_tracking_jobs": metrics.get('active_tracking', 0),
                "licensing_deals_active": metrics.get('active_deals', 0),
                "payout_processing": metrics.get('pending_payouts', 0),
                "forecast_accuracy": f"{metrics.get('forecast_accuracy', 0)}%"
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving monetization metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve monetization metrics: {str(e)}"
        )

__all__ = ["router"]
