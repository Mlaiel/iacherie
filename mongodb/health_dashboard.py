"""MongoDB Health Dashboard Module
===============================

Comprehensive real-time health monitoring and analytics dashboard for MongoDB.
Provides advanced monitoring, alerting, and performance visualization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

TEAM SPECIALTIES:
- Lead AI Engineer: Fahed Mlaiel (mlaiel@live.de)
- Database Performance Expert: Fahed Mlaiel (mlaiel@live.de)
- Monitoring & Observability Specialist: Fahed Mlaiel (mlaiel@live.de)
- DevOps & Infrastructure Expert: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class HealthMetrics:
    """Health metrics data structure."""
    timestamp: datetime
    status: str  # healthy, warning, critical
    response_time_ms: float
    connections_active: int
    connections_available: int
    memory_usage_mb: float
    disk_usage_gb: float
    operations_per_second: float
    query_performance_score: float
    errors_count: int
    warnings_count: int

@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    metric: str
    operator: str  # gt, lt, eq, ne
    threshold: float
    severity: str  # info, warning, critical
    enabled: bool = True

class MongoDBHealthDashboard:
    """Advanced MongoDB health monitoring dashboard."""
    
    def __init__(self, database, collection_name -> None: str = "health_metrics") -> None:
        """Initialize health dashboard.
        
        Args:
            database: MongoDB database instance
            collection_name: Collection for storing health metrics
        """
        self.database = database
        self.collection_name = collection_name
        self.collection = database[collection_name]
        self.alert_rules = []
        self.active_alerts = []
        self.metrics_history = []
        self.monitoring_active = False
        
        # Default alert rules
        self._setup_default_alerts()
    
    def _setup_default_alerts(self) -> None:
        """Setup default monitoring alert rules."""
        default_rules = [
            AlertRule("High Response Time", "response_time_ms", "gt", 1000.0, "warning"),
            AlertRule("Critical Response Time", "response_time_ms", "gt", 5000.0, "critical"),
            AlertRule("Low Available Connections", "connections_available", "lt", 10, "warning"),
            AlertRule("Critical Available Connections", "connections_available", "lt", 5, "critical"),
            AlertRule("High Memory Usage", "memory_usage_mb", "gt", 2048.0, "warning"),
            AlertRule("Critical Memory Usage", "memory_usage_mb", "gt", 4096.0, "critical"),
            AlertRule("Low Query Performance", "query_performance_score", "lt", 0.5, "warning"),
            AlertRule("Critical Query Performance", "query_performance_score", "lt", 0.3, "critical"),
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)
    
    def add_alert_rule(self, rule -> None: AlertRule) -> None:
        """Add a new alert rule."""
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_name -> None: str) -> None:
        """Remove an alert rule by name."""
        self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]
        logger.info(f"Removed alert rule: {rule_name}")
    
    async def collect_metrics(self) -> HealthMetrics:
        """Collect current health metrics."""
        try:
            start_time = time.time()
            
            # Basic database ping
            ping_result = await self.database.command("ping")
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Server status
            server_status = await self.database.command("serverStatus")
            
            # Connection information
            connections = server_status.get("connections", {})
            active_connections = connections.get("current", 0)
            available_connections = connections.get("available", 0)
            
            # Memory information
            mem = server_status.get("mem", {})
            memory_usage = mem.get("resident", 0)  # Resident memory in MB
            
            # Operations counters
            opcounters = server_status.get("opcounters", {})
            operations = sum([
                opcounters.get("insert", 0),
                opcounters.get("query", 0),
                opcounters.get("update", 0),
                opcounters.get("delete", 0)
            ])
            
            # Calculate ops/second (simplified)
            ops_per_second = operations / server_status.get("uptime", 1)
            
            # System metrics if available
            disk_usage = 0.0
            if PSUTIL_AVAILABLE:
                try:
                    disk_usage = psutil.disk_usage('/').used / (1024**3)  # GB
                except:
                    pass
            
            # Query performance score (simplified heuristic)
            avg_response_time = response_time
            performance_score = max(0.0, min(1.0, (2000 - avg_response_time) / 2000))
            
            # Status determination
            status = "healthy"
            if response_time > 5000 or available_connections < 5 or performance_score < 0.3:
                status = "critical"
            elif response_time > 1000 or available_connections < 10 or performance_score < 0.5:
                status = "warning"
            
            metrics = HealthMetrics(
                timestamp=datetime.now(timezone.utc),
                status=status,
                response_time_ms=response_time,
                connections_active=active_connections,
                connections_available=available_connections,
                memory_usage_mb=memory_usage,
                disk_usage_gb=disk_usage,
                operations_per_second=ops_per_second,
                query_performance_score=performance_score,
                errors_count=0,  # Would need error tracking system
                warnings_count=0  # Would need warning tracking system
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect health metrics: {e}")
            return HealthMetrics(
                timestamp=datetime.now(timezone.utc),
                status="critical",
                response_time_ms=9999.0,
                connections_active=0,
                connections_available=0,
                memory_usage_mb=0.0,
                disk_usage_gb=0.0,
                operations_per_second=0.0,
                query_performance_score=0.0,
                errors_count=1,
                warnings_count=0
            )
    
    async def store_metrics(self, metrics -> None: HealthMetrics) -> None:
        """Store metrics in MongoDB for historical analysis."""
        try:
            doc = asdict(metrics)
            await self.collection.insert_one(doc)
            
            # Keep only last 7 days of metrics
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
            await self.collection.delete_many({"timestamp": {"$lt": cutoff_date}})
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    def check_alerts(self, metrics: HealthMetrics) -> List[Dict[str, Any]]:
        """Check alert rules against current metrics."""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            try:
                metric_value = getattr(metrics, rule.metric)
                triggered = False
                
                if rule.operator == "gt" and metric_value > rule.threshold:
                    triggered = True
                elif rule.operator == "lt" and metric_value < rule.threshold:
                    triggered = True
                elif rule.operator == "eq" and metric_value == rule.threshold:
                    triggered = True
                elif rule.operator == "ne" and metric_value != rule.threshold:
                    triggered = True
                
                if triggered:
                    alert = {
                        "rule_name": rule.name,
                        "metric": rule.metric,
                        "current_value": metric_value,
                        "threshold": rule.threshold,
                        "severity": rule.severity,
                        "timestamp": metrics.timestamp,
                        "message": f"{rule.name}: {rule.metric} is {metric_value} (threshold: {rule.threshold})"
                    }
                    triggered_alerts.append(alert)
                    
            except AttributeError:
                logger.warning(f"Invalid metric in alert rule: {rule.metric}")
        
        return triggered_alerts
    
    async def get_historical_metrics(self, 
                                   hours: int = 24,
                                   limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical metrics for dashboard visualization."""
        try:
            start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            cursor = self.collection.find(
                {"timestamp": {"$gte": start_time}}
            ).sort("timestamp", -1).limit(limit)
            
            metrics = []
            async for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                doc["_id"] = str(doc["_id"])
                metrics.append(doc)
            
            return list(reversed(metrics))  # Chronological order
            
        except Exception as e:
            logger.error(f"Failed to get historical metrics: {e}")
            return []
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        try:
            # Current metrics
            current_metrics = await self.collect_metrics()
            
            # Check alerts
            alerts = self.check_alerts(current_metrics)
            
            # Historical data
            historical = await self.get_historical_metrics(hours=24, limit=288)  # 5-minute intervals for 24h
            
            # Summary statistics
            stats = await self._calculate_summary_stats()
            
            dashboard_data = {
                "current_metrics": asdict(current_metrics),
                "active_alerts": alerts,
                "historical_metrics": historical,
                "summary_statistics": stats,
                "alert_rules": [asdict(rule) for rule in self.alert_rules],
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "monitoring_status": "active" if self.monitoring_active else "inactive"
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {
                "error": str(e),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
    
    async def _calculate_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics from historical data."""
        try:
            # Get last 24 hours of data
            start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_time}}},
                {"$group": {
                    "_id": None,
                    "avg_response_time": {"$avg": "$response_time_ms"},
                    "max_response_time": {"$max": "$response_time_ms"},
                    "min_response_time": {"$min": "$response_time_ms"},
                    "avg_memory_usage": {"$avg": "$memory_usage_mb"},
                    "max_memory_usage": {"$max": "$memory_usage_mb"},
                    "avg_connections": {"$avg": "$connections_active"},
                    "max_connections": {"$max": "$connections_active"},
                    "avg_performance_score": {"$avg": "$query_performance_score"},
                    "min_performance_score": {"$min": "$query_performance_score"},
                    "total_errors": {"$sum": "$errors_count"},
                    "total_warnings": {"$sum": "$warnings_count"},
                    "status_counts": {"$push": "$status"}
                }}
            ]
            
            async for result in self.collection.aggregate(pipeline):
                # Count status occurrences
                status_counts = {}
                for status in result.get("status_counts", []):
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                return {
                    "time_period": "24 hours",
                    "average_response_time_ms": round(result.get("avg_response_time", 0), 2),
                    "max_response_time_ms": round(result.get("max_response_time", 0), 2),
                    "min_response_time_ms": round(result.get("min_response_time", 0), 2),
                    "average_memory_usage_mb": round(result.get("avg_memory_usage", 0), 2),
                    "max_memory_usage_mb": round(result.get("max_memory_usage", 0), 2),
                    "average_connections": round(result.get("avg_connections", 0), 1),
                    "max_connections": result.get("max_connections", 0),
                    "average_performance_score": round(result.get("avg_performance_score", 0), 3),
                    "min_performance_score": round(result.get("min_performance_score", 0), 3),
                    "total_errors": result.get("total_errors", 0),
                    "total_warnings": result.get("total_warnings", 0),
                    "status_distribution": status_counts
                }
            
            # Fallback if no data
            return {
                "time_period": "24 hours",
                "message": "No historical data available"
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate summary stats: {e}")
            return {"error": str(e)}
    
    async def start_monitoring(self, interval_seconds -> None: int = 300) -> None:
        """Start continuous monitoring (every 5 minutes by default)."""
        self.monitoring_active = True
        logger.info(f"Starting health monitoring with {interval_seconds}s interval")
        
        while self.monitoring_active:
            try:
                # Collect and store metrics
                metrics = await self.collect_metrics()
                await self.store_metrics(metrics)
                
                # Check for alerts
                alerts = self.check_alerts(metrics)
                if alerts:
                    for alert in alerts:
                        logger.warning(f"ALERT: {alert['message']}")
                
                # Add to in-memory history (keep last 100)
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > 100:
                    self.metrics_history.pop(0)
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        self.monitoring_active = False
        logger.info("Health monitoring stopped")
    
    async def export_dashboard_json(self, filepath -> None: str) -> None:
        """Export dashboard data to JSON file."""
        try:
            dashboard_data = await self.get_dashboard_data()
            
            with open(filepath, 'w') as f:
                json.dump(dashboard_data, f, indent=2, default=str)
            
            logger.info(f"Dashboard data exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export dashboard data: {e}")

# Export main classes
__all__ = [
    "MongoDBHealthDashboard",
    "HealthMetrics",
    "AlertRule",
    "PSUTIL_AVAILABLE"
]

# Log successful import
logger.info("Successfully loaded mongodb.health_dashboard")