"""MLOps Health Check Manager - Comprehensive ML Services Health Monitoring
Manager de health checks complet pour tous les services ML avec auto-healing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🎯 Business Logic Integration:
ML Services → Health Monitoring → Issue Detection → Auto-Healing → Business Continuity

🚀 Multi-Expert Implementation:
- DevOps: Service health monitoring and auto-scaling triggers
- Backend Senior: High-availability patterns and circuit breaker integration  
- ML Engineer: Model health validation and performance monitoring
- Microservices: Service mesh health checks and load balancer integration
"""

import asyncio
import logging
import json
import time
import psutil
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """États de santé des services."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class ServiceType(Enum):
    """Types de services ML pour health checking."""
    MODEL_INFERENCE = "model_inference"
    MODEL_TRAINING = "model_training"
    DATA_PIPELINE = "data_pipeline"
    FEATURE_STORE = "feature_store"
    MODEL_REGISTRY = "model_registry"
    MONITORING_DASHBOARD = "monitoring_dashboard"
    ORCHESTRATOR = "orchestrator"
    STORAGE_SERVICE = "storage_service"
    DATABASE = "database"
    CACHE_SERVICE = "cache_service"
    MESSAGE_QUEUE = "message_queue"
    API_GATEWAY = "api_gateway"

class CheckType(Enum):
    """Types de vérifications de santé."""
    HTTP_ENDPOINT = "http_endpoint"
    TCP_PORT = "tcp_port"
    DATABASE_QUERY = "database_query"
    CUSTOM_SCRIPT = "custom_script"
    RESOURCE_USAGE = "resource_usage"
    MODEL_ACCURACY = "model_accuracy"
    LATENCY_CHECK = "latency_check"
    THROUGHPUT_CHECK = "throughput_check"

@dataclass
class HealthCheck:
    """Configuration d'un health check."""
    check_id: str
    service_name: str
    service_type: ServiceType
    check_type: CheckType
    endpoint_url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    timeout_seconds: int = 30
    interval_seconds: int = 60
    failure_threshold: int = 3
    success_threshold: int = 2
    expected_response_code: int = 200
    expected_response_time_ms: int = 1000
    custom_script_path: Optional[str] = None
    creator_segments: Optional[List[str]] = None
    critical_for_business: bool = False

@dataclass
class HealthCheckResult:
    """Résultat d'un health check."""
    check_id: str
    service_name: str
    status: HealthStatus
    response_time_ms: Optional[float]
    error_message: Optional[str]
    timestamp: datetime
    details: Dict[str, Any]
    success_count: int = 0
    failure_count: int = 0

@dataclass
class ServiceHealth:
    """État de santé global d'un service."""
    service_name: str
    service_type: ServiceType
    overall_status: HealthStatus
    last_healthy: Optional[datetime]
    uptime_percentage: float
    avg_response_time_ms: float
    check_results: List[HealthCheckResult]
    auto_healing_attempts: int
    creator_segments_affected: List[str]

class HealthCheckManager:
    """Manager complet de health checks pour services ML enterprise."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize health check manager."""
        self.config = self._load_config(config_path)
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_results: Dict[str, List[HealthCheckResult]] = {}
        self.service_health: Dict[str, ServiceHealth] = {}
        self.running_checks: Dict[str, asyncio.Task] = {}
        self.auto_healing_handlers: Dict[str, Callable] = {}
        self.notification_handlers: List[Callable] = []
        
        # Circuit breaker states for services
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Performance baselines for creator segments
        self.creator_segment_baselines = {
            "musicians": {"max_latency_ms": 100, "min_uptime_pct": 99.5},
            "photographers": {"max_latency_ms": 150, "min_uptime_pct": 99.0},
            "bloggers": {"max_latency_ms": 200, "min_uptime_pct": 98.5},
            "influencers": {"max_latency_ms": 80, "min_uptime_pct": 99.9},
            "comedians": {"max_latency_ms": 120, "min_uptime_pct": 99.0}
        }
        
        logger.info("🏥 HealthCheckManager enterprise initialized with auto-healing")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load health check configuration."""
        default_config = {
            "global_settings": {
                "max_parallel_checks": 50,
                "check_result_retention_hours": 168,  # 7 days
                "auto_healing_enabled": True,
                "notification_enabled": True,
                "circuit_breaker_enabled": True
            },
            "thresholds": {
                "critical_service_count": 3,
                "degraded_threshold_pct": 80.0,
                "unhealthy_threshold_pct": 60.0,
                "critical_threshold_pct": 40.0
            },
            "auto_healing": {
                "max_attempts_per_hour": 3,
                "restart_delay_seconds": 30,
                "scale_up_threshold": 0.8,
                "scale_down_threshold": 0.3
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config

    async def register_health_check(self, health_check: HealthCheck) -> bool:
        """Enregistrer un nouveau health check."""
        try:
            self.health_checks[health_check.check_id] = health_check
            self.check_results[health_check.check_id] = []
            
            # Initialize circuit breaker for the service
            if health_check.service_name not in self.circuit_breakers:
                self.circuit_breakers[health_check.service_name] = {
                    "state": "closed",  # closed, open, half_open
                    "failure_count": 0,
                    "last_failure_time": None,
                    "timeout_seconds": 60
                }
            
            logger.info(f"✅ Registered health check {health_check.check_id} "
                       f"for {health_check.service_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registering health check: {e}")
            return False

    async def start_health_monitoring(self) -> None:
        """Démarrer le monitoring continu de tous les health checks."""
        try:
            logger.info("🚀 Starting continuous health monitoring...")
            
            for check_id, health_check in self.health_checks.items():
                if check_id not in self.running_checks:
                    task = asyncio.create_task(
                        self._run_continuous_check(health_check)
                    )
                    self.running_checks[check_id] = task
            
            logger.info(f"🔄 Started {len(self.running_checks)} continuous health checks")
            
        except Exception as e:
            logger.error(f"❌ Error starting health monitoring: {e}")

    async def stop_health_monitoring(self) -> None:
        """Arrêter le monitoring de santé."""
        try:
            logger.info("🛑 Stopping health monitoring...")
            
            for check_id, task in self.running_checks.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.running_checks.clear()
            logger.info("✅ Health monitoring stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping health monitoring: {e}")

    async def _run_continuous_check(self, health_check: HealthCheck) -> None:
        """Exécuter un health check en continu."""
        try:
            while True:
                # Perform the health check
                result = await self._perform_health_check(health_check)
                
                # Store result
                self.check_results[health_check.check_id].append(result)
                
                # Keep only recent results
                cutoff_time = datetime.now() - timedelta(
                    hours=self.config["global_settings"]["check_result_retention_hours"]
                )
                self.check_results[health_check.check_id] = [
                    r for r in self.check_results[health_check.check_id]
                    if r.timestamp > cutoff_time
                ]
                
                # Update service health
                await self._update_service_health(health_check.service_name)
                
                # Check if auto-healing is needed
                if (self.config["global_settings"]["auto_healing_enabled"] and
                    result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]):
                    await self._trigger_auto_healing(health_check.service_name, result)
                
                # Send notifications if needed
                if self.config["global_settings"]["notification_enabled"]:
                    await self._send_notifications(health_check.service_name, result)
                
                # Wait for next check
                await asyncio.sleep(health_check.interval_seconds)
                
        except asyncio.CancelledError:
            logger.info(f"Health check {health_check.check_id} cancelled")
        except Exception as e:
            logger.error(f"❌ Error in continuous health check {health_check.check_id}: {e}")

    async def _perform_health_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Effectuer un health check spécifique."""
        start_time = time.time()
        
        try:
            if health_check.check_type == CheckType.HTTP_ENDPOINT:
                result = await self._check_http_endpoint(health_check)
            elif health_check.check_type == CheckType.TCP_PORT:
                result = await self._check_tcp_port(health_check)
            elif health_check.check_type == CheckType.DATABASE_QUERY:
                result = await self._check_database(health_check)
            elif health_check.check_type == CheckType.RESOURCE_USAGE:
                result = await self._check_resource_usage(health_check)
            elif health_check.check_type == CheckType.MODEL_ACCURACY:
                result = await self._check_model_accuracy(health_check)
            elif health_check.check_type == CheckType.LATENCY_CHECK:
                result = await self._check_latency(health_check)
            elif health_check.check_type == CheckType.CUSTOM_SCRIPT:
                result = await self._check_custom_script(health_check)
            else:
                result = HealthCheckResult(
                    check_id=health_check.check_id,
                    service_name=health_check.service_name,
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=None,
                    error_message=f"Unknown check type: {health_check.check_type}",
                    timestamp=datetime.now(),
                    details={}
                )
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            if result.response_time_ms is None:
                result.response_time_ms = response_time
            
            # Update circuit breaker
            await self._update_circuit_breaker(health_check.service_name, result.status)
            
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Health check {health_check.check_id} failed: {e}")
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=HealthStatus.CRITICAL,
                response_time_ms=response_time,
                error_message=str(e),
                timestamp=datetime.now(),
                details={"exception_type": type(e).__name__}
            )

    async def _check_http_endpoint(self, health_check: HealthCheck) -> HealthCheckResult:
        """Vérifier un endpoint HTTP."""
        if not health_check.endpoint_url:
            raise ValueError("endpoint_url required for HTTP check")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=health_check.timeout_seconds)) as session:
            try:
                start_time = time.time()
                async with session.get(health_check.endpoint_url) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    # Check response code
                    if response.status == health_check.expected_response_code:
                        # Check response time
                        if response_time <= health_check.expected_response_time_ms:
                            status = HealthStatus.HEALTHY
                        else:
                            status = HealthStatus.DEGRADED
                        
                        # Try to parse response for additional details
                        try:
                            response_data = await response.json()
                            details = {"response_data": response_data}
                        except:
                            details = {"response_size": len(await response.text())}
                        
                        return HealthCheckResult(
                            check_id=health_check.check_id,
                            service_name=health_check.service_name,
                            status=status,
                            response_time_ms=response_time,
                            error_message=None,
                            timestamp=datetime.now(),
                            details=details
                        )
                    else:
                        return HealthCheckResult(
                            check_id=health_check.check_id,
                            service_name=health_check.service_name,
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time,
                            error_message=f"HTTP {response.status} (expected {health_check.expected_response_code})",
                            timestamp=datetime.now(),
                            details={"response_status": response.status}
                        )
                        
            except asyncio.TimeoutError:
                return HealthCheckResult(
                    check_id=health_check.check_id,
                    service_name=health_check.service_name,
                    status=HealthStatus.CRITICAL,
                    response_time_ms=health_check.timeout_seconds * 1000,
                    error_message="HTTP request timeout",
                    timestamp=datetime.now(),
                    details={"timeout_seconds": health_check.timeout_seconds}
                )

    async def _check_tcp_port(self, health_check: HealthCheck) -> HealthCheckResult:
        """Vérifier la connectivité TCP."""
        if not health_check.host or not health_check.port:
            raise ValueError("host and port required for TCP check")
        
        try:
            start_time = time.time()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(health_check.host, health_check.port),
                timeout=health_check.timeout_seconds
            )
            response_time = (time.time() - start_time) * 1000
            
            writer.close()
            await writer.wait_closed()
            
            status = HealthStatus.HEALTHY if response_time <= health_check.expected_response_time_ms else HealthStatus.DEGRADED
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=status,
                response_time_ms=response_time,
                error_message=None,
                timestamp=datetime.now(),
                details={"tcp_connection": "successful"}
            )
            
        except asyncio.TimeoutError:
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=HealthStatus.CRITICAL,
                response_time_ms=health_check.timeout_seconds * 1000,
                error_message="TCP connection timeout",
                timestamp=datetime.now(),
                details={"timeout_seconds": health_check.timeout_seconds}
            )

    async def _check_database(self, health_check: HealthCheck) -> HealthCheckResult:
        """Vérifier la santé de la base de données."""
        # This would integrate with actual database connections
        # For now, simulate database health check
        
        try:
            start_time = time.time()
            
            # Simulate database query
            await asyncio.sleep(0.05)  # Simulate DB query time
            
            response_time = (time.time() - start_time) * 1000
            
            # Simulate various database health scenarios
            import random
            db_health = random.choice([
                ("healthy", 0.95),
                ("degraded", 0.85),
                ("unhealthy", 0.15)
            ])
            
            if random.random() < db_health[1]:
                status = HealthStatus.HEALTHY if db_health[0] == "healthy" else HealthStatus.DEGRADED
                error_message = None
            else:
                status = HealthStatus.UNHEALTHY
                error_message = f"Database connection issues: {db_health[0]}"
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=status,
                response_time_ms=response_time,
                error_message=error_message,
                timestamp=datetime.now(),
                details={
                    "query_type": "health_check",
                    "connection_pool_status": "active" if status == HealthStatus.HEALTHY else "degraded"
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=HealthStatus.CRITICAL,
                response_time_ms=None,
                error_message=f"Database check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error_type": "database_error"}
            )

    async def _check_resource_usage(self, health_check: HealthCheck) -> HealthCheckResult:
        """Vérifier l'utilisation des ressources système."""
        try:
            start_time = time.time()
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine health status based on resource usage
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent > 80:
                status = HealthStatus.DEGRADED
                issues.append(f"Elevated CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > 95:
                status = HealthStatus.CRITICAL
                issues.append(f"Critical memory usage: {memory.percent:.1f}%")
            elif memory.percent > 85:
                status = max(status.value, HealthStatus.DEGRADED.value)
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > 95:
                status = HealthStatus.CRITICAL
                issues.append(f"Critical disk usage: {disk.percent:.1f}%")
            elif disk.percent > 85:
                status = max(status.value, HealthStatus.DEGRADED.value)
                issues.append(f"High disk usage: {disk.percent:.1f}%")
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=status,
                response_time_ms=response_time,
                error_message="; ".join(issues) if issues else None,
                timestamp=datetime.now(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_available_gb": memory.available / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=HealthStatus.CRITICAL,
                response_time_ms=None,
                error_message=f"Resource check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error_type": "resource_check_error"}
            )

    async def _check_model_accuracy(self, health_check: HealthCheck) -> HealthCheckResult:
        """Vérifier la précision d'un modèle ML."""
        try:
            start_time = time.time()
            
            # Simulate model accuracy check
            # In production, this would check actual model metrics
            await asyncio.sleep(0.1)  # Simulate model evaluation time
            
            # Simulate accuracy metrics for different creator segments
            import random
            base_accuracy = 0.85
            
            if health_check.creator_segments:
                # Adjust accuracy based on creator segments
                segment_adjustments = {
                    "musicians": 0.02,
                    "photographers": 0.01,
                    "bloggers": -0.01,
                    "influencers": 0.03,
                    "comedians": 0.00
                }
                
                avg_adjustment = statistics.mean([
                    segment_adjustments.get(seg, 0.0) 
                    for seg in health_check.creator_segments
                ])
                base_accuracy += avg_adjustment
            
            # Add some random variation
            current_accuracy = base_accuracy + random.uniform(-0.05, 0.05)
            current_accuracy = max(0.0, min(1.0, current_accuracy))
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on accuracy
            if current_accuracy >= 0.90:
                status = HealthStatus.HEALTHY
            elif current_accuracy >= 0.80:
                status = HealthStatus.DEGRADED
            elif current_accuracy >= 0.70:
                status = HealthStatus.UNHEALTHY
            else:
                status = HealthStatus.CRITICAL
            
            error_message = None
            if status != HealthStatus.HEALTHY:
                error_message = f"Model accuracy below threshold: {current_accuracy:.3f}"
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=status,
                response_time_ms=response_time,
                error_message=error_message,
                timestamp=datetime.now(),
                details={
                    "model_accuracy": current_accuracy,
                    "accuracy_threshold": 0.80,
                    "creator_segments": health_check.creator_segments or []
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=HealthStatus.CRITICAL,
                response_time_ms=None,
                error_message=f"Model accuracy check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error_type": "model_accuracy_error"}
            )

    async def _check_latency(self, health_check: HealthCheck) -> HealthCheckResult:
        """Vérifier la latence d'un service pour les créateurs."""
        try:
            start_time = time.time()
            
            # Simulate service latency check
            if health_check.endpoint_url:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=health_check.timeout_seconds)) as session:
                    async with session.get(health_check.endpoint_url) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        # Get latency requirements for creator segments
                        max_latency = health_check.expected_response_time_ms
                        
                        if health_check.creator_segments:
                            segment_requirements = [
                                self.creator_segment_baselines.get(seg, {}).get("max_latency_ms", 200)
                                for seg in health_check.creator_segments
                            ]
                            max_latency = min(segment_requirements) if segment_requirements else max_latency
                        
                        # Determine status based on latency
                        if response_time <= max_latency:
                            status = HealthStatus.HEALTHY
                        elif response_time <= max_latency * 1.5:
                            status = HealthStatus.DEGRADED
                        elif response_time <= max_latency * 2.0:
                            status = HealthStatus.UNHEALTHY
                        else:
                            status = HealthStatus.CRITICAL
                        
                        error_message = None
                        if status != HealthStatus.HEALTHY:
                            error_message = f"High latency: {response_time:.1f}ms (max: {max_latency}ms)"
                        
                        return HealthCheckResult(
                            check_id=health_check.check_id,
                            service_name=health_check.service_name,
                            status=status,
                            response_time_ms=response_time,
                            error_message=error_message,
                            timestamp=datetime.now(),
                            details={
                                "latency_ms": response_time,
                                "max_latency_ms": max_latency,
                                "creator_segments": health_check.creator_segments or []
                            }
                        )
            else:
                raise ValueError("endpoint_url required for latency check")
                
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=HealthStatus.CRITICAL,
                response_time_ms=None,
                error_message=f"Latency check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error_type": "latency_check_error"}
            )

    async def _check_custom_script(self, health_check: HealthCheck) -> HealthCheckResult:
        """Exécuter un script personnalisé de health check."""
        try:
            if not health_check.custom_script_path:
                raise ValueError("custom_script_path required for custom script check")
            
            start_time = time.time()
            
            # Execute custom script
            process = await asyncio.create_subprocess_exec(
                'python', health_check.custom_script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=health_check.timeout_seconds
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Parse script output
            if process.returncode == 0:
                try:
                    output_data = json.loads(stdout.decode())
                    status = HealthStatus(output_data.get("status", "unknown"))
                    error_message = output_data.get("error_message")
                    details = output_data.get("details", {})
                except json.JSONDecodeError:
                    status = HealthStatus.HEALTHY
                    error_message = None
                    details = {"script_output": stdout.decode()}
            else:
                status = HealthStatus.CRITICAL
                error_message = f"Script failed with code {process.returncode}"
                details = {"stderr": stderr.decode()}
            
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=status,
                response_time_ms=response_time,
                error_message=error_message,
                timestamp=datetime.now(),
                details=details
            )
            
        except asyncio.TimeoutError:
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=HealthStatus.CRITICAL,
                response_time_ms=health_check.timeout_seconds * 1000,
                error_message="Custom script timeout",
                timestamp=datetime.now(),
                details={"timeout_seconds": health_check.timeout_seconds}
            )
        except Exception as e:
            return HealthCheckResult(
                check_id=health_check.check_id,
                service_name=health_check.service_name,
                status=HealthStatus.CRITICAL,
                response_time_ms=None,
                error_message=f"Custom script check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error_type": "custom_script_error"}
            )

    async def _update_circuit_breaker(self, service_name: str, status: HealthStatus) -> None:
        """Mettre à jour l'état du circuit breaker."""
        if service_name not in self.circuit_breakers:
            return
        
        breaker = self.circuit_breakers[service_name]
        
        if status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
            breaker["failure_count"] += 1
            breaker["last_failure_time"] = time.time()
            
            # Open circuit if failure threshold reached
            if breaker["failure_count"] >= 5 and breaker["state"] == "closed":
                breaker["state"] = "open"
                logger.warning(f"🔴 Circuit breaker OPENED for {service_name}")
        else:
            # Reset failure count on success
            breaker["failure_count"] = 0
            
            # Close circuit if it was open/half-open
            if breaker["state"] in ["open", "half_open"]:
                breaker["state"] = "closed"
                logger.info(f"🟢 Circuit breaker CLOSED for {service_name}")

    async def _update_service_health(self, service_name: str) -> None:
        """Mettre à jour l'état de santé global d'un service."""
        try:
            # Get all check results for this service
            service_results = []
            for check_id, health_check in self.health_checks.items():
                if health_check.service_name == service_name:
                    service_results.extend(self.check_results.get(check_id, []))
            
            if not service_results:
                return
            
            # Calculate overall metrics
            recent_results = [r for r in service_results if r.timestamp > datetime.now() - timedelta(hours=1)]
            
            if not recent_results:
                return
            
            # Overall status (worst case)
            status_priority = {
                HealthStatus.CRITICAL: 0,
                HealthStatus.UNHEALTHY: 1,
                HealthStatus.DEGRADED: 2,
                HealthStatus.HEALTHY: 3,
                HealthStatus.UNKNOWN: 4
            }
            
            overall_status = min(recent_results, key=lambda r: status_priority[r.status]).status
            
            # Uptime calculation
            total_checks = len(recent_results)
            healthy_checks = len([r for r in recent_results if r.status == HealthStatus.HEALTHY])
            uptime_percentage = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
            
            # Average response time
            response_times = [r.response_time_ms for r in recent_results if r.response_time_ms is not None]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            # Last healthy time
            healthy_results = [r for r in recent_results if r.status == HealthStatus.HEALTHY]
            last_healthy = max([r.timestamp for r in healthy_results]) if healthy_results else None
            
            # Creator segments affected
            creator_segments = set()
            for check_id, health_check in self.health_checks.items():
                if (health_check.service_name == service_name and 
                    health_check.creator_segments):
                    creator_segments.update(health_check.creator_segments)
            
            # Auto-healing attempts count
            auto_healing_attempts = 0
            if service_name in self.service_health:
                auto_healing_attempts = self.service_health[service_name].auto_healing_attempts
            
            # Update service health
            service_type = None
            for health_check in self.health_checks.values():
                if health_check.service_name == service_name:
                    service_type = health_check.service_type
                    break
            
            self.service_health[service_name] = ServiceHealth(
                service_name=service_name,
                service_type=service_type or ServiceType.API_GATEWAY,
                overall_status=overall_status,
                last_healthy=last_healthy,
                uptime_percentage=uptime_percentage,
                avg_response_time_ms=avg_response_time,
                check_results=recent_results[-10:],  # Keep last 10 results
                auto_healing_attempts=auto_healing_attempts,
                creator_segments_affected=list(creator_segments)
            )
            
        except Exception as e:
            logger.error(f"❌ Error updating service health for {service_name}: {e}")

    async def _trigger_auto_healing(self, service_name: str, result: HealthCheckResult) -> None:
        """Déclencher l'auto-healing pour un service défaillant."""
        try:
            if service_name not in self.service_health:
                return
            
            service_health = self.service_health[service_name]
            
            # Check auto-healing rate limits
            current_hour = datetime.now().hour
            max_attempts = self.config["auto_healing"]["max_attempts_per_hour"]
            
            if service_health.auto_healing_attempts >= max_attempts:
                logger.warning(f"⚠️ Auto-healing rate limit reached for {service_name}")
                return
            
            # Increment auto-healing attempts
            service_health.auto_healing_attempts += 1
            
            logger.info(f"🔧 Triggering auto-healing for {service_name} "
                       f"(attempt {service_health.auto_healing_attempts}/{max_attempts})")
            
            # Call registered auto-healing handler
            if service_name in self.auto_healing_handlers:
                await self.auto_healing_handlers[service_name](service_name, result)
            else:
                # Default auto-healing actions
                await self._default_auto_healing(service_name, result)
            
        except Exception as e:
            logger.error(f"❌ Error in auto-healing for {service_name}: {e}")

    async def _default_auto_healing(self, service_name: str, result: HealthCheckResult) -> None:
        """Actions d'auto-healing par défaut."""
        service_health = self.service_health[service_name]
        
        if service_health.service_type == ServiceType.MODEL_INFERENCE:
            logger.info(f"🔄 Restarting inference service: {service_name}")
            # In production: restart inference pods/containers
            await asyncio.sleep(2)  # Simulate restart time
            
        elif service_health.service_type == ServiceType.DATABASE:
            logger.info(f"🔄 Recycling database connections: {service_name}")
            # In production: recycle connection pool
            await asyncio.sleep(1)
            
        elif service_health.service_type == ServiceType.API_GATEWAY:
            logger.info(f"🔄 Scaling up API gateway: {service_name}")
            # In production: trigger auto-scaling
            await asyncio.sleep(3)
            
        else:
            logger.info(f"🔄 Generic service restart: {service_name}")
            await asyncio.sleep(2)

    async def _send_notifications(self, service_name: str, result: HealthCheckResult) -> None:
        """Envoyer des notifications pour les problèmes de santé."""
        try:
            # Only notify on status changes or critical issues
            should_notify = (
                result.status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY] or
                (service_name in self.service_health and 
                 self.service_health[service_name].overall_status != result.status)
            )
            
            if should_notify:
                for handler in self.notification_handlers:
                    try:
                        await handler(service_name, result)
                    except Exception as e:
                        logger.error(f"Notification handler error: {e}")
            
        except Exception as e:
            logger.error(f"❌ Error sending notifications: {e}")

    def register_auto_healing_handler(self, service_name: str, handler: Callable) -> None:
        """Enregistrer un handler d'auto-healing personnalisé."""
        self.auto_healing_handlers[service_name] = handler
        logger.info(f"✅ Registered auto-healing handler for {service_name}")

    def register_notification_handler(self, handler: Callable) -> None:
        """Enregistrer un handler de notification."""
        self.notification_handlers.append(handler)
        logger.info(f"✅ Registered notification handler")

    async def get_overall_health_status(self) -> Dict[str, Any]:
        """Obtenir le statut de santé global de la plateforme."""
        try:
            if not self.service_health:
                return {"status": "unknown", "message": "No services monitored"}
            
            # Count services by status
            status_counts = {}
            for status in HealthStatus:
                status_counts[status.value] = len([
                    s for s in self.service_health.values() 
                    if s.overall_status == status
                ])
            
            total_services = len(self.service_health)
            healthy_services = status_counts.get("healthy", 0)
            critical_services = status_counts.get("critical", 0)
            
            # Determine overall status
            if critical_services >= self.config["thresholds"]["critical_service_count"]:
                overall_status = HealthStatus.CRITICAL
            elif healthy_services / total_services >= 0.8:
                overall_status = HealthStatus.HEALTHY
            elif healthy_services / total_services >= 0.6:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.UNHEALTHY
            
            # Creator segment impact analysis
            creator_impact = {}
            for segment in ["musicians", "photographers", "bloggers", "influencers", "comedians"]:
                affected_services = [
                    s for s in self.service_health.values()
                    if segment in s.creator_segments_affected and s.overall_status != HealthStatus.HEALTHY
                ]
                
                creator_impact[segment] = {
                    "affected_services": len(affected_services),
                    "status": "impacted" if affected_services else "healthy"
                }
            
            return {
                "overall_status": overall_status.value,
                "total_services": total_services,
                "status_distribution": status_counts,
                "healthy_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
                "creator_segment_impact": creator_impact,
                "circuit_breakers_open": len([
                    cb for cb in self.circuit_breakers.values() 
                    if cb["state"] == "open"
                ]),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting overall health status: {e}")
            return {"status": "error", "message": str(e)}

    async def export_health_report(self, format_type: str = "json") -> str:
        """Exporter un rapport de santé complet."""
        try:
            overall_status = await self.get_overall_health_status()
            
            report_data = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "ml_services_health_report",
                    "monitoring_duration_hours": self.config["global_settings"]["check_result_retention_hours"]
                },
                "overall_health": overall_status,
                "service_details": {
                    service_name: {
                        **asdict(service_health),
                        "service_type": service_health.service_type.value,
                        "overall_status": service_health.overall_status.value,
                        "last_healthy": service_health.last_healthy.isoformat() if service_health.last_healthy else None
                    } for service_name, service_health in self.service_health.items()
                },
                "circuit_breaker_states": self.circuit_breakers,
                "health_check_configurations": {
                    check_id: {
                        **asdict(health_check),
                        "service_type": health_check.service_type.value,
                        "check_type": health_check.check_type.value
                    } for check_id, health_check in self.health_checks.items()
                }
            }
            
            # Export to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/health_report_{timestamp}.{format_type}"
            
            async with aiofiles.open(filename, 'w') as f:
                if format_type == "json":
                    await f.write(json.dumps(report_data, indent=2, default=str))
            
            logger.info(f"📊 Health report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error exporting health report: {e}")
            return ""

# Example usage and testing
async def main():
    """Example usage of health check manager."""
    print("🏥 MLOps Health Check Manager - Enterprise Demo")
    print("="*60)
    
    # Create health check manager
    manager = HealthCheckManager()
    
    # Register sample health checks
    print("\n📋 Registering health checks...")
    
    # Model inference service health check
    inference_check = HealthCheck(
        check_id="inference_service_http",
        service_name="model_inference_service",
        service_type=ServiceType.MODEL_INFERENCE,
        check_type=CheckType.HTTP_ENDPOINT,
        endpoint_url="http://localhost:8080/health",
        timeout_seconds=10,
        interval_seconds=30,
        expected_response_time_ms=100,
        creator_segments=["musicians", "influencers"],
        critical_for_business=True
    )
    
    await manager.register_health_check(inference_check)
    
    # Database health check
    db_check = HealthCheck(
        check_id="database_tcp",
        service_name="postgresql_db",
        service_type=ServiceType.DATABASE,
        check_type=CheckType.DATABASE_QUERY,
        host="localhost",
        port=5432,
        interval_seconds=60,
        creator_segments=["photographers", "bloggers"]
    )
    
    await manager.register_health_check(db_check)
    
    # Resource usage check
    resource_check = HealthCheck(
        check_id="system_resources",
        service_name="ml_compute_cluster",
        service_type=ServiceType.MODEL_TRAINING,
        check_type=CheckType.RESOURCE_USAGE,
        interval_seconds=45,
        creator_segments=["musicians", "photographers", "influencers"]
    )
    
    await manager.register_health_check(resource_check)
    
    print(f"   Registered {len(manager.health_checks)} health checks")
    
    # Register custom auto-healing handler
    async def custom_inference_healing(service_name: str, result: HealthCheckResult):
        print(f"🔧 Custom healing for {service_name}: Restarting inference pods")
        await asyncio.sleep(1)  # Simulate healing action
    
    manager.register_auto_healing_handler("model_inference_service", custom_inference_healing)
    
    # Register notification handler
    async def alert_handler(service_name: str, result: HealthCheckResult):
        print(f"🚨 ALERT: {service_name} status changed to {result.status.value}")
        if result.error_message:
            print(f"    Error: {result.error_message}")
    
    manager.register_notification_handler(alert_handler)
    
    # Run some health checks manually
    print(f"\n🔍 Running manual health checks...")
    
    for check_id, health_check in list(manager.health_checks.items())[:2]:
        print(f"\n--- Checking {health_check.service_name} ---")
        result = await manager._perform_health_check(health_check)
        
        print(f"   Status: {result.status.value}")
        if result.response_time_ms:
            print(f"   Response time: {result.response_time_ms:.1f}ms")
        if result.error_message:
            print(f"   Error: {result.error_message}")
        
        # Store result
        manager.check_results[check_id].append(result)
        await manager._update_service_health(health_check.service_name)
    
    # Get overall health status
    print(f"\n📊 Overall platform health status...")
    overall_health = await manager.get_overall_health_status()
    
    print(f"   Overall Status: {overall_health.get('overall_status', 'unknown')}")
    print(f"   Total Services: {overall_health.get('total_services', 0)}")
    print(f"   Healthy Percentage: {overall_health.get('healthy_percentage', 0):.1f}%")
    
    if overall_health.get('creator_segment_impact'):
        print(f"   Creator Segment Impact:")
        for segment, impact in overall_health['creator_segment_impact'].items():
            print(f"     {segment}: {impact['status']} ({impact['affected_services']} affected services)")
    
    # Test continuous monitoring briefly
    print(f"\n🔄 Starting brief continuous monitoring (10 seconds)...")
    
    # Start monitoring
    await manager.start_health_monitoring()
    
    # Let it run for a few seconds
    await asyncio.sleep(10)
    
    # Stop monitoring
    await manager.stop_health_monitoring()
    
    print(f"   Continuous monitoring stopped")
    
    # Export health report
    print(f"\n📊 Exporting health report...")
    report_file = await manager.export_health_report()
    print(f"   Report saved to: {report_file}")
    
    print(f"\n✅ Health check manager demo complete!")

if __name__ == "__main__":
    asyncio.run(main())