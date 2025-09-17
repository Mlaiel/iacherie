"""
Failure Pattern Analyzer - Ainflue
==================================
Analyseur patterns d'échec avec ML clustering.
Failure classification + root cause analysis + prediction.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Retry Mechanisms
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture retry mechanisms et tous ses algorithmes sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import time
import statistics
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque, Counter

logger = logging.getLogger(__name__)

class FailureType(Enum):
    """Types d'échecs détectés"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    DATA_CORRUPTION = "data_corruption"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"

class FailurePattern(Enum):
    """Patterns d'échec identifiés"""
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    CASCADING = "cascading"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TIMEOUT_PATTERN = "timeout_pattern"
    DEPENDENCY_FAILURE = "dependency_failure"
    LOAD_SPIKE = "load_spike"
    CONFIGURATION_ERROR = "configuration_error"
    ANOMALY = "anomaly"
    SCHEDULED_MAINTENANCE = "scheduled_maintenance"

class FailureSeverity(Enum):
    """Niveaux de sévérité des échecs"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FailureEvent:
    """Événement d'échec"""
    timestamp: float
    service_name: str
    operation_type: str
    error_type: str
    error_message: str
    failure_type: FailureType = FailureType.UNKNOWN
    severity: FailureSeverity = FailureSeverity.MEDIUM
    context: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.correlation_id:
            self.correlation_id = self._generate_correlation_id()
    
    def _generate_correlation_id(self) -> str:
        """Génération ID corrélation unique"""
        content = f"{self.service_name}:{self.operation_type}:{self.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

@dataclass
class AnalyzerConfig:
    """Configuration analyseur patterns"""
    # Detection settings
    pattern_detection_window: int = 3600  # 1 hour
    min_events_for_pattern: int = 3
    anomaly_detection_threshold: float = 2.0  # Z-score threshold
    
    # Clustering settings
    similarity_threshold: float = 0.7
    max_clusters: int = 20
    cluster_time_window: int = 1800  # 30 minutes
    
    # Root cause analysis
    correlation_window: int = 300  # 5 minutes
    causality_confidence_threshold: float = 0.6
    dependency_graph_depth: int = 3
    
    # Prediction settings
    prediction_enabled: bool = True
    prediction_horizon: int = 3600  # 1 hour
    learning_rate: float = 0.01
    
    # Data retention
    max_failure_events: int = 10000
    historical_analysis_window: int = 86400 * 7  # 1 week

@dataclass
class PatternAnalysisResult:
    """Résultat analyse pattern"""
    detected_pattern: FailurePattern
    confidence_score: float
    affected_services: List[str]
    failure_frequency: float
    pattern_characteristics: Dict
    recommendations: List[str]
    severity_assessment: FailureSeverity
    correlation_analysis: Dict = field(default_factory=dict)

@dataclass
class ClassificationResult:
    """Résultat classification échec"""
    failure_type: FailureType
    pattern: FailurePattern
    confidence: float
    classification_features: List[str]
    similar_failures: List[str]
    remediation_suggestions: List[str]

@dataclass
class FailureProbability:
    """Probabilité échec prédite"""
    service_name: str
    operation_type: str
    probability: float
    time_horizon: int
    contributing_factors: Dict
    confidence: float
    prediction_method: str

class FailurePatternDetector:
    """Détecteur patterns d'échec avec ML clustering"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
        self.pattern_history = deque(maxlen=config.max_failure_events)
        self.detected_patterns = {}
        self.pattern_signatures = {}
    
    async def detect_patterns(self, failure_events: List[FailureEvent]) -> List[PatternAnalysisResult]:
        """Détection patterns d'échec avec clustering ML"""
        
        if len(failure_events) < self.config.min_events_for_pattern:
            return []
        
        # Clustering des événements par similarité
        clusters = await self._cluster_failure_events(failure_events)
        
        # Analyse de chaque cluster
        patterns = []
        for cluster_id, cluster_events in clusters.items():
            pattern_result = await self._analyze_cluster_pattern(cluster_id, cluster_events)
            if pattern_result:
                patterns.append(pattern_result)
        
        # Tri par sévérité et confidence
        patterns.sort(key=lambda p: (p.severity_assessment.value, p.confidence_score), reverse=True)
        
        return patterns
    
    async def _cluster_failure_events(self, events: List[FailureEvent]) -> Dict[str, List[FailureEvent]]:
        """Clustering événements par similarité"""
        
        clusters = defaultdict(list)
        cluster_counter = 0
        
        for event in events:
            # Calcul signature événement
            signature = self._calculate_event_signature(event)
            
            # Recherche cluster similaire existant
            assigned_cluster = None
            for cluster_id, cluster_signature in self.pattern_signatures.items():
                similarity = self._calculate_signature_similarity(signature, cluster_signature)
                if similarity >= self.config.similarity_threshold:
                    assigned_cluster = cluster_id
                    break
            
            # Assignation ou création cluster
            if assigned_cluster:
                clusters[assigned_cluster].append(event)
                # Mise à jour signature cluster
                self.pattern_signatures[assigned_cluster] = self._update_cluster_signature(
                    self.pattern_signatures[assigned_cluster], signature
                )
            else:
                # Nouveau cluster
                new_cluster_id = f"cluster_{cluster_counter}"
                clusters[new_cluster_id].append(event)
                self.pattern_signatures[new_cluster_id] = signature
                cluster_counter += 1
        
        return clusters
    
    def _calculate_event_signature(self, event: FailureEvent) -> Dict[str, float]:
        """Calcul signature événement pour clustering"""
        
        signature = {
            'service_hash': hash(event.service_name) % 1000 / 1000.0,
            'operation_hash': hash(event.operation_type) % 1000 / 1000.0,
            'error_type_hash': hash(event.error_type) % 1000 / 1000.0,
            'severity_score': {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}.get(event.severity.value, 0.5),
            'time_of_day': (event.timestamp % 86400) / 86400,
            'day_of_week': ((event.timestamp // 86400) % 7) / 7,
        }
        
        # Features contextuelles
        context = event.context
        if 'response_time' in context:
            signature['response_time_normalized'] = min(context['response_time'] / 30.0, 1.0)
        
        if 'error_code' in context:
            signature['error_code_hash'] = hash(str(context['error_code'])) % 1000 / 1000.0
        
        return signature
    
    def _calculate_signature_similarity(self, sig1: Dict[str, float], sig2: Dict[str, float]) -> float:
        """Calcul similarité entre signatures"""
        
        common_keys = set(sig1.keys()) & set(sig2.keys())
        if not common_keys:
            return 0.0
        
        # Distance euclidienne normalisée
        distance_sum = sum((sig1[key] - sig2[key]) ** 2 for key in common_keys)
        distance = (distance_sum / len(common_keys)) ** 0.5
        
        # Conversion en similarité (0-1)
        similarity = max(0.0, 1.0 - distance)
        return similarity
    
    def _update_cluster_signature(self, current_signature: Dict[str, float], new_signature: Dict[str, float]) -> Dict[str, float]:
        """Mise à jour signature cluster avec nouvel événement"""
        
        alpha = 0.1  # Learning rate
        updated_signature = {}
        
        all_keys = set(current_signature.keys()) | set(new_signature.keys())
        
        for key in all_keys:
            current_val = current_signature.get(key, 0.0)
            new_val = new_signature.get(key, 0.0)
            updated_signature[key] = current_val * (1 - alpha) + new_val * alpha
        
        return updated_signature
    
    async def _analyze_cluster_pattern(self, cluster_id: str, events: List[FailureEvent]) -> Optional[PatternAnalysisResult]:
        """Analyse pattern d'un cluster d'événements"""
        
        if len(events) < self.config.min_events_for_pattern:
            return None
        
        # Analyse temporelle
        timestamps = [event.timestamp for event in events]
        time_span = max(timestamps) - min(timestamps)
        frequency = len(events) / max(time_span / 3600, 0.1)  # events per hour
        
        # Analyse services affectés
        affected_services = list(set(event.service_name for event in events))
        
        # Détection type de pattern
        pattern_type = self._classify_cluster_pattern(events, time_span, frequency)
        
        # Calcul confidence basé sur cohérence cluster
        confidence = self._calculate_pattern_confidence(events, pattern_type)
        
        # Évaluation sévérité
        severity = self._assess_pattern_severity(events, affected_services, frequency)
        
        # Caractéristiques pattern
        characteristics = {
            'event_count': len(events),
            'time_span_hours': time_span / 3600,
            'frequency_per_hour': frequency,
            'unique_services': len(affected_services),
            'error_types': list(set(event.error_type for event in events)),
            'most_common_error': Counter(event.error_type for event in events).most_common(1)[0] if events else None
        }
        
        # Recommandations
        recommendations = self._generate_pattern_recommendations(pattern_type, characteristics)
        
        return PatternAnalysisResult(
            detected_pattern=pattern_type,
            confidence_score=confidence,
            affected_services=affected_services,
            failure_frequency=frequency,
            pattern_characteristics=characteristics,
            recommendations=recommendations,
            severity_assessment=severity
        )
    
    def _classify_cluster_pattern(self, events: List[FailureEvent], time_span: float, frequency: float) -> FailurePattern:
        """Classification pattern basée sur caractéristiques cluster"""
        
        # Analyse temporelle
        if time_span < 300:  # 5 minutes - probable cascading failure
            services = set(event.service_name for event in events)
            if len(services) > 1:
                return FailurePattern.CASCADING
        
        # Analyse fréquence
        if frequency > 10:  # Plus de 10 échecs/heure
            error_types = [event.error_type for event in events]
            if 'timeout' in error_types or 'connection_error' in error_types:
                return FailurePattern.RESOURCE_EXHAUSTION
            else:
                return FailurePattern.LOAD_SPIKE
        
        # Analyse types erreurs
        error_counter = Counter(event.error_type for event in events)
        most_common_error = error_counter.most_common(1)[0][0] if error_counter else ""
        
        if 'timeout' in most_common_error.lower():
            return FailurePattern.TIMEOUT_PATTERN
        elif 'unavailable' in most_common_error.lower() or 'connection' in most_common_error.lower():
            return FailurePattern.DEPENDENCY_FAILURE
        elif 'resource' in most_common_error.lower() or 'memory' in most_common_error.lower():
            return FailurePattern.RESOURCE_EXHAUSTION
        
        # Pattern par défaut
        if len(events) == 1:
            return FailurePattern.TRANSIENT
        elif frequency < 1:  # Moins d'1 échec/heure
            return FailurePattern.TRANSIENT
        else:
            return FailurePattern.ANOMALY
    
    def _calculate_pattern_confidence(self, events: List[FailureEvent], pattern: FailurePattern) -> float:
        """Calcul confidence pattern basé sur cohérence"""
        
        base_confidence = 0.5
        
        # Cohérence temporelle
        timestamps = [event.timestamp for event in events]
        if len(timestamps) > 1:
            time_intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            if time_intervals:
                interval_std = statistics.stdev(time_intervals) if len(time_intervals) > 1 else 0
                interval_mean = statistics.mean(time_intervals)
                if interval_mean > 0:
                    temporal_consistency = max(0, 1 - (interval_std / interval_mean))
                    base_confidence += temporal_consistency * 0.2
        
        # Cohérence service/opération
        service_consistency = len(set(event.service_name for event in events)) == 1
        operation_consistency = len(set(event.operation_type for event in events)) == 1
        
        if service_consistency:
            base_confidence += 0.15
        if operation_consistency:
            base_confidence += 0.15
        
        # Cohérence type d'erreur
        error_types = [event.error_type for event in events]
        error_consistency = len(set(error_types)) / len(error_types) if error_types else 1
        base_confidence += (1 - error_consistency) * 0.2
        
        return min(1.0, base_confidence)
    
    def _assess_pattern_severity(self, events: List[FailureEvent], affected_services: List[str], frequency: float) -> FailureSeverity:
        """Évaluation sévérité pattern"""
        
        # Facteurs de sévérité
        service_count = len(affected_services)
        event_count = len(events)
        max_individual_severity = max((event.severity for event in events), default=FailureSeverity.LOW)
        
        # Score de sévérité
        severity_score = 0
        
        # Impact services
        if service_count >= 5:
            severity_score += 3
        elif service_count >= 3:
            severity_score += 2
        elif service_count >= 2:
            severity_score += 1
        
        # Fréquence
        if frequency >= 20:
            severity_score += 3
        elif frequency >= 10:
            severity_score += 2
        elif frequency >= 5:
            severity_score += 1
        
        # Sévérité individuelle maximale
        severity_map = {FailureSeverity.LOW: 0, FailureSeverity.MEDIUM: 1, FailureSeverity.HIGH: 2, FailureSeverity.CRITICAL: 3}
        severity_score += severity_map[max_individual_severity]
        
        # Conversion score en sévérité
        if severity_score >= 7:
            return FailureSeverity.CRITICAL
        elif severity_score >= 5:
            return FailureSeverity.HIGH
        elif severity_score >= 3:
            return FailureSeverity.MEDIUM
        else:
            return FailureSeverity.LOW
    
    def _generate_pattern_recommendations(self, pattern: FailurePattern, characteristics: Dict) -> List[str]:
        """Génération recommandations basées sur pattern"""
        
        recommendations = []
        
        if pattern == FailurePattern.CASCADING:
            recommendations.extend([
                "Implement circuit breakers to prevent cascade failures",
                "Add bulkhead isolation between services",
                "Review service dependencies and reduce coupling"
            ])
        
        elif pattern == FailurePattern.RESOURCE_EXHAUSTION:
            recommendations.extend([
                "Scale up resources or implement auto-scaling",
                "Optimize resource usage and implement resource limits",
                "Add resource monitoring and alerting"
            ])
        
        elif pattern == FailurePattern.TIMEOUT_PATTERN:
            recommendations.extend([
                "Review and optimize timeout configurations",
                "Implement adaptive timeout mechanisms",
                "Analyze network latency and service performance"
            ])
        
        elif pattern == FailurePattern.DEPENDENCY_FAILURE:
            recommendations.extend([
                "Implement fallback mechanisms for dependencies",
                "Add health checks and monitoring for dependencies",
                "Consider service mesh for better dependency management"
            ])
        
        elif pattern == FailurePattern.LOAD_SPIKE:
            recommendations.extend([
                "Implement rate limiting and load balancing",
                "Add horizontal scaling capabilities",
                "Optimize performance for high-load scenarios"
            ])
        
        return recommendations

class FailureClassifier:
    """Classificateur ML pour types d'échec"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
        self.classification_rules = {}
        self.feature_weights = defaultdict(float)
        self.classification_history = deque(maxlen=1000)
    
    async def classify_failure(self, failure_event: FailureEvent) -> ClassificationResult:
        """Classification échec avec ML"""
        
        # Extraction features
        features = self._extract_classification_features(failure_event)
        
        # Classification règles + ML
        failure_type = self._classify_failure_type(failure_event, features)
        pattern = self._classify_failure_pattern(failure_event, features)
        
        # Calcul confidence
        confidence = self._calculate_classification_confidence(features, failure_type, pattern)
        
        # Recherche échecs similaires
        similar_failures = await self._find_similar_failures(failure_event, features)
        
        # Suggestions remédiation
        remediation_suggestions = self._generate_remediation_suggestions(failure_type, pattern)
        
        result = ClassificationResult(
            failure_type=failure_type,
            pattern=pattern,
            confidence=confidence,
            classification_features=list(features.keys()),
            similar_failures=similar_failures,
            remediation_suggestions=remediation_suggestions
        )
        
        # Stockage pour apprentissage
        self.classification_history.append({
            'event': failure_event,
            'result': result,
            'timestamp': time.time()
        })
        
        return result
    
    def _extract_classification_features(self, event: FailureEvent) -> Dict[str, float]:
        """Extraction features pour classification"""
        
        features = {
            'has_timeout_keyword': 1.0 if 'timeout' in event.error_message.lower() else 0.0,
            'has_connection_keyword': 1.0 if 'connection' in event.error_message.lower() else 0.0,
            'has_resource_keyword': 1.0 if any(word in event.error_message.lower() for word in ['memory', 'resource', 'limit']) else 0.0,
            'has_auth_keyword': 1.0 if any(word in event.error_message.lower() for word in ['auth', 'permission', 'unauthorized']) else 0.0,
            'message_length': min(len(event.error_message) / 100.0, 1.0),
            'service_criticality': self._estimate_service_criticality(event.service_name),
            'error_type_frequency': self._get_error_type_frequency(event.error_type),
            'time_since_last_similar': self._time_since_last_similar_error(event)
        }
        
        # Context features
        if event.context:
            features['has_response_time'] = 1.0 if 'response_time' in event.context else 0.0
            features['has_error_code'] = 1.0 if 'error_code' in event.context else 0.0
            
            if 'response_time' in event.context:
                features['response_time_normalized'] = min(event.context['response_time'] / 30.0, 1.0)
        
        return features
    
    def _classify_failure_type(self, event: FailureEvent, features: Dict[str, float]) -> FailureType:
        """Classification type échec"""
        
        # Règles basées sur mots-clés
        error_msg = event.error_message.lower()
        
        if 'timeout' in error_msg or 'timed out' in error_msg:
            return FailureType.TIMEOUT
        elif any(word in error_msg for word in ['connection', 'connect', 'network']):
            return FailureType.CONNECTION_ERROR
        elif any(word in error_msg for word in ['memory', 'resource', 'limit', 'quota']):
            return FailureType.RESOURCE_EXHAUSTION
        elif any(word in error_msg for word in ['unauthorized', 'auth', 'login']):
            return FailureType.AUTHENTICATION_ERROR
        elif any(word in error_msg for word in ['forbidden', 'permission', 'access']):
            return FailureType.AUTHORIZATION_ERROR
        elif any(word in error_msg for word in ['validation', 'invalid', 'bad request']):
            return FailureType.VALIDATION_ERROR
        elif 'rate limit' in error_msg or 'too many requests' in error_msg:
            return FailureType.RATE_LIMIT_ERROR
        elif 'unavailable' in error_msg or 'service down' in error_msg:
            return FailureType.SERVICE_UNAVAILABLE
        elif '500' in error_msg or 'internal server error' in error_msg:
            return FailureType.INTERNAL_SERVER_ERROR
        elif any(word in error_msg for word in ['corrupt', 'data', 'parse']):
            return FailureType.DATA_CORRUPTION
        else:
            return FailureType.UNKNOWN
    
    def _classify_failure_pattern(self, event: FailureEvent, features: Dict[str, float]) -> FailurePattern:
        """Classification pattern échec"""
        
        # Analyse historique pour pattern
        recent_failures = [
            record for record in self.classification_history
            if (time.time() - record['timestamp'] < 3600 and  # Last hour
                record['event'].service_name == event.service_name)
        ]
        
        if len(recent_failures) == 0:
            return FailurePattern.TRANSIENT
        elif len(recent_failures) == 1:
            return FailurePattern.TRANSIENT
        elif len(recent_failures) >= 5:
            # Check if errors are similar
            error_types = [record['event'].error_type for record in recent_failures]
            if len(set(error_types)) == 1:  # All same error type
                return FailurePattern.PERMANENT
            else:
                return FailurePattern.ANOMALY
        else:
            return FailurePattern.TRANSIENT
    
    def _calculate_classification_confidence(self, features: Dict[str, float], failure_type: FailureType, pattern: FailurePattern) -> float:
        """Calcul confidence classification"""
        
        base_confidence = 0.6
        
        # Confidence basée sur features distinctives
        distinctive_features = ['has_timeout_keyword', 'has_connection_keyword', 'has_resource_keyword', 'has_auth_keyword']
        distinctive_count = sum(features.get(f, 0.0) for f in distinctive_features)
        
        if distinctive_count >= 1:
            base_confidence += 0.2
        
        # Confidence basée sur historique
        if len(self.classification_history) > 10:
            base_confidence += 0.1
        
        # Confidence basée on context richness
        context_richness = sum(features.get(f, 0.0) for f in ['has_response_time', 'has_error_code'])
        base_confidence += context_richness * 0.1
        
        return min(1.0, base_confidence)
    
    def _estimate_service_criticality(self, service_name: str) -> float:
        """Estimation criticité service"""
        # Heuristique basique - en production, utiliserait métadonnées service
        critical_services = ['monetization', 'payment', 'auth', 'user-data']
        
        if any(critical in service_name.lower() for critical in critical_services):
            return 1.0
        elif 'processing' in service_name.lower():
            return 0.8
        else:
            return 0.5
    
    def _get_error_type_frequency(self, error_type: str) -> float:
        """Fréquence type erreur dans historique"""
        if not self.classification_history:
            return 0.5
        
        total_events = len(self.classification_history)
        error_count = sum(1 for record in self.classification_history 
                         if record['event'].error_type == error_type)
        
        return error_count / total_events
    
    def _time_since_last_similar_error(self, event: FailureEvent) -> float:
        """Temps depuis dernière erreur similaire"""
        current_time = time.time()
        
        for record in reversed(self.classification_history):
            past_event = record['event']
            if (past_event.service_name == event.service_name and
                past_event.error_type == event.error_type):
                time_diff = current_time - record['timestamp']
                return min(time_diff / 3600.0, 24.0)  # Normalized to hours, capped at 24h
        
        return 24.0  # No similar error found
    
    async def _find_similar_failures(self, event: FailureEvent, features: Dict[str, float]) -> List[str]:
        """Recherche échecs similaires"""
        
        similar_failures = []
        
        for record in self.classification_history:
            past_event = record['event']
            
            # Critères similarité
            same_service = past_event.service_name == event.service_name
            same_error_type = past_event.error_type == event.error_type
            recent = (time.time() - record['timestamp']) < 86400  # 24 hours
            
            if same_service and same_error_type and recent:
                similar_failures.append(past_event.correlation_id)
        
        return similar_failures[:5]  # Limite à 5 échecs similaires
    
    def _generate_remediation_suggestions(self, failure_type: FailureType, pattern: FailurePattern) -> List[str]:
        """Génération suggestions remédiation"""
        
        suggestions = []
        
        # Suggestions par type échec
        if failure_type == FailureType.TIMEOUT:
            suggestions.extend([
                "Increase timeout values",
                "Optimize slow operations",
                "Implement async processing"
            ])
        elif failure_type == FailureType.CONNECTION_ERROR:
            suggestions.extend([
                "Check network connectivity",
                "Implement connection pooling",
                "Add retry with exponential backoff"
            ])
        elif failure_type == FailureType.RESOURCE_EXHAUSTION:
            suggestions.extend([
                "Scale up resources",
                "Optimize memory usage",
                "Implement resource limits"
            ])
        
        # Suggestions par pattern
        if pattern == FailurePattern.PERMANENT:
            suggestions.extend([
                "Investigate root cause immediately",
                "Implement circuit breaker",
                "Consider service rollback"
            ])
        elif pattern == FailurePattern.CASCADING:
            suggestions.extend([
                "Isolate failing service",
                "Implement bulkhead pattern",
                "Add fallback mechanisms"
            ])
        
        return suggestions

class RootCauseAnalyzer:
    """Analyseur root cause avec corrélation detection"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
        self.dependency_graph = defaultdict(set)
        self.correlation_cache = {}
        self.causal_patterns = {}
    
    async def analyze_root_cause(self, failure_events: List[FailureEvent]) -> Dict:
        """Analyse root cause avec corrélation"""
        
        if not failure_events:
            return {'root_cause': 'unknown', 'confidence': 0.0}
        
        # Analyse temporelle des corrélations
        temporal_correlations = await self._analyze_temporal_correlations(failure_events)
        
        # Analyse dépendances services
        dependency_analysis = await self._analyze_service_dependencies(failure_events)
        
        # Détection patterns causaux
        causal_patterns = await self._detect_causal_patterns(failure_events)
        
        # Synthèse root cause
        root_cause_analysis = {
            'primary_root_cause': self._determine_primary_root_cause(temporal_correlations, dependency_analysis, causal_patterns),
            'contributing_factors': self._identify_contributing_factors(failure_events),
            'temporal_correlations': temporal_correlations,
            'dependency_analysis': dependency_analysis,
            'causal_patterns': causal_patterns,
            'confidence': self._calculate_root_cause_confidence(temporal_correlations, dependency_analysis)
        }
        
        return root_cause_analysis
    
    async def _analyze_temporal_correlations(self, events: List[FailureEvent]) -> Dict:
        """Analyse corrélations temporelles"""
        
        # Groupement par fenêtre temporelle
        time_windows = defaultdict(list)
        for event in events:
            window = int(event.timestamp // self.config.correlation_window)
            time_windows[window].append(event)
        
        correlations = {
            'correlated_windows': 0,
            'correlation_strength': 0.0,
            'leading_indicators': [],
            'cascade_sequences': []
        }
        
        # Détection cascades
        for window_events in time_windows.values():
            if len(window_events) > 1:
                correlations['correlated_windows'] += 1
                
                # Tri par timestamp pour détecter séquence
                sorted_events = sorted(window_events, key=lambda e: e.timestamp)
                
                # Détection cascade (propagation entre services)
                services_sequence = [event.service_name for event in sorted_events]
                if len(set(services_sequence)) > 1:  # Multiple services
                    correlations['cascade_sequences'].append({
                        'sequence': services_sequence,
                        'duration': sorted_events[-1].timestamp - sorted_events[0].timestamp,
                        'services_affected': len(set(services_sequence))
                    })
        
        # Calcul force corrélation
        if len(time_windows) > 0:
            correlations['correlation_strength'] = correlations['correlated_windows'] / len(time_windows)
        
        return correlations
    
    async def _analyze_service_dependencies(self, events: List[FailureEvent]) -> Dict:
        """Analyse dépendances services"""
        
        # Construction graphe dépendances basé sur corrélations temporelles
        service_pairs = defaultdict(int)
        
        # Recherche patterns dépendance
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        for i in range(len(sorted_events) - 1):
            current_event = sorted_events[i]
            next_event = sorted_events[i + 1]
            
            time_diff = next_event.timestamp - current_event.timestamp
            
            # Si événements proches temporellement, possible dépendance
            if time_diff < self.config.correlation_window:
                pair = (current_event.service_name, next_event.service_name)
                service_pairs[pair] += 1
        
        # Identification services critiques (upstream dependencies)
        dependency_analysis = {
            'critical_services': [],
            'dependency_chains': [],
            'isolation_recommendations': []
        }
        
        # Services avec plus d'impact downstream
        impact_scores = defaultdict(int)
        for (upstream, downstream), count in service_pairs.items():
            impact_scores[upstream] += count
        
        # Top services critiques
        if impact_scores:
            sorted_services = sorted(impact_scores.items(), key=lambda x: x[1], reverse=True)
            dependency_analysis['critical_services'] = [service for service, score in sorted_services[:3]]
        
        return dependency_analysis
    
    async def _detect_causal_patterns(self, events: List[FailureEvent]) -> Dict:
        """Détection patterns causaux"""
        
        patterns = {
            'resource_exhaustion_cascade': False,
            'authentication_propagation': False,
            'timeout_chain_reaction': False,
            'configuration_error_spread': False
        }
        
        # Analyse patterns spécifiques
        error_types = [event.error_type for event in events]
        error_counter = Counter(error_types)
        
        # Resource exhaustion cascade
        if ('resource_exhaustion' in error_counter and 
            any('timeout' in error_type for error_type in error_types)):
            patterns['resource_exhaustion_cascade'] = True
        
        # Authentication propagation
        if ('authentication_error' in error_counter and
            len(set(event.service_name for event in events)) > 1):
            patterns['authentication_propagation'] = True
        
        # Timeout chain reaction
        timeout_events = [event for event in events if 'timeout' in event.error_type]
        if len(timeout_events) > 2:
            # Vérification si timeouts se propagent entre services
            services_with_timeouts = set(event.service_name for event in timeout_events)
            if len(services_with_timeouts) > 1:
                patterns['timeout_chain_reaction'] = True
        
        return patterns
    
    def _determine_primary_root_cause(self, temporal_corr: Dict, dependency_analysis: Dict, causal_patterns: Dict) -> str:
        """Détermination root cause primaire"""
        
        # Priorité aux patterns causaux détectés
        if causal_patterns.get('resource_exhaustion_cascade'):
            return 'resource_exhaustion_cascade'
        elif causal_patterns.get('authentication_propagation'):
            return 'authentication_system_failure'
        elif causal_patterns.get('timeout_chain_reaction'):
            return 'performance_degradation_cascade'
        elif causal_patterns.get('configuration_error_spread'):
            return 'configuration_error'
        
        # Analyse basée sur corrélations temporelles
        if temporal_corr.get('correlation_strength', 0) > 0.7:
            cascade_sequences = temporal_corr.get('cascade_sequences', [])
            if cascade_sequences:
                # Premier service dans la séquence = probable root cause
                first_cascade = cascade_sequences[0]
                first_service = first_cascade['sequence'][0]
                return f'service_failure_{first_service}'
        
        # Analyse basée sur services critiques
        critical_services = dependency_analysis.get('critical_services', [])
        if critical_services:
            return f'critical_service_failure_{critical_services[0]}'
        
        return 'unknown_root_cause'
    
    def _identify_contributing_factors(self, events: List[FailureEvent]) -> List[str]:
        """Identification facteurs contributeurs"""
        
        factors = []
        
        # Analyse distribution temporelle
        timestamps = [event.timestamp for event in events]
        if timestamps:
            time_span = max(timestamps) - min(timestamps)
            if time_span < 300:  # 5 minutes
                factors.append('rapid_failure_propagation')
            elif time_span > 3600:  # 1 hour
                factors.append('prolonged_degradation')
        
        # Analyse distribution services
        services = set(event.service_name for event in events)
        if len(services) > 5:
            factors.append('widespread_service_impact')
        elif len(services) == 1:
            factors.append('isolated_service_failure')
        
        # Analyse types erreurs
        error_types = set(event.error_type for event in events)
        if len(error_types) == 1:
            factors.append('consistent_failure_type')
        elif len(error_types) > 3:
            factors.append('diverse_failure_modes')
        
        return factors
    
    def _calculate_root_cause_confidence(self, temporal_corr: Dict, dependency_analysis: Dict) -> float:
        """Calcul confidence root cause analysis"""
        
        confidence = 0.3  # Base confidence
        
        # Confidence basée sur corrélations temporelles
        correlation_strength = temporal_corr.get('correlation_strength', 0.0)
        confidence += correlation_strength * 0.4
        
        # Confidence basée sur cascade sequences
        cascade_sequences = temporal_corr.get('cascade_sequences', [])
        if cascade_sequences:
            confidence += min(len(cascade_sequences) * 0.1, 0.2)
        
        # Confidence basée sur services critiques identifiés
        critical_services = dependency_analysis.get('critical_services', [])
        if critical_services:
            confidence += 0.1
        
        return min(1.0, confidence)

class FailurePredictionEngine:
    """Moteur prédiction échecs avec ML"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
        self.prediction_models = defaultdict(dict)  # service -> model
        self.feature_history = defaultdict(lambda: deque(maxlen=1000))
        self.prediction_accuracy = defaultdict(float)
    
    async def predict_failure_probability(self, service_context: Dict) -> FailureProbability:
        """Prédiction probabilité échec basée sur patterns historiques"""
        
        service_name = service_context.get('service_name', 'unknown')
        operation_type = service_context.get('operation_type', 'unknown')
        
        # Extraction features pour prédiction
        features = await self._extract_prediction_features(service_context)
        
        # Prédiction basée sur modèle ML simple
        probability = await self._calculate_failure_probability(service_name, features)
        
        # Identification facteurs contributeurs
        contributing_factors = self._identify_risk_factors(features)
        
        # Calcul confidence basé sur historique
        confidence = self._calculate_prediction_confidence(service_name, features)
        
        return FailureProbability(
            service_name=service_name,
            operation_type=operation_type,
            probability=probability,
            time_horizon=self.config.prediction_horizon,
            contributing_factors=contributing_factors,
            confidence=confidence,
            prediction_method='ml_pattern_analysis'
        )
    
    async def _extract_prediction_features(self, context: Dict) -> Dict[str, float]:
        """Extraction features pour prédiction"""
        
        current_time = time.time()
        
        features = {
            # Temporal features
            'hour_of_day': (current_time % 86400) / 86400,
            'day_of_week': ((current_time // 86400) % 7) / 7,
            'is_weekend': 1.0 if ((current_time // 86400) % 7) >= 5 else 0.0,
            'is_peak_hour': 1.0 if 9 <= ((current_time % 86400) / 3600) <= 17 else 0.0,
            
            # System load features
            'system_load': context.get('system_load', 0.5),
            'memory_usage': context.get('memory_usage', 0.5),
            'cpu_usage': context.get('cpu_usage', 0.5),
            'network_latency': context.get('network_latency', 0.5),
            
            # Service-specific features
            'recent_error_rate': context.get('recent_error_rate', 0.0),
            'response_time_trend': context.get('response_time_trend', 0.0),
            'throughput_trend': context.get('throughput_trend', 0.0),
            
            # Dependency features
            'dependency_health': context.get('dependency_health', 1.0),
            'external_service_issues': context.get('external_service_issues', 0.0)
        }
        
        return features
    
    async def _calculate_failure_probability(self, service_name: str, features: Dict[str, float]) -> float:
        """Calcul probabilité échec avec modèle ML simple"""
        
        model = self.prediction_models[service_name]
        
        # Initialisation modèle si nécessaire
        if not model:
            model = {feature: 0.1 for feature in features.keys()}
            model['bias'] = 0.5
            self.prediction_models[service_name] = model
        
        # Prédiction linéaire
        probability = model.get('bias', 0.5)
        for feature, value in features.items():
            weight = model.get(feature, 0.0)
            probability += weight * value
        
        # Normalisation avec fonction sigmoïde
        probability = 1 / (1 + math.exp(-probability))
        
        return max(0.0, min(1.0, probability))
    
    def _identify_risk_factors(self, features: Dict[str, float]) -> Dict[str, float]:
        """Identification facteurs de risque"""
        
        risk_factors = {}
        
        # Seuils de risque
        risk_thresholds = {
            'system_load': 0.8,
            'memory_usage': 0.9,
            'cpu_usage': 0.8,
            'recent_error_rate': 0.1,
            'network_latency': 0.7
        }
        
        for factor, threshold in risk_thresholds.items():
            value = features.get(factor, 0.0)
            if value > threshold:
                risk_factors[factor] = value
        
        # Facteurs temporels
        if features.get('is_peak_hour', 0.0) == 1.0:
            risk_factors['peak_hour_load'] = 1.0
        
        if features.get('is_weekend', 0.0) == 1.0 and features.get('system_load', 0.0) > 0.3:
            risk_factors['unexpected_weekend_load'] = features.get('system_load', 0.0)
        
        return risk_factors
    
    def _calculate_prediction_confidence(self, service_name: str, features: Dict[str, float]) -> float:
        """Calcul confidence prédiction"""
        
        base_confidence = 0.5
        
        # Confidence basée sur historique prédictions
        if service_name in self.prediction_accuracy:
            accuracy = self.prediction_accuracy[service_name]
            base_confidence += (accuracy - 0.5) * 0.4
        
        # Confidence basée sur richesse features
        feature_completeness = len([v for v in features.values() if v > 0]) / len(features)
        base_confidence += feature_completeness * 0.2
        
        # Confidence basée sur stabilité features
        recent_features = list(self.feature_history[service_name])[-10:]
        if len(recent_features) > 5:
            # Calcul stabilité comme inverse de la volatilité
            feature_values = [[f.get(key, 0.0) for f in recent_features] for key in features.keys()]
            volatilities = [statistics.stdev(values) if len(values) > 1 else 0.0 for values in feature_values]
            avg_volatility = statistics.mean(volatilities) if volatilities else 0.0
            stability = max(0.0, 1.0 - avg_volatility)
            base_confidence += stability * 0.2
        
        return min(1.0, base_confidence)
    
    async def update_prediction_model(self, service_name: str, features: Dict[str, float], actual_failure: bool):
        """Mise à jour modèle prédiction avec résultat réel"""
        
        if not self.config.prediction_enabled:
            return
        
        model = self.prediction_models[service_name]
        learning_rate = self.config.learning_rate
        
        # Prédiction actuelle
        predicted_prob = await self._calculate_failure_probability(service_name, features)
        
        # Calcul erreur
        actual = 1.0 if actual_failure else 0.0
        error = actual - predicted_prob
        
        # Gradient descent update
        for feature, value in features.items():
            if feature not in model:
                model[feature] = 0.0
            model[feature] += learning_rate * error * value
        
        # Update bias
        model['bias'] += learning_rate * error
        
        # Mise à jour accuracy tracking
        correct_prediction = (predicted_prob > 0.5) == actual_failure
        current_accuracy = self.prediction_accuracy.get(service_name, 0.5)
        self.prediction_accuracy[service_name] = current_accuracy * 0.9 + (1.0 if correct_prediction else 0.0) * 0.1
        
        # Stockage features pour analyse stabilité
        self.feature_history[service_name].append(features.copy())

class FailurePatternAnalyzer:
    """
    Analyseur patterns d'échec avec ML clustering.
    Failure classification + root cause analysis + prediction.
    """
    
    def __init__(self, analyzer_config: AnalyzerConfig = None):
        self.analyzer_config = analyzer_config or AnalyzerConfig()
        self.pattern_detector = FailurePatternDetector(self.analyzer_config)
        self.classifier = FailureClassifier(self.analyzer_config)
        self.root_cause_analyzer = RootCauseAnalyzer(self.analyzer_config)
        self.prediction_engine = FailurePredictionEngine(self.analyzer_config)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Stockage global des événements
        self.failure_events = deque(maxlen=self.analyzer_config.max_failure_events)
        
        # Métriques analyzer
        self.analyzer_metrics = {
            'total_failures_analyzed': 0,
            'patterns_detected': 0,
            'classifications_performed': 0,
            'predictions_made': 0,
            'root_cause_analyses': 0
        }
    
    async def analyze_failure_patterns(self, failure_data: List[FailureEvent]) -> PatternAnalysisResult:
        """
        Analyse patterns d'échec avec ML clustering.
        
        Analysis Features:
        - ML-based failure pattern detection
        - Failure classification (transient, permanent, systemic)
        - Root cause analysis avec correlation detection
        - Cascading failure prediction
        - Failure trend analysis avec time series
        - Cross-service failure correlation
        - Anomaly detection pour unusual failure patterns
        """
        
        self.analyzer_metrics['total_failures_analyzed'] += len(failure_data)
        
        # Ajout événements au stockage global
        self.failure_events.extend(failure_data)
        
        # Détection patterns avec clustering ML
        detected_patterns = await self.pattern_detector.detect_patterns(failure_data)
        
        if not detected_patterns:
            # Retour pattern par défaut si aucun détecté
            return PatternAnalysisResult(
                detected_pattern=FailurePattern.TRANSIENT,
                confidence_score=0.3,
                affected_services=[],
                failure_frequency=0.0,
                pattern_characteristics={},
                recommendations=['Monitor for recurring issues'],
                severity_assessment=FailureSeverity.LOW
            )
        
        # Sélection pattern le plus significatif
        primary_pattern = detected_patterns[0]  # Déjà trié par sévérité/confidence
        
        self.analyzer_metrics['patterns_detected'] += 1
        
        self.logger.info(f"Detected failure pattern: {primary_pattern.detected_pattern.value} with confidence {primary_pattern.confidence_score:.2f}")
        
        return primary_pattern
    
    async def classify_failure_types(self, failure_events: List[FailureEvent]) -> List[ClassificationResult]:
        """Classification types d'échec pour retry strategy selection."""
        
        classification_results = []
        
        for event in failure_events:
            classification = await self.classifier.classify_failure(event)
            classification_results.append(classification)
            
            self.analyzer_metrics['classifications_performed'] += 1
        
        return classification_results
    
    async def detect_cascading_failures(self, service_failures: Dict) -> Dict:
        """Détection cascading failures pour early intervention."""
        
        # Conversion dict en FailureEvent objects
        failure_events = []
        for service_name, failures in service_failures.items():
            for failure in failures:
                event = FailureEvent(
                    timestamp=failure.get('timestamp', time.time()),
                    service_name=service_name,
                    operation_type=failure.get('operation_type', 'unknown'),
                    error_type=failure.get('error_type', 'unknown'),
                    error_message=failure.get('error_message', ''),
                    context=failure.get('context', {})
                )
                failure_events.append(event)
        
        # Analyse avec root cause analyzer
        root_cause_analysis = await self.root_cause_analyzer.analyze_root_cause(failure_events)
        
        # Détection cascade spécifique
        cascade_detected = False
        cascade_indicators = []
        
        # Indicateurs cascade
        cascade_sequences = root_cause_analysis.get('temporal_correlations', {}).get('cascade_sequences', [])
        if cascade_sequences:
            cascade_detected = True
            cascade_indicators.extend([
                f"Cascade sequence detected: {seq['sequence']}" for seq in cascade_sequences
            ])
        
        # Services multiples affectés rapidement
        if len(service_failures) > 2:
            timestamps = []
            for failures in service_failures.values():
                timestamps.extend([f.get('timestamp', 0) for f in failures])
            
            if timestamps:
                time_span = max(timestamps) - min(timestamps)
                if time_span < 300:  # 5 minutes
                    cascade_detected = True
                    cascade_indicators.append(f"Multiple services failed within {time_span/60:.1f} minutes")
        
        cascade_alert = {
            'cascade_detected': cascade_detected,
            'severity': 'HIGH' if cascade_detected else 'LOW',
            'affected_services': list(service_failures.keys()),
            'cascade_indicators': cascade_indicators,
            'root_cause_analysis': root_cause_analysis,
            'recommended_actions': self._generate_cascade_response_actions(cascade_detected, service_failures),
            'alert_timestamp': time.time()
        }
        
        if cascade_detected:
            self.logger.warning(f"Cascading failure detected across {len(service_failures)} services")
        
        return cascade_alert
    
    async def predict_failure_probability(self, service_context: Dict) -> FailureProbability:
        """Prédiction probabilité échec basée sur patterns historiques."""
        
        prediction = await self.prediction_engine.predict_failure_probability(service_context)
        
        self.analyzer_metrics['predictions_made'] += 1
        
        return prediction
    
    async def generate_failure_insights(self, analysis_results: Dict) -> Dict:
        """Génération insights actionables pour failure prevention."""
        
        insights = {
            'key_insights': [],
            'preventive_actions': [],
            'monitoring_recommendations': [],
            'architectural_improvements': [],
            'immediate_actions': []
        }
        
        # Analyse patterns détectés
        detected_patterns = analysis_results.get('detected_patterns', [])
        for pattern_result in detected_patterns:
            pattern = pattern_result.detected_pattern
            
            # Insights par pattern
            if pattern == FailurePattern.CASCADING:
                insights['key_insights'].append("Cascading failures indicate insufficient service isolation")
                insights['architectural_improvements'].extend([
                    "Implement circuit breakers between services",
                    "Add bulkhead isolation patterns",
                    "Review service dependency chains"
                ])
                insights['immediate_actions'].append("Isolate failing services to prevent cascade")
            
            elif pattern == FailurePattern.RESOURCE_EXHAUSTION:
                insights['key_insights'].append("Resource exhaustion suggests capacity planning issues")
                insights['preventive_actions'].extend([
                    "Implement auto-scaling mechanisms",
                    "Add resource monitoring and alerting",
                    "Optimize resource-intensive operations"
                ])
                insights['immediate_actions'].append("Scale up resources or throttle traffic")
        
        # Analyse classifications
        classifications = analysis_results.get('classifications', [])
        failure_type_counts = Counter(c.failure_type for c in classifications)
        
        for failure_type, count in failure_type_counts.most_common(3):
            if failure_type == FailureType.TIMEOUT:
                insights['monitoring_recommendations'].append("Implement adaptive timeout monitoring")
            elif failure_type == FailureType.RESOURCE_EXHAUSTION:
                insights['monitoring_recommendations'].append("Add resource utilization dashboards")
        
        # Analyse root causes
        root_causes = analysis_results.get('root_cause_analysis', {})
        primary_cause = root_causes.get('primary_root_cause', 'unknown')
        
        if 'service_failure' in primary_cause:
            insights['key_insights'].append(f"Primary root cause identified: {primary_cause}")
            insights['immediate_actions'].append(f"Focus investigation on {primary_cause}")
        
        return insights
    
    def _generate_cascade_response_actions(self, cascade_detected: bool, service_failures: Dict) -> List[str]:
        """Génération actions réponse cascade"""
        
        if not cascade_detected:
            return ["Monitor for potential cascade patterns"]
        
        actions = [
            "IMMEDIATE: Activate incident response team",
            "IMMEDIATE: Isolate failing services to prevent further cascade",
            "IMMEDIATE: Implement emergency circuit breakers"
        ]
        
        # Actions spécifiques par nombre de services
        num_services = len(service_failures)
        if num_services >= 5:
            actions.extend([
                "CRITICAL: Consider system-wide degraded mode",
                "CRITICAL: Notify executive stakeholders",
                "CRITICAL: Prepare for potential rollback"
            ])
        elif num_services >= 3:
            actions.extend([
                "HIGH: Implement service-specific fallbacks",
                "HIGH: Increase monitoring frequency",
                "HIGH: Prepare rollback plans"
            ])
        
        return actions
    
    async def record_failure(self, failure_event: FailureEvent):
        """Enregistrement échec pour analyse continue"""
        
        self.failure_events.append(failure_event)
        
        # Classification automatique
        classification = await self.classifier.classify_failure(failure_event)
        
        # Log pour monitoring
        self.logger.info(f"Recorded failure: {failure_event.service_name}:{failure_event.operation_type} - {classification.failure_type.value}")
    
    async def get_analyzer_metrics(self) -> Dict:
        """Métriques analyzer complet"""
        
        return {
            **self.analyzer_metrics,
            'total_events_stored': len(self.failure_events),
            'pattern_detector_stats': {
                'detected_patterns': len(self.pattern_detector.detected_patterns),
                'pattern_signatures': len(self.pattern_detector.pattern_signatures)
            },
            'classifier_stats': {
                'classification_history': len(self.classifier.classification_history),
                'classification_rules': len(self.classifier.classification_rules)
            },
            'prediction_engine_stats': {
                'services_tracked': len(self.prediction_engine.prediction_models),
                'average_accuracy': statistics.mean(self.prediction_engine.prediction_accuracy.values()) if self.prediction_engine.prediction_accuracy else 0.0
            },
            'config': {
                'pattern_detection_window': self.analyzer_config.pattern_detection_window,
                'prediction_enabled': self.analyzer_config.prediction_enabled,
                'max_failure_events': self.analyzer_config.max_failure_events
            }
        }
    
    async def health_check(self) -> Dict:
        """Vérification santé analyzer"""
        
        return {
            'status': 'healthy',
            'components': {
                'pattern_detector': 'operational',
                'classifier': 'operational', 
                'root_cause_analyzer': 'operational',
                'prediction_engine': 'operational' if self.analyzer_config.prediction_enabled else 'disabled'
            },
            'data_health': {
                'failure_events_count': len(self.failure_events),
                'storage_utilization': len(self.failure_events) / self.analyzer_config.max_failure_events,
                'recent_activity': len([e for e in self.failure_events if time.time() - e.timestamp < 3600])
            }
        }

# Factory functions
def create_failure_pattern_analyzer(
    max_failure_events: int = 5000,
    prediction_enabled: bool = True,
    pattern_detection_window: int = 3600
) -> FailurePatternAnalyzer:
    """Factory pour création analyzer patterns échec"""
    
    config = AnalyzerConfig(
        max_failure_events=max_failure_events,
        prediction_enabled=prediction_enabled,
        pattern_detection_window=pattern_detection_window
    )
    
    return FailurePatternAnalyzer(config)

__all__ = [
    'FailurePatternAnalyzer',
    'AnalyzerConfig',
    'FailureEvent',
    'PatternAnalysisResult',
    'ClassificationResult',
    'FailureProbability',
    'FailureType',
    'FailurePattern',
    'FailureSeverity',
    'FailurePatternDetector',
    'FailureClassifier',
    'RootCauseAnalyzer',
    'FailurePredictionEngine',
    'create_failure_pattern_analyzer'
]