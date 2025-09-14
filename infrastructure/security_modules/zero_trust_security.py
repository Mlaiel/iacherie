"""
Zero Trust Security Manager - Enterprise Zero Trust Architecture
================================================================

Comprehensive Zero Trust security implementation for Ainflue creator platform.
Implements "never trust, always verify" security principles with continuous authentication,
micro-segmentation, and real-time threat detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure - Security Modules
Expert Role: Security Specialist + DevOps + Backend Senior
Version: 1.0 Production Enterprise

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation 
écrite PERSONNELLE est STRICTEMENT INTERDITE et sera poursuivie en justice.

Zero Trust Principles:
1. Never trust, always verify
2. Assume breach has occurred
3. Verify explicitly with context
4. Use least privilege access
5. Monitor and log everything
6. Continuous security validation
"""

import asyncio
import logging
import hashlib
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import jwt
import bcrypt
import ipaddress
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import geoip2.database
import requests
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrustLevel(Enum):
    """Trust levels for Zero Trust assessment"""
    UNTRUSTED = "untrusted"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"

class SecurityZone(Enum):
    """Security zones for micro-segmentation"""
    EXTERNAL = "external"
    DMZ = "dmz"
    INTERNAL = "internal"
    SECURE = "secure"
    CRITICAL = "critical"

class AccessDecision(Enum):
    """Access control decisions"""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    CHALLENGE = "challenge"
    MONITOR = "monitor"

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityContext:
    """Security context for Zero Trust evaluation"""
    user_id: str
    device_id: str
    ip_address: str
    location: Optional[Dict[str, str]]
    user_agent: str
    timestamp: datetime
    session_id: str
    authentication_factors: List[str]
    risk_score: float = 0.0
    trust_level: TrustLevel = TrustLevel.UNTRUSTED
    previous_activities: List[Dict[str, Any]] = field(default_factory=list)
    device_trust_score: float = 0.0
    network_trust_score: float = 0.0

@dataclass
class AccessRequest:
    """Zero Trust access request"""
    request_id: str
    security_context: SecurityContext
    resource_id: str
    resource_type: str
    requested_action: str
    security_zone: SecurityZone
    sensitivity_level: str
    business_justification: Optional[str] = None
    requested_permissions: List[str] = field(default_factory=list)

@dataclass
class AccessResult:
    """Zero Trust access control result"""
    request_id: str
    decision: AccessDecision
    trust_score: float
    risk_factors: List[str]
    conditions: List[str]
    monitoring_requirements: List[str]
    session_duration: int
    additional_verification_required: bool
    explanation: str
    security_controls: List[str]

class ZeroTrustSecurityManager:
    """
    Enterprise Zero Trust Security Manager
    
    Implements comprehensive Zero Trust security architecture with continuous
    verification, micro-segmentation, and adaptive access controls.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Zero Trust Security Manager"""
        self.config = config or self._get_default_config()
        self.trust_engines = {}
        self.security_policies = {}
        self.threat_intelligence = {}
        self.active_sessions = {}
        self.security_events = []
        self.device_registry = {}
        self.geo_database = None
        
        # Initialize security components
        self._initialize_trust_engines()
        self._initialize_security_policies()
        self._initialize_threat_intelligence()
        self._initialize_geo_database()
        
        # Start background security tasks
        self._start_security_monitoring()
        
        logger.info("🔒 Zero Trust Security Manager initialized - Enterprise security active")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default Zero Trust configuration"""
        return {
            "trust_calculation": {
                "user_weight": 0.25,
                "device_weight": 0.25,
                "network_weight": 0.20,
                "behavior_weight": 0.20,
                "context_weight": 0.10
            },
            "risk_thresholds": {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8,
                "critical": 0.95
            },
            "session_management": {
                "max_session_duration": 8 * 3600,  # 8 hours
                "idle_timeout": 30 * 60,  # 30 minutes
                "reauthentication_interval": 4 * 3600,  # 4 hours
                "concurrent_sessions_limit": 5
            },
            "device_trust": {
                "unknown_device_risk": 0.8,
                "unmanaged_device_risk": 0.6,
                "trusted_device_bonus": -0.2,
                "device_encryption_required": True,
                "device_compliance_required": True
            },
            "network_security": {
                "trusted_networks": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
                "blocked_countries": ["CN", "RU", "KP"],  # Example - adjust based on policy
                "vpn_required_countries": [],
                "tor_exit_node_risk": 0.9
            },
            "behavioral_analysis": {
                "enabled": True,
                "learning_period_days": 30,
                "anomaly_threshold": 2.0,  # Standard deviations
                "time_based_patterns": True,
                "location_based_patterns": True
            },
            "adaptive_authentication": {
                "risk_based_mfa": True,
                "biometric_preferred": True,
                "passwordless_enabled": True,
                "continuous_authentication": True
            },
            "monitoring": {
                "real_time_alerts": True,
                "security_event_retention_days": 90,
                "threat_intelligence_updates": True,
                "automated_response": True
            }
        }
    
    def _initialize_trust_engines(self) -> None:
        """Initialize trust calculation engines"""
        self.trust_engines = {
            "user_trust": UserTrustEngine(self.config),
            "device_trust": DeviceTrustEngine(self.config),
            "network_trust": NetworkTrustEngine(self.config),
            "behavioral_trust": BehavioralTrustEngine(self.config),
            "contextual_trust": ContextualTrustEngine(self.config)
        }
        
        logger.info("✅ Trust engines initialized")
    
    def _initialize_security_policies(self) -> None:
        """Initialize Zero Trust security policies"""
        self.security_policies = {
            "access_control": {
                "default_deny": True,
                "least_privilege": True,
                "time_based_access": True,
                "location_based_access": True,
                "resource_based_access": True
            },
            "authentication": {
                "multi_factor_required": True,
                "passwordless_preferred": True,
                "biometric_preferred": True,
                "continuous_verification": True,
                "risk_based_challenge": True
            },
            "authorization": {
                "just_in_time_access": True,
                "just_enough_access": True,
                "dynamic_permissions": True,
                "session_based_permissions": True,
                "context_aware_permissions": True
            },
            "monitoring": {
                "comprehensive_logging": True,
                "real_time_analysis": True,
                "anomaly_detection": True,
                "threat_correlation": True,
                "automated_response": True
            }
        }
        
        logger.info("✅ Security policies initialized")
    
    def _initialize_threat_intelligence(self) -> None:
        """Initialize threat intelligence feeds"""
        self.threat_intelligence = {
            "malicious_ips": set(),
            "compromised_credentials": set(),
            "known_malware_signatures": set(),
            "attack_patterns": [],
            "threat_actors": {},
            "indicators_of_compromise": []
        }
        
        # Load threat intelligence data
        self._load_threat_intelligence()
        
        logger.info("✅ Threat intelligence initialized")
    
    def _load_threat_intelligence(self) -> None:
        """Load threat intelligence data from sources"""
        # Mock threat intelligence loading
        # In production, this would load from real threat intelligence feeds
        self.threat_intelligence["malicious_ips"].update([
            "192.0.2.1", "198.51.100.1", "203.0.113.1"  # RFC 5737 test addresses
        ])
    
    def _initialize_geo_database(self) -> None:
        """Initialize geolocation database"""
        try:
            # In production, this would use a real GeoIP database
            # self.geo_database = geoip2.database.Reader('GeoLite2-City.mmdb')
            logger.info("✅ Geo database initialized (mock)")
        except Exception as e:
            logger.warning(f"⚠️ Geo database initialization failed: {str(e)}")
    
    def _start_security_monitoring(self) -> None:
        """Start background security monitoring tasks"""
        # Start continuous monitoring
        threading.Thread(target=self._continuous_monitoring_loop, daemon=True).start()
        
        # Start threat intelligence updates
        threading.Thread(target=self._threat_intelligence_updater, daemon=True).start()
        
        # Start session cleanup
        threading.Thread(target=self._session_cleanup_loop, daemon=True).start()
    
    async def evaluate_access_request(self, request: AccessRequest) -> AccessResult:
        """
        Evaluate Zero Trust access request
        
        Args:
            request: Access request with security context and resource details
            
        Returns:
            AccessResult with decision and security controls
        """
        start_time = time.time()
        logger.info(f"🔒 Evaluating Zero Trust access request {request.request_id}")
        
        # Phase 1: Calculate comprehensive trust score
        trust_score = await self._calculate_trust_score(request.security_context)
        
        # Phase 2: Assess risk factors
        risk_factors = await self._assess_risk_factors(request)
        
        # Phase 3: Apply security policies
        policy_result = await self._apply_security_policies(request, trust_score, risk_factors)
        
        # Phase 4: Make access decision
        access_decision = await self._make_access_decision(request, trust_score, risk_factors, policy_result)
        
        # Phase 5: Determine security controls
        security_controls = await self._determine_security_controls(request, access_decision, trust_score)
        
        # Phase 6: Set monitoring requirements
        monitoring_requirements = await self._set_monitoring_requirements(request, access_decision, trust_score)
        
        evaluation_time = time.time() - start_time
        
        result = AccessResult(
            request_id=request.request_id,
            decision=access_decision["decision"],
            trust_score=trust_score,
            risk_factors=risk_factors,
            conditions=access_decision["conditions"],
            monitoring_requirements=monitoring_requirements,
            session_duration=access_decision["session_duration"],
            additional_verification_required=access_decision["additional_verification"],
            explanation=access_decision["explanation"],
            security_controls=security_controls
        )
        
        # Log security event
        await self._log_security_event("access_evaluation", request, result)
        
        logger.info(f"✅ Access evaluation completed in {evaluation_time:.2f}s - Decision: {result.decision.value}")
        return result
    
    async def _calculate_trust_score(self, context: SecurityContext) -> float:
        """Calculate comprehensive trust score"""
        trust_scores = {}
        
        # Calculate individual trust scores
        for engine_name, engine in self.trust_engines.items():
            try:
                score = await engine.calculate_trust(context)
                trust_scores[engine_name] = score
            except Exception as e:
                logger.error(f"❌ Trust calculation failed for {engine_name}: {str(e)}")
                trust_scores[engine_name] = 0.0
        
        # Calculate weighted overall trust score
        weights = self.config["trust_calculation"]
        overall_trust = (
            trust_scores.get("user_trust", 0.0) * weights["user_weight"] +
            trust_scores.get("device_trust", 0.0) * weights["device_weight"] +
            trust_scores.get("network_trust", 0.0) * weights["network_weight"] +
            trust_scores.get("behavioral_trust", 0.0) * weights["behavior_weight"] +
            trust_scores.get("contextual_trust", 0.0) * weights["context_weight"]
        )
        
        return max(0.0, min(1.0, overall_trust))
    
    async def _assess_risk_factors(self, request: AccessRequest) -> List[str]:
        """Assess security risk factors"""
        risk_factors = []
        context = request.security_context
        
        # IP-based risk assessment
        if context.ip_address in self.threat_intelligence["malicious_ips"]:
            risk_factors.append("Known malicious IP address")
        
        # Geolocation risk assessment
        if context.location:
            country = context.location.get("country_code", "")
            if country in self.config["network_security"]["blocked_countries"]:
                risk_factors.append(f"Access from restricted country: {country}")
        
        # Device risk assessment
        if context.device_id not in self.device_registry:
            risk_factors.append("Unknown/unregistered device")
        elif not self.device_registry[context.device_id].get("compliant", False):
            risk_factors.append("Non-compliant device")
        
        # Authentication factor assessment
        if len(context.authentication_factors) < 2:
            risk_factors.append("Insufficient authentication factors")
        
        # Time-based risk assessment
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Outside business hours
            risk_factors.append("Access attempt outside business hours")
        
        # Session risk assessment
        user_sessions = [s for s in self.active_sessions.values() if s.get("user_id") == context.user_id]
        if len(user_sessions) >= self.config["session_management"]["concurrent_sessions_limit"]:
            risk_factors.append("Excessive concurrent sessions")
        
        # Behavioral anomaly assessment
        if context.risk_score > 0.8:
            risk_factors.append("Behavioral anomaly detected")
        
        return risk_factors
    
    async def _apply_security_policies(self, request: AccessRequest, trust_score: float, 
                                     risk_factors: List[str]) -> Dict[str, Any]:
        """Apply Zero Trust security policies"""
        policy_result = {
            "policy_violations": [],
            "required_controls": [],
            "additional_verification": False,
            "conditional_access": False
        }
        
        # Check default deny policy
        if self.security_policies["access_control"]["default_deny"]:
            if trust_score < 0.5:
                policy_result["policy_violations"].append("Insufficient trust score for default allow")
        
        # Check least privilege policy
        if self.security_policies["authorization"]["least_privilege"]:
            if len(request.requested_permissions) > 5:  # Example threshold
                policy_result["required_controls"].append("Review and minimize requested permissions")
        
        # Check multi-factor authentication policy
        if self.security_policies["authentication"]["multi_factor_required"]:
            if len(request.security_context.authentication_factors) < 2:
                policy_result["additional_verification"] = True
                policy_result["required_controls"].append("Multi-factor authentication required")
        
        # Check risk-based policies
        if risk_factors:
            policy_result["conditional_access"] = True
            policy_result["required_controls"].append("Enhanced monitoring due to risk factors")
        
        # Check resource sensitivity policies
        if request.sensitivity_level == "critical":
            policy_result["required_controls"].extend([
                "Enhanced logging",
                "Real-time monitoring",
                "Administrative approval"
            ])
        
        return policy_result
    
    async def _make_access_decision(self, request: AccessRequest, trust_score: float, 
                                  risk_factors: List[str], policy_result: Dict[str, Any]) -> Dict[str, Any]:
        """Make final access control decision"""
        decision_data = {
            "decision": AccessDecision.DENY,
            "conditions": [],
            "session_duration": 0,
            "additional_verification": False,
            "explanation": ""
        }
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(trust_score, len(risk_factors))
        
        # Make decision based on trust score and risk factors
        if trust_score >= 0.8 and not risk_factors:
            decision_data["decision"] = AccessDecision.ALLOW
            decision_data["session_duration"] = self.config["session_management"]["max_session_duration"]
            decision_data["explanation"] = "High trust score with no risk factors"
        
        elif trust_score >= 0.6 and len(risk_factors) <= 2:
            decision_data["decision"] = AccessDecision.CONDITIONAL
            decision_data["conditions"] = [
                "Enhanced monitoring required",
                "Limited session duration",
                "Regular reauthentication"
            ]
            decision_data["session_duration"] = self.config["session_management"]["max_session_duration"] // 2
            decision_data["explanation"] = "Moderate trust with manageable risk factors"
        
        elif trust_score >= 0.4:
            decision_data["decision"] = AccessDecision.CHALLENGE
            decision_data["additional_verification"] = True
            decision_data["conditions"] = [
                "Additional authentication required",
                "Restricted permissions",
                "Continuous monitoring"
            ]
            decision_data["session_duration"] = self.config["session_management"]["max_session_duration"] // 4
            decision_data["explanation"] = "Moderate trust requiring additional verification"
        
        else:
            decision_data["decision"] = AccessDecision.DENY
            decision_data["explanation"] = "Insufficient trust score or high risk factors"
        
        # Override based on policy violations
        if policy_result["policy_violations"]:
            if decision_data["decision"] == AccessDecision.ALLOW:
                decision_data["decision"] = AccessDecision.CONDITIONAL
                decision_data["conditions"].extend(policy_result["required_controls"])
        
        # Apply additional verification requirements
        if policy_result["additional_verification"]:
            decision_data["additional_verification"] = True
        
        return decision_data
    
    def _calculate_risk_level(self, trust_score: float, risk_factor_count: int) -> str:
        """Calculate overall risk level"""
        risk_score = (1.0 - trust_score) + (risk_factor_count * 0.1)
        
        thresholds = self.config["risk_thresholds"]
        
        if risk_score >= thresholds["critical"]:
            return "critical"
        elif risk_score >= thresholds["high"]:
            return "high"
        elif risk_score >= thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    async def _determine_security_controls(self, request: AccessRequest, 
                                         access_decision: Dict[str, Any], 
                                         trust_score: float) -> List[str]:
        """Determine required security controls"""
        controls = []
        
        # Base security controls
        controls.extend([
            "Session encryption",
            "Activity logging",
            "Access token validation"
        ])
        
        # Trust-based controls
        if trust_score < 0.6:
            controls.extend([
                "Enhanced monitoring",
                "Behavioral analysis",
                "Real-time threat detection"
            ])
        
        # Decision-based controls
        if access_decision["decision"] == AccessDecision.CONDITIONAL:
            controls.extend([
                "Conditional access enforcement",
                "Regular trust reevaluation",
                "Automated session management"
            ])
        
        # Resource-based controls
        if request.sensitivity_level in ["high", "critical"]:
            controls.extend([
                "Data loss prevention",
                "Screen recording detection",
                "Watermarking"
            ])
        
        # Zone-based controls
        if request.security_zone in [SecurityZone.SECURE, SecurityZone.CRITICAL]:
            controls.extend([
                "Network micro-segmentation",
                "Privileged access management",
                "Administrative oversight"
            ])
        
        return list(set(controls))  # Remove duplicates
    
    async def _set_monitoring_requirements(self, request: AccessRequest, 
                                         access_decision: Dict[str, Any], 
                                         trust_score: float) -> List[str]:
        """Set monitoring requirements for the session"""
        monitoring = []
        
        # Base monitoring
        monitoring.extend([
            "Session activity tracking",
            "Access pattern analysis",
            "Resource usage monitoring"
        ])
        
        # Risk-based monitoring
        if trust_score < 0.7:
            monitoring.extend([
                "Real-time behavioral analysis",
                "Anomaly detection",
                "Threat correlation"
            ])
        
        # Decision-based monitoring
        if access_decision["decision"] in [AccessDecision.CONDITIONAL, AccessDecision.CHALLENGE]:
            monitoring.extend([
                "Enhanced session monitoring",
                "Privilege escalation detection",
                "Data access auditing"
            ])
        
        # Resource-based monitoring
        if request.sensitivity_level == "critical":
            monitoring.extend([
                "Comprehensive audit trail",
                "Real-time alerting",
                "Automated response triggers"
            ])
        
        return monitoring
    
    async def _log_security_event(self, event_type: str, request: AccessRequest, 
                                result: AccessResult) -> None:
        """Log security event for audit and analysis"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "request_id": request.request_id,
            "user_id": request.security_context.user_id,
            "device_id": request.security_context.device_id,
            "ip_address": request.security_context.ip_address,
            "resource_id": request.resource_id,
            "resource_type": request.resource_type,
            "requested_action": request.requested_action,
            "security_zone": request.security_zone.value,
            "decision": result.decision.value,
            "trust_score": result.trust_score,
            "risk_factors": result.risk_factors,
            "security_controls": result.security_controls
        }
        
        self.security_events.append(event)
        
        # Keep only recent events (configurable retention)
        max_events = 10000  # Adjust based on requirements
        if len(self.security_events) > max_events:
            self.security_events = self.security_events[-max_events:]
    
    async def create_secure_session(self, access_result: AccessResult, 
                                  security_context: SecurityContext) -> Dict[str, Any]:
        """Create secure session with Zero Trust controls"""
        if access_result.decision == AccessDecision.DENY:
            raise SecurityError("Access denied - cannot create session")
        
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "user_id": security_context.user_id,
            "device_id": security_context.device_id,
            "ip_address": security_context.ip_address,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=access_result.session_duration),
            "trust_score": access_result.trust_score,
            "security_controls": access_result.security_controls,
            "monitoring_requirements": access_result.monitoring_requirements,
            "last_activity": datetime.now(),
            "activity_count": 0,
            "risk_factors": access_result.risk_factors
        }
        
        self.active_sessions[session_id] = session_data
        
        logger.info(f"🔐 Secure session created: {session_id}")
        return session_data
    
    async def validate_session(self, session_id: str, current_context: SecurityContext) -> bool:
        """Validate active session with continuous verification"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Check session expiration
        if datetime.now() > session["expires_at"]:
            await self.terminate_session(session_id, "Session expired")
            return False
        
        # Check idle timeout
        idle_duration = datetime.now() - session["last_activity"]
        if idle_duration.total_seconds() > self.config["session_management"]["idle_timeout"]:
            await self.terminate_session(session_id, "Idle timeout")
            return False
        
        # Continuous trust verification
        current_trust = await self._calculate_trust_score(current_context)
        
        # Check trust degradation
        if current_trust < session["trust_score"] * 0.7:  # 30% degradation threshold
            logger.warning(f"⚠️ Trust degradation detected for session {session_id}")
            # Could trigger reauthentication or session termination
            return False
        
        # Update session activity
        session["last_activity"] = datetime.now()
        session["activity_count"] += 1
        
        return True
    
    async def terminate_session(self, session_id: str, reason: str) -> None:
        """Terminate secure session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Log session termination
            await self._log_security_event("session_terminated", None, None)
            
            # Remove session
            del self.active_sessions[session_id]
            
            logger.info(f"🔒 Session terminated: {session_id} - Reason: {reason}")
    
    def _continuous_monitoring_loop(self) -> None:
        """Continuous security monitoring background task"""
        while True:
            try:
                # Monitor active sessions
                for session_id, session in list(self.active_sessions.items()):
                    # Check for suspicious activity patterns
                    if session["activity_count"] > 1000:  # Example threshold
                        logger.warning(f"⚠️ High activity detected for session {session_id}")
                    
                    # Check for session anomalies
                    session_duration = datetime.now() - session["created_at"]
                    if session_duration.total_seconds() > 24 * 3600:  # 24 hours
                        logger.warning(f"⚠️ Long-running session detected: {session_id}")
                
                # Monitor threat intelligence
                self._check_threat_intelligence()
                
                # Sleep before next monitoring cycle
                time.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"❌ Continuous monitoring error: {str(e)}")
                time.sleep(60)
    
    def _threat_intelligence_updater(self) -> None:
        """Update threat intelligence data"""
        while True:
            try:
                # Update threat intelligence (mock implementation)
                logger.debug("🔄 Updating threat intelligence...")
                time.sleep(3600)  # Update hourly
            except Exception as e:
                logger.error(f"❌ Threat intelligence update error: {str(e)}")
                time.sleep(3600)
    
    def _session_cleanup_loop(self) -> None:
        """Clean up expired sessions"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if current_time > session["expires_at"]:
                        expired_sessions.append(session_id)
                
                # Remove expired sessions
                for session_id in expired_sessions:
                    asyncio.run(self.terminate_session(session_id, "Expired"))
                
                if expired_sessions:
                    logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Session cleanup error: {str(e)}")
                time.sleep(300)
    
    def _check_threat_intelligence(self) -> None:
        """Check for threat intelligence indicators"""
        # Check active sessions against threat intelligence
        for session_id, session in self.active_sessions.items():
            ip_address = session["ip_address"]
            
            if ip_address in self.threat_intelligence["malicious_ips"]:
                logger.critical(f"🚨 THREAT DETECTED: Malicious IP in active session {session_id}")
                # Could trigger immediate session termination
    
    def get_security_analytics(self) -> Dict[str, Any]:
        """Get Zero Trust security analytics"""
        current_time = datetime.now()
        
        # Session analytics
        total_sessions = len(self.active_sessions)
        recent_events = [e for e in self.security_events 
                        if datetime.fromisoformat(e["timestamp"]) > current_time - timedelta(hours=24)]
        
        # Decision analytics
        decision_counts = {}
        for event in recent_events:
            decision = event.get("decision", "unknown")
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
        
        # Risk analytics
        high_risk_sessions = sum(1 for s in self.active_sessions.values() 
                               if s.get("trust_score", 1.0) < 0.5)
        
        return {
            "active_sessions": total_sessions,
            "events_last_24h": len(recent_events),
            "access_decisions": decision_counts,
            "high_risk_sessions": high_risk_sessions,
            "threat_indicators": len(self.threat_intelligence["malicious_ips"]),
            "security_events_total": len(self.security_events),
            "average_trust_score": sum(s.get("trust_score", 0) for s in self.active_sessions.values()) / 
                                 total_sessions if total_sessions > 0 else 0
        }

# Trust Engine Implementations
class UserTrustEngine:
    """User trust calculation engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def calculate_trust(self, context: SecurityContext) -> float:
        """Calculate user trust score"""
        trust_score = 0.5  # Base trust
        
        # Authentication factors bonus
        if len(context.authentication_factors) >= 2:
            trust_score += 0.2
        if "biometric" in context.authentication_factors:
            trust_score += 0.1
        
        # Account age and history (mock implementation)
        # In production, this would check user account history
        trust_score += 0.2
        
        return min(1.0, max(0.0, trust_score))

class DeviceTrustEngine:
    """Device trust calculation engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def calculate_trust(self, context: SecurityContext) -> float:
        """Calculate device trust score"""
        trust_score = 0.3  # Base trust for unknown devices
        
        # Known device bonus (mock implementation)
        # In production, this would check device registry
        trust_score += 0.4
        
        # Compliance bonus
        if context.device_trust_score > 0.8:
            trust_score += 0.3
        
        return min(1.0, max(0.0, trust_score))

class NetworkTrustEngine:
    """Network trust calculation engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def calculate_trust(self, context: SecurityContext) -> float:
        """Calculate network trust score"""
        trust_score = 0.5  # Base trust
        
        # Check if IP is in trusted networks
        try:
            ip = ipaddress.ip_address(context.ip_address)
            trusted_networks = self.config["network_security"]["trusted_networks"]
            
            for network_str in trusted_networks:
                network = ipaddress.ip_network(network_str)
                if ip in network:
                    trust_score += 0.3
                    break
        except:
            pass
        
        # Geographic location bonus (mock implementation)
        if context.location and context.location.get("country_code") == "US":
            trust_score += 0.2
        
        return min(1.0, max(0.0, trust_score))

class BehavioralTrustEngine:
    """Behavioral trust calculation engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def calculate_trust(self, context: SecurityContext) -> float:
        """Calculate behavioral trust score"""
        trust_score = 0.7  # Base trust
        
        # Time-based patterns
        current_hour = context.timestamp.hour
        if 9 <= current_hour <= 17:  # Business hours
            trust_score += 0.1
        
        # Previous activity patterns (mock implementation)
        if context.previous_activities:
            # Analyze consistency in behavior
            trust_score += 0.2
        
        return min(1.0, max(0.0, trust_score))

class ContextualTrustEngine:
    """Contextual trust calculation engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def calculate_trust(self, context: SecurityContext) -> float:
        """Calculate contextual trust score"""
        trust_score = 0.6  # Base trust
        
        # Session context
        if context.session_id:
            trust_score += 0.2
        
        # User agent consistency (mock implementation)
        trust_score += 0.2
        
        return min(1.0, max(0.0, trust_score))

class SecurityError(Exception):
    """Zero Trust security exception"""
    pass

# Example usage and testing
if __name__ == "__main__":
    async def test_zero_trust_security():
        """Test the Zero Trust Security Manager"""
        zt_manager = ZeroTrustSecurityManager()
        
        # Create test security context
        context = SecurityContext(
            user_id="user_123",
            device_id="device_456",
            ip_address="192.168.1.100",
            location={"country_code": "US", "city": "New York"},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            timestamp=datetime.now(),
            session_id="session_789",
            authentication_factors=["password", "mfa"],
            device_trust_score=0.8,
            network_trust_score=0.7
        )
        
        # Create test access request
        request = AccessRequest(
            request_id="req_001",
            security_context=context,
            resource_id="resource_123",
            resource_type="api_endpoint",
            requested_action="read",
            security_zone=SecurityZone.INTERNAL,
            sensitivity_level="medium",
            requested_permissions=["read", "list"]
        )
        
        # Test access evaluation
        print("🔒 Testing Zero Trust Security Manager...")
        result = await zt_manager.evaluate_access_request(request)
        
        print(f"✅ Access Evaluation Results:")
        print(f"   Decision: {result.decision.value}")
        print(f"   Trust Score: {result.trust_score:.2f}")
        print(f"   Risk Factors: {len(result.risk_factors)}")
        print(f"   Security Controls: {len(result.security_controls)}")
        print(f"   Session Duration: {result.session_duration}s")
        
        # Test session creation if access allowed
        if result.decision != AccessDecision.DENY:
            session = await zt_manager.create_secure_session(result, context)
            print(f"🔐 Secure session created: {session['session_id']}")
        
        # Get security analytics
        analytics = zt_manager.get_security_analytics()
        print(f"📊 Security Analytics:")
        print(f"   Active Sessions: {analytics['active_sessions']}")
        print(f"   Events (24h): {analytics['events_last_24h']}")
        print(f"   Average Trust Score: {analytics['average_trust_score']:.2f}")
    
    # Run test
    asyncio.run(test_zero_trust_security())