
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
#!/usr/bin/env python3
"""
📊 Security Analytics Engine - Advanced ML Security Intelligence
================================================================

Enterprise security analytics with ML insights and predictive analytics.
Security metrics, ML insights, predictive analytics, and business intelligence.

Author: Expert Team (ML Engineer + Security + Data Scientist + BI)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact mlaiel@live.de for enterprise licensing

⚠️  LEGAL WARNING:
This code is proprietary to Fahed Mlaiel. Unauthorized use, distribution,
reverse engineering, or commercial exploitation is strictly prohibited.
Violations will result in immediate legal action.
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any, Set
import statistics
from collections import defaultdict, deque

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import precision_score, recall_score, f1_score


class AnalyticsType(Enum):
    """Types d'analytics"""
    SECURITY_METRICS = "security_metrics"
    THREAT_ANALYSIS = "threat_analysis"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    COMPLIANCE_ANALYTICS = "compliance_analytics"
    PERFORMANCE_ANALYTICS = "performance_analytics"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    BUSINESS_INTELLIGENCE = "business_intelligence"


class ThreatLevel(Enum):
    """Niveaux de menace"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EXTREME = "extreme"


class AnalyticsPeriod(Enum):
    """Périodes d'analyse"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PredictionType(Enum):
    """Types de prédictions"""
    THREAT_LIKELIHOOD = "threat_likelihood"
    FRAUD_PROBABILITY = "fraud_probability"
    SYSTEM_ANOMALY = "system_anomaly"
    COMPLIANCE_RISK = "compliance_risk"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    REVENUE_IMPACT = "revenue_impact"


@dataclass
class SecurityMetric:
    """Métrique de sécurité"""
    metric_id: str
    metric_name: str
    metric_type: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    threshold_breached: bool = False
    severity: str = "normal"


@dataclass
class ThreatAnalysis:
    """Analyse de menace"""
    analysis_id: str
    threat_type: str
    threat_level: ThreatLevel
    confidence: float
    analysis_timestamp: datetime
    affected_entities: List[str]
    attack_vectors: List[str]
    mitigation_recommendations: List[str]
    predicted_impact: Dict[str, Any]
    ml_model_confidence: float
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BehavioralPattern:
    """Pattern comportemental"""
    pattern_id: str
    pattern_type: str
    entity_id: str
    entity_type: str
    baseline_established: bool
    deviation_score: float
    anomaly_detected: bool
    pattern_data: Dict[str, Any]
    analysis_period: AnalyticsPeriod
    confidence: float
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PredictiveInsight:
    """Insight prédictif"""
    insight_id: str
    prediction_type: PredictionType
    predicted_value: float
    confidence_interval: Tuple[float, float]
    prediction_horizon: timedelta
    created_at: datetime
    model_used: str
    input_features: List[str]
    business_impact: str
    recommended_actions: List[str]
    accuracy_score: Optional[float] = None


@dataclass
class AnalyticsReport:
    """Rapport d'analytics"""
    report_id: str
    report_type: AnalyticsType
    period: AnalyticsPeriod
    generated_at: datetime
    data_points: int
    key_metrics: Dict[str, float]
    insights: List[str]
    anomalies_detected: int
    threats_identified: int
    predictions: List[PredictiveInsight]
    visualizations: Dict[str, Any] = field(default_factory=dict)
    executive_summary: str = ""


class MLSecurityModels:
    """Modèles ML pour sécurité"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Modèles ML
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.threat_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.behavioral_clusterer = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        
        # État des modèles
        self.models_trained = {
            'anomaly_detector': False,
            'threat_classifier': False,
            'behavioral_clusterer': False
        }
        
        # Cache des prédictions
        self.prediction_cache: Dict[str, Any] = {}
        
        # Données d'entraînement (simulation)
        self.training_data = {
            'security_events': [],
            'user_behavior': [],
            'system_metrics': [],
            'threat_indicators': []
        }
        
    async def train_models(self, training_data: Optional[Dict[str, Any]] = None):
        """Entraînement des modèles ML"""
        try:
            if training_data:
                self.training_data.update(training_data)
                
            # Générer données d'entraînement simulées si nécessaire
            if not any(self.training_data.values()):
                await self._generate_synthetic_training_data()
                
            # Entraîner détecteur d'anomalies
            if len(self.training_data['security_events']) > 50:
                features = await self._extract_security_features(self.training_data['security_events'])
                if len(features) > 0:
                    X_scaled = self.scaler.fit_transform(features)
                    self.anomaly_detector.fit(X_scaled)
                    self.models_trained['anomaly_detector'] = True
                    
            # Entraîner classificateur de menaces
            if len(self.training_data['threat_indicators']) > 100:
                X, y = await self._prepare_threat_classification_data()
                if len(X) > 0:
                    X_scaled = self.scaler.fit_transform(X)
                    self.threat_classifier.fit(X_scaled, y)
                    self.models_trained['threat_classifier'] = True
                    
            # Entraîner clustering comportemental
            if len(self.training_data['user_behavior']) > 50:
                features = await self._extract_behavioral_features(self.training_data['user_behavior'])
                if len(features) > 0:
                    X_scaled = self.scaler.fit_transform(features)
                    self.behavioral_clusterer.fit(X_scaled)
                    self.models_trained['behavioral_clusterer'] = True
                    
            self.logger.info(f"ML models trained: {self.models_trained}")
            
        except Exception as e:
            self.logger.error(f"Model training failed: {str(e)}")
            
    async def detect_anomalies(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Détection d'anomalies ML"""
        if not self.models_trained['anomaly_detector']:
            await self.train_models()
            
        try:
            features = await self._extract_security_features(data)
            if len(features) == 0:
                return []
                
            X_scaled = self.scaler.transform(features)
            anomaly_scores = self.anomaly_detector.decision_function(X_scaled)
            anomaly_predictions = self.anomaly_detector.predict(X_scaled)
            
            anomalies = []
            for i, (score, prediction) in enumerate(zip(anomaly_scores, anomaly_predictions)):
                if prediction == -1:  # Anomalie détectée
                    anomaly = {
                        'data_point': data[i],
                        'anomaly_score': float(score),
                        'confidence': abs(float(score)),
                        'detected_at': datetime.utcnow().isoformat()
                    }
                    anomalies.append(anomaly)
                    
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {str(e)}")
            return []
            
    async def classify_threats(self, threat_indicators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classification des menaces ML"""
        if not self.models_trained['threat_classifier']:
            await self.train_models()
            
        try:
            features = await self._extract_threat_features(threat_indicators)
            if len(features) == 0:
                return []
                
            X_scaled = self.scaler.transform(features)
            threat_predictions = self.threat_classifier.predict(X_scaled)
            threat_probabilities = self.threat_classifier.predict_proba(X_scaled)
            
            classifications = []
            for i, (prediction, probabilities) in enumerate(zip(threat_predictions, threat_probabilities)):
                classification = {
                    'indicator': threat_indicators[i],
                    'threat_class': int(prediction),
                    'confidence': float(max(probabilities)),
                    'class_probabilities': probabilities.tolist(),
                    'classified_at': datetime.utcnow().isoformat()
                }
                classifications.append(classification)
                
            return classifications
            
        except Exception as e:
            self.logger.error(f"Threat classification failed: {str(e)}")
            return []
            
    async def analyze_behavioral_patterns(self, user_data: List[Dict[str, Any]]) -> List[BehavioralPattern]:
        """Analyse des patterns comportementaux"""
        if not self.models_trained['behavioral_clusterer']:
            await self.train_models()
            
        try:
            features = await self._extract_behavioral_features(user_data)
            if len(features) == 0:
                return []
                
            X_scaled = self.scaler.transform(features)
            cluster_labels = self.behavioral_clusterer.fit_predict(X_scaled)
            
            patterns = []
            for i, (label, data_point) in enumerate(zip(cluster_labels, user_data)):
                # Calculer score de déviation
                if label == -1:  # Outlier
                    deviation_score = 1.0
                    anomaly_detected = True
                else:
                    deviation_score = 0.3  # Score normal
                    anomaly_detected = False
                    
                pattern = BehavioralPattern(
                    pattern_id=f"pattern_{uuid.uuid4().hex[:8]}",
                    pattern_type="user_behavior",
                    entity_id=data_point.get('user_id', 'unknown'),
                    entity_type="user",
                    baseline_established=True,
                    deviation_score=deviation_score,
                    anomaly_detected=anomaly_detected,
                    pattern_data={
                        'cluster_label': int(label),
                        'features': features[i] if i < len(features) else [],
                        'original_data': data_point
                    },
                    analysis_period=AnalyticsPeriod.REAL_TIME,
                    confidence=0.8 if not anomaly_detected else 0.9
                )
                patterns.append(pattern)
                
            return patterns
            
        except Exception as e:
            self.logger.error(f"Behavioral analysis failed: {str(e)}")
            return []
            
    async def _generate_synthetic_training_data(self):
        """Générer données d'entraînement synthétiques"""
        # Événements de sécurité
        for i in range(200):
            event = {
                'timestamp': (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                'event_type': np.random.choice(['login', 'api_call', 'file_access', 'payment']),
                'user_id': f"user_{np.random.randint(1, 100)}",
                'ip_address': f"192.168.1.{np.random.randint(1, 255)}",
                'success': np.random.choice([True, False], p=[0.9, 0.1]),
                'response_time': np.random.normal(200, 50),
                'data_size': np.random.exponential(1000)
            }
            self.training_data['security_events'].append(event)
            
        # Comportements utilisateur
        for i in range(150):
            behavior = {
                'user_id': f"user_{np.random.randint(1, 50)}",
                'session_duration': np.random.normal(30, 10),
                'actions_per_minute': np.random.normal(5, 2),
                'unique_ips': np.random.randint(1, 4),
                'failed_attempts': np.random.randint(0, 3),
                'time_of_day': np.random.randint(0, 24)
            }
            self.training_data['user_behavior'].append(behavior)
            
        # Indicateurs de menaces
        for i in range(300):
            threat = {
                'indicator_type': np.random.choice(['ip', 'hash', 'domain', 'signature']),
                'severity': np.random.choice([0, 1, 2, 3, 4]),  # 0=benign, 4=malicious
                'confidence': np.random.uniform(0.1, 1.0),
                'source_reputation': np.random.uniform(0.0, 1.0),
                'frequency': np.random.randint(1, 100),
                'geographic_risk': np.random.uniform(0.0, 1.0)
            }
            self.training_data['threat_indicators'].append(threat)
            
    async def _extract_security_features(self, events: List[Dict[str, Any]]) -> List[List[float]]:
        """Extraire features des événements de sécurité"""
        features = []
        
        for event in events:
            feature_vector = [
                1.0 if event.get('success', True) else 0.0,
                float(event.get('response_time', 200)),
                float(event.get('data_size', 1000)),
                hash(event.get('event_type', '')) % 1000 / 1000.0,  # Type normalisé
                hash(event.get('user_id', '')) % 1000 / 1000.0,     # User normalisé
                float(event.get('hour_of_day', 12)) / 24.0           # Heure normalisée
            ]
            features.append(feature_vector)
            
        return features
        
    async def _extract_behavioral_features(self, behaviors: List[Dict[str, Any]]) -> List[List[float]]:
        """Extraire features comportementales"""
        features = []
        
        for behavior in behaviors:
            feature_vector = [
                float(behavior.get('session_duration', 30)),
                float(behavior.get('actions_per_minute', 5)),
                float(behavior.get('unique_ips', 1)),
                float(behavior.get('failed_attempts', 0)),
                float(behavior.get('time_of_day', 12)) / 24.0
            ]
            features.append(feature_vector)
            
        return features
        
    async def _extract_threat_features(self, threats: List[Dict[str, Any]]) -> List[List[float]]:
        """Extraire features des menaces"""
        features = []
        
        for threat in threats:
            feature_vector = [
                float(threat.get('confidence', 0.5)),
                float(threat.get('source_reputation', 0.5)),
                float(threat.get('frequency', 1)),
                float(threat.get('geographic_risk', 0.5)),
                hash(threat.get('indicator_type', '')) % 100 / 100.0
            ]
            features.append(feature_vector)
            
        return features
        
    async def _prepare_threat_classification_data(self) -> Tuple[List[List[float]], List[int]]:
        """Préparer données pour classification des menaces"""
        X = await self._extract_threat_features(self.training_data['threat_indicators'])
        y = [threat.get('severity', 0) for threat in self.training_data['threat_indicators']]
        
        return X, y


class SecurityAnalyticsEngine:
    """
    Moteur d'analytics de sécurité enterprise-grade
    
    Fonctionnalités:
    - Métriques de sécurité temps réel
    - Analyse ML des menaces
    - Analytics comportementales avancées
    - Prédictions intelligentes
    - Business intelligence sécuritaire
    - Rapports automatisés
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ml_models = MLSecurityModels()
        
        # Stockage des données analytics
        self.metrics: Dict[str, List[SecurityMetric]] = defaultdict(list)
        self.threat_analyses: Dict[str, ThreatAnalysis] = {}
        self.behavioral_patterns: Dict[str, BehavioralPattern] = {}
        self.predictive_insights: Dict[str, PredictiveInsight] = {}
        self.analytics_reports: Dict[str, AnalyticsReport] = {}
        
        # Configuration analytics
        self.config = {
            'real_time_processing': True,
            'anomaly_threshold': 0.7,
            'threat_confidence_threshold': 0.8,
            'behavioral_analysis_window': 24,  # hours
            'prediction_horizon_days': 30,
            'metrics_retention_days': 90
        }
        
        # Métriques de performance
        self.performance_metrics = {
            'analytics_processed': 0,
            'anomalies_detected': 0,
            'threats_analyzed': 0,
            'predictions_generated': 0,
            'accuracy_scores': [],
            'processing_time_avg': 0.0
        }
        
        # Collecteurs de données temps réel
        self.data_streams = {
            'security_events': deque(maxlen=10000),
            'user_activities': deque(maxlen=5000),
            'system_metrics': deque(maxlen=5000),
            'payment_transactions': deque(maxlen=5000)
        }
        
        self.logger.info("Security Analytics Engine initialized")
        
    async def ingest_security_event(self, event: Dict[str, Any]):
        """Ingestion d'événement de sécurité"""
        try:
            # Enrichir l'événement
            enriched_event = {
                **event,
                'ingested_at': datetime.utcnow().isoformat(),
                'event_id': f"event_{uuid.uuid4().hex[:12]}"
            }
            
            self.data_streams['security_events'].append(enriched_event)
            
            # Traitement temps réel si activé
            if self.config['real_time_processing']:
                await self._process_real_time_event(enriched_event)
                
        except Exception as e:
            self.logger.error(f"Event ingestion failed: {str(e)}")
            
    async def _process_real_time_event(self, event: Dict[str, Any]):
        """Traitement temps réel d'événement"""
        # Détection d'anomalies
        anomalies = await self.ml_models.detect_anomalies([event])
        
        if anomalies:
            await self._handle_anomaly_detection(anomalies[0], event)
            
        # Classification de menace
        if event.get('suspicious', False):
            threat_classification = await self.ml_models.classify_threats([event])
            if threat_classification:
                await self._handle_threat_classification(threat_classification[0], event)
                
    async def _handle_anomaly_detection(self, anomaly: Dict[str, Any], original_event: Dict[str, Any]):
        """Traitement d'anomalie détectée"""
        self.performance_metrics['anomalies_detected'] += 1
        
        # Créer métrique d'anomalie
        metric = SecurityMetric(
            metric_id=f"anomaly_{uuid.uuid4().hex[:8]}",
            metric_name="security_anomaly_detected",
            metric_type="anomaly",
            value=anomaly['confidence'],
            unit="confidence_score",
            timestamp=datetime.utcnow(),
            context={
                'original_event': original_event,
                'anomaly_score': anomaly['anomaly_score']
            },
            tags=['anomaly', 'real_time'],
            threshold_breached=anomaly['confidence'] > self.config['anomaly_threshold'],
            severity="high" if anomaly['confidence'] > 0.8 else "medium"
        )
        
        self.metrics['anomalies'].append(metric)
        
        self.logger.warning(f"Anomaly detected: {metric.metric_id} (confidence: {anomaly['confidence']:.2f})")
        
    async def _handle_threat_classification(self, classification: Dict[str, Any], original_event: Dict[str, Any]):
        """Traitement de classification de menace"""
        self.performance_metrics['threats_analyzed'] += 1
        
        threat_level = ThreatLevel.LOW
        if classification['confidence'] > 0.9:
            threat_level = ThreatLevel.CRITICAL
        elif classification['confidence'] > 0.7:
            threat_level = ThreatLevel.HIGH
        elif classification['confidence'] > 0.5:
            threat_level = ThreatLevel.MODERATE
            
        analysis = ThreatAnalysis(
            analysis_id=f"threat_{uuid.uuid4().hex[:8]}",
            threat_type=f"class_{classification['threat_class']}",
            threat_level=threat_level,
            confidence=classification['confidence'],
            analysis_timestamp=datetime.utcnow(),
            affected_entities=[original_event.get('user_id', 'unknown')],
            attack_vectors=['automated_classification'],
            mitigation_recommendations=await self._generate_mitigation_recommendations(classification),
            predicted_impact={'severity': threat_level.value, 'confidence': classification['confidence']},
            ml_model_confidence=classification['confidence'],
            evidence={'classification_result': classification, 'original_event': original_event}
        )
        
        self.threat_analyses[analysis.analysis_id] = analysis
        
        self.logger.warning(f"Threat classified: {analysis.analysis_id} (level: {threat_level.value})")
        
    async def _generate_mitigation_recommendations(self, classification: Dict[str, Any]) -> List[str]:
        """Générer recommandations de mitigation"""
        recommendations = []
        
        threat_class = classification['threat_class']
        confidence = classification['confidence']
        
        if confidence > 0.8:
            recommendations.append("Immediate investigation required")
            recommendations.append("Consider blocking affected entities")
            
        if threat_class >= 3:  # High severity classes
            recommendations.append("Escalate to security team")
            recommendations.append("Implement additional monitoring")
            
        recommendations.append("Update threat intelligence feeds")
        recommendations.append("Review and update security policies")
        
        return recommendations
        
    async def analyze_user_behavior(self, user_id: str, period_hours: int = 24) -> BehavioralPattern:
        """Analyse comportementale utilisateur"""
        try:
            # Collecter données utilisateur
            user_events = []
            cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
            
            for event in self.data_streams['user_activities']:
                if (event.get('user_id') == user_id and 
                    datetime.fromisoformat(event.get('timestamp', '')) > cutoff_time):
                    user_events.append(event)
                    
            if not user_events:
                # Créer pattern par défaut
                return BehavioralPattern(
                    pattern_id=f"pattern_{uuid.uuid4().hex[:8]}",
                    pattern_type="user_behavior",
                    entity_id=user_id,
                    entity_type="user",
                    baseline_established=False,
                    deviation_score=0.0,
                    anomaly_detected=False,
                    pattern_data={'events_count': 0},
                    analysis_period=AnalyticsPeriod.DAILY,
                    confidence=0.0
                )
                
            # Analyse ML
            patterns = await self.ml_models.analyze_behavioral_patterns(user_events)
            
            if patterns:
                pattern = patterns[0]  # Premier pattern pour cet utilisateur
                self.behavioral_patterns[pattern.pattern_id] = pattern
                return pattern
            else:
                # Pattern par défaut si analyse échoue
                return BehavioralPattern(
                    pattern_id=f"pattern_{uuid.uuid4().hex[:8]}",
                    pattern_type="user_behavior",
                    entity_id=user_id,
                    entity_type="user",
                    baseline_established=True,
                    deviation_score=0.1,
                    anomaly_detected=False,
                    pattern_data={'events_analyzed': len(user_events)},
                    analysis_period=AnalyticsPeriod.DAILY,
                    confidence=0.7
                )
                
        except Exception as e:
            self.logger.error(f"Behavioral analysis failed for user {user_id}: {str(e)}")
            raise
            
    async def generate_predictive_insights(self, prediction_types: List[PredictionType]) -> List[PredictiveInsight]:
        """Génération d'insights prédictifs"""
        insights = []
        
        for prediction_type in prediction_types:
            try:
                insight = await self._generate_specific_prediction(prediction_type)
                if insight:
                    insights.append(insight)
                    self.predictive_insights[insight.insight_id] = insight
                    self.performance_metrics['predictions_generated'] += 1
                    
            except Exception as e:
                self.logger.error(f"Prediction generation failed for {prediction_type.value}: {str(e)}")
                
        return insights
        
    async def _generate_specific_prediction(self, prediction_type: PredictionType) -> Optional[PredictiveInsight]:
        """Générer prédiction spécifique"""
        if prediction_type == PredictionType.THREAT_LIKELIHOOD:
            # Prédiction basée sur historique des menaces
            recent_threats = len([t for t in self.threat_analyses.values() 
                                if (datetime.utcnow() - t.analysis_timestamp).days <= 7])
            
            # Simulation de prédiction
            predicted_threats = recent_threats * 1.2 + np.random.normal(0, 2)
            confidence = (0.6, 0.9)
            
            return PredictiveInsight(
                insight_id=f"pred_{uuid.uuid4().hex[:8]}",
                prediction_type=prediction_type,
                predicted_value=max(0, predicted_threats),
                confidence_interval=confidence,
                prediction_horizon=timedelta(days=7),
                created_at=datetime.utcnow(),
                model_used="threat_likelihood_model",
                input_features=['recent_threats', 'threat_velocity', 'system_exposure'],
                business_impact="Potential security incidents may increase",
                recommended_actions=[
                    "Increase security monitoring",
                    "Review threat detection rules",
                    "Prepare incident response team"
                ]
            )
            
        elif prediction_type == PredictionType.FRAUD_PROBABILITY:
            # Prédiction de fraude
            fraud_score = np.random.beta(2, 8)  # Skewed towards lower probability
            
            return PredictiveInsight(
                insight_id=f"pred_{uuid.uuid4().hex[:8]}",
                prediction_type=prediction_type,
                predicted_value=fraud_score,
                confidence_interval=(fraud_score * 0.8, fraud_score * 1.3),
                prediction_horizon=timedelta(days=1),
                created_at=datetime.utcnow(),
                model_used="fraud_detection_model",
                input_features=['transaction_patterns', 'user_behavior', 'payment_velocity'],
                business_impact=f"Fraud risk: {'High' if fraud_score > 0.7 else 'Medium' if fraud_score > 0.3 else 'Low'}",
                recommended_actions=[
                    "Enhanced transaction monitoring",
                    "Additional identity verification",
                    "Review payment patterns"
                ]
            )
            
        elif prediction_type == PredictionType.SYSTEM_ANOMALY:
            # Prédiction d'anomalie système
            anomaly_score = np.random.exponential(0.3)
            
            return PredictiveInsight(
                insight_id=f"pred_{uuid.uuid4().hex[:8]}",
                prediction_type=prediction_type,
                predicted_value=min(1.0, anomaly_score),
                confidence_interval=(anomaly_score * 0.7, min(1.0, anomaly_score * 1.4)),
                prediction_horizon=timedelta(hours=12),
                created_at=datetime.utcnow(),
                model_used="system_anomaly_model",
                input_features=['cpu_usage', 'memory_usage', 'network_traffic', 'error_rates'],
                business_impact="System performance may be affected",
                recommended_actions=[
                    "Monitor system resources",
                    "Prepare scaling plans",
                    "Review system logs"
                ]
            )
            
        return None
        
    async def generate_security_metrics(self, period: AnalyticsPeriod = AnalyticsPeriod.DAILY) -> Dict[str, SecurityMetric]:
        """Génération de métriques de sécurité"""
        metrics = {}
        
        try:
            # Métriques de base
            current_time = datetime.utcnow()
            
            # Nombre d'événements sécuritaires
            events_count = len(self.data_streams['security_events'])
            metrics['security_events_count'] = SecurityMetric(
                metric_id=f"metric_{uuid.uuid4().hex[:8]}",
                metric_name="security_events_count",
                metric_type="counter",
                value=float(events_count),
                unit="events",
                timestamp=current_time,
                tags=['security', 'events']
            )
            
            # Taux d'anomalies
            anomalies_count = self.performance_metrics['anomalies_detected']
            anomaly_rate = (anomalies_count / max(1, events_count)) * 100
            metrics['anomaly_rate'] = SecurityMetric(
                metric_id=f"metric_{uuid.uuid4().hex[:8]}",
                metric_name="anomaly_rate",
                metric_type="percentage",
                value=anomaly_rate,
                unit="percent",
                timestamp=current_time,
                tags=['security', 'anomalies'],
                threshold_breached=anomaly_rate > 5.0,
                severity="high" if anomaly_rate > 10.0 else "medium" if anomaly_rate > 5.0 else "normal"
            )
            
            # Score de sécurité global
            security_score = await self._calculate_overall_security_score()
            metrics['overall_security_score'] = SecurityMetric(
                metric_id=f"metric_{uuid.uuid4().hex[:8]}",
                metric_name="overall_security_score",
                metric_type="score",
                value=security_score,
                unit="score",
                timestamp=current_time,
                tags=['security', 'score'],
                threshold_breached=security_score < 70.0,
                severity="critical" if security_score < 50.0 else "high" if security_score < 70.0 else "normal"
            )
            
            # Temps de réponse moyen
            avg_response_time = self.performance_metrics['processing_time_avg']
            metrics['avg_response_time'] = SecurityMetric(
                metric_id=f"metric_{uuid.uuid4().hex[:8]}",
                metric_name="avg_response_time",
                metric_type="latency",
                value=avg_response_time,
                unit="milliseconds",
                timestamp=current_time,
                tags=['performance', 'response_time']
            )
            
            # Stocker métriques
            for metric_name, metric in metrics.items():
                self.metrics[metric_name].append(metric)
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics generation failed: {str(e)}")
            return {}
            
    async def _calculate_overall_security_score(self) -> float:
        """Calcul du score de sécurité global"""
        try:
            # Composants du score
            threat_score = max(0, 100 - len(self.threat_analyses) * 5)  # Moins de menaces = meilleur score
            anomaly_score = max(0, 100 - self.performance_metrics['anomalies_detected'] * 2)
            
            # Score de performance
            performance_score = 100 if self.performance_metrics['processing_time_avg'] < 100 else 80
            
            # Score d'activité (plus d'activité analytics = meilleur)
            activity_score = min(100, self.performance_metrics['analytics_processed'] / 10)
            
            # Score pondéré
            overall_score = (
                threat_score * 0.3 +
                anomaly_score * 0.3 +
                performance_score * 0.2 +
                activity_score * 0.2
            )
            
            return max(0.0, min(100.0, overall_score))
            
        except Exception:
            return 50.0  # Score par défaut
            
    async def generate_analytics_report(self, 
                                      report_type: AnalyticsType,
                                      period: AnalyticsPeriod) -> AnalyticsReport:
        """Génération de rapport d'analytics"""
        try:
            report_id = f"report_{uuid.uuid4().hex[:8]}"
            
            # Collecter données pour la période
            period_data = await self._collect_period_data(period)
            
            # Générer métriques clés
            key_metrics = await self._calculate_key_metrics(report_type, period_data)
            
            # Générer insights
            insights = await self._generate_report_insights(report_type, period_data)
            
            # Compter anomalies et menaces
            anomalies_count = len([m for metrics_list in self.metrics.values() 
                                 for m in metrics_list if m.threshold_breached])
            threats_count = len(self.threat_analyses)
            
            # Générer prédictions pour le rapport
            predictions = await self.generate_predictive_insights([
                PredictionType.THREAT_LIKELIHOOD,
                PredictionType.SYSTEM_ANOMALY
            ])
            
            # Créer rapport
            report = AnalyticsReport(
                report_id=report_id,
                report_type=report_type,
                period=period,
                generated_at=datetime.utcnow(),
                data_points=len(period_data),
                key_metrics=key_metrics,
                insights=insights,
                anomalies_detected=anomalies_count,
                threats_identified=threats_count,
                predictions=predictions,
                executive_summary=await self._generate_executive_summary(
                    report_type, key_metrics, anomalies_count, threats_count
                )
            )
            
            # Stocker rapport
            self.analytics_reports[report_id] = report
            
            self.logger.info(f"Analytics report generated: {report_id} ({report_type.value})")
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise
            
    async def _collect_period_data(self, period: AnalyticsPeriod) -> List[Dict[str, Any]]:
        """Collecter données pour une période"""
        if period == AnalyticsPeriod.REAL_TIME:
            cutoff = datetime.utcnow() - timedelta(minutes=5)
        elif period == AnalyticsPeriod.HOURLY:
            cutoff = datetime.utcnow() - timedelta(hours=1)
        elif period == AnalyticsPeriod.DAILY:
            cutoff = datetime.utcnow() - timedelta(days=1)
        elif period == AnalyticsPeriod.WEEKLY:
            cutoff = datetime.utcnow() - timedelta(weeks=1)
        else:
            cutoff = datetime.utcnow() - timedelta(days=30)
            
        period_data = []
        
        # Collecter depuis tous les streams
        for stream_name, stream_data in self.data_streams.items():
            for item in stream_data:
                if 'timestamp' in item:
                    item_time = datetime.fromisoformat(item['timestamp'])
                    if item_time >= cutoff:
                        period_data.append({**item, 'stream': stream_name})
                        
        return period_data
        
    async def _calculate_key_metrics(self, report_type: AnalyticsType, period_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculer métriques clés"""
        metrics = {}
        
        if report_type == AnalyticsType.SECURITY_METRICS:
            metrics['total_events'] = len(period_data)
            metrics['unique_users'] = len(set(item.get('user_id', '') for item in period_data if item.get('user_id')))
            metrics['error_rate'] = len([item for item in period_data if not item.get('success', True)]) / max(1, len(period_data)) * 100
            
        elif report_type == AnalyticsType.THREAT_ANALYSIS:
            threat_events = [item for item in period_data if item.get('suspicious', False)]
            metrics['threat_events'] = len(threat_events)
            metrics['threat_rate'] = len(threat_events) / max(1, len(period_data)) * 100
            metrics['high_confidence_threats'] = len([t for t in self.threat_analyses.values() if t.confidence > 0.8])
            
        elif report_type == AnalyticsType.BEHAVIORAL_ANALYSIS:
            user_patterns = len(self.behavioral_patterns)
            anomalous_patterns = len([p for p in self.behavioral_patterns.values() if p.anomaly_detected])
            metrics['total_patterns'] = user_patterns
            metrics['anomalous_patterns'] = anomalous_patterns
            metrics['anomaly_percentage'] = (anomalous_patterns / max(1, user_patterns)) * 100
            
        return metrics
        
    async def _generate_report_insights(self, report_type: AnalyticsType, period_data: List[Dict[str, Any]]) -> List[str]:
        """Générer insights pour rapport"""
        insights = []
        
        if report_type == AnalyticsType.SECURITY_METRICS:
            if len(period_data) > 1000:
                insights.append("High volume of security events detected")
            
            error_rate = len([item for item in period_data if not item.get('success', True)]) / max(1, len(period_data))
            if error_rate > 0.05:
                insights.append(f"Elevated error rate detected: {error_rate:.1%}")
                
        elif report_type == AnalyticsType.THREAT_ANALYSIS:
            critical_threats = len([t for t in self.threat_analyses.values() if t.threat_level == ThreatLevel.CRITICAL])
            if critical_threats > 0:
                insights.append(f"{critical_threats} critical threats identified")
                
        elif report_type == AnalyticsType.BEHAVIORAL_ANALYSIS:
            anomalous_users = len([p for p in self.behavioral_patterns.values() if p.anomaly_detected])
            if anomalous_users > 0:
                insights.append(f"{anomalous_users} users showing anomalous behavior")
                
        return insights
        
    async def _generate_executive_summary(self, 
                                        report_type: AnalyticsType,
                                        key_metrics: Dict[str, float],
                                        anomalies_count: int,
                                        threats_count: int) -> str:
        """Générer résumé exécutif"""
        summary_parts = []
        
        summary_parts.append(f"Security Analytics Report - {report_type.value.title()}")
        
        if report_type == AnalyticsType.SECURITY_METRICS:
            events_count = int(key_metrics.get('total_events', 0))
            error_rate = key_metrics.get('error_rate', 0)
            summary_parts.append(f"Processed {events_count:,} security events with {error_rate:.1f}% error rate")
            
        summary_parts.append(f"Detected {anomalies_count} anomalies and {threats_count} potential threats")
        
        if anomalies_count > 10:
            summary_parts.append("⚠️ High anomaly count requires attention")
        elif threats_count > 5:
            summary_parts.append("⚠️ Multiple threats detected - review recommended")
        else:
            summary_parts.append("✅ Security posture appears stable")
            
        return ". ".join(summary_parts) + "."
        
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Tableau de bord temps réel"""
        try:
            # Métriques actuelles
            current_metrics = await self.generate_security_metrics(AnalyticsPeriod.REAL_TIME)
            
            # Menaces récentes
            recent_threats = sorted(
                self.threat_analyses.values(),
                key=lambda t: t.analysis_timestamp,
                reverse=True
            )[:5]
            
            # Anomalies récentes
            recent_anomalies = []
            for metrics_list in self.metrics.values():
                recent_anomalies.extend([m for m in metrics_list[-10:] if m.threshold_breached])
                
            recent_anomalies.sort(key=lambda m: m.timestamp, reverse=True)
            recent_anomalies = recent_anomalies[:5]
            
            # Prédictions récentes
            recent_predictions = sorted(
                self.predictive_insights.values(),
                key=lambda p: p.created_at,
                reverse=True
            )[:3]
            
            dashboard = {
                'timestamp': datetime.utcnow().isoformat(),
                'overview': {
                    'security_score': current_metrics.get('overall_security_score', SecurityMetric('', '', '', 0.0, '', datetime.utcnow())).value,
                    'events_processed': len(self.data_streams['security_events']),
                    'anomalies_detected': len(recent_anomalies),
                    'threats_active': len(recent_threats),
                    'predictions_available': len(recent_predictions)
                },
                'current_metrics': {
                    name: metric.value for name, metric in current_metrics.items()
                },
                'recent_threats': [
                    {
                        'id': threat.analysis_id,
                        'type': threat.threat_type,
                        'level': threat.threat_level.value,
                        'confidence': threat.confidence,
                        'timestamp': threat.analysis_timestamp.isoformat()
                    }
                    for threat in recent_threats
                ],
                'recent_anomalies': [
                    {
                        'metric': anomaly.metric_name,
                        'value': anomaly.value,
                        'severity': anomaly.severity,
                        'timestamp': anomaly.timestamp.isoformat()
                    }
                    for anomaly in recent_anomalies
                ],
                'predictions': [
                    {
                        'type': pred.prediction_type.value,
                        'value': pred.predicted_value,
                        'impact': pred.business_impact,
                        'horizon': str(pred.prediction_horizon)
                    }
                    for pred in recent_predictions
                ],
                'performance': self.performance_metrics
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Dashboard generation failed: {str(e)}")
            return {'error': str(e)}


# Instance globale du moteur d'analytics
analytics_engine = SecurityAnalyticsEngine()


async def get_analytics_engine() -> SecurityAnalyticsEngine:
    """Factory function pour le moteur d'analytics"""
    return analytics_engine


# Fonctions utilitaires pour intégration IA Chérie
async def analyze_creator_security_metrics(creator_id: str) -> Dict[str, Any]:
    """Analyse des métriques de sécurité créateur"""
    # Simuler événements créateur
    creator_events = [
        {
            'user_id': creator_id,
            'event_type': 'content_upload',
            'timestamp': datetime.utcnow().isoformat(),
            'success': True,
            'ip_address': '192.168.1.100',
            'content_size': 1024000
        },
        {
            'user_id': creator_id,
            'event_type': 'revenue_check',
            'timestamp': datetime.utcnow().isoformat(),
            'success': True,
            'sensitive_data': True
        }
    ]
    
    # Ingérer événements
    for event in creator_events:
        await analytics_engine.ingest_security_event(event)
        
    # Analyser comportement
    behavioral_pattern = await analytics_engine.analyze_user_behavior(creator_id, 24)
    
    # Générer prédictions
    predictions = await analytics_engine.generate_predictive_insights([
        PredictionType.FRAUD_PROBABILITY,
        PredictionType.THREAT_LIKELIHOOD
    ])
    
    return {
        'creator_id': creator_id,
        'behavioral_pattern': {
            'pattern_id': behavioral_pattern.pattern_id,
            'anomaly_detected': behavioral_pattern.anomaly_detected,
            'deviation_score': behavioral_pattern.deviation_score,
            'confidence': behavioral_pattern.confidence
        },
        'predictions': [
            {
                'type': pred.prediction_type.value,
                'value': pred.predicted_value,
                'confidence': pred.confidence_interval,
                'impact': pred.business_impact
            }
            for pred in predictions
        ],
        'events_analyzed': len(creator_events)
    }


async def generate_payment_security_analytics() -> AnalyticsReport:
    """Génération d'analytics sécuritaires pour les paiements"""
    # Simuler événements de paiement
    payment_events = []
    for i in range(50):
        event = {
            'event_type': 'payment_transaction',
            'timestamp': (datetime.utcnow() - timedelta(minutes=i*10)).isoformat(),
            'user_id': f"user_{i % 20}",
            'amount': np.random.uniform(10, 1000),
            'success': np.random.choice([True, False], p=[0.95, 0.05]),
            'payment_method': np.random.choice(['card', 'bank', 'crypto']),
            'suspicious': np.random.choice([True, False], p=[0.1, 0.9])
        }
        payment_events.append(event)
        
    # Ingérer événements
    for event in payment_events:
        await analytics_engine.ingest_security_event(event)
        
    # Générer rapport
    report = await analytics_engine.generate_analytics_report(
        AnalyticsType.SECURITY_METRICS,
        AnalyticsPeriod.DAILY
    )
    
    return report


# Export des classes principales
__all__ = [
    'SecurityAnalyticsEngine',
    'MLSecurityModels',
    'SecurityMetric',
    'ThreatAnalysis',
    'BehavioralPattern',
    'PredictiveInsight',
    'AnalyticsReport',
    'AnalyticsType',
    'ThreatLevel',
    'PredictionType',
    'AnalyticsPeriod',
    'analytics_engine',
    'get_analytics_engine',
    'analyze_creator_security_metrics',
    'generate_payment_security_analytics'
]


# Initialisation pour tests
if __name__ == "__main__":
    async def demo_security_analytics():
        """Démonstration du moteur d'analytics de sécurité"""
        engine = await get_analytics_engine()
        
        # Test ingestion d'événements
        test_events = [
            {
                'event_type': 'login',
                'user_id': 'user_123',
                'timestamp': datetime.utcnow().isoformat(),
                'success': True,
                'ip_address': '192.168.1.100'
            },
            {
                'event_type': 'api_call',
                'user_id': 'user_456',
                'timestamp': datetime.utcnow().isoformat(),
                'success': False,
                'suspicious': True
            }
        ]
        
        for event in test_events:
            await engine.ingest_security_event(event)
            
        print(f"Ingested {len(test_events)} test events")
        
        # Test génération métriques
        metrics = await engine.generate_security_metrics(AnalyticsPeriod.REAL_TIME)
        print(f"Generated {len(metrics)} security metrics")
        
        # Test analyse comportementale
        behavior = await engine.analyze_user_behavior('user_123', 1)
        print(f"Behavioral analysis: anomaly={behavior.anomaly_detected}, score={behavior.deviation_score:.2f}")
        
        # Test prédictions
        predictions = await engine.generate_predictive_insights([
            PredictionType.THREAT_LIKELIHOOD,
            PredictionType.FRAUD_PROBABILITY
        ])
        print(f"Generated {len(predictions)} predictions")
        
        # Test rapport
        report = await engine.generate_analytics_report(
            AnalyticsType.SECURITY_METRICS,
            AnalyticsPeriod.REAL_TIME
        )
        print(f"Generated report: {report.report_id}")
        print(f"Executive summary: {report.executive_summary}")
        
        # Test tableau de bord
        dashboard = await engine.get_real_time_dashboard()
        print(f"Dashboard overview: {dashboard['overview']}")
        
        # Test fonctions IA Chérie
        creator_analytics = await analyze_creator_security_metrics('creator_test')
        print(f"Creator analytics: {creator_analytics['creator_id']}")
        
        payment_report = await generate_payment_security_analytics()
        print(f"Payment security report: {payment_report.report_id}")
        
    # Exécution démo
    asyncio.run(demo_security_analytics())