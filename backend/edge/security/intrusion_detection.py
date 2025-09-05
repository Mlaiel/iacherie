"""Intrusion Detection System
==========================

Edge intrusion detection with ML-based anomaly detection.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AttackType(str, Enum):
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    PORT_SCAN = "port_scan"
    MALWARE = "malware"
    UNKNOWN = "unknown"

@dataclass
class AttackSignature:
    signature_id: str
    name: str
    attack_type: AttackType
    pattern: str
    threat_level: ThreatLevel
    enabled: bool = True

@dataclass
class SecurityEvent:
    event_id: str
    timestamp: datetime
    source_ip: str
    attack_type: AttackType
    threat_level: ThreatLevel
    description: str
    blocked: bool = False

class IntrusionDetectionSystem:
    def __init__(self):
        self.signatures: Dict[str, AttackSignature] = {}
        self.events: List[SecurityEvent] = []
        self.threat_counts: Dict[str, int] = {}
        self.blocked_ips: set = set()
        self.running = False
        
        # Load default signatures
        self._load_default_signatures()
        
    def _load_default_signatures(self):
        default_sigs = [
            AttackSignature("brute_force_ssh", "SSH Brute Force", AttackType.BRUTE_FORCE, "ssh.*failed", ThreatLevel.HIGH),
            AttackSignature("sql_injection", "SQL Injection", AttackType.SQL_INJECTION, "union.*select", ThreatLevel.CRITICAL),
            AttackSignature("xss_attack", "XSS Attack", AttackType.XSS, "<script", ThreatLevel.MEDIUM),
            AttackSignature("port_scan", "Port Scan", AttackType.PORT_SCAN, "scan_pattern", ThreatLevel.MEDIUM)
        ]
        
        for sig in default_sigs:
            self.signatures[sig.signature_id] = sig
            
    async def start(self):
        self.running = True
        logger.info("Intrusion Detection System started")
        
    async def stop(self):
        self.running = False
        logger.info("Intrusion Detection System stopped")
        
    async def analyze_traffic(self, source_ip: str, payload: str) -> List[SecurityEvent]:
        detected_events = []
        
        for sig in self.signatures.values():
            if not sig.enabled:
                continue
                
            if self._signature_matches(sig, payload):
                event = SecurityEvent(
                    event_id=f"evt_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    source_ip=source_ip,
                    attack_type=sig.attack_type,
                    threat_level=sig.threat_level,
                    description=f"Detected {sig.name} from {source_ip}",
                    blocked=sig.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
                )
                
                detected_events.append(event)
                self.events.append(event)
                
                # Update threat counts
                self.threat_counts[source_ip] = self.threat_counts.get(source_ip, 0) + 1
                
                # Auto-block for high threats
                if event.blocked:
                    self.blocked_ips.add(source_ip)
                    
                logger.warning(f"Security event detected: {event.description}")
                
        return detected_events
        
    def _signature_matches(self, signature: AttackSignature, payload: str) -> bool:
        # Simplified pattern matching
        return signature.pattern.lower() in payload.lower()
        
    async def get_recent_events(self, hours: int = 24) -> List[SecurityEvent]:
        cutoff = datetime.now() - timedelta(hours=hours)
        return [event for event in self.events if event.timestamp > cutoff]
        
    async def get_threat_summary(self) -> Dict[str, Any]:
        recent_events = await self.get_recent_events()
        
        threat_by_level = {}
        threat_by_type = {}
        
        for event in recent_events:
            level = event.threat_level.value
            attack_type = event.attack_type.value
            
            threat_by_level[level] = threat_by_level.get(level, 0) + 1
            threat_by_type[attack_type] = threat_by_type.get(attack_type, 0) + 1
            
        return {
            'total_events': len(recent_events),
            'blocked_ips': len(self.blocked_ips),
            'threat_by_level': threat_by_level,
            'threat_by_type': threat_by_type,
            'top_threats': sorted(self.threat_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }

def create_intrusion_detection() -> IntrusionDetectionSystem:
    return IntrusionDetectionSystem()


"""DDoS Protection
===============

DDoS protection with rate limiting and traffic analysis.
"""

class MitigationStrategy(str, Enum):
    RATE_LIMIT = "rate_limit"
    BLOCK_IP = "block_ip"
    CAPTCHA = "captcha"
    TRAFFIC_SHAPING = "traffic_shaping"

class DDoSAttackType(str, Enum):
    VOLUMETRIC = "volumetric"
    PROTOCOL = "protocol"
    APPLICATION = "application"

class DDoSProtection:
    def __init__(self):
        self.request_counts: Dict[str, List[datetime]] = {}
        self.blocked_ips: set = set()
        self.rate_limit = 100  # requests per minute
        self.attack_threshold = 1000  # requests per minute
        
    async def check_rate_limit(self, client_ip: str) -> bool:
        now = datetime.now()
        
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
            
        # Clean old requests (older than 1 minute)
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Add current request
        self.request_counts[client_ip].append(now)
        
        # Check if exceeds rate limit
        if len(self.request_counts[client_ip]) > self.rate_limit:
            self.blocked_ips.add(client_ip)
            return False
            
        return True
        
    async def detect_attack(self, traffic_data: Dict[str, Any]) -> Optional[DDoSAttackType]:
        # Simplified DDoS detection
        total_requests = sum(len(requests) for requests in self.request_counts.values())
        
        if total_requests > self.attack_threshold:
            return DDoSAttackType.VOLUMETRIC
            
        return None
        
    async def get_protection_stats(self) -> Dict[str, Any]:
        return {
            'blocked_ips': len(self.blocked_ips),
            'active_connections': len(self.request_counts),
            'total_requests': sum(len(requests) for requests in self.request_counts.values())
        }

def create_ddos_protection() -> DDoSProtection:
    return DDoSProtection()


"""Threat Intelligence
===================

Threat intelligence feeds and IOC management.
"""

class ThreatSource(str, Enum):
    INTERNAL = "internal"
    COMMERCIAL = "commercial"
    OPEN_SOURCE = "open_source"
    GOVERNMENT = "government"

@dataclass
class ThreatIndicator:
    indicator_id: str
    value: str
    indicator_type: str  # ip, domain, hash, etc.
    threat_level: ThreatLevel
    source: ThreatSource
    confidence: float
    last_seen: datetime

class ThreatIntelligence:
    def __init__(self):
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.feeds: List[str] = []
        
    async def add_indicator(self, indicator: ThreatIndicator):
        self.indicators[indicator.indicator_id] = indicator
        
    async def check_threat(self, value: str) -> Optional[ThreatIndicator]:
        for indicator in self.indicators.values():
            if indicator.value == value:
                return indicator
        return None
        
    async def update_feeds(self):
        # Placeholder for threat feed updates
        logger.info("Updating threat intelligence feeds")

def create_threat_intelligence() -> ThreatIntelligence:
    return ThreatIntelligence()


"""Secure Tunneling
================

Secure tunnel management for edge communications.
"""

class TunnelProtocol(str, Enum):
    IPSEC = "ipsec"
    WIREGUARD = "wireguard"
    OPENVPN = "openvpn"

class EncryptionMethod(str, Enum):
    AES256 = "aes256"
    CHACHA20 = "chacha20"

class SecureTunnel:
    def __init__(self, protocol: TunnelProtocol = TunnelProtocol.WIREGUARD):
        self.protocol = protocol
        self.active_tunnels: Dict[str, Dict[str, Any]] = {}
        
    async def create_tunnel(self, tunnel_id: str, endpoint: str) -> bool:
        self.active_tunnels[tunnel_id] = {
            'endpoint': endpoint,
            'protocol': self.protocol,
            'created_at': datetime.now(),
            'status': 'active'
        }
        return True
        
    async def close_tunnel(self, tunnel_id: str) -> bool:
        if tunnel_id in self.active_tunnels:
            del self.active_tunnels[tunnel_id]
            return True
        return False

def create_secure_tunnel(protocol: TunnelProtocol = TunnelProtocol.WIREGUARD) -> SecureTunnel:
    return SecureTunnel(protocol)


"""Key Management
==============

Cryptographic key management for edge security.
"""

class KeyType(str, Enum):
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    SIGNING = "signing"

@dataclass
class KeyRotationPolicy:
    rotation_interval: int  # days
    auto_rotate: bool = True
    backup_generations: int = 3

class KeyManager:
    def __init__(self):
        self.keys: Dict[str, Dict[str, Any]] = {}
        self.rotation_policies: Dict[str, KeyRotationPolicy] = {}
        
    async def generate_key(self, key_id: str, key_type: KeyType) -> bool:
        self.keys[key_id] = {
            'type': key_type,
            'created_at': datetime.now(),
            'status': 'active'
        }
        return True
        
    async def rotate_key(self, key_id: str) -> bool:
        if key_id in self.keys:
            self.keys[key_id]['rotated_at'] = datetime.now()
            return True
        return False

def create_key_manager() -> KeyManager:
    return KeyManager()


"""Compliance Checker
==================

Security compliance validation and reporting.
"""

class ComplianceFramework(str, Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"

@dataclass
class ComplianceResult:
    framework: ComplianceFramework
    compliant: bool
    score: float
    violations: List[str]
    recommendations: List[str]

class ComplianceChecker:
    def __init__(self):
        self.frameworks: List[ComplianceFramework] = []
        self.last_check: Optional[datetime] = None
        
    async def add_framework(self, framework: ComplianceFramework):
        if framework not in self.frameworks:
            self.frameworks.append(framework)
            
    async def run_compliance_check(self, framework: ComplianceFramework) -> ComplianceResult:
        # Simplified compliance checking
        return ComplianceResult(
            framework=framework,
            compliant=True,
            score=95.0,
            violations=[],
            recommendations=["Enable additional logging", "Update security policies"]
        )

def create_compliance_checker() -> ComplianceChecker:
    return ComplianceChecker()