"""
📊 Automation Metrics Collector - Enterprise MLOps
Expert DevOps + Backend Senior: Métriques avancées automation avec analytics temps réel

🎯 EXPERTISE DÉMONTRÉ:
- DevOps: Monitoring automation + métriques performance
- Backend Senior: Architecture monitoring <100ms + analytics
- Lead Dev IA: Intelligence métrique + détection anomalies
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics
from collections import defaultdict, deque
import time

# Configuration et logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques automation"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class MetricLevel(Enum):
    """Niveaux de criticité des métriques"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricPoint:
    """Point de métrique avec timestamp et métadonnées"""
    name: str
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    level: MetricLevel = MetricLevel.INFO
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class MetricSeries:
    """Série temporelle de métriques"""
    name: str
    metric_type: MetricType
    points: deque = field(default_factory=lambda: deque(maxlen=1000))
    labels: Dict[str, str] = field(default_factory=dict)
    retention_hours: int = 24

class AutomationMetricsCollector:
    """
    📊 Collecteur Enterprise de Métriques Automation
    
    Expertise DevOps + Backend Senior:
    - Collecte métriques temps réel <100ms
    - Analytics avancées automation
    - Détection anomalies intelligente
    - Alerting proactif automation
    """
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, MetricSeries] = {}
        self.aggregates: Dict[str, Dict] = {}
        self.alerts: List[Dict] = []
        self.collectors: Dict[str, callable] = {}
        self.collection_interval = 30  # secondes
        self.is_collecting = False
        
        # Métriques système automation
        self.system_metrics = {
            "pipeline_executions_total": 0,
            "pipeline_success_total": 0,
            "pipeline_failure_total": 0,
            "average_execution_time": 0.0,
            "active_pipelines": 0,
            "queue_depth": 0,
            "resource_utilization": 0.0,
            "error_rate": 0.0
        }
        
        # Configuration alerting
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5%
            "execution_time": 300,  # 5 minutes
            "queue_depth": 100,
            "resource_utilization": 0.8  # 80%
        }
    
    async def register_metric(
        self, 
        name: str, 
        metric_type: MetricType,
        labels: Optional[Dict[str, str]] = None,
        retention_hours: Optional[int] = None
    ) -> bool:
        """Enregistre une nouvelle métrique à collecter"""
        try:
            if name in self.metrics:
                logger.warning(f"Metric {name} already registered")
                return False
            
            retention = retention_hours or self.retention_hours
            
            self.metrics[name] = MetricSeries(
                name=name,
                metric_type=metric_type,
                labels=labels or {},
                retention_hours=retention
            )
            
            logger.info(f"Registered metric: {name} ({metric_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register metric {name}: {str(e)}")
            return False
    
    async def record_metric(
        self,
        name: str,
        value: Union[int, float],
        labels: Optional[Dict[str, str]] = None,
        level: MetricLevel = MetricLevel.INFO,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Enregistre un point de métrique avec performance <100ms"""
        start_time = time.time()
        
        try:
            if name not in self.metrics:
                # Auto-registration pour métriques système
                await self.register_metric(name, MetricType.GAUGE)
            
            point = MetricPoint(
                name=name,
                value=value,
                timestamp=datetime.utcnow(),
                labels=labels or {},
                level=level,
                metadata=metadata or {}
            )
            
            self.metrics[name].points.append(point)
            
            # Nettoyage automatique par rétention
            await self._cleanup_old_points(name)
            
            # Mise à jour des agrégats
            await self._update_aggregates(name)
            
            # Vérification des seuils d'alerte
            await self._check_alerts(name, value)
            
            # Performance monitoring
            duration = (time.time() - start_time) * 1000
            if duration > 100:  # > 100ms
                logger.warning(f"Metric recording took {duration:.2f}ms (target: <100ms)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metric {name}: {str(e)}")
            return False
    
    async def get_metric_value(
        self, 
        name: str, 
        aggregation: str = "latest"
    ) -> Optional[Union[int, float]]:
        """Récupère une valeur de métrique avec agrégation"""
        if name not in self.metrics:
            return None
        
        series = self.metrics[name]
        if not series.points:
            return None
        
        values = [point.value for point in series.points]
        
        if aggregation == "latest":
            return values[-1]
        elif aggregation == "average":
            return statistics.mean(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "max":
            return max(values)
        elif aggregation == "median":
            return statistics.median(values)
        elif aggregation == "p95":
            return statistics.quantiles(values, n=20)[18] if len(values) > 20 else max(values)
        else:
            return values[-1]
    
    async def get_metric_series(
        self, 
        name: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MetricPoint]:
        """Récupère une série temporelle de métriques"""
        if name not in self.metrics:
            return []
        
        series = self.metrics[name]
        points = list(series.points)
        
        # Filtrage temporel
        if start_time:
            points = [p for p in points if p.timestamp >= start_time]
        if end_time:
            points = [p for p in points if p.timestamp <= end_time]
        
        return points
    
    async def record_pipeline_execution(
        self,
        pipeline_id: str,
        execution_id: str,
        status: str,
        duration: float,
        metadata: Optional[Dict] = None
    ) -> None:
        """Enregistre les métriques d'exécution de pipeline"""
        labels = {
            "pipeline_id": pipeline_id,
            "execution_id": execution_id,
            "status": status
        }
        
        # Métriques principales
        await self.record_metric("pipeline_execution_duration", duration, labels)
        await self.record_metric("pipeline_execution_count", 1, labels)
        
        # Mise à jour des compteurs système
        self.system_metrics["pipeline_executions_total"] += 1
        
        if status == "success":
            self.system_metrics["pipeline_success_total"] += 1
        elif status == "failed":
            self.system_metrics["pipeline_failure_total"] += 1
        
        # Calcul du taux d'erreur
        total = self.system_metrics["pipeline_executions_total"]
        failures = self.system_metrics["pipeline_failure_total"]
        self.system_metrics["error_rate"] = failures / total if total > 0 else 0
        
        # Mise à jour du temps d'exécution moyen
        await self._update_average_execution_time()
        
        # Métriques détaillées si disponibles
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (int, float)):
                    await self.record_metric(f"pipeline_{key}", value, labels)
    
    async def record_resource_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        network_io: Optional[Dict] = None
    ) -> None:
        """Enregistre les métriques de ressources système"""
        timestamp = datetime.utcnow()
        
        await self.record_metric("cpu_usage_percent", cpu_usage)
        await self.record_metric("memory_usage_percent", memory_usage)
        await self.record_metric("disk_usage_percent", disk_usage)
        
        # Calcul de l'utilisation globale
        resource_utilization = (cpu_usage + memory_usage + disk_usage) / 3
        self.system_metrics["resource_utilization"] = resource_utilization / 100
        
        await self.record_metric("resource_utilization_percent", resource_utilization)
        
        if network_io:
            for direction, bytes_count in network_io.items():
                await self.record_metric(f"network_{direction}_bytes", bytes_count)
    
    async def record_queue_metrics(
        self,
        queue_name: str,
        depth: int,
        processing_rate: float,
        wait_time: float
    ) -> None:
        """Enregistre les métriques de file d'attente"""
        labels = {"queue_name": queue_name}
        
        await self.record_metric("queue_depth", depth, labels)
        await self.record_metric("queue_processing_rate", processing_rate, labels)
        await self.record_metric("queue_wait_time", wait_time, labels)
        
        # Mise à jour de la profondeur totale des files
        self.system_metrics["queue_depth"] = depth
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques pour le dashboard automation"""
        metrics = {}
        
        # Métriques système en temps réel
        metrics["system"] = self.system_metrics.copy()
        
        # Métriques des dernières 24h
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        # Performance des pipelines
        execution_times = await self.get_metric_series(
            "pipeline_execution_duration", start_time, end_time
        )
        
        if execution_times:
            times = [p.value for p in execution_times]
            metrics["pipeline_performance"] = {
                "average_duration": statistics.mean(times),
                "min_duration": min(times),
                "max_duration": max(times),
                "p95_duration": statistics.quantiles(times, n=20)[18] if len(times) > 20 else max(times),
                "total_executions": len(times)
            }
        
        # Métriques par statut
        success_points = [p for p in execution_times if p.labels.get("status") == "success"]
        failed_points = [p for p in execution_times if p.labels.get("status") == "failed"]
        
        metrics["pipeline_status"] = {
            "success_count": len(success_points),
            "failure_count": len(failed_points),
            "success_rate": len(success_points) / len(execution_times) if execution_times else 0
        }
        
        # Métriques de ressources récentes
        recent_cpu = await self.get_metric_value("cpu_usage_percent", "average")
        recent_memory = await self.get_metric_value("memory_usage_percent", "average") 
        recent_disk = await self.get_metric_value("disk_usage_percent", "average")
        
        metrics["resources"] = {
            "cpu_usage": recent_cpu or 0,
            "memory_usage": recent_memory or 0,
            "disk_usage": recent_disk or 0,
            "resource_utilization": self.system_metrics["resource_utilization"]
        }
        
        return metrics
    
    async def get_alerts(self, level: Optional[MetricLevel] = None) -> List[Dict]:
        """Récupère les alertes actives"""
        if level:
            return [alert for alert in self.alerts if alert["level"] == level.value]
        return self.alerts.copy()
    
    async def _cleanup_old_points(self, metric_name: str) -> None:
        """Nettoie les points de métrique expirés"""
        series = self.metrics[metric_name]
        cutoff_time = datetime.utcnow() - timedelta(hours=series.retention_hours)
        
        # Filtrer les points récents
        recent_points = deque()
        for point in series.points:
            if point.timestamp >= cutoff_time:
                recent_points.append(point)
        
        series.points = recent_points
    
    async def _update_aggregates(self, metric_name: str) -> None:
        """Met à jour les agrégats pour une métrique"""
        series = self.metrics[metric_name]
        if not series.points:
            return
        
        values = [point.value for point in series.points]
        
        self.aggregates[metric_name] = {
            "count": len(values),
            "sum": sum(values),
            "average": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1],
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if len(values) > 1:
            self.aggregates[metric_name]["median"] = statistics.median(values)
            self.aggregates[metric_name]["stdev"] = statistics.stdev(values)
    
    async def _update_average_execution_time(self) -> None:
        """Met à jour le temps d'exécution moyen"""
        execution_times = await self.get_metric_series("pipeline_execution_duration")
        if execution_times:
            times = [p.value for p in execution_times if p.labels.get("status") == "success"]
            if times:
                self.system_metrics["average_execution_time"] = statistics.mean(times)
    
    async def _check_alerts(self, metric_name: str, value: Union[int, float]) -> None:
        """Vérifie les seuils d'alerte pour une métrique"""
        alerts_triggered = []
        
        # Vérification du taux d'erreur
        if metric_name == "error_rate" or "error_rate" in self.system_metrics:
            error_rate = self.system_metrics["error_rate"]
            if error_rate > self.alert_thresholds["error_rate"]:
                alerts_triggered.append({
                    "metric": "error_rate",
                    "value": error_rate,
                    "threshold": self.alert_thresholds["error_rate"],
                    "level": MetricLevel.ERROR.value,
                    "message": f"High error rate: {error_rate:.2%}",
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Vérification du temps d'exécution
        if "execution_duration" in metric_name and value > self.alert_thresholds["execution_time"]:
            alerts_triggered.append({
                "metric": metric_name,
                "value": value,
                "threshold": self.alert_thresholds["execution_time"],
                "level": MetricLevel.WARNING.value,
                "message": f"Long execution time: {value:.1f}s",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Vérification de la profondeur des files
        if metric_name == "queue_depth" and value > self.alert_thresholds["queue_depth"]:
            alerts_triggered.append({
                "metric": "queue_depth",
                "value": value,
                "threshold": self.alert_thresholds["queue_depth"],
                "level": MetricLevel.WARNING.value,
                "message": f"High queue depth: {value}",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Vérification de l'utilisation des ressources
        if self.system_metrics["resource_utilization"] > self.alert_thresholds["resource_utilization"]:
            alerts_triggered.append({
                "metric": "resource_utilization",
                "value": self.system_metrics["resource_utilization"],
                "threshold": self.alert_thresholds["resource_utilization"],
                "level": MetricLevel.WARNING.value,
                "message": f"High resource utilization: {self.system_metrics['resource_utilization']:.1%}",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Ajouter les nouvelles alertes
        for alert in alerts_triggered:
            # Éviter les doublons
            if not any(
                existing["metric"] == alert["metric"] and 
                existing["level"] == alert["level"]
                for existing in self.alerts
            ):
                self.alerts.append(alert)
                logger.warning(f"Alert triggered: {alert['message']}")
    
    async def register_custom_collector(
        self, 
        name: str, 
        collector_func: callable,
        interval: int = 60
    ) -> bool:
        """Enregistre un collecteur personnalisé"""
        try:
            self.collectors[name] = {
                "function": collector_func,
                "interval": interval,
                "last_run": None
            }
            logger.info(f"Registered custom collector: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register collector {name}: {str(e)}")
            return False
    
    async def start_collection(self) -> None:
        """Démarre la collecte automatique de métriques"""
        if self.is_collecting:
            logger.warning("Collection already started")
            return
        
        self.is_collecting = True
        logger.info("Starting metrics collection")
        
        while self.is_collecting:
            try:
                # Collecteurs personnalisés
                for name, collector in self.collectors.items():
                    last_run = collector.get("last_run")
                    interval = collector["interval"]
                    
                    if (not last_run or 
                        (datetime.utcnow() - last_run).total_seconds() >= interval):
                        
                        try:
                            await collector["function"](self)
                            collector["last_run"] = datetime.utcnow()
                        except Exception as e:
                            logger.error(f"Collector {name} failed: {str(e)}")
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Collection loop error: {str(e)}")
                await asyncio.sleep(self.collection_interval)
    
    async def stop_collection(self) -> None:
        """Arrête la collecte de métriques"""
        self.is_collecting = False
        logger.info("Stopped metrics collection")

# Collecteurs système prédéfinis
async def system_resource_collector(metrics_collector: AutomationMetricsCollector):
    """Collecteur de métriques système"""
    import psutil
    
    # CPU et mémoire
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    await metrics_collector.record_resource_metrics(
        cpu_usage=cpu_percent,
        memory_usage=memory.percent,
        disk_usage=disk.percent / disk.total * 100
    )

async def pipeline_health_collector(metrics_collector: AutomationMetricsCollector):
    """Collecteur de santé des pipelines"""
    # Simuler la collecte de métriques de santé
    await metrics_collector.record_metric("active_pipelines", 5)
    await metrics_collector.record_metric("pending_jobs", 12)
    await metrics_collector.record_metric("healthy_workers", 8)

# Exemple d'utilisation enterprise
async def demo_metrics_collection():
    """Démo de collecte de métriques automation enterprise"""
    collector = AutomationMetricsCollector()
    
    # Enregistrer des métriques
    await collector.register_metric("test_counter", MetricType.COUNTER)
    await collector.register_metric("test_gauge", MetricType.GAUGE)
    
    # Enregistrer des collecteurs
    await collector.register_custom_collector(
        "system_resources", 
        system_resource_collector, 
        interval=30
    )
    
    # Simuler des métriques de pipeline
    await collector.record_pipeline_execution(
        "data_pipeline_1", 
        "exec_123", 
        "success", 
        125.5,
        {"processed_records": 1000, "validation_score": 0.95}
    )
    
    # Obtenir les métriques du dashboard
    dashboard = await collector.get_dashboard_metrics()
    print(f"Dashboard metrics: {json.dumps(dashboard, indent=2, default=str)}")
    
    # Vérifier les alertes
    alerts = await collector.get_alerts()
    if alerts:
        print(f"Active alerts: {len(alerts)}")

if __name__ == "__main__":
    asyncio.run(demo_metrics_collection())