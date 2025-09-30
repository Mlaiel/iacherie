#!/usr/bin/env python3

"""
👁️ OBSERVABILITY PLATFORM ENGINE - ENTERPRISE IMPLEMENTATION
=============================================================

Observability platform enterprise avec unified monitoring et correlation.
Infrastructure robuste d'observabilité pour monitoring complet des applications IA Chérie.

© 2025 Fahed Mlaiel - Propriété intellectuelle exclusive
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import defaultdict, deque
import uuid

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Statuts de santé des services"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class AlertSeverity(Enum):
    """Sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ServiceHealth:
    """Statut de santé d'un service"""
    service_name: str
    status: HealthStatus
    score: float  # 0-100
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_rate: Optional[float] = None
    uptime_percentage: Optional[float] = None
    dependencies_healthy: bool = True
    metrics: Dict[str, float] = field(default_factory=dict)
    alerts: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ObservabilityMetric:
    """Métrique d'observabilité"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    service: str
    dimensions: Dict[str, str] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

@dataclass
class ServiceDependencyNode:
    """Nœud de dépendance de service"""
    service_name: str
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    criticality: str = "medium"  # low, medium, high, critical
    health_impact_weight: float = 1.0

@dataclass
class AnomalyDetection:
    """Détection d'anomalie"""
    anomaly_id: str
    service: str
    metric_name: str
    detected_at: datetime
    severity: AlertSeverity
    current_value: float
    expected_range: tuple[float, float]
    deviation_score: float
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ObservabilityInsight:
    """Insight d'observabilité"""
    insight_id: str
    title: str
    description: str
    category: str  # performance, reliability, security, business
    services_affected: List[str]
    confidence_score: float
    recommended_actions: List[str]
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class UnifiedMonitoringDashboard:
    """Dashboard de monitoring unifié"""
    
    def __init__(self):
        self.service_health: Dict[str, ServiceHealth] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        self.dashboard_widgets: Dict[str, Dict[str, Any]] = {}
        self.refresh_interval = timedelta(minutes=1)
        logger.info("📊 Unified Monitoring Dashboard initialisé")
    
    async def update_service_health(
        self,
        service_name: str,
        metrics: Dict[str, float],
        dependencies_status: Optional[Dict[str, bool]] = None
    ) -> ServiceHealth:
        """Met à jour la santé d'un service"""
        
        # Calcul du score de santé
        health_score = await self._calculate_health_score(metrics, dependencies_status)
        
        # Détermination du statut
        if health_score >= 90:
            status = HealthStatus.HEALTHY
        elif health_score >= 70:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY
        
        # Création/mise à jour de l'objet ServiceHealth
        service_health = ServiceHealth(
            service_name=service_name,
            status=status,
            score=health_score,
            last_check=datetime.now(),
            response_time_ms=metrics.get('response_time_ms'),
            error_rate=metrics.get('error_rate'),
            uptime_percentage=metrics.get('uptime_percentage'),
            dependencies_healthy=all(dependencies_status.values()) if dependencies_status else True,
            metrics=metrics
        )
        
        # Génération d'alertes si nécessaire
        alerts = await self._generate_health_alerts(service_health, metrics)
        service_health.alerts = alerts
        
        self.service_health[service_name] = service_health
        
        logger.debug(f"📊 Santé service mise à jour: {service_name} - {status.value} ({health_score:.1f})")
        return service_health
    
    async def _calculate_health_score(
        self,
        metrics: Dict[str, float],
        dependencies_status: Optional[Dict[str, bool]] = None
    ) -> float:
        """Calcule le score de santé basé sur les métriques"""
        
        base_score = 100.0
        
        # Impact temps de réponse
        response_time = metrics.get('response_time_ms', 0)
        if response_time > 2000:  # > 2s
            base_score -= 30
        elif response_time > 1000:  # > 1s
            base_score -= 15
        elif response_time > 500:  # > 500ms
            base_score -= 5
        
        # Impact taux d'erreur
        error_rate = metrics.get('error_rate', 0)
        if error_rate > 0.1:  # > 10%
            base_score -= 40
        elif error_rate > 0.05:  # > 5%
            base_score -= 25
        elif error_rate > 0.01:  # > 1%
            base_score -= 10
        
        # Impact uptime
        uptime = metrics.get('uptime_percentage', 100)
        if uptime < 99:
            base_score -= (100 - uptime) * 2
        
        # Impact utilisation ressources
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > 90:
            base_score -= 20
        elif cpu_usage > 80:
            base_score -= 10
        
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > 95:
            base_score -= 20
        elif memory_usage > 85:
            base_score -= 10
        
        # Impact dépendances
        if dependencies_status:
            unhealthy_deps = sum(1 for healthy in dependencies_status.values() if not healthy)
            if unhealthy_deps > 0:
                base_score -= unhealthy_deps * 15
        
        return max(0.0, min(100.0, base_score))
    
    async def _generate_health_alerts(
        self,
        service_health: ServiceHealth,
        metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Génère des alertes basées sur la santé du service"""
        
        alerts = []
        
        # Alerte santé critique
        if service_health.score < 50:
            alerts.append({
                'id': f"health_critical_{service_health.service_name}_{int(datetime.now().timestamp())}",
                'severity': AlertSeverity.CRITICAL.value,
                'title': f"Service {service_health.service_name} en état critique",
                'message': f"Score de santé: {service_health.score:.1f}/100",
                'timestamp': datetime.now().isoformat(),
                'service': service_health.service_name
            })
        
        # Alerte temps de réponse
        response_time = metrics.get('response_time_ms', 0)
        if response_time > 2000:
            alerts.append({
                'id': f"response_time_{service_health.service_name}_{int(datetime.now().timestamp())}",
                'severity': AlertSeverity.ERROR.value,
                'title': f"Temps de réponse élevé: {service_health.service_name}",
                'message': f"Temps de réponse: {response_time:.0f}ms (seuil: 2000ms)",
                'timestamp': datetime.now().isoformat(),
                'service': service_health.service_name
            })
        
        # Alerte taux d'erreur
        error_rate = metrics.get('error_rate', 0)
        if error_rate > 0.05:
            alerts.append({
                'id': f"error_rate_{service_health.service_name}_{int(datetime.now().timestamp())}",
                'severity': AlertSeverity.ERROR.value,
                'title': f"Taux d'erreur élevé: {service_health.service_name}",
                'message': f"Taux d'erreur: {error_rate:.1%} (seuil: 5%)",
                'timestamp': datetime.now().isoformat(),
                'service': service_health.service_name
            })
        
        return alerts
    
    async def get_dashboard_overview(self) -> Dict[str, Any]:
        """Retourne une vue d'ensemble du dashboard"""
        
        total_services = len(self.service_health)
        healthy_services = len([s for s in self.service_health.values() if s.status == HealthStatus.HEALTHY])
        degraded_services = len([s for s in self.service_health.values() if s.status == HealthStatus.DEGRADED])
        unhealthy_services = len([s for s in self.service_health.values() if s.status == HealthStatus.UNHEALTHY])
        
        # Score de santé global
        if total_services > 0:
            global_health_score = sum(s.score for s in self.service_health.values()) / total_services
        else:
            global_health_score = 100.0
        
        # Alertes actives par sévérité
        alert_counts = {}
        for alert in self.active_alerts:
            severity = alert.get('severity', 'info')
            alert_counts[severity] = alert_counts.get(severity, 0) + 1
        
        return {
            'global_health_score': global_health_score,
            'services': {
                'total': total_services,
                'healthy': healthy_services,
                'degraded': degraded_services,
                'unhealthy': unhealthy_services
            },
            'alerts': {
                'total': len(self.active_alerts),
                'by_severity': alert_counts
            },
            'last_updated': datetime.now().isoformat()
        }

class CrossServiceCorrelation:
    """Corrélation cross-service pour observabilité"""
    
    def __init__(self):
        self.correlation_graph: Dict[str, ServiceDependencyNode] = {}
        self.service_interactions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.correlation_patterns: List[Dict[str, Any]] = []
        logger.info("🔗 Cross-Service Correlation initialisé")
    
    async def add_service_dependency(
        self,
        service: str,
        depends_on: str,
        criticality: str = "medium"
    ):
        """Ajoute une dépendance entre services"""
        
        # Création des nœuds s'ils n'existent pas
        if service not in self.correlation_graph:
            self.correlation_graph[service] = ServiceDependencyNode(service_name=service)
        
        if depends_on not in self.correlation_graph:
            self.correlation_graph[depends_on] = ServiceDependencyNode(service_name=depends_on)
        
        # Ajout de la dépendance
        if depends_on not in self.correlation_graph[service].dependencies:
            self.correlation_graph[service].dependencies.append(depends_on)
        
        if service not in self.correlation_graph[depends_on].dependents:
            self.correlation_graph[depends_on].dependents.append(service)
        
        # Mise à jour de la criticité
        self.correlation_graph[service].criticality = criticality
        
        logger.debug(f"🔗 Dépendance ajoutée: {service} -> {depends_on} ({criticality})")
    
    async def record_service_interaction(
        self,
        from_service: str,
        to_service: str,
        interaction_count: int = 1
    ):
        """Enregistre une interaction entre services"""
        
        self.service_interactions[from_service][to_service] += interaction_count
        
        # Auto-détection de dépendances basée sur les interactions
        if self.service_interactions[from_service][to_service] > 100:  # Seuil
            await self.add_service_dependency(from_service, to_service, "medium")
    
    async def correlate_service_issues(
        self,
        unhealthy_services: List[str]
    ) -> List[Dict[str, Any]]:
        """Corrèle les problèmes entre services"""
        
        correlations = []
        
        for service in unhealthy_services:
            if service in self.correlation_graph:
                node = self.correlation_graph[service]
                
                # Analyse impact sur les dépendants
                affected_dependents = []
                for dependent in node.dependents:
                    if dependent in unhealthy_services:
                        affected_dependents.append(dependent)
                
                # Analyse problèmes de dépendances
                unhealthy_dependencies = []
                for dependency in node.dependencies:
                    if dependency in unhealthy_services:
                        unhealthy_dependencies.append(dependency)
                
                if affected_dependents or unhealthy_dependencies:
                    correlation = {
                        'service': service,
                        'affected_dependents': affected_dependents,
                        'unhealthy_dependencies': unhealthy_dependencies,
                        'correlation_score': await self._calculate_correlation_score(
                            service, affected_dependents, unhealthy_dependencies
                        ),
                        'impact_assessment': await self._assess_cascade_impact(service)
                    }
                    correlations.append(correlation)
        
        # Tri par score de corrélation
        correlations.sort(key=lambda x: x['correlation_score'], reverse=True)
        
        logger.info(f"🔗 {len(correlations)} corrélations détectées")
        return correlations
    
    async def _calculate_correlation_score(
        self,
        service: str,
        affected_dependents: List[str],
        unhealthy_dependencies: List[str]
    ) -> float:
        """Calcule un score de corrélation"""
        
        score = 0.0
        
        # Score basé sur le nombre de dépendants affectés
        score += len(affected_dependents) * 10
        
        # Score basé sur le nombre de dépendances défaillantes
        score += len(unhealthy_dependencies) * 15
        
        # Score basé sur la criticité du service
        if service in self.correlation_graph:
            criticality = self.correlation_graph[service].criticality
            criticality_weights = {
                'low': 1.0,
                'medium': 1.5,
                'high': 2.0,
                'critical': 3.0
            }
            score *= criticality_weights.get(criticality, 1.0)
        
        return min(100.0, score)
    
    async def _assess_cascade_impact(self, service: str) -> Dict[str, Any]:
        """Évalue l'impact en cascade d'un service défaillant"""
        
        if service not in self.correlation_graph:
            return {'total_impact': 0, 'affected_services': []}
        
        # BFS pour trouver tous les services impactés
        visited = set()
        queue = deque([service])
        affected_services = []
        
        while queue:
            current_service = queue.popleft()
            if current_service in visited:
                continue
            
            visited.add(current_service)
            affected_services.append(current_service)
            
            # Ajout des dépendants à la queue
            if current_service in self.correlation_graph:
                for dependent in self.correlation_graph[current_service].dependents:
                    if dependent not in visited:
                        queue.append(dependent)
        
        return {
            'total_impact': len(affected_services) - 1,  # Exclude le service original
            'affected_services': affected_services[1:],  # Exclude le service original
            'cascade_depth': len(affected_services)
        }

class IntelligentAnomalyDetection:
    """Détection intelligente d'anomalies"""
    
    def __init__(self):
        self.metric_baselines: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        self.anomaly_history: List[AnomalyDetection] = []
        self.detection_sensitivity = 2.5  # Seuil en écarts-types
        logger.info("🚨 Intelligent Anomaly Detection initialisé")
    
    async def train_baseline(
        self,
        service: str,
        metric_name: str,
        values: List[float]
    ):
        """Entraîne la baseline pour un métrique"""
        
        # Stockage des valeurs pour calcul statistique
        self.metric_baselines[service][metric_name] = values[-1000:]  # Garde les 1000 dernières valeurs
        
        logger.debug(f"🚨 Baseline mise à jour: {service}.{metric_name} ({len(values)} valeurs)")
    
    async def detect_anomaly(
        self,
        service: str,
        metric_name: str,
        current_value: float
    ) -> Optional[AnomalyDetection]:
        """Détecte une anomalie pour une métrique"""
        
        if service not in self.metric_baselines or metric_name not in self.metric_baselines[service]:
            return None
        
        baseline_values = self.metric_baselines[service][metric_name]
        
        if len(baseline_values) < 10:  # Pas assez de données historiques
            return None
        
        # Calcul statistiques baseline
        mean_value = statistics.mean(baseline_values)
        std_dev = statistics.stdev(baseline_values) if len(baseline_values) > 1 else 0
        
        if std_dev == 0:  # Pas de variation dans les données
            return None
        
        # Calcul du z-score
        z_score = abs(current_value - mean_value) / std_dev
        
        if z_score > self.detection_sensitivity:
            # Anomalie détectée
            severity = AlertSeverity.CRITICAL if z_score > 4 else AlertSeverity.ERROR if z_score > 3 else AlertSeverity.WARNING
            
            anomaly = AnomalyDetection(
                anomaly_id=f"anomaly_{service}_{metric_name}_{int(datetime.now().timestamp())}",
                service=service,
                metric_name=metric_name,
                detected_at=datetime.now(),
                severity=severity,
                current_value=current_value,
                expected_range=(
                    mean_value - (2 * std_dev),
                    mean_value + (2 * std_dev)
                ),
                deviation_score=z_score,
                context={
                    'mean': mean_value,
                    'std_dev': std_dev,
                    'baseline_size': len(baseline_values)
                }
            )
            
            self.anomaly_history.append(anomaly)
            
            # Nettoyage de l'historique
            if len(self.anomaly_history) > 10000:
                self.anomaly_history = self.anomaly_history[-5000:]
            
            logger.warning(f"🚨 Anomalie détectée: {service}.{metric_name} = {current_value} (z-score: {z_score:.2f})")
            return anomaly
        
        return None
    
    async def get_anomaly_trends(
        self,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Analyse les tendances d'anomalies"""
        
        cutoff_time = datetime.now() - time_window
        recent_anomalies = [a for a in self.anomaly_history if a.detected_at > cutoff_time]
        
        # Groupement par service
        anomalies_by_service = defaultdict(list)
        for anomaly in recent_anomalies:
            anomalies_by_service[anomaly.service].append(anomaly)
        
        # Groupement par métrique
        anomalies_by_metric = defaultdict(list)
        for anomaly in recent_anomalies:
            anomalies_by_metric[anomaly.metric_name].append(anomaly)
        
        # Analyse sévérité
        severity_counts = defaultdict(int)
        for anomaly in recent_anomalies:
            severity_counts[anomaly.severity.value] += 1
        
        return {
            'total_anomalies': len(recent_anomalies),
            'by_service': {k: len(v) for k, v in anomalies_by_service.items()},
            'by_metric': {k: len(v) for k, v in anomalies_by_metric.items()},
            'by_severity': dict(severity_counts),
            'time_range': (cutoff_time.isoformat(), datetime.now().isoformat())
        }

class ObservabilityDataLake:
    """Data lake pour données d'observabilité"""
    
    def __init__(self):
        self.metrics_store: Dict[str, List[ObservabilityMetric]] = defaultdict(list)
        self.events_store: List[Dict[str, Any]] = []
        self.traces_store: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.retention_policies = {
            'metrics': timedelta(days=90),
            'events': timedelta(days=30),
            'traces': timedelta(days=7)
        }
        logger.info("💾 Observability Data Lake initialisé")
    
    async def store_metric(
        self,
        name: str,
        value: float,
        unit: str,
        service: str,
        dimensions: Optional[Dict[str, str]] = None,
        tags: Optional[Set[str]] = None
    ) -> ObservabilityMetric:
        """Stocke une métrique dans le data lake"""
        
        metric = ObservabilityMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            service=service,
            dimensions=dimensions or {},
            tags=tags or set()
        )
        
        metric_key = f"{service}.{name}"
        self.metrics_store[metric_key].append(metric)
        
        # Nettoyage automatique selon politique de rétention
        await self._cleanup_old_metrics(metric_key)
        
        logger.debug(f"💾 Métrique stockée: {metric_key} = {value} {unit}")
        return metric
    
    async def store_event(
        self,
        event_type: str,
        service: str,
        details: Dict[str, Any]
    ):
        """Stocke un événement dans le data lake"""
        
        event = {
            'event_id': str(uuid.uuid4()),
            'event_type': event_type,
            'service': service,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        self.events_store.append(event)
        
        # Nettoyage automatique
        await self._cleanup_old_events()
        
        logger.debug(f"💾 Événement stocké: {event_type} pour {service}")
    
    async def query_metrics(
        self,
        service: str,
        metric_name: str,
        time_range: tuple[datetime, datetime],
        aggregation: str = "avg"  # avg, sum, min, max, count
    ) -> Dict[str, Any]:
        """Requête les métriques avec agrégation"""
        
        metric_key = f"{service}.{metric_name}"
        start_time, end_time = time_range
        
        if metric_key not in self.metrics_store:
            return {'values': [], 'aggregated_value': None}
        
        # Filtrage par période
        filtered_metrics = [
            m for m in self.metrics_store[metric_key]
            if start_time <= m.timestamp <= end_time
        ]
        
        if not filtered_metrics:
            return {'values': [], 'aggregated_value': None}
        
        values = [m.value for m in filtered_metrics]
        
        # Calcul agrégation
        if aggregation == "avg":
            aggregated_value = statistics.mean(values)
        elif aggregation == "sum":
            aggregated_value = sum(values)
        elif aggregation == "min":
            aggregated_value = min(values)
        elif aggregation == "max":
            aggregated_value = max(values)
        elif aggregation == "count":
            aggregated_value = len(values)
        else:
            aggregated_value = statistics.mean(values)  # Par défaut
        
        return {
            'values': [{'timestamp': m.timestamp.isoformat(), 'value': m.value} for m in filtered_metrics],
            'aggregated_value': aggregated_value,
            'count': len(values),
            'aggregation': aggregation
        }
    
    async def _cleanup_old_metrics(self, metric_key: str):
        """Nettoie les anciennes métriques"""
        
        cutoff_time = datetime.now() - self.retention_policies['metrics']
        
        if metric_key in self.metrics_store:
            self.metrics_store[metric_key] = [
                m for m in self.metrics_store[metric_key]
                if m.timestamp > cutoff_time
            ]
    
    async def _cleanup_old_events(self):
        """Nettoie les anciens événements"""
        
        cutoff_time = datetime.now() - self.retention_policies['events']
        
        self.events_store = [
            e for e in self.events_store
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
        ]

class PlatformIntelligenceEngine:
    """Moteur d'intelligence de plateforme"""
    
    def __init__(self):
        self.insights_history: List[ObservabilityInsight] = []
        self.pattern_recognition: Dict[str, Any] = {}
        self.business_context: Dict[str, Any] = {}
        logger.info("🧠 Platform Intelligence Engine initialisé")
    
    async def generate_insights(
        self,
        service_health: Dict[str, ServiceHealth],
        anomalies: List[AnomalyDetection],
        correlations: List[Dict[str, Any]]
    ) -> List[ObservabilityInsight]:
        """Génère des insights intelligents"""
        
        insights = []
        
        # Insight performance globale
        unhealthy_services = [s for s in service_health.values() if s.status != HealthStatus.HEALTHY]
        if len(unhealthy_services) > len(service_health) * 0.3:  # Plus de 30% défaillants
            insights.append(ObservabilityInsight(
                insight_id=f"perf_degradation_{int(datetime.now().timestamp())}",
                title="Dégradation Performance Globale Détectée",
                description=f"{len(unhealthy_services)}/{len(service_health)} services en difficulté",
                category="performance",
                services_affected=[s.service_name for s in unhealthy_services],
                confidence_score=0.9,
                recommended_actions=[
                    "Identifier la cause racine commune",
                    "Vérifier l'infrastructure sous-jacente",
                    "Analyser les dépendances partagées"
                ],
                created_at=datetime.now()
            ))
        
        # Insight anomalies récurrentes
        recurring_anomalies = await self._detect_recurring_anomalies(anomalies)
        if recurring_anomalies:
            insights.append(ObservabilityInsight(
                insight_id=f"recurring_anomalies_{int(datetime.now().timestamp())}",
                title="Anomalies Récurrentes Détectées",
                description=f"{len(recurring_anomalies)} patterns d'anomalies récurrents",
                category="reliability",
                services_affected=list(set(a['service'] for a in recurring_anomalies)),
                confidence_score=0.8,
                recommended_actions=[
                    "Analyse root cause des patterns récurrents",
                    "Optimiser les seuils d'alerte",
                    "Implémenter des solutions préventives"
                ],
                created_at=datetime.now(),
                metadata={'recurring_patterns': recurring_anomalies}
            ))
        
        # Insight corrélations critiques
        critical_correlations = [c for c in correlations if c['correlation_score'] > 70]
        if critical_correlations:
            insights.append(ObservabilityInsight(
                insight_id=f"critical_correlations_{int(datetime.now().timestamp())}",
                title="Corrélations Critiques entre Services",
                description=f"{len(critical_correlations)} corrélations critiques détectées",
                category="reliability",
                services_affected=list(set(c['service'] for c in critical_correlations)),
                confidence_score=0.85,
                recommended_actions=[
                    "Analyser les dépendances critiques",
                    "Implémenter circuit breakers",
                    "Considérer la réplication des services critiques"
                ],
                created_at=datetime.now(),
                metadata={'critical_correlations': critical_correlations}
            ))
        
        # Insight business impact
        business_insight = await self._analyze_business_impact(service_health, anomalies)
        if business_insight:
            insights.append(business_insight)
        
        # Stockage des insights
        self.insights_history.extend(insights)
        
        # Nettoyage historique
        if len(self.insights_history) > 1000:
            self.insights_history = self.insights_history[-500:]
        
        logger.info(f"🧠 {len(insights)} insights générés")
        return insights
    
    async def _detect_recurring_anomalies(
        self,
        anomalies: List[AnomalyDetection]
    ) -> List[Dict[str, Any]]:
        """Détecte les anomalies récurrentes"""
        
        # Groupement par service + métrique
        anomaly_groups = defaultdict(list)
        for anomaly in anomalies:
            key = f"{anomaly.service}.{anomaly.metric_name}"
            anomaly_groups[key].append(anomaly)
        
        recurring = []
        for key, group_anomalies in anomaly_groups.items():
            if len(group_anomalies) >= 3:  # Seuil pour récurrence
                recurring.append({
                    'pattern': key,
                    'service': group_anomalies[0].service,
                    'metric': group_anomalies[0].metric_name,
                    'occurrences': len(group_anomalies),
                    'avg_deviation': statistics.mean(a.deviation_score for a in group_anomalies),
                    'time_span': (
                        min(a.detected_at for a in group_anomalies),
                        max(a.detected_at for a in group_anomalies)
                    )
                })
        
        return recurring
    
    async def _analyze_business_impact(
        self,
        service_health: Dict[str, ServiceHealth],
        anomalies: List[AnomalyDetection]
    ) -> Optional[ObservabilityInsight]:
        """Analyse l'impact business"""
        
        # Services critiques pour IA Chérie
        critical_services = {
            'upload_service': 'Pipeline création contenu',
            'ai_service': 'Processing IA',
            'protection_service': 'Protection propriété intellectuelle',
            'distribution_service': 'Distribution multi-plateforme',
            'collaboration_service': 'Matching créateurs'
        }
        
        affected_critical_services = []
        for service_name, service_health_obj in service_health.items():
            if (service_name in critical_services and 
                service_health_obj.status != HealthStatus.HEALTHY):
                affected_critical_services.append({
                    'service': service_name,
                    'business_function': critical_services[service_name],
                    'health_score': service_health_obj.score
                })
        
        if affected_critical_services:
            return ObservabilityInsight(
                insight_id=f"business_impact_{int(datetime.now().timestamp())}",
                title="Impact Business Critique Détecté",
                description=f"{len(affected_critical_services)} services critiques affectés",
                category="business",
                services_affected=[s['service'] for s in affected_critical_services],
                confidence_score=0.95,
                recommended_actions=[
                    "Escalade immédiate équipe business",
                    "Activation plan de continuité",
                    "Communication transparente aux créateurs"
                ],
                created_at=datetime.now(),
                metadata={'affected_critical_services': affected_critical_services}
            )
        
        return None

class ObservabilityPlatform:
    """
    👁️ OBSERVABILITY PLATFORM ENGINE ENTERPRISE
    
    Infrastructure robuste d'observabilité avec:
    - Unified monitoring dashboard complet
    - Cross-service correlation intelligent
    - Intelligent anomaly detection ML
    - Observability data lake enterprise
    - Service health scoring avancé
    - Observability automation
    - Platform intelligence engine
    """
    
    def __init__(self):
        self.dashboard = UnifiedMonitoringDashboard()
        self.correlation = CrossServiceCorrelation()
        self.anomaly_detection = IntelligentAnomalyDetection()
        self.data_lake = ObservabilityDataLake()
        self.intelligence = PlatformIntelligenceEngine()
        self.automation_rules: List[Dict[str, Any]] = []
        logger.info("👁️ Observability Platform Engine enterprise initialisé")
    
    async def ingest_metrics(
        self,
        service: str,
        metrics: Dict[str, float]
    ) -> ServiceHealth:
        """Ingère les métriques d'un service"""
        
        # Stockage dans le data lake
        for metric_name, value in metrics.items():
            await self.data_lake.store_metric(
                name=metric_name,
                value=value,
                unit=self._get_metric_unit(metric_name),
                service=service
            )
            
            # Entraînement baseline pour détection anomalies
            await self.anomaly_detection.train_baseline(service, metric_name, [value])
            
            # Détection anomalies
            anomaly = await self.anomaly_detection.detect_anomaly(service, metric_name, value)
            if anomaly:
                await self.data_lake.store_event(
                    event_type="anomaly_detected",
                    service=service,
                    details={
                        'metric': metric_name,
                        'current_value': value,
                        'expected_range': anomaly.expected_range,
                        'deviation_score': anomaly.deviation_score
                    }
                )
        
        # Mise à jour santé service
        service_health = await self.dashboard.update_service_health(service, metrics)
        
        # Enregistrement interaction implicite (si métrique de communication)
        if 'outbound_requests' in metrics:
            # Logique pour détecter les services appelés (simplifiée)
            target_services = await self._infer_target_services(service, metrics)
            for target in target_services:
                await self.correlation.record_service_interaction(service, target)
        
        return service_health
    
    async def analyze_platform_health(self) -> Dict[str, Any]:
        """Analyse complète de la santé de la plateforme"""
        
        # Vue d'ensemble dashboard
        dashboard_overview = await self.dashboard.get_dashboard_overview()
        
        # Services en difficulté
        unhealthy_services = [
            name for name, health in self.dashboard.service_health.items()
            if health.status != HealthStatus.HEALTHY
        ]
        
        # Corrélations entre problèmes
        correlations = await self.correlation.correlate_service_issues(unhealthy_services)
        
        # Tendances d'anomalies
        anomaly_trends = await self.anomaly_detection.get_anomaly_trends()
        
        # Génération insights intelligents
        insights = await self.intelligence.generate_insights(
            service_health=self.dashboard.service_health,
            anomalies=self.anomaly_detection.anomaly_history[-100:],  # 100 dernières anomalies
            correlations=correlations
        )
        
        # Recommandations d'automation
        automation_recommendations = await self._generate_automation_recommendations(
            dashboard_overview, correlations, insights
        )
        
        return {
            'dashboard_overview': dashboard_overview,
            'service_correlations': correlations,
            'anomaly_trends': anomaly_trends,
            'intelligent_insights': [
                {
                    'title': i.title,
                    'description': i.description,
                    'category': i.category,
                    'confidence_score': i.confidence_score,
                    'recommended_actions': i.recommended_actions
                } for i in insights
            ],
            'automation_recommendations': automation_recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    async def query_observability_data(
        self,
        service: str,
        metric: str,
        time_range: tuple[datetime, datetime],
        aggregation: str = "avg"
    ) -> Dict[str, Any]:
        """Requête les données d'observabilité"""
        
        return await self.data_lake.query_metrics(service, metric, time_range, aggregation)
    
    async def add_automation_rule(
        self,
        rule_name: str,
        trigger_condition: Dict[str, Any],
        action: Dict[str, Any]
    ):
        """Ajoute une règle d'automation"""
        
        rule = {
            'rule_id': str(uuid.uuid4()),
            'name': rule_name,
            'trigger_condition': trigger_condition,
            'action': action,
            'created_at': datetime.now(),
            'enabled': True,
            'execution_count': 0
        }
        
        self.automation_rules.append(rule)
        logger.info(f"🤖 Règle automation ajoutée: {rule_name}")
    
    async def _get_metric_unit(self, metric_name: str) -> str:
        """Retourne l'unité d'une métrique"""
        
        unit_mapping = {
            'response_time_ms': 'milliseconds',
            'error_rate': 'percentage',
            'uptime_percentage': 'percentage',
            'cpu_usage': 'percentage',
            'memory_usage': 'percentage',
            'requests_per_second': 'requests/sec',
            'throughput': 'ops/sec'
        }
        
        return unit_mapping.get(metric_name, 'count')
    
    async def _infer_target_services(
        self,
        source_service: str,
        metrics: Dict[str, float]
    ) -> List[str]:
        """Infère les services cibles basés sur les métriques (logique simplifiée)"""
        
        # Logique simplifiée - dans un vrai système, cela serait basé sur 
        # les traces distribuées ou logs de communication
        service_patterns = {
            'upload_service': ['ai_service', 'protection_service'],
            'ai_service': ['protection_service', 'seo_service'],
            'protection_service': ['collaboration_service'],
            'collaboration_service': ['distribution_service'],
            'seo_service': ['distribution_service']
        }
        
        return service_patterns.get(source_service, [])
    
    async def _generate_automation_recommendations(
        self,
        dashboard_overview: Dict[str, Any],
        correlations: List[Dict[str, Any]],
        insights: List[ObservabilityInsight]
    ) -> List[Dict[str, Any]]:
        """Génère des recommandations d'automation"""
        
        recommendations = []
        
        # Automation pour services défaillants récurrents
        if dashboard_overview['services']['unhealthy'] > 0:
            recommendations.append({
                'type': 'auto_restart',
                'description': 'Auto-restart des services défaillants',
                'trigger': 'Service health score < 30 pendant 5 minutes',
                'action': 'Redémarrage gracieux du service',
                'priority': 'high'
            })
        
        # Automation pour scaling basé sur anomalies
        performance_insights = [i for i in insights if i.category == 'performance']
        if performance_insights:
            recommendations.append({
                'type': 'auto_scale',
                'description': 'Auto-scaling basé sur détection anomalies performance',
                'trigger': 'Anomalie performance détectée (z-score > 3)',
                'action': 'Scaling horizontal du service affecté',
                'priority': 'medium'
            })
        
        # Automation pour corrélations critiques
        critical_correlations = [c for c in correlations if c['correlation_score'] > 80]
        if critical_correlations:
            recommendations.append({
                'type': 'circuit_breaker',
                'description': 'Circuit breaker automatique pour corrélations critiques',
                'trigger': 'Corrélation critique détectée + service défaillant',
                'action': 'Activation circuit breaker sur dépendances',
                'priority': 'critical'
            })
        
        return recommendations

# Instance globale pour import facilité
_observability_platform = ObservabilityPlatform()

async def get_observability_platform() -> ObservabilityPlatform:
    """Retourne l'instance de la plateforme d'observabilité"""
    return _observability_platform

async def monitor_service_health(
    service: str,
    metrics: Dict[str, float]
) -> ServiceHealth:
    """Helper pour monitorer la santé d'un service"""
    return await _observability_platform.ingest_metrics(service, metrics)

# Export des classes principales
__all__ = [
    'ObservabilityPlatform',
    'ServiceHealth',
    'ObservabilityMetric',
    'AnomalyDetection',
    'ObservabilityInsight',
    'HealthStatus',
    'AlertSeverity',
    'get_observability_platform',
    'monitor_service_health'
]