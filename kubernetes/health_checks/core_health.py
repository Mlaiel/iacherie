"""Core Application Health Checker
Monitors essential application services and system components

This module provides health checking for core application infrastructure:
- FastAPI application status and performance
- Request/response metrics and latency
- System resources (CPU, memory, disk)
- Application configuration validation
- Security components status
- Multi-tenant isolation verification

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: IA Influencer Agent Platform - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use,
reproduction, or distribution without explicit written permission from
Fahed Mlaiel is strictly prohibited and may result in legal action.
"""

import asyncio
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from fastapi import FastAPI
from pydantic import BaseModel
import aiohttp


class HealthStatus(str, Enum):
    """
Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class HealthCheckResult:
    """Health check result structure"""
    service: str
    status: HealthStatus
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class SystemMetrics:
    """
System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    load_average: List[float]
    network_connections: int
    process_count: int


class CoreHealthChecker:
    """
    Core application health monitoring service
    
    Provides comprehensive health checking for essential application
    components including FastAPI app, system resources, and core services.
    """
    def __init__(self, app -> None: FastAPI, config -> None: Dict[str, Any]) -> None:
        """
        Initialize core health checker
        
        Args:
            app: FastAPI application instance
            config: Application configuration dictionary
        """
        self.app = app
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.utcnow()
        
        # Health check thresholds
        self.cpu_threshold = config.get("health_checks", {}).get("cpu_threshold", 80.0)
        self.memory_threshold = config.get("health_checks", {}).get("memory_threshold", 85.0)
        self.disk_threshold = config.get("health_checks", {}).get("disk_threshold", 90.0)
        self.response_time_threshold = config.get("health_checks", {}).get("response_time_ms", 5000)

    async def check_application_health(self) -> HealthCheckResult:
        """
        Check FastAPI application health and performance
        
        Returns:
            HealthCheckResult: Application health status and metrics
        """
        start_time = time.time()
        
        try:
            # Check application routes and middleware
            route_count = len(self.app.routes)
            middleware_count = len(self.app.user_middleware)
            
            # Calculate uptime
            uptime = datetime.utcnow() - self.start_time
            uptime_seconds = uptime.total_seconds()
            
            # Test basic application response
            details = {
                "uptime_seconds": uptime_seconds,
                "uptime_human": str(uptime),
                "route_count": route_count,
                "middleware_count": middleware_count,
                "app_title": getattr(self.app, "title", "IA Influencer Agent"),
                "app_version": getattr(self.app, "version", "1.0.0"),
                "environment": self.config.get("environment", "unknown"),
                "debug_mode": self.config.get("debug", False)
            }
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on performance
            if response_time > self.response_time_threshold:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
                
            return HealthCheckResult(
                service="application",
                status=status,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Application health check failed: {str(e)}")
            return HealthCheckResult(
                service="application",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_system_resources(self) -> HealthCheckResult:
        """
        Check system resource utilization and performance
        
        Returns:
            HealthCheckResult: System resource health status
        """
        start_time = time.time()
        
        try:
            # Collect system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            net_connections = len(psutil.net_connections())
            process_count = len(psutil.pids())
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                load_average=list(load_avg),
                network_connections=net_connections,
                process_count=process_count
            )
            
            # Determine health status based on thresholds
            status = HealthStatus.HEALTHY
            warnings = []
            
            if cpu_percent > self.cpu_threshold:
                status = HealthStatus.DEGRADED
                warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
                
            if memory.percent > self.memory_threshold:
                status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else HealthStatus.UNHEALTHY
                warnings.append(f"High memory usage: {memory.percent:.1f}%")
                
            if disk.percent > self.disk_threshold:
                status = HealthStatus.CRITICAL
                warnings.append(f"High disk usage: {disk.percent:.1f}%")
            
            details = asdict(metrics)
            details.update({
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "warnings": warnings,
                "thresholds": {
                    "cpu": self.cpu_threshold,
                    "memory": self.memory_threshold,
                    "disk": self.disk_threshold
                }
            })
            
            return HealthCheckResult(
                service="system_resources",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"System resources health check failed: {str(e)}")
            return HealthCheckResult(
                service="system_resources",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_security_components(self) -> HealthCheckResult:
        """
        Check security components and authentication systems
        
        Returns:
            HealthCheckResult: Security components health status
        """
        start_time = time.time()
        
        try:
            details = {}
            status = HealthStatus.HEALTHY
            
            # Check JWT configuration
            jwt_config = self.config.get("security", {}).get("jwt", {})
            details["jwt_configured"] = bool(jwt_config.get("secret_key"))
            details["jwt_algorithm"] = jwt_config.get("algorithm", "HS256")
            details["jwt_expiry_minutes"] = jwt_config.get("access_token_expire_minutes", 30)
            
            # Check OAuth2 configuration
            oauth_config = self.config.get("security", {}).get("oauth2", {})
            details["oauth2_configured"] = bool(oauth_config)
            
            # Check CORS configuration
            cors_config = self.config.get("security", {}).get("cors", {})
            details["cors_configured"] = bool(cors_config)
            details["cors_origins"] = cors_config.get("allow_origins", [])
            
            # Check encryption settings
            encryption_config = self.config.get("security", {}).get("encryption", {})
            details["encryption_configured"] = bool(encryption_config.get("key"))
            
            # Check rate limiting
            rate_limit_config = self.config.get("security", {}).get("rate_limiting", {})
            details["rate_limiting_enabled"] = bool(rate_limit_config)
            
            # Validate critical security components
            if not details["jwt_configured"]:
                status = HealthStatus.CRITICAL
                
            if not details["encryption_configured"]:
                status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
            
            return HealthCheckResult(
                service="security_components",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Security components health check failed: {str(e)}")
            return HealthCheckResult(
                service="security_components",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_configuration_validity(self) -> HealthCheckResult:
        """
        Validate application configuration completeness and correctness
        
        Returns:
            HealthCheckResult: Configuration validation status
        """
        start_time = time.time()
        
        try:
            details = {}
            status = HealthStatus.HEALTHY
            missing_configs = []
            
            # Required configuration sections
            required_sections = [
                "database",
                "redis", 
                "security",
                "logging",
                "ml",
                "protection",
                "monetization"
            ]
            
            for section in required_sections:
                if section not in self.config:
                    missing_configs.append(section)
                    details[f"{section}_configured"] = False
                else:
                    details[f"{section}_configured"] = True
                    
            # Check database configuration completeness
            db_config = self.config.get("database", {})
            db_required = ["host", "port", "username", "password", "database"]
            db_missing = [key for key in db_required if not db_config.get(key)]
            
            if db_missing:
                missing_configs.extend([f"database.{key}" for key in db_missing])
                
            # Check Redis configuration
            redis_config = self.config.get("redis", {})
            redis_required = ["host", "port"]
            redis_missing = [key for key in redis_required if not redis_config.get(key)]
            
            if redis_missing:
                missing_configs.extend([f"redis.{key}" for key in redis_missing])
            
            details.update({
                "total_config_sections": len(self.config),
                "required_sections_count": len(required_sections),
                "missing_configurations": missing_configs,
                "configuration_completeness": 1.0 - (len(missing_configs) / len(required_sections))
            })
            
            # Determine status based on missing configurations
            if len(missing_configs) > 5:
                status = HealthStatus.CRITICAL
            elif len(missing_configs) > 2:
                status = HealthStatus.DEGRADED
            elif len(missing_configs) > 0:
                status = HealthStatus.DEGRADED
                
            return HealthCheckResult(
                service="configuration",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return HealthCheckResult(
                service="configuration",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def perform_comprehensive_check(self) -> List[HealthCheckResult]:
        """
        Perform all core health checks concurrently
        
        Returns:
            List[HealthCheckResult]: All core health check results
        """
        checks = await asyncio.gather(
            self.check_application_health(),
            self.check_system_resources(),
            self.check_security_components(),
            self.check_configuration_validity(),
            return_exceptions=True
        )
        
        results = []
        for check in checks:
            if isinstance(check, Exception):
                self.logger.error(f"Health check failed with exception: {str(check)}")
                results.append(HealthCheckResult(
                    service="unknown",
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0.0,
                    timestamp=datetime.utcnow(),
                    details={},
                    error_message=str(check)
                ))
            else:
                results.append(check)
                
        return results

    async def get_health_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive health summary for core components
        
        Returns:
            Dict[str, Any]: Health summary with overall status and metrics
        """
        results = await self.perform_comprehensive_check()
        
        # Calculate overall status
        status_weights = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 1,
            HealthStatus.UNHEALTHY: 2,
            HealthStatus.CRITICAL: 3
        }
        
        overall_score = max([status_weights[result.status] for result in results])
        overall_status = [status for status, weight in status_weights.items() if weight == overall_score][0]
        
        # Calculate metrics
        avg_response_time = sum([result.response_time_ms for result in results]) / len(results)
        healthy_services = len([r for r in results if r.status == HealthStatus.HEALTHY])
        total_services = len(results)
        
        return {
            "overall_status": overall_status.value,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "health_percentage": (healthy_services / total_services) * 100,
            "average_response_time_ms": round(avg_response_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "results": [asdict(result) for result in results]
        }
