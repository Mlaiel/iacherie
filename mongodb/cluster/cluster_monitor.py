"""MongoDB Cluster Monitor
======================

Real-time cluster health monitoring and alerting system for MongoDB
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from . import ClusterState, ClusterStatus, ClusterNode

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """Cluster alert information."""
    alert_id: str
    severity: AlertSeverity
    message: str
    node_id: Optional[str]
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False

class ClusterMonitor:
    """Enterprise-grade MongoDB cluster monitoring system."""
    
    def __init__(self, connection_string -> None: str, replica_set_name -> None: str) -> None:
        """Initialize cluster monitor."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for cluster monitoring")
            
        self.connection_string = connection_string
        self.replica_set_name = replica_set_name
        self.client = None
        self.monitoring_active = False
        self.alert_handlers: List[Callable] = []
        self.active_alerts: List[Alert] = []
        
        # Monitoring configuration
        self.check_interval = 30  # seconds
        self.health_thresholds = {
            "max_replication_lag_ms": 5000,
            "min_oplog_hours": 24,
            "max_connections_percent": 80,
            "max_cpu_percent": 80,
            "max_memory_percent": 80,
            "min_disk_space_percent": 20
        }
        
        # Metrics storage
        self.metrics_history = []
        self.max_history_size = 1000
    
    async def start_monitoring(self) -> None:
        """Start continuous cluster monitoring."""
        self.monitoring_active = True
        logger.info("Starting cluster monitoring")
        
        while self.monitoring_active:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self) -> None:
        """Stop cluster monitoring."""
        self.monitoring_active = False
        logger.info("Stopped cluster monitoring")
    
    def add_alert_handler(self, handler -> None: Callable[[Alert], None]) -> None:
        """Add alert handler function."""
        self.alert_handlers.append(handler)
    
    async def _perform_health_checks(self) -> None:
        """Perform comprehensive cluster health checks."""
        try:
            if not self.client:
                self.client = MongoClient(self.connection_string)
            
            # Get cluster status
            status = self.client.admin.command("replSetGetStatus")
            cluster_status = self._parse_cluster_status(status)
            
            # Store metrics
            self._store_metrics(cluster_status)
            
            # Check for issues
            await self._check_replication_lag(status)
            await self._check_oplog_size()
            await self._check_node_health(status)
            await self._check_connections()
            await self._check_disk_space()
            
            # Update cluster state
            self._update_cluster_state(cluster_status)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            await self._create_alert(
                AlertSeverity.ERROR,
                f"Health check failed: {e}",
                None
            )
    
    async def _check_replication_lag(self, status -> None: Dict[str, Any]) -> None:
        """Check replication lag across the cluster."""
        max_lag = self._calculate_max_lag(status)
        
        if max_lag > self.health_thresholds["max_replication_lag_ms"]:
            await self._create_alert(
                AlertSeverity.WARNING if max_lag < 10000 else AlertSeverity.ERROR,
                f"High replication lag detected: {max_lag}ms",
                None
            )
    
    async def _check_oplog_size(self) -> None:
        """Check oplog size and retention."""
        try:
            oplog_stats = self.client.local.oplog.rs.stats()
            
            # Calculate oplog window in hours
            first_entry = self.client.local.oplog.rs.find().sort("ts", 1).limit(1).next()
            last_entry = self.client.local.oplog.rs.find().sort("ts", -1).limit(1).next()
            
            time_diff = last_entry["ts"].time - first_entry["ts"].time
            oplog_hours = time_diff / 3600
            
            if oplog_hours < self.health_thresholds["min_oplog_hours"]:
                await self._create_alert(
                    AlertSeverity.WARNING,
                    f"Oplog window too small: {oplog_hours:.1f} hours",
                    None
                )
                
        except Exception as e:
            logger.debug(f"Could not check oplog size: {e}")
    
    async def _check_node_health(self, status -> None: Dict[str, Any]) -> None:
        """Check health of individual nodes."""
        for member in status.get("members", []):
            node_name = member.get("name")
            
            # Check if node is healthy
            if member.get("health", 0) != 1:
                await self._create_alert(
                    AlertSeverity.ERROR,
                    f"Node unhealthy: {node_name}",
                    node_name
                )
            
            # Check node state
            state = member.get("stateStr")
            if state in ["DOWN", "UNKNOWN", "REMOVED"]:
                await self._create_alert(
                    AlertSeverity.CRITICAL,
                    f"Node in critical state: {node_name} ({state})",
                    node_name
                )
    
    async def _check_connections(self) -> None:
        """Check connection usage."""
        try:
            server_status = self.client.admin.command("serverStatus")
            connections = server_status.get("connections", {})
            
            current = connections.get("current", 0)
            available = connections.get("available", 0)
            total = current + available
            
            if total > 0:
                usage_percent = (current / total) * 100
                
                if usage_percent > self.health_thresholds["max_connections_percent"]:
                    await self._create_alert(
                        AlertSeverity.WARNING,
                        f"High connection usage: {usage_percent:.1f}%",
                        None
                    )
                    
        except Exception as e:
            logger.debug(f"Could not check connections: {e}")
    
    async def _check_disk_space(self) -> None:
        """Check disk space usage."""
        try:
            # This would typically require additional system monitoring
            # For now, we'll use database stats as a proxy
            db_stats = self.client.admin.command("dbStats")
            
            # Simplified disk space check
            # In production, you'd integrate with system monitoring tools
            
        except Exception as e:
            logger.debug(f"Could not check disk space: {e}")
    
    async def _create_alert(self, severity -> None: AlertSeverity, message -> None: str, node_id -> None: Optional[str]) -> None:
        """Create and process a new alert."""
        alert = Alert(
            alert_id=f"alert_{int(datetime.now().timestamp())}",
            severity=severity,
            message=message,
            node_id=node_id,
            timestamp=datetime.now()
        )
        
        # Check if similar alert already exists
        if not self._is_duplicate_alert(alert):
            self.active_alerts.append(alert)
            
            # Notify alert handlers
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler failed: {e}")
            
            logger.warning(f"Alert created: [{severity.value.upper()}] {message}")
    
    def _is_duplicate_alert(self, new_alert: Alert) -> bool:
        """Check if a similar alert already exists."""
        for alert in self.active_alerts:
            if (not alert.resolved and 
                alert.message == new_alert.message and 
                alert.node_id == new_alert.node_id):
                return True
        return False
    
    def _parse_cluster_status(self, status: Dict[str, Any]) -> ClusterStatus:
        """Parse cluster status from replica set status."""
        # Find primary node
        primary_node = None
        healthy_nodes = 0
        total_nodes = len(status.get("members", []))
        
        for member in status.get("members", []):
            if member.get("stateStr") == "PRIMARY":
                primary_node = member.get("name")
            if member.get("health", 0) == 1:
                healthy_nodes += 1
        
        # Determine cluster state
        if healthy_nodes == total_nodes:
            cluster_state = ClusterState.HEALTHY
        elif healthy_nodes >= (total_nodes // 2) + 1:
            cluster_state = ClusterState.DEGRADED
        else:
            cluster_state = ClusterState.CRITICAL
        
        return ClusterStatus(
            cluster_id=status.get("set", "unknown"),
            state=cluster_state,
            primary_node=primary_node,
            total_nodes=total_nodes,
            healthy_nodes=healthy_nodes,
            last_election=status.get("electionDate"),
            oplog_size_mb=0,  # Would be filled by separate query
            replication_lag_ms=self._calculate_max_lag(status),
            write_concern_timeout=10000
        )
    
    def _calculate_max_lag(self, status: Dict[str, Any]) -> int:
        """Calculate maximum replication lag."""
        primary_optime = None
        max_lag = 0
        
        # Find primary optime
        for member in status.get("members", []):
            if member.get("stateStr") == "PRIMARY":
                primary_optime = member.get("optimeDate")
                break
        
        if not primary_optime:
            return 0
        
        # Calculate lag for each secondary
        for member in status.get("members", []):
            if member.get("stateStr") == "SECONDARY":
                member_optime = member.get("optimeDate")
                if member_optime:
                    lag_ms = int((primary_optime - member_optime).total_seconds() * 1000)
                    max_lag = max(max_lag, lag_ms)
        
        return max_lag
    
    def _store_metrics(self, cluster_status -> None: ClusterStatus) -> None:
        """Store cluster metrics for historical analysis."""
        metrics = {
            "timestamp": datetime.now(),
            "cluster_state": cluster_status.state.value,
            "healthy_nodes": cluster_status.healthy_nodes,
            "total_nodes": cluster_status.total_nodes,
            "replication_lag_ms": cluster_status.replication_lag_ms,
            "primary_node": cluster_status.primary_node
        }
        
        self.metrics_history.append(metrics)
        
        # Trim history if too large
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def _update_cluster_state(self, cluster_status -> None: ClusterStatus) -> None:
        """Update overall cluster state based on current status."""
        if cluster_status.state == ClusterState.CRITICAL:
            logger.critical(f"Cluster in CRITICAL state: {cluster_status.cluster_id}")
        elif cluster_status.state == ClusterState.DEGRADED:
            logger.warning(f"Cluster in DEGRADED state: {cluster_status.cluster_id}")
    
    def get_current_status(self) -> Optional[ClusterStatus]:
        """Get current cluster status."""
        try:
            if not self.client:
                self.client = MongoClient(self.connection_string)
            
            status = self.client.admin.command("replSetGetStatus")
            return self._parse_cluster_status(status)
            
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            return None
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity."""
        alerts = [alert for alert in self.active_alerts if not alert.resolved]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metrics for metrics in self.metrics_history
            if metrics["timestamp"] > cutoff_time
        ]
    
    def get_cluster_summary(self) -> Dict[str, Any]:
        """Get comprehensive cluster summary."""
        current_status = self.get_current_status()
        active_alerts = self.get_active_alerts()
        
        alert_counts = {}
        for severity in AlertSeverity:
            alert_counts[severity.value] = len([
                a for a in active_alerts if a.severity == severity
            ])
        
        return {
            "cluster_status": asdict(current_status) if current_status else None,
            "active_alerts": len(active_alerts),
            "alert_counts": alert_counts,
            "monitoring_active": self.monitoring_active,
            "last_check": datetime.now(),
            "metrics_history_count": len(self.metrics_history)
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in the specified format."""
        data = {
            "cluster_summary": self.get_cluster_summary(),
            "active_alerts": [asdict(alert) for alert in self.get_active_alerts()],
            "metrics_history": self.metrics_history[-100:]  # Last 100 entries
        }
        
        if format.lower() == "json":
            return json.dumps(data, default=str, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def close(self) -> None:
        """Close monitoring connections."""
        self.stop_monitoring()
        if self.client:
            self.client.close()

# Export the main class
__all__ = ['ClusterMonitor', 'Alert', 'AlertSeverity']