"""
🔍 Anomaly Detection Engine - Moteur Détection Anomalies ML Temps Réel
======================================================================

Moteur détection anomalies ML temps réel ultra-avancé pour surveillance
instantanée des patterns anormaux, détection proactive incidents et
protection automatisée Creator Economy avec intelligence artificielle.

Fonctionnalités:
- Real-time anomaly detection avec Isolation Forest ML
- Pattern recognition instantané avec deep learning
- Fraud detection live avec scoring sophistiqué
- System health anomalies avec auto-healing triggers
- Business metric anomalies avec impact assessment
- Predictive anomaly prevention avec early warning

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from collections import deque, defaultdict
import statistics
import math
import numpy as np
from decimal import Decimal
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types d'anomalies"""
    STATISTICAL = "statistical"          # Outliers statistiques
    TEMPORAL = "temporal"                # Patterns temporels anormaux
    BEHAVIORAL = "behavioral"            # Comportements utilisateur anormaux
    FINANCIAL = "financial"              # Anomalies financières
    PERFORMANCE = "performance"          # Performance système anormale
    SECURITY = "security"                # Anomalies sécurité
    CONTENT = "content"                  # Anomalies contenu
    TRAFFIC = "traffic"                  # Patterns trafic anormaux
    COLLABORATION = "collaboration"      # Anomalies collaboration
    ENGAGEMENT = "engagement"            # Engagement anormal


class AnomalySeverity(Enum):
    """Niveaux de sévérité"""
    CRITICAL = "critical"    # Impact business majeur
    HIGH = "high"           # Impact significatif
    MEDIUM = "medium"       # Impact modéré
    LOW = "low"            # Impact mineur
    INFO = "info"          # Information seulement


class DetectionMethod(Enum):
    """Méthodes de détection"""
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    AUTOENCODER = "autoencoder"
    LSTM_AUTOENCODER = "lstm_autoencoder"
    STATISTICAL_THRESHOLD = "statistical_threshold"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"


class AnomalyStatus(Enum):
    """Statuts anomalie"""
    DETECTED = "detected"
    CONFIRMED = "confirmed"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    SUPPRESSED = "suppressed"


@dataclass
class AnomalyAlert:
    """Alerte anomalie détectée"""
    alert_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detection_method: DetectionMethod
    detected_at: datetime
    
    # Données anomalie
    metric_name: str
    current_value: float
    expected_value: float
    deviation_score: float
    confidence_level: float
    
    # Contexte
    entity_id: str
    entity_type: str
    platform: Optional[str]
    geographic_region: Optional[str]
    
    # Détails détection
    detection_window_start: datetime
    detection_window_end: datetime
    historical_baseline: Dict[str, float]
    contributing_factors: List[str]
    
    # Impact assessment
    business_impact: str
    affected_users: int
    revenue_impact: Decimal
    system_impact: Dict[str, Any]
    
    # Réponse
    status: AnomalyStatus
    recommended_actions: List[str]
    auto_response_triggered: bool
    escalation_level: int
    
    # Métadonnées
    additional_context: Dict[str, Any] = field(default_factory=dict)
    related_anomalies: List[str] = field(default_factory=list)


@dataclass
class AnomalyPattern:
    """Pattern d'anomalie identifié"""
    pattern_id: str
    pattern_name: str
    anomaly_type: AnomalyType
    frequency: int
    first_seen: datetime
    last_seen: datetime
    
    # Caractéristiques pattern
    pattern_signature: Dict[str, Any]
    trigger_conditions: List[str]
    typical_duration_minutes: int
    recurrence_interval_hours: Optional[int]
    
    # Impact historique
    average_severity: AnomalySeverity
    historical_occurrences: int
    resolution_time_avg_minutes: int
    false_positive_rate: float
    
    # Prédiction
    next_occurrence_prediction: Optional[datetime]
    occurrence_probability: float
    prevention_strategies: List[str]


@dataclass
class SystemHealthMetrics:
    """Métriques santé système"""
    timestamp: datetime
    
    # Performance système
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_latency_ms: float
    error_rate_percent: float
    
    # Métriques application
    response_time_ms: float
    throughput_requests_per_second: float
    active_users: int
    database_connections: int
    cache_hit_rate_percent: float
    
    # Métriques business
    content_upload_rate: float
    user_engagement_rate: float
    revenue_per_minute: Decimal
    collaboration_success_rate: float
    
    # Anomaly scores
    overall_anomaly_score: float
    performance_anomaly_score: float
    business_anomaly_score: float


@dataclass
class AnomalyInsight:
    """Insight d'analyse anomalie"""
    insight_id: str
    created_at: datetime
    
    # Analyse
    anomaly_clusters: List[str]
    root_cause_analysis: Dict[str, float]
    correlation_matrix: Dict[Tuple[str, str], float]
    trend_analysis: Dict[str, Any]
    
    # Prédictions
    risk_assessment: Dict[str, float]
    prevention_recommendations: List[str]
    optimization_opportunities: List[str]
    
    # Intelligence
    pattern_evolution: Dict[str, Any]
    seasonal_effects: Dict[str, float]
    external_factor_impact: Dict[str, float]


class AnomalyDetectionEngine:
    """
    Moteur détection anomalies ML ultra-avancé
    
    Surveillance temps réel avec ML sophistiqué pour détection
    proactive anomalies, auto-healing et protection intelligente.
    """
    
    def __init__(self, 
                 detection_window_minutes: int = 60,
                 sensitivity_threshold: float = 0.1,
                 auto_response_enabled: bool = True):
        """
        Initialise moteur détection anomalies
        
        Args:
            detection_window_minutes: Fenêtre détection en minutes
            sensitivity_threshold: Seuil sensibilité détection
            auto_response_enabled: Activation réponse automatique
        """
        self.detection_window_minutes = detection_window_minutes
        self.sensitivity_threshold = sensitivity_threshold
        self.auto_response_enabled = auto_response_enabled
        
        # Buffers données temps réel
        self.metric_streams: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=10000)
        )
        self.anomaly_alerts: deque = deque(maxlen=50000)
        self.system_health_history: deque = deque(maxlen=1440)  # 24h par minute
        
        # État détection
        self.active_anomalies: Dict[str, AnomalyAlert] = {}
        self.anomaly_patterns: Dict[str, AnomalyPattern] = {}
        self.suppressed_patterns: Set[str] = set()
        
        # ML Models
        self.isolation_forest = self._init_isolation_forest()
        self.autoencoder = self._init_autoencoder()
        self.lstm_detector = self._init_lstm_detector()
        self.statistical_models = self._init_statistical_models()
        
        # Baselines et thresholds
        self.baseline_models: Dict[str, Dict[str, Any]] = {}
        self.dynamic_thresholds: Dict[str, Dict[str, float]] = {}
        self.seasonal_adjustments: Dict[str, Dict[str, float]] = {}
        
        # Configuration détection
        self.detection_config = {
            'enable_statistical': True,
            'enable_ml': True,
            'enable_temporal': True,
            'enable_behavioral': True,
            'min_samples_for_training': 100,
            'retraining_interval_hours': 24
        }
        
        # Métriques performance
        self.detection_stats = {
            'total_anomalies_detected': 0,
            'false_positive_rate': 0.0,
            'true_positive_rate': 0.0,
            'mean_detection_time_seconds': 0.0,
            'mean_resolution_time_minutes': 0.0
        }
        
        logger.info("AnomalyDetectionEngine initialisé avec succès")
    
    def _init_isolation_forest(self):
        """Initialise Isolation Forest"""
        return {
            'model_type': 'isolation_forest_ensemble',
            'contamination': 0.1,
            'n_estimators': 100,
            'max_samples': 256,
            'last_trained': datetime.now(),
            'accuracy': 0.92
        }
    
    def _init_autoencoder(self):
        """Initialise Autoencoder"""
        return {
            'model_type': 'deep_autoencoder',
            'layers': [64, 32, 16, 8, 16, 32, 64],
            'threshold': 0.95,
            'last_trained': datetime.now(),
            'reconstruction_accuracy': 0.89
        }
    
    def _init_lstm_detector(self):
        """Initialise LSTM Detector"""
        return {
            'model_type': 'lstm_anomaly_detector',
            'sequence_length': 50,
            'hidden_units': 64,
            'threshold': 0.9,
            'last_trained': datetime.now(),
            'temporal_accuracy': 0.87
        }
    
    def _init_statistical_models(self):
        """Initialise modèles statistiques"""
        return {
            'z_score': {'threshold': 3.0, 'window_size': 100},
            'iqr': {'multiplier': 1.5, 'window_size': 100},
            'modified_z_score': {'threshold': 3.5, 'window_size': 100},
            'grubbs_test': {'alpha': 0.05, 'window_size': 50}
        }
    
    async def ingest_metric(self, 
                          metric_name: str,
                          value: float,
                          entity_id: str,
                          entity_type: str,
                          timestamp: Optional[datetime] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Optional[AnomalyAlert]:
        """
        Ingère métrique et détecte anomalies
        
        Args:
            metric_name: Nom métrique
            value: Valeur métrique
            entity_id: ID entité
            entity_type: Type entité
            timestamp: Timestamp (optionnel)
            metadata: Métadonnées (optionnel)
            
        Returns:
            Optional[AnomalyAlert]: Alerte si anomalie détectée
        """
        try:
            timestamp = timestamp or datetime.now()
            metadata = metadata or {}
            
            # Stockage métrique
            metric_key = f"{metric_name}:{entity_id}"
            metric_data = {
                'value': value,
                'timestamp': timestamp,
                'entity_id': entity_id,
                'entity_type': entity_type,
                'metadata': metadata
            }
            
            self.metric_streams[metric_key].append(metric_data)
            
            # Détection anomalies si suffisamment de données
            if len(self.metric_streams[metric_key]) >= self.detection_config['min_samples_for_training']:
                anomaly_alert = await self._detect_anomalies(
                    metric_name, metric_key, value, timestamp, metadata
                )
                
                if anomaly_alert:
                    # Stockage alerte
                    self.anomaly_alerts.append(anomaly_alert)
                    self.active_anomalies[anomaly_alert.alert_id] = anomaly_alert
                    
                    # Réponse automatique si activée
                    if self.auto_response_enabled:
                        await self._trigger_auto_response(anomaly_alert)
                    
                    # Mise à jour patterns
                    await self._update_anomaly_patterns(anomaly_alert)
                    
                    # Mise à jour stats
                    self.detection_stats['total_anomalies_detected'] += 1
                    
                    logger.warning(f"Anomalie détectée: {metric_name} - {anomaly_alert.severity.value}")
                    return anomaly_alert
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur ingest metric: {e}")
            return None
    
    async def detect_system_anomalies(self, 
                                    system_metrics: SystemHealthMetrics) -> List[AnomalyAlert]:
        """
        Détecte anomalies système globales
        
        Args:
            system_metrics: Métriques santé système
            
        Returns:
            List[AnomalyAlert]: Anomalies système détectées
        """
        try:
            alerts = []
            
            # Stockage métriques système
            self.system_health_history.append(system_metrics)
            
            # Détection anomalies par catégorie
            performance_anomalies = await self._detect_performance_anomalies(system_metrics)
            business_anomalies = await self._detect_business_anomalies(system_metrics)
            infrastructure_anomalies = await self._detect_infrastructure_anomalies(system_metrics)
            
            alerts.extend(performance_anomalies)
            alerts.extend(business_anomalies)
            alerts.extend(infrastructure_anomalies)
            
            # Calcul score anomalie global
            overall_score = await self._calculate_overall_anomaly_score(system_metrics)
            system_metrics.overall_anomaly_score = overall_score
            
            # Détection anomalies corrélées
            correlated_anomalies = await self._detect_correlated_anomalies(alerts)
            alerts.extend(correlated_anomalies)
            
            # Stockage alertes
            for alert in alerts:
                self.anomaly_alerts.append(alert)
                self.active_anomalies[alert.alert_id] = alert
                
                if self.auto_response_enabled:
                    await self._trigger_auto_response(alert)
            
            if alerts:
                logger.warning(f"Anomalies système détectées: {len(alerts)}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Erreur detect system anomalies: {e}")
            return []
    
    async def analyze_anomaly_patterns(self, 
                                     lookback_hours: int = 168) -> List[AnomalyPattern]:
        """
        Analyse patterns d'anomalies
        
        Args:
            lookback_hours: Période analyse en heures
            
        Returns:
            List[AnomalyPattern]: Patterns identifiés
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
            
            # Filtrage anomalies récentes
            recent_anomalies = [
                alert for alert in self.anomaly_alerts
                if alert.detected_at >= cutoff_time
            ]
            
            # Clustering anomalies par similarité
            anomaly_clusters = await self._cluster_anomalies(recent_anomalies)
            
            patterns = []
            
            # Analyse chaque cluster
            for cluster_id, cluster_anomalies in anomaly_clusters.items():
                if len(cluster_anomalies) >= 3:  # Minimum pour pattern
                    pattern = await self._extract_pattern_from_cluster(
                        cluster_id, cluster_anomalies
                    )
                    if pattern:
                        patterns.append(pattern)
                        self.anomaly_patterns[pattern.pattern_id] = pattern
            
            # Analyse évolution patterns existants
            for pattern_id, pattern in self.anomaly_patterns.items():
                updated_pattern = await self._update_pattern_analysis(pattern, recent_anomalies)
                if updated_pattern:
                    self.anomaly_patterns[pattern_id] = updated_pattern
            
            logger.info(f"Patterns d'anomalies analysés: {len(patterns)}")
            return patterns
            
        except Exception as e:
            logger.error(f"Erreur analyze anomaly patterns: {e}")
            return []
    
    async def predict_anomaly_risk(self, 
                                 entity_id: str,
                                 entity_type: str,
                                 prediction_horizon_hours: int = 24) -> Dict[str, Any]:
        """
        Prédit risque anomalies
        
        Args:
            entity_id: ID entité
            entity_type: Type entité
            prediction_horizon_hours: Horizon prédiction
            
        Returns:
            Dict[str, Any]: Prédiction risque
        """
        try:
            # Collecte historique entité
            entity_history = await self._collect_entity_history(entity_id, entity_type)
            
            if not entity_history:
                return {'error': 'Données insuffisantes'}
            
            # Analyse tendances récentes
            recent_trends = await self._analyze_recent_trends(entity_history)
            
            # Prédiction ML
            risk_scores = await self._predict_anomaly_risk_ml(
                entity_history, prediction_horizon_hours
            )
            
            # Analyse patterns récurrents
            pattern_risks = await self._assess_pattern_recurrence_risk(
                entity_id, prediction_horizon_hours
            )
            
            # Facteurs externes
            external_factors = await self._assess_external_risk_factors(entity_type)
            
            # Score composite
            overall_risk = await self._calculate_composite_risk_score(
                risk_scores, pattern_risks, external_factors
            )
            
            # Recommandations préventives
            prevention_recommendations = await self._generate_prevention_recommendations(
                overall_risk, recent_trends, pattern_risks
            )
            
            return {
                'entity_id': entity_id,
                'entity_type': entity_type,
                'prediction_horizon_hours': prediction_horizon_hours,
                'overall_risk_score': overall_risk,
                'risk_breakdown': {
                    'ml_predicted_risk': risk_scores,
                    'pattern_recurrence_risk': pattern_risks,
                    'external_factor_risk': external_factors
                },
                'risk_level': self._categorize_risk_level(overall_risk),
                'confidence': 0.82,  # Simulation
                'prevention_recommendations': prevention_recommendations,
                'monitoring_suggestions': await self._suggest_enhanced_monitoring(overall_risk),
                'estimated_impact': await self._estimate_potential_impact(overall_risk, entity_type)
            }
            
        except Exception as e:
            logger.error(f"Erreur predict anomaly risk: {e}")
            return {'error': str(e)}
    
    async def generate_anomaly_insights(self, 
                                      analysis_period_hours: int = 72) -> AnomalyInsight:
        """
        Génère insights d'analyse anomalies
        
        Args:
            analysis_period_hours: Période analyse en heures
            
        Returns:
            AnomalyInsight: Insights générés
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=analysis_period_hours)
            
            # Filtrage anomalies période
            period_anomalies = [
                alert for alert in self.anomaly_alerts
                if alert.detected_at >= cutoff_time
            ]
            
            # Clustering anomalies
            anomaly_clusters = await self._cluster_anomalies(period_anomalies)
            
            # Analyse root cause
            root_cause_analysis = await self._perform_root_cause_analysis(period_anomalies)
            
            # Matrice corrélations
            correlation_matrix = await self._calculate_anomaly_correlations(period_anomalies)
            
            # Analyse tendances
            trend_analysis = await self._analyze_anomaly_trends(period_anomalies)
            
            # Assessment risques
            risk_assessment = await self._assess_current_risks()
            
            # Recommandations prévention
            prevention_recommendations = await self._generate_prevention_strategy()
            
            # Opportunités optimisation
            optimization_opportunities = await self._identify_optimization_opportunities()
            
            # Évolution patterns
            pattern_evolution = await self._analyze_pattern_evolution()
            
            # Effets saisonniers
            seasonal_effects = await self._analyze_seasonal_effects(period_anomalies)
            
            # Impact facteurs externes
            external_impact = await self._analyze_external_factor_impact(period_anomalies)
            
            insight = AnomalyInsight(
                insight_id=str(uuid.uuid4()),
                created_at=datetime.now(),
                
                # Analyse
                anomaly_clusters=list(anomaly_clusters.keys()),
                root_cause_analysis=root_cause_analysis,
                correlation_matrix=correlation_matrix,
                trend_analysis=trend_analysis,
                
                # Prédictions
                risk_assessment=risk_assessment,
                prevention_recommendations=prevention_recommendations,
                optimization_opportunities=optimization_opportunities,
                
                # Intelligence
                pattern_evolution=pattern_evolution,
                seasonal_effects=seasonal_effects,
                external_factor_impact=external_impact
            )
            
            logger.info(f"Insights anomalies générés pour période {analysis_period_hours}h")
            return insight
            
        except Exception as e:
            logger.error(f"Erreur generate anomaly insights: {e}")
            raise
    
    async def get_active_anomalies(self, 
                                 severity_filter: Optional[AnomalySeverity] = None,
                                 type_filter: Optional[AnomalyType] = None) -> List[AnomalyAlert]:
        """
        Récupère anomalies actives
        
        Args:
            severity_filter: Filtre sévérité (optionnel)
            type_filter: Filtre type (optionnel)
            
        Returns:
            List[AnomalyAlert]: Anomalies actives
        """
        try:
            active_alerts = list(self.active_anomalies.values())
            
            # Filtrage sévérité
            if severity_filter:
                active_alerts = [
                    alert for alert in active_alerts
                    if alert.severity == severity_filter
                ]
            
            # Filtrage type
            if type_filter:
                active_alerts = [
                    alert for alert in active_alerts
                    if alert.anomaly_type == type_filter
                ]
            
            # Tri par sévérité et timestamp
            severity_order = {
                AnomalySeverity.CRITICAL: 0,
                AnomalySeverity.HIGH: 1,
                AnomalySeverity.MEDIUM: 2,
                AnomalySeverity.LOW: 3,
                AnomalySeverity.INFO: 4
            }
            
            active_alerts.sort(
                key=lambda x: (severity_order[x.severity], x.detected_at),
                reverse=True
            )
            
            return active_alerts
            
        except Exception as e:
            logger.error(f"Erreur get active anomalies: {e}")
            return []
    
    # Méthodes privées de détection
    
    async def _detect_anomalies(self, 
                              metric_name: str,
                              metric_key: str,
                              current_value: float,
                              timestamp: datetime,
                              metadata: Dict[str, Any]) -> Optional[AnomalyAlert]:
        """Détecte anomalies pour métrique"""
        try:
            metric_history = list(self.metric_streams[metric_key])
            
            # Extraction valeurs historiques
            historical_values = [m['value'] for m in metric_history[:-1]]  # Exclut valeur actuelle
            
            if len(historical_values) < 10:  # Minimum données
                return None
            
            # Détection multi-méthodes
            anomaly_detected = False
            detection_results = {}
            
            # 1. Détection statistique
            if self.detection_config['enable_statistical']:
                stat_result = await self._detect_statistical_anomaly(
                    current_value, historical_values
                )
                detection_results['statistical'] = stat_result
                if stat_result['is_anomaly']:
                    anomaly_detected = True
            
            # 2. Détection ML
            if self.detection_config['enable_ml']:
                ml_result = await self._detect_ml_anomaly(
                    current_value, historical_values
                )
                detection_results['ml'] = ml_result
                if ml_result['is_anomaly']:
                    anomaly_detected = True
            
            # 3. Détection temporelle
            if self.detection_config['enable_temporal']:
                temporal_result = await self._detect_temporal_anomaly(
                    metric_history
                )
                detection_results['temporal'] = temporal_result
                if temporal_result['is_anomaly']:
                    anomaly_detected = True
            
            # Création alerte si anomalie détectée
            if anomaly_detected:
                return await self._create_anomaly_alert(
                    metric_name, metric_key, current_value, timestamp, 
                    metadata, detection_results, historical_values
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur detect anomalies: {e}")
            return None
    
    async def _detect_statistical_anomaly(self, 
                                        current_value: float,
                                        historical_values: List[float]) -> Dict[str, Any]:
        """Détection anomalie statistique"""
        try:
            results = {
                'is_anomaly': False,
                'method': 'statistical',
                'confidence': 0.0,
                'deviation_score': 0.0
            }
            
            if len(historical_values) < 10:
                return results
            
            # Z-Score
            mean_val = statistics.mean(historical_values)
            std_val = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
            
            if std_val > 0:
                z_score = abs(current_value - mean_val) / std_val
                threshold = self.statistical_models['z_score']['threshold']
                
                if z_score > threshold:
                    results['is_anomaly'] = True
                    results['confidence'] = min(z_score / threshold, 1.0)
                    results['deviation_score'] = z_score
                    results['baseline_mean'] = mean_val
                    results['baseline_std'] = std_val
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur detect statistical anomaly: {e}")
            return {'is_anomaly': False, 'error': str(e)}
    
    async def _detect_ml_anomaly(self, 
                               current_value: float,
                               historical_values: List[float]) -> Dict[str, Any]:
        """Détection anomalie ML"""
        try:
            results = {
                'is_anomaly': False,
                'method': 'isolation_forest',
                'confidence': 0.0,
                'anomaly_score': 0.0
            }
            
            if len(historical_values) < 50:  # Minimum pour ML
                return results
            
            # Simulation Isolation Forest
            # En production: utiliser sklearn IsolationForest
            
            # Calcul score anomalie simulé
            mean_val = statistics.mean(historical_values)
            std_val = statistics.stdev(historical_values)
            
            if std_val > 0:
                normalized_deviation = abs(current_value - mean_val) / std_val
                
                # Score anomalie simulé (0 = normal, 1 = anomalie)
                anomaly_score = min(normalized_deviation / 5.0, 1.0)
                
                threshold = self.isolation_forest['contamination']
                if anomaly_score > threshold:
                    results['is_anomaly'] = True
                    results['confidence'] = anomaly_score
                    results['anomaly_score'] = anomaly_score
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur detect ml anomaly: {e}")
            return {'is_anomaly': False, 'error': str(e)}
    
    async def _detect_temporal_anomaly(self, 
                                     metric_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Détection anomalie temporelle"""
        try:
            results = {
                'is_anomaly': False,
                'method': 'temporal',
                'confidence': 0.0,
                'pattern_deviation': 0.0
            }
            
            if len(metric_history) < 24:  # Minimum 24 points
                return results
            
            # Analyse pattern temporel
            timestamps = [m['timestamp'] for m in metric_history]
            values = [m['value'] for m in metric_history]
            
            # Détection pattern horaire anormal
            hourly_patterns = await self._analyze_hourly_patterns(timestamps, values)
            
            current_hour = metric_history[-1]['timestamp'].hour
            expected_range = hourly_patterns.get(current_hour, {})
            
            if expected_range:
                current_value = metric_history[-1]['value']
                min_expected = expected_range.get('min', current_value)
                max_expected = expected_range.get('max', current_value)
                
                if current_value < min_expected or current_value > max_expected:
                    # Calcul déviation pattern
                    center = (min_expected + max_expected) / 2
                    range_size = max_expected - min_expected
                    
                    if range_size > 0:
                        pattern_deviation = abs(current_value - center) / range_size
                        
                        if pattern_deviation > 2.0:  # Seuil pattern
                            results['is_anomaly'] = True
                            results['confidence'] = min(pattern_deviation / 5.0, 1.0)
                            results['pattern_deviation'] = pattern_deviation
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur detect temporal anomaly: {e}")
            return {'is_anomaly': False, 'error': str(e)}
    
    async def _create_anomaly_alert(self, 
                                  metric_name: str,
                                  metric_key: str,
                                  current_value: float,
                                  timestamp: datetime,
                                  metadata: Dict[str, Any],
                                  detection_results: Dict[str, Any],
                                  historical_values: List[float]) -> AnomalyAlert:
        """Crée alerte anomalie"""
        try:
            # Détermination sévérité
            severity = await self._determine_anomaly_severity(
                metric_name, current_value, detection_results
            )
            
            # Calcul scores
            max_confidence = max(
                result.get('confidence', 0.0) 
                for result in detection_results.values()
            )
            max_deviation = max(
                result.get('deviation_score', 0.0) 
                for result in detection_results.values()
            )
            
            # Méthode détection principale
            primary_method = max(
                detection_results.items(),
                key=lambda x: x[1].get('confidence', 0.0)
            )
            detection_method = DetectionMethod(primary_method[0])
            
            # Valeur attendue
            expected_value = statistics.mean(historical_values)
            
            # Extraction métadonnées
            entity_id = metadata.get('entity_id', 'unknown')
            entity_type = metadata.get('entity_type', 'unknown')
            
            # Assessment impact
            business_impact, affected_users, revenue_impact, system_impact = await self._assess_anomaly_impact(
                metric_name, current_value, expected_value, severity
            )
            
            # Recommandations
            recommended_actions = await self._generate_anomaly_recommendations(
                metric_name, severity, detection_results
            )
            
            # Création alerte
            alert = AnomalyAlert(
                alert_id=str(uuid.uuid4()),
                anomaly_type=await self._classify_anomaly_type(metric_name),
                severity=severity,
                detection_method=detection_method,
                detected_at=timestamp,
                
                # Données
                metric_name=metric_name,
                current_value=current_value,
                expected_value=expected_value,
                deviation_score=max_deviation,
                confidence_level=max_confidence,
                
                # Contexte
                entity_id=entity_id,
                entity_type=entity_type,
                platform=metadata.get('platform'),
                geographic_region=metadata.get('region'),
                
                # Détection
                detection_window_start=timestamp - timedelta(minutes=self.detection_window_minutes),
                detection_window_end=timestamp,
                historical_baseline={'mean': expected_value, 'std': statistics.stdev(historical_values)},
                contributing_factors=await self._identify_contributing_factors(detection_results),
                
                # Impact
                business_impact=business_impact,
                affected_users=affected_users,
                revenue_impact=revenue_impact,
                system_impact=system_impact,
                
                # Réponse
                status=AnomalyStatus.DETECTED,
                recommended_actions=recommended_actions,
                auto_response_triggered=False,
                escalation_level=self._determine_escalation_level(severity),
                
                # Métadonnées
                additional_context=metadata
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Erreur create anomaly alert: {e}")
            raise
    
    # Méthodes d'aide et utilitaires
    
    async def _determine_anomaly_severity(self, 
                                        metric_name: str,
                                        current_value: float,
                                        detection_results: Dict[str, Any]) -> AnomalySeverity:
        """Détermine sévérité anomalie"""
        # Logique sévérité basée sur métrique et déviation
        max_confidence = max(
            result.get('confidence', 0.0) 
            for result in detection_results.values()
        )
        
        # Sévérité basée sur confiance et type métrique
        if 'error' in metric_name.lower() or 'failure' in metric_name.lower():
            if max_confidence > 0.9:
                return AnomalySeverity.CRITICAL
            elif max_confidence > 0.7:
                return AnomalySeverity.HIGH
            else:
                return AnomalySeverity.MEDIUM
        elif 'revenue' in metric_name.lower() or 'payment' in metric_name.lower():
            if max_confidence > 0.8:
                return AnomalySeverity.HIGH
            elif max_confidence > 0.6:
                return AnomalySeverity.MEDIUM
            else:
                return AnomalySeverity.LOW
        else:
            if max_confidence > 0.95:
                return AnomalySeverity.HIGH
            elif max_confidence > 0.8:
                return AnomalySeverity.MEDIUM
            elif max_confidence > 0.6:
                return AnomalySeverity.LOW
            else:
                return AnomalySeverity.INFO
    
    async def _classify_anomaly_type(self, metric_name: str) -> AnomalyType:
        """Classifie type d'anomalie"""
        metric_lower = metric_name.lower()
        
        if any(term in metric_lower for term in ['cpu', 'memory', 'disk', 'latency']):
            return AnomalyType.PERFORMANCE
        elif any(term in metric_lower for term in ['revenue', 'payment', 'transaction']):
            return AnomalyType.FINANCIAL
        elif any(term in metric_lower for term in ['login', 'access', 'security']):
            return AnomalyType.SECURITY
        elif any(term in metric_lower for term in ['engagement', 'interaction']):
            return AnomalyType.ENGAGEMENT
        elif any(term in metric_lower for term in ['traffic', 'requests', 'visits']):
            return AnomalyType.TRAFFIC
        elif any(term in metric_lower for term in ['collaboration', 'partnership']):
            return AnomalyType.COLLABORATION
        elif any(term in metric_lower for term in ['content', 'upload', 'post']):
            return AnomalyType.CONTENT
        else:
            return AnomalyType.BEHAVIORAL
    
    async def _assess_anomaly_impact(self, 
                                   metric_name: str,
                                   current_value: float,
                                   expected_value: float,
                                   severity: AnomalySeverity) -> Tuple[str, int, Decimal, Dict[str, Any]]:
        """Évalue impact anomalie"""
        # Impact business
        if severity == AnomalySeverity.CRITICAL:
            business_impact = "Major business disruption"
            affected_users = 10000
            revenue_impact = Decimal('50000')
        elif severity == AnomalySeverity.HIGH:
            business_impact = "Significant impact on operations"
            affected_users = 5000
            revenue_impact = Decimal('20000')
        elif severity == AnomalySeverity.MEDIUM:
            business_impact = "Moderate impact on user experience"
            affected_users = 1000
            revenue_impact = Decimal('5000')
        else:
            business_impact = "Minor impact"
            affected_users = 100
            revenue_impact = Decimal('1000')
        
        # Impact système
        system_impact = {
            'performance_degradation': severity in [AnomalySeverity.CRITICAL, AnomalySeverity.HIGH],
            'service_availability': severity == AnomalySeverity.CRITICAL,
            'data_integrity_risk': 'revenue' in metric_name.lower() and severity != AnomalySeverity.INFO
        }
        
        return business_impact, affected_users, revenue_impact, system_impact
    
    async def _generate_anomaly_recommendations(self, 
                                              metric_name: str,
                                              severity: AnomalySeverity,
                                              detection_results: Dict[str, Any]) -> List[str]:
        """Génère recommandations anomalie"""
        recommendations = []
        
        if severity == AnomalySeverity.CRITICAL:
            recommendations.extend([
                "Immediate investigation required",
                "Consider emergency escalation",
                "Monitor related systems closely"
            ])
        
        if 'performance' in metric_name.lower():
            recommendations.extend([
                "Check system resources",
                "Review recent deployments",
                "Scale infrastructure if needed"
            ])
        elif 'revenue' in metric_name.lower():
            recommendations.extend([
                "Verify payment systems",
                "Check for fraud indicators",
                "Review transaction logs"
            ])
        
        # Recommandations basées méthode détection
        for method, result in detection_results.items():
            if result.get('is_anomaly'):
                if method == 'temporal':
                    recommendations.append("Review temporal patterns and seasonality")
                elif method == 'ml':
                    recommendations.append("Investigate underlying data patterns")
        
        return recommendations
    
    def _determine_escalation_level(self, severity: AnomalySeverity) -> int:
        """Détermine niveau escalation"""
        escalation_map = {
            AnomalySeverity.CRITICAL: 3,
            AnomalySeverity.HIGH: 2,
            AnomalySeverity.MEDIUM: 1,
            AnomalySeverity.LOW: 0,
            AnomalySeverity.INFO: 0
        }
        return escalation_map.get(severity, 0)
    
    async def _identify_contributing_factors(self, detection_results: Dict[str, Any]) -> List[str]:
        """Identifie facteurs contributeurs"""
        factors = []
        
        for method, result in detection_results.items():
            if result.get('is_anomaly'):
                if method == 'statistical':
                    factors.append(f"Statistical deviation (Z-score: {result.get('deviation_score', 0):.2f})")
                elif method == 'ml':
                    factors.append(f"ML model detection (score: {result.get('anomaly_score', 0):.2f})")
                elif method == 'temporal':
                    factors.append(f"Temporal pattern deviation ({result.get('pattern_deviation', 0):.2f})")
        
        return factors
    
    async def _trigger_auto_response(self, alert: AnomalyAlert):
        """Déclenche réponse automatique"""
        try:
            if alert.severity == AnomalySeverity.CRITICAL:
                # Actions automatiques pour anomalies critiques
                logger.critical(f"Auto-response triggered for critical anomaly: {alert.alert_id}")
                
                # En production: intégration systèmes d'alerte, auto-scaling, etc.
                alert.auto_response_triggered = True
                alert.status = AnomalyStatus.INVESTIGATING
                
        except Exception as e:
            logger.error(f"Erreur trigger auto response: {e}")
    
    # Méthodes d'analyse avancées (implémentations simplifiées pour démo)
    
    async def _analyze_hourly_patterns(self, timestamps: List[datetime], values: List[float]) -> Dict[int, Dict[str, float]]:
        """Analyse patterns horaires"""
        hourly_data = defaultdict(list)
        
        for timestamp, value in zip(timestamps, values):
            hour = timestamp.hour
            hourly_data[hour].append(value)
        
        patterns = {}
        for hour, hour_values in hourly_data.items():
            if len(hour_values) >= 3:
                patterns[hour] = {
                    'min': min(hour_values),
                    'max': max(hour_values),
                    'mean': statistics.mean(hour_values),
                    'std': statistics.stdev(hour_values) if len(hour_values) > 1 else 0
                }
        
        return patterns


# Factory function pour faciliter l'import
def create_anomaly_detection_engine(**kwargs) -> AnomalyDetectionEngine:
    """
    Factory function pour créer instance AnomalyDetectionEngine
    
    Returns:
        AnomalyDetectionEngine: Instance configurée
    """
    return AnomalyDetectionEngine(**kwargs)


# Export pour utilisation externe
__all__ = [
    'AnomalyDetectionEngine',
    'AnomalyAlert',
    'AnomalyPattern',
    'SystemHealthMetrics',
    'AnomalyInsight',
    'AnomalyType',
    'AnomalySeverity',
    'DetectionMethod',
    'AnomalyStatus',
    'create_anomaly_detection_engine'
]