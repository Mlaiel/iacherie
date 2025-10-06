"""
Streaming Violation Detector - Real Implementation

Copyright (c) 2025 Fahed Mlaiel
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Pattern
from uuid import uuid4

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    TERMS_VIOLATION = "terms_violation"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    SPAM = "spam"
    HATE_SPEECH = "hate_speech"
    MISINFORMATION = "misinformation"


class ViolationSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Alias
SeverityLevel = ViolationSeverity


class DetectionMethod(Enum):
    KEYWORD_MATCHING = "keyword_matching"
    AI_CLASSIFICATION = "ai_classification"
    PATTERN_ANALYSIS = "pattern_analysis"
    USER_REPORT = "user_report"


class ViolationStatus(Enum):
    DETECTED = "detected"
    UNDER_REVIEW = "under_review"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


@dataclass
class ViolationDetectionConfig:
    config_id: str
    enabled_types: List[ViolationType]
    sensitivity: float = 0.75
    auto_action: bool = True
    review_threshold: float = 0.90


@dataclass
class ViolationRule:
    rule_id: str
    violation_type: ViolationType
    patterns: List[str]
    severity: ViolationSeverity
    auto_block: bool = False


@dataclass
class ViolationIncident:
    incident_id: str
    stream_id: str
    violation_type: ViolationType
    severity: ViolationSeverity
    detection_method: DetectionMethod
    confidence_score: float
    evidence: Dict[str, Any]
    status: ViolationStatus
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


@dataclass
class ViolationAction:
    action_id: str
    incident_id: str
    action_type: str
    executed_at: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ViolationMetrics:
    total_detections: int = 0
    confirmed_violations: int = 0
    false_positives: int = 0
    auto_resolved: int = 0
    manual_review_required: int = 0


@dataclass
class StreamingViolationRecord:
    record_id: str = field(default_factory=lambda: str(uuid4()))
    stream_id: str = ""
    config: Optional[ViolationDetectionConfig] = None
    incidents: List[ViolationIncident] = field(default_factory=list)
    actions: List[ViolationAction] = field(default_factory=list)
    metrics: Optional[ViolationMetrics] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


# Alias
StreamingViolationDetectionRecord = StreamingViolationRecord


class StreamingViolationDetector:
    """Détecteur de violations avec règles configurables et actions automatiques."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Base de règles de détection
        self.violation_rules: Dict[ViolationType, List[ViolationRule]] = {}
        self._init_default_rules()
        
        # Patterns compilés pour performance
        self.compiled_patterns: Dict[str, Pattern] = {}
        
        # Incidents détectés
        self.incidents: List[ViolationIncident] = []
        self.pending_review: List[ViolationIncident] = []
        
        # Métriques
        self.metrics = ViolationMetrics()
        
        # Actions prises
        self.actions_log: List[ViolationAction] = []
        
        self.logger = logging.getLogger(__name__)

    def _init_default_rules(self) -> None:
        """Initialise les règles de détection par défaut."""
        
        # Règles pour spam
        spam_rules = [
            ViolationRule(
                rule_id=str(uuid4()),
                violation_type=ViolationType.SPAM,
                patterns=[
                    r"(buy|purchase|click here|limited offer)",
                    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                    r"(free money|win prize|congratulations)"
                ],
                severity=ViolationSeverity.MEDIUM,
                auto_block=False
            )
        ]
        self.violation_rules[ViolationType.SPAM] = spam_rules
        
        # Règles pour hate speech
        hate_speech_rules = [
            ViolationRule(
                rule_id=str(uuid4()),
                violation_type=ViolationType.HATE_SPEECH,
                patterns=[
                    # Patterns génériques (en production: liste complète + NLP)
                    r"(offensive|profanity|slur)"
                ],
                severity=ViolationSeverity.HIGH,
                auto_block=True
            )
        ]
        self.violation_rules[ViolationType.HATE_SPEECH] = hate_speech_rules
        
        # Compiler les patterns
        for violation_type, rules in self.violation_rules.items():
            for rule in rules:
                for pattern in rule.patterns:
                    if pattern not in self.compiled_patterns:
                        self.compiled_patterns[pattern] = re.compile(pattern, re.IGNORECASE)

    async def analyze_content(
        self,
        stream_id: str,
        content: Dict[str, Any],
        config: Optional[ViolationDetectionConfig] = None
    ) -> List[ViolationIncident]:
        """Analyse le contenu pour détecter des violations."""
        
        detected_incidents: List[ViolationIncident] = []
        
        # Extraire le texte à analyser
        text_content = self._extract_text(content)
        
        # Analyser avec chaque type de règle
        enabled_types = config.enabled_types if config else list(ViolationType)
        
        for violation_type in enabled_types:
            if violation_type not in self.violation_rules:
                continue
            
            rules = self.violation_rules[violation_type]
            
            for rule in rules:
                # Vérification par pattern matching
                matches = await self._check_patterns(text_content, rule)
                
                if matches:
                    confidence = self._calculate_confidence(matches, rule)
                    
                    # Créer l'incident si confiance suffisante
                    threshold = config.sensitivity if config else 0.75
                    
                    if confidence >= threshold:
                        incident = ViolationIncident(
                            incident_id=str(uuid4()),
                            stream_id=stream_id,
                            violation_type=violation_type,
                            severity=rule.severity,
                            detection_method=DetectionMethod.PATTERN_ANALYSIS,
                            confidence_score=confidence,
                            evidence={
                                "matches": matches,
                                "rule_id": rule.rule_id,
                                "content_sample": text_content[:200]
                            },
                            status=ViolationStatus.DETECTED
                        )
                        
                        detected_incidents.append(incident)
                        self.incidents.append(incident)
                        self.metrics.total_detections += 1
                        
                        # Action automatique si configuré
                        if rule.auto_block and (config is None or config.auto_action):
                            await self._take_action(incident, "auto_block")
                        elif confidence < (config.review_threshold if config else 0.90):
                            self.pending_review.append(incident)
                            self.metrics.manual_review_required += 1
        
        # Analyse IA supplémentaire si disponible
        if config and DetectionMethod.AI_CLASSIFICATION in [DetectionMethod.AI_CLASSIFICATION]:
            ai_incidents = await self._ai_classification(stream_id, text_content, config)
            detected_incidents.extend(ai_incidents)
        
        if detected_incidents:
            self.logger.warning(
                f"Violations detected: stream={stream_id}, count={len(detected_incidents)}, "
                f"types={set(i.violation_type.value for i in detected_incidents)}"
            )
        
        return detected_incidents

    def _extract_text(self, content: Dict[str, Any]) -> str:
        """Extrait le texte du contenu."""
        text_parts = []
        
        # Titre
        if "title" in content:
            text_parts.append(content["title"])
        
        # Description
        if "description" in content:
            text_parts.append(content["description"])
        
        # Chat/commentaires
        if "chat_messages" in content:
            for msg in content["chat_messages"]:
                text_parts.append(msg.get("text", ""))
        
        # Metadata
        if "tags" in content:
            text_parts.extend(content["tags"])
        
        return " ".join(text_parts)

    async def _check_patterns(self, text: str, rule: ViolationRule) -> List[str]:
        """Vérifie les patterns d'une règle."""
        matches = []
        
        for pattern in rule.patterns:
            compiled = self.compiled_patterns.get(pattern)
            if compiled:
                found = compiled.findall(text)
                matches.extend(found)
        
        return matches

    def _calculate_confidence(self, matches: List[str], rule: ViolationRule) -> float:
        """Calcule le score de confiance basé sur les matches."""
        # Confidence basée sur le nombre de matches et la sévérité
        base_confidence = min(len(matches) * 0.20, 0.80)
        
        # Bonus selon la sévérité de la règle
        severity_bonus = {
            ViolationSeverity.LOW: 0.0,
            ViolationSeverity.MEDIUM: 0.05,
            ViolationSeverity.HIGH: 0.10,
            ViolationSeverity.CRITICAL: 0.15
        }
        
        confidence = base_confidence + severity_bonus.get(rule.severity, 0.0)
        
        return min(confidence, 1.0)

    async def _ai_classification(
        self,
        stream_id: str,
        text: str,
        config: ViolationDetectionConfig
    ) -> List[ViolationIncident]:
        """Classification IA du contenu."""
        # En production: modèle NLP/BERT pour classification
        # Simulation: détection basée sur longueur et mots-clés
        
        incidents = []
        
        # Exemple: détecter contenu inapproprié par analyse sémantique
        inappropriate_keywords = ["violence", "explicit", "graphic"]
        found_keywords = [kw for kw in inappropriate_keywords if kw in text.lower()]
        
        if found_keywords:
            incident = ViolationIncident(
                incident_id=str(uuid4()),
                stream_id=stream_id,
                violation_type=ViolationType.INAPPROPRIATE_CONTENT,
                severity=ViolationSeverity.HIGH,
                detection_method=DetectionMethod.AI_CLASSIFICATION,
                confidence_score=0.85,
                evidence={"ai_keywords": found_keywords},
                status=ViolationStatus.DETECTED
            )
            incidents.append(incident)
            self.incidents.append(incident)
            self.metrics.total_detections += 1
        
        return incidents

    async def _take_action(self, incident: ViolationIncident, action_type: str) -> None:
        """Prend une action sur une violation."""
        
        action = ViolationAction(
            action_id=str(uuid4()),
            incident_id=incident.incident_id,
            action_type=action_type,
            details={
                "violation_type": incident.violation_type.value,
                "severity": incident.severity.value,
                "stream_id": incident.stream_id
            }
        )
        
        self.actions_log.append(action)
        
        # Exécuter l'action
        if action_type == "auto_block":
            # En production: bloquer le stream, notifier l'utilisateur
            self.logger.warning(f"AUTO-BLOCKED: stream={incident.stream_id}, incident={incident.incident_id}")
            incident.status = ViolationStatus.CONFIRMED
            self.metrics.auto_resolved += 1
            
        elif action_type == "warn_user":
            # Envoyer avertissement
            self.logger.info(f"WARNING SENT: stream={incident.stream_id}")
            
        elif action_type == "flag_for_review":
            # Marquer pour revue manuelle
            incident.status = ViolationStatus.UNDER_REVIEW
            self.pending_review.append(incident)

    async def report_violation(
        self,
        stream_id: str,
        reported_by: str,
        violation_type: ViolationType,
        description: str
    ) -> ViolationIncident:
        """Rapporte une violation (user report)."""
        
        incident = ViolationIncident(
            incident_id=str(uuid4()),
            stream_id=stream_id,
            violation_type=violation_type,
            severity=ViolationSeverity.MEDIUM,
            detection_method=DetectionMethod.USER_REPORT,
            confidence_score=0.60,  # User reports ont moins de confiance initiale
            evidence={
                "reported_by": reported_by,
                "description": description
            },
            status=ViolationStatus.UNDER_REVIEW
        )
        
        self.incidents.append(incident)
        self.pending_review.append(incident)
        self.metrics.total_detections += 1
        self.metrics.manual_review_required += 1
        
        self.logger.info(f"User report: stream={stream_id}, type={violation_type.value}")
        
        return incident

    async def review_incident(
        self,
        incident_id: str,
        is_confirmed: bool,
        reviewer_id: str
    ) -> bool:
        """Revue manuelle d'un incident."""
        
        incident = next((i for i in self.incidents if i.incident_id == incident_id), None)
        
        if not incident:
            return False
        
        if is_confirmed:
            incident.status = ViolationStatus.CONFIRMED
            self.metrics.confirmed_violations += 1
            await self._take_action(incident, "block")
        else:
            incident.status = ViolationStatus.FALSE_POSITIVE
            self.metrics.false_positives += 1
        
        incident.resolved_at = datetime.utcnow()
        
        # Retirer de pending review
        if incident in self.pending_review:
            self.pending_review.remove(incident)
        
        self.logger.info(
            f"Incident reviewed: {incident_id}, confirmed={is_confirmed}, "
            f"reviewer={reviewer_id}"
        )
        
        return True

    def add_rule(self, rule: ViolationRule) -> None:
        """Ajoute une règle de détection."""
        if rule.violation_type not in self.violation_rules:
            self.violation_rules[rule.violation_type] = []
        
        self.violation_rules[rule.violation_type].append(rule)
        
        # Compiler les nouveaux patterns
        for pattern in rule.patterns:
            if pattern not in self.compiled_patterns:
                self.compiled_patterns[pattern] = re.compile(pattern, re.IGNORECASE)
        
        self.logger.info(f"Rule added: {rule.rule_id}, type={rule.violation_type.value}")

    def get_metrics(self) -> ViolationMetrics:
        """Retourne les métriques."""
        return self.metrics


def create_streamingviolation_detector(config: Optional[Dict[str, Any]] = None) -> StreamingViolationDetector:
    return StreamingViolationDetector(config=config)


create_streaming_violation_detector = create_streamingviolation_detector


__all__ = [
    "StreamingViolationDetector",
    "ViolationType",
    "ViolationSeverity",
    "SeverityLevel",
    "DetectionMethod",
    "ViolationStatus",
    "ViolationDetectionConfig",
    "ViolationRule",
    "ViolationIncident",
    "ViolationAction",
    "ViolationMetrics",
    "StreamingViolationRecord",
    "StreamingViolationDetectionRecord",
    "create_streamingviolation_detector",
    "create_streaming_violation_detector"
]
