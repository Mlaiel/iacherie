"""Health Monitor for IA Influencer Agent Platform
===============================================

Industrial-grade health monitoring system with AI-powered diagnostics,
predictive failure detection, and automated recovery for content protection
and influencer collaboration platforms.

Features:
- Multi-layer health checks with dependency mapping
- Circuit breaker patterns with intelligent recovery
- AI-powered anomaly detection and predictive analytics
- Content protection service monitoring
- Revenue system health tracking
- Real-time user experience impact assessment

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use, distribution, or modification prohibited
"""

import asyncio
import time
import logging
import statistics
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aioredis
import aiohttp
import psutil
import numpy as np
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
import json
import ssl
import socket
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """
Health status enumeration with business impact levels"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Service type classification for specialized monitoring"""

    CORE_API = "core_api"
    AI_ENGINE = "ai_engine"
    FINGERPRINT_SERVICE = "fingerprint_service"
    CONTENT_PROTECTION = "content_protection"
    REVENUE_TRACKING = "revenue_tracking"
    USER_MANAGEMENT = "user_management"
    NOTIFICATION_SERVICE = "notification_service"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_API = "external_api"


@dataclass
class HealthCheck:
    """Enhanced health check configuration with business context"""
    name: str
    check_function: Callable
    service_type: ServiceType
    interval: int = 30
    timeout: int = 10
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    business_impact: str = "medium"  # low, medium, high, critical
    recovery_actions: List[str] = field(default_factory=list)
    sla_target: float = 99.9  # Target uptime percentage


@dataclass
class HealthResult:
    """Enhanced health check result with detailed diagnostics"""
    name: str
    status: HealthStatus
    service_type: ServiceType
    value: Optional[float] = None
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    business_impact: str = "medium"
    trending: str = "stable"  # improving, stable, degrading
    confidence_score: float = 1.0  # AI confidence in health assessment
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CircuitBreakerState:
    """Enhanced circuit breaker with adaptive thresholds"""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    next_attempt_time: Optional[datetime] = None
    failure_rate: float = 0.0
    success_count: int = 0
    total_requests: int = 0
    adaptive_threshold: float = 5.0


@dataclass
class ServiceDependency:
    """Service dependency mapping with impact assessment"""
    service_name: str
    dependent_services: List[str]
    dependency_type: str = "hard"  # hard, soft, optional
    impact_weight: float = 1.0
    timeout_multiplier: float = 1.0


@dataclass
class HealthTrend:
    """Health trend analysis data"""
    service_name: str
    trend_direction: str = "stable"  # improving, stable, degrading
    trend_strength: float = 0.0  # -1.0 to 1.0
    prediction_confidence: float = 0.0
    estimated_failure_time: Optional[datetime] = None
    historical_values: deque = field(default_factory=lambda: deque(maxlen=100))


class HealthMonitor:
    """
    Industrial-grade health monitoring system with AI-powered diagnostics,
    predictive failure detection, and automated recovery mechanisms.
    
    Specialized for IA Influencer Agent Platform with content protection,
    revenue tracking, and multi-platform integration monitoring.
    """
    
    def __init__(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        db_engine: Optional[AsyncEngine] = None,
        check_interval: int = 30,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 300,
        enable_ai_diagnostics: bool = True,
        enable_predictive_analysis: bool = True
    ):
        self.redis_client = redis_client
        self.db_engine = db_engine
        self.check_interval = check_interval
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.enable_ai_diagnostics = enable_ai_diagnostics
        self.enable_predictive_analysis = enable_predictive_analysis
        
        # Health checks registry
        self._health_checks: Dict[str, HealthCheck] = {}
        self._health_results: Dict[str, HealthResult] = {}
        self._circuit_breakers: Dict[str, CircuitBreakerState] = {}
        
        # Dependency mapping
        self._service_dependencies: Dict[str, ServiceDependency] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
        
        # Monitoring state
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._trend_analysis_task: Optional[asyncio.Task] = None
        
        # AI-powered analytics
        self._health_trends: Dict[str, HealthTrend] = {}
        self._anomaly_thresholds: Dict[str, Tuple[float, float]] = {}
        self._baseline_metrics: Dict[str, Dict[str, float]] = {}
        
        # Recovery handlers
        self._recovery_handlers: Dict[str, Callable] = {}
        self._auto_recovery_enabled: bool = True
        
        # Performance tracking
        self._performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._sla_tracking: Dict[str, Dict[str, Any]] = {}
        
        # Business metrics integration
        self._business_health_weights = {
            ServiceType.CONTENT_PROTECTION: 0.3,
            ServiceType.AI_ENGINE: 0.25,
            ServiceType.REVENUE_TRACKING: 0.2,
            ServiceType.CORE_API: 0.15,
            ServiceType.USER_MANAGEMENT: 0.1
        }
        
        # Register default health checks
        self._register_default_health_checks()
        
    def _register_default_health_checks(self):
        """
Register default health checks for IA Influencer Agent Platform"""
        
        # Core API health
        self.register_health_check(HealthCheck(
            name="core_api",
            check_function=self._check_core_api_health,
            service_type=ServiceType.CORE_API,
            interval=15,
            timeout=5,
            business_impact="critical",
            sla_target=99.95,
            recovery_actions=["restart_api_service", "scale_horizontal"]
        ))
        
        # AI Engine health (fingerprinting, content analysis)
        self.register_health_check(HealthCheck(
            name="ai_fingerprint_engine",
            check_function=self._check_ai_engine_health,
            service_type=ServiceType.AI_ENGINE,
            interval=30,
            timeout=10,
            business_impact="critical",
            sla_target=99.9,
            recovery_actions=["restart_ai_workers", "reload_models"]
        ))
        
        # Content Protection Service
        self.register_health_check(HealthCheck(
            name="content_protection",
            check_function=self._check_content_protection_health,
            service_type=ServiceType.CONTENT_PROTECTION,
            interval=20,
            timeout=8,
            business_impact="high",
            sla_target=99.8,
            recovery_actions=["restart_protection_service", "clear_cache"]
        ))
        
        # Revenue Tracking System
        self.register_health_check(HealthCheck(
            name="revenue_tracking",
            check_function=self._check_revenue_tracking_health,
            service_type=ServiceType.REVENUE_TRACKING,
            interval=60,
            timeout=15,
            business_impact="high",
            sla_target=99.5,
            recovery_actions=["sync_revenue_data", "restart_tracking_service"]
        ))
        
        # Database Health
        self.register_health_check(HealthCheck(
            name="primary_database",
            check_function=self._check_database_health,
            service_type=ServiceType.DATABASE,
            interval=30,
            timeout=5,
            business_impact="critical",
            sla_target=99.99,
            recovery_actions=["restart_db_connections", "failover_to_replica"]
        ))
        
        # Redis Cache Health
        self.register_health_check(HealthCheck(
            name="redis_cache",
            check_function=self._check_redis_health,
            service_type=ServiceType.CACHE,
            interval=20,
            timeout=3,
            business_impact="medium",
            sla_target=99.9,
            recovery_actions=["clear_cache", "restart_redis"]
        ))
        
        # External APIs Health (Spotify, YouTube, etc.)
        self.register_health_check(HealthCheck(
            name="external_apis",
            check_function=self._check_external_apis_health,
            service_type=ServiceType.EXTERNAL_API,
            interval=120,
            timeout=20,
            business_impact="medium",
            sla_target=95.0,
            recovery_actions=["switch_api_provider", "use_cached_data"]
        ))
        
        # Notification Service Health
        self.register_health_check(HealthCheck(
            name="notification_service",
            check_function=self._check_notification_health,
            service_type=ServiceType.NOTIFICATION_SERVICE,
            interval=60,
            timeout=10,
            business_impact="low",
            sla_target=99.0,
            recovery_actions=["restart_notification_workers", "fallback_to_email"]
        ))

    async def _check_core_api_health(self) -> HealthResult:
        """Check core API health with endpoint validation"""
        start_time = time.time()
        
        try:
            # Test critical endpoints
            endpoints = [
                "/api/v1/health",
                "/api/v1/users/me",
                "/api/v1/content/fingerprint",
                "/api/v1/protection/status"
            ]
            
            total_response_time = 0
            successful_checks = 0
            detailed_results = {}
            
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints:
                    try:
                        endpoint_start = time.time()
                        async with session.get(
                            f"http://localhost:8000{endpoint}",
                            timeout=aiohttp.ClientTimeout(total=3)
                        ) as response:
                            endpoint_time = time.time() - endpoint_start
                            total_response_time += endpoint_time
                            
                            if response.status < 400:
                                successful_checks += 1
                                detailed_results[endpoint] = {
                                    "status": "healthy",
                                    "response_time": endpoint_time,
                                    "status_code": response.status
                                }
                            else:
                                detailed_results[endpoint] = {
                                    "status": "unhealthy",
                                    "response_time": endpoint_time,
                                    "status_code": response.status
                                }
                                
                    except Exception as e:
                        detailed_results[endpoint] = {
                            "status": "error",
                            "error": str(e)
                        }
            
            response_time = time.time() - start_time
            success_rate = successful_checks / len(endpoints)
            avg_response_time = total_response_time / len(endpoints) if endpoints else 0
            
            # Determine health status
            if success_rate >= 0.95 and avg_response_time < 2.0:
                status = HealthStatus.HEALTHY
                message = f"API healthy - {successful_checks}/{len(endpoints)} endpoints responsive"
            elif success_rate >= 0.8:
                status = HealthStatus.WARNING
                message = f"API degraded - {successful_checks}/{len(endpoints)} endpoints responsive"
            else:
                status = HealthStatus.CRITICAL
                message = f"API critical - Only {successful_checks}/{len(endpoints)} endpoints responsive"
            
            return HealthResult(
                name="core_api",
                status=status,
                service_type=ServiceType.CORE_API,
                value=success_rate,
                message=message,
                response_time=response_time,
                business_impact="critical",
                details={
                    "success_rate": success_rate,
                    "average_response_time": avg_response_time,
                    "endpoint_details": detailed_results,
                    "total_endpoints": len(endpoints)
                }
            )
            
        except Exception as e:
            return HealthResult(
                name="core_api",
                status=HealthStatus.CRITICAL,
                service_type=ServiceType.CORE_API,
                value=0.0,
                message=f"API health check failed: {str(e)}",
                response_time=time.time() - start_time,
                business_impact="critical",
                details={"error": str(e)}
            )

    async def _check_ai_engine_health(self) -> HealthResult:
        """Check AI fingerprinting engine health"""
        start_time = time.time()
        
        try:
            # Test AI engine components
            checks = {}
            
            # Check model loading and availability
            if self.redis_client:
                model_status = await self.redis_client.get("ai:models:loaded")
                checks["models_loaded"] = json.loads(model_status) if model_status else False
                
                # Check processing queue health
                queue_size = await self.redis_client.llen("ai:fingerprint:queue")
                processing_count = await self.redis_client.get("ai:processing:count") or 0
                
                checks["queue_size"] = queue_size
                checks["processing_count"] = int(processing_count)
                checks["queue_healthy"] = queue_size < 1000  # Threshold
            
            # Test fingerprint generation speed (mock test)
            fingerprint_start = time.time()
            test_result = await self._test_fingerprint_generation()
            fingerprint_time = time.time() - fingerprint_start
            
            checks["fingerprint_generation_time"] = fingerprint_time
            checks["fingerprint_test_success"] = test_result
            
            response_time = time.time() - start_time
            
            # Calculate health score
            health_score = self._calculate_ai_health_score(checks)
            
            if health_score >= 0.9:
                status = HealthStatus.HEALTHY
                message = "AI engine operating optimally"
            elif health_score >= 0.7:
                status = HealthStatus.WARNING
                message = "AI engine performance degraded"
            else:
                status = HealthStatus.CRITICAL
                message = "AI engine critical issues detected"
            
            return HealthResult(
                name="ai_fingerprint_engine",
                status=status,
                service_type=ServiceType.AI_ENGINE,
                value=health_score,
                message=message,
                response_time=response_time,
                business_impact="critical",
                details=checks
            )
            
        except Exception as e:
            return HealthResult(
                name="ai_fingerprint_engine",
                status=HealthStatus.CRITICAL,
                service_type=ServiceType.AI_ENGINE,
                value=0.0,
                message=f"AI engine health check failed: {str(e)}",
                response_time=time.time() - start_time,
                business_impact="critical",
                details={"error": str(e)}
            )

    async def _check_content_protection_health(self) -> HealthResult:
        """Check content protection service health"""
        start_time = time.time()
        
        try:
            checks = {}
            
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    # Check fingerprint database health
                    result = await conn.execute(text("""
                        SELECT 
                            COUNT(*) as total_fingerprints,
                            COUNT(CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN 1 END) as recent_fingerprints,
                            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_protections
                        FROM content_fingerprints
                    """))
                    
                    fingerprint_stats = result.fetchone()
                    if fingerprint_stats:
                        checks["total_fingerprints"] = fingerprint_stats.total_fingerprints
                        checks["recent_fingerprints"] = fingerprint_stats.recent_fingerprints
                        checks["active_protections"] = fingerprint_stats.active_protections
                    
                    # Check protection alerts
                    result = await conn.execute(text("""
                        SELECT 
                            COUNT(*) as total_alerts,
                            COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_alerts,
                            AVG(similarity_score) as avg_similarity
                        FROM protection_alerts
                        WHERE created_at > NOW() - INTERVAL '24 hours'
                    """))
                    
                    alert_stats = result.fetchone()
                    if alert_stats:
                        checks["daily_alerts"] = alert_stats.total_alerts
                        checks["pending_alerts"] = alert_stats.pending_alerts
                        checks["avg_similarity"] = float(alert_stats.avg_similarity or 0.0)
            
            # Test protection service response
            protection_response = await self._test_protection_service()
            checks["protection_service_responsive"] = protection_response
            
            response_time = time.time() - start_time
            
            # Calculate protection health score
            health_score = self._calculate_protection_health_score(checks)
            
            if health_score >= 0.9:
                status = HealthStatus.HEALTHY
                message = "Content protection fully operational"
            elif health_score >= 0.7:
                status = HealthStatus.WARNING
                message = "Content protection showing degraded performance"
            else:
                status = HealthStatus.CRITICAL
                message = "Content protection service critical"
            
            return HealthResult(
                name="content_protection",
                status=status,
                service_type=ServiceType.CONTENT_PROTECTION,
                value=health_score,
                message=message,
                response_time=response_time,
                business_impact="high",
                details=checks
            )
            
        except Exception as e:
            return HealthResult(
                name="content_protection",
                status=HealthStatus.CRITICAL,
                service_type=ServiceType.CONTENT_PROTECTION,
                value=0.0,
                message=f"Content protection health check failed: {str(e)}",
                response_time=time.time() - start_time,
                business_impact="high",
                details={"error": str(e)}
            )

    async def _check_revenue_tracking_health(self) -> HealthResult:
        """Check revenue tracking system health"""
        start_time = time.time()
        
        try:
            checks = {}
            
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    # Check revenue data freshness
                    result = await conn.execute(text("""
                        SELECT 
                            COUNT(*) as total_revenue_records,
                            COUNT(CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN 1 END) as recent_records,
                            SUM(revenue_amount) as total_revenue_24h,
                            COUNT(DISTINCT platform) as active_platforms
                        FROM revenue_tracking
                        WHERE created_at > NOW() - INTERVAL '24 hours'
                    """))
                    
                    revenue_stats = result.fetchone()
                    if revenue_stats:
                        checks["total_revenue_records"] = revenue_stats.total_revenue_records
                        checks["recent_records"] = revenue_stats.recent_records
                        checks["total_revenue_24h"] = float(revenue_stats.total_revenue_24h or 0.0)
                        checks["active_platforms"] = revenue_stats.active_platforms
                    
                    # Check for revenue sync issues
                    result = await conn.execute(text("""
                        SELECT platform, MAX(period_end) as last_sync
                        FROM revenue_tracking
                        GROUP BY platform
                    """))
                    
                    sync_status = {}
                    for row in result:
                        last_sync = row.last_sync
                        hours_since_sync = (datetime.utcnow() - last_sync).total_seconds() / 3600
                        sync_status[row.platform] = {
                            "last_sync": last_sync.isoformat(),
                            "hours_since_sync": hours_since_sync,
                            "is_current": hours_since_sync < 6  # Should sync every 6 hours
                        }
                    
                    checks["platform_sync_status"] = sync_status
            
            # Test external API connections for revenue data
            api_health = await self._test_revenue_apis()
            checks["external_api_health"] = api_health
            
            response_time = time.time() - start_time
            
            # Calculate revenue system health score
            health_score = self._calculate_revenue_health_score(checks)
            
            if health_score >= 0.9:
                status = HealthStatus.HEALTHY
                message = "Revenue tracking system fully operational"
            elif health_score >= 0.7:
                status = HealthStatus.WARNING
                message = "Revenue tracking showing delays or issues"
            else:
                status = HealthStatus.CRITICAL
                message = "Revenue tracking system critical"
            
            return HealthResult(
                name="revenue_tracking",
                status=status,
                service_type=ServiceType.REVENUE_TRACKING,
                value=health_score,
                message=message,
                response_time=response_time,
                business_impact="high",
                details=checks
            )
            
        except Exception as e:
            return HealthResult(
                name="revenue_tracking",
                status=HealthStatus.CRITICAL,
                service_type=ServiceType.REVENUE_TRACKING,
                value=0.0,
                message=f"Revenue tracking health check failed: {str(e)}",
                response_time=time.time() - start_time,
                business_impact="high",
                details={"error": str(e)}
            )

    async def _check_database_health(self) -> HealthResult:
        """Check primary database health"""
        start_time = time.time()
        
        try:
            checks = {}
            
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    # Test basic connectivity
                    await conn.execute(text("SELECT 1"))
                    checks["connectivity"] = True
                    
                    # Check connection pool
                    pool_status = self.db_engine.pool.status()
                    checks["pool_size"] = pool_status.pool_size
                    checks["checked_in"] = pool_status.checked_in
                    checks["checked_out"] = pool_status.checked_out
                    checks["pool_utilization"] = (pool_status.checked_out / pool_status.pool_size) * 100
                    
                    # Check database performance
                    perf_start = time.time()
                    result = await conn.execute(text("""
                        SELECT 
                            pg_database_size(current_database()) as db_size,
                            (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                            (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle_connections
                    """))
                    query_time = time.time() - perf_start
                    
                    db_stats = result.fetchone()
                    if db_stats:
                        checks["database_size_bytes"] = db_stats.db_size
                        checks["active_connections"] = db_stats.active_connections
                        checks["idle_connections"] = db_stats.idle_connections
                        checks["query_response_time"] = query_time
                    
                    # Check for slow queries
                    result = await conn.execute(text("""
                        SELECT count(*) as slow_queries
                        FROM pg_stat_statements 
                        WHERE mean_exec_time > 1000
                        LIMIT 1
                    """))
                    
                    slow_query_result = result.fetchone()
                    if slow_query_result:
                        checks["slow_queries"] = slow_query_result.slow_queries
            
            response_time = time.time() - start_time
            
            # Calculate database health score
            health_score = self._calculate_database_health_score(checks)
            
            if health_score >= 0.95:
                status = HealthStatus.HEALTHY
                message = "Database performing optimally"
            elif health_score >= 0.8:
                status = HealthStatus.WARNING
                message = "Database showing performance issues"
            else:
                status = HealthStatus.CRITICAL
                message = "Database critical performance issues"
            
            return HealthResult(
                name="primary_database",
                status=status,
                service_type=ServiceType.DATABASE,
                value=health_score,
                message=message,
                response_time=response_time,
                business_impact="critical",
                details=checks
            )
            
        except Exception as e:
            return HealthResult(
                name="primary_database",
                status=HealthStatus.CRITICAL,
                service_type=ServiceType.DATABASE,
                value=0.0,
                message=f"Database health check failed: {str(e)}",
                response_time=time.time() - start_time,
                business_impact="critical",
                details={"error": str(e)}
            )

    async def _check_redis_health(self) -> HealthResult:
        """Check Redis cache health"""
        start_time = time.time()
        
        try:
            checks = {}
            
            if self.redis_client:
                # Test basic connectivity
                await self.redis_client.ping()
                checks["connectivity"] = True
                
                # Get Redis info
                redis_info = await self.redis_client.info()
                checks["redis_version"] = redis_info.get("redis_version")
                checks["connected_clients"] = redis_info.get("connected_clients")
                checks["used_memory"] = redis_info.get("used_memory")
                checks["used_memory_human"] = redis_info.get("used_memory_human")
                checks["keyspace_hits"] = redis_info.get("keyspace_hits", 0)
                checks["keyspace_misses"] = redis_info.get("keyspace_misses", 0)
                
                # Calculate cache hit ratio
                total_ops = checks["keyspace_hits"] + checks["keyspace_misses"]
                hit_ratio = (checks["keyspace_hits"] / total_ops) * 100 if total_ops > 0 else 0
                checks["cache_hit_ratio"] = hit_ratio
                
                # Test performance
                perf_start = time.time()
                await self.redis_client.set("health_check", "test", ex=10)
                test_value = await self.redis_client.get("health_check")
                perf_time = time.time() - perf_start
                
                checks["performance_test_time"] = perf_time
                checks["performance_test_success"] = test_value == "test"
                
                # Check memory usage
                maxmemory = redis_info.get("maxmemory", 0)
                if maxmemory > 0:
                    memory_usage_percent = (checks["used_memory"] / maxmemory) * 100
                    checks["memory_usage_percent"] = memory_usage_percent
            
            response_time = time.time() - start_time
            
            # Calculate Redis health score
            health_score = self._calculate_redis_health_score(checks)
            
            if health_score >= 0.9:
                status = HealthStatus.HEALTHY
                message = "Redis cache performing well"
            elif health_score >= 0.7:
                status = HealthStatus.WARNING
                message = "Redis cache showing performance issues"
            else:
                status = HealthStatus.CRITICAL
                message = "Redis cache critical issues"
            
            return HealthResult(
                name="redis_cache",
                status=status,
                service_type=ServiceType.CACHE,
                value=health_score,
                message=message,
                response_time=response_time,
                business_impact="medium",
                details=checks
            )
            
        except Exception as e:
            return HealthResult(
                name="redis_cache",
                status=HealthStatus.CRITICAL,
                service_type=ServiceType.CACHE,
                value=0.0,
                message=f"Redis health check failed: {str(e)}",
                response_time=time.time() - start_time,
                business_impact="medium",
                details={"error": str(e)}
            )
        self.register_check(HealthCheck(
            name="system_cpu",
            check_function=self._check_cpu_usage,
            interval=30,
            warning_threshold=80.0,
            critical_threshold=95.0
        ))
        
        self.register_check(HealthCheck(
            name="system_memory",
            check_function=self._check_memory_usage,
            interval=30,
            warning_threshold=85.0,
            critical_threshold=95.0
        ))
        
        self.register_check(HealthCheck(
            name="system_disk",
            check_function=self._check_disk_usage,
            interval=60,
            warning_threshold=85.0,
            critical_threshold=95.0
        ))
        
        # Database health check
        if self.db_engine:
            self.register_check(HealthCheck(
                name="database_connection",
                check_function=self._check_database_health,
                interval=30,
                timeout=10
            ))
            
        # Redis health check
        if self.redis_client:
            self.register_check(HealthCheck(
                name="redis_connection",
                check_function=self._check_redis_health,
                interval=30,
                timeout=5
            ))
            
        # Application health checks
        self.register_check(HealthCheck(
            name="api_endpoints",
            check_function=self._check_api_endpoints,
            interval=60,
            timeout=15
        ))
        
        self.register_check(HealthCheck(
            name="fingerprint_service",
            check_function=self._check_fingerprint_service,
            interval=120,
            timeout=30,
            dependencies=["database_connection", "redis_connection"]
        ))
        
        self.register_check(HealthCheck(
            name="protection_alerts",
            check_function=self._check_protection_alerts,
            interval=300,
            dependencies=["database_connection"]
        ))
        
    async def start_monitoring(self):
        """Start health monitoring"""
        if self._monitoring:
            logger.warning("Health monitoring already running")
            return
            
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")
        
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")
        
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                await self._run_health_checks()
                await self._process_results()
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(5)  # Backoff on error
                
    async def _run_health_checks(self):
        """Run all enabled health checks"""
        tasks = []
        
        for check_name, health_check in self._health_checks.items():
            if not health_check.enabled:
                continue
                
            # Check circuit breaker
            if self._is_circuit_breaker_open(check_name):
                continue
                
            # Check dependencies
            if not self._check_dependencies(health_check):
                self._health_results[check_name] = HealthResult(
                    name=check_name,
                    status=HealthStatus.CRITICAL,
                    message="Dependencies not satisfied"
                )
                continue
                
            # Run health check
            task = asyncio.create_task(
                self._execute_health_check(health_check)
            )
            tasks.append(task)
            
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    check_name = list(self._health_checks.keys())[i]
                    logger.error(f"Health check '{check_name}' failed with exception: {result}")
                    self._handle_circuit_breaker(check_name, False)
                    
    async def _execute_health_check(self, health_check: HealthCheck) -> HealthResult:
        """Execute a single health check with timeout"""
        start_time = time.time()
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                health_check.check_function(),
                timeout=health_check.timeout
            )
            
            response_time = time.time() - start_time
            
            if isinstance(result, HealthResult):
                result.response_time = response_time
                self._health_results[health_check.name] = result
                self._handle_circuit_breaker(health_check.name, result.status != HealthStatus.CRITICAL)
                return result
            else:
                # Convert simple return value to HealthResult
                status = self._determine_status(result, health_check)
                result_obj = HealthResult(
                    name=health_check.name,
                    status=status,
                    value=result if isinstance(result, (int, float)) else None,
                    response_time=response_time
                )
                self._health_results[health_check.name] = result_obj
                self._handle_circuit_breaker(health_check.name, status != HealthStatus.CRITICAL)
                return result_obj
                
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            result = HealthResult(
                name=health_check.name,
                status=HealthStatus.CRITICAL,
                message=f"Timeout after {health_check.timeout}s",
                response_time=response_time
            )
            self._health_results[health_check.name] = result
            self._handle_circuit_breaker(health_check.name, False)
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            result = HealthResult(
                name=health_check.name,
                status=HealthStatus.CRITICAL,
                message=f"Exception: {str(e)}",
                response_time=response_time
            )
            self._health_results[health_check.name] = result
            self._handle_circuit_breaker(health_check.name, False)
            return result
            
    def _determine_status(self, value: Any, health_check: HealthCheck) -> HealthStatus:
        """Determine health status based on value and thresholds"""
        if not isinstance(value, (int, float)):
            return HealthStatus.HEALTHY
            
        if value >= health_check.critical_threshold:
            return HealthStatus.CRITICAL
        elif value >= health_check.warning_threshold:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
            
    def _check_dependencies(self, health_check: HealthCheck) -> bool:
        """
Check if all dependencies are satisfied"""
        for dep_name in health_check.dependencies:
            if dep_name not in self._health_results:
                return False
            if self._health_results[dep_name].status == HealthStatus.CRITICAL:
                return False
        return True
        
    def _is_circuit_breaker_open(self, check_name: str) -> bool:
        """
Check if circuit breaker is open for a health check"""
        if check_name not in self._circuit_breakers:
            return False
            
        cb_state = self._circuit_breakers[check_name]
        
        if cb_state.state == "open":
            if cb_state.next_attempt_time and datetime.utcnow() > cb_state.next_attempt_time:
                cb_state.state = "half_open"
                return False
            return True
            
        return False
        
    def _handle_circuit_breaker(self, check_name: str, success: bool):
        """Handle circuit breaker state transitions"""
        if check_name not in self._circuit_breakers:
            self._circuit_breakers[check_name] = CircuitBreakerState()
            
        cb_state = self._circuit_breakers[check_name]
        
        if success:
            if cb_state.state == "half_open":
                cb_state.state = "closed"
                cb_state.failure_count = 0
            elif cb_state.state == "closed":
                cb_state.failure_count = max(0, cb_state.failure_count - 1)
        else:
            cb_state.failure_count += 1
            cb_state.last_failure_time = datetime.utcnow()
            
            if cb_state.failure_count >= self.circuit_breaker_threshold:
                cb_state.state = "open"
                cb_state.next_attempt_time = datetime.utcnow() + timedelta(seconds=self.circuit_breaker_timeout)
                logger.warning(f"Circuit breaker opened for health check: {check_name}")
                
    async def _process_results(self):
        """Process health check results and trigger recovery if needed"""
        overall_status = self.get_overall_status()
        
        # Store results in Redis
        if self.redis_client:
            try:
                health_data = {
                    "overall_status": overall_status.value,
                    "timestamp": datetime.utcnow().isoformat(),
                    "checks": {
                        name: {
                            "status": result.status.value,
                            "value": result.value,
                            "message": result.message,
                            "response_time": result.response_time,
                            "details": result.details
                        }
                        for name, result in self._health_results.items()
                    }
                }
                
                await self.redis_client.set(
                    "health:current",
                    json.dumps(health_data),
                    ex=300  # 5 minutes TTL
                )
                
                # Store in time series
                await self.redis_client.zadd(
                    "health:history",
                    {json.dumps(health_data): time.time()}
                )
                
                # Cleanup old history
                cutoff = time.time() - (7 * 24 * 3600)  # 7 days
                await self.redis_client.zremrangebyscore("health:history", 0, cutoff)
                
            except Exception as e:
                logger.error(f"Error storing health results to Redis: {e}")
                
        # Trigger recovery handlers
        for check_name, result in self._health_results.items():
            if result.status == HealthStatus.CRITICAL and check_name in self._recovery_handlers:
                try:
                    await self._recovery_handlers[check_name](result)
                except Exception as e:
                    logger.error(f"Error in recovery handler for {check_name}: {e}")
                    
    # System health check implementations
    async def _check_cpu_usage(self) -> float:
        """Check CPU usage"""
        return psutil.cpu_percent(interval=1)
        
    async def _check_memory_usage(self) -> float:
        """
Check memory usage"""
        return psutil.virtual_memory().percent
        
    async def _check_disk_usage(self) -> float:
        """
Check disk usage"""
        disk_usage = psutil.disk_usage('/')
        return (disk_usage.used / disk_usage.total) * 100
        
    async def _check_database_health(self) -> HealthResult:
        """
Check database connection and performance"""
        if not self.db_engine:
            return HealthResult(
                name="database_connection",
                status=HealthStatus.CRITICAL,
                message="Database engine not configured"
            )
            
        try:
            async with self.db_engine.begin() as conn:
                # Test connection
                start_time = time.time()
                result = await conn.execute(text("SELECT 1"))
                query_time = time.time() - start_time
                
                # Check connection count
                result = await conn.execute(text(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                ))
                active_connections = result.scalar()
                
                # Check database size
                result = await conn.execute(text("SELECT pg_database_size(current_database())"))
                db_size = result.scalar()
                
                status = HealthStatus.HEALTHY
                if query_time > 5.0:
                    status = HealthStatus.CRITICAL
                elif query_time > 2.0:
                    status = HealthStatus.WARNING
                    
                return HealthResult(
                    name="database_connection",
                    status=status,
                    value=query_time,
                    message=f"Query time: {query_time:.3f}s",
                    details={
                        "active_connections": active_connections,
                        "database_size": db_size,
                        "query_time": query_time
                    }
                )
                
        except Exception as e:
            return HealthResult(
                name="database_connection",
                status=HealthStatus.CRITICAL,
                message=f"Database error: {str(e)}"
            )
            
    async def _check_redis_health(self) -> HealthResult:
        """Check Redis connection and performance"""
        if not self.redis_client:
            return HealthResult(
                name="redis_connection",
                status=HealthStatus.CRITICAL,
                message="Redis client not configured"
            )
            
        try:
            start_time = time.time()
            await self.redis_client.ping()
            ping_time = time.time() - start_time
            
            # Get Redis info
            info = await self.redis_client.info()
            used_memory = info.get('used_memory', 0)
            connected_clients = info.get('connected_clients', 0)
            
            status = HealthStatus.HEALTHY
            if ping_time > 1.0:
                status = HealthStatus.CRITICAL
            elif ping_time > 0.5:
                status = HealthStatus.WARNING
                
            return HealthResult(
                name="redis_connection",
                status=status,
                value=ping_time,
                message=f"Ping time: {ping_time:.3f}s",
                details={
                    "used_memory": used_memory,
                    "connected_clients": connected_clients,
                    "ping_time": ping_time
                }
            )
            
        except Exception as e:
            return HealthResult(
                name="redis_connection",
                status=HealthStatus.CRITICAL,
                message=f"Redis error: {str(e)}"
            )
            
    async def _check_api_endpoints(self) -> HealthResult:
        """Check critical API endpoints"""
        endpoints = [
            "http://localhost:8000/health",
            "http://localhost:8000/api/v1/status"
        ]
        
        failed_endpoints = []
        total_response_time = 0
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        response_time = time.time() - start_time
                        total_response_time += response_time
                        
                        if response.status >= 400:
                            failed_endpoints.append(f"{endpoint}: {response.status}")
                            
                except Exception as e:
                    failed_endpoints.append(f"{endpoint}: {str(e)}")
                    
        avg_response_time = total_response_time / len(endpoints) if endpoints else 0
        
        if failed_endpoints:
            status = HealthStatus.CRITICAL
            message = f"Failed endpoints: {', '.join(failed_endpoints)}"
        elif avg_response_time > 5.0:
            status = HealthStatus.WARNING
            message = f"Slow response time: {avg_response_time:.3f}s"
        else:
            status = HealthStatus.HEALTHY
            message = f"All endpoints healthy, avg response: {avg_response_time:.3f}s"
            
        return HealthResult(
            name="api_endpoints",
            status=status,
            value=avg_response_time,
            message=message,
            details={
                "failed_endpoints": failed_endpoints,
                "average_response_time": avg_response_time
            }
        )
        
    async def _check_fingerprint_service(self) -> HealthResult:
        """Check fingerprint service health"""
        if not self.db_engine:
            return HealthResult(
                name="fingerprint_service",
                status=HealthStatus.CRITICAL,
                message="Database not available"
            )
            
        try:
            async with self.db_engine.begin() as conn:
                # Check recent fingerprint operations
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM content_fingerprints 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                """))
                recent_count = result.scalar()
                
                # Check processing queue size
                if self.redis_client:
                    queue_size = await self.redis_client.llen("fingerprint_queue")
                else:
                    queue_size = 0
                    
                status = HealthStatus.HEALTHY
                message = f"Recent fingerprints: {recent_count}, Queue: {queue_size}"
                
                if queue_size > 1000:
                    status = HealthStatus.CRITICAL
                    message += " - Queue overloaded"
                elif queue_size > 500:
                    status = HealthStatus.WARNING
                    message += " - Queue high"
                    
                return HealthResult(
                    name="fingerprint_service",
                    status=status,
                    value=queue_size,
                    message=message,
                    details={
                        "recent_fingerprints": recent_count,
                        "queue_size": queue_size
                    }
                )
                
        except Exception as e:
            return HealthResult(
                name="fingerprint_service",
                status=HealthStatus.CRITICAL,
                message=f"Fingerprint service error: {str(e)}"
            )
            
    async def _check_protection_alerts(self) -> HealthResult:
        """Check protection alerts system"""
        if not self.db_engine:
            return HealthResult(
                name="protection_alerts",
                status=HealthStatus.CRITICAL,
                message="Database not available"
            )
            
        try:
            async with self.db_engine.begin() as conn:
                # Check recent alerts
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM protection_alerts 
                    WHERE created_at > NOW() - INTERVAL '1 day'
                """))
                daily_alerts = result.scalar()
                
                # Check pending alerts
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM protection_alerts 
                    WHERE status = 'pending'
                """))
                pending_alerts = result.scalar()
                
                status = HealthStatus.HEALTHY
                message = f"Daily alerts: {daily_alerts}, Pending: {pending_alerts}"
                
                if pending_alerts > 100:
                    status = HealthStatus.CRITICAL
                    message += " - Too many pending alerts"
                elif pending_alerts > 50:
                    status = HealthStatus.WARNING
                    message += " - High pending alerts"
                    
                return HealthResult(
                    name="protection_alerts",
                    status=status,
                    value=pending_alerts,
                    message=message,
                    details={
                        "daily_alerts": daily_alerts,
                        "pending_alerts": pending_alerts
                    }
                )
                
        except Exception as e:
            return HealthResult(
                name="protection_alerts",
                status=HealthStatus.CRITICAL,
                message=f"Protection alerts error: {str(e)}"
            )
            
    # Public interface methods
    def register_check(self, health_check: HealthCheck):
        """Register a new health check"""
        self._health_checks[health_check.name] = health_check
        logger.info(f"Registered health check: {health_check.name}")
        
    def unregister_check(self, check_name: str):
        """Unregister a health check"""
        if check_name in self._health_checks:
            del self._health_checks[check_name]
            if check_name in self._health_results:
                del self._health_results[check_name]
            logger.info(f"Unregistered health check: {check_name}")
            
    def register_recovery_handler(self, check_name: str, handler: Callable):
        """Register a recovery handler for a health check"""
        self._recovery_handlers[check_name] = handler
        logger.info(f"Registered recovery handler for: {check_name}")
        
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status"""
        if not self._health_results:
            return HealthStatus.UNKNOWN
            
        statuses = [result.status for result in self._health_results.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
            
    def get_health_summary(self) -> Dict[str, Any]:
        """
Get comprehensive health summary"""
        overall_status = self.get_overall_status()
        
        status_counts = {
            "healthy": 0,
            "warning": 0,
            "critical": 0,
            "unknown": 0
        }
        
        for result in self._health_results.values():
            status_counts[result.status.value] += 1
            
        return {
            "overall_status": overall_status.value,
            "total_checks": len(self._health_checks),
            "enabled_checks": len([hc for hc in self._health_checks.values() if hc.enabled]),
            "status_counts": status_counts,
            "last_check": max([r.timestamp for r in self._health_results.values()]).isoformat() if self._health_results else None,
            "monitoring_active": self._monitoring
        }
        
    def get_detailed_results(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed health check results"""
        return {
            name: {
                "status": result.status.value,
                "value": result.value,
                "message": result.message,
                "timestamp": result.timestamp.isoformat(),
                "response_time": result.response_time,
                "details": result.details
            }
            for name, result in self._health_results.items()
        }
