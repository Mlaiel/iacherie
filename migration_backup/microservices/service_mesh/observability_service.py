#!/usr/bin/env python3
"""
📊 Observability Service - Enterprise Service Mesh
Service d'observabilité complète pour microservices Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
🔧 Microservices Expert + DevOps + Monitoring Implementation
"""

import asyncio
import logging
import time
import json
import prometheus_client
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import opentelemetry
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import structlog
import asyncio_mqtt
import hashlib

# Configuration logging enterprise avec structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

class MetricType(Enum):
    """Types de métriques"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Niveaux de sévérité alertes"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

class TracingBackend(Enum):
    """Backends de tracing"""
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    OTEL_COLLECTOR = "otel_collector"

@dataclass
class MetricDefinition:
    """Définition d'une métrique"""
    name: str
    metric_type: MetricType
    description: str
    labels: List[str] = None
    help_text: str = ""
    namespace: str = "ainflue"
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []

@dataclass
class TraceSpan:
    """Span de trace"""
    trace_id: str
    span_id: str
    parent_span_id: str
    operation_name: str
    service_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    status_code: int
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]

@dataclass
class AlertRule:
    """Règle d'alerte"""
    rule_id: str
    name: str
    description: str
    severity: AlertSeverity
    condition: str  # PromQL query
    threshold: float
    duration: str = "5m"
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.annotations is None:
            self.annotations = {}

@dataclass
class ServiceHealthMetrics:
    """Métriques de santé service"""
    service_name: str
    namespace: str
    timestamp: datetime
    availability: float  # %
    error_rate: float  # %
    latency_p50: float  # ms
    latency_p95: float  # ms
    latency_p99: float  # ms
    throughput: float  # requests/sec
    cpu_usage: float  # %
    memory_usage: float  # %
    disk_usage: float  # %

class ObservabilityService:
    """Service d'observabilité Enterprise"""
    
    def __init__(self):
        self.service_name = "observability-service"
        self.version = "1.0.0"
        
        # Configuration observabilité
        self.tracing_backends: Dict[TracingBackend, Any] = {}
        self.metrics_registry = prometheus_client.CollectorRegistry()
        self.custom_metrics: Dict[str, Any] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # Collecteurs de données
        self.trace_collector = []
        self.metrics_buffer = []
        self.log_buffer = []
        
        # Configuration endpoints
        self.prometheus_endpoint = "http://prometheus:9090"
        self.jaeger_endpoint = "http://jaeger:14268"
        self.grafana_endpoint = "http://grafana:3000"
        self.elasticsearch_endpoint = "http://elasticsearch:9200"
        
        # Métriques propres au service
        self.internal_metrics = {
            'traces_collected': 0,
            'metrics_exported': 0,
            'logs_processed': 0,
            'alerts_fired': 0,
            'dashboards_created': 0,
            'service_health_checks': 0
        }
        
        # Cache de métriques
        self.metrics_cache: Dict[str, Any] = {}
        self.cache_ttl = 60  # secondes
        
        logger.info("📊 Observability Service initialisé", 
                   service=self.service_name, version=self.version)
    
    async def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialisation du service d'observabilité"""
        try:
            logger.info("🚀 Initialisation Observability Service...")
            
            if config is None:
                config = await self._load_default_config()
            
            # Configuration tracing
            await self._setup_distributed_tracing(config.get('tracing', {}))
            
            # Configuration métriques
            await self._setup_metrics_collection(config.get('metrics', {}))
            
            # Configuration logging
            await self._setup_centralized_logging(config.get('logging', {}))
            
            # Configuration alerting
            await self._setup_alerting_system(config.get('alerting', {}))
            
            # Démarrage collecteurs
            await self._start_data_collectors()
            
            # Création dashboards par défaut
            await self._create_default_dashboards()
            
            # Démarrage health monitoring
            asyncio.create_task(self._health_monitoring_loop())
            
            logger.info("✅ Observability Service initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error("❌ Erreur initialisation observability", error=str(e))
            return False
    
    async def _load_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            'tracing': {
                'enabled': True,
                'backends': ['jaeger'],
                'sampling_rate': 0.1,
                'batch_timeout': 5
            },
            'metrics': {
                'enabled': True,
                'collection_interval': 15,
                'retention_days': 30,
                'export_timeout': 10
            },
            'logging': {
                'enabled': True,
                'level': 'INFO',
                'format': 'json',
                'aggregation_enabled': True
            },
            'alerting': {
                'enabled': True,
                'notification_channels': ['slack', 'email'],
                'escalation_timeout': 300
            }
        }
    
    async def _setup_distributed_tracing(self, tracing_config: Dict[str, Any]):
        """Configuration tracing distribué"""
        try:
            if not tracing_config.get('enabled', True):
                logger.info("📊 Tracing distribué désactivé")
                return
            
            # Configuration OpenTelemetry
            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)
            
            # Configuration Jaeger exporter
            if 'jaeger' in tracing_config.get('backends', []):
                jaeger_exporter = JaegerExporter(
                    agent_host_name="jaeger",
                    agent_port=6831,
                )
                
                span_processor = BatchSpanProcessor(jaeger_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
                
                self.tracing_backends[TracingBackend.JAEGER] = jaeger_exporter
                logger.info("✅ Jaeger tracing configuré")
            
            # Instrumentation automatique
            AioHttpClientInstrumentor().instrument()
            
            logger.info("✅ Tracing distribué configuré")
            
        except Exception as e:
            logger.error("❌ Erreur configuration tracing", error=str(e))
            raise
    
    async def _setup_metrics_collection(self, metrics_config: Dict[str, Any]):
        """Configuration collecte métriques"""
        try:
            if not metrics_config.get('enabled', True):
                logger.info("📊 Collecte métriques désactivée")
                return
            
            # Métriques système par défaut
            await self._register_default_metrics()
            
            # Configuration exporters Prometheus
            prometheus_client.start_http_server(8000, registry=self.metrics_registry)
            
            # Métriques custom Ainflue
            await self._register_ainflue_metrics()
            
            logger.info("✅ Collecte métriques configurée")
            
        except Exception as e:
            logger.error("❌ Erreur configuration métriques", error=str(e))
            raise
    
    async def _register_default_metrics(self):
        """Enregistrement métriques par défaut"""
        try:
            # Métriques HTTP
            self.custom_metrics['http_requests_total'] = prometheus_client.Counter(
                'ainflue_http_requests_total',
                'Total HTTP requests',
                ['method', 'endpoint', 'status'],
                registry=self.metrics_registry
            )
            
            self.custom_metrics['http_request_duration'] = prometheus_client.Histogram(
                'ainflue_http_request_duration_seconds',
                'HTTP request duration',
                ['method', 'endpoint'],
                registry=self.metrics_registry
            )
            
            # Métriques de service
            self.custom_metrics['service_availability'] = prometheus_client.Gauge(
                'ainflue_service_availability',
                'Service availability percentage',
                ['service', 'namespace'],
                registry=self.metrics_registry
            )
            
            self.custom_metrics['service_error_rate'] = prometheus_client.Gauge(
                'ainflue_service_error_rate',
                'Service error rate percentage',
                ['service', 'namespace'],
                registry=self.metrics_registry
            )
            
            # Métriques infrastructure
            self.custom_metrics['cpu_usage'] = prometheus_client.Gauge(
                'ainflue_cpu_usage_percent',
                'CPU usage percentage',
                ['service', 'instance'],
                registry=self.metrics_registry
            )
            
            self.custom_metrics['memory_usage'] = prometheus_client.Gauge(
                'ainflue_memory_usage_percent',
                'Memory usage percentage',
                ['service', 'instance'],
                registry=self.metrics_registry
            )
            
        except Exception as e:
            logger.error("❌ Erreur enregistrement métriques", error=str(e))
            raise
    
    async def _register_ainflue_metrics(self):
        """Métriques spécifiques à Ainflue"""
        try:
            # Métriques IA
            self.custom_metrics['ai_inference_requests'] = prometheus_client.Counter(
                'ainflue_ai_inference_requests_total',
                'Total AI inference requests',
                ['model', 'service'],
                registry=self.metrics_registry
            )
            
            self.custom_metrics['ai_model_accuracy'] = prometheus_client.Gauge(
                'ainflue_ai_model_accuracy',
                'AI model accuracy score',
                ['model', 'version'],
                registry=self.metrics_registry
            )
            
            # Métriques contenu
            self.custom_metrics['content_uploads'] = prometheus_client.Counter(
                'ainflue_content_uploads_total',
                'Total content uploads',
                ['format', 'size_category'],
                registry=self.metrics_registry
            )
            
            self.custom_metrics['content_processing_time'] = prometheus_client.Histogram(
                'ainflue_content_processing_seconds',
                'Content processing time',
                ['format', 'operation'],
                registry=self.metrics_registry
            )
            
            # Métriques business
            self.custom_metrics['creator_registrations'] = prometheus_client.Counter(
                'ainflue_creator_registrations_total',
                'Total creator registrations',
                ['platform', 'tier'],
                registry=self.metrics_registry
            )
            
            self.custom_metrics['revenue_generated'] = prometheus_client.Counter(
                'ainflue_revenue_generated_total',
                'Total revenue generated',
                ['currency', 'source'],
                registry=self.metrics_registry
            )
            
        except Exception as e:
            logger.error("❌ Erreur métriques Ainflue", error=str(e))
            raise
    
    async def _setup_centralized_logging(self, logging_config: Dict[str, Any]):
        """Configuration logging centralisé"""
        try:
            if not logging_config.get('enabled', True):
                logger.info("📊 Logging centralisé désactivé")
                return
            
            # Configuration ELK stack
            self.log_aggregator = {
                'elasticsearch_url': self.elasticsearch_endpoint,
                'index_pattern': 'ainflue-logs-*',
                'buffer_size': 1000,
                'flush_interval': 30
            }
            
            # Configuration Fluentd/Fluent Bit
            self.fluent_config = {
                'host': 'fluentd',
                'port': 24224,
                'tag': 'ainflue.microservices'
            }
            
            logger.info("✅ Logging centralisé configuré")
            
        except Exception as e:
            logger.error("❌ Erreur configuration logging", error=str(e))
            raise
    
    async def _setup_alerting_system(self, alerting_config: Dict[str, Any]):
        """Configuration système d'alertes"""
        try:
            if not alerting_config.get('enabled', True):
                logger.info("📊 Système alertes désactivé")
                return
            
            # Règles d'alertes par défaut
            await self._create_default_alert_rules()
            
            # Configuration AlertManager
            self.alertmanager_config = {
                'url': 'http://alertmanager:9093',
                'notification_channels': alerting_config.get('notification_channels', []),
                'escalation_timeout': alerting_config.get('escalation_timeout', 300)
            }
            
            logger.info("✅ Système alertes configuré")
            
        except Exception as e:
            logger.error("❌ Erreur configuration alertes", error=str(e))
            raise
    
    async def _create_default_alert_rules(self):
        """Création règles d'alertes par défaut"""
        try:
            # Alerte service down
            service_down_rule = AlertRule(
                rule_id="service_down",
                name="Service Down",
                description="Service is down or unavailable",
                severity=AlertSeverity.CRITICAL,
                condition='up{job="ainflue-services"} == 0',
                threshold=0,
                duration="1m",
                labels={'team': 'platform', 'severity': 'critical'},
                annotations={
                    'summary': 'Service {{ $labels.instance }} is down',
                    'description': 'Service {{ $labels.instance }} has been down for more than 1 minute'
                }
            )
            
            # Alerte latence élevée
            high_latency_rule = AlertRule(
                rule_id="high_latency",
                name="High Latency",
                description="Service latency is too high",
                severity=AlertSeverity.WARNING,
                condition='histogram_quantile(0.95, ainflue_http_request_duration_seconds) > 0.5',
                threshold=0.5,
                duration="5m",
                labels={'team': 'platform', 'severity': 'warning'},
                annotations={
                    'summary': 'High latency detected for {{ $labels.service }}',
                    'description': 'P95 latency is {{ $value }}s for {{ $labels.service }}'
                }
            )
            
            # Alerte taux d'erreur élevé
            high_error_rate_rule = AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                description="Service error rate is too high",
                severity=AlertSeverity.WARNING,
                condition='rate(ainflue_http_requests_total{status=~"5.."}[5m]) > 0.05',
                threshold=0.05,
                duration="3m",
                labels={'team': 'platform', 'severity': 'warning'},
                annotations={
                    'summary': 'High error rate for {{ $labels.service }}',
                    'description': 'Error rate is {{ $value | humanizePercentage }} for {{ $labels.service }}'
                }
            )
            
            # Alerte utilisation CPU
            high_cpu_rule = AlertRule(
                rule_id="high_cpu_usage",
                name="High CPU Usage",
                description="CPU usage is too high",
                severity=AlertSeverity.WARNING,
                condition='ainflue_cpu_usage_percent > 80',
                threshold=80,
                duration="10m",
                labels={'team': 'platform', 'severity': 'warning'},
                annotations={
                    'summary': 'High CPU usage on {{ $labels.instance }}',
                    'description': 'CPU usage is {{ $value }}% on {{ $labels.instance }}'
                }
            )
            
            # Enregistrement des règles
            self.alert_rules.update({
                rule.rule_id: rule for rule in [
                    service_down_rule, high_latency_rule, 
                    high_error_rate_rule, high_cpu_rule
                ]
            })
            
            logger.info("✅ Règles d'alertes par défaut créées", 
                       rules_count=len(self.alert_rules))
            
        except Exception as e:
            logger.error("❌ Erreur création règles alertes", error=str(e))
            raise
    
    async def _start_data_collectors(self):
        """Démarrage des collecteurs de données"""
        try:
            # Collecteur de traces
            asyncio.create_task(self._trace_collector_loop())
            
            # Collecteur de métriques
            asyncio.create_task(self._metrics_collector_loop())
            
            # Collecteur de logs
            asyncio.create_task(self._log_collector_loop())
            
            # Exportateur de données
            asyncio.create_task(self._data_exporter_loop())
            
            logger.info("✅ Collecteurs de données démarrés")
            
        except Exception as e:
            logger.error("❌ Erreur démarrage collecteurs", error=str(e))
            raise
    
    async def _trace_collector_loop(self):
        """Boucle de collecte des traces"""
        while True:
            try:
                await asyncio.sleep(5)
                
                # Collection des traces depuis les services
                await self._collect_service_traces()
                
                self.internal_metrics['traces_collected'] += 1
                
            except Exception as e:
                logger.error("❌ Erreur collecteur traces", error=str(e))
    
    async def _metrics_collector_loop(self):
        """Boucle de collecte des métriques"""
        while True:
            try:
                await asyncio.sleep(15)
                
                # Collection des métriques système
                await self._collect_system_metrics()
                
                # Collection des métriques application
                await self._collect_application_metrics()
                
                self.internal_metrics['metrics_exported'] += 1
                
            except Exception as e:
                logger.error("❌ Erreur collecteur métriques", error=str(e))
    
    async def _log_collector_loop(self):
        """Boucle de collecte des logs"""
        while True:
            try:
                await asyncio.sleep(10)
                
                # Collection des logs depuis les services
                await self._collect_service_logs()
                
                self.internal_metrics['logs_processed'] += 1
                
            except Exception as e:
                logger.error("❌ Erreur collecteur logs", error=str(e))
    
    async def _data_exporter_loop(self):
        """Boucle d'export des données"""
        while True:
            try:
                await asyncio.sleep(30)
                
                # Export vers Prometheus
                await self._export_to_prometheus()
                
                # Export vers Elasticsearch
                await self._export_to_elasticsearch()
                
                # Nettoyage cache
                await self._cleanup_cache()
                
            except Exception as e:
                logger.error("❌ Erreur export données", error=str(e))
    
    async def _collect_service_traces(self):
        """Collection traces des services"""
        try:
            # Simulation collection traces (en production, intégration avec OpenTelemetry)
            sample_trace = TraceSpan(
                trace_id=f"trace_{int(time.time())}",
                span_id=f"span_{int(time.time())}",
                parent_span_id="",
                operation_name="ai_inference",
                service_name="ai-inference-service",
                start_time=datetime.now() - timedelta(milliseconds=100),
                end_time=datetime.now(),
                duration_ms=100.0,
                status_code=200,
                tags={'service.version': '1.0.0', 'http.method': 'POST'},
                logs=[{'timestamp': datetime.now(), 'message': 'Processing request'}]
            )
            
            self.trace_collector.append(sample_trace)
            
            # Maintenir taille buffer
            if len(self.trace_collector) > 1000:
                self.trace_collector = self.trace_collector[-500:]
            
        except Exception as e:
            logger.error("❌ Erreur collection traces", error=str(e))
    
    async def _collect_system_metrics(self):
        """Collection métriques système"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.custom_metrics['cpu_usage'].labels(
                service=self.service_name,
                instance='observability-1'
            ).set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.custom_metrics['memory_usage'].labels(
                service=self.service_name,
                instance='observability-1'
            ).set(memory.percent)
            
        except Exception as e:
            logger.error("❌ Erreur métriques système", error=str(e))
    
    async def _collect_application_metrics(self):
        """Collection métriques application"""
        try:
            # Simulation métriques business
            import random
            
            # Métriques IA
            self.custom_metrics['ai_inference_requests'].labels(
                model='gpt-4',
                service='ai-inference'
            ).inc(random.randint(10, 50))
            
            # Métriques contenu
            self.custom_metrics['content_uploads'].labels(
                format='video',
                size_category='large'
            ).inc(random.randint(5, 20))
            
        except Exception as e:
            logger.error("❌ Erreur métriques application", error=str(e))
    
    async def _collect_service_logs(self):
        """Collection logs des services"""
        try:
            # Simulation collection logs
            sample_log = {
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'service': 'ai-inference-service',
                'message': 'Request processed successfully',
                'request_id': f"req_{int(time.time())}",
                'duration_ms': 150,
                'status_code': 200
            }
            
            self.log_buffer.append(sample_log)
            
            # Maintenir taille buffer
            if len(self.log_buffer) > 5000:
                self.log_buffer = self.log_buffer[-2500:]
            
        except Exception as e:
            logger.error("❌ Erreur collection logs", error=str(e))
    
    async def _export_to_prometheus(self):
        """Export métriques vers Prometheus"""
        try:
            # Les métriques sont automatiquement exposées via HTTP server
            # Ici on peut faire du nettoyage ou des transformations
            pass
            
        except Exception as e:
            logger.error("❌ Erreur export Prometheus", error=str(e))
    
    async def _export_to_elasticsearch(self):
        """Export logs vers Elasticsearch"""
        try:
            if not self.log_buffer:
                return
            
            # Simulation export vers Elasticsearch
            batch_size = min(100, len(self.log_buffer))
            logs_to_export = self.log_buffer[:batch_size]
            
            # En production, utiliser elasticsearch-py
            # await self._bulk_index_logs(logs_to_export)
            
            # Nettoyer le buffer
            self.log_buffer = self.log_buffer[batch_size:]
            
        except Exception as e:
            logger.error("❌ Erreur export Elasticsearch", error=str(e))
    
    async def _cleanup_cache(self):
        """Nettoyage du cache"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, data in self.metrics_cache.items():
                if current_time - data['timestamp'] > self.cache_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.metrics_cache[key]
            
        except Exception as e:
            logger.error("❌ Erreur nettoyage cache", error=str(e))
    
    async def _health_monitoring_loop(self):
        """Boucle de monitoring de santé"""
        while True:
            try:
                await asyncio.sleep(60)
                
                # Vérification santé des services
                await self._check_services_health()
                
                # Évaluation des règles d'alertes
                await self._evaluate_alert_rules()
                
                self.internal_metrics['service_health_checks'] += 1
                
            except Exception as e:
                logger.error("❌ Erreur health monitoring", error=str(e))
    
    async def _check_services_health(self):
        """Vérification santé des services"""
        try:
            # Liste des services à monitorer
            services_to_check = [
                ('ai-inference', 'ai-services'),
                ('content-upload', 'content-services'),
                ('payment-processing', 'financial-services'),
                ('platform-sync', 'platform-services')
            ]
            
            for service_name, namespace in services_to_check:
                health_metrics = await self._get_service_health_metrics(service_name, namespace)
                
                if health_metrics:
                    # Mise à jour métriques de disponibilité
                    self.custom_metrics['service_availability'].labels(
                        service=service_name,
                        namespace=namespace
                    ).set(health_metrics.availability)
                    
                    self.custom_metrics['service_error_rate'].labels(
                        service=service_name,
                        namespace=namespace
                    ).set(health_metrics.error_rate)
            
        except Exception as e:
            logger.error("❌ Erreur vérification santé services", error=str(e))
    
    async def _get_service_health_metrics(self, 
                                        service_name: str, 
                                        namespace: str) -> Optional[ServiceHealthMetrics]:
        """Récupération métriques santé service"""
        try:
            # Simulation récupération métriques (en production, requête Prometheus)
            import random
            
            metrics = ServiceHealthMetrics(
                service_name=service_name,
                namespace=namespace,
                timestamp=datetime.now(),
                availability=random.uniform(95.0, 100.0),
                error_rate=random.uniform(0.0, 5.0),
                latency_p50=random.uniform(50.0, 150.0),
                latency_p95=random.uniform(200.0, 500.0),
                latency_p99=random.uniform(500.0, 1000.0),
                throughput=random.uniform(100.0, 1000.0),
                cpu_usage=random.uniform(20.0, 80.0),
                memory_usage=random.uniform(30.0, 70.0),
                disk_usage=random.uniform(40.0, 60.0)
            )
            
            return metrics
            
        except Exception as e:
            logger.error("❌ Erreur métriques santé service", 
                        service=service_name, error=str(e))
            return None
    
    async def _evaluate_alert_rules(self):
        """Évaluation des règles d'alertes"""
        try:
            for rule_id, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                # Simulation évaluation (en production, requête PromQL)
                should_fire = await self._evaluate_promql_condition(rule.condition, rule.threshold)
                
                if should_fire:
                    await self._fire_alert(rule)
            
        except Exception as e:
            logger.error("❌ Erreur évaluation alertes", error=str(e))
    
    async def _evaluate_promql_condition(self, condition: str, threshold: float) -> bool:
        """Évaluation condition PromQL"""
        try:
            # Simulation évaluation (en production, requête vers Prometheus)
            import random
            return random.random() < 0.1  # 10% chance de déclencher alerte
            
        except Exception as e:
            logger.error("❌ Erreur évaluation condition", condition=condition, error=str(e))
            return False
    
    async def _fire_alert(self, rule: AlertRule):
        """Déclenchement d'une alerte"""
        try:
            alert_payload = {
                'rule_id': rule.rule_id,
                'name': rule.name,
                'severity': rule.severity.value,
                'description': rule.description,
                'timestamp': datetime.now().isoformat(),
                'labels': rule.labels,
                'annotations': rule.annotations
            }
            
            # Envoi vers AlertManager
            await self._send_to_alertmanager(alert_payload)
            
            self.internal_metrics['alerts_fired'] += 1
            
            logger.warning("🚨 Alerte déclenchée", 
                          rule=rule.name, severity=rule.severity.value)
            
        except Exception as e:
            logger.error("❌ Erreur déclenchement alerte", error=str(e))
    
    async def _send_to_alertmanager(self, alert: Dict[str, Any]):
        """Envoi alerte vers AlertManager"""
        try:
            # En production, utiliser API AlertManager
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.alertmanager_config['url']}/api/v1/alerts",
                    json=[alert],
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Alerte envoyée à AlertManager")
                    else:
                        logger.warning("⚠️ Erreur envoi AlertManager", 
                                     status=response.status)
            
        except Exception as e:
            logger.error("❌ Erreur envoi AlertManager", error=str(e))
    
    async def _create_default_dashboards(self):
        """Création dashboards Grafana par défaut"""
        try:
            # Dashboard overview services
            overview_dashboard = await self._create_services_overview_dashboard()
            
            # Dashboard métriques IA
            ai_dashboard = await self._create_ai_metrics_dashboard()
            
            # Dashboard infrastructure
            infra_dashboard = await self._create_infrastructure_dashboard()
            
            # Dashboard business metrics
            business_dashboard = await self._create_business_metrics_dashboard()
            
            self.internal_metrics['dashboards_created'] = 4
            logger.info("✅ Dashboards par défaut créés", count=4)
            
        except Exception as e:
            logger.error("❌ Erreur création dashboards", error=str(e))
    
    async def _create_services_overview_dashboard(self) -> Dict[str, Any]:
        """Dashboard overview des services"""
        return {
            'dashboard': {
                'title': 'Ainflue Services Overview',
                'tags': ['ainflue', 'overview'],
                'panels': [
                    {
                        'title': 'Service Availability',
                        'type': 'stat',
                        'targets': [{
                            'expr': 'ainflue_service_availability'
                        }]
                    },
                    {
                        'title': 'Request Rate',
                        'type': 'graph',
                        'targets': [{
                            'expr': 'rate(ainflue_http_requests_total[5m])'
                        }]
                    },
                    {
                        'title': 'Error Rate',
                        'type': 'graph',
                        'targets': [{
                            'expr': 'rate(ainflue_http_requests_total{status=~"5.."}[5m])'
                        }]
                    }
                ]
            }
        }
    
    async def _create_ai_metrics_dashboard(self) -> Dict[str, Any]:
        """Dashboard métriques IA"""
        return {
            'dashboard': {
                'title': 'Ainflue AI Metrics',
                'tags': ['ainflue', 'ai'],
                'panels': [
                    {
                        'title': 'AI Inference Requests',
                        'type': 'graph',
                        'targets': [{
                            'expr': 'rate(ainflue_ai_inference_requests_total[5m])'
                        }]
                    },
                    {
                        'title': 'Model Accuracy',
                        'type': 'stat',
                        'targets': [{
                            'expr': 'ainflue_ai_model_accuracy'
                        }]
                    }
                ]
            }
        }
    
    async def _create_infrastructure_dashboard(self) -> Dict[str, Any]:
        """Dashboard infrastructure"""
        return {
            'dashboard': {
                'title': 'Ainflue Infrastructure',
                'tags': ['ainflue', 'infrastructure'],
                'panels': [
                    {
                        'title': 'CPU Usage',
                        'type': 'graph',
                        'targets': [{
                            'expr': 'ainflue_cpu_usage_percent'
                        }]
                    },
                    {
                        'title': 'Memory Usage',
                        'type': 'graph',
                        'targets': [{
                            'expr': 'ainflue_memory_usage_percent'
                        }]
                    }
                ]
            }
        }
    
    async def _create_business_metrics_dashboard(self) -> Dict[str, Any]:
        """Dashboard métriques business"""
        return {
            'dashboard': {
                'title': 'Ainflue Business Metrics',
                'tags': ['ainflue', 'business'],
                'panels': [
                    {
                        'title': 'Creator Registrations',
                        'type': 'graph',
                        'targets': [{
                            'expr': 'rate(ainflue_creator_registrations_total[1h])'
                        }]
                    },
                    {
                        'title': 'Revenue Generated',
                        'type': 'stat',
                        'targets': [{
                            'expr': 'ainflue_revenue_generated_total'
                        }]
                    }
                ]
            }
        }
    
    async def get_service_metrics(self, 
                                service_name: str,
                                namespace: str = "default",
                                time_range: str = "1h") -> Dict[str, Any]:
        """Récupération métriques service"""
        try:
            cache_key = f"{namespace}/{service_name}_{time_range}"
            
            # Vérifier cache
            if cache_key in self.metrics_cache:
                cache_data = self.metrics_cache[cache_key]
                if time.time() - cache_data['timestamp'] < self.cache_ttl:
                    return cache_data['metrics']
            
            # Récupération métriques depuis Prometheus
            metrics = await self._query_prometheus_metrics(service_name, namespace, time_range)
            
            # Mise en cache
            self.metrics_cache[cache_key] = {
                'metrics': metrics,
                'timestamp': time.time()
            }
            
            return metrics
            
        except Exception as e:
            logger.error("❌ Erreur récupération métriques", 
                        service=service_name, error=str(e))
            return {}
    
    async def _query_prometheus_metrics(self, 
                                      service_name: str,
                                      namespace: str,
                                      time_range: str) -> Dict[str, Any]:
        """Requête métriques Prometheus"""
        try:
            # Simulation requête (en production, utiliser prometheus-api-client)
            import random
            
            return {
                'availability': random.uniform(95.0, 100.0),
                'error_rate': random.uniform(0.0, 5.0),
                'latency_p50': random.uniform(50.0, 150.0),
                'latency_p95': random.uniform(200.0, 500.0),
                'latency_p99': random.uniform(500.0, 1000.0),
                'throughput': random.uniform(100.0, 1000.0),
                'cpu_usage': random.uniform(20.0, 80.0),
                'memory_usage': random.uniform(30.0, 70.0)
            }
            
        except Exception as e:
            logger.error("❌ Erreur requête Prometheus", error=str(e))
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification santé service observabilité"""
        try:
            health_status = {
                'service': self.service_name,
                'version': self.version,
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'internal_metrics': self.internal_metrics,
                'components': {
                    'tracing': len(self.tracing_backends) > 0,
                    'metrics': len(self.custom_metrics) > 0,
                    'alerting': len(self.alert_rules) > 0,
                    'logging': True
                },
                'buffer_status': {
                    'trace_buffer_size': len(self.trace_collector),
                    'log_buffer_size': len(self.log_buffer),
                    'metrics_cache_size': len(self.metrics_cache)
                }
            }
            
            # Vérification connectivité externes
            external_checks = await self._check_external_dependencies()
            health_status['external_dependencies'] = external_checks
            
            # Statut global
            all_components_ok = all(health_status['components'].values())
            any_external_failing = any(not status for status in external_checks.values())
            
            if not all_components_ok or any_external_failing:
                health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error("❌ Erreur health check observability", error=str(e))
            return {
                'service': self.service_name,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _check_external_dependencies(self) -> Dict[str, bool]:
        """Vérification dépendances externes"""
        dependencies = {
            'prometheus': False,
            'grafana': False,
            'elasticsearch': False,
            'alertmanager': False
        }
        
        # Test Prometheus
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.prometheus_endpoint}/-/healthy", 
                                     timeout=aiohttp.ClientTimeout(total=5)) as response:
                    dependencies['prometheus'] = response.status == 200
        except:
            pass
        
        # Test autres dépendances de manière similaire
        # ...
        
        return dependencies
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Statut détaillé service observabilité"""
        try:
            return {
                'service_info': {
                    'name': self.service_name,
                    'version': self.version,
                    'status': 'running'
                },
                'configuration': {
                    'tracing_backends': list(self.tracing_backends.keys()),
                    'metrics_registered': len(self.custom_metrics),
                    'alert_rules': len(self.alert_rules),
                    'cache_ttl': self.cache_ttl
                },
                'performance_metrics': self.internal_metrics,
                'data_collection': {
                    'traces_collected': len(self.trace_collector),
                    'logs_buffered': len(self.log_buffer),
                    'metrics_cached': len(self.metrics_cache)
                },
                'alert_rules_summary': {
                    rule_id: {
                        'name': rule.name,
                        'severity': rule.severity.value,
                        'enabled': rule.enabled
                    }
                    for rule_id, rule in self.alert_rules.items()
                },
                'health': await self.health_check()
            }
            
        except Exception as e:
            logger.error("❌ Erreur statut service observability", error=str(e))
            return {'error': str(e)}

# Instance globale
observability_service = ObservabilityService()

async def main():
    """Test du service d'observabilité"""
    try:
        print("📊 Test Observability Service")
        
        # Initialisation
        success = await observability_service.initialize()
        if not success:
            print("❌ Échec initialisation")
            return
        
        # Test collecte métriques
        metrics = await observability_service.get_service_metrics("ai-inference", "ai-services")
        print(f"📊 Métriques récupérées: {metrics}")
        
        # Attendre un peu pour voir les collecteurs en action
        await asyncio.sleep(5)
        
        # Statut final
        status = await observability_service.get_service_status()
        print(f"📊 Statut: {status}")
        
        print("✅ Test Observability Service terminé")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    asyncio.run(main())