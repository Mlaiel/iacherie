"""Intrusion Prevention System for Events Security

Real-time intrusion detection and prevention for Ainflue platform events.
Automatically blocks malicious activities and protects business-critical operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class IntrusionType(Enum):
    """Types of intrusions detected"""
    BRUTE_FORCE = "brute_force"
    DDoS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    ACCOUNT_TAKEOVER = "account_takeover"
    MALWARE = "malware"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


class PreventionAction(Enum):
    """Prevention actions available"""
    BLOCK_IP = "block_ip"
    BLOCK_USER = "block_user"
    RATE_LIMIT = "rate_limit"
    QUARANTINE = "quarantine"
    CHALLENGE = "challenge"
    LOG_ONLY = "log_only"
    ESCALATE = "escalate"


@dataclass
class IntrusionAttempt:
    """Represents a detected intrusion attempt"""
    attempt_id: str
    intrusion_type: IntrusionType
    severity: str
    source_ip: str
    user_id: Optional[str]
    event_type: str
    event_id: str
    description: str
    evidence: Dict[str, Any]
    detected_at: datetime
    confidence: float
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = {}


@dataclass
class PreventionRule:
    """Prevention rule configuration"""
    rule_id: str
    name: str
    intrusion_types: List[IntrusionType]
    conditions: Dict[str, Any]
    actions: List[PreventionAction]
    enabled: bool = True
    priority: int = 100
    
    def matches_intrusion(self, intrusion: IntrusionAttempt) -> bool:
        """Check if rule matches the intrusion"""
        return intrusion.intrusion_type in self.intrusion_types


@dataclass
class PreventionResponse:
    """Response to an intrusion attempt"""
    attempt_id: str
    actions_taken: List[PreventionAction]
    blocked: bool
    challenge_issued: bool
    escalated: bool
    response_time_ms: float
    details: str


class IntrusionPreventionSystem:
    """
    Real-time intrusion prevention system for Ainflue events.
    Detects and prevents various types of security intrusions.
    """
    
    def __init__(self):
        self.enabled = True
        self.prevention_rules = self._initialize_prevention_rules()
        self.blocked_ips = set()
        self.blocked_users = set()
        self.rate_limits = {}  # ip/user -> {event_type: [timestamps]}
        self.intrusion_history = []
        self.monitoring_patterns = self._initialize_monitoring_patterns()
        self.auto_response_enabled = True
        logger.info("IntrusionPreventionSystem initialized")
    
    async def analyze_event_for_intrusion(self,
                                        event: Any,
                                        source_ip: str,
                                        user_id: Optional[str] = None,
                                        request_context: Dict[str, Any] = None) -> Optional[IntrusionAttempt]:
        """
        Analyze an event for potential intrusion attempts.
        
        Args:
            event: Domain event to analyze
            source_ip: Source IP address
            user_id: User ID if authenticated
            request_context: Additional request context
            
        Returns:
            IntrusionAttempt if intrusion detected, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            event_id = getattr(event, 'event_id', 'unknown')
            event_type = getattr(event, 'event_type', 'unknown')
            event_data = getattr(event, 'data', {})
            request_context = request_context or {}
            
            # Check for various intrusion types
            intrusion_attempts = []
            
            # Brute force detection
            brute_force = await self._detect_brute_force(event_type, source_ip, user_id, request_context)
            if brute_force:
                intrusion_attempts.append(brute_force)
            
            # DDoS detection
            ddos = await self._detect_ddos(event_type, source_ip, request_context)
            if ddos:
                intrusion_attempts.append(ddos)
            
            # Injection attacks
            injection = await self._detect_injection_attacks(event_data, request_context)
            if injection:
                intrusion_attempts.append(injection)
            
            # Privilege escalation
            privilege_escalation = await self._detect_privilege_escalation(event_type, user_id, event_data)
            if privilege_escalation:
                intrusion_attempts.append(privilege_escalation)
            
            # Data exfiltration
            data_exfiltration = await self._detect_data_exfiltration(event_type, event_data, user_id)
            if data_exfiltration:
                intrusion_attempts.append(data_exfiltration)
            
            # Suspicious patterns
            suspicious_pattern = await self._detect_suspicious_patterns(
                event_type, source_ip, user_id, event_data, request_context
            )
            if suspicious_pattern:
                intrusion_attempts.append(suspicious_pattern)
            
            # Return highest severity intrusion
            if intrusion_attempts:
                highest_severity = max(intrusion_attempts, key=lambda x: self._get_severity_score(x.severity))
                highest_severity.event_id = event_id
                highest_severity.event_type = event_type
                return highest_severity
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing event for intrusion: {str(e)}")
            return None
    
    async def prevent_intrusion(self, intrusion: IntrusionAttempt) -> PreventionResponse:
        """
        Take prevention actions against detected intrusion.
        
        Args:
            intrusion: Detected intrusion attempt
            
        Returns:
            PreventionResponse with actions taken
        """
        start_time = datetime.utcnow()
        
        try:
            # Find applicable prevention rules
            applicable_rules = [
                rule for rule in self.prevention_rules.values()
                if rule.enabled and rule.matches_intrusion(intrusion)
            ]
            
            # Sort by priority
            applicable_rules.sort(key=lambda x: x.priority)
            
            actions_taken = []
            blocked = False
            challenge_issued = False
            escalated = False
            
            # Execute prevention actions
            for rule in applicable_rules:
                for action in rule.actions:
                    if await self._execute_prevention_action(action, intrusion):
                        actions_taken.append(action)
                        
                        if action == PreventionAction.BLOCK_IP or action == PreventionAction.BLOCK_USER:
                            blocked = True
                        elif action == PreventionAction.CHALLENGE:
                            challenge_issued = True
                        elif action == PreventionAction.ESCALATE:
                            escalated = True
            
            # Store intrusion in history
            self.intrusion_history.append(intrusion)
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Generate response details
            details = self._generate_response_details(intrusion, actions_taken)
            
            response = PreventionResponse(
                attempt_id=intrusion.attempt_id,
                actions_taken=actions_taken,
                blocked=blocked,
                challenge_issued=challenge_issued,
                escalated=escalated,
                response_time_ms=response_time,
                details=details
            )
            
            logger.info(f"Intrusion prevention response: {response.details}")
            return response
            
        except Exception as e:
            logger.error(f"Error preventing intrusion: {str(e)}")
            return PreventionResponse(
                attempt_id=intrusion.attempt_id,
                actions_taken=[],
                blocked=False,
                challenge_issued=False,
                escalated=True,
                response_time_ms=0.0,
                details=f"Prevention error: {str(e)}"
            )
    
    async def _detect_brute_force(self,
                                event_type: str,
                                source_ip: str,
                                user_id: Optional[str],
                                request_context: Dict[str, Any]) -> Optional[IntrusionAttempt]:
        """Detect brute force attacks"""
        
        # Focus on authentication events
        if not event_type.startswith('user.auth'):
            return None
        
        # Count recent attempts from IP
        ip_attempts = self._count_recent_attempts(source_ip, 'auth_failed', timedelta(minutes=15))
        
        # Count recent attempts for user
        user_attempts = 0
        if user_id:
            user_attempts = self._count_recent_attempts(user_id, 'auth_failed', timedelta(minutes=30))
        
        # Detect brute force
        if ip_attempts > 10 or user_attempts > 5:
            return IntrusionAttempt(
                attempt_id=f"brute_force_{datetime.utcnow().timestamp()}",
                intrusion_type=IntrusionType.BRUTE_FORCE,
                severity="high",
                source_ip=source_ip,
                user_id=user_id,
                event_type=event_type,
                event_id="",
                description=f"Brute force attack detected: {ip_attempts} IP attempts, {user_attempts} user attempts",
                evidence={
                    'ip_attempts': ip_attempts,
                    'user_attempts': user_attempts,
                    'time_window_minutes': 15
                },
                detected_at=datetime.utcnow(),
                confidence=0.95 if ip_attempts > 20 else 0.85
            )
        
        return None
    
    async def _detect_ddos(self,
                         event_type: str,
                         source_ip: str,
                         request_context: Dict[str, Any]) -> Optional[IntrusionAttempt]:
        """Detect DDoS attacks"""
        
        # Count requests from IP in last minute
        recent_requests = self._count_recent_attempts(source_ip, 'request', timedelta(minutes=1))
        
        # Count unique IPs making high-volume requests
        high_volume_ips = self._count_high_volume_ips(timedelta(minutes=5))
        
        # DDoS indicators
        if recent_requests > 100 or (recent_requests > 50 and high_volume_ips > 10):
            return IntrusionAttempt(
                attempt_id=f"ddos_{datetime.utcnow().timestamp()}",
                intrusion_type=IntrusionType.DDoS,
                severity="critical",
                source_ip=source_ip,
                user_id=None,
                event_type=event_type,
                event_id="",
                description=f"DDoS attack detected: {recent_requests} requests/minute from IP",
                evidence={
                    'requests_per_minute': recent_requests,
                    'high_volume_ip_count': high_volume_ips,
                    'threshold_exceeded': recent_requests > 100
                },
                detected_at=datetime.utcnow(),
                confidence=0.90
            )
        
        return None
    
    async def _detect_injection_attacks(self,
                                      event_data: Dict[str, Any],
                                      request_context: Dict[str, Any]) -> Optional[IntrusionAttempt]:
        """Detect SQL injection and XSS attacks"""
        
        # Check for SQL injection patterns
        sql_patterns = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION',
            'OR 1=1', 'AND 1=1', '--', ';--', '/*', '*/'
        ]
        
        # Check for XSS patterns
        xss_patterns = [
            '<script>', '</script>', 'javascript:', 'onload=', 'onerror=',
            'alert(', 'document.cookie', 'eval(', 'expression('
        ]
        
        # Collect all text data to check
        text_data = []
        text_data.extend(str(v) for v in event_data.values() if isinstance(v, (str, int, float)))
        text_data.extend(str(v) for v in request_context.values() if isinstance(v, (str, int, float)))
        
        combined_text = ' '.join(text_data).upper()
        
        # Check for SQL injection
        sql_matches = [pattern for pattern in sql_patterns if pattern.upper() in combined_text]
        if sql_matches:
            return IntrusionAttempt(
                attempt_id=f"sql_injection_{datetime.utcnow().timestamp()}",
                intrusion_type=IntrusionType.SQL_INJECTION,
                severity="critical",
                source_ip=request_context.get('source_ip', 'unknown'),
                user_id=event_data.get('user_id'),
                event_type="",
                event_id="",
                description=f"SQL injection attempt detected: {', '.join(sql_matches)}",
                evidence={
                    'patterns_found': sql_matches,
                    'data_sample': combined_text[:200] + '...' if len(combined_text) > 200 else combined_text
                },
                detected_at=datetime.utcnow(),
                confidence=0.95
            )
        
        # Check for XSS
        xss_matches = [pattern for pattern in xss_patterns if pattern.upper() in combined_text]
        if xss_matches:
            return IntrusionAttempt(
                attempt_id=f"xss_{datetime.utcnow().timestamp()}",
                intrusion_type=IntrusionType.XSS,
                severity="high",
                source_ip=request_context.get('source_ip', 'unknown'),
                user_id=event_data.get('user_id'),
                event_type="",
                event_id="",
                description=f"XSS attempt detected: {', '.join(xss_matches)}",
                evidence={
                    'patterns_found': xss_matches,
                    'data_sample': combined_text[:200] + '...' if len(combined_text) > 200 else combined_text
                },
                detected_at=datetime.utcnow(),
                confidence=0.85
            )
        
        return None
    
    async def _detect_privilege_escalation(self,
                                         event_type: str,
                                         user_id: Optional[str],
                                         event_data: Dict[str, Any]) -> Optional[IntrusionAttempt]:
        """Detect privilege escalation attempts"""
        
        if not user_id:
            return None
        
        # Check for suspicious privilege changes
        privilege_events = ['user.role.change', 'user.permission.grant', 'admin.action']
        
        if any(pattern in event_type for pattern in privilege_events):
            # Check if user is trying to escalate their own privileges
            target_user = event_data.get('target_user_id', event_data.get('user_id'))
            
            if target_user == user_id:
                return IntrusionAttempt(
                    attempt_id=f"privilege_escalation_{datetime.utcnow().timestamp()}",
                    intrusion_type=IntrusionType.PRIVILEGE_ESCALATION,
                    severity="high",
                    source_ip="",
                    user_id=user_id,
                    event_type=event_type,
                    event_id="",
                    description="User attempting to escalate own privileges",
                    evidence={
                        'self_privilege_escalation': True,
                        'event_type': event_type,
                        'target_user': target_user
                    },
                    detected_at=datetime.utcnow(),
                    confidence=0.80
                )
        
        return None
    
    async def _detect_data_exfiltration(self,
                                      event_type: str,
                                      event_data: Dict[str, Any],
                                      user_id: Optional[str]) -> Optional[IntrusionAttempt]:
        """Detect data exfiltration attempts"""
        
        # Focus on data export events
        if not any(pattern in event_type for pattern in ['data.export', 'user.data', 'content.download']):
            return None
        
        # Check for large data requests
        data_size = event_data.get('data_size', 0)
        record_count = event_data.get('record_count', 0)
        
        # Count recent data export attempts
        if user_id:
            recent_exports = self._count_recent_attempts(user_id, 'data_export', timedelta(hours=1))
        else:
            recent_exports = 0
        
        # Suspicious indicators
        if data_size > 100_000_000 or record_count > 10000 or recent_exports > 5:
            return IntrusionAttempt(
                attempt_id=f"data_exfiltration_{datetime.utcnow().timestamp()}",
                intrusion_type=IntrusionType.DATA_EXFILTRATION,
                severity="high",
                source_ip="",
                user_id=user_id,
                event_type=event_type,
                event_id="",
                description=f"Potential data exfiltration: {data_size} bytes, {record_count} records",
                evidence={
                    'data_size': data_size,
                    'record_count': record_count,
                    'recent_exports': recent_exports,
                    'large_data_request': data_size > 100_000_000
                },
                detected_at=datetime.utcnow(),
                confidence=0.75
            )
        
        return None
    
    async def _detect_suspicious_patterns(self,
                                        event_type: str,
                                        source_ip: str,
                                        user_id: Optional[str],
                                        event_data: Dict[str, Any],
                                        request_context: Dict[str, Any]) -> Optional[IntrusionAttempt]:
        """Detect various suspicious activity patterns"""
        
        suspicious_indicators = []
        
        # Unusual time activity
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:
            suspicious_indicators.append("unusual_time")
        
        # Geographic anomaly (simplified)
        user_agent = request_context.get('user_agent', '')
        if 'bot' in user_agent.lower() or 'crawler' in user_agent.lower():
            suspicious_indicators.append("bot_user_agent")
        
        # Rapid sequence of different event types
        if user_id:
            recent_event_types = self._get_recent_event_types(user_id, timedelta(minutes=5))
            if len(recent_event_types) > 10:
                suspicious_indicators.append("rapid_event_diversity")
        
        # Failed events pattern
        if 'failed' in event_data.get('outcome', '').lower():
            recent_failures = self._count_recent_attempts(user_id or source_ip, 'failure', timedelta(minutes=10))
            if recent_failures > 5:
                suspicious_indicators.append("high_failure_rate")
        
        # Multiple session IDs from same IP
        session_count = self._count_unique_sessions(source_ip, timedelta(hours=1))
        if session_count > 10:
            suspicious_indicators.append("multiple_sessions")
        
        # If enough suspicious indicators, create intrusion attempt
        if len(suspicious_indicators) >= 2:
            return IntrusionAttempt(
                attempt_id=f"suspicious_pattern_{datetime.utcnow().timestamp()}",
                intrusion_type=IntrusionType.SUSPICIOUS_PATTERN,
                severity="medium",
                source_ip=source_ip,
                user_id=user_id,
                event_type=event_type,
                event_id="",
                description=f"Suspicious activity pattern: {', '.join(suspicious_indicators)}",
                evidence={
                    'indicators': suspicious_indicators,
                    'indicator_count': len(suspicious_indicators),
                    'current_hour': current_hour,
                    'user_agent': user_agent
                },
                detected_at=datetime.utcnow(),
                confidence=0.60
            )
        
        return None
    
    async def _execute_prevention_action(self,
                                       action: PreventionAction,
                                       intrusion: IntrusionAttempt) -> bool:
        """Execute a specific prevention action"""
        
        try:
            if action == PreventionAction.BLOCK_IP:
                self.blocked_ips.add(intrusion.source_ip)
                logger.warning(f"Blocked IP: {intrusion.source_ip}")
                return True
            
            elif action == PreventionAction.BLOCK_USER and intrusion.user_id:
                self.blocked_users.add(intrusion.user_id)
                logger.warning(f"Blocked user: {intrusion.user_id}")
                return True
            
            elif action == PreventionAction.RATE_LIMIT:
                self._apply_rate_limit(intrusion.source_ip, intrusion.user_id)
                logger.info(f"Applied rate limit: {intrusion.source_ip}")
                return True
            
            elif action == PreventionAction.QUARANTINE:
                # In a real implementation, this would quarantine the event
                logger.info(f"Quarantined event: {intrusion.event_id}")
                return True
            
            elif action == PreventionAction.CHALLENGE:
                # In a real implementation, this would trigger a CAPTCHA or similar
                logger.info(f"Challenge issued for: {intrusion.source_ip}")
                return True
            
            elif action == PreventionAction.LOG_ONLY:
                logger.info(f"Logged intrusion attempt: {intrusion.attempt_id}")
                return True
            
            elif action == PreventionAction.ESCALATE:
                # In a real implementation, this would alert security team
                logger.error(f"SECURITY ESCALATION: {intrusion.description}")
                return True
            
        except Exception as e:
            logger.error(f"Error executing prevention action {action}: {str(e)}")
        
        return False
    
    def _count_recent_attempts(self, identifier: str, event_type: str, time_window: timedelta) -> int:
        """Count recent attempts by identifier within time window"""
        
        # This is a simplified implementation
        # In a real system, this would query a proper storage system
        
        cutoff_time = datetime.utcnow() - time_window
        count = 0
        
        for intrusion in self.intrusion_history:
            if (intrusion.detected_at > cutoff_time and
                (intrusion.source_ip == identifier or intrusion.user_id == identifier)):
                count += 1
        
        # Simulate some baseline activity
        import random
        return count + random.randint(0, 3)
    
    def _count_high_volume_ips(self, time_window: timedelta) -> int:
        """Count IPs with high request volume"""
        
        # Simplified implementation
        return len(self.blocked_ips) + len([
            ip for ip in ['192.168.1.100', '10.0.0.1', '172.16.0.1']
            if ip not in self.blocked_ips
        ])
    
    def _get_recent_event_types(self, user_id: str, time_window: timedelta) -> Set[str]:
        """Get recent event types for user"""
        
        # Simplified implementation
        return {'user.auth', 'content.upload', 'collaboration.request'}
    
    def _count_unique_sessions(self, ip_address: str, time_window: timedelta) -> int:
        """Count unique sessions from IP"""
        
        # Simplified implementation
        return 3 if ip_address in self.blocked_ips else 1
    
    def _apply_rate_limit(self, source_ip: str, user_id: Optional[str]):
        """Apply rate limiting"""
        
        if source_ip not in self.rate_limits:
            self.rate_limits[source_ip] = {}
        
        if user_id and user_id not in self.rate_limits:
            self.rate_limits[user_id] = {}
        
        # Set rate limit timestamps
        now = datetime.utcnow()
        self.rate_limits[source_ip]['limited_until'] = now + timedelta(minutes=15)
        
        if user_id:
            self.rate_limits[user_id]['limited_until'] = now + timedelta(minutes=10)
    
    def _get_severity_score(self, severity: str) -> int:
        """Get numeric score for severity"""
        
        severity_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        return severity_scores.get(severity, 0)
    
    def _generate_response_details(self,
                                 intrusion: IntrusionAttempt,
                                 actions_taken: List[PreventionAction]) -> str:
        """Generate detailed response description"""
        
        details = [
            f"Intrusion Type: {intrusion.intrusion_type.value}",
            f"Severity: {intrusion.severity}",
            f"Source: {intrusion.source_ip}",
            f"Confidence: {intrusion.confidence:.2f}"
        ]
        
        if intrusion.user_id:
            details.append(f"User: {intrusion.user_id}")
        
        if actions_taken:
            action_names = [action.value for action in actions_taken]
            details.append(f"Actions: {', '.join(action_names)}")
        
        return " | ".join(details)
    
    def _initialize_prevention_rules(self) -> Dict[str, PreventionRule]:
        """Initialize prevention rules"""
        
        rules = [
            PreventionRule(
                rule_id="brute_force_block",
                name="Block Brute Force Attacks",
                intrusion_types=[IntrusionType.BRUTE_FORCE],
                conditions={'severity': ['high', 'critical']},
                actions=[PreventionAction.BLOCK_IP, PreventionAction.ESCALATE],
                priority=10
            ),
            PreventionRule(
                rule_id="ddos_rate_limit",
                name="Rate Limit DDoS Attacks",
                intrusion_types=[IntrusionType.DDoS],
                conditions={'severity': ['critical']},
                actions=[PreventionAction.BLOCK_IP, PreventionAction.ESCALATE],
                priority=5
            ),
            PreventionRule(
                rule_id="injection_block",
                name="Block Injection Attacks",
                intrusion_types=[IntrusionType.SQL_INJECTION, IntrusionType.XSS],
                conditions={'severity': ['high', 'critical']},
                actions=[PreventionAction.BLOCK_IP, PreventionAction.QUARANTINE, PreventionAction.ESCALATE],
                priority=1
            ),
            PreventionRule(
                rule_id="privilege_escalation_monitor",
                name="Monitor Privilege Escalation",
                intrusion_types=[IntrusionType.PRIVILEGE_ESCALATION],
                conditions={'severity': ['medium', 'high']},
                actions=[PreventionAction.BLOCK_USER, PreventionAction.ESCALATE],
                priority=15
            ),
            PreventionRule(
                rule_id="data_exfiltration_quarantine",
                name="Quarantine Data Exfiltration",
                intrusion_types=[IntrusionType.DATA_EXFILTRATION],
                conditions={'severity': ['high']},
                actions=[PreventionAction.BLOCK_USER, PreventionAction.QUARANTINE, PreventionAction.ESCALATE],
                priority=20
            ),
            PreventionRule(
                rule_id="suspicious_pattern_challenge",
                name="Challenge Suspicious Patterns",
                intrusion_types=[IntrusionType.SUSPICIOUS_PATTERN],
                conditions={'severity': ['medium']},
                actions=[PreventionAction.CHALLENGE, PreventionAction.RATE_LIMIT],
                priority=50
            )
        ]
        
        return {rule.rule_id: rule for rule in rules}
    
    def _initialize_monitoring_patterns(self) -> Dict[str, Any]:
        """Initialize monitoring patterns"""
        
        return {
            'brute_force': {
                'max_attempts_per_ip': 10,
                'max_attempts_per_user': 5,
                'time_window_minutes': 15
            },
            'ddos': {
                'max_requests_per_minute': 100,
                'max_concurrent_ips': 10
            },
            'data_exfiltration': {
                'max_data_size_bytes': 100_000_000,
                'max_records': 10000,
                'max_exports_per_hour': 5
            }
        }
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        return ip_address in self.blocked_ips
    
    def is_user_blocked(self, user_id: str) -> bool:
        """Check if user is blocked"""
        return user_id in self.blocked_users
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if IP or user is rate limited"""
        
        if identifier not in self.rate_limits:
            return False
        
        limited_until = self.rate_limits[identifier].get('limited_until')
        if limited_until and datetime.utcnow() < limited_until:
            return True
        
        return False
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip_address)
        logger.info(f"Unblocked IP: {ip_address}")
    
    def unblock_user(self, user_id: str):
        """Unblock a user"""
        self.blocked_users.discard(user_id)
        logger.info(f"Unblocked user: {user_id}")
    
    def get_intrusion_statistics(self) -> Dict[str, Any]:
        """Get intrusion detection and prevention statistics"""
        
        if not self.intrusion_history:
            return {
                'total_intrusions': 0,
                'by_type': {},
                'by_severity': {},
                'blocked_ips': len(self.blocked_ips),
                'blocked_users': len(self.blocked_users),
                'recent_intrusions': 0
            }
        
        # Count by type and severity
        by_type = {}
        by_severity = {}
        recent_count = 0
        
        recent_threshold = datetime.utcnow() - timedelta(hours=24)
        
        for intrusion in self.intrusion_history:
            # By type
            intrusion_type = intrusion.intrusion_type.value
            by_type[intrusion_type] = by_type.get(intrusion_type, 0) + 1
            
            # By severity
            severity = intrusion.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Recent intrusions
            if intrusion.detected_at > recent_threshold:
                recent_count += 1
        
        return {
            'total_intrusions': len(self.intrusion_history),
            'by_type': by_type,
            'by_severity': by_severity,
            'blocked_ips': len(self.blocked_ips),
            'blocked_users': len(self.blocked_users),
            'recent_intrusions': recent_count
        }
    
    def enable_prevention(self):
        """Enable intrusion prevention"""
        self.enabled = True
        logger.info("Intrusion prevention enabled")
    
    def disable_prevention(self):
        """Disable intrusion prevention"""
        self.enabled = False
        logger.info("Intrusion prevention disabled")
    
    def enable_auto_response(self):
        """Enable automatic response to intrusions"""
        self.auto_response_enabled = True
        logger.info("Auto-response enabled")
    
    def disable_auto_response(self):
        """Disable automatic response to intrusions"""
        self.auto_response_enabled = False
        logger.info("Auto-response disabled")


# Export for module use
__all__ = ['IntrusionPreventionSystem', 'IntrusionAttempt', 'PreventionResponse', 'IntrusionType', 'PreventionAction']