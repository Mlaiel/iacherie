"""Fraud Detection Engine - Industrial ML-Based Security

Advanced fraud detection system using machine learning, behavioral analysis,
and real-time risk assessment for payment security.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
import math

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from .models import PaymentTransaction, FraudAnalysis
from .exceptions import FraudDetectedError
from .config import PaymentConfig

logger = logging.getLogger(__name__)


class FraudRiskLevel(str, Enum):
    """Fraud risk levels"""    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudIndicator(str, Enum):
    """Fraud detection indicators"""    VELOCITY_ANOMALY = "velocity_anomaly"
    AMOUNT_ANOMALY = "amount_anomaly"
    GEOGRAPHIC_RISK = "geographic_risk"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    DEVICE_FINGERPRINT = "device_fingerprint"
    TIME_PATTERN = "time_pattern"
    MERCHANT_RISK = "merchant_risk"
    CARD_RISK = "card_risk"
    ACCOUNT_AGE = "account_age"
    DUPLICATE_TRANSACTION = "duplicate_transaction"


@dataclass
class FraudRule:
    """Fraud detection rule configuration"""    name: str
    enabled: bool = True
    weight: float = 1.0
    threshold: float = 0.5
    conditions: Dict[str, Any] = field(default_factory=dict)
    action: str = "flag"  # flag, block, review
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskFeatures:
    """Risk assessment features"""    transaction_amount: float = 0.0
    account_age_days: int = 0
    transaction_velocity: float = 0.0
    avg_transaction_amount: float = 0.0
    transaction_hour: int = 0
    transaction_day_of_week: int = 0
    geographic_risk_score: float = 0.0
    device_risk_score: float = 0.0
    merchant_risk_score: float = 0.0
    time_since_last_transaction: float = 0.0
    transaction_count_24h: int = 0
    failed_attempts_24h: int = 0
    
    def to_array(self) -> np.ndarray:
        """Convert features to numpy array for ML model"""        return np.array([
            self.transaction_amount,
            self.account_age_days,
            self.transaction_velocity,
            self.avg_transaction_amount,
            self.transaction_hour,
            self.transaction_day_of_week,
            self.geographic_risk_score,
            self.device_risk_score,
            self.merchant_risk_score,
            self.time_since_last_transaction,
            self.transaction_count_24h,
            self.failed_attempts_24h
        ])


class FraudDetectionEngine:
    """    Industrial fraud detection engine with ML-based risk assessment.
    
    Combines rule-based detection, machine learning models, and behavioral
    analysis for comprehensive fraud prevention and risk scoring.
    """    def __init__(
        self,
        config: Optional[PaymentConfig] = None,
        db_session: Optional[Session] = None
    ):
        """Initialize fraud detection engine"""        self.config = config or PaymentConfig()
        self.db_session = db_session
        
        # ML Models (would be loaded from trained model files)
        self.anomaly_model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.models_trained = False
        
        # Fraud detection rules
        self.rules = self._initialize_fraud_rules()
        
        # Risk scoring weights
        self.risk_weights = {
            FraudIndicator.VELOCITY_ANOMALY: 0.25,
            FraudIndicator.AMOUNT_ANOMALY: 0.20,
            FraudIndicator.GEOGRAPHIC_RISK: 0.15,
            FraudIndicator.BEHAVIORAL_ANOMALY: 0.15,
            FraudIndicator.DEVICE_FINGERPRINT: 0.10,
            FraudIndicator.TIME_PATTERN: 0.05,
            FraudIndicator.ACCOUNT_AGE: 0.05,
            FraudIndicator.DUPLICATE_TRANSACTION: 0.05
        }
        
        # Blocklists and allowlists
        self.blocked_ips = set()
        self.blocked_cards = set()
        self.blocked_emails = set()
        self.trusted_merchants = set()
        
        # Geographic risk mappings
        self.country_risk_scores = {
            'US': 0.1, 'DE': 0.1, 'GB': 0.1, 'CA': 0.1, 'FR': 0.1,
            'CN': 0.3, 'RU': 0.4, 'NG': 0.6, 'PK': 0.5,
            'XX': 0.9  # Unknown/suspicious countries
        }

    def _initialize_fraud_rules(self) -> Dict[str, FraudRule]:
        """Initialize fraud detection rules"""        return {
            "velocity_check": FraudRule(
                name="Transaction Velocity Check",
                weight=0.3,
                threshold=10.0,  # Max 10 transactions per hour
                conditions={"time_window": 3600, "max_count": 10}
            ),
            "amount_anomaly": FraudRule(
                name="Amount Anomaly Detection",
                weight=0.25,
                threshold=5.0,  # 5x average amount
                conditions={"multiplier": 5.0}
            ),
            "duplicate_transaction": FraudRule(
                name="Duplicate Transaction Check",
                weight=0.4,
                threshold=0.9,  # 90% similarity
                conditions={"similarity_threshold": 0.9, "time_window": 300}
            ),
            "geographic_anomaly": FraudRule(
                name="Geographic Risk Check",
                weight=0.2,
                threshold=0.7,  # 70% risk score
                conditions={"risk_threshold": 0.7}
            ),
            "time_anomaly": FraudRule(
                name="Unusual Time Pattern",
                weight=0.15,
                threshold=0.8,
                conditions={"unusual_hours": [2, 3, 4, 5]}  # 2-5 AM
            ),
            "new_account_risk": FraudRule(
                name="New Account Risk",
                weight=0.2,
                threshold=7,  # Account younger than 7 days
                conditions={"min_age_days": 7, "max_transaction_amount": 500.0}
            )
        }

    async def analyze_transaction(self, transaction: PaymentTransaction) -> FraudAnalysis:
        """        Comprehensive fraud analysis for transaction.
        
        Args:
            transaction: Payment transaction to analyze
            
        Returns:
            FraudAnalysis with risk assessment
        """        try:
            logger.info(f"Starting fraud analysis for transaction {transaction.id}")
            
            # Extract risk features
            features = await self._extract_risk_features(transaction)
            
            # Rule-based detection
            rule_results = await self._apply_fraud_rules(transaction, features)
            
            # ML-based anomaly detection
            ml_score = await self._ml_anomaly_detection(features)
            
            # Behavioral analysis
            behavioral_score = await self._behavioral_analysis(transaction)
            
            # Device and network analysis
            device_score = await self._device_risk_analysis(transaction)
            
            # Calculate composite risk score
            risk_score = await self._calculate_composite_risk_score(
                rule_results, ml_score, behavioral_score, device_score
            )
            
            # Determine risk level and recommendation
            risk_level, recommendation = self._classify_risk(risk_score)
            
            # Generate risk factors list
            risk_factors = self._generate_risk_factors(
                rule_results, ml_score, behavioral_score, device_score
            )
            
            # Create fraud analysis result
            analysis = FraudAnalysis(
                transaction_id=str(transaction.id),
                risk_level=risk_score,
                risk_factors=risk_factors,
                recommendation=recommendation,
                confidence=self._calculate_confidence(rule_results, features),
                analysis_timestamp=datetime.utcnow(),
                metadata={
                    "rule_results": rule_results,
                    "ml_score": ml_score,
                    "behavioral_score": behavioral_score,
                    "device_score": device_score,
                    "features": features.__dict__,
                    "risk_classification": risk_level.value
                }
            )
            
            logger.info(
                f"Fraud analysis completed for {transaction.id}: "
                f"Risk={risk_score:.3f}, Level={risk_level.value}"
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Fraud analysis failed for transaction {transaction.id}: {str(e)}")
            # Return safe default analysis
            return FraudAnalysis(
                transaction_id=str(transaction.id),
                risk_level=0.5,
                risk_factors=["analysis_error"],
                recommendation="review",
                confidence=0.0,
                analysis_timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )

    async def analyze_revenue(
        self,
        creator_id: str,
        amount: Decimal,
        source: str,
        metadata: Dict[str, Any]
    ) -> float:
        """        Analyze revenue transaction for fraud indicators.
        
        Args:
            creator_id: Creator account identifier
            amount: Revenue amount
            source: Revenue source
            metadata: Transaction metadata
            
        Returns:
            Fraud risk score (0.0 to 1.0)
        """        try:
            risk_score = 0.0
            
            # Check revenue velocity (unusual volume)
            velocity_risk = await self._check_revenue_velocity(creator_id, amount)
            risk_score += velocity_risk * 0.3
            
            # Check source legitimacy
            source_risk = await self._check_revenue_source(source, metadata)
            risk_score += source_risk * 0.25
            
            # Check amount patterns
            amount_risk = await self._check_amount_patterns(creator_id, float(amount))
            risk_score += amount_risk * 0.2
            
            # Check creator behavior
            behavior_risk = await self._check_creator_behavior(creator_id)
            risk_score += behavior_risk * 0.15
            
            # Check time patterns
            time_risk = await self._check_time_patterns(creator_id)
            risk_score += time_risk * 0.1
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Revenue fraud analysis failed: {str(e)}")
            return 0.5  # Default moderate risk

    async def analyze_parameters(
        self,
        amount: Optional[Decimal] = None,
        user_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """        Analyze transaction parameters for fraud risk.
        
        Args:
            amount: Transaction amount
            user_id: User identifier
            payment_method: Payment method type
            metadata: Additional context data
            
        Returns:
            Dict with fraud analysis results
        """        try:
            metadata = metadata or {}
            risk_factors = []
            risk_score = 0.0
            
            # Amount analysis
            if amount:
                amount_float = float(amount)
                if amount_float > 10000:  # Large transaction
                    risk_factors.append("large_transaction_amount")
                    risk_score += 0.2
                elif amount_float < 1:  # Micro transaction
                    risk_factors.append("micro_transaction")
                    risk_score += 0.1
            
            # User analysis
            if user_id:
                user_risk = await self._analyze_user_risk(user_id)
                risk_score += user_risk * 0.3
                if user_risk > 0.5:
                    risk_factors.append("high_risk_user")
            
            # Payment method analysis
            if payment_method:
                method_risk = self._analyze_payment_method_risk(payment_method)
                risk_score += method_risk * 0.2
                if method_risk > 0.5:
                    risk_factors.append("high_risk_payment_method")
            
            # Metadata analysis
            metadata_risk = self._analyze_metadata_risk(metadata)
            risk_score += metadata_risk * 0.15
            
            # Device/IP analysis
            if "ip_address" in metadata:
                ip_risk = await self._analyze_ip_risk(metadata["ip_address"])
                risk_score += ip_risk * 0.15
                if ip_risk > 0.7:
                    risk_factors.append("high_risk_ip")
            
            risk_level = self._classify_risk(risk_score)[0]
            
            return {
                "risk_level": min(risk_score, 1.0),
                "risk_classification": risk_level.value,
                "risk_factors": risk_factors,
                "recommendation": "approve" if risk_score < 0.3 else "review" if risk_score < 0.7 else "block",
                "confidence": 0.8,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Parameter fraud analysis failed: {str(e)}")
            return {
                "risk_level": 0.5,
                "risk_classification": "medium",
                "risk_factors": ["analysis_error"],
                "recommendation": "review",
                "confidence": 0.0
            }

    async def update_fraud_model(self, training_data: List[Dict[str, Any]]):
        """        Update fraud detection model with new training data.
        
        Args:
            training_data: List of training examples with features and labels
        """        try:
            if len(training_data) < 100:  # Minimum training data required
                logger.warning("Insufficient training data for model update")
                return
            
            # Prepare training data
            features = []
            labels = []
            
            for example in training_data:
                feature_vector = example.get("features", [])
                is_fraud = example.get("is_fraud", False)
                
                if len(feature_vector) == 12:  # Expected feature count
                    features.append(feature_vector)
                    labels.append(1 if is_fraud else -1)  # IsolationForest uses -1 for anomalies
            
            if len(features) < 50:
                logger.warning("Insufficient valid training examples")
                return
            
            # Convert to numpy arrays
            X = np.array(features)
            
            # Fit scaler
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)
            
            # Train anomaly detection model
            self.anomaly_model.fit(X_scaled)
            self.models_trained = True
            
            logger.info(f"Fraud model updated with {len(features)} training examples")
            
        except Exception as e:
            logger.error(f"Model update failed: {str(e)}")

    # Private methods for fraud analysis
    async def _extract_risk_features(self, transaction: PaymentTransaction) -> RiskFeatures:
        """Extract risk features from transaction"""        features = RiskFeatures()
        
        # Basic transaction features
        features.transaction_amount = float(transaction.amount)
        features.transaction_hour = transaction.created_at.hour
        features.transaction_day_of_week = transaction.created_at.weekday()
        
        # Account-based features
        features.account_age_days = await self._get_account_age_days(transaction.creator_id)
        
        # Velocity features
        features.transaction_velocity = await self._calculate_transaction_velocity(transaction.creator_id)
        features.transaction_count_24h = await self._get_transaction_count_24h(transaction.creator_id)
        features.failed_attempts_24h = await self._get_failed_attempts_24h(transaction.creator_id)
        
        # Historical features
        features.avg_transaction_amount = await self._get_avg_transaction_amount(transaction.creator_id)
        features.time_since_last_transaction = await self._get_time_since_last_transaction(transaction.creator_id)
        
        # Risk scores
        features.geographic_risk_score = await self._calculate_geographic_risk(transaction)
        features.device_risk_score = await self._calculate_device_risk(transaction)
        features.merchant_risk_score = await self._calculate_merchant_risk(transaction)
        
        return features

    async def _apply_fraud_rules(
        self, 
        transaction: PaymentTransaction, 
        features: RiskFeatures
    ) -> Dict[str, Any]:
        """Apply rule-based fraud detection"""        results = {}
        
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
                
            try:
                if rule_name == "velocity_check":
                    triggered = features.transaction_count_24h > rule.threshold
                elif rule_name == "amount_anomaly":
                    triggered = (features.transaction_amount > 
                               features.avg_transaction_amount * rule.threshold)
                elif rule_name == "geographic_anomaly":
                    triggered = features.geographic_risk_score > rule.threshold
                elif rule_name == "time_anomaly":
                    triggered = features.transaction_hour in rule.conditions["unusual_hours"]
                elif rule_name == "new_account_risk":
                    triggered = (features.account_age_days < rule.threshold and 
                               features.transaction_amount > rule.conditions["max_transaction_amount"])
                elif rule_name == "duplicate_transaction":
                    triggered = await self._check_duplicate_transaction(transaction)
                else:
                    triggered = False
                
                results[rule_name] = {
                    "triggered": triggered,
                    "weight": rule.weight,
                    "score": rule.weight if triggered else 0.0
                }
                
            except Exception as e:
                logger.error(f"Rule {rule_name} execution failed: {str(e)}")
                results[rule_name] = {"triggered": False, "weight": 0.0, "score": 0.0}
        
        return results

    async def _ml_anomaly_detection(self, features: RiskFeatures) -> float:
        """Perform ML-based anomaly detection"""        if not self.models_trained:
            return 0.0
        
        try:
            # Convert features to array
            feature_array = features.to_array().reshape(1, -1)
            
            # Scale features
            feature_scaled = self.scaler.transform(feature_array)
            
            # Get anomaly score
            anomaly_score = self.anomaly_model.decision_function(feature_scaled)[0]
            
            # Convert to risk score (0-1)
            # IsolationForest returns negative scores for anomalies
            risk_score = max(0, (0.5 - anomaly_score) / 1.0)
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"ML anomaly detection failed: {str(e)}")
            return 0.0

    async def _behavioral_analysis(self, transaction: PaymentTransaction) -> float:
        """Analyze behavioral patterns"""        try:
            risk_score = 0.0
            
            # Check transaction patterns
            pattern_risk = await self._analyze_transaction_patterns(transaction.creator_id)
            risk_score += pattern_risk * 0.4
            
            # Check spending behavior
            spending_risk = await self._analyze_spending_behavior(transaction)
            risk_score += spending_risk * 0.3
            
            # Check timing patterns
            timing_risk = await self._analyze_timing_patterns(transaction)
            risk_score += timing_risk * 0.3
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Behavioral analysis failed: {str(e)}")
            return 0.0

    async def _device_risk_analysis(self, transaction: PaymentTransaction) -> float:
        """Analyze device and network risk factors"""        try:
            risk_score = 0.0
            
            # Check device fingerprint (would be passed in metadata)
            device_info = transaction.metadata.get("device_info", {})
            
            # New device risk
            if device_info.get("is_new_device"):
                risk_score += 0.3
            
            # Suspicious user agent
            user_agent = device_info.get("user_agent", "")
            if self._is_suspicious_user_agent(user_agent):
                risk_score += 0.2
            
            # VPN/Proxy detection
            if device_info.get("is_vpn") or device_info.get("is_proxy"):
                risk_score += 0.4
            
            # IP reputation
            ip_address = device_info.get("ip_address")
            if ip_address:
                ip_risk = await self._analyze_ip_risk(ip_address)
                risk_score += ip_risk * 0.3
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Device risk analysis failed: {str(e)}")
            return 0.0

    async def _calculate_composite_risk_score(
        self,
        rule_results: Dict[str, Any],
        ml_score: float,
        behavioral_score: float,
        device_score: float
    ) -> float:
        """Calculate composite risk score from all indicators"""        
        # Rule-based score
        rule_score = sum(result["score"] for result in rule_results.values()) / len(rule_results)
        
        # Weighted composite score
        composite_score = (
            rule_score * 0.4 +
            ml_score * 0.3 +
            behavioral_score * 0.2 +
            device_score * 0.1
        )
        
        return min(composite_score, 1.0)

    def _classify_risk(self, risk_score: float) -> Tuple[FraudRiskLevel, str]:
        """Classify risk score into risk level and recommendation"""        if risk_score < 0.2:
            return FraudRiskLevel.VERY_LOW, "approve"
        elif risk_score < 0.4:
            return FraudRiskLevel.LOW, "approve"
        elif risk_score < 0.6:
            return FraudRiskLevel.MEDIUM, "review"
        elif risk_score < 0.8:
            return FraudRiskLevel.HIGH, "review"
        else:
            return FraudRiskLevel.CRITICAL, "block"

    def _generate_risk_factors(
        self,
        rule_results: Dict[str, Any],
        ml_score: float,
        behavioral_score: float,
        device_score: float
    ) -> List[str]:
        """Generate list of risk factors"""        factors = []
        
        # Add triggered rules
        for rule_name, result in rule_results.items():
            if result["triggered"]:
                factors.append(rule_name)
        
        # Add ML indicators
        if ml_score > 0.5:
            factors.append("ml_anomaly_detected")
        
        # Add behavioral indicators
        if behavioral_score > 0.5:
            factors.append("behavioral_anomaly")
        
        # Add device indicators
        if device_score > 0.5:
            factors.append("device_risk")
        
        return factors

    def _calculate_confidence(
        self, 
        rule_results: Dict[str, Any], 
        features: RiskFeatures
    ) -> float:
        """Calculate confidence in fraud analysis"""        # Base confidence based on data quality
        confidence = 0.7
        
        # Increase confidence if multiple rules trigger
        triggered_rules = sum(1 for result in rule_results.values() if result["triggered"])
        if triggered_rules > 2:
            confidence += 0.2
        
        # Decrease confidence for new accounts (less historical data)
        if features.account_age_days < 30:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))

    # Helper methods (simplified implementations)
    async def _get_account_age_days(self, creator_id: str) -> int:
        """Get account age in days"""        return 180  # Mock value

    async def _calculate_transaction_velocity(self, creator_id: str) -> float:
        """Calculate transaction velocity"""        return 2.5  # Mock value

    async def _get_transaction_count_24h(self, creator_id: str) -> int:
        """Get transaction count in last 24 hours"""        return 3  # Mock value

    async def _get_failed_attempts_24h(self, creator_id: str) -> int:
        """Get failed transaction attempts in last 24 hours"""        return 0  # Mock value

    async def _get_avg_transaction_amount(self, creator_id: str) -> float:
        """Get average transaction amount"""        return 125.0  # Mock value

    async def _get_time_since_last_transaction(self, creator_id: str) -> float:
        """Get time since last transaction in hours"""        return 8.5  # Mock value

    async def _calculate_geographic_risk(self, transaction: PaymentTransaction) -> float:
        """Calculate geographic risk score"""        country = transaction.metadata.get("country", "XX")
        return self.country_risk_scores.get(country, 0.5)

    async def _calculate_device_risk(self, transaction: PaymentTransaction) -> float:
        """Calculate device risk score"""        return 0.1  # Mock value

    async def _calculate_merchant_risk(self, transaction: PaymentTransaction) -> float:
        """Calculate merchant/platform risk score"""        return 0.05  # Mock value

    async def _check_duplicate_transaction(self, transaction: PaymentTransaction) -> bool:
        """Check for duplicate transactions"""        return False  # Mock implementation

    async def _check_revenue_velocity(self, creator_id: str, amount: Decimal) -> float:
        """Check revenue velocity anomalies"""        return 0.1  # Mock value

    async def _check_revenue_source(self, source: str, metadata: Dict[str, Any]) -> float:
        """Check revenue source legitimacy"""        suspicious_sources = {'unknown', 'suspicious', 'blocked'}
        return 0.8 if source.lower() in suspicious_sources else 0.1

    async def _check_amount_patterns(self, creator_id: str, amount: float) -> float:
        """Check amount patterns for anomalies"""        return 0.05  # Mock value

    async def _check_creator_behavior(self, creator_id: str) -> float:
        """Check creator behavioral patterns"""        return 0.1  # Mock value

    async def _check_time_patterns(self, creator_id: str) -> float:
        """Check time-based patterns"""        return 0.05  # Mock value

    async def _analyze_user_risk(self, user_id: str) -> float:
        """Analyze user-specific risk factors"""        return 0.1  # Mock value

    def _analyze_payment_method_risk(self, payment_method: str) -> float:
        """Analyze payment method risk"""        high_risk_methods = {'crypto', 'gift_card', 'prepaid'}
        return 0.6 if payment_method.lower() in high_risk_methods else 0.1

    def _analyze_metadata_risk(self, metadata: Dict[str, Any]) -> float:
        """Analyze transaction metadata for risk indicators"""        return 0.05  # Mock value

    async def _analyze_ip_risk(self, ip_address: str) -> float:
        """Analyze IP address risk"""        if ip_address in self.blocked_ips:
            return 1.0
        return 0.1  # Mock value

    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""        suspicious_patterns = ['bot', 'crawler', 'script', 'automated']
        return any(pattern in user_agent.lower() for pattern in suspicious_patterns)

    async def _analyze_transaction_patterns(self, creator_id: str) -> float:
        """Analyze transaction patterns"""        return 0.1  # Mock value

    async def _analyze_spending_behavior(self, transaction: PaymentTransaction) -> float:
        """Analyze spending behavior"""        return 0.05  # Mock value

    async def _analyze_timing_patterns(self, transaction: PaymentTransaction) -> float:
        """Analyze timing patterns"""        # Check if transaction is at unusual time
        hour = transaction.created_at.hour
        if 2 <= hour <= 5:  # 2-5 AM is unusual
            return 0.3
        return 0.0
