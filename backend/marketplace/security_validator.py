"""Security Validator - Transaction Security Validation Engine
==========================================================

Enterprise-level security validation system for marketplace transactions,
providing comprehensive security checks, threat detection, and validation.

Features:
- Real-time transaction security validation
- Multi-layer security checks (authentication, authorization, integrity)
- Advanced threat detection and prevention
- Security policy enforcement and compliance
- Risk assessment and scoring

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/marketplace/security_validator.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import json
import re

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    MAXIMUM = "maximum"

class ThreatType(Enum):
    """Security threat type enumeration"""
    FRAUD = "fraud"
    IDENTITY_THEFT = "identity_theft"
    MONEY_LAUNDERING = "money_laundering"
    PHISHING = "phishing"
    ACCOUNT_TAKEOVER = "account_takeover"
    PAYMENT_FRAUD = "payment_fraud"
    VELOCITY_FRAUD = "velocity_fraud"
    SYNTHETIC_IDENTITY = "synthetic_identity"
    CREDENTIAL_STUFFING = "credential_stuffing"
    BOT_ATTACK = "bot_attack"
    DDoS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    OTHER = "other"

class ValidationStatus(Enum):
    """Validation status enumeration"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"
    BLOCKED = "blocked"
    REQUIRES_REVIEW = "requires_review"

class SecurityAction(Enum):
    """Security action enumeration"""
    ALLOW = "allow"
    DENY = "deny"
    BLOCK = "block"
    FLAG = "flag"
    REQUIRE_2FA = "require_2fa"
    REQUIRE_VERIFICATION = "require_verification"
    QUARANTINE = "quarantine"
    MONITOR = "monitor"

@dataclass
class SecurityRule:
    """Security validation rule"""
    rule_id: str
    name: str
    description: str
    rule_type: str  # "threshold", "pattern", "blacklist", "whitelist", etc.
    condition: str
    action: SecurityAction
    severity: SecurityLevel
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityCheck:
    """Individual security check result"""
    check_id: str
    check_type: str
    status: ValidationStatus
    score: float  # 0.0 to 1.0
    risk_level: SecurityLevel
    details: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    performed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityValidationResult:
    """Complete security validation result"""
    validation_id: str
    transaction_id: str
    user_id: str
    overall_status: ValidationStatus
    overall_score: float  # 0.0 to 1.0
    risk_level: SecurityLevel
    recommended_action: SecurityAction
    checks: List[SecurityCheck] = field(default_factory=list)
    threats_detected: List[ThreatType] = field(default_factory=list)
    validation_time_ms: int = 0
    performed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityContext:
    """Security context for validation"""
    user_id: str
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_fingerprint: Optional[str] = None
    location: Optional[Dict[str, str]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TransactionContext:
    """Transaction context for security validation"""
    transaction_id: str
    transaction_type: str
    amount: Decimal
    currency: str = "USD"
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    payment_method: Optional[str] = None
    merchant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class SecurityValidator:
    """Advanced security validation and threat detection system"""
    
    def __init__(self):
        self.security_rules: Dict[str, SecurityRule] = {}
        self.validation_results: Dict[str, SecurityValidationResult] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.blacklisted_ips: Set[str] = set()
        self.blacklisted_devices: Set[str] = set()
        self.security_policies: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting tracking
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Initialize default rules and policies
        self._initialize_default_rules()
        self._initialize_security_policies()
    
    def _initialize_default_rules(self):
        """Initialize default security rules"""
        default_rules = [
            SecurityRule(
                rule_id="rate_limit_login",
                name="Login Rate Limiting",
                description="Prevent brute force login attempts",
                rule_type="rate_limit",
                condition="login_attempts > 5 in 15 minutes",
                action=SecurityAction.BLOCK,
                severity=SecurityLevel.HIGH
            ),
            SecurityRule(
                rule_id="suspicious_amount",
                name="Suspicious Transaction Amount",
                description="Flag unusually large transactions",
                rule_type="threshold",
                condition="amount > 10000 USD",
                action=SecurityAction.REQUIRE_VERIFICATION,
                severity=SecurityLevel.MEDIUM
            ),
            SecurityRule(
                rule_id="velocity_check",
                name="Transaction Velocity Check",
                description="Monitor transaction frequency",
                rule_type="velocity",
                condition="transactions > 10 in 1 hour",
                action=SecurityAction.FLAG,
                severity=SecurityLevel.MEDIUM
            ),
            SecurityRule(
                rule_id="geo_anomaly",
                name="Geographic Anomaly Detection",
                description="Detect unusual geographic patterns",
                rule_type="geographic",
                condition="location_change > 1000 km in 1 hour",
                action=SecurityAction.REQUIRE_2FA,
                severity=SecurityLevel.HIGH
            ),
            SecurityRule(
                rule_id="device_fingerprint",
                name="Device Fingerprint Validation",
                description="Validate device consistency",
                rule_type="device",
                condition="device_fingerprint not in known_devices",
                action=SecurityAction.REQUIRE_VERIFICATION,
                severity=SecurityLevel.MEDIUM
            )
        ]
        
        for rule in default_rules:
            self.security_rules[rule.rule_id] = rule
    
    def _initialize_security_policies(self):
        """Initialize security policies"""
        self.security_policies = {
            "authentication": {
                "max_login_attempts": 5,
                "lockout_duration_minutes": 15,
                "session_timeout_minutes": 30,
                "require_2fa_for_high_value": True,
                "high_value_threshold": Decimal("1000.00")
            },
            "transaction_limits": {
                "daily_limit_unverified": Decimal("500.00"),
                "daily_limit_verified": Decimal("10000.00"),
                "single_transaction_limit": Decimal("50000.00"),
                "velocity_limit_per_hour": 10
            },
            "risk_scoring": {
                "low_risk_threshold": 0.3,
                "medium_risk_threshold": 0.6,
                "high_risk_threshold": 0.8,
                "auto_block_threshold": 0.9
            }
        }
    
    async def validate_transaction_security(
        self,
        transaction_context: TransactionContext,
        security_context: SecurityContext
    ) -> SecurityValidationResult:
        """Perform comprehensive security validation on transaction"""
        try:
            start_time = time.time()
            validation_id = f"validation_{uuid.uuid4().hex[:12]}"
            
            checks = []
            threats_detected = []
            
            # Perform individual security checks
            checks.extend(await self._check_authentication_security(security_context))
            checks.extend(await self._check_transaction_limits(transaction_context, security_context))
            checks.extend(await self._check_rate_limits(security_context))
            checks.extend(await self._check_geographic_anomalies(security_context))
            checks.extend(await self._check_device_fingerprint(security_context))
            checks.extend(await self._check_payment_fraud_indicators(transaction_context))
            checks.extend(await self._check_velocity_patterns(transaction_context, security_context))
            checks.extend(await self._check_blacklists(security_context))
            
            # Calculate overall risk score
            overall_score, risk_level = self._calculate_risk_score(checks)
            
            # Determine overall status and action
            overall_status, recommended_action = self._determine_action(overall_score, risk_level, checks)
            
            # Detect specific threats
            threats_detected = self._detect_threats(checks)
            
            validation_time_ms = int((time.time() - start_time) * 1000)
            
            result = SecurityValidationResult(
                validation_id=validation_id,
                transaction_id=transaction_context.transaction_id,
                user_id=security_context.user_id,
                overall_status=overall_status,
                overall_score=overall_score,
                risk_level=risk_level,
                recommended_action=recommended_action,
                checks=checks,
                threats_detected=threats_detected,
                validation_time_ms=validation_time_ms
            )
            
            self.validation_results[validation_id] = result
            
            # Log security event
            await self._log_security_event(result)
            
            logger.info(f"Security validation completed for transaction {transaction_context.transaction_id}: {overall_status.value}")
            return result
            
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            # Return failed validation
            return SecurityValidationResult(
                validation_id=f"error_{uuid.uuid4().hex[:12]}",
                transaction_id=transaction_context.transaction_id,
                user_id=security_context.user_id,
                overall_status=ValidationStatus.FAILED,
                overall_score=1.0,
                risk_level=SecurityLevel.CRITICAL,
                recommended_action=SecurityAction.BLOCK,
                metadata={"error": str(e)}
            )
    
    async def _check_authentication_security(self, context: SecurityContext) -> List[SecurityCheck]:
        """Check authentication security"""
        checks = []
        
        # Session validation
        session_valid = await self._validate_session(context.user_id, context.session_id)
        checks.append(SecurityCheck(
            check_id=f"session_{uuid.uuid4().hex[:8]}",
            check_type="session_validation",
            status=ValidationStatus.PASSED if session_valid else ValidationStatus.FAILED,
            score=0.0 if session_valid else 0.8,
            risk_level=SecurityLevel.LOW if session_valid else SecurityLevel.HIGH,
            details="Session validation",
            evidence={"session_valid": session_valid}
        ))
        
        # Multi-factor authentication check
        mfa_required = await self._check_mfa_requirement(context.user_id)
        mfa_completed = await self._check_mfa_status(context.user_id)
        
        if mfa_required and not mfa_completed:
            checks.append(SecurityCheck(
                check_id=f"mfa_{uuid.uuid4().hex[:8]}",
                check_type="mfa_validation",
                status=ValidationStatus.FAILED,
                score=0.6,
                risk_level=SecurityLevel.MEDIUM,
                details="MFA required but not completed",
                evidence={"mfa_required": True, "mfa_completed": False}
            ))
        
        return checks
    
    async def _check_transaction_limits(
        self,
        transaction_context: TransactionContext,
        security_context: SecurityContext
    ) -> List[SecurityCheck]:
        """Check transaction limits"""
        checks = []
        
        # Single transaction limit
        single_limit = self.security_policies["transaction_limits"]["single_transaction_limit"]
        if transaction_context.amount > single_limit:
            checks.append(SecurityCheck(
                check_id=f"limit_{uuid.uuid4().hex[:8]}",
                check_type="transaction_limit",
                status=ValidationStatus.FAILED,
                score=0.9,
                risk_level=SecurityLevel.CRITICAL,
                details=f"Transaction amount {transaction_context.amount} exceeds single limit {single_limit}",
                evidence={"amount": float(transaction_context.amount), "limit": float(single_limit)}
            ))
        
        # Daily limit check
        daily_total = await self._get_daily_transaction_total(security_context.user_id)
        is_verified = await self._is_user_verified(security_context.user_id)
        
        daily_limit_key = "daily_limit_verified" if is_verified else "daily_limit_unverified"
        daily_limit = self.security_policies["transaction_limits"][daily_limit_key]
        
        if daily_total + transaction_context.amount > daily_limit:
            checks.append(SecurityCheck(
                check_id=f"daily_{uuid.uuid4().hex[:8]}",
                check_type="daily_limit",
                status=ValidationStatus.WARNING,
                score=0.7,
                risk_level=SecurityLevel.MEDIUM,
                details=f"Daily total would exceed limit",
                evidence={
                    "daily_total": float(daily_total),
                    "new_amount": float(transaction_context.amount),
                    "daily_limit": float(daily_limit)
                }
            ))
        
        return checks
    
    async def _check_rate_limits(self, context: SecurityContext) -> List[SecurityCheck]:
        """Check rate limiting"""
        checks = []
        
        # Check transaction velocity
        user_key = f"user_{context.user_id}"
        current_time = datetime.utcnow()
        
        if user_key not in self.rate_limits:
            self.rate_limits[user_key] = []
        
        # Clean old entries (older than 1 hour)
        cutoff_time = current_time - timedelta(hours=1)
        self.rate_limits[user_key] = [
            timestamp for timestamp in self.rate_limits[user_key]
            if timestamp > cutoff_time
        ]
        
        # Check velocity
        velocity_limit = self.security_policies["transaction_limits"]["velocity_limit_per_hour"]
        current_velocity = len(self.rate_limits[user_key])
        
        if current_velocity >= velocity_limit:
            checks.append(SecurityCheck(
                check_id=f"velocity_{uuid.uuid4().hex[:8]}",
                check_type="velocity_check",
                status=ValidationStatus.FAILED,
                score=0.8,
                risk_level=SecurityLevel.HIGH,
                details=f"Transaction velocity {current_velocity} exceeds limit {velocity_limit}",
                evidence={"current_velocity": current_velocity, "limit": velocity_limit}
            ))
        
        # Add current transaction to rate limit tracking
        self.rate_limits[user_key].append(current_time)
        
        return checks
    
    async def _check_geographic_anomalies(self, context: SecurityContext) -> List[SecurityCheck]:
        """Check for geographic anomalies"""
        checks = []
        
        if not context.location:
            return checks
        
        # Get user's recent locations
        recent_locations = await self._get_recent_locations(context.user_id)
        
        if recent_locations:
            # Calculate distance from most recent location
            distance_km = self._calculate_distance(
                recent_locations[0],
                context.location
            )
            
            # Check for impossible travel
            time_diff_hours = (datetime.utcnow() - recent_locations[0]["timestamp"]).total_seconds() / 3600
            max_travel_speed = 1000  # km/h (commercial aircraft speed)
            
            if distance_km > (max_travel_speed * time_diff_hours):
                checks.append(SecurityCheck(
                    check_id=f"geo_{uuid.uuid4().hex[:8]}",
                    check_type="geographic_anomaly",
                    status=ValidationStatus.WARNING,
                    score=0.7,
                    risk_level=SecurityLevel.MEDIUM,
                    details=f"Impossible travel detected: {distance_km:.0f}km in {time_diff_hours:.1f}h",
                    evidence={
                        "distance_km": distance_km,
                        "time_hours": time_diff_hours,
                        "max_possible": max_travel_speed * time_diff_hours
                    }
                ))
        
        return checks
    
    async def _check_device_fingerprint(self, context: SecurityContext) -> List[SecurityCheck]:
        """Check device fingerprint consistency"""
        checks = []
        
        if not context.device_fingerprint:
            return checks
        
        # Get user's known devices
        known_devices = await self._get_known_devices(context.user_id)
        
        if context.device_fingerprint not in known_devices:
            checks.append(SecurityCheck(
                check_id=f"device_{uuid.uuid4().hex[:8]}",
                check_type="device_fingerprint",
                status=ValidationStatus.WARNING,
                score=0.5,
                risk_level=SecurityLevel.MEDIUM,
                details="Unknown device fingerprint",
                evidence={
                    "fingerprint": context.device_fingerprint,
                    "known_devices_count": len(known_devices)
                }
            ))
        
        return checks
    
    async def _check_payment_fraud_indicators(self, context: TransactionContext) -> List[SecurityCheck]:
        """Check for payment fraud indicators"""
        checks = []
        
        # Check for suspicious payment patterns
        if context.payment_method:
            # Check for recently added payment methods
            payment_age = await self._get_payment_method_age(context.payment_method)
            
            if payment_age and payment_age < timedelta(hours=24) and context.amount > Decimal("100"):
                checks.append(SecurityCheck(
                    check_id=f"payment_{uuid.uuid4().hex[:8]}",
                    check_type="payment_fraud",
                    status=ValidationStatus.WARNING,
                    score=0.6,
                    risk_level=SecurityLevel.MEDIUM,
                    details="High-value transaction with recently added payment method",
                    evidence={
                        "payment_age_hours": payment_age.total_seconds() / 3600,
                        "amount": float(context.amount)
                    }
                ))
        
        return checks
    
    async def _check_velocity_patterns(
        self,
        transaction_context: TransactionContext,
        security_context: SecurityContext
    ) -> List[SecurityCheck]:
        """Check for suspicious velocity patterns"""
        checks = []
        
        # Check for rapid-fire transactions
        recent_transactions = await self._get_recent_transactions(security_context.user_id, minutes=5)
        
        if len(recent_transactions) > 3:
            checks.append(SecurityCheck(
                check_id=f"rapid_{uuid.uuid4().hex[:8]}",
                check_type="rapid_transactions",
                status=ValidationStatus.WARNING,
                score=0.7,
                risk_level=SecurityLevel.MEDIUM,
                details=f"Rapid transactions detected: {len(recent_transactions)} in 5 minutes",
                evidence={"transaction_count": len(recent_transactions)}
            ))
        
        return checks
    
    async def _check_blacklists(self, context: SecurityContext) -> List[SecurityCheck]:
        """Check against blacklists"""
        checks = []
        
        # Check IP blacklist
        if context.ip_address and context.ip_address in self.blacklisted_ips:
            checks.append(SecurityCheck(
                check_id=f"blacklist_{uuid.uuid4().hex[:8]}",
                check_type="ip_blacklist",
                status=ValidationStatus.FAILED,
                score=1.0,
                risk_level=SecurityLevel.CRITICAL,
                details="IP address is blacklisted",
                evidence={"ip_address": context.ip_address}
            ))
        
        # Check device blacklist
        if context.device_fingerprint and context.device_fingerprint in self.blacklisted_devices:
            checks.append(SecurityCheck(
                check_id=f"device_blacklist_{uuid.uuid4().hex[:8]}",
                check_type="device_blacklist",
                status=ValidationStatus.FAILED,
                score=1.0,
                risk_level=SecurityLevel.CRITICAL,
                details="Device is blacklisted",
                evidence={"device_fingerprint": context.device_fingerprint}
            ))
        
        return checks
    
    def _calculate_risk_score(self, checks: List[SecurityCheck]) -> Tuple[float, SecurityLevel]:
        """Calculate overall risk score from individual checks"""
        if not checks:
            return 0.0, SecurityLevel.LOW
        
        # Weighted scoring - failed checks contribute more
        total_score = 0.0
        weight_sum = 0.0
        
        for check in checks:
            weight = 1.0
            if check.status == ValidationStatus.FAILED:
                weight = 3.0
            elif check.status == ValidationStatus.WARNING:
                weight = 2.0
            
            total_score += check.score * weight
            weight_sum += weight
        
        overall_score = total_score / weight_sum if weight_sum > 0 else 0.0
        
        # Determine risk level
        thresholds = self.security_policies["risk_scoring"]
        if overall_score >= thresholds["high_risk_threshold"]:
            risk_level = SecurityLevel.HIGH
        elif overall_score >= thresholds["medium_risk_threshold"]:
            risk_level = SecurityLevel.MEDIUM
        else:
            risk_level = SecurityLevel.LOW
        
        return overall_score, risk_level
    
    def _determine_action(
        self,
        overall_score: float,
        risk_level: SecurityLevel,
        checks: List[SecurityCheck]
    ) -> Tuple[ValidationStatus, SecurityAction]:
        """Determine overall status and recommended action"""
        # Check for critical failures
        critical_failures = [
            check for check in checks
            if check.status == ValidationStatus.FAILED and check.risk_level == SecurityLevel.CRITICAL
        ]
        
        if critical_failures:
            return ValidationStatus.BLOCKED, SecurityAction.BLOCK
        
        # Check auto-block threshold
        auto_block_threshold = self.security_policies["risk_scoring"]["auto_block_threshold"]
        if overall_score >= auto_block_threshold:
            return ValidationStatus.BLOCKED, SecurityAction.BLOCK
        
        # Check for high-risk scenarios requiring additional verification
        high_risk_checks = [
            check for check in checks
            if check.risk_level == SecurityLevel.HIGH
        ]
        
        if high_risk_checks or risk_level == SecurityLevel.HIGH:
            return ValidationStatus.REQUIRES_REVIEW, SecurityAction.REQUIRE_VERIFICATION
        
        # Check for medium-risk scenarios
        if risk_level == SecurityLevel.MEDIUM:
            return ValidationStatus.WARNING, SecurityAction.FLAG
        
        return ValidationStatus.PASSED, SecurityAction.ALLOW
    
    def _detect_threats(self, checks: List[SecurityCheck]) -> List[ThreatType]:
        """Detect specific threat types from checks"""
        threats = []
        
        threat_patterns = {
            "velocity_check": ThreatType.VELOCITY_FRAUD,
            "rapid_transactions": ThreatType.VELOCITY_FRAUD,
            "payment_fraud": ThreatType.PAYMENT_FRAUD,
            "geographic_anomaly": ThreatType.FRAUD,
            "ip_blacklist": ThreatType.FRAUD,
            "device_blacklist": ThreatType.FRAUD,
            "session_validation": ThreatType.ACCOUNT_TAKEOVER
        }
        
        for check in checks:
            if check.status in [ValidationStatus.FAILED, ValidationStatus.WARNING]:
                threat_type = threat_patterns.get(check.check_type)
                if threat_type and threat_type not in threats:
                    threats.append(threat_type)
        
        return threats
    
    async def _log_security_event(self, result: SecurityValidationResult):
        """Log security validation event"""
        event_data = {
            "validation_id": result.validation_id,
            "transaction_id": result.transaction_id,
            "user_id": result.user_id,
            "status": result.overall_status.value,
            "score": result.overall_score,
            "risk_level": result.risk_level.value,
            "threats": [threat.value for threat in result.threats_detected],
            "validation_time_ms": result.validation_time_ms
        }
        
        logger.info(f"Security validation logged: {json.dumps(event_data)}")
    
    # Helper methods with mock implementations
    
    async def _validate_session(self, user_id: str, session_id: Optional[str]) -> bool:
        """Validate user session"""
        # Mock implementation
        return session_id is not None
    
    async def _check_mfa_requirement(self, user_id: str) -> bool:
        """Check if MFA is required for user"""
        # Mock implementation
        return False
    
    async def _check_mfa_status(self, user_id: str) -> bool:
        """Check MFA completion status"""
        # Mock implementation
        return True
    
    async def _get_daily_transaction_total(self, user_id: str) -> Decimal:
        """Get user's daily transaction total"""
        # Mock implementation
        return Decimal("100.00")
    
    async def _is_user_verified(self, user_id: str) -> bool:
        """Check if user is verified"""
        # Mock implementation
        return True
    
    async def _get_recent_locations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's recent locations"""
        # Mock implementation
        return []
    
    def _calculate_distance(self, loc1: Dict[str, str], loc2: Dict[str, str]) -> float:
        """Calculate distance between two locations"""
        # Mock implementation - would use geospatial calculation
        return 0.0
    
    async def _get_known_devices(self, user_id: str) -> Set[str]:
        """Get user's known device fingerprints"""
        # Mock implementation
        return set()
    
    async def _get_payment_method_age(self, payment_method: str) -> Optional[timedelta]:
        """Get age of payment method"""
        # Mock implementation
        return timedelta(days=30)
    
    async def _get_recent_transactions(self, user_id: str, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get recent transactions for user"""
        # Mock implementation
        return []
    
    # Public interface methods
    
    async def add_security_rule(self, rule: SecurityRule) -> bool:
        """Add or update security rule"""
        try:
            self.security_rules[rule.rule_id] = rule
            logger.info(f"Security rule added/updated: {rule.rule_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding security rule: {e}")
            return False
    
    async def blacklist_ip(self, ip_address: str, reason: str = "") -> bool:
        """Add IP address to blacklist"""
        try:
            self.blacklisted_ips.add(ip_address)
            logger.warning(f"IP address blacklisted: {ip_address} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error blacklisting IP: {e}")
            return False
    
    async def blacklist_device(self, device_fingerprint: str, reason: str = "") -> bool:
        """Add device to blacklist"""
        try:
            self.blacklisted_devices.add(device_fingerprint)
            logger.warning(f"Device blacklisted: {device_fingerprint} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error blacklisting device: {e}")
            return False
    
    def get_validation_result(self, validation_id: str) -> Optional[SecurityValidationResult]:
        """Get validation result by ID"""
        return self.validation_results.get(validation_id)
    
    async def get_security_analytics(self) -> Dict[str, Any]:
        """Get security analytics and metrics"""
        total_validations = len(self.validation_results)
        
        if total_validations == 0:
            return {"total_validations": 0}
        
        passed = len([r for r in self.validation_results.values() if r.overall_status == ValidationStatus.PASSED])
        blocked = len([r for r in self.validation_results.values() if r.overall_status == ValidationStatus.BLOCKED])
        
        # Calculate average risk score
        avg_risk_score = sum(r.overall_score for r in self.validation_results.values()) / total_validations
        
        # Count threat types
        threat_counts = {}
        for result in self.validation_results.values():
            for threat in result.threats_detected:
                threat_counts[threat.value] = threat_counts.get(threat.value, 0) + 1
        
        return {
            "total_validations": total_validations,
            "passed_rate": (passed / total_validations) * 100,
            "blocked_rate": (blocked / total_validations) * 100,
            "average_risk_score": avg_risk_score,
            "threat_breakdown": threat_counts,
            "blacklisted_ips": len(self.blacklisted_ips),
            "blacklisted_devices": len(self.blacklisted_devices)
        }

# Example usage
async def main():
    """Example usage of SecurityValidator"""
    validator = SecurityValidator()
    
    # Create contexts
    transaction_context = TransactionContext(
        transaction_id="txn_123",
        transaction_type="purchase",
        amount=Decimal("500.00"),
        currency="USD",
        payment_method="credit_card"
    )
    
    security_context = SecurityContext(
        user_id="user_001",
        session_id="session_abc123",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0...",
        device_fingerprint="fp_xyz789"
    )
    
    # Validate transaction security
    result = await validator.validate_transaction_security(transaction_context, security_context)
    
    print(f"Validation result: {result.overall_status.value}")
    print(f"Risk score: {result.overall_score:.2f}")
    print(f"Recommended action: {result.recommended_action.value}")
    print(f"Threats detected: {[threat.value for threat in result.threats_detected]}")
    
    # Get analytics
    analytics = await validator.get_security_analytics()
    print(f"Security analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(main())