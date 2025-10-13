"""
Pipeline de Monitoring - IA Chérie Enterprise ML Pipeline
Système de surveillance en temps réel avec métriques avancées et alertes

Auteur: Mlaiel (Expert Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + DevOps)  
Copyright: © 2024 IA Chérie. Tous droits réservés.
Licence: Propriétaire - Usage strictement réservé à IA Chérie
Version: 1.0.0 - Architecture Niveau 3 Backend

CONFIDENTIAL - NE PAS DISTRIBUER
Ce code contient des informations propriétaires et des algorithmes d'IA confidentiels.
Toute reproduction, modification ou distribution non autorisée est strictement interdite.
"""

import asyncio
import json
import logging
import os
import psutil
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import requests
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest


class MetricType(Enum):
    """Types de métriques disponibles"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    EMERGENCY = 5


class MonitoringStatus(Enum):
    """Statuts du système de monitoring"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class MetricConfig:
    """Configuration d'une métrique"""
    name: str
    metric_type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None
    alert_thresholds: Dict[AlertSeverity, float] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Règle d'alerte"""
    name: str
    condition: str
    severity: AlertSeverity
    threshold: float
    duration: timedelta
    description: str
    notification_channels: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class MonitoringEvent:
    """Événement de monitoring"""
    timestamp: datetime
    event_type: str
    severity: AlertSeverity
    message: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False


@dataclass
class SystemHealth:
    """État de santé du système"""
    status: MonitoringStatus
    score: float
    components: Dict[str, Dict[str, Any]]
    alerts_active: int
    last_check: datetime
    uptime: timedelta


class PipelineMonitoring:
    """
    Système de monitoring avancé pour IA Chérie
    
    Fonctionnalités:
    - Surveillance en temps réel des performances
    - Métriques personnalisées avec Prometheus
    - Système d'alertes intelligent avec escalade
    - Monitoring de santé des composants
    - Dashboards en temps réel
    - Intégration avec systèmes externes
    - Historique des performances
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = self._setup_logger()
        
        # Registre Prometheus
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        
        # Stockage des données
        self.time_series_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.events: deque = deque(maxlen=1000)
        self.active_alerts: Dict[str, MonitoringEvent] = {}
        
        # Configuration par défaut
        self.alert_rules = self._setup_default_alert_rules()
        self.metric_configs = self._setup_default_metrics()
        
        # Thread pool pour les tâches asynchrones
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # État du système
        self.system_start_time = datetime.now()
        self.monitoring_enabled = True
        
        # Initialisation des métriques
        self._initialize_metrics()
        
        # Démarrage du monitoring en arrière-plan
        self._start_background_monitoring()
    
    def _setup_logger(self) -> logging.Logger:
        """Configuration du logging"""
        logger = logging.getLogger(f"iacherie_monitoring_{id(self)}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _setup_default_metrics(self) -> List[MetricConfig]:
        """Configuration des métriques par défaut"""
        return [
            MetricConfig(
                name="pipeline_requests_total",
                metric_type=MetricType.COUNTER,
                description="Nombre total de requêtes traitées",
                labels=["pipeline", "status"]
            ),
            MetricConfig(
                name="pipeline_duration_seconds",
                metric_type=MetricType.HISTOGRAM,
                description="Durée de traitement des pipelines",
                labels=["pipeline"],
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
            ),
            MetricConfig(
                name="pipeline_active_connections",
                metric_type=MetricType.GAUGE,
                description="Nombre de connexions actives",
                labels=["pipeline"]
            ),
            MetricConfig(
                name="system_cpu_usage",
                metric_type=MetricType.GAUGE,
                description="Usage CPU du système"
            ),
            MetricConfig(
                name="system_memory_usage",
                metric_type=MetricType.GAUGE,
                description="Usage mémoire du système"
            ),
            MetricConfig(
                name="pipeline_errors_total",
                metric_type=MetricType.COUNTER,
                description="Nombre total d'erreurs",
                labels=["pipeline", "error_type"]
            )
        ]
    
    def _setup_default_alert_rules(self) -> List[AlertRule]:
        """Configuration des règles d'alerte par défaut"""
        return [
            AlertRule(
                name="high_cpu_usage",
                condition="system_cpu_usage > threshold",
                severity=AlertSeverity.WARNING,
                threshold=80.0,
                duration=timedelta(minutes=5),
                description="Usage CPU élevé détecté"
            ),
            AlertRule(
                name="high_memory_usage",
                condition="system_memory_usage > threshold",
                severity=AlertSeverity.WARNING,
                threshold=85.0,
                duration=timedelta(minutes=3),
                description="Usage mémoire élevé détecté"
            ),
            AlertRule(
                name="pipeline_error_rate",
                condition="error_rate > threshold",
                severity=AlertSeverity.ERROR,
                threshold=5.0,
                duration=timedelta(minutes=2),
                description="Taux d'erreur élevé dans les pipelines"
            ),
            AlertRule(
                name="pipeline_response_time",
                condition="avg_response_time > threshold",
                severity=AlertSeverity.WARNING,
                threshold=10.0,
                duration=timedelta(minutes=5),
                description="Temps de réponse des pipelines dégradé"
            )
        ]
    
    def _initialize_metrics(self):
        """Initialisation des métriques Prometheus"""
        for config in self.metric_configs:
            if config.metric_type == MetricType.COUNTER:
                metric = Counter(
                    config.name,
                    config.description,
                    config.labels,
                    registry=self.registry
                )
            elif config.metric_type == MetricType.GAUGE:
                metric = Gauge(
                    config.name,
                    config.description,
                    config.labels,
                    registry=self.registry
                )
            elif config.metric_type == MetricType.HISTOGRAM:
                metric = Histogram(
                    config.name,
                    config.description,
                    config.labels,
                    buckets=config.buckets,
                    registry=self.registry
                )
            
            self.metrics[config.name] = metric
    
    def _start_background_monitoring(self):
        """Démarrage du monitoring en arrière-plan"""
        def monitoring_loop():
            while self.monitoring_enabled:
                try:
                    self._collect_system_metrics()
                    self._check_alert_rules()
                    time.sleep(10)  # Collecte toutes les 10 secondes
                except Exception as e:
                    self.logger.error(f"Erreur dans la boucle de monitoring: {e}")
                    time.sleep(5)
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
    
    def _collect_system_metrics(self):
        """Collecte des métriques système"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system_cpu_usage", cpu_percent)
            
            # Mémoire
            memory = psutil.virtual_memory()
            self.record_metric("system_memory_usage", memory.percent)
            
            # Disque
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("system_disk_usage", disk_percent)
            
            # Réseau
            network = psutil.net_io_counters()
            self.record_metric("network_bytes_sent", network.bytes_sent)
            self.record_metric("network_bytes_recv", network.bytes_recv)
            
        except Exception as e:
            self.logger.error(f"Erreur collecte métriques système: {e}")
    
    def record_metric(
        self, 
        metric_name: str, 
        value: Union[int, float], 
        labels: Optional[Dict[str, str]] = None
    ):
        """Enregistrement d'une métrique"""
        try:
            timestamp = datetime.now()
            
            # Stockage dans les séries temporelles
            self.time_series_data[metric_name].append({
                "timestamp": timestamp,
                "value": value,
                "labels": labels or {}
            })
            
            # Mise à jour Prometheus
            if metric_name in self.metrics:
                metric = self.metrics[metric_name]
                
                if isinstance(metric, (Counter, Gauge)):
                    if labels:
                        metric.labels(**labels).set(value)
                    else:
                        metric.set(value)
                elif isinstance(metric, Histogram):
                    if labels:
                        metric.labels(**labels).observe(value)
                    else:
                        metric.observe(value)
            
        except Exception as e:
            self.logger.error(f"Erreur enregistrement métrique {metric_name}: {e}")
    
    def increment_counter(
        self, 
        metric_name: str, 
        value: float = 1.0, 
        labels: Optional[Dict[str, str]] = None
    ):
        """Incrémentation d'un compteur"""
        try:
            if metric_name in self.metrics:
                counter = self.metrics[metric_name]
                if isinstance(counter, Counter):
                    if labels:
                        counter.labels(**labels).inc(value)
                    else:
                        counter.inc(value)
        except Exception as e:
            self.logger.error(f"Erreur incrémentation compteur {metric_name}: {e}")
    
    def start_timer(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Démarrage d'un timer pour mesurer la durée"""
        class Timer:
            def __init__(self, monitoring, name, labels):
                self.monitoring = monitoring
                self.name = name
                self.labels = labels
                self.start_time = None
            
            def __enter__(self):
                self.start_time = time.time()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.start_time:
                    duration = time.time() - self.start_time
                    self.monitoring.record_metric(self.name, duration, self.labels)
        
        return Timer(self, metric_name, labels)
    
    def _check_alert_rules(self):
        """Vérification des règles d'alerte"""
        current_time = datetime.now()
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            try:
                should_alert = self._evaluate_alert_condition(rule)
                alert_key = f"{rule.name}_{rule.severity.name}"
                
                if should_alert and alert_key not in self.active_alerts:
                    # Nouvelle alerte
                    alert_event = MonitoringEvent(
                        timestamp=current_time,
                        event_type="alert",
                        severity=rule.severity,
                        message=f"Alerte {rule.name}: {rule.description}",
                        source="monitoring_system",
                        metadata={"rule": rule.name, "threshold": rule.threshold}
                    )
                    
                    self.active_alerts[alert_key] = alert_event
                    self.events.append(alert_event)
                    
                    self._send_alert_notification(alert_event, rule)
                    
                elif not should_alert and alert_key in self.active_alerts:
                    # Résolution d'alerte
                    resolved_alert = self.active_alerts[alert_key]
                    resolved_alert.resolved = True
                    del self.active_alerts[alert_key]
                    
                    resolution_event = MonitoringEvent(
                        timestamp=current_time,
                        event_type="alert_resolved",
                        severity=AlertSeverity.INFO,
                        message=f"Alerte {rule.name} résolue",
                        source="monitoring_system",
                        metadata={"rule": rule.name}
                    )
                    
                    self.events.append(resolution_event)
                    
            except Exception as e:
                self.logger.error(f"Erreur vérification règle {rule.name}: {e}")
    
    def _evaluate_alert_condition(self, rule: AlertRule) -> bool:
        """Évaluation d'une condition d'alerte"""
        try:
            if rule.name == "high_cpu_usage":
                recent_data = list(self.time_series_data["system_cpu_usage"])[-5:]
                if recent_data:
                    avg_cpu = sum(d["value"] for d in recent_data) / len(recent_data)
                    return avg_cpu > rule.threshold
            
            elif rule.name == "high_memory_usage":
                recent_data = list(self.time_series_data["system_memory_usage"])[-3:]
                if recent_data:
                    avg_memory = sum(d["value"] for d in recent_data) / len(recent_data)
                    return avg_memory > rule.threshold
            
            elif rule.name == "pipeline_error_rate":
                return self._calculate_error_rate() > rule.threshold
            
            elif rule.name == "pipeline_response_time":
                return self._calculate_avg_response_time() > rule.threshold
            
        except Exception as e:
            self.logger.error(f"Erreur évaluation condition {rule.name}: {e}")
        
        return False
    
    def _calculate_error_rate(self) -> float:
        """Calcul du taux d'erreur"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(minutes=5)
            
            total_requests = 0
            error_requests = 0
            
            for data_point in self.time_series_data["pipeline_requests_total"]:
                if data_point["timestamp"] >= cutoff_time:
                    total_requests += data_point["value"]
                    if data_point["labels"].get("status") == "error":
                        error_requests += data_point["value"]
            
            if total_requests > 0:
                return (error_requests / total_requests) * 100
            
        except Exception as e:
            self.logger.error(f"Erreur calcul taux d'erreur: {e}")
        
        return 0.0
    
    def _calculate_avg_response_time(self) -> float:
        """Calcul du temps de réponse moyen"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(minutes=5)
            
            response_times = []
            for data_point in self.time_series_data["pipeline_duration_seconds"]:
                if data_point["timestamp"] >= cutoff_time:
                    response_times.append(data_point["value"])
            
            if response_times:
                return sum(response_times) / len(response_times)
            
        except Exception as e:
            self.logger.error(f"Erreur calcul temps de réponse: {e}")
        
        return 0.0
    
    def _send_alert_notification(self, alert: MonitoringEvent, rule: AlertRule):
        """Envoi de notifications d'alerte"""
        try:
            notification_data = {
                "alert_name": rule.name,
                "severity": alert.severity.name,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata
            }
            
            # Log local
            self.logger.warning(f"ALERTE {alert.severity.name}: {alert.message}")
            
            # Notifications externes (webhook, email, etc.)
            for channel in rule.notification_channels:
                self._send_to_channel(channel, notification_data)
                
        except Exception as e:
            self.logger.error(f"Erreur envoi notification: {e}")
    
    def _send_to_channel(self, channel: str, data: Dict[str, Any]):
        """Envoi vers un canal de notification spécifique"""
        try:
            if channel.startswith("webhook:"):
                webhook_url = channel.replace("webhook:", "")
                requests.post(webhook_url, json=data, timeout=5)
            
            elif channel == "log":
                self.logger.info(f"Notification: {json.dumps(data)}")
            
            # Autres canaux (email, Slack, etc.) peuvent être ajoutés ici
            
        except Exception as e:
            self.logger.error(f"Erreur envoi vers canal {channel}: {e}")
    
    def get_system_health(self) -> SystemHealth:
        """Obtention de l'état de santé du système"""
        try:
            current_time = datetime.now()
            uptime = current_time - self.system_start_time
            
            # Calcul du score de santé
            health_score = self._calculate_health_score()
            
            # Détermination du statut
            if health_score >= 90:
                status = MonitoringStatus.HEALTHY
            elif health_score >= 70:
                status = MonitoringStatus.DEGRADED
            elif health_score >= 50:
                status = MonitoringStatus.UNHEALTHY
            else:
                status = MonitoringStatus.CRITICAL
            
            # Analyse des composants
            components = {
                "cpu": self._get_component_health("cpu"),
                "memory": self._get_component_health("memory"),
                "disk": self._get_component_health("disk"),
                "network": self._get_component_health("network"),
                "pipelines": self._get_component_health("pipelines")
            }
            
            return SystemHealth(
                status=status,
                score=health_score,
                components=components,
                alerts_active=len(self.active_alerts),
                last_check=current_time,
                uptime=uptime
            )
            
        except Exception as e:
            self.logger.error(f"Erreur calcul santé système: {e}")
            return SystemHealth(
                status=MonitoringStatus.CRITICAL,
                score=0.0,
                components={},
                alerts_active=len(self.active_alerts),
                last_check=datetime.now(),
                uptime=timedelta(0)
            )
    
    def _calculate_health_score(self) -> float:
        """Calcul du score de santé global"""
        try:
            scores = []
            
            # Score CPU
            cpu_data = list(self.time_series_data["system_cpu_usage"])[-5:]
            if cpu_data:
                avg_cpu = sum(d["value"] for d in cpu_data) / len(cpu_data)
                cpu_score = max(0, 100 - avg_cpu)
                scores.append(cpu_score)
            
            # Score mémoire
            memory_data = list(self.time_series_data["system_memory_usage"])[-5:]
            if memory_data:
                avg_memory = sum(d["value"] for d in memory_data) / len(memory_data)
                memory_score = max(0, 100 - avg_memory)
                scores.append(memory_score)
            
            # Score erreurs
            error_rate = self._calculate_error_rate()
            error_score = max(0, 100 - error_rate * 2)
            scores.append(error_score)
            
            # Score alertes
            alert_penalty = len(self.active_alerts) * 10
            alert_score = max(0, 100 - alert_penalty)
            scores.append(alert_score)
            
            if scores:
                return sum(scores) / len(scores)
            
        except Exception as e:
            self.logger.error(f"Erreur calcul score santé: {e}")
        
        return 50.0
    
    def _get_component_health(self, component: str) -> Dict[str, Any]:
        """Obtention de la santé d'un composant spécifique"""
        try:
            if component == "cpu":
                recent_data = list(self.time_series_data["system_cpu_usage"])[-5:]
                if recent_data:
                    avg_usage = sum(d["value"] for d in recent_data) / len(recent_data)
                    return {
                        "status": "healthy" if avg_usage < 80 else "warning",
                        "usage_percent": avg_usage,
                        "last_update": recent_data[-1]["timestamp"].isoformat()
                    }
            
            elif component == "memory":
                recent_data = list(self.time_series_data["system_memory_usage"])[-5:]
                if recent_data:
                    avg_usage = sum(d["value"] for d in recent_data) / len(recent_data)
                    return {
                        "status": "healthy" if avg_usage < 85 else "warning",
                        "usage_percent": avg_usage,
                        "last_update": recent_data[-1]["timestamp"].isoformat()
                    }
            
            elif component == "pipelines":
                error_rate = self._calculate_error_rate()
                avg_response_time = self._calculate_avg_response_time()
                
                return {
                    "status": "healthy" if error_rate < 5 and avg_response_time < 10 else "warning",
                    "error_rate": error_rate,
                    "avg_response_time": avg_response_time
                }
            
        except Exception as e:
            self.logger.error(f"Erreur santé composant {component}: {e}")
        
        return {"status": "unknown", "error": "Unable to determine health"}
    
    def get_metrics_export(self) -> str:
        """Export des métriques au format Prometheus"""
        try:
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Erreur export métriques: {e}")
            return ""
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Données pour dashboard en temps réel"""
        try:
            current_time = datetime.now()
            
            # Métriques système récentes
            recent_metrics = {}
            for metric_name in ["system_cpu_usage", "system_memory_usage", "pipeline_duration_seconds"]:
                recent_data = list(self.time_series_data[metric_name])[-60:]  # Dernière minute
                if recent_data:
                    recent_metrics[metric_name] = [
                        {
                            "timestamp": d["timestamp"].isoformat(),
                            "value": d["value"]
                        }
                        for d in recent_data
                    ]
            
            # Événements récents
            recent_events = [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "severity": event.severity.name,
                    "message": event.message,
                    "resolved": event.resolved
                }
                for event in list(self.events)[-20:]  # 20 derniers événements
            ]
            
            # Santé du système
            system_health = self.get_system_health()
            
            return {
                "timestamp": current_time.isoformat(),
                "system_health": {
                    "status": system_health.status.value,
                    "score": system_health.score,
                    "uptime_seconds": system_health.uptime.total_seconds(),
                    "active_alerts": system_health.alerts_active
                },
                "metrics": recent_metrics,
                "events": recent_events,
                "active_alerts": [
                    {
                        "name": alert.source,
                        "severity": alert.severity.name,
                        "message": alert.message,
                        "duration": (current_time - alert.timestamp).total_seconds()
                    }
                    for alert in self.active_alerts.values()
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Erreur génération données dashboard: {e}")
            return {"error": "Unable to generate dashboard data"}
    
    def add_custom_metric(self, config: MetricConfig):
        """Ajout d'une métrique personnalisée"""
        try:
            self.metric_configs.append(config)
            
            # Initialisation de la métrique Prometheus
            if config.metric_type == MetricType.COUNTER:
                metric = Counter(
                    config.name,
                    config.description,
                    config.labels,
                    registry=self.registry
                )
            elif config.metric_type == MetricType.GAUGE:
                metric = Gauge(
                    config.name,
                    config.description,
                    config.labels,
                    registry=self.registry
                )
            elif config.metric_type == MetricType.HISTOGRAM:
                metric = Histogram(
                    config.name,
                    config.description,
                    config.labels,
                    buckets=config.buckets,
                    registry=self.registry
                )
            
            self.metrics[config.name] = metric
            self.logger.info(f"Métrique personnalisée ajoutée: {config.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur ajout métrique {config.name}: {e}")
    
    def add_alert_rule(self, rule: AlertRule):
        """Ajout d'une règle d'alerte personnalisée"""
        try:
            self.alert_rules.append(rule)
            self.logger.info(f"Règle d'alerte ajoutée: {rule.name}")
        except Exception as e:
            self.logger.error(f"Erreur ajout règle d'alerte {rule.name}: {e}")
    
    def stop_monitoring(self):
        """Arrêt du système de monitoring"""
        self.monitoring_enabled = False
        self.executor.shutdown(wait=True)
        self.logger.info("Système de monitoring arrêté")


# Configuration par défaut
DEFAULT_MONITORING_CONFIG = {
    "collection_interval": 10,
    "retention_days": 30,
    "alert_channels": ["log"],
    "dashboard_enabled": True,
    "prometheus_enabled": True
}


async def main():
    """Fonction principale pour tests"""
    monitoring = PipelineMonitoring(DEFAULT_MONITORING_CONFIG)
    
    # Simulation de métriques
    monitoring.increment_counter("pipeline_requests_total", labels={"pipeline": "test", "status": "success"})
    monitoring.record_metric("pipeline_duration_seconds", 2.5, {"pipeline": "test"})
    
    # Attente pour collecte des métriques
    await asyncio.sleep(5)
    
    # Vérification de la santé
    health = monitoring.get_system_health()
    print(f"Santé du système: {health.status.value} (Score: {health.score:.2f})")
    
    # Données dashboard
    dashboard = monitoring.get_dashboard_data()
    print(f"Alertes actives: {dashboard['system_health']['active_alerts']}")
    
    monitoring.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())