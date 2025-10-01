"""⚡ Performance Metrics Logger - Real-time Platform Performance Monitoring
==================================================================
Experts: DevOps + ML Engineer + Backend Senior + DBA + SRE
Technologies: Prometheus + Grafana + OpenTelemetry + InfluxDB + Real-time Streaming
Business Logic: Performance plateforme → Optimisation UX → Métriques temps réel → SLA monitoring
==================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import uuid
import statistics
import os

# Configure logging
logger = logging.getLogger(__name__)

# ==================== ENUMS & CONSTANTS ====================

class MetricType(Enum):
    """Types de métriques de performance"""
    # Response Time Metrics
    API_RESPONSE_TIME = "api_response_time"
    DB_QUERY_TIME = "db_query_time"
    CACHE_HIT_LATENCY = "cache_hit_latency"
    FILE_UPLOAD_TIME = "file_upload_time"
    
    # Throughput Metrics
    REQUESTS_PER_SECOND = "requests_per_second"
    TRANSACTIONS_PER_SECOND = "transactions_per_second"
    CONTENT_PROCESSING_RATE = "content_processing_rate"
    USER_SESSIONS_ACTIVE = "user_sessions_active"
    
    # Resource Utilization
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_BANDWIDTH = "network_bandwidth"
    
    # Creator Economy Specific
    CONTENT_CREATION_TIME = "content_creation_time"
    REVENUE_PROCESSING_TIME = "revenue_processing_time"
    COLLABORATION_MATCH_TIME = "collaboration_match_time"
    SEO_OPTIMIZATION_TIME = "seo_optimization_time"
    
    # User Experience
    PAGE_LOAD_TIME = "page_load_time"
    FIRST_CONTENTFUL_PAINT = "first_contentful_paint"
    TIME_TO_INTERACTIVE = "time_to_interactive"
    CREATOR_DASHBOARD_LOAD = "creator_dashboard_load"
    
    # Error Metrics
    ERROR_RATE = "error_rate"
    TIMEOUT_RATE = "timeout_rate"
    RETRY_RATE = "retry_rate"
    FAILED_UPLOADS = "failed_uploads"

class PerformanceLevel(Enum):
    """Niveaux de performance"""
    EXCELLENT = "excellent"  # > 95th percentile
    GOOD = "good"           # 75th-95th percentile
    AVERAGE = "average"     # 25th-75th percentile
    POOR = "poor"           # 5th-25th percentile
    CRITICAL = "critical"   # < 5th percentile

class AlertSeverity(Enum):
    """Sévérité des alertes performance"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ServiceType(Enum):
    """Types de services monitorés"""
    API_GATEWAY = "api_gateway"
    AUTH_SERVICE = "auth_service"
    CONTENT_SERVICE = "content_service"
    PAYMENT_SERVICE = "payment_service"
    NOTIFICATION_SERVICE = "notification_service"
    AI_PROCESSING = "ai_processing"
    CREATOR_DASHBOARD = "creator_dashboard"
    ADMIN_PANEL = "admin_panel"

# ==================== DATA MODELS ====================

@dataclass
class PerformanceMetric:
    """Métrique de performance complète"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Metric identification
    metric_type: MetricType = MetricType.API_RESPONSE_TIME
    service_name: str = "iacherie-platform"
    service_type: Optional[ServiceType] = None
    endpoint: Optional[str] = None
    
    # Metric values
    value: float = 0.0
    unit: str = "ms"  # ms, seconds, percent, count, bytes, etc.
    
    # Context information
    creator_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    # Performance context
    request_method: Optional[str] = None
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    
    # Geographic context
    region: Optional[str] = None
    country: Optional[str] = None
    cdn_edge: Optional[str] = None
    
    # Technical context
    server_instance: Optional[str] = None
    container_id: Optional[str] = None
    deployment_version: Optional[str] = None
    
    # Performance analysis
    performance_level: Optional[PerformanceLevel] = None
    baseline_comparison: Optional[float] = None  # % difference from baseline
    sla_compliance: bool = True
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_performance_level(self, percentiles: Dict[str, float]) -> PerformanceLevel:
        """Calcule le niveau de performance basé sur les percentiles"""
        if self.value <= percentiles.get('p95', float('inf')):
            self.performance_level = PerformanceLevel.EXCELLENT
        elif self.value <= percentiles.get('p75', float('inf')):
            self.performance_level = PerformanceLevel.GOOD
        elif self.value <= percentiles.get('p50', float('inf')):
            self.performance_level = PerformanceLevel.AVERAGE
        elif self.value <= percentiles.get('p25', float('inf')):
            self.performance_level = PerformanceLevel.POOR
        else:
            self.performance_level = PerformanceLevel.CRITICAL
            
        return self.performance_level
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour stockage"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'metric_type': self.metric_type.value,
            'service_name': self.service_name,
            'service_type': self.service_type.value if self.service_type else None,
            'endpoint': self.endpoint,
            'value': self.value,
            'unit': self.unit,
            'creator_id': self.creator_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'trace_id': self.trace_id,
            'request_method': self.request_method,
            'status_code': self.status_code,
            'content_type': self.content_type,
            'file_size': self.file_size,
            'region': self.region,
            'country': self.country,
            'cdn_edge': self.cdn_edge,
            'server_instance': self.server_instance,
            'container_id': self.container_id,
            'deployment_version': self.deployment_version,
            'performance_level': self.performance_level.value if self.performance_level else None,
            'baseline_comparison': self.baseline_comparison,
            'sla_compliance': self.sla_compliance,
            'tags': self.tags,
            'labels': self.labels,
            'additional_data': self.additional_data
        }

@dataclass
class PerformanceAlert:
    """Alerte de performance"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    severity: AlertSeverity = AlertSeverity.WARNING
    metric_type: MetricType = MetricType.API_RESPONSE_TIME
    service_name: str = ""
    
    current_value: float = 0.0
    threshold_value: float = 0.0
    threshold_type: str = "above"  # above, below, equals
    
    description: str = ""
    suggested_actions: List[str] = field(default_factory=list)
    
    # Context
    affected_endpoints: List[str] = field(default_factory=list)
    affected_users: int = 0
    business_impact: str = "low"
    
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    resolution_notes: str = ""

@dataclass
class SLADefinition:
    """Définition d'un SLA"""
    name: str
    metric_type: MetricType
    threshold_value: float
    threshold_operator: str = "less_than"  # less_than, greater_than, equals
    measurement_window: int = 300  # seconds
    target_percentage: float = 99.0  # percentage of time SLA should be met

# ==================== ANALYTICS ENGINE ====================

class PerformanceAnalyticsEngine:
    """Moteur d'analytics performance avancé"""
    
    def __init__(self):
        self.metrics_history: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.percentiles_cache: Dict[str, Dict[str, float]] = {}
        self.baselines: Dict[str, float] = {}
        self.alerts: List[PerformanceAlert] = []
        self.slas: List[SLADefinition] = []
        self.lock = threading.RLock()
        
        # Real-time aggregations
        self.realtime_stats = {
            'requests_per_minute': 0,
            'average_response_time': 0.0,
            'error_rate_percentage': 0.0,
            'active_users': 0,
            'slowest_endpoints': [],
            'performance_score': 100.0
        }
        
        # Initialize default SLAs
        self._initialize_default_slas()
        
    def _initialize_default_slas(self):
        """Initialise les SLAs par défaut pour Creator Economy"""
        default_slas = [
            SLADefinition(
                name="API Response Time",
                metric_type=MetricType.API_RESPONSE_TIME,
                threshold_value=500.0,  # 500ms
                threshold_operator="less_than",
                target_percentage=95.0
            ),
            SLADefinition(
                name="Content Upload Performance",
                metric_type=MetricType.FILE_UPLOAD_TIME,
                threshold_value=30000.0,  # 30 seconds
                threshold_operator="less_than",
                target_percentage=90.0
            ),
            SLADefinition(
                name="Creator Dashboard Load Time",
                metric_type=MetricType.CREATOR_DASHBOARD_LOAD,
                threshold_value=2000.0,  # 2 seconds
                threshold_operator="less_than",
                target_percentage=98.0
            ),
            SLADefinition(
                name="Error Rate",
                metric_type=MetricType.ERROR_RATE,
                threshold_value=1.0,  # 1%
                threshold_operator="less_than",
                target_percentage=99.0
            )
        ]
        self.slas.extend(default_slas)
    
    def analyze_metric(self, metric: PerformanceMetric):
        """Analyse une métrique en temps réel"""
        with self.lock:
            metric_key = f"{metric.metric_type.value}_{metric.service_name}"
            
            # Ajouter à l'historique
            self.metrics_history[metric_key].append(metric)
            
            # Maintenir une fenêtre glissante (dernières 1000 métriques)
            if len(self.metrics_history[metric_key]) > 1000:
                self.metrics_history[metric_key] = self.metrics_history[metric_key][-1000:]
            
            # Calculer les percentiles
            self._update_percentiles(metric_key)
            
            # Mettre à jour les baselines
            self._update_baselines(metric_key)
            
            # Analyser la performance
            self._analyze_metric_performance(metric, metric_key)
            
            # Vérifier les SLAs
            self._check_sla_compliance(metric)
            
            # Mettre à jour les stats temps réel
            self._update_realtime_stats(metric)
            
            # Détecter les anomalies
            self._detect_performance_anomalies(metric, metric_key)
    
    def _update_percentiles(self, metric_key: str):
        """Met à jour les percentiles pour une métrique"""
        values = [m.value for m in self.metrics_history[metric_key]]
        
        if len(values) >= 10:  # Minimum pour calculs statistiques
            self.percentiles_cache[metric_key] = {
                'p50': statistics.median(values),
                'p75': statistics.quantiles(values, n=4)[2],
                'p90': statistics.quantiles(values, n=10)[8],
                'p95': statistics.quantiles(values, n=20)[18],
                'p99': statistics.quantiles(values, n=100)[98],
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0.0
            }
    
    def _update_baselines(self, metric_key: str):
        """Met à jour les baselines de performance"""
        if metric_key in self.percentiles_cache:
            # Baseline = moyenne des 7 derniers jours (simulation)
            self.baselines[metric_key] = self.percentiles_cache[metric_key]['mean']
    
    def _analyze_metric_performance(self, metric: PerformanceMetric, metric_key: str):
        """Analyse la performance d'une métrique"""
        if metric_key in self.percentiles_cache:
            percentiles = self.percentiles_cache[metric_key]
            metric.calculate_performance_level(percentiles)
            
            # Comparaison avec baseline
            if metric_key in self.baselines:
                baseline = self.baselines[metric_key]
                if baseline > 0:
                    metric.baseline_comparison = ((metric.value - baseline) / baseline) * 100
    
    def _check_sla_compliance(self, metric: PerformanceMetric):
        """Vérifie la conformité SLA"""
        for sla in self.slas:
            if sla.metric_type == metric.metric_type:
                if sla.threshold_operator == "less_than":
                    metric.sla_compliance = metric.value < sla.threshold_value
                elif sla.threshold_operator == "greater_than":
                    metric.sla_compliance = metric.value > sla.threshold_value
                
                # Générer une alerte si SLA violé
                if not metric.sla_compliance:
                    self._generate_sla_alert(metric, sla)
    
    def _generate_sla_alert(self, metric: PerformanceMetric, sla: SLADefinition):
        """Génère une alerte de violation SLA"""
        alert = PerformanceAlert(
            severity=AlertSeverity.CRITICAL,
            metric_type=metric.metric_type,
            service_name=metric.service_name,
            current_value=metric.value,
            threshold_value=sla.threshold_value,
            description=f"SLA violation: {sla.name} - {metric.value}{metric.unit} exceeds threshold {sla.threshold_value}{metric.unit}",
            suggested_actions=[
                "Investigate service performance",
                "Check resource utilization",
                "Review recent deployments",
                "Scale infrastructure if needed"
            ]
        )
        
        self.alerts.append(alert)
        logger.warning(f"SLA Alert: {alert.description}")
    
    def _update_realtime_stats(self, metric: PerformanceMetric):
        """Met à jour les statistiques temps réel"""
        current_minute = datetime.utcnow().replace(second=0, microsecond=0)
        
        # Requests per minute (simulation basée sur métriques reçues)
        if metric.metric_type == MetricType.API_RESPONSE_TIME:
            self.realtime_stats['requests_per_minute'] += 1
        
        # Average response time
        if metric.metric_type == MetricType.API_RESPONSE_TIME:
            current_avg = self.realtime_stats['average_response_time']
            count = self.realtime_stats.get('response_time_count', 0) + 1
            new_avg = (current_avg * (count - 1) + metric.value) / count
            self.realtime_stats['average_response_time'] = new_avg
            self.realtime_stats['response_time_count'] = count
        
        # Error rate
        if metric.metric_type == MetricType.ERROR_RATE:
            self.realtime_stats['error_rate_percentage'] = metric.value
        
        # Performance score (simplified calculation)
        perf_score = 100.0
        if self.realtime_stats['average_response_time'] > 500:
            perf_score -= 20
        if self.realtime_stats['error_rate_percentage'] > 1:
            perf_score -= 30
        self.realtime_stats['performance_score'] = max(perf_score, 0.0)
    
    def _detect_performance_anomalies(self, metric: PerformanceMetric, metric_key: str):
        """Détecte les anomalies de performance"""
        if metric_key not in self.percentiles_cache:
            return
        
        percentiles = self.percentiles_cache[metric_key]
        
        # Anomalie: valeur > p99 (très lente)
        if metric.value > percentiles.get('p99', float('inf')):
            alert = PerformanceAlert(
                severity=AlertSeverity.WARNING,
                metric_type=metric.metric_type,
                service_name=metric.service_name,
                current_value=metric.value,
                threshold_value=percentiles['p99'],
                threshold_type="above",
                description=f"Performance anomaly: {metric.metric_type.value} value {metric.value}{metric.unit} exceeds 99th percentile",
                suggested_actions=[
                    "Check for resource contention",
                    "Review application logs",
                    "Monitor related services"
                ]
            )
            self.alerts.append(alert)
        
        # Anomalie: spike soudain (>3 standard deviations)
        if percentiles.get('stdev', 0) > 0:
            z_score = abs(metric.value - percentiles['mean']) / percentiles['stdev']
            if z_score > 3:
                alert = PerformanceAlert(
                    severity=AlertSeverity.CRITICAL,
                    metric_type=metric.metric_type,
                    service_name=metric.service_name,
                    current_value=metric.value,
                    threshold_value=percentiles['mean'],
                    description=f"Statistical anomaly: {metric.metric_type.value} deviates {z_score:.2f} standard deviations from mean",
                    suggested_actions=[
                        "Immediate investigation required",
                        "Check for system events",
                        "Review error logs"
                    ]
                )
                self.alerts.append(alert)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Résumé des performances"""
        return {
            'realtime_stats': self.realtime_stats,
            'active_alerts': len([a for a in self.alerts if not a.resolved]),
            'total_metrics_tracked': len(self.metrics_history),
            'sla_definitions': len(self.slas),
            'performance_overview': self._calculate_overall_performance()
        }
    
    def _calculate_overall_performance(self) -> Dict[str, Any]:
        """Calcule la performance globale"""
        total_metrics = sum(len(metrics) for metrics in self.metrics_history.values())
        
        if total_metrics == 0:
            return {'status': 'no_data', 'score': 0}
        
        # Calcul simplifié du score de performance
        excellent_count = 0
        total_count = 0
        
        for metrics in self.metrics_history.values():
            for metric in metrics[-100:]:  # Dernières 100 métriques par type
                total_count += 1
                if metric.performance_level == PerformanceLevel.EXCELLENT:
                    excellent_count += 1
        
        if total_count > 0:
            excellence_ratio = excellent_count / total_count
            overall_score = excellence_ratio * 100
            
            if overall_score >= 90:
                status = "excellent"
            elif overall_score >= 75:
                status = "good"
            elif overall_score >= 50:
                status = "average"
            else:
                status = "poor"
            
            return {
                'status': status,
                'score': overall_score,
                'excellence_ratio': excellence_ratio
            }
        
        return {'status': 'insufficient_data', 'score': 0}
    
    def get_service_performance(self, service_name: str) -> Dict[str, Any]:
        """Performance spécifique d'un service"""
        service_metrics = {}
        
        for metric_key, metrics in self.metrics_history.items():
            service_metrics_filtered = [m for m in metrics if m.service_name == service_name]
            if service_metrics_filtered:
                service_metrics[metric_key] = service_metrics_filtered[-50:]  # Dernières 50
        
        if not service_metrics:
            return {'service': service_name, 'status': 'no_data'}
        
        # Calculer les métriques du service
        avg_response_times = []
        error_rates = []
        
        for metrics in service_metrics.values():
            for metric in metrics:
                if metric.metric_type == MetricType.API_RESPONSE_TIME:
                    avg_response_times.append(metric.value)
                elif metric.metric_type == MetricType.ERROR_RATE:
                    error_rates.append(metric.value)
        
        return {
            'service': service_name,
            'average_response_time': statistics.mean(avg_response_times) if avg_response_times else 0,
            'current_error_rate': error_rates[-1] if error_rates else 0,
            'total_metrics': sum(len(m) for m in service_metrics.values()),
            'recent_alerts': [a for a in self.alerts if a.service_name == service_name and not a.resolved]
        }

# ==================== MAIN LOGGER CLASS ====================

class PerformanceMetricsLogger:
    """Logger principal pour métriques de performance Creator Economy"""
    
    def __init__(self, buffer_size: int = 10000, auto_flush_interval: int = 30):
        self.buffer_size = buffer_size
        self.auto_flush_interval = auto_flush_interval
        
        # Storage
        self.metrics_buffer = deque(maxlen=buffer_size)
        self.analytics_engine = PerformanceAnalyticsEngine()
        
        # Threading
        self.lock = threading.RLock()
        self.is_running = False
        self.flush_thread = None
        
        # Statistics
        self.total_logged = 0
        self.dropped_metrics = 0
        self.processing_time_total = 0.0
        
        logger.info("⚡ Performance Metrics Logger initialized")
    
    def start(self):
        """Démarre le logger"""
        if self.is_running:
            return
            
        self.is_running = True
        self.flush_thread = threading.Thread(
            target=self._auto_flush_loop,
            daemon=True,
            name="PerformanceLogger-AutoFlush"
        )
        self.flush_thread.start()
        
        logger.info("🚀 Performance Metrics Logger started")
    
    def stop(self):
        """Arrête le logger"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5.0)
            
        # Flush final
        self._flush_buffer()
        
        logger.info("🛑 Performance Metrics Logger stopped")
    
    def _auto_flush_loop(self):
        """Boucle de flush automatique"""
        while self.is_running:
            time.sleep(self.auto_flush_interval)
            if self.is_running:
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Vide le buffer et traite les métriques"""
        with self.lock:
            metrics_to_process = list(self.metrics_buffer)
            self.metrics_buffer.clear()
        
        start_time = time.time()
        
        for metric in metrics_to_process:
            try:
                self.analytics_engine.analyze_metric(metric)
                logger.debug(f"Processed performance metric: {metric.metric_type.value}")
            except Exception as e:
                logger.error(f"Error processing metric {metric.id}: {e}")
        
        processing_time = time.time() - start_time
        self.processing_time_total += processing_time
        
        if metrics_to_process:
            logger.debug(f"Processed {len(metrics_to_process)} metrics in {processing_time:.3f}s")
    
    def log_metric(self, 
                  metric_type: MetricType,
                  value: float,
                  unit: str = "ms",
                  service_name: str = "iacherie-platform",
                  **kwargs) -> str:
        """Log une métrique de performance"""
        
        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            service_name=service_name,
            **kwargs
        )
        
        with self.lock:
            if len(self.metrics_buffer) >= self.buffer_size:
                self.dropped_metrics += 1
                logger.warning(f"Metrics buffer full, dropping metric {metric.id}")
                return ""
            
            self.metrics_buffer.append(metric)
            self.total_logged += 1
        
        logger.debug(f"Logged metric: {metric_type.value} = {value}{unit}")
        return metric.id
    
    # ==================== SPECIALIZED LOG METHODS ====================
    
    def log_api_response_time(self, endpoint: str, response_time_ms: float,
                            status_code: int = 200, method: str = "GET", **kwargs) -> str:
        """Log temps de réponse API"""
        return self.log_metric(
            metric_type=MetricType.API_RESPONSE_TIME,
            value=response_time_ms,
            unit="ms",
            endpoint=endpoint,
            status_code=status_code,
            request_method=method,
            service_type=ServiceType.API_GATEWAY,
            tags=["api", "response_time"],
            **kwargs
        )
    
    def log_content_upload_time(self, creator_id: str, file_size: int, 
                              upload_time_ms: float, content_type: str = "", **kwargs) -> str:
        """Log temps d'upload de contenu"""
        return self.log_metric(
            metric_type=MetricType.FILE_UPLOAD_TIME,
            value=upload_time_ms,
            unit="ms",
            creator_id=creator_id,
            file_size=file_size,
            content_type=content_type,
            service_type=ServiceType.CONTENT_SERVICE,
            tags=["content", "upload", "creator"],
            **kwargs
        )
    
    def log_creator_dashboard_load(self, creator_id: str, load_time_ms: float,
                                 components_loaded: int = 0, **kwargs) -> str:
        """Log temps de chargement dashboard créateur"""
        return self.log_metric(
            metric_type=MetricType.CREATOR_DASHBOARD_LOAD,
            value=load_time_ms,
            unit="ms",
            creator_id=creator_id,
            service_type=ServiceType.CREATOR_DASHBOARD,
            additional_data={"components_loaded": components_loaded},
            tags=["dashboard", "creator", "ui"],
            **kwargs
        )
    
    def log_revenue_processing_time(self, creator_id: str, processing_time_ms: float,
                                  transaction_amount: float = 0.0, **kwargs) -> str:
        """Log temps de traitement des revenus"""
        return self.log_metric(
            metric_type=MetricType.REVENUE_PROCESSING_TIME,
            value=processing_time_ms,
            unit="ms",
            creator_id=creator_id,
            service_type=ServiceType.PAYMENT_SERVICE,
            additional_data={"transaction_amount": transaction_amount},
            tags=["revenue", "payment", "creator"],
            **kwargs
        )
    
    def log_collaboration_match_time(self, creator_id: str, match_time_ms: float,
                                   matches_found: int = 0, **kwargs) -> str:
        """Log temps de matching collaboration"""
        return self.log_metric(
            metric_type=MetricType.COLLABORATION_MATCH_TIME,
            value=match_time_ms,
            unit="ms",
            creator_id=creator_id,
            additional_data={"matches_found": matches_found},
            tags=["collaboration", "matching", "creator"],
            **kwargs
        )
    
    def log_ai_processing_time(self, content_id: str, processing_time_ms: float,
                             ai_model: str = "", operation: str = "", **kwargs) -> str:
        """Log temps de traitement IA"""
        return self.log_metric(
            metric_type=MetricType.CONTENT_PROCESSING_RATE,
            value=processing_time_ms,
            unit="ms",
            content_id=content_id,
            service_type=ServiceType.AI_PROCESSING,
            additional_data={"ai_model": ai_model, "operation": operation},
            tags=["ai", "processing", "content"],
            **kwargs
        )
    
    def log_error_rate(self, service_name: str, error_percentage: float,
                      error_count: int = 0, total_requests: int = 0, **kwargs) -> str:
        """Log taux d'erreur"""
        return self.log_metric(
            metric_type=MetricType.ERROR_RATE,
            value=error_percentage,
            unit="percent",
            service_name=service_name,
            additional_data={"error_count": error_count, "total_requests": total_requests},
            tags=["error", "rate"],
            **kwargs
        )
    
    def log_resource_usage(self, resource_type: str, usage_percentage: float,
                         server_instance: str = "", **kwargs) -> str:
        """Log utilisation des ressources"""
        metric_types = {
            "cpu": MetricType.CPU_USAGE,
            "memory": MetricType.MEMORY_USAGE,
            "disk": MetricType.DISK_USAGE
        }
        
        metric_type = metric_types.get(resource_type.lower(), MetricType.CPU_USAGE)
        
        return self.log_metric(
            metric_type=metric_type,
            value=usage_percentage,
            unit="percent",
            server_instance=server_instance,
            tags=["resource", resource_type],
            **kwargs
        )
    
    # ==================== ANALYTICS METHODS ====================
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Dashboard de performance complet"""
        summary = self.analytics_engine.get_performance_summary()
        
        return {
            'summary': summary,
            'alerts': {
                'active': len([a for a in self.analytics_engine.alerts if not a.resolved]),
                'critical': len([a for a in self.analytics_engine.alerts 
                               if not a.resolved and a.severity == AlertSeverity.CRITICAL]),
                'recent': [a.to_dict() if hasattr(a, 'to_dict') else {
                    'id': a.id,
                    'severity': a.severity.value,
                    'description': a.description
                } for a in self.analytics_engine.alerts[-5:]]
            },
            'sla_status': {
                'total_slas': len(self.analytics_engine.slas),
                'sla_definitions': [
                    {
                        'name': sla.name,
                        'metric': sla.metric_type.value,
                        'threshold': sla.threshold_value,
                        'target': sla.target_percentage
                    } for sla in self.analytics_engine.slas
                ]
            },
            'logger_stats': {
                'total_logged': self.total_logged,
                'dropped_metrics': self.dropped_metrics,
                'processing_efficiency': self.processing_time_total / max(self.total_logged, 1)
            }
        }
    
    def get_service_report(self, service_name: str) -> Dict[str, Any]:
        """Rapport de performance pour un service"""
        return self.analytics_engine.get_service_performance(service_name)
    
    def get_creator_performance(self, creator_id: str) -> Dict[str, Any]:
        """Performance spécifique d'un créateur"""
        creator_metrics = []
        
        with self.lock:
            for metric in list(self.metrics_buffer):
                if metric.creator_id == creator_id:
                    creator_metrics.append(metric.to_dict())
        
        if not creator_metrics:
            return {
                'creator_id': creator_id,
                'status': 'no_data',
                'message': 'No performance data available for this creator'
            }
        
        # Analyser les métriques du créateur
        dashboard_loads = [m for m in creator_metrics if m['metric_type'] == 'creator_dashboard_load']
        uploads = [m for m in creator_metrics if m['metric_type'] == 'file_upload_time']
        revenue_processing = [m for m in creator_metrics if m['metric_type'] == 'revenue_processing_time']
        
        return {
            'creator_id': creator_id,
            'dashboard_performance': {
                'average_load_time': statistics.mean([m['value'] for m in dashboard_loads]) if dashboard_loads else 0,
                'load_count': len(dashboard_loads)
            },
            'upload_performance': {
                'average_upload_time': statistics.mean([m['value'] for m in uploads]) if uploads else 0,
                'upload_count': len(uploads)
            },
            'revenue_performance': {
                'average_processing_time': statistics.mean([m['value'] for m in revenue_processing]) if revenue_processing else 0,
                'transaction_count': len(revenue_processing)
            },
            'total_metrics': len(creator_metrics),
            'performance_score': self._calculate_creator_performance_score(creator_metrics)
        }
    
    def _calculate_creator_performance_score(self, metrics: List[Dict[str, Any]]) -> float:
        """Calcule un score de performance pour un créateur"""
        if not metrics:
            return 0.0
        
        score = 100.0
        
        # Pénaliser les temps de réponse lents
        slow_responses = len([m for m in metrics if m.get('value', 0) > 2000])  # >2s
        if slow_responses > 0:
            score -= (slow_responses / len(metrics)) * 30
        
        # Récompenser la cohérence
        response_times = [m['value'] for m in metrics if m.get('metric_type') in ['api_response_time', 'creator_dashboard_load']]
        if len(response_times) > 1:
            consistency = 1 - (statistics.stdev(response_times) / statistics.mean(response_times))
            score *= consistency
        
        return max(score, 0.0)
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Métriques temps réel"""
        return self.analytics_engine.realtime_stats
    
    def get_logger_stats(self) -> Dict[str, Any]:
        """Statistiques du logger"""
        with self.lock:
            buffer_size = len(self.metrics_buffer)
            
        return {
            'total_logged': self.total_logged,
            'dropped_metrics': self.dropped_metrics,
            'current_buffer_size': buffer_size,
            'max_buffer_size': self.buffer_size,
            'buffer_utilization': buffer_size / self.buffer_size,
            'is_running': self.is_running,
            'processing_time_total': self.processing_time_total,
            'average_processing_time': self.processing_time_total / max(self.total_logged, 1)
        }

# ==================== HELPER FUNCTIONS ====================

# Instance globale
_performance_logger_instance: Optional[PerformanceMetricsLogger] = None

def get_performance_logger() -> PerformanceMetricsLogger:
    """Récupère l'instance singleton du logger"""
    global _performance_logger_instance
    
    if _performance_logger_instance is None:
        _performance_logger_instance = PerformanceMetricsLogger()
        _performance_logger_instance.start()
        
    return _performance_logger_instance

def log_api_performance(endpoint: str, response_time: float, **kwargs):
    """Helper: Log performance API"""
    logger_instance = get_performance_logger()
    return logger_instance.log_api_response_time(endpoint, response_time, **kwargs)

def log_creator_upload(creator_id: str, file_size: int, upload_time: float, **kwargs):
    """Helper: Log upload créateur"""
    logger_instance = get_performance_logger()
    return logger_instance.log_content_upload_time(creator_id, file_size, upload_time, **kwargs)

def log_dashboard_load(creator_id: str, load_time: float, **kwargs):
    """Helper: Log chargement dashboard"""
    logger_instance = get_performance_logger()
    return logger_instance.log_creator_dashboard_load(creator_id, load_time, **kwargs)

# ==================== DEMO ====================

if __name__ == "__main__":
    # Configuration et démonstration
    perf_logger = PerformanceMetricsLogger(buffer_size=1000, auto_flush_interval=10)
    perf_logger.start()
    
    try:
        # Simulation de métriques
        creators = ["creator_1", "creator_2", "creator_3"]
        
        for i, creator_id in enumerate(creators):
            # API Response times
            perf_logger.log_api_response_time(
                endpoint=f"/api/creator/{creator_id}/content",
                response_time_ms=150.0 + i*50,
                status_code=200,
                method="GET"
            )
            
            # Content uploads
            perf_logger.log_content_upload_time(
                creator_id=creator_id,
                file_size=1024*1024*10,  # 10MB
                upload_time_ms=5000.0 + i*1000,
                content_type="video/mp4"
            )
            
            # Dashboard loads
            perf_logger.log_creator_dashboard_load(
                creator_id=creator_id,
                load_time_ms=800.0 + i*200,
                components_loaded=15
            )
            
            # Revenue processing
            perf_logger.log_revenue_processing_time(
                creator_id=creator_id,
                processing_time_ms=300.0 + i*100,
                transaction_amount=50.0 + i*25
            )
            
            # Error rates
            perf_logger.log_error_rate(
                service_name="creator-service",
                error_percentage=0.5 + i*0.2,
                error_count=5 + i*2,
                total_requests=1000 + i*200
            )
        
        # Attendre le traitement
        time.sleep(2)
        
        # Afficher les résultats
        print("⚡ Performance Metrics Logger Demo Results:")
        print("\n🔧 Logger Stats:")
        print(json.dumps(perf_logger.get_logger_stats(), indent=2))
        
        print("\n📊 Performance Dashboard:")
        dashboard = perf_logger.get_performance_dashboard()
        print(json.dumps(dashboard, indent=2, default=str))
        
        print("\n👤 Creator Performance (creator_1):")
        creator_perf = perf_logger.get_creator_performance("creator_1")
        print(json.dumps(creator_perf, indent=2))
        
        print("\n⏱️ Realtime Metrics:")
        realtime = perf_logger.get_realtime_metrics()
        print(json.dumps(realtime, indent=2))
        
    finally:
        perf_logger.stop()