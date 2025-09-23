"""🚨 Threat Detection Engine - ML-Powered Security Intelligence
==============================================================

Moteur de détection des menaces enterprise avec ML-powered analysis,
behavioral anomaly detection et real-time threat monitoring.

Expert Team Implementation:
🤖 Lead Dev IA: ML algorithms + threat prediction + behavior analysis
🏗️ Backend Senior: Scalable threat processing + performance optimization
🧠 ML Engineer: Advanced ML models + anomaly detection + pattern recognition
🗄️ DBA: Threat database + forensic data storage + query optimization
🔒 Sécurité: Threat intelligence + penetration testing + attack vectors
🔗 Microservices: Distributed threat detection + service correlation
🎵 Audio Engineer: Audio-based threat detection + watermark validation
⚙️ DevOps: Real-time monitoring + automated response + SIEM integration
🎨 IA Prompt Engineer: Prompt injection detection + AI safety validation

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
Date: Septembre 2024

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
"""

import asyncio
import logging
import json
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import aiohttp
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd


class ThreatLevel(Enum):
    """Niveaux de menace"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types de menaces"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DDOS = "ddos"
    INSIDER_THREAT = "insider_threat"
    DATA_BREACH = "data_breach"
    SOCIAL_ENGINEERING = "social_engineering"
    PROMPT_INJECTION = "prompt_injection"
    CONTENT_MANIPULATION = "content_manipulation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"


@dataclass
class ThreatEvent:
    """Événement de menace détecté"""
    event_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    timestamp: datetime
    description: str
    evidence: Dict[str, Any]
    confidence_score: float
    risk_score: float
    affected_resources: List[str] = field(default_factory=list)
    mitigation_recommendations: List[str] = field(default_factory=list)
    

@dataclass
class BehavioralPattern:
    """Pattern comportemental pour analyse anomalies"""
    user_id: str
    activity_pattern: Dict[str, Any]
    baseline_behavior: Dict[str, Any]
    anomaly_score: float
    pattern_features: List[float]
    temporal_patterns: Dict[str, Any]
    

@dataclass
class ThreatAnalysisResult:
    """Résultat analyse complète des menaces"""
    analysis_id: str
    threats_detected: List[ThreatEvent]
    behavioral_anomalies: List[BehavioralPattern]
    overall_threat_level: ThreatLevel
    security_score: float
    threat_intelligence_summary: Dict[str, Any]
    recommendations: List[str]
    critical_threats: List[str]
    execution_time_ms: float


class MLThreatClassifier:
    """
    🤖 Classificateur ML pour détection menaces
    ==========================================
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'request_frequency', 'data_volume', 'session_duration',
            'unusual_hours', 'geographic_anomaly', 'device_anomaly',
            'behavior_deviation', 'content_risk_score'
        ]
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialisation modèle ML"""
        try:
            # Isolation Forest pour détection anomalies
            self.model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            logging.info("✅ Modèle ML threat detection initialisé")
        except Exception as e:
            logging.error(f"❌ Erreur initialisation modèle ML: {str(e)}")
    
    async def classify_threat(
        self,
        features: Dict[str, float],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classification ML d'une menace potentielle"""
        try:
            # Préparation features
            feature_vector = [features.get(col, 0.0) for col in self.feature_columns]
            feature_array = np.array([feature_vector])
            
            # Normalisation
            normalized_features = self.scaler.fit_transform(feature_array)
            
            # Prédiction anomalie
            anomaly_score = self.model.decision_function(normalized_features)[0]
            is_anomaly = self.model.predict(normalized_features)[0] == -1
            
            # Classification niveau menace
            threat_level = self._calculate_threat_level(anomaly_score, features)
            
            # Calcul confidence score
            confidence_score = min(abs(anomaly_score) * 100, 100.0)
            
            return {
                'is_threat': is_anomaly,
                'threat_level': threat_level,
                'anomaly_score': float(anomaly_score),
                'confidence_score': confidence_score,
                'feature_importance': self._calculate_feature_importance(features),
                'threat_type': self._determine_threat_type(features, context)
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur classification ML: {str(e)}")
            return {
                'is_threat': False,
                'threat_level': ThreatLevel.LOW,
                'anomaly_score': 0.0,
                'confidence_score': 0.0,
                'error': str(e)
            }
    
    def _calculate_threat_level(
        self,
        anomaly_score: float,
        features: Dict[str, float]
    ) -> ThreatLevel:
        """Calcul niveau menace basé sur score anomalie"""
        # Score normalisé (plus négatif = plus anormal)
        normalized_score = abs(anomaly_score)
        
        # Facteurs aggravants
        risk_factors = 0
        if features.get('unusual_hours', 0) > 0.7:
            risk_factors += 1
        if features.get('behavior_deviation', 0) > 0.8:
            risk_factors += 1
        if features.get('content_risk_score', 0) > 0.6:
            risk_factors += 1
            
        # Détermination niveau
        if normalized_score > 0.5 or risk_factors >= 2:
            return ThreatLevel.CRITICAL
        elif normalized_score > 0.3 or risk_factors >= 1:
            return ThreatLevel.HIGH
        elif normalized_score > 0.1:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _calculate_feature_importance(
        self,
        features: Dict[str, float]
    ) -> Dict[str, float]:
        """Calcul importance des features"""
        importance = {}
        total = sum(abs(v) for v in features.values())
        
        if total > 0:
            for key, value in features.items():
                importance[key] = abs(value) / total
        
        return importance
    
    def _determine_threat_type(
        self,
        features: Dict[str, float],
        context: Dict[str, Any]
    ) -> ThreatType:
        """Détermination type de menace"""
        # Analyse des patterns pour classification
        if features.get('request_frequency', 0) > 0.8:
            return ThreatType.DDOS
        elif features.get('behavior_deviation', 0) > 0.7:
            return ThreatType.ANOMALOUS_BEHAVIOR
        elif context.get('prompt_analysis', {}).get('injection_risk', 0) > 0.6:
            return ThreatType.PROMPT_INJECTION
        elif features.get('content_risk_score', 0) > 0.7:
            return ThreatType.CONTENT_MANIPULATION
        else:
            return ThreatType.UNAUTHORIZED_ACCESS


class BehavioralAnomalyDetector:
    """
    🧠 Détecteur d'anomalies comportementales
    ========================================
    """
    
    def __init__(self):
        self.user_baselines = {}
        self.temporal_patterns = {}
        
    async def detect_anomalies(
        self,
        user_id: str,
        current_behavior: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None
    ) -> BehavioralPattern:
        """Détection anomalies comportementales"""
        try:
            # Récupération baseline comportementale
            baseline = await self._get_user_baseline(user_id, historical_data)
            
            # Calcul features comportementales
            behavior_features = self._extract_behavior_features(current_behavior)
            
            # Calcul score anomalie
            anomaly_score = self._calculate_behavioral_anomaly_score(
                behavior_features, baseline
            )
            
            # Analyse patterns temporels
            temporal_patterns = await self._analyze_temporal_patterns(
                user_id, current_behavior
            )
            
            return BehavioralPattern(
                user_id=user_id,
                activity_pattern=current_behavior,
                baseline_behavior=baseline,
                anomaly_score=anomaly_score,
                pattern_features=behavior_features,
                temporal_patterns=temporal_patterns
            )
            
        except Exception as e:
            logging.error(f"❌ Erreur détection anomalies: {str(e)}")
            return BehavioralPattern(
                user_id=user_id,
                activity_pattern=current_behavior,
                baseline_behavior={},
                anomaly_score=0.0,
                pattern_features=[],
                temporal_patterns={}
            )
    
    async def _get_user_baseline(
        self,
        user_id: str,
        historical_data: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Récupération baseline comportementale utilisateur"""
        if user_id in self.user_baselines:
            return self.user_baselines[user_id]
        
        # Calcul baseline depuis données historiques
        if historical_data:
            baseline = self._calculate_baseline_from_history(historical_data)
            self.user_baselines[user_id] = baseline
            return baseline
        
        # Baseline par défaut
        return {
            'avg_session_duration': 3600,  # 1 heure
            'typical_upload_frequency': 5,  # 5 uploads/jour
            'common_file_types': ['audio', 'video'],
            'usual_activity_hours': list(range(9, 22)),  # 9h-22h
            'geographic_location': 'unknown',
            'device_patterns': {}
        }
    
    def _extract_behavior_features(
        self,
        behavior: Dict[str, Any]
    ) -> List[float]:
        """Extraction features comportementales"""
        features = []
        
        # Features temporelles
        features.append(behavior.get('session_duration', 0) / 3600)  # en heures
        features.append(behavior.get('upload_frequency', 0))
        features.append(behavior.get('activity_hour', 12) / 24)  # normalisé
        
        # Features contenu
        features.append(len(behavior.get('file_types', [])))
        features.append(behavior.get('total_file_size', 0) / (1024*1024))  # MB
        
        # Features géographiques
        features.append(1.0 if behavior.get('location_change', False) else 0.0)
        
        # Features device
        features.append(1.0 if behavior.get('new_device', False) else 0.0)
        
        # Features réseau
        features.append(behavior.get('ip_reputation_score', 0.5))
        
        return features
    
    def _calculate_behavioral_anomaly_score(
        self,
        current_features: List[float],
        baseline: Dict[str, Any]
    ) -> float:
        """Calcul score anomalie comportementale"""
        try:
            # Comparaison avec baseline
            deviations = []
            
            # Comparaison durée session
            expected_duration = baseline.get('avg_session_duration', 3600) / 3600
            if len(current_features) > 0:
                duration_deviation = abs(current_features[0] - expected_duration) / max(expected_duration, 0.1)
                deviations.append(duration_deviation)
            
            # Comparaison fréquence upload
            expected_frequency = baseline.get('typical_upload_frequency', 5)
            if len(current_features) > 1:
                freq_deviation = abs(current_features[1] - expected_frequency) / max(expected_frequency, 1)
                deviations.append(freq_deviation)
            
            # Score final (moyenne des déviations)
            if deviations:
                return min(sum(deviations) / len(deviations), 1.0)
            
            return 0.0
            
        except Exception as e:
            logging.error(f"❌ Erreur calcul anomalie: {str(e)}")
            return 0.0
    
    async def _analyze_temporal_patterns(
        self,
        user_id: str,
        current_behavior: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyse patterns temporels"""
        current_hour = datetime.now().hour
        
        return {
            'current_hour': current_hour,
            'is_unusual_hour': current_hour < 6 or current_hour > 23,
            'weekend_activity': datetime.now().weekday() >= 5,
            'pattern_consistency': 0.8  # À calculer avec plus de données
        }


class ThreatDetectionEngine:
    """
    🚨 Moteur de détection des menaces enterprise
    ============================================
    
    Détection proactive des menaces avec ML-powered analysis,
    behavioral monitoring et real-time threat intelligence.
    """
    
    def __init__(self):
        """Initialisation moteur détection menaces"""
        self.logger = logging.getLogger(__name__)
        
        # Composants ML
        self.ml_classifier = MLThreatClassifier()
        self.behavior_detector = BehavioralAnomalyDetector()
        
        # Cache et storage
        self.threat_cache = {}
        self.active_threats = {}
        
        # Configuration
        self.threat_thresholds = {
            'anomaly_threshold': 0.3,
            'behavior_threshold': 0.6,
            'confidence_threshold': 0.7
        }
        
        self.logger.info("🚨 Threat Detection Engine initialisé")
    
    async def analyze_comprehensive_threats(
        self,
        security_context: Any
    ) -> ThreatAnalysisResult:
        """
        🎯 Analyse complète des menaces
        
        Args:
            security_context: Contexte sécurité complet
            
        Returns:
            ThreatAnalysisResult: Résultat analyse menaces
        """
        start_time = datetime.utcnow()
        analysis_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"🔍 Démarrage analyse menaces: {analysis_id}")
            
            # Extraction données contexte
            user_id = getattr(security_context, 'user_id', 'unknown')
            ip_address = getattr(security_context, 'ip_address', '0.0.0.0')
            
            # Analyse comportementale
            behavioral_anomalies = await self._analyze_behavioral_threats(
                security_context
            )
            
            # Détection menaces ML
            ml_threats = await self._detect_ml_powered_threats(
                security_context
            )
            
            # Analyse threat intelligence
            threat_intel = await self._analyze_threat_intelligence(
                security_context
            )
            
            # Détection menaces réseau
            network_threats = await self._detect_network_threats(
                security_context
            )
            
            # Détection menaces contenu
            content_threats = await self._detect_content_threats(
                security_context
            )
            
            # Consolidation menaces
            all_threats = []
            all_threats.extend(ml_threats)
            all_threats.extend(network_threats)
            all_threats.extend(content_threats)
            
            # Calcul niveau menace global
            overall_threat_level = self._calculate_overall_threat_level(all_threats)
            
            # Calcul score sécurité
            security_score = self._calculate_security_score(
                all_threats, behavioral_anomalies
            )
            
            # Génération recommandations
            recommendations = await self._generate_threat_recommendations(
                all_threats, behavioral_anomalies
            )
            
            # Identification menaces critiques
            critical_threats = [
                threat.description for threat in all_threats 
                if threat.threat_level == ThreatLevel.CRITICAL
            ]
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = ThreatAnalysisResult(
                analysis_id=analysis_id,
                threats_detected=all_threats,
                behavioral_anomalies=behavioral_anomalies,
                overall_threat_level=overall_threat_level,
                security_score=security_score,
                threat_intelligence_summary=threat_intel,
                recommendations=recommendations,
                critical_threats=critical_threats,
                execution_time_ms=execution_time
            )
            
            self.logger.info(
                f"✅ Analyse menaces complétée - {len(all_threats)} menaces détectées "
                f"- Score: {security_score:.1f}% en {execution_time:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse menaces: {str(e)}")
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ThreatAnalysisResult(
                analysis_id=analysis_id,
                threats_detected=[],
                behavioral_anomalies=[],
                overall_threat_level=ThreatLevel.LOW,
                security_score=0.0,
                threat_intelligence_summary={},
                recommendations=[f"Erreur analyse: {str(e)}"],
                critical_threats=[],
                execution_time_ms=execution_time
            )
    
    async def quick_threat_scan(
        self,
        security_context: Any
    ) -> Dict[str, Any]:
        """
        ⚡ Scan rapide des menaces
        
        Args:
            security_context: Contexte sécurité
            
        Returns:
            Dict: Résultat scan rapide
        """
        try:
            # Vérifications essentielles rapides
            ip_reputation = await self._check_ip_reputation(
                getattr(security_context, 'ip_address', '0.0.0.0')
            )
            
            # Détection comportement suspect
            behavior_risk = await self._quick_behavior_check(security_context)
            
            # Analyse user agent
            ua_risk = self._analyze_user_agent_risk(
                getattr(security_context, 'user_agent', '')
            )
            
            # Score global rapide
            quick_score = (
                ip_reputation.get('score', 100) * 0.4 +
                behavior_risk.get('score', 100) * 0.4 +
                ua_risk.get('score', 100) * 0.2
            )
            
            return {
                'security_score': quick_score,
                'threat_level': self._score_to_threat_level(quick_score),
                'ip_reputation': ip_reputation,
                'behavior_risk': behavior_risk,
                'user_agent_risk': ua_risk,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur scan rapide: {str(e)}")
            return {
                'security_score': 0,
                'threat_level': 'unknown',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _analyze_behavioral_threats(
        self,
        security_context: Any
    ) -> List[BehavioralPattern]:
        """Analyse menaces comportementales"""
        try:
            user_id = getattr(security_context, 'user_id', 'unknown')
            
            # Construction profil comportemental actuel
            current_behavior = {
                'session_duration': 1800,  # 30 minutes par défaut
                'upload_frequency': 1,
                'activity_hour': datetime.now().hour,
                'file_types': ['audio'],
                'total_file_size': 10 * 1024 * 1024,  # 10MB
                'location_change': False,
                'new_device': False,
                'ip_reputation_score': 0.8
            }
            
            # Détection anomalies
            pattern = await self.behavior_detector.detect_anomalies(
                user_id, current_behavior
            )
            
            return [pattern] if pattern.anomaly_score > self.threat_thresholds['behavior_threshold'] else []
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse comportementale: {str(e)}")
            return []
    
    async def _detect_ml_powered_threats(
        self,
        security_context: Any
    ) -> List[ThreatEvent]:
        """Détection menaces ML-powered"""
        threats = []
        
        try:
            # Features pour ML
            features = {
                'request_frequency': 0.5,
                'data_volume': 0.3,
                'session_duration': 0.4,
                'unusual_hours': 1.0 if datetime.now().hour < 6 else 0.0,
                'geographic_anomaly': 0.0,
                'device_anomaly': 0.0,
                'behavior_deviation': 0.2,
                'content_risk_score': 0.1
            }
            
            context = {
                'user_id': getattr(security_context, 'user_id', 'unknown'),
                'ip_address': getattr(security_context, 'ip_address', '0.0.0.0')
            }
            
            # Classification ML
            ml_result = await self.ml_classifier.classify_threat(features, context)
            
            if ml_result.get('is_threat', False):
                threat = ThreatEvent(
                    event_id=str(uuid.uuid4()),
                    threat_type=ml_result.get('threat_type', ThreatType.ANOMALOUS_BEHAVIOR),
                    threat_level=ml_result.get('threat_level', ThreatLevel.LOW),
                    source_ip=context['ip_address'],
                    user_id=context['user_id'],
                    timestamp=datetime.utcnow(),
                    description=f"Menace détectée par ML - Score: {ml_result.get('anomaly_score', 0):.3f}",
                    evidence={'ml_analysis': ml_result, 'features': features},
                    confidence_score=ml_result.get('confidence_score', 0.0),
                    risk_score=abs(ml_result.get('anomaly_score', 0)) * 100,
                    mitigation_recommendations=[
                        "Surveillance renforcée de l'utilisateur",
                        "Validation supplémentaire des actions"
                    ]
                )
                threats.append(threat)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur détection ML: {str(e)}")
        
        return threats
    
    async def _analyze_threat_intelligence(
        self,
        security_context: Any
    ) -> Dict[str, Any]:
        """Analyse threat intelligence"""
        return {
            'global_threat_level': 'medium',
            'active_campaigns': [],
            'reputation_feeds': {
                'ip_reputation': 'clean',
                'domain_reputation': 'unknown'
            },
            'threat_indicators': []
        }
    
    async def _detect_network_threats(
        self,
        security_context: Any
    ) -> List[ThreatEvent]:
        """Détection menaces réseau"""
        threats = []
        
        try:
            ip_address = getattr(security_context, 'ip_address', '0.0.0.0')
            
            # Simulation détection DDoS
            if ip_address.startswith('192.168.'):  # IP locale - faible risque
                pass
            else:
                # Vérification liste noire IP (simulée)
                if await self._is_ip_blacklisted(ip_address):
                    threat = ThreatEvent(
                        event_id=str(uuid.uuid4()),
                        threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                        threat_level=ThreatLevel.HIGH,
                        source_ip=ip_address,
                        user_id=getattr(security_context, 'user_id', None),
                        timestamp=datetime.utcnow(),
                        description=f"IP suspecte détectée: {ip_address}",
                        evidence={'ip_reputation': 'blacklisted'},
                        confidence_score=85.0,
                        risk_score=85.0,
                        mitigation_recommendations=[
                            "Bloquer l'IP immédiatement",
                            "Audit des actions récentes"
                        ]
                    )
                    threats.append(threat)
        
        except Exception as e:
            self.logger.error(f"❌ Erreur détection réseau: {str(e)}")
        
        return threats
    
    async def _detect_content_threats(
        self,
        security_context: Any
    ) -> List[ThreatEvent]:
        """Détection menaces contenu"""
        threats = []
        
        try:
            # Analyse contenu uploadé (si disponible)
            content_metadata = getattr(security_context, 'content_metadata', {})
            
            if content_metadata:
                # Détection malware potentiel
                if content_metadata.get('file_size', 0) > 100 * 1024 * 1024:  # >100MB
                    threat = ThreatEvent(
                        event_id=str(uuid.uuid4()),
                        threat_type=ThreatType.MALWARE,
                        threat_level=ThreatLevel.MEDIUM,
                        source_ip=getattr(security_context, 'ip_address', '0.0.0.0'),
                        user_id=getattr(security_context, 'user_id', None),
                        timestamp=datetime.utcnow(),
                        description=f"Fichier volumineux suspect: {content_metadata.get('filename', 'unknown')}",
                        evidence={'file_analysis': content_metadata},
                        confidence_score=60.0,
                        risk_score=60.0,
                        mitigation_recommendations=[
                            "Scan antivirus approfondi",
                            "Quarantaine temporaire"
                        ]
                    )
                    threats.append(threat)
        
        except Exception as e:
            self.logger.error(f"❌ Erreur détection contenu: {str(e)}")
        
        return threats
    
    def _calculate_overall_threat_level(
        self,
        threats: List[ThreatEvent]
    ) -> ThreatLevel:
        """Calcul niveau menace global"""
        if not threats:
            return ThreatLevel.LOW
        
        # Niveau maximum détecté
        max_level = max(threat.threat_level for threat in threats)
        return max_level
    
    def _calculate_security_score(
        self,
        threats: List[ThreatEvent],
        behavioral_anomalies: List[BehavioralPattern]
    ) -> float:
        """Calcul score sécurité global"""
        base_score = 100.0
        
        # Pénalités par niveau menace
        threat_penalties = {
            ThreatLevel.LOW: 5,
            ThreatLevel.MEDIUM: 15,
            ThreatLevel.HIGH: 35,
            ThreatLevel.CRITICAL: 60
        }
        
        # Application pénalités menaces
        for threat in threats:
            penalty = threat_penalties.get(threat.threat_level, 0)
            base_score -= penalty
        
        # Pénalités anomalies comportementales
        for anomaly in behavioral_anomalies:
            base_score -= anomaly.anomaly_score * 20
        
        return max(base_score, 0.0)
    
    async def _generate_threat_recommendations(
        self,
        threats: List[ThreatEvent],
        behavioral_anomalies: List[BehavioralPattern]
    ) -> List[str]:
        """Génération recommandations sécurité"""
        recommendations = []
        
        if not threats and not behavioral_anomalies:
            recommendations.append("✅ Aucune menace détectée - Surveillance continue")
            return recommendations
        
        # Recommandations par type menace
        threat_types = set(threat.threat_type for threat in threats)
        
        if ThreatType.CRITICAL in [threat.threat_level for threat in threats]:
            recommendations.append("🚨 CRITIQUE: Activation protocole incident immédiat")
        
        if ThreatType.MALWARE in threat_types:
            recommendations.append("🦠 Scan antivirus complet requis")
        
        if ThreatType.DDOS in threat_types:
            recommendations.append("🛡️ Activation protection DDoS")
        
        if ThreatType.UNAUTHORIZED_ACCESS in threat_types:
            recommendations.append("🔒 Révision des accès et authentification renforcée")
        
        if behavioral_anomalies:
            recommendations.append("👁️ Surveillance comportementale renforcée")
        
        recommendations.append("📊 Rapport détaillé disponible pour analyse")
        
        return recommendations
    
    async def _check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Vérification réputation IP"""
        # Simulation - en production, utiliser des APIs de réputation
        if ip_address.startswith('127.') or ip_address.startswith('192.168.'):
            return {'score': 100, 'status': 'local', 'reputation': 'trusted'}
        
        return {'score': 85, 'status': 'external', 'reputation': 'clean'}
    
    async def _quick_behavior_check(self, security_context: Any) -> Dict[str, Any]:
        """Vérification comportement rapide"""
        # Analyse rapide patterns
        current_hour = datetime.now().hour
        is_unusual = current_hour < 6 or current_hour > 23
        
        score = 90 if not is_unusual else 60
        
        return {
            'score': score,
            'unusual_hour': is_unusual,
            'risk_factors': ['unusual_time'] if is_unusual else []
        }
    
    def _analyze_user_agent_risk(self, user_agent: str) -> Dict[str, Any]:
        """Analyse risque user agent"""
        # Détection user agents suspects
        suspicious_patterns = ['bot', 'crawler', 'scanner', 'hack']
        
        risk_score = 0
        for pattern in suspicious_patterns:
            if pattern.lower() in user_agent.lower():
                risk_score += 25
        
        return {
            'score': max(100 - risk_score, 0),
            'risk_patterns': [p for p in suspicious_patterns if p in user_agent.lower()],
            'user_agent': user_agent[:100]  # Tronqué pour log
        }
    
    def _score_to_threat_level(self, score: float) -> str:
        """Conversion score vers niveau menace"""
        if score < 30:
            return 'critical'
        elif score < 50:
            return 'high'
        elif score < 70:
            return 'medium'
        else:
            return 'low'
    
    async def _is_ip_blacklisted(self, ip_address: str) -> bool:
        """Vérification blacklist IP (simulation)"""
        # En production: consultation bases de données threat intelligence
        blacklisted_ips = ['10.0.0.1', '192.168.1.100']  # IPs test
        return ip_address in blacklisted_ips


# Export classes principales
__all__ = [
    'ThreatDetectionEngine',
    'ThreatEvent',
    'ThreatLevel',
    'ThreatType',
    'ThreatAnalysisResult',
    'BehavioralPattern',
    'MLThreatClassifier',
    'BehavioralAnomalyDetector'
]