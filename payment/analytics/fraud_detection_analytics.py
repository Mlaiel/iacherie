"""🔒 Fraud Detection Analytics - Enterprise Security Intelligence
==============================================================

Advanced ML-powered fraud detection and prevention analytics for Creator Economy Platform.
Provides comprehensive fraud pattern analysis, risk assessment, and real-time threat detection.

Performance Targets: < 100ms fraud analysis
Security-first design with ML anomaly detection.

Key Features:
- Real-time fraud pattern detection
- ML-powered risk scoring
- Suspicious transaction analysis
- Creator behavior anomaly detection
- Payment method fraud analysis
- Geographic fraud pattern recognition
- Velocity fraud detection
- Account takeover prevention

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import statistics
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid
from concurrent.futures import ThreadPoolExecutor
import redis
import asyncpg
import hashlib
import ipaddress
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)


class FraudType(Enum):
    """Types of fraud detected"""
    CARD_FRAUD = "card_fraud"
    ACCOUNT_TAKEOVER = "account_takeover"
    IDENTITY_THEFT = "identity_theft"
    VELOCITY_FRAUD = "velocity_fraud"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    SYNTHETIC_IDENTITY = "synthetic_identity"
    CHARGEBACK_FRAUD = "chargeback_fraud"
    REFUND_ABUSE = "refund_abuse"
    BONUS_ABUSE = "bonus_abuse"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudStatus(Enum):
    """Fraud case status"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


@dataclass
class FraudAlert:
    """Fraud detection alert"""
    alert_id: str
    fraud_type: FraudType
    risk_level: RiskLevel
    risk_score: float
    transaction_id: Optional[str]
    creator_id: Optional[str]
    user_id: Optional[str]
    amount: Optional[Decimal]
    currency: str
    payment_method: str
    ip_address: str
    user_agent: str
    geographic_location: Dict[str, str]
    detection_rules: List[str]
    ml_features: Dict[str, float]
    confidence_score: float
    detected_at: datetime
    investigation_notes: str = ""
    status: FraudStatus = FraudStatus.DETECTED
    false_positive_probability: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class FraudPattern:
    """Detected fraud pattern"""
    pattern_id: str
    pattern_type: FraudType
    pattern_name: str
    description: str
    detection_rules: List[str]
    affected_transactions: List[str]
    affected_users: List[str]
    total_loss_amount: Decimal
    detection_rate: float
    false_positive_rate: float
    pattern_strength: float
    first_detected: datetime
    last_detected: datetime
    geographic_distribution: Dict[str, int]
    time_distribution: Dict[str, int]
    prevention_effectiveness: float


@dataclass
class RiskAssessment:
    """User/Creator risk assessment"""
    entity_id: str
    entity_type: str  # "user", "creator", "merchant"
    overall_risk_score: float
    risk_level: RiskLevel
    risk_factors: Dict[str, float]
    behavioral_anomalies: List[Dict[str, Any]]
    transaction_patterns: Dict[str, Any]
    account_age_days: int
    verification_status: Dict[str, bool]
    previous_fraud_incidents: int
    trust_score: float
    velocity_metrics: Dict[str, float]
    geographic_risk: float
    device_risk: float
    payment_method_risk: float
    assessment_date: datetime
    expires_at: datetime
    recommendations: List[str]


@dataclass
class FraudMetrics:
    """Fraud detection performance metrics"""
    period_start: datetime
    period_end: datetime
    total_transactions: int
    flagged_transactions: int
    confirmed_fraud_cases: int
    false_positive_cases: int
    fraud_detection_rate: float
    false_positive_rate: float
    precision: float
    recall: float
    f1_score: float
    total_fraud_amount: Decimal
    prevented_fraud_amount: Decimal
    fraud_rate_by_type: Dict[FraudType, float]
    fraud_rate_by_geography: Dict[str, float]
    fraud_rate_by_payment_method: Dict[str, float]
    average_detection_time_seconds: float
    model_performance: Dict[str, float]
    cost_savings: Decimal
    roi_fraud_prevention: float


class FraudAnalyzer:
    """Core fraud analysis engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ml_models = {}
        self.scaler = StandardScaler()
        self.fraud_rules = self._load_fraud_rules()
        self.risk_thresholds = config.get("risk_thresholds", {})
        self.geographic_risk_db = self._load_geographic_risks()
        
        # Performance tracking
        self.analysis_times = deque(maxlen=1000)
        self.cache_hit_rate = 0.0
        
    async def analyze_transaction_fraud(
        self,
        transaction: Dict[str, Any],
        user_context: Dict[str, Any],
        real_time: bool = True
    ) -> FraudAlert:
        """Analyze transaction for fraud indicators"""
        start_time = datetime.now()
        
        try:
            transaction_id = transaction.get('id', str(uuid.uuid4()))
            amount = Decimal(str(transaction.get('amount', 0)))
            
            # Extract features for ML analysis
            features = await self._extract_fraud_features(transaction, user_context)
            
            # Rule-based fraud detection
            rule_violations = await self._check_fraud_rules(transaction, user_context)
            
            # ML-based anomaly detection
            ml_score = await self._calculate_ml_fraud_score(features)
            
            # Velocity checking
            velocity_score = await self._check_velocity_fraud(transaction, user_context)
            
            # Geographic risk assessment
            geo_risk = await self._assess_geographic_risk(transaction, user_context)
            
            # Behavioral analysis
            behavior_score = await self._analyze_behavioral_patterns(transaction, user_context)
            
            # Calculate composite risk score
            risk_score = await self._calculate_composite_risk_score({
                'ml_score': ml_score,
                'velocity_score': velocity_score,
                'geo_risk': geo_risk,
                'behavior_score': behavior_score,
                'rule_violations': len(rule_violations)
            })
            
            # Determine fraud type and risk level
            fraud_type = await self._classify_fraud_type(features, rule_violations)
            risk_level = self._classify_risk_level(risk_score)
            
            # Calculate confidence and false positive probability
            confidence_score = await self._calculate_confidence_score(risk_score, features)
            fp_probability = await self._estimate_false_positive_probability(features, rule_violations)
            
            # Generate recommendations
            recommendations = await self._generate_fraud_recommendations(
                risk_level, fraud_type, rule_violations
            )
            
            # Record analysis time
            analysis_time = (datetime.now() - start_time).total_seconds() * 1000
            self.analysis_times.append(analysis_time)
            
            alert = FraudAlert(
                alert_id=str(uuid.uuid4()),
                fraud_type=fraud_type,
                risk_level=risk_level,
                risk_score=risk_score,
                transaction_id=transaction_id,
                creator_id=transaction.get('creator_id'),
                user_id=user_context.get('user_id'),
                amount=amount,
                currency=transaction.get('currency', 'USD'),
                payment_method=transaction.get('payment_method', 'unknown'),
                ip_address=user_context.get('ip_address', ''),
                user_agent=user_context.get('user_agent', ''),
                geographic_location=user_context.get('location', {}),
                detection_rules=rule_violations,
                ml_features=features,
                confidence_score=confidence_score,
                detected_at=datetime.now(),
                false_positive_probability=fp_probability,
                recommended_actions=recommendations
            )
            
            # Store alert if significant risk
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self._store_fraud_alert(alert)
                
                # Real-time notifications for critical cases
                if risk_level == RiskLevel.CRITICAL and real_time:
                    await self._send_real_time_alert(alert)
            
            logger.info(f"Fraud analysis completed in {analysis_time:.2f}ms - Risk: {risk_level.value}")
            return alert
            
        except Exception as e:
            logger.error(f"Error in fraud analysis: {e}")
            raise
    
    async def detect_fraud_patterns(
        self,
        period_start: datetime,
        period_end: datetime,
        min_pattern_strength: float = 0.7
    ) -> List[FraudPattern]:
        """Detect fraud patterns across transactions"""
        try:
            # Get fraud alerts for period
            fraud_alerts = await self._get_fraud_alerts(period_start, period_end)
            
            # Group alerts by similarity
            pattern_groups = await self._group_similar_alerts(fraud_alerts)
            
            patterns = []
            for group_id, alert_group in pattern_groups.items():
                if len(alert_group) < 3:  # Minimum alerts for pattern
                    continue
                
                pattern = await self._analyze_pattern_group(alert_group, min_pattern_strength)
                if pattern and pattern.pattern_strength >= min_pattern_strength:
                    patterns.append(pattern)
            
            # Sort by pattern strength and impact
            patterns.sort(key=lambda p: (p.pattern_strength, p.total_loss_amount), reverse=True)
            
            logger.info(f"Detected {len(patterns)} fraud patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting fraud patterns: {e}")
            raise
    
    async def analyze_suspicious_behavior(
        self,
        entity_id: str,
        entity_type: str,
        lookback_days: int = 30
    ) -> RiskAssessment:
        """Analyze entity for suspicious behavior patterns"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Get entity transaction history
            transactions = await self._get_entity_transactions(entity_id, start_date, end_date)
            
            # Get entity profile data
            profile_data = await self._get_entity_profile(entity_id, entity_type)
            
            # Calculate behavioral metrics
            behavior_metrics = await self._calculate_behavioral_metrics(transactions, profile_data)
            
            # Detect behavioral anomalies
            anomalies = await self._detect_behavioral_anomalies(behavior_metrics, entity_type)
            
            # Calculate risk factors
            risk_factors = await self._calculate_risk_factors(
                transactions, profile_data, behavior_metrics, anomalies
            )
            
            # Calculate overall risk score
            overall_risk = await self._calculate_overall_risk_score(risk_factors)
            risk_level = self._classify_risk_level(overall_risk)
            
            # Generate recommendations
            recommendations = await self._generate_risk_recommendations(
                risk_level, risk_factors, anomalies
            )
            
            assessment = RiskAssessment(
                entity_id=entity_id,
                entity_type=entity_type,
                overall_risk_score=overall_risk,
                risk_level=risk_level,
                risk_factors=risk_factors,
                behavioral_anomalies=anomalies,
                transaction_patterns=behavior_metrics,
                account_age_days=profile_data.get('account_age_days', 0),
                verification_status=profile_data.get('verification_status', {}),
                previous_fraud_incidents=profile_data.get('fraud_incidents', 0),
                trust_score=await self._calculate_trust_score(profile_data, behavior_metrics),
                velocity_metrics=await self._calculate_velocity_metrics(transactions),
                geographic_risk=await self._calculate_geographic_risk_score(transactions),
                device_risk=await self._calculate_device_risk_score(transactions),
                payment_method_risk=await self._calculate_payment_method_risk_score(transactions),
                assessment_date=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7),
                recommendations=recommendations
            )
            
            # Store assessment
            await self._store_risk_assessment(assessment)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error analyzing suspicious behavior for {entity_id}: {e}")
            raise
    
    def _load_fraud_rules(self) -> List[Dict[str, Any]]:
        """Load fraud detection rules"""
        return [
            {
                'name': 'high_velocity_transactions',
                'description': 'Multiple transactions in short time',
                'condition': lambda tx, ctx: self._check_velocity_rule(tx, ctx),
                'severity': 'high'
            },
            {
                'name': 'geographic_mismatch',
                'description': 'Transaction from unexpected location',
                'condition': lambda tx, ctx: self._check_geographic_rule(tx, ctx),
                'severity': 'medium'
            },
            {
                'name': 'unusual_amount',
                'description': 'Transaction amount significantly different from normal',
                'condition': lambda tx, ctx: self._check_amount_rule(tx, ctx),
                'severity': 'medium'
            },
            {
                'name': 'new_payment_method',
                'description': 'New payment method used for large amount',
                'condition': lambda tx, ctx: self._check_payment_method_rule(tx, ctx),
                'severity': 'low'
            }
        ]
    
    def _load_geographic_risks(self) -> Dict[str, float]:
        """Load geographic risk scores"""
        return {
            'US': 0.1, 'CA': 0.1, 'UK': 0.1, 'DE': 0.1, 'FR': 0.1,
            'AU': 0.2, 'JP': 0.2, 'KR': 0.2, 'SG': 0.2,
            'IN': 0.4, 'BR': 0.4, 'MX': 0.4, 'RU': 0.6,
            'CN': 0.3, 'PH': 0.5, 'VN': 0.5, 'NG': 0.7,
            'UNKNOWN': 0.9
        }
    
    async def _extract_fraud_features(
        self,
        transaction: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Extract features for ML fraud detection"""
        features = {}
        
        # Transaction features
        features['amount'] = float(transaction.get('amount', 0))
        features['hour_of_day'] = datetime.now().hour
        features['day_of_week'] = datetime.now().weekday()
        
        # User behavior features
        features['account_age_days'] = user_context.get('account_age_days', 0)
        features['transaction_count_30d'] = user_context.get('recent_transaction_count', 0)
        features['avg_transaction_amount'] = user_context.get('avg_transaction_amount', 0)
        
        # Geographic features
        location = user_context.get('location', {})
        features['country_risk'] = self.geographic_risk_db.get(location.get('country', 'UNKNOWN'), 0.5)
        features['is_vpn'] = float(user_context.get('is_vpn', False))
        
        # Device features
        features['is_mobile'] = float('mobile' in user_context.get('user_agent', '').lower())
        features['new_device'] = float(user_context.get('is_new_device', False))
        
        # Payment features
        payment_method = transaction.get('payment_method', 'unknown')
        features['payment_method_risk'] = self._get_payment_method_risk(payment_method)
        
        return features
    
    async def _check_fraud_rules(
        self,
        transaction: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> List[str]:
        """Check transaction against fraud rules"""
        violations = []
        
        for rule in self.fraud_rules:
            try:
                if rule['condition'](transaction, user_context):
                    violations.append(rule['name'])
            except Exception as e:
                logger.warning(f"Error checking rule {rule['name']}: {e}")
        
        return violations
    
    def _check_velocity_rule(self, transaction: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """Check velocity fraud rule"""
        recent_count = user_context.get('recent_transaction_count', 0)
        return recent_count > 10  # More than 10 transactions in recent period
    
    def _check_geographic_rule(self, transaction: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """Check geographic anomaly rule"""
        user_country = user_context.get('usual_country', 'US')
        current_country = user_context.get('location', {}).get('country', 'UNKNOWN')
        return user_country != current_country
    
    def _check_amount_rule(self, transaction: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """Check unusual amount rule"""
        amount = float(transaction.get('amount', 0))
        avg_amount = user_context.get('avg_transaction_amount', 100)
        return amount > avg_amount * 5  # 5x normal amount
    
    def _check_payment_method_rule(self, transaction: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """Check new payment method rule"""
        is_new_method = user_context.get('is_new_payment_method', False)
        amount = float(transaction.get('amount', 0))
        return is_new_method and amount > 500
    
    async def _calculate_ml_fraud_score(self, features: Dict[str, float]) -> float:
        """Calculate ML-based fraud score"""
        try:
            # Prepare feature vector
            feature_vector = np.array(list(features.values())).reshape(1, -1)
            
            # Scale features
            scaled_features = self.scaler.transform(feature_vector)
            
            # Use isolation forest for anomaly detection
            if 'isolation_forest' not in self.ml_models:
                self.ml_models['isolation_forest'] = IsolationForest(contamination=0.1, random_state=42)
                # In production, this would be trained on historical data
                self.ml_models['isolation_forest'].fit(np.random.randn(1000, len(features)))
            
            # Get anomaly score
            anomaly_score = self.ml_models['isolation_forest'].decision_function(scaled_features)[0]
            
            # Convert to 0-1 score (higher = more fraudulent)
            fraud_score = max(0, min(1, (1 - anomaly_score) / 2))
            
            return fraud_score
            
        except Exception as e:
            logger.warning(f"Error calculating ML fraud score: {e}")
            return 0.5  # Default moderate risk
    
    async def _check_velocity_fraud(
        self,
        transaction: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> float:
        """Check for velocity-based fraud"""
        user_id = user_context.get('user_id')
        if not user_id:
            return 0.5
        
        # Get recent transaction velocity
        recent_count = user_context.get('transactions_last_hour', 0)
        recent_amount = user_context.get('amount_last_hour', 0)
        
        # Calculate velocity scores
        count_score = min(1.0, recent_count / 10)  # Normalize to max 10 transactions/hour
        amount_score = min(1.0, recent_amount / 10000)  # Normalize to max $10k/hour
        
        return max(count_score, amount_score)
    
    async def _assess_geographic_risk(
        self,
        transaction: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> float:
        """Assess geographic risk for transaction"""
        location = user_context.get('location', {})
        country = location.get('country', 'UNKNOWN')
        
        # Base country risk
        base_risk = self.geographic_risk_db.get(country, 0.5)
        
        # Check for geographic velocity (impossible travel)
        if user_context.get('impossible_travel', False):
            base_risk = min(1.0, base_risk + 0.4)
        
        # Check for VPN/proxy usage
        if user_context.get('is_vpn', False):
            base_risk = min(1.0, base_risk + 0.2)
        
        return base_risk
    
    async def _analyze_behavioral_patterns(
        self,
        transaction: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> float:
        """Analyze behavioral patterns for anomalies"""
        behavior_score = 0.0
        
        # Time-based patterns
        current_hour = datetime.now().hour
        usual_hours = user_context.get('usual_transaction_hours', [9, 10, 11, 12, 13, 14, 15, 16, 17])
        if current_hour not in usual_hours:
            behavior_score += 0.2
        
        # Amount patterns
        amount = float(transaction.get('amount', 0))
        usual_amount_range = user_context.get('usual_amount_range', [0, 1000])
        if amount < usual_amount_range[0] or amount > usual_amount_range[1]:
            behavior_score += 0.3
        
        # Device patterns
        if user_context.get('is_new_device', False):
            behavior_score += 0.2
        
        # Payment method patterns
        if user_context.get('is_new_payment_method', False):
            behavior_score += 0.2
        
        return min(1.0, behavior_score)
    
    async def _calculate_composite_risk_score(self, component_scores: Dict[str, float]) -> float:
        """Calculate composite risk score from components"""
        weights = {
            'ml_score': 0.3,
            'velocity_score': 0.2,
            'geo_risk': 0.2,
            'behavior_score': 0.2,
            'rule_violations': 0.1
        }
        
        weighted_score = 0.0
        for component, score in component_scores.items():
            if component == 'rule_violations':
                # Normalize rule violations (max 5 rules)
                normalized_score = min(1.0, score / 5)
            else:
                normalized_score = score
            
            weighted_score += weights.get(component, 0) * normalized_score
        
        return min(1.0, weighted_score)
    
    async def _classify_fraud_type(
        self,
        features: Dict[str, float],
        rule_violations: List[str]
    ) -> FraudType:
        """Classify the type of fraud detected"""
        if 'high_velocity_transactions' in rule_violations:
            return FraudType.VELOCITY_FRAUD
        elif 'geographic_mismatch' in rule_violations:
            return FraudType.GEOGRAPHIC_ANOMALY
        elif features.get('new_device', 0) > 0.5 and features.get('amount', 0) > 1000:
            return FraudType.ACCOUNT_TAKEOVER
        elif features.get('payment_method_risk', 0) > 0.7:
            return FraudType.CARD_FRAUD
        else:
            return FraudType.BEHAVIORAL_ANOMALY
    
    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify risk level based on score"""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _calculate_confidence_score(self, risk_score: float, features: Dict[str, float]) -> float:
        """Calculate confidence in fraud detection"""
        # Higher confidence for extreme scores and clear indicators
        base_confidence = abs(risk_score - 0.5) * 2  # 0.5 = maximum uncertainty
        
        # Boost confidence for clear indicators
        if features.get('is_vpn', 0) > 0.5:
            base_confidence = min(1.0, base_confidence + 0.2)
        
        if features.get('country_risk', 0) > 0.7:
            base_confidence = min(1.0, base_confidence + 0.1)
        
        return base_confidence
    
    async def _estimate_false_positive_probability(
        self,
        features: Dict[str, float],
        rule_violations: List[str]
    ) -> float:
        """Estimate probability of false positive"""
        # Start with base false positive rate
        base_fp_rate = 0.05  # 5% base false positive rate
        
        # Adjust based on risk factors
        if len(rule_violations) == 0:
            base_fp_rate += 0.2  # Higher FP if only ML detected
        
        if features.get('account_age_days', 0) > 365:
            base_fp_rate *= 0.5  # Lower FP for established accounts
        
        return min(0.5, base_fp_rate)
    
    async def _generate_fraud_recommendations(
        self,
        risk_level: RiskLevel,
        fraud_type: FraudType,
        rule_violations: List[str]
    ) -> List[str]:
        """Generate fraud prevention recommendations"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Block transaction immediately",
                "Freeze user account pending investigation",
                "Contact security team",
                "Initiate fraud investigation"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Require additional verification",
                "Manual review required",
                "Implement enhanced monitoring",
                "Consider temporary limits"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Enhanced verification recommended",
                "Monitor subsequent transactions",
                "Log for pattern analysis"
            ])
        
        # Fraud type specific recommendations
        if fraud_type == FraudType.VELOCITY_FRAUD:
            recommendations.append("Implement velocity limits")
        elif fraud_type == FraudType.GEOGRAPHIC_ANOMALY:
            recommendations.append("Verify location with user")
        elif fraud_type == FraudType.ACCOUNT_TAKEOVER:
            recommendations.append("Force password reset")
        
        return recommendations
    
    def _get_payment_method_risk(self, payment_method: str) -> float:
        """Get risk score for payment method"""
        risk_scores = {
            'credit_card': 0.3,
            'debit_card': 0.2,
            'bank_transfer': 0.1,
            'paypal': 0.2,
            'apple_pay': 0.1,
            'google_pay': 0.1,
            'cryptocurrency': 0.7,
            'prepaid_card': 0.6,
            'unknown': 0.9
        }
        return risk_scores.get(payment_method.lower(), 0.5)
    
    # Additional helper methods would continue here...
    
    async def _store_fraud_alert(self, alert: FraudAlert):
        """Store fraud alert in database"""
        # This would store in actual database
        logger.info(f"Storing fraud alert {alert.alert_id}")
    
    async def _send_real_time_alert(self, alert: FraudAlert):
        """Send real-time alert for critical fraud"""
        # This would send to monitoring systems
        logger.critical(f"CRITICAL FRAUD ALERT: {alert.alert_id} - {alert.fraud_type.value}")


class PatternDetector:
    """Fraud pattern detection engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pattern_cache = {}
        
    async def detect_emerging_patterns(
        self,
        fraud_alerts: List[FraudAlert],
        min_occurrences: int = 5
    ) -> List[FraudPattern]:
        """Detect emerging fraud patterns"""
        try:
            # Group alerts by similar characteristics
            pattern_groups = await self._cluster_fraud_alerts(fraud_alerts)
            
            patterns = []
            for group in pattern_groups:
                if len(group) >= min_occurrences:
                    pattern = await self._analyze_alert_cluster(group)
                    if pattern:
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting emerging patterns: {e}")
            raise
    
    async def _cluster_fraud_alerts(self, alerts: List[FraudAlert]) -> List[List[FraudAlert]]:
        """Cluster fraud alerts by similarity"""
        # Simple clustering by fraud type and geographic location
        clusters = defaultdict(list)
        
        for alert in alerts:
            cluster_key = (
                alert.fraud_type,
                alert.geographic_location.get('country', 'unknown'),
                alert.payment_method
            )
            clusters[cluster_key].append(alert)
        
        return list(clusters.values())
    
    async def _analyze_alert_cluster(self, alerts: List[FraudAlert]) -> Optional[FraudPattern]:
        """Analyze cluster of alerts to identify pattern"""
        if not alerts:
            return None
        
        # Calculate pattern metrics
        total_loss = sum(alert.amount or Decimal('0') for alert in alerts)
        avg_confidence = statistics.mean(alert.confidence_score for alert in alerts)
        
        # Get common characteristics
        common_rules = set(alerts[0].detection_rules)
        for alert in alerts[1:]:
            common_rules &= set(alert.detection_rules)
        
        pattern = FraudPattern(
            pattern_id=str(uuid.uuid4()),
            pattern_type=alerts[0].fraud_type,
            pattern_name=f"{alerts[0].fraud_type.value}_pattern_{datetime.now().strftime('%Y%m%d')}",
            description=f"Pattern detected in {len(alerts)} similar fraud cases",
            detection_rules=list(common_rules),
            affected_transactions=[alert.transaction_id for alert in alerts if alert.transaction_id],
            affected_users=[alert.user_id for alert in alerts if alert.user_id],
            total_loss_amount=total_loss,
            detection_rate=avg_confidence,
            false_positive_rate=statistics.mean(alert.false_positive_probability for alert in alerts),
            pattern_strength=min(1.0, len(alerts) / 20),  # Normalize to 20 max occurrences
            first_detected=min(alert.detected_at for alert in alerts),
            last_detected=max(alert.detected_at for alert in alerts),
            geographic_distribution=self._analyze_geographic_distribution(alerts),
            time_distribution=self._analyze_time_distribution(alerts),
            prevention_effectiveness=0.0  # Would be calculated based on prevented cases
        )
        
        return pattern
    
    def _analyze_geographic_distribution(self, alerts: List[FraudAlert]) -> Dict[str, int]:
        """Analyze geographic distribution of alerts"""
        geo_dist = defaultdict(int)
        for alert in alerts:
            country = alert.geographic_location.get('country', 'unknown')
            geo_dist[country] += 1
        return dict(geo_dist)
    
    def _analyze_time_distribution(self, alerts: List[FraudAlert]) -> Dict[str, int]:
        """Analyze time distribution of alerts"""
        time_dist = defaultdict(int)
        for alert in alerts:
            hour = alert.detected_at.hour
            time_dist[f"hour_{hour}"] += 1
        return dict(time_dist)


class RiskAssessor:
    """Risk assessment engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.risk_models = {}
        
    async def assess_entity_risk(
        self,
        entity_id: str,
        entity_type: str,
        context: Dict[str, Any]
    ) -> RiskAssessment:
        """Assess comprehensive risk for entity"""
        try:
            # Get entity data
            entity_data = await self._get_entity_data(entity_id, entity_type)
            
            # Calculate risk components
            risk_components = await self._calculate_risk_components(entity_data, context)
            
            # Generate risk assessment
            assessment = await self._generate_risk_assessment(
                entity_id, entity_type, entity_data, risk_components
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing entity risk for {entity_id}: {e}")
            raise
    
    async def _calculate_risk_components(
        self,
        entity_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate individual risk components"""
        components = {}
        
        # Account age risk (newer = higher risk)
        age_days = entity_data.get('account_age_days', 0)
        components['account_age_risk'] = max(0, 1 - (age_days / 365))
        
        # Verification risk
        verification = entity_data.get('verification_status', {})
        verification_score = sum(verification.values()) / len(verification) if verification else 0
        components['verification_risk'] = 1 - verification_score
        
        # Transaction behavior risk
        components['behavior_risk'] = await self._calculate_behavior_risk(entity_data)
        
        # Geographic risk
        components['geographic_risk'] = await self._calculate_geo_risk(entity_data, context)
        
        # Historical fraud risk
        fraud_history = entity_data.get('fraud_incidents', 0)
        components['fraud_history_risk'] = min(1.0, fraud_history / 10)
        
        return components
    
    async def _calculate_behavior_risk(self, entity_data: Dict[str, Any]) -> float:
        """Calculate behavioral risk score"""
        # This would analyze actual behavioral patterns
        return 0.3  # Sample behavior risk
    
    async def _calculate_geo_risk(self, entity_data: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate geographic risk score"""
        # This would analyze geographic patterns
        return 0.2  # Sample geo risk
    
    async def _get_entity_data(self, entity_id: str, entity_type: str) -> Dict[str, Any]:
        """Get entity data from database"""
        # This would query actual database
        return {
            'account_age_days': 180,
            'verification_status': {'email': True, 'phone': True, 'identity': False},
            'fraud_incidents': 0,
            'transaction_count': 50,
            'total_volume': 5000.0
        }
    
    async def _generate_risk_assessment(
        self,
        entity_id: str,
        entity_type: str,
        entity_data: Dict[str, Any],
        risk_components: Dict[str, float]
    ) -> RiskAssessment:
        """Generate comprehensive risk assessment"""
        # Calculate overall risk score
        overall_risk = statistics.mean(risk_components.values())
        risk_level = self._classify_risk_level(overall_risk)
        
        # Generate recommendations
        recommendations = await self._generate_risk_recommendations(risk_level, risk_components)
        
        return RiskAssessment(
            entity_id=entity_id,
            entity_type=entity_type,
            overall_risk_score=overall_risk,
            risk_level=risk_level,
            risk_factors=risk_components,
            behavioral_anomalies=[],  # Would be populated with actual anomalies
            transaction_patterns={},   # Would be populated with actual patterns
            account_age_days=entity_data.get('account_age_days', 0),
            verification_status=entity_data.get('verification_status', {}),
            previous_fraud_incidents=entity_data.get('fraud_incidents', 0),
            trust_score=1.0 - overall_risk,
            velocity_metrics={},
            geographic_risk=risk_components.get('geographic_risk', 0),
            device_risk=0.2,  # Sample device risk
            payment_method_risk=0.3,  # Sample payment method risk
            assessment_date=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
            recommendations=recommendations
        )
    
    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify risk level from score"""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _generate_risk_recommendations(
        self,
        risk_level: RiskLevel,
        risk_components: Dict[str, float]
    ) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if risk_components.get('verification_risk', 0) > 0.5:
            recommendations.append("Complete additional verification steps")
        
        if risk_components.get('account_age_risk', 0) > 0.7:
            recommendations.append("Implement graduated limits for new accounts")
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Enhanced monitoring required")
        
        return recommendations


class FraudDetectionAnalytics:
    """Main fraud detection analytics orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fraud_analyzer = FraudAnalyzer(config)
        self.pattern_detector = PatternDetector(config)
        self.risk_assessor = RiskAssessor(config)
        self.logger = logging.getLogger(__name__)
        
        # Performance metrics
        self.performance_metrics = {
            'analysis_times': deque(maxlen=1000),
            'fraud_detection_rate': 0.0,
            'false_positive_rate': 0.0,
            'total_analyses': 0,
            'confirmed_fraud_cases': 0,
            'false_positives': 0
        }
    
    async def initialize(self):
        """Initialize fraud detection system"""
        try:
            self.logger.info("Initializing Fraud Detection Analytics...")
            
            # Load ML models
            await self._load_ml_models()
            
            # Initialize databases
            await self._initialize_databases()
            
            # Start background tasks
            asyncio.create_task(self._pattern_monitoring_task())
            asyncio.create_task(self._model_performance_monitoring())
            
            self.logger.info("Fraud Detection Analytics initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Fraud Detection Analytics: {e}")
            raise
    
    async def analyze_transaction_fraud(
        self,
        transaction: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> FraudAlert:
        """Analyze transaction for fraud"""
        start_time = datetime.now()
        
        try:
            alert = await self.fraud_analyzer.analyze_transaction_fraud(transaction, user_context)
            
            # Update performance metrics
            analysis_time = (datetime.now() - start_time).total_seconds() * 1000
            self.performance_metrics['analysis_times'].append(analysis_time)
            self.performance_metrics['total_analyses'] += 1
            
            return alert
            
        except Exception as e:
            self.logger.error(f"Error analyzing transaction fraud: {e}")
            raise
    
    async def generate_fraud_reports(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive fraud analytics reports"""
        try:
            # Get fraud metrics
            fraud_metrics = await self._calculate_fraud_metrics(period_start, period_end)
            
            # Detect patterns
            patterns = await self.pattern_detector.detect_emerging_patterns(
                await self._get_fraud_alerts(period_start, period_end)
            )
            
            # Performance analysis
            performance = await self._analyze_detection_performance(period_start, period_end)
            
            # Trends analysis
            trends = await self._analyze_fraud_trends(period_start, period_end)
            
            return {
                'fraud_metrics': fraud_metrics,
                'detected_patterns': patterns,
                'detection_performance': performance,
                'fraud_trends': trends,
                'recommendations': await self._generate_system_recommendations(fraud_metrics),
                'report_generated_at': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating fraud reports: {e}")
            raise
    
    async def track_fraud_prevention_effectiveness(self) -> Dict[str, Any]:
        """Track fraud prevention effectiveness metrics"""
        try:
            metrics = self.performance_metrics.copy()
            
            # Calculate derived metrics
            if metrics['total_analyses'] > 0:
                metrics['fraud_detection_rate'] = (
                    metrics['confirmed_fraud_cases'] / metrics['total_analyses']
                )
                metrics['false_positive_rate'] = (
                    metrics['false_positives'] / metrics['total_analyses']
                )
            
            # Calculate precision and recall
            true_positives = metrics['confirmed_fraud_cases']
            false_positives = metrics['false_positives']
            
            if true_positives + false_positives > 0:
                precision = true_positives / (true_positives + false_positives)
            else:
                precision = 0.0
            
            # Recall would need false negatives from external validation
            recall = 0.85  # Sample recall rate
            
            f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            metrics.update({
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'avg_analysis_time_ms': statistics.mean(metrics['analysis_times']) if metrics['analysis_times'] else 0
            })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error tracking fraud prevention effectiveness: {e}")
            raise
    
    async def optimize_fraud_rules(self) -> Dict[str, Any]:
        """Optimize fraud detection rules based on performance"""
        try:
            # Analyze rule performance
            rule_performance = await self._analyze_rule_performance()
            
            # Identify optimization opportunities
            optimizations = await self._identify_rule_optimizations(rule_performance)
            
            # Generate recommendations
            recommendations = await self._generate_rule_recommendations(optimizations)
            
            return {
                'rule_performance': rule_performance,
                'optimization_opportunities': optimizations,
                'recommendations': recommendations,
                'expected_improvements': await self._estimate_improvement_impact(optimizations)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing fraud rules: {e}")
            raise
    
    async def monitor_fraud_trends(self) -> Dict[str, Any]:
        """Monitor fraud trends and emerging threats"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Get trend data
            daily_trends = await self._calculate_daily_fraud_trends(start_date, end_date)
            geographic_trends = await self._analyze_geographic_fraud_trends(start_date, end_date)
            payment_method_trends = await self._analyze_payment_method_trends(start_date, end_date)
            
            # Emerging threats
            emerging_threats = await self._identify_emerging_threats(start_date, end_date)
            
            return {
                'daily_trends': daily_trends,
                'geographic_trends': geographic_trends,
                'payment_method_trends': payment_method_trends,
                'emerging_threats': emerging_threats,
                'risk_assessment': await self._assess_overall_fraud_risk(),
                'monitoring_period': {'start': start_date, 'end': end_date}
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring fraud trends: {e}")
            raise
    
    # Helper methods
    async def _load_ml_models(self):
        """Load ML models for fraud detection"""
        # This would load actual trained models
        self.logger.info("Loading ML models for fraud detection")
    
    async def _initialize_databases(self):
        """Initialize database connections"""
        # This would initialize actual database connections
        self.logger.info("Initializing fraud detection databases")
    
    async def _pattern_monitoring_task(self):
        """Background task for pattern monitoring"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                # Monitor for new patterns
                patterns = await self.pattern_detector.detect_emerging_patterns(
                    await self._get_recent_fraud_alerts()
                )
                if patterns:
                    self.logger.info(f"Detected {len(patterns)} new fraud patterns")
            except Exception as e:
                self.logger.error(f"Error in pattern monitoring task: {e}")
    
    async def _model_performance_monitoring(self):
        """Background task for model performance monitoring"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                performance = await self.track_fraud_prevention_effectiveness()
                self.logger.info(f"Fraud detection performance: {performance}")
            except Exception as e:
                self.logger.error(f"Error in performance monitoring task: {e}")
    
    async def _calculate_fraud_metrics(self, start: datetime, end: datetime) -> FraudMetrics:
        """Calculate fraud metrics for period"""
        # This would calculate from actual data
        return FraudMetrics(
            period_start=start,
            period_end=end,
            total_transactions=10000,
            flagged_transactions=150,
            confirmed_fraud_cases=120,
            false_positive_cases=30,
            fraud_detection_rate=0.012,
            false_positive_rate=0.003,
            precision=0.80,
            recall=0.85,
            f1_score=0.825,
            total_fraud_amount=Decimal('25000.00'),
            prevented_fraud_amount=Decimal('22500.00'),
            fraud_rate_by_type={FraudType.CARD_FRAUD: 0.008, FraudType.VELOCITY_FRAUD: 0.004},
            fraud_rate_by_geography={'US': 0.010, 'Unknown': 0.025},
            fraud_rate_by_payment_method={'credit_card': 0.015, 'bank_transfer': 0.005},
            average_detection_time_seconds=0.085,
            model_performance={'accuracy': 0.92, 'auc': 0.89},
            cost_savings=Decimal('18000.00'),
            roi_fraud_prevention=3.2
        )
    
    async def _get_fraud_alerts(self, start: datetime, end: datetime) -> List[FraudAlert]:
        """Get fraud alerts for period"""
        # This would query actual database
        return []  # Sample empty list
    
    async def _get_recent_fraud_alerts(self) -> List[FraudAlert]:
        """Get recent fraud alerts"""
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=24)
        return await self._get_fraud_alerts(start_date, end_date)
    
    async def _analyze_detection_performance(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Analyze detection performance"""
        return {
            'detection_accuracy': 0.92,
            'response_time_avg_ms': 85,
            'false_positive_trend': 'decreasing',
            'model_drift_detected': False
        }
    
    async def _analyze_fraud_trends(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Analyze fraud trends"""
        return {
            'overall_trend': 'stable',
            'emerging_threats': ['synthetic_identity', 'account_takeover'],
            'geographic_hotspots': ['Unknown', 'High-risk countries'],
            'seasonal_patterns': 'holiday_increase'
        }
    
    async def _generate_system_recommendations(self, metrics: FraudMetrics) -> List[str]:
        """Generate system-level recommendations"""
        recommendations = []
        
        if metrics.false_positive_rate > 0.05:
            recommendations.append("Optimize ML models to reduce false positives")
        
        if metrics.fraud_detection_rate < 0.90:
            recommendations.append("Enhance detection rules for better coverage")
        
        return recommendations


# Export main classes
__all__ = [
    "FraudDetectionAnalytics",
    "FraudAnalyzer",
    "PatternDetector", 
    "RiskAssessor",
    "FraudAlert",
    "FraudPattern",
    "RiskAssessment",
    "FraudMetrics",
    "FraudType",
    "RiskLevel",
    "FraudStatus"
]
