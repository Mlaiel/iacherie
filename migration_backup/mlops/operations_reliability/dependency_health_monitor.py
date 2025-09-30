"""
🛡️ MLOps Operations & Reliability - Dependency Health Monitor
==============================================================

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

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Enterprise dependency health monitor for Creator Economy external service monitoring.
Combining expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

import asyncio
import logging
import time
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
import hashlib
from urllib.parse import urljoin, urlparse


class DependencyType(Enum):
    """Types of external dependencies"""
    API_SERVICE = "api_service"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    STORAGE = "storage"
    CDN = "cdn"
    PAYMENT_GATEWAY = "payment_gateway"
    SOCIAL_MEDIA_API = "social_media_api"
    AI_SERVICE = "ai_service"
    ANALYTICS = "analytics"


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class CheckType(Enum):
    """Types of health checks"""
    HTTP_GET = "http_get"
    HTTP_POST = "http_post"
    TCP_CONNECT = "tcp_connect"
    DNS_RESOLVE = "dns_resolve"
    DATABASE_QUERY = "database_query"
    CUSTOM_SCRIPT = "custom_script"


@dataclass
class DependencyConfig:
    """Configuration for external dependency"""
    dependency_id: str
    name: str
    dependency_type: DependencyType
    endpoint: str
    check_type: CheckType
    check_interval: timedelta = timedelta(minutes=1)
    timeout: timedelta = timedelta(seconds=30)
    retry_count: int = 3
    expected_response_time: timedelta = timedelta(seconds=5)
    critical_for_creators: bool = False
    sla_target: float = 99.9  # 99.9% availability
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    dependency_id: str
    timestamp: datetime
    status: HealthStatus
    response_time: timedelta
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyMetrics:
    """Aggregated metrics for a dependency"""
    dependency_id: str
    availability_percentage: float
    average_response_time: timedelta
    p95_response_time: timedelta
    p99_response_time: timedelta
    error_rate: float
    last_successful_check: Optional[datetime]
    last_failed_check: Optional[datetime]
    consecutive_failures: int
    total_checks: int
    successful_checks: int


@dataclass
class HealthAlert:
    """Health alert for dependency issues"""
    alert_id: str
    dependency_id: str
    severity: AlertSeverity
    message: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    creator_impact_estimate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DependencyHealthMonitor:
    """
    Enterprise dependency health monitor for Creator Economy external services.
    
    Provides comprehensive monitoring of external dependencies, SLA tracking,
    and intelligent alerting for creator-impacting service degradations.
    """
    
    def __init__(self):
        """Initialize dependency health monitor"""
        self.logger = logging.getLogger(__name__)
        self.dependencies = {}
        self.health_results = {}
        self.metrics_cache = {}
        self.active_alerts = {}
        self.alert_callbacks = []
        self.monitoring_tasks = {}
        
        # Health check session with connection pooling
        self.session = None
        
        self.logger.info("DependencyHealthMonitor initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=20)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def register_dependency(
        self,
        dependency_config: DependencyConfig
    ) -> bool:
        """
        Register a new external dependency for monitoring
        
        Args:
            dependency_config: Dependency configuration
            
        Returns:
            True if registration successful
        """
        try:
            dependency_id = dependency_config.dependency_id
            
            # Validate configuration
            if not dependency_config.endpoint:
                raise ValueError("Endpoint is required for dependency monitoring")
            
            # Store dependency configuration
            self.dependencies[dependency_id] = dependency_config
            
            # Initialize health results storage
            self.health_results[dependency_id] = []
            
            # Initialize metrics cache
            self.metrics_cache[dependency_id] = None
            
            self.logger.info(f"Registered dependency: {dependency_id} ({dependency_config.name})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering dependency: {str(e)}")
            raise
    
    async def start_monitoring(self, dependency_id: str) -> bool:
        """
        Start monitoring a registered dependency
        
        Args:
            dependency_id: ID of dependency to monitor
            
        Returns:
            True if monitoring started successfully
        """
        try:
            if dependency_id not in self.dependencies:
                raise ValueError(f"Dependency {dependency_id} not registered")
            
            if dependency_id in self.monitoring_tasks:
                self.logger.warning(f"Monitoring already active for {dependency_id}")
                return True
            
            # Start monitoring task
            config = self.dependencies[dependency_id]
            task = asyncio.create_task(self._monitor_dependency(config))
            self.monitoring_tasks[dependency_id] = task
            
            self.logger.info(f"Started monitoring for dependency: {dependency_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring for {dependency_id}: {str(e)}")
            raise
    
    async def stop_monitoring(self, dependency_id: str) -> bool:
        """
        Stop monitoring a dependency
        
        Args:
            dependency_id: ID of dependency to stop monitoring
            
        Returns:
            True if monitoring stopped successfully
        """
        try:
            if dependency_id in self.monitoring_tasks:
                task = self.monitoring_tasks[dependency_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                del self.monitoring_tasks[dependency_id]
                self.logger.info(f"Stopped monitoring for dependency: {dependency_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring for {dependency_id}: {str(e)}")
            raise
    
    async def _monitor_dependency(self, config: DependencyConfig):
        """
        Main monitoring loop for a dependency
        
        Args:
            config: Dependency configuration
        """
        dependency_id = config.dependency_id
        
        try:
            while True:
                # Perform health check
                result = await self._perform_health_check(config)
                
                # Store result
                self._store_health_result(dependency_id, result)
                
                # Update metrics
                await self._update_dependency_metrics(dependency_id)
                
                # Check for alerts
                await self._evaluate_alerts(dependency_id, result)
                
                # Wait for next check
                await asyncio.sleep(config.check_interval.total_seconds())
                
        except asyncio.CancelledError:
            self.logger.info(f"Monitoring cancelled for dependency: {dependency_id}")
            raise
        except Exception as e:
            self.logger.error(f"Error in monitoring loop for {dependency_id}: {str(e)}")
    
    async def _perform_health_check(
        self,
        config: DependencyConfig
    ) -> HealthCheckResult:
        """
        Perform health check for a dependency
        
        Args:
            config: Dependency configuration
            
        Returns:
            Health check result
        """
        dependency_id = config.dependency_id
        check_start = time.time()
        
        try:
            if config.check_type == CheckType.HTTP_GET:
                result = await self._perform_http_check(config, "GET")
            elif config.check_type == CheckType.HTTP_POST:
                result = await self._perform_http_check(config, "POST")
            elif config.check_type == CheckType.TCP_CONNECT:
                result = await self._perform_tcp_check(config)
            elif config.check_type == CheckType.DNS_RESOLVE:
                result = await self._perform_dns_check(config)
            elif config.check_type == CheckType.DATABASE_QUERY:
                result = await self._perform_database_check(config)
            elif config.check_type == CheckType.CUSTOM_SCRIPT:
                result = await self._perform_custom_check(config)
            else:
                raise ValueError(f"Unsupported check type: {config.check_type}")
            
            # Calculate response time
            response_time = timedelta(seconds=time.time() - check_start)
            result.response_time = response_time
            
            return result
            
        except Exception as e:
            response_time = timedelta(seconds=time.time() - check_start)
            
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=HealthStatus.CRITICAL,
                response_time=response_time,
                error_message=str(e)
            )
    
    async def _perform_http_check(
        self,
        config: DependencyConfig,
        method: str
    ) -> HealthCheckResult:
        """Perform HTTP health check"""
        dependency_id = config.dependency_id
        
        if not self.session:
            raise RuntimeError("HTTP session not initialized. Use async context manager.")
        
        headers = config.metadata.get('headers', {})
        data = config.metadata.get('data') if method == "POST" else None
        expected_status = config.metadata.get('expected_status_code', 200)
        
        async with self.session.request(
            method,
            config.endpoint,
            headers=headers,
            data=data,
            timeout=aiohttp.ClientTimeout(total=config.timeout.total_seconds())
        ) as response:
            status_code = response.status
            response_text = await response.text()
            
            # Determine health status
            if status_code == expected_status:
                status = HealthStatus.HEALTHY
            elif 200 <= status_code < 300:
                status = HealthStatus.HEALTHY
            elif 400 <= status_code < 500:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=status,
                response_time=timedelta(0),  # Will be set by caller
                status_code=status_code,
                details={
                    'response_size': len(response_text),
                    'headers': dict(response.headers)
                }
            )
    
    async def _perform_tcp_check(self, config: DependencyConfig) -> HealthCheckResult:
        """Perform TCP connectivity check"""
        dependency_id = config.dependency_id
        
        try:
            # Parse endpoint for host and port
            parsed = urlparse(f"//{config.endpoint}")
            host = parsed.hostname
            port = parsed.port or 80
            
            # Attempt TCP connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=config.timeout.total_seconds()
            )
            
            writer.close()
            await writer.wait_closed()
            
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=HealthStatus.HEALTHY,
                response_time=timedelta(0),
                details={'host': host, 'port': port}
            )
            
        except Exception as e:
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=HealthStatus.UNHEALTHY,
                response_time=timedelta(0),
                error_message=f"TCP connection failed: {str(e)}"
            )
    
    async def _perform_dns_check(self, config: DependencyConfig) -> HealthCheckResult:
        """Perform DNS resolution check"""
        dependency_id = config.dependency_id
        
        try:
            import socket
            
            # Extract hostname from endpoint
            parsed = urlparse(f"//{config.endpoint}")
            hostname = parsed.hostname or config.endpoint
            
            # Perform DNS lookup
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, socket.gethostbyname, hostname
            )
            
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=HealthStatus.HEALTHY,
                response_time=timedelta(0),
                details={'hostname': hostname, 'resolved_ip': result}
            )
            
        except Exception as e:
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=HealthStatus.UNHEALTHY,
                response_time=timedelta(0),
                error_message=f"DNS resolution failed: {str(e)}"
            )
    
    async def _perform_database_check(self, config: DependencyConfig) -> HealthCheckResult:
        """Perform database health check"""
        dependency_id = config.dependency_id
        
        # Simulate database health check
        # In real implementation, would connect to actual database
        try:
            test_query = config.metadata.get('test_query', 'SELECT 1')
            
            # Simulate query execution
            await asyncio.sleep(0.1)  # Simulate query time
            
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=HealthStatus.HEALTHY,
                response_time=timedelta(0),
                details={'query': test_query, 'simulated': True}
            )
            
        except Exception as e:
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=HealthStatus.UNHEALTHY,
                response_time=timedelta(0),
                error_message=f"Database check failed: {str(e)}"
            )
    
    async def _perform_custom_check(self, config: DependencyConfig) -> HealthCheckResult:
        """Perform custom script health check"""
        dependency_id = config.dependency_id
        
        try:
            script_path = config.metadata.get('script_path')
            if not script_path:
                raise ValueError("script_path required for custom check")
            
            # Simulate script execution
            await asyncio.sleep(0.2)  # Simulate script execution time
            
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=HealthStatus.HEALTHY,
                response_time=timedelta(0),
                details={'script_path': script_path, 'simulated': True}
            )
            
        except Exception as e:
            return HealthCheckResult(
                dependency_id=dependency_id,
                timestamp=datetime.now(),
                status=HealthStatus.UNHEALTHY,
                response_time=timedelta(0),
                error_message=f"Custom check failed: {str(e)}"
            )
    
    def _store_health_result(self, dependency_id: str, result: HealthCheckResult):
        """Store health check result"""
        if dependency_id not in self.health_results:
            self.health_results[dependency_id] = []
        
        # Store result
        self.health_results[dependency_id].append(result)
        
        # Keep only last 1000 results to manage memory
        if len(self.health_results[dependency_id]) > 1000:
            self.health_results[dependency_id] = self.health_results[dependency_id][-1000:]
    
    async def _update_dependency_metrics(self, dependency_id: str):
        """Update aggregated metrics for a dependency"""
        if dependency_id not in self.health_results:
            return
        
        results = self.health_results[dependency_id]
        if not results:
            return
        
        # Calculate metrics from recent results (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_results = [r for r in results if r.timestamp >= cutoff_time]
        
        if not recent_results:
            return
        
        # Calculate availability
        successful_checks = len([r for r in recent_results if r.status == HealthStatus.HEALTHY])
        total_checks = len(recent_results)
        availability = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
        
        # Calculate response times
        response_times = [r.response_time.total_seconds() for r in recent_results]
        avg_response_time = timedelta(seconds=statistics.mean(response_times)) if response_times else timedelta(0)
        
        # Calculate percentiles
        if response_times:
            p95_response_time = timedelta(seconds=statistics.quantiles(response_times, n=20)[18])  # 95th percentile
            p99_response_time = timedelta(seconds=statistics.quantiles(response_times, n=100)[98])  # 99th percentile
        else:
            p95_response_time = timedelta(0)
            p99_response_time = timedelta(0)
        
        # Calculate error rate
        error_rate = ((total_checks - successful_checks) / total_checks) * 100 if total_checks > 0 else 0
        
        # Find last successful and failed checks
        last_successful = None
        last_failed = None
        for result in reversed(recent_results):
            if result.status == HealthStatus.HEALTHY and last_successful is None:
                last_successful = result.timestamp
            elif result.status != HealthStatus.HEALTHY and last_failed is None:
                last_failed = result.timestamp
        
        # Count consecutive failures
        consecutive_failures = 0
        for result in reversed(recent_results):
            if result.status != HealthStatus.HEALTHY:
                consecutive_failures += 1
            else:
                break
        
        # Create metrics object
        metrics = DependencyMetrics(
            dependency_id=dependency_id,
            availability_percentage=availability,
            average_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            error_rate=error_rate,
            last_successful_check=last_successful,
            last_failed_check=last_failed,
            consecutive_failures=consecutive_failures,
            total_checks=total_checks,
            successful_checks=successful_checks
        )
        
        self.metrics_cache[dependency_id] = metrics
    
    async def _evaluate_alerts(self, dependency_id: str, result: HealthCheckResult):
        """Evaluate if alerts should be triggered"""
        config = self.dependencies[dependency_id]
        metrics = self.metrics_cache.get(dependency_id)
        
        if not metrics:
            return
        
        alerts_to_create = []
        
        # Check availability threshold
        if metrics.availability_percentage < config.sla_target:
            severity = AlertSeverity.CRITICAL if config.critical_for_creators else AlertSeverity.WARNING
            creator_impact = self._estimate_creator_impact(dependency_id, metrics)
            
            alert = HealthAlert(
                alert_id=f"availability_{dependency_id}_{int(time.time())}",
                dependency_id=dependency_id,
                severity=severity,
                message=f"Availability dropped to {metrics.availability_percentage:.1f}% "
                       f"(SLA: {config.sla_target}%)",
                created_at=datetime.now(),
                creator_impact_estimate=creator_impact
            )
            alerts_to_create.append(alert)
        
        # Check consecutive failures
        if metrics.consecutive_failures >= 5:
            severity = AlertSeverity.EMERGENCY if config.critical_for_creators else AlertSeverity.CRITICAL
            creator_impact = self._estimate_creator_impact(dependency_id, metrics)
            
            alert = HealthAlert(
                alert_id=f"consecutive_failures_{dependency_id}_{int(time.time())}",
                dependency_id=dependency_id,
                severity=severity,
                message=f"{metrics.consecutive_failures} consecutive failures detected",
                created_at=datetime.now(),
                creator_impact_estimate=creator_impact
            )
            alerts_to_create.append(alert)
        
        # Check response time degradation
        if metrics.average_response_time > config.expected_response_time * 2:
            severity = AlertSeverity.WARNING
            creator_impact = self._estimate_creator_impact(dependency_id, metrics)
            
            alert = HealthAlert(
                alert_id=f"response_time_{dependency_id}_{int(time.time())}",
                dependency_id=dependency_id,
                severity=severity,
                message=f"Response time degraded to {metrics.average_response_time.total_seconds():.1f}s "
                       f"(expected: {config.expected_response_time.total_seconds():.1f}s)",
                created_at=datetime.now(),
                creator_impact_estimate=creator_impact
            )
            alerts_to_create.append(alert)
        
        # Create and store alerts
        for alert in alerts_to_create:
            await self._create_alert(alert)
    
    def _estimate_creator_impact(
        self,
        dependency_id: str,
        metrics: DependencyMetrics
    ) -> float:
        """Estimate creator impact percentage"""
        config = self.dependencies[dependency_id]
        
        # Base impact on dependency type and criticality
        base_impact = {
            DependencyType.PAYMENT_GATEWAY: 80.0,
            DependencyType.SOCIAL_MEDIA_API: 60.0,
            DependencyType.AI_SERVICE: 70.0,
            DependencyType.CDN: 50.0,
            DependencyType.STORAGE: 65.0,
            DependencyType.API_SERVICE: 40.0,
            DependencyType.DATABASE: 90.0,
            DependencyType.CACHE: 30.0,
            DependencyType.MESSAGE_QUEUE: 45.0,
            DependencyType.ANALYTICS: 20.0
        }.get(config.dependency_type, 30.0)
        
        # Adjust based on availability
        availability_factor = (100 - metrics.availability_percentage) / 100
        
        # Critical dependencies have higher impact
        criticality_multiplier = 2.0 if config.critical_for_creators else 1.0
        
        estimated_impact = base_impact * availability_factor * criticality_multiplier
        return min(100.0, estimated_impact)
    
    async def _create_alert(self, alert: HealthAlert):
        """Create and process a new alert"""
        alert_key = f"{alert.dependency_id}_{alert.severity.value}"
        
        # Avoid duplicate alerts
        if alert_key in self.active_alerts:
            existing_alert = self.active_alerts[alert_key]
            if (datetime.now() - existing_alert.created_at) < timedelta(minutes=15):
                return  # Skip duplicate alert within 15 minutes
        
        # Store active alert
        self.active_alerts[alert_key] = alert
        
        # Notify alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {str(e)}")
        
        self.logger.warning(f"Created alert: {alert.alert_id} - {alert.message}")
    
    async def register_alert_callback(self, callback: Callable[[HealthAlert], None]):
        """Register callback for health alerts"""
        self.alert_callbacks.append(callback)
        self.logger.info("Registered alert callback")
    
    async def get_dependency_metrics(self, dependency_id: str) -> Optional[DependencyMetrics]:
        """Get current metrics for a dependency"""
        return self.metrics_cache.get(dependency_id)
    
    async def get_all_dependencies_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status overview for all dependencies"""
        status_overview = {}
        
        for dependency_id, config in self.dependencies.items():
            metrics = self.metrics_cache.get(dependency_id)
            recent_results = self.health_results.get(dependency_id, [])
            
            # Get last result
            last_result = recent_results[-1] if recent_results else None
            
            status_info = {
                'name': config.name,
                'type': config.dependency_type.value,
                'endpoint': config.endpoint,
                'critical_for_creators': config.critical_for_creators,
                'last_check': last_result.timestamp.isoformat() if last_result else None,
                'current_status': last_result.status.value if last_result else HealthStatus.UNKNOWN.value,
                'monitoring_active': dependency_id in self.monitoring_tasks
            }
            
            if metrics:
                status_info.update({
                    'availability_percentage': metrics.availability_percentage,
                    'average_response_time_ms': metrics.average_response_time.total_seconds() * 1000,
                    'error_rate': metrics.error_rate,
                    'consecutive_failures': metrics.consecutive_failures,
                    'sla_compliant': metrics.availability_percentage >= config.sla_target
                })
            
            status_overview[dependency_id] = status_info
        
        return status_overview
    
    async def generate_health_report(
        self,
        time_range: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """
        Generate comprehensive health report
        
        Args:
            time_range: Time range for report data
            
        Returns:
            Comprehensive health report
        """
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'time_range': str(time_range),
                'summary': {},
                'dependencies': {},
                'alerts': [],
                'recommendations': []
            }
            
            # Get all dependency statuses
            all_status = await self.get_all_dependencies_status()
            
            # Calculate summary metrics
            total_dependencies = len(all_status)
            healthy_dependencies = len([
                dep for dep in all_status.values()
                if dep.get('current_status') == HealthStatus.HEALTHY.value
            ])
            critical_dependencies = len([
                dep for dep in all_status.values()
                if dep.get('critical_for_creators', False)
            ])
            sla_violations = len([
                dep for dep in all_status.values()
                if not dep.get('sla_compliant', True)
            ])
            
            report['summary'] = {
                'total_dependencies': total_dependencies,
                'healthy_dependencies': healthy_dependencies,
                'health_percentage': (healthy_dependencies / total_dependencies * 100) if total_dependencies > 0 else 0,
                'critical_dependencies': critical_dependencies,
                'sla_violations': sla_violations,
                'overall_creator_impact': await self._calculate_overall_creator_impact()
            }
            
            # Add detailed dependency information
            report['dependencies'] = all_status
            
            # Add active alerts
            report['alerts'] = [
                {
                    'alert_id': alert.alert_id,
                    'dependency_id': alert.dependency_id,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'created_at': alert.created_at.isoformat(),
                    'creator_impact_estimate': alert.creator_impact_estimate
                }
                for alert in self.active_alerts.values()
            ]
            
            # Generate recommendations
            report['recommendations'] = await self._generate_health_recommendations(all_status)
            
            self.logger.info(f"Generated health report for {total_dependencies} dependencies")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating health report: {str(e)}")
            raise
    
    async def _calculate_overall_creator_impact(self) -> float:
        """Calculate overall creator impact across all dependencies"""
        total_impact = 0.0
        dependency_count = 0
        
        for dependency_id in self.dependencies:
            metrics = self.metrics_cache.get(dependency_id)
            if metrics:
                impact = self._estimate_creator_impact(dependency_id, metrics)
                total_impact += impact
                dependency_count += 1
        
        return total_impact / dependency_count if dependency_count > 0 else 0.0
    
    async def _generate_health_recommendations(
        self,
        all_status: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        # Check for SLA violations
        sla_violations = [
            dep_id for dep_id, status in all_status.items()
            if not status.get('sla_compliant', True)
        ]
        
        if sla_violations:
            recommendations.append(
                f"Address SLA violations in {len(sla_violations)} dependencies: "
                f"{', '.join(sla_violations[:3])}"
                + ("..." if len(sla_violations) > 3 else "")
            )
        
        # Check for high error rates
        high_error_rate_deps = [
            dep_id for dep_id, status in all_status.items()
            if status.get('error_rate', 0) > 5.0
        ]
        
        if high_error_rate_deps:
            recommendations.append(
                f"Investigate high error rates in: {', '.join(high_error_rate_deps[:3])}"
            )
        
        # Check for slow response times
        slow_response_deps = [
            dep_id for dep_id, status in all_status.items()
            if status.get('average_response_time_ms', 0) > 5000
        ]
        
        if slow_response_deps:
            recommendations.append(
                f"Optimize response times for: {', '.join(slow_response_deps[:3])}"
            )
        
        # Check for unmonitored critical dependencies
        unmonitored_critical = [
            dep_id for dep_id, status in all_status.items()
            if status.get('critical_for_creators', False) and not status.get('monitoring_active', False)
        ]
        
        if unmonitored_critical:
            recommendations.append(
                f"Enable monitoring for critical dependencies: {', '.join(unmonitored_critical)}"
            )
        
        return recommendations
    
    def get_monitor_status(self) -> Dict[str, Any]:
        """Get dependency monitor status"""
        return {
            'monitor_name': 'DependencyHealthMonitor',
            'version': '1.0.0',
            'status': 'active',
            'registered_dependencies': len(self.dependencies),
            'active_monitoring_tasks': len(self.monitoring_tasks),
            'active_alerts': len(self.active_alerts),
            'supported_dependency_types': [dep_type.value for dep_type in DependencyType],
            'supported_check_types': [check_type.value for check_type in CheckType]
        }


# Export main classes and enums
__all__ = [
    'DependencyHealthMonitor',
    'DependencyType',
    'HealthStatus',
    'AlertSeverity',
    'CheckType',
    'DependencyConfig',
    'HealthCheckResult',
    'DependencyMetrics',
    'HealthAlert'
]