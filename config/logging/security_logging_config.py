"""Security Logging Configuration for IA-Influencer Agent Platform
===============================================================

Enterprise-grade security logging with threat detection, incident tracking,
compliance monitoring, and advanced security analytics for content protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import json
import time
import hashlib
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Union, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import ipaddress
import geoip2.database
import geoip2.errors
from collections import defaultdict, deque
import re

import structlog


class ThreatLevel(str, Enum):
    """
Security threat levels"""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class SecurityEventType(str, Enum):
    """Types of security events"""
    # Authentication & Authorization
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    AUTH_BRUTE_FORCE = "auth_brute_force"
    AUTH_ACCOUNT_LOCKED = "auth_account_locked"
    AUTH_MFA_BYPASS = "auth_mfa_bypass"
    
    # Access Control
    ACCESS_DENIED = "access_denied"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    
    # Network Security
    SUSPICIOUS_IP = "suspicious_ip"
    IP_BLOCKED = "ip_blocked"
    DDoS_ATTEMPT = "ddos_attempt"
    PORT_SCAN = "port_scan"
    NETWORK_INTRUSION = "network_intrusion"
    
    # Application Security
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTACK = "csrf_attack"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    DESERIALIZATION_ATTACK = "deserialization_attack"
    
    # API Security
    API_ABUSE = "api_abuse"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_API_KEY = "invalid_api_key"
    API_ENUMERATION = "api_enumeration"
    
    # Data Security
    DATA_BREACH = "data_breach"
    DATA_LEAK = "data_leak"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"
    UNAUTHORIZED_DOWNLOAD = "unauthorized_download"
    DATA_EXFILTRATION = "data_exfiltration"
    
    # Content Protection
    COPYRIGHT_VIOLATION = "copyright_violation"
    CONTENT_SCRAPING = "content_scraping"
    PIRACY_ATTEMPT = "piracy_attempt"
    DMCA_VIOLATION = "dmca_violation"
    
    # System Security
    MALWARE_DETECTED = "malware_detected"
    VIRUS_DETECTED = "virus_detected"
    SUSPICIOUS_FILE = "suspicious_file"
    SYSTEM_COMPROMISE = "system_compromise"
    ROOTKIT_DETECTED = "rootkit_detected"
    
    # Compliance Violations
    GDPR_VIOLATION = "gdpr_violation"
    PCI_VIOLATION = "pci_violation"
    HIPAA_VIOLATION = "hipaa_violation"
    SOX_VIOLATION = "sox_violation"


class IncidentStatus(str, Enum):
    """Security incident status"""

    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"


@dataclass
class ThreatIndicator:
    """Threat indicator information"""
    type: str  # ip, domain, hash, pattern
    value: str
    confidence: float  # 0.0 to 1.0
    source: str
    last_seen: datetime
    threat_types: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class GeoLocation:
    """Geographic location information"""
    country: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    asn: Optional[str] = None
    organization: Optional[str] = None


@dataclass
class SecurityEvent:
    """
Security event data structure"""
    event_id: str
    timestamp: datetime
    event_type: SecurityEventType
    threat_level: ThreatLevel
    
    # Source information
    source_ip: Optional[str] = None
    source_port: Optional[int] = None
    source_geo: Optional[GeoLocation] = None
    user_agent: Optional[str] = None
    
    # Target information
    target_resource: Optional[str] = None
    target_user: Optional[str] = None
    target_endpoint: Optional[str] = None
    
    # Event details
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Attack information
    attack_signature: Optional[str] = None
    attack_vector: Optional[str] = None
    payload: Optional[str] = None
    
    # Threat intelligence
    threat_indicators: List[ThreatIndicator] = field(default_factory=list)
    threat_score: float = 0.0
    
    # Response information
    blocked: bool = False
    mitigated: bool = False
    response_actions: List[str] = field(default_factory=list)
    
    # Context
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # Incident tracking
    incident_id: Optional[str] = None
    incident_status: Optional[IncidentStatus] = None


@dataclass
class AttackPattern:
    """Attack pattern definition"""
    name: str
    pattern: Union[str, re.Pattern]
    event_type: SecurityEventType
    threat_level: ThreatLevel
    description: str = ""
    confidence: float = 0.8
    enabled: bool = True


@dataclass
class IPReputation:
    """IP address reputation information"""
    ip: str
    reputation_score: float  # -1.0 to 1.0
    threat_types: List[str] = field(default_factory=list)
    last_seen_malicious: Optional[datetime] = None
    blacklisted: bool = False
    whitelisted: bool = False
    geo_location: Optional[GeoLocation] = None


class SecurityLoggingConfig:
    """
    Enterprise security logging configuration for IA-Influencer platform.
    
    Provides comprehensive security event detection, threat intelligence,
    incident tracking, and compliance monitoring for multi-format content
    protection and business operations.
    """
    
    def __init__(
        self,
        enabled: bool = True,
        threat_detection_enabled: bool = True,
        geo_ip_enabled: bool = True,
        geo_ip_database_path: Optional[str] = None,
        reputation_checking_enabled: bool = True,
        incident_tracking_enabled: bool = True,
        compliance_monitoring_enabled: bool = True,
        real_time_alerting_enabled: bool = True,
        threat_intelligence_enabled: bool = True,
        attack_patterns: Optional[List[AttackPattern]] = None,
        ip_whitelist: Optional[List[str]] = None,
        ip_blacklist: Optional[List[str]] = None,
        max_events_memory: int = 10000,
        event_correlation_window: int = 300,  # seconds
        auto_incident_threshold: float = 0.8,
        enable_ml_detection: bool = False,
        webhook_urls: Optional[List[str]] = None
    ):
        """
        Initialize security logging configuration.
        
        Args:
            enabled: Enable security logging
            threat_detection_enabled: Enable automated threat detection
            geo_ip_enabled: Enable GeoIP lookup
            geo_ip_database_path: Path to GeoIP database
            reputation_checking_enabled: Enable IP reputation checking
            incident_tracking_enabled: Enable incident tracking
            compliance_monitoring_enabled: Enable compliance monitoring
            real_time_alerting_enabled: Enable real-time alerts
            threat_intelligence_enabled: Enable threat intelligence
            attack_patterns: Custom attack patterns
            ip_whitelist: IP addresses to whitelist
            ip_blacklist: IP addresses to blacklist
            max_events_memory: Maximum events to keep in memory
            event_correlation_window: Time window for event correlation (seconds)
            auto_incident_threshold: Threshold for automatic incident creation
            enable_ml_detection: Enable ML-based threat detection
            webhook_urls: Webhook URLs for alerts
        """
        self.enabled = enabled
        self.threat_detection_enabled = threat_detection_enabled
        self.geo_ip_enabled = geo_ip_enabled
        self.reputation_checking_enabled = reputation_checking_enabled
        self.incident_tracking_enabled = incident_tracking_enabled
        self.compliance_monitoring_enabled = compliance_monitoring_enabled
        self.real_time_alerting_enabled = real_time_alerting_enabled
        self.threat_intelligence_enabled = threat_intelligence_enabled
        self.max_events_memory = max_events_memory
        self.event_correlation_window = event_correlation_window
        self.auto_incident_threshold = auto_incident_threshold
        self.enable_ml_detection = enable_ml_detection
        self.webhook_urls = webhook_urls or []
        
        # Initialize GeoIP
        self._geo_reader = None
        if geo_ip_enabled and geo_ip_database_path:
            self._initialize_geoip(geo_ip_database_path)
        
        # Initialize attack patterns
        self.attack_patterns = attack_patterns or self._create_default_attack_patterns()
        self._compile_attack_patterns()
        
        # Initialize IP lists
        self.ip_whitelist = set(ip_whitelist or [])
        self.ip_blacklist = set(ip_blacklist or [])
        
        # Initialize data structures
        self._events_buffer: deque = deque(maxlen=max_events_memory)
        self._ip_reputation_cache: Dict[str, IPReputation] = {}
        self._active_incidents: Dict[str, Dict[str, Any]] = {}
        self._event_correlations: Dict[str, List[SecurityEvent]] = defaultdict(list)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'total_events': 0,
            'events_by_type': defaultdict(int),
            'events_by_threat_level': defaultdict(int),
            'blocked_ips': set(),
            'active_incidents': 0,
            'false_positives': 0
        }
        
        # Initialize logger
        self._security_logger = self._initialize_security_logger()
    
    def _initialize_geoip(self, database_path: str) -> None:
        """
Initialize GeoIP database reader"""
        try:
            self._geo_reader = geoip2.database.Reader(database_path)
            logging.info(f"Initialized GeoIP database: {database_path}")
        except Exception as e:
            logging.error(f"Failed to initialize GeoIP database: {e}")
            self._geo_reader = None
    
    def _initialize_security_logger(self) -> structlog.BoundLogger:
        """Initialize structured security logger"""
        return structlog.get_logger("ia_influencer_security")
    
    def _create_default_attack_patterns(self) -> List[AttackPattern]:
        """Create default attack detection patterns"""
        patterns = [
            # SQL Injection patterns
            AttackPattern(
                name="sql_injection_union",
                pattern=re.compile(r"union\s+select", re.IGNORECASE),
                event_type=SecurityEventType.SQL_INJECTION,
                threat_level=ThreatLevel.HIGH,
                description="SQL injection using UNION SELECT"
            ),
            AttackPattern(
                name="sql_injection_or1",
                pattern=re.compile(r"'\s*or\s*'1'\s*=\s*'1", re.IGNORECASE),
                event_type=SecurityEventType.SQL_INJECTION,
                threat_level=ThreatLevel.HIGH,
                description="SQL injection using OR 1=1"
            ),
            
            # XSS patterns
            AttackPattern(
                name="xss_script_tag",
                pattern=re.compile(r"<script[^>]*>", re.IGNORECASE),
                event_type=SecurityEventType.XSS_ATTEMPT,
                threat_level=ThreatLevel.MEDIUM,
                description="XSS attempt using script tag"
            ),
            AttackPattern(
                name="xss_javascript",
                pattern=re.compile(r"javascript:", re.IGNORECASE),
                event_type=SecurityEventType.XSS_ATTEMPT,
                threat_level=ThreatLevel.MEDIUM,
                description="XSS attempt using javascript protocol"
            ),
            
            # Path traversal
            AttackPattern(
                name="path_traversal_dotdot",
                pattern=re.compile(r"\.\./", re.IGNORECASE),
                event_type=SecurityEventType.PATH_TRAVERSAL,
                threat_level=ThreatLevel.MEDIUM,
                description="Path traversal using ../"
            ),
            
            # Command injection
            AttackPattern(
                name="command_injection_pipe",
                pattern=re.compile(r"[;&|`]", re.IGNORECASE),
                event_type=SecurityEventType.COMMAND_INJECTION,
                threat_level=ThreatLevel.HIGH,
                description="Command injection using shell metacharacters"
            ),
            
            # API enumeration
            AttackPattern(
                name="api_enumeration_admin",
                pattern=re.compile(r"/admin|/api/v\d+/admin", re.IGNORECASE),
                event_type=SecurityEventType.API_ENUMERATION,
                threat_level=ThreatLevel.MEDIUM,
                description="Attempt to access admin API endpoints"
            ),
            
            # Content scraping
            AttackPattern(
                name="content_scraping_bot",
                pattern=re.compile(r"bot|crawler|scraper|spider", re.IGNORECASE),
                event_type=SecurityEventType.CONTENT_SCRAPING,
                threat_level=ThreatLevel.LOW,
                description="Potential content scraping bot"
            ),
            
            # DDoS patterns
            AttackPattern(
                name="ddos_high_frequency",
                pattern=re.compile(r".*"),  # Special case - handled by frequency analysis
                event_type=SecurityEventType.DDoS_ATTEMPT,
                threat_level=ThreatLevel.CRITICAL,
                description="High frequency request pattern"
            )
        ]
        
        return patterns
    
    def _compile_attack_patterns(self) -> None:
        """Compile regex patterns for attack detection"""
        for pattern in self.attack_patterns:
            if isinstance(pattern.pattern, str):
                try:
                    pattern.pattern = re.compile(pattern.pattern, re.IGNORECASE)
                except re.error as e:
                    logging.error(f"Invalid regex in attack pattern {pattern.name}: {e}")
                    pattern.enabled = False
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        threat_level: ThreatLevel,
        description: str,
        source_ip: Optional[str] = None,
        target_user: Optional[str] = None,
        target_resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            threat_level: Threat severity level
            description: Event description
            source_ip: Source IP address
            target_user: Target user
            target_resource: Target resource
            details: Additional event details
            **kwargs: Additional event fields
            
        Returns:
            Event ID
        """
        if not self.enabled:
            return ""
        
        # Create security event
        event = SecurityEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            threat_level=threat_level,
            description=description,
            source_ip=source_ip,
            target_user=target_user,
            target_resource=target_resource,
            details=details or {},
            **kwargs
        )
        
        # Enrich event with additional context
        self._enrich_security_event(event)
        
        # Perform threat detection
        if self.threat_detection_enabled:
            self._perform_threat_detection(event)
        
        # Store event
        with self._lock:
            self._events_buffer.append(event)
            self._update_statistics(event)
        
        # Log the event
        self._log_security_event(event)
        
        # Check for incident creation
        if self.incident_tracking_enabled:
            self._check_incident_creation(event)
        
        # Perform event correlation
        self._correlate_events(event)
        
        # Send real-time alerts
        if self.real_time_alerting_enabled:
            self._send_security_alert(event)
        
        return event.event_id
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"SEC_{timestamp}_{random_part}"
    
    def _enrich_security_event(self, event: SecurityEvent) -> None:
        """Enrich security event with additional context"""
        # GeoIP lookup
        if self.geo_ip_enabled and event.source_ip and self._geo_reader:
            try:
                response = self._geo_reader.city(event.source_ip)
                event.source_geo = GeoLocation(
                    country=response.country.name,
                    country_code=response.country.iso_code,
                    region=response.subdivisions.most_specific.name,
                    city=response.city.name,
                    latitude=float(response.location.latitude) if response.location.latitude else None,
                    longitude=float(response.location.longitude) if response.location.longitude else None,
                    asn=str(response.traits.autonomous_system_number) if response.traits.autonomous_system_number else None,
                    organization=response.traits.autonomous_system_organization
                )
            except geoip2.errors.AddressNotFoundError:
                pass
            except Exception as e:
                logging.debug(f"GeoIP lookup failed for {event.source_ip}: {e}")
        
        # IP reputation check
        if self.reputation_checking_enabled and event.source_ip:
            reputation = self._get_ip_reputation(event.source_ip)
            if reputation:
                event.threat_score = max(event.threat_score, reputation.reputation_score)
                if reputation.threat_types:
                    for threat_type in reputation.threat_types:
                        event.threat_indicators.append(ThreatIndicator(
                            type="ip",
                            value=event.source_ip,
                            confidence=0.8,
                            source="reputation_db",
                            last_seen=datetime.now(timezone.utc),
                            threat_types=[threat_type]
                        ))
        
        # Check IP lists
        if event.source_ip:
            if self._is_ip_whitelisted(event.source_ip):
                event.threat_score = min(event.threat_score, 0.1)
            elif self._is_ip_blacklisted(event.source_ip):
                event.threat_score = max(event.threat_score, 0.9)
                event.blocked = True
    
    def _perform_threat_detection(self, event: SecurityEvent) -> None:
        """Perform automated threat detection"""
        for pattern in self.attack_patterns:
            if not pattern.enabled:
                continue
            
            # Check if pattern matches
            match_found = False
            
            # Check different fields based on pattern type
            fields_to_check = [
                event.description,
                event.target_resource,
                str(event.details),
                event.payload or ""
            ]
            
            for field in fields_to_check:
                if field and pattern.pattern.search(str(field)):
                    match_found = True
                    break
            
            if match_found:
                # Update event information
                event.event_type = pattern.event_type
                event.threat_level = max(event.threat_level, pattern.threat_level, key=lambda x: self._threat_level_value(x))
                event.attack_signature = pattern.name
                event.threat_score = max(event.threat_score, pattern.confidence)
                
                # Add threat indicator
                event.threat_indicators.append(ThreatIndicator(
                    type="pattern",
                    value=pattern.name,
                    confidence=pattern.confidence,
                    source="attack_patterns",
                    last_seen=datetime.now(timezone.utc),
                    description=pattern.description
                ))
                
                break  # Use first matching pattern
    
    def _threat_level_value(self, level: ThreatLevel) -> int:
        """Get numeric value for threat level comparison"""
        values = {
            ThreatLevel.INFO: 1,
            ThreatLevel.LOW: 2,
            ThreatLevel.MEDIUM: 3,
            ThreatLevel.HIGH: 4,
            ThreatLevel.CRITICAL: 5
        }
        return values.get(level, 0)
    
    def _get_ip_reputation(self, ip: str) -> Optional[IPReputation]:
        """
Get IP reputation information"""
        if ip in self._ip_reputation_cache:
            return self._ip_reputation_cache[ip]
        
        # In a real implementation, this would query external threat intelligence
        # For now, we'll create a basic reputation based on IP characteristics
        reputation = self._calculate_basic_ip_reputation(ip)
        
        if reputation:
            self._ip_reputation_cache[ip] = reputation
        
        return reputation
    
    def _calculate_basic_ip_reputation(self, ip: str) -> Optional[IPReputation]:
        """
Calculate basic IP reputation"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            reputation_score = 0.0
            threat_types = []
            
            # Check for private/reserved IPs
            if ip_obj.is_private or ip_obj.is_reserved or ip_obj.is_loopback:
                reputation_score = 0.5  # Neutral for internal IPs
            
            # Check for known malicious ranges (simplified example)
            if str(ip_obj).startswith(('192.0.2.', '198.51.100.', '203.0.113.')):
                # TEST-NET ranges - should not appear in production
                reputation_score = -0.8
                threat_types.append('test_network')
            
            return IPReputation(
                ip=ip,
                reputation_score=reputation_score,
                threat_types=threat_types,
                geo_location=None  # Would be filled by GeoIP
            )
            
        except ValueError:
            return None
    
    def _is_ip_whitelisted(self, ip: str) -> bool:
        """
Check if IP is in whitelist"""
        return ip in self.ip_whitelist
    
    def _is_ip_blacklisted(self, ip: str) -> bool:
        """
Check if IP is in blacklist"""
        return ip in self.ip_blacklist
    
    def _update_statistics(self, event: SecurityEvent) -> None:
        """
Update security statistics"""
        self._stats['total_events'] += 1
        self._stats['events_by_type'][event.event_type.value] += 1
        self._stats['events_by_threat_level'][event.threat_level.value] += 1
        
        if event.blocked and event.source_ip:
            self._stats['blocked_ips'].add(event.source_ip)
    
    def _log_security_event(self, event: SecurityEvent) -> None:
        """
Log security event using structured logging"""
        try:
            event_dict = asdict(event)
            
            # Convert datetime objects to ISO format
            event_dict['timestamp'] = event.timestamp.isoformat()
            if event.source_geo and hasattr(event.source_geo, '__dict__'):
                event_dict['source_geo'] = asdict(event.source_geo)
            
            # Convert threat indicators
            if event.threat_indicators:
                event_dict['threat_indicators'] = [
                    {**asdict(indicator), 'last_seen': indicator.last_seen.isoformat()}
                    for indicator in event.threat_indicators
                ]
            
            # Log with appropriate level
            log_level = self._get_log_level_for_threat(event.threat_level)
            
            self._security_logger.log(
                log_level,
                "Security event detected",
                **event_dict
            )
            
        except Exception as e:
            logging.error(f"Failed to log security event: {e}")
    
    def _get_log_level_for_threat(self, threat_level: ThreatLevel) -> int:
        """Get logging level for threat level"""
        mapping = {
            ThreatLevel.INFO: logging.INFO,
            ThreatLevel.LOW: logging.INFO,
            ThreatLevel.MEDIUM: logging.WARNING,
            ThreatLevel.HIGH: logging.ERROR,
            ThreatLevel.CRITICAL: logging.CRITICAL
        }
        return mapping.get(threat_level, logging.WARNING)
    
    def _check_incident_creation(self, event: SecurityEvent) -> None:
        """
Check if event should trigger incident creation"""
        if event.threat_score >= self.auto_incident_threshold:
            incident_id = self._create_incident(event)
            event.incident_id = incident_id
    
    def _create_incident(self, triggering_event: SecurityEvent) -> str:
        """
Create a new security incident"""
        incident_id = f"INC_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        incident = {
            'id': incident_id,
            'created_at': datetime.now(timezone.utc),
            'status': IncidentStatus.OPEN,
            'threat_level': triggering_event.threat_level,
            'event_type': triggering_event.event_type,
            'triggering_event_id': triggering_event.event_id,
            'related_events': [triggering_event.event_id],
            'source_ips': [triggering_event.source_ip] if triggering_event.source_ip else [],
            'affected_users': [triggering_event.target_user] if triggering_event.target_user else [],
            'affected_resources': [triggering_event.target_resource] if triggering_event.target_resource else [],
            'description': f"Automated incident created for {triggering_event.event_type.value}",
            'response_actions': []
        }
        
        with self._lock:
            self._active_incidents[incident_id] = incident
            self._stats['active_incidents'] += 1
        
        # Log incident creation
        self._security_logger.critical(
            "Security incident created",
            incident_id=incident_id,
            triggering_event=triggering_event.event_id,
            threat_level=triggering_event.threat_level.value
        )
        
        return incident_id
    
    def _correlate_events(self, event: SecurityEvent) -> None:
        """Correlate events for pattern detection"""
        correlation_key = self._get_correlation_key(event)
        
        with self._lock:
            self._event_correlations[correlation_key].append(event)
            
            # Remove old events outside correlation window
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=self.event_correlation_window)
            self._event_correlations[correlation_key] = [
                e for e in self._event_correlations[correlation_key]
                if e.timestamp > cutoff_time
            ]
            
            # Check for patterns in correlated events
            self._analyze_correlated_events(correlation_key)
    
    def _get_correlation_key(self, event: SecurityEvent) -> str:
        """
Get correlation key for event grouping"""
        # Group by source IP and event type
        return f"{event.source_ip or 'unknown'}_{event.event_type.value}"
    
    def _analyze_correlated_events(self, correlation_key: str) -> None:
        """Analyze correlated events for attack patterns"""
        events = self._event_correlations[correlation_key]
        
        if len(events) < 2:
            return
        
        # Check for brute force attacks
        if len(events) >= 5:
            auth_failures = [e for e in events if e.event_type == SecurityEventType.AUTH_FAILURE]
            if len(auth_failures) >= 5:
                # Create brute force event
                latest_event = max(events, key=lambda e: e.timestamp)
                self.log_security_event(
                    event_type=SecurityEventType.AUTH_BRUTE_FORCE,
                    threat_level=ThreatLevel.HIGH,
                    description=f"Brute force attack detected: {len(auth_failures)} failed attempts",
                    source_ip=latest_event.source_ip,
                    details={'failed_attempts': len(auth_failures), 'time_window': self.event_correlation_window}
                )
        
        # Check for DDoS patterns
        if len(events) >= 100:  # High frequency requests
            self.log_security_event(
                event_type=SecurityEventType.DDoS_ATTEMPT,
                threat_level=ThreatLevel.CRITICAL,
                description=f"DDoS attack detected: {len(events)} requests in {self.event_correlation_window} seconds",
                source_ip=events[0].source_ip,
                details={'request_count': len(events), 'time_window': self.event_correlation_window}
            )
    
    def _send_security_alert(self, event: SecurityEvent) -> None:
        """Send real-time security alert"""
        if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._send_webhook_alert(event)
    
    def _send_webhook_alert(self, event: SecurityEvent) -> None:
        """
Send webhook alert for security event"""
        if not self.webhook_urls:
            return
        
        try:
            import requests
            
            alert_data = {
                'event_id': event.event_id,
                'timestamp': event.timestamp.isoformat(),
                'event_type': event.event_type.value,
                'threat_level': event.threat_level.value,
                'description': event.description,
                'source_ip': event.source_ip,
                'target_user': event.target_user,
                'target_resource': event.target_resource,
                'threat_score': event.threat_score,
                'blocked': event.blocked
            }
            
            for webhook_url in self.webhook_urls:
                try:
                    response = requests.post(
                        webhook_url,
                        json=alert_data,
                        timeout=10,
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status()
                except requests.RequestException as e:
                    logging.error(f"Failed to send webhook alert to {webhook_url}: {e}")
                    
        except ImportError:
            logging.warning("requests library not available for webhook alerts")
        except Exception as e:
            logging.error(f"Error sending webhook alert: {e}")
    
    def get_security_events(
        self,
        limit: int = 100,
        threat_level: Optional[ThreatLevel] = None,
        event_type: Optional[SecurityEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[SecurityEvent]:
        """
        Get security events with filtering.
        
        Args:
            limit: Maximum number of events to return
            threat_level: Filter by threat level
            event_type: Filter by event type
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of security events
        """
        with self._lock:
            events = list(self._events_buffer)
        
        # Apply filters
        if threat_level:
            events = [e for e in events if e.threat_level == threat_level]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
    
    def get_security_statistics(self) -> Dict[str, Any]:
        """
Get security statistics"""
        with self._lock:
            stats = self._stats.copy()
            stats['blocked_ips'] = list(stats['blocked_ips'])
            stats['events_by_type'] = dict(stats['events_by_type'])
            stats['events_by_threat_level'] = dict(stats['events_by_threat_level'])
            stats['buffer_size'] = len(self._events_buffer)
            stats['active_correlations'] = len(self._event_correlations)
            stats['ip_reputation_cache_size'] = len(self._ip_reputation_cache)
        
        return stats
    
    def add_ip_to_whitelist(self, ip: str) -> None:
        """
Add IP to whitelist"""
        self.ip_whitelist.add(ip)
        logging.info(f"Added IP to whitelist: {ip}")
    
    def remove_ip_from_whitelist(self, ip: str) -> None:
        """Remove IP from whitelist"""
        self.ip_whitelist.discard(ip)
        logging.info(f"Removed IP from whitelist: {ip}")
    
    def add_ip_to_blacklist(self, ip: str) -> None:
        """Add IP to blacklist"""
        self.ip_blacklist.add(ip)
        logging.info(f"Added IP to blacklist: {ip}")
    
    def remove_ip_from_blacklist(self, ip: str) -> None:
        """Remove IP from blacklist"""
        self.ip_blacklist.discard(ip)
        logging.info(f"Removed IP from blacklist: {ip}")
    
    def update_incident_status(self, incident_id: str, status: IncidentStatus, notes: str = "") -> bool:
        """Update incident status"""
        with self._lock:
            if incident_id in self._active_incidents:
                incident = self._active_incidents[incident_id]
                old_status = incident['status']
                incident['status'] = status
                incident['updated_at'] = datetime.now(timezone.utc)
                
                if notes:
                    if 'notes' not in incident:
                        incident['notes'] = []
                    incident['notes'].append({
                        'timestamp': datetime.now(timezone.utc),
                        'note': notes
                    })
                
                # Update statistics
                if status == IncidentStatus.CLOSED and old_status != IncidentStatus.CLOSED:
                    self._stats['active_incidents'] -= 1
                
                self._security_logger.info(
                    "Incident status updated",
                    incident_id=incident_id,
                    old_status=old_status.value,
                    new_status=status.value,
                    notes=notes
                )
                
                return True
        
        return False
    
    def add_attack_pattern(self, pattern: AttackPattern) -> None:
        """Add custom attack pattern"""
        self.attack_patterns.append(pattern)
        self._compile_attack_patterns()
        logging.info(f"Added attack pattern: {pattern.name}")
    
    def remove_attack_pattern(self, pattern_name: str) -> bool:
        """Remove attack pattern"""
        pattern = next((p for p in self.attack_patterns if p.name == pattern_name), None)
        if pattern:
            self.attack_patterns.remove(pattern)
            logging.info(f"Removed attack pattern: {pattern_name}")
            return True
        return False
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get current configuration status"""
        return {
            "enabled": self.enabled,
            "threat_detection_enabled": self.threat_detection_enabled,
            "geo_ip_enabled": self.geo_ip_enabled,
            "reputation_checking_enabled": self.reputation_checking_enabled,
            "incident_tracking_enabled": self.incident_tracking_enabled,
            "compliance_monitoring_enabled": self.compliance_monitoring_enabled,
            "real_time_alerting_enabled": self.real_time_alerting_enabled,
            "threat_intelligence_enabled": self.threat_intelligence_enabled,
            "attack_patterns_count": len(self.attack_patterns),
            "ip_whitelist_count": len(self.ip_whitelist),
            "ip_blacklist_count": len(self.ip_blacklist),
            "max_events_memory": self.max_events_memory,
            "event_correlation_window": self.event_correlation_window,
            "auto_incident_threshold": self.auto_incident_threshold,
            "webhook_urls_count": len(self.webhook_urls),
            "geoip_available": self._geo_reader is not None
        }


# Global security logging configuration instance
_security_config: Optional[SecurityLoggingConfig] = None


def initialize_security_logging(
    config: Optional[SecurityLoggingConfig] = None
) -> SecurityLoggingConfig:
    """
    Initialize global security logging configuration.
    
    Args:
        config: Custom SecurityLoggingConfig instance
        
    Returns:
        Initialized security logging configuration
    """
    global _security_config
    
    if config:
        _security_config = config
    else:
        _security_config = SecurityLoggingConfig()
    
    return _security_config


def get_security_config() -> SecurityLoggingConfig:
    """
Get the global security logging configuration"""
    if not _security_config:
        initialize_security_logging()
    
    return _security_config


def log_security_event(
    event_type: SecurityEventType,
    threat_level: ThreatLevel,
    description: str,
    **kwargs
) -> str:
    """
    Log a security event using global configuration.
    
    Args:
        event_type: Type of security event
        threat_level: Threat severity level
        description: Event description
        **kwargs: Additional event fields
        
    Returns:
        Event ID
    """
    config = get_security_config()
    return config.log_security_event(event_type, threat_level, description, **kwargs)
