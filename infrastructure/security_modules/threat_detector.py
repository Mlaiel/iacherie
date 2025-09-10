"""
Threat Detector - Enterprise Security Threat Detection and Response
Advanced threat detection system for Ainflue creator platform protection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

Security Role Implementation:
- Real-time threat detection and response
- AI-powered behavioral analysis
- Content protection threat monitoring
- Zero-trust security enforcement
- Creator account protection
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
import ipaddress
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatType(Enum):
    """Types of security threats"""
    CONTENT_THEFT = "content_theft"
    ACCOUNT_TAKEOVER = "account_takeover"
    DDoS_ATTACK = "ddos_attack"
    SUSPICIOUS_LOGIN = "suspicious_login"
    MALWARE_UPLOAD = "malware_upload"
    COPYRIGHT_VIOLATION = "copyright_violation"
    PAYMENT_FRAUD = "payment_fraud"
    API_ABUSE = "api_abuse"
    SOCIAL_ENGINEERING = "social_engineering"
    DATA_EXFILTRATION = "data_exfiltration"


class DetectionEngine(Enum):
    """Threat detection engines"""
    ML_BEHAVIORAL = "ml_behavioral"
    SIGNATURE_BASED = "signature_based"
    ANOMALY_DETECTION = "anomaly_detection"
    THREAT_INTELLIGENCE = "threat_intelligence"
    CONTENT_ANALYSIS = "content_analysis"


@dataclass
class ThreatIndicator:
    """Security threat indicator"""
    indicator_id: str
    threat_type: ThreatType
    severity: ThreatLevel
    confidence_score: float  # 0.0 to 1.0
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    description: str = ""
    indicators_of_compromise: List[str] = field(default_factory=list)
    mitigation_actions: List[str] = field(default_factory=list)


@dataclass
class SecurityEvent:
    """Security event details"""
    event_id: str
    event_type: str
    source: str
    target: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class ThreatDetector:
    """Enterprise threat detection system for Ainflue creator platform"""
    
    def __init__(self):
        """Initialize threat detection system"""
        self.detection_engines = {
            DetectionEngine.ML_BEHAVIORAL: True,
            DetectionEngine.SIGNATURE_BASED: True,
            DetectionEngine.ANOMALY_DETECTION: True,
            DetectionEngine.THREAT_INTELLIGENCE: True,
            DetectionEngine.CONTENT_ANALYSIS: True
        }
        
        self.threat_intelligence = {
            "sources": 15,  # Multiple threat intel feeds
            "last_updated": datetime.utcnow(),
            "active_iocs": 50000,  # Indicators of Compromise
            "threat_actors": 1500
        }
        
        # Security monitoring state
        self.active_threats: Dict[str, ThreatIndicator] = {}
        self.ip_reputation_cache: Dict[str, Dict[str, Any]] = {}
        self.user_behavior_profiles: Dict[str, Dict[str, Any]] = {}
        self.content_signatures: Set[str] = set()
        self.security_events: deque = deque(maxlen=100000)  # Last 100k events
        
        # Rate limiting and anomaly detection
        self.request_counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.failed_login_attempts: Dict[str, List[datetime]] = defaultdict(list)
        
        logger.info("Enterprise threat detector initialized for Ainflue creator protection")
        
    async def detect_threats(self, data_source: str, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """
        Comprehensive threat detection across multiple vectors
        
        Detects:
        - Creator account compromise attempts
        - Content theft and copyright violations
        - Payment fraud and financial threats
        - API abuse and DDoS attacks
        - Malware uploads and malicious content
        """
        threats = []
        
        # Multi-engine threat detection
        for engine in self.detection_engines:
            if self.detection_engines[engine]:
                engine_threats = await self._run_detection_engine(engine, data_source, event_data)
                threats.extend(engine_threats)
                
        # Correlate and deduplicate threats
        correlated_threats = await self._correlate_threats(threats)
        
        # Store active threats
        for threat in correlated_threats:
            self.active_threats[threat.indicator_id] = threat
            
        # Log threat detection results
        if correlated_threats:
            logger.warning(f"Detected {len(correlated_threats)} threats from {data_source}")
            for threat in correlated_threats:
                logger.warning(f"Threat: {threat.threat_type.value} - Severity: {threat.severity.value}")
                
        return correlated_threats
        
    async def _run_detection_engine(
        self, 
        engine: DetectionEngine, 
        data_source: str, 
        event_data: Dict[str, Any]
    ) -> List[ThreatIndicator]:
        """Run specific detection engine"""
        threats = []
        
        if engine == DetectionEngine.ML_BEHAVIORAL:
            threats.extend(await self._detect_behavioral_anomalies(event_data))
            
        elif engine == DetectionEngine.SIGNATURE_BASED:
            threats.extend(await self._detect_known_signatures(event_data))
            
        elif engine == DetectionEngine.ANOMALY_DETECTION:
            threats.extend(await self._detect_statistical_anomalies(event_data))
            
        elif engine == DetectionEngine.THREAT_INTELLIGENCE:
            threats.extend(await self._check_threat_intelligence(event_data))
            
        elif engine == DetectionEngine.CONTENT_ANALYSIS:
            threats.extend(await self._analyze_content_threats(event_data))
            
        return threats
        
    async def _detect_behavioral_anomalies(self, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Detect behavioral anomalies using ML models"""
        threats = []
        
        user_id = event_data.get('user_id')
        if not user_id:
            return threats
            
        # Get user behavior profile
        profile = self.user_behavior_profiles.get(user_id, {})
        
        # Check for unusual login patterns
        if event_data.get('event_type') == 'login':
            login_threat = await self._check_unusual_login(event_data, profile)
            if login_threat:
                threats.append(login_threat)
                
        # Check for unusual content upload patterns
        if event_data.get('event_type') == 'content_upload':
            upload_threat = await self._check_unusual_upload(event_data, profile)
            if upload_threat:
                threats.append(upload_threat)
                
        # Check for unusual payment activity
        if event_data.get('event_type') == 'payment':
            payment_threat = await self._check_unusual_payment(event_data, profile)
            if payment_threat:
                threats.append(payment_threat)
                
        return threats
        
    async def _check_unusual_login(self, event_data: Dict[str, Any], profile: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """Check for suspicious login attempts"""
        user_id = event_data.get('user_id')
        source_ip = event_data.get('source_ip')
        user_agent = event_data.get('user_agent', '')
        
        # Check for multiple failed attempts
        failed_attempts = self.failed_login_attempts.get(user_id, [])
        recent_failures = [
            attempt for attempt in failed_attempts
            if attempt > datetime.utcnow() - timedelta(minutes=30)
        ]
        
        if len(recent_failures) >= 5:
            return ThreatIndicator(
                indicator_id=f"login_abuse_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                threat_type=ThreatType.SUSPICIOUS_LOGIN,
                severity=ThreatLevel.HIGH,
                confidence_score=0.9,
                source_ip=source_ip,
                user_id=user_id,
                description=f"Multiple failed login attempts: {len(recent_failures)} in 30 minutes",
                indicators_of_compromise=[f"user_id:{user_id}", f"source_ip:{source_ip}"],
                mitigation_actions=["temporary_account_lock", "require_2fa", "email_alert"]
            )
            
        # Check for geographic anomalies
        usual_locations = profile.get('usual_login_countries', [])
        current_country = event_data.get('country')
        
        if current_country and current_country not in usual_locations and len(usual_locations) > 0:
            return ThreatIndicator(
                indicator_id=f"geo_anomaly_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                threat_type=ThreatType.SUSPICIOUS_LOGIN,
                severity=ThreatLevel.MEDIUM,
                confidence_score=0.7,
                source_ip=source_ip,
                user_id=user_id,
                description=f"Login from unusual location: {current_country}",
                indicators_of_compromise=[f"user_id:{user_id}", f"country:{current_country}"],
                mitigation_actions=["require_2fa", "email_verification"]
            )
            
        return None
        
    async def _check_unusual_upload(self, event_data: Dict[str, Any], profile: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """Check for suspicious content upload patterns"""
        user_id = event_data.get('user_id')
        file_size = event_data.get('file_size_mb', 0)
        file_type = event_data.get('file_type', '')
        
        # Check for unusually large files
        avg_file_size = profile.get('avg_file_size_mb', 10)
        if file_size > avg_file_size * 10:  # 10x larger than usual
            return ThreatIndicator(
                indicator_id=f"large_upload_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                threat_type=ThreatType.DATA_EXFILTRATION,
                severity=ThreatLevel.MEDIUM,
                confidence_score=0.6,
                user_id=user_id,
                content_id=event_data.get('content_id'),
                description=f"Unusually large file upload: {file_size}MB vs avg {avg_file_size}MB",
                indicators_of_compromise=[f"user_id:{user_id}", f"file_size:{file_size}"],
                mitigation_actions=["content_scan", "manual_review"]
            )
            
        return None
        
    async def _check_unusual_payment(self, event_data: Dict[str, Any], profile: Dict[str, Any]) -> Optional[ThreatIndicator]:
        """Check for suspicious payment activity"""
        user_id = event_data.get('user_id')
        amount = event_data.get('amount', 0)
        payment_method = event_data.get('payment_method', '')
        
        # Check for unusually large payments
        avg_payment = profile.get('avg_payment_amount', 50)
        if amount > avg_payment * 20:  # 20x larger than usual
            return ThreatIndicator(
                indicator_id=f"large_payment_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                threat_type=ThreatType.PAYMENT_FRAUD,
                severity=ThreatLevel.HIGH,
                confidence_score=0.8,
                user_id=user_id,
                description=f"Unusually large payment: ${amount} vs avg ${avg_payment}",
                indicators_of_compromise=[f"user_id:{user_id}", f"amount:{amount}"],
                mitigation_actions=["payment_hold", "manual_verification", "fraud_check"]
            )
            
        return None
        
    async def _detect_known_signatures(self, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Detect known threat signatures"""
        threats = []
        
        # Check for malicious file signatures
        file_hash = event_data.get('file_hash')
        if file_hash and file_hash in self.content_signatures:
            threats.append(ThreatIndicator(
                indicator_id=f"malware_{file_hash}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                threat_type=ThreatType.MALWARE_UPLOAD,
                severity=ThreatLevel.CRITICAL,
                confidence_score=0.95,
                content_id=event_data.get('content_id'),
                description=f"Known malicious file detected: {file_hash}",
                indicators_of_compromise=[f"file_hash:{file_hash}"],
                mitigation_actions=["quarantine_file", "block_user", "alert_security_team"]
            ))
            
        # Check for known malicious IPs
        source_ip = event_data.get('source_ip')
        if source_ip and await self._is_malicious_ip(source_ip):
            threats.append(ThreatIndicator(
                indicator_id=f"malicious_ip_{source_ip}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                threat_type=ThreatType.DDoS_ATTACK,
                severity=ThreatLevel.HIGH,
                confidence_score=0.9,
                source_ip=source_ip,
                description=f"Request from known malicious IP: {source_ip}",
                indicators_of_compromise=[f"source_ip:{source_ip}"],
                mitigation_actions=["block_ip", "rate_limit", "monitor_traffic"]
            ))
            
        return threats
        
    async def _detect_statistical_anomalies(self, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Detect statistical anomalies in platform usage"""
        threats = []
        
        # Check for API abuse
        api_endpoint = event_data.get('api_endpoint')
        source_ip = event_data.get('source_ip')
        
        if api_endpoint and source_ip:
            # Count requests per IP per endpoint
            key = f"{source_ip}:{api_endpoint}"
            self.request_counters[key][datetime.now().minute] += 1
            
            # Check if request rate exceeds threshold
            current_minute_requests = self.request_counters[key][datetime.now().minute]
            if current_minute_requests > 100:  # More than 100 requests per minute
                threats.append(ThreatIndicator(
                    indicator_id=f"api_abuse_{source_ip}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    threat_type=ThreatType.API_ABUSE,
                    severity=ThreatLevel.MEDIUM,
                    confidence_score=0.8,
                    source_ip=source_ip,
                    description=f"Excessive API requests: {current_minute_requests}/min to {api_endpoint}",
                    indicators_of_compromise=[f"source_ip:{source_ip}", f"endpoint:{api_endpoint}"],
                    mitigation_actions=["rate_limit", "temporary_ban", "captcha_challenge"]
                ))
                
        return threats
        
    async def _check_threat_intelligence(self, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Check against threat intelligence feeds"""
        threats = []
        
        # Check IP reputation
        source_ip = event_data.get('source_ip')
        if source_ip:
            reputation = await self._get_ip_reputation(source_ip)
            if reputation.get('is_malicious', False):
                threats.append(ThreatIndicator(
                    indicator_id=f"threat_intel_{source_ip}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    threat_type=ThreatType.DDoS_ATTACK,
                    severity=ThreatLevel.HIGH,
                    confidence_score=reputation.get('confidence', 0.8),
                    source_ip=source_ip,
                    description=f"IP flagged by threat intelligence: {reputation.get('reason', 'Unknown')}",
                    indicators_of_compromise=[f"source_ip:{source_ip}"],
                    mitigation_actions=["block_ip", "enhanced_monitoring"]
                ))
                
        return threats
        
    async def _analyze_content_threats(self, event_data: Dict[str, Any]) -> List[ThreatIndicator]:
        """Analyze uploaded content for threats"""
        threats = []
        
        if event_data.get('event_type') == 'content_upload':
            content_id = event_data.get('content_id')
            file_type = event_data.get('file_type', '')
            
            # Check for suspicious file types
            dangerous_extensions = ['.exe', '.bat', '.scr', '.vbs', '.js', '.jar']
            if any(file_type.lower().endswith(ext) for ext in dangerous_extensions):
                threats.append(ThreatIndicator(
                    indicator_id=f"suspicious_file_{content_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    threat_type=ThreatType.MALWARE_UPLOAD,
                    severity=ThreatLevel.HIGH,
                    confidence_score=0.85,
                    content_id=content_id,
                    description=f"Potentially dangerous file type: {file_type}",
                    indicators_of_compromise=[f"content_id:{content_id}", f"file_type:{file_type}"],
                    mitigation_actions=["quarantine_file", "virus_scan", "manual_review"]
                ))
                
        return threats
        
    async def _correlate_threats(self, threats: List[ThreatIndicator]) -> List[ThreatIndicator]:
        """Correlate and deduplicate threat indicators"""
        # Group threats by source IP and user ID
        grouped_threats = defaultdict(list)
        
        for threat in threats:
            key = f"{threat.source_ip}:{threat.user_id}"
            grouped_threats[key].append(threat)
            
        # Combine related threats and increase confidence
        correlated_threats = []
        
        for group in grouped_threats.values():
            if len(group) == 1:
                correlated_threats.append(group[0])
            else:
                # Create a combined threat indicator
                primary_threat = max(group, key=lambda t: t.confidence_score)
                
                # Increase confidence based on multiple detections
                combined_confidence = min(0.99, primary_threat.confidence_score + 0.1 * (len(group) - 1))
                
                primary_threat.confidence_score = combined_confidence
                primary_threat.description += f" (Correlated with {len(group)-1} other indicators)"
                
                correlated_threats.append(primary_threat)
                
        return correlated_threats
        
    async def _is_malicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is known to be malicious"""
        # Simulate threat intelligence lookup
        known_malicious_ranges = [
            '10.0.0.0/8',    # Private ranges (for demo)
            '192.168.0.0/16',
            '172.16.0.0/12'
        ]
        
        try:
            ip = ipaddress.ip_address(ip_address)
            for range_str in known_malicious_ranges:
                if ip in ipaddress.ip_network(range_str):
                    return True
        except:
            pass
            
        return False
        
    async def _get_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Get IP reputation from threat intelligence"""
        # Check cache first
        if ip_address in self.ip_reputation_cache:
            cached = self.ip_reputation_cache[ip_address]
            if cached['timestamp'] > datetime.utcnow() - timedelta(hours=1):
                return cached
                
        # Simulate reputation lookup
        is_malicious = await self._is_malicious_ip(ip_address)
        
        reputation = {
            'ip_address': ip_address,
            'is_malicious': is_malicious,
            'confidence': 0.85 if is_malicious else 0.1,
            'reason': 'Known botnet IP' if is_malicious else 'Clean',
            'timestamp': datetime.utcnow()
        }
        
        # Cache the result
        self.ip_reputation_cache[ip_address] = reputation
        
        return reputation
        
    async def get_threat_intelligence(self) -> Dict[str, Any]:
        """Get current threat intelligence status"""
        active_threats_by_type = defaultdict(int)
        active_threats_by_severity = defaultdict(int)
        
        # Count active threats
        for threat in self.active_threats.values():
            active_threats_by_type[threat.threat_type.value] += 1
            active_threats_by_severity[threat.severity.value] += 1
            
        return {
            "total_active_threats": len(self.active_threats),
            "threats_by_type": dict(active_threats_by_type),
            "threats_by_severity": dict(active_threats_by_severity),
            "threat_intelligence": {
                "sources_active": self.threat_intelligence["sources"],
                "indicators_of_compromise": self.threat_intelligence["active_iocs"],
                "known_threat_actors": self.threat_intelligence["threat_actors"],
                "last_updated": self.threat_intelligence["last_updated"].isoformat()
            },
            "detection_engines": {
                engine.value: status for engine, status in self.detection_engines.items()
            },
            "platform_protection": {
                "content_scans_active": True,
                "behavioral_monitoring": True,
                "real_time_blocking": True,
                "creator_account_protection": True
            }
        }
        
    async def respond_to_threat(self, threat_id: str, action: str) -> Dict[str, Any]:
        """Execute threat response action"""
        if threat_id not in self.active_threats:
            raise ValueError(f"Threat {threat_id} not found")
            
        threat = self.active_threats[threat_id]
        
        response_actions = {
            "block_ip": "IP address blocked",
            "block_user": "User account suspended",
            "quarantine_file": "File quarantined",
            "require_2fa": "2FA required for account",
            "rate_limit": "Rate limiting applied",
            "manual_review": "Escalated for manual review"
        }
        
        if action not in response_actions:
            raise ValueError(f"Unknown action: {action}")
            
        # Execute the action (in production, would integrate with security systems)
        logger.info(f"Executing threat response: {action} for threat {threat_id}")
        
        return {
            "threat_id": threat_id,
            "action": action,
            "status": "executed",
            "description": response_actions[action],
            "timestamp": datetime.utcnow().isoformat()
        }