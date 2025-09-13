#!/usr/bin/env python3
"""
🛡️ Model Poisoning Detector - Enterprise MLOps Platform
Sécurité Expertise: Détection d'empoisonnement de modèles avec protection

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
import hashlib
import sqlite3
from collections import defaultdict, deque
import statistics
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoisoningType(Enum):
    """Types d'empoisonnement détectés"""
    DATA_POISONING = "data_poisoning"
    MODEL_POISONING = "model_poisoning"
    LABEL_FLIPPING = "label_flipping"
    BACKDOOR_ATTACK = "backdoor_attack"
    ADVERSARIAL_TRAINING = "adversarial_training"
    GRADIENT_MANIPULATION = "gradient_manipulation"
    EVASION_ATTACK = "evasion_attack"
    UNKNOWN = "unknown"

class ThreatLevel(Enum):
    """Niveaux de menace"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CreatorModelType(Enum):
    """Types de modèles par créateur"""
    MUSICIAN_AUDIO_CLASSIFIER = "musician_audio_classifier"
    MUSICIAN_GENRE_DETECTOR = "musician_genre_detector"
    BLOGGER_CONTENT_CLASSIFIER = "blogger_content_classifier"
    BLOGGER_SENTIMENT_ANALYZER = "blogger_sentiment_analyzer"
    PHOTOGRAPHER_IMAGE_CLASSIFIER = "photographer_image_classifier"
    PHOTOGRAPHER_STYLE_DETECTOR = "photographer_style_detector"
    INFLUENCER_ENGAGEMENT_PREDICTOR = "influencer_engagement_predictor"
    INFLUENCER_TREND_ANALYZER = "influencer_trend_analyzer"
    COMEDIAN_HUMOR_CLASSIFIER = "comedian_humor_classifier"
    COMEDIAN_TIMING_PREDICTOR = "comedian_timing_predictor"

@dataclass
class PoisoningDetection:
    """Détection d'empoisonnement"""
    detection_id: str
    model_id: str
    model_type: CreatorModelType
    poisoning_type: PoisoningType
    threat_level: ThreatLevel
    confidence_score: float
    affected_samples: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    mitigation_strategies: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    detection_time_ms: float = 0.0

@dataclass
class ModelHealth:
    """Santé d'un modèle"""
    model_id: str
    health_score: float  # 0-1
    performance_degradation: float
    anomaly_score: float
    data_integrity_score: float
    behavioral_consistency: float
    last_check: datetime = field(default_factory=datetime.now)
    issues_detected: List[str] = field(default_factory=list)

@dataclass
class SecurityBaseline:
    """Baseline de sécurité pour un modèle"""
    model_id: str
    baseline_accuracy: float
    baseline_loss: float
    feature_importance_baseline: Dict[str, float]
    prediction_distribution: Dict[str, float]
    gradient_norms: List[float]
    established_at: datetime = field(default_factory=datetime.now)

class ModelPoisoningDetector:
    """
    Détecteur d'empoisonnement de modèles enterprise
    
    Fonctionnalités:
    - Détection multi-types d'empoisonnement
    - Analyse comportementale des modèles
    - Monitoring de l'intégrité des données
    - Protection en temps réel contre les attaques
    - Mitigation automatique des menaces
    - Audit trail complet des incidents
    """
    
    def __init__(self,
                 db_path: str = "/tmp/model_poisoning_detector.db",
                 detection_sensitivity: float = 0.8,
                 max_baseline_age_days: int = 30):
        self.db_path = db_path
        self.detection_sensitivity = detection_sensitivity
        self.max_baseline_age_days = max_baseline_age_days
        
        # Stockage des baselines et détections
        self.security_baselines: Dict[str, SecurityBaseline] = {}
        self.model_health: Dict[str, ModelHealth] = {}
        self.detection_history: Dict[str, List[PoisoningDetection]] = defaultdict(list)
        
        # Seuils par type de créateur
        self.creator_thresholds = {
            CreatorModelType.MUSICIAN_AUDIO_CLASSIFIER: {
                "max_accuracy_drop": 0.05,
                "max_loss_increase": 0.10,
                "anomaly_threshold": 0.15,
                "gradient_norm_threshold": 2.0
            },
            CreatorModelType.BLOGGER_SENTIMENT_ANALYZER: {
                "max_accuracy_drop": 0.03,
                "max_loss_increase": 0.08,
                "anomaly_threshold": 0.12,
                "gradient_norm_threshold": 1.5
            },
            CreatorModelType.PHOTOGRAPHER_IMAGE_CLASSIFIER: {
                "max_accuracy_drop": 0.04,
                "max_loss_increase": 0.09,
                "anomaly_threshold": 0.18,
                "gradient_norm_threshold": 2.5
            },
            CreatorModelType.INFLUENCER_ENGAGEMENT_PREDICTOR: {
                "max_accuracy_drop": 0.06,
                "max_loss_increase": 0.12,
                "anomaly_threshold": 0.20,
                "gradient_norm_threshold": 1.8
            },
            CreatorModelType.COMEDIAN_HUMOR_CLASSIFIER: {
                "max_accuracy_drop": 0.07,
                "max_loss_increase": 0.15,
                "anomaly_threshold": 0.25,
                "gradient_norm_threshold": 2.2
            }
        }
        
        # Détecteurs spécialisés
        self.poison_detectors = {
            PoisoningType.DATA_POISONING: self._detect_data_poisoning,
            PoisoningType.LABEL_FLIPPING: self._detect_label_flipping,
            PoisoningType.BACKDOOR_ATTACK: self._detect_backdoor_attack,
            PoisoningType.GRADIENT_MANIPULATION: self._detect_gradient_manipulation,
            PoisoningType.EVASION_ATTACK: self._detect_evasion_attack
        }
        
        # Callbacks
        self.detection_callbacks: List[Callable] = []
        self.mitigation_callbacks: List[Callable] = []
        
        self._setup_database()
        logger.info("🛡️ ModelPoisoningDetector initialized for enterprise security")
    
    def _setup_database(self):
        """Initialisation de la base de données"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des détections
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS poisoning_detections (
                        detection_id TEXT PRIMARY KEY,
                        model_id TEXT NOT NULL,
                        model_type TEXT NOT NULL,
                        poisoning_type TEXT NOT NULL,
                        threat_level TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        affected_samples TEXT,
                        evidence TEXT,
                        mitigation_strategies TEXT,
                        timestamp TEXT NOT NULL,
                        detection_time_ms REAL NOT NULL
                    )
                """)
                
                # Table des baselines de sécurité
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS security_baselines (
                        model_id TEXT PRIMARY KEY,
                        baseline_accuracy REAL NOT NULL,
                        baseline_loss REAL NOT NULL,
                        feature_importance_baseline TEXT NOT NULL,
                        prediction_distribution TEXT NOT NULL,
                        gradient_norms TEXT NOT NULL,
                        established_at TEXT NOT NULL
                    )
                """)
                
                # Table de santé des modèles
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS model_health (
                        model_id TEXT PRIMARY KEY,
                        health_score REAL NOT NULL,
                        performance_degradation REAL NOT NULL,
                        anomaly_score REAL NOT NULL,
                        data_integrity_score REAL NOT NULL,
                        behavioral_consistency REAL NOT NULL,
                        last_check TEXT NOT NULL,
                        issues_detected TEXT
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Database setup error: {e}")
            raise
    
    async def establish_security_baseline(self,
                                        model_id: str,
                                        model_type: CreatorModelType,
                                        validation_data: np.ndarray,
                                        validation_labels: np.ndarray,
                                        model_predictions: np.ndarray) -> SecurityBaseline:
        """Établissement d'un baseline de sécurité"""
        try:
            # Calcul des métriques de base
            accuracy = np.mean(validation_labels == model_predictions)
            
            # Simulation du calcul de loss (remplacer par vraie implémentation)
            loss = -np.mean(validation_labels * np.log(model_predictions + 1e-10))
            
            # Feature importance simulée
            feature_importance = {}
            for i in range(min(10, validation_data.shape[1])):
                feature_importance[f"feature_{i}"] = np.random.uniform(0.01, 0.15)
            
            # Distribution des prédictions
            unique_preds, counts = np.unique(model_predictions, return_counts=True)
            prediction_distribution = {
                str(pred): count / len(model_predictions) 
                for pred, count in zip(unique_preds, counts)
            }
            
            # Gradient norms simulés
            gradient_norms = [np.random.uniform(0.1, 2.0) for _ in range(100)]
            
            baseline = SecurityBaseline(
                model_id=model_id,
                baseline_accuracy=accuracy,
                baseline_loss=loss,
                feature_importance_baseline=feature_importance,
                prediction_distribution=prediction_distribution,
                gradient_norms=gradient_norms
            )
            
            # Stockage
            self.security_baselines[model_id] = baseline
            await self._save_baseline_to_db(baseline)
            
            logger.info(f"🔒 Security baseline established for {model_id}: accuracy={accuracy:.4f}")
            return baseline
            
        except Exception as e:
            logger.error(f"❌ Error establishing baseline for {model_id}: {e}")
            raise
    
    async def scan_model_for_poisoning(self,
                                     model_id: str,
                                     model_type: CreatorModelType,
                                     current_data: np.ndarray,
                                     current_labels: np.ndarray,
                                     current_predictions: np.ndarray) -> List[PoisoningDetection]:
        """Scan complet d'un modèle pour détecter l'empoisonnement"""
        start_time = datetime.now()
        detections = []
        
        try:
            logger.info(f"🔍 Scanning model {model_id} for poisoning...")
            
            # Vérification du baseline
            if model_id not in self.security_baselines:
                logger.warning(f"⚠️ No security baseline for {model_id}, establishing one...")
                await self.establish_security_baseline(
                    model_id, model_type, current_data, current_labels, current_predictions
                )
                return []  # Première fois, pas de détection possible
            
            baseline = self.security_baselines[model_id]
            
            # Exécution de tous les détecteurs
            for poison_type, detector_func in self.poison_detectors.items():
                try:
                    detection = await detector_func(
                        model_id, model_type, baseline,
                        current_data, current_labels, current_predictions
                    )
                    
                    if detection:
                        detections.append(detection)
                        
                except Exception as e:
                    logger.error(f"❌ Error in {poison_type.value} detector: {e}")
            
            # Calcul du temps de détection total
            detection_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Mise à jour du temps pour toutes les détections
            for detection in detections:
                detection.detection_time_ms = detection_time
            
            # Stockage des détections
            for detection in detections:
                self.detection_history[model_id].append(detection)
                await self._save_detection_to_db(detection)
            
            # Mise à jour de la santé du modèle
            await self._update_model_health(model_id, model_type, baseline, current_predictions, detections)
            
            # Callbacks de détection
            for detection in detections:
                for callback in self.detection_callbacks:
                    try:
                        await callback(detection)
                    except Exception as e:
                        logger.error(f"❌ Detection callback error: {e}")
            
            # Mitigation automatique si détections critiques
            critical_detections = [d for d in detections if d.threat_level == ThreatLevel.CRITICAL]
            if critical_detections:
                await self._trigger_automatic_mitigation(model_id, critical_detections)
            
            logger.info(f"🔍 Scan completed for {model_id}: {len(detections)} detections found")
            return detections
            
        except Exception as e:
            logger.error(f"❌ Error scanning model {model_id}: {e}")
            return []
    
    async def _detect_data_poisoning(self,
                                   model_id: str,
                                   model_type: CreatorModelType,
                                   baseline: SecurityBaseline,
                                   data: np.ndarray,
                                   labels: np.ndarray,
                                   predictions: np.ndarray) -> Optional[PoisoningDetection]:
        """Détection d'empoisonnement des données"""
        try:
            # Calcul de l'accuracy actuelle
            current_accuracy = np.mean(labels == predictions)
            accuracy_drop = baseline.baseline_accuracy - current_accuracy
            
            # Seuils par type de créateur
            thresholds = self.creator_thresholds.get(model_type, {})
            max_drop = thresholds.get("max_accuracy_drop", 0.05)
            
            if accuracy_drop > max_drop:
                # Analyse des patterns de données
                suspicious_samples = []
                
                # Détection d'anomalies dans les features
                for i, sample in enumerate(data):
                    anomaly_score = np.mean(np.abs(sample - np.mean(data, axis=0)))
                    if anomaly_score > np.std(data) * 2:  # 2 sigma
                        suspicious_samples.append(str(i))
                
                confidence = min(1.0, accuracy_drop / max_drop)
                threat_level = ThreatLevel.HIGH if accuracy_drop > max_drop * 1.5 else ThreatLevel.MEDIUM
                
                detection = PoisoningDetection(
                    detection_id=f"data_poison_{model_id}_{int(datetime.now().timestamp())}",
                    model_id=model_id,
                    model_type=model_type,
                    poisoning_type=PoisoningType.DATA_POISONING,
                    threat_level=threat_level,
                    confidence_score=confidence,
                    affected_samples=suspicious_samples,
                    evidence={
                        "accuracy_drop": accuracy_drop,
                        "baseline_accuracy": baseline.baseline_accuracy,
                        "current_accuracy": current_accuracy,
                        "suspicious_sample_count": len(suspicious_samples)
                    },
                    mitigation_strategies=[
                        "Remove suspicious samples from training data",
                        "Implement data validation pipeline",
                        "Increase data quality monitoring",
                        "Retrain model with clean dataset"
                    ]
                )
                
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Data poisoning detection error: {e}")
            return None
    
    async def _detect_label_flipping(self,
                                   model_id: str,
                                   model_type: CreatorModelType,
                                   baseline: SecurityBaseline,
                                   data: np.ndarray,
                                   labels: np.ndarray,
                                   predictions: np.ndarray) -> Optional[PoisoningDetection]:
        """Détection de label flipping"""
        try:
            # Analyse de la distribution des labels
            unique_labels, label_counts = np.unique(labels, return_counts=True)
            current_distribution = {
                str(label): count / len(labels) 
                for label, count in zip(unique_labels, label_counts)
            }
            
            # Comparaison avec le baseline
            distribution_drift = 0.0
            for label, baseline_freq in baseline.prediction_distribution.items():
                current_freq = current_distribution.get(label, 0.0)
                distribution_drift += abs(baseline_freq - current_freq)
            
            # Détection d'inconsistances dans les prédictions
            prediction_inconsistency = 0.0
            for i, (true_label, pred_label) in enumerate(zip(labels, predictions)):
                if true_label != pred_label:
                    # Vérifier si c'est une erreur suspecte
                    prediction_inconsistency += 1
            
            prediction_inconsistency /= len(labels)
            
            # Seuil de détection
            if distribution_drift > 0.2 or prediction_inconsistency > 0.3:
                confidence = min(1.0, (distribution_drift + prediction_inconsistency) / 2)
                threat_level = ThreatLevel.HIGH if distribution_drift > 0.4 else ThreatLevel.MEDIUM
                
                detection = PoisoningDetection(
                    detection_id=f"label_flip_{model_id}_{int(datetime.now().timestamp())}",
                    model_id=model_id,
                    model_type=model_type,
                    poisoning_type=PoisoningType.LABEL_FLIPPING,
                    threat_level=threat_level,
                    confidence_score=confidence,
                    evidence={
                        "distribution_drift": distribution_drift,
                        "prediction_inconsistency": prediction_inconsistency,
                        "current_distribution": current_distribution,
                        "baseline_distribution": baseline.prediction_distribution
                    },
                    mitigation_strategies=[
                        "Verify label integrity in training data",
                        "Implement label validation checks",
                        "Cross-validate labels with multiple annotators",
                        "Use label smoothing techniques"
                    ]
                )
                
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Label flipping detection error: {e}")
            return None
    
    async def _detect_backdoor_attack(self,
                                    model_id: str,
                                    model_type: CreatorModelType,
                                    baseline: SecurityBaseline,
                                    data: np.ndarray,
                                    labels: np.ndarray,
                                    predictions: np.ndarray) -> Optional[PoisoningDetection]:
        """Détection d'attaques backdoor"""
        try:
            # Recherche de patterns suspects dans les données
            suspicious_patterns = []
            
            # Analyse des activations par feature
            for feature_idx in range(min(10, data.shape[1])):
                feature_values = data[:, feature_idx]
                
                # Détection de valeurs inhabituelles
                q25, q75 = np.percentile(feature_values, [25, 75])
                iqr = q75 - q25
                outlier_threshold = q75 + 1.5 * iqr
                
                outlier_count = np.sum(feature_values > outlier_threshold)
                if outlier_count > len(feature_values) * 0.05:  # Plus de 5% d'outliers
                    suspicious_patterns.append(f"feature_{feature_idx}")
            
            # Analyse des prédictions groupées
            prediction_clusters = defaultdict(list)
            for i, pred in enumerate(predictions):
                prediction_clusters[pred].append(i)
            
            # Recherche de clusters suspects
            suspicious_clusters = []
            for pred_class, indices in prediction_clusters.items():
                if len(indices) > 0:
                    cluster_data = data[indices]
                    cluster_variance = np.var(cluster_data, axis=0)
                    
                    # Si variance très faible sur certaines features = pattern suspect
                    low_variance_features = np.sum(cluster_variance < 0.01)
                    if low_variance_features > 2:
                        suspicious_clusters.append({
                            "class": pred_class,
                            "size": len(indices),
                            "low_variance_features": low_variance_features
                        })
            
            if suspicious_patterns or suspicious_clusters:
                confidence = min(1.0, (len(suspicious_patterns) + len(suspicious_clusters)) / 10)
                threat_level = ThreatLevel.CRITICAL if len(suspicious_clusters) > 0 else ThreatLevel.HIGH
                
                detection = PoisoningDetection(
                    detection_id=f"backdoor_{model_id}_{int(datetime.now().timestamp())}",
                    model_id=model_id,
                    model_type=model_type,
                    poisoning_type=PoisoningType.BACKDOOR_ATTACK,
                    threat_level=threat_level,
                    confidence_score=confidence,
                    evidence={
                        "suspicious_patterns": suspicious_patterns,
                        "suspicious_clusters": suspicious_clusters,
                        "pattern_count": len(suspicious_patterns),
                        "cluster_count": len(suspicious_clusters)
                    },
                    mitigation_strategies=[
                        "Analyze and remove trigger patterns",
                        "Implement input sanitization",
                        "Use adversarial training",
                        "Deploy ensemble models for verification",
                        "Implement trigger detection mechanisms"
                    ]
                )
                
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Backdoor detection error: {e}")
            return None
    
    async def _detect_gradient_manipulation(self,
                                          model_id: str,
                                          model_type: CreatorModelType,
                                          baseline: SecurityBaseline,
                                          data: np.ndarray,
                                          labels: np.ndarray,
                                          predictions: np.ndarray) -> Optional[PoisoningDetection]:
        """Détection de manipulation des gradients"""
        try:
            # Simulation du calcul de gradients (remplacer par vraie implémentation)
            current_gradients = [np.random.uniform(-1, 1) * np.random.uniform(0.1, 3.0) for _ in range(100)]
            
            # Calcul des normes de gradient
            current_grad_norms = [abs(g) for g in current_gradients]
            baseline_grad_norms = baseline.gradient_norms
            
            # Comparaison avec le baseline
            current_mean_norm = np.mean(current_grad_norms)
            baseline_mean_norm = np.mean(baseline_grad_norms)
            
            norm_deviation = abs(current_mean_norm - baseline_mean_norm) / baseline_mean_norm
            
            # Détection d'anomalies dans la distribution des gradients
            gradient_anomalies = 0
            for current_norm in current_grad_norms:
                if current_norm > baseline_mean_norm * 3:  # 3x la norme moyenne
                    gradient_anomalies += 1
            
            gradient_anomaly_rate = gradient_anomalies / len(current_grad_norms)
            
            # Seuils par type de créateur
            thresholds = self.creator_thresholds.get(model_type, {})
            grad_threshold = thresholds.get("gradient_norm_threshold", 2.0)
            
            if norm_deviation > 0.5 or gradient_anomaly_rate > 0.1:
                confidence = min(1.0, (norm_deviation + gradient_anomaly_rate) / 2)
                threat_level = ThreatLevel.HIGH if norm_deviation > 1.0 else ThreatLevel.MEDIUM
                
                detection = PoisoningDetection(
                    detection_id=f"grad_manip_{model_id}_{int(datetime.now().timestamp())}",
                    model_id=model_id,
                    model_type=model_type,
                    poisoning_type=PoisoningType.GRADIENT_MANIPULATION,
                    threat_level=threat_level,
                    confidence_score=confidence,
                    evidence={
                        "norm_deviation": norm_deviation,
                        "gradient_anomaly_rate": gradient_anomaly_rate,
                        "current_mean_norm": current_mean_norm,
                        "baseline_mean_norm": baseline_mean_norm,
                        "anomalous_gradients": gradient_anomalies
                    },
                    mitigation_strategies=[
                        "Implement gradient clipping",
                        "Use differential privacy in training",
                        "Monitor training process in real-time",
                        "Implement Byzantine-robust aggregation",
                        "Add gradient noise for protection"
                    ]
                )
                
                return detection
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Gradient manipulation detection error: {e}")
            return None
    
    async def _detect_evasion_attack(self,
                                   model_id: str,
                                   model_type: CreatorModelType,
                                   baseline: SecurityBaseline,
                                   data: np.ndarray,
                                   labels: np.ndarray,
                                   predictions: np.ndarray) -> Optional[PoisoningDetection]:
        """Détection d'attaques d'évasion"""
        try:
            # Analyse des échecs de prédiction
            misclassified_indices = np.where(labels != predictions)[0]
            misclassification_rate = len(misclassified_indices) / len(labels)
            
            # Analyse des données mal classifiées
            if len(misclassified_indices) > 0:
                misclassified_data = data[misclassified_indices]
                
                # Calcul de la distance par rapport aux données normales
                correctly_classified_data = data[labels == predictions]
                
                if len(correctly_classified_data) > 0:
                    # Distance moyenne entre données mal classifiées et bien classifiées
                    distances = []
                    for misc_sample in misclassified_data:
                        min_distance = np.min([
                            np.linalg.norm(misc_sample - correct_sample)
                            for correct_sample in correctly_classified_data[:100]  # Échantillon
                        ])
                        distances.append(min_distance)
                    
                    avg_distance = np.mean(distances)
                    distance_threshold = np.std(distances) * 2
                    
                    # Détection d'adversarial examples
                    adversarial_samples = [
                        str(misclassified_indices[i]) 
                        for i, dist in enumerate(distances) 
                        if dist < distance_threshold
                    ]
                    
                    if len(adversarial_samples) > len(misclassified_indices) * 0.3:
                        confidence = min(1.0, len(adversarial_samples) / len(misclassified_indices))
                        threat_level = ThreatLevel.HIGH
                        
                        detection = PoisoningDetection(
                            detection_id=f"evasion_{model_id}_{int(datetime.now().timestamp())}",
                            model_id=model_id,
                            model_type=model_type,
                            poisoning_type=PoisoningType.EVASION_ATTACK,
                            threat_level=threat_level,
                            confidence_score=confidence,
                            affected_samples=adversarial_samples,
                            evidence={
                                "misclassification_rate": misclassification_rate,
                                "adversarial_sample_count": len(adversarial_samples),
                                "avg_distance": avg_distance,
                                "distance_threshold": distance_threshold
                            },
                            mitigation_strategies=[
                                "Implement adversarial training",
                                "Use input preprocessing defenses",
                                "Deploy ensemble models",
                                "Add randomization to model",
                                "Implement detection mechanisms"
                            ]
                        )
                        
                        return detection
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Evasion attack detection error: {e}")
            return None
    
    async def _update_model_health(self,
                                 model_id: str,
                                 model_type: CreatorModelType,
                                 baseline: SecurityBaseline,
                                 current_predictions: np.ndarray,
                                 detections: List[PoisoningDetection]):
        """Mise à jour de la santé d'un modèle"""
        try:
            # Calcul des scores de santé
            accuracy = np.mean(current_predictions == current_predictions)  # Simulé
            performance_degradation = max(0, baseline.baseline_accuracy - accuracy)
            
            # Score d'anomalie basé sur les détections
            anomaly_score = 0.0
            if detections:
                threat_weights = {ThreatLevel.LOW: 0.1, ThreatLevel.MEDIUM: 0.3, 
                                ThreatLevel.HIGH: 0.6, ThreatLevel.CRITICAL: 1.0}
                anomaly_score = sum(
                    threat_weights.get(d.threat_level, 0.5) * d.confidence_score 
                    for d in detections
                ) / len(detections)
            
            # Score d'intégrité des données
            data_integrity_score = 1.0 - min(1.0, performance_degradation * 5)
            
            # Consistance comportementale
            behavioral_consistency = 1.0 - anomaly_score
            
            # Score de santé global
            health_score = (
                (1.0 - performance_degradation) * 0.3 +
                (1.0 - anomaly_score) * 0.3 +
                data_integrity_score * 0.2 +
                behavioral_consistency * 0.2
            )
            
            # Issues détectées
            issues = [d.poisoning_type.value for d in detections]
            
            model_health = ModelHealth(
                model_id=model_id,
                health_score=health_score,
                performance_degradation=performance_degradation,
                anomaly_score=anomaly_score,
                data_integrity_score=data_integrity_score,
                behavioral_consistency=behavioral_consistency,
                issues_detected=issues
            )
            
            self.model_health[model_id] = model_health
            await self._save_model_health_to_db(model_health)
            
            logger.info(f"📊 Model health updated for {model_id}: score={health_score:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Error updating model health: {e}")
    
    async def _trigger_automatic_mitigation(self,
                                          model_id: str,
                                          critical_detections: List[PoisoningDetection]):
        """Déclenchement de mitigation automatique"""
        try:
            logger.warning(f"🚨 Triggering automatic mitigation for {model_id}")
            
            mitigation_actions = []
            
            for detection in critical_detections:
                # Actions spécifiques par type d'attaque
                if detection.poisoning_type == PoisoningType.DATA_POISONING:
                    mitigation_actions.extend([
                        "Quarantine suspicious training samples",
                        "Trigger data quality audit",
                        "Activate backup model"
                    ])
                elif detection.poisoning_type == PoisoningType.BACKDOOR_ATTACK:
                    mitigation_actions.extend([
                        "Switch to ensemble inference",
                        "Activate trigger detection",
                        "Isolate model for analysis"
                    ])
                elif detection.poisoning_type == PoisoningType.EVASION_ATTACK:
                    mitigation_actions.extend([
                        "Enable adversarial detection",
                        "Increase input validation",
                        "Route to secure model variant"
                    ])
            
            # Callbacks de mitigation
            for callback in self.mitigation_callbacks:
                try:
                    await callback(model_id, critical_detections, mitigation_actions)
                except Exception as e:
                    logger.error(f"❌ Mitigation callback error: {e}")
            
            logger.info(f"🛡️ Automatic mitigation triggered: {len(mitigation_actions)} actions")
            
        except Exception as e:
            logger.error(f"❌ Error in automatic mitigation: {e}")
    
    async def _save_baseline_to_db(self, baseline: SecurityBaseline):
        """Sauvegarde baseline en DB"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO security_baselines 
                    (model_id, baseline_accuracy, baseline_loss, feature_importance_baseline,
                     prediction_distribution, gradient_norms, established_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    baseline.model_id,
                    baseline.baseline_accuracy,
                    baseline.baseline_loss,
                    json.dumps(baseline.feature_importance_baseline),
                    json.dumps(baseline.prediction_distribution),
                    json.dumps(baseline.gradient_norms),
                    baseline.established_at.isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saving baseline: {e}")
    
    async def _save_detection_to_db(self, detection: PoisoningDetection):
        """Sauvegarde détection en DB"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO poisoning_detections 
                    (detection_id, model_id, model_type, poisoning_type, threat_level,
                     confidence_score, affected_samples, evidence, mitigation_strategies,
                     timestamp, detection_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    detection.detection_id,
                    detection.model_id,
                    detection.model_type.value,
                    detection.poisoning_type.value,
                    detection.threat_level.value,
                    detection.confidence_score,
                    json.dumps(detection.affected_samples),
                    json.dumps(detection.evidence, default=str),
                    json.dumps(detection.mitigation_strategies),
                    detection.timestamp.isoformat(),
                    detection.detection_time_ms
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saving detection: {e}")
    
    async def _save_model_health_to_db(self, health: ModelHealth):
        """Sauvegarde santé modèle en DB"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO model_health 
                    (model_id, health_score, performance_degradation, anomaly_score,
                     data_integrity_score, behavioral_consistency, last_check, issues_detected)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    health.model_id,
                    health.health_score,
                    health.performance_degradation,
                    health.anomaly_score,
                    health.data_integrity_score,
                    health.behavioral_consistency,
                    health.last_check.isoformat(),
                    json.dumps(health.issues_detected)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saving model health: {e}")
    
    async def get_security_report(self, model_id: str) -> Dict[str, Any]:
        """Génération d'un rapport de sécurité"""
        try:
            report = {
                "model_id": model_id,
                "scan_timestamp": datetime.now().isoformat(),
                "baseline_established": model_id in self.security_baselines,
                "total_detections": len(self.detection_history.get(model_id, [])),
                "health_status": "unknown"
            }
            
            # Informations de santé
            if model_id in self.model_health:
                health = self.model_health[model_id]
                report.update({
                    "health_status": "healthy" if health.health_score > 0.8 else 
                                   "degraded" if health.health_score > 0.5 else "unhealthy",
                    "health_score": health.health_score,
                    "performance_degradation": health.performance_degradation,
                    "anomaly_score": health.anomaly_score,
                    "current_issues": health.issues_detected
                })
            
            # Historique des détections
            detections = self.detection_history.get(model_id, [])
            if detections:
                # Détections récentes (dernières 24h)
                recent_detections = [
                    d for d in detections 
                    if (datetime.now() - d.timestamp).total_seconds() < 86400
                ]
                
                # Répartition par type de menace
                threat_distribution = defaultdict(int)
                for detection in detections:
                    threat_distribution[detection.threat_level.value] += 1
                
                # Types d'attaques détectées
                attack_types = defaultdict(int)
                for detection in detections:
                    attack_types[detection.poisoning_type.value] += 1
                
                report.update({
                    "recent_detections_24h": len(recent_detections),
                    "threat_level_distribution": dict(threat_distribution),
                    "attack_types_detected": dict(attack_types),
                    "latest_detection": detections[-1].timestamp.isoformat() if detections else None
                })
            
            # Recommandations de sécurité
            recommendations = []
            if model_id not in self.security_baselines:
                recommendations.append("Establish security baseline for the model")
            
            if model_id in self.model_health:
                health = self.model_health[model_id]
                if health.health_score < 0.8:
                    recommendations.append("Model health is degraded - review recent changes")
                if health.anomaly_score > 0.3:
                    recommendations.append("High anomaly score detected - investigate data sources")
            
            report["security_recommendations"] = recommendations
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating security report: {e}")
            return {"error": str(e)}
    
    def add_detection_callback(self, callback: Callable):
        """Ajouter callback de détection"""
        self.detection_callbacks.append(callback)
        logger.info(f"🔍 Detection callback added. Total: {len(self.detection_callbacks)}")
    
    def add_mitigation_callback(self, callback: Callable):
        """Ajouter callback de mitigation"""
        self.mitigation_callbacks.append(callback)
        logger.info(f"🛡️ Mitigation callback added. Total: {len(self.mitigation_callbacks)}")


# Exemple d'utilisation pour démonstration
async def main():
    """Démonstration des capacités du ModelPoisoningDetector"""
    
    detector = ModelPoisoningDetector(detection_sensitivity=0.7)
    
    # Callbacks de démonstration
    async def detection_callback(detection: PoisoningDetection):
        print(f"🚨 THREAT DETECTED: {detection.poisoning_type.value}")
        print(f"   Model: {detection.model_id}")
        print(f"   Threat Level: {detection.threat_level.value}")
        print(f"   Confidence: {detection.confidence_score:.3f}")
    
    async def mitigation_callback(model_id: str, detections: List[PoisoningDetection], actions: List[str]):
        print(f"🛡️ AUTOMATIC MITIGATION: {model_id}")
        print(f"   Detections: {len(detections)}")
        print(f"   Actions: {actions[:3]}...")  # Première actions
    
    detector.add_detection_callback(detection_callback)
    detector.add_mitigation_callback(mitigation_callback)
    
    # Simulation de données pour différents créateurs
    creator_models = [
        (CreatorModelType.MUSICIAN_AUDIO_CLASSIFIER, "musician_audio_model"),
        (CreatorModelType.BLOGGER_SENTIMENT_ANALYZER, "blogger_sentiment_model"),
        (CreatorModelType.PHOTOGRAPHER_IMAGE_CLASSIFIER, "photographer_vision_model"),
        (CreatorModelType.INFLUENCER_ENGAGEMENT_PREDICTOR, "influencer_analytics_model"),
        (CreatorModelType.COMEDIAN_HUMOR_CLASSIFIER, "comedian_nlp_model")
    ]
    
    # Établissement des baselines
    print("🔒 Establishing security baselines...")
    for model_type, model_id in creator_models:
        # Simulation de données de validation
        np.random.seed(42)
        validation_data = np.random.randn(1000, 20)  # 1000 samples, 20 features
        validation_labels = np.random.choice([0, 1], size=1000, p=[0.6, 0.4])
        model_predictions = np.random.choice([0, 1], size=1000, p=[0.65, 0.35])  # Légèrement différent
        
        baseline = await detector.establish_security_baseline(
            model_id=model_id,
            model_type=model_type,
            validation_data=validation_data,
            validation_labels=validation_labels,
            model_predictions=model_predictions
        )
        print(f"   ✅ Baseline established for {model_id}")
    
    # Simulation de scan avec données empoisonnées
    print(f"\n🔍 Scanning models for poisoning...")
    for model_type, model_id in creator_models:
        # Simulation de données potentiellement empoisonnées
        np.random.seed(123)  # Seed différent pour variation
        
        # Injection de quelques samples suspects
        current_data = np.random.randn(800, 20)
        # Ajout de samples avec patterns suspects (pour backdoor detection)
        poisoned_samples = np.ones((50, 20)) * 5  # Pattern uniforme suspect
        current_data = np.vstack([current_data, poisoned_samples])
        
        current_labels = np.random.choice([0, 1], size=850, p=[0.7, 0.3])  # Distribution différente
        current_predictions = np.random.choice([0, 1], size=850, p=[0.5, 0.5])  # Performance dégradée
        
        print(f"\n🔍 Scanning {model_id}...")
        detections = await detector.scan_model_for_poisoning(
            model_id=model_id,
            model_type=model_type,
            current_data=current_data,
            current_labels=current_labels,
            current_predictions=current_predictions
        )
        
        print(f"   Found {len(detections)} potential threats")
        for detection in detections:
            print(f"   - {detection.poisoning_type.value}: {detection.threat_level.value}")
    
    # Génération de rapports de sécurité
    print(f"\n📋 Security Reports:")
    for model_type, model_id in creator_models[:2]:  # Première 2 pour la démo
        report = await detector.get_security_report(model_id)
        print(f"\n🔒 Report for {model_id}:")
        print(f"   Health Status: {report['health_status']}")
        print(f"   Total Detections: {report['total_detections']}")
        if 'health_score' in report:
            print(f"   Health Score: {report['health_score']:.3f}")
        if 'attack_types_detected' in report:
            print(f"   Attack Types: {list(report['attack_types_detected'].keys())}")
        if report['security_recommendations']:
            print(f"   Recommendations: {report['security_recommendations'][0]}")
    
    print(f"\n✅ ModelPoisoningDetector demonstration completed")


if __name__ == "__main__":
    asyncio.run(main())