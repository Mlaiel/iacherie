"""🚀 Model Performance Tracker - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/model_registry/model_performance_tracker.py
Author: Fahed Mlaiel (mlaiel@live.de) - DBA Expert
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SUIVI DE PERFORMANCE DE MODÈLES À LONG TERME
Suivi et analyse de performance avec détection de dégradation
- Long-term performance tracking et trending
- Model degradation detection avec alertes
- Creator-specific performance metrics
- Business impact correlation tracking
"""

import asyncio
import logging
import time
import uuid
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Configuration
logger = logging.getLogger(__name__)

class PerformanceStatus(Enum):
    """Status de performance du modèle"""
    HEALTHY = "healthy"
    DEGRADING = "degrading"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class MetricType(Enum):
    """Types de métriques de performance"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    ENGAGEMENT_RATE = "engagement_rate"
    CREATOR_SATISFACTION = "creator_satisfaction"
    BUSINESS_IMPACT = "business_impact"

class CreatorType(Enum):
    """Types de créateurs pour métriques spécialisées"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

@dataclass
class PerformanceMetric:
    """Métrique de performance individuelle"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    creator_type: Optional[CreatorType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_interval: Optional[Tuple[float, float]] = None

@dataclass
class ModelPerformanceSnapshot:
    """Snapshot de performance d'un modèle"""
    model_id: str
    model_version: str
    timestamp: datetime
    metrics: Dict[MetricType, PerformanceMetric]
    environment: str = "production"
    data_window: timedelta = timedelta(hours=24)
    sample_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceTrend:
    """Tendance de performance"""
    metric_type: MetricType
    trend_direction: str  # "improving", "stable", "degrading"
    trend_magnitude: float
    confidence: float
    time_period: timedelta
    data_points: int
    statistical_significance: bool = False

@dataclass
class DegradationAlert:
    """Alerte de dégradation de performance"""
    alert_id: str
    model_id: str
    metric_type: MetricType
    current_value: float
    baseline_value: float
    degradation_percentage: float
    severity: str  # "low", "medium", "high", "critical"
    timestamp: datetime
    creator_impact: Dict[CreatorType, float] = field(default_factory=dict)
    recommended_actions: List[str] = field(default_factory=list)

@dataclass
class TrackerConfig:
    """Configuration du tracker de performance"""
    model_id: str
    baseline_window: timedelta = timedelta(days=7)
    monitoring_window: timedelta = timedelta(hours=1)
    degradation_threshold: float = 0.05  # 5% de dégradation
    critical_threshold: float = 0.15  # 15% de dégradation critique
    min_samples: int = 100
    confidence_level: float = 0.95
    enable_creator_specific_tracking: bool = True
    business_metrics_correlation: bool = True

class ModelPerformanceTracker:
    """🗄️ Tracker de performance de modèles ML"""
    
    def __init__(self, config -> None: TrackerConfig) -> None:
        self.config = config
        self.tracker_id = str(uuid.uuid4())
        self.performance_history: List[ModelPerformanceSnapshot] = []
        self.trends: Dict[MetricType, PerformanceTrend] = {}
        self.alerts: List[DegradationAlert] = []
        self.baseline_metrics: Dict[MetricType, float] = {}
        self.creator_baselines: Dict[CreatorType, Dict[MetricType, float]] = {}
        
        logger.info(f"Model Performance Tracker initialized: {self.tracker_id}")
    
    async def record_performance_snapshot(self, snapshot -> None: ModelPerformanceSnapshot) -> None:
        """Enregistre un snapshot de performance"""
        try:
            self.performance_history.append(snapshot)
            
            # Maintenir l'historique dans une fenêtre glissante
            cutoff_time = datetime.now() - timedelta(days=30)
            self.performance_history = [
                s for s in self.performance_history 
                if s.timestamp > cutoff_time
            ]
            
            # Mettre à jour les baselines si nécessaire
            await self._update_baselines()
            
            # Analyser les tendances
            await self._analyze_trends()
            
            # Détecter les dégradations
            await self._detect_degradation(snapshot)
            
            logger.info(f"Performance snapshot recorded for model {snapshot.model_id}")
            
        except Exception as e:
            logger.error(f"Error recording performance snapshot: {e}")
            raise
    
    async def _update_baselines(self) -> None:
        """Met à jour les métriques de baseline"""
        try:
            if len(self.performance_history) < 2:
                return
            
            # Calculer les baselines sur la fenêtre de baseline
            baseline_cutoff = datetime.now() - self.config.baseline_window
            baseline_snapshots = [
                s for s in self.performance_history 
                if s.timestamp > baseline_cutoff
            ]
            
            if not baseline_snapshots:
                return
            
            # Baseline globale
            for metric_type in MetricType:
                values = []
                for snapshot in baseline_snapshots:
                    if metric_type in snapshot.metrics:
                        values.append(snapshot.metrics[metric_type].value)
                
                if values:
                    self.baseline_metrics[metric_type] = statistics.mean(values)
            
            # Baselines par type de créateur
            if self.config.enable_creator_specific_tracking:
                for creator_type in CreatorType:
                    creator_values = {}
                    for snapshot in baseline_snapshots:
                        for metric_type, metric in snapshot.metrics.items():
                            if metric.creator_type == creator_type:
                                if metric_type not in creator_values:
                                    creator_values[metric_type] = []
                                creator_values[metric_type].append(metric.value)
                    
                    if creator_values:
                        if creator_type not in self.creator_baselines:
                            self.creator_baselines[creator_type] = {}
                        
                        for metric_type, values in creator_values.items():
                            if values:
                                self.creator_baselines[creator_type][metric_type] = statistics.mean(values)
            
        except Exception as e:
            logger.error(f"Error updating baselines: {e}")
    
    async def _analyze_trends(self) -> None:
        """Analyse les tendances de performance"""
        try:
            if len(self.performance_history) < 10:
                return
            
            # Analyser chaque type de métrique
            for metric_type in MetricType:
                await self._analyze_metric_trend(metric_type)
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
    
    async def _analyze_metric_trend(self, metric_type -> None: MetricType) -> None:
        """Analyse la tendance d'une métrique spécifique"""
        try:
            # Extraire les valeurs et timestamps
            data_points = []
            for snapshot in self.performance_history[-20:]:  # 20 derniers points
                if metric_type in snapshot.metrics:
                    data_points.append({
                        'timestamp': snapshot.timestamp,
                        'value': snapshot.metrics[metric_type].value
                    })
            
            if len(data_points) < 5:
                return
            
            # Calculer la tendance avec régression linéaire simple
            timestamps = [(dp['timestamp'] - data_points[0]['timestamp']).total_seconds() 
                         for dp in data_points]
            values = [dp['value'] for dp in data_points]
            
            # Régression linéaire
            n = len(timestamps)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(t * v for t, v in zip(timestamps, values))
            sum_x2 = sum(t * t for t in timestamps)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Déterminer la direction de la tendance
            if abs(slope) < 1e-6:
                direction = "stable"
            elif slope > 0:
                direction = "improving" if metric_type in [MetricType.ACCURACY, MetricType.PRECISION, 
                                                         MetricType.RECALL, MetricType.F1_SCORE] else "degrading"
            else:
                direction = "degrading" if metric_type in [MetricType.ACCURACY, MetricType.PRECISION, 
                                                          MetricType.RECALL, MetricType.F1_SCORE] else "improving"
            
            # Calculer la confiance basée sur R²
            y_mean = statistics.mean(values)
            ss_tot = sum((v - y_mean) ** 2 for v in values)
            predicted_values = [slope * t + (sum_y - slope * sum_x) / n for t in timestamps]
            ss_res = sum((v - p) ** 2 for v, p in zip(values, predicted_values))
            
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            confidence = max(0, min(1, r_squared))
            
            # Créer la tendance
            trend = PerformanceTrend(
                metric_type=metric_type,
                trend_direction=direction,
                trend_magnitude=abs(slope),
                confidence=confidence,
                time_period=data_points[-1]['timestamp'] - data_points[0]['timestamp'],
                data_points=len(data_points),
                statistical_significance=confidence > 0.7
            )
            
            self.trends[metric_type] = trend
            
        except Exception as e:
            logger.error(f"Error analyzing trend for {metric_type}: {e}")
    
    async def _detect_degradation(self, snapshot -> None: ModelPerformanceSnapshot) -> None:
        """Détecte la dégradation de performance"""
        try:
            for metric_type, metric in snapshot.metrics.items():
                await self._check_metric_degradation(metric_type, metric, snapshot)
                
        except Exception as e:
            logger.error(f"Error detecting degradation: {e}")
    
    async def _check_metric_degradation(self, metric_type -> None: MetricType, 
                                       metric -> None: PerformanceMetric, 
                                       snapshot -> None: ModelPerformanceSnapshot) -> None:
        """Vérifie la dégradation d'une métrique spécifique"""
        try:
            # Obtenir la baseline appropriée
            baseline_value = None
            
            if metric.creator_type and metric.creator_type in self.creator_baselines:
                baseline_value = self.creator_baselines[metric.creator_type].get(metric_type)
            
            if baseline_value is None:
                baseline_value = self.baseline_metrics.get(metric_type)
            
            if baseline_value is None:
                return
            
            # Calculer la dégradation
            if metric_type in [MetricType.ACCURACY, MetricType.PRECISION, MetricType.RECALL, 
                              MetricType.F1_SCORE, MetricType.AUC_ROC]:
                # Pour ces métriques, une diminution est une dégradation
                degradation = (baseline_value - metric.value) / baseline_value
            else:
                # Pour les métriques comme latency, error_rate, une augmentation est une dégradation
                degradation = (metric.value - baseline_value) / baseline_value
            
            # Vérifier si dégradation significative
            if degradation > self.config.degradation_threshold:
                severity = self._calculate_severity(degradation)
                
                alert = DegradationAlert(
                    alert_id=str(uuid.uuid4()),
                    model_id=self.config.model_id,
                    metric_type=metric_type,
                    current_value=metric.value,
                    baseline_value=baseline_value,
                    degradation_percentage=degradation * 100,
                    severity=severity,
                    timestamp=datetime.now(),
                    recommended_actions=self._get_recommended_actions(metric_type, degradation)
                )
                
                # Calculer l'impact par créateur si applicable
                if self.config.enable_creator_specific_tracking:
                    alert.creator_impact = await self._calculate_creator_impact(metric_type)
                
                self.alerts.append(alert)
                
                logger.warning(f"Performance degradation detected: {metric_type.value} "
                             f"degraded by {degradation*100:.2f}% (severity: {severity})")
                
        except Exception as e:
            logger.error(f"Error checking metric degradation: {e}")
    
    def _calculate_severity(self, degradation: float) -> str:
        """Calcule la sévérité de la dégradation"""
        if degradation >= self.config.critical_threshold:
            return "critical"
        elif degradation >= self.config.degradation_threshold * 2:
            return "high"
        elif degradation >= self.config.degradation_threshold * 1.5:
            return "medium"
        else:
            return "low"
    
    def _get_recommended_actions(self, metric_type: MetricType, degradation: float) -> List[str]:
        """Génère des actions recommandées basées sur la dégradation"""
        actions = []
        
        if degradation >= self.config.critical_threshold:
            actions.append("Immediate model rollback to previous version")
            actions.append("Emergency investigation of data pipeline")
        
        if metric_type in [MetricType.ACCURACY, MetricType.F1_SCORE]:
            actions.extend([
                "Check for data drift in input features",
                "Validate training data quality",
                "Consider model retraining with recent data"
            ])
        elif metric_type == MetricType.LATENCY:
            actions.extend([
                "Check system resource utilization",
                "Review model optimization settings",
                "Consider scaling inference infrastructure"
            ])
        elif metric_type == MetricType.ERROR_RATE:
            actions.extend([
                "Investigate recent code deployments",
                "Check system dependencies and health",
                "Review error logs for patterns"
            ])
        
        return actions
    
    async def _calculate_creator_impact(self, metric_type: MetricType) -> Dict[CreatorType, float]:
        """Calcule l'impact par type de créateur"""
        impact = {}
        
        for creator_type in CreatorType:
            # Calculer l'impact basé sur l'utilisation récente
            recent_snapshots = self.performance_history[-10:]
            creator_metrics = []
            
            for snapshot in recent_snapshots:
                if metric_type in snapshot.metrics:
                    metric = snapshot.metrics[metric_type]
                    if metric.creator_type == creator_type:
                        creator_metrics.append(metric.value)
            
            if creator_metrics and creator_type in self.creator_baselines:
                baseline = self.creator_baselines[creator_type].get(metric_type)
                if baseline:
                    current_avg = statistics.mean(creator_metrics)
                    if metric_type in [MetricType.ACCURACY, MetricType.PRECISION, MetricType.RECALL]:
                        impact[creator_type] = (baseline - current_avg) / baseline
                    else:
                        impact[creator_type] = (current_avg - baseline) / baseline
        
        return impact
    
    async def get_performance_status(self) -> PerformanceStatus:
        """Obtient le statut global de performance"""
        try:
            if not self.alerts:
                return PerformanceStatus.HEALTHY
            
            # Vérifier les alertes critiques récentes
            recent_cutoff = datetime.now() - timedelta(hours=1)
            recent_alerts = [a for a in self.alerts if a.timestamp > recent_cutoff]
            
            if any(alert.severity == "critical" for alert in recent_alerts):
                return PerformanceStatus.CRITICAL
            elif any(alert.severity in ["high", "medium"] for alert in recent_alerts):
                return PerformanceStatus.DEGRADING
            else:
                return PerformanceStatus.HEALTHY
                
        except Exception as e:
            logger.error(f"Error getting performance status: {e}")
            return PerformanceStatus.UNKNOWN
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Génère un résumé de performance complet"""
        try:
            status = await self.get_performance_status()
            
            # Métriques actuelles
            current_metrics = {}
            if self.performance_history:
                latest_snapshot = self.performance_history[-1]
                current_metrics = {
                    metric_type.value: metric.value 
                    for metric_type, metric in latest_snapshot.metrics.items()
                }
            
            # Alertes récentes
            recent_alerts = [
                {
                    'metric_type': alert.metric_type.value,
                    'severity': alert.severity,
                    'degradation_percentage': alert.degradation_percentage,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in self.alerts[-10:]
            ]
            
            # Tendances
            trends_summary = {
                metric_type.value: {
                    'direction': trend.trend_direction,
                    'confidence': trend.confidence,
                    'significant': trend.statistical_significance
                }
                for metric_type, trend in self.trends.items()
            }
            
            return {
                'tracker_id': self.tracker_id,
                'model_id': self.config.model_id,
                'status': status.value,
                'current_metrics': current_metrics,
                'baseline_metrics': {k.value: v for k, v in self.baseline_metrics.items()},
                'trends': trends_summary,
                'recent_alerts': recent_alerts,
                'total_snapshots': len(self.performance_history),
                'tracking_period': {
                    'start': self.performance_history[0].timestamp.isoformat() if self.performance_history else None,
                    'end': self.performance_history[-1].timestamp.isoformat() if self.performance_history else None
                },
                'creator_tracking_enabled': self.config.enable_creator_specific_tracking,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return {}
    
    async def get_creator_performance_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Génère une analyse de performance par type de créateur"""
        try:
            breakdown = {}
            
            for creator_type in CreatorType:
                creator_metrics = {}
                creator_trends = {}
                
                # Métriques actuelles par créateur
                if self.performance_history:
                    latest_snapshot = self.performance_history[-1]
                    for metric_type, metric in latest_snapshot.metrics.items():
                        if metric.creator_type == creator_type:
                            creator_metrics[metric_type.value] = metric.value
                
                # Tendances par créateur
                for metric_type, trend in self.trends.items():
                    creator_snapshots = [
                        s for s in self.performance_history[-10:]
                        if metric_type in s.metrics and s.metrics[metric_type].creator_type == creator_type
                    ]
                    if creator_snapshots:
                        creator_trends[metric_type.value] = trend.trend_direction
                
                if creator_metrics or creator_trends:
                    breakdown[creator_type.value] = {
                        'current_metrics': creator_metrics,
                        'trends': creator_trends,
                        'baseline_metrics': self.creator_baselines.get(creator_type, {})
                    }
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error generating creator performance breakdown: {e}")
            return {}

# Factory functions
def create_model_performance_tracker(
    model_id: str,
    baseline_window_hours: int = 168,  # 7 days
    degradation_threshold: float = 0.05
) -> ModelPerformanceTracker:
    """Factory pour créer un tracker de performance"""
    config = TrackerConfig(
        model_id=model_id,
        baseline_window=timedelta(hours=baseline_window_hours),
        degradation_threshold=degradation_threshold
    )
    return ModelPerformanceTracker(config)

async def demo_performance_tracker() -> None:
    """Démo du tracker de performance"""
    tracker = create_model_performance_tracker("musician-classifier-v1")
    
    print("📊 Model Performance Tracker Demo")
    
    # Simuler des snapshots de performance
    for i in range(10):
        metrics = {
            MetricType.ACCURACY: PerformanceMetric(
                metric_type=MetricType.ACCURACY,
                value=0.95 - (i * 0.01),  # Dégradation simulée
                timestamp=datetime.now() - timedelta(hours=10-i),
                creator_type=CreatorType.MUSICIAN
            ),
            MetricType.LATENCY: PerformanceMetric(
                metric_type=MetricType.LATENCY,
                value=50 + (i * 5),  # Augmentation de latence
                timestamp=datetime.now() - timedelta(hours=10-i)
            )
        }
        
        snapshot = ModelPerformanceSnapshot(
            model_id="musician-classifier-v1",
            model_version="1.0",
            timestamp=datetime.now() - timedelta(hours=10-i),
            metrics=metrics,
            sample_size=1000
        )
        
        await tracker.record_performance_snapshot(snapshot)
    
    # Statut et résumé
    status = await tracker.get_performance_status()
    summary = await tracker.get_performance_summary()
    
    print(f"\n📈 Performance Status: {status.value}")
    print(f"Current Accuracy: {summary['current_metrics'].get('accuracy', 'N/A')}")
    print(f"Active Alerts: {len(summary['recent_alerts'])}")
    
    if summary['recent_alerts']:
        print("\n🚨 Recent Alerts:")
        for alert in summary['recent_alerts'][-3:]:
            print(f"  - {alert['metric_type']}: {alert['degradation_percentage']:.2f}% degradation ({alert['severity']})")

if __name__ == "__main__":
    # Configurer le logging
    logging.basicConfig(level=logging.INFO)
    
    # Lancer la démo
    asyncio.run(demo_performance_tracker())