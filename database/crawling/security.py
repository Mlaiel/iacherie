"""
Enterprise Crawler Security Database Module

Advanced database layer for security monitoring, threat detection,
and protection mechanisms in crawler operations.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against copyright infringement.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + 
                 Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
import hashlib
from enum import Enum
import ipaddress
import re

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    SecurityIncident, ThreatDetection, SecurityAlert,
    BlocklistEntry, SecurityConfig, VulnerabilityAssessment
)
from ..core.exceptions import (
    DatabaseError, SecurityError, ThreatDetectionError,
    AuthenticationError, AuthorizationError
)


class ThreatLevel(Enum):
    """Security threat levels."""
    CRITICAL = "critical"        # Immediate response required
    HIGH = "high"               # Response within 1 hour
    MEDIUM = "medium"           # Response within 4 hours  
    LOW = "low"                 # Response within 24 hours
    INFORMATIONAL = "informational"  # For awareness only


class SecurityEventType(Enum):
    """Types of security events."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    MALICIOUS_CONTENT = "malicious_content"
    PLATFORM_VIOLATION = "platform_violation"
    PROXY_COMPROMISE = "proxy_compromise"
    CREDENTIAL_THEFT = "credential_theft"
    DDOS_ATTACK = "ddos_attack"
    INJECTION_ATTEMPT = "injection_attempt"


class BlocklistType(Enum):
    """Types of blocklist entries."""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    USER_AGENT = "user_agent"
    API_KEY = "api_key"
    CONTENT_HASH = "content_hash"
    FINGERPRINT = "fingerprint"


class SecurityAction(Enum):
    """Security response actions."""
    BLOCK_REQUEST = "block_request"
    THROTTLE_REQUESTS = "throttle_requests"
    REQUIRE_AUTHENTICATION = "require_authentication"
    LOG_AND_MONITOR = "log_and_monitor"
    QUARANTINE_DATA = "quarantine_data"
    ALERT_ADMINISTRATORS = "alert_administrators"
    ESCALATE_INCIDENT = "escalate_incident"
    AUTO_REMEDIATE = "auto_remediate"


class CrawlerSecurityManager(DatabaseManager):
    """
    Enterprise security management system for crawler operations.
    
    Manages:
    - Real-time threat detection and response
    - Security incident tracking and analysis
    - Automated security controls and policies
    - Vulnerability assessment and remediation
    - Access control and authentication
    - Security audit and compliance monitoring
    """
    
    def __init__(self, db_session: Session):
        """Initialize security manager."""
        super().__init__(db_session)
        self.active_threats = {}
        self.security_rules = {}
        self.blocklists = {}
        self._initialize_security_system()
    
    async def detect_security_threat(
        self,
        request_data: Dict[str, Any],
        session_context: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Perform real-time security threat detection on crawler requests.
        
        Args:
            request_data: Data about the crawling request
            session_context: Current session context
            platform: Target platform
            
        Returns:
            Threat detection results with recommended actions
            
        Raises:
            ThreatDetectionError: If threat detection fails
        """
        try:
            threat_analysis = {
                "request_id": request_data.get("request_id", str(uuid4())),
                "timestamp": datetime.utcnow().isoformat(),
                "platform": platform,
                "threat_indicators": [],
                "risk_score": 0.0,
                "threat_level": ThreatLevel.LOW.value,
                "recommended_actions": []
            }
            
            # Analyze multiple threat vectors
            ip_analysis = await self._analyze_ip_reputation(request_data.get("source_ip"))
            threat_analysis["threat_indicators"].extend(ip_analysis["indicators"])
            threat_analysis["risk_score"] += ip_analysis["risk_contribution"]
            
            ua_analysis = await self._analyze_user_agent(request_data.get("user_agent"))
            threat_analysis["threat_indicators"].extend(ua_analysis["indicators"])
            threat_analysis["risk_score"] += ua_analysis["risk_contribution"]
            
            pattern_analysis = await self._analyze_request_patterns(request_data, session_context)
            threat_analysis["threat_indicators"].extend(pattern_analysis["indicators"])
            threat_analysis["risk_score"] += pattern_analysis["risk_contribution"]
            
            content_analysis = await self._analyze_content_threats(request_data)
            threat_analysis["threat_indicators"].extend(content_analysis["indicators"])
            threat_analysis["risk_score"] += content_analysis["risk_contribution"]
            
            # Calculate overall threat level
            threat_analysis["threat_level"] = await self._calculate_threat_level(
                threat_analysis["risk_score"]
            )
            
            # Generate recommended security actions
            threat_analysis["recommended_actions"] = await self._generate_security_actions(
                threat_analysis["threat_level"],
                threat_analysis["threat_indicators"]
            )
            
            # Log threat detection if significant
            if threat_analysis["risk_score"] > 0.3:
                await self._log_threat_detection(threat_analysis)
            
            return threat_analysis
            
        except Exception as e:
            raise ThreatDetectionError(f"Failed to detect security threats: {str(e)}")
    
    async def create_security_incident(
        self,
        incident_type: SecurityEventType,
        threat_level: ThreatLevel,
        incident_data: Dict[str, Any],
        affected_systems: List[str],
        user_id: str
    ) -> str:
        """
        Create and track a security incident.
        
        Args:
            incident_type: Type of security incident
            threat_level: Severity level of the threat
            incident_data: Detailed incident information
            affected_systems: Systems affected by the incident
            user_id: User identifier
            
        Returns:
            Security incident ID
            
        Raises:
            SecurityError: If incident creation fails
        """
        try:
            incident_id = str(uuid4())
            
            # Create security incident record
            incident = SecurityIncident(
                incident_id=incident_id,
                incident_type=incident_type.value,
                threat_level=threat_level.value,
                incident_data=incident_data,
                affected_systems=affected_systems,
                status="open",
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db_session.add(incident)
            await self.db_session.commit()
            
            # Trigger automated response if configured
            await self._trigger_incident_response(incident_id, threat_level, incident_data)
            
            # Send security alerts if required
            if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                await self._send_security_alert(incident_id, threat_level, incident_data)
            
            return incident_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise SecurityError(f"Failed to create security incident: {str(e)}")
    
    async def add_to_blocklist(
        self,
        blocklist_type: BlocklistType,
        value: str,
        reason: str,
        expiry_time: Optional[datetime] = None,
        severity: ThreatLevel = ThreatLevel.MEDIUM
    ) -> str:
        """
        Add an entry to the security blocklist.
        
        Args:
            blocklist_type: Type of blocklist entry
            value: Value to blocklist (IP, domain, etc.)
            reason: Reason for blocklisting
            expiry_time: When the blocklist entry expires
            severity: Severity level of the threat
            
        Returns:
            Blocklist entry ID
        """
        try:
            entry_id = str(uuid4())
            
            # Validate blocklist entry
            await self._validate_blocklist_entry(blocklist_type, value)
            
            # Create blocklist entry
            entry = BlocklistEntry(
                entry_id=entry_id,
                blocklist_type=blocklist_type.value,
                value=value,
                reason=reason,
                severity=severity.value,
                expiry_time=expiry_time,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db_session.add(entry)
            await self.db_session.commit()
            
            # Update active blocklists cache
            await self._update_blocklist_cache(blocklist_type, value, True)
            
            return entry_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise SecurityError(f"Failed to add blocklist entry: {str(e)}")
    
    async def check_blocklist(
        self,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if request data matches any blocklist entries.
        
        Args:
            request_data: Request data to check
            
        Returns:
            Blocklist check results
        """
        try:
            check_results = {
                "is_blocked": False,
                "blocked_items": [],
                "block_reasons": [],
                "recommended_action": SecurityAction.LOG_AND_MONITOR.value,
                "check_timestamp": datetime.utcnow().isoformat()
            }
            
            # Check IP address blocklist
            if "source_ip" in request_data:
                ip_blocked = await self._check_ip_blocklist(request_data["source_ip"])
                if ip_blocked:
                    check_results["is_blocked"] = True
                    check_results["blocked_items"].append(f"IP: {request_data['source_ip']}")
                    check_results["block_reasons"].extend(ip_blocked["reasons"])
            
            # Check domain blocklist
            if "target_domain" in request_data:
                domain_blocked = await self._check_domain_blocklist(request_data["target_domain"])
                if domain_blocked:
                    check_results["is_blocked"] = True
                    check_results["blocked_items"].append(f"Domain: {request_data['target_domain']}")
                    check_results["block_reasons"].extend(domain_blocked["reasons"])
            
            # Check user agent blocklist
            if "user_agent" in request_data:
                ua_blocked = await self._check_user_agent_blocklist(request_data["user_agent"])
                if ua_blocked:
                    check_results["is_blocked"] = True
                    check_results["blocked_items"].append(f"User-Agent: {request_data['user_agent']}")
                    check_results["block_reasons"].extend(ua_blocked["reasons"])
            
            # Determine recommended action
            if check_results["is_blocked"]:
                check_results["recommended_action"] = SecurityAction.BLOCK_REQUEST.value
            
            return check_results
            
        except Exception as e:
            raise SecurityError(f"Failed to check blocklist: {str(e)}")
    
    async def perform_vulnerability_assessment(
        self,
        target_systems: List[str],
        assessment_type: str = "comprehensive"
    ) -> str:
        """
        Perform security vulnerability assessment on crawler infrastructure.
        
        Args:
            target_systems: List of systems to assess
            assessment_type: Type of assessment to perform
            
        Returns:
            Assessment ID for tracking
        """
        try:
            assessment_id = str(uuid4())
            
            # Create vulnerability assessment record
            assessment = VulnerabilityAssessment(
                assessment_id=assessment_id,
                target_systems=target_systems,
                assessment_type=assessment_type,
                status="initiated",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db_session.add(assessment)
            await self.db_session.commit()
            
            # Execute assessment procedures
            assessment_results = await self._execute_vulnerability_assessment(
                assessment_id, target_systems, assessment_type
            )
            
            # Update assessment with results
            assessment.assessment_results = assessment_results
            assessment.status = "completed"
            assessment.completed_at = datetime.utcnow()
            await self.db_session.commit()
            
            # Generate security recommendations
            if assessment_results.get("vulnerabilities"):
                await self._generate_vulnerability_remediation_plan(
                    assessment_id, assessment_results["vulnerabilities"]
                )
            
            return assessment_id
            
        except Exception as e:
            await self.db_session.rollback()
            raise SecurityError(f"Failed to perform vulnerability assessment: {str(e)}")
    
    async def monitor_security_metrics(
        self,
        time_range: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """
        Monitor and analyze security metrics over specified time range.
        
        Args:
            time_range: Time range for metrics analysis
            
        Returns:
            Comprehensive security metrics report
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            metrics = {
                "monitoring_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration_hours": time_range.total_seconds() / 3600
                },
                "threat_statistics": await self._get_threat_statistics(start_time, end_time),
                "incident_summary": await self._get_incident_summary(start_time, end_time),
                "blocklist_activity": await self._get_blocklist_activity(start_time, end_time),
                "security_alerts": await self._get_security_alerts_summary(start_time, end_time),
                "performance_impact": await self._assess_security_performance_impact(),
                "compliance_status": await self._check_security_compliance_status(),
                "recommendations": await self._generate_security_recommendations()
            }
            
            return metrics
            
        except Exception as e:
            raise SecurityError(f"Failed to monitor security metrics: {str(e)}")
    
    async def generate_security_report(
        self,
        report_type: str,
        time_period: timedelta,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive security report.
        
        Args:
            report_type: Type of security report
            time_period: Time period for report
            include_details: Whether to include detailed information
            
        Returns:
            Comprehensive security report
        """
        try:
            report = {
                "report_metadata": {
                    "report_type": report_type,
                    "time_period_start": (datetime.utcnow() - time_period).isoformat(),
                    "time_period_end": datetime.utcnow().isoformat(),
                    "generated_at": datetime.utcnow().isoformat(),
                    "include_details": include_details
                },
                "executive_summary": await self._generate_security_executive_summary(time_period),
                "threat_landscape": await self._analyze_threat_landscape(time_period),
                "incident_analysis": await self._analyze_security_incidents(time_period),
                "vulnerability_status": await self._get_vulnerability_status(),
                "security_controls": await self._assess_security_controls_effectiveness(),
                "compliance_posture": await self._assess_security_compliance_posture()
            }
            
            if include_details:
                report["detailed_incidents"] = await self._get_detailed_incident_reports(time_period)
                report["threat_intelligence"] = await self._get_threat_intelligence_summary(time_period)
                report["remediation_tracking"] = await self._get_remediation_tracking_status()
            
            return report
            
        except Exception as e:
            raise SecurityError(f"Failed to generate security report: {str(e)}")
    
    # Private helper methods
    
    async def _analyze_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Analyze IP address reputation and threat indicators."""
        if not ip_address:
            return {"indicators": [], "risk_contribution": 0.0}
        
        indicators = []
        risk_score = 0.0
        
        # Check if IP is in known malicious ranges
        try:
            ip_obj = ipaddress.ip_address(ip_address)
            
            # Check for private/reserved IP ranges
            if ip_obj.is_private or ip_obj.is_reserved:
                indicators.append("private_or_reserved_ip")
                risk_score += 0.1
            
            # Check against threat intelligence feeds (simulated)
            if await self._check_threat_intelligence_ip(ip_address):
                indicators.append("malicious_ip_detected")
                risk_score += 0.8
                
        except ValueError:
            indicators.append("invalid_ip_format")
            risk_score += 0.3
        
        return {
            "indicators": indicators,
            "risk_contribution": min(risk_score, 1.0)
        }
    
    async def _analyze_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """Analyze user agent string for threat indicators."""
        if not user_agent:
            return {"indicators": [], "risk_contribution": 0.2}
        
        indicators = []
        risk_score = 0.0
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r"bot|crawler|spider|scraper",
            r"curl|wget|python|php",
            r"scan|hack|exploit|attack"
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                indicators.append(f"suspicious_user_agent_pattern: {pattern}")
                risk_score += 0.2
        
        # Check user agent length (very short or very long can be suspicious)
        if len(user_agent) < 10:
            indicators.append("unusually_short_user_agent")
            risk_score += 0.1
        elif len(user_agent) > 500:
            indicators.append("unusually_long_user_agent")
            risk_score += 0.1
        
        return {
            "indicators": indicators,
            "risk_contribution": min(risk_score, 1.0)
        }
    
    async def _analyze_request_patterns(
        self,
        request_data: Dict[str, Any],
        session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze request patterns for anomalous behavior."""
        indicators = []
        risk_score = 0.0
        
        # Check request frequency
        if session_context.get("requests_per_minute", 0) > 100:
            indicators.append("high_request_frequency")
            risk_score += 0.3
        
        # Check for sequential URL patterns
        if self._detect_sequential_crawling_pattern(request_data, session_context):
            indicators.append("sequential_crawling_detected")
            risk_score += 0.2
        
        # Check for distributed crawling patterns
        if self._detect_distributed_crawling_pattern(session_context):
            indicators.append("distributed_crawling_detected")
            risk_score += 0.3
        
        return {
            "indicators": indicators,
            "risk_contribution": min(risk_score, 1.0)
        }
    
    async def _analyze_content_threats(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content for security threats."""
        indicators = []
        risk_score = 0.0
        
        # Check for injection attempts in parameters
        if "parameters" in request_data:
            for param, value in request_data["parameters"].items():
                if isinstance(value, str):
                    if self._detect_injection_attempt(value):
                        indicators.append(f"injection_attempt_in_parameter: {param}")
                        risk_score += 0.6
        
        return {
            "indicators": indicators,
            "risk_contribution": min(risk_score, 1.0)
        }
    
    def _initialize_security_system(self) -> None:
        """Initialize security management system."""
        self.active_threats = {}
        self.security_rules = {}
        self.blocklists = {
            "ip_addresses": set(),
            "domains": set(),
            "user_agents": set()
        }
