"""Advanced Fraud Detection System
Comprehensive fraud detection and prevention for payment processing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import re
from collections import defaultdict, deque

from .billing_engine import FraudRiskLevel, FraudAnalysis

logger = logging.getLogger(__name__)


class FraudSignal(Enum):
    """Types of fraud signals"""
    VELOCITY_ANOMALY = "velocity_anomaly"
    AMOUNT_ANOMALY = "amount_anomaly"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    DEVICE_ANOMALY = "device_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    BLACKLIST_MATCH = "blacklist_match"
    PATTERN_MATCH = "pattern_match"
    ML_PREDICTION = "ml_prediction"


class ActionType(Enum):
    """Fraud detection actions"""
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"
    CHALLENGE = "challenge"
    DELAY = "delay"


@dataclass
class FraudRule:
    """Fraud detection rule definition"""
    id: str
    name: str
    description: str
    signal_type: FraudSignal
    conditions: Dict[str, Any]
    action: ActionType
    risk_score: float
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TransactionContext:
    """Context information for fraud analysis"""
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_fingerprint: Optional[str] = None
    billing_country: Optional[str] = None
    shipping_country: Optional[str] = None
    payment_method_type: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FraudEvent:
    """Fraud detection event record"""
    id: str
    transaction_id: str
    customer_id: str
    signal_type: FraudSignal
    rule_id: str
    risk_score: float
    action_taken: ActionType
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class AdvancedFraudDetector:
    """Advanced fraud detection and prevention system"""
    
    def __init__(self):
        self.rules: Dict[str, FraudRule] = {}
        self.fraud_events: Dict[str, FraudEvent] = {}
        self.customer_profiles: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.transaction_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.blacklists: Dict[str, set] = {
            "emails": set(),
            "ips": set(),
            "cards": set(),
            "devices": set()
        }
        
        # Initialize fraud rules
        self._initialize_fraud_rules()
        
        # Risk scoring weights
        self.risk_weights = {
            FraudSignal.VELOCITY_ANOMALY: 25,
            FraudSignal.AMOUNT_ANOMALY: 20,
            FraudSignal.GEOGRAPHIC_ANOMALY: 15,
            FraudSignal.DEVICE_ANOMALY: 15,
            FraudSignal.BEHAVIORAL_ANOMALY: 10,
            FraudSignal.BLACKLIST_MATCH: 30,
            FraudSignal.PATTERN_MATCH: 20,
            FraudSignal.ML_PREDICTION: 25
        }
    
    def _initialize_fraud_rules(self):
        """Initialize default fraud detection rules"""
        
        # High velocity transactions
        self.rules["velocity_high"] = FraudRule(
            id="velocity_high",
            name="High Transaction Velocity",
            description="Multiple transactions in short time period",
            signal_type=FraudSignal.VELOCITY_ANOMALY,
            conditions={
                "transaction_count": 5,
                "time_window_minutes": 10
            },
            action=ActionType.REVIEW,
            risk_score=25.0
        )
        
        # Large amount transactions
        self.rules["amount_large"] = FraudRule(
            id="amount_large",
            name="Large Transaction Amount",
            description="Transaction amount significantly above customer average",
            signal_type=FraudSignal.AMOUNT_ANOMALY,
            conditions={
                "amount_multiplier": 5.0,  # 5x above average
                "minimum_amount": 1000.0
            },
            action=ActionType.REVIEW,
            risk_score=20.0
        )
        
        # Geographic inconsistency
        self.rules["geo_inconsistent"] = FraudRule(
            id="geo_inconsistent",
            name="Geographic Inconsistency",
            description="Transaction from unusual geographic location",
            signal_type=FraudSignal.GEOGRAPHIC_ANOMALY,
            conditions={
                "distance_km": 1000,  # More than 1000km from usual location
                "time_hours": 24      # Within 24 hours
            },
            action=ActionType.CHALLENGE,
            risk_score=15.0
        )
        
        # Device fingerprint mismatch
        self.rules["device_new"] = FraudRule(
            id="device_new",
            name="New Device",
            description="Transaction from previously unseen device",
            signal_type=FraudSignal.DEVICE_ANOMALY,
            conditions={
                "new_device": True,
                "high_amount": 500.0
            },
            action=ActionType.CHALLENGE,
            risk_score=15.0
        )
        
        # Blacklist checks
        self.rules["blacklist_email"] = FraudRule(
            id="blacklist_email",
            name="Blacklisted Email",
            description="Email address on fraud blacklist",
            signal_type=FraudSignal.BLACKLIST_MATCH,
            conditions={"check_email": True},
            action=ActionType.BLOCK,
            risk_score=30.0
        )
        
        # Pattern matching - stolen card patterns
        self.rules["pattern_stolen_card"] = FraudRule(
            id="pattern_stolen_card",
            name="Stolen Card Pattern",
            description="Transaction pattern matching stolen card behavior",
            signal_type=FraudSignal.PATTERN_MATCH,
            conditions={
                "small_test_transaction": True,
                "followed_by_large": True,
                "time_gap_minutes": 30
            },
            action=ActionType.BLOCK,
            risk_score=25.0
        )
    
    async def analyze_transaction(self, context: TransactionContext) -> FraudAnalysis:
        """Comprehensive fraud analysis of a transaction"""
        signals_detected = []
        total_risk_score = 0.0
        fraud_events = []
        
        # Update customer profile
        await self._update_customer_profile(context)
        
        # Run all enabled fraud rules
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            try:
                signal_detected, event = await self._evaluate_rule(rule, context)
                if signal_detected:
                    signals_detected.append(rule.signal_type)
                    total_risk_score += rule.risk_score
                    fraud_events.append(event)
                    
                    logger.info(f"Fraud signal detected: {rule.signal_type.value} for transaction {context.transaction_id}")
                
            except Exception as e:
                logger.error(f"Error evaluating fraud rule {rule.id}: {str(e)}")
        
        # Determine overall risk level
        risk_level = self._calculate_risk_level(total_risk_score)
        
        # Determine recommended action
        recommended_action = self._determine_action(signals_detected, total_risk_score)
        
        # Create fraud analysis
        analysis = FraudAnalysis(
            transaction_id=context.transaction_id,
            risk_level=risk_level,
            risk_score=min(total_risk_score, 100.0),  # Cap at 100
            flags=[signal.value for signal in signals_detected],
            recommended_action=recommended_action,
            additional_checks={
                "signals_count": len(signals_detected),
                "rules_triggered": [event.rule_id for event in fraud_events],
                "customer_risk_profile": await self._get_customer_risk_profile(context.customer_id)
            }
        )
        
        # Store fraud events
        for event in fraud_events:
            self.fraud_events[event.id] = event
        
        # Update transaction history
        self.transaction_history[context.customer_id].append({
            "transaction_id": context.transaction_id,
            "amount": float(context.amount),
            "timestamp": context.timestamp.isoformat(),
            "risk_score": total_risk_score,
            "signals": [signal.value for signal in signals_detected]
        })
        
        return analysis
    
    async def _evaluate_rule(self, rule: FraudRule, context: TransactionContext) -> Tuple[bool, Optional[FraudEvent]]:
        """Evaluate a specific fraud rule against transaction context"""
        
        if rule.signal_type == FraudSignal.VELOCITY_ANOMALY:
            return await self._check_velocity_anomaly(rule, context)
        
        elif rule.signal_type == FraudSignal.AMOUNT_ANOMALY:
            return await self._check_amount_anomaly(rule, context)
        
        elif rule.signal_type == FraudSignal.GEOGRAPHIC_ANOMALY:
            return await self._check_geographic_anomaly(rule, context)
        
        elif rule.signal_type == FraudSignal.DEVICE_ANOMALY:
            return await self._check_device_anomaly(rule, context)
        
        elif rule.signal_type == FraudSignal.BLACKLIST_MATCH:
            return await self._check_blacklist_match(rule, context)
        
        elif rule.signal_type == FraudSignal.PATTERN_MATCH:
            return await self._check_pattern_match(rule, context)
        
        elif rule.signal_type == FraudSignal.ML_PREDICTION:
            return await self._check_ml_prediction(rule, context)
        
        return False, None
    
    async def _check_velocity_anomaly(self, rule: FraudRule, context: TransactionContext) -> Tuple[bool, Optional[FraudEvent]]:
        """Check for transaction velocity anomalies"""
        conditions = rule.conditions
        time_window = timedelta(minutes=conditions["time_window_minutes"])
        cutoff_time = context.timestamp - time_window
        
        # Count recent transactions
        recent_transactions = [
            tx for tx in self.transaction_history[context.customer_id]
            if datetime.fromisoformat(tx["timestamp"]) > cutoff_time
        ]
        
        if len(recent_transactions) >= conditions["transaction_count"]:
            event = FraudEvent(
                id=str(uuid.uuid4()),
                transaction_id=context.transaction_id,
                customer_id=context.customer_id,
                signal_type=rule.signal_type,
                rule_id=rule.id,
                risk_score=rule.risk_score,
                action_taken=rule.action,
                details={
                    "transaction_count": len(recent_transactions),
                    "time_window_minutes": conditions["time_window_minutes"],
                    "recent_transactions": [tx["transaction_id"] for tx in recent_transactions]
                }
            )
            return True, event
        
        return False, None
    
    async def _check_amount_anomaly(self, rule: FraudRule, context: TransactionContext) -> Tuple[bool, Optional[FraudEvent]]:
        """Check for transaction amount anomalies"""
        conditions = rule.conditions
        
        if context.amount < Decimal(str(conditions["minimum_amount"])):
            return False, None
        
        # Calculate customer's average transaction amount
        customer_transactions = list(self.transaction_history[context.customer_id])
        if len(customer_transactions) < 3:  # Need minimum history
            return False, None
        
        avg_amount = sum(tx["amount"] for tx in customer_transactions) / len(customer_transactions)
        
        if float(context.amount) > avg_amount * conditions["amount_multiplier"]:
            event = FraudEvent(
                id=str(uuid.uuid4()),
                transaction_id=context.transaction_id,
                customer_id=context.customer_id,
                signal_type=rule.signal_type,
                rule_id=rule.id,
                risk_score=rule.risk_score,
                action_taken=rule.action,
                details={
                    "transaction_amount": float(context.amount),
                    "customer_average": avg_amount,
                    "multiplier": float(context.amount) / avg_amount,
                    "threshold": conditions["amount_multiplier"]
                }
            )
            return True, event
        
        return False, None
    
    async def _check_geographic_anomaly(self, rule: FraudRule, context: TransactionContext) -> Tuple[bool, Optional[FraudEvent]]:
        """Check for geographic anomalies"""
        if not context.billing_country:
            return False, None
        
        conditions = rule.conditions
        customer_profile = self.customer_profiles[context.customer_id]
        
        # Get customer's usual countries
        usual_countries = customer_profile.get("usual_countries", set())
        
        if context.billing_country not in usual_countries and len(usual_countries) > 0:
            # Check if this is a sudden geographic change
            recent_transactions = [
                tx for tx in self.transaction_history[context.customer_id]
                if datetime.fromisoformat(tx["timestamp"]) > context.timestamp - timedelta(hours=conditions["time_hours"])
            ]
            
            if recent_transactions:
                event = FraudEvent(
                    id=str(uuid.uuid4()),
                    transaction_id=context.transaction_id,
                    customer_id=context.customer_id,
                    signal_type=rule.signal_type,
                    rule_id=rule.id,
                    risk_score=rule.risk_score,
                    action_taken=rule.action,
                    details={
                        "current_country": context.billing_country,
                        "usual_countries": list(usual_countries),
                        "recent_activity": len(recent_transactions)
                    }
                )
                return True, event
        
        return False, None
    
    async def _check_device_anomaly(self, rule: FraudRule, context: TransactionContext) -> Tuple[bool, Optional[FraudEvent]]:
        """Check for device-related anomalies"""
        if not context.device_fingerprint:
            return False, None
        
        conditions = rule.conditions
        customer_profile = self.customer_profiles[context.customer_id]
        
        known_devices = customer_profile.get("known_devices", set())
        
        if (context.device_fingerprint not in known_devices and 
            conditions.get("new_device") and 
            context.amount >= Decimal(str(conditions["high_amount"]))):
            
            event = FraudEvent(
                id=str(uuid.uuid4()),
                transaction_id=context.transaction_id,
                customer_id=context.customer_id,
                signal_type=rule.signal_type,
                rule_id=rule.id,
                risk_score=rule.risk_score,
                action_taken=rule.action,
                details={
                    "device_fingerprint": context.device_fingerprint,
                    "known_devices_count": len(known_devices),
                    "transaction_amount": float(context.amount)
                }
            )
            return True, event
        
        return False, None
    
    async def _check_blacklist_match(self, rule: FraudRule, context: TransactionContext) -> Tuple[bool, Optional[FraudEvent]]:
        """Check against fraud blacklists"""
        conditions = rule.conditions
        
        matches = []
        
        if conditions.get("check_email") and context.email:
            if context.email.lower() in self.blacklists["emails"]:
                matches.append(f"email:{context.email}")
        
        if context.ip_address and context.ip_address in self.blacklists["ips"]:
            matches.append(f"ip:{context.ip_address}")
        
        if context.device_fingerprint and context.device_fingerprint in self.blacklists["devices"]:
            matches.append(f"device:{context.device_fingerprint}")
        
        if matches:
            event = FraudEvent(
                id=str(uuid.uuid4()),
                transaction_id=context.transaction_id,
                customer_id=context.customer_id,
                signal_type=rule.signal_type,
                rule_id=rule.id,
                risk_score=rule.risk_score,
                action_taken=rule.action,
                details={
                    "blacklist_matches": matches,
                    "match_count": len(matches)
                }
            )
            return True, event
        
        return False, None
    
    async def _check_pattern_match(self, rule: FraudRule, context: TransactionContext) -> Tuple[bool, Optional[FraudEvent]]:
        """Check for known fraud patterns"""
        conditions = rule.conditions
        
        if conditions.get("small_test_transaction") and conditions.get("followed_by_large"):
            # Look for small test transaction followed by large transaction pattern
            customer_transactions = list(self.transaction_history[context.customer_id])
            
            if len(customer_transactions) >= 2:
                latest_tx = customer_transactions[-1]
                if (latest_tx["amount"] < 10.0 and  # Small test transaction
                    context.amount > Decimal("100.0") and  # Current large transaction
                    (context.timestamp - datetime.fromisoformat(latest_tx["timestamp"])).total_seconds() < conditions["time_gap_minutes"] * 60):
                    
                    event = FraudEvent(
                        id=str(uuid.uuid4()),
                        transaction_id=context.transaction_id,
                        customer_id=context.customer_id,
                        signal_type=rule.signal_type,
                        rule_id=rule.id,
                        risk_score=rule.risk_score,
                        action_taken=rule.action,
                        details={
                            "pattern": "small_test_followed_by_large",
                            "test_amount": latest_tx["amount"],
                            "large_amount": float(context.amount),
                            "time_gap_minutes": (context.timestamp - datetime.fromisoformat(latest_tx["timestamp"])).total_seconds() / 60
                        }
                    )
                    return True, event
        
        return False, None
    
    async def _check_ml_prediction(self, rule: FraudRule, context: TransactionContext) -> Tuple[bool, Optional[FraudEvent]]:
        """ML-based fraud prediction (simplified implementation)"""
        # This would integrate with a real ML model
        # For now, implement a simple heuristic-based prediction
        
        features = await self._extract_ml_features(context)
        risk_score = await self._simple_ml_prediction(features)
        
        if risk_score > 0.7:  # High risk threshold
            event = FraudEvent(
                id=str(uuid.uuid4()),
                transaction_id=context.transaction_id,
                customer_id=context.customer_id,
                signal_type=rule.signal_type,
                rule_id=rule.id,
                risk_score=rule.risk_score,
                action_taken=rule.action,
                details={
                    "ml_risk_score": risk_score,
                    "features": features,
                    "model_version": "simple_heuristic_v1"
                }
            )
            return True, event
        
        return False, None
    
    async def _extract_ml_features(self, context: TransactionContext) -> Dict[str, float]:
        """Extract features for ML model"""
        customer_profile = self.customer_profiles[context.customer_id]
        customer_transactions = list(self.transaction_history[context.customer_id])
        
        features = {
            "amount": float(context.amount),
            "hour_of_day": context.timestamp.hour,
            "day_of_week": context.timestamp.weekday(),
            "customer_age_days": (context.timestamp - customer_profile.get("first_seen", context.timestamp)).days,
            "transaction_count": len(customer_transactions),
            "avg_amount": sum(tx["amount"] for tx in customer_transactions) / max(len(customer_transactions), 1),
            "time_since_last_tx": 0 if not customer_transactions else 
                (context.timestamp - datetime.fromisoformat(customer_transactions[-1]["timestamp"])).total_seconds() / 3600,
            "country_risk": self._get_country_risk_score(context.billing_country),
            "email_risk": self._get_email_risk_score(context.email)
        }
        
        return features
    
    async def _simple_ml_prediction(self, features: Dict[str, float]) -> float:
        """Simple ML prediction based on features"""
        risk_score = 0.0
        
        # Amount-based risk
        if features["amount"] > 1000:
            risk_score += 0.2
        elif features["amount"] > 500:
            risk_score += 0.1
        
        # Time-based risk
        if features["hour_of_day"] < 6 or features["hour_of_day"] > 23:
            risk_score += 0.1  # Late night transactions
        
        # Customer history risk
        if features["customer_age_days"] < 1:
            risk_score += 0.3  # New customer
        elif features["customer_age_days"] < 7:
            risk_score += 0.2
        
        # Transaction frequency risk
        if features["time_since_last_tx"] < 0.1:  # Less than 6 minutes
            risk_score += 0.2
        
        # Geographic risk
        risk_score += features["country_risk"] * 0.2
        
        # Email risk
        risk_score += features["email_risk"] * 0.1
        
        return min(risk_score, 1.0)
    
    def _get_country_risk_score(self, country: Optional[str]) -> float:
        """Get risk score for a country (simplified)"""
        if not country:
            return 0.5
        
        high_risk_countries = {"XX", "YY", "ZZ"}  # Placeholder
        medium_risk_countries = {"AB", "CD", "EF"}
        
        if country in high_risk_countries:
            return 1.0
        elif country in medium_risk_countries:
            return 0.5
        else:
            return 0.1
    
    def _get_email_risk_score(self, email: Optional[str]) -> float:
        """Get risk score for an email (simplified)"""
        if not email:
            return 0.3
        
        # Check for suspicious patterns
        suspicious_domains = {"tempmail.com", "guerrillamail.com", "10minutemail.com"}
        
        domain = email.split("@")[-1].lower()
        if domain in suspicious_domains:
            return 0.8
        
        # Check for suspicious patterns in email
        if re.search(r'\d{10,}', email):  # Long sequence of numbers
            return 0.6
        
        return 0.1
    
    async def _update_customer_profile(self, context: TransactionContext):
        """Update customer profile with transaction data"""
        profile = self.customer_profiles[context.customer_id]
        
        # Update first seen date
        if "first_seen" not in profile:
            profile["first_seen"] = context.timestamp
        
        # Update usual countries
        if "usual_countries" not in profile:
            profile["usual_countries"] = set()
        if context.billing_country:
            profile["usual_countries"].add(context.billing_country)
        
        # Update known devices
        if "known_devices" not in profile:
            profile["known_devices"] = set()
        if context.device_fingerprint:
            profile["known_devices"].add(context.device_fingerprint)
        
        # Update transaction patterns
        profile["last_transaction"] = context.timestamp
        profile["total_transactions"] = profile.get("total_transactions", 0) + 1
        profile["total_amount"] = profile.get("total_amount", 0.0) + float(context.amount)
    
    async def _get_customer_risk_profile(self, customer_id: str) -> Dict[str, Any]:
        """Get customer risk profile summary"""
        profile = self.customer_profiles[customer_id]
        transactions = list(self.transaction_history[customer_id])
        
        # Calculate risk indicators
        fraud_events = [e for e in self.fraud_events.values() if e.customer_id == customer_id]
        avg_risk_score = sum(tx.get("risk_score", 0) for tx in transactions) / max(len(transactions), 1)
        
        return {
            "customer_age_days": (datetime.now() - profile.get("first_seen", datetime.now())).days,
            "total_transactions": len(transactions),
            "total_amount": sum(tx["amount"] for tx in transactions),
            "avg_transaction_amount": sum(tx["amount"] for tx in transactions) / max(len(transactions), 1),
            "fraud_events_count": len(fraud_events),
            "avg_risk_score": avg_risk_score,
            "countries_used": len(profile.get("usual_countries", set())),
            "devices_used": len(profile.get("known_devices", set()))
        }
    
    def _calculate_risk_level(self, risk_score: float) -> FraudRiskLevel:
        """Calculate risk level from risk score"""
        if risk_score >= 70:
            return FraudRiskLevel.CRITICAL
        elif risk_score >= 50:
            return FraudRiskLevel.HIGH
        elif risk_score >= 30:
            return FraudRiskLevel.MEDIUM
        else:
            return FraudRiskLevel.LOW
    
    def _determine_action(self, signals: List[FraudSignal], risk_score: float) -> str:
        """Determine recommended action based on signals and risk score"""
        if FraudSignal.BLACKLIST_MATCH in signals:
            return "block_payment"
        elif risk_score >= 70:
            return "block_payment"
        elif risk_score >= 50:
            return "manual_review"
        elif risk_score >= 30:
            return "enhanced_verification"
        else:
            return "proceed"
    
    async def add_to_blacklist(self, list_type: str, value: str):
        """Add value to fraud blacklist"""
        if list_type in self.blacklists:
            self.blacklists[list_type].add(value.lower())
            logger.info(f"Added {value} to {list_type} blacklist")
    
    async def remove_from_blacklist(self, list_type: str, value: str):
        """Remove value from fraud blacklist"""
        if list_type in self.blacklists:
            self.blacklists[list_type].discard(value.lower())
            logger.info(f"Removed {value} from {list_type} blacklist")
    
    async def get_fraud_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get fraud detection statistics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_events = [
            event for event in self.fraud_events.values()
            if event.timestamp > cutoff_date
        ]
        
        signal_counts = defaultdict(int)
        for event in recent_events:
            signal_counts[event.signal_type.value] += 1
        
        action_counts = defaultdict(int)
        for event in recent_events:
            action_counts[event.action_taken.value] += 1
        
        statistics = {
            "period_days": days,
            "total_fraud_events": len(recent_events),
            "fraud_signals": dict(signal_counts),
            "actions_taken": dict(action_counts),
            "avg_risk_score": sum(event.risk_score for event in recent_events) / max(len(recent_events), 1),
            "blacklist_sizes": {k: len(v) for k, v in self.blacklists.items()},
            "rules_enabled": sum(1 for rule in self.rules.values() if rule.enabled),
            "generated_at": datetime.now().isoformat()
        }
        
        return statistics