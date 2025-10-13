"""
Retry Analytics Engine - IA Chérie
================================
Moteur analytics retry avec insights business.
Success rate analytics + cost optimization + performance insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Retry Mechanisms
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture retry mechanisms et tous ses algorithmes sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import time
import json
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import random

logger = logging.getLogger(__name__)

class AnalyticsMetric(Enum):
    """Types de métriques analytics"""
    SUCCESS_RATE = "success_rate"
    FAILURE_RATE = "failure_rate"
    RETRY_FREQUENCY = "retry_frequency"
    COST_PER_OPERATION = "cost_per_operation"
    LATENCY_PERCENTILES = "latency_percentiles"
    RESOURCE_UTILIZATION = "resource_utilization"
    ERROR_DISTRIBUTION = "error_distribution"
    PERFORMANCE_TRENDS = "performance_trends"

class TimeWindow(Enum):
    """Fenêtres temporelles pour analytics"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class BusinessImpact(Enum):
    """Types d'impact business"""
    REVENUE_IMPACT = "revenue_impact"
    USER_EXPERIENCE = "user_experience"
    OPERATIONAL_COST = "operational_cost"
    SYSTEM_RELIABILITY = "system_reliability"
    COMPLIANCE_RISK = "compliance_risk"

@dataclass
class RetryEvent:
    """Événement retry pour analytics"""
    event_id: str
    operation_id: str
    service_name: str
    retry_count: int
    success: bool
    execution_time: float
    error_type: Optional[str] = None
    cost: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsConfig:
    """Configuration pour analytics engine"""
    enabled_metrics: List[AnalyticsMetric]
    time_windows: List[TimeWindow]
    business_impact_tracking: bool = True
    cost_tracking_enabled: bool = True
    real_time_alerts: bool = True
    data_retention_days: int = 90
    aggregation_intervals: Dict[str, int] = field(default_factory=lambda: {
        'real_time': 60,  # 1 minute
        'hourly': 3600,   # 1 hour
        'daily': 86400    # 1 day
    })

@dataclass
class PerformanceMetrics:
    """Métriques performance retry"""
    success_rate: float
    average_retry_count: float
    p50_latency: float
    p95_latency: float
    p99_latency: float
    total_operations: int
    failed_operations: int
    total_cost: float
    cost_per_success: float
    efficiency_score: float

@dataclass
class BusinessInsights:
    """Insights business pour retry operations"""
    revenue_impact: float
    user_satisfaction_impact: float
    operational_cost_savings: float
    reliability_improvement: float
    compliance_score: float
    recommendations: List[str]

@dataclass
class RetryAnalytics:
    """Résultat complet analytics retry"""
    analysis_id: str
    time_window: TimeWindow
    performance_metrics: PerformanceMetrics
    business_insights: BusinessInsights
    service_breakdown: Dict[str, PerformanceMetrics]
    trends: Dict[str, List[float]]
    anomalies: List[Dict]
    generated_at: datetime = field(default_factory=datetime.now)

class MetricsCollector:
    """Collecteur métriques retry en temps réel"""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.retry_events = deque(maxlen=10000)  # Buffer événements
        self.service_metrics = defaultdict(list)
        self.cost_tracking = {}
        self.real_time_buffer = deque(maxlen=1000)
        
    async def collect_retry_event(self, event: RetryEvent):
        """Collection événement retry"""
        self.retry_events.append(event)
        self.service_metrics[event.service_name].append(event)
        self.real_time_buffer.append(event)
        
        # Tracking coût
        if self.config.cost_tracking_enabled:
            await self._update_cost_tracking(event)
        
        # Alertes temps réel si activées
        if self.config.real_time_alerts:
            await self._check_real_time_alerts(event)
    
    async def _update_cost_tracking(self, event: RetryEvent):
        """Mise à jour tracking coûts"""
        service_key = event.service_name
        
        if service_key not in self.cost_tracking:
            self.cost_tracking[service_key] = {
                'total_cost': 0.0,
                'successful_operations': 0,
                'failed_operations': 0,
                'retry_costs': 0.0
            }
        
        tracking = self.cost_tracking[service_key]
        tracking['total_cost'] += event.cost
        
        if event.success:
            tracking['successful_operations'] += 1
        else:
            tracking['failed_operations'] += 1
        
        if event.retry_count > 0:
            tracking['retry_costs'] += event.cost
    
    async def _check_real_time_alerts(self, event: RetryEvent):
        """Vérification alertes temps réel"""
        # Calcul success rate sur dernières 100 opérations
        recent_events = list(self.real_time_buffer)[-100:]
        if len(recent_events) >= 10:
            success_rate = sum(1 for e in recent_events if e.success) / len(recent_events)
            
            if success_rate < 0.8:  # Seuil alerte
                logger.warning(f"Low success rate detected: {success_rate:.2%} for {event.service_name}")
        
        # Alertes coût élevé
        if event.cost > 10.0:  # Seuil coût
            logger.warning(f"High cost operation detected: ${event.cost:.2f} for {event.operation_id}")

class PerformanceAnalyzer:
    """Analyseur performance retry operations"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    async def analyze_performance(self, events: List[RetryEvent], time_window: TimeWindow) -> PerformanceMetrics:
        """Analyse performance sur fenêtre temporelle"""
        if not events:
            return self._empty_metrics()
        
        # Calculs métriques de base
        total_operations = len(events)
        successful_operations = sum(1 for e in events if e.success)
        success_rate = successful_operations / total_operations if total_operations > 0 else 0.0
        
        # Métriques retry
        retry_counts = [e.retry_count for e in events]
        average_retry_count = statistics.mean(retry_counts) if retry_counts else 0.0
        
        # Métriques latence
        execution_times = [e.execution_time for e in events]
        p50_latency = statistics.median(execution_times) if execution_times else 0.0
        p95_latency = self._percentile(execution_times, 0.95) if execution_times else 0.0
        p99_latency = self._percentile(execution_times, 0.99) if execution_times else 0.0
        
        # Métriques coût
        total_cost = sum(e.cost for e in events)
        cost_per_success = total_cost / successful_operations if successful_operations > 0 else 0.0
        
        # Score efficacité (composite)
        efficiency_score = self._calculate_efficiency_score(
            success_rate, average_retry_count, p95_latency, cost_per_success
        )
        
        return PerformanceMetrics(
            success_rate=success_rate,
            average_retry_count=average_retry_count,
            p50_latency=p50_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            total_operations=total_operations,
            failed_operations=total_operations - successful_operations,
            total_cost=total_cost,
            cost_per_success=cost_per_success,
            efficiency_score=efficiency_score
        )
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calcul percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _calculate_efficiency_score(self, success_rate: float, avg_retries: float, 
                                  p95_latency: float, cost_per_success: float) -> float:
        """Calcul score efficacité composite"""
        # Normalisation des métriques (0-1)
        success_score = success_rate
        retry_score = max(0, 1 - (avg_retries / 5.0))  # Pénalité pour retries élevés
        latency_score = max(0, 1 - (p95_latency / 1000.0))  # Pénalité latence >1s
        cost_score = max(0, 1 - (cost_per_success / 100.0))  # Pénalité coût >$100
        
        # Score pondéré
        weights = {'success': 0.4, 'retry': 0.2, 'latency': 0.2, 'cost': 0.2}
        
        return (
            weights['success'] * success_score +
            weights['retry'] * retry_score +
            weights['latency'] * latency_score +
            weights['cost'] * cost_score
        )
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Métriques vides pour cas sans données"""
        return PerformanceMetrics(
            success_rate=0.0,
            average_retry_count=0.0,
            p50_latency=0.0,
            p95_latency=0.0,
            p99_latency=0.0,
            total_operations=0,
            failed_operations=0,
            total_cost=0.0,
            cost_per_success=0.0,
            efficiency_score=0.0
        )

class BusinessImpactAnalyzer:
    """Analyseur impact business des retry operations"""
    
    def __init__(self):
        self.business_models = {
            'revenue_model': self._calculate_revenue_impact,
            'user_experience_model': self._calculate_ux_impact,
            'cost_model': self._calculate_cost_impact,
            'reliability_model': self._calculate_reliability_impact,
            'compliance_model': self._calculate_compliance_impact
        }
    
    async def analyze_business_impact(self, metrics: PerformanceMetrics, 
                                    events: List[RetryEvent]) -> BusinessInsights:
        """Analyse impact business des retry operations"""
        
        # Calcul impacts individuels
        revenue_impact = await self._calculate_revenue_impact(metrics, events)
        ux_impact = await self._calculate_ux_impact(metrics, events)
        cost_impact = await self._calculate_cost_impact(metrics, events)
        reliability_impact = await self._calculate_reliability_impact(metrics, events)
        compliance_impact = await self._calculate_compliance_impact(metrics, events)
        
        # Génération recommandations
        recommendations = await self._generate_recommendations(
            metrics, revenue_impact, ux_impact, cost_impact
        )
        
        return BusinessInsights(
            revenue_impact=revenue_impact,
            user_satisfaction_impact=ux_impact,
            operational_cost_savings=cost_impact,
            reliability_improvement=reliability_impact,
            compliance_score=compliance_impact,
            recommendations=recommendations
        )
    
    async def _calculate_revenue_impact(self, metrics: PerformanceMetrics, events: List[RetryEvent]) -> float:
        """Calcul impact revenus"""
        # Simulation modèle business
        # Success rate impact sur conversion
        conversion_impact = (metrics.success_rate - 0.95) * 1000000  # $1M base revenue
        
        # Latency impact sur abandon rate
        latency_penalty = min(0, (200 - metrics.p95_latency) * 5000)  # Pénalité latence >200ms
        
        return conversion_impact + latency_penalty
    
    async def _calculate_ux_impact(self, metrics: PerformanceMetrics, events: List[RetryEvent]) -> float:
        """Calcul impact expérience utilisateur"""
        # Score UX basé sur success rate et latence
        success_ux = metrics.success_rate * 100
        latency_ux = max(0, 100 - (metrics.p95_latency / 10))  # Pénalité latence
        retry_ux = max(0, 100 - (metrics.average_retry_count * 10))  # Pénalité retries
        
        return (success_ux + latency_ux + retry_ux) / 3
    
    async def _calculate_cost_impact(self, metrics: PerformanceMetrics, events: List[RetryEvent]) -> float:
        """Calcul impact coût opérationnel"""
        # Calcul économies par optimisation retry
        baseline_cost = metrics.total_operations * 1.0  # $1 par opération baseline
        actual_cost = metrics.total_cost
        
        return baseline_cost - actual_cost
    
    async def _calculate_reliability_impact(self, metrics: PerformanceMetrics, events: List[RetryEvent]) -> float:
        """Calcul impact fiabilité système"""
        # Score fiabilité basé sur success rate et consistency
        base_reliability = metrics.success_rate * 100
        
        # Bonus pour consistency (faible variance retry count)
        retry_counts = [e.retry_count for e in events]
        if retry_counts:
            variance_penalty = statistics.stdev(retry_counts) * 5
            return max(0, base_reliability - variance_penalty)
        
        return base_reliability
    
    async def _calculate_compliance_impact(self, metrics: PerformanceMetrics, events: List[RetryEvent]) -> float:
        """Calcul score compliance"""
        # Score compliance basé sur audit trail et success rate
        audit_score = 85.0  # Score base
        
        # Bonus pour success rate élevé
        if metrics.success_rate > 0.95:
            audit_score += 10
        elif metrics.success_rate > 0.90:
            audit_score += 5
        
        # Pénalité pour retries excessifs
        if metrics.average_retry_count > 3:
            audit_score -= 10
        
        return min(100, max(0, audit_score))
    
    async def _generate_recommendations(self, metrics: PerformanceMetrics, 
                                      revenue_impact: float, ux_impact: float, 
                                      cost_impact: float) -> List[str]:
        """Génération recommandations basées sur analytics"""
        recommendations = []
        
        # Recommandations success rate
        if metrics.success_rate < 0.95:
            recommendations.append(
                f"Success rate ({metrics.success_rate:.1%}) below target. "
                f"Consider reviewing error handling and retry strategies."
            )
        
        # Recommandations latence
        if metrics.p95_latency > 500:
            recommendations.append(
                f"P95 latency ({metrics.p95_latency:.0f}ms) exceeds target. "
                f"Consider optimizing timeout strategies and parallel processing."
            )
        
        # Recommandations coût
        if metrics.cost_per_success > 5.0:
            recommendations.append(
                f"Cost per success (${metrics.cost_per_success:.2f}) is high. "
                f"Consider implementing more efficient retry patterns."
            )
        
        # Recommandations retries
        if metrics.average_retry_count > 2.0:
            recommendations.append(
                f"Average retry count ({metrics.average_retry_count:.1f}) is high. "
                f"Review failure patterns and consider circuit breaker implementation."
            )
        
        # Recommandations business impact
        if revenue_impact < 0:
            recommendations.append(
                "Negative revenue impact detected. Prioritize reliability improvements."
            )
        
        if ux_impact < 80:
            recommendations.append(
                "User experience impact below acceptable threshold. Focus on latency optimization."
            )
        
        return recommendations

class TrendAnalyzer:
    """Analyseur tendances retry performance"""
    
    def __init__(self):
        self.trend_window = 168  # 7 jours en heures
        
    async def analyze_trends(self, events: List[RetryEvent]) -> Dict[str, List[float]]:
        """Analyse tendances performance"""
        # Groupement par heure
        hourly_groups = self._group_by_hour(events)
        
        trends = {
            'success_rate_trend': [],
            'latency_trend': [],
            'cost_trend': [],
            'retry_frequency_trend': []
        }
        
        for hour_key in sorted(hourly_groups.keys()):
            hour_events = hourly_groups[hour_key]
            
            if hour_events:
                # Success rate
                success_rate = sum(1 for e in hour_events if e.success) / len(hour_events)
                trends['success_rate_trend'].append(success_rate)
                
                # Latence moyenne
                avg_latency = sum(e.execution_time for e in hour_events) / len(hour_events)
                trends['latency_trend'].append(avg_latency)
                
                # Coût total
                total_cost = sum(e.cost for e in hour_events)
                trends['cost_trend'].append(total_cost)
                
                # Fréquence retry
                avg_retries = sum(e.retry_count for e in hour_events) / len(hour_events)
                trends['retry_frequency_trend'].append(avg_retries)
            else:
                # Valeurs par défaut pour heures sans données
                trends['success_rate_trend'].append(0.0)
                trends['latency_trend'].append(0.0)
                trends['cost_trend'].append(0.0)
                trends['retry_frequency_trend'].append(0.0)
        
        return trends
    
    def _group_by_hour(self, events: List[RetryEvent]) -> Dict[str, List[RetryEvent]]:
        """Groupement événements par heure"""
        groups = defaultdict(list)
        
        for event in events:
            hour_key = event.timestamp.strftime('%Y-%m-%d_%H')
            groups[hour_key].append(event)
        
        return groups

class AnomalyDetector:
    """Détecteur anomalies dans retry patterns"""
    
    def __init__(self):
        self.anomaly_thresholds = {
            'success_rate_drop': 0.1,  # Chute >10%
            'latency_spike': 2.0,      # Spike >200%
            'cost_spike': 3.0,         # Spike >300%
            'retry_burst': 5.0         # Burst >500%
        }
    
    async def detect_anomalies(self, current_metrics: PerformanceMetrics, 
                             historical_baseline: PerformanceMetrics) -> List[Dict]:
        """Détection anomalies par rapport baseline historique"""
        anomalies = []
        
        # Anomalie success rate
        if (historical_baseline.success_rate - current_metrics.success_rate) > self.anomaly_thresholds['success_rate_drop']:
            anomalies.append({
                'type': 'success_rate_drop',
                'severity': 'high',
                'current_value': current_metrics.success_rate,
                'baseline_value': historical_baseline.success_rate,
                'description': f"Success rate dropped from {historical_baseline.success_rate:.1%} to {current_metrics.success_rate:.1%}"
            })
        
        # Anomalie latence
        if current_metrics.p95_latency > (historical_baseline.p95_latency * self.anomaly_thresholds['latency_spike']):
            anomalies.append({
                'type': 'latency_spike',
                'severity': 'medium',
                'current_value': current_metrics.p95_latency,
                'baseline_value': historical_baseline.p95_latency,
                'description': f"P95 latency spiked from {historical_baseline.p95_latency:.0f}ms to {current_metrics.p95_latency:.0f}ms"
            })
        
        # Anomalie coût
        if current_metrics.total_cost > (historical_baseline.total_cost * self.anomaly_thresholds['cost_spike']):
            anomalies.append({
                'type': 'cost_spike',
                'severity': 'high',
                'current_value': current_metrics.total_cost,
                'baseline_value': historical_baseline.total_cost,
                'description': f"Cost spiked from ${historical_baseline.total_cost:.2f} to ${current_metrics.total_cost:.2f}"
            })
        
        # Anomalie retry frequency
        if current_metrics.average_retry_count > (historical_baseline.average_retry_count * self.anomaly_thresholds['retry_burst']):
            anomalies.append({
                'type': 'retry_burst',
                'severity': 'medium',
                'current_value': current_metrics.average_retry_count,
                'baseline_value': historical_baseline.average_retry_count,
                'description': f"Retry frequency burst from {historical_baseline.average_retry_count:.1f} to {current_metrics.average_retry_count:.1f}"
            })
        
        return anomalies

class RetryAnalyticsEngine:
    """
    Moteur analytics retry avec insights business.
    Success rate analytics + cost optimization + performance insights.
    """
    
    def __init__(self, config: AnalyticsConfig = None):
        self.config = config or AnalyticsConfig(
            enabled_metrics=[AnalyticsMetric.SUCCESS_RATE, AnalyticsMetric.LATENCY_PERCENTILES, AnalyticsMetric.COST_PER_OPERATION],
            time_windows=[TimeWindow.HOURLY, TimeWindow.DAILY],
            business_impact_tracking=True
        )
        
        self.metrics_collector = MetricsCollector(self.config)
        self.performance_analyzer = PerformanceAnalyzer()
        self.business_analyzer = BusinessImpactAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cache analytics
        self.analytics_cache = {}
        self.baseline_metrics = {}
    
    async def analyze_retry_performance(self, analytics_config: AnalyticsConfig = None) -> RetryAnalytics:
        """
        Analyse performance retry pour optimization.
        
        Analytics Features:
        - Comprehensive performance metrics (success rate, latency, cost)
        - Business impact analysis (revenue, UX, operational cost)
        - Trend analysis pour pattern detection
        - Anomaly detection pour proactive alerts
        - Service-level breakdown pour targeted optimization
        - Cost optimization recommendations
        - Real-time monitoring capabilities
        """
        config = analytics_config or self.config
        analysis_id = str(uuid.uuid4())
        
        # Collection événements pour analyse
        events = list(self.metrics_collector.retry_events)
        
        if not events:
            self.logger.warning("No retry events available for analysis")
            return self._empty_analytics(analysis_id)
        
        # Analyse performance globale
        performance_metrics = await self.performance_analyzer.analyze_performance(
            events, TimeWindow.DAILY
        )
        
        # Analyse impact business
        business_insights = await self.business_analyzer.analyze_business_impact(
            performance_metrics, events
        )
        
        # Breakdown par service
        service_breakdown = await self._analyze_service_breakdown(events)
        
        # Analyse tendances
        trends = await self.trend_analyzer.analyze_trends(events)
        
        # Détection anomalies
        anomalies = []
        if self.baseline_metrics:
            anomalies = await self.anomaly_detector.detect_anomalies(
                performance_metrics, self.baseline_metrics.get('global', performance_metrics)
            )
        
        # Mise à jour baseline
        self.baseline_metrics['global'] = performance_metrics
        
        analytics_result = RetryAnalytics(
            analysis_id=analysis_id,
            time_window=TimeWindow.DAILY,
            performance_metrics=performance_metrics,
            business_insights=business_insights,
            service_breakdown=service_breakdown,
            trends=trends,
            anomalies=anomalies
        )
        
        # Cache résultat
        self.analytics_cache[analysis_id] = analytics_result
        
        self.logger.info(f"Analytics completed: {analysis_id}, Success rate: {performance_metrics.success_rate:.1%}")
        
        return analytics_result
    
    async def calculate_retry_roi(self, retry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcul ROI retry operations pour cost optimization.
        
        ROI Calculation Features:
        - Cost-benefit analysis des retry strategies
        - Revenue impact calculation
        - Operational cost savings
        - User experience value quantification
        - Reliability improvement value
        - Compliance cost avoidance
        """
        baseline_cost = retry_data.get('baseline_cost', 0.0)
        retry_investment = retry_data.get('retry_investment', 0.0)
        
        # Bénéfices quantifiés
        benefits = {
            'revenue_recovery': retry_data.get('revenue_recovery', 0.0),
            'cost_savings': retry_data.get('operational_savings', 0.0),
            'compliance_value': retry_data.get('compliance_value', 0.0),
            'brand_protection': retry_data.get('brand_protection_value', 0.0)
        }
        
        total_benefits = sum(benefits.values())
        
        # Calcul ROI
        roi_percentage = ((total_benefits - retry_investment) / retry_investment * 100) if retry_investment > 0 else 0.0
        
        # Payback period (mois)
        monthly_benefits = total_benefits / 12 if total_benefits > 0 else 0.0
        payback_months = retry_investment / monthly_benefits if monthly_benefits > 0 else float('inf')
        
        return {
            'roi_percentage': roi_percentage,
            'total_investment': retry_investment,
            'total_benefits': total_benefits,
            'net_benefit': total_benefits - retry_investment,
            'payback_period_months': min(payback_months, 999.9),
            'benefit_breakdown': benefits,
            'recommendation': self._generate_roi_recommendation(roi_percentage, payback_months)
        }
    
    async def _analyze_service_breakdown(self, events: List[RetryEvent]) -> Dict[str, PerformanceMetrics]:
        """Analyse breakdown par service"""
        service_groups = defaultdict(list)
        
        for event in events:
            service_groups[event.service_name].append(event)
        
        service_breakdown = {}
        for service_name, service_events in service_groups.items():
            service_breakdown[service_name] = await self.performance_analyzer.analyze_performance(
                service_events, TimeWindow.DAILY
            )
        
        return service_breakdown
    
    def _generate_roi_recommendation(self, roi_percentage: float, payback_months: float) -> str:
        """Génération recommandation ROI"""
        if roi_percentage > 200 and payback_months < 6:
            return "Excellent ROI - Continue and expand retry optimization investments"
        elif roi_percentage > 100 and payback_months < 12:
            return "Good ROI - Maintain current retry strategy with minor optimizations"
        elif roi_percentage > 50 and payback_months < 18:
            return "Moderate ROI - Consider targeted improvements in high-impact areas"
        elif roi_percentage > 0:
            return "Positive ROI but low - Review retry strategies for efficiency improvements"
        else:
            return "Negative ROI - Urgent review of retry strategies and cost structure needed"
    
    def _empty_analytics(self, analysis_id: str) -> RetryAnalytics:
        """Analytics vide pour cas sans données"""
        return RetryAnalytics(
            analysis_id=analysis_id,
            time_window=TimeWindow.DAILY,
            performance_metrics=PerformanceMetrics(
                success_rate=0.0, average_retry_count=0.0, p50_latency=0.0,
                p95_latency=0.0, p99_latency=0.0, total_operations=0,
                failed_operations=0, total_cost=0.0, cost_per_success=0.0,
                efficiency_score=0.0
            ),
            business_insights=BusinessInsights(
                revenue_impact=0.0, user_satisfaction_impact=0.0,
                operational_cost_savings=0.0, reliability_improvement=0.0,
                compliance_score=0.0, recommendations=["No data available for analysis"]
            ),
            service_breakdown={},
            trends={},
            anomalies=[]
        )
    
    async def register_retry_event(self, event: RetryEvent):
        """Enregistrement événement retry pour analytics"""
        await self.metrics_collector.collect_retry_event(event)
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Métriques temps réel"""
        recent_events = list(self.metrics_collector.real_time_buffer)
        
        if not recent_events:
            return {'status': 'no_data', 'message': 'No recent retry events'}
        
        # Métriques temps réel (dernières 5 minutes)
        now = datetime.now()
        recent_events = [
            e for e in recent_events 
            if (now - e.timestamp).total_seconds() <= 300
        ]
        
        if recent_events:
            success_rate = sum(1 for e in recent_events if e.success) / len(recent_events)
            avg_latency = sum(e.execution_time for e in recent_events) / len(recent_events)
            total_cost = sum(e.cost for e in recent_events)
            
            return {
                'status': 'active',
                'time_window': '5_minutes',
                'total_operations': len(recent_events),
                'success_rate': success_rate,
                'average_latency': avg_latency,
                'total_cost': total_cost,
                'timestamp': now.isoformat()
            }
        
        return {'status': 'no_recent_data', 'message': 'No events in last 5 minutes'}

# Instance globale
retry_analytics_engine = RetryAnalyticsEngine()

# Export des classes principales
__all__ = [
    'RetryAnalyticsEngine',
    'AnalyticsConfig',
    'RetryEvent',
    'RetryAnalytics',
    'PerformanceMetrics',
    'BusinessInsights',
    'retry_analytics_engine'
]