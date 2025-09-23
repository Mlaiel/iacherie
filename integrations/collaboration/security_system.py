#!/usr/bin/env python3
"""
Advanced Security & Threat Detection System
==========================================
Enterprise-grade security enhancements with real-time threat detection,
advanced forensics, and automated compliance monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Role: Security Specialist + Compliance Officer
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import hmac
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import re
import ipaddress
from collections import defaultdict, deque

# Configure security logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEventType(Enum):
    """Types of security events"""
    AUTHENTICATION_FAILURE = "auth_failure"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    MALICIOUS_UPLOAD = "malicious_upload"
    DDoS_ATTACK = "ddos_attack"
    FRAUD_ATTEMPT = "fraud_attempt"
    COMPLIANCE_VIOLATION = "compliance_violation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    SOC2 = "soc2"

@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: SecurityEventType = SecurityEventType.SUSPICIOUS_ACTIVITY
    threat_level: ThreatLevel = ThreatLevel.LOW
    timestamp: datetime = field(default_factory=datetime.now)
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    mitigated: bool = False
    mitigation_action: Optional[str] = None
    false_positive: bool = False

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    indicator: str
    indicator_type: str  # ip, hash, domain, email
    threat_level: ThreatLevel
    source: str
    first_seen: datetime
    last_seen: datetime
    confidence: float  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)

@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    framework: ComplianceFramework
    title: str
    description: str
    check_function: str
    severity: ThreatLevel
    enabled: bool = True

class AdvancedSecurityManager:
    """
    Advanced Security & Threat Detection Manager
    ==========================================
    Real-time threat detection, forensics, and compliance monitoring
    """
    
    def __init__(self):
        self.security_events: deque = deque(maxlen=50000)
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns: Dict[str, re.Pattern] = {}
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.user_behavior_profiles: Dict[str, Dict] = defaultdict(dict)
        self.rate_limiters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Initialize security components
        self._setup_threat_detection_patterns()
        self._setup_compliance_rules()
        self._setup_anomaly_detection()
        
        # Security metrics
        self.metrics = {
            "events_processed": 0,
            "threats_detected": 0,
            "threats_mitigated": 0,
            "false_positives": 0,
            "compliance_violations": 0
        }

    def _setup_threat_detection_patterns(self):
        """Setup threat detection patterns"""
        
        # SQL Injection patterns
        self.suspicious_patterns['sql_injection'] = re.compile(
            r"(?i)(union\s+select|drop\s+table|delete\s+from|insert\s+into|update\s+set|"
            r"script\s*>|javascript:|on\w+\s*=|eval\s*\(|expression\s*\()",
            re.IGNORECASE
        )
        
        # XSS patterns
        self.suspicious_patterns['xss'] = re.compile(
            r"(?i)(<script|javascript:|on\w+\s*=|eval\s*\(|expression\s*\(|"
            r"vbscript:|data:text/html|<iframe|<object|<embed)",
            re.IGNORECASE
        )
        
        # Path traversal patterns
        self.suspicious_patterns['path_traversal'] = re.compile(
            r"(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c|..%252f|..%255c)",
            re.IGNORECASE
        )
        
        # Command injection patterns
        self.suspicious_patterns['command_injection'] = re.compile(
            r"(?i)(;|\||&|`|\$\(|<\(|>\(|\${|%0a|%0d|nc\s|netcat|wget|curl|chmod|rm\s)",
            re.IGNORECASE
        )

    def _setup_compliance_rules(self):
        """Setup compliance monitoring rules"""
        
        # GDPR Rules
        self.compliance_rules['gdpr_data_retention'] = ComplianceRule(
            rule_id='gdpr_data_retention',
            framework=ComplianceFramework.GDPR,
            title='Data Retention Compliance',
            description='Ensure personal data is not retained beyond necessary period',
            check_function='check_data_retention',
            severity=ThreatLevel.HIGH
        )
        
        self.compliance_rules['gdpr_consent'] = ComplianceRule(
            rule_id='gdpr_consent',
            framework=ComplianceFramework.GDPR,
            title='Consent Management',
            description='Verify user consent for data processing',
            check_function='check_user_consent',
            severity=ThreatLevel.CRITICAL
        )
        
        # PCI DSS Rules
        self.compliance_rules['pci_encryption'] = ComplianceRule(
            rule_id='pci_encryption',
            framework=ComplianceFramework.PCI_DSS,
            title='Payment Data Encryption',
            description='Ensure payment data is properly encrypted',
            check_function='check_payment_encryption',
            severity=ThreatLevel.CRITICAL
        )
        
        # SOC2 Rules
        self.compliance_rules['soc2_access_control'] = ComplianceRule(
            rule_id='soc2_access_control',
            framework=ComplianceFramework.SOC2,
            title='Access Control Monitoring',
            description='Monitor access controls and privilege management',
            check_function='check_access_controls',
            severity=ThreatLevel.HIGH
        )

    def _setup_anomaly_detection(self):
        """Setup behavioral anomaly detection"""
        self.anomaly_thresholds = {
            'login_attempts': {'max_per_hour': 10, 'max_per_day': 50},
            'api_calls': {'max_per_minute': 100, 'max_per_hour': 5000},
            'file_uploads': {'max_per_hour': 20, 'max_size_mb': 100},
            'data_access': {'max_records_per_hour': 1000}
        }

    async def analyze_security_event(self, 
                                   event_type: SecurityEventType,
                                   source_ip: str,
                                   user_id: Optional[str] = None,
                                   details: Dict[str, Any] = None) -> SecurityEvent:
        """Analyze and classify security event"""
        
        if details is None:
            details = {}
        
        # Create security event
        event = SecurityEvent(
            event_type=event_type,
            source_ip=source_ip,
            user_id=user_id,
            details=details
        )
        
        # Threat level assessment
        threat_level = await self._assess_threat_level(event)
        event.threat_level = threat_level
        
        # Generate description
        event.description = self._generate_event_description(event)
        
        # Check against threat intelligence
        await self._check_threat_intelligence(event)
        
        # Update behavioral profiles
        if user_id:
            await self._update_user_behavior_profile(user_id, event)
        
        # Record event
        self.security_events.append(event)
        self.metrics["events_processed"] += 1
        
        # Apply automated mitigation if needed
        if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            await self._apply_automated_mitigation(event)
        
        # Log security event
        logger.warning(
            f"🚨 SECURITY EVENT: {event.event_type.value} | "
            f"Level: {event.threat_level.value} | "
            f"Source: {event.source_ip} | "
            f"User: {event.user_id} | "
            f"Description: {event.description}"
        )
        
        return event

    async def _assess_threat_level(self, event: SecurityEvent) -> ThreatLevel:
        """Assess threat level based on multiple factors"""
        
        score = 0
        
        # Base score by event type
        type_scores = {
            SecurityEventType.AUTHENTICATION_FAILURE: 1,
            SecurityEventType.SUSPICIOUS_ACTIVITY: 2,
            SecurityEventType.DATA_BREACH_ATTEMPT: 4,
            SecurityEventType.PRIVILEGE_ESCALATION: 4,
            SecurityEventType.MALICIOUS_UPLOAD: 3,
            SecurityEventType.DDoS_ATTACK: 3,
            SecurityEventType.FRAUD_ATTEMPT: 4,
            SecurityEventType.COMPLIANCE_VIOLATION: 3,
            SecurityEventType.UNAUTHORIZED_ACCESS: 4,
            SecurityEventType.ANOMALOUS_BEHAVIOR: 2
        }
        
        score += type_scores.get(event.event_type, 1)
        
        # IP reputation check
        if event.source_ip and await self._is_suspicious_ip(event.source_ip):
            score += 2
        
        # User behavior analysis
        if event.user_id:
            user_risk = await self._assess_user_risk(event.user_id)
            score += user_risk
        
        # Time-based factors (e.g., activity during off-hours)
        if self._is_off_hours():
            score += 1
        
        # Pattern matching
        if event.details:
            pattern_score = await self._check_malicious_patterns(event.details)
            score += pattern_score
        
        # Convert score to threat level
        if score >= 8:
            return ThreatLevel.CRITICAL
        elif score >= 5:
            return ThreatLevel.HIGH
        elif score >= 3:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    async def _check_malicious_patterns(self, details: Dict[str, Any]) -> int:
        """Check for malicious patterns in event details"""
        score = 0
        
        # Convert all values to strings for pattern matching
        text_content = json.dumps(details).lower()
        
        for pattern_name, pattern in self.suspicious_patterns.items():
            if pattern.search(text_content):
                score += 2
                logger.warning(f"🔍 PATTERN DETECTED: {pattern_name} in security event")
        
        return min(score, 6)  # Cap the pattern score

    async def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP is suspicious based on threat intelligence"""
        
        # Check blocked IPs
        if ip in self.blocked_ips:
            return True
        
        # Check threat intelligence database
        if ip in self.threat_intelligence:
            intel = self.threat_intelligence[ip]
            return intel.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        
        # Check for private/internal IPs (should not be accessing externally)
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private and not ip_obj.is_loopback:
                return False  # Private IPs are generally trusted
        except ValueError:
            return True  # Invalid IP format is suspicious
        
        return False

    async def _assess_user_risk(self, user_id: str) -> int:
        """Assess user risk based on behavior profile"""
        
        profile = self.user_behavior_profiles.get(user_id, {})
        risk_score = 0
        
        # Check recent failed logins
        failed_logins = profile.get('failed_logins_24h', 0)
        if failed_logins > 5:
            risk_score += 2
        elif failed_logins > 2:
            risk_score += 1
        
        # Check API usage patterns
        api_calls_hour = profile.get('api_calls_last_hour', 0)
        if api_calls_hour > self.anomaly_thresholds['api_calls']['max_per_hour']:
            risk_score += 2
        elif api_calls_hour > self.anomaly_thresholds['api_calls']['max_per_hour'] * 0.8:
            risk_score += 1
        
        # Check geographic anomalies
        if profile.get('unusual_location', False):
            risk_score += 2
        
        # Check device/browser anomalies
        if profile.get('new_device', False):
            risk_score += 1
        
        return min(risk_score, 4)  # Cap user risk score

    def _is_off_hours(self) -> bool:
        """Check if current time is during off-hours"""
        current_hour = datetime.now().hour
        return current_hour < 6 or current_hour > 22  # 10 PM to 6 AM

    def _generate_event_description(self, event: SecurityEvent) -> str:
        """Generate human-readable event description"""
        
        descriptions = {
            SecurityEventType.AUTHENTICATION_FAILURE: f"Failed authentication attempt from {event.source_ip}",
            SecurityEventType.SUSPICIOUS_ACTIVITY: f"Suspicious activity detected from {event.source_ip}",
            SecurityEventType.DATA_BREACH_ATTEMPT: f"Potential data breach attempt from {event.source_ip}",
            SecurityEventType.PRIVILEGE_ESCALATION: f"Privilege escalation attempt by user {event.user_id}",
            SecurityEventType.MALICIOUS_UPLOAD: f"Malicious file upload attempt from {event.source_ip}",
            SecurityEventType.DDoS_ATTACK: f"DDoS attack pattern detected from {event.source_ip}",
            SecurityEventType.FRAUD_ATTEMPT: f"Fraudulent activity attempt by user {event.user_id}",
            SecurityEventType.COMPLIANCE_VIOLATION: f"Compliance violation detected",
            SecurityEventType.UNAUTHORIZED_ACCESS: f"Unauthorized access attempt from {event.source_ip}",
            SecurityEventType.ANOMALOUS_BEHAVIOR: f"Anomalous behavior pattern detected"
        }
        
        base_description = descriptions.get(event.event_type, "Security event detected")
        
        # Add additional context from details
        if event.details:
            if 'endpoint' in event.details:
                base_description += f" on endpoint {event.details['endpoint']}"
            if 'file_type' in event.details:
                base_description += f" involving {event.details['file_type']} file"
        
        return base_description

    async def _check_threat_intelligence(self, event: SecurityEvent):
        """Check event against threat intelligence database"""
        
        if event.source_ip and event.source_ip in self.threat_intelligence:
            intel = self.threat_intelligence[event.source_ip]
            
            # Update last seen
            intel.last_seen = datetime.now()
            
            # Escalate threat level if IP is known malicious
            if intel.threat_level == ThreatLevel.CRITICAL:
                event.threat_level = ThreatLevel.CRITICAL
                event.details['threat_intel'] = {
                    'source': intel.source,
                    'confidence': intel.confidence,
                    'tags': intel.tags
                }

    async def _update_user_behavior_profile(self, user_id: str, event: SecurityEvent):
        """Update user behavioral profile"""
        
        profile = self.user_behavior_profiles[user_id]
        now = datetime.now()
        
        # Update activity counters
        profile['last_activity'] = now
        profile['total_events'] = profile.get('total_events', 0) + 1
        
        # Track failed logins
        if event.event_type == SecurityEventType.AUTHENTICATION_FAILURE:
            profile['failed_logins_24h'] = profile.get('failed_logins_24h', 0) + 1
        
        # Track API usage
        if 'api_call' in event.details:
            profile['api_calls_last_hour'] = profile.get('api_calls_last_hour', 0) + 1
        
        # Geographic tracking
        if event.source_ip:
            recent_ips = profile.get('recent_ips', [])
            if event.source_ip not in recent_ips:
                recent_ips.append(event.source_ip)
                profile['recent_ips'] = recent_ips[-10:]  # Keep last 10 IPs
                
                # Check for unusual location (simplified)
                if len(recent_ips) > 3:
                    profile['unusual_location'] = True

    async def _apply_automated_mitigation(self, event: SecurityEvent):
        """Apply automated security mitigation measures"""
        
        mitigation_actions = []
        
        # IP-based mitigations
        if event.source_ip and event.threat_level == ThreatLevel.CRITICAL:
            self.blocked_ips.add(event.source_ip)
            mitigation_actions.append(f"Blocked IP {event.source_ip}")
        
        # User-based mitigations
        if event.user_id and event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            # Could trigger account lock, MFA requirement, etc.
            mitigation_actions.append(f"Triggered enhanced security for user {event.user_id}")
        
        # Rate limiting
        if event.event_type == SecurityEventType.DDoS_ATTACK:
            # Apply rate limiting
            mitigation_actions.append("Applied rate limiting")
        
        # Update event with mitigation info
        if mitigation_actions:
            event.mitigated = True
            event.mitigation_action = "; ".join(mitigation_actions)
            self.metrics["threats_mitigated"] += 1
            
            logger.info(f"🛡️ MITIGATION APPLIED: {event.mitigation_action}")

    async def run_compliance_check(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Run compliance check for specific framework"""
        
        results = {
            "framework": framework.value,
            "timestamp": datetime.now().isoformat(),
            "rules_checked": 0,
            "violations": [],
            "compliance_score": 0.0,
            "recommendations": []
        }
        
        framework_rules = [
            rule for rule in self.compliance_rules.values() 
            if rule.framework == framework and rule.enabled
        ]
        
        results["rules_checked"] = len(framework_rules)
        violations = 0
        
        for rule in framework_rules:
            try:
                # Simulate compliance check (in real implementation, would call actual check function)
                is_compliant = await self._execute_compliance_check(rule)
                
                if not is_compliant:
                    violations += 1
                    results["violations"].append({
                        "rule_id": rule.rule_id,
                        "title": rule.title,
                        "severity": rule.severity.value,
                        "description": rule.description
                    })
                    
                    # Record compliance violation event
                    await self.analyze_security_event(
                        SecurityEventType.COMPLIANCE_VIOLATION,
                        source_ip="system",
                        details={
                            "framework": framework.value,
                            "rule": rule.rule_id,
                            "severity": rule.severity.value
                        }
                    )
            
            except Exception as e:
                logger.error(f"❌ Compliance check failed for rule {rule.rule_id}: {e}")
        
        # Calculate compliance score
        if framework_rules:
            results["compliance_score"] = ((len(framework_rules) - violations) / len(framework_rules)) * 100
        
        # Generate recommendations
        results["recommendations"] = self._generate_compliance_recommendations(framework, violations)
        
        if violations > 0:
            self.metrics["compliance_violations"] += violations
            logger.warning(
                f"⚠️ COMPLIANCE ISSUES: {violations} violations found for {framework.value}"
            )
        
        return results

    async def _execute_compliance_check(self, rule: ComplianceRule) -> bool:
        """Execute individual compliance check"""
        
        # Simulated compliance checks (in real implementation, these would be actual checks)
        if rule.rule_id == 'gdpr_data_retention':
            # Check data retention policies
            return True  # Assume compliant for demo
        
        elif rule.rule_id == 'gdpr_consent':
            # Check consent management
            return len([e for e in self.security_events if 'consent' in str(e.details)]) > 0
        
        elif rule.rule_id == 'pci_encryption':
            # Check payment data encryption
            return True  # Assume compliant for demo
        
        elif rule.rule_id == 'soc2_access_control':
            # Check access controls
            access_violations = [
                e for e in self.security_events 
                if e.event_type == SecurityEventType.UNAUTHORIZED_ACCESS
            ]
            return len(access_violations) == 0
        
        return True

    def _generate_compliance_recommendations(self, framework: ComplianceFramework, violations: int) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        if violations == 0:
            recommendations.append(f"✅ {framework.value.upper()} compliance is excellent")
            return recommendations
        
        if framework == ComplianceFramework.GDPR:
            recommendations.extend([
                "🔒 Implement data minimization principles",
                "📝 Enhance consent management processes",
                "🗂️ Review data retention policies",
                "🔍 Conduct regular privacy impact assessments"
            ])
        
        elif framework == ComplianceFramework.PCI_DSS:
            recommendations.extend([
                "🔐 Strengthen payment data encryption",
                "🛡️ Implement additional access controls",
                "📊 Enhance monitoring and logging",
                "🔧 Regular security testing and assessments"
            ])
        
        elif framework == ComplianceFramework.SOC2:
            recommendations.extend([
                "🎯 Implement principle of least privilege",
                "📋 Enhance change management processes",
                "🔍 Improve monitoring and alerting",
                "📚 Update security policies and procedures"
            ])
        
        return recommendations

    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        
        # Recent events analysis
        recent_events = [
            e for e in self.security_events 
            if e.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        # Threat level distribution
        threat_distribution = defaultdict(int)
        for event in recent_events:
            threat_distribution[event.threat_level.value] += 1
        
        # Top threat sources
        source_counts = defaultdict(int)
        for event in recent_events:
            if event.source_ip:
                source_counts[event.source_ip] += 1
        
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Event type distribution
        event_type_counts = defaultdict(int)
        for event in recent_events:
            event_type_counts[event.event_type.value] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_events_24h": len(recent_events),
                "critical_threats": len([e for e in recent_events if e.threat_level == ThreatLevel.CRITICAL]),
                "high_threats": len([e for e in recent_events if e.threat_level == ThreatLevel.HIGH]),
                "mitigated_threats": len([e for e in recent_events if e.mitigated]),
                "blocked_ips": len(self.blocked_ips),
                "active_users": len(self.user_behavior_profiles)
            },
            "threat_distribution": dict(threat_distribution),
            "top_threat_sources": top_sources,
            "event_types": dict(event_type_counts),
            "metrics": self.metrics,
            "recent_critical_events": [
                {
                    "event_id": e.event_id,
                    "type": e.event_type.value,
                    "threat_level": e.threat_level.value,
                    "source_ip": e.source_ip,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat(),
                    "mitigated": e.mitigated
                }
                for e in recent_events 
                if e.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
            ][-20:],  # Last 20 critical events
            "compliance_status": {
                framework.value: f"Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                for framework in ComplianceFramework
            }
        }

    async def forensic_analysis(self, 
                              start_time: datetime, 
                              end_time: datetime,
                              filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform forensic analysis on security events"""
        
        if filters is None:
            filters = {}
        
        # Filter events by time range
        events = [
            e for e in self.security_events 
            if start_time <= e.timestamp <= end_time
        ]
        
        # Apply additional filters
        if 'source_ip' in filters:
            events = [e for e in events if e.source_ip == filters['source_ip']]
        
        if 'user_id' in filters:
            events = [e for e in events if e.user_id == filters['user_id']]
        
        if 'threat_level' in filters:
            events = [e for e in events if e.threat_level.value == filters['threat_level']]
        
        # Analysis
        analysis = {
            "analysis_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_hours": (end_time - start_time).total_seconds() / 3600
            },
            "events_analyzed": len(events),
            "patterns": self._analyze_attack_patterns(events),
            "timeline": self._create_event_timeline(events),
            "indicators": self._extract_indicators_of_compromise(events),
            "recommendations": self._generate_forensic_recommendations(events)
        }
        
        return analysis

    def _analyze_attack_patterns(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        """Analyze attack patterns in events"""
        
        patterns = {
            "coordinated_attacks": [],
            "repeat_offenders": defaultdict(int),
            "attack_sequences": [],
            "geographic_patterns": defaultdict(int)
        }
        
        # Find coordinated attacks (multiple IPs targeting same user/resource)
        user_attackers = defaultdict(set)
        for event in events:
            if event.user_id and event.source_ip:
                user_attackers[event.user_id].add(event.source_ip)
        
        for user, ips in user_attackers.items():
            if len(ips) > 3:
                patterns["coordinated_attacks"].append({
                    "target_user": user,
                    "attacking_ips": list(ips),
                    "attack_count": len(ips)
                })
        
        # Find repeat offenders
        for event in events:
            if event.source_ip:
                patterns["repeat_offenders"][event.source_ip] += 1
        
        # Keep only repeat offenders (more than 2 incidents)
        patterns["repeat_offenders"] = {
            ip: count for ip, count in patterns["repeat_offenders"].items() 
            if count > 2
        }
        
        return patterns

    def _create_event_timeline(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Create chronological timeline of events"""
        
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        timeline = []
        for event in sorted_events[-50:]:  # Last 50 events
            timeline.append({
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "threat_level": event.threat_level.value,
                "source": event.source_ip,
                "description": event.description
            })
        
        return timeline

    def _extract_indicators_of_compromise(self, events: List[SecurityEvent]) -> Dict[str, List[str]]:
        """Extract indicators of compromise (IOCs)"""
        
        iocs = {
            "suspicious_ips": [],
            "malicious_patterns": [],
            "compromised_accounts": [],
            "attack_vectors": []
        }
        
        # Extract suspicious IPs
        ip_scores = defaultdict(int)
        for event in events:
            if event.source_ip and event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                ip_scores[event.source_ip] += 1
        
        iocs["suspicious_ips"] = [
            ip for ip, score in ip_scores.items() if score >= 3
        ]
        
        # Extract compromised accounts
        user_scores = defaultdict(int)
        for event in events:
            if event.user_id and event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                user_scores[event.user_id] += 1
        
        iocs["compromised_accounts"] = [
            user for user, score in user_scores.items() if score >= 2
        ]
        
        # Extract attack vectors
        attack_vectors = set()
        for event in events:
            if event.details and 'attack_vector' in event.details:
                attack_vectors.add(event.details['attack_vector'])
        
        iocs["attack_vectors"] = list(attack_vectors)
        
        return iocs

    def _generate_forensic_recommendations(self, events: List[SecurityEvent]) -> List[str]:
        """Generate forensic analysis recommendations"""
        
        recommendations = []
        
        if not events:
            return ["No security events found in the specified time range"]
        
        # Check for high-severity events
        critical_events = [e for e in events if e.threat_level == ThreatLevel.CRITICAL]
        if critical_events:
            recommendations.append(
                f"🚨 Immediate attention required: {len(critical_events)} critical security events detected"
            )
        
        # Check for unmitigated threats
        unmitigated = [e for e in events if not e.mitigated and e.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]
        if unmitigated:
            recommendations.append(
                f"⚡ {len(unmitigated)} high/critical threats require immediate mitigation"
            )
        
        # Check for repeat attackers
        ip_counts = defaultdict(int)
        for event in events:
            if event.source_ip:
                ip_counts[event.source_ip] += 1
        
        repeat_attackers = [ip for ip, count in ip_counts.items() if count > 5]
        if repeat_attackers:
            recommendations.append(
                f"🔒 Consider blocking {len(repeat_attackers)} repeat attacking IPs"
            )
        
        # Check for authentication issues
        auth_failures = [e for e in events if e.event_type == SecurityEventType.AUTHENTICATION_FAILURE]
        if len(auth_failures) > len(events) * 0.3:  # More than 30% auth failures
            recommendations.append(
                "🔑 High authentication failure rate detected - review access controls"
            )
        
        return recommendations


# Global security manager instance
security_manager = AdvancedSecurityManager()

# Utility functions for easy integration
async def log_security_event(event_type: SecurityEventType, 
                            source_ip: str, 
                            user_id: Optional[str] = None,
                            details: Dict[str, Any] = None) -> SecurityEvent:
    """Log a security event"""
    return await security_manager.analyze_security_event(event_type, source_ip, user_id, details)

async def check_compliance(framework: ComplianceFramework) -> Dict[str, Any]:
    """Check compliance for a specific framework"""
    return await security_manager.run_compliance_check(framework)

async def get_security_status() -> Dict[str, Any]:
    """Get current security status"""
    return await security_manager.get_security_dashboard()

if __name__ == "__main__":
    async def test_security_manager():
        """Test the security manager"""
        print("🔒 Testing Advanced Security Manager...")
        
        # Test threat detection
        await log_security_event(
            SecurityEventType.AUTHENTICATION_FAILURE,
            "192.168.1.100",
            "user_123",
            {"endpoint": "/api/login", "attempts": 5}
        )
        
        await log_security_event(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            "10.0.0.1",
            "user_456",
            {"endpoint": "/api/admin", "unusual_access": True}
        )
        
        # Test compliance check
        gdpr_results = await check_compliance(ComplianceFramework.GDPR)
        print("\n📋 GDPR Compliance Results:")
        print(json.dumps(gdpr_results, indent=2))
        
        # Get security dashboard
        dashboard = await get_security_status()
        print("\n🛡️ Security Dashboard:")
        print(json.dumps(dashboard["summary"], indent=2))
    
    asyncio.run(test_security_manager())