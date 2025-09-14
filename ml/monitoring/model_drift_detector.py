"""🚀 Model Drift Detector - IA Influencer Agent Platform Enterprise
===================================================================
Module: backend/ml/monitoring/model_drift_detector.py
Author: Fahed Mlaiel (mlaiel@live.de)
===================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 DÉTECTEUR DE DRIFT DE MODÈLES
Détection statistique de drift des modèles ML
- Data drift detection avec tests statistiques
- Concept drift monitoring et alerte automatique
- Performance degradation tracking
- Adaptation triggers et retraining automation
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
import pickle
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import statistics
from scipy import stats
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

# Configuration
logger = logging.getLogger(__name__)

class DriftType(Enum):
    """Types de drift"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    PERFORMANCE_DRIFT = "performance_drift"
    FEATURE_DRIFT = "feature_drift"
    LABEL_DRIFT = "label_drift"

class DriftSeverity(Enum):
    """Sévérité du drift"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class StatisticalTest(Enum):
    """Tests statistiques"""
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    MANN_WHITNEY_U = "mann_whitney_u"
    CHI_SQUARE = "chi_square"
    CRAMERS_V = "cramers_v"
    POPULATION_STABILITY_INDEX = "psi"
    JENSEN_SHANNON_DIVERGENCE = "jensen_shannon"
    WASSERSTEIN_DISTANCE = "wasserstein"
    ANDERSON_DARLING = "anderson_darling"

class AdaptationAction(Enum):
    """Actions d'adaptation"""
    ALERT_ONLY = "alert_only"
    RETRAIN_MODEL = "retrain_model"
    UPDATE_FEATURES = "update_features"
    ADJUST_THRESHOLDS = "adjust_thresholds"
    SWITCH_MODEL = "switch_model"
    COLLECT_MORE_DATA = "collect_more_data"

@dataclass
class DriftDetectionConfig:
    """Configuration de détection de drift"""
    window_size: int = 1000
    reference_window_size: int = 5000
    detection_frequency_minutes: int = 30
    statistical_tests: List[StatisticalTest] = field(default_factory=lambda: [
        StatisticalTest.KOLMOGOROV_SMIRNOV,
        StatisticalTest.POPULATION_STABILITY_INDEX
    ])
    significance_level: float = 0.05
    min_samples_for_detection: int = 100
    feature_importance_threshold: float = 0.01
    performance_threshold: float = 0.05
    enable_concept_drift: bool = True
    enable_data_drift: bool = True
    enable_prediction_drift: bool = True
    adaptation_actions: List[AdaptationAction] = field(default_factory=lambda: [
        AdaptationAction.ALERT_ONLY
    ])

@dataclass
class DriftTestResult:
    """Résultat d'un test de drift"""
    test_name: StatisticalTest
    p_value: float
    statistic: float
    threshold: float
    is_drift_detected: bool
    confidence: float
    effect_size: Optional[float] = None
    interpretation: Optional[str] = None

@dataclass
class FeatureDriftResult:
    """Résultat de drift pour une feature"""
    feature_name: str
    drift_type: DriftType
    test_results: List[DriftTestResult]
    overall_drift_score: float
    is_drift_detected: bool
    severity: DriftSeverity
    recommendations: List[str] = field(default_factory=list)

@dataclass
class DriftDetectionResult:
    """Résultat global de détection de drift"""
    detection_id: str
    model_id: str
    timestamp: datetime
    drift_type: DriftType
    overall_drift_detected: bool
    severity: DriftSeverity
    affected_features: List[FeatureDriftResult]
    performance_metrics: Dict[str, float]
    adaptation_recommendations: List[AdaptationAction]
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReferenceDataset:
    """Dataset de référence"""
    data: pd.DataFrame
    labels: Optional[pd.Series]
    feature_statistics: Dict[str, Dict[str, float]]
    timestamp: datetime
    model_performance: Dict[str, float]
    feature_importance: Dict[str, float]

class ModelDriftDetector:
    """Détecteur de drift de modèles enterprise"""
    
    def __init__(self,
                 config -> None: DriftDetectionConfig,
                 enable_adaptive_thresholds -> None: bool = True,
                 enable_automatic_adaptation -> None: bool = False) -> None:
        
        self.config = config
        self.enable_adaptive_thresholds = enable_adaptive_thresholds
        self.enable_automatic_adaptation = enable_automatic_adaptation
        
        # Storage
        self.reference_datasets: Dict[str, ReferenceDataset] = {}
        self.current_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=config.window_size))
        self.detection_history: Dict[str, List[DriftDetectionResult]] = defaultdict(list)
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Models
        self.registered_models: Dict[str, BaseEstimator] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Adaptive thresholds
        self.adaptive_thresholds: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.threshold_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # State management
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Callbacks
        self.drift_callbacks: List[Callable[[DriftDetectionResult], None]] = []
        self.adaptation_callbacks: List[Callable[[str, AdaptationAction], None]] = []
        self.alert_callbacks: List[Callable[[DriftDetectionResult], None]] = []
        
        # Metrics
        self.detection_metrics = {
            "total_detections": 0,
            "drift_detections": 0,
            "false_positive_rate": 0.0,
            "detection_latency_avg": 0.0,
            "adaptation_actions_triggered": 0
        }
    
    async def start(self) -> None:
        """Démarre le détecteur de drift"""
        try:
            self.is_running = True
            logger.info("Démarrage détecteur de drift de modèles")
            
            # Démarrer les tâches de détection
            asyncio.create_task(self._detection_loop())
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._adaptation_loop())
            
            if self.enable_adaptive_thresholds:
                asyncio.create_task(self._threshold_adaptation_loop())
            
            logger.info("Détecteur de drift démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage détecteur de drift: {e}")
            raise
    
    async def stop(self) -> None:
        """Arrête le détecteur de drift"""
        try:
            logger.info("Arrêt détecteur de drift...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            logger.info("Détecteur de drift arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt détecteur de drift: {e}")
    
    async def register_model(self,
                           model_id: str,
                           model: BaseEstimator,
                           reference_data: pd.DataFrame,
                           reference_labels: Optional[pd.Series] = None,
                           feature_importance: Optional[Dict[str, float]] = None) -> bool:
        """Enregistre un modèle pour la détection de drift"""
        
        try:
            # Valider les données de référence
            if len(reference_data) < self.config.min_samples_for_detection:
                raise ValueError(f"Données de référence insuffisantes: {len(reference_data)} < {self.config.min_samples_for_detection}")
            
            # Calculer les statistiques de référence
            feature_stats = self._calculate_feature_statistics(reference_data)
            
            # Calculer les performances de référence si possible
            reference_performance = {}
            if reference_labels is not None and hasattr(model, 'predict'):
                predictions = model.predict(reference_data)
                reference_performance = self._calculate_performance_metrics(reference_labels, predictions)
            
            # Obtenir l'importance des features
            if feature_importance is None:
                feature_importance = self._extract_feature_importance(model, reference_data)
            
            # Créer le dataset de référence
            reference_dataset = ReferenceDataset(
                data=reference_data.copy(),
                labels=reference_labels.copy() if reference_labels is not None else None,
                feature_statistics=feature_stats,
                timestamp=datetime.now(),
                model_performance=reference_performance,
                feature_importance=feature_importance
            )
            
            # Enregistrer
            self.registered_models[model_id] = model
            self.reference_datasets[model_id] = reference_dataset
            self.model_metadata[model_id] = {
                "registered_at": datetime.now(),
                "feature_count": len(reference_data.columns),
                "reference_samples": len(reference_data),
                "has_labels": reference_labels is not None
            }
            
            logger.info(f"Modèle {model_id} enregistré pour détection de drift")
            return True
            
        except Exception as e:
            logger.error(f"Erreur enregistrement modèle {model_id}: {e}")
            return False
    
    async def feed_data(self,
                       model_id: str,
                       data: pd.DataFrame,
                       labels: Optional[pd.Series] = None,
                       predictions: Optional[pd.Series] = None) -> bool:
        """Alimente le détecteur avec de nouvelles données"""
        
        try:
            if model_id not in self.registered_models:
                raise ValueError(f"Modèle {model_id} non enregistré")
            
            # Ajouter aux fenêtres courantes
            timestamp = datetime.now()
            
            for idx, row in data.iterrows():
                sample = {
                    "timestamp": timestamp,
                    "data": row,
                    "label": labels.iloc[idx] if labels is not None else None,
                    "prediction": predictions.iloc[idx] if predictions is not None else None
                }
                self.current_windows[model_id].append(sample)
            
            # Calculer les performances si possible
            if labels is not None and predictions is not None:
                performance = self._calculate_performance_metrics(labels, predictions)
                self.performance_history[model_id].append({
                    "timestamp": timestamp,
                    "performance": performance
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur alimentation données {model_id}: {e}")
            return False
    
    async def detect_drift(self, model_id: str) -> Optional[DriftDetectionResult]:
        """Détecte le drift pour un modèle"""
        
        try:
            if model_id not in self.registered_models:
                raise ValueError(f"Modèle {model_id} non enregistré")
            
            if len(self.current_windows[model_id]) < self.config.min_samples_for_detection:
                logger.debug(f"Données insuffisantes pour {model_id}: {len(self.current_windows[model_id])}")
                return None
            
            detection_start = time.time()
            
            # Préparer les données
            current_data = self._extract_current_data(model_id)
            reference_data = self.reference_datasets[model_id].data
            
            # Résultats de détection
            feature_drift_results = []
            overall_drift_detected = False
            max_severity = DriftSeverity.LOW
            adaptation_recommendations = []
            
            # Détection de data drift
            if self.config.enable_data_drift:
                data_drift_results = await self._detect_data_drift(
                    model_id, reference_data, current_data
                )
                feature_drift_results.extend(data_drift_results)
            
            # Détection de concept drift
            if self.config.enable_concept_drift:
                concept_drift_result = await self._detect_concept_drift(model_id)
                if concept_drift_result:
                    feature_drift_results.append(concept_drift_result)
            
            # Détection de prediction drift
            if self.config.enable_prediction_drift:
                prediction_drift_result = await self._detect_prediction_drift(model_id)
                if prediction_drift_result:
                    feature_drift_results.append(prediction_drift_result)
            
            # Analyser les résultats globaux
            if feature_drift_results:
                drift_scores = [result.overall_drift_score for result in feature_drift_results]
                overall_drift_detected = any(result.is_drift_detected for result in feature_drift_results)
                
                # Déterminer la sévérité globale
                severities = [result.severity for result in feature_drift_results if result.is_drift_detected]
                if severities:
                    severity_values = {
                        DriftSeverity.LOW: 1,
                        DriftSeverity.MEDIUM: 2,
                        DriftSeverity.HIGH: 3,
                        DriftSeverity.CRITICAL: 4
                    }
                    max_severity_value = max(severity_values[s] for s in severities)
                    max_severity = [k for k, v in severity_values.items() if v == max_severity_value][0]
                
                # Générer des recommandations d'adaptation
                adaptation_recommendations = self._generate_adaptation_recommendations(
                    feature_drift_results, max_severity
                )
            
            # Calculer les métriques de performance actuelles
            current_performance = {}
            if self.performance_history[model_id]:
                recent_performance = list(self.performance_history[model_id])[-10:]  # 10 dernières
                current_performance = self._aggregate_performance_metrics(recent_performance)
            
            # Créer le résultat
            detection_result = DriftDetectionResult(
                detection_id=str(uuid.uuid4()),
                model_id=model_id,
                timestamp=datetime.now(),
                drift_type=DriftType.DATA_DRIFT,  # Type principal détecté
                overall_drift_detected=overall_drift_detected,
                severity=max_severity,
                affected_features=feature_drift_results,
                performance_metrics=current_performance,
                adaptation_recommendations=adaptation_recommendations,
                confidence_score=np.mean(drift_scores) if drift_scores else 0.0,
                metadata={
                    "detection_time_ms": (time.time() - detection_start) * 1000,
                    "samples_analyzed": len(current_data),
                    "reference_samples": len(reference_data)
                }
            )
            
            # Enregistrer dans l'historique
            self.detection_history[model_id].append(detection_result)
            
            # Mettre à jour les métriques
            self.detection_metrics["total_detections"] += 1
            if overall_drift_detected:
                self.detection_metrics["drift_detections"] += 1
            
            detection_latency = (time.time() - detection_start) * 1000
            avg_latency = self.detection_metrics["detection_latency_avg"]
            total_detections = self.detection_metrics["total_detections"]
            self.detection_metrics["detection_latency_avg"] = (
                (avg_latency * (total_detections - 1) + detection_latency) / total_detections
            )
            
            # Appeler les callbacks
            for callback in self.drift_callbacks:
                try:
                    await callback(detection_result)
                except Exception as e:
                    logger.error(f"Erreur callback drift: {e}")
            
            if overall_drift_detected:
                for callback in self.alert_callbacks:
                    try:
                        await callback(detection_result)
                    except Exception as e:
                        logger.error(f"Erreur callback alerte: {e}")
            
            logger.info(f"Détection drift {model_id}: {'DRIFT' if overall_drift_detected else 'OK'} "
                       f"(sévérité: {max_severity.value}, features affectées: {len([r for r in feature_drift_results if r.is_drift_detected])})")
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Erreur détection drift {model_id}: {e}")
            return None
    
    def _extract_current_data(self, model_id: str) -> pd.DataFrame:
        """Extrait les données courantes de la fenêtre"""
        samples = list(self.current_windows[model_id])
        data_rows = [sample["data"] for sample in samples]
        return pd.DataFrame(data_rows)
    
    def _calculate_feature_statistics(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calcule les statistiques des features"""
        stats_dict = {}
        
        for column in data.columns:
            column_data = data[column]
            
            if pd.api.types.is_numeric_dtype(column_data):
                # Statistiques numériques
                stats_dict[column] = {
                    "mean": float(column_data.mean()),
                    "std": float(column_data.std()),
                    "min": float(column_data.min()),
                    "max": float(column_data.max()),
                    "median": float(column_data.median()),
                    "q25": float(column_data.quantile(0.25)),
                    "q75": float(column_data.quantile(0.75)),
                    "skewness": float(column_data.skew()),
                    "kurtosis": float(column_data.kurtosis())
                }
            else:
                # Statistiques catégorielles
                value_counts = column_data.value_counts()
                stats_dict[column] = {
                    "unique_count": int(column_data.nunique()),
                    "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else "",
                    "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    "entropy": float(-np.sum((value_counts / len(column_data)) * np.log2(value_counts / len(column_data) + 1e-8)))
                }
        
        return stats_dict
    
    def _calculate_performance_metrics(self, y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
        """Calcule les métriques de performance"""
        try:
            # Déterminer si c'est de la classification ou régression
            unique_true = y_true.nunique()
            unique_pred = y_pred.nunique()
            
            if unique_true <= 10 and unique_pred <= 10:  # Classification
                return {
                    "accuracy": float(accuracy_score(y_true, y_pred)),
                    "precision": float(precision_score(y_true, y_pred, average='weighted')),
                    "recall": float(recall_score(y_true, y_pred, average='weighted')),
                    "f1": float(f1_score(y_true, y_pred, average='weighted'))
                }
            else:  # Régression
                mse = np.mean((y_true - y_pred) ** 2)
                rmse = np.sqrt(mse)
                mae = np.mean(np.abs(y_true - y_pred))
                
                return {
                    "mse": float(mse),
                    "rmse": float(rmse),
                    "mae": float(mae),
                    "r2": float(1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - y_true.mean()) ** 2))
                }
        except Exception as e:
            logger.error(f"Erreur calcul métriques performance: {e}")
            return {}
    
    def _extract_feature_importance(self, model: BaseEstimator, data: pd.DataFrame) -> Dict[str, float]:
        """Extrait l'importance des features"""
        try:
            if hasattr(model, 'feature_importances_'):
                return dict(zip(data.columns, model.feature_importances_))
            elif hasattr(model, 'coef_'):
                return dict(zip(data.columns, np.abs(model.coef_).flatten()))
            else:
                # Importance uniforme par défaut
                return {col: 1.0 / len(data.columns) for col in data.columns}
        except Exception as e:
            logger.error(f"Erreur extraction importance features: {e}")
            return {col: 1.0 / len(data.columns) for col in data.columns}
    
    async def _detect_data_drift(self,
                               model_id: str,
                               reference_data: pd.DataFrame,
                               current_data: pd.DataFrame) -> List[FeatureDriftResult]:
        """Détecte le drift des données"""
        
        results = []
        feature_importance = self.reference_datasets[model_id].feature_importance
        
        for column in reference_data.columns:
            if column not in current_data.columns:
                continue
            
            # Importance de la feature
            importance = feature_importance.get(column, 0.0)
            if importance < self.config.feature_importance_threshold:
                continue  # Skip features peu importantes
            
            ref_values = reference_data[column].dropna()
            current_values = current_data[column].dropna()
            
            if len(ref_values) == 0 or len(current_values) == 0:
                continue
            
            # Effectuer les tests statistiques
            test_results = []
            
            for test_type in self.config.statistical_tests:
                test_result = await self._perform_statistical_test(
                    test_type, ref_values, current_values, column
                )
                if test_result:
                    test_results.append(test_result)
            
            # Analyser les résultats
            if test_results:
                drift_scores = [1 - r.p_value for r in test_results if r.p_value is not None]
                overall_drift_score = np.mean(drift_scores) if drift_scores else 0.0
                
                # Déterminer si drift détecté
                significant_tests = [r for r in test_results if r.is_drift_detected]
                is_drift_detected = len(significant_tests) >= len(test_results) // 2
                
                # Déterminer la sévérité
                severity = self._determine_severity(overall_drift_score, importance)
                
                # Générer des recommandations
                recommendations = self._generate_feature_recommendations(
                    column, test_results, is_drift_detected, severity
                )
                
                result = FeatureDriftResult(
                    feature_name=column,
                    drift_type=DriftType.FEATURE_DRIFT,
                    test_results=test_results,
                    overall_drift_score=overall_drift_score,
                    is_drift_detected=is_drift_detected,
                    severity=severity,
                    recommendations=recommendations
                )
                
                results.append(result)
        
        return results
    
    async def _perform_statistical_test(self,
                                      test_type: StatisticalTest,
                                      reference: pd.Series,
                                      current: pd.Series,
                                      feature_name: str) -> Optional[DriftTestResult]:
        """Effectue un test statistique"""
        
        try:
            if test_type == StatisticalTest.KOLMOGOROV_SMIRNOV:
                return await self._ks_test(reference, current, feature_name)
            elif test_type == StatisticalTest.MANN_WHITNEY_U:
                return await self._mann_whitney_test(reference, current, feature_name)
            elif test_type == StatisticalTest.CHI_SQUARE:
                return await self._chi_square_test(reference, current, feature_name)
            elif test_type == StatisticalTest.POPULATION_STABILITY_INDEX:
                return await self._psi_test(reference, current, feature_name)
            elif test_type == StatisticalTest.JENSEN_SHANNON_DIVERGENCE:
                return await self._jensen_shannon_test(reference, current, feature_name)
            elif test_type == StatisticalTest.WASSERSTEIN_DISTANCE:
                return await self._wasserstein_test(reference, current, feature_name)
            else:
                logger.warning(f"Test statistique non implémenté: {test_type}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur test statistique {test_type} pour {feature_name}: {e}")
            return None
    
    async def _ks_test(self, reference: pd.Series, current: pd.Series, feature_name: str) -> DriftTestResult:
        """Test de Kolmogorov-Smirnov"""
        try:
            if pd.api.types.is_numeric_dtype(reference) and pd.api.types.is_numeric_dtype(current):
                statistic, p_value = stats.ks_2samp(reference, current)
                
                return DriftTestResult(
                    test_name=StatisticalTest.KOLMOGOROV_SMIRNOV,
                    p_value=p_value,
                    statistic=statistic,
                    threshold=self.config.significance_level,
                    is_drift_detected=p_value < self.config.significance_level,
                    confidence=1 - p_value,
                    interpretation=f"KS statistic: {statistic:.4f}, p-value: {p_value:.4f}"
                )
            else:
                return None
        except Exception as e:
            logger.error(f"Erreur test KS: {e}")
            return None
    
    async def _mann_whitney_test(self, reference: pd.Series, current: pd.Series, feature_name: str) -> DriftTestResult:
        """Test de Mann-Whitney U"""
        try:
            if pd.api.types.is_numeric_dtype(reference) and pd.api.types.is_numeric_dtype(current):
                statistic, p_value = stats.mannwhitneyu(reference, current, alternative='two-sided')
                
                return DriftTestResult(
                    test_name=StatisticalTest.MANN_WHITNEY_U,
                    p_value=p_value,
                    statistic=statistic,
                    threshold=self.config.significance_level,
                    is_drift_detected=p_value < self.config.significance_level,
                    confidence=1 - p_value,
                    interpretation=f"Mann-Whitney U statistic: {statistic:.4f}, p-value: {p_value:.4f}"
                )
            else:
                return None
        except Exception as e:
            logger.error(f"Erreur test Mann-Whitney: {e}")
            return None
    
    async def _chi_square_test(self, reference: pd.Series, current: pd.Series, feature_name: str) -> DriftTestResult:
        """Test du Chi-carré pour variables catégorielles"""
        try:
            if not pd.api.types.is_numeric_dtype(reference):
                # Créer une table de contingence
                ref_counts = reference.value_counts()
                curr_counts = current.value_counts()
                
                # Aligner les catégories
                all_categories = set(ref_counts.index) | set(curr_counts.index)
                
                ref_aligned = [ref_counts.get(cat, 0) for cat in all_categories]
                curr_aligned = [curr_counts.get(cat, 0) for cat in all_categories]
                
                if sum(ref_aligned) > 0 and sum(curr_aligned) > 0:
                    statistic, p_value = stats.chisquare(curr_aligned, ref_aligned)
                    
                    return DriftTestResult(
                        test_name=StatisticalTest.CHI_SQUARE,
                        p_value=p_value,
                        statistic=statistic,
                        threshold=self.config.significance_level,
                        is_drift_detected=p_value < self.config.significance_level,
                        confidence=1 - p_value,
                        interpretation=f"Chi-square statistic: {statistic:.4f}, p-value: {p_value:.4f}"
                    )
            return None
        except Exception as e:
            logger.error(f"Erreur test Chi-carré: {e}")
            return None
    
    async def _psi_test(self, reference: pd.Series, current: pd.Series, feature_name: str) -> DriftTestResult:
        """Population Stability Index"""
        try:
            if pd.api.types.is_numeric_dtype(reference) and pd.api.types.is_numeric_dtype(current):
                # Créer des bins basés sur les quantiles de référence
                n_bins = min(10, len(reference.unique()))
                bins = np.quantile(reference, np.linspace(0, 1, n_bins + 1))
                bins = np.unique(bins)  # Supprimer les doublons
                
                if len(bins) > 1:
                    ref_hist, _ = np.histogram(reference, bins=bins)
                    curr_hist, _ = np.histogram(current, bins=bins)
                    
                    # Éviter les divisions par zéro
                    ref_prop = (ref_hist + 1e-8) / (np.sum(ref_hist) + 1e-8 * len(ref_hist))
                    curr_prop = (curr_hist + 1e-8) / (np.sum(curr_hist) + 1e-8 * len(curr_hist))
                    
                    # Calculer PSI
                    psi = np.sum((curr_prop - ref_prop) * np.log(curr_prop / ref_prop))
                    
                    # Seuils PSI standards
                    is_drift = psi > 0.1  # Seuil couramment utilisé
                    
                    return DriftTestResult(
                        test_name=StatisticalTest.POPULATION_STABILITY_INDEX,
                        p_value=None,  # PSI n'a pas de p-value
                        statistic=psi,
                        threshold=0.1,
                        is_drift_detected=is_drift,
                        confidence=min(psi / 0.25, 1.0),  # Normaliser à [0,1]
                        interpretation=f"PSI: {psi:.4f} ({'STABLE' if psi < 0.1 else 'DRIFT'})"
                    )
            return None
        except Exception as e:
            logger.error(f"Erreur test PSI: {e}")
            return None
    
    async def _jensen_shannon_test(self, reference: pd.Series, current: pd.Series, feature_name: str) -> DriftTestResult:
        """Divergence de Jensen-Shannon"""
        try:
            # Créer des histogrammes
            if pd.api.types.is_numeric_dtype(reference):
                bins = np.histogram_bin_edges(np.concatenate([reference, current]), bins='auto')
                ref_hist, _ = np.histogram(reference, bins=bins, density=True)
                curr_hist, _ = np.histogram(current, bins=bins, density=True)
            else:
                # Pour les variables catégorielles
                all_values = set(reference) | set(current)
                ref_hist = np.array([np.sum(reference == val) for val in all_values])
                curr_hist = np.array([np.sum(current == val) for val in all_values])
                
                ref_hist = ref_hist / np.sum(ref_hist)
                curr_hist = curr_hist / np.sum(curr_hist)
            
            # Éviter les zéros
            ref_hist = ref_hist + 1e-8
            curr_hist = curr_hist + 1e-8
            
            # Normaliser
            ref_hist = ref_hist / np.sum(ref_hist)
            curr_hist = curr_hist / np.sum(curr_hist)
            
            # Calculer JS divergence
            m = (ref_hist + curr_hist) / 2
            js_div = (
                np.sum(ref_hist * np.log(ref_hist / m)) +
                np.sum(curr_hist * np.log(curr_hist / m))
            ) / 2
            
            # JS distance (racine de la divergence)
            js_distance = np.sqrt(js_div)
            
            # Seuil empirique
            threshold = 0.1
            is_drift = js_distance > threshold
            
            return DriftTestResult(
                test_name=StatisticalTest.JENSEN_SHANNON_DIVERGENCE,
                p_value=None,
                statistic=js_distance,
                threshold=threshold,
                is_drift_detected=is_drift,
                confidence=min(js_distance / 0.5, 1.0),
                interpretation=f"JS distance: {js_distance:.4f}"
            )
            
        except Exception as e:
            logger.error(f"Erreur test Jensen-Shannon: {e}")
            return None
    
    async def _wasserstein_test(self, reference: pd.Series, current: pd.Series, feature_name: str) -> DriftTestResult:
        """Distance de Wasserstein (Earth Mover's Distance)"""
        try:
            if pd.api.types.is_numeric_dtype(reference) and pd.api.types.is_numeric_dtype(current):
                distance = stats.wasserstein_distance(reference, current)
                
                # Normaliser par la plage des données
                data_range = max(reference.max(), current.max()) - min(reference.min(), current.min())
                normalized_distance = distance / (data_range + 1e-8)
                
                threshold = 0.1  # Seuil empirique
                is_drift = normalized_distance > threshold
                
                return DriftTestResult(
                    test_name=StatisticalTest.WASSERSTEIN_DISTANCE,
                    p_value=None,
                    statistic=normalized_distance,
                    threshold=threshold,
                    is_drift_detected=is_drift,
                    confidence=min(normalized_distance / 0.5, 1.0),
                    interpretation=f"Wasserstein distance: {distance:.4f} (normalized: {normalized_distance:.4f})"
                )
            return None
        except Exception as e:
            logger.error(f"Erreur test Wasserstein: {e}")
            return None
    
    async def _detect_concept_drift(self, model_id: str) -> Optional[FeatureDriftResult]:
        """Détecte le concept drift"""
        try:
            if len(self.performance_history[model_id]) < 10:
                return None
            
            # Analyser la dégradation des performances
            recent_performance = list(self.performance_history[model_id])[-10:]
            reference_performance = self.reference_datasets[model_id].model_performance
            
            if not reference_performance or not recent_performance:
                return None
            
            # Calculer la dégradation moyenne
            degradation_scores = []
            
            for perf_record in recent_performance:
                current_metrics = perf_record["performance"]
                
                for metric_name, reference_value in reference_performance.items():
                    if metric_name in current_metrics:
                        current_value = current_metrics[metric_name]
                        
                        # Calculer la dégradation (plus c'est haut, moins bon pour la plupart des métriques)
                        if metric_name in ["accuracy", "precision", "recall", "f1", "r2"]:
                            degradation = max(0, reference_value - current_value)
                        else:  # mse, rmse, mae
                            degradation = max(0, current_value - reference_value)
                        
                        degradation_scores.append(degradation)
            
            if degradation_scores:
                avg_degradation = np.mean(degradation_scores)
                is_drift = avg_degradation > self.config.performance_threshold
                
                severity = DriftSeverity.LOW
                if avg_degradation > 0.15:
                    severity = DriftSeverity.CRITICAL
                elif avg_degradation > 0.10:
                    severity = DriftSeverity.HIGH
                elif avg_degradation > 0.05:
                    severity = DriftSeverity.MEDIUM
                
                return FeatureDriftResult(
                    feature_name="model_performance",
                    drift_type=DriftType.CONCEPT_DRIFT,
                    test_results=[],
                    overall_drift_score=avg_degradation,
                    is_drift_detected=is_drift,
                    severity=severity,
                    recommendations=[
                        "Analyser les changements dans les patterns de données",
                        "Considérer un re-entraînement du modèle",
                        "Vérifier la qualité des données d'entrée",
                        "Évaluer si les features sont toujours pertinentes"
                    ]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détection concept drift: {e}")
            return None
    
    async def _detect_prediction_drift(self, model_id: str) -> Optional[FeatureDriftResult]:
        """Détecte le drift des prédictions"""
        try:
            # Récupérer les prédictions récentes
            recent_samples = list(self.current_windows[model_id])
            recent_predictions = [s["prediction"] for s in recent_samples if s["prediction"] is not None]
            
            if len(recent_predictions) < self.config.min_samples_for_detection:
                return None
            
            # Obtenir les prédictions de référence (simulation)
            reference_model = self.registered_models[model_id]
            reference_data = self.reference_datasets[model_id].data
            
            if hasattr(reference_model, 'predict'):
                reference_predictions = reference_model.predict(reference_data.sample(min(1000, len(reference_data))))
                
                # Comparer les distributions de prédictions
                ref_series = pd.Series(reference_predictions)
                curr_series = pd.Series(recent_predictions)
                
                # Utiliser le test KS pour les prédictions numériques
                if pd.api.types.is_numeric_dtype(ref_series):
                    statistic, p_value = stats.ks_2samp(ref_series, curr_series)
                    
                    is_drift = p_value < self.config.significance_level
                    drift_score = 1 - p_value
                    
                    severity = DriftSeverity.LOW
                    if drift_score > 0.95:
                        severity = DriftSeverity.CRITICAL
                    elif drift_score > 0.9:
                        severity = DriftSeverity.HIGH
                    elif drift_score > 0.8:
                        severity = DriftSeverity.MEDIUM
                    
                    return FeatureDriftResult(
                        feature_name="model_predictions",
                        drift_type=DriftType.PREDICTION_DRIFT,
                        test_results=[
                            DriftTestResult(
                                test_name=StatisticalTest.KOLMOGOROV_SMIRNOV,
                                p_value=p_value,
                                statistic=statistic,
                                threshold=self.config.significance_level,
                                is_drift_detected=is_drift,
                                confidence=drift_score,
                                interpretation=f"Prediction distribution drift: KS={statistic:.4f}, p={p_value:.4f}"
                            )
                        ],
                        overall_drift_score=drift_score,
                        is_drift_detected=is_drift,
                        severity=severity,
                        recommendations=[
                            "Analyser les changements dans la distribution des prédictions",
                            "Vérifier la calibration du modèle",
                            "Considérer un recalibrage ou re-entraînement"
                        ]
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détection prediction drift: {e}")
            return None
    
    def _determine_severity(self, drift_score: float, feature_importance: float) -> DriftSeverity:
        """Détermine la sévérité du drift"""
        # Pondérer par l'importance de la feature
        weighted_score = drift_score * (1 + feature_importance)
        
        if weighted_score > 0.9:
            return DriftSeverity.CRITICAL
        elif weighted_score > 0.7:
            return DriftSeverity.HIGH
        elif weighted_score > 0.5:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW
    
    def _generate_feature_recommendations(self,
                                        feature_name: str,
                                        test_results: List[DriftTestResult],
                                        is_drift: bool,
                                        severity: DriftSeverity) -> List[str]:
        """Génère des recommandations pour une feature"""
        recommendations = []
        
        if is_drift:
            recommendations.append(f"Drift détecté sur la feature '{feature_name}'")
            
            if severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
                recommendations.extend([
                    "Action immédiate requise",
                    "Analyser la source des changements de données",
                    "Considérer un re-entraînement du modèle"
                ])
            else:
                recommendations.extend([
                    "Surveiller de près l'évolution",
                    "Analyser les causes potentielles"
                ])
        else:
            recommendations.append(f"Feature '{feature_name}' stable")
        
        return recommendations
    
    def _generate_adaptation_recommendations(self,
                                          feature_results: List[FeatureDriftResult],
                                          max_severity: DriftSeverity) -> List[AdaptationAction]:
        """Génère des recommandations d'adaptation"""
        recommendations = []
        
        drift_count = len([r for r in feature_results if r.is_drift_detected])
        total_features = len(feature_results)
        
        if drift_count == 0:
            recommendations.append(AdaptationAction.ALERT_ONLY)
        elif max_severity == DriftSeverity.CRITICAL or drift_count / total_features > 0.5:
            recommendations.extend([
                AdaptationAction.RETRAIN_MODEL,
                AdaptationAction.COLLECT_MORE_DATA
            ])
        elif max_severity == DriftSeverity.HIGH:
            recommendations.extend([
                AdaptationAction.UPDATE_FEATURES,
                AdaptationAction.ADJUST_THRESHOLDS
            ])
        else:
            recommendations.extend([
                AdaptationAction.ALERT_ONLY,
                AdaptationAction.ADJUST_THRESHOLDS
            ])
        
        return recommendations
    
    def _aggregate_performance_metrics(self, performance_records: List[Dict]) -> Dict[str, float]:
        """Agrège les métriques de performance"""
        if not performance_records:
            return {}
        
        # Collecter toutes les métriques
        all_metrics = defaultdict(list)
        for record in performance_records:
            for metric, value in record["performance"].items():
                all_metrics[metric].append(value)
        
        # Calculer les moyennes
        return {metric: np.mean(values) for metric, values in all_metrics.items()}
    
    # Boucles de traitement
    
    async def _detection_loop(self) -> None:
        """Boucle de détection périodique"""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.detection_frequency_minutes * 60)
                
                # Effectuer la détection pour tous les modèles
                for model_id in self.registered_models.keys():
                    try:
                        result = await self.detect_drift(model_id)
                        if result:
                            logger.debug(f"Détection effectuée pour {model_id}")
                    except Exception as e:
                        logger.error(f"Erreur détection périodique {model_id}: {e}")
                
            except Exception as e:
                logger.error(f"Erreur boucle détection: {e}")
    
    async def _monitoring_loop(self) -> None:
        """Boucle de monitoring"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                # Log des métriques
                logger.info(
                    f"Drift detection metrics - "
                    f"Total: {self.detection_metrics['total_detections']}, "
                    f"Drift detected: {self.detection_metrics['drift_detections']}, "
                    f"Detection rate: {self.detection_metrics['drift_detections'] / max(self.detection_metrics['total_detections'], 1):.2%}, "
                    f"Avg latency: {self.detection_metrics['detection_latency_avg']:.2f}ms"
                )
                
            except Exception as e:
                logger.error(f"Erreur boucle monitoring: {e}")
    
    async def _adaptation_loop(self) -> None:
        """Boucle d'adaptation automatique"""
        if not self.enable_automatic_adaptation:
            return
        
        while self.is_running:
            try:
                await asyncio.sleep(600)  # 10 minutes
                
                # Analyser les recommandations d'adaptation
                for model_id in self.registered_models.keys():
                    recent_detections = [
                        d for d in self.detection_history[model_id]
                        if d.timestamp > datetime.now() - timedelta(hours=1)
                    ]
                    
                    # Déclencher des actions si nécessaire
                    for detection in recent_detections:
                        if detection.overall_drift_detected:
                            for action in detection.adaptation_recommendations:
                                if action != AdaptationAction.ALERT_ONLY:
                                    await self._trigger_adaptation_action(model_id, action)
                
            except Exception as e:
                logger.error(f"Erreur boucle adaptation: {e}")
    
    async def _threshold_adaptation_loop(self) -> None:
        """Boucle d'adaptation des seuils"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # 1 heure
                
                # Adapter les seuils basés sur l'historique
                for model_id in self.registered_models.keys():
                    await self._adapt_thresholds(model_id)
                
            except Exception as e:
                logger.error(f"Erreur adaptation seuils: {e}")
    
    async def _trigger_adaptation_action(self, model_id -> None: str, action -> None: AdaptationAction) -> None:
        """Déclenche une action d'adaptation"""
        try:
            logger.info(f"Déclenchement action d'adaptation {action.value} pour {model_id}")
            
            self.detection_metrics["adaptation_actions_triggered"] += 1
            
            # Appeler les callbacks d'adaptation
            for callback in self.adaptation_callbacks:
                try:
                    await callback(model_id, action)
                except Exception as e:
                    logger.error(f"Erreur callback adaptation: {e}")
            
        except Exception as e:
            logger.error(f"Erreur déclenchement action adaptation: {e}")
    
    async def _adapt_thresholds(self, model_id -> None: str) -> None:
        """Adapte les seuils de détection"""
        try:
            # Analyser l'historique des détections
            recent_detections = [
                d for d in self.detection_history[model_id]
                if d.timestamp > datetime.now() - timedelta(days=7)
            ]
            
            if len(recent_detections) < 10:
                return
            
            # Calculer les taux de faux positifs estimés
            # (implémentation simplifiée)
            
            # Adapter les seuils si nécessaire
            # (implémentation à compléter selon les besoins spécifiques)
            
        except Exception as e:
            logger.error(f"Erreur adaptation seuils {model_id}: {e}")
    
    # API publique
    
    def get_detection_history(self, model_id: str) -> List[DriftDetectionResult]:
        """Récupère l'historique des détections"""
        return self.detection_history.get(model_id, [])
    
    def get_detection_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de détection"""
        return self.detection_metrics.copy()
    
    def add_drift_callback(self, callback -> None: Callable[[DriftDetectionResult], None]) -> None:
        """Ajoute un callback de drift"""
        self.drift_callbacks.append(callback)
    
    def add_adaptation_callback(self, callback -> None: Callable[[str, AdaptationAction], None]) -> None:
        """Ajoute un callback d'adaptation"""
        self.adaptation_callbacks.append(callback)
    
    def add_alert_callback(self, callback -> None: Callable[[DriftDetectionResult], None]) -> None:
        """Ajoute un callback d'alerte"""
        self.alert_callbacks.append(callback)
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "registered_models": len(self.registered_models),
            "detection_metrics": self.detection_metrics,
            "adaptive_thresholds_enabled": self.enable_adaptive_thresholds,
            "automatic_adaptation_enabled": self.enable_automatic_adaptation
        }


# Exemple d'utilisation
async def example_usage() -> None:
    """Exemple d'utilisation du détecteur de drift"""
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    import numpy as np
    
    # Créer des données d'exemple
    X, y = make_classification(n_samples=2000, n_features=10, random_state=42)
    
    # Diviser en référence et données courantes
    X_ref, X_current, y_ref, y_current = train_test_split(X, y, test_size=0.5, random_state=42)
    
    # Entraîner un modèle
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_ref, y_ref)
    
    # Configuration de détection
    config = DriftDetectionConfig(
        window_size=500,
        detection_frequency_minutes=1,  # Fréquence élevée pour la démo
        statistical_tests=[
            StatisticalTest.KOLMOGOROV_SMIRNOV,
            StatisticalTest.POPULATION_STABILITY_INDEX
        ]
    )
    
    # Créer le détecteur
    detector = ModelDriftDetector(config, enable_automatic_adaptation=True)
    
    # Callbacks
    async def drift_callback(result -> None: DriftDetectionResult) -> None:
        print(f"Drift détecté: {result.model_id} - Sévérité: {result.severity.value}")
        print(f"Features affectées: {len([f for f in result.affected_features if f.is_drift_detected])}")
    
    async def adaptation_callback(model_id -> None: str, action -> None: AdaptationAction) -> None:
        print(f"Action d'adaptation: {action.value} pour {model_id}")
    
    detector.add_drift_callback(drift_callback)
    detector.add_adaptation_callback(adaptation_callback)
    
    try:
        await detector.start()
        
        # Enregistrer le modèle
        df_ref = pd.DataFrame(X_ref, columns=[f"feature_{i}" for i in range(X_ref.shape[1])])
        df_current = pd.DataFrame(X_current, columns=[f"feature_{i}" for i in range(X_current.shape[1])])
        
        success = await detector.register_model(
            "test_classifier",
            model,
            df_ref,
            pd.Series(y_ref)
        )
        
        if success:
            print("Modèle enregistré avec succès")
            
            # Faire des prédictions sur les données courantes
            predictions = model.predict(X_current)
            
            # Alimenter avec des données normales
            print("Alimentation avec données normales...")
            await detector.feed_data(
                "test_classifier",
                df_current[:200],
                pd.Series(y_current[:200]),
                pd.Series(predictions[:200])
            )
            
            # Première détection
            result1 = await detector.detect_drift("test_classifier")
            if result1:
                print(f"Détection 1: {'DRIFT' if result1.overall_drift_detected else 'OK'}")
            
            # Introduire du drift artificiel
            print("Introduction de drift artificiel...")
            X_drift = X_current[200:400].copy()
            X_drift[:, 0] += 2  # Shift sur la première feature
            X_drift[:, 1] *= 1.5  # Scale sur la deuxième feature
            
            df_drift = pd.DataFrame(X_drift, columns=[f"feature_{i}" for i in range(X_drift.shape[1])])
            predictions_drift = model.predict(X_drift)
            
            await detector.feed_data(
                "test_classifier",
                df_drift,
                pd.Series(y_current[200:400]),
                pd.Series(predictions_drift)
            )
            
            # Seconde détection
            result2 = await detector.detect_drift("test_classifier")
            if result2:
                print(f"Détection 2: {'DRIFT' if result2.overall_drift_detected else 'OK'}")
                if result2.overall_drift_detected:
                    print(f"Recommandations: {[a.value for a in result2.adaptation_recommendations]}")
            
            # Attendre un cycle de détection automatique
            await asyncio.sleep(70)  # Laisser le temps à la détection automatique
            
            # Afficher les métriques
            metrics = detector.get_detection_metrics()
            print(f"Métriques de détection: {metrics}")
            
            # Historique
            history = detector.get_detection_history("test_classifier")
            print(f"Historique: {len(history)} détections")
            
            # Santé
            health = await detector.health_check()
            print(f"Santé: {health}")
        
    finally:
        await detector.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())