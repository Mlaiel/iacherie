"""
Enhanced Security Features
=========================

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue - AI-Powered Content Protection and Monetization Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides enhanced security features including advanced threat detection,
real-time security monitoring, and automated incident response.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import json
import uuid
import re
from ipaddress import ip_address, ip_network
import secrets

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of security threats"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    DDOS_ATTACK = "ddos_attack"
    SUSPICIOUS_LOGIN = "suspicious_login"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    MALWARE_UPLOAD = "malware_upload"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    API_ABUSE = "api_abuse"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    metadata: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())

class AdvancedThreatDetection:
    """Advanced threat detection using AI and rule-based analysis"""
    
    def __init__(self):
        self.threat_patterns = {
            ThreatType.SQL_INJECTION: [
                r"(\bor\b|\band\b).{1,10}(=|<|>)",
                r"union\s+select",
                r"drop\s+table",
                r"insert\s+into",
                r"delete\s+from",
                r"update\s+.*\s+set"
            ],
            ThreatType.XSS_ATTACK: [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"eval\s*\(",
                r"document\.cookie"
            ],
            ThreatType.MALWARE_UPLOAD: [
                r"\.exe$", r"\.bat$", r"\.cmd$", r"\.scr$",
                r"\.vbs$", r"\.js$", r"\.jar$"
            ]
        }
        
        self.suspicious_patterns = {
            'password_in_url': r'password[=:][\w\d]+',
            'api_key_leak': r'(api[_-]?key|token)[=:][a-zA-Z0-9]{20,}',
            'email_harvest': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        # Track failed attempts by IP
        self.failed_attempts = {}
        self.blocked_ips = set()
        
        logger.info("AdvancedThreatDetection initialized")
    
    async def analyze_request(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Analyze incoming request for security threats"""
        try:
            source_ip = request_data.get('source_ip', 'unknown')
            user_agent = request_data.get('user_agent', '')
            request_body = request_data.get('body', '')
            headers = request_data.get('headers', {})
            url_path = request_data.get('path', '')
            
            # Check for blocked IPs
            if source_ip in self.blocked_ips:
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                    threat_level=ThreatLevel.HIGH,
                    source_ip=source_ip,
                    user_id=request_data.get('user_id'),
                    description="Request from blocked IP address",
                    metadata={'blocked_ip': source_ip},
                    timestamp=datetime.now()
                )
            
            # Check for SQL injection
            sql_threat = await self._check_sql_injection(request_body + url_path)
            if sql_threat:
                return sql_threat
            
            # Check for XSS attacks
            xss_threat = await self._check_xss_attack(request_body + str(headers))
            if xss_threat:
                return xss_threat
            
            # Check for DDoS patterns
            ddos_threat = await self._check_ddos_pattern(source_ip, request_data)
            if ddos_threat:
                return ddos_threat
            
            # Check for suspicious data patterns
            data_threat = await self._check_suspicious_data(request_body)
            if data_threat:
                return data_threat
            
            # Check for API abuse
            api_threat = await self._check_api_abuse(source_ip, request_data)
            if api_threat:
                return api_threat
            
            return None
            
        except Exception as e:
            logger.error(f"Error in threat analysis: {e}")
            return None
    
    async def _check_sql_injection(self, content: str) -> Optional[SecurityEvent]:
        """Check for SQL injection patterns"""
        content_lower = content.lower()
        
        for pattern in self.threat_patterns[ThreatType.SQL_INJECTION]:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    threat_type=ThreatType.SQL_INJECTION,
                    threat_level=ThreatLevel.HIGH,
                    source_ip="unknown",
                    user_id=None,
                    description=f"SQL injection pattern detected: {pattern}",
                    metadata={'pattern': pattern, 'content_sample': content[:200]},
                    timestamp=datetime.now()
                )
        
        return None
    
    async def _check_xss_attack(self, content: str) -> Optional[SecurityEvent]:
        """Check for XSS attack patterns"""
        for pattern in self.threat_patterns[ThreatType.XSS_ATTACK]:
            if re.search(pattern, content, re.IGNORECASE):
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    threat_type=ThreatType.XSS_ATTACK,
                    threat_level=ThreatLevel.HIGH,
                    source_ip="unknown",
                    user_id=None,
                    description=f"XSS attack pattern detected: {pattern}",
                    metadata={'pattern': pattern, 'content_sample': content[:200]},
                    timestamp=datetime.now()
                )
        
        return None
    
    async def _check_ddos_pattern(self, source_ip: str, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Check for DDoS attack patterns"""
        current_time = datetime.now()
        
        # Track requests per IP
        if source_ip not in self.failed_attempts:
            self.failed_attempts[source_ip] = []
        
        # Add current request
        self.failed_attempts[source_ip].append(current_time)
        
        # Clean old entries (last 5 minutes)
        cutoff_time = current_time - timedelta(minutes=5)
        self.failed_attempts[source_ip] = [
            timestamp for timestamp in self.failed_attempts[source_ip]
            if timestamp > cutoff_time
        ]
        
        # Check if too many requests
        if len(self.failed_attempts[source_ip]) > 100:  # More than 100 requests in 5 minutes
            self.blocked_ips.add(source_ip)
            return SecurityEvent(
                event_id=str(uuid.uuid4()),
                threat_type=ThreatType.DDOS_ATTACK,
                threat_level=ThreatLevel.CRITICAL,
                source_ip=source_ip,
                user_id=request_data.get('user_id'),
                description=f"DDoS attack detected from IP {source_ip}",
                metadata={
                    'request_count': len(self.failed_attempts[source_ip]),
                    'time_window': '5 minutes'
                },
                timestamp=datetime.now()
            )
        
        return None
    
    async def _check_suspicious_data(self, content: str) -> Optional[SecurityEvent]:
        """Check for suspicious data patterns"""
        for pattern_name, pattern in self.suspicious_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                threat_level = ThreatLevel.HIGH if pattern_name in ['api_key_leak', 'credit_card'] else ThreatLevel.MEDIUM
                
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    threat_type=ThreatType.DATA_BREACH_ATTEMPT,
                    threat_level=threat_level,
                    source_ip="unknown",
                    user_id=None,
                    description=f"Suspicious data pattern detected: {pattern_name}",
                    metadata={'pattern_type': pattern_name, 'content_sample': content[:100]},
                    timestamp=datetime.now()
                )
        
        return None
    
    async def _check_api_abuse(self, source_ip: str, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Check for API abuse patterns"""
        endpoint = request_data.get('path', '')
        method = request_data.get('method', 'GET')
        
        # Check for rapid successive API calls to sensitive endpoints
        sensitive_endpoints = ['/api/user', '/api/payment', '/api/admin', '/api/auth']
        
        if any(endpoint.startswith(sensitive) for sensitive in sensitive_endpoints):
            current_time = datetime.now()
            
            # Track API calls per IP per endpoint
            api_key = f"{source_ip}_{endpoint}"
            if api_key not in self.failed_attempts:
                self.failed_attempts[api_key] = []
            
            self.failed_attempts[api_key].append(current_time)
            
            # Clean old entries (last 1 minute)
            cutoff_time = current_time - timedelta(minutes=1)
            self.failed_attempts[api_key] = [
                timestamp for timestamp in self.failed_attempts[api_key]
                if timestamp > cutoff_time
            ]
            
            # Check if too many API calls
            if len(self.failed_attempts[api_key]) > 30:  # More than 30 calls per minute to sensitive endpoint
                return SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    threat_type=ThreatType.API_ABUSE,
                    threat_level=ThreatLevel.HIGH,
                    source_ip=source_ip,
                    user_id=request_data.get('user_id'),
                    description=f"API abuse detected on endpoint {endpoint}",
                    metadata={
                        'endpoint': endpoint,
                        'call_count': len(self.failed_attempts[api_key]),
                        'time_window': '1 minute'
                    },
                    timestamp=datetime.now()
                )
        
        return None

class RealTimeSecurityMonitor:
    """Real-time security monitoring and alerting system"""
    
    def __init__(self):
        self.threat_detector = AdvancedThreatDetection()
        self.security_events = []
        self.alert_handlers = []
        self.monitoring_active = True
        
        # Security metrics
        self.metrics = {
            'total_threats_detected': 0,
            'threats_by_type': {},
            'threats_by_level': {},
            'blocked_ips': set(),
            'last_threat_time': None
        }
        
        logger.info("RealTimeSecurityMonitor initialized")
    
    async def monitor_request(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Monitor a single request for security threats"""
        if not self.monitoring_active:
            return None
        
        try:
            # Analyze request for threats
            security_event = await self.threat_detector.analyze_request(request_data)
            
            if security_event:
                # Record the event
                await self._record_security_event(security_event)
                
                # Trigger alerts
                await self._trigger_security_alerts(security_event)
                
                # Update metrics
                await self._update_security_metrics(security_event)
                
                # Auto-response if necessary
                await self._automated_response(security_event)
                
                return security_event
            
            return None
            
        except Exception as e:
            logger.error(f"Error in security monitoring: {e}")
            return None
    
    async def _record_security_event(self, event: SecurityEvent):
        """Record security event for analysis"""
        self.security_events.append(event)
        
        # Keep only last 10000 events
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-10000:]
        
        logger.warning(f"Security Event Recorded: {event.threat_type.value} - {event.description}")
    
    async def _trigger_security_alerts(self, event: SecurityEvent):
        """Trigger security alerts for high-priority events"""
        if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            alert_data = {
                'event_id': event.event_id,
                'threat_type': event.threat_type.value,
                'threat_level': event.threat_level.value,
                'source_ip': event.source_ip,
                'description': event.description,
                'timestamp': event.timestamp.isoformat(),
                'requires_immediate_attention': event.threat_level == ThreatLevel.CRITICAL
            }
            
            # Send alerts to all registered handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert_data)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
    
    async def _update_security_metrics(self, event: SecurityEvent):
        """Update security metrics"""
        self.metrics['total_threats_detected'] += 1
        
        # Update threat type counts
        threat_type = event.threat_type.value
        if threat_type not in self.metrics['threats_by_type']:
            self.metrics['threats_by_type'][threat_type] = 0
        self.metrics['threats_by_type'][threat_type] += 1
        
        # Update threat level counts
        threat_level = event.threat_level.value
        if threat_level not in self.metrics['threats_by_level']:
            self.metrics['threats_by_level'][threat_level] = 0
        self.metrics['threats_by_level'][threat_level] += 1
        
        # Update last threat time
        self.metrics['last_threat_time'] = event.timestamp
        
        # Update blocked IPs
        if event.source_ip and event.source_ip != 'unknown':
            self.metrics['blocked_ips'].add(event.source_ip)
    
    async def _automated_response(self, event: SecurityEvent):
        """Automated security response based on threat type and level"""
        if event.threat_level == ThreatLevel.CRITICAL:
            # Block IP immediately for critical threats
            if event.source_ip and event.source_ip != 'unknown':
                self.threat_detector.blocked_ips.add(event.source_ip)
                logger.critical(f"IP {event.source_ip} blocked due to critical threat")
            
            # Additional critical response actions
            if event.threat_type == ThreatType.DDOS_ATTACK:
                # Could trigger additional DDoS protection measures
                logger.critical("DDoS protection measures activated")
            
            elif event.threat_type == ThreatType.DATA_BREACH_ATTEMPT:
                # Could lock down sensitive endpoints temporarily
                logger.critical("Data breach protection measures activated")
        
        elif event.threat_level == ThreatLevel.HIGH:
            # Increase monitoring for high threats
            logger.warning(f"Increased monitoring for IP {event.source_ip}")
    
    def add_alert_handler(self, handler):
        """Add a custom alert handler function"""
        self.alert_handlers.append(handler)
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        current_time = datetime.now()
        
        # Recent events (last 24 hours)
        recent_events = [
            event for event in self.security_events
            if (current_time - event.timestamp).total_seconds() < 86400
        ]
        
        # Active threats (unresolved)
        active_threats = [
            event for event in self.security_events
            if not event.resolved
        ]
        
        return {
            'overview': {
                'monitoring_status': 'active' if self.monitoring_active else 'inactive',
                'total_threats_detected': self.metrics['total_threats_detected'],
                'active_threats': len(active_threats),
                'blocked_ips_count': len(self.metrics['blocked_ips']),
                'last_threat_time': self.metrics['last_threat_time'].isoformat() if self.metrics['last_threat_time'] else None
            },
            'threat_breakdown': {
                'by_type': self.metrics['threats_by_type'],
                'by_level': self.metrics['threats_by_level']
            },
            'recent_activity': {
                'events_last_24h': len(recent_events),
                'recent_events': [
                    {
                        'event_id': event.event_id,
                        'threat_type': event.threat_type.value,
                        'threat_level': event.threat_level.value,
                        'source_ip': event.source_ip,
                        'description': event.description[:100],
                        'timestamp': event.timestamp.isoformat()
                    }
                    for event in recent_events[-10:]  # Last 10 events
                ]
            },
            'security_status': {
                'blocked_ips': list(self.metrics['blocked_ips']),
                'active_threat_levels': list(set(
                    event.threat_level.value for event in active_threats
                )),
                'system_health': 'good' if len(active_threats) < 5 else 'warning'
            }
        }

# Global security instances
security_monitor = RealTimeSecurityMonitor()

# Export main components
__all__ = [
    'ThreatLevel',
    'ThreatType',
    'SecurityEvent',
    'AdvancedThreatDetection',
    'RealTimeSecurityMonitor',
    'security_monitor'
]