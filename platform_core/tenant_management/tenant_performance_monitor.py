#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 Tenant Performance Monitor - Enterprise Multi-Tenant Performance Monitoring

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
Cette architecture tenant performance monitoring est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite PERSONNELLE
est STRICTEMENT INTERDITE et sera poursuivie en justice.
"""

import asyncio
import logging
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import psutil
import redis
import psycopg2
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
import aiohttp
import yaml


# Configuration du logging avancé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/tenant_performance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types de métriques"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class PerformanceThreshold(Enum):
    """Seuils de performance"""
    RESPONSE_TIME_MS = 200
    CPU_USAGE_PERCENT = 80
    MEMORY_USAGE_PERCENT = 85
    DISK_USAGE_PERCENT = 90
    ERROR_RATE_PERCENT = 5


@dataclass
class PerformanceMetric:
    """Métrique de performance"""
    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    tenant_id: str
    service_name: Optional[str]
    instance_id: Optional[str]
    labels: Dict[str, str]
    unit: str


@dataclass
class Alert:
    """Alerte de performance"""
    alert_id: str
    tenant_id: str
    metric_name: str
    current_value: float
    threshold_value: float
    level: AlertLevel
    message: str
    timestamp: datetime
    resolved: bool
    resolution_timestamp: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class PerformanceReport:
    """Rapport de performance"""
    tenant_id: str
    report_id: str
    start_time: datetime
    end_time: datetime
    metrics_summary: Dict[str, Any]
    alerts_count: int
    performance_score: float
    recommendations: List[str]
    trends: Dict[str, Any]


class TenantPerformanceMonitor:
    """
    📊 Enterprise Tenant Performance Monitor
    
    Système de monitoring de performance enterprise pour architecture multi-tenant avec:
    - Métriques temps réel par tenant
    - Alerting intelligent et prédictif
    - Dashboards personnalisés
    - Analyse de tendances et anomalies
    - SLA monitoring et reporting
    - Auto-scaling recommendations
    """
    
    def __init__(self, config_path: str = '/etc/ainflue/performance_config.yaml'):
        """Initialisation du moniteur de performance"""
        self.config = self._load_config(config_path)
        self.metrics_buffer: queue.Queue = queue.Queue(maxsize=10000)
        self.alerts: Dict[str, Alert] = {}
        self.tenant_metrics: Dict[str, Dict[str, Any]] = {}
        self.running = True
        
        # Métriques Prometheus
        self._init_prometheus_metrics()
        
        # Connexions aux services
        self._init_database_connections()
        self._init_monitoring_backends()
        
        # Démarrage des workers
        self._start_monitoring_workers()
        self._start_alert_processor()
        
        logger.info("TenantPerformanceMonitor initialisé avec succès")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Chargement de la configuration"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration chargée depuis {config_path}")
            return config
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            'collection_interval_seconds': 10,
            'retention_days': 30,
            'alert_cooldown_minutes': 5,
            'batch_size': 100,
            'enable_predictions': True,
            'prometheus': {
                'enabled': True,
                'port': 8000,
                'endpoint': '/metrics'
            },
            'database': {
                'host': 'localhost',
                'port': 5432,
                'ssl_mode': 'require'
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'ssl': True
            },
            'thresholds': {
                'response_time_ms': 200,
                'cpu_usage_percent': 80,
                'memory_usage_percent': 85,
                'error_rate_percent': 5
            }
        }
    
    def _init_prometheus_metrics(self):
        """Initialisation des métriques Prometheus"""
        # Métriques de base
        self.request_count = Counter(
            'tenant_requests_total',
            'Total requests by tenant',
            ['tenant_id', 'service', 'method', 'status']
        )
        
        self.request_duration = Histogram(
            'tenant_request_duration_seconds',
            'Request duration by tenant',
            ['tenant_id', 'service', 'method'],
            buckets=[0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.active_users = Gauge(
            'tenant_active_users',
            'Active users by tenant',
            ['tenant_id']
        )
        
        self.resource_usage = Gauge(
            'tenant_resource_usage',
            'Resource usage by tenant',
            ['tenant_id', 'resource_type']
        )
        
        self.error_rate = Gauge(
            'tenant_error_rate',
            'Error rate by tenant',
            ['tenant_id', 'service']
        )
        
        self.throughput = Gauge(
            'tenant_throughput_ops_per_second',
            'Operations per second by tenant',
            ['tenant_id', 'operation_type']
        )
        
        # Démarrage du serveur Prometheus si activé
        if self.config.get('prometheus', {}).get('enabled', True):
            prometheus_port = self.config.get('prometheus', {}).get('port', 8000)
            prometheus_client.start_http_server(prometheus_port)
            logger.info(f"Serveur Prometheus démarré sur le port {prometheus_port}")
    
    def _init_database_connections(self):
        """Initialisation des connexions bases de données"""
        db_config = self.config.get('database', {})
        
        # Configuration PostgreSQL
        self.pg_config = {
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 5432),
            'sslmode': db_config.get('ssl_mode', 'require')
        }
        
        # Configuration Redis
        redis_config = self.config.get('redis', {})
        self.redis_client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            ssl=redis_config.get('ssl', True),
            decode_responses=True
        )
        
        logger.info("Connexions base de données initialisées")
    
    def _init_monitoring_backends(self):
        """Initialisation des backends de monitoring"""
        # Métriques système
        self.system_metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_percent': 0.0,
            'network_bytes_sent': 0,
            'network_bytes_recv': 0
        }
        
        # Cache des métriques par tenant
        self.tenant_cache: Dict[str, Dict[str, float]] = {}
        
        logger.info("Backends de monitoring initialisés")
    
    def _start_monitoring_workers(self):
        """Démarrage des workers de monitoring"""
        # Worker collecte système
        self.system_worker = threading.Thread(
            target=self._system_metrics_worker,
            daemon=True
        )
        self.system_worker.start()
        
        # Worker collecte tenant
        self.tenant_worker = threading.Thread(
            target=self._tenant_metrics_worker,
            daemon=True
        )
        self.tenant_worker.start()
        
        # Worker traitement métriques
        self.processing_worker = threading.Thread(
            target=self._metrics_processing_worker,
            daemon=True
        )
        self.processing_worker.start()
        
        logger.info("Workers de monitoring démarrés")
    
    def _start_alert_processor(self):
        """Démarrage du processeur d'alertes"""
        self.alert_worker = threading.Thread(
            target=self._alert_processing_worker,
            daemon=True
        )
        self.alert_worker.start()
        
        logger.info("Processeur d'alertes démarré")
    
    async def record_metric(self, metric: PerformanceMetric) -> bool:
        """
        📊 Enregistrement d'une métrique de performance
        
        Args:
            metric: Métrique à enregistrer
            
        Returns:
            True si succès
        """
        try:
            # Validation de la métrique
            if not self._validate_metric(metric):
                logger.error(f"Métrique invalide: {metric.metric_name}")
                return False
            
            # Ajout à la queue de traitement
            try:
                self.metrics_buffer.put(metric, timeout=1)
            except queue.Full:
                logger.warning("Buffer de métriques plein, métrique ignorée")
                return False
            
            # Mise à jour des métriques Prometheus
            self._update_prometheus_metrics(metric)
            
            # Mise à jour du cache tenant
            self._update_tenant_cache(metric)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur enregistrement métrique: {e}")
            return False
    
    async def record_request_metrics(self, tenant_id: str, service: str, method: str,
                                   duration_ms: float, status_code: int,
                                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        🌐 Enregistrement des métriques de requête
        
        Args:
            tenant_id: ID du tenant
            service: Nom du service
            method: Méthode HTTP
            duration_ms: Durée en millisecondes
            status_code: Code de statut HTTP
            metadata: Métadonnées additionnelles
            
        Returns:
            True si succès
        """
        try:
            # Métriques de requête
            self.request_count.labels(
                tenant_id=tenant_id,
                service=service,
                method=method,
                status=str(status_code)
            ).inc()
            
            self.request_duration.labels(
                tenant_id=tenant_id,
                service=service,
                method=method
            ).observe(duration_ms / 1000.0)
            
            # Métrique de performance personnalisée
            metric = PerformanceMetric(
                metric_name="request_duration",
                metric_type=MetricType.HISTOGRAM,
                value=duration_ms,
                timestamp=datetime.utcnow(),
                tenant_id=tenant_id,
                service_name=service,
                instance_id=None,
                labels={
                    'method': method,
                    'status': str(status_code)
                },
                unit="milliseconds"
            )
            
            return await self.record_metric(metric)
            
        except Exception as e:
            logger.error(f"Erreur enregistrement métriques requête: {e}")
            return False
    
    async def get_tenant_metrics(self, tenant_id: str, 
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None,
                               metric_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        📈 Récupération des métriques d'un tenant
        
        Args:
            tenant_id: ID du tenant
            start_time: Début de la période
            end_time: Fin de la période
            metric_names: Noms des métriques (optionnel)
            
        Returns:
            Dictionnaire des métriques
        """
        try:
            # Valeurs par défaut
            if not end_time:
                end_time = datetime.utcnow()
            if not start_time:
                start_time = end_time - timedelta(hours=1)
            
            # Récupération depuis le cache pour les données récentes
            if end_time - start_time <= timedelta(minutes=10):
                cached_metrics = self.tenant_cache.get(tenant_id, {})
                return {
                    'tenant_id': tenant_id,
                    'period': {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat()
                    },
                    'metrics': cached_metrics,
                    'source': 'cache'
                }
            
            # Récupération depuis la base de données
            metrics = await self._fetch_metrics_from_db(
                tenant_id, start_time, end_time, metric_names
            )
            
            # Calcul des statistiques
            stats = self._calculate_metrics_statistics(metrics)
            
            return {
                'tenant_id': tenant_id,
                'period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'metrics': metrics,
                'statistics': stats,
                'source': 'database'
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération métriques tenant {tenant_id}: {e}")
            return {}
    
    async def get_performance_report(self, tenant_id: str,
                                   start_time: datetime,
                                   end_time: datetime) -> PerformanceReport:
        """
        📋 Génération d'un rapport de performance
        
        Args:
            tenant_id: ID du tenant
            start_time: Début de la période
            end_time: Fin de la période
            
        Returns:
            Rapport de performance complet
        """
        try:
            # Récupération des métriques
            metrics_data = await self.get_tenant_metrics(tenant_id, start_time, end_time)
            
            # Récupération des alertes
            tenant_alerts = [
                alert for alert in self.alerts.values()
                if alert.tenant_id == tenant_id
                and start_time <= alert.timestamp <= end_time
            ]
            
            # Calcul du score de performance
            performance_score = self._calculate_performance_score(metrics_data, tenant_alerts)
            
            # Analyse des tendances
            trends = await self._analyze_performance_trends(tenant_id, start_time, end_time)
            
            # Génération des recommandations
            recommendations = self._generate_recommendations(metrics_data, tenant_alerts, trends)
            
            # Création du rapport
            report = PerformanceReport(
                tenant_id=tenant_id,
                report_id=f"perf_report_{tenant_id}_{int(time.time())}",
                start_time=start_time,
                end_time=end_time,
                metrics_summary=metrics_data.get('statistics', {}),
                alerts_count=len(tenant_alerts),
                performance_score=performance_score,
                recommendations=recommendations,
                trends=trends
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur génération rapport performance: {e}")
            raise
    
    async def create_alert_rule(self, tenant_id: str, metric_name: str,
                              threshold: float, comparison: str,
                              level: AlertLevel = AlertLevel.WARNING,
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        🚨 Création d'une règle d'alerte
        
        Args:
            tenant_id: ID du tenant
            metric_name: Nom de la métrique à surveiller
            threshold: Seuil d'alerte
            comparison: Type de comparaison ('>', '<', '>=', '<=', '==')
            level: Niveau d'alerte
            metadata: Métadonnées additionnelles
            
        Returns:
            ID de la règle d'alerte
        """
        try:
            rule_id = f"alert_rule_{tenant_id}_{metric_name}_{int(time.time())}"
            
            # Stockage de la règle dans Redis
            rule_data = {
                'rule_id': rule_id,
                'tenant_id': tenant_id,
                'metric_name': metric_name,
                'threshold': threshold,
                'comparison': comparison,
                'level': level.value,
                'metadata': metadata or {},
                'created_at': datetime.utcnow().isoformat(),
                'enabled': True
            }
            
            self.redis_client.hset(
                f"alert_rules:{tenant_id}",
                rule_id,
                json.dumps(rule_data)
            )
            
            logger.info(f"Règle d'alerte créée: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Erreur création règle d'alerte: {e}")
            raise
    
    async def get_active_alerts(self, tenant_id: Optional[str] = None,
                              level: Optional[AlertLevel] = None) -> List[Alert]:
        """
        🚨 Récupération des alertes actives
        
        Args:
            tenant_id: ID du tenant (optionnel)
            level: Niveau d'alerte (optionnel)
            
        Returns:
            Liste des alertes actives
        """
        try:
            alerts = list(self.alerts.values())
            
            # Filtrage par tenant
            if tenant_id:
                alerts = [a for a in alerts if a.tenant_id == tenant_id]
            
            # Filtrage par niveau
            if level:
                alerts = [a for a in alerts if a.level == level]
            
            # Seulement les alertes non résolues
            alerts = [a for a in alerts if not a.resolved]
            
            # Tri par niveau puis par timestamp
            alerts.sort(key=lambda x: (x.level.value, x.timestamp), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Erreur récupération alertes actives: {e}")
            return []
    
    async def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
        """
        ✅ Résolution d'une alerte
        
        Args:
            alert_id: ID de l'alerte
            resolution_note: Note de résolution
            
        Returns:
            True si succès
        """
        try:
            alert = self.alerts.get(alert_id)
            if not alert:
                logger.warning(f"Alerte non trouvée: {alert_id}")
                return False
            
            # Marquage comme résolue
            alert.resolved = True
            alert.resolution_timestamp = datetime.utcnow()
            alert.metadata['resolution_note'] = resolution_note
            
            # Mise à jour dans Redis
            self.redis_client.hset(
                f"alerts:{alert.tenant_id}",
                alert_id,
                json.dumps({
                    **alert.__dict__,
                    'timestamp': alert.timestamp.isoformat(),
                    'resolution_timestamp': alert.resolution_timestamp.isoformat() if alert.resolution_timestamp else None,
                    'level': alert.level.value
                })
            )
            
            logger.info(f"Alerte résolue: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur résolution alerte {alert_id}: {e}")
            return False
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        🏥 Récupération de la santé du système
        
        Returns:
            État de santé global du système
        """
        try:
            # Métriques système
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métriques réseau
            network = psutil.net_io_counters()
            
            # Métriques par tenant
            tenant_count = len(self.tenant_cache)
            active_alerts = len([a for a in self.alerts.values() if not a.resolved])
            
            # État de santé global
            health_status = "healthy"
            if cpu_percent > 90 or memory.percent > 95 or disk.percent > 95:
                health_status = "critical"
            elif cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
                health_status = "warning"
            
            return {
                'status': health_status,
                'timestamp': datetime.utcnow().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024**3),
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv
                },
                'monitoring': {
                    'tenant_count': tenant_count,
                    'active_alerts': active_alerts,
                    'metrics_buffer_size': self.metrics_buffer.qsize(),
                    'workers_running': all([
                        self.system_worker.is_alive(),
                        self.tenant_worker.is_alive(),
                        self.processing_worker.is_alive(),
                        self.alert_worker.is_alive()
                    ])
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération santé système: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # Méthodes privées
    
    def _validate_metric(self, metric: PerformanceMetric) -> bool:
        """Validation d'une métrique"""
        try:
            if not metric.tenant_id:
                return False
            if not metric.metric_name:
                return False
            if not isinstance(metric.value, (int, float)):
                return False
            return True
        except Exception:
            return False
    
    def _update_prometheus_metrics(self, metric: PerformanceMetric):
        """Mise à jour des métriques Prometheus"""
        try:
            if metric.metric_name == "response_time":
                self.request_duration.labels(
                    tenant_id=metric.tenant_id,
                    service=metric.service_name or "unknown",
                    method=metric.labels.get('method', 'unknown')
                ).observe(metric.value / 1000.0)
            
            elif metric.metric_name == "error_rate":
                self.error_rate.labels(
                    tenant_id=metric.tenant_id,
                    service=metric.service_name or "unknown"
                ).set(metric.value)
            
            elif metric.metric_name == "active_users":
                self.active_users.labels(
                    tenant_id=metric.tenant_id
                ).set(metric.value)
            
            elif metric.metric_name in ["cpu_usage", "memory_usage", "disk_usage"]:
                self.resource_usage.labels(
                    tenant_id=metric.tenant_id,
                    resource_type=metric.metric_name.split('_')[0]
                ).set(metric.value)
                
        except Exception as e:
            logger.error(f"Erreur mise à jour Prometheus: {e}")
    
    def _update_tenant_cache(self, metric: PerformanceMetric):
        """Mise à jour du cache tenant"""
        try:
            if metric.tenant_id not in self.tenant_cache:
                self.tenant_cache[metric.tenant_id] = {}
            
            self.tenant_cache[metric.tenant_id][metric.metric_name] = metric.value
            self.tenant_cache[metric.tenant_id]['last_update'] = metric.timestamp.isoformat()
            
        except Exception as e:
            logger.error(f"Erreur mise à jour cache tenant: {e}")
    
    def _system_metrics_worker(self):
        """Worker de collecte des métriques système"""
        while self.running:
            try:
                # Collecte des métriques système
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Mise à jour des métriques globales
                self.system_metrics.update({
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                })
                
                # Vérification des seuils système
                self._check_system_thresholds()
                
                time.sleep(self.config.get('collection_interval_seconds', 10))
                
            except Exception as e:
                logger.error(f"Erreur worker métriques système: {e}")
                time.sleep(10)
    
    def _tenant_metrics_worker(self):
        """Worker de collecte des métriques tenant"""
        while self.running:
            try:
                # Collecte des métriques par tenant depuis Redis
                for tenant_id in self._get_active_tenants():
                    tenant_metrics = self._collect_tenant_metrics(tenant_id)
                    
                    for metric_name, value in tenant_metrics.items():
                        metric = PerformanceMetric(
                            metric_name=metric_name,
                            metric_type=MetricType.GAUGE,
                            value=value,
                            timestamp=datetime.utcnow(),
                            tenant_id=tenant_id,
                            service_name=None,
                            instance_id=None,
                            labels={},
                            unit=""
                        )
                        
                        try:
                            self.metrics_buffer.put(metric, timeout=0.1)
                        except queue.Full:
                            pass  # Ignore si buffer plein
                
                time.sleep(self.config.get('collection_interval_seconds', 10))
                
            except Exception as e:
                logger.error(f"Erreur worker métriques tenant: {e}")
                time.sleep(10)
    
    def _metrics_processing_worker(self):
        """Worker de traitement des métriques"""
        batch = []
        batch_size = self.config.get('batch_size', 100)
        
        while self.running:
            try:
                # Récupération des métriques par batch
                try:
                    metric = self.metrics_buffer.get(timeout=1)
                    batch.append(metric)
                except queue.Empty:
                    if batch:
                        self._process_metrics_batch(batch)
                        batch = []
                    continue
                
                # Traitement si batch plein
                if len(batch) >= batch_size:
                    self._process_metrics_batch(batch)
                    batch = []
                
            except Exception as e:
                logger.error(f"Erreur worker traitement métriques: {e}")
                time.sleep(1)
    
    def _alert_processing_worker(self):
        """Worker de traitement des alertes"""
        while self.running:
            try:
                # Vérification des règles d'alerte pour chaque tenant
                for tenant_id in self._get_active_tenants():
                    self._check_alert_rules(tenant_id)
                
                # Nettoyage des alertes anciennes
                self._cleanup_old_alerts()
                
                time.sleep(30)  # Vérification toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Erreur worker alertes: {e}")
                time.sleep(30)
    
    def _get_active_tenants(self) -> List[str]:
        """Récupération de la liste des tenants actifs"""
        try:
            # Récupération depuis Redis
            tenant_keys = self.redis_client.keys("tenant:*:metrics")
            tenant_ids = [key.split(':')[1] for key in tenant_keys]
            return tenant_ids
        except Exception as e:
            logger.error(f"Erreur récupération tenants actifs: {e}")
            return []
    
    def _collect_tenant_metrics(self, tenant_id: str) -> Dict[str, float]:
        """Collecte des métriques d'un tenant"""
        try:
            # Récupération depuis Redis
            metrics_key = f"tenant:{tenant_id}:metrics"
            metrics_data = self.redis_client.hgetall(metrics_key)
            
            # Conversion en float
            metrics = {}
            for key, value in metrics_data.items():
                try:
                    metrics[key] = float(value)
                except (ValueError, TypeError):
                    continue
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur collecte métriques tenant {tenant_id}: {e}")
            return {}
    
    def _process_metrics_batch(self, metrics: List[PerformanceMetric]):
        """Traitement d'un batch de métriques"""
        try:
            # Stockage en base de données
            self._store_metrics_to_db(metrics)
            
            # Mise à jour des agrégations
            self._update_metric_aggregations(metrics)
            
            # Vérification des seuils
            for metric in metrics:
                self._check_metric_thresholds(metric)
            
        except Exception as e:
            logger.error(f"Erreur traitement batch métriques: {e}")
    
    def _store_metrics_to_db(self, metrics: List[PerformanceMetric]):
        """Stockage des métriques en base de données"""
        try:
            # Implémentation simplifiée - à adapter selon votre schema
            # INSERT INTO performance_metrics (tenant_id, metric_name, value, timestamp, ...)
            pass
        except Exception as e:
            logger.error(f"Erreur stockage métriques DB: {e}")
    
    def _check_system_thresholds(self):
        """Vérification des seuils système"""
        try:
            thresholds = self.config.get('thresholds', {})
            
            # CPU
            if self.system_metrics['cpu_percent'] > thresholds.get('cpu_usage_percent', 80):
                self._create_system_alert('cpu_usage', self.system_metrics['cpu_percent'])
            
            # Mémoire
            if self.system_metrics['memory_percent'] > thresholds.get('memory_usage_percent', 85):
                self._create_system_alert('memory_usage', self.system_metrics['memory_percent'])
            
            # Disque
            if self.system_metrics['disk_percent'] > thresholds.get('disk_usage_percent', 90):
                self._create_system_alert('disk_usage', self.system_metrics['disk_percent'])
                
        except Exception as e:
            logger.error(f"Erreur vérification seuils système: {e}")
    
    def _check_metric_thresholds(self, metric: PerformanceMetric):
        """Vérification des seuils pour une métrique"""
        try:
            thresholds = self.config.get('thresholds', {})
            threshold_key = f"{metric.metric_name}_{metric.unit}" if metric.unit else metric.metric_name
            
            if threshold_key in thresholds:
                threshold_value = thresholds[threshold_key]
                
                if metric.value > threshold_value:
                    self._create_metric_alert(metric, threshold_value)
                    
        except Exception as e:
            logger.error(f"Erreur vérification seuil métrique: {e}")
    
    def _create_system_alert(self, metric_name: str, value: float):
        """Création d'une alerte système"""
        alert_id = f"system_alert_{metric_name}_{int(time.time())}"
        
        alert = Alert(
            alert_id=alert_id,
            tenant_id="system",
            metric_name=metric_name,
            current_value=value,
            threshold_value=self.config.get('thresholds', {}).get(f'{metric_name}_percent', 80),
            level=AlertLevel.CRITICAL if value > 95 else AlertLevel.WARNING,
            message=f"System {metric_name} is {value}%",
            timestamp=datetime.utcnow(),
            resolved=False,
            resolution_timestamp=None,
            metadata={'system_alert': True}
        )
        
        self.alerts[alert_id] = alert
    
    def _create_metric_alert(self, metric: PerformanceMetric, threshold: float):
        """Création d'une alerte métrique"""
        alert_id = f"metric_alert_{metric.tenant_id}_{metric.metric_name}_{int(time.time())}"
        
        # Vérification du cooldown
        if self._is_alert_in_cooldown(metric.tenant_id, metric.metric_name):
            return
        
        alert = Alert(
            alert_id=alert_id,
            tenant_id=metric.tenant_id,
            metric_name=metric.metric_name,
            current_value=metric.value,
            threshold_value=threshold,
            level=AlertLevel.WARNING,
            message=f"{metric.metric_name} for tenant {metric.tenant_id} is {metric.value} (threshold: {threshold})",
            timestamp=datetime.utcnow(),
            resolved=False,
            resolution_timestamp=None,
            metadata={'service': metric.service_name, 'labels': metric.labels}
        )
        
        self.alerts[alert_id] = alert
        
        # Enregistrement du cooldown
        self._set_alert_cooldown(metric.tenant_id, metric.metric_name)
    
    def _is_alert_in_cooldown(self, tenant_id: str, metric_name: str) -> bool:
        """Vérification du cooldown d'alerte"""
        try:
            cooldown_key = f"alert_cooldown:{tenant_id}:{metric_name}"
            return self.redis_client.exists(cooldown_key)
        except Exception:
            return False
    
    def _set_alert_cooldown(self, tenant_id: str, metric_name: str):
        """Définition du cooldown d'alerte"""
        try:
            cooldown_key = f"alert_cooldown:{tenant_id}:{metric_name}"
            cooldown_minutes = self.config.get('alert_cooldown_minutes', 5)
            self.redis_client.setex(cooldown_key, cooldown_minutes * 60, "1")
        except Exception as e:
            logger.error(f"Erreur définition cooldown alerte: {e}")
    
    def _check_alert_rules(self, tenant_id: str):
        """Vérification des règles d'alerte pour un tenant"""
        try:
            # Récupération des règles
            rules_key = f"alert_rules:{tenant_id}"
            rules_data = self.redis_client.hgetall(rules_key)
            
            for rule_id, rule_json in rules_data.items():
                rule = json.loads(rule_json)
                
                if not rule.get('enabled', True):
                    continue
                
                # Récupération de la métrique actuelle
                current_value = self.tenant_cache.get(tenant_id, {}).get(rule['metric_name'])
                
                if current_value is not None:
                    # Évaluation de la condition
                    if self._evaluate_alert_condition(current_value, rule['threshold'], rule['comparison']):
                        self._trigger_alert_rule(tenant_id, rule, current_value)
                        
        except Exception as e:
            logger.error(f"Erreur vérification règles alerte tenant {tenant_id}: {e}")
    
    def _evaluate_alert_condition(self, value: float, threshold: float, comparison: str) -> bool:
        """Évaluation d'une condition d'alerte"""
        try:
            if comparison == '>':
                return value > threshold
            elif comparison == '<':
                return value < threshold
            elif comparison == '>=':
                return value >= threshold
            elif comparison == '<=':
                return value <= threshold
            elif comparison == '==':
                return value == threshold
            else:
                return False
        except Exception:
            return False
    
    def _trigger_alert_rule(self, tenant_id: str, rule: Dict[str, Any], current_value: float):
        """Déclenchement d'une règle d'alerte"""
        try:
            # Vérification du cooldown
            if self._is_alert_in_cooldown(tenant_id, rule['metric_name']):
                return
            
            alert_id = f"rule_alert_{rule['rule_id']}_{int(time.time())}"
            
            alert = Alert(
                alert_id=alert_id,
                tenant_id=tenant_id,
                metric_name=rule['metric_name'],
                current_value=current_value,
                threshold_value=rule['threshold'],
                level=AlertLevel(rule['level']),
                message=f"Alert rule triggered: {rule['metric_name']} is {current_value} (threshold: {rule['threshold']} {rule['comparison']})",
                timestamp=datetime.utcnow(),
                resolved=False,
                resolution_timestamp=None,
                metadata=rule.get('metadata', {})
            )
            
            self.alerts[alert_id] = alert
            self._set_alert_cooldown(tenant_id, rule['metric_name'])
            
        except Exception as e:
            logger.error(f"Erreur déclenchement règle alerte: {e}")
    
    def _cleanup_old_alerts(self):
        """Nettoyage des alertes anciennes"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            
            alerts_to_remove = []
            for alert_id, alert in self.alerts.items():
                if alert.resolved and alert.resolution_timestamp and alert.resolution_timestamp < cutoff_time:
                    alerts_to_remove.append(alert_id)
            
            for alert_id in alerts_to_remove:
                del self.alerts[alert_id]
                
        except Exception as e:
            logger.error(f"Erreur nettoyage alertes anciennes: {e}")
    
    async def _fetch_metrics_from_db(self, tenant_id: str, start_time: datetime,
                                   end_time: datetime, metric_names: Optional[List[str]]) -> Dict[str, List[float]]:
        """Récupération des métriques depuis la base de données"""
        try:
            # Implémentation simplifiée
            # SELECT * FROM performance_metrics WHERE tenant_id = ? AND timestamp BETWEEN ? AND ?
            return {}
        except Exception as e:
            logger.error(f"Erreur récupération métriques DB: {e}")
            return {}
    
    def _calculate_metrics_statistics(self, metrics: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calcul des statistiques des métriques"""
        try:
            stats = {}
            
            for metric_name, values in metrics.items():
                if values:
                    stats[metric_name] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'mean': statistics.mean(values),
                        'median': statistics.median(values),
                        'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur calcul statistiques métriques: {e}")
            return {}
    
    def _calculate_performance_score(self, metrics_data: Dict[str, Any], alerts: List[Alert]) -> float:
        """Calcul du score de performance"""
        try:
            base_score = 100.0
            
            # Pénalités pour les alertes
            for alert in alerts:
                if alert.level == AlertLevel.CRITICAL:
                    base_score -= 20
                elif alert.level == AlertLevel.WARNING:
                    base_score -= 10
                elif alert.level == AlertLevel.INFO:
                    base_score -= 5
            
            # Pénalités pour les métriques dégradées
            stats = metrics_data.get('statistics', {})
            for metric_name, metric_stats in stats.items():
                if 'response_time' in metric_name and metric_stats['mean'] > 1000:  # > 1s
                    base_score -= 15
                elif 'error_rate' in metric_name and metric_stats['mean'] > 5:  # > 5%
                    base_score -= 25
            
            return max(0.0, min(100.0, base_score))
            
        except Exception as e:
            logger.error(f"Erreur calcul score performance: {e}")
            return 50.0
    
    async def _analyze_performance_trends(self, tenant_id: str, start_time: datetime,
                                        end_time: datetime) -> Dict[str, Any]:
        """Analyse des tendances de performance"""
        try:
            # Récupération des données historiques
            historical_data = await self._fetch_metrics_from_db(
                tenant_id, start_time - timedelta(days=7), end_time, None
            )
            
            trends = {}
            
            # Analyse simple des tendances (à améliorer avec des algorithmes plus sophistiqués)
            for metric_name, values in historical_data.items():
                if len(values) >= 2:
                    # Calcul de la pente de régression linéaire simplifiée
                    first_half = values[:len(values)//2]
                    second_half = values[len(values)//2:]
                    
                    if first_half and second_half:
                        first_avg = statistics.mean(first_half)
                        second_avg = statistics.mean(second_half)
                        
                        if first_avg != 0:
                            trend_percent = ((second_avg - first_avg) / first_avg) * 100
                            
                            trends[metric_name] = {
                                'trend_percent': round(trend_percent, 2),
                                'direction': 'increasing' if trend_percent > 5 else 'decreasing' if trend_percent < -5 else 'stable'
                            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Erreur analyse tendances: {e}")
            return {}
    
    def _generate_recommendations(self, metrics_data: Dict[str, Any], alerts: List[Alert],
                                trends: Dict[str, Any]) -> List[str]:
        """Génération de recommandations"""
        try:
            recommendations = []
            
            # Recommandations basées sur les alertes
            critical_alerts = [a for a in alerts if a.level == AlertLevel.CRITICAL]
            if critical_alerts:
                recommendations.append("Attention immédiate requise pour les alertes critiques")
            
            # Recommandations basées sur les tendances
            for metric_name, trend_info in trends.items():
                if trend_info['direction'] == 'increasing' and 'error_rate' in metric_name:
                    recommendations.append(f"Surveillance accrue recommandée pour {metric_name}")
                elif trend_info['direction'] == 'increasing' and 'response_time' in metric_name:
                    recommendations.append(f"Optimisation de performance recommandée pour {metric_name}")
            
            # Recommandations générales
            stats = metrics_data.get('statistics', {})
            if any('response_time' in metric and metric_stats['mean'] > 500 for metric, metric_stats in stats.items()):
                recommendations.append("Optimisation du temps de réponse recommandée")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {e}")
            return []
    
    def _update_metric_aggregations(self, metrics: List[PerformanceMetric]):
        """Mise à jour des agrégations de métriques"""
        try:
            # Groupement par tenant et métrique
            tenant_metrics = {}
            
            for metric in metrics:
                if metric.tenant_id not in tenant_metrics:
                    tenant_metrics[metric.tenant_id] = {}
                
                if metric.metric_name not in tenant_metrics[metric.tenant_id]:
                    tenant_metrics[metric.tenant_id][metric.metric_name] = []
                
                tenant_metrics[metric.tenant_id][metric.metric_name].append(metric.value)
            
            # Calcul et stockage des agrégations
            for tenant_id, metrics_dict in tenant_metrics.items():
                for metric_name, values in metrics_dict.items():
                    if values:
                        avg_value = statistics.mean(values)
                        
                        # Stockage dans Redis avec TTL
                        aggregation_key = f"tenant:{tenant_id}:aggregations:{metric_name}"
                        self.redis_client.setex(
                            aggregation_key,
                            3600,  # TTL 1 heure
                            json.dumps({
                                'avg': avg_value,
                                'count': len(values),
                                'timestamp': datetime.utcnow().isoformat()
                            })
                        )
                        
        except Exception as e:
            logger.error(f"Erreur mise à jour agrégations: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        🏥 Vérification de santé du service
        
        Returns:
            État de santé du service
        """
        try:
            health_status = {
                'service': 'tenant_performance_monitor',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {}
            }
            
            # Vérification workers
            workers_status = {
                'system_worker': self.system_worker.is_alive(),
                'tenant_worker': self.tenant_worker.is_alive(),
                'processing_worker': self.processing_worker.is_alive(),
                'alert_worker': self.alert_worker.is_alive()
            }
            
            health_status['checks']['workers'] = workers_status
            if not all(workers_status.values()):
                health_status['status'] = 'degraded'
            
            # Vérification buffer
            buffer_size = self.metrics_buffer.qsize()
            health_status['checks']['buffer_size'] = buffer_size
            if buffer_size > 8000:  # 80% de la capacité
                health_status['status'] = 'degraded'
            
            # Vérification Redis
            try:
                self.redis_client.ping()
                health_status['checks']['redis'] = 'healthy'
            except Exception as e:
                health_status['checks']['redis'] = f'unhealthy: {e}'
                health_status['status'] = 'degraded'
            
            # Métriques système
            health_status['checks']['system_metrics'] = self.system_metrics
            
            return health_status
            
        except Exception as e:
            logger.error(f"Erreur health check: {e}")
            return {
                'service': 'tenant_performance_monitor',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def shutdown(self):
        """Arrêt propre du service"""
        logger.info("Arrêt du service de monitoring de performance")
        self.running = False
        
        # Traitement des métriques restantes
        remaining_metrics = []
        while not self.metrics_buffer.empty():
            try:
                metric = self.metrics_buffer.get_nowait()
                remaining_metrics.append(metric)
            except queue.Empty:
                break
        
        if remaining_metrics:
            self._process_metrics_batch(remaining_metrics)
        
        # Attendre l'arrêt des workers
        for worker in [self.system_worker, self.tenant_worker, self.processing_worker, self.alert_worker]:
            if worker.is_alive():
                worker.join(timeout=5)


# Factory function pour l'initialisation
def create_tenant_performance_monitor(config_path: Optional[str] = None) -> TenantPerformanceMonitor:
    """
    🏭 Factory pour créer une instance du moniteur de performance
    
    Args:
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        Instance configurée du TenantPerformanceMonitor
    """
    return TenantPerformanceMonitor(config_path or '/etc/ainflue/performance_config.yaml')


# Exemple d'utilisation
if __name__ == "__main__":
    async def main():
        # Création du moniteur
        monitor = create_tenant_performance_monitor()
        
        # Enregistrement de métriques de requête
        await monitor.record_request_metrics(
            tenant_id="tenant_123",
            service="api",
            method="GET",
            duration_ms=150,
            status_code=200
        )
        
        # Création d'une règle d'alerte
        alert_rule_id = await monitor.create_alert_rule(
            tenant_id="tenant_123",
            metric_name="response_time",
            threshold=500,
            comparison=">",
            level=AlertLevel.WARNING
        )
        
        print(f"Règle d'alerte créée: {alert_rule_id}")
        
        # Récupération des métriques
        metrics = await monitor.get_tenant_metrics("tenant_123")
        print(f"Métriques: {metrics}")
        
        # Génération d'un rapport de performance
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        report = await monitor.get_performance_report("tenant_123", start_time, end_time)
        print(f"Score de performance: {report.performance_score}")
        
        # État de santé du système
        health = await monitor.get_system_health()
        print(f"Santé système: {health['status']}")
    
    asyncio.run(main())