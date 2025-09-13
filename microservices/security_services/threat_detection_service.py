"""
🕵️ THREAT DETECTION SERVICE
Détection de menaces en temps réel pour Ainflue

Fonctionnalités:
- Détection d'anomalies basée sur l'IA
- Analyse comportementale en temps réel
- Protection contre les attaques DDoS, brute force
- Corrélation d'événements de sécurité
- Réponse automatisée aux incidents

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set
import time
import json
import hashlib
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import re

logger = logging.getLogger(__name__)

class ThreatType(Enum):
    """Types de menaces"""
    BRUTE_FORCE = "brute_force"
    DDOS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    MALWARE = "malware"
    PHISHING = "phishing"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    CREDENTIAL_STUFFING = "credential_stuffing"
    API_ABUSE = "api_abuse"
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_THREAT = "insider_threat"

class ThreatSeverity(Enum):
    """Niveaux de sévérité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ResponseAction(Enum):
    """Actions de réponse automatique"""
    LOG_ONLY = "log_only"
    ALERT = "alert"
    BLOCK_IP = "block_ip"
    RATE_LIMIT = "rate_limit"
    QUARANTINE_USER = "quarantine_user"
    DISABLE_ACCOUNT = "disable_account"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"

@dataclass
class ThreatEvent:
    """Événement de menace détecté"""
    event_id: str
    threat_type: ThreatType
    severity: ThreatSeverity
    source_ip: str
    target_resource: str
    user_id: Optional[str]
    timestamp: float
    description: str
    indicators: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    raw_data: Dict[str, Any] = field(default_factory=dict)
    response_actions: List[ResponseAction] = field(default_factory=list)
    resolved: bool = False
    false_positive: bool = False

@dataclass
class ThreatPattern:
    """Pattern de menace pour détection"""
    pattern_id: str
    name: str
    threat_type: ThreatType
    severity: ThreatSeverity
    indicators: List[str]
    regex_patterns: List[str] = field(default_factory=list)
    ip_ranges: List[str] = field(default_factory=list)
    threshold_count: int = 5
    time_window_seconds: int = 300
    confidence_threshold: float = 0.7

@dataclass
class UserBehaviorProfile:
    """Profil comportemental utilisateur"""
    user_id: str
    normal_ips: Set[str] = field(default_factory=set)
    normal_locations: Set[str] = field(default_factory=set)
    typical_login_times: List[int] = field(default_factory=list)  # Heures de la journée
    average_session_duration: float = 0.0
    common_endpoints: Set[str] = field(default_factory=set)
    device_fingerprints: Set[str] = field(default_factory=set)
    last_updated: float = 0.0

class ThreatDetectionService:
    """
    🕵️ SERVICE DÉTECTION MENACES ENTERPRISE
    
    Détection intelligente des menaces de sécurité avec analyse comportementale,
    corrélation d'événements et réponse automatisée
    """
    
    def __init__(self, service_id: str = None):
        self.service_id = service_id or f"threat-detection-{int(time.time())}"
        self.status = "initializing"
        
        # Événements de menaces
        self.threat_events: List[ThreatEvent] = []
        self.active_threats: Dict[str, ThreatEvent] = {}
        
        # Patterns de détection
        self.threat_patterns: Dict[str, ThreatPattern] = {}
        
        # Profils comportementaux
        self.user_profiles: Dict[str, UserBehaviorProfile] = {}
        
        # Listes de réputation
        self.malicious_ips: Set[str] = set()
        self.suspicious_domains: Set[str] = set()
        self.known_attack_signatures: Set[str] = set()
        
        # Configuration de détection
        self.detection_config = {
            "enable_ml_detection": True,
            "enable_behavior_analysis": True,
            "enable_ip_reputation": True,
            "enable_geo_blocking": True,
            "auto_response_enabled": True,
            "correlation_window_seconds": 300,
            "max_events_per_minute": 1000
        }
        
        # Métriques
        self.detection_metrics = {
            "total_events_analyzed": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "blocked_attacks": 0,
            "response_actions_taken": 0,
            "average_detection_time_ms": 0.0
        }
        
        # Règles de corrélation
        self.correlation_rules = {}
        
    async def initialize(self) -> bool:
        """Initialiser le service de détection de menaces"""
        logger.info("🕵️ Initializing Threat Detection Service...")
        
        try:
            # Charger les patterns de menaces
            await self._load_threat_patterns()
            
            # Charger les listes de réputation
            await self._load_reputation_lists()
            
            # Initialiser les règles de corrélation
            await self._setup_correlation_rules()
            
            # Charger les profils comportementaux
            await self._load_user_profiles()
            
            self.status = "ready"
            logger.info("✅ Threat Detection Service initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Threat Detection Service: {e}")
            self.status = "error"
            return False
    
    async def _load_threat_patterns(self) -> None:
        """Charger les patterns de détection de menaces"""
        patterns = [
            ThreatPattern(
                pattern_id="brute_force_login",
                name="Brute Force Login Attack",
                threat_type=ThreatType.BRUTE_FORCE,
                severity=ThreatSeverity.HIGH,
                indicators=["failed_login", "multiple_attempts", "short_intervals"],
                regex_patterns=[r"login.*failed", r"authentication.*error"],
                threshold_count=10,
                time_window_seconds=300
            ),
            ThreatPattern(
                pattern_id="sql_injection_attempt",
                name="SQL Injection Attack",
                threat_type=ThreatType.SQL_INJECTION,
                severity=ThreatSeverity.CRITICAL,
                indicators=["sql_keywords", "special_characters", "union_select"],
                regex_patterns=[
                    r"(\bUNION\b.*\bSELECT\b)",
                    r"(\bDROP\b.*\bTABLE\b)",
                    r"(\bINSERT\b.*\bINTO\b)",
                    r"('.*OR.*'.*')"
                ],
                threshold_count=1,
                time_window_seconds=60
            ),
            ThreatPattern(
                pattern_id="xss_attempt",
                name="Cross-Site Scripting Attack",
                threat_type=ThreatType.XSS,
                severity=ThreatSeverity.HIGH,
                indicators=["script_tags", "javascript", "encoded_payload"],
                regex_patterns=[
                    r"<script[^>]*>.*</script>",
                    r"javascript:",
                    r"on\w+\s*=",
                    r"eval\s*\("
                ],
                threshold_count=1,
                time_window_seconds=60
            ),
            ThreatPattern(
                pattern_id="ddos_detection",
                name="DDoS Attack Detection",
                threat_type=ThreatType.DDOS,
                severity=ThreatSeverity.CRITICAL,
                indicators=["high_request_rate", "multiple_sources", "resource_exhaustion"],
                threshold_count=1000,
                time_window_seconds=60
            ),
            ThreatPattern(
                pattern_id="api_abuse",
                name="API Abuse Detection",
                threat_type=ThreatType.API_ABUSE,
                severity=ThreatSeverity.MEDIUM,
                indicators=["high_api_calls", "unusual_patterns", "rate_limit_exceeded"],
                threshold_count=500,
                time_window_seconds=300
            ),
            ThreatPattern(
                pattern_id="credential_stuffing",
                name="Credential Stuffing Attack",
                threat_type=ThreatType.CREDENTIAL_STUFFING,
                severity=ThreatSeverity.HIGH,
                indicators=["multiple_accounts", "common_passwords", "automated_behavior"],
                threshold_count=50,
                time_window_seconds=600
            )
        ]
        
        for pattern in patterns:
            self.threat_patterns[pattern.pattern_id] = pattern
        
        logger.info(f"📋 Loaded {len(patterns)} threat patterns")
    
    async def _load_reputation_lists(self) -> None:
        """Charger les listes de réputation IP et domaines"""
        # En production, charger depuis des sources de threat intelligence
        self.malicious_ips = {
            "192.0.2.1",    # Exemple RFC5737
            "198.51.100.1", # Exemple RFC5737
            "203.0.113.1",  # Exemple RFC5737
            "185.220.101.1", # Tor exit node exemple
            "45.133.1.1"    # Malware C&C exemple
        }
        
        self.suspicious_domains = {
            "malicious-site.example",
            "phishing-domain.example", 
            "c2-server.example",
            "fake-bank.example"
        }
        
        self.known_attack_signatures = {
            "nikto_scan",
            "sqlmap_injection",
            "metasploit_payload",
            "burp_suite_scan"
        }
        
        logger.info(f"🛡️ Loaded reputation lists: {len(self.malicious_ips)} IPs, {len(self.suspicious_domains)} domains")
    
    async def _setup_correlation_rules(self) -> None:
        """Configurer les règles de corrélation d'événements"""
        self.correlation_rules = {
            "coordinated_attack": {
                "description": "Multiple threat types from same source",
                "conditions": [
                    {"threat_types": [ThreatType.BRUTE_FORCE, ThreatType.SQL_INJECTION], "time_window": 600},
                    {"threat_types": [ThreatType.XSS, ThreatType.CSRF], "time_window": 300}
                ],
                "severity_escalation": ThreatSeverity.CRITICAL,
                "auto_response": [ResponseAction.BLOCK_IP, ResponseAction.ALERT]
            },
            "insider_threat_pattern": {
                "description": "Unusual access patterns indicating insider threat",
                "conditions": [
                    {"indicators": ["off_hours_access", "unusual_data_access", "privilege_escalation"], "time_window": 3600}
                ],
                "severity_escalation": ThreatSeverity.HIGH,
                "auto_response": [ResponseAction.ALERT, ResponseAction.QUARANTINE_USER]
            }
        }
    
    async def _load_user_profiles(self) -> None:
        """Charger les profils comportementaux des utilisateurs"""
        # En production, charger depuis la base de données
        # Pour la démo, créer quelques profils exemple
        self.user_profiles = {
            "user_123": UserBehaviorProfile(
                user_id="user_123",
                normal_ips={"192.168.1.100", "10.0.0.50"},
                normal_locations={"US-CA", "US-NY"},
                typical_login_times=[9, 10, 14, 15, 16],
                average_session_duration=3600.0,
                common_endpoints={"/api/v1/creators", "/api/v1/content", "/dashboard"},
                device_fingerprints={"device_123", "device_456"}
            )
        }
    
    async def analyze_event(
        self,
        event_data: Dict[str, Any],
        source_ip: str,
        user_id: Optional[str] = None,
        request_path: str = "",
        user_agent: str = "",
        additional_context: Dict[str, Any] = None
    ) -> Optional[ThreatEvent]:
        """
        Analyser un événement pour détecter des menaces
        
        Args:
            event_data: Données de l'événement à analyser
            source_ip: Adresse IP source
            user_id: ID utilisateur (si authentifié)
            request_path: Chemin de la requête
            user_agent: User-Agent du client
            additional_context: Contexte supplémentaire
        """
        start_time = time.time()
        self.detection_metrics["total_events_analyzed"] += 1
        
        try:
            # Vérification IP de réputation
            if await self._check_ip_reputation(source_ip):
                threat = await self._create_threat_event(
                    ThreatType.MALWARE,
                    ThreatSeverity.HIGH,
                    source_ip,
                    request_path,
                    user_id,
                    "Malicious IP detected from threat intelligence",
                    ["malicious_ip", "threat_intelligence"],
                    confidence_score=0.95
                )
                await self._process_threat_event(threat)
                return threat
            
            # Détection par patterns
            for pattern_id, pattern in self.threat_patterns.items():
                if await self._match_pattern(event_data, pattern, source_ip, request_path, user_agent):
                    confidence = await self._calculate_confidence(event_data, pattern)
                    
                    if confidence >= pattern.confidence_threshold:
                        threat = await self._create_threat_event(
                            pattern.threat_type,
                            pattern.severity,
                            source_ip,
                            request_path,
                            user_id,
                            f"Pattern match: {pattern.name}",
                            pattern.indicators,
                            confidence_score=confidence
                        )
                        await self._process_threat_event(threat)
                        return threat
            
            # Analyse comportementale (si utilisateur authentifié)
            if user_id and self.detection_config["enable_behavior_analysis"]:
                behavioral_threat = await self._analyze_user_behavior(
                    user_id, source_ip, request_path, event_data
                )
                if behavioral_threat:
                    await self._process_threat_event(behavioral_threat)
                    return behavioral_threat
            
            # Corrélation d'événements
            correlated_threat = await self._correlate_events(source_ip, user_id)
            if correlated_threat:
                await self._process_threat_event(correlated_threat)
                return correlated_threat
            
            # Calculer le temps de détection
            detection_time = (time.time() - start_time) * 1000
            self.detection_metrics["average_detection_time_ms"] = (
                (self.detection_metrics["average_detection_time_ms"] + detection_time) / 2
            )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error analyzing event: {e}")
            return None
    
    async def _check_ip_reputation(self, ip_address: str) -> bool:
        """Vérifier la réputation d'une IP"""
        try:
            # Vérification dans les listes locales
            if ip_address in self.malicious_ips:
                return True
            
            # Vérification des ranges malveillants
            ip = ipaddress.ip_address(ip_address)
            malicious_ranges = [
                "192.0.2.0/24",    # RFC5737 example
                "198.51.100.0/24", # RFC5737 example
                "203.0.113.0/24"   # RFC5737 example
            ]
            
            for range_str in malicious_ranges:
                network = ipaddress.ip_network(range_str, strict=False)
                if ip in network:
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"IP reputation check failed: {e}")
            return False
    
    async def _match_pattern(
        self,
        event_data: Dict[str, Any],
        pattern: ThreatPattern,
        source_ip: str,
        request_path: str,
        user_agent: str
    ) -> bool:
        """Vérifier si un événement correspond à un pattern"""
        
        # Vérification des regex patterns
        for regex_pattern in pattern.regex_patterns:
            try:
                # Vérifier dans les données de l'événement
                event_string = json.dumps(event_data).lower()
                if re.search(regex_pattern, event_string, re.IGNORECASE):
                    return True
                
                # Vérifier dans le chemin de requête
                if re.search(regex_pattern, request_path, re.IGNORECASE):
                    return True
                
                # Vérifier dans le user agent
                if re.search(regex_pattern, user_agent, re.IGNORECASE):
                    return True
                    
            except re.error as e:
                logger.warning(f"Invalid regex pattern {regex_pattern}: {e}")
        
        # Vérification des seuils de comptage (pour DDoS, brute force, etc.)
        if pattern.threat_type in [ThreatType.DDOS, ThreatType.BRUTE_FORCE, ThreatType.API_ABUSE]:
            count = await self._count_recent_events(
                source_ip,
                pattern.threat_type,
                pattern.time_window_seconds
            )
            return count >= pattern.threshold_count
        
        return False
    
    async def _calculate_confidence(self, event_data: Dict[str, Any], pattern: ThreatPattern) -> float:
        """Calculer le score de confiance pour une détection"""
        confidence = 0.0
        max_indicators = len(pattern.indicators)
        
        if max_indicators == 0:
            return 0.5  # Confiance par défaut
        
        # Compter les indicateurs présents
        indicators_found = 0
        event_string = json.dumps(event_data).lower()
        
        for indicator in pattern.indicators:
            if indicator.lower() in event_string:
                indicators_found += 1
        
        # Calculer la confiance basée sur les indicateurs
        confidence = indicators_found / max_indicators
        
        # Ajustements basés sur la sévérité
        if pattern.severity == ThreatSeverity.CRITICAL:
            confidence *= 1.2
        elif pattern.severity == ThreatSeverity.HIGH:
            confidence *= 1.1
        
        # Limiter à 1.0
        return min(confidence, 1.0)
    
    async def _count_recent_events(
        self,
        source_ip: str,
        threat_type: ThreatType,
        time_window_seconds: int
    ) -> int:
        """Compter les événements récents pour un IP et type de menace"""
        current_time = time.time()
        cutoff_time = current_time - time_window_seconds
        
        count = 0
        for event in self.threat_events:
            if (event.source_ip == source_ip and
                event.threat_type == threat_type and
                event.timestamp >= cutoff_time):
                count += 1
        
        return count
    
    async def _analyze_user_behavior(
        self,
        user_id: str,
        source_ip: str,
        request_path: str,
        event_data: Dict[str, Any]
    ) -> Optional[ThreatEvent]:
        """Analyser le comportement utilisateur pour détecter des anomalies"""
        
        profile = self.user_profiles.get(user_id)
        if not profile:
            # Créer un nouveau profil
            profile = UserBehaviorProfile(user_id=user_id)
            self.user_profiles[user_id] = profile
            return None  # Pas assez de données pour analyser
        
        anomalies = []
        
        # Vérifier l'IP source
        if source_ip not in profile.normal_ips:
            anomalies.append("unusual_ip")
        
        # Vérifier l'heure de connexion
        current_hour = int(time.localtime().tm_hour)
        if current_hour not in profile.typical_login_times:
            anomalies.append("unusual_time")
        
        # Vérifier les endpoints accédés
        if request_path not in profile.common_endpoints:
            anomalies.append("unusual_endpoint")
        
        # Si plusieurs anomalies, considérer comme menace
        if len(anomalies) >= 2:
            return await self._create_threat_event(
                ThreatType.ANOMALOUS_BEHAVIOR,
                ThreatSeverity.MEDIUM,
                source_ip,
                request_path,
                user_id,
                f"Anomalous user behavior detected: {', '.join(anomalies)}",
                anomalies,
                confidence_score=0.7
            )
        
        return None
    
    async def _correlate_events(
        self,
        source_ip: str,
        user_id: Optional[str]
    ) -> Optional[ThreatEvent]:
        """Corréler les événements pour détecter des attaques coordonnées"""
        
        # Vérifier les règles de corrélation
        for rule_name, rule_config in self.correlation_rules.items():
            if await self._match_correlation_rule(source_ip, user_id, rule_config):
                return await self._create_threat_event(
                    ThreatType.ANOMALOUS_BEHAVIOR,
                    rule_config["severity_escalation"],
                    source_ip,
                    "multiple_endpoints",
                    user_id,
                    f"Correlated attack pattern detected: {rule_name}",
                    ["correlation", "coordinated_attack"],
                    confidence_score=0.85
                )
        
        return None
    
    async def _match_correlation_rule(
        self,
        source_ip: str,
        user_id: Optional[str],
        rule_config: Dict[str, Any]
    ) -> bool:
        """Vérifier si une règle de corrélation est satisfaite"""
        current_time = time.time()
        
        for condition in rule_config["conditions"]:
            time_window = condition.get("time_window", 300)
            cutoff_time = current_time - time_window
            
            # Vérifier les types de menaces
            if "threat_types" in condition:
                threat_types_found = set()
                for event in self.threat_events:
                    if (event.source_ip == source_ip and
                        event.timestamp >= cutoff_time):
                        threat_types_found.add(event.threat_type)
                
                required_types = set(condition["threat_types"])
                if required_types.issubset(threat_types_found):
                    return True
        
        return False
    
    async def _create_threat_event(
        self,
        threat_type: ThreatType,
        severity: ThreatSeverity,
        source_ip: str,
        target_resource: str,
        user_id: Optional[str],
        description: str,
        indicators: List[str],
        confidence_score: float = 0.8
    ) -> ThreatEvent:
        """Créer un événement de menace"""
        event_id = hashlib.sha256(
            f"{threat_type.value}_{source_ip}_{target_resource}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        # Déterminer les actions de réponse
        response_actions = await self._determine_response_actions(threat_type, severity)
        
        threat_event = ThreatEvent(
            event_id=event_id,
            threat_type=threat_type,
            severity=severity,
            source_ip=source_ip,
            target_resource=target_resource,
            user_id=user_id,
            timestamp=time.time(),
            description=description,
            indicators=indicators,
            confidence_score=confidence_score,
            response_actions=response_actions
        )
        
        return threat_event
    
    async def _determine_response_actions(
        self,
        threat_type: ThreatType,
        severity: ThreatSeverity
    ) -> List[ResponseAction]:
        """Déterminer les actions de réponse appropriées"""
        actions = [ResponseAction.LOG_ONLY, ResponseAction.ALERT]
        
        # Actions basées sur la sévérité
        if severity == ThreatSeverity.CRITICAL:
            actions.extend([ResponseAction.BLOCK_IP, ResponseAction.EMERGENCY_SHUTDOWN])
        elif severity == ThreatSeverity.HIGH:
            actions.append(ResponseAction.BLOCK_IP)
        elif severity == ThreatSeverity.MEDIUM:
            actions.append(ResponseAction.RATE_LIMIT)
        
        # Actions basées sur le type de menace
        if threat_type in [ThreatType.BRUTE_FORCE, ThreatType.CREDENTIAL_STUFFING]:
            actions.append(ResponseAction.QUARANTINE_USER)
        elif threat_type == ThreatType.DDOS:
            actions.extend([ResponseAction.RATE_LIMIT, ResponseAction.BLOCK_IP])
        elif threat_type == ThreatType.INSIDER_THREAT:
            actions.extend([ResponseAction.QUARANTINE_USER, ResponseAction.DISABLE_ACCOUNT])
        
        return list(set(actions))  # Supprimer les doublons
    
    async def _process_threat_event(self, threat_event: ThreatEvent) -> None:
        """Traiter un événement de menace détecté"""
        logger.warning(f"🚨 THREAT DETECTED: {threat_event.threat_type.value} from {threat_event.source_ip}")
        
        # Enregistrer l'événement
        self.threat_events.append(threat_event)
        self.active_threats[threat_event.event_id] = threat_event
        
        # Mettre à jour les métriques
        self.detection_metrics["threats_detected"] += 1
        
        # Exécuter les actions de réponse automatique
        if self.detection_config["auto_response_enabled"]:
            await self._execute_response_actions(threat_event)
        
        # Notifier les équipes de sécurité
        await self._send_security_alert(threat_event)
    
    async def _execute_response_actions(self, threat_event: ThreatEvent) -> None:
        """Exécuter les actions de réponse automatique"""
        for action in threat_event.response_actions:
            try:
                if action == ResponseAction.BLOCK_IP:
                    await self._block_ip(threat_event.source_ip)
                elif action == ResponseAction.RATE_LIMIT:
                    await self._apply_rate_limit(threat_event.source_ip)
                elif action == ResponseAction.QUARANTINE_USER:
                    if threat_event.user_id:
                        await self._quarantine_user(threat_event.user_id)
                elif action == ResponseAction.DISABLE_ACCOUNT:
                    if threat_event.user_id:
                        await self._disable_account(threat_event.user_id)
                elif action == ResponseAction.EMERGENCY_SHUTDOWN:
                    await self._emergency_shutdown(threat_event.target_resource)
                
                self.detection_metrics["response_actions_taken"] += 1
                
            except Exception as e:
                logger.error(f"Failed to execute response action {action.value}: {e}")
    
    async def _block_ip(self, ip_address: str) -> None:
        """Bloquer une adresse IP"""
        self.malicious_ips.add(ip_address)
        logger.info(f"🚫 Blocked IP: {ip_address}")
        self.detection_metrics["blocked_attacks"] += 1
    
    async def _apply_rate_limit(self, ip_address: str) -> None:
        """Appliquer une limitation de taux"""
        logger.info(f"⏱️ Applied rate limit to IP: {ip_address}")
    
    async def _quarantine_user(self, user_id: str) -> None:
        """Mettre un utilisateur en quarantaine"""
        logger.info(f"🔒 Quarantined user: {user_id}")
    
    async def _disable_account(self, user_id: str) -> None:
        """Désactiver un compte utilisateur"""
        logger.info(f"🔐 Disabled account: {user_id}")
    
    async def _emergency_shutdown(self, resource: str) -> None:
        """Arrêt d'urgence d'une ressource"""
        logger.critical(f"🚨 EMERGENCY SHUTDOWN: {resource}")
    
    async def _send_security_alert(self, threat_event: ThreatEvent) -> None:
        """Envoyer une alerte de sécurité"""
        alert_data = {
            "event_id": threat_event.event_id,
            "threat_type": threat_event.threat_type.value,
            "severity": threat_event.severity.value,
            "source_ip": threat_event.source_ip,
            "description": threat_event.description,
            "confidence": threat_event.confidence_score,
            "timestamp": threat_event.timestamp
        }
        
        # En production, envoyer via système d'alertes (email, Slack, PagerDuty)
        logger.info(f"📧 Security alert sent: {alert_data}")
    
    async def mark_false_positive(self, event_id: str) -> bool:
        """Marquer un événement comme faux positif"""
        if event_id in self.active_threats:
            self.active_threats[event_id].false_positive = True
            self.detection_metrics["false_positives"] += 1
            logger.info(f"✅ Marked event {event_id} as false positive")
            return True
        return False
    
    async def resolve_threat(self, event_id: str) -> bool:
        """Résoudre une menace"""
        if event_id in self.active_threats:
            self.active_threats[event_id].resolved = True
            del self.active_threats[event_id]
            logger.info(f"✅ Resolved threat {event_id}")
            return True
        return False
    
    def get_threat_summary(self, time_window: str = "24h") -> Dict[str, Any]:
        """Obtenir un résumé des menaces"""
        if time_window == "24h":
            cutoff_time = time.time() - 86400
        elif time_window == "1h":
            cutoff_time = time.time() - 3600
        else:
            cutoff_time = time.time() - 86400
        
        recent_threats = [
            event for event in self.threat_events
            if event.timestamp >= cutoff_time
        ]
        
        # Grouper par type de menace
        threats_by_type = {}
        for threat in recent_threats:
            threat_type = threat.threat_type.value
            if threat_type not in threats_by_type:
                threats_by_type[threat_type] = 0
            threats_by_type[threat_type] += 1
        
        # Grouper par sévérité
        threats_by_severity = {}
        for threat in recent_threats:
            severity = threat.severity.value
            if severity not in threats_by_severity:
                threats_by_severity[severity] = 0
            threats_by_severity[severity] += 1
        
        return {
            "time_window": time_window,
            "total_threats": len(recent_threats),
            "active_threats": len(self.active_threats),
            "threats_by_type": threats_by_type,
            "threats_by_severity": threats_by_severity,
            "false_positive_rate": round(
                (self.detection_metrics["false_positives"] / max(1, self.detection_metrics["threats_detected"])) * 100, 2
            ),
            "top_threat_sources": self._get_top_threat_sources(recent_threats),
            "metrics": self.detection_metrics
        }
    
    def _get_top_threat_sources(self, threats: List[ThreatEvent], limit: int = 10) -> List[Dict[str, Any]]:
        """Obtenir les principales sources de menaces"""
        ip_counts = {}
        for threat in threats:
            ip = threat.source_ip
            if ip not in ip_counts:
                ip_counts[ip] = {"count": 0, "threat_types": set()}
            ip_counts[ip]["count"] += 1
            ip_counts[ip]["threat_types"].add(threat.threat_type.value)
        
        # Trier par count
        sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1]["count"], reverse=True)
        
        return [
            {
                "ip": ip,
                "threat_count": data["count"],
                "threat_types": list(data["threat_types"])
            }
            for ip, data in sorted_ips[:limit]
        ]
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtenir le statut du service"""
        return {
            "service_id": self.service_id,
            "status": self.status,
            "threat_patterns_loaded": len(self.threat_patterns),
            "active_threats": len(self.active_threats),
            "user_profiles": len(self.user_profiles),
            "malicious_ips": len(self.malicious_ips),
            "detection_config": self.detection_config,
            "metrics": self.detection_metrics
        }

# Instance globale du service
threat_detection = ThreatDetectionService()

async def main():
    """Test du service de détection de menaces"""
    await threat_detection.initialize()
    
    # Test de détection SQL injection
    sql_injection_event = {
        "request_path": "/api/users",
        "query_params": "id=1' OR '1'='1",
        "method": "GET",
        "payload": "SELECT * FROM users WHERE id=1' UNION SELECT * FROM passwords--"
    }
    
    threat = await threat_detection.analyze_event(
        event_data=sql_injection_event,
        source_ip="192.0.2.1",
        user_id="user_123",
        request_path="/api/users",
        user_agent="sqlmap/1.0"
    )
    
    if threat:
        print(f"Threat detected: {threat.threat_type.value} - {threat.description}")
    
    # Test de détection brute force (simulation)
    for i in range(15):  # 15 tentatives rapides
        brute_force_event = {
            "event_type": "login_attempt",
            "status": "failed",
            "username": "admin",
            "attempt_number": i + 1
        }
        
        await threat_detection.analyze_event(
            event_data=brute_force_event,
            source_ip="203.0.113.1",
            request_path="/login",
            user_agent="Python/requests"
        )
    
    # Résumé des menaces
    summary = threat_detection.get_threat_summary("1h")
    print(f"Threat summary: {summary}")

if __name__ == "__main__":
    asyncio.run(main())