"""
🔍 Health Monitoring Service
Comprehensive system health monitoring and alerting service

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import asyncio
import logging
import psutil
import time
import uuid
from enum import Enum
import json

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class HealthMonitoringService:
    """Comprehensive health monitoring service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.health_checks: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.metrics_history: List[Dict[str, Any]] = []
        self.service_registry: Dict[str, Dict[str, Any]] = {}
        self.monitoring_active = True
        
        # Health thresholds
        self.thresholds = {
            "cpu_warning": 70.0,
            "cpu_critical": 90.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "disk_warning": 80.0,
            "disk_critical": 95.0,
            "response_time_warning": 2.0,
            "response_time_critical": 5.0
        }
        
        self.logger.info("✅ HealthMonitoringService initialized")
    
    async def register_service(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Register a service for health monitoring"""
        try:
            service_id = str(uuid.uuid4())
            
            self.service_registry[service_name] = {
                "service_id": service_id,
                "service_name": service_name,
                "endpoint": service_config.get("endpoint", ""),
                "health_check_url": service_config.get("health_check_url", ""),
                "check_interval": service_config.get("check_interval", 60),
                "timeout": service_config.get("timeout", 5),
                "retry_count": service_config.get("retry_count", 3),
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "last_check": None,
                "status": HealthStatus.UNKNOWN.value,
                "metadata": service_config.get("metadata", {})
            }
            
            self.logger.info(f"Registered service: {service_name}")
            return {
                "success": True,
                "service_id": service_id,
                "service_name": service_name,
                "message": "Service registered for health monitoring"
            }
            
        except Exception as e:
            self.logger.error(f"Service registration failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def perform_system_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        try:
            start_time = time.time()
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Process information
            process_count = len(psutil.pids())
            
            # Calculate health status
            health_status = self._calculate_system_health_status({
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk_usage.used / disk_usage.total) * 100
            })
            
            health_check = {
                "check_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "check_duration": round(time.time() - start_time, 3),
                "overall_status": health_status,
                "system_metrics": {
                    "cpu": {
                        "percent": cpu_percent,
                        "count": cpu_count,
                        "frequency_mhz": cpu_freq.current if cpu_freq else None,
                        "status": self._get_cpu_status(cpu_percent)
                    },
                    "memory": {
                        "total_gb": round(memory.total / (1024**3), 2),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "used_percent": memory.percent,
                        "status": self._get_memory_status(memory.percent)
                    },
                    "swap": {
                        "total_gb": round(swap.total / (1024**3), 2),
                        "used_percent": swap.percent
                    },
                    "disk": {
                        "total_gb": round(disk_usage.total / (1024**3), 2),
                        "free_gb": round(disk_usage.free / (1024**3), 2),
                        "used_percent": round((disk_usage.used / disk_usage.total) * 100, 1),
                        "status": self._get_disk_status((disk_usage.used / disk_usage.total) * 100)
                    },
                    "network": {
                        "bytes_sent": network_io.bytes_sent,
                        "bytes_recv": network_io.bytes_recv,
                        "packets_sent": network_io.packets_sent,
                        "packets_recv": network_io.packets_recv
                    },
                    "processes": {
                        "total_count": process_count
                    }
                }
            }
            
            # Store health check result
            self.health_checks[health_check["check_id"]] = health_check
            
            # Add to metrics history
            self.metrics_history.append({
                "timestamp": health_check["timestamp"],
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk_usage.used / disk_usage.total) * 100,
                "process_count": process_count
            })
            
            # Keep only last 1000 metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            # Generate alerts if needed
            await self._check_for_alerts(health_check["system_metrics"])
            
            return health_check
            
        except Exception as e:
            self.logger.error(f"System health check failed: {str(e)}")
            return {
                "check_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "overall_status": HealthStatus.UNKNOWN.value,
                "error": str(e)
            }
    
    def _calculate_system_health_status(self, metrics: Dict[str, float]) -> str:
        """Calculate overall system health status"""
        cpu_percent = metrics["cpu_percent"]
        memory_percent = metrics["memory_percent"]
        disk_percent = metrics["disk_percent"]
        
        # Check critical thresholds
        if (cpu_percent >= self.thresholds["cpu_critical"] or
            memory_percent >= self.thresholds["memory_critical"] or
            disk_percent >= self.thresholds["disk_critical"]):
            return HealthStatus.CRITICAL.value
        
        # Check warning thresholds
        if (cpu_percent >= self.thresholds["cpu_warning"] or
            memory_percent >= self.thresholds["memory_warning"] or
            disk_percent >= self.thresholds["disk_warning"]):
            return HealthStatus.WARNING.value
        
        return HealthStatus.HEALTHY.value
    
    def _get_cpu_status(self, cpu_percent: float) -> str:
        """Get CPU health status"""
        if cpu_percent >= self.thresholds["cpu_critical"]:
            return HealthStatus.CRITICAL.value
        elif cpu_percent >= self.thresholds["cpu_warning"]:
            return HealthStatus.WARNING.value
        return HealthStatus.HEALTHY.value
    
    def _get_memory_status(self, memory_percent: float) -> str:
        """Get memory health status"""
        if memory_percent >= self.thresholds["memory_critical"]:
            return HealthStatus.CRITICAL.value
        elif memory_percent >= self.thresholds["memory_warning"]:
            return HealthStatus.WARNING.value
        return HealthStatus.HEALTHY.value
    
    def _get_disk_status(self, disk_percent: float) -> str:
        """Get disk health status"""
        if disk_percent >= self.thresholds["disk_critical"]:
            return HealthStatus.CRITICAL.value
        elif disk_percent >= self.thresholds["disk_warning"]:
            return HealthStatus.WARNING.value
        return HealthStatus.HEALTHY.value
    
    async def _check_for_alerts(self, system_metrics: Dict[str, Any]):
        """Check system metrics and generate alerts if needed"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # CPU alerts
            cpu_percent = system_metrics["cpu"]["percent"]
            if cpu_percent >= self.thresholds["cpu_critical"]:
                await self._create_alert(
                    "High CPU Usage Critical",
                    f"CPU usage is critically high: {cpu_percent}%",
                    AlertSeverity.CRITICAL,
                    {"metric": "cpu_percent", "value": cpu_percent}
                )
            elif cpu_percent >= self.thresholds["cpu_warning"]:
                await self._create_alert(
                    "High CPU Usage Warning",
                    f"CPU usage is high: {cpu_percent}%",
                    AlertSeverity.WARNING,
                    {"metric": "cpu_percent", "value": cpu_percent}
                )
            
            # Memory alerts
            memory_percent = system_metrics["memory"]["used_percent"]
            if memory_percent >= self.thresholds["memory_critical"]:
                await self._create_alert(
                    "High Memory Usage Critical",
                    f"Memory usage is critically high: {memory_percent}%",
                    AlertSeverity.CRITICAL,
                    {"metric": "memory_percent", "value": memory_percent}
                )
            elif memory_percent >= self.thresholds["memory_warning"]:
                await self._create_alert(
                    "High Memory Usage Warning",
                    f"Memory usage is high: {memory_percent}%",
                    AlertSeverity.WARNING,
                    {"metric": "memory_percent", "value": memory_percent}
                )
            
            # Disk alerts
            disk_percent = system_metrics["disk"]["used_percent"]
            if disk_percent >= self.thresholds["disk_critical"]:
                await self._create_alert(
                    "Low Disk Space Critical",
                    f"Disk usage is critically high: {disk_percent}%",
                    AlertSeverity.CRITICAL,
                    {"metric": "disk_percent", "value": disk_percent}
                )
            elif disk_percent >= self.thresholds["disk_warning"]:
                await self._create_alert(
                    "Low Disk Space Warning",
                    f"Disk usage is high: {disk_percent}%",
                    AlertSeverity.WARNING,
                    {"metric": "disk_percent", "value": disk_percent}
                )
            
        except Exception as e:
            self.logger.error(f"Alert checking failed: {str(e)}")
    
    async def _create_alert(self, title: str, message: str, severity: AlertSeverity, metadata: Dict[str, Any] = None):
        """Create and store an alert"""
        try:
            alert = {
                "alert_id": str(uuid.uuid4()),
                "title": title,
                "message": message,
                "severity": severity.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "resolved": False,
                "metadata": metadata or {}
            }
            
            self.alerts.append(alert)
            
            # Keep only last 1000 alerts
            if len(self.alerts) > 1000:
                self.alerts = self.alerts[-1000:]
            
            self.logger.warning(f"Alert created: {title} - {message}")
            
        except Exception as e:
            self.logger.error(f"Alert creation failed: {str(e)}")
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific registered service"""
        try:
            if service_name not in self.service_registry:
                return {
                    "success": False,
                    "error": "Service not registered",
                    "service_name": service_name
                }
            
            service = self.service_registry[service_name]
            start_time = time.time()
            
            # Simulate service health check (replace with actual HTTP call in production)
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Simulate service response (90% success rate)
            import random
            is_healthy = random.random() > 0.1
            
            response_time = time.time() - start_time
            
            # Determine status
            if is_healthy:
                if response_time < self.thresholds["response_time_warning"]:
                    status = HealthStatus.HEALTHY.value
                elif response_time < self.thresholds["response_time_critical"]:
                    status = HealthStatus.WARNING.value
                else:
                    status = HealthStatus.CRITICAL.value
            else:
                status = HealthStatus.CRITICAL.value
            
            # Update service status
            service["last_check"] = datetime.now(timezone.utc).isoformat()
            service["status"] = status
            
            health_result = {
                "service_name": service_name,
                "status": status,
                "response_time": round(response_time, 3),
                "is_healthy": is_healthy,
                "last_check": service["last_check"],
                "endpoint": service["endpoint"]
            }
            
            # Generate alert if service is unhealthy
            if status == HealthStatus.CRITICAL.value:
                await self._create_alert(
                    f"Service Health Critical: {service_name}",
                    f"Service {service_name} is unhealthy",
                    AlertSeverity.CRITICAL,
                    {"service_name": service_name, "response_time": response_time}
                )
            
            return health_result
            
        except Exception as e:
            self.logger.error(f"Service health check failed for {service_name}: {str(e)}")
            return {
                "service_name": service_name,
                "status": HealthStatus.UNKNOWN.value,
                "error": str(e)
            }
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        try:
            # Perform system health check
            system_health = await self.perform_system_health_check()
            
            # Check all registered services
            service_health_results = {}
            for service_name in self.service_registry.keys():
                service_health = await self.check_service_health(service_name)
                service_health_results[service_name] = service_health
            
            # Count alert severities
            alert_counts = {
                "info": 0,
                "warning": 0,
                "critical": 0,
                "emergency": 0
            }
            
            for alert in self.alerts:
                if not alert["resolved"]:
                    severity = alert["severity"]
                    if severity in alert_counts:
                        alert_counts[severity] += 1
            
            # Calculate overall health
            overall_status = system_health["overall_status"]
            
            # Check if any services are critical
            critical_services = [name for name, health in service_health_results.items() 
                               if health["status"] == HealthStatus.CRITICAL.value]
            
            if critical_services or overall_status == HealthStatus.CRITICAL.value:
                overall_status = HealthStatus.CRITICAL.value
            elif overall_status == HealthStatus.WARNING.value:
                overall_status = HealthStatus.WARNING.value
            
            return {
                "overall_status": overall_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_health": system_health,
                "service_health": service_health_results,
                "alerts": {
                    "total_active": sum(alert_counts.values()),
                    "by_severity": alert_counts
                },
                "summary": {
                    "total_services": len(self.service_registry),
                    "healthy_services": sum(1 for h in service_health_results.values() 
                                          if h["status"] == HealthStatus.HEALTHY.value),
                    "critical_services": len(critical_services),
                    "total_checks_performed": len(self.health_checks)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Health summary generation failed: {str(e)}")
            return {
                "overall_status": HealthStatus.UNKNOWN.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
    
    async def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """Mark an alert as resolved"""
        try:
            for alert in self.alerts:
                if alert["alert_id"] == alert_id:
                    alert["resolved"] = True
                    alert["resolved_at"] = datetime.now(timezone.utc).isoformat()
                    
                    return {
                        "success": True,
                        "alert_id": alert_id,
                        "message": "Alert resolved"
                    }
            
            return {
                "success": False,
                "error": "Alert not found",
                "alert_id": alert_id
            }
            
        except Exception as e:
            self.logger.error(f"Alert resolution failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_metrics_history(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics history for specified period"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            filtered_metrics = [
                metric for metric in self.metrics_history
                if datetime.fromisoformat(metric["timestamp"]) >= cutoff_time
            ]
            
            if not filtered_metrics:
                return {
                    "period_hours": hours,
                    "data_points": 0,
                    "metrics": []
                }
            
            # Calculate averages
            avg_cpu = sum(m["cpu_percent"] for m in filtered_metrics) / len(filtered_metrics)
            avg_memory = sum(m["memory_percent"] for m in filtered_metrics) / len(filtered_metrics)
            avg_disk = sum(m["disk_percent"] for m in filtered_metrics) / len(filtered_metrics)
            
            return {
                "period_hours": hours,
                "data_points": len(filtered_metrics),
                "averages": {
                    "cpu_percent": round(avg_cpu, 1),
                    "memory_percent": round(avg_memory, 1),
                    "disk_percent": round(avg_disk, 1)
                },
                "metrics": filtered_metrics[-100:]  # Return last 100 data points
            }
            
        except Exception as e:
            self.logger.error(f"Metrics history retrieval failed: {str(e)}")
            return {"error": str(e), "period_hours": hours}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "HealthMonitoringService",
            "status": "healthy",
            "monitoring_active": self.monitoring_active,
            "registered_services": len(self.service_registry),
            "total_health_checks": len(self.health_checks),
            "active_alerts": len([a for a in self.alerts if not a["resolved"]]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


__all__ = ['HealthMonitoringService', 'HealthStatus', 'AlertSeverity']