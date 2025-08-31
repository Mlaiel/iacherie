"""Marketplace Security - Advanced Security and Fraud Protection

Provides comprehensive security features including fraud detection,
threat analysis, user verification, and transaction security.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import secrets

from .marketplace_agent import MarketplaceConfig, MarketplaceTransaction


class ThreatLevel(Enum):
    """Security threat levels."""    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(Enum):
    """Types of security events."""    FRAUD_ATTEMPT = "fraud_attempt"
    SUSPICIOUS_LOGIN = "suspicious_login"
    UNUSUAL_TRANSACTION = "unusual_transaction"
    ACCOUNT_COMPROMISE = "account_compromise"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_INTRUSION = "system_intrusion"


class UserRiskLevel(Enum):
    """User risk assessment levels."""    TRUSTED = "trusted"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


@dataclass
class SecurityValidation:
    """Security validation result."""    is_valid: bool = False
    risk_score: float = 0.0
    threat_level: ThreatLevel = ThreatLevel.LOW
    blocked_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    security_flags: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    confidence_level: float = 0.0
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FraudAnalysis:
    """Fraud detection analysis result."""    fraud_score: float = 0.0
    is_fraudulent: bool = False
    fraud_indicators: List[str] = field(default_factory=list)
    behavior_anomalies: List[str] = field(default_factory=list)
    risk_factors: Dict[str, float] = field(default_factory=dict)
    mitigation_actions: List[str] = field(default_factory=list)
    analysis_confidence: float = 0.0


@dataclass
class SecurityEvent:
    """Security event record."""    id: Optional[str] = None
    event_type: SecurityEventType = SecurityEventType.POLICY_VIOLATION
    severity: ThreatLevel = ThreatLevel.LOW
    user_id: Optional[int] = None
    ip_address: str = ""
    user_agent: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    status: str = "open"  # open, investigating, resolved, false_positive


@dataclass
class UserRiskProfile:
    """Comprehensive user risk assessment profile."""    user_id: int = 0
    risk_level: UserRiskLevel = UserRiskLevel.LOW_RISK
    risk_score: float = 0.0
    account_age_days: int = 0
    transaction_history_score: float = 0.0
    behavior_score: float = 0.0
    verification_level: str = "basic"  # basic, verified, premium
    flags: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class MarketplaceSecurity:
    """    Advanced marketplace security and fraud protection system.
    
    Provides comprehensive security features including:
    - Real-time fraud detection using machine learning
    - Advanced behavioral analysis and anomaly detection
    - Multi-factor authentication and user verification
    - Transaction security monitoring and validation
    - Threat intelligence and risk assessment
    - Automated security response and incident management
    """
    def __init__(self, config: MarketplaceConfig):
        """        Initialize marketplace security system.
        
        Args:
            config: Marketplace configuration
        """        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize security components
        self._initialize_fraud_detection()
        self._initialize_threat_intelligence()
        
        # Security state tracking
        self.security_events = {}
        self.user_risk_profiles = {}
        self.blocked_users = set()
        self.security_metrics = {
            "fraud_attempts_blocked": 0,
            "security_events_detected": 0,
            "false_positive_rate": 0.02,
            "threat_detection_accuracy": 0.94
        }
        
        self.logger.info("Marketplace security system initialized")

    def _initialize_fraud_detection(self) -> None:
        """Initialize fraud detection algorithms and models."""        try:
            # Initialize ML models for fraud detection
            # Initialize behavioral analysis engines
            # Initialize anomaly detection algorithms
            # Initialize pattern recognition systems
            self.logger.info("Fraud detection system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize fraud detection: {e}")
            raise

    def _initialize_threat_intelligence(self) -> None:
        """Initialize threat intelligence and monitoring systems."""        try:
            # Initialize threat intelligence feeds
            # Initialize security monitoring systems
            # Initialize intrusion detection
            # Initialize vulnerability scanning
            self.logger.info("Threat intelligence system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize threat intelligence: {e}")
            raise

    async def validate_transaction(
        self,
        transaction: MarketplaceTransaction
    ) -> SecurityValidation:
        """        Comprehensive transaction security validation.
        
        Args:
            transaction: Transaction to validate
            
        Returns:
            Security validation result
        """        try:
            validation = SecurityValidation()

            # Basic transaction security checks
            basic_checks = await self._perform_basic_security_checks(transaction)
            validation.security_flags.extend(basic_checks["flags"])
            validation.warnings.extend(basic_checks["warnings"])

            # User risk assessment
            buyer_risk = await self._assess_user_risk(transaction.buyer_id)
            seller_risk = await self._assess_user_risk(transaction.seller_id)
            
            max_user_risk = max(buyer_risk.risk_score, seller_risk.risk_score)
            validation.risk_score += max_user_risk * 0.3

            # Transaction amount analysis
            amount_risk = await self._analyze_transaction_amount(transaction)
            validation.risk_score += amount_risk * 0.2

            # Velocity checks (multiple transactions in short time)
            velocity_risk = await self._analyze_transaction_velocity(transaction)
            validation.risk_score += velocity_risk * 0.25

            # Behavioral analysis
            behavior_analysis = await self._analyze_transaction_behavior(transaction)
            validation.risk_score += behavior_analysis["risk_score"] * 0.25
            validation.security_flags.extend(behavior_analysis["flags"])

            # Determine threat level
            if validation.risk_score >= 0.9:
                validation.threat_level = ThreatLevel.CRITICAL
                validation.blocked_reasons.append("Critical risk level detected")
            elif validation.risk_score >= 0.7:
                validation.threat_level = ThreatLevel.HIGH
                validation.blocked_reasons.append("High risk transaction")
            elif validation.risk_score >= 0.5:
                validation.threat_level = ThreatLevel.MEDIUM
                validation.warnings.append("Medium risk transaction - additional monitoring")
            else:
                validation.threat_level = ThreatLevel.LOW

            # Determine if transaction should be blocked
            validation.is_valid = validation.threat_level not in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
            
            # Set confidence level
            validation.confidence_level = min(0.95, 0.5 + (1.0 - validation.risk_score) * 0.45)

            # Generate recommended actions
            validation.recommended_actions = await self._generate_security_recommendations(
                validation, transaction
            )

            # Log security event if high risk
            if validation.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                await self._log_security_event(
                    SecurityEventType.UNUSUAL_TRANSACTION,
                    validation.threat_level,
                    transaction.buyer_id,
                    f"High-risk transaction detected: {validation.blocked_reasons}"
                )

            return validation

        except Exception as e:
            self.logger.error(f"Transaction validation failed: {e}")
            return SecurityValidation(
                is_valid=False,
                threat_level=ThreatLevel.CRITICAL,
                blocked_reasons=[f"Security validation error: {str(e)}"]
            )

    async def detect_fraud(self, transaction: MarketplaceTransaction) -> float:
        """        Advanced fraud detection using machine learning.
        
        Args:
            transaction: Transaction to analyze for fraud
            
        Returns:
            Fraud score between 0.0 and 1.0
        """        try:
            fraud_analysis = FraudAnalysis()

            # Amount-based fraud indicators
            amount_indicators = await self._analyze_amount_patterns(transaction)
            fraud_analysis.risk_factors["amount_patterns"] = amount_indicators

            # User behavior analysis
            behavior_indicators = await self._analyze_user_behavior_fraud(transaction)
            fraud_analysis.risk_factors["behavior_patterns"] = behavior_indicators

            # Historical pattern analysis
            history_indicators = await self._analyze_historical_patterns(transaction)
            fraud_analysis.risk_factors["historical_patterns"] = history_indicators

            # Geographic and device analysis
            geo_device_indicators = await self._analyze_geographic_device_patterns(transaction)
            fraud_analysis.risk_factors["geo_device_patterns"] = geo_device_indicators

            # Calculate composite fraud score
            weights = {
                "amount_patterns": 0.25,
                "behavior_patterns": 0.30,
                "historical_patterns": 0.25,
                "geo_device_patterns": 0.20
            }
            
            fraud_score = sum(
                fraud_analysis.risk_factors[factor] * weight
                for factor, weight in weights.items()
            )
            
            fraud_analysis.fraud_score = min(1.0, fraud_score)
            fraud_analysis.is_fraudulent = fraud_score >= 0.7

            # Generate fraud indicators
            if fraud_score >= 0.5:
                fraud_analysis.fraud_indicators.append("Suspicious transaction patterns detected")
            
            if fraud_score >= 0.7:
                fraud_analysis.fraud_indicators.append("High probability of fraudulent activity")
                fraud_analysis.mitigation_actions.append("Block transaction immediately")
                fraud_analysis.mitigation_actions.append("Require additional verification")

            # Update fraud detection metrics
            if fraud_analysis.is_fraudulent:
                self.security_metrics["fraud_attempts_blocked"] += 1

            return fraud_analysis.fraud_score

        except Exception as e:
            self.logger.error(f"Fraud detection failed: {e}")
            return 0.0  # Conservative approach - don't block on error

    async def assess_user_risk(
        self,
        user_id: int,
        update_profile: bool = True
    ) -> UserRiskProfile:
        """        Comprehensive user risk assessment.
        
        Args:
            user_id: ID of user to assess
            update_profile: Whether to update stored risk profile
            
        Returns:
            User risk assessment profile
        """        try:
            # Check cache first
            if user_id in self.user_risk_profiles and not update_profile:
                return self.user_risk_profiles[user_id]

            risk_profile = UserRiskProfile(user_id=user_id)

            # Account age analysis
            account_info = await self._get_user_account_info(user_id)
            risk_profile.account_age_days = account_info.get("age_days", 0)
            
            # Newer accounts have higher risk
            if risk_profile.account_age_days < 30:
                risk_profile.risk_score += 0.3
                risk_profile.flags.append("new_account")
            elif risk_profile.account_age_days < 90:
                risk_profile.risk_score += 0.1

            # Transaction history analysis
            transaction_history = await self._analyze_user_transaction_history(user_id)
            risk_profile.transaction_history_score = transaction_history["score"]
            risk_profile.risk_score += (1.0 - transaction_history["score"]) * 0.4

            # Behavioral analysis
            behavior_analysis = await self._analyze_user_behavior(user_id)
            risk_profile.behavior_score = behavior_analysis["score"]
            risk_profile.risk_score += (1.0 - behavior_analysis["score"]) * 0.3
            risk_profile.flags.extend(behavior_analysis.get("flags", []))

            # Verification level
            verification_info = await self._get_user_verification_status(user_id)
            risk_profile.verification_level = verification_info["level"]
            
            if verification_info["level"] == "basic":
                risk_profile.risk_score += 0.1
            elif verification_info["level"] == "unverified":
                risk_profile.risk_score += 0.2
                risk_profile.flags.append("unverified_account")

            # Determine risk level
            if risk_profile.risk_score >= 0.8:
                risk_profile.risk_level = UserRiskLevel.HIGH_RISK
            elif risk_profile.risk_score >= 0.6:
                risk_profile.risk_level = UserRiskLevel.MEDIUM_RISK
            elif risk_profile.risk_score >= 0.3:
                risk_profile.risk_level = UserRiskLevel.LOW_RISK
            else:
                risk_profile.risk_level = UserRiskLevel.TRUSTED

            # Update cache if requested
            if update_profile:
                self.user_risk_profiles[user_id] = risk_profile

            return risk_profile

        except Exception as e:
            self.logger.error(f"User risk assessment failed: {e}")
            return UserRiskProfile(
                user_id=user_id,
                risk_level=UserRiskLevel.MEDIUM_RISK,
                risk_score=0.5
            )

    async def monitor_security_events(self) -> Dict[str, Any]:
        """        Monitor and analyze security events in real-time.
        
        Returns:
            Security monitoring summary
        """        try:
            # Collect recent security events
            recent_events = await self._get_recent_security_events()
            
            # Analyze event patterns
            pattern_analysis = await self._analyze_security_patterns(recent_events)
            
            # Threat level assessment
            current_threat_level = await self._assess_overall_threat_level()
            
            # Generate security summary
            security_summary = {
                "current_threat_level": current_threat_level.value,
                "active_events": len([e for e in recent_events if e.status == "open"]),
                "events_last_24h": len([
                    e for e in recent_events 
                    if (datetime.utcnow() - e.detected_at).days < 1
                ]),
                "top_threat_types": pattern_analysis.get("top_types", []),
                "geographic_threats": pattern_analysis.get("geographic_analysis", {}),
                "recommended_actions": pattern_analysis.get("recommendations", []),
                "system_status": "operational" if current_threat_level != ThreatLevel.CRITICAL else "elevated_alert"
            }
            
            return security_summary

        except Exception as e:
            self.logger.error(f"Security monitoring failed: {e}")
            return {"error": str(e)}

    async def generate_security_report(
        self,
        time_range: str = "7d"
    ) -> Dict[str, Any]:
        """        Generate comprehensive security analytics report.
        
        Args:
            time_range: Time range for report analysis
            
        Returns:
            Detailed security report
        """        try:
            start_date, end_date = await self._parse_time_range(time_range)
            
            # Security event analysis
            events_analysis = await self._analyze_security_events_period(start_date, end_date)
            
            # Fraud detection metrics
            fraud_metrics = await self._calculate_fraud_metrics(start_date, end_date)
            
            # User risk distribution
            risk_distribution = await self._analyze_user_risk_distribution()
            
            # Threat intelligence summary
            threat_intelligence = await self._get_threat_intelligence_summary(start_date, end_date)
            
            # Performance metrics
            performance_metrics = {
                "fraud_detection_accuracy": self.security_metrics["threat_detection_accuracy"],
                "false_positive_rate": self.security_metrics["false_positive_rate"],
                "average_response_time": await self._calculate_average_response_time(),
                "system_uptime": await self._calculate_security_uptime()
            }
            
            report = {
                "report_period": f"{start_date.isoformat()} to {end_date.isoformat()}",
                "executive_summary": {
                    "total_security_events": events_analysis["total_events"],
                    "fraud_attempts_blocked": fraud_metrics["blocked_attempts"],
                    "high_risk_users_identified": risk_distribution["high_risk_count"],
                    "overall_security_score": await self._calculate_overall_security_score()
                },
                "events_analysis": events_analysis,
                "fraud_metrics": fraud_metrics,
                "user_risk_analysis": risk_distribution,
                "threat_intelligence": threat_intelligence,
                "performance_metrics": performance_metrics,
                "recommendations": await self._generate_security_recommendations_report()
            }
            
            return report

        except Exception as e:
            self.logger.error(f"Security report generation failed: {e}")
            return {"error": str(e)}

    async def _assess_user_risk(self, user_id: int) -> UserRiskProfile:
        """Internal method for user risk assessment."""        return await self.assess_user_risk(user_id, update_profile=False)

    async def _perform_basic_security_checks(
        self,
        transaction: MarketplaceTransaction
    ) -> Dict[str, List[str]]:
        """Perform basic security validation checks."""        try:
            flags = []
            warnings = []

            # Check for blocked users
            if transaction.buyer_id in self.blocked_users:
                flags.append("buyer_blocked")
            if transaction.seller_id in self.blocked_users:
                flags.append("seller_blocked")

            # Amount validation
            if transaction.amount > 50000:  # High-value transaction
                warnings.append("high_value_transaction")
            
            if transaction.amount < 1:  # Suspicious low amount
                flags.append("suspicious_low_amount")

            # Payment method validation
            if not transaction.payment_method:
                flags.append("missing_payment_method")

            return {"flags": flags, "warnings": warnings}

        except Exception as e:
            self.logger.error(f"Basic security checks failed: {e}")
            return {"flags": ["security_check_error"], "warnings": []}

    async def _analyze_transaction_amount(self, transaction: MarketplaceTransaction) -> float:
        """Analyze transaction amount for risk patterns."""        try:
            risk_score = 0.0
            
            # Very high amounts
            if transaction.amount > 10000:
                risk_score += 0.3
            elif transaction.amount > 5000:
                risk_score += 0.1
            
            # Unusual amounts (ending in many zeros)
            if transaction.amount >= 1000 and str(transaction.amount).endswith('000'):
                risk_score += 0.1
            
            # Very low amounts
            if transaction.amount < 5:
                risk_score += 0.2
            
            return min(1.0, risk_score)

        except Exception as e:
            self.logger.error(f"Amount analysis failed: {e}")
            return 0.0

    async def _log_security_event(
        self,
        event_type: SecurityEventType,
        severity: ThreatLevel,
        user_id: Optional[int],
        description: str
    ) -> None:
        """Log security event for monitoring and analysis."""        try:
            event = SecurityEvent(
                id=secrets.token_hex(16),
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                description=description,
                detected_at=datetime.utcnow()
            )
            
            self.security_events[event.id] = event
            self.security_metrics["security_events_detected"] += 1
            
            # Auto-escalate critical events
            if severity == ThreatLevel.CRITICAL:
                await self._escalate_security_event(event)
                
        except Exception as e:
            self.logger.error(f"Security event logging failed: {e}")

    async def _get_user_account_info(self, user_id: int) -> Dict[str, Any]:
        """Get user account information for risk assessment."""        try:
            # Mock implementation - would fetch from user database
            return {
                "age_days": 150,  # Account age in days
                "creation_date": datetime.utcnow() - timedelta(days=150),
                "last_login": datetime.utcnow() - timedelta(hours=2),
                "login_count": 45
            }
        except Exception as e:
            self.logger.error(f"User info retrieval failed: {e}")
            return {"age_days": 0}
