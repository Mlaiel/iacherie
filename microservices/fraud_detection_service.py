"""
🕵️ Fraud Detection Microservice
Advanced payment fraud detection and prevention with AI-powered analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json
import hashlib
import ipaddress
from abc import ABC, abstractmethod
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class FraudRiskLevel(str, Enum):
    """Fraud risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudType(str, Enum):
    """Types of fraud patterns"""
    CARD_FRAUD = "card_fraud"
    IDENTITY_THEFT = "identity_theft"
    ACCOUNT_TAKEOVER = "account_takeover"
    SYNTHETIC_IDENTITY = "synthetic_identity"
    PAYMENT_MANIPULATION = "payment_manipulation"
    CHARGEBACK_FRAUD = "chargeback_fraud"
    VELOCITY_FRAUD = "velocity_fraud"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    GEOLOCATION_FRAUD = "geolocation_fraud"
    DEVICE_FRAUD = "device_fraud"


class ActionType(str, Enum):
    """Fraud prevention actions"""
    ALLOW = "allow"
    CHALLENGE = "challenge"
    BLOCK = "block"
    REVIEW = "review"
    FLAG = "flag"
    REQUIRE_MFA = "require_mfa"


@dataclass
class TransactionData:
    """Transaction information for fraud analysis"""
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    payment_method: str
    merchant_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_fingerprint: Optional[str] = None
    billing_address: Optional[Dict[str, str]] = None
    shipping_address: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    """User profile for behavioral analysis"""
    user_id: str
    registration_date: datetime
    email_verified: bool = False
    phone_verified: bool = False
    kyc_verified: bool = False
    total_transactions: int = 0
    total_amount_spent: float = 0.0
    average_transaction_amount: float = 0.0
    preferred_payment_methods: List[str] = field(default_factory=list)
    typical_locations: List[str] = field(default_factory=list)
    account_changes: int = 0
    last_activity: Optional[datetime] = None
    risk_score: float = 0.0


@dataclass
class FraudAnalysisResult:
    """Result of fraud analysis"""
    transaction_id: str
    risk_score: float
    risk_level: FraudRiskLevel
    detected_fraud_types: List[FraudType]
    recommended_action: ActionType
    confidence: float
    reasons: List[str]
    additional_checks_required: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FraudRule:
    """Fraud detection rule"""
    rule_id: str
    name: str
    description: str
    fraud_type: FraudType
    condition: str  # Rule condition logic
    risk_weight: float  # Weight in overall risk calculation
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class FraudDetectionEngine(ABC):
    """Abstract fraud detection engine"""
    
    @abstractmethod
    async def analyze_transaction(
        self, 
        transaction: TransactionData, 
        user_profile: UserProfile
    ) -> FraudAnalysisResult:
        """Analyze transaction for fraud"""
        pass


class RuleBasedEngine(FraudDetectionEngine):
    """Rule-based fraud detection engine"""
    
    def __init__(self):
        self.rules: List[FraudRule] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default fraud detection rules"""
        default_rules = [
            FraudRule(
                rule_id="high_amount",
                name="High Amount Transaction",
                description="Transaction amount exceeds user's typical spending",
                fraud_type=FraudType.PAYMENT_MANIPULATION,
                condition="amount > user_avg_amount * 10",
                risk_weight=0.3
            ),
            FraudRule(
                rule_id="velocity_check",
                name="High Velocity Transactions",
                description="Multiple transactions in short time period",
                fraud_type=FraudType.VELOCITY_FRAUD,
                condition="transactions_last_hour > 5",
                risk_weight=0.4
            ),
            FraudRule(
                rule_id="new_location",
                name="Unusual Location",
                description="Transaction from new or unusual location",
                fraud_type=FraudType.GEOLOCATION_FRAUD,
                condition="location not in typical_locations",
                risk_weight=0.2
            ),
            FraudRule(
                rule_id="new_device",
                name="New Device",
                description="Transaction from unrecognized device",
                fraud_type=FraudType.DEVICE_FRAUD,
                condition="device_fingerprint not in known_devices",
                risk_weight=0.3
            ),
            FraudRule(
                rule_id="unverified_account",
                name="Unverified Account",
                description="High-value transaction from unverified account",
                fraud_type=FraudType.IDENTITY_THEFT,
                condition="amount > 100 and not kyc_verified",
                risk_weight=0.5
            )
        ]
        
        self.rules.extend(default_rules)
    
    async def analyze_transaction(
        self, 
        transaction: TransactionData, 
        user_profile: UserProfile
    ) -> FraudAnalysisResult:
        """Analyze transaction using rules"""
        
        detected_fraud_types = []
        risk_score = 0.0
        reasons = []
        
        for rule in self.rules:
            if not rule.is_active:
                continue
            
            triggered = await self._evaluate_rule(rule, transaction, user_profile)
            
            if triggered:
                detected_fraud_types.append(rule.fraud_type)
                risk_score += rule.risk_weight
                reasons.append(f"{rule.name}: {rule.description}")
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = FraudRiskLevel.LOW
        elif risk_score < 0.6:
            risk_level = FraudRiskLevel.MEDIUM
        elif risk_score < 0.8:
            risk_level = FraudRiskLevel.HIGH
        else:
            risk_level = FraudRiskLevel.CRITICAL
        
        # Determine recommended action
        if risk_level == FraudRiskLevel.LOW:
            action = ActionType.ALLOW
        elif risk_level == FraudRiskLevel.MEDIUM:
            action = ActionType.CHALLENGE
        elif risk_level == FraudRiskLevel.HIGH:
            action = ActionType.REVIEW
        else:
            action = ActionType.BLOCK
        
        return FraudAnalysisResult(
            transaction_id=transaction.transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            detected_fraud_types=detected_fraud_types,
            recommended_action=action,
            confidence=0.8,  # Rule-based confidence
            reasons=reasons
        )
    
    async def _evaluate_rule(
        self, 
        rule: FraudRule, 
        transaction: TransactionData, 
        user_profile: UserProfile
    ) -> bool:
        """Evaluate if a rule is triggered"""
        
        # Simplified rule evaluation
        if rule.rule_id == "high_amount":
            return transaction.amount > user_profile.average_transaction_amount * 10
        
        elif rule.rule_id == "velocity_check":
            # This would require transaction history
            return False  # Simplified
        
        elif rule.rule_id == "new_location":
            # Check if IP location is in typical locations
            return transaction.ip_address not in user_profile.typical_locations
        
        elif rule.rule_id == "new_device":
            # Check device fingerprint
            return transaction.device_fingerprint not in ["known_device_1", "known_device_2"]
        
        elif rule.rule_id == "unverified_account":
            return transaction.amount > 100 and not user_profile.kyc_verified
        
        return False


class MLFraudEngine(FraudDetectionEngine):
    """Machine learning fraud detection engine"""
    
    def __init__(self):
        self.model_loaded = False
        self.feature_weights = {
            "amount_ratio": 0.3,
            "time_since_last": 0.2,
            "location_risk": 0.2,
            "velocity_score": 0.3
        }
    
    async def analyze_transaction(
        self, 
        transaction: TransactionData, 
        user_profile: UserProfile
    ) -> FraudAnalysisResult:
        """ML-based fraud analysis"""
        
        # Extract features
        features = await self._extract_features(transaction, user_profile)
        
        # Calculate ML risk score
        risk_score = await self._calculate_ml_score(features)
        
        # Determine fraud types based on feature analysis
        detected_fraud_types = await self._identify_fraud_patterns(features)
        
        # Generate explanations
        reasons = await self._generate_explanations(features, detected_fraud_types)
        
        # Determine risk level and action
        if risk_score < 0.2:
            risk_level = FraudRiskLevel.LOW
            action = ActionType.ALLOW
        elif risk_score < 0.5:
            risk_level = FraudRiskLevel.MEDIUM
            action = ActionType.CHALLENGE
        elif risk_score < 0.8:
            risk_level = FraudRiskLevel.HIGH
            action = ActionType.REVIEW
        else:
            risk_level = FraudRiskLevel.CRITICAL
            action = ActionType.BLOCK
        
        return FraudAnalysisResult(
            transaction_id=transaction.transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            detected_fraud_types=detected_fraud_types,
            recommended_action=action,
            confidence=0.92,  # Higher confidence for ML
            reasons=reasons
        )
    
    async def _extract_features(
        self, 
        transaction: TransactionData, 
        user_profile: UserProfile
    ) -> Dict[str, float]:
        """Extract features for ML model"""
        
        features = {}
        
        # Amount-based features
        if user_profile.average_transaction_amount > 0:
            features["amount_ratio"] = transaction.amount / user_profile.average_transaction_amount
        else:
            features["amount_ratio"] = 10.0  # High risk for new users
        
        # Time-based features
        if user_profile.last_activity:
            time_diff = (transaction.timestamp - user_profile.last_activity).total_seconds()
            features["time_since_last"] = min(time_diff / 3600, 24)  # Cap at 24 hours
        else:
            features["time_since_last"] = 24.0
        
        # Account verification features
        features["verification_score"] = (
            (1.0 if user_profile.email_verified else 0.0) +
            (1.0 if user_profile.phone_verified else 0.0) +
            (2.0 if user_profile.kyc_verified else 0.0)
        ) / 4.0
        
        # Account age feature
        account_age_days = (transaction.timestamp - user_profile.registration_date).days
        features["account_age"] = min(account_age_days / 365.0, 5.0)  # Cap at 5 years
        
        # Transaction history features
        features["transaction_experience"] = min(user_profile.total_transactions / 100.0, 1.0)
        
        return features
    
    async def _calculate_ml_score(self, features: Dict[str, float]) -> float:
        """Calculate ML risk score (simplified)"""
        
        # Simplified ML scoring
        score = 0.0
        
        # High amount ratio increases risk
        if features["amount_ratio"] > 5.0:
            score += 0.4
        elif features["amount_ratio"] > 2.0:
            score += 0.2
        
        # New accounts are riskier
        if features["account_age"] < 0.1:  # Less than 1 month
            score += 0.3
        
        # Unverified accounts are riskier
        if features["verification_score"] < 0.5:
            score += 0.2
        
        # Inexperienced users are riskier
        if features["transaction_experience"] < 0.1:
            score += 0.1
        
        return min(score, 1.0)
    
    async def _identify_fraud_patterns(self, features: Dict[str, float]) -> List[FraudType]:
        """Identify potential fraud patterns"""
        
        patterns = []
        
        if features["amount_ratio"] > 5.0:
            patterns.append(FraudType.PAYMENT_MANIPULATION)
        
        if features["account_age"] < 0.1 and features["verification_score"] < 0.5:
            patterns.append(FraudType.SYNTHETIC_IDENTITY)
        
        if features["verification_score"] == 0.0:
            patterns.append(FraudType.IDENTITY_THEFT)
        
        return patterns
    
    async def _generate_explanations(
        self, 
        features: Dict[str, float], 
        fraud_types: List[FraudType]
    ) -> List[str]:
        """Generate human-readable explanations"""
        
        explanations = []
        
        if features["amount_ratio"] > 5.0:
            explanations.append(f"Transaction amount is {features['amount_ratio']:.1f}x user's average")
        
        if features["account_age"] < 0.1:
            explanations.append("Very new account (less than 1 month old)")
        
        if features["verification_score"] < 0.5:
            explanations.append("Account has limited verification")
        
        if FraudType.SYNTHETIC_IDENTITY in fraud_types:
            explanations.append("Pattern consistent with synthetic identity fraud")
        
        return explanations


class FraudDetectionService:
    """Advanced fraud detection and prevention service"""
    
    def __init__(self):
        self.rule_engine = RuleBasedEngine()
        self.ml_engine = MLFraudEngine()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.transaction_history: List[TransactionData] = []
        self.fraud_cases: List[FraudAnalysisResult] = []
        self.whitelist_ips: set = set()
        self.blacklist_ips: set = set()
        self.device_fingerprints: Dict[str, Dict[str, Any]] = {}
        
        # Fraud statistics
        self.stats = {
            "total_transactions": 0,
            "fraud_detected": 0,
            "false_positives": 0,
            "blocked_transactions": 0
        }
    
    async def analyze_transaction(self, transaction: TransactionData) -> FraudAnalysisResult:
        """Perform comprehensive fraud analysis"""
        
        # Get or create user profile
        user_profile = await self._get_user_profile(transaction.user_id)
        
        # Perform IP reputation check
        ip_risk = await self._check_ip_reputation(transaction.ip_address)
        
        # Device fingerprint analysis
        device_risk = await self._analyze_device_fingerprint(transaction.device_fingerprint)
        
        # Run both detection engines
        rule_result = await self.rule_engine.analyze_transaction(transaction, user_profile)
        ml_result = await self.ml_engine.analyze_transaction(transaction, user_profile)
        
        # Combine results
        combined_result = await self._combine_results([rule_result, ml_result], ip_risk, device_risk)
        
        # Update statistics
        await self._update_statistics(combined_result)
        
        # Store transaction and result
        self.transaction_history.append(transaction)
        self.fraud_cases.append(combined_result)
        
        # Update user profile
        await self._update_user_profile(transaction, user_profile)
        
        return combined_result
    
    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                registration_date=datetime.utcnow()
            )
        
        return self.user_profiles[user_id]
    
    async def _check_ip_reputation(self, ip_address: Optional[str]) -> float:
        """Check IP address reputation"""
        
        if not ip_address:
            return 0.5  # Unknown IP
        
        if ip_address in self.blacklist_ips:
            return 1.0  # High risk
        
        if ip_address in self.whitelist_ips:
            return 0.0  # Low risk
        
        # Simplified IP risk assessment
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Private IPs are generally safer
            if ip.is_private:
                return 0.1
            
            # Check for known risky ranges (simplified)
            if str(ip).startswith("10.0.0."):
                return 0.8  # Example risky range
            
            return 0.3  # Default risk for public IPs
            
        except ValueError:
            return 0.5  # Invalid IP format
    
    async def _analyze_device_fingerprint(self, device_fingerprint: Optional[str]) -> float:
        """Analyze device fingerprint for risk"""
        
        if not device_fingerprint:
            return 0.4  # Missing fingerprint is somewhat risky
        
        if device_fingerprint in self.device_fingerprints:
            device_info = self.device_fingerprints[device_fingerprint]
            
            # Check if device has been associated with fraud
            if device_info.get("fraud_count", 0) > 0:
                return 0.9
            
            # Established device is less risky
            return 0.1
        else:
            # New device
            self.device_fingerprints[device_fingerprint] = {
                "first_seen": datetime.utcnow(),
                "transaction_count": 0,
                "fraud_count": 0
            }
            return 0.3
    
    async def _combine_results(
        self, 
        results: List[FraudAnalysisResult], 
        ip_risk: float, 
        device_risk: float
    ) -> FraudAnalysisResult:
        """Combine multiple analysis results"""
        
        # Weighted average of risk scores
        total_weight = 0.5 + 0.3 + 0.1 + 0.1  # Rule + ML + IP + Device
        combined_score = (
            results[0].risk_score * 0.5 +  # Rule-based weight
            results[1].risk_score * 0.3 +  # ML weight
            ip_risk * 0.1 +                # IP risk weight
            device_risk * 0.1              # Device risk weight
        ) / total_weight
        
        # Combine fraud types
        all_fraud_types = []
        all_reasons = []
        
        for result in results:
            all_fraud_types.extend(result.detected_fraud_types)
            all_reasons.extend(result.reasons)
        
        # Add IP and device reasons
        if ip_risk > 0.7:
            all_reasons.append("High-risk IP address detected")
        if device_risk > 0.7:
            all_reasons.append("Suspicious device fingerprint")
        
        # Determine final risk level and action
        if combined_score < 0.25:
            risk_level = FraudRiskLevel.LOW
            action = ActionType.ALLOW
        elif combined_score < 0.5:
            risk_level = FraudRiskLevel.MEDIUM
            action = ActionType.CHALLENGE
        elif combined_score < 0.8:
            risk_level = FraudRiskLevel.HIGH
            action = ActionType.REVIEW
        else:
            risk_level = FraudRiskLevel.CRITICAL
            action = ActionType.BLOCK
        
        return FraudAnalysisResult(
            transaction_id=results[0].transaction_id,
            risk_score=combined_score,
            risk_level=risk_level,
            detected_fraud_types=list(set(all_fraud_types)),
            recommended_action=action,
            confidence=0.9,  # High confidence from combined analysis
            reasons=all_reasons
        )
    
    async def _update_statistics(self, result: FraudAnalysisResult):
        """Update fraud detection statistics"""
        
        self.stats["total_transactions"] += 1
        
        if result.risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL]:
            self.stats["fraud_detected"] += 1
        
        if result.recommended_action == ActionType.BLOCK:
            self.stats["blocked_transactions"] += 1
    
    async def _update_user_profile(self, transaction: TransactionData, profile: UserProfile):
        """Update user profile with transaction data"""
        
        profile.total_transactions += 1
        profile.total_amount_spent += transaction.amount
        profile.average_transaction_amount = profile.total_amount_spent / profile.total_transactions
        profile.last_activity = transaction.timestamp
        
        # Update preferred payment methods
        if transaction.payment_method not in profile.preferred_payment_methods:
            profile.preferred_payment_methods.append(transaction.payment_method)
        
        # Update device fingerprint tracking
        if transaction.device_fingerprint and transaction.device_fingerprint in self.device_fingerprints:
            self.device_fingerprints[transaction.device_fingerprint]["transaction_count"] += 1
    
    async def report_fraud(self, transaction_id: str, is_fraud: bool):
        """Report actual fraud status for learning"""
        
        # Find the transaction result
        for result in self.fraud_cases:
            if result.transaction_id == transaction_id:
                if is_fraud and result.risk_level == FraudRiskLevel.LOW:
                    self.stats["false_positives"] += 1
                
                # Update device fraud count if confirmed fraud
                transaction = next(
                    (t for t in self.transaction_history if t.transaction_id == transaction_id), 
                    None
                )
                
                if transaction and is_fraud and transaction.device_fingerprint:
                    if transaction.device_fingerprint in self.device_fingerprints:
                        self.device_fingerprints[transaction.device_fingerprint]["fraud_count"] += 1
                
                break
    
    async def get_fraud_statistics(self) -> Dict[str, Any]:
        """Get fraud detection statistics"""
        
        total = self.stats["total_transactions"]
        if total == 0:
            return self.stats.copy()
        
        stats = self.stats.copy()
        stats.update({
            "fraud_rate_percent": (self.stats["fraud_detected"] / total) * 100,
            "block_rate_percent": (self.stats["blocked_transactions"] / total) * 100,
            "false_positive_rate": (self.stats["false_positives"] / max(1, self.stats["fraud_detected"])) * 100
        })
        
        return stats
    
    async def add_to_whitelist(self, ip_address: str):
        """Add IP to whitelist"""
        self.whitelist_ips.add(ip_address)
    
    async def add_to_blacklist(self, ip_address: str):
        """Add IP to blacklist"""
        self.blacklist_ips.add(ip_address)


# Global service instance
fraud_detection_service = FraudDetectionService()

async def get_fraud_detection_service() -> FraudDetectionService:
    """Get fraud detection service instance"""
    return fraud_detection_service