"""🔒 Fraud Detection Engine
==========================

Advanced fraud detection engine using machine learning, behavioral analysis,
and real-time transaction monitoring to prevent fraudulent activities.

Features:
- Real-time transaction analysis
- Machine learning fraud models
- Risk scoring algorithms
- Behavioral pattern recognition
- Velocity checking
- Geographic anomaly detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import statistics
import hashlib
from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import geoip2.database
import geoip2.errors

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudIndicator(Enum):
    """Types of fraud indicators"""
    VELOCITY_ANOMALY = "velocity_anomaly"
    AMOUNT_ANOMALY = "amount_anomaly"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    DEVICE_ANOMALY = "device_anomaly"
    PATTERN_ANOMALY = "pattern_anomaly"
    BLACKLIST_MATCH = "blacklist_match"
    SUSPICIOUS_TIMING = "suspicious_timing"


class ActionType(Enum):
    """Actions to take based on fraud assessment"""
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"
    CHALLENGE = "challenge"  # Additional verification
    STEP_UP_AUTH = "step_up_auth"  # Require stronger authentication


@dataclass
class TransactionFeatures:
    """Features extracted from transaction for ML analysis"""
    amount: float
    currency: str
    hour_of_day: int
    day_of_week: int
    merchant_category: str
    payment_method: str
    
    # User behavioral features
    user_transaction_count_24h: int
    user_transaction_count_7d: int
    user_avg_transaction_amount: float
    user_velocity_score: float
    
    # Geographic features
    country_code: str
    city: str
    distance_from_last_transaction: float
    new_location: bool
    
    # Device features
    device_fingerprint: str
    new_device: bool
    user_agent_hash: str
    
    # Timing features
    time_since_last_transaction: float
    unusual_timing: bool


@dataclass
class FraudAssessment:
    """Result of fraud detection analysis"""
    transaction_id: str
    risk_level: RiskLevel
    risk_score: float  # 0-1, higher = more risky
    confidence: float  # 0-1, higher = more confident in assessment
    indicators: List[FraudIndicator]
    recommended_action: ActionType
    explanation: str
    
    # Detailed scores
    ml_anomaly_score: float
    velocity_score: float
    geographic_score: float
    behavioral_score: float
    
    # Processing info
    processing_time: float
    model_version: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UserProfile:
    """User behavioral profile for fraud detection"""
    user_id: str
    transaction_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    location_history: deque = field(default_factory=lambda: deque(maxlen=100))
    device_history: deque = field(default_factory=lambda: deque(maxlen=50))
    
    # Behavioral metrics
    avg_transaction_amount: float = 0.0
    typical_hours: List[int] = field(default_factory=list)
    typical_countries: List[str] = field(default_factory=list)
    typical_merchants: List[str] = field(default_factory=list)
    
    # Risk metrics
    historical_risk_score: float = 0.0
    false_positive_rate: float = 0.0
    
    last_updated: datetime = field(default_factory=datetime.now)


class FraudDetectionEngine:
    """
    Advanced fraud detection engine using machine learning and behavioral
    analysis to detect and prevent fraudulent payment transactions.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize fraud detection engine"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # ML Models
        self.anomaly_model = None
        self.classification_model = None
        self.scaler = StandardScaler()
        self.model_version = "1.0.0"
        
        # User profiles
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Blacklists and whitelists
        self.blacklisted_cards = set()
        self.blacklisted_ips = set()
        self.blacklisted_emails = set()
        self.whitelisted_users = set()
        
        # Velocity tracking
        self.velocity_trackers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Geographic database
        self.geoip_reader = None
        
        # Real-time statistics
        self.fraud_stats = {
            'total_transactions': 0,
            'flagged_transactions': 0,
            'blocked_transactions': 0,
            'false_positives': 0,
            'confirmed_fraud': 0
        }
        
        # Feature engineering pipeline
        self.feature_extractors = []
        
        # Model performance tracking
        self.model_performance = {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'last_evaluation': None
        }
    
    async def initialize(self) -> None:
        """Initialize the fraud detection engine"""
        try:
            # Load ML models
            await self._load_models()
            
            # Load blacklists
            await self._load_blacklists()
            
            # Initialize GeoIP database
            await self._initialize_geoip()
            
            # Load user profiles
            await self._load_user_profiles()
            
            self.logger.info("Fraud detection engine initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize fraud detection engine: {e}")
            raise
    
    async def assess_transaction(self, transaction_data: Dict[str, Any]) -> FraudAssessment:
        """
        Assess a transaction for fraud risk
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            transaction_id = transaction_data.get('transaction_id')
            user_id = transaction_data.get('user_id')
            
            # Extract features
            features = await self._extract_features(transaction_data)
            
            # Get user profile
            user_profile = await self._get_or_create_user_profile(user_id)
            
            # Perform various fraud checks
            ml_score = await self._ml_anomaly_detection(features)
            velocity_score = await self._velocity_check(user_id, transaction_data)
            geographic_score = await self._geographic_analysis(user_id, transaction_data)
            behavioral_score = await self._behavioral_analysis(user_profile, features)
            
            # Check blacklists
            blacklist_indicators = await self._check_blacklists(transaction_data)
            
            # Calculate overall risk score
            risk_score, indicators = await self._calculate_risk_score(
                ml_score, velocity_score, geographic_score, behavioral_score, blacklist_indicators
            )
            
            # Determine risk level and recommended action
            risk_level = await self._determine_risk_level(risk_score)
            recommended_action = await self._determine_action(risk_level, indicators, user_profile)
            
            # Generate explanation
            explanation = await self._generate_explanation(indicators, risk_score)
            
            # Calculate confidence
            confidence = await self._calculate_confidence(features, risk_score)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            assessment = FraudAssessment(
                transaction_id=transaction_id,
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=confidence,
                indicators=indicators,
                recommended_action=recommended_action,
                explanation=explanation,
                ml_anomaly_score=ml_score,
                velocity_score=velocity_score,
                geographic_score=geographic_score,
                behavioral_score=behavioral_score,
                processing_time=processing_time,
                model_version=self.model_version
            )
            
            # Update user profile
            await self._update_user_profile(user_profile, features, assessment)
            
            # Update statistics
            await self._update_statistics(assessment)
            
            self.logger.info(f"Fraud assessment complete: {transaction_id} - {risk_level.value} risk")
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Fraud assessment failed for transaction {transaction_id}: {e}")
            # Return safe assessment in case of error
            return FraudAssessment(
                transaction_id=transaction_id,
                risk_level=RiskLevel.MEDIUM,
                risk_score=0.5,
                confidence=0.0,
                indicators=[],
                recommended_action=ActionType.REVIEW,
                explanation="Assessment failed - manual review required",
                ml_anomaly_score=0.5,
                velocity_score=0.5,
                geographic_score=0.5,
                behavioral_score=0.5,
                processing_time=0.0,
                model_version=self.model_version
            )
    
    async def _extract_features(self, transaction_data: Dict[str, Any]) -> TransactionFeatures:
        """Extract features from transaction data for ML analysis"""
        user_id = transaction_data.get('user_id')
        amount = float(transaction_data.get('amount', 0))
        timestamp = datetime.fromisoformat(transaction_data.get('timestamp', datetime.now().isoformat()))
        
        # Basic transaction features
        features = TransactionFeatures(
            amount=amount,
            currency=transaction_data.get('currency', 'USD'),
            hour_of_day=timestamp.hour,
            day_of_week=timestamp.weekday(),
            merchant_category=transaction_data.get('merchant_category', 'unknown'),
            payment_method=transaction_data.get('payment_method', 'card'),
            
            # User behavioral features (will be calculated)
            user_transaction_count_24h=0,
            user_transaction_count_7d=0,
            user_avg_transaction_amount=0.0,
            user_velocity_score=0.0,
            
            # Geographic features
            country_code=transaction_data.get('country_code', 'US'),
            city=transaction_data.get('city', 'Unknown'),
            distance_from_last_transaction=0.0,
            new_location=False,
            
            # Device features
            device_fingerprint=transaction_data.get('device_fingerprint', ''),
            new_device=False,
            user_agent_hash=hashlib.md5(transaction_data.get('user_agent', '').encode()).hexdigest(),
            
            # Timing features
            time_since_last_transaction=0.0,
            unusual_timing=False
        )
        
        # Calculate user-specific features
        user_profile = self.user_profiles.get(user_id)
        if user_profile:
            # Calculate transaction counts
            now = datetime.now()
            features.user_transaction_count_24h = len([
                t for t in user_profile.transaction_history
                if now - t['timestamp'] <= timedelta(hours=24)
            ])
            features.user_transaction_count_7d = len([
                t for t in user_profile.transaction_history
                if now - t['timestamp'] <= timedelta(days=7)
            ])
            
            # Calculate average transaction amount
            if user_profile.transaction_history:
                amounts = [t['amount'] for t in user_profile.transaction_history]
                features.user_avg_transaction_amount = statistics.mean(amounts)
            
            # Check for new location
            recent_locations = [l['country_code'] for l in user_profile.location_history[-10:]]
            features.new_location = features.country_code not in recent_locations
            
            # Check for new device
            recent_devices = [d['fingerprint'] for d in user_profile.device_history[-5:]]
            features.new_device = features.device_fingerprint not in recent_devices
            
            # Calculate time since last transaction
            if user_profile.transaction_history:
                last_transaction = user_profile.transaction_history[-1]
                time_diff = timestamp - last_transaction['timestamp']
                features.time_since_last_transaction = time_diff.total_seconds()
            
            # Check for unusual timing
            typical_hours = user_profile.typical_hours
            if typical_hours and features.hour_of_day not in typical_hours:
                features.unusual_timing = True
        
        return features
    
    async def _ml_anomaly_detection(self, features: TransactionFeatures) -> float:
        """Use ML models to detect anomalies"""
        try:
            if not self.anomaly_model:
                return 0.5  # Neutral score if no model
            
            # Convert features to numpy array
            feature_vector = self._features_to_vector(features)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            # Get anomaly score (lower = more anomalous)
            anomaly_score = self.anomaly_model.decision_function(feature_vector_scaled)[0]
            
            # Convert to 0-1 range (higher = more anomalous)
            normalized_score = max(0, min(1, (anomaly_score + 1) / 2))
            
            return 1 - normalized_score  # Invert so higher = more risky
            
        except Exception as e:
            self.logger.error(f"ML anomaly detection failed: {e}")
            return 0.5
    
    async def _velocity_check(self, user_id: str, transaction_data: Dict[str, Any]) -> float:
        """Check transaction velocity for suspicious patterns"""
        try:
            amount = float(transaction_data.get('amount', 0))
            now = datetime.now()
            
            # Track velocity by different keys
            velocity_keys = [
                f"user:{user_id}",
                f"card:{transaction_data.get('card_hash', '')}",
                f"ip:{transaction_data.get('ip_address', '')}",
                f"merchant:{transaction_data.get('merchant_id', '')}"
            ]
            
            risk_score = 0.0
            
            for key in velocity_keys:
                if not key.split(':')[1]:  # Skip empty keys
                    continue
                
                velocity_history = self.velocity_trackers[key]
                
                # Count transactions in different time windows
                count_1h = len([t for t in velocity_history if now - t['timestamp'] <= timedelta(hours=1)])
                count_24h = len([t for t in velocity_history if now - t['timestamp'] <= timedelta(hours=24)])
                
                # Calculate amount velocity
                amount_1h = sum([t['amount'] for t in velocity_history 
                               if now - t['timestamp'] <= timedelta(hours=1)])
                amount_24h = sum([t['amount'] for t in velocity_history 
                                if now - t['timestamp'] <= timedelta(hours=24)])
                
                # Define velocity thresholds
                thresholds = {
                    'transactions_1h': 10,
                    'transactions_24h': 50,
                    'amount_1h': 10000,
                    'amount_24h': 100000
                }
                
                # Calculate velocity risk
                velocity_risk = 0.0
                if count_1h > thresholds['transactions_1h']:
                    velocity_risk += 0.3
                if count_24h > thresholds['transactions_24h']:
                    velocity_risk += 0.2
                if amount_1h > thresholds['amount_1h']:
                    velocity_risk += 0.3
                if amount_24h > thresholds['amount_24h']:
                    velocity_risk += 0.2
                
                risk_score = max(risk_score, velocity_risk)
                
                # Record this transaction
                velocity_history.append({
                    'timestamp': now,
                    'amount': amount
                })
            
            return min(1.0, risk_score)
            
        except Exception as e:
            self.logger.error(f"Velocity check failed: {e}")
            return 0.0
    
    async def _geographic_analysis(self, user_id: str, transaction_data: Dict[str, Any]) -> float:
        """Analyze geographic patterns for anomalies"""
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile or not user_profile.location_history:
                return 0.0  # No history to compare
            
            current_country = transaction_data.get('country_code', 'US')
            current_city = transaction_data.get('city', 'Unknown')
            ip_address = transaction_data.get('ip_address', '')
            
            # Check against typical countries
            typical_countries = user_profile.typical_countries
            if typical_countries and current_country not in typical_countries:
                # New country - higher risk
                risk_score = 0.5
                
                # Check if it's a high-risk country (simplified list)
                high_risk_countries = ['CN', 'RU', 'NG', 'PK', 'BD']
                if current_country in high_risk_countries:
                    risk_score += 0.3
                
                return min(1.0, risk_score)
            
            # Check for rapid geographic changes
            if user_profile.location_history:
                last_location = user_profile.location_history[-1]
                last_country = last_location.get('country_code')
                last_timestamp = last_location.get('timestamp', datetime.now())
                
                time_diff = datetime.now() - last_timestamp
                
                # If different country within short time, higher risk
                if (current_country != last_country and 
                    time_diff < timedelta(hours=4)):  # 4 hours travel time
                    return 0.7
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Geographic analysis failed: {e}")
            return 0.0
    
    async def _behavioral_analysis(self, user_profile: UserProfile, 
                                 features: TransactionFeatures) -> float:
        """Analyze behavioral patterns for anomalies"""
        try:
            if not user_profile.transaction_history:
                return 0.0  # No behavioral data
            
            risk_score = 0.0
            
            # Amount anomaly detection
            if user_profile.avg_transaction_amount > 0:
                amount_ratio = features.amount / user_profile.avg_transaction_amount
                if amount_ratio > 10:  # 10x normal amount
                    risk_score += 0.4
                elif amount_ratio > 5:  # 5x normal amount
                    risk_score += 0.2
            
            # Timing anomaly
            if features.unusual_timing:
                risk_score += 0.2
            
            # Payment method anomaly
            historical_methods = [t.get('payment_method', 'card') 
                                for t in user_profile.transaction_history]
            if historical_methods and features.payment_method not in historical_methods:
                risk_score += 0.1
            
            # Merchant category anomaly
            historical_categories = [t.get('merchant_category', 'unknown') 
                                   for t in user_profile.transaction_history]
            if (historical_categories and 
                features.merchant_category not in historical_categories):
                risk_score += 0.1
            
            return min(1.0, risk_score)
            
        except Exception as e:
            self.logger.error(f"Behavioral analysis failed: {e}")
            return 0.0
    
    async def _check_blacklists(self, transaction_data: Dict[str, Any]) -> List[FraudIndicator]:
        """Check transaction against blacklists"""
        indicators = []
        
        # Check card blacklist
        card_hash = transaction_data.get('card_hash', '')
        if card_hash in self.blacklisted_cards:
            indicators.append(FraudIndicator.BLACKLIST_MATCH)
        
        # Check IP blacklist
        ip_address = transaction_data.get('ip_address', '')
        if ip_address in self.blacklisted_ips:
            indicators.append(FraudIndicator.BLACKLIST_MATCH)
        
        # Check email blacklist
        email = transaction_data.get('email', '')
        if email in self.blacklisted_emails:
            indicators.append(FraudIndicator.BLACKLIST_MATCH)
        
        return indicators
    
    async def _calculate_risk_score(self, ml_score: float, velocity_score: float,
                                  geographic_score: float, behavioral_score: float,
                                  blacklist_indicators: List[FraudIndicator]) -> Tuple[float, List[FraudIndicator]]:
        """Calculate overall risk score and identify indicators"""
        indicators = blacklist_indicators.copy()
        
        # Weighted combination of scores
        weights = {
            'ml': 0.3,
            'velocity': 0.25,
            'geographic': 0.25,
            'behavioral': 0.2
        }
        
        base_score = (
            ml_score * weights['ml'] +
            velocity_score * weights['velocity'] +
            geographic_score * weights['geographic'] +
            behavioral_score * weights['behavioral']
        )
        
        # Add indicators based on individual scores
        if ml_score > 0.7:
            indicators.append(FraudIndicator.PATTERN_ANOMALY)
        if velocity_score > 0.6:
            indicators.append(FraudIndicator.VELOCITY_ANOMALY)
        if geographic_score > 0.5:
            indicators.append(FraudIndicator.GEOGRAPHIC_ANOMALY)
        if behavioral_score > 0.5:
            indicators.append(FraudIndicator.BEHAVIORAL_ANOMALY)
        
        # Boost score if blacklisted
        if blacklist_indicators:
            base_score = min(1.0, base_score + 0.5)
        
        return base_score, indicators
    
    async def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score"""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _determine_action(self, risk_level: RiskLevel, 
                              indicators: List[FraudIndicator],
                              user_profile: UserProfile) -> ActionType:
        """Determine recommended action based on risk assessment"""
        # Check whitelist first
        if user_profile.user_id in self.whitelisted_users:
            if risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
                return ActionType.ALLOW
        
        # Check for blacklist matches
        if FraudIndicator.BLACKLIST_MATCH in indicators:
            return ActionType.BLOCK
        
        # Risk-based actions
        if risk_level == RiskLevel.CRITICAL:
            return ActionType.BLOCK
        elif risk_level == RiskLevel.HIGH:
            return ActionType.CHALLENGE
        elif risk_level == RiskLevel.MEDIUM:
            return ActionType.REVIEW
        else:
            return ActionType.ALLOW
    
    async def _generate_explanation(self, indicators: List[FraudIndicator], 
                                  risk_score: float) -> str:
        """Generate human-readable explanation for the assessment"""
        if not indicators:
            return f"Low risk transaction (score: {risk_score:.2f})"
        
        explanations = {
            FraudIndicator.VELOCITY_ANOMALY: "unusual transaction frequency",
            FraudIndicator.AMOUNT_ANOMALY: "unusual transaction amount",
            FraudIndicator.GEOGRAPHIC_ANOMALY: "unusual location",
            FraudIndicator.BEHAVIORAL_ANOMALY: "unusual behavior pattern",
            FraudIndicator.DEVICE_ANOMALY: "new or suspicious device",
            FraudIndicator.PATTERN_ANOMALY: "suspicious transaction pattern",
            FraudIndicator.BLACKLIST_MATCH: "blacklisted entity",
            FraudIndicator.SUSPICIOUS_TIMING: "unusual timing"
        }
        
        reasons = [explanations.get(indicator, str(indicator)) for indicator in indicators]
        return f"Risk factors detected: {', '.join(reasons)} (score: {risk_score:.2f})"
    
    async def _calculate_confidence(self, features: TransactionFeatures, 
                                  risk_score: float) -> float:
        """Calculate confidence in the assessment"""
        # Higher confidence for users with more transaction history
        confidence = 0.5
        
        if features.user_transaction_count_7d > 10:
            confidence += 0.2
        if features.user_transaction_count_7d > 50:
            confidence += 0.1
        
        # Higher confidence for extreme scores
        if risk_score > 0.8 or risk_score < 0.2:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    async def _get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile for behavioral analysis"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        return self.user_profiles[user_id]
    
    async def _update_user_profile(self, user_profile -> None: UserProfile, 
                                 features -> None: TransactionFeatures,
                                 assessment -> None: FraudAssessment) -> None:
        """Update user profile with new transaction data"""
        # Add transaction to history
        transaction_record = {
            'timestamp': datetime.now(),
            'amount': features.amount,
            'currency': features.currency,
            'merchant_category': features.merchant_category,
            'payment_method': features.payment_method,
            'risk_score': assessment.risk_score
        }
        user_profile.transaction_history.append(transaction_record)
        
        # Add location to history
        location_record = {
            'timestamp': datetime.now(),
            'country_code': features.country_code,
            'city': features.city
        }
        user_profile.location_history.append(location_record)
        
        # Add device to history
        device_record = {
            'timestamp': datetime.now(),
            'fingerprint': features.device_fingerprint,
            'user_agent_hash': features.user_agent_hash
        }
        user_profile.device_history.append(device_record)
        
        # Update behavioral metrics
        if user_profile.transaction_history:
            amounts = [t['amount'] for t in user_profile.transaction_history]
            user_profile.avg_transaction_amount = statistics.mean(amounts)
            
            hours = [t['timestamp'].hour for t in user_profile.transaction_history]
            user_profile.typical_hours = list(set(hours))
            
            countries = [l['country_code'] for l in user_profile.location_history]
            user_profile.typical_countries = list(set(countries))
        
        user_profile.last_updated = datetime.now()
    
    async def _update_statistics(self, assessment -> None: FraudAssessment) -> None:
        """Update fraud detection statistics"""
        self.fraud_stats['total_transactions'] += 1
        
        if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.fraud_stats['flagged_transactions'] += 1
        
        if assessment.recommended_action == ActionType.BLOCK:
            self.fraud_stats['blocked_transactions'] += 1
    
    def _features_to_vector(self, features: TransactionFeatures) -> np.ndarray:
        """Convert features to numpy vector for ML models"""
        # This is a simplified feature vector
        # In practice, this would include proper feature engineering
        return np.array([
            features.amount,
            features.hour_of_day,
            features.day_of_week,
            features.user_transaction_count_24h,
            features.user_transaction_count_7d,
            features.user_avg_transaction_amount,
            features.distance_from_last_transaction,
            1 if features.new_location else 0,
            1 if features.new_device else 0,
            features.time_since_last_transaction,
            1 if features.unusual_timing else 0
        ])
    
    async def _load_models(self) -> None:
        """Load pre-trained ML models"""
        try:
            # In practice, these would be loaded from files
            # For now, creating simple models
            self.anomaly_model = IsolationForest(contamination=0.1, random_state=42)
            self.classification_model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Initialize with dummy data for demo
            dummy_data = np.random.rand(100, 11)  # 11 features
            self.anomaly_model.fit(dummy_data)
            self.scaler.fit(dummy_data)
            
        except Exception as e:
            self.logger.error(f"Failed to load ML models: {e}")
    
    async def _load_blacklists(self) -> None:
        """Load blacklists from storage"""
        # This would load from database/files
        # For demo purposes, adding sample entries
        self.blacklisted_cards.add("4111111111111111")
        self.blacklisted_ips.add("192.168.1.100")
        self.blacklisted_emails.add("fraud@example.com")
    
    async def _initialize_geoip(self) -> None:
        """Initialize GeoIP database"""
        try:
            # In practice, this would use a real GeoIP database
            # For demo, we'll skip the actual database
            pass
        except Exception as e:
            self.logger.error(f"Failed to initialize GeoIP: {e}")
    
    async def _load_user_profiles(self) -> None:
        """Load user profiles from storage"""
        # This would load from database
        # For demo, starting with empty profiles
        pass
    
    async def report_fraud_feedback(self, transaction_id -> None: str, is_fraud -> None: bool) -> None:
        """Report feedback on fraud assessment for model improvement"""
        try:
            if is_fraud:
                self.fraud_stats['confirmed_fraud'] += 1
            else:
                self.fraud_stats['false_positives'] += 1
            
            # This would be used to retrain models
            self.logger.info(f"Fraud feedback received: {transaction_id} - fraud: {is_fraud}")
            
        except Exception as e:
            self.logger.error(f"Failed to record fraud feedback: {e}")
    
    async def get_fraud_statistics(self) -> Dict[str, Any]:
        """Get fraud detection statistics"""
        total = self.fraud_stats['total_transactions']
        if total == 0:
            return self.fraud_stats
        
        stats = self.fraud_stats.copy()
        stats['fraud_rate'] = self.fraud_stats['flagged_transactions'] / total
        stats['block_rate'] = self.fraud_stats['blocked_transactions'] / total
        
        if self.fraud_stats['flagged_transactions'] > 0:
            stats['false_positive_rate'] = (
                self.fraud_stats['false_positives'] / 
                self.fraud_stats['flagged_transactions']
            )
        
        return stats


# Export main classes
__all__ = [
    "FraudDetectionEngine",
    "FraudAssessment",
    "TransactionFeatures",
    "UserProfile",
    "RiskLevel",
    "FraudIndicator",
    "ActionType"
]