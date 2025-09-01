"""Advanced Fraud Detection for Payments
Machine learning-based fraud detection system with real-time analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import json
import hashlib
import re

logger = logging.getLogger(__name__)


class FraudRiskLevel(Enum):
    """Fraud risk levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class FraudCheckType(Enum):
    """Types of fraud checks"""
    VELOCITY = "velocity"
    GEOLOCATION = "geolocation"
    DEVICE_FINGERPRINT = "device_fingerprint"
    BEHAVIORAL = "behavioral"
    PATTERN = "pattern"
    BIN_CHECK = "bin_check"
    BLACKLIST = "blacklist"
    ML_MODEL = "ml_model"


class FraudAction(Enum):
    """Actions to take based on fraud detection"""
    ALLOW = "allow"
    REVIEW = "review"
    CHALLENGE = "challenge"
    BLOCK = "block"
    DENY = "deny"


@dataclass
class FraudCheck:
    """Individual fraud check result"""
    check_type: FraudCheckType
    risk_score: float  # 0-100
    risk_level: FraudRiskLevel
    details: Dict[str, Any]
    passed: bool
    reason: Optional[str] = None


@dataclass
class FraudAnalysis:
    """Complete fraud analysis result"""
    transaction_id: str
    customer_id: str
    overall_risk_score: float
    overall_risk_level: FraudRiskLevel
    recommended_action: FraudAction
    checks: List[FraudCheck]
    analysis_time: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DeviceFingerprint:
    """Device fingerprinting data"""
    device_id: str
    ip_address: str
    user_agent: str
    screen_resolution: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    platform: Optional[str] = None
    browser: Optional[str] = None
    fingerprint_hash: Optional[str] = None
    
    def __post_init__(self):
        if not self.fingerprint_hash:
            self.fingerprint_hash = self._generate_fingerprint()
    
    def _generate_fingerprint(self) -> str:
        """Generate unique device fingerprint hash"""
        components = [
            self.ip_address,
            self.user_agent,
            self.screen_resolution or "",
            self.timezone or "",
            self.language or "",
            self.platform or "",
            self.browser or ""
        ]
        fingerprint_string = "|".join(components)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()


@dataclass
class TransactionContext:
    """Transaction context for fraud analysis"""
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    payment_method: str
    merchant_category: str
    device_fingerprint: DeviceFingerprint
    billing_address: Optional[Dict[str, str]] = None
    shipping_address: Optional[Dict[str, str]] = None
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class FraudDetectionEngine:
    """Advanced fraud detection system"""
    
    def __init__(self):
        self.fraud_rules = self._initialize_fraud_rules()
        self.blacklisted_devices = set()
        self.blacklisted_ips = set()
        self.blacklisted_emails = set()
        self.velocity_tracking = {}  # customer_id -> transactions
        self.device_history = {}  # device_id -> usage history
        self.geographical_patterns = {}  # customer_id -> location history
        self.ml_model_weights = self._initialize_ml_weights()
    
    def _initialize_fraud_rules(self) -> Dict[str, Any]:
        """Initialize fraud detection rules"""
        return {
            "velocity_limits": {
                "max_transactions_per_hour": 10,
                "max_transactions_per_day": 50,
                "max_amount_per_hour": Decimal("1000.00"),
                "max_amount_per_day": Decimal("5000.00")
            },
            "amount_thresholds": {
                "review_threshold": Decimal("500.00"),
                "high_risk_threshold": Decimal("1000.00"),
                "critical_threshold": Decimal("2500.00")
            },
            "geographical_rules": {
                "max_distance_km": 1000,  # Max distance between transactions
                "time_window_hours": 1    # Time window for distance check
            },
            "behavioral_patterns": {
                "unusual_hour_score": 20,
                "weekend_transaction_score": 10,
                "multiple_failed_attempts_score": 50
            },
            "device_rules": {
                "new_device_score": 30,
                "suspicious_user_agent_score": 40,
                "tor_proxy_score": 80
            }
        }
    
    def _initialize_ml_weights(self) -> Dict[str, float]:
        """Initialize ML model weights for fraud scoring"""
        return {
            "amount_factor": 0.2,
            "velocity_factor": 0.25,
            "device_factor": 0.15,
            "geographical_factor": 0.2,
            "behavioral_factor": 0.1,
            "pattern_factor": 0.1
        }
    
    async def analyze_transaction(self, context: TransactionContext) -> FraudAnalysis:
        """Perform comprehensive fraud analysis on transaction"""
        try:
            checks = []
            start_time = datetime.now()
            
            # Run all fraud checks
            velocity_check = await self._check_velocity_limits(context)
            checks.append(velocity_check)
            
            geo_check = await self._check_geographical_anomalies(context)
            checks.append(geo_check)
            
            device_check = await self._check_device_fingerprint(context)
            checks.append(device_check)
            
            behavioral_check = await self._check_behavioral_patterns(context)
            checks.append(behavioral_check)
            
            pattern_check = await self._check_transaction_patterns(context)
            checks.append(pattern_check)
            
            blacklist_check = await self._check_blacklists(context)
            checks.append(blacklist_check)
            
            ml_check = await self._ml_fraud_scoring(context)
            checks.append(ml_check)
            
            # Calculate overall risk score
            overall_score = self._calculate_overall_risk_score(checks)
            overall_level = self._determine_risk_level(overall_score)
            recommended_action = self._determine_action(overall_level, checks)
            
            analysis = FraudAnalysis(
                transaction_id=context.transaction_id,
                customer_id=context.customer_id,
                overall_risk_score=overall_score,
                overall_risk_level=overall_level,
                recommended_action=recommended_action,
                checks=checks,
                analysis_time=start_time,
                metadata={
                    "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "checks_performed": len(checks),
                    "amount": float(context.amount),
                    "currency": context.currency
                }
            )
            
            # Update tracking data
            await self._update_tracking_data(context, analysis)
            
            logger.info(f"Fraud analysis completed: {context.transaction_id} - {overall_level.value}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in fraud analysis: {str(e)}")
            # Return safe default analysis
            return FraudAnalysis(
                transaction_id=context.transaction_id,
                customer_id=context.customer_id,
                overall_risk_score=50.0,
                overall_risk_level=FraudRiskLevel.MEDIUM,
                recommended_action=FraudAction.REVIEW,
                checks=[],
                analysis_time=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def _check_velocity_limits(self, context: TransactionContext) -> FraudCheck:
        """Check transaction velocity limits"""
        try:
            customer_id = context.customer_id
            now = context.timestamp
            
            # Get recent transactions
            if customer_id not in self.velocity_tracking:
                self.velocity_tracking[customer_id] = []
            
            recent_transactions = self.velocity_tracking[customer_id]
            
            # Count transactions in last hour and day
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(days=1)
            
            hour_count = sum(1 for t in recent_transactions if t["timestamp"] >= hour_ago)
            day_count = sum(1 for t in recent_transactions if t["timestamp"] >= day_ago)
            
            hour_amount = sum(t["amount"] for t in recent_transactions if t["timestamp"] >= hour_ago)
            day_amount = sum(t["amount"] for t in recent_transactions if t["timestamp"] >= day_ago)
            
            # Check limits
            risk_score = 0
            reasons = []
            
            rules = self.fraud_rules["velocity_limits"]
            
            if hour_count >= rules["max_transactions_per_hour"]:
                risk_score += 40
                reasons.append(f"Too many transactions per hour: {hour_count}")
            
            if day_count >= rules["max_transactions_per_day"]:
                risk_score += 30
                reasons.append(f"Too many transactions per day: {day_count}")
            
            if hour_amount >= rules["max_amount_per_hour"]:
                risk_score += 35
                reasons.append(f"Amount limit exceeded per hour: {hour_amount}")
            
            if day_amount >= rules["max_amount_per_day"]:
                risk_score += 25
                reasons.append(f"Amount limit exceeded per day: {day_amount}")
            
            return FraudCheck(
                check_type=FraudCheckType.VELOCITY,
                risk_score=min(risk_score, 100),
                risk_level=self._determine_risk_level(risk_score),
                details={
                    "hour_count": hour_count,
                    "day_count": day_count,
                    "hour_amount": float(hour_amount),
                    "day_amount": float(day_amount),
                    "limits": rules
                },
                passed=risk_score < 50,
                reason="; ".join(reasons) if reasons else None
            )
            
        except Exception as e:
            logger.error(f"Error in velocity check: {str(e)}")
            return FraudCheck(
                check_type=FraudCheckType.VELOCITY,
                risk_score=30,
                risk_level=FraudRiskLevel.MEDIUM,
                details={"error": str(e)},
                passed=False,
                reason="Velocity check failed"
            )
    
    async def _check_geographical_anomalies(self, context: TransactionContext) -> FraudCheck:
        """Check for geographical anomalies"""
        try:
            customer_id = context.customer_id
            current_ip = context.device_fingerprint.ip_address
            
            # Get IP geolocation (simplified - in production use real geolocation API)
            current_location = await self._get_ip_location(current_ip)
            
            # Check customer's location history
            if customer_id not in self.geographical_patterns:
                self.geographical_patterns[customer_id] = []
            
            location_history = self.geographical_patterns[customer_id]
            
            risk_score = 0
            reasons = []
            
            if location_history:
                # Check distance from recent locations
                recent_locations = [
                    loc for loc in location_history 
                    if loc["timestamp"] >= context.timestamp - timedelta(hours=24)
                ]
                
                if recent_locations:
                    last_location = recent_locations[-1]
                    distance = self._calculate_distance(
                        current_location, last_location["location"]
                    )
                    
                    time_diff_hours = (
                        context.timestamp - last_location["timestamp"]
                    ).total_seconds() / 3600
                    
                    # Check if distance is suspicious for time elapsed
                    max_reasonable_speed = 1000  # km/h (accounting for flights)
                    max_distance = max_reasonable_speed * time_diff_hours
                    
                    if distance > max_distance and time_diff_hours < 6:
                        risk_score += 60
                        reasons.append(f"Impossible travel: {distance}km in {time_diff_hours}h")
                    elif distance > 500 and time_diff_hours < 2:
                        risk_score += 40
                        reasons.append(f"Unusual travel pattern: {distance}km in {time_diff_hours}h")
                
                # Check for new country
                if current_location["country"] not in [
                    loc["location"]["country"] for loc in location_history[-10:]
                ]:
                    risk_score += 25
                    reasons.append(f"New country: {current_location['country']}")
            else:
                # New customer, lower risk
                risk_score += 10
                reasons.append("New customer location")
            
            return FraudCheck(
                check_type=FraudCheckType.GEOLOCATION,
                risk_score=min(risk_score, 100),
                risk_level=self._determine_risk_level(risk_score),
                details={
                    "current_location": current_location,
                    "location_history_count": len(location_history),
                    "new_location": len(location_history) == 0
                },
                passed=risk_score < 50,
                reason="; ".join(reasons) if reasons else None
            )
            
        except Exception as e:
            logger.error(f"Error in geographical check: {str(e)}")
            return FraudCheck(
                check_type=FraudCheckType.GEOLOCATION,
                risk_score=20,
                risk_level=FraudRiskLevel.LOW,
                details={"error": str(e)},
                passed=True,
                reason="Geographical check failed"
            )
    
    async def _check_device_fingerprint(self, context: TransactionContext) -> FraudCheck:
        """Check device fingerprint for fraud indicators"""
        try:
            device = context.device_fingerprint
            device_id = device.device_id
            
            risk_score = 0
            reasons = []
            
            # Check if device is blacklisted
            if device.fingerprint_hash in self.blacklisted_devices:
                risk_score += 90
                reasons.append("Device is blacklisted")
            
            # Check IP address
            if device.ip_address in self.blacklisted_ips:
                risk_score += 80
                reasons.append("IP address is blacklisted")
            
            # Check for suspicious user agent
            if self._is_suspicious_user_agent(device.user_agent):
                risk_score += 40
                reasons.append("Suspicious user agent")
            
            # Check for automation/bot indicators
            if self._detect_automation(device):
                risk_score += 70
                reasons.append("Automation detected")
            
            # Check device history
            if device_id not in self.device_history:
                self.device_history[device_id] = []
                risk_score += 20
                reasons.append("New device")
            else:
                device_hist = self.device_history[device_id]
                
                # Check for rapid successive transactions
                recent_uses = [
                    use for use in device_hist
                    if use["timestamp"] >= context.timestamp - timedelta(minutes=30)
                ]
                
                if len(recent_uses) > 5:
                    risk_score += 35
                    reasons.append("Too many rapid transactions from device")
            
            # Check for proxy/VPN/Tor usage
            if await self._detect_proxy_usage(device.ip_address):
                risk_score += 50
                reasons.append("Proxy/VPN/Tor usage detected")
            
            return FraudCheck(
                check_type=FraudCheckType.DEVICE_FINGERPRINT,
                risk_score=min(risk_score, 100),
                risk_level=self._determine_risk_level(risk_score),
                details={
                    "device_fingerprint": device.fingerprint_hash[:12] + "...",
                    "is_new_device": device_id not in self.device_history,
                    "user_agent": device.user_agent[:50] + "..." if len(device.user_agent) > 50 else device.user_agent,
                    "ip_address": device.ip_address
                },
                passed=risk_score < 50,
                reason="; ".join(reasons) if reasons else None
            )
            
        except Exception as e:
            logger.error(f"Error in device fingerprint check: {str(e)}")
            return FraudCheck(
                check_type=FraudCheckType.DEVICE_FINGERPRINT,
                risk_score=25,
                risk_level=FraudRiskLevel.LOW,
                details={"error": str(e)},
                passed=True,
                reason="Device fingerprint check failed"
            )
    
    async def _check_behavioral_patterns(self, context: TransactionContext) -> FraudCheck:
        """Analyze behavioral patterns for fraud detection"""
        try:
            risk_score = 0
            reasons = []
            
            # Check transaction timing
            hour = context.timestamp.hour
            if hour < 6 or hour > 23:  # Unusual hours
                risk_score += 15
                reasons.append(f"Unusual transaction hour: {hour}")
            
            # Check if weekend transaction (might be unusual for business)
            if context.timestamp.weekday() >= 5:  # Saturday or Sunday
                risk_score += 5
                reasons.append("Weekend transaction")
            
            # Check amount patterns
            amount = context.amount
            amount_thresholds = self.fraud_rules["amount_thresholds"]
            
            if amount >= amount_thresholds["critical_threshold"]:
                risk_score += 40
                reasons.append(f"Critical amount threshold: {amount}")
            elif amount >= amount_thresholds["high_risk_threshold"]:
                risk_score += 25
                reasons.append(f"High amount threshold: {amount}")
            elif amount >= amount_thresholds["review_threshold"]:
                risk_score += 10
                reasons.append(f"Review amount threshold: {amount}")
            
            # Check for round amounts (potentially suspicious)
            if amount % 100 == 0 and amount >= 500:
                risk_score += 15
                reasons.append("Round amount transaction")
            
            # Check payment method risk
            if context.payment_method in ["prepaid_card", "gift_card"]:
                risk_score += 30
                reasons.append(f"High-risk payment method: {context.payment_method}")
            
            return FraudCheck(
                check_type=FraudCheckType.BEHAVIORAL,
                risk_score=min(risk_score, 100),
                risk_level=self._determine_risk_level(risk_score),
                details={
                    "transaction_hour": hour,
                    "is_weekend": context.timestamp.weekday() >= 5,
                    "amount": float(amount),
                    "payment_method": context.payment_method,
                    "is_round_amount": amount % 100 == 0
                },
                passed=risk_score < 50,
                reason="; ".join(reasons) if reasons else None
            )
            
        except Exception as e:
            logger.error(f"Error in behavioral check: {str(e)}")
            return FraudCheck(
                check_type=FraudCheckType.BEHAVIORAL,
                risk_score=15,
                risk_level=FraudRiskLevel.LOW,
                details={"error": str(e)},
                passed=True,
                reason="Behavioral check failed"
            )
    
    async def _check_transaction_patterns(self, context: TransactionContext) -> FraudCheck:
        """Check for suspicious transaction patterns"""
        try:
            customer_id = context.customer_id
            risk_score = 0
            reasons = []
            
            # Get customer transaction history
            if customer_id in self.velocity_tracking:
                recent_transactions = self.velocity_tracking[customer_id]
                
                # Check for amount escalation pattern
                if len(recent_transactions) >= 3:
                    recent_amounts = [t["amount"] for t in recent_transactions[-3:]]
                    if all(recent_amounts[i] < recent_amounts[i+1] for i in range(len(recent_amounts)-1)):
                        if context.amount > recent_amounts[-1] * 2:
                            risk_score += 35
                            reasons.append("Suspicious amount escalation pattern")
                
                # Check for repeated exact amounts
                exact_matches = sum(1 for t in recent_transactions if t["amount"] == context.amount)
                if exact_matches >= 3:
                    risk_score += 25
                    reasons.append(f"Repeated exact amount: {exact_matches} times")
                
                # Check for frequency spikes
                last_hour_count = sum(
                    1 for t in recent_transactions 
                    if t["timestamp"] >= context.timestamp - timedelta(hours=1)
                )
                if last_hour_count >= 5:
                    risk_score += 30
                    reasons.append(f"High frequency: {last_hour_count} transactions in 1 hour")
            
            # Check for suspicious merchant categories
            if context.merchant_category in ["gambling", "adult", "cryptocurrency"]:
                risk_score += 20
                reasons.append(f"High-risk merchant category: {context.merchant_category}")
            
            return FraudCheck(
                check_type=FraudCheckType.PATTERN,
                risk_score=min(risk_score, 100),
                risk_level=self._determine_risk_level(risk_score),
                details={
                    "merchant_category": context.merchant_category,
                    "transaction_count": len(self.velocity_tracking.get(customer_id, [])),
                    "amount": float(context.amount)
                },
                passed=risk_score < 50,
                reason="; ".join(reasons) if reasons else None
            )
            
        except Exception as e:
            logger.error(f"Error in pattern check: {str(e)}")
            return FraudCheck(
                check_type=FraudCheckType.PATTERN,
                risk_score=10,
                risk_level=FraudRiskLevel.LOW,
                details={"error": str(e)},
                passed=True,
                reason="Pattern check failed"
            )
    
    async def _check_blacklists(self, context: TransactionContext) -> FraudCheck:
        """Check against various blacklists"""
        try:
            risk_score = 0
            reasons = []
            
            # Check customer blacklist (would be loaded from database)
            customer_email = context.metadata.get("email", "") if context.metadata else ""
            if customer_email in self.blacklisted_emails:
                risk_score += 95
                reasons.append("Customer email is blacklisted")
            
            # Check device blacklist
            device_hash = context.device_fingerprint.fingerprint_hash
            if device_hash in self.blacklisted_devices:
                risk_score += 90
                reasons.append("Device is blacklisted")
            
            # Check IP blacklist
            if context.device_fingerprint.ip_address in self.blacklisted_ips:
                risk_score += 85
                reasons.append("IP address is blacklisted")
            
            # Check BIN (Bank Identification Number) if available
            payment_method_id = context.metadata.get("payment_method_id", "") if context.metadata else ""
            if payment_method_id and await self._check_bin_reputation(payment_method_id):
                risk_score += 40
                reasons.append("Suspicious payment method BIN")
            
            return FraudCheck(
                check_type=FraudCheckType.BLACKLIST,
                risk_score=min(risk_score, 100),
                risk_level=self._determine_risk_level(risk_score),
                details={
                    "email_checked": bool(customer_email),
                    "device_checked": True,
                    "ip_checked": True,
                    "bin_checked": bool(payment_method_id)
                },
                passed=risk_score < 50,
                reason="; ".join(reasons) if reasons else None
            )
            
        except Exception as e:
            logger.error(f"Error in blacklist check: {str(e)}")
            return FraudCheck(
                check_type=FraudCheckType.BLACKLIST,
                risk_score=5,
                risk_level=FraudRiskLevel.VERY_LOW,
                details={"error": str(e)},
                passed=True,
                reason="Blacklist check failed"
            )
    
    async def _ml_fraud_scoring(self, context: TransactionContext) -> FraudCheck:
        """Machine learning based fraud scoring"""
        try:
            weights = self.ml_model_weights
            
            # Feature extraction and scoring
            features = {
                "amount_score": self._calculate_amount_score(context.amount),
                "time_score": self._calculate_time_score(context.timestamp),
                "device_score": self._calculate_device_score(context.device_fingerprint),
                "customer_score": self._calculate_customer_score(context.customer_id),
                "pattern_score": self._calculate_pattern_score(context)
            }
            
            # Weighted scoring
            ml_score = (
                features["amount_score"] * weights["amount_factor"] +
                features["time_score"] * weights["behavioral_factor"] +
                features["device_score"] * weights["device_factor"] +
                features["customer_score"] * weights["velocity_factor"] +
                features["pattern_score"] * weights["pattern_factor"]
            ) * 100
            
            return FraudCheck(
                check_type=FraudCheckType.ML_MODEL,
                risk_score=min(ml_score, 100),
                risk_level=self._determine_risk_level(ml_score),
                details={
                    "features": features,
                    "weights": weights,
                    "model_version": "1.0"
                },
                passed=ml_score < 60,
                reason="ML model prediction" if ml_score >= 60 else None
            )
            
        except Exception as e:
            logger.error(f"Error in ML fraud scoring: {str(e)}")
            return FraudCheck(
                check_type=FraudCheckType.ML_MODEL,
                risk_score=30,
                risk_level=FraudRiskLevel.MEDIUM,
                details={"error": str(e)},
                passed=True,
                reason="ML model failed"
            )
    
    def _calculate_overall_risk_score(self, checks: List[FraudCheck]) -> float:
        """Calculate overall risk score from individual checks"""
        if not checks:
            return 50.0
        
        # Weighted average with emphasis on highest scoring checks
        scores = [check.risk_score for check in checks]
        scores.sort(reverse=True)
        
        # Weight: 40% highest score, 30% second highest, 20% third, 10% average of rest
        if len(scores) >= 3:
            weighted_score = (
                scores[0] * 0.4 +
                scores[1] * 0.3 +
                scores[2] * 0.2 +
                (sum(scores[3:]) / len(scores[3:]) if len(scores) > 3 else 0) * 0.1
            )
        elif len(scores) == 2:
            weighted_score = scores[0] * 0.6 + scores[1] * 0.4
        else:
            weighted_score = scores[0]
        
        return min(weighted_score, 100.0)
    
    def _determine_risk_level(self, risk_score: float) -> FraudRiskLevel:
        """Determine risk level from score"""
        if risk_score >= 90:
            return FraudRiskLevel.CRITICAL
        elif risk_score >= 75:
            return FraudRiskLevel.VERY_HIGH
        elif risk_score >= 60:
            return FraudRiskLevel.HIGH
        elif risk_score >= 40:
            return FraudRiskLevel.MEDIUM
        elif risk_score >= 20:
            return FraudRiskLevel.LOW
        else:
            return FraudRiskLevel.VERY_LOW
    
    def _determine_action(self, risk_level: FraudRiskLevel, checks: List[FraudCheck]) -> FraudAction:
        """Determine recommended action based on risk level and checks"""
        if risk_level == FraudRiskLevel.CRITICAL:
            return FraudAction.DENY
        elif risk_level == FraudRiskLevel.VERY_HIGH:
            return FraudAction.BLOCK
        elif risk_level == FraudRiskLevel.HIGH:
            return FraudAction.CHALLENGE
        elif risk_level == FraudRiskLevel.MEDIUM:
            return FraudAction.REVIEW
        else:
            return FraudAction.ALLOW
    
    # Helper methods (simplified implementations)
    
    async def _get_ip_location(self, ip_address: str) -> Dict[str, Any]:
        """Get IP geolocation (simplified)"""
        # In production, use real geolocation API
        return {
            "country": "US",
            "region": "California",
            "city": "San Francisco",
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two locations in km"""
        # Simplified distance calculation
        lat_diff = abs(loc1.get("latitude", 0) - loc2.get("latitude", 0))
        lng_diff = abs(loc1.get("longitude", 0) - loc2.get("longitude", 0))
        return (lat_diff + lng_diff) * 111  # Rough km conversion
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""
        suspicious_patterns = [
            r"curl", r"wget", r"python", r"bot", r"crawler", r"scraper"
        ]
        return any(re.search(pattern, user_agent.lower()) for pattern in suspicious_patterns)
    
    def _detect_automation(self, device: DeviceFingerprint) -> bool:
        """Detect automation/bot indicators"""
        return (
            not device.screen_resolution or
            not device.timezone or
            "headless" in device.user_agent.lower()
        )
    
    async def _detect_proxy_usage(self, ip_address: str) -> bool:
        """Detect proxy/VPN/Tor usage"""
        # In production, use real proxy detection service
        return False
    
    async def _check_bin_reputation(self, payment_method_id: str) -> bool:
        """Check BIN reputation"""
        # In production, check against BIN reputation database
        return False
    
    def _calculate_amount_score(self, amount: Decimal) -> float:
        """Calculate risk score based on amount"""
        if amount >= 2500:
            return 0.9
        elif amount >= 1000:
            return 0.7
        elif amount >= 500:
            return 0.5
        elif amount >= 100:
            return 0.3
        else:
            return 0.1
    
    def _calculate_time_score(self, timestamp: datetime) -> float:
        """Calculate risk score based on time"""
        hour = timestamp.hour
        if hour < 6 or hour > 22:
            return 0.7
        elif timestamp.weekday() >= 5:
            return 0.4
        else:
            return 0.2
    
    def _calculate_device_score(self, device: DeviceFingerprint) -> float:
        """Calculate risk score based on device"""
        score = 0.1
        if device.device_id not in self.device_history:
            score += 0.3
        if self._is_suspicious_user_agent(device.user_agent):
            score += 0.4
        return min(score, 1.0)
    
    def _calculate_customer_score(self, customer_id: str) -> float:
        """Calculate risk score based on customer history"""
        if customer_id not in self.velocity_tracking:
            return 0.3  # New customer
        
        transactions = self.velocity_tracking[customer_id]
        if len(transactions) > 50:
            return 0.1  # Established customer
        elif len(transactions) > 10:
            return 0.2
        else:
            return 0.4
    
    def _calculate_pattern_score(self, context: TransactionContext) -> float:
        """Calculate risk score based on patterns"""
        score = 0.1
        if context.merchant_category in ["gambling", "adult"]:
            score += 0.4
        if context.amount % 100 == 0 and context.amount >= 500:
            score += 0.2
        return min(score, 1.0)
    
    async def _update_tracking_data(self, context: TransactionContext, analysis: FraudAnalysis):
        """Update tracking data after analysis"""
        try:
            customer_id = context.customer_id
            
            # Update velocity tracking
            if customer_id not in self.velocity_tracking:
                self.velocity_tracking[customer_id] = []
            
            self.velocity_tracking[customer_id].append({
                "transaction_id": context.transaction_id,
                "amount": context.amount,
                "timestamp": context.timestamp,
                "risk_score": analysis.overall_risk_score
            })
            
            # Keep only last 100 transactions per customer
            if len(self.velocity_tracking[customer_id]) > 100:
                self.velocity_tracking[customer_id] = self.velocity_tracking[customer_id][-100:]
            
            # Update device history
            device_id = context.device_fingerprint.device_id
            if device_id not in self.device_history:
                self.device_history[device_id] = []
            
            self.device_history[device_id].append({
                "transaction_id": context.transaction_id,
                "timestamp": context.timestamp,
                "customer_id": customer_id,
                "risk_score": analysis.overall_risk_score
            })
            
            # Update geographical patterns
            if customer_id not in self.geographical_patterns:
                self.geographical_patterns[customer_id] = []
            
            location = await self._get_ip_location(context.device_fingerprint.ip_address)
            self.geographical_patterns[customer_id].append({
                "location": location,
                "timestamp": context.timestamp,
                "transaction_id": context.transaction_id
            })
            
        except Exception as e:
            logger.error(f"Error updating tracking data: {str(e)}")
    
    async def add_to_blacklist(
        self,
        blacklist_type: str,
        value: str,
        reason: str = "Manual addition"
    ) -> Dict[str, Any]:
        """Add entry to blacklist"""
        try:
            if blacklist_type == "device":
                self.blacklisted_devices.add(value)
            elif blacklist_type == "ip":
                self.blacklisted_ips.add(value)
            elif blacklist_type == "email":
                self.blacklisted_emails.add(value)
            else:
                return {"success": False, "error": "Invalid blacklist type"}
            
            logger.info(f"Added to {blacklist_type} blacklist: {value}")
            return {"success": True, "message": f"Added to {blacklist_type} blacklist"}
            
        except Exception as e:
            logger.error(f"Error adding to blacklist: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_fraud_statistics(self) -> Dict[str, Any]:
        """Get fraud detection statistics"""
        try:
            total_customers = len(self.velocity_tracking)
            total_devices = len(self.device_history)
            
            blacklist_counts = {
                "devices": len(self.blacklisted_devices),
                "ips": len(self.blacklisted_ips),
                "emails": len(self.blacklisted_emails)
            }
            
            return {
                "success": True,
                "statistics": {
                    "total_customers_tracked": total_customers,
                    "total_devices_tracked": total_devices,
                    "blacklist_counts": blacklist_counts,
                    "fraud_rules": self.fraud_rules,
                    "ml_model_version": "1.0"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting fraud statistics: {str(e)}")
            return {"success": False, "error": str(e)}