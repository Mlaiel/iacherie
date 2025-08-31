"""IA-Influencer-Agent - Event Metrics and Analytics System
Module: backend/core/events/event_metrics.py
Architecture: Advanced Event Analytics and Performance Monitoring
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
INTERDIT : Copie, reproduction, modification, ou usage sans autorisation écrite explicite.
Toute violation sera poursuivie selon la loi allemande et française.
Contact autorisations : mlaiel@live.de

Description:
    Système avancé de métriques et analytics pour les événements de la plateforme
    IA-Influencer-Agent. Monitoring temps réel, KPIs business et alertes intelligentes.
"""from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from collections import defaultdict, deque
import asyncio
import json
import logging
import statistics
import time
from abc import ABC, abstractmethod

import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry
import psutil

from .event_bus import Event, EventPriority, EventStatus
from .event_types import EventType

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types de métriques"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    CUSTOM = "custom"


class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AggregationPeriod(Enum):
    """Périodes d'agrégation"""    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"


@dataclass
class MetricValue:
    """Valeur de métrique avec timestamp"""    value: Union[int, float]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricDefinition:
    """Définition d'une métrique"""    name: str
    metric_type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    unit: str = ""
    buckets: Optional[List[float]] = None  # Pour histogrammes
    quantiles: Optional[List[float]] = None  # Pour summaries
    enabled: bool = True


@dataclass
class AlertRule:
    """Règle d'alerte"""    rule_id: str
    metric_name: str
    condition: str  # ex: "> 100", "< 0.95", "rate > 10/min"
    severity: AlertSeverity
    description: str
    duration: timedelta = timedelta(minutes=1)  # Durée avant déclenchement
    labels: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    cooldown: timedelta = timedelta(minutes=5)


@dataclass
class Alert:
    """Alerte générée"""    alert_id: str
    rule_id: str
    metric_name: str
    current_value: Union[int, float]
    threshold_value: Union[int, float]
    severity: AlertSeverity
    message: str
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricCollector(ABC):
    """Interface pour collecteurs de métriques"""    
    @abstractmethod
    async def collect(self) -> Dict[str, MetricValue]:
        """Collecte les métriques"""        pass
    
    @abstractmethod
    def get_definitions(self) -> List[MetricDefinition]:
        """Retourne les définitions de métriques"""        pass


class EventMetricsCollector(MetricCollector):
    """Collecteur de métriques pour les événements"""    
    def __init__(self):
        self.event_counts = defaultdict(int)
        self.event_durations = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.last_reset = datetime.now(timezone.utc)
        self.processing_times = deque(maxlen=1000)
        
    async def collect(self) -> Dict[str, MetricValue]:
        """Collecte les métriques d'événements"""        now = datetime.now(timezone.utc)
        metrics = {}
        
        # Compteurs d'événements par type
        for event_type, count in self.event_counts.items():
            metrics[f"events_total_{event_type}"] = MetricValue(
                value=count,
                labels={"type": event_type}
            )
        
        # Durées moyennes de traitement
        for event_type, durations in self.event_durations.items():
            if durations:
                avg_duration = statistics.mean(durations)
                metrics[f"event_duration_avg_{event_type}"] = MetricValue(
                    value=avg_duration,
                    labels={"type": event_type}
                )
        
        # Taux d'erreur
        total_events = sum(self.event_counts.values())
        total_errors = sum(self.error_counts.values())
        error_rate = (total_errors / total_events * 100) if total_events > 0 else 0
        
        metrics["event_error_rate"] = MetricValue(value=error_rate)
        
        # Débit d'événements (événements/seconde)
        time_diff = (now - self.last_reset).total_seconds()
        event_rate = total_events / time_diff if time_diff > 0 else 0
        metrics["event_rate"] = MetricValue(value=event_rate)
        
        # Temps de traitement récents
        if self.processing_times:
            metrics["event_processing_time_p50"] = MetricValue(
                value=statistics.median(self.processing_times)
            )
            metrics["event_processing_time_p95"] = MetricValue(
                value=statistics.quantiles(self.processing_times, n=20)[18]
            )
            metrics["event_processing_time_p99"] = MetricValue(
                value=statistics.quantiles(self.processing_times, n=100)[98]
            )
        
        return metrics
    
    def get_definitions(self) -> List[MetricDefinition]:
        """Définitions des métriques d'événements"""        return [
            MetricDefinition(
                name="events_total",
                metric_type=MetricType.COUNTER,
                description="Total number of events processed",
                labels=["type", "status"],
                unit="events"
            ),
            MetricDefinition(
                name="event_duration_avg",
                metric_type=MetricType.GAUGE,
                description="Average event processing duration",
                labels=["type"],
                unit="seconds"
            ),
            MetricDefinition(
                name="event_error_rate",
                metric_type=MetricType.GAUGE,
                description="Event processing error rate",
                unit="percentage"
            ),
            MetricDefinition(
                name="event_rate",
                metric_type=MetricType.GAUGE,
                description="Event processing rate",
                unit="events_per_second"
            ),
            MetricDefinition(
                name="event_processing_time",
                metric_type=MetricType.HISTOGRAM,
                description="Event processing time distribution",
                unit="seconds",
                buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
            )
        ]
    
    def record_event(self, event: Event, duration: Optional[float] = None):
        """Enregistre une métrique d'événement"""        self.event_counts[event.type] += 1
        
        if duration:
            self.event_durations[event.type].append(duration)
            self.processing_times.append(duration)
        
        if event.status == EventStatus.FAILED:
            self.error_counts[event.type] += 1


class SystemMetricsCollector(MetricCollector):
    """Collecteur de métriques système"""    
    async def collect(self) -> Dict[str, MetricValue]:
        """Collecte les métriques système"""        metrics = {}
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics["system_cpu_usage"] = MetricValue(value=cpu_percent)
        
        # Mémoire
        memory = psutil.virtual_memory()
        metrics["system_memory_usage"] = MetricValue(value=memory.percent)
        metrics["system_memory_available"] = MetricValue(value=memory.available)
        
        # Disque
        disk = psutil.disk_usage('/')
        metrics["system_disk_usage"] = MetricValue(value=disk.percent)
        metrics["system_disk_free"] = MetricValue(value=disk.free)
        
        # Réseau
        network = psutil.net_io_counters()
        metrics["system_network_bytes_sent"] = MetricValue(value=network.bytes_sent)
        metrics["system_network_bytes_recv"] = MetricValue(value=network.bytes_recv)
        
        # Processus
        process_count = len(psutil.pids())
        metrics["system_process_count"] = MetricValue(value=process_count)
        
        return metrics
    
    def get_definitions(self) -> List[MetricDefinition]:
        """Définitions des métriques système"""        return [
            MetricDefinition(
                name="system_cpu_usage",
                metric_type=MetricType.GAUGE,
                description="System CPU usage percentage",
                unit="percentage"
            ),
            MetricDefinition(
                name="system_memory_usage",
                metric_type=MetricType.GAUGE,
                description="System memory usage percentage",
                unit="percentage"
            ),
            MetricDefinition(
                name="system_disk_usage",
                metric_type=MetricType.GAUGE,
                description="System disk usage percentage",
                unit="percentage"
            ),
            MetricDefinition(
                name="system_network_bytes_sent",
                metric_type=MetricType.COUNTER,
                description="Total network bytes sent",
                unit="bytes"
            )
        ]


class BusinessMetricsCollector(MetricCollector):
    """Collecteur de métriques business pour IA-Influencer-Agent"""    
    def __init__(self):
        self.content_uploads = defaultdict(int)
        self.protection_violations = defaultdict(int)
        self.revenue_amounts = defaultdict(float)
        self.collaboration_matches = defaultdict(int)
        self.user_activities = defaultdict(int)
        
    async def collect(self) -> Dict[str, MetricValue]:
        """Collecte les métriques business"""        metrics = {}
        
        # Métriques de contenu
        total_uploads = sum(self.content_uploads.values())
        metrics["business_content_uploads_total"] = MetricValue(value=total_uploads)
        
        for content_type, count in self.content_uploads.items():
            metrics[f"business_content_uploads_{content_type}"] = MetricValue(
                value=count,
                labels={"content_type": content_type}
            )
        
        # Métriques de protection
        total_violations = sum(self.protection_violations.values())
        metrics["business_protection_violations_total"] = MetricValue(value=total_violations)
        
        for platform, count in self.protection_violations.items():
            metrics[f"business_protection_violations_{platform}"] = MetricValue(
                value=count,
                labels={"platform": platform}
            )
        
        # Métriques de monétisation
        total_revenue = sum(self.revenue_amounts.values())
        metrics["business_revenue_total"] = MetricValue(value=total_revenue)
        
        for currency, amount in self.revenue_amounts.items():
            metrics[f"business_revenue_{currency}"] = MetricValue(
                value=amount,
                labels={"currency": currency}
            )
        
        # Métriques de collaboration
        total_matches = sum(self.collaboration_matches.values())
        metrics["business_collaboration_matches_total"] = MetricValue(value=total_matches)
        
        # Métriques utilisateurs
        total_active_users = sum(self.user_activities.values())
        metrics["business_active_users_total"] = MetricValue(value=total_active_users)
        
        return metrics
    
    def get_definitions(self) -> List[MetricDefinition]:
        """Définitions des métriques business"""        return [
            MetricDefinition(
                name="business_content_uploads_total",
                metric_type=MetricType.COUNTER,
                description="Total content uploads",
                labels=["content_type", "user_tier"],
                unit="uploads"
            ),
            MetricDefinition(
                name="business_protection_violations_total",
                metric_type=MetricType.COUNTER,
                description="Total protection violations detected",
                labels=["platform", "severity"],
                unit="violations"
            ),
            MetricDefinition(
                name="business_revenue_total",
                metric_type=MetricType.GAUGE,
                description="Total revenue generated",
                labels=["currency", "platform"],
                unit="currency"
            ),
            MetricDefinition(
                name="business_collaboration_matches_total",
                metric_type=MetricType.COUNTER,
                description="Total collaboration matches",
                labels=["match_type"],
                unit="matches"
            ),
            MetricDefinition(
                name="business_active_users_total",
                metric_type=MetricType.GAUGE,
                description="Total active users",
                labels=["user_type", "subscription_tier"],
                unit="users"
            )
        ]
    
    def record_content_upload(self, content_type: str):
        """Enregistre un upload de contenu"""        self.content_uploads[content_type] += 1
    
    def record_protection_violation(self, platform: str):
        """Enregistre une violation de protection"""        self.protection_violations[platform] += 1
    
    def record_revenue(self, amount: float, currency: str):
        """Enregistre des revenus"""        self.revenue_amounts[currency] += amount
    
    def record_collaboration_match(self, match_type: str):
        """Enregistre un match de collaboration"""        self.collaboration_matches[match_type] += 1
    
    def record_user_activity(self, user_id: str):
        """Enregistre une activité utilisateur"""        self.user_activities[user_id] = int(time.time())


class AlertManager:
    """Gestionnaire d'alertes"""    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.callbacks: List[Callable[[Alert], None]] = []
        
    def add_rule(self, rule: AlertRule):
        """Ajoute une règle d'alerte"""        self.rules[rule.rule_id] = rule
        logger.info("Alert rule added: %s", rule.rule_id)
    
    def remove_rule(self, rule_id: str):
        """Supprime une règle d'alerte"""        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info("Alert rule removed: %s", rule_id)
    
    def add_callback(self, callback: Callable[[Alert], None]):
        """Ajoute un callback pour les alertes"""        self.callbacks.append(callback)
    
    async def evaluate_metrics(self, metrics: Dict[str, MetricValue]):
        """Évalue les métriques contre les règles d'alerte"""        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            metric_value = metrics.get(rule.metric_name)
            if not metric_value:
                continue
                
            should_alert = self._evaluate_condition(
                metric_value.value, rule.condition
            )
            
            if should_alert:
                await self._trigger_alert(rule, metric_value)
            else:
                await self._resolve_alert(rule.rule_id)
    
    def _evaluate_condition(self, value: Union[int, float], condition: str) -> bool:
        """Évalue une condition d'alerte"""        try:
            # Parse simple conditions like "> 100", "< 0.5", "== 0"
            if condition.startswith("> "):
                threshold = float(condition[2:])
                return value > threshold
            elif condition.startswith("< "):
                threshold = float(condition[2:])
                return value < threshold
            elif condition.startswith(">= "):
                threshold = float(condition[3:])
                return value >= threshold
            elif condition.startswith("<= "):
                threshold = float(condition[3:])
                return value <= threshold
            elif condition.startswith("== "):
                threshold = float(condition[3:])
                return value == threshold
            elif condition.startswith("!= "):
                threshold = float(condition[3:])
                return value != threshold
            else:
                logger.warning("Unsupported alert condition: %s", condition)
                return False
        except (ValueError, IndexError) as e:
            logger.error("Failed to evaluate condition '%s': %s", condition, e)
            return False
    
    async def _trigger_alert(self, rule: AlertRule, metric: MetricValue):
        """Déclenche une alerte"""        now = datetime.now(timezone.utc)
        
        # Vérification cooldown
        if (rule.last_triggered and 
            now - rule.last_triggered < rule.cooldown):
            return
        
        # Création de l'alerte
        alert_id = f"{rule.rule_id}_{int(now.timestamp())}"
        threshold = float(rule.condition.split()[-1])
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            metric_name=rule.metric_name,
            current_value=metric.value,
            threshold_value=threshold,
            severity=rule.severity,
            message=f"{rule.description}: {metric.value} {rule.condition}",
            labels=rule.labels.copy(),
            metadata=metric.metadata.copy()
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        rule.last_triggered = now
        
        logger.warning("Alert triggered: %s", alert.message)
        
        # Callbacks
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error("Alert callback failed: %s", e)
    
    async def _resolve_alert(self, rule_id: str):
        """Résout une alerte"""        alerts_to_resolve = [
            alert for alert in self.active_alerts.values()
            if alert.rule_id == rule_id and alert.resolved_at is None
        ]
        
        for alert in alerts_to_resolve:
            alert.resolved_at = datetime.now(timezone.utc)
            del self.active_alerts[alert.alert_id]
            logger.info("Alert resolved: %s", alert.alert_id)


class EventMetricsManager:
    """Gestionnaire principal des métriques d'événements"""    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        collection_interval: int = 60,
        retention_days: int = 30
    ):
        self.redis_client = redis_client
        self.collection_interval = collection_interval
        self.retention_days = retention_days
        
        # Collecteurs
        self.collectors: Dict[str, MetricCollector] = {}
        self.event_collector = EventMetricsCollector()
        self.system_collector = SystemMetricsCollector()
        self.business_collector = BusinessMetricsCollector()
        
        # Métriques en cours
        self.current_metrics: Dict[str, MetricValue] = {}
        self.historical_metrics: Dict[str, List[MetricValue]] = defaultdict(list)
        
        # Alertes
        self.alert_manager = AlertManager()
        
        # Prometheus registry
        self.prometheus_registry = CollectorRegistry()
        self.prometheus_metrics: Dict[str, Any] = {}
        
        # État
        self._collecting = False
        self._collection_task: Optional[asyncio.Task] = None
        
        logger.info("EventMetricsManager initialized")
    
    async def start(self):
        """Démarre la collecte de métriques"""        if self._collecting:
            return
        
        # Enregistrement des collecteurs par défaut
        self.register_collector("events", self.event_collector)
        self.register_collector("system", self.system_collector)
        self.register_collector("business", self.business_collector)
        
        # Configuration des alertes par défaut
        self._setup_default_alerts()
        
        # Démarrage de la collecte
        self._collecting = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        
        logger.info("EventMetricsManager started")
    
    async def stop(self):
        """Arrête la collecte de métriques"""        self._collecting = False
        
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("EventMetricsManager stopped")
    
    def register_collector(self, name: str, collector: MetricCollector):
        """Enregistre un collecteur de métriques"""        self.collectors[name] = collector
        
        # Enregistrement des métriques Prometheus
        for definition in collector.get_definitions():
            self._register_prometheus_metric(definition)
        
        logger.info("Metric collector registered: %s", name)
    
    def _register_prometheus_metric(self, definition: MetricDefinition):
        """Enregistre une métrique Prometheus"""        metric_name = f"ia_influencer_{definition.name}"
        
        if definition.metric_type == MetricType.COUNTER:
            metric = Counter(
                metric_name,
                definition.description,
                labelnames=definition.labels,
                registry=self.prometheus_registry
            )
        elif definition.metric_type == MetricType.GAUGE:
            metric = Gauge(
                metric_name,
                definition.description,
                labelnames=definition.labels,
                registry=self.prometheus_registry
            )
        elif definition.metric_type == MetricType.HISTOGRAM:
            metric = Histogram(
                metric_name,
                definition.description,
                labelnames=definition.labels,
                buckets=definition.buckets or [0.1, 0.5, 1, 2.5, 5, 10],
                registry=self.prometheus_registry
            )
        elif definition.metric_type == MetricType.SUMMARY:
            metric = Summary(
                metric_name,
                definition.description,
                labelnames=definition.labels,
                registry=self.prometheus_registry
            )
        else:
            return
        
        self.prometheus_metrics[definition.name] = metric
    
    def _setup_default_alerts(self):
        """Configure les alertes par défaut"""        default_rules = [
            AlertRule(
                rule_id="high_error_rate",
                metric_name="event_error_rate",
                condition="> 5.0",
                severity=AlertSeverity.WARNING,
                description="Event error rate too high"
            ),
            AlertRule(
                rule_id="critical_error_rate",
                metric_name="event_error_rate",
                condition="> 10.0",
                severity=AlertSeverity.CRITICAL,
                description="Event error rate critical"
            ),
            AlertRule(
                rule_id="high_cpu_usage",
                metric_name="system_cpu_usage",
                condition="> 80.0",
                severity=AlertSeverity.WARNING,
                description="High CPU usage"
            ),
            AlertRule(
                rule_id="low_memory",
                metric_name="system_memory_usage",
                condition="> 90.0",
                severity=AlertSeverity.CRITICAL,
                description="Low memory available"
            ),
            AlertRule(
                rule_id="protection_violations_spike",
                metric_name="business_protection_violations_total",
                condition="> 100",
                severity=AlertSeverity.WARNING,
                description="High number of protection violations"
            )
        ]
        
        for rule in default_rules:
            self.alert_manager.add_rule(rule)
    
    async def _collection_loop(self):
        """Boucle principale de collecte"""        while self._collecting:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in metrics collection loop: %s", e)
                await asyncio.sleep(5)  # Retry delay
    
    async def _collect_all_metrics(self):
        """Collecte toutes les métriques"""        all_metrics = {}
        
        # Collecte depuis tous les collecteurs
        for name, collector in self.collectors.items():
            try:
                metrics = await collector.collect()
                all_metrics.update(metrics)
            except Exception as e:
                logger.error("Failed to collect metrics from %s: %s", name, e)
        
        # Mise à jour des métriques courantes
        self.current_metrics.update(all_metrics)
        
        # Stockage historique
        now = datetime.now(timezone.utc)
        for metric_name, metric_value in all_metrics.items():
            self.historical_metrics[metric_name].append(metric_value)
            
            # Nettoyage des anciennes métriques
            cutoff = now - timedelta(days=self.retention_days)
            self.historical_metrics[metric_name] = [
                m for m in self.historical_metrics[metric_name]
                if m.timestamp > cutoff
            ]
        
        # Mise à jour Prometheus
        self._update_prometheus_metrics(all_metrics)
        
        # Évaluation des alertes
        await self.alert_manager.evaluate_metrics(all_metrics)
        
        # Persistance Redis si disponible
        if self.redis_client:
            await self._persist_metrics(all_metrics)
    
    def _update_prometheus_metrics(self, metrics: Dict[str, MetricValue]):
        """Met à jour les métriques Prometheus"""        for metric_name, metric_value in metrics.items():
            prometheus_metric = self.prometheus_metrics.get(metric_name)
            if not prometheus_metric:
                continue
            
            try:
                if isinstance(prometheus_metric, Counter):
                    # Pour les compteurs, on observe la différence
                    prometheus_metric.inc(metric_value.value)
                elif isinstance(prometheus_metric, Gauge):
                    prometheus_metric.set(metric_value.value)
                elif isinstance(prometheus_metric, Histogram):
                    prometheus_metric.observe(metric_value.value)
                elif isinstance(prometheus_metric, Summary):
                    prometheus_metric.observe(metric_value.value)
            except Exception as e:
                logger.error("Failed to update Prometheus metric %s: %s", metric_name, e)
    
    async def _persist_metrics(self, metrics: Dict[str, MetricValue]):
        """Persiste les métriques dans Redis"""        try:
            pipe = self.redis_client.pipeline()
            timestamp = int(time.time())
            
            for metric_name, metric_value in metrics.items():
                key = f"metrics:{metric_name}:{timestamp}"
                data = {
                    "value": metric_value.value,
                    "timestamp": metric_value.timestamp.isoformat(),
                    "labels": json.dumps(metric_value.labels),
                    "metadata": json.dumps(metric_value.metadata)
                }
                pipe.hset(key, mapping=data)
                pipe.expire(key, self.retention_days * 24 * 3600)
            
            await pipe.execute()
        except Exception as e:
            logger.error("Failed to persist metrics to Redis: %s", e)
    
    def record_event_metric(self, event: Event, duration: Optional[float] = None):
        """Enregistre une métrique d'événement"""        self.event_collector.record_event(event, duration)
        
        # Métriques business selon le type d'événement
        if event.type.startswith("content.uploaded"):
            content_type = event.data.get("content_type", "unknown")
            self.business_collector.record_content_upload(content_type)
        elif event.type.startswith("protection.violation"):
            platform = event.data.get("platform", "unknown")
            self.business_collector.record_protection_violation(platform)
        elif event.type.startswith("monetization.revenue"):
            amount = event.data.get("revenue_amount", 0)
            currency = event.data.get("currency", "EUR")
            self.business_collector.record_revenue(amount, currency)
        elif event.type.startswith("collaboration.matching"):
            match_type = event.data.get("match_type", "general")
            self.business_collector.record_collaboration_match(match_type)
        
        if event.user_id:
            self.business_collector.record_user_activity(event.user_id)
    
    def get_current_metrics(self) -> Dict[str, MetricValue]:
        """Retourne les métriques courantes"""        return self.current_metrics.copy()
    
    def get_historical_metrics(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MetricValue]:
        """Retourne les métriques historiques"""        metrics = self.historical_metrics.get(metric_name, [])
        
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        
        return metrics
    
    def get_active_alerts(self) -> List[Alert]:
        """Retourne les alertes actives"""        return list(self.alert_manager.active_alerts.values())
    
    def get_alert_history(
        self,
        limit: int = 100,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Retourne l'historique des alertes"""        alerts = self.alert_manager.alert_history
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: a.triggered_at, reverse=True)[:limit]
    
    def add_alert_rule(self, rule: AlertRule):
        """Ajoute une règle d'alerte"""        self.alert_manager.add_rule(rule)
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Ajoute un callback d'alerte"""        self.alert_manager.add_callback(callback)


# Instance globale
event_metrics_manager = EventMetricsManager()
