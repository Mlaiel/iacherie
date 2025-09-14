"""Ainflue Core Payments - Fraud Detection Core
============================================

Enterprise-grade fraud detection system providing real-time transaction analysis,
risk scoring, pattern recognition, machine learning models, and automated
fraud prevention for the Ainflue platform payment systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import hashlib
import time
import numpy as np

# Setup logger
logger = logging.getLogger(__name__)

class RiskLevel(str, Enum):
    """Risk levels for transactions"""
    VERY_LOW = "very_low"    # 0.0 - 0.2
    LOW = "low"              # 0.2 - 0.4
    MEDIUM = "medium"        # 0.4 - 0.6
    HIGH = "high"            # 0.6 - 0.8
    VERY_HIGH = "very_high"  # 0.8 - 1.0

class FraudType(str, Enum):
    """Types of fraud"""
    CARD_FRAUD = "card_fraud"
    ACCOUNT_TAKEOVER = "account_takeover"
    IDENTITY_THEFT = "identity_theft"
    PAYMENT_FRAUD = "payment_fraud"
    CHARGEBACK_FRAUD = "chargeback_fraud"
    SYNTHETIC_IDENTITY = "synthetic_identity"
    VELOCITY_FRAUD = "velocity_fraud"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    DEVICE_FRAUD = "device_fraud"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"

class ActionType(str, Enum):
    """Fraud prevention actions"""
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"
    CHALLENGE = "challenge"
    STEP_UP_AUTH = "step_up_auth"
    DECLINE = "decline"
    MONITOR = "monitor"

class TransactionStatus(str, Enum):
    """Transaction processing status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    APPROVED = "approved"
    DECLINED = "declined"
    UNDER_REVIEW = "under_review"
    BLOCKED = "blocked"
    FLAGGED = "flagged"

@dataclass
class TransactionData:
    """Transaction data for fraud analysis"""
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    amount: float = 0.0
    currency: str = "USD"
    payment_method: str = ""
    card_last_four: Optional[str] = None
    card_type: Optional[str] = None
    merchant_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_fingerprint: Optional[str] = None
    billing_address: Dict[str, str] = field(default_factory=dict)
    shipping_address: Dict[str, str] = field(default_factory=dict)
    session_id: Optional[str] = None
    referrer: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserProfile:
    """User profile for behavioral analysis"""
    user_id: str
    account_age_days: int = 0
    total_transactions: int = 0
    total_amount: float = 0.0
    avg_transaction_amount: float = 0.0
    countries_used: Set[str] = field(default_factory=set)
    payment_methods_used: Set[str] = field(default_factory=set)
    devices_used: Set[str] = field(default_factory=set)
    suspicious_activity_count: int = 0
    last_login: Optional[datetime] = None
    last_transaction: Optional[datetime] = None
    risk_score: float = 0.0
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FraudRule:
    """Fraud detection rule"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    fraud_type: FraudType = FraudType.PAYMENT_FRAUD
    conditions: Dict[str, Any] = field(default_factory=dict)
    risk_score_impact: float = 0.0
    action: ActionType = ActionType.REVIEW
    enabled: bool = True
    priority: int = 5  # 1-10, 10 being highest priority
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FraudAnalysisResult:
    """Result of fraud analysis"""
    transaction_id: str
    overall_risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    recommended_action: ActionType = ActionType.ALLOW
    fraud_indicators: List[FraudType] = field(default_factory=list)
    rule_matches: List[str] = field(default_factory=list)
    risk_factors: Dict[str, float] = field(default_factory=dict)
    analysis_details: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    processing_time_ms: float = 0.0
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
    model_version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

class FraudDetectionModel(ABC):
    """Abstract fraud detection model"""
    
    def __init__(self, name -> None: str, version -> None: str = "1.0.0") -> None:
        self.name = name
        self.version = version
        self.loaded = False
        self.accuracy = 0.0
        self.last_updated = datetime.utcnow()
    
    @abstractmethod
    async def load_model(self) -> bool:
        """Load the fraud detection model"""
        pass
    
    @abstractmethod
    async def predict(self, transaction_data: TransactionData, 
                     user_profile: UserProfile) -> float:
        """Predict fraud probability"""
        pass
    
    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        pass

class VelocityFraudModel(FraudDetectionModel):
    """Velocity-based fraud detection model"""
    
    def __init__(self) -> None:
        super().__init__("VelocityFraudModel", "1.0.0")
        self.transaction_history: Dict[str, List[TransactionData]] = {}
        self.accuracy = 0.85
    
    async def load_model(self) -> bool:
        """Load velocity fraud model"""
        try:
            # Simulate model loading
            await asyncio.sleep(0.1)
            self.loaded = True
            logger.info("Velocity fraud model loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load velocity fraud model: {str(e)}")
            return False
    
    async def predict(self, transaction_data: TransactionData, 
                     user_profile: UserProfile) -> float:
        """Predict fraud based on transaction velocity"""
        if not self.loaded:
            raise Exception("Model not loaded")
        
        risk_score = 0.0
        
        # Get recent transactions for user
        user_transactions = self.transaction_history.get(transaction_data.user_id, [])
        recent_transactions = [
            t for t in user_transactions 
            if (datetime.utcnow() - t.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        # Check transaction frequency
        if len(recent_transactions) > 10:  # More than 10 transactions in last hour
            risk_score += 0.3
        elif len(recent_transactions) > 5:
            risk_score += 0.1
        
        # Check amount velocity
        recent_amount = sum(t.amount for t in recent_transactions)
        if recent_amount > user_profile.avg_transaction_amount * 10:  # 10x average
            risk_score += 0.4
        elif recent_amount > user_profile.avg_transaction_amount * 5:
            risk_score += 0.2
        
        # Check geographic velocity
        unique_countries = len(set(t.billing_address.get('country', '') for t in recent_transactions))
        if unique_countries > 2:  # Multiple countries in short time
            risk_score += 0.3
        
        # Add some randomness for simulation
        risk_score += np.random.random() * 0.1
        
        return min(risk_score, 1.0)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance for velocity model"""
        return {
            'transaction_frequency': 0.4,
            'amount_velocity': 0.3,
            'geographic_velocity': 0.2,
            'payment_method_changes': 0.1
        }

class BehavioralFraudModel(FraudDetectionModel):
    """Behavioral anomaly detection model"""
    
    def __init__(self) -> None:
        super().__init__("BehavioralFraudModel", "1.0.0")
        self.accuracy = 0.82
    
    async def load_model(self) -> bool:
        """Load behavioral fraud model"""
        try:
            # Simulate model loading
            await asyncio.sleep(0.1)
            self.loaded = True
            logger.info("Behavioral fraud model loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load behavioral fraud model: {str(e)}")
            return False
    
    async def predict(self, transaction_data: TransactionData, 
                     user_profile: UserProfile) -> float:
        """Predict fraud based on behavioral patterns"""
        if not self.loaded:
            raise Exception("Model not loaded")
        
        risk_score = 0.0
        
        # Check if transaction amount is unusual for user
        if transaction_data.amount > user_profile.avg_transaction_amount * 5:
            risk_score += 0.3
        elif transaction_data.amount > user_profile.avg_transaction_amount * 3:
            risk_score += 0.1
        
        # Check new payment method
        if transaction_data.payment_method not in user_profile.payment_methods_used:
            risk_score += 0.2
        
        # Check new country
        transaction_country = transaction_data.billing_address.get('country', '')
        if transaction_country and transaction_country not in user_profile.countries_used:
            risk_score += 0.2
        
        # Check new device
        if (transaction_data.device_fingerprint and 
            transaction_data.device_fingerprint not in user_profile.devices_used):
            risk_score += 0.1
        
        # Check time since last transaction
        if user_profile.last_transaction:
            time_diff = (datetime.utcnow() - user_profile.last_transaction).days
            if time_diff > 90:  # No activity for 3 months
                risk_score += 0.2
        
        # Add some randomness for simulation
        risk_score += np.random.random() * 0.1
        
        return min(risk_score, 1.0)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance for behavioral model"""
        return {
            'amount_deviation': 0.3,
            'new_payment_method': 0.2,
            'geographic_anomaly': 0.2,
            'device_anomaly': 0.15,
            'temporal_anomaly': 0.15
        }

class RuleEngine:
    """Rule-based fraud detection engine"""
    
    def __init__(self) -> None:
        self.rules: Dict[str, FraudRule] = {}
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default fraud detection rules"""
        default_rules = [
            FraudRule(
                id="high_amount_new_user",
                name="High Amount New User",
                description="High transaction amount for new user account",
                fraud_type=FraudType.PAYMENT_FRAUD,
                conditions={
                    'account_age_days': {'operator': '<', 'value': 30},
                    'amount': {'operator': '>', 'value': 1000}
                },
                risk_score_impact=0.4,
                action=ActionType.REVIEW
            ),
            FraudRule(
                id="multiple_failed_attempts",
                name="Multiple Failed Attempts",
                description="Multiple failed payment attempts in short time",
                fraud_type=FraudType.CARD_FRAUD,
                conditions={
                    'failed_attempts_last_hour': {'operator': '>', 'value': 3}
                },
                risk_score_impact=0.5,
                action=ActionType.BLOCK
            ),
            FraudRule(
                id="suspicious_velocity",
                name="Suspicious Transaction Velocity",
                description="Too many transactions in short time period",
                fraud_type=FraudType.VELOCITY_FRAUD,
                conditions={
                    'transactions_last_hour': {'operator': '>', 'value': 5},
                    'total_amount_last_hour': {'operator': '>', 'value': 5000}
                },
                risk_score_impact=0.3,
                action=ActionType.CHALLENGE
            ),
            FraudRule(
                id="geographic_mismatch",
                name="Geographic Mismatch",
                description="Transaction from unusual geographic location",
                fraud_type=FraudType.GEOGRAPHIC_ANOMALY,
                conditions={
                    'new_country': {'operator': '==', 'value': True},
                    'distance_from_usual': {'operator': '>', 'value': 1000}  # km
                },
                risk_score_impact=0.2,
                action=ActionType.STEP_UP_AUTH
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    def add_rule(self, rule -> None: FraudRule) -> None:
        """Add fraud detection rule"""
        self.rules[rule.id] = rule
        logger.info(f"Added fraud rule: {rule.name}")
    
    def evaluate_rules(self, transaction_data: TransactionData, 
                      user_profile: UserProfile, 
                      analysis_context: Dict[str, Any]) -> Tuple[List[str], float]:
        """Evaluate all rules against transaction"""
        matched_rules = []
        total_risk_impact = 0.0
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            if self._evaluate_rule_conditions(rule, transaction_data, user_profile, analysis_context):
                matched_rules.append(rule.id)
                total_risk_impact += rule.risk_score_impact
        
        return matched_rules, min(total_risk_impact, 1.0)
    
    def _evaluate_rule_conditions(self, rule: FraudRule, transaction_data: TransactionData,
                                 user_profile: UserProfile, context: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met"""
        for field, condition in rule.conditions.items():
            operator = condition.get('operator')
            expected_value = condition.get('value')
            
            # Get actual value from transaction, user profile, or context
            actual_value = self._get_field_value(field, transaction_data, user_profile, context)
            
            if actual_value is None:
                continue
            
            # Evaluate condition
            if not self._evaluate_condition(actual_value, operator, expected_value):
                return False
        
        return True
    
    def _get_field_value(self, field: str, transaction_data: TransactionData,
                        user_profile: UserProfile, context: Dict[str, Any]) -> Any:
        """Get field value from data sources"""
        # Try transaction data first
        if hasattr(transaction_data, field):
            return getattr(transaction_data, field)
        
        # Try user profile
        if hasattr(user_profile, field):
            return getattr(user_profile, field)
        
        # Try context
        return context.get(field)
    
    def _evaluate_condition(self, actual_value: Any, operator: str, expected_value: Any) -> bool:
        """Evaluate single condition"""
        try:
            if operator == '>':
                return float(actual_value) > float(expected_value)
            elif operator == '<':
                return float(actual_value) < float(expected_value)
            elif operator == '>=':
                return float(actual_value) >= float(expected_value)
            elif operator == '<=':
                return float(actual_value) <= float(expected_value)
            elif operator == '==':
                return actual_value == expected_value
            elif operator == '!=':
                return actual_value != expected_value
            elif operator == 'in':
                return actual_value in expected_value
            elif operator == 'not_in':
                return actual_value not in expected_value
        except (ValueError, TypeError):
            pass
        
        return False

class FraudDetectionCore:
    """Core fraud detection system"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        self.level = level
        self.models: Dict[str, FraudDetectionModel] = {}
        self.rule_engine = RuleEngine()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.transaction_history: Dict[str, List[TransactionData]] = {}
        self.analysis_results: Dict[str, FraudAnalysisResult] = {}
        self.blacklisted_ips: Set[str] = set()
        self.blacklisted_devices: Set[str] = set()
        self.whitelisted_users: Set[str] = set()
        self.is_running = False
        self.metrics = {
            'total_transactions_analyzed': 0,
            'fraudulent_transactions_detected': 0,
            'false_positives': 0,
            'total_blocked_transactions': 0,
            'total_reviewed_transactions': 0,
            'avg_analysis_time': 0.0,
            'model_accuracy': 0.0
        }
        
        # Initialize models
        self._initialize_models()
        
        logger.info(f"Fraud Detection Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize fraud detection system"""
        try:
            # Load all models
            load_tasks = []
            for model in self.models.values():
                load_tasks.append(model.load_model())
            
            results = await asyncio.gather(*load_tasks, return_exceptions=True)
            
            loaded_count = 0
            for i, result in enumerate(results):
                if result is True:
                    loaded_count += 1
                elif isinstance(result, Exception):
                    logger.error(f"Model loading failed: {str(result)}")
            
            logger.info(f"Fraud Detection Core initialized - {loaded_count}/{len(self.models)} models loaded")
            return loaded_count > 0
        except Exception as e:
            logger.error(f"Failed to initialize Fraud Detection Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start fraud detection system"""
        try:
            self.is_running = True
            logger.info("Fraud Detection Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start Fraud Detection Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop fraud detection system"""
        try:
            self.is_running = False
            logger.info("Fraud Detection Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Fraud Detection Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Check if models are loaded
            loaded_models = sum(1 for model in self.models.values() if model.loaded)
            if loaded_models == 0:
                logger.warning("No fraud detection models are loaded")
                return False
            
            # Check if analysis times are reasonable
            if self.metrics['avg_analysis_time'] > 5000:  # More than 5 seconds
                logger.warning("Fraud analysis taking too long")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def _initialize_models(self) -> None:
        """Initialize fraud detection models"""
        self.models = {
            'velocity_fraud': VelocityFraudModel(),
            'behavioral_fraud': BehavioralFraudModel()
        }
    
    async def analyze_transaction(self, transaction_data: TransactionData) -> FraudAnalysisResult:
        """Analyze transaction for fraud"""
        start_time = time.time()
        
        try:
            # Get or create user profile
            user_profile = self._get_or_create_user_profile(transaction_data.user_id)
            
            # Check whitelisted users
            if transaction_data.user_id in self.whitelisted_users:
                result = FraudAnalysisResult(
                    transaction_id=transaction_data.transaction_id,
                    overall_risk_score=0.0,
                    risk_level=RiskLevel.VERY_LOW,
                    recommended_action=ActionType.ALLOW,
                    analysis_details={'whitelisted_user': True}
                )
                processing_time = (time.time() - start_time) * 1000
                result.processing_time_ms = processing_time
                self.analysis_results[transaction_data.transaction_id] = result
                return result
            
            # Quick blacklist checks
            risk_score = 0.0
            fraud_indicators = []
            risk_factors = {}
            
            if transaction_data.ip_address in self.blacklisted_ips:
                risk_score = 1.0
                fraud_indicators.append(FraudType.DEVICE_FRAUD)
                risk_factors['blacklisted_ip'] = 1.0
            
            if transaction_data.device_fingerprint in self.blacklisted_devices:
                risk_score = 1.0
                fraud_indicators.append(FraudType.DEVICE_FRAUD)
                risk_factors['blacklisted_device'] = 1.0
            
            # Run ML models if not already blocked
            if risk_score < 1.0:
                model_scores = {}
                for model_name, model in self.models.items():
                    if model.loaded:
                        try:
                            score = await model.predict(transaction_data, user_profile)
                            model_scores[model_name] = score
                            risk_factors[f'{model_name}_score'] = score
                        except Exception as e:
                            logger.error(f"Model {model_name} prediction failed: {str(e)}")
                
                # Combine model scores
                if model_scores:
                    risk_score = max(risk_score, max(model_scores.values()))
            
            # Evaluate rules
            analysis_context = self._build_analysis_context(transaction_data, user_profile)
            matched_rules, rule_risk_score = self.rule_engine.evaluate_rules(
                transaction_data, user_profile, analysis_context
            )
            risk_score = max(risk_score, rule_risk_score)
            
            # Determine risk level and action
            risk_level = self._calculate_risk_level(risk_score)
            recommended_action = self._determine_action(risk_score, matched_rules)
            
            # Identify fraud types
            if risk_score > 0.6:
                fraud_indicators.extend(self._identify_fraud_types(transaction_data, user_profile, analysis_context))
            
            # Calculate confidence
            confidence_score = min(risk_score * 0.9 + 0.1, 1.0)
            
            # Create result
            result = FraudAnalysisResult(
                transaction_id=transaction_data.transaction_id,
                overall_risk_score=risk_score,
                risk_level=risk_level,
                recommended_action=recommended_action,
                fraud_indicators=list(set(fraud_indicators)),
                rule_matches=matched_rules,
                risk_factors=risk_factors,
                analysis_details=analysis_context,
                confidence_score=confidence_score
            )
            
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            
            # Store result and update metrics
            self.analysis_results[transaction_data.transaction_id] = result
            self._update_metrics(result)
            
            # Update user profile and transaction history
            self._update_user_profile(user_profile, transaction_data, result)
            self._store_transaction_history(transaction_data)
            
            logger.info(f"Fraud analysis completed for transaction {transaction_data.transaction_id} - Risk: {risk_level.value}")
            return result
            
        except Exception as e:
            logger.error(f"Fraud analysis failed for transaction {transaction_data.transaction_id}: {str(e)}")
            raise
    
    def _get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        return self.user_profiles[user_id]
    
    def _build_analysis_context(self, transaction_data: TransactionData, 
                               user_profile: UserProfile) -> Dict[str, Any]:
        """Build analysis context"""
        context = {}
        
        # Calculate velocity metrics
        user_transactions = self.transaction_history.get(transaction_data.user_id, [])
        recent_transactions = [
            t for t in user_transactions 
            if (datetime.utcnow() - t.timestamp).total_seconds() < 3600
        ]
        
        context['transactions_last_hour'] = len(recent_transactions)
        context['total_amount_last_hour'] = sum(t.amount for t in recent_transactions)
        context['failed_attempts_last_hour'] = 0  # Would be tracked separately
        
        # Geographic analysis
        transaction_country = transaction_data.billing_address.get('country', '')
        context['new_country'] = transaction_country not in user_profile.countries_used
        context['distance_from_usual'] = 0  # Would calculate from usual locations
        
        return context
    
    def _calculate_risk_level(self, risk_score: float) -> RiskLevel:
        """Calculate risk level from score"""
        if risk_score < 0.2:
            return RiskLevel.VERY_LOW
        elif risk_score < 0.4:
            return RiskLevel.LOW
        elif risk_score < 0.6:
            return RiskLevel.MEDIUM
        elif risk_score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _determine_action(self, risk_score: float, matched_rules: List[str]) -> ActionType:
        """Determine recommended action"""
        if risk_score >= 0.9:
            return ActionType.BLOCK
        elif risk_score >= 0.7:
            return ActionType.DECLINE
        elif risk_score >= 0.5:
            return ActionType.REVIEW
        elif risk_score >= 0.3:
            return ActionType.CHALLENGE
        else:
            return ActionType.ALLOW
    
    def _identify_fraud_types(self, transaction_data: TransactionData, 
                             user_profile: UserProfile, context: Dict[str, Any]) -> List[FraudType]:
        """Identify specific fraud types"""
        fraud_types = []
        
        if context.get('transactions_last_hour', 0) > 5:
            fraud_types.append(FraudType.VELOCITY_FRAUD)
        
        if context.get('new_country', False):
            fraud_types.append(FraudType.GEOGRAPHIC_ANOMALY)
        
        if transaction_data.amount > user_profile.avg_transaction_amount * 5:
            fraud_types.append(FraudType.PAYMENT_FRAUD)
        
        return fraud_types
    
    def _update_metrics(self, result -> None: FraudAnalysisResult) -> None:
        """Update system metrics"""
        self.metrics['total_transactions_analyzed'] += 1
        
        if result.recommended_action == ActionType.BLOCK:
            self.metrics['total_blocked_transactions'] += 1
        elif result.recommended_action == ActionType.REVIEW:
            self.metrics['total_reviewed_transactions'] += 1
        
        if result.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            self.metrics['fraudulent_transactions_detected'] += 1
        
        # Update average analysis time
        total_time = (self.metrics['avg_analysis_time'] * 
                     (self.metrics['total_transactions_analyzed'] - 1) + 
                     result.processing_time_ms)
        self.metrics['avg_analysis_time'] = total_time / self.metrics['total_transactions_analyzed']
    
    def _update_user_profile(self, user_profile -> None: UserProfile, 
                           transaction_data -> None: TransactionData, 
                           result -> None: FraudAnalysisResult) -> None:
        """Update user profile with transaction data"""
        user_profile.total_transactions += 1
        user_profile.total_amount += transaction_data.amount
        user_profile.avg_transaction_amount = user_profile.total_amount / user_profile.total_transactions
        user_profile.last_transaction = transaction_data.timestamp
        
        # Add new data to sets
        if transaction_data.billing_address.get('country'):
            user_profile.countries_used.add(transaction_data.billing_address['country'])
        
        if transaction_data.payment_method:
            user_profile.payment_methods_used.add(transaction_data.payment_method)
        
        if transaction_data.device_fingerprint:
            user_profile.devices_used.add(transaction_data.device_fingerprint)
        
        # Update risk score
        if result.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            user_profile.suspicious_activity_count += 1
            user_profile.risk_score = min(user_profile.risk_score + 0.1, 1.0)
        else:
            user_profile.risk_score = max(user_profile.risk_score - 0.01, 0.0)
        
        user_profile.updated_at = datetime.utcnow()
    
    def _store_transaction_history(self, transaction_data -> None: TransactionData) -> None:
        """Store transaction in history"""
        if transaction_data.user_id not in self.transaction_history:
            self.transaction_history[transaction_data.user_id] = []
        
        self.transaction_history[transaction_data.user_id].append(transaction_data)
        
        # Keep only recent transactions (last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        self.transaction_history[transaction_data.user_id] = [
            t for t in self.transaction_history[transaction_data.user_id]
            if t.timestamp >= cutoff_date
        ]
    
    def add_to_blacklist(self, item_type -> None: str, value -> None: str) -> None:
        """Add item to blacklist"""
        if item_type == 'ip':
            self.blacklisted_ips.add(value)
        elif item_type == 'device':
            self.blacklisted_devices.add(value)
        logger.info(f"Added {item_type} to blacklist: {value}")
    
    def add_to_whitelist(self, user_id -> None: str) -> None:
        """Add user to whitelist"""
        self.whitelisted_users.add(user_id)
        logger.info(f"Added user to whitelist: {user_id}")
    
    def get_analysis_result(self, transaction_id: str) -> Optional[FraudAnalysisResult]:
        """Get fraud analysis result"""
        return self.analysis_results.get(transaction_id)
    
    def get_user_risk_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user risk profile"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return None
        
        return {
            'user_id': profile.user_id,
            'risk_score': profile.risk_score,
            'account_age_days': profile.account_age_days,
            'total_transactions': profile.total_transactions,
            'avg_transaction_amount': profile.avg_transaction_amount,
            'suspicious_activity_count': profile.suspicious_activity_count,
            'countries_used': list(profile.countries_used),
            'payment_methods_used': list(profile.payment_methods_used),
            'last_transaction': profile.last_transaction.isoformat() if profile.last_transaction else None,
            'is_verified': profile.is_verified
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        fraud_detection_rate = (
            self.metrics['fraudulent_transactions_detected'] / self.metrics['total_transactions_analyzed']
            if self.metrics['total_transactions_analyzed'] > 0 else 0
        )
        
        block_rate = (
            self.metrics['total_blocked_transactions'] / self.metrics['total_transactions_analyzed']
            if self.metrics['total_transactions_analyzed'] > 0 else 0
        )
        
        return {
            'level': self.level,
            'total_transactions_analyzed': self.metrics['total_transactions_analyzed'],
            'fraudulent_transactions_detected': self.metrics['fraudulent_transactions_detected'],
            'false_positives': self.metrics['false_positives'],
            'total_blocked_transactions': self.metrics['total_blocked_transactions'],
            'total_reviewed_transactions': self.metrics['total_reviewed_transactions'],
            'fraud_detection_rate': fraud_detection_rate,
            'block_rate': block_rate,
            'avg_analysis_time_ms': self.metrics['avg_analysis_time'],
            'loaded_models': len([m for m in self.models.values() if m.loaded]),
            'total_models': len(self.models),
            'active_rules': len([r for r in self.rule_engine.rules.values() if r.enabled]),
            'total_rules': len(self.rule_engine.rules),
            'user_profiles': len(self.user_profiles),
            'blacklisted_ips': len(self.blacklisted_ips),
            'blacklisted_devices': len(self.blacklisted_devices),
            'whitelisted_users': len(self.whitelisted_users),
            'supported_fraud_types': [ft.value for ft in FraudType],
            'is_running': self.is_running
        }

# Global instance
fraud_detection_core = FraudDetectionCore()

# Convenience functions
async def analyze_transaction_fraud(transaction_data: TransactionData) -> FraudAnalysisResult:
    """Analyze transaction for fraud"""
    return await fraud_detection_core.analyze_transaction(transaction_data)

def get_fraud_analysis_result(transaction_id: str) -> Optional[FraudAnalysisResult]:
    """Get fraud analysis result"""
    return fraud_detection_core.get_analysis_result(transaction_id)

def get_user_risk_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user risk profile"""
    return fraud_detection_core.get_user_risk_profile(user_id)

def blacklist_ip(ip_address -> None: str) -> None:
    """Blacklist IP address"""
    fraud_detection_core.add_to_blacklist('ip', ip_address)

def whitelist_user(user_id -> None: str) -> None:
    """Whitelist user"""
    fraud_detection_core.add_to_whitelist(user_id)

# Module exports
__all__ = [
    "FraudDetectionCore", "TransactionData", "UserProfile", "FraudRule",
    "FraudAnalysisResult", "FraudDetectionModel", "RuleEngine",
    "RiskLevel", "FraudType", "ActionType", "TransactionStatus",
    "fraud_detection_core", "analyze_transaction_fraud", "get_fraud_analysis_result",
    "get_user_risk_profile", "blacklist_ip", "whitelist_user"
]

logger.info("Fraud Detection Core module loaded")