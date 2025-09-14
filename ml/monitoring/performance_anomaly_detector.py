"""🚀 Performance Anomaly Detector - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/monitoring/performance_anomaly_detector.py
Author: Fahed Mlaiel (mlaiel@live.de) - Security Expert
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 DÉTECTEUR D'ANOMALIES DE PERFORMANCE
Détection d'anomalies avec méthodes statistiques et ML
- Statistical anomaly detection (Z-score, IQR, etc.)
- ML-based anomaly detection (Isolation Forest, One-Class SVM)
- Time-series anomaly detection avec tendances
- Security threat detection via performance patterns
"""

import asyncio
import logging
import time
import uuid
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from pathlib import Path

# ML Libraries pour détection d'anomalies
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.svm import OneClassSVM
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("Scikit-learn not available, using statistical methods only")

# Configuration
logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Types d'anomalies détectées"""
    STATISTICAL = "statistical"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BEHAVIORAL = "behavioral"
    TEMPORAL = "temporal"

class AnomalySeverity(Enum):
    """Sévérité des anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DetectionMethod(Enum):
    """Méthodes de détection d'anomalies"""
    Z_SCORE = "z_score"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    MOVING_AVERAGE = "moving_average"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    ENSEMBLE = "ensemble"

class CreatorType(Enum):
    """Types de créateurs pour détection spécialisée"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

@dataclass
class PerformanceMetric:
    """Métrique de performance à analyser"""
    metric_name: str
    value: float
    timestamp: datetime
    creator_type: Optional[CreatorType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnomalyDetection:
    """Détection d'anomalie"""
    anomaly_id: str
    metric_name: str
    value: float
    expected_value: float
    deviation: float
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detection_method: DetectionMethod
    timestamp: datetime
    confidence: float
    creator_type: Optional[CreatorType] = None
    security_implications: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnomalyPattern:
    """Modèle d'anomalie récurrente"""
    pattern_id: str
    anomaly_type: AnomalyType
    metrics_involved: List[str]
    frequency: str  # "daily", "weekly", "irregular"
    severity_trend: str  # "increasing", "stable", "decreasing"
    creator_correlation: Dict[CreatorType, float] = field(default_factory=dict)
    security_risk_score: float = 0.0
    last_occurrence: datetime = field(default_factory=datetime.now)

@dataclass
class DetectorConfig:
    """Configuration du détecteur d'anomalies"""
    z_score_threshold: float = 3.0
    iqr_multiplier: float = 1.5
    isolation_contamination: float = 0.1
    svm_nu: float = 0.05
    moving_window_size: int = 50
    min_data_points: int = 30
    enable_ml_detection: bool = True
    enable_security_analysis: bool = True
    creator_specific_thresholds: Dict[CreatorType, Dict[str, float]] = field(default_factory=dict)
    security_sensitive_metrics: List[str] = field(default_factory=lambda: [
        'error_rate', 'latency', 'failed_requests', 'unauthorized_access'
    ])

class PerformanceAnomalyDetector:
    """🔐 Détecteur d'anomalies de performance avec analyse de sécurité"""
    
    def __init__(self, config -> None: DetectorConfig) -> None:
        self.config = config
        self.detector_id = str(uuid.uuid4())
        self.metrics_history: List[PerformanceMetric] = []
        self.anomalies: List[AnomalyDetection] = []
        self.patterns: List[AnomalyPattern] = []
        self.ml_models: Dict[str, Any] = {}
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self._initialize_ml_models()
        
        logger.info(f"Performance Anomaly Detector initialized: {self.detector_id}")
    
    def _initialize_ml_models(self) -> None:
        """Initialise les modèles ML pour détection d'anomalies"""
        if not ML_AVAILABLE:
            logger.warning("ML models not available, using statistical methods only")
            return
        
        try:
            # Isolation Forest
            self.ml_models['isolation_forest'] = IsolationForest(
                contamination=self.config.isolation_contamination,
                random_state=42
            )
            
            # One-Class SVM
            self.ml_models['one_class_svm'] = OneClassSVM(
                nu=self.config.svm_nu,
                kernel='rbf',
                gamma='scale'
            )
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
    
    async def add_metric(self, metric -> None: PerformanceMetric) -> None:
        """Ajoute une métrique et détecte les anomalies"""
        try:
            self.metrics_history.append(metric)
            
            # Maintenir l'historique dans une fenêtre glissante
            cutoff_time = datetime.now() - timedelta(days=7)
            self.metrics_history = [
                m for m in self.metrics_history 
                if m.timestamp > cutoff_time
            ]
            
            # Détecter les anomalies
            await self._detect_anomalies(metric)
            
            # Analyser les patterns si assez de données
            if len(self.metrics_history) > self.config.min_data_points:
                await self._analyze_patterns()
            
            # Mise à jour des modèles ML
            if len(self.metrics_history) % 100 == 0:  # Tous les 100 points
                await self._update_ml_models()
            
        except Exception as e:
            logger.error(f"Error adding metric: {e}")
            raise
    
    async def _detect_anomalies(self, metric -> None: PerformanceMetric) -> None:
        """Détecte les anomalies pour une métrique"""
        try:
            # Obtenir l'historique pour cette métrique
            metric_history = [
                m for m in self.metrics_history 
                if m.metric_name == metric.metric_name
            ]
            
            if len(metric_history) < self.config.min_data_points:
                return
            
            # Détecter avec différentes méthodes
            anomalies = []
            
            # Méthode Z-score
            z_anomaly = await self._detect_z_score_anomaly(metric, metric_history)
            if z_anomaly:
                anomalies.append(z_anomaly)
            
            # Méthode IQR
            iqr_anomaly = await self._detect_iqr_anomaly(metric, metric_history)
            if iqr_anomaly:
                anomalies.append(iqr_anomaly)
            
            # Méthodes ML si disponibles
            if ML_AVAILABLE and self.config.enable_ml_detection:
                ml_anomaly = await self._detect_ml_anomaly(metric, metric_history)
                if ml_anomaly:
                    anomalies.append(ml_anomaly)
            
            # Analyse temporelle
            temporal_anomaly = await self._detect_temporal_anomaly(metric, metric_history)
            if temporal_anomaly:
                anomalies.append(temporal_anomaly)
            
            # Ajouter les anomalies détectées
            for anomaly in anomalies:
                await self._process_anomaly(anomaly)
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
    
    async def _detect_z_score_anomaly(self, metric: PerformanceMetric, history: List[PerformanceMetric]) -> Optional[AnomalyDetection]:
        """Détecte les anomalies avec Z-score"""
        try:
            values = [m.value for m in history]
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
            
            if std_val == 0:
                return None
            
            z_score = abs(metric.value - mean_val) / std_val
            
            if z_score > self.config.z_score_threshold:
                severity = self._calculate_severity(z_score, self.config.z_score_threshold)
                
                anomaly = AnomalyDetection(
                    anomaly_id=str(uuid.uuid4()),
                    metric_name=metric.metric_name,
                    value=metric.value,
                    expected_value=mean_val,
                    deviation=z_score,
                    anomaly_type=AnomalyType.STATISTICAL,
                    severity=severity,
                    detection_method=DetectionMethod.Z_SCORE,
                    timestamp=metric.timestamp,
                    confidence=min(0.95, z_score / self.config.z_score_threshold),
                    creator_type=metric.creator_type,
                    metadata={'z_score': z_score, 'std_dev': std_val}
                )
                
                return anomaly
            
            return None
            
        except Exception as e:
            logger.error(f"Error in Z-score detection: {e}")
            return None
    
    async def _detect_iqr_anomaly(self, metric: PerformanceMetric, history: List[PerformanceMetric]) -> Optional[AnomalyDetection]:
        """Détecte les anomalies avec méthode IQR"""
        try:
            values = [m.value for m in history]
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - self.config.iqr_multiplier * iqr
            upper_bound = q3 + self.config.iqr_multiplier * iqr
            
            if metric.value < lower_bound or metric.value > upper_bound:
                expected_value = (q1 + q3) / 2
                deviation = min(abs(metric.value - lower_bound), abs(metric.value - upper_bound))
                normalized_deviation = deviation / (iqr if iqr > 0 else 1)
                
                severity = self._calculate_severity(normalized_deviation, 1.0)
                
                anomaly = AnomalyDetection(
                    anomaly_id=str(uuid.uuid4()),
                    metric_name=metric.metric_name,
                    value=metric.value,
                    expected_value=expected_value,
                    deviation=normalized_deviation,
                    anomaly_type=AnomalyType.STATISTICAL,
                    severity=severity,
                    detection_method=DetectionMethod.IQR,
                    timestamp=metric.timestamp,
                    confidence=min(0.9, normalized_deviation),
                    creator_type=metric.creator_type,
                    metadata={'q1': q1, 'q3': q3, 'iqr': iqr, 'bounds': [lower_bound, upper_bound]}
                )
                
                return anomaly
            
            return None
            
        except Exception as e:
            logger.error(f"Error in IQR detection: {e}")
            return None
    
    async def _detect_ml_anomaly(self, metric: PerformanceMetric, history: List[PerformanceMetric]) -> Optional[AnomalyDetection]:
        """Détecte les anomalies avec méthodes ML"""
        try:
            if not ML_AVAILABLE or len(history) < 50:
                return None
            
            # Préparer les données
            features = self._prepare_features_for_ml(history)
            current_features = self._prepare_single_feature(metric, history)
            
            if features is None or current_features is None:
                return None
            
            # Utiliser Isolation Forest
            if 'isolation_forest' in self.ml_models:
                model = self.ml_models['isolation_forest']
                
                # Entraîner si nécessaire
                if not hasattr(model, 'decision_function_'):
                    scaled_features = self.scaler.fit_transform(features)
                    model.fit(scaled_features)
                
                # Prédire pour la nouvelle métrique
                scaled_current = self.scaler.transform([current_features])
                anomaly_score = model.decision_function(scaled_current)[0]
                prediction = model.predict(scaled_current)[0]
                
                if prediction == -1:  # Anomalie détectée
                    severity = self._calculate_severity(abs(anomaly_score), 0.1)
                    
                    anomaly = AnomalyDetection(
                        anomaly_id=str(uuid.uuid4()),
                        metric_name=metric.metric_name,
                        value=metric.value,
                        expected_value=np.mean([m.value for m in history[-10:]]),
                        deviation=abs(anomaly_score),
                        anomaly_type=AnomalyType.PERFORMANCE,
                        severity=severity,
                        detection_method=DetectionMethod.ISOLATION_FOREST,
                        timestamp=metric.timestamp,
                        confidence=min(0.95, abs(anomaly_score) * 10),
                        creator_type=metric.creator_type,
                        metadata={'anomaly_score': anomaly_score, 'model': 'isolation_forest'}
                    )
                    
                    return anomaly
            
            return None
            
        except Exception as e:
            logger.error(f"Error in ML anomaly detection: {e}")
            return None
    
    async def _detect_temporal_anomaly(self, metric: PerformanceMetric, history: List[PerformanceMetric]) -> Optional[AnomalyDetection]:
        """Détecte les anomalies temporelles"""
        try:
            if len(history) < self.config.moving_window_size:
                return None
            
            # Calculer la moyenne mobile
            recent_values = [m.value for m in history[-self.config.moving_window_size:]]
            moving_avg = statistics.mean(recent_values)
            moving_std = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
            
            if moving_std == 0:
                return None
            
            # Détecter les changements brusques
            deviation = abs(metric.value - moving_avg) / moving_std
            
            if deviation > 2.5:  # Seuil pour anomalie temporelle
                severity = self._calculate_severity(deviation, 2.5)
                
                anomaly = AnomalyDetection(
                    anomaly_id=str(uuid.uuid4()),
                    metric_name=metric.metric_name,
                    value=metric.value,
                    expected_value=moving_avg,
                    deviation=deviation,
                    anomaly_type=AnomalyType.TEMPORAL,
                    severity=severity,
                    detection_method=DetectionMethod.MOVING_AVERAGE,
                    timestamp=metric.timestamp,
                    confidence=min(0.9, deviation / 2.5),
                    creator_type=metric.creator_type,
                    metadata={'moving_average': moving_avg, 'window_size': self.config.moving_window_size}
                )
                
                return anomaly
            
            return None
            
        except Exception as e:
            logger.error(f"Error in temporal anomaly detection: {e}")
            return None
    
    def _prepare_features_for_ml(self, history: List[PerformanceMetric]) -> Optional[np.ndarray]:
        """Prépare les features pour les modèles ML"""
        try:
            features = []
            
            for i in range(len(history) - 5):  # Fenêtre de 5 points
                window = history[i:i+5]
                feature_vector = [
                    window[-1].value,  # Valeur actuelle
                    np.mean([m.value for m in window]),  # Moyenne
                    np.std([m.value for m in window]) if len(window) > 1 else 0,  # Écart-type
                    max([m.value for m in window]) - min([m.value for m in window]),  # Range
                    # Tendance (pente)
                    (window[-1].value - window[0].value) / 5 if window[0].value != 0 else 0
                ]
                features.append(feature_vector)
            
            return np.array(features) if features else None
            
        except Exception as e:
            logger.error(f"Error preparing ML features: {e}")
            return None
    
    def _prepare_single_feature(self, metric: PerformanceMetric, history: List[PerformanceMetric]) -> Optional[List[float]]:
        """Prépare les features pour une métrique unique"""
        try:
            if len(history) < 5:
                return None
            
            recent_window = history[-5:] + [metric]
            
            feature_vector = [
                metric.value,
                np.mean([m.value for m in recent_window]),
                np.std([m.value for m in recent_window]) if len(recent_window) > 1 else 0,
                max([m.value for m in recent_window]) - min([m.value for m in recent_window]),
                (recent_window[-1].value - recent_window[0].value) / 5 if recent_window[0].value != 0 else 0
            ]
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error preparing single feature: {e}")
            return None
    
    def _calculate_severity(self, deviation: float, threshold: float) -> AnomalySeverity:
        """Calcule la sévérité d'une anomalie"""
        ratio = deviation / threshold
        
        if ratio >= 3.0:
            return AnomalySeverity.CRITICAL
        elif ratio >= 2.0:
            return AnomalySeverity.HIGH
        elif ratio >= 1.5:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    async def _process_anomaly(self, anomaly -> None: AnomalyDetection) -> None:
        """Traite une anomalie détectée"""
        try:
            # Ajouter des implications de sécurité si métrique sensible
            if self.config.enable_security_analysis:
                await self._analyze_security_implications(anomaly)
            
            # Générer des actions recommandées
            anomaly.recommended_actions = self._generate_recommended_actions(anomaly)
            
            # Ajouter à la liste des anomalies
            self.anomalies.append(anomaly)
            
            # Maintenir la liste des anomalies (garder les 1000 dernières)
            if len(self.anomalies) > 1000:
                self.anomalies = self.anomalies[-1000:]
            
            logger.warning(f"Anomaly detected: {anomaly.metric_name} = {anomaly.value:.3f} "
                         f"(expected: {anomaly.expected_value:.3f}, severity: {anomaly.severity.value})")
            
        except Exception as e:
            logger.error(f"Error processing anomaly: {e}")
    
    async def _analyze_security_implications(self, anomaly -> None: AnomalyDetection) -> None:
        """Analyse les implications de sécurité"""
        try:
            if anomaly.metric_name in self.config.security_sensitive_metrics:
                anomaly.anomaly_type = AnomalyType.SECURITY
                
                security_implications = []
                
                if anomaly.metric_name == 'error_rate' and anomaly.value > anomaly.expected_value:
                    security_implications.extend([
                        "Potential DDoS attack or system overload",
                        "Possible injection attacks causing errors",
                        "System instability affecting security"
                    ])
                
                elif anomaly.metric_name == 'latency' and anomaly.value > anomaly.expected_value:
                    security_implications.extend([
                        "Possible resource exhaustion attack",
                        "Potential cryptographic computation overload",
                        "System stress affecting security mechanisms"
                    ])
                
                elif anomaly.metric_name == 'failed_requests':
                    security_implications.extend([
                        "Potential brute force attack",
                        "Systematic probing of endpoints",
                        "Authentication bypass attempts"
                    ])
                
                elif anomaly.metric_name == 'unauthorized_access':
                    security_implications.extend([
                        "Active security breach attempt",
                        "Credential stuffing attack",
                        "Privilege escalation attempt"
                    ])
                
                anomaly.security_implications = security_implications
                
                # Augmenter la sévérité pour les anomalies de sécurité
                if anomaly.severity == AnomalySeverity.LOW:
                    anomaly.severity = AnomalySeverity.MEDIUM
                elif anomaly.severity == AnomalySeverity.MEDIUM:
                    anomaly.severity = AnomalySeverity.HIGH
            
        except Exception as e:
            logger.error(f"Error analyzing security implications: {e}")
    
    def _generate_recommended_actions(self, anomaly: AnomalyDetection) -> List[str]:
        """Génère des actions recommandées"""
        actions = []
        
        if anomaly.severity == AnomalySeverity.CRITICAL:
            actions.append("Immediate investigation required")
            actions.append("Consider emergency system isolation")
        
        if anomaly.anomaly_type == AnomalyType.SECURITY:
            actions.extend([
                "Review security logs for suspicious activity",
                "Check firewall and intrusion detection systems",
                "Verify user authentication patterns"
            ])
        
        if anomaly.metric_name == 'latency':
            actions.extend([
                "Check system resource utilization",
                "Review recent deployments",
                "Monitor database performance"
            ])
        
        elif anomaly.metric_name == 'error_rate':
            actions.extend([
                "Review application logs",
                "Check for recent configuration changes",
                "Monitor system health metrics"
            ])
        
        if anomaly.creator_type:
            actions.append(f"Review {anomaly.creator_type.value}-specific patterns")
        
        return actions
    
    async def _analyze_patterns(self) -> None:
        """Analyse les patterns d'anomalies"""
        try:
            # Analyser les anomalies des dernières 24h
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_anomalies = [a for a in self.anomalies if a.timestamp > recent_cutoff]
            
            if len(recent_anomalies) < 3:
                return
            
            # Grouper par type et métrique
            patterns = {}
            for anomaly in recent_anomalies:
                key = f"{anomaly.metric_name}_{anomaly.anomaly_type.value}"
                if key not in patterns:
                    patterns[key] = []
                patterns[key].append(anomaly)
            
            # Identifier les patterns récurrents
            for pattern_key, anomalies in patterns.items():
                if len(anomalies) >= 3:  # Au moins 3 occurrences
                    await self._create_anomaly_pattern(pattern_key, anomalies)
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
    
    async def _create_anomaly_pattern(self, pattern_key -> None: str, anomalies -> None: List[AnomalyDetection]) -> None:
        """Crée un pattern d'anomalie"""
        try:
            # Calculer les caractéristiques du pattern
            severity_scores = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            avg_severity = np.mean([severity_scores[a.severity.value] for a in anomalies])
            
            # Analyser la fréquence
            timestamps = [a.timestamp for a in anomalies]
            time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
            avg_interval = np.mean(time_diffs) if time_diffs else 0
            
            frequency = "irregular"
            if avg_interval < 3600:  # < 1 heure
                frequency = "high_frequency"
            elif avg_interval < 86400:  # < 1 jour
                frequency = "daily"
            elif avg_interval < 604800:  # < 1 semaine
                frequency = "weekly"
            
            # Calculer le risque de sécurité
            security_risk = 0.0
            if any(a.anomaly_type == AnomalyType.SECURITY for a in anomalies):
                security_risk = min(1.0, len([a for a in anomalies if a.anomaly_type == AnomalyType.SECURITY]) / len(anomalies))
            
            pattern = AnomalyPattern(
                pattern_id=str(uuid.uuid4()),
                anomaly_type=anomalies[0].anomaly_type,
                metrics_involved=[anomalies[0].metric_name],
                frequency=frequency,
                severity_trend="stable",  # Pourrait être calculé sur une période plus longue
                security_risk_score=security_risk,
                last_occurrence=max(timestamps)
            )
            
            # Corrélation par créateur
            creator_counts = {}
            for anomaly in anomalies:
                if anomaly.creator_type:
                    creator_counts[anomaly.creator_type] = creator_counts.get(anomaly.creator_type, 0) + 1
            
            total_creator_anomalies = sum(creator_counts.values())
            if total_creator_anomalies > 0:
                pattern.creator_correlation = {
                    creator: count / total_creator_anomalies 
                    for creator, count in creator_counts.items()
                }
            
            self.patterns.append(pattern)
            
            logger.info(f"Anomaly pattern detected: {pattern_key} (frequency: {frequency}, risk: {security_risk:.2f})")
            
        except Exception as e:
            logger.error(f"Error creating anomaly pattern: {e}")
    
    async def _update_ml_models(self) -> None:
        """Met à jour les modèles ML avec nouvelles données"""
        try:
            if not ML_AVAILABLE or len(self.metrics_history) < 100:
                return
            
            # Grouper par métrique
            metrics_by_name = {}
            for metric in self.metrics_history:
                if metric.metric_name not in metrics_by_name:
                    metrics_by_name[metric.metric_name] = []
                metrics_by_name[metric.metric_name].append(metric)
            
            # Réentraîner pour chaque métrique
            for metric_name, metric_history in metrics_by_name.items():
                if len(metric_history) >= 50:
                    features = self._prepare_features_for_ml(metric_history)
                    if features is not None:
                        scaled_features = self.scaler.fit_transform(features)
                        
                        # Réentraîner Isolation Forest
                        if 'isolation_forest' in self.ml_models:
                            self.ml_models['isolation_forest'].fit(scaled_features)
            
            logger.info("ML models updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating ML models: {e}")
    
    async def get_anomaly_summary(self) -> Dict[str, Any]:
        """Génère un résumé des anomalies"""
        try:
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_anomalies = [a for a in self.anomalies if a.timestamp > recent_cutoff]
            
            # Statistiques générales
            total_anomalies = len(self.anomalies)
            recent_anomalies_count = len(recent_anomalies)
            
            # Par sévérité
            severity_counts = {}
            for severity in AnomalySeverity:
                severity_counts[severity.value] = len([a for a in recent_anomalies if a.severity == severity])
            
            # Par type
            type_counts = {}
            for anomaly_type in AnomalyType:
                type_counts[anomaly_type.value] = len([a for a in recent_anomalies if a.anomaly_type == anomaly_type])
            
            # Métriques les plus affectées
            metric_counts = {}
            for anomaly in recent_anomalies:
                metric_counts[anomaly.metric_name] = metric_counts.get(anomaly.metric_name, 0) + 1
            
            top_affected_metrics = sorted(metric_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Patterns actifs
            active_patterns = [p for p in self.patterns if p.last_occurrence > recent_cutoff]
            
            # Score de risque global
            security_anomalies = [a for a in recent_anomalies if a.anomaly_type == AnomalyType.SECURITY]
            security_risk_score = len(security_anomalies) / max(1, recent_anomalies_count)
            
            return {
                'detector_id': self.detector_id,
                'total_anomalies': total_anomalies,
                'recent_anomalies_24h': recent_anomalies_count,
                'severity_breakdown': severity_counts,
                'type_breakdown': type_counts,
                'top_affected_metrics': top_affected_metrics,
                'active_patterns': len(active_patterns),
                'security_risk_score': security_risk_score,
                'ml_models_available': ML_AVAILABLE,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating anomaly summary: {e}")
            return {}
    
    async def get_security_analysis(self) -> Dict[str, Any]:
        """Génère une analyse de sécurité détaillée"""
        try:
            recent_cutoff = datetime.now() - timedelta(hours=24)
            security_anomalies = [
                a for a in self.anomalies 
                if a.timestamp > recent_cutoff and a.anomaly_type == AnomalyType.SECURITY
            ]
            
            if not security_anomalies:
                return {'status': 'no_security_anomalies', 'risk_level': 'low'}
            
            # Analyser les implications de sécurité
            all_implications = []
            for anomaly in security_anomalies:
                all_implications.extend(anomaly.security_implications)
            
            # Compter les types d'implications
            implication_counts = {}
            for implication in all_implications:
                implication_counts[implication] = implication_counts.get(implication, 0) + 1
            
            top_threats = sorted(implication_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Calculer le niveau de risque
            critical_count = len([a for a in security_anomalies if a.severity == AnomalySeverity.CRITICAL])
            high_count = len([a for a in security_anomalies if a.severity == AnomalySeverity.HIGH])
            
            if critical_count > 0:
                risk_level = 'critical'
            elif high_count > 2:
                risk_level = 'high'
            elif len(security_anomalies) > 5:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'status': 'security_anomalies_detected',
                'risk_level': risk_level,
                'total_security_anomalies': len(security_anomalies),
                'critical_anomalies': critical_count,
                'high_severity_anomalies': high_count,
                'top_threats': top_threats,
                'recommended_immediate_actions': [
                    'Review security logs',
                    'Check firewall configurations',
                    'Monitor user authentication patterns',
                    'Verify system integrity'
                ] if risk_level in ['critical', 'high'] else [],
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating security analysis: {e}")
            return {'status': 'error', 'error': str(e)}

# Factory functions
def create_anomaly_detector(
    z_score_threshold: float = 3.0,
    enable_ml: bool = True,
    enable_security: bool = True
) -> PerformanceAnomalyDetector:
    """Factory pour créer un détecteur d'anomalies"""
    config = DetectorConfig(
        z_score_threshold=z_score_threshold,
        enable_ml_detection=enable_ml,
        enable_security_analysis=enable_security
    )
    return PerformanceAnomalyDetector(config)

async def demo_anomaly_detector() -> None:
    """Démo du détecteur d'anomalies"""
    detector = create_anomaly_detector()
    
    print("🔐 Performance Anomaly Detector Demo")
    
    # Simuler des métriques normales et anormales
    base_time = datetime.now()
    
    # Métriques normales
    for i in range(50):
        metric = PerformanceMetric(
            metric_name="response_time",
            value=100 + np.random.normal(0, 10),  # Temps de réponse normal ~100ms ±10ms
            timestamp=base_time + timedelta(minutes=i),
            creator_type=CreatorType.MUSICIAN
        )
        await detector.add_metric(metric)
    
    # Anomalies simulées
    anomalous_values = [200, 350, 180, 400]  # Valeurs anormalement élevées
    for i, value in enumerate(anomalous_values):
        metric = PerformanceMetric(
            metric_name="response_time",
            value=value,
            timestamp=base_time + timedelta(minutes=50 + i),
            creator_type=CreatorType.MUSICIAN
        )
        await detector.add_metric(metric)
    
    # Métriques de sécurité suspectes
    security_metric = PerformanceMetric(
        metric_name="failed_requests",
        value=50,  # Normalement ~2-3
        timestamp=base_time + timedelta(minutes=55),
        creator_type=CreatorType.MUSICIAN
    )
    await detector.add_metric(security_metric)
    
    # Résumé des anomalies
    summary = await detector.get_anomaly_summary()
    security_analysis = await detector.get_security_analysis()
    
    print(f"\n📊 Anomaly Summary:")
    print(f"Total Anomalies (24h): {summary['recent_anomalies_24h']}")
    print(f"Security Risk Score: {summary['security_risk_score']:.2f}")
    print(f"Most Affected Metrics: {summary['top_affected_metrics'][:3]}")
    
    print(f"\n🔒 Security Analysis:")
    print(f"Risk Level: {security_analysis['risk_level']}")
    if security_analysis.get('top_threats'):
        print("Top Threats:")
        for threat, count in security_analysis['top_threats'][:3]:
            print(f"  • {threat} ({count} occurrences)")

if __name__ == "__main__":
    # Configurer le logging
    logging.basicConfig(level=logging.INFO)
    
    # Lancer la démo
    asyncio.run(demo_anomaly_detector())