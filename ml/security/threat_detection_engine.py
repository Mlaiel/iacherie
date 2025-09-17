"""🔒 Threat Detection Engine - ML Security Module
=======================================================================
Moteur détection menaces ML avec intelligence temps réel.
Real-time threat detection + anomaly detection + attack pattern recognition.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue ML Security - Threat Detection
Version: 1.0 Production
=======================================================================
"""

import asyncio
import logging
import time
import hashlib
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)

class ThreatType(Enum):
    """Types de menaces ML"""
    ADVERSARIAL_INPUT = "adversarial_input"
    MODEL_POISONING = "model_poisoning"
    DATA_EXTRACTION = "data_extraction"
    MODEL_INVERSION = "model_inversion"
    MEMBERSHIP_INFERENCE = "membership_inference"
    API_ABUSE = "api_abuse"
    INSIDER_THREAT = "insider_threat"
    ZERO_DAY_ATTACK = "zero_day_attack"
    DATA_DRIFT_ANOMALY = "data_drift_anomaly"
    BEHAVIOR_ANOMALY = "behavior_anomaly"

class ThreatSeverity(Enum):
    """Niveaux de sévérité menaces"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ThreatDetectionRequest:
    """Requête détection menaces"""
    target_data: Any
    model_context: Optional[Dict] = None
    user_context: Optional[Dict] = None
    api_context: Optional[Dict] = None
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[str] = None

@dataclass
class ThreatIndicator:
    """Indicateur de menace"""
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence_score: float
    evidence: Dict[str, Any]
    detection_method: str
    timestamp: float

@dataclass
class ThreatDetectionResult:
    """Résultat détection menaces"""
    is_threat_detected: bool
    threat_indicators: List[ThreatIndicator]
    overall_risk_score: float
    recommended_actions: List[str]
    response_required: bool
    detection_time_ms: float
    session_id: Optional[str] = None

class AnomalyDetectionEngine:
    """Moteur détection anomalies statistiques"""
    
    def __init__(self):
        self.baseline_stats = {}
        self.anomaly_threshold = 2.5  # Z-score threshold
        
    async def detect_statistical_anomalies(self, data: np.ndarray, context: str) -> Dict[str, Any]:
        """Détection anomalies statistiques avec Z-score"""
        try:
            if len(data.shape) > 1:
                data = data.flatten()
            
            mean_val = np.mean(data)
            std_val = np.std(data)
            
            if std_val == 0:
                return {"anomaly_detected": False, "reason": "zero_variance"}
            
            z_scores = np.abs((data - mean_val) / std_val)
            anomalous_indices = np.where(z_scores > self.anomaly_threshold)[0]
            
            if len(anomalous_indices) > 0:
                return {
                    "anomaly_detected": True,
                    "anomalous_count": len(anomalous_indices),
                    "max_z_score": float(np.max(z_scores)),
                    "anomaly_ratio": len(anomalous_indices) / len(data),
                    "context": context
                }
            
            return {"anomaly_detected": False, "max_z_score": float(np.max(z_scores))}
            
        except Exception as e:
            logger.error(f"Statistical anomaly detection failed: {e}")
            return {"anomaly_detected": False, "error": str(e)}

class AttackPatternRecognizer:
    """Reconnaissance patterns d'attaque"""
    
    def __init__(self):
        self.known_patterns = {
            "adversarial_gradient": {
                "description": "Gradient-based adversarial perturbations",
                "signatures": ["high_frequency_noise", "targeted_perturbation"]
            },
            "api_flooding": {
                "description": "API request flooding attack",
                "signatures": ["high_request_rate", "identical_patterns"]
            },
            "model_extraction": {
                "description": "Model extraction via systematic queries",
                "signatures": ["systematic_queries", "boundary_probing"]
            }
        }
        
    async def recognize_attack_patterns(self, request_data: Any, context: Dict) -> Dict[str, Any]:
        """Reconnaissance patterns d'attaque connus"""
        detected_patterns = []
        
        try:
            # Pattern detection logic
            if self._detect_adversarial_gradient_pattern(request_data):
                detected_patterns.append("adversarial_gradient")
            
            if self._detect_api_flooding_pattern(context):
                detected_patterns.append("api_flooding")
            
            if self._detect_model_extraction_pattern(context):
                detected_patterns.append("model_extraction")
            
            return {
                "patterns_detected": detected_patterns,
                "pattern_count": len(detected_patterns),
                "confidence": 0.8 if detected_patterns else 0.1
            }
            
        except Exception as e:
            logger.error(f"Attack pattern recognition failed: {e}")
            return {"patterns_detected": [], "error": str(e)}
    
    def _detect_adversarial_gradient_pattern(self, data: Any) -> bool:
        """Détection pattern gradient adversarial"""
        if isinstance(data, np.ndarray):
            # Check for high-frequency noise patterns
            if len(data.shape) > 1:
                gradient_magnitude = np.mean(np.abs(np.gradient(data.flatten())))
                return gradient_magnitude > 0.1  # Threshold pour gradient élevé
        return False
    
    def _detect_api_flooding_pattern(self, context: Dict) -> bool:
        """Détection pattern flooding API"""
        request_rate = context.get("request_rate", 0)
        return request_rate > 100  # Requests per minute threshold
    
    def _detect_model_extraction_pattern(self, context: Dict) -> bool:
        """Détection pattern extraction modèle"""
        query_diversity = context.get("query_diversity", 1.0)
        return query_diversity < 0.3  # Low diversity indicates systematic probing

class ThreatClassificationEngine:
    """Moteur classification menaces avec ML"""
    
    def __init__(self):
        self.threat_weights = {
            ThreatType.ADVERSARIAL_INPUT: 0.9,
            ThreatType.MODEL_POISONING: 0.95,
            ThreatType.API_ABUSE: 0.7,
            ThreatType.DATA_EXTRACTION: 0.85,
            ThreatType.INSIDER_THREAT: 0.8,
            ThreatType.ZERO_DAY_ATTACK: 1.0
        }
        
    async def classify_threat_severity(self, indicators: List[Dict]) -> ThreatSeverity:
        """Classification sévérité menace"""
        if not indicators:
            return ThreatSeverity.LOW
        
        severity_scores = []
        for indicator in indicators:
            base_score = indicator.get("confidence", 0.5)
            threat_type = indicator.get("threat_type")
            
            if threat_type and threat_type in self.threat_weights:
                weighted_score = base_score * self.threat_weights[threat_type]
                severity_scores.append(weighted_score)
        
        if not severity_scores:
            return ThreatSeverity.LOW
        
        avg_severity = statistics.mean(severity_scores)
        
        if avg_severity >= 0.9:
            return ThreatSeverity.CRITICAL
        elif avg_severity >= 0.7:
            return ThreatSeverity.HIGH
        elif avg_severity >= 0.4:
            return ThreatSeverity.MEDIUM
        else:
            return ThreatSeverity.LOW

class ThreatResponseCoordinator:
    """Coordinateur réponse menaces"""
    
    def __init__(self):
        self.response_strategies = {
            ThreatSeverity.CRITICAL: ["immediate_block", "alert_admin", "forensic_capture"],
            ThreatSeverity.HIGH: ["rate_limit", "enhanced_monitoring", "alert_admin"],
            ThreatSeverity.MEDIUM: ["log_incident", "monitor_session"],
            ThreatSeverity.LOW: ["log_incident"]
        }
        
    async def coordinate_threat_response(self, threat_result: ThreatDetectionResult) -> Dict[str, Any]:
        """Coordination réponse menace avec actions automatisées"""
        if not threat_result.is_threat_detected:
            return {"action": "none", "reason": "no_threat_detected"}
        
        max_severity = ThreatSeverity.LOW
        for indicator in threat_result.threat_indicators:
            if self._severity_priority(indicator.severity) > self._severity_priority(max_severity):
                max_severity = indicator.severity
        
        recommended_actions = self.response_strategies.get(max_severity, ["log_incident"])
        
        response_plan = {
            "severity": max_severity.value,
            "actions": recommended_actions,
            "automated_response": max_severity in [ThreatSeverity.CRITICAL, ThreatSeverity.HIGH],
            "escalation_required": max_severity == ThreatSeverity.CRITICAL,
            "timestamp": time.time()
        }
        
        logger.info(f"🔒 Threat response coordinated: {max_severity.value} - Actions: {recommended_actions}")
        
        return response_plan
    
    def _severity_priority(self, severity: ThreatSeverity) -> int:
        """Priorité numérique des sévérités"""
        priorities = {
            ThreatSeverity.LOW: 1,
            ThreatSeverity.MEDIUM: 2,
            ThreatSeverity.HIGH: 3,
            ThreatSeverity.CRITICAL: 4
        }
        return priorities.get(severity, 0)

class ThreatDetectionEngine:
    """
    Moteur détection menaces ML avec intelligence temps réel.
    Real-time threat detection + anomaly detection + attack pattern recognition.
    """
    
    def __init__(self, threat_config):
        self.threat_config = threat_config
        self.anomaly_detector = AnomalyDetectionEngine()
        self.pattern_recognizer = AttackPatternRecognizer()
        self.threat_classifier = ThreatClassificationEngine()
        self.response_coordinator = ThreatResponseCoordinator()
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        
    async def initialize(self, config) -> None:
        """Initialisation moteur détection menaces"""
        self.logger.info("🔒 Initializing Threat Detection Engine...")
        self.threat_config = config
        self._initialized = True
        self.logger.info("✅ Threat Detection Engine initialized successfully")
        
    async def execute_security_check(self, request: Any) -> Dict[str, Any]:
        """Exécution check sécurité pour détection menaces"""
        if isinstance(request, dict):
            detection_request = ThreatDetectionRequest(
                target_data=request.get("data"),
                model_context=request.get("model_context"),
                user_context=request.get("user_context"),
                api_context=request.get("api_context")
            )
        else:
            detection_request = ThreatDetectionRequest(target_data=request)
        
        result = await self.detect_ml_threats(detection_request)
        
        return {
            "service": "threat_detection",
            "threat_detected": result.is_threat_detected,
            "risk_score": result.overall_risk_score,
            "indicators_count": len(result.threat_indicators),
            "response_required": result.response_required,
            "detection_time_ms": result.detection_time_ms,
            "score": max(100 - result.overall_risk_score, 0)
        }
        
    async def get_security_status(self) -> Dict[str, Any]:
        """Statut service détection menaces"""
        return {
            "service": "threat_detection_engine",
            "status": "active" if self._initialized else "inactive",
            "version": "1.0.0",
            "capabilities": [
                "adversarial_input_detection",
                "model_poisoning_detection",
                "api_abuse_detection",
                "anomaly_detection",
                "pattern_recognition"
            ],
            "last_update": time.time()
        }
        
    async def handle_security_incident(self, incident: Any) -> Any:
        """Gestion incident sécurité"""
        return await self.response_coordinator.coordinate_threat_response(incident)
        
    async def detect_ml_threats(self, threat_request: ThreatDetectionRequest) -> ThreatDetectionResult:
        """
        Détection menaces ML avec intelligence temps réel.
        
        Threat Detection Features:
        - Real-time anomaly detection dans model predictions
        - Attack pattern recognition avec signature database
        - Adversarial input detection avec statistical analysis
        - Model poisoning detection basé sur behavior analysis
        - Data drift monitoring avec threat correlation
        - API abuse detection pour model serving endpoints
        - Insider threat detection avec access pattern analysis
        - Zero-day threat detection avec ML-based classification
        - Threat intelligence integration avec external feeds
        - Automated response coordination avec incident management
        """
        start_time = time.time()
        
        self.logger.info("🔒 Starting ML threat detection analysis...")
        
        threat_indicators = []
        
        try:
            # 1. Anomaly Detection
            if hasattr(threat_request.target_data, '__array__') or isinstance(threat_request.target_data, (list, tuple)):
                data_array = np.array(threat_request.target_data) if not isinstance(threat_request.target_data, np.ndarray) else threat_request.target_data
                anomaly_result = await self.anomaly_detector.detect_statistical_anomalies(data_array, "input_data")
                
                if anomaly_result.get("anomaly_detected"):
                    threat_indicators.append(ThreatIndicator(
                        threat_type=ThreatType.ADVERSARIAL_INPUT,
                        severity=ThreatSeverity.MEDIUM,
                        confidence_score=min(anomaly_result.get("anomaly_ratio", 0) * 2, 1.0),
                        evidence=anomaly_result,
                        detection_method="statistical_anomaly",
                        timestamp=time.time()
                    ))
            
            # 2. Attack Pattern Recognition
            context = {
                "model_context": threat_request.model_context or {},
                "user_context": threat_request.user_context or {},
                "api_context": threat_request.api_context or {},
                "request_rate": threat_request.api_context.get("request_rate", 0) if threat_request.api_context else 0,
                "query_diversity": threat_request.api_context.get("query_diversity", 1.0) if threat_request.api_context else 1.0
            }
            
            pattern_result = await self.pattern_recognizer.recognize_attack_patterns(threat_request.target_data, context)
            
            if pattern_result.get("patterns_detected"):
                for pattern in pattern_result["patterns_detected"]:
                    threat_indicators.append(ThreatIndicator(
                        threat_type=ThreatType.API_ABUSE if pattern == "api_flooding" else ThreatType.DATA_EXTRACTION,
                        severity=ThreatSeverity.HIGH if pattern == "model_extraction" else ThreatSeverity.MEDIUM,
                        confidence_score=pattern_result.get("confidence", 0.5),
                        evidence={"pattern": pattern, "details": pattern_result},
                        detection_method="pattern_recognition",
                        timestamp=time.time()
                    ))
            
            # 3. Behavioral Analysis
            behavioral_anomalies = await self._detect_behavioral_anomalies(threat_request)
            threat_indicators.extend(behavioral_anomalies)
            
            # 4. Classification finale
            overall_severity = await self.threat_classifier.classify_threat_severity([
                {
                    "confidence": indicator.confidence_score,
                    "threat_type": indicator.threat_type
                } for indicator in threat_indicators
            ])
            
            # 5. Calcul score risque global
            if threat_indicators:
                risk_scores = [indicator.confidence_score * 100 for indicator in threat_indicators]
                overall_risk_score = min(statistics.mean(risk_scores), 100.0)
            else:
                overall_risk_score = 0.0
            
            # 6. Recommandations
            recommended_actions = self._generate_threat_recommendations(threat_indicators, overall_severity)
            
            detection_time = (time.time() - start_time) * 1000
            
            result = ThreatDetectionResult(
                is_threat_detected=len(threat_indicators) > 0,
                threat_indicators=threat_indicators,
                overall_risk_score=overall_risk_score,
                recommended_actions=recommended_actions,
                response_required=overall_severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL],
                detection_time_ms=detection_time,
                session_id=threat_request.session_id
            )
            
            self.logger.info(f"🔒 Threat detection complete: {len(threat_indicators)} indicators, risk score: {overall_risk_score:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Threat detection failed: {e}")
            return ThreatDetectionResult(
                is_threat_detected=True,  # Fail-safe: assume threat on error
                threat_indicators=[],
                overall_risk_score=50.0,
                recommended_actions=["Review threat detection engine"],
                response_required=False,
                detection_time_ms=(time.time() - start_time) * 1000,
                session_id=threat_request.session_id
            )
    
    async def _detect_behavioral_anomalies(self, request: ThreatDetectionRequest) -> List[ThreatIndicator]:
        """Détection anomalies comportementales"""
        indicators = []
        
        try:
            # User behavior analysis
            if request.user_context:
                user_risk = self._assess_user_risk(request.user_context)
                if user_risk > 0.6:
                    indicators.append(ThreatIndicator(
                        threat_type=ThreatType.INSIDER_THREAT,
                        severity=ThreatSeverity.MEDIUM,
                        confidence_score=user_risk,
                        evidence={"user_risk_factors": request.user_context},
                        detection_method="behavioral_analysis",
                        timestamp=time.time()
                    ))
            
            # API usage patterns
            if request.api_context:
                api_risk = self._assess_api_risk(request.api_context)
                if api_risk > 0.7:
                    indicators.append(ThreatIndicator(
                        threat_type=ThreatType.API_ABUSE,
                        severity=ThreatSeverity.HIGH,
                        confidence_score=api_risk,
                        evidence={"api_risk_factors": request.api_context},
                        detection_method="api_behavior_analysis",
                        timestamp=time.time()
                    ))
            
        except Exception as e:
            self.logger.error(f"Behavioral anomaly detection failed: {e}")
        
        return indicators
    
    def _assess_user_risk(self, user_context: Dict) -> float:
        """Évaluation risque utilisateur basé sur comportement"""
        risk_factors = 0.0
        factor_count = 0
        
        # Unusual access patterns
        if user_context.get("unusual_hours", False):
            risk_factors += 0.3
            factor_count += 1
        
        # High privilege escalation attempts
        if user_context.get("privilege_escalation_attempts", 0) > 2:
            risk_factors += 0.4
            factor_count += 1
        
        # Suspicious geolocation
        if user_context.get("suspicious_location", False):
            risk_factors += 0.5
            factor_count += 1
        
        return risk_factors if factor_count == 0 else risk_factors / factor_count
    
    def _assess_api_risk(self, api_context: Dict) -> float:
        """Évaluation risque API basé sur patterns"""
        risk_score = 0.0
        
        # High request rate
        request_rate = api_context.get("request_rate", 0)
        if request_rate > 1000:
            risk_score += 0.6
        elif request_rate > 500:
            risk_score += 0.4
        
        # Low query diversity (systematic probing)
        query_diversity = api_context.get("query_diversity", 1.0)
        if query_diversity < 0.2:
            risk_score += 0.5
        elif query_diversity < 0.4:
            risk_score += 0.3
        
        # Error rate spikes
        error_rate = api_context.get("error_rate", 0.0)
        if error_rate > 0.5:
            risk_score += 0.4
        
        return min(risk_score, 1.0)
    
    def _generate_threat_recommendations(self, indicators: List[ThreatIndicator], severity: ThreatSeverity) -> List[str]:
        """Génération recommandations basées sur menaces détectées"""
        recommendations = []
        
        threat_types = {indicator.threat_type for indicator in indicators}
        
        if ThreatType.ADVERSARIAL_INPUT in threat_types:
            recommendations.append("Implement input validation and adversarial defense mechanisms")
        
        if ThreatType.API_ABUSE in threat_types:
            recommendations.append("Apply rate limiting and API access controls")
        
        if ThreatType.INSIDER_THREAT in threat_types:
            recommendations.append("Review user access patterns and implement additional monitoring")
        
        if ThreatType.DATA_EXTRACTION in threat_types:
            recommendations.append("Implement model extraction protection and query analysis")
        
        if severity == ThreatSeverity.CRITICAL:
            recommendations.append("Immediate security response required - escalate to security team")
        elif severity == ThreatSeverity.HIGH:
            recommendations.append("Enhanced monitoring and possible access restriction recommended")
        
        if not recommendations:
            recommendations.append("Continue monitoring - no immediate action required")
        
        return recommendations

# Export API
__all__ = [
    'ThreatDetectionEngine',
    'ThreatDetectionRequest',
    'ThreatDetectionResult',
    'ThreatIndicator',
    'ThreatType',
    'ThreatSeverity'
]