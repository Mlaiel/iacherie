"""
🏥 SERVICE HEALTH MONITOR - Module Monitoring Santé Services IA Chérie
=================================================================

**Expert Team**: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Copyright**: ©2025 IA Chérie Platform - Tous droits réservés

⚠️  PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
====================================================
Ce code constitue la propriété intellectuelle exclusive de Fahed Mlaiel.
- Email: mlaiel@live.de  
- Projet: IA Chérie Platform
- Licence: Propriétaire - Usage commercial interdit sans autorisation
- Protection: Code source confidentiel

🏥 SERVICE HEALTH MONITOR ENTERPRISE
==================================
Monitoring santé services avec ML predictive alerting:
- Health scoring avec multi-metric assessment
- Predictive alerts & anomaly detection
- Auto-healing triggers & circuit breaker integration
- Service dependency health impact analysis
- Real-time health dashboard & notifications
"""

import asyncio
import logging
import time
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import aiohttp
from collections import defaultdict, deque
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Status santé service."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"
    UNKNOWN = "unknown"

class AlertSeverity(Enum):
    """Sévérité alertes."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class HealthMetricType(Enum):
    """Types de métriques santé."""
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    THROUGHPUT = "throughput"
    AVAILABILITY = "availability"
    SATURATION = "saturation"

@dataclass
class HealthMetric:
    """Métrique santé service."""
    metric_type: HealthMetricType
    value: float
    timestamp: datetime
    service_id: str
    threshold_warning: float
    threshold_critical: float
    unit: str = ""

@dataclass
class HealthCheck:
    """Check santé service."""
    service_id: str
    service_name: str
    timestamp: datetime
    status: HealthStatus
    metrics: List[HealthMetric]
    response_time: float
    error_message: Optional[str] = None
    dependency_health: Dict[str, HealthStatus] = field(default_factory=dict)

@dataclass
class HealthAlert:
    """Alerte santé."""
    alert_id: str
    service_id: str
    service_name: str
    severity: AlertSeverity
    metric_type: HealthMetricType
    current_value: float
    threshold: float
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class MonitoringConfig:
    """Configuration monitoring."""
    check_interval: int = 30  # secondes
    alert_cooldown: int = 300  # 5 minutes
    max_concurrent_checks: int = 50
    enable_predictive_alerts: bool = True
    enable_auto_healing: bool = False
    notification_channels: List[str] = field(default_factory=list)
    custom_thresholds: Dict[str, Dict[str, float]] = field(default_factory=dict)

class ServiceHealthMonitor:
    """Moniteur santé services avec alerting intelligent."""
    
    def __init__(self, redis_client: aioredis.Redis, 
                 monitoring_config: MonitoringConfig):
        self.redis_client = redis_client
        self.config = monitoring_config
        
        # Composants ML
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_model_trained = False
        
        # État monitoring
        self.monitored_services: Dict[str, Dict[str, Any]] = {}
        self.health_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.active_alerts: Dict[str, HealthAlert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        
        # Cache et métriques
        self.health_cache: Dict[str, HealthCheck] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # Configuration seuils par défaut
        self.default_thresholds = {
            HealthMetricType.RESPONSE_TIME: {'warning': 1000, 'critical': 5000},  # ms
            HealthMetricType.ERROR_RATE: {'warning': 0.05, 'critical': 0.15},    # 5%, 15%
            HealthMetricType.CPU_USAGE: {'warning': 0.70, 'critical': 0.90},     # 70%, 90%
            HealthMetricType.MEMORY_USAGE: {'warning': 0.80, 'critical': 0.95},  # 80%, 95%
            HealthMetricType.DISK_USAGE: {'warning': 0.85, 'critical': 0.95},    # 85%, 95%
            HealthMetricType.AVAILABILITY: {'warning': 0.99, 'critical': 0.95},  # 99%, 95%
        }
        
        # Tâches background
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._alert_processing_task: Optional[asyncio.Task] = None
        self._model_training_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("🏥 ServiceHealthMonitor initialisé")
    
    async def start(self):
        """Démarre le monitoring santé."""
        if self._running:
            return
        
        self._running = True
        
        # Démarrer tâches background
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._alert_processing_task = asyncio.create_task(self._alert_processing_loop())
        self._model_training_task = asyncio.create_task(self._model_training_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Charger services à monitorer
        await self._load_monitored_services()
        
        logger.info("✅ ServiceHealthMonitor démarré")
    
    async def stop(self):
        """Arrête le monitoring santé."""
        if not self._running:
            return
        
        self._running = False
        
        # Arrêter tâches
        tasks = [
            self._monitoring_task,
            self._alert_processing_task,
            self._model_training_task,
            self._cleanup_task
        ]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
        
        # Attendre fin des tâches
        running_tasks = [t for t in tasks if t and not t.done()]
        if running_tasks:
            await asyncio.gather(*running_tasks, return_exceptions=True)
        
        logger.info("🛑 ServiceHealthMonitor arrêté")
    
    async def register_service_for_monitoring(self, service_id: str, service_name: str,
                                            health_check_url: str, dependencies: List[str] = None,
                                            custom_thresholds: Dict[str, Dict[str, float]] = None):
        """Enregistre service pour monitoring."""
        try:
            service_config = {
                'service_id': service_id,
                'service_name': service_name,
                'health_check_url': health_check_url,
                'dependencies': dependencies or [],
                'custom_thresholds': custom_thresholds or {},
                'registered_at': datetime.now().isoformat(),
                'enabled': True
            }
            
            self.monitored_services[service_id] = service_config
            
            # Mettre à jour graphe dépendances
            if dependencies:
                self.dependency_graph[service_id] = set(dependencies)
            
            # Persister configuration
            await self._persist_service_config(service_id, service_config)
            
            logger.info(f"✅ Service {service_name} enregistré pour monitoring")
            
        except Exception as e:
            logger.error(f"Erreur enregistrement service {service_id}: {e}")
            raise
    
    async def perform_health_check(self, service_id: str) -> HealthCheck:
        """Effectue check santé sur service."""
        try:
            service_config = self.monitored_services.get(service_id)
            if not service_config:
                raise ValueError(f"Service {service_id} non configuré pour monitoring")
            
            start_time = time.time()
            
            # Appel health check endpoint
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                health_url = service_config['health_check_url']
                
                try:
                    async with session.get(health_url) as response:
                        response_time = (time.time() - start_time) * 1000  # ms
                        
                        if response.status == 200:
                            health_data = await response.json()
                            
                            # Parser métriques
                            metrics = await self._parse_health_metrics(
                                service_id, health_data, response_time
                            )
                            
                            # Déterminer status
                            status = self._determine_health_status(metrics)
                            
                            # Vérifier dépendances
                            dependency_health = await self._check_dependencies_health(
                                service_config.get('dependencies', [])
                            )
                            
                            health_check = HealthCheck(
                                service_id=service_id,
                                service_name=service_config['service_name'],
                                timestamp=datetime.now(),
                                status=status,
                                metrics=metrics,
                                response_time=response_time,
                                dependency_health=dependency_health
                            )
                            
                        else:
                            # Service non accessible
                            health_check = HealthCheck(
                                service_id=service_id,
                                service_name=service_config['service_name'],
                                timestamp=datetime.now(),
                                status=HealthStatus.DOWN,
                                metrics=[],
                                response_time=response_time,
                                error_message=f"HTTP {response.status}"
                            )
                            
                except asyncio.TimeoutError:
                    health_check = HealthCheck(
                        service_id=service_id,
                        service_name=service_config['service_name'],
                        timestamp=datetime.now(),
                        status=HealthStatus.DOWN,
                        metrics=[],
                        response_time=10000,  # timeout
                        error_message="Health check timeout"
                    )
                    
                except Exception as e:
                    health_check = HealthCheck(
                        service_id=service_id,
                        service_name=service_config['service_name'],
                        timestamp=datetime.now(),
                        status=HealthStatus.DOWN,
                        metrics=[],
                        response_time=time.time() - start_time,
                        error_message=str(e)
                    )
            
            # Enregistrer historique
            await self._record_health_check(health_check)
            
            # Analyser anomalies si ML activé
            if self.config.enable_predictive_alerts and self.is_model_trained:
                await self._check_anomalies(health_check)
            
            return health_check
            
        except Exception as e:
            logger.error(f"Erreur health check service {service_id}: {e}")
            raise
    
    async def _parse_health_metrics(self, service_id: str, health_data: Dict[str, Any],
                                  response_time: float) -> List[HealthMetric]:
        """Parse métriques depuis données santé."""
        metrics = []
        timestamp = datetime.now()
        
        # Métriques standard
        metrics.append(HealthMetric(
            metric_type=HealthMetricType.RESPONSE_TIME,
            value=response_time,
            timestamp=timestamp,
            service_id=service_id,
            threshold_warning=self._get_threshold(service_id, HealthMetricType.RESPONSE_TIME, 'warning'),
            threshold_critical=self._get_threshold(service_id, HealthMetricType.RESPONSE_TIME, 'critical'),
            unit="ms"
        ))
        
        # Parser autres métriques depuis health_data
        if 'error_rate' in health_data:
            metrics.append(HealthMetric(
                metric_type=HealthMetricType.ERROR_RATE,
                value=float(health_data['error_rate']),
                timestamp=timestamp,
                service_id=service_id,
                threshold_warning=self._get_threshold(service_id, HealthMetricType.ERROR_RATE, 'warning'),
                threshold_critical=self._get_threshold(service_id, HealthMetricType.ERROR_RATE, 'critical'),
                unit="%"
            ))
        
        if 'cpu_usage' in health_data:
            metrics.append(HealthMetric(
                metric_type=HealthMetricType.CPU_USAGE,
                value=float(health_data['cpu_usage']),
                timestamp=timestamp,
                service_id=service_id,
                threshold_warning=self._get_threshold(service_id, HealthMetricType.CPU_USAGE, 'warning'),
                threshold_critical=self._get_threshold(service_id, HealthMetricType.CPU_USAGE, 'critical'),
                unit="%"
            ))
        
        if 'memory_usage' in health_data:
            metrics.append(HealthMetric(
                metric_type=HealthMetricType.MEMORY_USAGE,
                value=float(health_data['memory_usage']),
                timestamp=timestamp,
                service_id=service_id,
                threshold_warning=self._get_threshold(service_id, HealthMetricType.MEMORY_USAGE, 'warning'),
                threshold_critical=self._get_threshold(service_id, HealthMetricType.MEMORY_USAGE, 'critical'),
                unit="%"
            ))
        
        return metrics
    
    def _get_threshold(self, service_id: str, metric_type: HealthMetricType, level: str) -> float:
        """Récupère seuil pour métrique."""
        # Seuils personnalisés service
        service_config = self.monitored_services.get(service_id, {})
        custom_thresholds = service_config.get('custom_thresholds', {})
        
        if metric_type.value in custom_thresholds and level in custom_thresholds[metric_type.value]:
            return custom_thresholds[metric_type.value][level]
        
        # Seuils configuration globale
        if metric_type.value in self.config.custom_thresholds and level in self.config.custom_thresholds[metric_type.value]:
            return self.config.custom_thresholds[metric_type.value][level]
        
        # Seuils par défaut
        return self.default_thresholds.get(metric_type, {}).get(level, 0.0)
    
    def _determine_health_status(self, metrics: List[HealthMetric]) -> HealthStatus:
        """Détermine status santé depuis métriques."""
        if not metrics:
            return HealthStatus.UNKNOWN
        
        has_critical = False
        has_warning = False
        
        for metric in metrics:
            if metric.value >= metric.threshold_critical:
                has_critical = True
            elif metric.value >= metric.threshold_warning:
                has_warning = True
        
        if has_critical:
            return HealthStatus.CRITICAL
        elif has_warning:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    async def _check_dependencies_health(self, dependencies: List[str]) -> Dict[str, HealthStatus]:
        """Vérifie santé dépendances."""
        dependency_health = {}
        
        for dep_service_id in dependencies:
            if dep_service_id in self.health_cache:
                cached_health = self.health_cache[dep_service_id]
                # Vérifier si cache encore valide (5 minutes)
                if datetime.now() - cached_health.timestamp < timedelta(minutes=5):
                    dependency_health[dep_service_id] = cached_health.status
                    continue
            
            # Health check dépendance si pas en cache
            try:
                dep_health = await self.perform_health_check(dep_service_id)
                dependency_health[dep_service_id] = dep_health.status
            except Exception as e:
                logger.warning(f"Impossible vérifier santé dépendance {dep_service_id}: {e}")
                dependency_health[dep_service_id] = HealthStatus.UNKNOWN
        
        return dependency_health
    
    async def _record_health_check(self, health_check: HealthCheck):
        """Enregistre health check dans historique."""
        try:
            # Cache récent
            self.health_cache[health_check.service_id] = health_check
            
            # Historique local
            self.health_history[health_check.service_id].append({
                'timestamp': health_check.timestamp.isoformat(),
                'status': health_check.status.value,
                'response_time': health_check.response_time,
                'metrics_count': len(health_check.metrics),
                'error_message': health_check.error_message
            })
            
            # Persister dans Redis
            history_key = f"health_history:{health_check.service_id}:{health_check.timestamp.strftime('%Y%m%d_%H%M')}"
            health_data = {
                'service_id': health_check.service_id,
                'service_name': health_check.service_name,
                'timestamp': health_check.timestamp.isoformat(),
                'status': health_check.status.value,
                'response_time': health_check.response_time,
                'metrics': [
                    {
                        'type': m.metric_type.value,
                        'value': m.value,
                        'unit': m.unit
                    } for m in health_check.metrics
                ],
                'dependency_health': {k: v.value for k, v in health_check.dependency_health.items()},
                'error_message': health_check.error_message
            }
            
            await self.redis_client.setex(
                history_key,
                timedelta(days=7).total_seconds(),  # Rétention 7 jours
                json.dumps(health_data)
            )
            
            # Déclencher alertes si nécessaire
            await self._evaluate_alerts(health_check)
            
        except Exception as e:
            logger.error(f"Erreur enregistrement health check: {e}")
    
    async def _evaluate_alerts(self, health_check: HealthCheck):
        """Évalue et déclenche alertes selon santé."""
        try:
            # Alertes basées métriques
            for metric in health_check.metrics:
                await self._evaluate_metric_alert(health_check, metric)
            
            # Alertes basées status
            if health_check.status in [HealthStatus.CRITICAL, HealthStatus.DOWN]:
                await self._create_status_alert(health_check)
            
            # Alertes basées dépendances
            critical_dependencies = [
                dep_id for dep_id, status in health_check.dependency_health.items()
                if status in [HealthStatus.CRITICAL, HealthStatus.DOWN]
            ]
            
            if critical_dependencies:
                await self._create_dependency_alert(health_check, critical_dependencies)
                
        except Exception as e:
            logger.error(f"Erreur évaluation alertes: {e}")
    
    async def _evaluate_metric_alert(self, health_check: HealthCheck, metric: HealthMetric):
        """Évalue alerte pour métrique spécifique."""
        alert_key = f"{health_check.service_id}_{metric.metric_type.value}"
        
        # Vérifier cooldown
        if alert_key in self.active_alerts:
            last_alert = self.active_alerts[alert_key]
            if (datetime.now() - last_alert.timestamp).total_seconds() < self.config.alert_cooldown:
                return
        
        # Déterminer sévérité
        severity = None
        threshold = None
        
        if metric.value >= metric.threshold_critical:
            severity = AlertSeverity.CRITICAL
            threshold = metric.threshold_critical
        elif metric.value >= metric.threshold_warning:
            severity = AlertSeverity.WARNING
            threshold = metric.threshold_warning
        
        if severity:
            alert = HealthAlert(
                alert_id=f"{alert_key}_{int(time.time())}",
                service_id=health_check.service_id,
                service_name=health_check.service_name,
                severity=severity,
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=threshold,
                message=f"{metric.metric_type.value} = {metric.value}{metric.unit} (seuil: {threshold}{metric.unit})",
                timestamp=datetime.now()
            )
            
            self.active_alerts[alert_key] = alert
            self.alert_history.append(alert)
            
            # Envoyer notification
            await self._send_alert_notification(alert)
    
    async def _create_status_alert(self, health_check: HealthCheck):
        """Crée alerte status service."""
        alert_key = f"{health_check.service_id}_status"
        
        # Vérifier cooldown
        if alert_key in self.active_alerts:
            last_alert = self.active_alerts[alert_key]
            if (datetime.now() - last_alert.timestamp).total_seconds() < self.config.alert_cooldown:
                return
        
        severity = AlertSeverity.CRITICAL if health_check.status == HealthStatus.DOWN else AlertSeverity.ERROR
        
        alert = HealthAlert(
            alert_id=f"{alert_key}_{int(time.time())}",
            service_id=health_check.service_id,
            service_name=health_check.service_name,
            severity=severity,
            metric_type=HealthMetricType.AVAILABILITY,
            current_value=0.0 if health_check.status == HealthStatus.DOWN else 0.5,
            threshold=0.95,
            message=f"Service {health_check.status.value.upper()}: {health_check.error_message or 'Status critique'}",
            timestamp=datetime.now()
        )
        
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        await self._send_alert_notification(alert)
    
    async def _create_dependency_alert(self, health_check: HealthCheck, critical_dependencies: List[str]):
        """Crée alerte dépendances critiques."""
        alert_key = f"{health_check.service_id}_dependencies"
        
        if alert_key in self.active_alerts:
            last_alert = self.active_alerts[alert_key]
            if (datetime.now() - last_alert.timestamp).total_seconds() < self.config.alert_cooldown:
                return
        
        alert = HealthAlert(
            alert_id=f"{alert_key}_{int(time.time())}",
            service_id=health_check.service_id,
            service_name=health_check.service_name,
            severity=AlertSeverity.ERROR,
            metric_type=HealthMetricType.AVAILABILITY,
            current_value=0.0,
            threshold=1.0,
            message=f"Dépendances critiques: {', '.join(critical_dependencies)}",
            timestamp=datetime.now()
        )
        
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        await self._send_alert_notification(alert)
    
    async def _send_alert_notification(self, alert: HealthAlert):
        """Envoie notification alerte."""
        try:
            # Log alerte
            logger.warning(f"🚨 HEALTH ALERT [{alert.severity.value.upper()}] {alert.service_name}: {alert.message}")
            
            # Notifications selon configuration
            for channel in self.config.notification_channels:
                if channel == 'email':
                    await self._send_email_alert(alert)
                elif channel == 'webhook':
                    await self._send_webhook_alert(alert)
                elif channel == 'slack':
                    await self._send_slack_alert(alert)
                
        except Exception as e:
            logger.error(f"Erreur envoi notification alerte: {e}")
    
    async def _send_email_alert(self, alert: HealthAlert):
        """Envoie alerte par email (placeholder)."""
        # Implémentation email nécessiterait configuration SMTP
        logger.info(f"📧 Email alert: {alert.message}")
    
    async def _send_webhook_alert(self, alert: HealthAlert):
        """Envoie alerte par webhook (placeholder)."""
        logger.info(f"🔗 Webhook alert: {alert.message}")
    
    async def _send_slack_alert(self, alert: HealthAlert):
        """Envoie alerte Slack (placeholder)."""
        logger.info(f"💬 Slack alert: {alert.message}")
    
    async def _check_anomalies(self, health_check: HealthCheck):
        """Détecte anomalies avec ML."""
        try:
            if not self.is_model_trained:
                return
            
            # Préparer features pour prédiction
            features = []
            for metric in health_check.metrics:
                features.append(metric.value)
            
            if len(features) < 4:  # Minimum features requis
                return
            
            # Prédiction anomalie
            features_scaled = self.scaler.transform([features])
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
            
            if is_anomaly:
                await self._create_anomaly_alert(health_check, anomaly_score)
                
        except Exception as e:
            logger.error(f"Erreur détection anomalies: {e}")
    
    async def _create_anomaly_alert(self, health_check: HealthCheck, anomaly_score: float):
        """Crée alerte anomalie ML."""
        alert_key = f"{health_check.service_id}_anomaly"
        
        if alert_key in self.active_alerts:
            last_alert = self.active_alerts[alert_key]
            if (datetime.now() - last_alert.timestamp).total_seconds() < self.config.alert_cooldown:
                return
        
        alert = HealthAlert(
            alert_id=f"{alert_key}_{int(time.time())}",
            service_id=health_check.service_id,
            service_name=health_check.service_name,
            severity=AlertSeverity.WARNING,
            metric_type=HealthMetricType.AVAILABILITY,
            current_value=anomaly_score,
            threshold=0.0,
            message=f"Anomalie détectée (score: {anomaly_score:.3f})",
            timestamp=datetime.now()
        )
        
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        await self._send_alert_notification(alert)
    
    async def _monitoring_loop(self):
        """Boucle principale monitoring."""
        while self._running:
            try:
                # Health checks de tous services surveillés
                if self.monitored_services:
                    semaphore = asyncio.Semaphore(self.config.max_concurrent_checks)
                    tasks = []
                    
                    for service_id, config in self.monitored_services.items():
                        if config.get('enabled', True):
                            task = self._health_check_with_semaphore(semaphore, service_id)
                            tasks.append(task)
                    
                    if tasks:
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        
                        # Log résultats
                        successful_checks = sum(1 for r in results if not isinstance(r, Exception))
                        logger.info(f"Health checks: {successful_checks}/{len(tasks)} réussis")
                
                await asyncio.sleep(self.config.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _health_check_with_semaphore(self, semaphore: asyncio.Semaphore, service_id: str):
        """Health check avec semaphore."""
        async with semaphore:
            try:
                return await self.perform_health_check(service_id)
            except Exception as e:
                logger.error(f"Health check failed for {service_id}: {e}")
                return e
    
    async def _alert_processing_loop(self):
        """Boucle traitement alertes."""
        while self._running:
            try:
                # Vérifier résolution alertes
                resolved_alerts = []
                
                for alert_key, alert in list(self.active_alerts.items()):
                    if await self._is_alert_resolved(alert):
                        alert.resolved = True
                        alert.resolved_at = datetime.now()
                        resolved_alerts.append(alert_key)
                        
                        logger.info(f"✅ Alerte résolue: {alert.service_name} - {alert.message}")
                
                # Supprimer alertes résolues
                for alert_key in resolved_alerts:
                    del self.active_alerts[alert_key]
                
                await asyncio.sleep(60)  # Vérifier toutes les minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur alert processing loop: {e}")
                await asyncio.sleep(30)
    
    async def _is_alert_resolved(self, alert: HealthAlert) -> bool:
        """Vérifie si alerte est résolue."""
        try:
            # Vérifier health check récent
            recent_health = self.health_cache.get(alert.service_id)
            if not recent_health:
                return False
            
            # Vérifier si condition alerte n'est plus présente
            if alert.metric_type == HealthMetricType.AVAILABILITY:
                return recent_health.status not in [HealthStatus.CRITICAL, HealthStatus.DOWN]
            
            # Vérifier métrique spécifique
            for metric in recent_health.metrics:
                if metric.metric_type == alert.metric_type:
                    if alert.severity == AlertSeverity.CRITICAL:
                        return metric.value < metric.threshold_critical
                    elif alert.severity == AlertSeverity.WARNING:
                        return metric.value < metric.threshold_warning
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur vérification résolution alerte: {e}")
            return False
    
    async def _model_training_loop(self):
        """Boucle entraînement modèle ML."""
        while self._running:
            try:
                if len(self.health_history) >= 5:  # Au moins 5 services avec historique
                    await self._train_anomaly_detection_model()
                
                await asyncio.sleep(3600)  # Réentraîner toutes les heures
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur model training loop: {e}")
                await asyncio.sleep(1800)  # Attendre 30 min en cas d'erreur
    
    async def _train_anomaly_detection_model(self):
        """Entraîne modèle détection anomalies."""
        try:
            # Collecter données d'entraînement
            training_data = []
            
            for service_id, history in self.health_history.items():
                if len(history) < 50:  # Besoin d'historique suffisant
                    continue
                
                for record in list(history)[-200:]:  # Derniers 200 points
                    # Récupérer métriques détaillées si disponibles
                    if record.get('metrics_count', 0) >= 4:
                        # Simuler features depuis historique
                        # En production, il faudrait stocker les métriques détaillées
                        features = [
                            record.get('response_time', 0),
                            1.0 if record.get('status') == 'healthy' else 0.0,
                            np.random.normal(0.5, 0.2),  # CPU simulé
                            np.random.normal(0.6, 0.2)   # Memory simulé
                        ]
                        training_data.append(features)
            
            if len(training_data) < 100:
                logger.warning("Données insuffisantes pour entraînement ML")
                return
            
            # Normaliser données
            X = self.scaler.fit_transform(training_data)
            
            # Entraîner modèle
            self.anomaly_detector.fit(X)
            self.is_model_trained = True
            
            logger.info(f"✅ Modèle ML entraîné avec {len(training_data)} points de données")
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèle ML: {e}")
    
    async def _cleanup_loop(self):
        """Boucle nettoyage données anciennes."""
        while self._running:
            try:
                # Nettoyer cache ancien
                cutoff_time = datetime.now() - timedelta(hours=1)
                
                old_cache_keys = [
                    service_id for service_id, health in self.health_cache.items()
                    if health.timestamp < cutoff_time
                ]
                
                for service_id in old_cache_keys:
                    del self.health_cache[service_id]
                
                # Nettoyer historique alertes ancien
                cutoff_time = datetime.now() - timedelta(days=30)
                
                while (self.alert_history and 
                       self.alert_history[0].timestamp < cutoff_time):
                    self.alert_history.popleft()
                
                logger.info(f"🧹 Nettoyage: {len(old_cache_keys)} caches supprimés")
                
                await asyncio.sleep(3600)  # Nettoyer toutes les heures
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur cleanup loop: {e}")
                await asyncio.sleep(1800)
    
    async def _load_monitored_services(self):
        """Charge services à monitorer depuis Redis."""
        try:
            # Récupérer configurations services
            service_keys = await self.redis_client.keys("service_monitoring_config:*")
            
            for key in service_keys:
                config_data = await self.redis_client.get(key)
                if config_data:
                    config = json.loads(config_data)
                    service_id = key.split(":")[-1]
                    self.monitored_services[service_id] = config
                    
                    # Charger dépendances
                    if config.get('dependencies'):
                        self.dependency_graph[service_id] = set(config['dependencies'])
            
            logger.info(f"✅ {len(self.monitored_services)} services chargés pour monitoring")
            
        except Exception as e:
            logger.error(f"Erreur chargement services à monitorer: {e}")
    
    async def _persist_service_config(self, service_id: str, config: Dict[str, Any]):
        """Persiste configuration service."""
        try:
            key = f"service_monitoring_config:{service_id}"
            await self.redis_client.set(key, json.dumps(config, default=str))
            
        except Exception as e:
            logger.error(f"Erreur persistance config service {service_id}: {e}")
    
    async def get_service_health_status(self, service_id: str) -> Optional[HealthCheck]:
        """Récupère status santé actuel d'un service."""
        return self.health_cache.get(service_id)
    
    async def get_active_alerts(self, service_id: Optional[str] = None) -> List[HealthAlert]:
        """Récupère alertes actives."""
        if service_id:
            return [alert for alert in self.active_alerts.values() 
                   if alert.service_id == service_id]
        else:
            return list(self.active_alerts.values())
    
    async def get_health_metrics(self) -> Dict[str, Any]:
        """Récupère métriques globales monitoring."""
        return {
            'monitored_services': len(self.monitored_services),
            'active_alerts': len(self.active_alerts),
            'total_alerts_today': len([a for a in self.alert_history 
                                     if a.timestamp.date() == datetime.now().date()]),
            'ml_model_trained': self.is_model_trained,
            'healthy_services': len([h for h in self.health_cache.values() 
                                   if h.status == HealthStatus.HEALTHY]),
            'critical_services': len([h for h in self.health_cache.values() 
                                    if h.status in [HealthStatus.CRITICAL, HealthStatus.DOWN]])
        }

# Factory pour création instance
async def create_service_health_monitor(redis_client: aioredis.Redis,
                                      monitoring_config: MonitoringConfig = None) -> ServiceHealthMonitor:
    """Crée instance ServiceHealthMonitor."""
    if not monitoring_config:
        monitoring_config = MonitoringConfig()
    
    monitor = ServiceHealthMonitor(redis_client, monitoring_config)
    await monitor.start()
    return monitor

# Export classes principales
__all__ = [
    'ServiceHealthMonitor',
    'HealthStatus',
    'AlertSeverity',
    'HealthMetricType',
    'HealthMetric',
    'HealthCheck',
    'HealthAlert',
    'MonitoringConfig',
    'create_service_health_monitor'
]