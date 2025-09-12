"""
Ainflue Platform - Chargeback Prevention System
==============================================

Advanced chargeback prevention and management system for monitoring,
predicting, and preventing chargebacks with ML-powered risk assessment
for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class ChargebackReason(Enum):
    """Chargeback reason codes."""
    FRAUD = "fraud"
    AUTHORIZATION = "authorization"
    PROCESSING_ERROR = "processing_error"
    CONSUMER_DISPUTE = "consumer_dispute"
    NON_RECEIPT = "non_receipt"
    DUPLICATE_PROCESSING = "duplicate_processing"
    CREDIT_NOT_PROCESSED = "credit_not_processed"
    CANCELLED_RECURRING = "cancelled_recurring"
    PRODUCT_NOT_RECEIVED = "product_not_received"
    PRODUCT_UNACCEPTABLE = "product_unacceptable"
    OTHER = "other"

class ChargebackStatus(Enum):
    """Chargeback status types."""
    INITIATED = "initiated"
    PENDING = "pending"
    DISPUTED = "disputed"
    WON = "won"
    LOST = "lost"
    ACCEPTED = "accepted"
    REVERSED = "reversed"

class RiskLevel(Enum):
    """Risk level classifications."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"

class PreventionAction(Enum):
    """Prevention action types."""
    BLOCK_TRANSACTION = "block_transaction"
    REQUIRE_VERIFICATION = "require_verification"
    FLAG_FOR_REVIEW = "flag_for_review"
    ADDITIONAL_AUTHENTICATION = "additional_authentication"
    CONTACT_CUSTOMER = "contact_customer"
    REFUND_PROACTIVELY = "refund_proactively"
    NO_ACTION = "no_action"

@dataclass
class ChargebackCase:
    """Chargeback case record."""
    case_id: str
    transaction_id: str
    partnership_id: str
    creator_id: str
    amount: float
    currency: str
    reason: ChargebackReason
    status: ChargebackStatus
    initiation_date: datetime
    response_deadline: datetime
    evidence_submitted: bool
    outcome: Optional[str]
    resolution_date: Optional[datetime]
    fees_incurred: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskAssessment:
    """Risk assessment for a transaction."""
    transaction_id: str
    risk_level: RiskLevel
    risk_score: float
    risk_factors: List[str]
    prevention_actions: List[PreventionAction]
    confidence_score: float
    assessment_timestamp: datetime
    expiry_timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PreventionRule:
    """Chargeback prevention rule."""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    action: PreventionAction
    threshold: float
    is_active: bool
    priority: int
    created_date: datetime
    last_modified: datetime
    effectiveness_score: float

@dataclass
class PreventionMetrics:
    """Chargeback prevention metrics."""
    time_period: Tuple[datetime, datetime]
    total_transactions: int
    total_chargebacks: int
    chargeback_rate: float
    prevented_chargebacks: int
    false_positives: int
    prevention_accuracy: float
    total_savings: float
    average_response_time: float
    win_rate: float
    risk_distribution: Dict[RiskLevel, int]
    timestamp: datetime = field(default_factory=datetime.now)

class ChargebackPreventionSystem:
    """
    Advanced chargeback prevention system for monetization protection.
    
    Features:
    - Real-time risk assessment
    - ML-powered chargeback prediction
    - Automated prevention actions
    - Evidence management
    - Dispute tracking and management
    - Performance analytics
    - Rule-based prevention engine
    - Cost-benefit optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.chargeback_cases: Dict[str, List[ChargebackCase]] = defaultdict(list)
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        self.prevention_rules: Dict[str, PreventionRule] = {}
        self.transaction_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # ML models for risk prediction
        self.risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_model_trained = False
        
        # Prevention thresholds
        self.risk_thresholds = {
            RiskLevel.VERY_LOW: 0.1,
            RiskLevel.LOW: 0.2,
            RiskLevel.MEDIUM: 0.4,
            RiskLevel.HIGH: 0.6,
            RiskLevel.VERY_HIGH: 0.8,
            RiskLevel.CRITICAL: 0.9
        }
        
        # Performance metrics
        self.metrics = {
            'total_chargebacks': 0,
            'prevented_chargebacks': 0,
            'total_savings': 0.0,
            'prevention_accuracy': 0.0,
            'false_positive_rate': 0.0,
            'average_risk_score': 0.0,
            'rules_triggered': 0,
            'model_predictions': 0
        }
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info("ChargebackPreventionSystem initialized")

    def _initialize_default_rules(self):
        """Initialize default prevention rules."""
        default_rules = [
            {
                'name': 'High Amount Transaction',
                'description': 'Flag transactions above $1000 for review',
                'conditions': {'amount_threshold': 1000.0},
                'action': PreventionAction.FLAG_FOR_REVIEW,
                'threshold': 0.5,
                'priority': 1
            },
            {
                'name': 'Multiple Failed Attempts',
                'description': 'Block transactions after multiple failed attempts',
                'conditions': {'failed_attempts_threshold': 3},
                'action': PreventionAction.BLOCK_TRANSACTION,
                'threshold': 0.8,
                'priority': 2
            },
            {
                'name': 'New Payment Method',
                'description': 'Require verification for new payment methods',
                'conditions': {'new_payment_method': True},
                'action': PreventionAction.REQUIRE_VERIFICATION,
                'threshold': 0.3,
                'priority': 3
            },
            {
                'name': 'Suspicious Geographic Pattern',
                'description': 'Flag transactions from unusual locations',
                'conditions': {'geographic_anomaly': True},
                'action': PreventionAction.ADDITIONAL_AUTHENTICATION,
                'threshold': 0.6,
                'priority': 4
            },
            {
                'name': 'High Velocity Transactions',
                'description': 'Flag rapid successive transactions',
                'conditions': {'transaction_velocity_threshold': 5},
                'action': PreventionAction.FLAG_FOR_REVIEW,
                'threshold': 0.7,
                'priority': 5
            }
        ]
        
        for rule_data in default_rules:
            rule = PreventionRule(
                rule_id=str(uuid.uuid4()),
                name=rule_data['name'],
                description=rule_data['description'],
                conditions=rule_data['conditions'],
                action=rule_data['action'],
                threshold=rule_data['threshold'],
                is_active=True,
                priority=rule_data['priority'],
                created_date=datetime.now(),
                last_modified=datetime.now(),
                effectiveness_score=0.0
            )
            self.prevention_rules[rule.rule_id] = rule

    async def assess_transaction_risk(
        self,
        transaction_data: Dict[str, Any],
        partnership_id: str
    ) -> RiskAssessment:
        """Assess chargeback risk for a transaction."""
        try:
            transaction_id = transaction_data.get('transaction_id', str(uuid.uuid4()))
            
            # Extract features for risk assessment
            features = self._extract_risk_features(transaction_data, partnership_id)
            
            # Calculate ML-based risk score
            ml_risk_score = await self._calculate_ml_risk_score(features)
            
            # Apply rule-based assessment
            rule_risk_score, triggered_rules = await self._apply_prevention_rules(transaction_data)
            
            # Combine scores
            combined_risk_score = (0.7 * ml_risk_score + 0.3 * rule_risk_score)
            
            # Determine risk level
            risk_level = self._determine_risk_level(combined_risk_score)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(features, triggered_rules)
            
            # Determine prevention actions
            prevention_actions = self._determine_prevention_actions(risk_level, triggered_rules)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(features, ml_risk_score, rule_risk_score)
            
            # Create risk assessment
            assessment = RiskAssessment(
                transaction_id=transaction_id,
                risk_level=risk_level,
                risk_score=combined_risk_score,
                risk_factors=risk_factors,
                prevention_actions=prevention_actions,
                confidence_score=confidence_score,
                assessment_timestamp=datetime.now(),
                expiry_timestamp=datetime.now() + timedelta(hours=24),
                metadata={
                    'ml_score': ml_risk_score,
                    'rule_score': rule_risk_score,
                    'triggered_rules': [rule.name for rule in triggered_rules],
                    'features_analyzed': len(features)
                }
            )
            
            # Store assessment
            self.risk_assessments[transaction_id] = assessment
            
            # Update metrics
            self.metrics['model_predictions'] += 1
            self.metrics['average_risk_score'] = (
                (self.metrics['average_risk_score'] * (self.metrics['model_predictions'] - 1) + combined_risk_score) /
                self.metrics['model_predictions']
            )
            
            logger.info(f"Risk assessment completed: {risk_level.value} (score: {combined_risk_score:.3f})")
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing transaction risk: {e}")
            raise

    def _extract_risk_features(self, transaction_data: Dict[str, Any], partnership_id: str) -> Dict[str, float]:
        """Extract features for risk assessment."""
        features = {}
        
        try:
            # Transaction amount features
            amount = transaction_data.get('amount', 0.0)
            features['transaction_amount'] = amount
            features['amount_log'] = np.log(amount + 1)
            
            # Historical amount comparison
            history = list(self.transaction_history[partnership_id])
            if history:
                avg_historical_amount = np.mean([t.get('amount', 0) for t in history])
                features['amount_vs_historical'] = amount / avg_historical_amount if avg_historical_amount > 0 else 1.0
            else:
                features['amount_vs_historical'] = 1.0
            
            # Payment method features
            payment_method = transaction_data.get('payment_method', 'unknown')
            payment_method_risk = {
                'credit_card': 0.3,
                'debit_card': 0.2,
                'paypal': 0.1,
                'apple_pay': 0.1,
                'google_pay': 0.1,
                'bank_transfer': 0.05,
                'unknown': 0.5
            }
            features['payment_method_risk'] = payment_method_risk.get(payment_method, 0.5)
            
            # Customer features
            customer_data = transaction_data.get('customer', {})
            features['customer_age_days'] = (datetime.now() - datetime.fromisoformat(
                customer_data.get('registration_date', datetime.now().isoformat())
            )).days
            features['customer_transaction_count'] = customer_data.get('transaction_count', 0)
            features['customer_chargeback_history'] = customer_data.get('chargeback_count', 0)
            
            # Geographic features
            geo_data = transaction_data.get('geographic', {})
            country_risk = {
                'US': 0.1, 'CA': 0.1, 'GB': 0.1, 'DE': 0.1, 'FR': 0.1,
                'AU': 0.1, 'JP': 0.1, 'KR': 0.1, 'SG': 0.1, 'NL': 0.1,
                'unknown': 0.3
            }
            features['country_risk'] = country_risk.get(geo_data.get('country', 'unknown'), 0.3)
            
            # Time-based features
            hour = datetime.now().hour
            features['transaction_hour'] = hour
            features['is_weekend'] = datetime.now().weekday() >= 5
            features['is_night_time'] = hour < 6 or hour > 22
            
            # Velocity features
            recent_transactions = [t for t in history if 
                                   (datetime.now() - datetime.fromisoformat(t.get('timestamp', datetime.now().isoformat()))).hours < 24]
            features['transactions_last_24h'] = len(recent_transactions)
            features['amount_last_24h'] = sum(t.get('amount', 0) for t in recent_transactions)
            
            # Platform features
            features['is_first_transaction'] = len(history) == 0
            features['average_days_between_transactions'] = self._calculate_avg_days_between_transactions(history)
            
            # Device/IP features
            device_data = transaction_data.get('device', {})
            features['new_device'] = device_data.get('is_new_device', False)
            features['new_ip'] = device_data.get('is_new_ip', False)
            features['device_risk_score'] = device_data.get('risk_score', 0.0)
            
            # Merchant category features
            merchant_data = transaction_data.get('merchant', {})
            features['merchant_category_risk'] = merchant_data.get('category_risk', 0.0)
            features['merchant_chargeback_rate'] = merchant_data.get('chargeback_rate', 0.0)
            
        except Exception as e:
            logger.error(f"Error extracting risk features: {e}")
        
        return features

    def _calculate_avg_days_between_transactions(self, history: List[Dict[str, Any]]) -> float:
        """Calculate average days between transactions."""
        if len(history) < 2:
            return 0.0
        
        timestamps = [datetime.fromisoformat(t.get('timestamp', datetime.now().isoformat())) for t in history]
        timestamps.sort()
        
        intervals = [(timestamps[i] - timestamps[i-1]).days for i in range(1, len(timestamps))]
        return np.mean(intervals) if intervals else 0.0

    async def _calculate_ml_risk_score(self, features: Dict[str, float]) -> float:
        """Calculate ML-based risk score."""
        try:
            if not self.is_model_trained:
                # If model isn't trained, use a simple heuristic
                return self._calculate_heuristic_risk_score(features)
            
            # Convert features to array
            feature_array = np.array([list(features.values())]).reshape(1, -1)
            
            # Scale features
            feature_array_scaled = self.scaler.transform(feature_array)
            
            # Predict risk probability
            risk_probabilities = self.risk_model.predict_proba(feature_array_scaled)
            
            # Return probability of chargeback
            return risk_probabilities[0][1] if len(risk_probabilities[0]) > 1 else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating ML risk score: {e}")
            return self._calculate_heuristic_risk_score(features)

    def _calculate_heuristic_risk_score(self, features: Dict[str, float]) -> float:
        """Calculate heuristic risk score when ML model is not available."""
        score = 0.0
        
        # Amount-based risk
        amount = features.get('transaction_amount', 0)
        if amount > 1000:
            score += 0.3
        elif amount > 500:
            score += 0.2
        elif amount > 100:
            score += 0.1
        
        # Payment method risk
        score += features.get('payment_method_risk', 0) * 0.3
        
        # Customer history risk
        if features.get('customer_chargeback_history', 0) > 0:
            score += 0.4
        
        if features.get('is_first_transaction', False):
            score += 0.2
        
        # Geographic risk
        score += features.get('country_risk', 0) * 0.2
        
        # Velocity risk
        if features.get('transactions_last_24h', 0) > 5:
            score += 0.3
        
        # Time-based risk
        if features.get('is_night_time', False):
            score += 0.1
        
        # Device risk
        if features.get('new_device', False):
            score += 0.2
        
        return min(score, 1.0)

    async def _apply_prevention_rules(self, transaction_data: Dict[str, Any]) -> Tuple[float, List[PreventionRule]]:
        """Apply prevention rules and return risk score."""
        triggered_rules = []
        max_risk_score = 0.0
        
        for rule in self.prevention_rules.values():
            if not rule.is_active:
                continue
            
            if self._evaluate_rule_conditions(rule, transaction_data):
                triggered_rules.append(rule)
                max_risk_score = max(max_risk_score, rule.threshold)
                self.metrics['rules_triggered'] += 1
        
        # Sort by priority
        triggered_rules.sort(key=lambda r: r.priority)
        
        return max_risk_score, triggered_rules

    def _evaluate_rule_conditions(self, rule: PreventionRule, transaction_data: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met."""
        try:
            conditions = rule.conditions
            
            # Amount threshold check
            if 'amount_threshold' in conditions:
                amount = transaction_data.get('amount', 0)
                if amount < conditions['amount_threshold']:
                    return False
            
            # Failed attempts check
            if 'failed_attempts_threshold' in conditions:
                failed_attempts = transaction_data.get('customer', {}).get('failed_attempts', 0)
                if failed_attempts < conditions['failed_attempts_threshold']:
                    return False
            
            # New payment method check
            if 'new_payment_method' in conditions:
                is_new = transaction_data.get('customer', {}).get('new_payment_method', False)
                if is_new != conditions['new_payment_method']:
                    return False
            
            # Geographic anomaly check
            if 'geographic_anomaly' in conditions:
                is_anomaly = transaction_data.get('geographic', {}).get('is_anomaly', False)
                if is_anomaly != conditions['geographic_anomaly']:
                    return False
            
            # Transaction velocity check
            if 'transaction_velocity_threshold' in conditions:
                velocity = transaction_data.get('velocity', {}).get('last_24h', 0)
                if velocity < conditions['transaction_velocity_threshold']:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating rule conditions: {e}")
            return False

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score."""
        for level, threshold in reversed(list(self.risk_thresholds.items())):
            if risk_score >= threshold:
                return level
        return RiskLevel.VERY_LOW

    def _identify_risk_factors(self, features: Dict[str, float], triggered_rules: List[PreventionRule]) -> List[str]:
        """Identify specific risk factors."""
        factors = []
        
        # Rule-based factors
        for rule in triggered_rules:
            factors.append(f"Rule triggered: {rule.name}")
        
        # Feature-based factors
        if features.get('transaction_amount', 0) > 1000:
            factors.append("High transaction amount")
        
        if features.get('customer_chargeback_history', 0) > 0:
            factors.append("Customer has chargeback history")
        
        if features.get('is_first_transaction', False):
            factors.append("First-time customer")
        
        if features.get('transactions_last_24h', 0) > 5:
            factors.append("High transaction velocity")
        
        if features.get('new_device', False):
            factors.append("New device detected")
        
        if features.get('country_risk', 0) > 0.2:
            factors.append("High-risk geographic location")
        
        if features.get('is_night_time', False):
            factors.append("Off-hours transaction")
        
        return factors

    def _determine_prevention_actions(self, risk_level: RiskLevel, triggered_rules: List[PreventionRule]) -> List[PreventionAction]:
        """Determine prevention actions based on risk level and rules."""
        actions = set()
        
        # Rule-based actions
        for rule in triggered_rules:
            actions.add(rule.action)
        
        # Risk level-based actions
        if risk_level == RiskLevel.CRITICAL:
            actions.add(PreventionAction.BLOCK_TRANSACTION)
        elif risk_level == RiskLevel.VERY_HIGH:
            actions.add(PreventionAction.ADDITIONAL_AUTHENTICATION)
            actions.add(PreventionAction.FLAG_FOR_REVIEW)
        elif risk_level == RiskLevel.HIGH:
            actions.add(PreventionAction.REQUIRE_VERIFICATION)
        elif risk_level == RiskLevel.MEDIUM:
            actions.add(PreventionAction.FLAG_FOR_REVIEW)
        
        if not actions:
            actions.add(PreventionAction.NO_ACTION)
        
        return list(actions)

    def _calculate_confidence_score(self, features: Dict[str, float], ml_score: float, rule_score: float) -> float:
        """Calculate confidence score for risk assessment."""
        factors = []
        
        # Feature completeness
        expected_features = 20  # Expected number of features
        completeness = len(features) / expected_features
        factors.append(min(completeness, 1.0))
        
        # ML model confidence (if trained)
        if self.is_model_trained:
            factors.append(0.9)  # High confidence in trained model
        else:
            factors.append(0.6)  # Lower confidence in heuristic
        
        # Rule consistency
        rule_confidence = min(rule_score * 2, 1.0) if rule_score > 0 else 0.8
        factors.append(rule_confidence)
        
        # Score consistency between ML and rules
        score_diff = abs(ml_score - rule_score)
        consistency = max(0.5, 1.0 - score_diff)
        factors.append(consistency)
        
        return np.mean(factors)

    async def record_chargeback(
        self,
        transaction_id: str,
        partnership_id: str,
        creator_id: str,
        amount: float,
        currency: str,
        reason: ChargebackReason,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChargebackCase:
        """Record a new chargeback case."""
        try:
            case = ChargebackCase(
                case_id=str(uuid.uuid4()),
                transaction_id=transaction_id,
                partnership_id=partnership_id,
                creator_id=creator_id,
                amount=amount,
                currency=currency,
                reason=reason,
                status=ChargebackStatus.INITIATED,
                initiation_date=datetime.now(),
                response_deadline=datetime.now() + timedelta(days=7),  # Typical response time
                evidence_submitted=False,
                outcome=None,
                resolution_date=None,
                fees_incurred=amount * 0.15,  # Typical chargeback fee (15%)
                metadata=metadata or {}
            )
            
            # Store chargeback case
            self.chargeback_cases[partnership_id].append(case)
            
            # Update metrics
            self.metrics['total_chargebacks'] += 1
            
            # Check if this chargeback was predicted
            await self._evaluate_prediction_accuracy(transaction_id)
            
            # Update ML model with new data
            await self._update_model_with_chargeback(transaction_id, case)
            
            logger.info(f"Recorded chargeback: ${amount} for transaction {transaction_id}")
            return case
            
        except Exception as e:
            logger.error(f"Error recording chargeback: {e}")
            raise

    async def _evaluate_prediction_accuracy(self, transaction_id: str):
        """Evaluate prediction accuracy for a chargeback."""
        assessment = self.risk_assessments.get(transaction_id)
        if assessment:
            # If we predicted high risk and got a chargeback, it's accurate
            if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL]:
                # Correct prediction
                self._update_accuracy_metrics(True)
            else:
                # Missed prediction
                self._update_accuracy_metrics(False)

    def _update_accuracy_metrics(self, correct_prediction: bool):
        """Update prediction accuracy metrics."""
        current_accuracy = self.metrics['prevention_accuracy']
        total_predictions = self.metrics['model_predictions']
        
        if total_predictions > 0:
            new_accuracy = ((current_accuracy * (total_predictions - 1)) + (1.0 if correct_prediction else 0.0)) / total_predictions
            self.metrics['prevention_accuracy'] = new_accuracy

    async def _update_model_with_chargeback(self, transaction_id: str, case: ChargebackCase):
        """Update ML model with chargeback data."""
        # This would typically involve retraining the model with new data
        # For now, we'll just log the update
        logger.info(f"Model update triggered by chargeback {case.case_id}")

    async def execute_prevention_action(
        self,
        transaction_id: str,
        action: PreventionAction,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a prevention action."""
        try:
            result = {'action': action.value, 'executed': True, 'timestamp': datetime.now()}
            
            if action == PreventionAction.BLOCK_TRANSACTION:
                result['message'] = "Transaction blocked due to high chargeback risk"
                result['blocked'] = True
                
            elif action == PreventionAction.REQUIRE_VERIFICATION:
                result['message'] = "Additional verification required"
                result['verification_required'] = True
                
            elif action == PreventionAction.FLAG_FOR_REVIEW:
                result['message'] = "Transaction flagged for manual review"
                result['review_required'] = True
                
            elif action == PreventionAction.ADDITIONAL_AUTHENTICATION:
                result['message'] = "Additional authentication required"
                result['auth_required'] = True
                
            elif action == PreventionAction.CONTACT_CUSTOMER:
                result['message'] = "Customer contact initiated for verification"
                result['contact_initiated'] = True
                
            elif action == PreventionAction.REFUND_PROACTIVELY:
                result['message'] = "Proactive refund processed to prevent chargeback"
                result['refund_processed'] = True
                self.metrics['prevented_chargebacks'] += 1
                
            else:  # NO_ACTION
                result['message'] = "No action required"
                result['blocked'] = False
            
            # Add metadata
            if metadata:
                result['metadata'] = metadata
            
            logger.info(f"Executed prevention action: {action.value} for transaction {transaction_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing prevention action: {e}")
            return {'action': action.value, 'executed': False, 'error': str(e)}

    async def update_chargeback_status(
        self,
        case_id: str,
        status: ChargebackStatus,
        outcome: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update chargeback case status."""
        try:
            # Find the case
            case = None
            for partnership_cases in self.chargeback_cases.values():
                for cb_case in partnership_cases:
                    if cb_case.case_id == case_id:
                        case = cb_case
                        break
                if case:
                    break
            
            if not case:
                logger.error(f"Chargeback case {case_id} not found")
                return False
            
            # Update case
            case.status = status
            if outcome:
                case.outcome = outcome
            
            if status in [ChargebackStatus.WON, ChargebackStatus.LOST, ChargebackStatus.ACCEPTED]:
                case.resolution_date = datetime.now()
            
            if metadata:
                case.metadata.update(metadata)
            
            logger.info(f"Updated chargeback case {case_id} status to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating chargeback status: {e}")
            return False

    async def get_prevention_metrics(
        self,
        partnership_id: Optional[str] = None,
        time_period: Optional[Tuple[datetime, datetime]] = None
    ) -> PreventionMetrics:
        """Get chargeback prevention metrics."""
        try:
            # Determine time period
            if not time_period:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                time_period = (start_date, end_date)
            else:
                start_date, end_date = time_period
            
            # Get relevant data
            if partnership_id:
                chargeback_cases = [
                    case for case in self.chargeback_cases.get(partnership_id, [])
                    if start_date <= case.initiation_date <= end_date
                ]
                # Would need transaction data to get total transactions
                total_transactions = 100  # Placeholder
            else:
                chargeback_cases = []
                for partnership_cases in self.chargeback_cases.values():
                    chargeback_cases.extend([
                        case for case in partnership_cases
                        if start_date <= case.initiation_date <= end_date
                    ])
                total_transactions = 1000  # Placeholder
            
            # Calculate metrics
            total_chargebacks = len(chargeback_cases)
            chargeback_rate = total_chargebacks / total_transactions if total_transactions > 0 else 0.0
            
            # Prevention metrics
            prevented_chargebacks = self.metrics['prevented_chargebacks']
            false_positives = 0  # Would need to calculate from blocked legitimate transactions
            
            prevention_accuracy = self.metrics['prevention_accuracy']
            
            # Financial metrics
            total_chargeback_amount = sum(case.amount + case.fees_incurred for case in chargeback_cases)
            total_savings = prevented_chargebacks * 50  # Placeholder average chargeback amount
            self.metrics['total_savings'] = total_savings
            
            # Response time metrics
            resolved_cases = [case for case in chargeback_cases if case.resolution_date]
            if resolved_cases:
                response_times = [
                    (case.resolution_date - case.initiation_date).days
                    for case in resolved_cases
                ]
                average_response_time = np.mean(response_times)
            else:
                average_response_time = 0.0
            
            # Win rate
            won_cases = len([case for case in resolved_cases if case.status == ChargebackStatus.WON])
            win_rate = won_cases / len(resolved_cases) if resolved_cases else 0.0
            
            # Risk distribution
            risk_distribution = defaultdict(int)
            for assessment in self.risk_assessments.values():
                if start_date <= assessment.assessment_timestamp <= end_date:
                    risk_distribution[assessment.risk_level] += 1
            
            metrics = PreventionMetrics(
                time_period=time_period,
                total_transactions=total_transactions,
                total_chargebacks=total_chargebacks,
                chargeback_rate=chargeback_rate,
                prevented_chargebacks=prevented_chargebacks,
                false_positives=false_positives,
                prevention_accuracy=prevention_accuracy,
                total_savings=total_savings,
                average_response_time=average_response_time,
                win_rate=win_rate,
                risk_distribution=dict(risk_distribution)
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting prevention metrics: {e}")
            raise

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        try:
            return {
                'total_chargebacks': self.metrics['total_chargebacks'],
                'prevented_chargebacks': self.metrics['prevented_chargebacks'],
                'total_savings': self.metrics['total_savings'],
                'prevention_accuracy': self.metrics['prevention_accuracy'],
                'false_positive_rate': self.metrics['false_positive_rate'],
                'average_risk_score': self.metrics['average_risk_score'],
                'rules_triggered': self.metrics['rules_triggered'],
                'model_predictions': self.metrics['model_predictions'],
                'active_rules': len([r for r in self.prevention_rules.values() if r.is_active]),
                'total_rules': len(self.prevention_rules),
                'partnerships_monitored': len(self.chargeback_cases),
                'assessments_cached': len(self.risk_assessments),
                'is_model_trained': self.is_model_trained,
                'risk_thresholds': {level.value: threshold for level, threshold in self.risk_thresholds.items()}
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    async def test_chargeback_prevention():
        """Test chargeback prevention system."""
        system = ChargebackPreventionSystem()
        
        # Sample transaction data
        transaction_data = {
            'transaction_id': 'txn_001',
            'amount': 1500.0,
            'payment_method': 'credit_card',
            'customer': {
                'registration_date': '2024-01-01T00:00:00',
                'transaction_count': 5,
                'chargeback_count': 0,
                'failed_attempts': 1
            },
            'geographic': {
                'country': 'US',
                'is_anomaly': False
            },
            'device': {
                'is_new_device': True,
                'is_new_ip': False,
                'risk_score': 0.3
            },
            'velocity': {
                'last_24h': 2
            }
        }
        
        try:
            # Assess transaction risk
            assessment = await system.assess_transaction_risk(transaction_data, "partnership_001")
            print(f"Risk Assessment:")
            print(f"  Risk Level: {assessment.risk_level.value}")
            print(f"  Risk Score: {assessment.risk_score:.3f}")
            print(f"  Confidence: {assessment.confidence_score:.3f}")
            print(f"  Risk Factors: {assessment.risk_factors}")
            print(f"  Prevention Actions: {[action.value for action in assessment.prevention_actions]}")
            
            # Execute prevention action
            if assessment.prevention_actions:
                result = await system.execute_prevention_action(
                    transaction_data['transaction_id'],
                    assessment.prevention_actions[0]
                )
                print(f"Prevention Action Result: {result}")
            
            # Record a chargeback (for testing)
            chargeback = await system.record_chargeback(
                transaction_data['transaction_id'],
                "partnership_001",
                "creator_001",
                1500.0,
                "USD",
                ChargebackReason.FRAUD
            )
            print(f"Recorded chargeback: {chargeback.case_id}")
            
            # Get prevention metrics
            metrics = await system.get_prevention_metrics("partnership_001")
            print(f"Prevention Metrics:")
            print(f"  Chargeback Rate: {metrics.chargeback_rate:.3f}")
            print(f"  Prevention Accuracy: {metrics.prevention_accuracy:.3f}")
            print(f"  Total Savings: ${metrics.total_savings}")
            
            # Get system metrics
            system_metrics = await system.get_system_metrics()
            print(f"System Metrics: {system_metrics}")
            
        except Exception as e:
            print(f"Error in test: {e}")
    
    # Run test
    asyncio.run(test_chargeback_prevention())