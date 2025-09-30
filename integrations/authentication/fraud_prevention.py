# -*- coding: utf-8 -*-
"""
IA Chérie Platform - Enterprise Fraud Prevention
Advanced fraud detection and prevention system
Author: IA Chérie Team
Version: 2.0.0
Date: 2024
"""

import logging
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
import re
from collections import defaultdict, deque
import ipaddress

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class FraudType(Enum):
    """Types of fraud"""
    IDENTITY_THEFT = "identity_theft"
    PAYMENT_FRAUD = "payment_fraud"
    ACCOUNT_TAKEOVER = "account_takeover"
    SYNTHETIC_IDENTITY = "synthetic_identity"
    TRANSACTION_FRAUD = "transaction_fraud"
    APPLICATION_FRAUD = "application_fraud"
    SOCIAL_ENGINEERING = "social_engineering"
    PROMO_ABUSE = "promo_abuse"
    CHARGEBACK_FRAUD = "chargeback_fraud"
    FRIENDLY_FRAUD = "friendly_fraud"
    AFFILIATE_FRAUD = "affiliate_fraud"
    CLICK_FRAUD = "click_fraud"
    FAKE_REVIEWS = "fake_reviews"
    COLLUSION = "collusion"

class RiskLevel(Enum):
    """Risk assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"

class FraudStatus(Enum):
    """Fraud case status"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class ActionType(Enum):
    """Fraud prevention actions"""
    ALLOW = "allow"
    REVIEW = "review"
    CHALLENGE = "challenge"
    DENY = "deny"
    BLOCK_USER = "block_user"
    BLOCK_IP = "block_ip"
    FREEZE_ACCOUNT = "freeze_account"
    REQUIRE_VERIFICATION = "require_verification"

@dataclass
class RiskFactor:
    """Individual risk factor"""
    id: str
    name: str
    category: str
    weight: float  # 0.0 - 1.0
    score: float  # Risk contribution
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FraudRule:
    """Fraud detection rule"""
    id: str
    name: str
    description: str
    fraud_type: FraudType
    conditions: List[Dict[str, Any]]
    risk_score: float  # 0.0 - 100.0
    action: ActionType
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class FraudEvent:
    """Detected fraud event"""
    id: str
    user_id: Optional[str]
    session_id: Optional[str]
    transaction_id: Optional[str]
    fraud_type: FraudType
    risk_level: RiskLevel
    risk_score: float  # 0.0 - 100.0
    risk_factors: List[RiskFactor]
    triggered_rules: List[str]
    action_taken: ActionType
    status: FraudStatus = FraudStatus.DETECTED
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_fingerprint: Optional[str] = None
    geolocation: Optional[Dict[str, Any]] = None
    transaction_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserProfile:
    """User behavior profile for fraud detection"""
    user_id: str
    creation_date: datetime
    total_transactions: int = 0
    total_amount: float = 0.0
    average_transaction: float = 0.0
    typical_locations: Set[str] = field(default_factory=set)
    typical_devices: Set[str] = field(default_factory=set)
    typical_hours: Set[int] = field(default_factory=set)
    fraud_history: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    last_activity: Optional[datetime] = None
    verification_level: str = "basic"
    trusted_contacts: Set[str] = field(default_factory=set)

class FraudPreventionSystem:
    """Enterprise Fraud Prevention System"""
    
    def __init__(self):
        """Initialize fraud prevention system"""
        self.fraud_rules: Dict[str, FraudRule] = {}
        self.fraud_events: List[FraudEvent] = []
        self.user_profiles: Dict[str, UserProfile] = {}
        self.blocked_ips: Set[str] = set()
        self.blocked_users: Set[str] = set()
        self.suspicious_patterns: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._event_counter = 0
        
        # Transaction tracking
        self.transaction_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.velocity_tracking: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Device and session tracking
        self.device_sessions: Dict[str, List[str]] = defaultdict(list)
        self.session_activities: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        
        # Initialize fraud rules and patterns
        self._initialize_fraud_rules()
        self._initialize_suspicious_patterns()
        
        logger.info("🛡️ Fraud Prevention System initialized successfully")
    
    def _initialize_fraud_rules(self):
        """Initialize fraud detection rules"""
        rules = [
            # Velocity-based rules
            FraudRule(
                id="velocity_001",
                name="High Transaction Velocity",
                description="Too many transactions in short time",
                fraud_type=FraudType.TRANSACTION_FRAUD,
                conditions=[
                    {"metric": "transaction_count", "threshold": 10, "timeframe": 300},  # 10 in 5 min
                    {"metric": "transaction_amount", "threshold": 5000, "timeframe": 3600}  # $5000 in 1 hour
                ],
                risk_score=75.0,
                action=ActionType.REVIEW
            ),
            
            # Geographic anomaly
            FraudRule(
                id="geo_001",
                name="Geographic Anomaly",
                description="Transaction from unusual location",
                fraud_type=FraudType.ACCOUNT_TAKEOVER,
                conditions=[
                    {"metric": "location_change", "threshold": 500},  # 500+ miles from usual
                    {"metric": "time_since_last", "threshold": 3600}  # Within 1 hour
                ],
                risk_score=60.0,
                action=ActionType.CHALLENGE
            ),
            
            # Device fingerprint mismatch
            FraudRule(
                id="device_001",
                name="Unknown Device",
                description="Transaction from unrecognized device",
                fraud_type=FraudType.ACCOUNT_TAKEOVER,
                conditions=[
                    {"metric": "device_known", "threshold": 0},  # Unknown device
                    {"metric": "transaction_amount", "threshold": 100}  # Above $100
                ],
                risk_score=45.0,
                action=ActionType.CHALLENGE
            ),
            
            # Amount anomaly
            FraudRule(
                id="amount_001",
                name="Unusual Transaction Amount",
                description="Transaction amount significantly different from usual",
                fraud_type=FraudType.PAYMENT_FRAUD,
                conditions=[
                    {"metric": "amount_deviation", "threshold": 5.0},  # 5x normal amount
                    {"metric": "user_history", "threshold": 30}  # At least 30 days history
                ],
                risk_score=55.0,
                action=ActionType.REVIEW
            ),
            
            # Time-based anomaly
            FraudRule(
                id="time_001",
                name="Unusual Transaction Time",
                description="Transaction at unusual time for user",
                fraud_type=FraudType.ACCOUNT_TAKEOVER,
                conditions=[
                    {"metric": "time_unusual", "threshold": 1},  # Outside normal hours
                    {"metric": "transaction_amount", "threshold": 500}  # Above $500
                ],
                risk_score=35.0,
                action=ActionType.CHALLENGE
            ),
            
            # Synthetic identity detection
            FraudRule(
                id="synthetic_001",
                name="Synthetic Identity Indicators",
                description="Patterns indicating synthetic identity",
                fraud_type=FraudType.SYNTHETIC_IDENTITY,
                conditions=[
                    {"metric": "profile_completeness", "threshold": 0.3},  # Incomplete profile
                    {"metric": "verification_failures", "threshold": 2},  # Multiple failures
                    {"metric": "account_age", "threshold": 7}  # Very new account
                ],
                risk_score=80.0,
                action=ActionType.DENY
            ),
            
            # Promo abuse detection
            FraudRule(
                id="promo_001",
                name="Promotion Abuse",
                description="Patterns indicating promo code abuse",
                fraud_type=FraudType.PROMO_ABUSE,
                conditions=[
                    {"metric": "promo_usage", "threshold": 5},  # Multiple promos
                    {"metric": "account_similarity", "threshold": 0.8},  # Similar to other accounts
                    {"metric": "rapid_account_creation", "threshold": 1}
                ],
                risk_score=70.0,
                action=ActionType.BLOCK_USER
            )
        ]
        
        for rule in rules:
            self.fraud_rules[rule.id] = rule
        
        logger.info(f"📋 Initialized {len(rules)} fraud detection rules")
    
    def _initialize_suspicious_patterns(self):
        """Initialize suspicious behavior patterns"""
        self.suspicious_patterns = {
            "rapid_succession": {
                "description": "Multiple actions in rapid succession",
                "threshold": 5,
                "timeframe": 60,  # seconds
                "risk_weight": 0.7
            },
            "round_amounts": {
                "description": "Transactions with round amounts",
                "pattern": r"^\\d+00(\\.00)?$",
                "risk_weight": 0.3
            },
            "sequential_amounts": {
                "description": "Sequential transaction amounts",
                "risk_weight": 0.5
            },
            "midnight_activity": {
                "description": "Activity during unusual hours",
                "hours": [0, 1, 2, 3, 4, 5],
                "risk_weight": 0.4
            },
            "high_failure_rate": {
                "description": "High rate of failed attempts",
                "threshold": 0.5,  # 50% failure rate
                "risk_weight": 0.8
            }
        }
        
        logger.info(f"🔍 Initialized {len(self.suspicious_patterns)} suspicious patterns")
    
    def analyze_transaction(self, transaction_data: Dict[str, Any]) -> FraudEvent:
        """Analyze transaction for fraud indicators"""
        try:
            with self._lock:
                self._event_counter += 1
                event_id = f"fraud_{self._event_counter}_{int(time.time())}"
                
                # Extract transaction details
                user_id = transaction_data.get("user_id")
                amount = float(transaction_data.get("amount", 0))
                currency = transaction_data.get("currency", "USD")
                ip_address = transaction_data.get("ip_address")
                device_id = transaction_data.get("device_id")
                session_id = transaction_data.get("session_id")
                transaction_id = transaction_data.get("transaction_id")
                
                # Get or create user profile
                if user_id:
                    user_profile = self._get_or_create_user_profile(user_id)
                else:
                    user_profile = None
                
                # Calculate risk factors
                risk_factors = self._calculate_risk_factors(transaction_data, user_profile)
                
                # Check fraud rules
                triggered_rules, max_risk_score = self._check_fraud_rules(transaction_data, risk_factors)
                
                # Determine overall risk level and action
                risk_level = self._determine_risk_level(max_risk_score)
                action = self._determine_action(triggered_rules, risk_level)
                
                # Determine fraud type
                fraud_type = self._determine_fraud_type(triggered_rules, risk_factors)
                
                # Create fraud event
                fraud_event = FraudEvent(
                    id=event_id,
                    user_id=user_id,
                    session_id=session_id,
                    transaction_id=transaction_id,
                    fraud_type=fraud_type,
                    risk_level=risk_level,
                    risk_score=max_risk_score,
                    risk_factors=risk_factors,
                    triggered_rules=triggered_rules,
                    action_taken=action,
                    ip_address=ip_address,
                    device_fingerprint=device_id,
                    transaction_data=transaction_data
                )
                
                # Store event
                self.fraud_events.append(fraud_event)
                
                # Update user profile
                if user_profile:
                    self._update_user_profile(user_profile, transaction_data, fraud_event)
                
                # Track transaction history
                self._track_transaction(user_id, ip_address, transaction_data)
                
                # Execute prevention actions
                self._execute_prevention_action(action, fraud_event)
                
                # Log significant events
                if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]:
                    logger.warning(f"🚨 High-risk fraud event: {fraud_type.value} - Risk: {max_risk_score:.1f} - Action: {action.value}")
                
                return fraud_event
                
        except Exception as e:
            logger.error(f"❌ Error analyzing transaction: {str(e)}")
            # Return minimal fraud event for error case
            return FraudEvent(
                id=f"error_{int(time.time())}",
                user_id=transaction_data.get("user_id"),
                fraud_type=FraudType.TRANSACTION_FRAUD,
                risk_level=RiskLevel.MEDIUM,
                risk_score=50.0,
                risk_factors=[],
                triggered_rules=[],
                action_taken=ActionType.REVIEW,
                metadata={"error": str(e)}
            )
    
    def _get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get existing user profile or create new one"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                creation_date=datetime.now()
            )
        return self.user_profiles[user_id]
    
    def _calculate_risk_factors(self, transaction_data: Dict[str, Any], 
                               user_profile: Optional[UserProfile]) -> List[RiskFactor]:
        """Calculate risk factors for transaction"""
        risk_factors = []
        
        try:
            user_id = transaction_data.get("user_id")
            amount = float(transaction_data.get("amount", 0))
            ip_address = transaction_data.get("ip_address")
            device_id = transaction_data.get("device_id")
            current_time = datetime.now()
            
            # IP-based risk factors
            if ip_address:
                if ip_address in self.blocked_ips:
                    risk_factors.append(RiskFactor(
                        id="blocked_ip",
                        name="Blocked IP Address",
                        category="network",
                        weight=1.0,
                        score=100.0,
                        description="Transaction from blocked IP address",
                        evidence={"ip": ip_address}
                    ))
                
                # Check for TOR/VPN usage (simplified check)
                if self._is_suspicious_ip(ip_address):
                    risk_factors.append(RiskFactor(
                        id="suspicious_ip",
                        name="Suspicious IP",
                        category="network",
                        weight=0.6,
                        score=60.0,
                        description="Transaction from potentially suspicious IP",
                        evidence={"ip": ip_address}
                    ))
            
            # User-based risk factors
            if user_profile:
                # Velocity check
                recent_transactions = self._get_recent_transactions(user_id, minutes=60)
                if len(recent_transactions) > 5:
                    risk_factors.append(RiskFactor(
                        id="high_velocity",
                        name="High Transaction Velocity",
                        category="behavior",
                        weight=0.8,
                        score=min(len(recent_transactions) * 10, 100),
                        description=f"{len(recent_transactions)} transactions in last hour",
                        evidence={"transaction_count": len(recent_transactions)}
                    ))
                
                # Amount deviation
                if user_profile.average_transaction > 0:
                    deviation = amount / user_profile.average_transaction
                    if deviation > 5.0:  # More than 5x normal
                        risk_factors.append(RiskFactor(
                            id="amount_deviation",
                            name="Unusual Transaction Amount",
                            category="amount",
                            weight=0.7,
                            score=min(deviation * 10, 100),
                            description=f"Amount {deviation:.1f}x higher than average",
                            evidence={"deviation": deviation, "amount": amount}
                        ))
                
                # Time-based anomaly
                current_hour = current_time.hour
                if user_profile.typical_hours and current_hour not in user_profile.typical_hours:
                    risk_factors.append(RiskFactor(
                        id="unusual_time",
                        name="Unusual Transaction Time",
                        category="temporal",
                        weight=0.4,
                        score=40.0,
                        description=f"Transaction at unusual hour: {current_hour}:00",
                        evidence={"hour": current_hour}
                    ))
                
                # Device anomaly
                if device_id and user_profile.typical_devices and device_id not in user_profile.typical_devices:
                    risk_factors.append(RiskFactor(
                        id="unknown_device",
                        name="Unknown Device",
                        category="device",
                        weight=0.6,
                        score=60.0,
                        description="Transaction from unrecognized device",
                        evidence={"device_id": device_id}
                    ))
            
            # Pattern-based risk factors
            if self._matches_suspicious_pattern(transaction_data):
                risk_factors.append(RiskFactor(
                    id="suspicious_pattern",
                    name="Suspicious Pattern",
                    category="pattern",
                    weight=0.5,
                    score=50.0,
                    description="Transaction matches known suspicious patterns"
                ))
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"❌ Error calculating risk factors: {str(e)}")
            return []
    
    def _check_fraud_rules(self, transaction_data: Dict[str, Any], 
                          risk_factors: List[RiskFactor]) -> Tuple[List[str], float]:
        """Check transaction against fraud rules"""
        triggered_rules = []
        max_risk_score = 0.0
        
        try:
            for rule_id, rule in self.fraud_rules.items():
                if not rule.is_active:
                    continue
                
                if self._rule_matches(rule, transaction_data, risk_factors):
                    triggered_rules.append(rule_id)
                    max_risk_score = max(max_risk_score, rule.risk_score)
            
            # Factor in risk factors
            risk_factor_score = sum(rf.score * rf.weight for rf in risk_factors)
            max_risk_score = max(max_risk_score, min(risk_factor_score, 100.0))
            
            return triggered_rules, max_risk_score
            
        except Exception as e:
            logger.error(f"❌ Error checking fraud rules: {str(e)}")
            return [], 50.0
    
    def _rule_matches(self, rule: FraudRule, transaction_data: Dict[str, Any], 
                     risk_factors: List[RiskFactor]) -> bool:
        """Check if transaction matches a specific fraud rule"""
        try:
            user_id = transaction_data.get("user_id")
            amount = float(transaction_data.get("amount", 0))
            
            for condition in rule.conditions:
                metric = condition["metric"]
                threshold = condition["threshold"]
                
                if metric == "transaction_count":
                    timeframe = condition.get("timeframe", 3600)
                    recent_txns = self._get_recent_transactions(user_id, seconds=timeframe)
                    if len(recent_txns) < threshold:
                        return False
                
                elif metric == "transaction_amount":
                    timeframe = condition.get("timeframe", 3600)
                    recent_txns = self._get_recent_transactions(user_id, seconds=timeframe)
                    total_amount = sum(txn.get("amount", 0) for txn in recent_txns)
                    if total_amount < threshold:
                        return False
                
                elif metric == "amount_deviation":
                    if user_id in self.user_profiles:
                        profile = self.user_profiles[user_id]
                        if profile.average_transaction > 0:
                            deviation = amount / profile.average_transaction
                            if deviation < threshold:
                                return False
                
                elif metric == "device_known":
                    device_id = transaction_data.get("device_id")
                    if user_id in self.user_profiles and device_id:
                        profile = self.user_profiles[user_id]
                        known = 1 if device_id in profile.typical_devices else 0
                        if known > threshold:
                            return False
                
                # Add more condition checks as needed
            
            return True
            
        except Exception:
            return False
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score"""
        if risk_score >= 90:
            return RiskLevel.CRITICAL
        elif risk_score >= 75:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 40:
            return RiskLevel.MEDIUM
        elif risk_score >= 20:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    def _determine_action(self, triggered_rules: List[str], risk_level: RiskLevel) -> ActionType:
        """Determine action based on triggered rules and risk level"""
        # Find the most severe action from triggered rules
        most_severe_action = ActionType.ALLOW
        
        for rule_id in triggered_rules:
            if rule_id in self.fraud_rules:
                rule_action = self.fraud_rules[rule_id].action
                if self._action_severity(rule_action) > self._action_severity(most_severe_action):
                    most_severe_action = rule_action
        
        # Override based on risk level if needed
        if risk_level == RiskLevel.CRITICAL:
            return ActionType.DENY
        elif risk_level == RiskLevel.VERY_HIGH:
            return max(most_severe_action, ActionType.REVIEW, key=self._action_severity)
        
        return most_severe_action
    
    def _action_severity(self, action: ActionType) -> int:
        """Get severity level of action"""
        severity_map = {
            ActionType.ALLOW: 0,
            ActionType.REVIEW: 1,
            ActionType.CHALLENGE: 2,
            ActionType.REQUIRE_VERIFICATION: 3,
            ActionType.DENY: 4,
            ActionType.FREEZE_ACCOUNT: 5,
            ActionType.BLOCK_IP: 6,
            ActionType.BLOCK_USER: 7
        }
        return severity_map.get(action, 0)
    
    def _determine_fraud_type(self, triggered_rules: List[str], 
                             risk_factors: List[RiskFactor]) -> FraudType:
        """Determine most likely fraud type"""
        fraud_types = []
        
        # From triggered rules
        for rule_id in triggered_rules:
            if rule_id in self.fraud_rules:
                fraud_types.append(self.fraud_rules[rule_id].fraud_type)
        
        # From risk factors (simplified logic)
        for factor in risk_factors:
            if "device" in factor.category:
                fraud_types.append(FraudType.ACCOUNT_TAKEOVER)
            elif "amount" in factor.category:
                fraud_types.append(FraudType.PAYMENT_FRAUD)
            elif "network" in factor.category:
                fraud_types.append(FraudType.TRANSACTION_FRAUD)
        
        # Return most common fraud type or default
        if fraud_types:
            return max(set(fraud_types), key=fraud_types.count)
        else:
            return FraudType.TRANSACTION_FRAUD
    
    def _update_user_profile(self, profile: UserProfile, transaction_data: Dict[str, Any], 
                           fraud_event: FraudEvent):
        """Update user profile with transaction data"""
        try:
            amount = float(transaction_data.get("amount", 0))
            ip_address = transaction_data.get("ip_address")
            device_id = transaction_data.get("device_id")
            
            # Update transaction statistics
            profile.total_transactions += 1
            profile.total_amount += amount
            profile.average_transaction = profile.total_amount / profile.total_transactions
            profile.last_activity = datetime.now()
            
            # Update typical patterns
            if ip_address:
                # Simplified location from IP (in production, use proper geolocation)
                location = f"region_{ip_address.split('.')[0]}"
                profile.typical_locations.add(location)
            
            if device_id:
                profile.typical_devices.add(device_id)
            
            current_hour = datetime.now().hour
            profile.typical_hours.add(current_hour)
            
            # Update risk score
            if fraud_event.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]:
                profile.risk_score = min(profile.risk_score + 10, 100)
                profile.fraud_history.append(fraud_event.id)
            else:
                # Gradually decrease risk score for good behavior
                profile.risk_score = max(profile.risk_score - 1, 0)
            
        except Exception as e:
            logger.error(f"❌ Error updating user profile: {str(e)}")
    
    def _track_transaction(self, user_id: Optional[str], ip_address: Optional[str], 
                          transaction_data: Dict[str, Any]):
        """Track transaction for velocity and pattern analysis"""
        try:
            timestamp = datetime.now()
            
            if user_id:
                self.transaction_history[user_id].append({
                    "timestamp": timestamp,
                    "data": transaction_data
                })
                
                self.velocity_tracking[user_id].append(timestamp)
            
            if ip_address:
                self.velocity_tracking[f"ip_{ip_address}"].append(timestamp)
            
        except Exception as e:
            logger.error(f"❌ Error tracking transaction: {str(e)}")
    
    def _execute_prevention_action(self, action: ActionType, fraud_event: FraudEvent):
        """Execute fraud prevention action"""
        try:
            if action == ActionType.BLOCK_USER and fraud_event.user_id:
                self.blocked_users.add(fraud_event.user_id)
                logger.info(f"🚫 Blocked user: {fraud_event.user_id}")
            
            elif action == ActionType.BLOCK_IP and fraud_event.ip_address:
                self.blocked_ips.add(fraud_event.ip_address)
                logger.info(f"🚫 Blocked IP: {fraud_event.ip_address}")
            
            elif action == ActionType.FREEZE_ACCOUNT and fraud_event.user_id:
                # In production, integrate with account management system
                logger.info(f"🧊 Account freeze requested for user: {fraud_event.user_id}")
            
            # Log other actions
            if action != ActionType.ALLOW:
                logger.info(f"🛡️ Fraud prevention action: {action.value} for event {fraud_event.id}")
            
        except Exception as e:
            logger.error(f"❌ Error executing prevention action: {str(e)}")
    
    def _get_recent_transactions(self, user_id: Optional[str], minutes: int = 60, 
                               seconds: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent transactions for user"""
        if not user_id or user_id not in self.transaction_history:
            return []
        
        timeframe = seconds if seconds else minutes * 60
        cutoff_time = datetime.now() - timedelta(seconds=timeframe)
        
        recent = [
            txn["data"] for txn in self.transaction_history[user_id]
            if txn["timestamp"] >= cutoff_time
        ]
        
        return recent
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious (simplified)"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check for private/local addresses
            if ip.is_private or ip.is_loopback:
                return False
            
            # Simplified suspicious IP detection
            # In production, use threat intelligence feeds
            suspicious_ranges = [
                "10.0.0.0/8",    # Example suspicious range
                "192.168.0.0/16"  # Another example
            ]
            
            for range_str in suspicious_ranges:
                if ip in ipaddress.ip_network(range_str):
                    return True
            
            return False
            
        except Exception:
            return True  # Invalid IP is suspicious
    
    def _matches_suspicious_pattern(self, transaction_data: Dict[str, Any]) -> bool:
        """Check if transaction matches suspicious patterns"""
        try:
            amount = str(transaction_data.get("amount", ""))
            
            # Check for round amounts
            if re.match(self.suspicious_patterns["round_amounts"]["pattern"], amount):
                return True
            
            # Check time
            current_hour = datetime.now().hour
            if current_hour in self.suspicious_patterns["midnight_activity"]["hours"]:
                return True
            
            return False
            
        except Exception:
            return False
    
    def get_fraud_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get fraud detection summary"""
        try:
            with self._lock:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                recent_events = [e for e in self.fraud_events if e.detected_at >= cutoff_time]
                
                # Count by fraud type
                type_counts = {}
                for fraud_type in FraudType:
                    type_counts[fraud_type.value] = sum(
                        1 for e in recent_events if e.fraud_type == fraud_type
                    )
                
                # Count by risk level
                risk_counts = {}
                for risk_level in RiskLevel:
                    risk_counts[risk_level.value] = sum(
                        1 for e in recent_events if e.risk_level == risk_level
                    )
                
                # Count by action
                action_counts = {}
                for action in ActionType:
                    action_counts[action.value] = sum(
                        1 for e in recent_events if e.action_taken == action
                    )
                
                return {
                    "period_hours": hours,
                    "total_events": len(recent_events),
                    "fraud_types": type_counts,
                    "risk_levels": risk_counts,
                    "actions_taken": action_counts,
                    "blocked_users": len(self.blocked_users),
                    "blocked_ips": len(self.blocked_ips),
                    "active_rules": sum(1 for r in self.fraud_rules.values() if r.is_active)
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating fraud summary: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old fraud data"""
        try:
            with self._lock:
                cutoff_time = datetime.now() - timedelta(days=days)
                
                # Clean old events
                initial_count = len(self.fraud_events)
                self.fraud_events = [e for e in self.fraud_events if e.detected_at >= cutoff_time]
                
                # Clean old transaction history
                for user_id in list(self.transaction_history.keys()):
                    recent_txns = [
                        txn for txn in self.transaction_history[user_id]
                        if txn["timestamp"] >= cutoff_time
                    ]
                    if recent_txns:
                        self.transaction_history[user_id] = deque(recent_txns, maxlen=1000)
                    else:
                        del self.transaction_history[user_id]
                
                cleaned_count = initial_count - len(self.fraud_events)
                if cleaned_count > 0:
                    logger.info(f"🧹 Cleaned up {cleaned_count} old fraud events (>{days} days)")
                    
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {str(e)}")

# Create global instance
fraud_prevention = FraudPreventionSystem()

# Export main classes and instance
__all__ = [
    'FraudPreventionSystem',
    'FraudEvent',
    'FraudRule',
    'UserProfile',
    'RiskFactor',
    'FraudType',
    'RiskLevel',
    'FraudStatus',
    'ActionType',
    'fraud_prevention'
]