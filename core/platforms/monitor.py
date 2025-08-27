"""
Platform Monitor Module

Real-time monitoring and health checking for all platform integrations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from dataclasses import dataclass, asdict
import time

from .base import PlatformBase, PlatformConfig, PlatformType, PlatformStatus

logger = logging.getLogger(__name__)


class MonitorSeverity(Enum):
    """Monitor alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitorStatus(Enum):
    """Platform monitor status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a platform health check"""
    platform_id: str
    status: MonitorStatus
    response_time_ms: float
    timestamp: datetime
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['status'] = self.status.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class MonitorAlert:
    """Platform monitoring alert"""
    platform_id: str
    severity: MonitorSeverity
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['severity'] = self.severity.value
        result['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            result['resolved_at'] = self.resolved_at.isoformat()
        return result


class PlatformMonitor:
    """Monitor platform health and performance"""
    
    def __init__(self, check_interval: int = 60, alert_threshold: int = 3):
        """
        Initialize platform monitor
        
        Args:
            check_interval: Health check interval in seconds
            alert_threshold: Number of consecutive failures before alerting
        """
        self.check_interval = check_interval
        self.alert_threshold = alert_threshold
        self.platforms: Dict[str, PlatformBase] = {}
        self.health_history: Dict[str, List[HealthCheckResult]] = {}
        self.active_alerts: Dict[str, List[MonitorAlert]] = {}
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.alert_handlers: List[Callable[[MonitorAlert], Awaitable[None]]] = []
        
    def register_platform(self, platform: PlatformBase):
        """Register a platform for monitoring"""
        self.platforms[platform.platform_id] = platform
        self.health_history[platform.platform_id] = []
        self.active_alerts[platform.platform_id] = []
        logger.info(f"Registered platform {platform.platform_id} for monitoring")
    
    def unregister_platform(self, platform_id: str):
        """Unregister a platform from monitoring"""
        if platform_id in self.platforms:
            del self.platforms[platform_id]
            del self.health_history[platform_id]
            del self.active_alerts[platform_id]
            logger.info(f"Unregistered platform {platform_id} from monitoring")
    
    def add_alert_handler(self, handler: Callable[[MonitorAlert], Awaitable[None]]):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    async def check_platform_health(self, platform: PlatformBase) -> HealthCheckResult:
        """Check health of a specific platform"""
        start_time = time.time()
        
        try:
            # Test basic connectivity with platform API
            if hasattr(platform, 'health_check'):
                # Use platform-specific health check if available
                is_healthy = await platform.health_check()
            else:
                # Default health check - try authentication
                is_healthy = await platform.authenticate()
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Determine status based on response time and success
            if is_healthy:
                if response_time < 1000:  # Under 1 second
                    status = MonitorStatus.HEALTHY
                elif response_time < 5000:  # Under 5 seconds
                    status = MonitorStatus.DEGRADED
                else:
                    status = MonitorStatus.DOWN
            else:
                status = MonitorStatus.DOWN
            
            result = HealthCheckResult(
                platform_id=platform.platform_id,
                status=status,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                metadata={
                    'error_count': platform.error_count,
                    'last_error': platform.last_error,
                    'platform_status': platform.status.value if platform.status else None
                }
            )
            
            # Store health result
            self.health_history[platform.platform_id].append(result)
            
            # Keep only last 100 health checks
            if len(self.health_history[platform.platform_id]) > 100:
                self.health_history[platform.platform_id] = self.health_history[platform.platform_id][-100:]
            
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_message = str(e)
            
            result = HealthCheckResult(
                platform_id=platform.platform_id,
                status=MonitorStatus.DOWN,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                error_message=error_message,
                metadata={'exception_type': type(e).__name__}
            )
            
            self.health_history[platform.platform_id].append(result)
            logger.error(f"Health check failed for {platform.platform_id}: {error_message}")
            
            return result
    
    async def check_all_platforms(self) -> Dict[str, HealthCheckResult]:
        """Check health of all registered platforms"""
        results = {}
        
        # Run health checks concurrently
        tasks = []
        for platform_id, platform in self.platforms.items():
            task = asyncio.create_task(
                self.check_platform_health(platform),
                name=f"health_check_{platform_id}"
            )
            tasks.append((platform_id, task))
        
        # Wait for all checks to complete
        for platform_id, task in tasks:
            try:
                result = await task
                results[platform_id] = result
                
                # Check for alerting conditions
                await self._evaluate_alerts(platform_id, result)
                
            except Exception as e:
                logger.error(f"Error checking {platform_id}: {e}")
                results[platform_id] = HealthCheckResult(
                    platform_id=platform_id,
                    status=MonitorStatus.UNKNOWN,
                    response_time_ms=0,
                    timestamp=datetime.utcnow(),
                    error_message=str(e)
                )
        
        return results
    
    async def _evaluate_alerts(self, platform_id: str, result: HealthCheckResult):
        """Evaluate if alerts should be triggered"""
        history = self.health_history[platform_id]
        
        # Check for consecutive failures
        if len(history) >= self.alert_threshold:
            recent_checks = history[-self.alert_threshold:]
            
            # Critical alert: all recent checks failed
            if all(check.status == MonitorStatus.DOWN for check in recent_checks):
                await self._trigger_alert(
                    platform_id,
                    MonitorSeverity.CRITICAL,
                    f"Platform {platform_id} has been down for {self.alert_threshold} consecutive checks",
                    {'consecutive_failures': self.alert_threshold}
                )
            
            # Warning alert: degraded performance
            elif all(check.status == MonitorStatus.DEGRADED for check in recent_checks):
                await self._trigger_alert(
                    platform_id,
                    MonitorSeverity.WARNING,
                    f"Platform {platform_id} has degraded performance for {self.alert_threshold} consecutive checks",
                    {'consecutive_degraded': self.alert_threshold}
                )
        
        # Check for high response times
        if result.response_time_ms > 10000:  # Over 10 seconds
            await self._trigger_alert(
                platform_id,
                MonitorSeverity.ERROR,
                f"Platform {platform_id} response time is {result.response_time_ms:.0f}ms",
                {'response_time_ms': result.response_time_ms}
            )
        
        # Check for recovery
        if len(history) >= 2:
            prev_result = history[-2]
            if (prev_result.status in [MonitorStatus.DOWN, MonitorStatus.DEGRADED] and 
                result.status == MonitorStatus.HEALTHY):
                await self._resolve_alerts(platform_id, "Platform recovered to healthy status")
    
    async def _trigger_alert(self, platform_id: str, severity: MonitorSeverity, 
                           message: str, metadata: Dict[str, Any] = None):
        """Trigger a monitoring alert"""
        # Check if similar alert already exists
        active_alerts = self.active_alerts[platform_id]
        for alert in active_alerts:
            if not alert.resolved and alert.severity == severity and message in alert.message:
                return  # Don't duplicate similar alerts
        
        alert = MonitorAlert(
            platform_id=platform_id,
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.active_alerts[platform_id].append(alert)
        logger.warning(f"Alert triggered: {alert.severity.value} - {message}")
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    async def _resolve_alerts(self, platform_id: str, resolution_message: str):
        """Resolve active alerts for a platform"""
        active_alerts = self.active_alerts[platform_id]
        resolved_count = 0
        
        for alert in active_alerts:
            if not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                alert.metadata = alert.metadata or {}
                alert.metadata['resolution'] = resolution_message
                resolved_count += 1
        
        if resolved_count > 0:
            logger.info(f"Resolved {resolved_count} alerts for {platform_id}: {resolution_message}")
    
    async def get_platform_status(self, platform_id: str) -> Dict[str, Any]:
        """Get comprehensive status for a platform"""
        if platform_id not in self.platforms:
            return {'error': 'Platform not found'}
        
        history = self.health_history[platform_id]
        active_alerts = [alert for alert in self.active_alerts[platform_id] if not alert.resolved]
        
        # Calculate uptime percentage (last 24 hours)
        now = datetime.utcnow()
        day_ago = now - timedelta(hours=24)
        recent_checks = [check for check in history if check.timestamp > day_ago]
        
        if recent_checks:
            healthy_checks = sum(1 for check in recent_checks if check.status == MonitorStatus.HEALTHY)
            uptime_percentage = (healthy_checks / len(recent_checks)) * 100
        else:
            uptime_percentage = 0
        
        # Calculate average response time
        if recent_checks:
            avg_response_time = sum(check.response_time_ms for check in recent_checks) / len(recent_checks)
        else:
            avg_response_time = 0
        
        latest_check = history[-1] if history else None
        
        return {
            'platform_id': platform_id,
            'current_status': latest_check.status.value if latest_check else 'unknown',
            'uptime_percentage_24h': round(uptime_percentage, 2),
            'average_response_time_ms': round(avg_response_time, 2),
            'active_alerts': len(active_alerts),
            'total_checks': len(history),
            'last_check': latest_check.to_dict() if latest_check else None,
            'alerts': [alert.to_dict() for alert in active_alerts]
        }
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get system-wide monitoring overview"""
        total_platforms = len(self.platforms)
        healthy_platforms = 0
        degraded_platforms = 0
        down_platforms = 0
        total_alerts = 0
        
        for platform_id in self.platforms:
            history = self.health_history[platform_id]
            if history:
                latest = history[-1]
                if latest.status == MonitorStatus.HEALTHY:
                    healthy_platforms += 1
                elif latest.status == MonitorStatus.DEGRADED:
                    degraded_platforms += 1
                elif latest.status == MonitorStatus.DOWN:
                    down_platforms += 1
            
            total_alerts += len([alert for alert in self.active_alerts[platform_id] if not alert.resolved])
        
        return {
            'total_platforms': total_platforms,
            'healthy_platforms': healthy_platforms,
            'degraded_platforms': degraded_platforms,
            'down_platforms': down_platforms,
            'total_active_alerts': total_alerts,
            'monitoring_active': self.monitoring_active,
            'check_interval_seconds': self.check_interval,
            'last_check': datetime.utcnow().isoformat()
        }
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Started platform monitoring with {self.check_interval}s interval")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped platform monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        try:
            while self.monitoring_active:
                logger.debug("Running platform health checks")
                
                try:
                    await self.check_all_platforms()
                except Exception as e:
                    logger.error(f"Error during health checks: {e}")
                
                # Wait for next check interval
                await asyncio.sleep(self.check_interval)
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
            self.monitoring_active = False
    
    async def force_check(self, platform_id: str = None) -> Dict[str, HealthCheckResult]:
        """Force immediate health check"""
        if platform_id:
            if platform_id not in self.platforms:
                raise ValueError(f"Platform {platform_id} not found")
            
            platform = self.platforms[platform_id]
            result = await self.check_platform_health(platform)
            return {platform_id: result}
        else:
            return await self.check_all_platforms()
    
    def get_alert_history(self, platform_id: str = None, 
                         severity: MonitorSeverity = None,
                         limit: int = 50) -> List[MonitorAlert]:
        """Get alert history with optional filtering"""
        all_alerts = []
        
        if platform_id:
            platform_ids = [platform_id] if platform_id in self.active_alerts else []
        else:
            platform_ids = list(self.active_alerts.keys())
        
        for pid in platform_ids:
            alerts = self.active_alerts[pid]
            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]
            all_alerts.extend(alerts)
        
        # Sort by timestamp (newest first) and apply limit
        all_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        return all_alerts[:limit]
    
    def clear_alert_history(self, platform_id: str = None):
        """Clear alert history"""
        if platform_id:
            if platform_id in self.active_alerts:
                self.active_alerts[platform_id] = []
                logger.info(f"Cleared alert history for {platform_id}")
        else:
            for pid in self.active_alerts:
                self.active_alerts[pid] = []
            logger.info("Cleared all alert history")


# Default alert handlers
async def log_alert_handler(alert: MonitorAlert):
    """Default alert handler that logs alerts"""
    level = {
        MonitorSeverity.INFO: logging.INFO,
        MonitorSeverity.WARNING: logging.WARNING,
        MonitorSeverity.ERROR: logging.ERROR,
        MonitorSeverity.CRITICAL: logging.CRITICAL
    }.get(alert.severity, logging.INFO)
    
    logger.log(level, f"Platform Alert [{alert.platform_id}]: {alert.message}")


async def webhook_alert_handler(webhook_url: str):
    """Create webhook alert handler"""
    async def handler(alert: MonitorAlert):
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'platform_id': alert.platform_id,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'metadata': alert.metadata
                }
                
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Webhook alert failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Webhook alert error: {e}")
    
    return handler
