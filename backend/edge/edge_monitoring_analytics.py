"""Edge Monitoring Analytics
============================

Monitoring & Analytics Edge ultra-performant pour surveillance temps réel.
Consolidation de tous les composants monitoring en un système unifié.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
import uuid
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Niveaux d'alerte."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(str, Enum):
    """Types de métriques."""
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    SYSTEM = "system"


@dataclass
class Alert:
    """Alerte système."""
    alert_id: str
    title: str
    level: AlertLevel
    description: str
    timestamp: datetime
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """Métrique système."""
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)


class AlertingSystemIntelligence:
    """Système alertes intelligent."""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules = {}
        self.notification_channels = []
        self.alert_history = deque(maxlen=1000)
    
    async def create_alert(self, title: str, level: AlertLevel, 
                          description: str, metadata: Dict[str, Any] = None) -> str:
        """Crée une alerte."""
        alert_id = str(uuid.uuid4())
        
        alert = Alert(
            alert_id=alert_id,
            title=title,
            level=level,
            description=description,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        logger.info(f"Alert created: {title} ({level.value})")
        
        # Auto-notification for critical alerts
        if level == AlertLevel.CRITICAL:
            await self._send_notification(alert)
        
        return alert_id
    
    async def _send_notification(self, alert: Alert):
        """Envoie une notification."""
        # Simulation d'envoi de notification
        pass
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Résout une alerte."""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            return True
        return False
    
    async def get_active_alerts(self) -> List[Alert]:
        """Récupère les alertes actives."""
        return [alert for alert in self.alerts.values() if not alert.resolved]


class EdgeMetricsOptimization:
    """Optimisation métriques edge."""
    
    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.metric_thresholds = {}
        self.aggregated_metrics = {}
    
    async def record_metric(self, name: str, value: float, 
                          metric_type: MetricType, labels: Dict[str, str] = None) -> str:
        """Enregistre une métrique."""
        metric_id = str(uuid.uuid4())
        
        metric = Metric(
            metric_id=metric_id,
            name=name,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {}
        )
        
        self.metrics[name].append(metric)
        
        # Keep only recent metrics (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.metrics[name] = [
            m for m in self.metrics[name] 
            if m.timestamp > cutoff_time
        ]
        
        return metric_id
    
    async def get_metric_stats(self, metric_name: str, 
                             time_range: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Récupère les statistiques d'une métrique."""
        cutoff_time = datetime.utcnow() - time_range
        recent_metrics = [
            m for m in self.metrics[metric_name]
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics found"}
        
        values = [m.value for m in recent_metrics]
        
        return {
            "metric_name": metric_name,
            "count": len(values),
            "average": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1] if values else 0,
            "time_range": str(time_range)
        }


class PerformanceMonitoringAI:
    """Monitoring performance IA."""
    
    def __init__(self):
        self.performance_data = defaultdict(list)
        self.anomaly_threshold = 2.0  # Standard deviations
        self.baseline_metrics = {}
    
    async def monitor_performance(self, component: str, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Surveille les performances."""
        timestamp = datetime.utcnow()
        
        for metric_name, value in metrics.items():
            self.performance_data[f"{component}.{metric_name}"].append({
                "value": value,
                "timestamp": timestamp
            })
        
        # Détection d'anomalies
        anomalies = await self._detect_anomalies(component, metrics)
        
        return {
            "component": component,
            "timestamp": timestamp.isoformat(),
            "metrics": metrics,
            "anomalies": anomalies,
            "status": "anomalous" if anomalies else "normal"
        }
    
    async def _detect_anomalies(self, component: str, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Détecte les anomalies de performance."""
        anomalies = []
        
        for metric_name, current_value in current_metrics.items():
            key = f"{component}.{metric_name}"
            historical_data = self.performance_data[key]
            
            if len(historical_data) < 10:  # Pas assez de données historiques
                continue
            
            # Calcul de la moyenne et écart-type
            values = [d["value"] for d in historical_data[-50:]]  # 50 derniers points
            mean_value = sum(values) / len(values)
            variance = sum((x - mean_value) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            # Détection d'anomalie
            if abs(current_value - mean_value) > self.anomaly_threshold * std_dev:
                anomalies.append({
                    "metric": metric_name,
                    "current_value": current_value,
                    "expected_range": [mean_value - std_dev, mean_value + std_dev],
                    "severity": "high" if abs(current_value - mean_value) > 3 * std_dev else "medium"
                })
        
        return anomalies


class EdgeMonitoringAnalytics:
    """Monitoring & Analytics Edge ultra-performant."""
    
    def __init__(self):
        self.alerting_system = AlertingSystemIntelligence()
        self.metrics_optimizer = EdgeMetricsOptimization()
        self.performance_monitor = PerformanceMonitoringAI()
        
        self.monitoring_stats = {
            "total_metrics_collected": 0,
            "active_alerts": 0,
            "performance_score": 95.0,
            "uptime": 99.99
        }
    
    # Alerting System Intelligence
    async def create_alert(self, title: str, level: AlertLevel, 
                          description: str, metadata: Dict[str, Any] = None) -> str:
        """Crée une alerte système."""
        alert_id = await self.alerting_system.create_alert(title, level, description, metadata)
        self.monitoring_stats["active_alerts"] = len(await self.alerting_system.get_active_alerts())
        return alert_id
    
    # Edge Metrics Optimization
    async def record_metric(self, name: str, value: float, 
                          metric_type: MetricType, labels: Dict[str, str] = None) -> str:
        """Enregistre une métrique."""
        metric_id = await self.metrics_optimizer.record_metric(name, value, metric_type, labels)
        self.monitoring_stats["total_metrics_collected"] += 1
        return metric_id
    
    # Performance Monitoring AI
    async def monitor_component_performance(self, component: str, 
                                          metrics: Dict[str, float]) -> Dict[str, Any]:
        """Surveille les performances d'un composant."""
        result = await self.performance_monitor.monitor_performance(component, metrics)
        
        # Créer des alertes pour les anomalies critiques
        if result["anomalies"]:
            for anomaly in result["anomalies"]:
                if anomaly["severity"] == "high":
                    await self.create_alert(
                        f"Performance Anomaly: {component}",
                        AlertLevel.WARNING,
                        f"Anomaly detected in {anomaly['metric']}: {anomaly['current_value']}"
                    )
        
        return result
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Récupère le tableau de bord de monitoring."""
        active_alerts = await self.alerting_system.get_active_alerts()
        
        # Métriques système récentes
        system_metrics = {}
        for metric_name in ["cpu_usage", "memory_usage", "network_latency"]:
            stats = await self.metrics_optimizer.get_metric_stats(metric_name)
            if "error" not in stats:
                system_metrics[metric_name] = stats
        
        return {
            "overview": self.monitoring_stats,
            "active_alerts": [{
                "id": alert.alert_id,
                "title": alert.title,
                "level": alert.level.value,
                "timestamp": alert.timestamp.isoformat()
            } for alert in active_alerts],
            "system_metrics": system_metrics,
            "dashboard_updated": datetime.utcnow().isoformat()
        }
    
    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Récupère les analytics de performance."""
        return {
            "monitoring_stats": self.monitoring_stats,
            "alert_summary": {
                "total_alerts": len(self.alerting_system.alert_history),
                "active_alerts": len(await self.alerting_system.get_active_alerts()),
                "resolved_alerts": len([a for a in self.alerting_system.alerts.values() if a.resolved])
            },
            "metrics_summary": {
                "total_metrics": sum(len(metrics) for metrics in self.metrics_optimizer.metrics.values()),
                "metric_types": len(self.metrics_optimizer.metrics)
            }
        }
    
    async def shutdown(self):
        """Arrête le système de monitoring."""
        logger.info("Shutting down EdgeMonitoringAnalytics")


def create_edge_monitoring_analytics() -> EdgeMonitoringAnalytics:
    """Factory function pour créer une instance de monitoring."""
    return EdgeMonitoringAnalytics()


__all__ = [
    "EdgeMonitoringAnalytics",
    "AlertingSystemIntelligence",
    "EdgeMetricsOptimization",
    "PerformanceMonitoringAI",
    "AlertLevel",
    "MetricType",
    "Alert",
    "Metric",
    "create_edge_monitoring_analytics"
]
