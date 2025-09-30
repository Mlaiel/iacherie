"""
🛡️ Health Check Orchestrator - Enterprise Creator Economy
==========================================================

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

Enterprise health check orchestrator with comprehensive monitoring
Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import time
import statistics
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import aiohttp

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class CheckType(Enum):
    """Types of health checks"""
    HTTP_ENDPOINT = "http_endpoint"
    DATABASE_CONNECTION = "database_connection"
    CACHE_CONNECTIVITY = "cache_connectivity"
    MESSAGE_QUEUE = "message_queue"
    EXTERNAL_API = "external_api"
    DISK_SPACE = "disk_space"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CUSTOM = "custom"
    
    # Creator Economy specific
    CREATOR_WORKFLOW = "creator_workflow"
    CONTENT_PROCESSING = "content_processing"
    PAYMENT_SYSTEM = "payment_system"
    REVENUE_TRACKING = "revenue_tracking"
    CREATOR_DASHBOARD = "creator_dashboard"


@dataclass
class HealthCheckConfig:
    """Configuration for a health check"""
    check_id: str
    name: str
    check_type: CheckType
    
    # Check parameters
    endpoint_url: Optional[str] = None
    timeout_seconds: int = 10
    interval_seconds: int = 30
    retry_count: int = 3
    
    # Thresholds
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    
    # Headers and authentication
    headers: Dict[str, str] = field(default_factory=dict)
    auth_token: Optional[str] = None
    
    # Custom check function
    custom_check_function: Optional[Callable] = None
    
    # Creator Economy specific
    creator_impact_level: str = "medium"  # "critical", "high", "medium", "low"
    affects_revenue: bool = False
    affects_content_creation: bool = False
    creator_facing: bool = False


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    check_id: str
    timestamp: datetime
    status: HealthStatus
    response_time_ms: float
    
    # Check details
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Metrics
    value: Optional[float] = None  # For numeric checks (CPU, memory, etc.)
    unit: Optional[str] = None
    
    # Creator Economy impact
    creator_impact_score: float = 0.0
    revenue_impact_estimate: float = 0.0


@dataclass
class ServiceHealth:
    """Overall health of a service"""
    service_id: str
    service_name: str
    overall_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Check results
    check_results: Dict[str, HealthCheckResult] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Aggregated metrics
    total_checks: int = 0
    healthy_checks: int = 0
    warning_checks: int = 0
    critical_checks: int = 0
    
    # Performance metrics
    average_response_time_ms: float = 0.0
    availability_percentage: float = 100.0
    
    # Creator Economy metrics
    creator_impact_level: str = "medium"
    creator_services_affected: List[str] = field(default_factory=list)
    revenue_systems_affected: List[str] = field(default_factory=list)


class HealthCheckOrchestrator:
    """
    🏥 Enterprise Health Check Orchestrator for Creator Economy
    
    Orchestrateur health checks complets avec:
    - Deep health validation
    - Creator journey health checks
    - Dependency health monitoring
    - Business logic health validation
    - Health metric aggregation
    
    Features:
    - Comprehensive multi-layer health monitoring
    - Creator-aware health checks with business impact analysis
    - Intelligent health aggregation and correlation
    - Real-time health alerting with escalation
    - Performance-based health scoring and trending
    """
    
    def __init__(self):
        self.orchestrator_id = str(uuid.uuid4())
        self.health_checks: Dict[str, HealthCheckConfig] = {}
        self.services: Dict[str, ServiceHealth] = {}
        self.check_results_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Execution management
        self.monitoring_active = False
        self.check_executors: Dict[str, asyncio.Task] = {}
        
        # Aggregation and alerting
        self.alert_handlers: List[Callable] = []
        self.health_aggregation_rules: Dict[str, Any] = {}
        
        # Metrics
        self.global_metrics = {
            "total_checks": 0,
            "healthy_services": 0,
            "warning_services": 0,
            "critical_services": 0,
            "average_response_time_ms": 0.0,
            "overall_availability": 100.0
        }
        
        # Creator Economy specific
        self.creator_health_mapping: Dict[str, List[str]] = {}
        self.revenue_critical_checks: List[str] = []
        self.creator_journey_checks: Dict[str, List[str]] = {}
        
        logger.info(f"Health Check Orchestrator initialized: {self.orchestrator_id}")
    
    async def initialize(self) -> bool:
        """
        Initialize health check orchestrator
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing Health Check Orchestrator...")
            
            # Setup default health checks
            await self._setup_default_health_checks()
            
            # Configure Creator Economy mappings
            await self._setup_creator_health_mappings()
            
            # Initialize health aggregation rules
            await self._setup_health_aggregation_rules()
            
            # Start monitoring
            await self._start_health_monitoring()
            
            # Setup alerting
            await self._setup_alerting()
            
            logger.info("Health Check Orchestrator successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize health check orchestrator: {str(e)}")
            return False
    
    async def _setup_default_health_checks(self):
        """Setup default health checks for key services"""
        
        # Creator Dashboard Health Check
        dashboard_check = HealthCheckConfig(
            check_id="creator_dashboard_health",
            name="Creator Dashboard Health",
            check_type=CheckType.HTTP_ENDPOINT,
            endpoint_url="https://dashboard.ainflue.com/health",
            timeout_seconds=5,
            interval_seconds=30,
            warning_threshold=1000.0,  # ms
            critical_threshold=3000.0,  # ms
            headers={"User-Agent": "HealthCheck/1.0"},
            creator_impact_level="critical",
            affects_revenue=False,
            affects_content_creation=True,
            creator_facing=True
        )
        
        # Payment System Health Check
        payment_check = HealthCheckConfig(
            check_id="payment_system_health",
            name="Payment System Health",
            check_type=CheckType.HTTP_ENDPOINT,
            endpoint_url="https://payments.ainflue.com/health",
            timeout_seconds=3,
            interval_seconds=15,  # More frequent for payments
            warning_threshold=500.0,
            critical_threshold=2000.0,
            creator_impact_level="critical",
            affects_revenue=True,
            affects_content_creation=False,
            creator_facing=False
        )
        
        # Content Processing Health Check
        content_check = HealthCheckConfig(
            check_id="content_processing_health",
            name="Content Processing Health",
            check_type=CheckType.CONTENT_PROCESSING,
            timeout_seconds=10,
            interval_seconds=60,
            creator_impact_level="high",
            affects_revenue=False,
            affects_content_creation=True,
            creator_facing=True
        )
        
        # Database Health Check
        database_check = HealthCheckConfig(
            check_id="primary_database_health",
            name="Primary Database Health",
            check_type=CheckType.DATABASE_CONNECTION,
            timeout_seconds=5,
            interval_seconds=30,
            warning_threshold=100.0,
            critical_threshold=500.0,
            creator_impact_level="critical",
            affects_revenue=True,
            affects_content_creation=True,
            creator_facing=False
        )
        
        # Cache System Health Check
        cache_check = HealthCheckConfig(
            check_id="cache_system_health",
            name="Cache System Health",
            check_type=CheckType.CACHE_CONNECTIVITY,
            timeout_seconds=2,
            interval_seconds=45,
            warning_threshold=50.0,
            critical_threshold=200.0,
            creator_impact_level="medium",
            affects_revenue=False,
            affects_content_creation=False,
            creator_facing=False
        )
        
        # Analytics API Health Check
        analytics_check = HealthCheckConfig(
            check_id="analytics_api_health",
            name="Analytics API Health",
            check_type=CheckType.HTTP_ENDPOINT,
            endpoint_url="https://analytics.ainflue.com/health",
            timeout_seconds=8,
            interval_seconds=60,
            warning_threshold=2000.0,
            critical_threshold=5000.0,
            creator_impact_level="medium",
            affects_revenue=False,
            affects_content_creation=False,
            creator_facing=True
        )
        
        # Creator Workflow Health Check (Custom)
        workflow_check = HealthCheckConfig(
            check_id="creator_workflow_health",
            name="Creator Workflow End-to-End Health",
            check_type=CheckType.CREATOR_WORKFLOW,
            timeout_seconds=30,
            interval_seconds=300,  # Every 5 minutes
            creator_impact_level="critical",
            affects_revenue=True,
            affects_content_creation=True,
            creator_facing=True
        )
        
        # Revenue Tracking Health Check
        revenue_check = HealthCheckConfig(
            check_id="revenue_tracking_health",
            name="Revenue Tracking Health",
            check_type=CheckType.REVENUE_TRACKING,
            timeout_seconds=15,
            interval_seconds=120,  # Every 2 minutes
            creator_impact_level="critical",
            affects_revenue=True,
            affects_content_creation=False,
            creator_facing=False
        )
        
        # Store health checks
        checks = [
            dashboard_check, payment_check, content_check, database_check,
            cache_check, analytics_check, workflow_check, revenue_check
        ]
        
        for check in checks:
            self.health_checks[check.check_id] = check
            
            if check.affects_revenue:
                self.revenue_critical_checks.append(check.check_id)
        
        logger.info(f"Setup {len(checks)} default health checks")
    
    async def _setup_creator_health_mappings(self):
        """Setup Creator Economy health mappings"""
        
        # Map Creator services to health checks
        self.creator_health_mapping = {
            "creator_dashboard": ["creator_dashboard_health", "cache_system_health"],
            "content_creation": ["content_processing_health", "creator_workflow_health"],
            "monetization": ["payment_system_health", "revenue_tracking_health"],
            "analytics": ["analytics_api_health", "primary_database_health"],
            "user_experience": ["creator_dashboard_health", "content_processing_health"]
        }
        
        # Define Creator journey health checks
        self.creator_journey_checks = {
            "onboarding": ["creator_dashboard_health", "primary_database_health"],
            "content_upload": ["content_processing_health", "creator_workflow_health"],
            "audience_engagement": ["analytics_api_health", "cache_system_health"],
            "monetization": ["payment_system_health", "revenue_tracking_health"],
            "collaboration": ["creator_dashboard_health", "primary_database_health"]
        }
        
        logger.info("Creator health mappings configured")
    
    async def _setup_health_aggregation_rules(self):
        """Setup rules for aggregating health across services"""
        
        self.health_aggregation_rules = {
            "service_level": {
                "healthy_threshold": 0.8,    # 80% of checks must be healthy
                "warning_threshold": 0.6,    # 60% of checks must be non-critical
                "critical_threshold": 0.4    # Below 40% healthy = critical
            },
            "creator_impact": {
                "critical_service_weight": 3,
                "high_service_weight": 2,
                "medium_service_weight": 1,
                "low_service_weight": 0.5
            },
            "revenue_impact": {
                "revenue_critical_multiplier": 5,
                "revenue_affecting_multiplier": 3,
                "non_revenue_multiplier": 1
            }
        }
        
        logger.info("Health aggregation rules configured")
    
    async def _start_health_monitoring(self):
        """Start health monitoring for all configured checks"""
        self.monitoring_active = True
        
        # Start individual check executors
        for check_id, check_config in self.health_checks.items():
            task = asyncio.create_task(self._health_check_executor(check_config))
            self.check_executors[check_id] = task
        
        # Start aggregation and alerting loops
        asyncio.create_task(self._health_aggregation_loop())
        asyncio.create_task(self._alerting_loop())
        
        logger.info(f"Started health monitoring for {len(self.health_checks)} checks")
    
    async def _setup_alerting(self):
        """Setup health alerting mechanisms"""
        
        # Add default alert handlers
        self.alert_handlers.append(self._log_alert_handler)
        # In real implementation, would add email, Slack, PagerDuty handlers
        
        logger.info("Health alerting configured")
    
    async def _health_check_executor(self, check_config: HealthCheckConfig):
        """Execute individual health check continuously"""
        while self.monitoring_active:
            try:
                # Perform health check
                result = await self._perform_health_check(check_config)
                
                # Store result
                self.check_results_history[check_config.check_id].append(result)
                
                # Update service health
                await self._update_service_health(check_config, result)
                
                # Check for alerts
                await self._check_health_alerts(check_config, result)
                
                # Wait for next check
                await asyncio.sleep(check_config.interval_seconds)
                
            except Exception as e:
                logger.error(f"Health check executor error for {check_config.check_id}: {str(e)}")
                await asyncio.sleep(check_config.interval_seconds)
    
    async def _perform_health_check(self, check_config: HealthCheckConfig) -> HealthCheckResult:
        """Perform individual health check"""
        start_time = time.time()
        
        try:
            if check_config.check_type == CheckType.HTTP_ENDPOINT:
                result = await self._http_health_check(check_config)
            elif check_config.check_type == CheckType.DATABASE_CONNECTION:
                result = await self._database_health_check(check_config)
            elif check_config.check_type == CheckType.CACHE_CONNECTIVITY:
                result = await self._cache_health_check(check_config)
            elif check_config.check_type == CheckType.CONTENT_PROCESSING:
                result = await self._content_processing_health_check(check_config)
            elif check_config.check_type == CheckType.CREATOR_WORKFLOW:
                result = await self._creator_workflow_health_check(check_config)
            elif check_config.check_type == CheckType.REVENUE_TRACKING:
                result = await self._revenue_tracking_health_check(check_config)
            elif check_config.check_type == CheckType.CUSTOM and check_config.custom_check_function:
                result = await check_config.custom_check_function()
            else:
                result = await self._generic_health_check(check_config)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            result.response_time_ms = response_time_ms
            
            # Determine status based on thresholds
            if result.status == HealthStatus.UNKNOWN:
                result.status = self._determine_health_status(check_config, response_time_ms, result.value)
            
            return result
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.CRITICAL,
                response_time_ms=response_time_ms,
                message="Health check failed",
                error_message=str(e)
            )
    
    async def _http_health_check(self, check_config: HealthCheckConfig) -> HealthCheckResult:
        """Perform HTTP endpoint health check"""
        try:
            timeout = aiohttp.ClientTimeout(total=check_config.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    check_config.endpoint_url,
                    headers=check_config.headers
                ) as response:
                    
                    response_text = await response.text()
                    
                    # Determine status based on HTTP status code
                    if 200 <= response.status < 300:
                        status = HealthStatus.HEALTHY
                        message = f"HTTP {response.status}: OK"
                    elif 300 <= response.status < 500:
                        status = HealthStatus.WARNING
                        message = f"HTTP {response.status}: Warning"
                    else:
                        status = HealthStatus.CRITICAL
                        message = f"HTTP {response.status}: Error"
                    
                    return HealthCheckResult(
                        check_id=check_config.check_id,
                        timestamp=datetime.utcnow(),
                        status=status,
                        response_time_ms=0,  # Will be set by caller
                        message=message,
                        details={
                            "http_status": response.status,
                            "response_size": len(response_text),
                            "content_type": response.headers.get("content-type", "")
                        }
                    )
                    
        except asyncio.TimeoutError:
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.CRITICAL,
                response_time_ms=0,
                message="Request timeout",
                error_message=f"Request timed out after {check_config.timeout_seconds} seconds"
            )
    
    async def _database_health_check(self, check_config: HealthCheckConfig) -> HealthCheckResult:
        """Perform database health check"""
        try:
            # Simulate database connection check
            await asyncio.sleep(0.1)  # Simulate connection time
            
            # Simulate query execution
            query_time_ms = 50.0  # Simulated query time
            
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.HEALTHY,
                response_time_ms=0,
                message="Database connection successful",
                details={
                    "connection_pool_size": 10,
                    "active_connections": 5,
                    "query_time_ms": query_time_ms
                },
                value=query_time_ms,
                unit="ms"
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.CRITICAL,
                response_time_ms=0,
                message="Database connection failed",
                error_message=str(e)
            )
    
    async def _cache_health_check(self, check_config: HealthCheckConfig) -> HealthCheckResult:
        """Perform cache health check"""
        try:
            # Simulate cache connectivity check
            await asyncio.sleep(0.05)  # Simulate cache response time
            
            cache_response_time = 25.0  # Simulated cache response time
            
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.HEALTHY,
                response_time_ms=0,
                message="Cache system operational",
                details={
                    "cache_hit_rate": 85.0,
                    "memory_usage_percent": 60.0,
                    "evictions_per_second": 0.5
                },
                value=cache_response_time,
                unit="ms"
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.CRITICAL,
                response_time_ms=0,
                message="Cache system failed",
                error_message=str(e)
            )
    
    async def _content_processing_health_check(self, check_config: HealthCheckConfig) -> HealthCheckResult:
        """Perform content processing health check"""
        try:
            # Simulate content processing system check
            await asyncio.sleep(1)  # Simulate processing time
            
            # Simulate processing metrics
            queue_size = 25
            processing_rate = 15.0  # files per minute
            
            # Determine status based on queue size
            if queue_size < 50:
                status = HealthStatus.HEALTHY
                message = "Content processing normal"
            elif queue_size < 200:
                status = HealthStatus.WARNING
                message = "Content processing queue elevated"
            else:
                status = HealthStatus.CRITICAL
                message = "Content processing queue critical"
            
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=status,
                response_time_ms=0,
                message=message,
                details={
                    "queue_size": queue_size,
                    "processing_rate_per_minute": processing_rate,
                    "active_workers": 8,
                    "failed_jobs_last_hour": 2
                },
                value=queue_size,
                unit="jobs",
                creator_impact_score=queue_size / 100.0  # Higher queue = higher impact
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.CRITICAL,
                response_time_ms=0,
                message="Content processing check failed",
                error_message=str(e)
            )
    
    async def _creator_workflow_health_check(self, check_config: HealthCheckConfig) -> HealthCheckResult:
        """Perform end-to-end creator workflow health check"""
        try:
            # Simulate comprehensive creator workflow test
            await asyncio.sleep(5)  # Simulate workflow execution time
            
            # Test steps: login -> upload -> process -> publish
            workflow_steps = {
                "login": True,
                "content_upload": True, 
                "content_processing": True,
                "content_publishing": True,
                "analytics_update": True
            }
            
            failed_steps = [step for step, success in workflow_steps.items() if not success]
            success_rate = len([s for s in workflow_steps.values() if s]) / len(workflow_steps) * 100
            
            if success_rate == 100:
                status = HealthStatus.HEALTHY
                message = "Creator workflow fully operational"
            elif success_rate >= 80:
                status = HealthStatus.WARNING
                message = f"Creator workflow partially functional ({success_rate:.1f}%)"
            else:
                status = HealthStatus.CRITICAL 
                message = f"Creator workflow severely impacted ({success_rate:.1f}%)"
            
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=status,
                response_time_ms=0,
                message=message,
                details={
                    "workflow_steps": workflow_steps,
                    "success_rate_percent": success_rate,
                    "failed_steps": failed_steps,
                    "test_creator_id": "test_creator_123"
                },
                value=success_rate,
                unit="percent",
                creator_impact_score=(100 - success_rate) / 20.0,  # Impact score 0-5
                revenue_impact_estimate=max(0, (100 - success_rate) * 100)  # Revenue impact estimate
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.CRITICAL,
                response_time_ms=0,
                message="Creator workflow test failed",
                error_message=str(e),
                creator_impact_score=5.0,  # Maximum impact
                revenue_impact_estimate=1000.0
            )
    
    async def _revenue_tracking_health_check(self, check_config: HealthCheckConfig) -> HealthCheckResult:
        """Perform revenue tracking health check"""
        try:
            # Simulate revenue tracking system check
            await asyncio.sleep(2)  # Simulate check time
            
            # Simulate revenue system metrics
            transaction_success_rate = 99.5
            payment_latency_ms = 150.0
            reconciliation_delay_minutes = 5.0
            
            # Determine status based on metrics
            if transaction_success_rate >= 99.0 and payment_latency_ms < 500:
                status = HealthStatus.HEALTHY
                message = "Revenue tracking optimal"
            elif transaction_success_rate >= 95.0 and payment_latency_ms < 1000:
                status = HealthStatus.WARNING
                message = "Revenue tracking degraded"
            else:
                status = HealthStatus.CRITICAL
                message = "Revenue tracking critical"
            
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=status,
                response_time_ms=0,
                message=message,
                details={
                    "transaction_success_rate": transaction_success_rate,
                    "payment_latency_ms": payment_latency_ms,
                    "reconciliation_delay_minutes": reconciliation_delay_minutes,
                    "daily_transaction_count": 15420,
                    "revenue_processed_today": 125000.0
                },
                value=transaction_success_rate,
                unit="percent",
                revenue_impact_estimate=(100 - transaction_success_rate) * 1000
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.CRITICAL,
                response_time_ms=0,
                message="Revenue tracking check failed",
                error_message=str(e),
                revenue_impact_estimate=5000.0
            )
    
    async def _generic_health_check(self, check_config: HealthCheckConfig) -> HealthCheckResult:
        """Generic health check implementation"""
        try:
            # Simulate generic check
            await asyncio.sleep(0.5)
            
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.HEALTHY,
                response_time_ms=0,
                message="Generic health check passed"
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=check_config.check_id,
                timestamp=datetime.utcnow(),
                status=HealthStatus.CRITICAL,
                response_time_ms=0,
                message="Generic health check failed",
                error_message=str(e)
            )
    
    def _determine_health_status(
        self, 
        check_config: HealthCheckConfig, 
        response_time_ms: float, 
        value: Optional[float]
    ) -> HealthStatus:
        """Determine health status based on thresholds"""
        
        # Check response time thresholds
        if check_config.critical_threshold and response_time_ms > check_config.critical_threshold:
            return HealthStatus.CRITICAL
        elif check_config.warning_threshold and response_time_ms > check_config.warning_threshold:
            return HealthStatus.WARNING
        
        # Check value thresholds (for numeric metrics)
        if value is not None:
            if check_config.critical_threshold and value > check_config.critical_threshold:
                return HealthStatus.CRITICAL
            elif check_config.warning_threshold and value > check_config.warning_threshold:
                return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    async def _update_service_health(self, check_config: HealthCheckConfig, result: HealthCheckResult):
        """Update overall service health based on check result"""
        try:
            # Determine service ID from check (simplified mapping)
            service_id = check_config.check_id.split('_')[0]  # e.g., "creator" from "creator_dashboard_health"
            service_name = check_config.name.split(' ')[0]
            
            # Get or create service health
            if service_id not in self.services:
                self.services[service_id] = ServiceHealth(
                    service_id=service_id,
                    service_name=service_name,
                    creator_impact_level=check_config.creator_impact_level
                )
            
            service = self.services[service_id]
            
            # Update check result
            service.check_results[check_config.check_id] = result
            service.last_updated = datetime.utcnow()
            
            # Recalculate service health
            await self._calculate_service_health(service)
            
        except Exception as e:
            logger.error(f"Failed to update service health: {str(e)}")
    
    async def _calculate_service_health(self, service: ServiceHealth):
        """Calculate overall service health from individual checks"""
        try:
            if not service.check_results:
                return
            
            # Count status types
            healthy_count = 0
            warning_count = 0
            critical_count = 0
            total_count = len(service.check_results)
            
            total_response_time = 0.0
            response_time_count = 0
            
            for result in service.check_results.values():
                if result.status == HealthStatus.HEALTHY:
                    healthy_count += 1
                elif result.status == HealthStatus.WARNING:
                    warning_count += 1
                elif result.status == HealthStatus.CRITICAL:
                    critical_count += 1
                
                if result.response_time_ms > 0:
                    total_response_time += result.response_time_ms
                    response_time_count += 1
            
            # Update counts
            service.total_checks = total_count
            service.healthy_checks = healthy_count
            service.warning_checks = warning_count
            service.critical_checks = critical_count
            
            # Calculate metrics
            if response_time_count > 0:
                service.average_response_time_ms = total_response_time / response_time_count
            
            service.availability_percentage = (healthy_count / total_count) * 100
            
            # Determine overall status
            healthy_ratio = healthy_count / total_count
            critical_ratio = critical_count / total_count
            
            rules = self.health_aggregation_rules["service_level"]
            
            if critical_ratio > 0.5 or healthy_ratio < rules["critical_threshold"]:
                service.overall_status = HealthStatus.CRITICAL
            elif critical_ratio > 0.2 or healthy_ratio < rules["warning_threshold"]:
                service.overall_status = HealthStatus.WARNING
            else:
                service.overall_status = HealthStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Failed to calculate service health: {str(e)}")
    
    async def _check_health_alerts(self, check_config: HealthCheckConfig, result: HealthCheckResult):
        """Check if health result should trigger alerts"""
        try:
            # Check for status changes
            previous_results = list(self.check_results_history[check_config.check_id])
            if len(previous_results) > 1:
                previous_result = previous_results[-2]
                if previous_result.status != result.status:
                    await self._trigger_health_alert(check_config, result, previous_result.status)
            
            # Check for critical status
            if result.status == HealthStatus.CRITICAL:
                await self._trigger_critical_alert(check_config, result)
            
        except Exception as e:
            logger.error(f"Failed to check health alerts: {str(e)}")
    
    async def _trigger_health_alert(
        self, 
        check_config: HealthCheckConfig, 
        result: HealthCheckResult, 
        previous_status: HealthStatus
    ):
        """Trigger health status change alert"""
        alert_data = {
            "type": "status_change",
            "check_id": check_config.check_id,
            "check_name": check_config.name,
            "previous_status": previous_status.value,
            "current_status": result.status.value,
            "timestamp": result.timestamp.isoformat(),
            "creator_impact_level": check_config.creator_impact_level,
            "affects_revenue": check_config.affects_revenue,
            "message": result.message,
            "error": result.error_message
        }
        
        for handler in self.alert_handlers:
            await handler(alert_data)
    
    async def _trigger_critical_alert(self, check_config: HealthCheckConfig, result: HealthCheckResult):
        """Trigger critical status alert"""
        alert_data = {
            "type": "critical_status",
            "check_id": check_config.check_id,
            "check_name": check_config.name,
            "status": result.status.value,
            "timestamp": result.timestamp.isoformat(),
            "creator_impact_level": check_config.creator_impact_level,
            "affects_revenue": check_config.affects_revenue,
            "creator_impact_score": result.creator_impact_score,
            "revenue_impact_estimate": result.revenue_impact_estimate,
            "message": result.message,
            "error": result.error_message,
            "response_time_ms": result.response_time_ms
        }
        
        for handler in self.alert_handlers:
            await handler(alert_data)
    
    async def _log_alert_handler(self, alert_data: Dict[str, Any]):
        """Default log alert handler"""
        alert_type = alert_data["type"]
        check_name = alert_data["check_name"]
        
        if alert_type == "critical_status":
            logger.critical(f"CRITICAL HEALTH ALERT: {check_name} - {alert_data['message']}")
            if alert_data["affects_revenue"]:
                logger.critical(f"REVENUE IMPACT: ${alert_data['revenue_impact_estimate']:.2f}")
        elif alert_type == "status_change":
            logger.warning(f"HEALTH STATUS CHANGE: {check_name} - {alert_data['previous_status']} -> {alert_data['current_status']}")
    
    async def _health_aggregation_loop(self):
        """Health aggregation and global metrics loop"""
        while self.monitoring_active:
            try:
                await self._update_global_metrics()
                await self._check_creator_journey_health()
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Health aggregation loop error: {str(e)}")
                await asyncio.sleep(120)
    
    async def _alerting_loop(self):
        """Alerting and escalation loop"""
        while self.monitoring_active:
            try:
                await self._check_escalation_conditions()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Alerting loop error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _update_global_metrics(self):
        """Update global health metrics"""
        try:
            if not self.services:
                return
            
            healthy_services = 0
            warning_services = 0
            critical_services = 0
            total_response_time = 0.0
            response_time_count = 0
            total_availability = 0.0
            
            for service in self.services.values():
                if service.overall_status == HealthStatus.HEALTHY:
                    healthy_services += 1
                elif service.overall_status == HealthStatus.WARNING:
                    warning_services += 1
                elif service.overall_status == HealthStatus.CRITICAL:
                    critical_services += 1
                
                if service.average_response_time_ms > 0:
                    total_response_time += service.average_response_time_ms
                    response_time_count += 1
                
                total_availability += service.availability_percentage
            
            total_services = len(self.services)
            
            self.global_metrics.update({
                "total_checks": sum(len(s.check_results) for s in self.services.values()),
                "healthy_services": healthy_services,
                "warning_services": warning_services,
                "critical_services": critical_services,
                "average_response_time_ms": total_response_time / max(1, response_time_count),
                "overall_availability": total_availability / max(1, total_services)
            })
            
        except Exception as e:
            logger.error(f"Failed to update global metrics: {str(e)}")
    
    async def _check_creator_journey_health(self):
        """Check health of Creator journeys"""
        try:
            for journey_name, check_ids in self.creator_journey_checks.items():
                journey_health = await self._calculate_journey_health(check_ids)
                
                if journey_health["status"] == HealthStatus.CRITICAL:
                    logger.error(f"Creator journey '{journey_name}' is critical: {journey_health['message']}")
                elif journey_health["status"] == HealthStatus.WARNING:
                    logger.warning(f"Creator journey '{journey_name}' has warnings: {journey_health['message']}")
                
        except Exception as e:
            logger.error(f"Failed to check creator journey health: {str(e)}")
    
    async def _calculate_journey_health(self, check_ids: List[str]) -> Dict[str, Any]:
        """Calculate health for a Creator journey"""
        try:
            healthy_checks = 0
            total_checks = 0
            issues = []
            
            for check_id in check_ids:
                if check_id in self.check_results_history and self.check_results_history[check_id]:
                    latest_result = self.check_results_history[check_id][-1]
                    total_checks += 1
                    
                    if latest_result.status == HealthStatus.HEALTHY:
                        healthy_checks += 1
                    else:
                        issues.append(f"{check_id}: {latest_result.message}")
            
            if total_checks == 0:
                return {"status": HealthStatus.UNKNOWN, "message": "No health data"}
            
            health_percentage = (healthy_checks / total_checks) * 100
            
            if health_percentage == 100:
                status = HealthStatus.HEALTHY
                message = "All checks healthy"
            elif health_percentage >= 75:
                status = HealthStatus.WARNING
                message = f"{health_percentage:.1f}% healthy - Issues: {', '.join(issues)}"
            else:
                status = HealthStatus.CRITICAL
                message = f"{health_percentage:.1f}% healthy - Critical issues: {', '.join(issues)}"
            
            return {
                "status": status,
                "message": message,
                "health_percentage": health_percentage,
                "issues": issues
            }
            
        except Exception as e:
            return {"status": HealthStatus.UNKNOWN, "message": f"Error calculating journey health: {str(e)}"}
    
    async def _check_escalation_conditions(self):
        """Check for conditions requiring escalation"""
        try:
            # Check for too many critical services
            if self.global_metrics["critical_services"] > 2:
                logger.critical(f"ESCALATION: {self.global_metrics['critical_services']} services in critical state")
            
            # Check for revenue-critical issues
            revenue_critical_issues = 0
            for check_id in self.revenue_critical_checks:
                if (check_id in self.check_results_history and 
                    self.check_results_history[check_id] and
                    self.check_results_history[check_id][-1].status == HealthStatus.CRITICAL):
                    revenue_critical_issues += 1
            
            if revenue_critical_issues > 0:
                logger.critical(f"REVENUE ESCALATION: {revenue_critical_issues} revenue-critical systems failing")
            
        except Exception as e:
            logger.error(f"Failed to check escalation conditions: {str(e)}")
    
    async def add_health_check(self, check_config: HealthCheckConfig) -> bool:
        """
        Add a new health check
        
        Args:
            check_config: Health check configuration
            
        Returns:
            bool: True if added successfully
        """
        try:
            if check_config.check_id in self.health_checks:
                raise ValueError(f"Health check {check_config.check_id} already exists")
            
            self.health_checks[check_config.check_id] = check_config
            
            # Start executor if monitoring is active
            if self.monitoring_active:
                task = asyncio.create_task(self._health_check_executor(check_config))
                self.check_executors[check_config.check_id] = task
            
            logger.info(f"Added health check: {check_config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add health check: {str(e)}")
            return False
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "monitoring_active": self.monitoring_active,
            "global_metrics": self.global_metrics,
            "services": {
                service_id: {
                    "name": service.service_name,
                    "overall_status": service.overall_status.value,
                    "total_checks": service.total_checks,
                    "healthy_checks": service.healthy_checks,
                    "warning_checks": service.warning_checks,
                    "critical_checks": service.critical_checks,
                    "availability_percentage": service.availability_percentage,
                    "average_response_time_ms": service.average_response_time_ms,
                    "creator_impact_level": service.creator_impact_level,
                    "last_updated": service.last_updated.isoformat()
                }
                for service_id, service in self.services.items()
            },
            "health_checks": {
                check_id: {
                    "name": check.name,
                    "type": check.check_type.value,
                    "interval_seconds": check.interval_seconds,
                    "creator_impact_level": check.creator_impact_level,
                    "affects_revenue": check.affects_revenue,
                    "affects_content_creation": check.affects_content_creation,
                    "creator_facing": check.creator_facing,
                    "last_result": self.check_results_history[check_id][-1].__dict__ if self.check_results_history[check_id] else None
                }
                for check_id, check in self.health_checks.items()
            },
            "creator_health_mapping": self.creator_health_mapping,
            "creator_journey_health": {
                journey_name: await self._calculate_journey_health(check_ids)
                for journey_name, check_ids in self.creator_journey_checks.items()
            },
            "revenue_critical_checks": self.revenue_critical_checks
        }
    
    async def health_check(self) -> bool:
        """Health check for the orchestrator itself"""
        try:
            # Check if monitoring is active
            if not self.monitoring_active:
                return False
            
            # Check if executors are running
            active_executors = sum(1 for task in self.check_executors.values() if not task.done())
            expected_executors = len(self.health_checks)
            
            if active_executors < expected_executors * 0.8:  # At least 80% of executors should be running
                return False
            
            # Check overall system health
            if self.global_metrics["critical_services"] > len(self.services) * 0.5:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check orchestrator health check failed: {str(e)}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown of health check orchestrator"""
        try:
            logger.info("Shutting down Health Check Orchestrator...")
            
            # Stop monitoring
            self.monitoring_active = False
            
            # Cancel all executor tasks
            for check_id, task in self.check_executors.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                logger.info(f"Stopped health check executor: {check_id}")
            
            self.check_executors.clear()
            
            logger.info("Health Check Orchestrator shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during health check orchestrator shutdown: {str(e)}")


# Factory function
def create_health_check_orchestrator() -> HealthCheckOrchestrator:
    """Factory function to create health check orchestrator"""
    return HealthCheckOrchestrator()


# Example usage
async def main():
    """Example usage of health check orchestrator"""
    logging.basicConfig(level=logging.INFO)
    
    orchestrator = create_health_check_orchestrator()
    
    try:
        # Initialize
        await orchestrator.initialize()
        
        # Get initial status
        status = await orchestrator.get_health_status()
        print("Health Check Orchestrator Status:")
        print(f"Total health checks: {len(status['health_checks'])}")
        print(f"Services monitored: {len(status['services'])}")
        print(f"Overall availability: {status['global_metrics']['overall_availability']:.2f}%")
        
        # Monitor for a while
        print("\nMonitoring health checks...")
        for i in range(20):  # Monitor for 2 minutes
            status = await orchestrator.get_health_status()
            
            print(f"\nHealth Summary:")
            print(f"  Healthy services: {status['global_metrics']['healthy_services']}")
            print(f"  Warning services: {status['global_metrics']['warning_services']}")
            print(f"  Critical services: {status['global_metrics']['critical_services']}")
            print(f"  Avg response time: {status['global_metrics']['average_response_time_ms']:.1f}ms")
            
            # Show Creator journey health
            for journey_name, journey_health in status['creator_journey_health'].items():
                print(f"  {journey_name}: {journey_health['status']} ({journey_health.get('health_percentage', 0):.1f}%)")
            
            await asyncio.sleep(6)  # Check every 6 seconds
        
        # Final status
        final_status = await orchestrator.get_health_status()
        print(f"\nFinal Metrics:")
        print(f"Total checks performed: {final_status['global_metrics']['total_checks']}")
        print(f"Overall availability: {final_status['global_metrics']['overall_availability']:.2f}%")
        print(f"Revenue critical checks: {len(final_status['revenue_critical_checks'])}")
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())