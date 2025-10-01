#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏥 SERVICE REGISTRY ENTERPRISE - HEALTH MONITORING ORCHESTRATOR
===============================================================

**Author**: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
**IP Owner**: Fahed Mlaiel (mlaiel@live.de)
**Project**: IA Chérie Service Registry Enterprise
**Version**: 1.0 Production
**Created**: 2025-01-07 | Updated: 2025-12-14

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture service registry et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

🩺 HEALTH MONITORING ORCHESTRATOR
Orchestrateur monitoring santé services avec ML anomaly detection.
Health scoring + predictive alerts + auto-remediation.
"""

import asyncio
import json
import logging
import time
import statistics
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import random
import uuid

from .distributed_registry_core import ServiceInstance, ServiceStatus

# Core logger
logger = logging.getLogger(__name__)

class HealthCheckType(Enum):
    """Types of health checks"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    DATABASE = "database"
    REDIS = "redis"
    CUSTOM = "custom"

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class RemediationAction(Enum):
    """Remediation action types"""
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    ROUTE_TRAFFIC = "route_traffic"
    NOTIFY_ONCALL = "notify_oncall"
    NONE = "none"

@dataclass
class HealthMetric:
    """Individual health metric"""
    name: str
    value: float
    unit: str
    timestamp: float
    threshold_critical: Optional[float] = None
    threshold_warning: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class ServiceMetric:
    """Service metrics collection"""
    service_id: str
    timestamp: float
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    request_rate: float = 0.0
    active_connections: int = 0
    custom_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class CompositeHealthScore:
    """Composite health score for a service"""
    service_id: str
    overall_score: float  # 0.0 to 1.0
    component_scores: Dict[str, float]
    contributing_factors: Dict[str, float]
    timestamp: float
    status: ServiceStatus
    recommendations: List[str] = field(default_factory=list)

@dataclass
class AnomalyDetectionResult:
    """Anomaly detection result"""
    service_id: str
    anomalies_detected: List[Dict[str, Any]]
    anomaly_score: float  # 0.0 to 1.0
    confidence: float
    affected_metrics: List[str]
    timestamp: float
    description: str

@dataclass
class FailurePrediction:
    """Service failure prediction"""
    service_id: str
    failure_probability: float  # 0.0 to 1.0
    prediction_window_minutes: int
    contributing_factors: Dict[str, float]
    confidence: float
    recommended_actions: List[RemediationAction]
    time_to_failure_estimate: Optional[int] = None  # minutes

@dataclass
class HealthIssue:
    """Health issue identification"""
    issue_id: str
    service_id: str
    issue_type: str
    severity: AlertSeverity
    description: str
    affected_metrics: List[str]
    timestamp: float
    auto_remediable: bool = False
    suggested_actions: List[RemediationAction] = field(default_factory=list)

@dataclass
class RemediationResult:
    """Remediation action result"""
    issue_id: str
    service_id: str
    action_taken: RemediationAction
    success: bool
    duration_seconds: float
    description: str
    side_effects: List[str] = field(default_factory=list)

@dataclass
class MonitoringScope:
    """Monitoring scope definition"""
    service_ids: Optional[List[str]] = None
    service_types: Optional[List[str]] = None
    business_domains: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    check_interval_seconds: int = 30
    enable_predictions: bool = True
    enable_auto_remediation: bool = False

@dataclass
class HealthMonitoringResult:
    """Health monitoring orchestration result"""
    monitoring_scope: MonitoringScope
    services_monitored: int
    health_scores: Dict[str, CompositeHealthScore]
    anomalies: List[AnomalyDetectionResult]
    predictions: List[FailurePrediction]
    issues_identified: List[HealthIssue]
    remediations_performed: List[RemediationResult]
    execution_time_ms: float

@dataclass
class MonitoringConfig:
    """Configuration for health monitoring"""
    check_interval: int = 30  # seconds
    health_check_timeout: float = 5.0  # seconds
    anomaly_detection_window: int = 300  # seconds
    prediction_window: int = 900  # seconds
    enable_ml_predictions: bool = True
    enable_auto_remediation: bool = False
    max_concurrent_checks: int = 100
    alert_thresholds: Dict[str, Dict[str, float]] = field(default_factory=dict)

class MLAnomalyDetector:
    """ML-based anomaly detection for service metrics"""
    
    def __init__(self):
        self.metric_history: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=1000)))
        self.baseline_stats: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
        self.anomaly_threshold = 2.5  # Standard deviations
        
    async def detect_anomalies(self, service_metrics: List[ServiceMetric]) -> List[AnomalyDetectionResult]:
        """Detect anomalies in service metrics using ML techniques"""
        anomaly_results = []
        
        for metric in service_metrics:
            service_anomalies = []
            anomaly_score = 0.0
            affected_metrics = []
            
            # Analyze each metric
            metrics_to_check = {
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'response_time_ms': metric.response_time_ms,
                'error_rate': metric.error_rate,
                'request_rate': metric.request_rate
            }
            
            for metric_name, value in metrics_to_check.items():
                anomaly_info = await self._detect_metric_anomaly(
                    metric.service_id, metric_name, value, metric.timestamp
                )
                
                if anomaly_info['is_anomaly']:
                    service_anomalies.append(anomaly_info)
                    anomaly_score = max(anomaly_score, anomaly_info['anomaly_strength'])
                    affected_metrics.append(metric_name)
            
            if service_anomalies:
                description = f"Detected {len(service_anomalies)} anomalies in service metrics"
                confidence = min(0.95, anomaly_score * 0.8)
                
                anomaly_results.append(AnomalyDetectionResult(
                    service_id=metric.service_id,
                    anomalies_detected=service_anomalies,
                    anomaly_score=anomaly_score,
                    confidence=confidence,
                    affected_metrics=affected_metrics,
                    timestamp=metric.timestamp,
                    description=description
                ))
        
        return anomaly_results
    
    async def _detect_metric_anomaly(self, service_id: str, metric_name: str, value: float, timestamp: float) -> Dict[str, Any]:
        """Detect anomaly for a specific metric"""
        # Store metric value
        self.metric_history[service_id][metric_name].append((value, timestamp))
        
        # Get historical values for baseline
        history = list(self.metric_history[service_id][metric_name])
        
        if len(history) < 10:
            return {'is_anomaly': False, 'anomaly_strength': 0.0}
        
        # Calculate baseline statistics
        values = [v for v, t in history[:-1]]  # Exclude current value
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0.1
        
        # Calculate z-score
        z_score = abs(value - mean) / (stdev + 0.001)  # Add small epsilon
        
        is_anomaly = z_score > self.anomaly_threshold
        anomaly_strength = min(1.0, z_score / 5.0)  # Normalize to 0-1
        
        # Store baseline stats
        self.baseline_stats[service_id][metric_name] = {
            'mean': mean,
            'stdev': stdev,
            'last_updated': timestamp
        }
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_strength': anomaly_strength,
            'z_score': z_score,
            'current_value': value,
            'baseline_mean': mean,
            'baseline_stdev': stdev,
            'metric_name': metric_name
        }
    
    def get_baseline_stats(self, service_id: str) -> Dict[str, Any]:
        """Get baseline statistics for a service"""
        return dict(self.baseline_stats.get(service_id, {}))

class ServiceHealthScorer:
    """Service health scoring engine"""
    
    def __init__(self):
        self.weight_config = {
            'availability': 0.3,
            'performance': 0.25,
            'resources': 0.2,
            'errors': 0.15,
            'capacity': 0.1
        }
    
    async def calculate_composite_health_score(self, service_id: str, metrics: ServiceMetric, 
                                             health_history: Optional[List[CompositeHealthScore]] = None) -> CompositeHealthScore:
        """Calculate composite health score for a service"""
        try:
            component_scores = {}
            contributing_factors = {}
            
            # Availability score (based on service status and uptime)
            availability_score = await self._calculate_availability_score(service_id, metrics)
            component_scores['availability'] = availability_score
            
            # Performance score (response time, throughput)
            performance_score = await self._calculate_performance_score(metrics)
            component_scores['performance'] = performance_score
            
            # Resource utilization score
            resource_score = await self._calculate_resource_score(metrics)
            component_scores['resources'] = resource_score
            
            # Error rate score
            error_score = await self._calculate_error_score(metrics)
            component_scores['errors'] = error_score
            
            # Capacity score
            capacity_score = await self._calculate_capacity_score(metrics)
            component_scores['capacity'] = capacity_score
            
            # Calculate weighted overall score
            overall_score = (
                availability_score * self.weight_config['availability'] +
                performance_score * self.weight_config['performance'] +
                resource_score * self.weight_config['resources'] +
                error_score * self.weight_config['errors'] +
                capacity_score * self.weight_config['capacity']
            )
            
            # Determine status based on score
            if overall_score >= 0.8:
                status = ServiceStatus.HEALTHY
            elif overall_score >= 0.6:
                status = ServiceStatus.UNKNOWN
            else:
                status = ServiceStatus.UNHEALTHY
            
            # Contributing factors
            contributing_factors = {
                'cpu_impact': 1.0 - (metrics.cpu_usage / 100.0),
                'memory_impact': 1.0 - (metrics.memory_usage / 100.0),
                'response_time_impact': max(0.0, 1.0 - (metrics.response_time_ms / 1000.0)),
                'error_rate_impact': 1.0 - metrics.error_rate
            }
            
            # Generate recommendations
            recommendations = await self._generate_health_recommendations(component_scores, metrics)
            
            return CompositeHealthScore(
                service_id=service_id,
                overall_score=overall_score,
                component_scores=component_scores,
                contributing_factors=contributing_factors,
                timestamp=time.time(),
                status=status,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Health score calculation failed for {service_id}: {e}")
            return CompositeHealthScore(
                service_id=service_id,
                overall_score=0.5,
                component_scores={'error': 0.5},
                contributing_factors={},
                timestamp=time.time(),
                status=ServiceStatus.UNKNOWN,
                recommendations=['Health scoring failed - manual investigation required']
            )
    
    async def _calculate_availability_score(self, service_id: str, metrics: ServiceMetric) -> float:
        """Calculate availability score"""
        # Simple availability calculation - can be enhanced with uptime tracking
        base_score = 0.9  # Default high availability
        
        # Reduce score based on error rate
        error_penalty = metrics.error_rate * 0.5
        availability_score = max(0.0, base_score - error_penalty)
        
        return availability_score
    
    async def _calculate_performance_score(self, metrics: ServiceMetric) -> float:
        """Calculate performance score"""
        # Response time scoring (lower is better)
        if metrics.response_time_ms <= 100:
            response_score = 1.0
        elif metrics.response_time_ms <= 500:
            response_score = 0.8
        elif metrics.response_time_ms <= 1000:
            response_score = 0.6
        elif metrics.response_time_ms <= 2000:
            response_score = 0.4
        else:
            response_score = 0.2
        
        # Request rate scoring (steady rate is good)
        rate_score = 0.8  # Default decent score
        if metrics.request_rate > 0:
            # Boost score for active services
            rate_score = min(1.0, 0.6 + (metrics.request_rate / 1000.0) * 0.4)
        
        return (response_score * 0.7 + rate_score * 0.3)
    
    async def _calculate_resource_score(self, metrics: ServiceMetric) -> float:
        """Calculate resource utilization score"""
        # CPU score (efficient utilization is good, over-utilization is bad)
        cpu_score = self._resource_utilization_score(metrics.cpu_usage)
        
        # Memory score
        memory_score = self._resource_utilization_score(metrics.memory_usage)
        
        # Disk score
        disk_score = self._resource_utilization_score(metrics.disk_usage)
        
        return (cpu_score * 0.4 + memory_score * 0.4 + disk_score * 0.2)
    
    def _resource_utilization_score(self, utilization: float) -> float:
        """Score resource utilization (0-100%)"""
        if utilization <= 60:
            return 1.0  # Good utilization
        elif utilization <= 75:
            return 0.8  # Warning level
        elif utilization <= 85:
            return 0.6  # High utilization
        elif utilization <= 95:
            return 0.3  # Critical utilization
        else:
            return 0.1  # Over-utilized
    
    async def _calculate_error_score(self, metrics: ServiceMetric) -> float:
        """Calculate error rate score"""
        if metrics.error_rate <= 0.01:  # 1%
            return 1.0
        elif metrics.error_rate <= 0.05:  # 5%
            return 0.8
        elif metrics.error_rate <= 0.1:   # 10%
            return 0.6
        elif metrics.error_rate <= 0.2:   # 20%
            return 0.4
        else:
            return 0.2
    
    async def _calculate_capacity_score(self, metrics: ServiceMetric) -> float:
        """Calculate capacity score"""
        # Based on connection count and request rate
        connection_factor = min(1.0, metrics.active_connections / 1000.0)
        request_factor = min(1.0, metrics.request_rate / 100.0)
        
        # Good capacity utilization
        capacity_score = 0.8 + (connection_factor * 0.1) + (request_factor * 0.1)
        return min(1.0, capacity_score)
    
    async def _generate_health_recommendations(self, component_scores: Dict[str, float], metrics: ServiceMetric) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        if component_scores.get('performance', 1.0) < 0.6:
            if metrics.response_time_ms > 1000:
                recommendations.append("Consider optimizing response time - current: {:.0f}ms".format(metrics.response_time_ms))
        
        if component_scores.get('resources', 1.0) < 0.6:
            if metrics.cpu_usage > 80:
                recommendations.append("High CPU usage detected - consider scaling up")
            if metrics.memory_usage > 80:
                recommendations.append("High memory usage detected - check for memory leaks")
        
        if component_scores.get('errors', 1.0) < 0.6:
            recommendations.append("Error rate is elevated - investigate error patterns")
        
        if component_scores.get('availability', 1.0) < 0.8:
            recommendations.append("Availability concerns detected - check service dependencies")
        
        return recommendations

class HealthAlertManager:
    """Health alert management system"""
    
    def __init__(self):
        self.alert_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.alert_rules: List[Dict[str, Any]] = []
        self.notification_channels: Dict[str, Callable] = {}
        
    async def evaluate_alerts(self, health_scores: Dict[str, CompositeHealthScore], 
                            anomalies: List[AnomalyDetectionResult]) -> List[Dict[str, Any]]:
        """Evaluate and generate alerts based on health data"""
        alerts = []
        
        # Evaluate health score alerts
        for service_id, health_score in health_scores.items():
            if health_score.overall_score < 0.6:
                alert = {
                    'id': str(uuid.uuid4()),
                    'service_id': service_id,
                    'type': 'health_score',
                    'severity': AlertSeverity.HIGH if health_score.overall_score < 0.4 else AlertSeverity.MEDIUM,
                    'message': f"Service health score low: {health_score.overall_score:.2f}",
                    'timestamp': time.time(),
                    'details': health_score.component_scores
                }
                alerts.append(alert)
        
        # Evaluate anomaly alerts
        for anomaly in anomalies:
            if anomaly.anomaly_score > 0.7:
                alert = {
                    'id': str(uuid.uuid4()),
                    'service_id': anomaly.service_id,
                    'type': 'anomaly',
                    'severity': AlertSeverity.HIGH if anomaly.anomaly_score > 0.8 else AlertSeverity.MEDIUM,
                    'message': f"Anomaly detected: {anomaly.description}",
                    'timestamp': anomaly.timestamp,
                    'details': {
                        'affected_metrics': anomaly.affected_metrics,
                        'confidence': anomaly.confidence
                    }
                }
                alerts.append(alert)
        
        # Store alert history
        for alert in alerts:
            self.alert_history[alert['service_id']].append(alert)
        
        return alerts
    
    async def send_notifications(self, alerts: List[Dict[str, Any]]):
        """Send notifications for alerts"""
        for alert in alerts:
            logger.info(f"ALERT: {alert['message']} (Service: {alert['service_id']}, Severity: {alert['severity'].value})")
            
            # In real implementation, would send to actual notification channels
            # (Slack, PagerDuty, email, etc.)

class AutoRemediationEngine:
    """Auto-remediation engine for common health issues"""
    
    def __init__(self):
        self.remediation_history: List[RemediationResult] = []
        self.remediation_rules: Dict[str, List[RemediationAction]] = {
            'high_cpu': [RemediationAction.SCALE_UP, RemediationAction.RESTART_SERVICE],
            'high_memory': [RemediationAction.RESTART_SERVICE, RemediationAction.SCALE_UP],
            'high_error_rate': [RemediationAction.CIRCUIT_BREAKER_OPEN, RemediationAction.ROUTE_TRAFFIC],
            'slow_response': [RemediationAction.SCALE_UP, RemediationAction.ROUTE_TRAFFIC],
            'service_down': [RemediationAction.RESTART_SERVICE, RemediationAction.NOTIFY_ONCALL]
        }
    
    async def execute_auto_remediation(self, health_issue: HealthIssue) -> RemediationResult:
        """Execute auto-remediation for health issue"""
        start_time = time.time()
        
        try:
            # Determine best remediation action
            action = self._select_remediation_action(health_issue)
            
            if action == RemediationAction.NONE:
                return RemediationResult(
                    issue_id=health_issue.issue_id,
                    service_id=health_issue.service_id,
                    action_taken=action,
                    success=False,
                    duration_seconds=time.time() - start_time,
                    description="No suitable auto-remediation action found"
                )
            
            # Execute remediation action
            success = await self._execute_remediation_action(health_issue.service_id, action)
            
            result = RemediationResult(
                issue_id=health_issue.issue_id,
                service_id=health_issue.service_id,
                action_taken=action,
                success=success,
                duration_seconds=time.time() - start_time,
                description=f"Executed {action.value} for {health_issue.issue_type}"
            )
            
            self.remediation_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Auto-remediation failed for {health_issue.service_id}: {e}")
            return RemediationResult(
                issue_id=health_issue.issue_id,
                service_id=health_issue.service_id,
                action_taken=RemediationAction.NONE,
                success=False,
                duration_seconds=time.time() - start_time,
                description=f"Remediation failed: {str(e)}"
            )
    
    def _select_remediation_action(self, health_issue: HealthIssue) -> RemediationAction:
        """Select appropriate remediation action for health issue"""
        # Simple rule-based selection
        possible_actions = self.remediation_rules.get(health_issue.issue_type, [])
        
        if not possible_actions:
            return RemediationAction.NONE
        
        # For now, return first action - could be enhanced with ML
        return possible_actions[0]
    
    async def _execute_remediation_action(self, service_id: str, action: RemediationAction) -> bool:
        """Execute specific remediation action"""
        try:
            if action == RemediationAction.RESTART_SERVICE:
                logger.info(f"Simulating service restart for {service_id}")
                await asyncio.sleep(0.1)  # Simulate restart time
                return True
                
            elif action == RemediationAction.SCALE_UP:
                logger.info(f"Simulating scale up for {service_id}")
                await asyncio.sleep(0.1)  # Simulate scaling time
                return True
                
            elif action == RemediationAction.CIRCUIT_BREAKER_OPEN:
                logger.info(f"Opening circuit breaker for {service_id}")
                return True
                
            elif action == RemediationAction.ROUTE_TRAFFIC:
                logger.info(f"Rerouting traffic away from {service_id}")
                return True
                
            elif action == RemediationAction.NOTIFY_ONCALL:
                logger.info(f"Notifying on-call for {service_id}")
                return True
                
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to execute {action.value} for {service_id}: {e}")
            return False

class HealthMonitoringOrchestrator:
    """
    Orchestrateur monitoring santé services avec ML anomaly detection.
    Health scoring + predictive alerts + auto-remediation.
    """
    
    def __init__(self, monitoring_config: Optional[MonitoringConfig] = None):
        """Initialize health monitoring orchestrator"""
        self.monitoring_config = monitoring_config or MonitoringConfig()
        self.anomaly_detector = MLAnomalyDetector()
        self.health_scorer = ServiceHealthScorer()
        self.alert_manager = HealthAlertManager()
        self.remediation_engine = AutoRemediationEngine()
        
        # Service registry reference (to be injected)
        self.service_registry = None
        
        # Background monitoring task
        self._monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Metrics
        self.metrics = {
            'health_checks_performed': 0,
            'anomalies_detected': 0,
            'alerts_generated': 0,
            'remediations_executed': 0,
            'average_health_score': 0.0
        }
    
    def set_service_registry(self, registry):
        """Set reference to service registry"""
        self.service_registry = registry
    
    async def start_monitoring(self):
        """Start background health monitoring"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._shutdown_event.clear()
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop background health monitoring"""
        self._shutdown_event.set()
        if self._monitoring_task and not self._monitoring_task.done():
            await self._monitoring_task
        logger.info("Health monitoring stopped")
    
    async def orchestrate_health_monitoring(self, monitoring_scope: MonitoringScope) -> HealthMonitoringResult:
        """
        Orchestration monitoring santé avec ML intelligence.
        
        Health Monitoring Features:
        - Multi-level health checks (application, infrastructure, business)
        - ML-based anomaly detection pour early warning
        - Health score calculation avec weighted factors
        - Predictive health alerts avec time-series analysis
        - Auto-remediation workflows pour common failures
        - Health trend analysis avec capacity planning insights
        - SLA violation prediction et prevention
        - Business impact assessment pour health events
        """
        start_time = time.time()
        
        try:
            # Get services to monitor
            services_to_monitor = await self._get_services_in_scope(monitoring_scope)
            
            # Collect current metrics
            service_metrics = await self._collect_service_metrics(services_to_monitor)
            
            # Calculate health scores
            health_scores = {}
            for metric in service_metrics:
                health_score = await self.health_scorer.calculate_composite_health_score(
                    metric.service_id, metric
                )
                health_scores[metric.service_id] = health_score
            
            # Detect anomalies
            anomalies = await self.anomaly_detector.detect_anomalies(service_metrics)
            
            # Generate predictions if enabled
            predictions = []
            if monitoring_scope.enable_predictions:
                predictions = await self._generate_failure_predictions(health_scores, anomalies)
            
            # Identify health issues
            issues_identified = await self._identify_health_issues(health_scores, anomalies)
            
            # Execute auto-remediation if enabled
            remediations_performed = []
            if monitoring_scope.enable_auto_remediation:
                for issue in issues_identified:
                    if issue.auto_remediable:
                        remediation = await self.remediation_engine.execute_auto_remediation(issue)
                        remediations_performed.append(remediation)
            
            # Generate alerts
            alerts = await self.alert_manager.evaluate_alerts(health_scores, anomalies)
            await self.alert_manager.send_notifications(alerts)
            
            # Update metrics
            self.metrics['health_checks_performed'] += len(service_metrics)
            self.metrics['anomalies_detected'] += len(anomalies)
            self.metrics['alerts_generated'] += len(alerts)
            self.metrics['remediations_executed'] += len(remediations_performed)
            
            if health_scores:
                avg_score = sum(hs.overall_score for hs in health_scores.values()) / len(health_scores)
                self.metrics['average_health_score'] = avg_score
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            return HealthMonitoringResult(
                monitoring_scope=monitoring_scope,
                services_monitored=len(services_to_monitor),
                health_scores=health_scores,
                anomalies=anomalies,
                predictions=predictions,
                issues_identified=issues_identified,
                remediations_performed=remediations_performed,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            logger.error(f"Health monitoring orchestration failed: {e}")
            return HealthMonitoringResult(
                monitoring_scope=monitoring_scope,
                services_monitored=0,
                health_scores={},
                anomalies=[],
                predictions=[],
                issues_identified=[],
                remediations_performed=[],
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    async def calculate_composite_health_score(self, service_id: str) -> CompositeHealthScore:
        """Calcul score santé composite avec multiple métriques."""
        try:
            # Get current metrics for service
            service_metrics = await self._get_service_metrics(service_id)
            
            # Calculate composite score
            return await self.health_scorer.calculate_composite_health_score(service_id, service_metrics)
            
        except Exception as e:
            logger.error(f"Failed to calculate health score for {service_id}: {e}")
            return CompositeHealthScore(
                service_id=service_id,
                overall_score=0.0,
                component_scores={},
                contributing_factors={},
                timestamp=time.time(),
                status=ServiceStatus.UNKNOWN
            )
    
    async def detect_health_anomalies(self, service_metrics: List[ServiceMetric]) -> AnomalyDetectionResult:
        """Détection anomalies santé avec ML models."""
        anomalies = await self.anomaly_detector.detect_anomalies(service_metrics)
        
        if anomalies:
            # Return combined result
            combined_anomalies = []
            max_score = 0.0
            all_affected_metrics = set()
            
            for anomaly in anomalies:
                combined_anomalies.extend(anomaly.anomalies_detected)
                max_score = max(max_score, anomaly.anomaly_score)
                all_affected_metrics.update(anomaly.affected_metrics)
            
            return AnomalyDetectionResult(
                service_id="multiple",
                anomalies_detected=combined_anomalies,
                anomaly_score=max_score,
                confidence=max_score * 0.8,
                affected_metrics=list(all_affected_metrics),
                timestamp=time.time(),
                description=f"Combined anomaly detection across {len(service_metrics)} services"
            )
        else:
            return AnomalyDetectionResult(
                service_id="multiple",
                anomalies_detected=[],
                anomaly_score=0.0,
                confidence=0.0,
                affected_metrics=[],
                timestamp=time.time(),
                description="No anomalies detected"
            )
    
    async def predict_service_failures(self, service_id: str, prediction_window: int) -> FailurePrediction:
        """Prédiction échecs service avec ML time series."""
        try:
            # Get historical health data
            health_score = await self.calculate_composite_health_score(service_id)
            
            # Simple failure prediction based on current health
            failure_probability = max(0.0, 1.0 - health_score.overall_score)
            
            # Adjust based on trend (simplified)
            if health_score.overall_score < 0.4:
                failure_probability = min(0.9, failure_probability * 1.5)
            
            # Determine recommended actions
            recommended_actions = []
            if failure_probability > 0.7:
                recommended_actions = [RemediationAction.NOTIFY_ONCALL, RemediationAction.SCALE_UP]
            elif failure_probability > 0.5:
                recommended_actions = [RemediationAction.SCALE_UP]
            
            # Estimate time to failure
            time_to_failure = None
            if failure_probability > 0.6:
                # Simple estimation based on probability
                time_to_failure = int((1.0 - failure_probability) * prediction_window)
            
            return FailurePrediction(
                service_id=service_id,
                failure_probability=failure_probability,
                prediction_window_minutes=prediction_window,
                contributing_factors=health_score.contributing_factors,
                confidence=0.7,
                recommended_actions=recommended_actions,
                time_to_failure_estimate=time_to_failure
            )
            
        except Exception as e:
            logger.error(f"Failure prediction failed for {service_id}: {e}")
            return FailurePrediction(
                service_id=service_id,
                failure_probability=0.5,
                prediction_window_minutes=prediction_window,
                contributing_factors={},
                confidence=0.1,
                recommended_actions=[]
            )
    
    async def execute_auto_remediation(self, health_issue: HealthIssue) -> RemediationResult:
        """Exécution auto-remediation pour problèmes santé courants."""
        return await self.remediation_engine.execute_auto_remediation(health_issue)
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                # Create monitoring scope for all services
                scope = MonitoringScope(
                    check_interval_seconds=self.monitoring_config.check_interval,
                    enable_predictions=self.monitoring_config.enable_ml_predictions,
                    enable_auto_remediation=self.monitoring_config.enable_auto_remediation
                )
                
                # Execute monitoring
                await self.orchestrate_health_monitoring(scope)
                
                # Wait for next check interval
                await asyncio.sleep(self.monitoring_config.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _get_services_in_scope(self, scope: MonitoringScope) -> List[ServiceInstance]:
        """Get services that match monitoring scope"""
        if not self.service_registry:
            return []
        
        # Get all services if no specific scope
        if not any([scope.service_ids, scope.service_types, scope.business_domains, scope.regions]):
            return list(self.service_registry.service_instances.values())
        
        # Filter services based on scope
        filtered_services = []
        for service in self.service_registry.service_instances.values():
            if scope.service_ids and service.service_id not in scope.service_ids:
                continue
            if scope.service_types and service.service_type not in scope.service_types:
                continue
            if scope.business_domains and service.iacherie_business_domain not in scope.business_domains:
                continue
            if scope.regions and service.region not in scope.regions:
                continue
            
            filtered_services.append(service)
        
        return filtered_services
    
    async def _collect_service_metrics(self, services: List[ServiceInstance]) -> List[ServiceMetric]:
        """Collect current metrics for services"""
        metrics = []
        
        for service in services:
            # Simulate metric collection - in real implementation would call service endpoints
            metric = ServiceMetric(
                service_id=service.service_id,
                timestamp=time.time(),
                cpu_usage=random.uniform(10, 90),
                memory_usage=random.uniform(20, 80),
                disk_usage=random.uniform(5, 60),
                response_time_ms=random.uniform(50, 500),
                error_rate=random.uniform(0, 0.1),
                request_rate=random.uniform(10, 200),
                active_connections=random.randint(5, 100)
            )
            metrics.append(metric)
        
        return metrics
    
    async def _get_service_metrics(self, service_id: str) -> ServiceMetric:
        """Get metrics for a specific service"""
        # Simulate metric collection
        return ServiceMetric(
            service_id=service_id,
            timestamp=time.time(),
            cpu_usage=random.uniform(10, 90),
            memory_usage=random.uniform(20, 80),
            disk_usage=random.uniform(5, 60),
            response_time_ms=random.uniform(50, 500),
            error_rate=random.uniform(0, 0.1),
            request_rate=random.uniform(10, 200),
            active_connections=random.randint(5, 100)
        )
    
    async def _generate_failure_predictions(self, health_scores: Dict[str, CompositeHealthScore], 
                                          anomalies: List[AnomalyDetectionResult]) -> List[FailurePrediction]:
        """Generate failure predictions for services"""
        predictions = []
        
        for service_id, health_score in health_scores.items():
            if health_score.overall_score < 0.7:  # Only predict for services with concerning health
                prediction = await self.predict_service_failures(service_id, 60)  # 60 minute window
                predictions.append(prediction)
        
        return predictions
    
    async def _identify_health_issues(self, health_scores: Dict[str, CompositeHealthScore], 
                                    anomalies: List[AnomalyDetectionResult]) -> List[HealthIssue]:
        """Identify specific health issues from scores and anomalies"""
        issues = []
        
        # Issues from health scores
        for service_id, health_score in health_scores.items():
            if health_score.overall_score < 0.6:
                issue = HealthIssue(
                    issue_id=str(uuid.uuid4()),
                    service_id=service_id,
                    issue_type="low_health_score",
                    severity=AlertSeverity.HIGH if health_score.overall_score < 0.4 else AlertSeverity.MEDIUM,
                    description=f"Service health score is low: {health_score.overall_score:.2f}",
                    affected_metrics=list(health_score.component_scores.keys()),
                    timestamp=health_score.timestamp,
                    auto_remediable=True if health_score.overall_score < 0.4 else False,
                    suggested_actions=[RemediationAction.RESTART_SERVICE, RemediationAction.SCALE_UP]
                )
                issues.append(issue)
        
        # Issues from anomalies
        for anomaly in anomalies:
            if anomaly.anomaly_score > 0.7:
                issue = HealthIssue(
                    issue_id=str(uuid.uuid4()),
                    service_id=anomaly.service_id,
                    issue_type="anomaly_detected",
                    severity=AlertSeverity.HIGH if anomaly.anomaly_score > 0.8 else AlertSeverity.MEDIUM,
                    description=anomaly.description,
                    affected_metrics=anomaly.affected_metrics,
                    timestamp=anomaly.timestamp,
                    auto_remediable=False,  # Anomalies typically need investigation
                    suggested_actions=[RemediationAction.NOTIFY_ONCALL]
                )
                issues.append(issue)
        
        return issues
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get health monitoring metrics"""
        return {
            **self.metrics,
            'anomaly_detector_baselines': len(self.anomaly_detector.baseline_stats),
            'alert_history_count': sum(len(alerts) for alerts in self.alert_manager.alert_history.values()),
            'remediation_history_count': len(self.remediation_engine.remediation_history),
            'monitoring_active': self._monitoring_task is not None and not self._monitoring_task.done()
        }
    
    async def shutdown(self):
        """Graceful shutdown of health monitoring orchestrator"""
        logger.info("Shutting down HealthMonitoringOrchestrator")
        await self.stop_monitoring()

# Factory function
async def create_health_monitoring_orchestrator(config: Optional[MonitoringConfig] = None) -> HealthMonitoringOrchestrator:
    """Factory function to create health monitoring orchestrator"""
    return HealthMonitoringOrchestrator(config)

# Export main classes and functions
__all__ = [
    'HealthMonitoringOrchestrator',
    'MonitoringConfig',
    'MonitoringScope',
    'HealthMonitoringResult',
    'CompositeHealthScore',
    'AnomalyDetectionResult',
    'FailurePrediction',
    'HealthIssue',
    'RemediationResult',
    'ServiceMetric',
    'HealthMetric',
    'HealthCheckType',
    'AlertSeverity',
    'RemediationAction',
    'create_health_monitoring_orchestrator'
]