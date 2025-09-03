"""Threat Detection Service - Détection menaces

Enterprise threat detection and security monitoring service.
Consolidates functionality from crawlers/monitors/threat_detector.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import hashlib
import json
import re
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    DDOS_ATTACK = "ddos_attack"
    MALWARE_DETECTION = "malware_detection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    SCRAPING_ABUSE = "scraping_abuse"
    API_ABUSE = "api_abuse"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    INJECTION_ATTACK = "injection_attack"


class ThreatSource(Enum):
    """Sources of threat detection"""
    WEB_TRAFFIC = "web_traffic"
    API_REQUESTS = "api_requests"
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_LOGS = "system_logs"
    NETWORK_TRAFFIC = "network_traffic"
    FILE_UPLOADS = "file_uploads"


@dataclass
class ThreatIndicator:
    """Threat indicator information"""
    indicator_type: str
    value: str
    confidence: float
    first_seen: datetime
    last_seen: datetime
    source: ThreatSource
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatEvent:
    """Threat event information"""
    event_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    source_ip: str
    target: str
    description: str
    indicators: List[ThreatIndicator]
    detected_at: datetime
    confidence_score: float
    mitigated: bool = False
    mitigation_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityMetrics:
    """Security monitoring metrics"""
    total_events: int
    threat_levels: Dict[str, int]
    threat_types: Dict[str, int]
    source_ips: Dict[str, int]
    detection_rate: float
    false_positive_rate: float
    response_time_avg: float
    last_updated: datetime


class ThreatDetectionService:
    """
    Enterprise threat detection and security monitoring service.
    Consolidates functionality from existing threat detection modules.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logger
        self.config = config or {}
        
        # Threat storage and tracking
        self.active_threats: Dict[str, ThreatEvent] = {}
        self.threat_history: List[ThreatEvent] = []
        self.blocked_ips: Set[str] = set()
        self.threat_indicators: Dict[str, ThreatIndicator] = {}
        
        # Detection patterns consolidated from existing implementation
        self.threat_patterns = {
            ThreatType.SQL_INJECTION: [
                r"union\s+select",
                r"1=1",
                r"drop\s+table",
                r"delete\s+from",
                r"insert\s+into",
                r"update\s+.*set",
                r"'\s*or\s*'",
                r"--\s*$",
                r"/\*.*\*/"
            ],
            ThreatType.XSS_ATTACK: [
                r"<script.*?>.*?</script>",
                r"javascript:",
                r"onload\s*=",
                r"onerror\s*=",
                r"<iframe.*?>",
                r"eval\s*\(",
                r"document\.cookie",
                r"window\.location"
            ],
            ThreatType.INJECTION_ATTACK: [
                r"\.\.\/",
                r"\/etc\/passwd",
                r"cmd\.exe",
                r"powershell",
                r"bash\s+-c",
                r"sh\s+-c",
                r"\|",
                r"&&",
                r";"
            ],
            ThreatType.SCRAPING_ABUSE: [
                r"bot",
                r"crawler",
                r"spider",
                r"scraper",
                r"wget",
                r"curl",
                r"python-requests",
                r"scrapy"
            ]
        }
        
        # Configuration
        self.detection_enabled = self.config.get('detection_enabled', True)
        self.auto_block = self.config.get('auto_block', True)
        self.block_threshold = self.config.get('block_threshold', 5)
        self.monitoring_interval = self.config.get('monitoring_interval', 60)  # seconds
        
        # Request tracking for rate limiting
        self.request_counts: defaultdict = defaultdict(lambda: deque(maxlen=100))
        
        # Start monitoring if enabled
        if self.detection_enabled:
            asyncio.create_task(self._start_monitoring())
    
    async def _start_monitoring(self):
        """Start background threat monitoring"""
        self.logger.info("Starting threat detection monitoring")
        
        while self.detection_enabled:
            try:
                await self._monitor_threats()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(30)  # Brief pause before retry
    
    async def _monitor_threats(self):
        """Monitor for various threat types"""
        # Monitor user behavior patterns
        await self._monitor_user_behavior()
        
        # Check for suspicious network activity
        await self._monitor_network_activity()
        
        # Process pending threat events
        await self._process_threat_events()
        
        # Clean up old events
        await self._cleanup_old_events()
    
    async def _monitor_user_behavior(self):
        """Monitor user behavior for suspicious activity"""
        # Simplified behavioral monitoring
        for ip, requests in self.request_counts.items():
            if len(requests) > 0:
                # Check for rapid requests (potential DDoS)
                recent_requests = [
                    r for r in requests
                    if datetime.now() - r['timestamp'] < timedelta(minutes=5)
                ]
                
                if len(recent_requests) > 50:  # Threshold for suspicious activity
                    await self._create_threat_event(
                        threat_type=ThreatType.DDOS_ATTACK,
                        source_ip=ip,
                        description=f"Rapid requests detected: {len(recent_requests)} in 5 minutes",
                        confidence=0.8
                    )
    
    async def _monitor_network_activity(self):
        """Monitor network activity for threats"""
        # Check blocked IPs for continued activity
        for blocked_ip in list(self.blocked_ips):
            # In production, this would check actual network logs
            # For now, we simulate checking
            pass
    
    async def _process_threat_events(self):
        """Process pending threat events"""
        for threat_id, threat_event in list(self.active_threats.items()):
            if not threat_event.mitigated:
                await self._handle_threat_event(threat_event)
    
    async def analyze_request(
        self,
        request_data: Dict[str, Any],
        source_ip: str,
        user_agent: str,
        path: str
    ) -> Optional[ThreatEvent]:
        """
        Analyze incoming request for threats
        Consolidated from crawlers/monitors/threat_detector.py
        """
        try:
            # Track request for rate limiting
            self.request_counts[source_ip].append({
                'timestamp': datetime.now(),
                'path': path,
                'user_agent': user_agent
            })
            
            threats_detected = []
            
            # Check for injection attacks
            if self._detect_injection_attack(path, str(request_data)):
                threats_detected.append({
                    'type': ThreatType.INJECTION_ATTACK,
                    'confidence': 0.9,
                    'description': 'Injection attack pattern detected in request'
                })
            
            # Check for XSS attacks
            if self._detect_xss_attack(str(request_data)):
                threats_detected.append({
                    'type': ThreatType.XSS_ATTACK,
                    'confidence': 0.85,
                    'description': 'XSS attack pattern detected'
                })
            
            # Check for scraping abuse
            if self._detect_scraping_abuse(user_agent, {'source_ip': source_ip}):
                threats_detected.append({
                    'type': ThreatType.SCRAPING_ABUSE,
                    'confidence': 0.7,
                    'description': 'Scraping abuse detected'
                })
            
            # Check for DDoS patterns
            if self._detect_ddos_pattern(source_ip):
                threats_detected.append({
                    'type': ThreatType.DDOS_ATTACK,
                    'confidence': 0.8,
                    'description': 'DDoS attack pattern detected'
                })
            
            # Create threat event if threats detected
            if threats_detected:
                # Use highest confidence threat
                primary_threat = max(threats_detected, key=lambda x: x['confidence'])
                
                threat_event = await self._create_threat_event(
                    threat_type=primary_threat['type'],
                    source_ip=source_ip,
                    description=primary_threat['description'],
                    confidence=primary_threat['confidence'],
                    target=path,
                    additional_data={
                        'user_agent': user_agent,
                        'all_threats': threats_detected,
                        'request_data': request_data
                    }
                )
                
                return threat_event
            
            return None
            
        except Exception as e:
            self.logger.error(f"Request analysis failed: {str(e)}")
            return None
    
    def _detect_injection_attack(self, path: str, data: str) -> bool:
        """
        Detect injection attack patterns
        From crawlers/monitors/threat_detector.py
        """
        patterns = self.threat_patterns.get(ThreatType.INJECTION_ATTACK, [])
        
        combined_input = f"{path} {data}".lower()
        
        for pattern in patterns:
            if re.search(pattern, combined_input, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_xss_attack(self, data: str) -> bool:
        """Detect XSS attack patterns"""
        patterns = self.threat_patterns.get(ThreatType.XSS_ATTACK, [])
        
        for pattern in patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_scraping_abuse(self, user_agent: str, event: Dict[str, Any]) -> bool:
        """
        Detect scraping abuse patterns
        From crawlers/monitors/threat_detector.py
        """
        patterns = self.threat_patterns.get(ThreatType.SCRAPING_ABUSE, [])
        
        for pattern in patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        # Check request frequency
        source_ip = event.get("source_ip")
        if source_ip:
            recent_requests = self._count_recent_requests(source_ip)
            if recent_requests > 100:  # Threshold for suspicious activity
                return True
        
        return False
    
    def _detect_ddos_pattern(self, source_ip: str) -> bool:
        """Detect DDoS attack patterns"""
        recent_count = self._count_recent_requests(source_ip, minutes=1)
        return recent_count > 20  # More than 20 requests per minute
    
    def _count_recent_requests(self, source_ip: str, minutes: int = 5) -> int:
        """Count recent requests from IP"""
        if source_ip not in self.request_counts:
            return 0
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_requests = [
            r for r in self.request_counts[source_ip]
            if r['timestamp'] > cutoff_time
        ]
        
        return len(recent_requests)
    
    async def _create_threat_event(
        self,
        threat_type: ThreatType,
        source_ip: str,
        description: str,
        confidence: float,
        target: str = "",
        additional_data: Optional[Dict[str, Any]] = None
    ) -> ThreatEvent:
        """Create and store threat event"""
        event_id = hashlib.md5(
            f"{threat_type.value}{source_ip}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Calculate threat level
        threat_level = self._calculate_threat_level(threat_type, confidence)
        
        # Create indicators
        indicators = [
            ThreatIndicator(
                indicator_type="ip_address",
                value=source_ip,
                confidence=confidence,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                source=ThreatSource.WEB_TRAFFIC
            )
        ]
        
        threat_event = ThreatEvent(
            event_id=event_id,
            threat_type=threat_type,
            threat_level=threat_level,
            source_ip=source_ip,
            target=target,
            description=description,
            indicators=indicators,
            detected_at=datetime.now(),
            confidence_score=confidence,
            metadata=additional_data or {}
        )
        
        # Store threat event
        self.active_threats[event_id] = threat_event
        self.threat_history.append(threat_event)
        
        # Handle threat
        await self._handle_threat_event(threat_event)
        
        return threat_event
    
    def _calculate_threat_level(self, threat_type: ThreatType, confidence: float) -> ThreatLevel:
        """
        Calculate threat level based on type and confidence
        From crawlers/monitors/threat_detector.py
        """
        base_level = ThreatLevel.LOW
        
        # High-risk threat types
        if threat_type in [
            ThreatType.SQL_INJECTION,
            ThreatType.DATA_EXFILTRATION,
            ThreatType.UNAUTHORIZED_ACCESS
        ]:
            base_level = ThreatLevel.HIGH
        elif threat_type in [
            ThreatType.XSS_ATTACK,
            ThreatType.INJECTION_ATTACK,
            ThreatType.API_ABUSE
        ]:
            base_level = ThreatLevel.MEDIUM
        
        # Adjust based on confidence
        if confidence >= 0.9:
            if base_level == ThreatLevel.HIGH:
                return ThreatLevel.CRITICAL
            elif base_level == ThreatLevel.MEDIUM:
                return ThreatLevel.HIGH
        
        return base_level
    
    async def _handle_threat_event(self, threat_event: ThreatEvent):
        """
        Handle detected threat event
        From crawlers/monitors/threat_detector.py
        """
        try:
            # Log threat event
            self.logger.warning(
                f"Threat detected: {threat_event.threat_type.value} "
                f"(Level: {threat_event.threat_level.name}) "
                f"from {threat_event.source_ip}"
            )
            
            # Auto-mitigation based on threat level
            if self.auto_block and threat_event.threat_level.value >= ThreatLevel.HIGH.value:
                await self._block_ip(threat_event.source_ip, threat_event.event_id)
                threat_event.mitigated = True
                threat_event.mitigation_actions.append(f"IP blocked: {threat_event.source_ip}")
            
            # Additional response actions
            await self._respond_to_threat(threat_event)
            
        except Exception as e:
            self.logger.error(f"Failed to handle threat event: {e}")
    
    async def _respond_to_threat(self, threat_event: ThreatEvent):
        """Respond to threat based on type and level"""
        if threat_event.threat_type == ThreatType.DDOS_ATTACK:
            # Implement rate limiting
            await self._implement_rate_limiting(threat_event.source_ip)
            threat_event.mitigation_actions.append("Rate limiting applied")
        
        elif threat_event.threat_type in [ThreatType.SQL_INJECTION, ThreatType.XSS_ATTACK]:
            # Block and alert security team
            await self._alert_security_team(threat_event)
            threat_event.mitigation_actions.append("Security team alerted")
        
        elif threat_event.threat_type == ThreatType.SCRAPING_ABUSE:
            # Apply CAPTCHA challenge
            await self._apply_captcha_challenge(threat_event.source_ip)
            threat_event.mitigation_actions.append("CAPTCHA challenge applied")
    
    async def _block_ip(self, ip_address: str, reason: str):
        """Block IP address"""
        self.blocked_ips.add(ip_address)
        self.logger.info(f"Blocked IP {ip_address} - Reason: {reason}")
    
    async def _implement_rate_limiting(self, ip_address: str):
        """Implement rate limiting for IP"""
        # In production, this would configure actual rate limiting
        self.logger.info(f"Applied rate limiting to {ip_address}")
    
    async def _alert_security_team(self, threat_event: ThreatEvent):
        """Alert security team about threat"""
        # In production, this would send actual alerts
        self.logger.critical(f"SECURITY ALERT: {threat_event.description}")
    
    async def _apply_captcha_challenge(self, ip_address: str):
        """Apply CAPTCHA challenge to IP"""
        # In production, this would configure CAPTCHA
        self.logger.info(f"Applied CAPTCHA challenge to {ip_address}")
    
    async def _cleanup_old_events(self):
        """Clean up old threat events"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Remove old active threats
        old_threats = [
            event_id for event_id, event in self.active_threats.items()
            if event.detected_at < cutoff_time and event.mitigated
        ]
        
        for event_id in old_threats:
            del self.active_threats[event_id]
        
        # Limit history size
        if len(self.threat_history) > 1000:
            self.threat_history = self.threat_history[-800:]  # Keep last 800
    
    async def get_threat_metrics(self) -> SecurityMetrics:
        """Get security monitoring metrics"""
        total_events = len(self.threat_history)
        
        if total_events == 0:
            return SecurityMetrics(
                total_events=0,
                threat_levels={},
                threat_types={},
                source_ips={},
                detection_rate=0.0,
                false_positive_rate=0.0,
                response_time_avg=0.0,
                last_updated=datetime.now()
            )
        
        # Calculate metrics
        threat_levels = {}
        threat_types = {}
        source_ips = {}
        
        for event in self.threat_history:
            # Count by threat level
            level = event.threat_level.name
            threat_levels[level] = threat_levels.get(level, 0) + 1
            
            # Count by threat type
            ttype = event.threat_type.value
            threat_types[ttype] = threat_types.get(ttype, 0) + 1
            
            # Count by source IP
            source_ips[event.source_ip] = source_ips.get(event.source_ip, 0) + 1
        
        # Calculate rates (simplified)
        mitigated_events = sum(1 for e in self.threat_history if e.mitigated)
        detection_rate = mitigated_events / total_events if total_events > 0 else 0
        
        return SecurityMetrics(
            total_events=total_events,
            threat_levels=threat_levels,
            threat_types=threat_types,
            source_ips=source_ips,
            detection_rate=detection_rate,
            false_positive_rate=0.05,  # Simulated
            response_time_avg=2.5,  # Simulated average in seconds
            last_updated=datetime.now()
        )
    
    async def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips
    
    async def unblock_ip(self, ip_address: str) -> bool:
        """Unblock IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            self.logger.info(f"Unblocked IP {ip_address}")
            return True
        return False
    
    async def get_active_threats(self) -> List[ThreatEvent]:
        """Get currently active threats"""
        return list(self.active_threats.values())
    
    async def get_threat_by_id(self, event_id: str) -> Optional[ThreatEvent]:
        """Get threat event by ID"""
        return self.active_threats.get(event_id)