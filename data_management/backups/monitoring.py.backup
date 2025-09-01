"""📊 Monitoring System - Advanced Backup Monitoring & Analytics
============================================================
Module: backend/data_management/backups/monitoring.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Monitoring System - Enterprise Production-Ready
Responsibility: Monitoring temps réel et analytics des sauvegardes
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""
import asyncio
import logging
import time
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import weakref

from .models import BackupMetadata, BackupStatus, BackupType
from .exceptions import MonitoringException

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types de métriques"""
    COUNTER = "counter"           # Compteur incrémental
    GAUGE = "gauge"              # Valeur instantanée
    HISTOGRAM = "histogram"       # Distribution de valeurs
    TIMER = "timer"              # Durée d'opération


@dataclass
class Alert:
    """Alerte de monitoring"""
    alert_id: str
    level: AlertLevel
    message: str
    source: str
    metric_name: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "alert_id": self.alert_id,
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "metric_name": self.metric_name,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "metadata": self.metadata
        }


@dataclass
class Metric:
    """Métrique de monitoring"""
    name: str
    type: MetricType
    value: Union[float, int]
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "unit": self.unit,
            "description": self.description
        }


@dataclass
class PerformanceStats:
    """Statistiques de performance"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Dict[str, float] = field(default_factory=dict)
    backup_throughput: float = 0.0  # MB/s
    active_jobs: int = 0
    queue_size: int = 0
    error_rate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "network_io": self.network_io,
            "backup_throughput": self.backup_throughput,
            "active_jobs": self.active_jobs,
            "queue_size": self.queue_size,
            "error_rate": self.error_rate,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class MonitoringConfig:
    """Configuration du monitoring"""
    collection_interval: float = 10.0  # secondes
    retention_days: int = 30
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    enable_system_metrics: bool = True
    enable_alerts: bool = True
    max_alerts_per_hour: int = 100
    metrics_buffer_size: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "collection_interval": self.collection_interval,
            "retention_days": self.retention_days,
            "alert_thresholds": self.alert_thresholds,
            "enable_system_metrics": self.enable_system_metrics,
            "enable_alerts": self.enable_alerts,
            "max_alerts_per_hour": self.max_alerts_per_hour,
            "metrics_buffer_size": self.metrics_buffer_size
        }


class MetricsCollector:
    """
    Collecteur de métriques avec buffers circulaires
    
    Fonctionnalités:
    - Collection métriques système et application
    - Buffers circulaires pour performance
    - Agrégation et calculs statistiques
    - Export vers systèmes externes
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        
        # Buffers circulaires pour métriques
        self.metrics_buffer: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=config.metrics_buffer_size)
        )
        
        # Métriques agrégées
        self.aggregated_metrics: Dict[str, Dict[str, float]] = {}
        
        # Lock pour thread safety
        self._lock = threading.Lock()
        
        logger.info("MetricsCollector initialized")
    
    def record_metric(
        self,
        name: str,
        value: Union[float, int],
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None,
        unit: Optional[str] = None
    ):
        """
        Enregistre une métrique
        
        Args:
            name: Nom de la métrique
            value: Valeur
            metric_type: Type de métrique
            labels: Labels additionnels
            unit: Unité de mesure
        """
        try:
            metric = Metric(
                name=name,
                type=metric_type,
                value=value,
                labels=labels or {},
                unit=unit
            )
            
            with self._lock:
                self.metrics_buffer[name].append(metric)
            
            # Mise à jour agrégations en temps réel
            self._update_aggregations(name, value)
            
        except Exception as e:
            logger.error(f"Failed to record metric {name}: {e}")
    
    def _update_aggregations(self, metric_name: str, value: float):
        """Met à jour les agrégations en temps réel"""
        if metric_name not in self.aggregated_metrics:
            self.aggregated_metrics[metric_name] = {
                "count": 0,
                "sum": 0.0,
                "min": float('inf'),
                "max": float('-inf'),
                "avg": 0.0
            }
        
        agg = self.aggregated_metrics[metric_name]
        agg["count"] += 1
        agg["sum"] += value
        agg["min"] = min(agg["min"], value)
        agg["max"] = max(agg["max"], value)
        agg["avg"] = agg["sum"] / agg["count"]
    
    def get_metric_history(
        self,
        metric_name: str,
        duration: Optional[timedelta] = None
    ) -> List[Metric]:
        """
        Récupère l'historique d'une métrique
        
        Args:
            metric_name: Nom de la métrique
            duration: Durée à récupérer (None = toute)
            
        Returns:
            List[Metric]: Historique des valeurs
        """
        with self._lock:
            metrics = list(self.metrics_buffer.get(metric_name, []))
        
        if duration:
            cutoff_time = datetime.now() - duration
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        return sorted(metrics, key=lambda x: x.timestamp)
    
    def get_metric_stats(self, metric_name: str) -> Optional[Dict[str, float]]:
        """
        Récupère les statistiques agrégées d'une métrique
        
        Args:
            metric_name: Nom de la métrique
            
        Returns:
            Optional[Dict[str, float]]: Statistiques ou None
        """
        return self.aggregated_metrics.get(metric_name)
    
    def collect_system_metrics(self) -> PerformanceStats:
        """
        Collecte les métriques système
        
        Returns:
            PerformanceStats: Statistiques système
        """
        try:
            # CPU
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Mémoire
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disque
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Réseau
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            stats = PerformanceStats(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io
            )
            
            # Enregistrement comme métriques
            self.record_metric("system.cpu_usage", cpu_usage, MetricType.GAUGE, unit="%")
            self.record_metric("system.memory_usage", memory_usage, MetricType.GAUGE, unit="%")
            self.record_metric("system.disk_usage", disk_usage, MetricType.GAUGE, unit="%")
            
            return stats
            
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
            return PerformanceStats()
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Exporte les métriques vers format externe
        
        Args:
            format: Format d'export (json, prometheus, etc.)
            
        Returns:
            str: Métriques exportées
        """
        try:
            if format == "json":
                return self._export_json()
            elif format == "prometheus":
                return self._export_prometheus()
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Metrics export failed: {e}")
            return ""
    
    def _export_json(self) -> str:
        """Export au format JSON"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "aggregations": self.aggregated_metrics
        }
        
        with self._lock:
            for metric_name, metrics in self.metrics_buffer.items():
                export_data["metrics"][metric_name] = [
                    m.to_dict() for m in list(metrics)
                ]
        
        return json.dumps(export_data, indent=2)
    
    def _export_prometheus(self) -> str:
        """Export au format Prometheus"""
        lines = []
        
        with self._lock:
            for metric_name, metrics in self.metrics_buffer.items():
                if not metrics:
                    continue
                
                latest_metric = metrics[-1]
                
                # Help line
                if latest_metric.description:
                    lines.append(f"# HELP {metric_name} {latest_metric.description}")
                
                # Type line
                lines.append(f"# TYPE {metric_name} {latest_metric.type.value}")
                
                # Metric line avec labels
                labels_str = ""
                if latest_metric.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in latest_metric.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"
                
                lines.append(f"{metric_name}{labels_str} {latest_metric.value}")
        
        return "\n".join(lines)


class AlertManager:
    """
    Gestionnaire d'alertes intelligent
    
    Fonctionnalités:
    - Évaluation règles d'alerte
    - Déduplication et groupement
    - Escalade et notifications
    - Historique et analytics
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        
        # Alertes actives et historique
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Règles d'alerte
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting
        self.alert_counts: Dict[str, int] = defaultdict(int)
        self.alert_timestamps: Dict[str, datetime] = {}
        
        # Callbacks de notification
        self.notification_callbacks: List[Callable[[Alert], None]] = []
        
        # Initialisation règles par défaut
        self._setup_default_rules()
        
        logger.info("AlertManager initialized")
    
    def _setup_default_rules(self):
        """Configure les règles d'alerte par défaut"""
        default_rules = {
            "high_cpu_usage": {
                "metric": "system.cpu_usage",
                "condition": ">",
                "threshold": 80.0,
                "level": AlertLevel.WARNING,
                "message": "High CPU usage detected: {value}%"
            },
            "high_memory_usage": {
                "metric": "system.memory_usage",
                "condition": ">",
                "threshold": 90.0,
                "level": AlertLevel.ERROR,
                "message": "High memory usage detected: {value}%"
            },
            "backup_failure_rate": {
                "metric": "backup.failure_rate",
                "condition": ">",
                "threshold": 10.0,
                "level": AlertLevel.CRITICAL,
                "message": "High backup failure rate: {value}%"
            },
            "disk_space_low": {
                "metric": "system.disk_usage",
                "condition": ">",
                "threshold": 95.0,
                "level": AlertLevel.CRITICAL,
                "message": "Low disk space: {value}% used"
            }
        }
        
        # Intégration seuils personnalisés
        for rule_name, rule in default_rules.items():
            if rule["metric"] in self.config.alert_thresholds:
                rule["threshold"] = self.config.alert_thresholds[rule["metric"]]
        
        self.alert_rules.update(default_rules)
    
    def add_alert_rule(
        self,
        rule_name: str,
        metric: str,
        condition: str,
        threshold: float,
        level: AlertLevel,
        message: str
    ):
        """
        Ajoute une règle d'alerte
        
        Args:
            rule_name: Nom de la règle
            metric: Métrique à surveiller
            condition: Condition (>, <, ==, etc.)
            threshold: Seuil déclencheur
            level: Niveau d'alerte
            message: Message d'alerte
        """
        self.alert_rules[rule_name] = {
            "metric": metric,
            "condition": condition,
            "threshold": threshold,
            "level": level,
            "message": message
        }
        
        logger.info(f"Added alert rule: {rule_name}")
    
    def evaluate_metrics(self, metrics: List[Metric]):
        """
        Évalue les métriques contre les règles d'alerte
        
        Args:
            metrics: Liste de métriques à évaluer
        """
        if not self.config.enable_alerts:
            return
        
        for metric in metrics:
            self._evaluate_metric_against_rules(metric)
    
    def _evaluate_metric_against_rules(self, metric: Metric):
        """Évalue une métrique contre toutes les règles"""
        for rule_name, rule in self.alert_rules.items():
            if rule["metric"] != metric.name:
                continue
            
            if self._check_condition(metric.value, rule["condition"], rule["threshold"]):
                self._trigger_alert(rule_name, rule, metric)
    
    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Vérifie si une condition est remplie"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False
    
    def _trigger_alert(self, rule_name: str, rule: Dict[str, Any], metric: Metric):
        """Déclenche une alerte"""
        try:
            # Rate limiting
            if not self._check_rate_limit(rule_name):
                return
            
            alert_id = f"{rule_name}_{int(time.time())}"
            
            alert = Alert(
                alert_id=alert_id,
                level=rule["level"],
                message=rule["message"].format(value=metric.value),
                source=f"rule:{rule_name}",
                metric_name=metric.name,
                value=metric.value,
                threshold=rule["threshold"],
                metadata={
                    "rule_name": rule_name,
                    "metric_labels": metric.labels
                }
            )
            
            # Déduplication
            if not self._is_duplicate_alert(alert):
                self.active_alerts[alert_id] = alert
                self.alert_history.append(alert)
                
                # Notifications
                self._send_notifications(alert)
                
                logger.warning(f"Alert triggered: {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert for rule {rule_name}: {e}")
    
    def _check_rate_limit(self, rule_name: str) -> bool:
        """Vérifie les limites de taux d'alerte"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Nettoyage ancien comptage
        if rule_name in self.alert_timestamps:
            if self.alert_timestamps[rule_name] < hour_ago:
                self.alert_counts[rule_name] = 0
        
        # Vérification limite
        if self.alert_counts[rule_name] >= self.config.max_alerts_per_hour:
            return False
        
        # Mise à jour compteurs
        self.alert_counts[rule_name] += 1
        self.alert_timestamps[rule_name] = now
        
        return True
    
    def _is_duplicate_alert(self, new_alert: Alert) -> bool:
        """Vérifie si l'alerte est un doublon"""
        for existing_alert in self.active_alerts.values():
            if (existing_alert.source == new_alert.source and
                existing_alert.metric_name == new_alert.metric_name and
                not existing_alert.resolved):
                
                # Mise à jour timestamp si même alerte
                existing_alert.timestamp = new_alert.timestamp
                return True
        
        return False
    
    def _send_notifications(self, alert: Alert):
        """Envoie les notifications d'alerte"""
        for callback in self.notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Notification callback failed: {e}")
    
    def add_notification_callback(self, callback: Callable[[Alert], None]):
        """
        Ajoute un callback de notification
        
        Args:
            callback: Function appelée lors d'une alerte
        """
        self.notification_callbacks.append(callback)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acquitte une alerte
        
        Args:
            alert_id: ID de l'alerte
            
        Returns:
            bool: True si acquittement réussi
        """
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
        
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Résout une alerte
        
        Args:
            alert_id: ID de l'alerte
            
        Returns:
            bool: True si résolution réussie
        """
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
        
        return False
    
    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """
        Récupère les alertes actives
        
        Args:
            level: Filtrer par niveau (optionnel)
            
        Returns:
            List[Alert]: Alertes actives
        """
        alerts = list(self.active_alerts.values())
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alert_history(
        self,
        hours: int = 24,
        level: Optional[AlertLevel] = None
    ) -> List[Alert]:
        """
        Récupère l'historique des alertes
        
        Args:
            hours: Nombre d'heures à récupérer
            level: Filtrer par niveau (optionnel)
            
        Returns:
            List[Alert]: Historique des alertes
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        alerts = [
            a for a in self.alert_history
            if a.timestamp >= cutoff_time
        ]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)


class BackupMonitor:
    """
    Moniteur principal des sauvegardes
    
    Fonctionnalités:
    - Monitoring temps réel
    - Collection métriques centralisée
    - Gestion alertes
    - Dashboard et reporting
    - Intégration systèmes externes
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        
        # Composants de monitoring
        self.metrics_collector = MetricsCollector(self.config)
        self.alert_manager = AlertManager(self.config)
        
        # État du monitoring
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Références faibles aux objets monitorés
        self.monitored_objects: List[weakref.ref] = []
        
        # Callbacks personnalisés
        self.metric_callbacks: List[Callable[[List[Metric]], None]] = []
        
        # Initialisation callbacks par défaut
        self._setup_default_callbacks()
        
        logger.info("BackupMonitor initialized")
    
    def _setup_default_callbacks(self):
        """Configure les callbacks par défaut"""
        # Callback pour évaluation alertes
        def evaluate_alerts(metrics: List[Metric]):
            self.alert_manager.evaluate_metrics(metrics)
        
        self.add_metric_callback(evaluate_alerts)
        
        # Callback notification simple (log)
        def log_alert(alert: Alert):
            logger.warning(f"ALERT [{alert.level.value.upper()}]: {alert.message}")
        
        self.alert_manager.add_notification_callback(log_alert)
    
    async def start_monitoring(self):
        """Démarre le monitoring en arrière-plan"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Backup monitoring started")
    
    async def stop_monitoring(self):
        """Arrête le monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Backup monitoring stopped")
    
    async def _monitoring_loop(self):
        """Boucle principale de monitoring"""
        try:
            while self.monitoring_active:
                await self._collect_and_process_metrics()
                await asyncio.sleep(self.config.collection_interval)
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
    
    async def _collect_and_process_metrics(self):
        """Collecte et traite les métriques"""
        try:
            collected_metrics = []
            
            # Métriques système
            if self.config.enable_system_metrics:
                system_stats = self.metrics_collector.collect_system_metrics()
                
                # Conversion en métriques
                system_metrics = [
                    Metric("system.cpu_usage", MetricType.GAUGE, system_stats.cpu_usage, unit="%"),
                    Metric("system.memory_usage", MetricType.GAUGE, system_stats.memory_usage, unit="%"),
                    Metric("system.disk_usage", MetricType.GAUGE, system_stats.disk_usage, unit="%"),
                ]
                
                collected_metrics.extend(system_metrics)
            
            # Métriques des objets monitorés
            for obj_ref in self.monitored_objects[:]:  # Copie pour éviter modification pendant itération
                obj = obj_ref()
                if obj is None:
                    # Objet supprimé, nettoyage référence
                    self.monitored_objects.remove(obj_ref)
                    continue
                
                obj_metrics = await self._collect_object_metrics(obj)
                collected_metrics.extend(obj_metrics)
            
            # Traitement par callbacks
            for callback in self.metric_callbacks:
                try:
                    callback(collected_metrics)
                except Exception as e:
                    logger.error(f"Metric callback failed: {e}")
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
    
    async def _collect_object_metrics(self, obj: Any) -> List[Metric]:
        """Collecte les métriques d'un objet spécifique"""
        metrics = []
        
        try:
            # BackupManager
            if hasattr(obj, 'get_backup_stats'):
                stats = obj.get_backup_stats()
                
                metrics.extend([
                    Metric("backup.total_backups", MetricType.COUNTER, stats.get("total_backups", 0)),
                    Metric("backup.successful_backups", MetricType.COUNTER, stats.get("successful_backups", 0)),
                    Metric("backup.failed_backups", MetricType.COUNTER, stats.get("failed_backups", 0)),
                    Metric("backup.total_size_gb", MetricType.GAUGE, stats.get("total_size_gb", 0), unit="GB"),
                    Metric("backup.average_duration", MetricType.GAUGE, stats.get("average_duration", 0), unit="s"),
                ])
                
                # Calcul taux d'échec
                total_backups = stats.get("total_backups", 0)
                failed_backups = stats.get("failed_backups", 0)
                
                if total_backups > 0:
                    failure_rate = (failed_backups / total_backups) * 100
                    metrics.append(Metric("backup.failure_rate", MetricType.GAUGE, failure_rate, unit="%"))
            
            # VerificationEngine
            if hasattr(obj, 'get_verification_stats'):
                stats = obj.get_verification_stats()
                
                metrics.extend([
                    Metric("verification.total_files", MetricType.COUNTER, stats.get("total_files_verified", 0)),
                    Metric("verification.corruption_detected", MetricType.COUNTER, stats.get("corruption_detected", 0)),
                    Metric("verification.success_rate", MetricType.GAUGE, stats.get("success_rate", 0), unit="%"),
                ])
            
            # RecoveryEngine
            if hasattr(obj, 'get_recovery_stats'):
                stats = obj.get_recovery_stats()
                
                metrics.extend([
                    Metric("recovery.total_recoveries", MetricType.COUNTER, stats.get("total_recoveries", 0)),
                    Metric("recovery.successful_recoveries", MetricType.COUNTER, stats.get("successful_recoveries", 0)),
                    Metric("recovery.active_recoveries", MetricType.GAUGE, stats.get("active_recoveries", 0)),
                ])
            
        except Exception as e:
            logger.error(f"Object metrics collection failed: {e}")
        
        return metrics
    
    def register_object(self, obj: Any):
        """
        Enregistre un objet pour monitoring
        
        Args:
            obj: Objet à monitorer
        """
        self.monitored_objects.append(weakref.ref(obj))
        logger.debug(f"Registered object for monitoring: {type(obj).__name__}")
    
    def add_metric_callback(self, callback: Callable[[List[Metric]], None]):
        """
        Ajoute un callback de traitement de métriques
        
        Args:
            callback: Function appelée avec les métriques
        """
        self.metric_callbacks.append(callback)
    
    def record_backup_event(
        self,
        event_type: str,
        backup_id: str,
        duration: Optional[float] = None,
        size: Optional[int] = None,
        success: bool = True
    ):
        """
        Enregistre un événement de sauvegarde
        
        Args:
            event_type: Type d'événement (started, completed, failed, etc.)
            backup_id: ID de la sauvegarde
            duration: Durée en secondes
            size: Taille en bytes
            success: Succès de l'opération
        """
        labels = {
            "event_type": event_type,
            "backup_id": backup_id,
            "success": str(success).lower()
        }
        
        # Événement
        self.metrics_collector.record_metric(
            "backup.events",
            1,
            MetricType.COUNTER,
            labels
        )
        
        # Durée si disponible
        if duration is not None:
            self.metrics_collector.record_metric(
                "backup.duration",
                duration,
                MetricType.TIMER,
                labels,
                unit="s"
            )
        
        # Taille si disponible
        if size is not None:
            self.metrics_collector.record_metric(
                "backup.size",
                size,
                MetricType.GAUGE,
                labels,
                unit="bytes"
            )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Récupère les données pour dashboard
        
        Returns:
            Dict[str, Any]: Données du dashboard
        """
        try:
            # Métriques récentes
            recent_metrics = {}
            
            for metric_name in ["system.cpu_usage", "system.memory_usage", "backup.failure_rate"]:
                history = self.metrics_collector.get_metric_history(
                    metric_name,
                    timedelta(hours=1)
                )
                
                if history:
                    recent_metrics[metric_name] = {
                        "current": history[-1].value,
                        "history": [{"timestamp": m.timestamp.isoformat(), "value": m.value} for m in history]
                    }
            
            # Alertes actives
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Statistiques agrégées
            aggregated_stats = {}
            for metric_name, stats in self.metrics_collector.aggregated_metrics.items():
                aggregated_stats[metric_name] = stats
            
            return {
                "timestamp": datetime.now().isoformat(),
                "recent_metrics": recent_metrics,
                "active_alerts": [alert.to_dict() for alert in active_alerts],
                "alert_counts": {
                    "critical": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
                    "error": len([a for a in active_alerts if a.level == AlertLevel.ERROR]),
                    "warning": len([a for a in active_alerts if a.level == AlertLevel.WARNING]),
                    "info": len([a for a in active_alerts if a.level == AlertLevel.INFO])
                },
                "aggregated_stats": aggregated_stats,
                "monitoring_status": {
                    "active": self.monitoring_active,
                    "monitored_objects": len(self.monitored_objects),
                    "collection_interval": self.config.collection_interval
                }
            }
            
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {e}")
            return {"error": str(e)}
    
    def export_monitoring_data(
        self,
        format: str = "json",
        duration: Optional[timedelta] = None
    ) -> str:
        """
        Exporte les données de monitoring
        
        Args:
            format: Format d'export
            duration: Durée à exporter
            
        Returns:
            str: Données exportées
        """
        try:
            if format == "json":
                return self._export_monitoring_json(duration)
            elif format == "prometheus":
                return self.metrics_collector.export_metrics("prometheus")
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Monitoring data export failed: {e}")
            return ""
    
    def _export_monitoring_json(self, duration: Optional[timedelta]) -> str:
        """Export complet au format JSON"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "config": self.config.to_dict(),
            "metrics": self.metrics_collector.export_metrics("json"),
            "active_alerts": [alert.to_dict() for alert in self.alert_manager.get_active_alerts()],
            "alert_history": [
                alert.to_dict() for alert in self.alert_manager.get_alert_history(
                    hours=duration.total_seconds() // 3600 if duration else 24
                )
            ]
        }
        
        return json.dumps(export_data, indent=2)
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques de monitoring
        
        Returns:
            Dict[str, Any]: Statistiques détaillées
        """
        return {
            "monitoring_active": self.monitoring_active,
            "collection_interval": self.config.collection_interval,
            "monitored_objects": len(self.monitored_objects),
            "total_metrics": sum(len(buffer) for buffer in self.metrics_collector.metrics_buffer.values()),
            "active_alerts": len(self.alert_manager.active_alerts),
            "total_alert_rules": len(self.alert_manager.alert_rules),
            "config": self.config.to_dict()
        }


# Export des classes principales
__all__ = [
    'BackupMonitor',
    'MetricsCollector',
    'AlertManager',
    'Metric',
    'Alert',
    'PerformanceStats',
    'MonitoringConfig',
    'AlertLevel',
    'MetricType'
]
