"""🚀 Model Performance Monitor - IA Influencer Agent Platform Enterprise
=====================================================================
Module: backend/ml/monitoring/performance_monitor.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MONITORING DES PERFORMANCES DE MODÈLES
Surveillance en temps réel des modèles ML en production
- Data drift detection et model drift monitoring
- Performance degradation alerts
- A/B testing metrics comparison
- Real-time dashboards et reporting
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import statistics
from collections import defaultdict, deque

# Configuration
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """
Niveaux de sévérité des alertes"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types de métriques"""

    PERFORMANCE = "performance"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    DATA_DRIFT = "data_drift"
    MODEL_DRIFT = "model_drift"
    RESOURCE_USAGE = "resource_usage"

class DriftType(Enum):
    """Types de drift"""

    FEATURE_DRIFT = "feature_drift"
    LABEL_DRIFT = "label_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"

@dataclass
class MetricPoint:
    """Point de métrique"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """
Alerte de monitoring"""
    alert_id: str
    model_id: str
    metric_type: MetricType
    severity: AlertSeverity
    message: str
    threshold_value: float
    actual_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class DriftAnalysis:
    """
Analyse de drift"""
    drift_type: DriftType
    drift_score: float
    p_value: float
    threshold: float
    is_drifting: bool
    detected_at: datetime
    features_affected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class PerformanceReport:
    """
Rapport de performance"""
    model_id: str
    period_start: datetime
    period_end: datetime
    total_predictions: int
    avg_latency: float
    p95_latency: float
    p99_latency: float
    error_rate: float
    throughput: float
    accuracy: Optional[float] = None
    drift_analysis: List[DriftAnalysis] = field(default_factory=list)
    alerts: List[Alert] = field(default_factory=list)

class ModelPerformanceMonitor:
    """
Moniteur de performance des modèles"""
    
    def __init__(self, 
                 buffer_size: int = 10000,
                 drift_detection_window: int = 1000,
                 alert_cooldown_minutes: int = 30):
        self.buffer_size = buffer_size
        self.drift_detection_window = drift_detection_window
        self.alert_cooldown_minutes = alert_cooldown_minutes
        
        # Stockage des métriques
        self.metrics: Dict[str, Dict[MetricType, deque]] = defaultdict(lambda: defaultdict(lambda: deque(maxlen=buffer_size)))
        self.predictions: Dict[str, deque] = defaultdict(lambda: deque(maxlen=buffer_size))
        self.features: Dict[str, deque] = defaultdict(lambda: deque(maxlen=buffer_size))
        self.labels: Dict[str, deque] = defaultdict(lambda: deque(maxlen=buffer_size))
        
        # Alertes et thresholds
        self.alerts: Dict[str, List[Alert]] = defaultdict(list)
        self.thresholds: Dict[str, Dict[MetricType, Dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
        self.last_alert_time: Dict[str, datetime] = {}
        
        # Configuration par défaut des thresholds
        self._setup_default_thresholds()
        
        # Modèles de référence pour drift detection
        self.reference_distributions: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Callbacks pour les alertes
        self.alert_callbacks: List[Callable[[Alert], None]] = []
    
    def _setup_default_thresholds(self):
        """
Configure les thresholds par défaut"""
        default_thresholds = {
            MetricType.LATENCY: {"warning": 0.5, "critical": 1.0},
            MetricType.ERROR_RATE: {"warning": 0.05, "critical": 0.10},
            MetricType.THROUGHPUT: {"warning": 50, "critical": 20},
            MetricType.DATA_DRIFT: {"warning": 0.05, "critical": 0.01},
            MetricType.MODEL_DRIFT: {"warning": 0.1, "critical": 0.2}
        }
        
        # Appliquer à tous les modèles par défaut
        self.default_thresholds = default_thresholds
    
    def set_thresholds(self, model_id: str, thresholds: Dict[MetricType, Dict[str, float]]):
        """Configure les thresholds pour un modèle"""
        self.thresholds[model_id] = thresholds
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """
Ajoute un callback pour les alertes"""
        self.alert_callbacks.append(callback)
    
    async def record_prediction(self, 
                               model_id: str,
                               features: np.ndarray,
                               prediction: Any,
                               latency: float,
                               actual_label: Optional[Any] = None,
                               metadata: Optional[Dict[str, Any]] = None):
        """
Enregistre une prédiction et ses métriques"""
        
        timestamp = datetime.now()
        
        try:
            # Stocker les données
            self.predictions[model_id].append({
                "timestamp": timestamp,
                "prediction": prediction,
                "features": features,
                "actual_label": actual_label,
                "metadata": metadata or {}
            })
            
            if features is not None:
                self.features[model_id].append(features)
            
            if actual_label is not None:
                self.labels[model_id].append(actual_label)
            
            # Enregistrer les métriques
            await self._record_metric(model_id, MetricType.LATENCY, latency, timestamp)
            
            # Analyser en temps réel si on a assez de données
            if len(self.predictions[model_id]) % 100 == 0:  # Analyse tous les 100 prédictions
                await self._analyze_performance(model_id)
            
        except Exception as e:
            logger.error(f"Erreur enregistrement prédiction pour {model_id}: {e}")
    
    async def _record_metric(self, 
                            model_id: str, 
                            metric_type: MetricType, 
                            value: float, 
                            timestamp: datetime):
        """Enregistre une métrique"""
        
        metric_point = MetricPoint(timestamp=timestamp, value=value)
        self.metrics[model_id][metric_type].append(metric_point)
        
        # Vérifier les thresholds
        await self._check_thresholds(model_id, metric_type, value, timestamp)
    
    async def _check_thresholds(self, 
                               model_id: str, 
                               metric_type: MetricType, 
                               value: float, 
                               timestamp: datetime):
        """
Vérifie les thresholds et génère des alertes"""
        
        try:
            # Récupérer les thresholds pour ce modèle
            model_thresholds = self.thresholds.get(model_id, self.default_thresholds)
            metric_thresholds = model_thresholds.get(metric_type, {})
            
            if not metric_thresholds:
                return
            
            # Vérifier le cooldown des alertes
            cooldown_key = f"{model_id}_{metric_type.value}"
            if cooldown_key in self.last_alert_time:
                time_since_last_alert = timestamp - self.last_alert_time[cooldown_key]
                if time_since_last_alert.total_seconds() < self.alert_cooldown_minutes * 60:
                    return
            
            # Déterminer la sévérité
            severity = None
            threshold_value = None
            
            if "critical" in metric_thresholds:
                critical_threshold = metric_thresholds["critical"]
                if (metric_type in [MetricType.LATENCY, MetricType.ERROR_RATE] and value > critical_threshold) or \
                   (metric_type == MetricType.THROUGHPUT and value < critical_threshold) or \
                   (metric_type in [MetricType.DATA_DRIFT, MetricType.MODEL_DRIFT] and value < critical_threshold):
                    severity = AlertSeverity.CRITICAL
                    threshold_value = critical_threshold
            
            if severity is None and "warning" in metric_thresholds:
                warning_threshold = metric_thresholds["warning"]
                if (metric_type in [MetricType.LATENCY, MetricType.ERROR_RATE] and value > warning_threshold) or \
                   (metric_type == MetricType.THROUGHPUT and value < warning_threshold) or \
                   (metric_type in [MetricType.DATA_DRIFT, MetricType.MODEL_DRIFT] and value < warning_threshold):
                    severity = AlertSeverity.MEDIUM
                    threshold_value = warning_threshold
            
            # Créer l'alerte si nécessaire
            if severity:
                alert = Alert(
                    alert_id=str(uuid.uuid4()),
                    model_id=model_id,
                    metric_type=metric_type,
                    severity=severity,
                    message=f"{metric_type.value} threshold exceeded: {value:.4f} > {threshold_value:.4f}",
                    threshold_value=threshold_value,
                    actual_value=value,
                    timestamp=timestamp
                )
                
                self.alerts[model_id].append(alert)
                self.last_alert_time[cooldown_key] = timestamp
                
                # Déclencher les callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        logger.error(f"Erreur callback alerte: {e}")
                
                logger.warning(f"Alerte générée: {alert.message}")
        
        except Exception as e:
            logger.error(f"Erreur vérification thresholds: {e}")
    
    async def _analyze_performance(self, model_id: str):
        """Analyse la performance globale d'un modèle"""
        
        try:
            predictions = list(self.predictions[model_id])
            if len(predictions) < 10:
                return
            
            # Calculer les métriques de performance
            latencies = [p.get("latency", 0) for p in predictions[-100:]]  # Dernières 100 prédictions
            
            if latencies:
                avg_latency = statistics.mean(latencies)
                p95_latency = np.percentile(latencies, 95)
                
                await self._record_metric(model_id, MetricType.PERFORMANCE, avg_latency, datetime.now())
            
            # Analyser le drift si on a assez de données
            if len(predictions) >= self.drift_detection_window:
                await self._detect_drift(model_id)
            
        except Exception as e:
            logger.error(f"Erreur analyse performance pour {model_id}: {e}")
    
    async def _detect_drift(self, model_id: str):
        """Détecte le drift des données et du modèle"""
        
        try:
            # Récupérer les données récentes
            recent_features = list(self.features[model_id])[-self.drift_detection_window:]
            recent_predictions = list(self.predictions[model_id])[-self.drift_detection_window:]
            
            if len(recent_features) < self.drift_detection_window:
                return
            
            # Drift detection simple basé sur la distribution
            drift_analyses = []
            
            # Feature drift
            if model_id in self.reference_distributions:
                feature_drift = await self._calculate_feature_drift(model_id, recent_features)
                if feature_drift:
                    drift_analyses.append(feature_drift)
            else:
                # Créer la distribution de référence avec les premières données
                await self._create_reference_distribution(model_id, recent_features)
            
            # Prediction drift
            prediction_drift = await self._calculate_prediction_drift(model_id, recent_predictions)
            if prediction_drift:
                drift_analyses.append(prediction_drift)
            
            # Générer des alertes pour les drifts détectés
            for drift in drift_analyses:
                if drift.is_drifting:
                    alert = Alert(
                        alert_id=str(uuid.uuid4()),
                        model_id=model_id,
                        metric_type=MetricType.DATA_DRIFT if drift.drift_type == DriftType.FEATURE_DRIFT else MetricType.MODEL_DRIFT,
                        severity=AlertSeverity.HIGH if drift.drift_score > 0.1 else AlertSeverity.MEDIUM,
                        message=f"{drift.drift_type.value} detected: score={drift.drift_score:.4f}",
                        threshold_value=drift.threshold,
                        actual_value=drift.drift_score,
                        timestamp=drift.detected_at
                    )
                    
                    self.alerts[model_id].append(alert)
                    
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            logger.error(f"Erreur callback drift: {e}")
        
        except Exception as e:
            logger.error(f"Erreur détection drift pour {model_id}: {e}")
    
    async def _create_reference_distribution(self, model_id: str, features: List[np.ndarray]):
        """Crée la distribution de référence pour le drift detection"""
        
        try:
            if not features:
                return
            
            # Convertir en matrice
            feature_matrix = np.array(features)
            
            # Calculer les statistiques de référence
            reference_stats = {
                "mean": np.mean(feature_matrix, axis=0),
                "std": np.std(feature_matrix, axis=0),
                "min": np.min(feature_matrix, axis=0),
                "max": np.max(feature_matrix, axis=0),
                "percentiles": {
                    "25": np.percentile(feature_matrix, 25, axis=0),
                    "50": np.percentile(feature_matrix, 50, axis=0),
                    "75": np.percentile(feature_matrix, 75, axis=0)
                }
            }
            
            self.reference_distributions[model_id] = reference_stats
            logger.info(f"Distribution de référence créée pour {model_id}")
            
        except Exception as e:
            logger.error(f"Erreur création distribution référence: {e}")
    
    async def _calculate_feature_drift(self, model_id: str, recent_features: List[np.ndarray]) -> Optional[DriftAnalysis]:
        """Calcule le drift des features"""
        
        try:
            if model_id not in self.reference_distributions:
                return None
            
            reference = self.reference_distributions[model_id]
            current_matrix = np.array(recent_features)
            
            # Calculer les statistiques actuelles
            current_mean = np.mean(current_matrix, axis=0)
            current_std = np.std(current_matrix, axis=0)
            
            # Calcul simple du drift basé sur la différence des moyennes
            mean_diff = np.abs(current_mean - reference["mean"])
            normalized_diff = mean_diff / (reference["std"] + 1e-8)  # Éviter division par zéro
            
            # Score de drift = moyenne des différences normalisées
            drift_score = np.mean(normalized_diff)
            
            # Test statistique simple (ici on utilise un threshold fixe)
            p_value = 1.0 - drift_score  # Simplification
            threshold = 0.05
            
            is_drifting = drift_score > 0.1  # Threshold empirique
            
            # Identifier les features les plus affectées
            affected_features = []
            for i, diff in enumerate(normalized_diff):
                if diff > 0.15:  # Threshold par feature
                    affected_features.append(f"feature_{i}")
            
            recommendations = []
            if is_drifting:
                recommendations.extend([
                    "Vérifier la qualité des données d'entrée",
                    "Considérer un re-entraînement du modèle",
                    "Analyser les changements dans la distribution source"
                ])
            
            return DriftAnalysis(
                drift_type=DriftType.FEATURE_DRIFT,
                drift_score=drift_score,
                p_value=p_value,
                threshold=threshold,
                is_drifting=is_drifting,
                detected_at=datetime.now(),
                features_affected=affected_features,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Erreur calcul feature drift: {e}")
            return None
    
    async def _calculate_prediction_drift(self, model_id: str, recent_predictions: List[Dict]) -> Optional[DriftAnalysis]:
        """Calcule le drift des prédictions"""
        
        try:
            # Extraire les prédictions
            predictions = [p.get("prediction") for p in recent_predictions if p.get("prediction") is not None]
            
            if len(predictions) < 100:
                return None
            
            # Pour les prédictions numériques, calculer la variance
            if all(isinstance(p, (int, float)) for p in predictions):
                recent_preds = np.array(predictions[-500:])
                older_preds = np.array(predictions[-1000:-500]) if len(predictions) >= 1000 else recent_preds
                
                # Comparer les moyennes et variances
                recent_mean = np.mean(recent_preds)
                older_mean = np.mean(older_preds)
                
                recent_std = np.std(recent_preds)
                older_std = np.std(older_preds)
                
                # Score de drift basé sur la différence des moyennes
                mean_diff = abs(recent_mean - older_mean)
                std_diff = abs(recent_std - older_std)
                
                drift_score = (mean_diff + std_diff) / 2
                
            else:
                # Pour les prédictions catégorielles, utiliser la distribution
                from collections import Counter
                recent_dist = Counter(predictions[-500:])
                older_dist = Counter(predictions[-1000:-500]) if len(predictions) >= 1000 else recent_dist
                
                # Calculer la divergence de distribution (simplifiée)
                all_classes = set(recent_dist.keys()) | set(older_dist.keys())
                drift_score = 0
                
                for cls in all_classes:
                    recent_prob = recent_dist.get(cls, 0) / len(predictions[-500:])
                    older_prob = older_dist.get(cls, 0) / len(predictions[-1000:-500:] if len(predictions) >= 1000 else predictions[-500:])
                    drift_score += abs(recent_prob - older_prob)
                
                drift_score /= len(all_classes)
            
            threshold = 0.05
            is_drifting = drift_score > threshold
            
            recommendations = []
            if is_drifting:
                recommendations.extend([
                    "Vérifier les performances du modèle",
                    "Analyser les changements dans les patterns de données",
                    "Considérer un A/B test avec un nouveau modèle"
                ])
            
            return DriftAnalysis(
                drift_type=DriftType.PREDICTION_DRIFT,
                drift_score=drift_score,
                p_value=1.0 - drift_score,
                threshold=threshold,
                is_drifting=is_drifting,
                detected_at=datetime.now(),
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Erreur calcul prediction drift: {e}")
            return None
    
    async def get_performance_report(self, 
                                   model_id: str, 
                                   hours_back: int = 24) -> Optional[PerformanceReport]:
        """Génère un rapport de performance"""
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Filtrer les prédictions par période
            predictions = [
                p for p in self.predictions[model_id] 
                if start_time <= p.get("timestamp", datetime.min) <= end_time
            ]
            
            if not predictions:
                return None
            
            # Calculer les métriques
            latencies = [p.get("latency", 0) for p in predictions if "latency" in p]
            total_predictions = len(predictions)
            
            avg_latency = statistics.mean(latencies) if latencies else 0
            p95_latency = np.percentile(latencies, 95) if latencies else 0
            p99_latency = np.percentile(latencies, 99) if latencies else 0
            
            # Calculer le throughput
            duration_hours = (end_time - start_time).total_seconds() / 3600
            throughput = total_predictions / duration_hours if duration_hours > 0 else 0
            
            # Error rate (simulé)
            error_rate = 0.02  # À implémenter avec de vraies erreurs
            
            # Accuracy si on a des labels
            accuracy = None
            with_labels = [p for p in predictions if p.get("actual_label") is not None]
            if with_labels:
                # Calcul d'accuracy simplifié
                correct = sum(1 for p in with_labels if p.get("prediction") == p.get("actual_label"))
                accuracy = correct / len(with_labels)
            
            # Récupérer les alertes de la période
            period_alerts = [
                alert for alert in self.alerts[model_id]
                if start_time <= alert.timestamp <= end_time
            ]
            
            # Analyse de drift récente
            drift_analyses = []
            if len(self.predictions[model_id]) >= self.drift_detection_window:
                recent_drift = await self._detect_drift(model_id)
                # Les analyses de drift sont stockées dans les alertes pour cet exemple
            
            return PerformanceReport(
                model_id=model_id,
                period_start=start_time,
                period_end=end_time,
                total_predictions=total_predictions,
                avg_latency=avg_latency,
                p95_latency=p95_latency,
                p99_latency=p99_latency,
                error_rate=error_rate,
                throughput=throughput,
                accuracy=accuracy,
                drift_analysis=drift_analyses,
                alerts=period_alerts
            )
            
        except Exception as e:
            logger.error(f"Erreur génération rapport pour {model_id}: {e}")
            return None
    
    async def get_active_alerts(self, model_id: Optional[str] = None) -> List[Alert]:
        """Récupère les alertes actives"""
        
        if model_id:
            return [alert for alert in self.alerts[model_id] if not alert.resolved]
        else:
            all_alerts = []
            for model_alerts in self.alerts.values():
                all_alerts.extend([alert for alert in model_alerts if not alert.resolved])
            return all_alerts
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """
Résout une alerte"""
        
        for model_alerts in self.alerts.values():
            for alert in model_alerts:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    logger.info(f"Alerte résolue: {alert_id}")
                    return True
        
        return False
    
    async def export_metrics(self, model_id: str, filepath: str):
        """Exporte les métriques vers un fichier"""
        
        try:
            export_data = {
                "model_id": model_id,
                "exported_at": datetime.now().isoformat(),
                "metrics": {},
                "predictions": list(self.predictions[model_id]),
                "alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "metric_type": alert.metric_type.value,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat(),
                        "resolved": alert.resolved
                    }
                    for alert in self.alerts[model_id]
                ]
            }
            
            # Exporter les métriques
            for metric_type, points in self.metrics[model_id].items():
                export_data["metrics"][metric_type.value] = [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "value": point.value,
                        "metadata": point.metadata
                    }
                    for point in points
                ]
            
            # Sauvegarder
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Métriques exportées vers: {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur export métriques: {e}")
    
    async def cleanup_old_data(self, days_old: int = 7):
        """Nettoie les anciennes données"""
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for model_id in list(self.metrics.keys()):
            # Nettoyer les métriques
            for metric_type in self.metrics[model_id]:
                old_metrics = [
                    point for point in self.metrics[model_id][metric_type]
                    if point.timestamp < cutoff_date
                ]
                for _ in range(len(old_metrics)):
                    if self.metrics[model_id][metric_type]:
                        self.metrics[model_id][metric_type].popleft()
            
            # Nettoyer les alertes
            self.alerts[model_id] = [
                alert for alert in self.alerts[model_id]
                if alert.timestamp >= cutoff_date
            ]
        
        logger.info(f"Données antérieures à {cutoff_date} nettoyées")


# Factory pour créer des moniteurs spécialisés
class MonitorFactory:
    """Factory pour créer des moniteurs spécialisés"""
    
    @staticmethod
    def create_production_monitor() -> ModelPerformanceMonitor:
        """
Moniteur pour production avec alertes strictes"""
        monitor = ModelPerformanceMonitor(
            buffer_size=50000,
            drift_detection_window=2000,
            alert_cooldown_minutes=15
        )
        
        # Thresholds stricts pour production
        strict_thresholds = {
            MetricType.LATENCY: {"warning": 0.2, "critical": 0.5},
            MetricType.ERROR_RATE: {"warning": 0.02, "critical": 0.05},
            MetricType.THROUGHPUT: {"warning": 100, "critical": 50},
            MetricType.DATA_DRIFT: {"warning": 0.03, "critical": 0.01}
        }
        
        monitor.default_thresholds = strict_thresholds
        return monitor
    
    @staticmethod
    def create_development_monitor() -> ModelPerformanceMonitor:
        """Moniteur pour développement avec alertes plus permissives"""
        return ModelPerformanceMonitor(
            buffer_size=10000,
            drift_detection_window=500,
            alert_cooldown_minutes=60
        )


# Exemple d'utilisation
async def example_usage():
    """
Exemple d'utilisation du moniteur de performance"""
    
    # Créer le moniteur
    monitor = MonitorFactory.create_production_monitor()
    
    # Callback pour les alertes
    def alert_handler(alert: Alert):
        print(f"🚨 ALERTE: {alert.message} (Sévérité: {alert.severity.value})")
    
    monitor.add_alert_callback(alert_handler)
    
    # Simuler des prédictions
    model_id = "content_protection_classifier_v1"
    
    for i in range(1000):
        # Simuler des features et prédictions
        features = np.random.randn(10)
        prediction = 1 if np.sum(features) > 0 else 0
        latency = np.random.uniform(0.1, 0.3)  # Latence normale
        
        # Simuler une dégradation après 500 prédictions
        if i > 500:
            latency += np.random.uniform(0.2, 0.5)  # Latence élevée
        
        await monitor.record_prediction(
            model_id=model_id,
            features=features,
            prediction=prediction,
            latency=latency,
            actual_label=prediction  # Dans un vrai cas, serait disponible plus tard
        )
        
        await asyncio.sleep(0.01)  # Simulation temps réel
    
    # Générer un rapport
    report = await monitor.get_performance_report(model_id, hours_back=1)
    if report:
        print(f"\n📊 RAPPORT DE PERFORMANCE:")
        print(f"Prédictions totales: {report.total_predictions}")
        print(f"Latence moyenne: {report.avg_latency:.3f}s")
        print(f"Latence P95: {report.p95_latency:.3f}s")
        print(f"Throughput: {report.throughput:.1f} pred/heure")
        print(f"Alertes: {len(report.alerts)}")
    
    # Lister les alertes actives
    active_alerts = await monitor.get_active_alerts(model_id)
    print(f"\n🔔 Alertes actives: {len(active_alerts)}")
    
    for alert in active_alerts:
        print(f"  - {alert.message}")


if __name__ == "__main__":
    asyncio.run(example_usage())