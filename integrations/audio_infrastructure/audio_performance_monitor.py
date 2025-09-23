"""📊 Enterprise Audio Performance Monitor - Advanced Analytics & Optimization
==========================================================================

Moniteur de performance audio enterprise avec analytics avancées,
optimization temps réel et insights business pour Ainflue.

Expert Roles Implementation:
🎵 Audio Engineer: Métriques qualité audio + performance DSP + analysis acoustique
🏗️ Backend Senior: Monitoring infrastructure + performance metrics + scalability
🤖 Lead Dev IA: ML performance prediction + optimization automatique + anomaly detection
🧠 ML Engineer: Performance models + predictive analytics + resource optimization
🔒 Sécurité: Performance security + audit monitoring + compliance tracking
⚙️ DevOps: APM integration + monitoring automation + alerting systems
🔗 Microservices: Service monitoring + distributed tracing + health checks
⚡ Performance: Real-time monitoring + optimization algorithms + resource management

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Enterprise Production
Date: 16 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture de monitoring audio est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import defaultdict, deque
import statistics
import numpy as np
import aiofiles
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
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques"""
    # Performance système
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    
    # Performance audio
    PROCESSING_LATENCY = "processing_latency"
    AUDIO_QUALITY_SCORE = "audio_quality_score"
    COMPRESSION_RATIO = "compression_ratio"
    THROUGHPUT = "throughput"
    
    # Performance application
    REQUEST_RATE = "request_rate"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    
    # Métriques business
    USER_ENGAGEMENT = "user_engagement"
    CONTENT_POPULARITY = "content_popularity"
    CREATOR_SATISFACTION = "creator_satisfaction"
    REVENUE_IMPACT = "revenue_impact"

class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ResourceType(Enum):
    """Types de ressources"""
    AUDIO_PROCESSOR = "audio_processor"
    STREAMING_SERVICE = "streaming_service"
    DATABASE = "database"
    CACHE = "cache"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    EXTERNAL_API = "external_api"

@dataclass
class PerformanceMetric:
    """Métrique de performance"""
    metric_id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    resource_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceAlert:
    """Alerte de performance"""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resource_id: Optional[str] = None
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class ResourceHealth:
    """État de santé d'une ressource"""
    resource_id: str
    resource_type: ResourceType
    status: str  # healthy, degraded, unhealthy, unknown
    last_check: datetime
    uptime: float  # en secondes
    metrics: Dict[MetricType, float] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)  # IDs des alertes actives

@dataclass
class PerformanceReport:
    """Rapport de performance"""
    report_id: str
    period_start: datetime
    period_end: datetime
    summary: Dict[str, Any]
    detailed_metrics: Dict[str, List[PerformanceMetric]]
    alerts_summary: Dict[AlertSeverity, int]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)

class SystemMonitor:
    """Moniteur système pour métriques hardware"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.memory_total = psutil.virtual_memory().total
        self.disk_usage_cache = {}
        self.network_io_cache = {}
        
    async def collect_system_metrics(self) -> Dict[MetricType, float]:
        """Collecte les métriques système"""
        metrics = {}
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics[MetricType.CPU_USAGE] = cpu_percent
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            metrics[MetricType.MEMORY_USAGE] = memory_percent
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                # Calculer les taux (bytes/seconde)
                current_time = time.time()
                
                if 'last_disk_check' in self.disk_usage_cache:
                    time_delta = current_time - self.disk_usage_cache['last_disk_check']
                    read_delta = disk_io.read_bytes - self.disk_usage_cache['last_read']
                    write_delta = disk_io.write_bytes - self.disk_usage_cache['last_write']
                    
                    if time_delta > 0:
                        read_rate = read_delta / time_delta
                        write_rate = write_delta / time_delta
                        metrics[MetricType.DISK_IO] = read_rate + write_rate
                
                self.disk_usage_cache.update({
                    'last_disk_check': current_time,
                    'last_read': disk_io.read_bytes,
                    'last_write': disk_io.write_bytes
                })
            
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io:
                current_time = time.time()
                
                if 'last_network_check' in self.network_io_cache:
                    time_delta = current_time - self.network_io_cache['last_network_check']
                    sent_delta = network_io.bytes_sent - self.network_io_cache['last_sent']
                    recv_delta = network_io.bytes_recv - self.network_io_cache['last_recv']
                    
                    if time_delta > 0:
                        network_rate = (sent_delta + recv_delta) / time_delta
                        metrics[MetricType.NETWORK_IO] = network_rate
                
                self.network_io_cache.update({
                    'last_network_check': current_time,
                    'last_sent': network_io.bytes_sent,
                    'last_recv': network_io.bytes_recv
                })
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
        
        return metrics
    
    async def get_resource_usage(self, pid: Optional[int] = None) -> Dict[str, float]:
        """Obtient l'usage des ressources pour un processus spécifique"""
        try:
            if pid:
                process = psutil.Process(pid)
            else:
                process = psutil.Process()
            
            return {
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_rss': process.memory_info().rss,
                'memory_vms': process.memory_info().vms,
                'num_threads': process.num_threads(),
                'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0,
                'create_time': process.create_time()
            }
            
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {}

class AudioMetricsCollector:
    """Collecteur de métriques spécifiques à l'audio"""
    
    def __init__(self):
        self.processing_times = deque(maxlen=1000)
        self.quality_scores = deque(maxlen=1000)
        self.throughput_measurements = deque(maxlen=100)
        self.error_counts = defaultdict(int)
        
    async def record_processing_time(self, processing_time: float, operation: str):
        """Enregistre un temps de traitement"""
        self.processing_times.append({
            'time': processing_time,
            'operation': operation,
            'timestamp': datetime.now()
        })
    
    async def record_quality_score(self, score: float, audio_type: str):
        """Enregistre un score de qualité"""
        self.quality_scores.append({
            'score': score,
            'type': audio_type,
            'timestamp': datetime.now()
        })
    
    async def record_throughput(self, items_processed: int, time_window: float):
        """Enregistre le débit de traitement"""
        throughput = items_processed / time_window if time_window > 0 else 0
        self.throughput_measurements.append({
            'throughput': throughput,
            'items': items_processed,
            'window': time_window,
            'timestamp': datetime.now()
        })
    
    async def record_error(self, error_type: str):
        """Enregistre une erreur"""
        self.error_counts[error_type] += 1
    
    async def get_audio_metrics(self) -> Dict[MetricType, float]:
        """Calcule les métriques audio agrégées"""
        metrics = {}
        
        try:
            # Latence moyenne de traitement
            if self.processing_times:
                recent_times = [
                    entry['time'] for entry in self.processing_times
                    if datetime.now() - entry['timestamp'] < timedelta(minutes=5)
                ]
                if recent_times:
                    metrics[MetricType.PROCESSING_LATENCY] = statistics.mean(recent_times)
            
            # Score de qualité moyen
            if self.quality_scores:
                recent_scores = [
                    entry['score'] for entry in self.quality_scores
                    if datetime.now() - entry['timestamp'] < timedelta(minutes=5)
                ]
                if recent_scores:
                    metrics[MetricType.AUDIO_QUALITY_SCORE] = statistics.mean(recent_scores)
            
            # Débit de traitement
            if self.throughput_measurements:
                recent_throughput = [
                    entry['throughput'] for entry in self.throughput_measurements
                    if datetime.now() - entry['timestamp'] < timedelta(minutes=5)
                ]
                if recent_throughput:
                    metrics[MetricType.THROUGHPUT] = statistics.mean(recent_throughput)
            
            # Taux d'erreur
            total_operations = len(self.processing_times)
            total_errors = sum(self.error_counts.values())
            if total_operations > 0:
                error_rate = (total_errors / total_operations) * 100
                metrics[MetricType.ERROR_RATE] = error_rate
                
        except Exception as e:
            logger.error(f"Error calculating audio metrics: {e}")
        
        return metrics
    
    async def get_performance_insights(self) -> Dict[str, Any]:
        """Génère des insights de performance"""
        insights = {
            'processing_efficiency': 'unknown',
            'quality_trend': 'stable',
            'bottlenecks': [],
            'recommendations': []
        }
        
        try:
            # Analyser l'efficacité du traitement
            if len(self.processing_times) >= 10:
                recent_times = [entry['time'] for entry in list(self.processing_times)[-10:]]
                older_times = [entry['time'] for entry in list(self.processing_times)[-20:-10]]
                
                if older_times:
                    recent_avg = statistics.mean(recent_times)
                    older_avg = statistics.mean(older_times)
                    
                    if recent_avg < older_avg * 0.9:
                        insights['processing_efficiency'] = 'improving'
                    elif recent_avg > older_avg * 1.1:
                        insights['processing_efficiency'] = 'degrading'
                    else:
                        insights['processing_efficiency'] = 'stable'
            
            # Analyser la tendance qualité
            if len(self.quality_scores) >= 10:
                recent_scores = [entry['score'] for entry in list(self.quality_scores)[-10:]]
                older_scores = [entry['score'] for entry in list(self.quality_scores)[-20:-10]]
                
                if older_scores:
                    recent_avg = statistics.mean(recent_scores)
                    older_avg = statistics.mean(older_scores)
                    
                    if recent_avg > older_avg + 0.05:
                        insights['quality_trend'] = 'improving'
                    elif recent_avg < older_avg - 0.05:
                        insights['quality_trend'] = 'degrading'
            
            # Identifier les goulots d'étranglement
            if self.processing_times:
                operation_times = defaultdict(list)
                for entry in self.processing_times:
                    operation_times[entry['operation']].append(entry['time'])
                
                # Trouver les opérations les plus lentes
                avg_times = {
                    op: statistics.mean(times)
                    for op, times in operation_times.items()
                    if len(times) >= 5
                }
                
                if avg_times:
                    slowest_ops = sorted(avg_times.items(), key=lambda x: x[1], reverse=True)[:3]
                    insights['bottlenecks'] = [op for op, _ in slowest_ops]
            
            # Générer des recommandations
            if insights['processing_efficiency'] == 'degrading':
                insights['recommendations'].append("Consider optimizing audio processing algorithms")
            
            if insights['quality_trend'] == 'degrading':
                insights['recommendations'].append("Review quality control parameters")
            
            if 'transcoding' in insights['bottlenecks']:
                insights['recommendations'].append("Consider hardware acceleration for transcoding")
                
        except Exception as e:
            logger.error(f"Error generating performance insights: {e}")
        
        return insights

class AlertManager:
    """Gestionnaire d'alertes"""
    
    def __init__(self):
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = deque(maxlen=10000)
        self.notification_handlers = []
        
    async def add_alert_rule(
        self,
        rule_name: str,
        metric_type: MetricType,
        threshold: float,
        operator: str,  # >, <, >=, <=, ==, !=
        severity: AlertSeverity,
        resource_filter: Optional[str] = None
    ):
        """Ajoute une règle d'alerte"""
        self.alert_rules[rule_name] = {
            'metric_type': metric_type,
            'threshold': threshold,
            'operator': operator,
            'severity': severity,
            'resource_filter': resource_filter,
            'enabled': True
        }
    
    async def evaluate_metrics(self, metrics: List[PerformanceMetric]):
        """Évalue les métriques contre les règles d'alerte"""
        for metric in metrics:
            await self._check_metric_against_rules(metric)
    
    async def _check_metric_against_rules(self, metric: PerformanceMetric):
        """Vérifie une métrique contre toutes les règles"""
        for rule_name, rule in self.alert_rules.items():
            if not rule['enabled']:
                continue
                
            if rule['metric_type'] != metric.metric_type:
                continue
            
            # Filtrer par ressource si spécifié
            if rule['resource_filter'] and metric.resource_id != rule['resource_filter']:
                continue
            
            # Évaluer la condition
            triggered = await self._evaluate_condition(
                metric.value, rule['threshold'], rule['operator']
            )
            
            if triggered:
                await self._trigger_alert(rule_name, rule, metric)
            else:
                await self._resolve_alert(rule_name, metric.resource_id)
    
    async def _evaluate_condition(self, value: float, threshold: float, operator: str) -> bool:
        """Évalue une condition d'alerte"""
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return abs(value - threshold) < 0.001  # Tolérance pour float
        elif operator == '!=':
            return abs(value - threshold) >= 0.001
        else:
            return False
    
    async def _trigger_alert(
        self,
        rule_name: str,
        rule: Dict[str, Any],
        metric: PerformanceMetric
    ):
        """Déclenche une alerte"""
        alert_key = f"{rule_name}:{metric.resource_id or 'global'}"
        
        # Éviter la duplication d'alertes
        if alert_key in self.active_alerts:
            return
        
        alert = PerformanceAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=rule_name,
            severity=rule['severity'],
            message=f"Metric {metric.metric_type.value} ({metric.value:.2f}) exceeded threshold ({rule['threshold']:.2f})",
            timestamp=datetime.now(),
            resource_id=metric.resource_id,
            metric_value=metric.value,
            threshold_value=rule['threshold']
        )
        
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        # Notifier
        await self._send_notifications(alert)
        
        logger.warning(f"Alert triggered: {alert.message}")
    
    async def _resolve_alert(self, rule_name: str, resource_id: Optional[str]):
        """Résout une alerte"""
        alert_key = f"{rule_name}:{resource_id or 'global'}"
        
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            
            del self.active_alerts[alert_key]
            
            logger.info(f"Alert resolved: {alert.alert_type}")
    
    async def _send_notifications(self, alert: PerformanceAlert):
        """Envoie les notifications d'alerte"""
        for handler in self.notification_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
    
    def add_notification_handler(self, handler: Callable):
        """Ajoute un gestionnaire de notification"""
        self.notification_handlers.append(handler)
    
    async def get_active_alerts(self) -> List[PerformanceAlert]:
        """Retourne les alertes actives"""
        return list(self.active_alerts.values())
    
    async def get_alert_summary(self) -> Dict[AlertSeverity, int]:
        """Retourne un résumé des alertes par sévérité"""
        summary = {severity: 0 for severity in AlertSeverity}
        
        for alert in self.active_alerts.values():
            summary[alert.severity] += 1
        
        return summary

class PerformancePredictor:
    """Prédicteur de performance basé sur ML"""
    
    def __init__(self):
        self.historical_data = defaultdict(deque)  # Par type de métrique
        self.prediction_models = {}
        self.max_history = 1000
        
    async def add_historical_data(self, metric: PerformanceMetric):
        """Ajoute des données historiques"""
        key = f"{metric.metric_type.value}:{metric.resource_id or 'global'}"
        
        self.historical_data[key].append({
            'timestamp': metric.timestamp,
            'value': metric.value,
            'tags': metric.tags
        })
        
        # Limiter la taille de l'historique
        if len(self.historical_data[key]) > self.max_history:
            self.historical_data[key].popleft()
    
    async def predict_future_values(
        self,
        metric_type: MetricType,
        resource_id: Optional[str],
        prediction_horizon: int = 60  # minutes
    ) -> List[Tuple[datetime, float]]:
        """Prédit les valeurs futures d'une métrique"""
        
        key = f"{metric_type.value}:{resource_id or 'global'}"
        
        if key not in self.historical_data or len(self.historical_data[key]) < 10:
            return []
        
        try:
            # Extraction des données pour la prédiction
            data = list(self.historical_data[key])
            values = [entry['value'] for entry in data[-50:]]  # 50 derniers points
            
            # Prédiction simple par moyenne mobile et tendance
            # Dans une vraie implémentation, utiliser des modèles ML sophistiqués
            
            # Calculer la tendance
            if len(values) >= 10:
                recent_avg = statistics.mean(values[-10:])
                older_avg = statistics.mean(values[-20:-10]) if len(values) >= 20 else recent_avg
                trend = (recent_avg - older_avg) / 10  # Tendance par point
            else:
                trend = 0
            
            # Générer les prédictions
            predictions = []
            current_time = datetime.now()
            current_value = values[-1]
            
            for i in range(1, prediction_horizon + 1):
                # Prédiction simple: valeur actuelle + tendance * i + bruit
                predicted_value = current_value + (trend * i)
                
                # Ajouter une variation aléatoire basée sur la variance historique
                if len(values) > 5:
                    variance = statistics.variance(values[-10:])
                    noise = np.random.normal(0, np.sqrt(variance) * 0.1)
                    predicted_value += noise
                
                prediction_time = current_time + timedelta(minutes=i)
                predictions.append((prediction_time, max(0, predicted_value)))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting values: {e}")
            return []
    
    async def detect_anomalies(
        self,
        metric_type: MetricType,
        resource_id: Optional[str],
        current_value: float
    ) -> Tuple[bool, float]:
        """Détecte les anomalies dans les métriques"""
        
        key = f"{metric_type.value}:{resource_id or 'global'}"
        
        if key not in self.historical_data or len(self.historical_data[key]) < 20:
            return False, 0.0
        
        try:
            # Récupérer les données historiques
            historical_values = [
                entry['value'] for entry in list(self.historical_data[key])[-50:]
            ]
            
            # Calculer les statistiques
            mean_value = statistics.mean(historical_values)
            std_dev = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
            
            # Détecter l'anomalie (seuil à 2 écarts-types)
            if std_dev > 0:
                z_score = abs(current_value - mean_value) / std_dev
                is_anomaly = z_score > 2.0
                return is_anomaly, z_score
            
            return False, 0.0
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return False, 0.0

class AudioPerformanceMonitor:
    """Moniteur de performance audio enterprise"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialise le moniteur de performance"""
        self.system_monitor = SystemMonitor()
        self.audio_metrics_collector = AudioMetricsCollector()
        self.alert_manager = AlertManager()
        self.performance_predictor = PerformancePredictor()
        
        # Stockage des métriques
        self.metrics_storage = deque(maxlen=100000)
        self.resource_health_status = {}
        
        # Configuration
        self.collection_interval = 30  # secondes
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Cache Redis
        self.redis_client = None
        self.redis_url = redis_url
        
        # Statistiques
        self.stats = {
            'metrics_collected': 0,
            'alerts_triggered': 0,
            'anomalies_detected': 0,
            'uptime_start': datetime.now(),
            'last_collection': None
        }
        
        # Initialiser les règles d'alerte par défaut
        asyncio.create_task(self._setup_default_alert_rules())
        
        logger.info("AudioPerformanceMonitor initialized successfully")
    
    async def initialize_redis(self):
        """Initialise la connexion Redis"""
        if self.redis_url:
            try:
                self.redis_client = await aioredis.from_url(self.redis_url)
                logger.info("Redis connection established for performance monitoring")
            except Exception as e:
                logger.warning(f"Could not connect to Redis: {e}")
    
    async def start_monitoring(self):
        """Démarre le monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        await self.initialize_redis()
        
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Arrête le monitoring"""
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Boucle principale de monitoring"""
        while self.monitoring_active:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Attendre avant de réessayer
    
    async def _collect_all_metrics(self):
        """Collecte toutes les métriques"""
        timestamp = datetime.now()
        collected_metrics = []
        
        try:
            # Métriques système
            system_metrics = await self.system_monitor.collect_system_metrics()
            for metric_type, value in system_metrics.items():
                metric = PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=metric_type,
                    value=value,
                    unit=self._get_metric_unit(metric_type),
                    timestamp=timestamp,
                    resource_id="system",
                    tags={"source": "system_monitor"}
                )
                collected_metrics.append(metric)
            
            # Métriques audio
            audio_metrics = await self.audio_metrics_collector.get_audio_metrics()
            for metric_type, value in audio_metrics.items():
                metric = PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_type=metric_type,
                    value=value,
                    unit=self._get_metric_unit(metric_type),
                    timestamp=timestamp,
                    resource_id="audio_processor",
                    tags={"source": "audio_collector"}
                )
                collected_metrics.append(metric)
            
            # Stocker les métriques
            for metric in collected_metrics:
                self.metrics_storage.append(metric)
                await self.performance_predictor.add_historical_data(metric)
            
            # Évaluer les alertes
            await self.alert_manager.evaluate_metrics(collected_metrics)
            
            # Détecter les anomalies
            await self._detect_anomalies(collected_metrics)
            
            # Mettre à jour l'état de santé des ressources
            await self._update_resource_health(collected_metrics)
            
            # Sauvegarder dans Redis si disponible
            if self.redis_client:
                await self._save_metrics_to_redis(collected_metrics)
            
            # Mettre à jour les statistiques
            self.stats['metrics_collected'] += len(collected_metrics)
            self.stats['last_collection'] = timestamp
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    async def _detect_anomalies(self, metrics: List[PerformanceMetric]):
        """Détecte les anomalies dans les métriques"""
        for metric in metrics:
            is_anomaly, confidence = await self.performance_predictor.detect_anomalies(
                metric.metric_type, metric.resource_id, metric.value
            )
            
            if is_anomaly:
                self.stats['anomalies_detected'] += 1
                
                # Créer une alerte d'anomalie
                alert = PerformanceAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type="anomaly_detection",
                    severity=AlertSeverity.WARNING,
                    message=f"Anomaly detected in {metric.metric_type.value}: {metric.value:.2f} (confidence: {confidence:.2f})",
                    timestamp=datetime.now(),
                    resource_id=metric.resource_id,
                    metric_value=metric.value
                )
                
                logger.warning(f"Anomaly detected: {alert.message}")
    
    async def _update_resource_health(self, metrics: List[PerformanceMetric]):
        """Met à jour l'état de santé des ressources"""
        resource_metrics = defaultdict(dict)
        
        # Grouper les métriques par ressource
        for metric in metrics:
            resource_id = metric.resource_id or "global"
            resource_metrics[resource_id][metric.metric_type] = metric.value
        
        # Évaluer la santé de chaque ressource
        for resource_id, metrics_dict in resource_metrics.items():
            health_status = await self._calculate_health_status(metrics_dict)
            
            # Déterminer le type de ressource
            resource_type = self._infer_resource_type(resource_id)
            
            # Obtenir les alertes actives pour cette ressource
            active_alerts = [
                alert.alert_id for alert in await self.alert_manager.get_active_alerts()
                if alert.resource_id == resource_id
            ]
            
            # Calculer l'uptime (simulation)
            uptime = (datetime.now() - self.stats['uptime_start']).total_seconds()
            
            self.resource_health_status[resource_id] = ResourceHealth(
                resource_id=resource_id,
                resource_type=resource_type,
                status=health_status,
                last_check=datetime.now(),
                uptime=uptime,
                metrics=metrics_dict,
                alerts=active_alerts
            )
    
    async def _calculate_health_status(self, metrics_dict: Dict[MetricType, float]) -> str:
        """Calcule l'état de santé basé sur les métriques"""
        health_score = 100.0
        
        # Évaluer chaque métrique
        if MetricType.CPU_USAGE in metrics_dict:
            cpu_usage = metrics_dict[MetricType.CPU_USAGE]
            if cpu_usage > 90:
                health_score -= 30
            elif cpu_usage > 75:
                health_score -= 15
        
        if MetricType.MEMORY_USAGE in metrics_dict:
            memory_usage = metrics_dict[MetricType.MEMORY_USAGE]
            if memory_usage > 90:
                health_score -= 25
            elif memory_usage > 80:
                health_score -= 10
        
        if MetricType.ERROR_RATE in metrics_dict:
            error_rate = metrics_dict[MetricType.ERROR_RATE]
            if error_rate > 10:
                health_score -= 40
            elif error_rate > 5:
                health_score -= 20
        
        if MetricType.PROCESSING_LATENCY in metrics_dict:
            latency = metrics_dict[MetricType.PROCESSING_LATENCY]
            if latency > 5000:  # 5 secondes
                health_score -= 35
            elif latency > 2000:  # 2 secondes
                health_score -= 15
        
        # Déterminer le statut
        if health_score >= 80:
            return "healthy"
        elif health_score >= 60:
            return "degraded"
        elif health_score >= 30:
            return "unhealthy"
        else:
            return "critical"
    
    def _infer_resource_type(self, resource_id: str) -> ResourceType:
        """Infer le type de ressource basé sur l'ID"""
        if "system" in resource_id.lower():
            return ResourceType.AUDIO_PROCESSOR
        elif "audio" in resource_id.lower():
            return ResourceType.AUDIO_PROCESSOR
        elif "stream" in resource_id.lower():
            return ResourceType.STREAMING_SERVICE
        elif "db" in resource_id.lower() or "database" in resource_id.lower():
            return ResourceType.DATABASE
        elif "cache" in resource_id.lower() or "redis" in resource_id.lower():
            return ResourceType.CACHE
        elif "network" in resource_id.lower():
            return ResourceType.NETWORK
        else:
            return ResourceType.AUDIO_PROCESSOR
    
    def _get_metric_unit(self, metric_type: MetricType) -> str:
        """Retourne l'unité pour un type de métrique"""
        unit_map = {
            MetricType.CPU_USAGE: "%",
            MetricType.MEMORY_USAGE: "%",
            MetricType.DISK_IO: "bytes/s",
            MetricType.NETWORK_IO: "bytes/s",
            MetricType.PROCESSING_LATENCY: "ms",
            MetricType.AUDIO_QUALITY_SCORE: "score",
            MetricType.COMPRESSION_RATIO: "ratio",
            MetricType.THROUGHPUT: "items/s",
            MetricType.REQUEST_RATE: "req/s",
            MetricType.ERROR_RATE: "%",
            MetricType.RESPONSE_TIME: "ms",
            MetricType.QUEUE_LENGTH: "items"
        }
        return unit_map.get(metric_type, "value")
    
    async def _save_metrics_to_redis(self, metrics: List[PerformanceMetric]):
        """Sauvegarde les métriques dans Redis"""
        try:
            pipeline = self.redis_client.pipeline()
            
            for metric in metrics:
                key = f"metrics:{metric.metric_type.value}:{metric.resource_id or 'global'}"
                value = {
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat(),
                    'unit': metric.unit,
                    'tags': metric.tags
                }
                
                # Ajouter à une liste triée par timestamp
                score = metric.timestamp.timestamp()
                pipeline.zadd(key, {json.dumps(value): score})
                
                # Limiter la taille (garder 24h de données)
                pipeline.zremrangebyscore(key, 0, score - 86400)
                
                # Définir une expiration
                pipeline.expire(key, 86400)  # 24 heures
            
            await pipeline.execute()
            
        except Exception as e:
            logger.error(f"Error saving metrics to Redis: {e}")
    
    async def _setup_default_alert_rules(self):
        """Configure les règles d'alerte par défaut"""
        # CPU usage élevé
        await self.alert_manager.add_alert_rule(
            "high_cpu_usage",
            MetricType.CPU_USAGE,
            85.0,
            ">",
            AlertSeverity.WARNING
        )
        
        # Utilisation mémoire élevée
        await self.alert_manager.add_alert_rule(
            "high_memory_usage",
            MetricType.MEMORY_USAGE,
            90.0,
            ">",
            AlertSeverity.ERROR
        )
        
        # Latence de traitement élevée
        await self.alert_manager.add_alert_rule(
            "high_processing_latency",
            MetricType.PROCESSING_LATENCY,
            3000.0,  # 3 secondes
            ">",
            AlertSeverity.WARNING
        )
        
        # Taux d'erreur élevé
        await self.alert_manager.add_alert_rule(
            "high_error_rate",
            MetricType.ERROR_RATE,
            5.0,  # 5%
            ">",
            AlertSeverity.ERROR
        )
        
        # Score de qualité faible
        await self.alert_manager.add_alert_rule(
            "low_quality_score",
            MetricType.AUDIO_QUALITY_SCORE,
            0.8,
            "<",
            AlertSeverity.WARNING
        )
    
    async def generate_performance_report(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> PerformanceReport:
        """Génère un rapport de performance"""
        
        # Filtrer les métriques par période
        period_metrics = [
            metric for metric in self.metrics_storage
            if start_time <= metric.timestamp <= end_time
        ]
        
        # Organiser par type de métrique
        detailed_metrics = defaultdict(list)
        for metric in period_metrics:
            detailed_metrics[metric.metric_type.value].append(metric)
        
        # Calculer le résumé
        summary = await self._calculate_performance_summary(period_metrics)
        
        # Résumé des alertes
        period_alerts = [
            alert for alert in self.alert_manager.alert_history
            if start_time <= alert.timestamp <= end_time
        ]
        
        alerts_summary = defaultdict(int)
        for alert in period_alerts:
            alerts_summary[alert.severity] += 1
        
        # Générer des recommandations
        recommendations = await self._generate_performance_recommendations(
            period_metrics, period_alerts
        )
        
        report = PerformanceReport(
            report_id=str(uuid.uuid4()),
            period_start=start_time,
            period_end=end_time,
            summary=summary,
            detailed_metrics=detailed_metrics,
            alerts_summary=dict(alerts_summary),
            recommendations=recommendations
        )
        
        return report
    
    async def _calculate_performance_summary(
        self,
        metrics: List[PerformanceMetric]
    ) -> Dict[str, Any]:
        """Calcule le résumé de performance"""
        summary = {
            'total_metrics': len(metrics),
            'metrics_by_type': defaultdict(int),
            'average_values': {},
            'peak_values': {},
            'health_overview': {}
        }
        
        # Grouper par type
        metrics_by_type = defaultdict(list)
        for metric in metrics:
            metrics_by_type[metric.metric_type].append(metric.value)
            summary['metrics_by_type'][metric.metric_type.value] += 1
        
        # Calculer moyennes et pics
        for metric_type, values in metrics_by_type.items():
            if values:
                summary['average_values'][metric_type.value] = statistics.mean(values)
                summary['peak_values'][metric_type.value] = max(values)
        
        # Vue d'ensemble de la santé
        healthy_resources = len([
            r for r in self.resource_health_status.values()
            if r.status == "healthy"
        ])
        total_resources = len(self.resource_health_status)
        
        summary['health_overview'] = {
            'healthy_resources': healthy_resources,
            'total_resources': total_resources,
            'health_percentage': (healthy_resources / max(total_resources, 1)) * 100
        }
        
        return summary
    
    async def _generate_performance_recommendations(
        self,
        metrics: List[PerformanceMetric],
        alerts: List[PerformanceAlert]
    ) -> List[str]:
        """Génère des recommandations de performance"""
        recommendations = []
        
        # Analyser les métriques
        cpu_metrics = [m.value for m in metrics if m.metric_type == MetricType.CPU_USAGE]
        memory_metrics = [m.value for m in metrics if m.metric_type == MetricType.MEMORY_USAGE]
        latency_metrics = [m.value for m in metrics if m.metric_type == MetricType.PROCESSING_LATENCY]
        
        # Recommandations basées sur les métriques
        if cpu_metrics and statistics.mean(cpu_metrics) > 75:
            recommendations.append("Consider upgrading CPU or optimizing processing algorithms")
        
        if memory_metrics and statistics.mean(memory_metrics) > 80:
            recommendations.append("Consider increasing memory or optimizing memory usage")
        
        if latency_metrics and statistics.mean(latency_metrics) > 2000:
            recommendations.append("Investigate processing bottlenecks and optimize latency")
        
        # Recommandations basées sur les alertes
        alert_types = [alert.alert_type for alert in alerts]
        
        if alert_types.count("high_error_rate") > 5:
            recommendations.append("Investigate and fix recurring errors in the system")
        
        if alert_types.count("anomaly_detection") > 10:
            recommendations.append("Review system behavior for unusual patterns")
        
        # Recommandations générales
        if len(alerts) > 50:
            recommendations.append("Consider reviewing alert thresholds to reduce noise")
        
        return recommendations
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques actuelles"""
        current_time = datetime.now()
        recent_cutoff = current_time - timedelta(minutes=5)
        
        recent_metrics = [
            metric for metric in self.metrics_storage
            if metric.timestamp > recent_cutoff
        ]
        
        # Organiser par type et ressource
        current_values = {}
        for metric in recent_metrics:
            key = f"{metric.metric_type.value}:{metric.resource_id or 'global'}"
            if key not in current_values or metric.timestamp > current_values[key]['timestamp']:
                current_values[key] = {
                    'value': metric.value,
                    'unit': metric.unit,
                    'timestamp': metric.timestamp
                }
        
        return current_values
    
    async def get_resource_health(self) -> Dict[str, ResourceHealth]:
        """Retourne l'état de santé des ressources"""
        return self.resource_health_status.copy()
    
    async def get_active_alerts(self) -> List[PerformanceAlert]:
        """Retourne les alertes actives"""
        return await self.alert_manager.get_active_alerts()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du moniteur"""
        current_time = datetime.now()
        uptime = (current_time - self.stats['uptime_start']).total_seconds()
        
        stats = self.stats.copy()
        stats['uptime_seconds'] = uptime
        stats['monitoring_active'] = self.monitoring_active
        stats['metrics_in_storage'] = len(self.metrics_storage)
        stats['active_alerts'] = len(await self.alert_manager.get_active_alerts())
        
        return stats
    
    # Méthodes pour l'intégration avec les composants audio
    async def record_audio_processing_time(self, processing_time: float, operation: str):
        """Enregistre un temps de traitement audio"""
        await self.audio_metrics_collector.record_processing_time(processing_time, operation)
    
    async def record_audio_quality_score(self, score: float, audio_type: str):
        """Enregistre un score de qualité audio"""
        await self.audio_metrics_collector.record_quality_score(score, audio_type)
    
    async def record_throughput(self, items_processed: int, time_window: float):
        """Enregistre le débit de traitement"""
        await self.audio_metrics_collector.record_throughput(items_processed, time_window)
    
    async def record_error(self, error_type: str):
        """Enregistre une erreur"""
        await self.audio_metrics_collector.record_error(error_type)

# Factory functions
async def create_audio_performance_monitor(
    redis_url: Optional[str] = None,
    collection_interval: int = 30
) -> AudioPerformanceMonitor:
    """Crée une instance du moniteur de performance"""
    monitor = AudioPerformanceMonitor(redis_url)
    monitor.collection_interval = collection_interval
    return monitor

# Export des classes et fonctions principales
__all__ = [
    'AudioPerformanceMonitor',
    'MetricType',
    'AlertSeverity',
    'ResourceType',
    'PerformanceMetric',
    'PerformanceAlert',
    'ResourceHealth',
    'PerformanceReport',
    'SystemMonitor',
    'AudioMetricsCollector',
    'AlertManager',
    'PerformancePredictor',
    'create_audio_performance_monitor'
]