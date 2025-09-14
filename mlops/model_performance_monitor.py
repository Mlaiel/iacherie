"""
Model Performance Monitor module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🚀 Model Performance Monitor - Enterprise MLOps Platform
ML Engineer Expertise: Monitor de performance de modèles avec drift detection avancé

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriftType(Enum):
    """Types de drift détectés"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    PERFORMANCE_DRIFT = "performance_drift"
    NO_DRIFT = "no_drift"

class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ModelType(Enum):
    """Types de modèles supportés"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    RECOMMENDATION = "recommendation"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    TIME_SERIES = "time_series"

class MetricType(Enum):
    """Types de métriques de performance"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    MSE = "mse"
    RMSE = "rmse"
    MAE = "mae"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    CUSTOM = "custom"

@dataclass
class ModelMetrics:
    """Métriques de performance d'un modèle"""
    model_id: str
    timestamp: datetime
    model_version: str
    dataset_name: str
    sample_size: int
    metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DriftDetectionResult:
    """Résultat de détection de drift"""
    model_id: str
    timestamp: datetime
    drift_type: DriftType
    severity: AlertSeverity
    confidence_score: float
    affected_features: List[str]
    drift_magnitude: float
    baseline_period: Tuple[datetime, datetime]
    current_period: Tuple[datetime, datetime]
    test_statistic: float
    p_value: float
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceBenchmark:
    """Benchmark de performance de référence"""
    model_id: str
    model_type: ModelType
    baseline_metrics: Dict[str, float]
    baseline_period: Tuple[datetime, datetime]
    sample_size: int
    confidence_interval: Dict[str, Tuple[float, float]]
    created_at: datetime
    updated_at: datetime

@dataclass
class AlertRule:
    """Règle d'alerte pour monitoring"""
    rule_id: str
    model_id: str
    metric_type: MetricType
    threshold_type: str  # "absolute", "relative", "percentile"
    threshold_value: float
    comparison_operator: str  # ">", "<", ">=", "<=", "=="
    severity: AlertSeverity
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Alerte de monitoring"""
    alert_id: str
    timestamp: datetime
    model_id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False

class StatisticalDriftDetector:
    """Détecteur de drift statistique avancé"""
    
    def __init__(self, sensitivity -> None: float = 0.05) -> None:
        self.sensitivity = sensitivity  # Seuil p-value
        
    def detect_data_drift(
        self,
        baseline_data: np.ndarray,
        current_data: np.ndarray,
        feature_names: Optional[List[str]] = None
    ) -> DriftDetectionResult:
        """Détecte le drift dans les données d'entrée"""
        
        if baseline_data.shape[1] != current_data.shape[1]:
            raise ValueError("Les données baseline et current doivent avoir le même nombre de features")
        
        n_features = baseline_data.shape[1]
        feature_names = feature_names or [f"feature_{i}" for i in range(n_features)]
        
        drift_scores = []
        p_values = []
        affected_features = []
        
        for i in range(n_features):
            baseline_feature = baseline_data[:, i]
            current_feature = current_data[:, i]
            
            # Test de Kolmogorov-Smirnov pour drift de distribution
            ks_statistic, p_value = stats.ks_2samp(baseline_feature, current_feature)
            
            drift_scores.append(ks_statistic)
            p_values.append(p_value)
            
            if p_value < self.sensitivity:
                affected_features.append(feature_names[i])
        
        # Score global de drift
        avg_drift_score = np.mean(drift_scores)
        min_p_value = np.min(p_values)
        
        # Détermination de la sévérité
        if len(affected_features) == 0:
            severity = AlertSeverity.LOW
            drift_type = DriftType.NO_DRIFT
        elif len(affected_features) / n_features < 0.2:
            severity = AlertSeverity.MEDIUM
            drift_type = DriftType.DATA_DRIFT
        elif len(affected_features) / n_features < 0.5:
            severity = AlertSeverity.HIGH
            drift_type = DriftType.DATA_DRIFT
        else:
            severity = AlertSeverity.CRITICAL
            drift_type = DriftType.DATA_DRIFT
        
        return DriftDetectionResult(
            model_id="",  # À remplir par l'appelant
            timestamp=datetime.now(),
            drift_type=drift_type,
            severity=severity,
            confidence_score=1 - min_p_value,
            affected_features=affected_features,
            drift_magnitude=avg_drift_score,
            baseline_period=(datetime.now() - timedelta(days=7), datetime.now() - timedelta(days=1)),
            current_period=(datetime.now() - timedelta(hours=24), datetime.now()),
            test_statistic=avg_drift_score,
            p_value=min_p_value,
            recommendations=self._generate_drift_recommendations(affected_features, avg_drift_score)
        )
    
    def detect_concept_drift(
        self,
        baseline_predictions: np.ndarray,
        baseline_targets: np.ndarray,
        current_predictions: np.ndarray,
        current_targets: np.ndarray,
        model_type: ModelType
    ) -> DriftDetectionResult:
        """Détecte le concept drift (changement dans la relation X->y)"""
        
        # Calcul des performances baseline et current
        baseline_perf = self._calculate_performance(
            baseline_predictions, baseline_targets, model_type
        )
        current_perf = self._calculate_performance(
            current_predictions, current_targets, model_type
        )
        
        # Test statistique sur la différence de performance
        if model_type == ModelType.CLASSIFICATION:
            # Test sur l'accuracy
            baseline_correct = (baseline_predictions == baseline_targets).astype(int)
            current_correct = (current_predictions == current_targets).astype(int)
            
            # Test de proportions
            t_stat, p_value = stats.ttest_ind(baseline_correct, current_correct)
            
            drift_magnitude = abs(baseline_perf['accuracy'] - current_perf['accuracy'])
            
        else:  # Regression
            # Test sur les erreurs
            baseline_errors = np.abs(baseline_predictions - baseline_targets)
            current_errors = np.abs(current_predictions - current_targets)
            
            t_stat, p_value = stats.ttest_ind(baseline_errors, current_errors)
            
            drift_magnitude = abs(baseline_perf['mse'] - current_perf['mse']) / baseline_perf['mse']
        
        # Détermination de la sévérité
        if p_value > self.sensitivity:
            severity = AlertSeverity.LOW
            drift_type = DriftType.NO_DRIFT
        elif drift_magnitude < 0.05:
            severity = AlertSeverity.MEDIUM
            drift_type = DriftType.CONCEPT_DRIFT
        elif drift_magnitude < 0.15:
            severity = AlertSeverity.HIGH
            drift_type = DriftType.CONCEPT_DRIFT
        else:
            severity = AlertSeverity.CRITICAL
            drift_type = DriftType.CONCEPT_DRIFT
        
        return DriftDetectionResult(
            model_id="",
            timestamp=datetime.now(),
            drift_type=drift_type,
            severity=severity,
            confidence_score=1 - p_value if p_value < self.sensitivity else 0.5,
            affected_features=["target_relationship"],
            drift_magnitude=drift_magnitude,
            baseline_period=(datetime.now() - timedelta(days=7), datetime.now() - timedelta(days=1)),
            current_period=(datetime.now() - timedelta(hours=24), datetime.now()),
            test_statistic=abs(t_stat),
            p_value=p_value,
            recommendations=self._generate_concept_drift_recommendations(drift_magnitude, model_type),
            metadata={
                'baseline_performance': baseline_perf,
                'current_performance': current_perf
            }
        )
    
    def _calculate_performance(
        self,
        predictions: np.ndarray,
        targets: np.ndarray,
        model_type: ModelType
    ) -> Dict[str, float]:
        """Calcule les métriques de performance"""
        
        if model_type == ModelType.CLASSIFICATION:
            return {
                'accuracy': accuracy_score(targets, predictions),
                'precision': precision_score(targets, predictions, average='weighted', zero_division=0),
                'recall': recall_score(targets, predictions, average='weighted', zero_division=0),
                'f1_score': f1_score(targets, predictions, average='weighted', zero_division=0)
            }
        else:  # Regression
            mse = mean_squared_error(targets, predictions)
            return {
                'mse': mse,
                'rmse': np.sqrt(mse),
                'mae': np.mean(np.abs(targets - predictions))
            }
    
    def _generate_drift_recommendations(
        self,
        affected_features: List[str],
        drift_magnitude: float
    ) -> List[str]:
        """Génère des recommandations pour le drift de données"""
        
        recommendations = []
        
        if len(affected_features) > 0:
            recommendations.append("Analyser les changements dans les sources de données")
            recommendations.append(f"Revoir les features affectées: {', '.join(affected_features)}")
            
            if drift_magnitude > 0.3:
                recommendations.append("Considérer un ré-entraînement du modèle")
                recommendations.append("Mettre en place des transformations de données adaptatives")
            else:
                recommendations.append("Surveiller l'évolution du drift")
                recommendations.append("Ajuster les seuils de monitoring si nécessaire")
        
        return recommendations
    
    def _generate_concept_drift_recommendations(
        self,
        drift_magnitude: float,
        model_type: ModelType
    ) -> List[str]:
        """Génère des recommandations pour le concept drift"""
        
        recommendations = []
        
        if drift_magnitude > 0.1:
            recommendations.append("Ré-entraînement urgent du modèle recommandé")
            recommendations.append("Analyser les changements dans le domaine métier")
            
            if model_type == ModelType.CLASSIFICATION:
                recommendations.append("Revoir la distribution des classes")
                recommendations.append("Considérer l'ajout de nouvelles features")
            else:
                recommendations.append("Analyser les changements dans la variable cible")
                recommendations.append("Vérifier la pertinence des features actuelles")
        else:
            recommendations.append("Surveiller l'évolution de la performance")
            recommendations.append("Planifier un ré-entraînement préventif")
        
        return recommendations

class PerformanceAnalyzer:
    """Analyseur de performance avancé"""
    
    def __init__(self) -> None:
        self.baseline_cache: Dict[str, PerformanceBenchmark] = {}
        
    def create_baseline(
        self,
        model_id: str,
        model_type: ModelType,
        predictions: np.ndarray,
        targets: np.ndarray,
        feature_data: Optional[np.ndarray] = None
    ) -> PerformanceBenchmark:
        """Crée un benchmark de référence"""
        
        # Calcul des métriques de base
        if model_type == ModelType.CLASSIFICATION:
            metrics = {
                'accuracy': accuracy_score(targets, predictions),
                'precision': precision_score(targets, predictions, average='weighted', zero_division=0),
                'recall': recall_score(targets, predictions, average='weighted', zero_division=0),
                'f1_score': f1_score(targets, predictions, average='weighted', zero_division=0)
            }
        else:
            mse = mean_squared_error(targets, predictions)
            metrics = {
                'mse': mse,
                'rmse': np.sqrt(mse),
                'mae': np.mean(np.abs(targets - predictions))
            }
        
        # Calcul des intervalles de confiance par bootstrap
        confidence_interval = {}
        for metric_name, metric_value in metrics.items():
            ci_lower, ci_upper = self._bootstrap_confidence_interval(
                predictions, targets, metric_name, model_type
            )
            confidence_interval[metric_name] = (ci_lower, ci_upper)
        
        benchmark = PerformanceBenchmark(
            model_id=model_id,
            model_type=model_type,
            baseline_metrics=metrics,
            baseline_period=(datetime.now() - timedelta(days=7), datetime.now()),
            sample_size=len(predictions),
            confidence_interval=confidence_interval,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.baseline_cache[model_id] = benchmark
        return benchmark
    
    def _bootstrap_confidence_interval(
        self,
        predictions: np.ndarray,
        targets: np.ndarray,
        metric_name: str,
        model_type: ModelType,
        n_bootstrap: int = 1000,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Calcule l'intervalle de confiance par bootstrap"""
        
        bootstrap_scores = []
        n_samples = len(predictions)
        
        for _ in range(n_bootstrap):
            # Échantillonnage avec remise
            indices = np.random.choice(n_samples, size=n_samples, replace=True)
            bootstrap_predictions = predictions[indices]
            bootstrap_targets = targets[indices]
            
            # Calcul de la métrique
            if model_type == ModelType.CLASSIFICATION:
                if metric_name == 'accuracy':
                    score = accuracy_score(bootstrap_targets, bootstrap_predictions)
                elif metric_name == 'precision':
                    score = precision_score(bootstrap_targets, bootstrap_predictions, average='weighted', zero_division=0)
                elif metric_name == 'recall':
                    score = recall_score(bootstrap_targets, bootstrap_predictions, average='weighted', zero_division=0)
                elif metric_name == 'f1_score':
                    score = f1_score(bootstrap_targets, bootstrap_predictions, average='weighted', zero_division=0)
                else:
                    continue
            else:
                if metric_name == 'mse':
                    score = mean_squared_error(bootstrap_targets, bootstrap_predictions)
                elif metric_name == 'rmse':
                    score = np.sqrt(mean_squared_error(bootstrap_targets, bootstrap_predictions))
                elif metric_name == 'mae':
                    score = np.mean(np.abs(bootstrap_targets - bootstrap_predictions))
                else:
                    continue
            
            bootstrap_scores.append(score)
        
        # Calcul de l'intervalle de confiance
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        ci_lower = np.percentile(bootstrap_scores, lower_percentile)
        ci_upper = np.percentile(bootstrap_scores, upper_percentile)
        
        return ci_lower, ci_upper
    
    def compare_with_baseline(
        self,
        model_id: str,
        current_predictions: np.ndarray,
        current_targets: np.ndarray
    ) -> Dict[str, Any]:
        """Compare les performances actuelles avec la baseline"""
        
        baseline = self.baseline_cache.get(model_id)
        if not baseline:
            return {"error": "Aucune baseline trouvée pour ce modèle"}
        
        # Calcul des métriques actuelles
        if baseline.model_type == ModelType.CLASSIFICATION:
            current_metrics = {
                'accuracy': accuracy_score(current_targets, current_predictions),
                'precision': precision_score(current_targets, current_predictions, average='weighted', zero_division=0),
                'recall': recall_score(current_targets, current_predictions, average='weighted', zero_division=0),
                'f1_score': f1_score(current_targets, current_predictions, average='weighted', zero_division=0)
            }
        else:
            mse = mean_squared_error(current_targets, current_predictions)
            current_metrics = {
                'mse': mse,
                'rmse': np.sqrt(mse),
                'mae': np.mean(np.abs(current_targets - current_predictions))
            }
        
        # Comparaison avec la baseline
        comparison = {}
        performance_alerts = []
        
        for metric_name, current_value in current_metrics.items():
            baseline_value = baseline.baseline_metrics.get(metric_name, 0)
            ci_lower, ci_upper = baseline.confidence_interval.get(metric_name, (0, 0))
            
            # Calcul du changement relatif
            if baseline_value != 0:
                relative_change = (current_value - baseline_value) / baseline_value
            else:
                relative_change = 0
            
            # Vérification si dans l'intervalle de confiance
            within_ci = ci_lower <= current_value <= ci_upper
            
            comparison[metric_name] = {
                'current_value': current_value,
                'baseline_value': baseline_value,
                'relative_change': relative_change,
                'absolute_change': current_value - baseline_value,
                'within_confidence_interval': within_ci,
                'confidence_interval': (ci_lower, ci_upper)
            }
            
            # Génération d'alertes si nécessaire
            if not within_ci:
                if baseline.model_type == ModelType.CLASSIFICATION and metric_name in ['accuracy', 'precision', 'recall', 'f1_score']:
                    if current_value < ci_lower:
                        severity = AlertSeverity.HIGH if abs(relative_change) > 0.1 else AlertSeverity.MEDIUM
                        performance_alerts.append({
                            'metric': metric_name,
                            'severity': severity.value,
                            'message': f"{metric_name} a chuté de {abs(relative_change)*100:.1f}%"
                        })
                elif baseline.model_type in [ModelType.REGRESSION] and metric_name in ['mse', 'rmse', 'mae']:
                    if current_value > ci_upper:
                        severity = AlertSeverity.HIGH if abs(relative_change) > 0.1 else AlertSeverity.MEDIUM
                        performance_alerts.append({
                            'metric': metric_name,
                            'severity': severity.value,
                            'message': f"{metric_name} a augmenté de {abs(relative_change)*100:.1f}%"
                        })
        
        return {
            'model_id': model_id,
            'comparison_timestamp': datetime.now().isoformat(),
            'baseline_period': [baseline.baseline_period[0].isoformat(), baseline.baseline_period[1].isoformat()],
            'current_sample_size': len(current_predictions),
            'baseline_sample_size': baseline.sample_size,
            'metrics_comparison': comparison,
            'performance_alerts': performance_alerts,
            'overall_status': 'degraded' if performance_alerts else 'stable'
        }

class ModelPerformanceMonitor:
    """Monitor principal de performance de modèles avec drift detection avancé"""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.drift_detector = StatisticalDriftDetector(
            sensitivity=config.get('drift_sensitivity', 0.05)
        )
        self.performance_analyzer = PerformanceAnalyzer()
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.metrics_history: List[ModelMetrics] = []
        self.drift_history: List[DriftDetectionResult] = []
        self.monitoring_models: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        
    async def start(self) -> None:
        """Démarre le monitoring de performance"""
        try:
            logger.info("Démarrage du monitor de performance de modèles")
            
            self.is_running = True
            
            # Démarrage des tâches de fond
            asyncio.create_task(self._drift_detection_loop())
            asyncio.create_task(self._performance_analysis_loop())
            asyncio.create_task(self._alert_processor())
            asyncio.create_task(self._metrics_cleanup())
            
            logger.info("Monitor de performance démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage monitor: {e}")
            raise
    
    async def stop(self) -> None:
        """Arrête le monitoring"""
        logger.info("Arrêt du monitor de performance")
        self.is_running = False
    
    def register_model(
        self,
        model_id -> None: str,
        model_type -> None: ModelType,
        baseline_data -> None: Dict[str, np.ndarray],
        metadata -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        """Enregistre un modèle pour monitoring"""
        
        # Création de la baseline de performance
        baseline_benchmark = self.performance_analyzer.create_baseline(
            model_id=model_id,
            model_type=model_type,
            predictions=baseline_data['predictions'],
            targets=baseline_data['targets'],
            feature_data=baseline_data.get('features')
        )
        
        # Enregistrement du modèle
        self.monitoring_models[model_id] = {
            'model_type': model_type,
            'baseline_benchmark': baseline_benchmark,
            'baseline_features': baseline_data.get('features'),
            'registered_at': datetime.now(),
            'metadata': metadata or {}
        }
        
        logger.info(f"Modèle enregistré pour monitoring: {model_id}")
    
    async def submit_inference_data(
        self,
        model_id -> None: str,
        predictions -> None: np.ndarray,
        targets -> None: Optional[np.ndarray] = None,
        features -> None: Optional[np.ndarray] = None,
        metadata -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        """Soumet des données d'inférence pour analyse"""
        
        if model_id not in self.monitoring_models:
            logger.warning(f"Modèle non enregistré: {model_id}")
            return
        
        model_info = self.monitoring_models[model_id]
        
        # Stockage des métriques si on a les targets
        if targets is not None:
            model_type = model_info['model_type']
            
            if model_type == ModelType.CLASSIFICATION:
                metrics = {
                    'accuracy': accuracy_score(targets, predictions),
                    'precision': precision_score(targets, predictions, average='weighted', zero_division=0),
                    'recall': recall_score(targets, predictions, average='weighted', zero_division=0),
                    'f1_score': f1_score(targets, predictions, average='weighted', zero_division=0)
                }
            else:
                mse = mean_squared_error(targets, predictions)
                metrics = {
                    'mse': mse,
                    'rmse': np.sqrt(mse),
                    'mae': np.mean(np.abs(targets - predictions))
                }
            
            # Ajout des métriques personnalisées
            if metadata:
                metrics.update(metadata.get('custom_metrics', {}))
            
            model_metrics = ModelMetrics(
                model_id=model_id,
                timestamp=datetime.now(),
                model_version=metadata.get('model_version', 'unknown') if metadata else 'unknown',
                dataset_name=metadata.get('dataset_name', 'inference') if metadata else 'inference',
                sample_size=len(predictions),
                metrics=metrics,
                metadata=metadata or {}
            )
            
            self.metrics_history.append(model_metrics)
        
        # Détection de drift si on a les features
        if features is not None and model_info.get('baseline_features') is not None:
            asyncio.create_task(self._detect_drift_async(model_id, features, predictions, targets))
    
    async def _detect_drift_async(
        self,
        model_id -> None: str,
        current_features -> None: np.ndarray,
        current_predictions -> None: np.ndarray,
        current_targets -> None: Optional[np.ndarray]
    ) -> None:
        """Détection de drift asynchrone"""
        try:
            model_info = self.monitoring_models[model_id]
            baseline_features = model_info['baseline_features']
            
            # Détection de data drift
            data_drift_result = self.drift_detector.detect_data_drift(
                baseline_data=baseline_features,
                current_data=current_features
            )
            data_drift_result.model_id = model_id
            
            self.drift_history.append(data_drift_result)
            
            # Génération d'alerte si drift détecté
            if data_drift_result.drift_type != DriftType.NO_DRIFT:
                await self._generate_drift_alert(data_drift_result)
            
            # Détection de concept drift si on a les targets
            if current_targets is not None:
                baseline_benchmark = model_info['baseline_benchmark']
                
                # On doit reconstituer les baseline predictions
                # En pratique, elles seraient stockées lors de l'enregistrement
                # Ici on simule avec des données similaires
                baseline_size = min(len(current_predictions), 1000)
                baseline_predictions = np.random.choice(
                    current_predictions, size=baseline_size, replace=True
                )
                baseline_targets = np.random.choice(
                    current_targets, size=baseline_size, replace=True
                )
                
                concept_drift_result = self.drift_detector.detect_concept_drift(
                    baseline_predictions=baseline_predictions,
                    baseline_targets=baseline_targets,
                    current_predictions=current_predictions,
                    current_targets=current_targets,
                    model_type=model_info['model_type']
                )
                concept_drift_result.model_id = model_id
                
                self.drift_history.append(concept_drift_result)
                
                if concept_drift_result.drift_type != DriftType.NO_DRIFT:
                    await self._generate_drift_alert(concept_drift_result)
            
        except Exception as e:
            logger.error(f"Erreur détection drift pour {model_id}: {e}")
    
    async def _generate_drift_alert(self, drift_result -> None: DriftDetectionResult) -> None:
        """Génère une alerte de drift"""
        alert_id = f"drift-{drift_result.model_id}-{int(drift_result.timestamp.timestamp())}"
        
        message = f"Drift {drift_result.drift_type.value} détecté sur {drift_result.model_id} "
        message += f"(magnitude: {drift_result.drift_magnitude:.3f}, "
        message += f"features affectées: {len(drift_result.affected_features)})"
        
        alert = Alert(
            alert_id=alert_id,
            timestamp=drift_result.timestamp,
            model_id=drift_result.model_id,
            rule_id="drift_detection",
            severity=drift_result.severity,
            message=message,
            current_value=drift_result.drift_magnitude,
            threshold_value=self.drift_detector.sensitivity,
            metadata={
                'drift_type': drift_result.drift_type.value,
                'affected_features': drift_result.affected_features,
                'recommendations': drift_result.recommendations,
                'p_value': drift_result.p_value,
                'test_statistic': drift_result.test_statistic
            }
        )
        
        self.active_alerts[alert_id] = alert
        logger.warning(f"Alerte drift générée: {alert_id}")
    
    def add_alert_rule(self, rule -> None: AlertRule) -> None:
        """Ajoute une règle d'alerte"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Règle d'alerte ajoutée: {rule.rule_id}")
    
    def remove_alert_rule(self, rule_id -> None: str) -> None:
        """Supprime une règle d'alerte"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Règle d'alerte supprimée: {rule_id}")
    
    async def _drift_detection_loop(self) -> None:
        """Boucle de détection de drift"""
        while self.is_running:
            try:
                # La détection de drift est déclenchée par submit_inference_data
                # Cette boucle peut servir pour des analyses périodiques
                await asyncio.sleep(300)  # Vérification toutes les 5 minutes
                
            except Exception as e:
                logger.error(f"Erreur loop drift detection: {e}")
                await asyncio.sleep(300)
    
    async def _performance_analysis_loop(self) -> None:
        """Boucle d'analyse de performance"""
        while self.is_running:
            try:
                # Analyse des métriques récentes
                recent_cutoff = datetime.now() - timedelta(hours=1)
                recent_metrics = [
                    m for m in self.metrics_history
                    if m.timestamp >= recent_cutoff
                ]
                
                # Analyse par modèle
                for model_id in self.monitoring_models.keys():
                    model_metrics = [m for m in recent_metrics if m.model_id == model_id]
                    
                    if model_metrics:
                        await self._analyze_model_performance(model_id, model_metrics)
                
                await asyncio.sleep(600)  # Analyse toutes les 10 minutes
                
            except Exception as e:
                logger.error(f"Erreur loop analyse performance: {e}")
                await asyncio.sleep(600)
    
    async def _analyze_model_performance(
        self,
        model_id -> None: str,
        recent_metrics -> None: List[ModelMetrics]
    ) -> None:
        """Analyse la performance d'un modèle"""
        try:
            if not recent_metrics:
                return
            
            # Métriques moyennes récentes
            avg_metrics = {}
            for metric_name in recent_metrics[0].metrics.keys():
                values = [m.metrics[metric_name] for m in recent_metrics if metric_name in m.metrics]
                if values:
                    avg_metrics[metric_name] = np.mean(values)
            
            # Vérification des règles d'alerte
            for rule in self.alert_rules.values():
                if rule.model_id != model_id or not rule.enabled:
                    continue
                
                metric_value = avg_metrics.get(rule.metric_type.value)
                if metric_value is None:
                    continue
                
                # Évaluation de la règle
                if self._evaluate_alert_rule(rule, metric_value):
                    await self._generate_performance_alert(rule, metric_value)
            
        except Exception as e:
            logger.error(f"Erreur analyse performance {model_id}: {e}")
    
    def _evaluate_alert_rule(self, rule: AlertRule, current_value: float) -> bool:
        """Évalue une règle d'alerte"""
        
        threshold = rule.threshold_value
        operator = rule.comparison_operator
        
        if operator == ">":
            return current_value > threshold
        elif operator == "<":
            return current_value < threshold
        elif operator == ">=":
            return current_value >= threshold
        elif operator == "<=":
            return current_value <= threshold
        elif operator == "==":
            return abs(current_value - threshold) < 0.001
        else:
            return False
    
    async def _generate_performance_alert(self, rule -> None: AlertRule, current_value -> None: float) -> None:
        """Génère une alerte de performance"""
        
        alert_id = f"perf-{rule.rule_id}-{int(datetime.now().timestamp())}"
        
        message = f"Seuil de performance dépassé pour {rule.model_id}: "
        message += f"{rule.metric_type.value} = {current_value:.3f} {rule.comparison_operator} {rule.threshold_value}"
        
        alert = Alert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            model_id=rule.model_id,
            rule_id=rule.rule_id,
            severity=rule.severity,
            message=message,
            current_value=current_value,
            threshold_value=rule.threshold_value,
            metadata=rule.metadata.copy()
        )
        
        self.active_alerts[alert_id] = alert
        logger.warning(f"Alerte performance générée: {alert_id}")
    
    async def _alert_processor(self) -> None:
        """Processeur d'alertes"""
        while self.is_running:
            try:
                # Traitement des alertes actives
                for alert_id, alert in list(self.active_alerts.items()):
                    if not alert.acknowledged:
                        await self._process_alert(alert)
                
                await asyncio.sleep(60)  # Traitement toutes les minutes
                
            except Exception as e:
                logger.error(f"Erreur processeur alertes: {e}")
                await asyncio.sleep(60)
    
    async def _process_alert(self, alert -> None: Alert) -> None:
        """Traite une alerte"""
        try:
            # En production, ceci enverrait des notifications
            # (email, Slack, webhook, etc.)
            
            logger.info(f"Traitement alerte {alert.alert_id}: {alert.message}")
            
            # Simulation de l'envoi de notification
            await asyncio.sleep(0.1)
            
            # Marquer comme traitée
            alert.acknowledged = True
            
        except Exception as e:
            logger.error(f"Erreur traitement alerte {alert.alert_id}: {e}")
    
    async def _metrics_cleanup(self) -> None:
        """Nettoyage périodique des métriques"""
        while self.is_running:
            try:
                # Nettoyage des métriques anciennes
                cutoff_date = datetime.now() - timedelta(days=self.config.get('metrics_retention_days', 30))
                
                self.metrics_history = [
                    m for m in self.metrics_history
                    if m.timestamp >= cutoff_date
                ]
                
                self.drift_history = [
                    d for d in self.drift_history
                    if d.timestamp >= cutoff_date
                ]
                
                # Nettoyage des alertes résolues anciennes
                alert_cutoff = datetime.now() - timedelta(days=7)
                self.active_alerts = {
                    alert_id: alert for alert_id, alert in self.active_alerts.items()
                    if not alert.resolved or alert.timestamp >= alert_cutoff
                }
                
                await asyncio.sleep(3600)  # Nettoyage toutes les heures
                
            except Exception as e:
                logger.error(f"Erreur nettoyage métriques: {e}")
                await asyncio.sleep(3600)
    
    def get_model_status(self, model_id: str) -> Dict[str, Any]:
        """Récupère le statut d'un modèle"""
        
        if model_id not in self.monitoring_models:
            return {"error": "Modèle non trouvé"}
        
        model_info = self.monitoring_models[model_id]
        
        # Métriques récentes
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_metrics = [
            m for m in self.metrics_history
            if m.model_id == model_id and m.timestamp >= recent_cutoff
        ]
        
        # Drift récent
        recent_drift = [
            d for d in self.drift_history
            if d.model_id == model_id and d.timestamp >= recent_cutoff
        ]
        
        # Alertes actives
        active_model_alerts = [
            alert for alert in self.active_alerts.values()
            if alert.model_id == model_id and not alert.resolved
        ]
        
        # Calcul des métriques moyennes récentes
        avg_metrics = {}
        if recent_metrics:
            for metric_name in recent_metrics[0].metrics.keys():
                values = [m.metrics[metric_name] for m in recent_metrics if metric_name in m.metrics]
                if values:
                    avg_metrics[metric_name] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values)
                    }
        
        # Statut global
        status = "healthy"
        if active_model_alerts:
            max_severity = max(alert.severity for alert in active_model_alerts)
            if max_severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                status = "critical"
            else:
                status = "warning"
        elif recent_drift and any(d.drift_type != DriftType.NO_DRIFT for d in recent_drift):
            status = "drift_detected"
        
        return {
            'model_id': model_id,
            'status': status,
            'model_type': model_info['model_type'].value,
            'registered_at': model_info['registered_at'].isoformat(),
            'recent_metrics_24h': avg_metrics,
            'recent_drift_events': len(recent_drift),
            'active_alerts': len(active_model_alerts),
            'total_inferences_24h': len(recent_metrics),
            'baseline_created': model_info['baseline_benchmark'].created_at.isoformat(),
            'baseline_metrics': model_info['baseline_benchmark'].baseline_metrics
        }
    
    def get_global_status(self) -> Dict[str, Any]:
        """Récupère le statut global du monitoring"""
        
        total_models = len(self.monitoring_models)
        total_alerts = len([a for a in self.active_alerts.values() if not a.resolved])
        
        # Statut par modèle
        model_statuses = {}
        healthy_models = 0
        
        for model_id in self.monitoring_models.keys():
            status = self.get_model_status(model_id)
            model_statuses[model_id] = status['status']
            if status['status'] == 'healthy':
                healthy_models += 1
        
        # Métriques globales récentes
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= recent_cutoff]
        recent_drift = [d for d in self.drift_history if d.timestamp >= recent_cutoff]
        
        return {
            'monitoring_status': 'running' if self.is_running else 'stopped',
            'total_models': total_models,
            'healthy_models': healthy_models,
            'models_with_issues': total_models - healthy_models,
            'total_active_alerts': total_alerts,
            'total_inferences_24h': len(recent_metrics),
            'drift_events_24h': len([d for d in recent_drift if d.drift_type != DriftType.NO_DRIFT]),
            'model_statuses': model_statuses,
            'alert_rules_count': len(self.alert_rules),
            'metrics_retention_days': self.config.get('metrics_retention_days', 30),
            'drift_sensitivity': self.drift_detector.sensitivity
        }
    
    def get_drift_analysis(self, model_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyse détaillée du drift pour un modèle"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        model_drift_events = [
            d for d in self.drift_history
            if d.model_id == model_id and d.timestamp >= cutoff_date
        ]
        
        if not model_drift_events:
            return {
                'model_id': model_id,
                'period_days': days,
                'drift_events': 0,
                'analysis': 'Aucun drift détecté sur la période'
            }
        
        # Analyse des types de drift
        drift_type_counts = {}
        for drift_event in model_drift_events:
            drift_type = drift_event.drift_type.value
            drift_type_counts[drift_type] = drift_type_counts.get(drift_type, 0) + 1
        
        # Features les plus affectées
        all_affected_features = []
        for drift_event in model_drift_events:
            all_affected_features.extend(drift_event.affected_features)
        
        feature_counts = {}
        for feature in all_affected_features:
            feature_counts[feature] = feature_counts.get(feature, 0) + 1
        
        most_affected_features = sorted(
            feature_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Évolution de la magnitude de drift
        drift_timeline = [
            {
                'timestamp': d.timestamp.isoformat(),
                'drift_type': d.drift_type.value,
                'magnitude': d.drift_magnitude,
                'severity': d.severity.value,
                'affected_features_count': len(d.affected_features)
            }
            for d in sorted(model_drift_events, key=lambda x: x.timestamp)
        ]
        
        return {
            'model_id': model_id,
            'period_days': days,
            'drift_events': len(model_drift_events),
            'drift_type_distribution': drift_type_counts,
            'most_affected_features': most_affected_features,
            'average_drift_magnitude': np.mean([d.drift_magnitude for d in model_drift_events]),
            'max_drift_magnitude': np.max([d.drift_magnitude for d in model_drift_events]),
            'drift_timeline': drift_timeline,
            'recommendations': self._generate_drift_analysis_recommendations(model_drift_events)
        }
    
    def _generate_drift_analysis_recommendations(
        self, 
        drift_events: List[DriftDetectionResult]
    ) -> List[str]:
        """Génère des recommandations basées sur l'analyse de drift"""
        
        recommendations = []
        
        if not drift_events:
            return recommendations
        
        # Analyse de la fréquence
        severe_drifts = [d for d in drift_events if d.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]]
        
        if len(severe_drifts) > len(drift_events) * 0.3:
            recommendations.append("Drift sévère fréquent détecté - Ré-entraînement urgent recommandé")
            recommendations.append("Analyser les sources de données pour identifier les changements")
        
        # Analyse des features affectées
        all_features = []
        for drift_event in drift_events:
            all_features.extend(drift_event.affected_features)
        
        unique_features = set(all_features)
        if len(unique_features) > 10:
            recommendations.append("Nombreuses features affectées - Revoir l'architecture du modèle")
        
        # Analyse temporelle
        if len(drift_events) > 1:
            time_intervals = []
            for i in range(1, len(drift_events)):
                interval = (drift_events[i].timestamp - drift_events[i-1].timestamp).total_seconds() / 3600
                time_intervals.append(interval)
            
            avg_interval = np.mean(time_intervals)
            if avg_interval < 24:  # Moins de 24h entre les drifts
                recommendations.append("Drift très fréquent - Mettre en place un monitoring continu")
        
        return recommendations

# Factory pour la création du monitor
def create_model_performance_monitor(config: Dict[str, Any]) -> ModelPerformanceMonitor:
    """Factory pour créer un monitor de performance configuré"""
    return ModelPerformanceMonitor(config)

# Exemple d'utilisation
async def main() -> None:
    """Exemple d'utilisation du monitor de performance"""
    
    # Configuration
    config = {
        'drift_sensitivity': 0.05,
        'metrics_retention_days': 30,
        'alert_processing_interval': 60
    }
    
    # Création du monitor
    monitor = create_model_performance_monitor(config)
    
    try:
        # Démarrage
        await monitor.start()
        
        # Génération de données de test
        np.random.seed(42)
        
        # Données baseline
        baseline_features = np.random.normal(0, 1, (1000, 10))
        baseline_targets = np.random.choice([0, 1], size=1000)
        baseline_predictions = (baseline_features.sum(axis=1) > 0).astype(int)
        
        # Enregistrement du modèle
        monitor.register_model(
            model_id="test_classifier",
            model_type=ModelType.CLASSIFICATION,
            baseline_data={
                'features': baseline_features,
                'targets': baseline_targets,
                'predictions': baseline_predictions
            },
            metadata={'version': 'v1.0.0'}
        )
        
        # Ajout de règles d'alerte
        accuracy_rule = AlertRule(
            rule_id="accuracy_threshold",
            model_id="test_classifier",
            metric_type=MetricType.ACCURACY,
            threshold_type="absolute",
            threshold_value=0.85,
            comparison_operator="<",
            severity=AlertSeverity.HIGH
        )
        
        monitor.add_alert_rule(accuracy_rule)
        
        # Simulation de données avec drift
        for i in range(5):
            # Drift progressif dans les features
            drift_factor = i * 0.2
            current_features = np.random.normal(drift_factor, 1, (200, 10))
            current_targets = np.random.choice([0, 1], size=200)
            current_predictions = (current_features.sum(axis=1) > 0).astype(int)
            
            # Soumission des données
            await monitor.submit_inference_data(
                model_id="test_classifier",
                predictions=current_predictions,
                targets=current_targets,
                features=current_features,
                metadata={'batch': i}
            )
            
            await asyncio.sleep(2)
        
        # Attente pour le traitement
        await asyncio.sleep(10)
        
        # Affichage des résultats
        status = monitor.get_model_status("test_classifier")
        print(f"Statut modèle: {json.dumps(status, indent=2)}")
        
        global_status = monitor.get_global_status()
        print(f"Statut global: {json.dumps(global_status, indent=2)}")
        
        drift_analysis = monitor.get_drift_analysis("test_classifier", days=1)
        print(f"Analyse drift: {json.dumps(drift_analysis, indent=2)}")
        
    finally:
        # Arrêt
        await monitor.stop()

if __name__ == "__main__":
    asyncio.run(main())