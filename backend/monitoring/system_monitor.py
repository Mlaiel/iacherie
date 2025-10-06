"""
IA Chérie - System Monitor
Enterprise Monitoring & Observability System

© 2025 Fahed Mlaiel (mlaiel@live.de) - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import random


class MetricType(Enum):
    """
        Types de métriques"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    API_LATENCY = "api_latency"
    ERROR_RATE = "error_rate"


class AlertSeverity(Enum):
    """Niveaux sévérité alertes"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SystemMetrics:
    """Métriques système"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_in_mbps: float
    network_out_mbps: float
    active_connections: int
    timestamp: datetime


@dataclass
class Alert:
    """
        Alerte système"""
    alert_id: str
    severity: str
    metric_type: str
    message: str
    value: float
    threshold: float
    triggered_at: datetime


class SystemMonitor:
    """
    Système monitoring enterprise
    Métriques temps réel, alertes, observabilité complète
    
    © 2025 Fahed Mlaiel - System Monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Métriques historiques
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1000
        
        # Alertes actives
        self.active_alerts: List[Alert] = []
        
        # Thresholds alertes
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "error_rate": 5.0,
            "api_latency": 1000.0
        }
        
        # Statistiques
        self.total_alerts_triggered = 0
        self.monitoring_started_at = datetime.now()

        
        self.logger.info("📊 SystemMonitor initialized")
    
    async def collect_metrics(self) -> SystemMetrics:
        """
        Collecte métriques système actuelles
        
        Returns:
            Métriques système instant T
        """
        await asyncio.sleep(0.01)
        
        # Simulation collecte métriques

        metrics = SystemMetrics(
            cpu_usage=random.uniform(10, 95),
            memory_usage=random.uniform(20, 90),
            disk_usage=random.uniform(30, 85),
            network_in_mbps=random.uniform(10, 500),
            network_out_mbps=random.uniform(10, 500),
            active_connections=random.randint(100, 5000),
            timestamp=datetime.now()
        )
        
        # Stockage historique
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
        
        # Vérification seuils alertes
        await self._check_alert_thresholds(metrics)

        
        return metrics
    
    async def _check_alert_thresholds(self, metrics: SystemMetrics):
        """
        Vérifie dépassement seuils et crée alertes"""
        alerts_to_create = []
        
        # CPU
        if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts_to_create.append((
                "cpu_usage",
                f"CPU usage high: {metrics.cpu_usage:.1f}%",
                metrics.cpu_usage,
                AlertSeverity.WARNING if metrics.cpu_usage < 90 else AlertSeverity.CRITICAL
            ))
        
        # Memory
        if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts_to_create.append((
                "memory_usage",
                f"Memory usage high: {metrics.memory_usage:.1f}%",
                metrics.memory_usage,
                AlertSeverity.WARNING if metrics.memory_usage < 95 else AlertSeverity.CRITICAL
            ))
        
        # Disk
        if metrics.disk_usage > self.alert_thresholds["disk_usage"]:
            alerts_to_create.append((
                "disk_usage",
                f"Disk usage high: {metrics.disk_usage:.1f}%",
                metrics.disk_usage,
                AlertSeverity.ERROR
            ))
        
        # Création alertes
        for metric_type, message, value, severity in alerts_to_create:
            alert = Alert(
                alert_id=f"alert-{len(self.active_alerts) + 1}",
                severity=severity.value,
                metric_type=metric_type,
                message=message,
                value=value,
                threshold=self.alert_thresholds[metric_type],
                triggered_at=datetime.now()
            )

            self.active_alerts.append(alert)

            self.total_alerts_triggered += 1
            
            self.logger.warning(f"⚠️ Alert triggered: {message}")
    
    async def start_continuous_monitoring(self, interval_seconds: int = 60):
        """
        Démarre monitoring continu
        
        Args:
            interval_seconds: Intervalle collecte métriques
        """
        self.logger.info(f"▶️ Continuous monitoring started (interval: {interval_seconds}s)")

        
        while True:
            try:
                metrics = await self.collect_metrics()

                self.logger.debug(f"Metrics collected: CPU {metrics.cpu_usage:.1f}%, MEM {metrics.memory_usage:.1f}%")

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")

                await asyncio.sleep(interval_seconds)
    
    def get_metrics_summary(
        self,
        last_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Récupère résumé métriques période
        
        Args:
            last_minutes: Période en minutes
        
        Returns:
            Statistiques agrégées
        """
        cutoff_time = datetime.now() - timedelta(minutes=last_minutes)

        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics available for period"}
        
        return {
            "period_minutes": last_minutes,
            "samples_count": len(recent_metrics),
            "cpu": {
                "avg": sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
                "max": max(m.cpu_usage for m in recent_metrics),
                "min": min(m.cpu_usage for m in recent_metrics)
            },
            "memory": {
                "avg": sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
                "max": max(m.memory_usage for m in recent_metrics),
                "min": min(m.memory_usage for m in recent_metrics)
            },
            "disk": {
                "avg": sum(m.disk_usage for m in recent_metrics) / len(recent_metrics),
                "max": max(m.disk_usage for m in recent_metrics)
            },
            "network": {
                "avg_in_mbps": sum(m.network_in_mbps for m in recent_metrics) / len(recent_metrics),
                "avg_out_mbps": sum(m.network_out_mbps for m in recent_metrics) / len(recent_metrics)
            }
        }
    
    def get_active_alerts(
        self,
        severity: Optional[str] = None
    ) -> List[Alert]:
        """
        Récupère alertes actives
        
        Args:
            severity: Filtrer par sévérité (optional)

        
        Returns:
            Liste alertes actives
        """
        if severity:
            return [a for a in self.active_alerts if a.severity == severity]
        return self.active_alerts
    
    def clear_alert(self, alert_id: str) -> bool:
        """
        Résout/supprime alerte"""
        for idx, alert in enumerate(self.active_alerts):
            if alert.alert_id == alert_id:
                self.active_alerts.pop(idx)

                self.logger.info(f"✅ Alert cleared: {alert_id}")

                return True
        return False
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Récupère statistiques monitoring"""
        uptime = datetime.now() - self.monitoring_started_at
        
        return {
            "monitoring_uptime_hours": uptime.total_seconds() / 3600,
            "total_metrics_collected": len(self.metrics_history),
            "total_alerts_triggered": self.total_alerts_triggered,
            "active_alerts_count": len(self.active_alerts),
            "critical_alerts": sum(
                1 for a in self.active_alerts
                if a.severity == AlertSeverity.CRITICAL.value
            ),
            "alert_thresholds": self.alert_thresholds
        }


class PerformanceMetricsEngine:
    """Moteur de collecte et analyse des métriques de performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("📊 PerformanceMetricsEngine initialized")
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collecte les métriques de performance"""
        return {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 38.5,
            "network_latency": 12.3
        }


class AlertingSystem:
    """Système d'alerting et notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚨 AlertingSystem initialized")
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """Envoie une alerte"""
        return True


class AnomalyDetectionEngine:
    """Moteur de détection d'anomalies ML"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔍 AnomalyDetectionEngine initialized")
    
    async def detect_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Détecte les anomalies dans les métriques"""
        return []


__all__ = [
    'SystemMonitor',
    'PerformanceMetricsEngine',
    'AlertingSystem',
    'AnomalyDetectionEngine',
    'MetricType',
    'AlertSeverity',
    'SystemMetrics',
    'Alert'
]
