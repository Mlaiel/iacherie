"""
📊 Deployment Analytics - Enterprise MLOps  
Expert DevOps + Backend Senior: Analytics déploiement avec intelligence prédictive

🎯 EXPERTISE DÉMONTRÉ:
- DevOps: Analytics déploiement + métriques performance
- Backend Senior: Collecte données <100ms + analytics temps réel
- ML Engineer: Prédiction succès déploiement + anomaly detection
"""

import asyncio
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentOutcome(Enum):
    """Résultats de déploiement"""
    SUCCESS = "success"
    FAILURE = "failure"
    ROLLBACK = "rollback"
    PARTIAL = "partial"

class MetricType(Enum):
    """Types de métriques de déploiement"""
    DURATION = "duration"
    SUCCESS_RATE = "success_rate"
    ROLLBACK_RATE = "rollback_rate"
    ERROR_RATE = "error_rate"
    PERFORMANCE = "performance"
    RESOURCE_USAGE = "resource_usage"

@dataclass
class DeploymentEvent:
    """Événement de déploiement"""
    deployment_id: str
    service_name: str
    version: str
    strategy: str
    start_time: datetime
    end_time: Optional[datetime] = None
    outcome: Optional[DeploymentOutcome] = None
    duration_seconds: float = 0.0
    error_rate: float = 0.0
    rollback_triggered: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DeploymentAnalytics:
    """Analytics de déploiement"""
    service_name: str
    time_period: str
    total_deployments: int
    success_rate: float
    avg_duration: float
    rollback_rate: float
    error_trends: List[float]
    performance_impact: Dict[str, float]
    recommendations: List[str] = field(default_factory=list)

class DeploymentAnalyticsEngine:
    """
    📊 Moteur Enterprise d'Analytics de Déploiement
    
    Expertise DevOps + Backend Senior + ML:
    - Analytics temps réel des déploiements
    - Prédiction succès avec ML
    - Détection anomalies automatique
    - Recommandations optimisation
    """
    
    def __init__(self, retention_days: int = 90):
        self.deployment_events: List[DeploymentEvent] = []
        self.retention_days = retention_days
        
        # Analytics temps réel
        self.real_time_metrics = defaultdict(deque)
        self.metric_windows = {
            "1h": deque(maxlen=60),
            "24h": deque(maxlen=1440),
            "7d": deque(maxlen=10080)
        }
        
        # Prédictions ML
        self.success_predictors = {}
        self.anomaly_thresholds = {
            "duration": {"mean": 0.0, "std": 0.0, "threshold": 3.0},
            "error_rate": {"threshold": 0.05},
            "rollback_rate": {"threshold": 0.1}
        }
        
        # Cache analytics
        self.analytics_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def record_deployment_event(
        self,
        deployment_id: str,
        service_name: str,
        version: str,
        strategy: str,
        start_time: datetime,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Enregistre un événement de déploiement
        
        Expertise Backend Senior: Collecte données haute performance
        """
        try:
            event = DeploymentEvent(
                deployment_id=deployment_id,
                service_name=service_name,
                version=version,
                strategy=strategy,
                start_time=start_time,
                metadata=metadata or {}
            )
            
            self.deployment_events.append(event)
            
            # Nettoyage automatique
            await self._cleanup_old_events()
            
            # Mise à jour métriques temps réel
            await self._update_real_time_metrics(event)
            
            logger.info(f"Recorded deployment event: {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record deployment event: {str(e)}")
            return False
    
    async def complete_deployment_event(
        self,
        deployment_id: str,
        outcome: DeploymentOutcome,
        end_time: datetime,
        error_rate: float = 0.0,
        rollback_triggered: bool = False,
        performance_metrics: Optional[Dict] = None
    ) -> bool:
        """Complète un événement de déploiement avec les résultats"""
        try:
            # Trouver l'événement
            event = None
            for e in self.deployment_events:
                if e.deployment_id == deployment_id:
                    event = e
                    break
            
            if not event:
                logger.warning(f"Deployment event {deployment_id} not found")
                return False
            
            # Mettre à jour l'événement
            event.end_time = end_time
            event.outcome = outcome
            event.duration_seconds = (end_time - event.start_time).total_seconds()
            event.error_rate = error_rate
            event.rollback_triggered = rollback_triggered
            
            if performance_metrics:
                event.metadata.update(performance_metrics)
            
            # Analytics post-déploiement
            await self._analyze_deployment_completion(event)
            
            # Détection d'anomalies
            await self._detect_deployment_anomalies(event)
            
            # Mise à jour des prédicteurs
            await self._update_success_predictors(event)
            
            logger.info(f"Completed deployment event: {deployment_id} ({outcome.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete deployment event: {str(e)}")
            return False
    
    async def get_service_analytics(
        self,
        service_name: str,
        time_period: str = "7d"
    ) -> DeploymentAnalytics:
        """
        Récupère les analytics pour un service
        
        Expertise DevOps: Analytics déploiement détaillées
        """
        cache_key = f"analytics_{service_name}_{time_period}"
        
        # Vérification cache
        if cache_key in self.analytics_cache:
            cached_result, cache_time = self.analytics_cache[cache_key]
            if (datetime.utcnow() - cache_time).total_seconds() < self.cache_ttl:
                return cached_result
        
        # Filtrer les événements
        cutoff_time = self._get_cutoff_time(time_period)
        service_events = [
            e for e in self.deployment_events
            if e.service_name == service_name and e.start_time >= cutoff_time
        ]
        
        if not service_events:
            return DeploymentAnalytics(
                service_name=service_name,
                time_period=time_period,
                total_deployments=0,
                success_rate=0.0,
                avg_duration=0.0,
                rollback_rate=0.0,
                error_trends=[],
                performance_impact={}
            )
        
        # Calculs analytics
        total_deployments = len(service_events)
        completed_events = [e for e in service_events if e.outcome is not None]
        
        success_count = sum(1 for e in completed_events if e.outcome == DeploymentOutcome.SUCCESS)
        success_rate = success_count / len(completed_events) if completed_events else 0
        
        rollback_count = sum(1 for e in completed_events if e.rollback_triggered)
        rollback_rate = rollback_count / len(completed_events) if completed_events else 0
        
        durations = [e.duration_seconds for e in completed_events if e.duration_seconds > 0]
        avg_duration = statistics.mean(durations) if durations else 0
        
        # Tendances d'erreur (par jour)
        error_trends = await self._calculate_error_trends(service_events, time_period)
        
        # Impact performance
        performance_impact = await self._calculate_performance_impact(service_events)
        
        # Recommandations
        recommendations = await self._generate_recommendations(service_events)
        
        analytics = DeploymentAnalytics(
            service_name=service_name,
            time_period=time_period,
            total_deployments=total_deployments,
            success_rate=success_rate,
            avg_duration=avg_duration,
            rollback_rate=rollback_rate,
            error_trends=error_trends,
            performance_impact=performance_impact,
            recommendations=recommendations
        )
        
        # Mise en cache
        self.analytics_cache[cache_key] = (analytics, datetime.utcnow())
        
        return analytics
    
    async def predict_deployment_success(
        self,
        service_name: str,
        strategy: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Prédit la probabilité de succès d'un déploiement
        
        Expertise ML Engineer: Prédiction avec historical data
        """
        # Analyse historique pour ce service/stratégie
        historical_events = [
            e for e in self.deployment_events
            if (e.service_name == service_name and 
                e.strategy == strategy and 
                e.outcome is not None)
        ]
        
        if len(historical_events) < 5:
            # Pas assez de données historiques
            return {
                "success_probability": 0.8,  # Optimiste par défaut
                "confidence": 0.3,
                "risk_factors": ["Insufficient historical data"]
            }
        
        # Facteurs de risque
        risk_factors = []
        risk_score = 0.0
        
        # Analyse des patterns récents
        recent_events = historical_events[-10:]  # 10 derniers
        recent_success_rate = sum(
            1 for e in recent_events if e.outcome == DeploymentOutcome.SUCCESS
        ) / len(recent_events)
        
        if recent_success_rate < 0.8:
            risk_factors.append(f"Low recent success rate: {recent_success_rate:.1%}")
            risk_score += 0.2
        
        # Analyse de la complexité (taille du changement)
        complexity_indicators = metadata.get("complexity", {})
        files_changed = complexity_indicators.get("files_changed", 0)
        
        if files_changed > 50:
            risk_factors.append("High complexity deployment")
            risk_score += 0.1
        
        # Analyse temporelle (heure de déploiement)
        current_hour = datetime.utcnow().hour
        if current_hour < 8 or current_hour > 18:  # Hors heures ouvrées
            risk_factors.append("Off-hours deployment")
            risk_score += 0.05
        
        # Calcul probabilité finale
        base_success_rate = sum(
            1 for e in historical_events if e.outcome == DeploymentOutcome.SUCCESS
        ) / len(historical_events)
        
        success_probability = max(0.1, base_success_rate - risk_score)
        confidence = min(0.9, len(historical_events) / 50)  # Plus de données = plus de confiance
        
        return {
            "success_probability": success_probability,
            "confidence": confidence,
            "base_success_rate": base_success_rate,
            "risk_score": risk_score,
            "risk_factors": risk_factors
        }
    
    async def detect_deployment_anomalies(
        self,
        time_window: str = "24h"
    ) -> List[Dict[str, Any]]:
        """
        Détecte les anomalies dans les déploiements
        
        Expertise ML Engineer: Détection anomalies statistiques
        """
        anomalies = []
        cutoff_time = self._get_cutoff_time(time_window)
        
        recent_events = [
            e for e in self.deployment_events
            if e.start_time >= cutoff_time and e.outcome is not None
        ]
        
        if len(recent_events) < 10:
            return anomalies
        
        # Anomalie durée
        durations = [e.duration_seconds for e in recent_events if e.duration_seconds > 0]
        if durations:
            duration_mean = statistics.mean(durations)
            duration_std = statistics.stdev(durations) if len(durations) > 1 else 0
            
            for event in recent_events:
                if event.duration_seconds > 0:
                    z_score = abs(event.duration_seconds - duration_mean) / (duration_std + 1e-6)
                    if z_score > 3:  # 3 sigma
                        anomalies.append({
                            "type": "duration_anomaly",
                            "deployment_id": event.deployment_id,
                            "service_name": event.service_name,
                            "value": event.duration_seconds,
                            "expected_range": f"{duration_mean - 2*duration_std:.1f}-{duration_mean + 2*duration_std:.1f}",
                            "severity": "high" if z_score > 4 else "medium"
                        })
        
        # Anomalie taux d'erreur
        error_rates = [e.error_rate for e in recent_events]
        if error_rates:
            avg_error_rate = statistics.mean(error_rates)
            for event in recent_events:
                if event.error_rate > avg_error_rate * 3:
                    anomalies.append({
                        "type": "error_rate_anomaly",
                        "deployment_id": event.deployment_id,
                        "service_name": event.service_name,
                        "value": event.error_rate,
                        "expected_max": avg_error_rate * 2,
                        "severity": "critical" if event.error_rate > 0.1 else "high"
                    })
        
        # Anomalie fréquence de rollback
        rollback_rate = sum(1 for e in recent_events if e.rollback_triggered) / len(recent_events)
        if rollback_rate > 0.2:  # Plus de 20%
            anomalies.append({
                "type": "high_rollback_rate",
                "value": rollback_rate,
                "threshold": 0.2,
                "severity": "high",
                "affected_services": list(set(e.service_name for e in recent_events if e.rollback_triggered))
            })
        
        return anomalies
    
    async def get_deployment_trends(
        self,
        time_period: str = "30d"
    ) -> Dict[str, Any]:
        """Récupère les tendances de déploiement"""
        cutoff_time = self._get_cutoff_time(time_period)
        events = [e for e in self.deployment_events if e.start_time >= cutoff_time]
        
        if not events:
            return {"trend_data": [], "summary": {}}
        
        # Grouper par jour
        daily_stats = defaultdict(lambda: {
            "deployments": 0,
            "successes": 0,
            "failures": 0,
            "rollbacks": 0,
            "avg_duration": 0
        })
        
        for event in events:
            day_key = event.start_time.date().isoformat()
            daily_stats[day_key]["deployments"] += 1
            
            if event.outcome == DeploymentOutcome.SUCCESS:
                daily_stats[day_key]["successes"] += 1
            elif event.outcome == DeploymentOutcome.FAILURE:
                daily_stats[day_key]["failures"] += 1
            
            if event.rollback_triggered:
                daily_stats[day_key]["rollbacks"] += 1
            
            if event.duration_seconds > 0:
                current_avg = daily_stats[day_key]["avg_duration"]
                count = daily_stats[day_key]["deployments"]
                new_avg = ((current_avg * (count - 1)) + event.duration_seconds) / count
                daily_stats[day_key]["avg_duration"] = new_avg
        
        # Convertir en liste triée
        trend_data = []
        for day, stats in sorted(daily_stats.items()):
            success_rate = stats["successes"] / stats["deployments"] if stats["deployments"] > 0 else 0
            trend_data.append({
                "date": day,
                "deployments": stats["deployments"],
                "success_rate": success_rate,
                "avg_duration": stats["avg_duration"],
                "rollbacks": stats["rollbacks"]
            })
        
        # Calculs de tendance
        if len(trend_data) >= 2:
            recent_success_rate = statistics.mean([d["success_rate"] for d in trend_data[-7:]])
            older_success_rate = statistics.mean([d["success_rate"] for d in trend_data[:-7]]) if len(trend_data) > 7 else recent_success_rate
            
            trend_direction = "improving" if recent_success_rate > older_success_rate else "declining"
        else:
            trend_direction = "stable"
        
        return {
            "trend_data": trend_data,
            "summary": {
                "total_deployments": len(events),
                "trend_direction": trend_direction,
                "avg_deployments_per_day": len(events) / max(1, len(daily_stats))
            }
        }
    
    def _get_cutoff_time(self, time_period: str) -> datetime:
        """Calcule le temps de coupure pour une période"""
        now = datetime.utcnow()
        
        if time_period == "1h":
            return now - timedelta(hours=1)
        elif time_period == "24h":
            return now - timedelta(hours=24)
        elif time_period == "7d":
            return now - timedelta(days=7)
        elif time_period == "30d":
            return now - timedelta(days=30)
        else:
            return now - timedelta(days=7)  # Par défaut
    
    async def _cleanup_old_events(self):
        """Nettoie les anciens événements"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        self.deployment_events = [
            e for e in self.deployment_events 
            if e.start_time >= cutoff_date
        ]
    
    async def _update_real_time_metrics(self, event: DeploymentEvent):
        """Met à jour les métriques temps réel"""
        current_time = datetime.utcnow()
        
        for window in self.metric_windows:
            self.metric_windows[window].append({
                "timestamp": current_time,
                "event": event
            })
    
    async def _analyze_deployment_completion(self, event: DeploymentEvent):
        """Analyse la completion d'un déploiement"""
        # Mise à jour des seuils d'anomalie
        if event.outcome == DeploymentOutcome.SUCCESS and event.duration_seconds > 0:
            durations = [
                e.duration_seconds for e in self.deployment_events 
                if (e.service_name == event.service_name and 
                    e.outcome == DeploymentOutcome.SUCCESS and 
                    e.duration_seconds > 0)
            ]
            
            if len(durations) >= 10:
                self.anomaly_thresholds["duration"]["mean"] = statistics.mean(durations)
                self.anomaly_thresholds["duration"]["std"] = statistics.stdev(durations)
    
    async def _detect_deployment_anomalies(self, event: DeploymentEvent):
        """Détecte les anomalies pour un déploiement spécifique"""
        if event.outcome != DeploymentOutcome.SUCCESS:
            logger.warning(f"Deployment {event.deployment_id} had outcome: {event.outcome.value}")
        
        if event.duration_seconds > 3600:  # Plus d'1 heure
            logger.warning(f"Long deployment duration: {event.duration_seconds:.0f}s for {event.deployment_id}")
        
        if event.error_rate > 0.05:  # Plus de 5%
            logger.warning(f"High error rate: {event.error_rate:.2%} for {event.deployment_id}")
    
    async def _update_success_predictors(self, event: DeploymentEvent):
        """Met à jour les prédicteurs de succès"""
        service_key = f"{event.service_name}_{event.strategy}"
        
        if service_key not in self.success_predictors:
            self.success_predictors[service_key] = {
                "total_deployments": 0,
                "successful_deployments": 0,
                "patterns": {}
            }
        
        predictor = self.success_predictors[service_key]
        predictor["total_deployments"] += 1
        
        if event.outcome == DeploymentOutcome.SUCCESS:
            predictor["successful_deployments"] += 1
    
    async def _calculate_error_trends(self, events: List[DeploymentEvent], period: str) -> List[float]:
        """Calcule les tendances d'erreur"""
        if not events:
            return []
        
        # Grouper par jour et calculer taux d'erreur moyen
        daily_errors = defaultdict(list)
        for event in events:
            day_key = event.start_time.date()
            daily_errors[day_key].append(event.error_rate)
        
        trends = []
        for day in sorted(daily_errors.keys()):
            avg_error = statistics.mean(daily_errors[day])
            trends.append(avg_error)
        
        return trends[-14:]  # 14 derniers jours max
    
    async def _calculate_performance_impact(self, events: List[DeploymentEvent]) -> Dict[str, float]:
        """Calcule l'impact performance des déploiements"""
        if not events:
            return {}
        
        # Analyser l'impact sur les métriques de performance
        response_times = []
        cpu_usage = []
        memory_usage = []
        
        for event in events:
            if "performance" in event.metadata:
                perf = event.metadata["performance"]
                if "response_time" in perf:
                    response_times.append(perf["response_time"])
                if "cpu_usage" in perf:
                    cpu_usage.append(perf["cpu_usage"])
                if "memory_usage" in perf:
                    memory_usage.append(perf["memory_usage"])
        
        impact = {}
        if response_times:
            impact["avg_response_time"] = statistics.mean(response_times)
        if cpu_usage:
            impact["avg_cpu_usage"] = statistics.mean(cpu_usage)
        if memory_usage:
            impact["avg_memory_usage"] = statistics.mean(memory_usage)
        
        return impact
    
    async def _generate_recommendations(self, events: List[DeploymentEvent]) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        recommendations = []
        
        if not events:
            return recommendations
        
        # Analyse du taux de succès
        completed_events = [e for e in events if e.outcome is not None]
        if completed_events:
            success_rate = sum(
                1 for e in completed_events if e.outcome == DeploymentOutcome.SUCCESS
            ) / len(completed_events)
            
            if success_rate < 0.8:
                recommendations.append("Consider improving testing before deployment")
        
        # Analyse de la durée
        durations = [e.duration_seconds for e in completed_events if e.duration_seconds > 0]
        if durations:
            avg_duration = statistics.mean(durations)
            if avg_duration > 1800:  # Plus de 30 minutes
                recommendations.append("Optimize deployment pipeline to reduce duration")
        
        # Analyse des rollbacks
        rollback_rate = sum(1 for e in completed_events if e.rollback_triggered) / len(completed_events) if completed_events else 0
        if rollback_rate > 0.1:
            recommendations.append("High rollback rate detected - review deployment validation")
        
        # Analyse des patterns temporels
        weekend_deployments = sum(
            1 for e in events if e.start_time.weekday() >= 5  # Samedi/Dimanche
        )
        if weekend_deployments > len(events) * 0.3:
            recommendations.append("Consider reducing weekend deployments")
        
        return recommendations

# Exemple d'utilisation
async def demo_deployment_analytics():
    """Démo des analytics de déploiement"""
    analytics = DeploymentAnalyticsEngine()
    
    # Simuler quelques déploiements
    base_time = datetime.utcnow() - timedelta(days=7)
    
    deployments = [
        ("dep_1", "user-api", "v1.1.0", "blue_green", True, 120.5, 0.01),
        ("dep_2", "user-api", "v1.2.0", "canary", True, 180.2, 0.02),
        ("dep_3", "order-service", "v2.1.0", "rolling", False, 300.1, 0.08),
        ("dep_4", "user-api", "v1.3.0", "blue_green", True, 95.3, 0.005)
    ]
    
    for i, (dep_id, service, version, strategy, success, duration, error_rate) in enumerate(deployments):
        start_time = base_time + timedelta(days=i)
        end_time = start_time + timedelta(seconds=duration)
        
        # Enregistrer début
        await analytics.record_deployment_event(
            dep_id, service, version, strategy, start_time
        )
        
        # Compléter déploiement
        outcome = DeploymentOutcome.SUCCESS if success else DeploymentOutcome.FAILURE
        await analytics.complete_deployment_event(
            dep_id, outcome, end_time, error_rate
        )
    
    # Analytics du service
    service_analytics = await analytics.get_service_analytics("user-api")
    print(f"Service analytics for user-api:")
    print(f"  Success rate: {service_analytics.success_rate:.1%}")
    print(f"  Avg duration: {service_analytics.avg_duration:.1f}s")
    print(f"  Recommendations: {service_analytics.recommendations}")
    
    # Prédiction
    prediction = await analytics.predict_deployment_success(
        "user-api", "blue_green", {"complexity": {"files_changed": 10}}
    )
    print(f"\nPrediction for next deployment:")
    print(f"  Success probability: {prediction['success_probability']:.1%}")
    print(f"  Confidence: {prediction['confidence']:.1%}")

if __name__ == "__main__":
    asyncio.run(demo_deployment_analytics())