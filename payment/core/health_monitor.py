"""💳 Gateway Health Monitor
==========================

Enterprise health monitoring system for payment gateway providers
with real-time monitoring, alerting, SLA tracking, and automated
failover capabilities.

Features:
- Provider uptime and performance tracking
- Response time and success rate monitoring
- Automatic failover trigger mechanisms
- SLA compliance monitoring
- Real-time alerting and notifications
- Performance trend analysis

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import statistics
from collections import deque, defaultdict
import aiohttp
import time

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNAVAILABLE = "unavailable"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class HealthMetric:
    """Individual health metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    status: HealthStatus
    threshold_warning: float
    threshold_critical: float


@dataclass
class ProviderHealthStatus:
    """Complete health status for a provider"""
    provider_name: str
    overall_status: HealthStatus
    uptime_percentage: float
    response_time_avg: float
    success_rate: float
    error_rate: float
    last_successful_request: datetime
    last_failed_request: Optional[datetime]
    metrics: Dict[str, HealthMetric]
    alerts: List['HealthAlert']
    sla_compliance: float
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class HealthAlert:
    """Health monitoring alert"""
    alert_id: str
    provider_name: str
    alert_level: AlertLevel
    message: str
    metric_name: str
    current_value: float
    threshold_value: float
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


@dataclass
class SLATarget:
    """SLA target definition"""
    metric_name: str
    target_value: float
    measurement_period: timedelta
    penalty_threshold: float
    enabled: bool = True


@dataclass
class HealthCheckConfig:
    """Configuration for health checks"""
    provider_name: str
    endpoint_url: str
    check_interval: int  # seconds
    timeout: int  # seconds
    success_criteria: Dict[str, Any]
    headers: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True


class GatewayHealthMonitor:
    """
    Comprehensive health monitoring system for payment gateway providers
    with real-time monitoring, alerting, and SLA tracking.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize gateway health monitor"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Health status tracking
        self.provider_health: Dict[str, ProviderHealthStatus] = {}
        
        # Health check configurations
        self.health_check_configs: Dict[str, HealthCheckConfig] = {}
        
        # Performance history
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # SLA targets
        self.sla_targets: Dict[str, List[SLATarget]] = defaultdict(list)
        
        # Active alerts
        self.active_alerts: Dict[str, List[HealthAlert]] = defaultdict(list)
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring task
        self.monitoring_task = None
        self.is_monitoring = False
        
        # HTTP session for health checks
        self.http_session = None
    
    async def initialize(self):
        """Initialize the health monitor"""
        try:
            # Create HTTP session
            self.http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Load health check configurations
            await self._load_health_check_configs()
            
            # Load SLA targets
            await self._load_sla_targets()
            
            # Start monitoring
            await self.start_monitoring()
            
            self.logger.info("Gateway health monitor initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize health monitor: {e}")
            raise
    
    async def start_monitoring(self):
        """Start health monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self.http_session:
            await self.http_session.close()
        
        self.logger.info("Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Perform health checks for all configured providers
                check_tasks = []
                for provider_name, config in self.health_check_configs.items():
                    if config.enabled:
                        task = asyncio.create_task(
                            self._perform_health_check(provider_name, config)
                        )
                        check_tasks.append(task)
                
                # Wait for all health checks to complete
                if check_tasks:
                    await asyncio.gather(*check_tasks, return_exceptions=True)
                
                # Update overall health status
                await self._update_health_status()
                
                # Check SLA compliance
                await self._check_sla_compliance()
                
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_check(self, provider_name: str, config: HealthCheckConfig):
        """Perform health check for a provider"""
        try:
            start_time = time.time()
            
            # Make health check request
            async with self.http_session.get(
                config.endpoint_url,
                headers=config.headers,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                response_time = time.time() - start_time
                
                # Check success criteria
                success = await self._evaluate_success_criteria(
                    response, config.success_criteria
                )
                
                # Record result
                await self._record_health_check_result(
                    provider_name, success, response_time, response.status
                )
                
        except asyncio.TimeoutError:
            response_time = config.timeout
            await self._record_health_check_result(
                provider_name, False, response_time, 0, "Timeout"
            )
            
        except Exception as e:
            await self._record_health_check_result(
                provider_name, False, 0, 0, str(e)
            )
    
    async def _evaluate_success_criteria(self, response: aiohttp.ClientResponse, 
                                       criteria: Dict[str, Any]) -> bool:
        """Evaluate if response meets success criteria"""
        # Check status code
        if 'status_code' in criteria:
            expected_status = criteria['status_code']
            if isinstance(expected_status, list):
                if response.status not in expected_status:
                    return False
            elif response.status != expected_status:
                return False
        
        # Check response time (already handled in calling function)
        
        # Check response body if specified
        if 'response_contains' in criteria:
            try:
                body = await response.text()
                if criteria['response_contains'] not in body:
                    return False
            except:
                return False
        
        # Check JSON response if specified
        if 'json_field' in criteria:
            try:
                data = await response.json()
                field_path = criteria['json_field'].split('.')
                value = data
                for field in field_path:
                    value = value[field]
                
                if 'json_value' in criteria and value != criteria['json_value']:
                    return False
                    
            except:
                return False
        
        return True
    
    async def _record_health_check_result(self, provider_name: str, success: bool, 
                                        response_time: float, status_code: int,
                                        error_message: Optional[str] = None):
        """Record health check result"""
        timestamp = datetime.now()
        
        # Record in performance history
        result = {
            'timestamp': timestamp.isoformat(),
            'success': success,
            'response_time': response_time,
            'status_code': status_code,
            'error_message': error_message
        }
        
        self.performance_history[provider_name].append(result)
        
        # Update provider health status
        if provider_name not in self.provider_health:
            self.provider_health[provider_name] = ProviderHealthStatus(
                provider_name=provider_name,
                overall_status=HealthStatus.HEALTHY,
                uptime_percentage=100.0,
                response_time_avg=0.0,
                success_rate=100.0,
                error_rate=0.0,
                last_successful_request=timestamp,
                last_failed_request=None,
                metrics={},
                alerts=[],
                sla_compliance=100.0
            )
        
        health_status = self.provider_health[provider_name]
        
        if success:
            health_status.last_successful_request = timestamp
        else:
            health_status.last_failed_request = timestamp
            
            # Create alert for failure
            await self._create_alert(
                provider_name=provider_name,
                alert_level=AlertLevel.WARNING,
                message=f"Health check failed: {error_message or 'Unknown error'}",
                metric_name="health_check",
                current_value=0,
                threshold_value=1
            )
        
        # Update metrics
        await self._update_provider_metrics(provider_name)
    
    async def _update_provider_metrics(self, provider_name: str):
        """Update calculated metrics for provider"""
        history = list(self.performance_history[provider_name])
        if not history:
            return
        
        health_status = self.provider_health[provider_name]
        
        # Calculate success rate (last 100 checks)
        recent_checks = history[-100:]
        success_count = sum(1 for check in recent_checks if check['success'])
        health_status.success_rate = (success_count / len(recent_checks)) * 100
        health_status.error_rate = 100 - health_status.success_rate
        
        # Calculate average response time
        successful_checks = [check for check in recent_checks if check['success']]
        if successful_checks:
            response_times = [check['response_time'] for check in successful_checks]
            health_status.response_time_avg = statistics.mean(response_times)
        
        # Calculate uptime (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_24h = [
            check for check in history 
            if datetime.fromisoformat(check['timestamp']) > cutoff_time
        ]
        
        if recent_24h:
            uptime_count = sum(1 for check in recent_24h if check['success'])
            health_status.uptime_percentage = (uptime_count / len(recent_24h)) * 100
        
        # Update overall status based on metrics
        health_status.overall_status = await self._calculate_overall_status(health_status)
        health_status.last_updated = datetime.now()
        
        # Check for threshold violations
        await self._check_metric_thresholds(provider_name, health_status)
    
    async def _calculate_overall_status(self, health_status: ProviderHealthStatus) -> HealthStatus:
        """Calculate overall health status"""
        # Critical conditions
        if health_status.uptime_percentage < 95.0:
            return HealthStatus.CRITICAL
        if health_status.success_rate < 90.0:
            return HealthStatus.CRITICAL
        
        # Warning conditions
        if health_status.uptime_percentage < 98.0:
            return HealthStatus.WARNING
        if health_status.success_rate < 95.0:
            return HealthStatus.WARNING
        if health_status.response_time_avg > 5.0:  # 5 seconds
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    async def _check_metric_thresholds(self, provider_name: str, 
                                     health_status: ProviderHealthStatus):
        """Check metrics against thresholds and create alerts"""
        thresholds = {
            'success_rate': {'warning': 95.0, 'critical': 90.0},
            'uptime_percentage': {'warning': 98.0, 'critical': 95.0},
            'response_time_avg': {'warning': 3.0, 'critical': 5.0},
            'error_rate': {'warning': 5.0, 'critical': 10.0}
        }
        
        for metric_name, values in thresholds.items():
            current_value = getattr(health_status, metric_name)
            
            # For error_rate, higher is worse
            if metric_name == 'error_rate':
                if current_value >= values['critical']:
                    await self._create_alert(
                        provider_name, AlertLevel.CRITICAL,
                        f"High error rate: {current_value:.1f}%",
                        metric_name, current_value, values['critical']
                    )
                elif current_value >= values['warning']:
                    await self._create_alert(
                        provider_name, AlertLevel.WARNING,
                        f"Elevated error rate: {current_value:.1f}%",
                        metric_name, current_value, values['warning']
                    )
            
            # For response_time_avg, higher is worse
            elif metric_name == 'response_time_avg':
                if current_value >= values['critical']:
                    await self._create_alert(
                        provider_name, AlertLevel.CRITICAL,
                        f"Slow response time: {current_value:.2f}s",
                        metric_name, current_value, values['critical']
                    )
                elif current_value >= values['warning']:
                    await self._create_alert(
                        provider_name, AlertLevel.WARNING,
                        f"Elevated response time: {current_value:.2f}s",
                        metric_name, current_value, values['warning']
                    )
            
            # For success_rate and uptime_percentage, lower is worse
            else:
                if current_value <= values['critical']:
                    await self._create_alert(
                        provider_name, AlertLevel.CRITICAL,
                        f"Low {metric_name.replace('_', ' ')}: {current_value:.1f}%",
                        metric_name, current_value, values['critical']
                    )
                elif current_value <= values['warning']:
                    await self._create_alert(
                        provider_name, AlertLevel.WARNING,
                        f"Decreased {metric_name.replace('_', ' ')}: {current_value:.1f}%",
                        metric_name, current_value, values['warning']
                    )
    
    async def _create_alert(self, provider_name: str, alert_level: AlertLevel,
                          message: str, metric_name: str, current_value: float,
                          threshold_value: float):
        """Create health alert"""
        alert_id = f"alert_{provider_name}_{metric_name}_{int(time.time())}"
        
        alert = HealthAlert(
            alert_id=alert_id,
            provider_name=provider_name,
            alert_level=alert_level,
            message=message,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            created_at=datetime.now()
        )
        
        # Check if similar alert already exists
        existing_alert = await self._find_existing_alert(provider_name, metric_name)
        if existing_alert:
            # Update existing alert
            existing_alert.current_value = current_value
            existing_alert.message = message
        else:
            # Add new alert
            self.active_alerts[provider_name].append(alert)
            
            # Update provider health status
            if provider_name in self.provider_health:
                self.provider_health[provider_name].alerts.append(alert)
            
            # Trigger alert callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback failed: {e}")
        
        self.logger.warning(f"Health alert: {provider_name} - {message}")
    
    async def _find_existing_alert(self, provider_name: str, metric_name: str) -> Optional[HealthAlert]:
        """Find existing unresolved alert for same metric"""
        for alert in self.active_alerts[provider_name]:
            if alert.metric_name == metric_name and not alert.resolved_at:
                return alert
        return None
    
    async def _update_health_status(self):
        """Update overall health status"""
        for provider_name in self.provider_health:
            await self._update_provider_metrics(provider_name)
    
    async def _check_sla_compliance(self):
        """Check SLA compliance for all providers"""
        for provider_name, targets in self.sla_targets.items():
            if provider_name not in self.provider_health:
                continue
                
            health_status = self.provider_health[provider_name]
            compliance_scores = []
            
            for target in targets:
                if not target.enabled:
                    continue
                    
                compliance = await self._calculate_sla_compliance(
                    provider_name, target
                )
                compliance_scores.append(compliance)
            
            # Overall SLA compliance is average of individual targets
            if compliance_scores:
                health_status.sla_compliance = statistics.mean(compliance_scores)
    
    async def _calculate_sla_compliance(self, provider_name: str, 
                                      target: SLATarget) -> float:
        """Calculate SLA compliance for specific target"""
        cutoff_time = datetime.now() - target.measurement_period
        
        relevant_history = [
            check for check in self.performance_history[provider_name]
            if datetime.fromisoformat(check['timestamp']) > cutoff_time
        ]
        
        if not relevant_history:
            return 100.0  # No data means compliance
        
        if target.metric_name == 'uptime':
            successful_checks = sum(1 for check in relevant_history if check['success'])
            actual_uptime = (successful_checks / len(relevant_history)) * 100
            return min(100.0, (actual_uptime / target.target_value) * 100)
        
        elif target.metric_name == 'response_time':
            successful_checks = [check for check in relevant_history if check['success']]
            if not successful_checks:
                return 0.0
            
            avg_response_time = statistics.mean(check['response_time'] for check in successful_checks)
            if avg_response_time <= target.target_value:
                return 100.0
            else:
                return max(0.0, 100.0 - ((avg_response_time - target.target_value) / target.target_value * 100))
        
        return 100.0
    
    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts"""
        cutoff_time = datetime.now() - timedelta(days=7)  # Keep alerts for 7 days
        
        for provider_name in self.active_alerts:
            self.active_alerts[provider_name] = [
                alert for alert in self.active_alerts[provider_name]
                if not alert.resolved_at or alert.resolved_at > cutoff_time
            ]
    
    async def get_provider_health(self, provider_name: str) -> Optional[ProviderHealthStatus]:
        """Get health status for specific provider"""
        return self.provider_health.get(provider_name)
    
    async def get_all_health_status(self) -> Dict[str, ProviderHealthStatus]:
        """Get health status for all providers"""
        return self.provider_health.copy()
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        for provider_alerts in self.active_alerts.values():
            for alert in provider_alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged_at = datetime.now()
                    alert.acknowledged_by = acknowledged_by
                    self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
                    return True
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for provider_alerts in self.active_alerts.values():
            for alert in provider_alerts:
                if alert.alert_id == alert_id:
                    alert.resolved_at = datetime.now()
                    self.logger.info(f"Alert {alert_id} resolved")
                    return True
        return False
    
    def add_alert_callback(self, callback: Callable):
        """Add callback function to be called when alerts are created"""
        self.alert_callbacks.append(callback)
    
    async def _load_health_check_configs(self):
        """Load health check configurations"""
        # This would typically load from database or configuration files
        # For now, providing a basic example
        default_configs = {
            'stripe': HealthCheckConfig(
                provider_name='stripe',
                endpoint_url='https://api.stripe.com/healthcheck',
                check_interval=60,
                timeout=10,
                success_criteria={'status_code': 200}
            )
        }
        
        self.health_check_configs.update(default_configs)
    
    async def _load_sla_targets(self):
        """Load SLA targets"""
        # Default SLA targets
        default_targets = {
            'stripe': [
                SLATarget(
                    metric_name='uptime',
                    target_value=99.9,
                    measurement_period=timedelta(hours=24),
                    penalty_threshold=99.0
                ),
                SLATarget(
                    metric_name='response_time',
                    target_value=2.0,  # 2 seconds
                    measurement_period=timedelta(hours=1),
                    penalty_threshold=5.0
                )
            ]
        }
        
        self.sla_targets.update(default_targets)


# Export main classes
__all__ = [
    "GatewayHealthMonitor",
    "ProviderHealthStatus",
    "HealthAlert",
    "HealthMetric",
    "SLATarget",
    "HealthCheckConfig",
    "HealthStatus",
    "AlertLevel"
]