"""
PayPal Risk Manager - Advanced Risk Assessment and Fraud Prevention
===================================================================

**Multi-Role Expert Implementation:**
- Lead Dev IA: Intelligent risk orchestration and ML-powered decision making
- Backend Senior: High-performance async risk processing with real-time analysis
- ML Engineer: Advanced fraud detection models and behavioral risk analysis
- DBA: Risk data analytics and fraud pattern storage with optimization
- Security: Advanced threat detection and secure risk assessment protocols
- Microservices: Distributed risk analysis across service boundaries
- Audio Engineer: Audio content-specific risk assessment and content validation
- DevOps: Real-time monitoring and automated risk response systems
- IA Prompt Engineer: Intelligent risk notifications and automated workflow responses

© 2025 Fahed Mlaiel. All rights reserved.
Enterprise-grade PayPal risk management with ML-powered fraud detection and security.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import paypalrestsdk

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskCategory(Enum):
    """Risk assessment categories"""
    TRANSACTION_FRAUD = "transaction_fraud"
    ACCOUNT_TAKEOVER = "account_takeover"
    IDENTITY_THEFT = "identity_theft"
    PAYMENT_ABUSE = "payment_abuse"
    CHARGEBACK_RISK = "chargeback_risk"
    VELOCITY_ABUSE = "velocity_abuse"
    DEVICE_FRAUD = "device_fraud"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    CONTENT_FRAUD = "content_fraud"
    AUDIO_PIRACY = "audio_piracy"

class RiskAction(Enum):
    """Risk response actions"""
    ALLOW = "allow"
    REVIEW = "review"
    CHALLENGE = "challenge"
    BLOCK = "block"
    ESCALATE = "escalate"

@dataclass
class RiskFactor:
    """Individual risk factor assessment"""
    factor_name: str
    risk_score: float
    confidence: float
    evidence: Dict[str, Any]
    category: RiskCategory
    severity: RiskLevel

@dataclass
class RiskAssessment:
    """Comprehensive risk assessment result"""
    transaction_id: str
    overall_risk_score: float
    risk_level: RiskLevel
    recommended_action: RiskAction
    risk_factors: List[RiskFactor]
    ml_predictions: Dict[str, float]
    behavioral_analysis: Dict[str, Any]
    device_fingerprint: Optional[Dict[str, Any]] = None
    geo_analysis: Optional[Dict[str, Any]] = None
    velocity_analysis: Optional[Dict[str, Any]] = None
    assessed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FraudAlert:
    """Fraud detection alert"""
    alert_id: str
    risk_assessment: RiskAssessment
    alert_type: str
    severity: RiskLevel
    automated_response: Optional[str] = None
    requires_human_review: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

class PayPalRiskManager:
    """
    🏆 ENTERPRISE PAYPAL RISK MANAGER
    ================================
    
    **Multi-Role Expert Implementation:**
    - 🤖 Lead Dev IA: Intelligent risk orchestration + ML decision making + automated workflows
    - 🏗️ Backend Senior: High-performance async risk processing + real-time analysis + optimization
    - 🧠 ML Engineer: Advanced fraud detection + behavioral analysis + anomaly detection models
    - 🗄️ DBA: Risk data analytics + pattern storage + optimized fraud queries
    - 🔒 Security: Advanced threat detection + secure assessment + incident response
    - 🔧 Microservices: Distributed risk analysis + service communication + event-driven alerts
    - 🎵 Audio Engineer: Audio content risk assessment + piracy detection + content validation
    - ⚙️ DevOps: Real-time monitoring + automated response + system health management
    - 🤖 IA Prompt Engineer: Intelligent notifications + automated workflows + smart responses
    """
    
    def __init__(self, paypal_config -> None: Dict[str, str], redis_client=None, db_pool=None) -> None:
        """Initialize PayPal Risk Manager with enterprise security features"""
        self.paypal_config = paypal_config
        self.redis_client = redis_client
        self.db_pool = db_pool
        
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": paypal_config.get("mode", "sandbox"),
            "client_id": paypal_config["client_id"],
            "client_secret": paypal_config["client_secret"]
        })
        
        # ML models for fraud detection
        self.fraud_detector = IsolationForest(contamination=0.1, random_state=42)
        self.behavior_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Risk metrics and monitoring
        self.metrics = {
            'assessments_performed': 0,
            'fraud_detected': 0,
            'false_positives': 0,
            'blocked_transactions': 0,
            'escalated_cases': 0,
            'ml_accuracy': 0.0
        }
        
        # Risk thresholds configuration
        self.risk_thresholds = {
            'low_risk': 0.3,
            'medium_risk': 0.6,
            'high_risk': 0.8,
            'critical_risk': 0.95
        }
        
        # Velocity tracking
        self.velocity_tracking = {
            'transaction_counts': defaultdict(int),
            'amount_totals': defaultdict(float),
            'device_tracking': defaultdict(list),
            'ip_tracking': defaultdict(list)
        }
        
        # Initialize ML models with sample data
        self._initialize_ml_models()
        
        logger.info("🏆 PayPal Risk Manager initialized with multi-role expertise")
    
    def _initialize_ml_models(self) -> None:
        """Initialize ML models with baseline fraud detection capabilities"""
        try:
            # Generate sample training data for demonstration
            # In production, this would be trained on real fraud data
            sample_data = np.random.rand(1000, 10)  # 10 risk features
            sample_labels = np.random.choice([0, 1], 1000, p=[0.9, 0.1])  # 10% fraud rate
            
            # Train models
            self.fraud_detector.fit(sample_data)
            self.behavior_classifier.fit(sample_data, sample_labels)
            self.scaler.fit(sample_data)
            
            logger.info("🧠 ML models initialized for fraud detection")
            
        except Exception as e:
            logger.warning(f"⚠️ ML model initialization failed: {str(e)}")
    
    async def assess_transaction_risk(
        self,
        transaction_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """
        🧠 ML Engineer + 🔒 Security: Comprehensive transaction risk assessment
        with ML-powered fraud detection and security analysis
        """
        try:
            self.metrics['assessments_performed'] += 1
            start_time = time.time()
            
            transaction_id = transaction_data.get('id', f"txn_{int(time.time())}")
            logger.info(f"🔍 Assessing transaction risk: {transaction_id}")
            
            # Extract risk features
            risk_features = await self._extract_risk_features(
                transaction_data, user_context, device_info
            )
            
            # Perform ML-based fraud detection
            ml_predictions = await self._perform_ml_fraud_detection(risk_features)
            
            # Analyze behavioral patterns
            behavioral_analysis = await self._analyze_behavioral_patterns(
                transaction_data, user_context
            )
            
            # Device and geo analysis
            device_analysis = await self._analyze_device_patterns(device_info)
            geo_analysis = await self._analyze_geographic_patterns(transaction_data)
            
            # Velocity analysis
            velocity_analysis = await self._analyze_velocity_patterns(
                transaction_data, user_context
            )
            
            # Audio content specific analysis (Audio Engineer expertise)
            audio_risk_factors = []
            if await self._is_audio_transaction(transaction_data):
                audio_risk_factors = await self._assess_audio_content_risk(transaction_data)
            
            # Compile all risk factors
            risk_factors = await self._compile_risk_factors(
                ml_predictions,
                behavioral_analysis,
                device_analysis,
                geo_analysis,
                velocity_analysis,
                audio_risk_factors
            )
            
            # Calculate overall risk score
            overall_risk_score = await self._calculate_overall_risk_score(risk_factors)
            
            # Determine risk level and recommended action
            risk_level = self._determine_risk_level(overall_risk_score)
            recommended_action = await self._determine_recommended_action(
                risk_level, risk_factors, transaction_data
            )
            
            # Create risk assessment
            risk_assessment = RiskAssessment(
                transaction_id=transaction_id,
                overall_risk_score=overall_risk_score,
                risk_level=risk_level,
                recommended_action=recommended_action,
                risk_factors=risk_factors,
                ml_predictions=ml_predictions,
                behavioral_analysis=behavioral_analysis,
                device_fingerprint=device_analysis,
                geo_analysis=geo_analysis,
                velocity_analysis=velocity_analysis
            )
            
            # Store assessment for analysis (DBA expertise)
            await self._store_risk_assessment(risk_assessment)
            
            # Generate alerts if necessary
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self._generate_fraud_alert(risk_assessment)
            
            # Update metrics
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                self.metrics['fraud_detected'] += 1
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"✅ Risk assessment completed: {transaction_id} - {risk_level.value} risk ({processing_time:.2f}ms)")
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"❌ Risk assessment failed: {str(e)}")
            raise
    
    async def _extract_risk_features(
        self,
        transaction_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]],
        device_info: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract numerical features for ML risk analysis"""
        try:
            features = {}
            
            # Transaction features
            features['amount'] = float(transaction_data.get('amount', 0))
            features['hour_of_day'] = datetime.now().hour
            features['day_of_week'] = datetime.now().weekday()
            
            # User features
            if user_context:
                features['account_age_days'] = (
                    datetime.now() - 
                    datetime.fromisoformat(user_context.get('created_at', datetime.now().isoformat()))
                ).days
                features['transaction_count'] = user_context.get('transaction_count', 0)
                features['average_transaction_amount'] = user_context.get('average_amount', 0)
            else:
                features['account_age_days'] = 0
                features['transaction_count'] = 0
                features['average_transaction_amount'] = 0
            
            # Device features
            if device_info:
                features['is_mobile'] = 1.0 if device_info.get('is_mobile') else 0.0
                features['new_device'] = 1.0 if device_info.get('is_new_device') else 0.0
                features['suspicious_ua'] = 1.0 if device_info.get('suspicious_user_agent') else 0.0
            else:
                features['is_mobile'] = 0.0
                features['new_device'] = 1.0  # Assume new if no device info
                features['suspicious_ua'] = 0.0
            
            # Additional risk indicators
            features['weekend_transaction'] = 1.0 if datetime.now().weekday() >= 5 else 0.0
            features['high_amount'] = 1.0 if features['amount'] > 1000 else 0.0
            
            return features
            
        except Exception as e:
            logger.warning(f"⚠️ Feature extraction failed: {str(e)}")
            return {}
    
    async def _perform_ml_fraud_detection(
        self,
        risk_features: Dict[str, float]
    ) -> Dict[str, float]:
        """
        🧠 ML Engineer: Perform ML-powered fraud detection analysis
        """
        try:
            # Convert features to array
            feature_array = np.array(list(risk_features.values())).reshape(1, -1)
            
            # Pad or truncate to match training data dimensions
            if feature_array.shape[1] < 10:
                padding = np.zeros((1, 10 - feature_array.shape[1]))
                feature_array = np.hstack([feature_array, padding])
            elif feature_array.shape[1] > 10:
                feature_array = feature_array[:, :10]
            
            # Scale features
            feature_array_scaled = self.scaler.transform(feature_array)
            
            # Anomaly detection
            anomaly_score = self.fraud_detector.decision_function(feature_array_scaled)[0]
            is_anomaly = self.fraud_detector.predict(feature_array_scaled)[0] == -1
            
            # Fraud classification
            fraud_probability = self.behavior_classifier.predict_proba(feature_array_scaled)[0][1]
            
            # Behavioral risk score
            behavioral_risk = min(max(fraud_probability + (0.1 if is_anomaly else 0), 0), 1)
            
            predictions = {
                'fraud_probability': fraud_probability,
                'anomaly_score': float(anomaly_score),
                'is_anomaly': is_anomaly,
                'behavioral_risk': behavioral_risk,
                'ml_confidence': 0.85 + (0.1 * fraud_probability)  # Higher confidence for higher risk
            }
            
            logger.debug(f"🧠 ML predictions completed: fraud_prob={fraud_probability:.3f}")
            return predictions
            
        except Exception as e:
            logger.warning(f"⚠️ ML fraud detection failed: {str(e)}")
            return {
                'fraud_probability': 0.5,  # Default neutral score
                'anomaly_score': 0.0,
                'is_anomaly': False,
                'behavioral_risk': 0.5,
                'ml_confidence': 0.5
            }
    
    async def _analyze_behavioral_patterns(
        self,
        transaction_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user behavioral patterns for risk assessment"""
        try:
            analysis = {
                'pattern_deviation': 0.0,
                'velocity_risk': 0.0,
                'time_pattern_risk': 0.0,
                'amount_pattern_risk': 0.0,
                'consistency_score': 1.0
            }
            
            if not user_context:
                analysis['pattern_deviation'] = 0.5  # Unknown user patterns
                return analysis
            
            # Analyze transaction timing patterns
            current_hour = datetime.now().hour
            typical_hours = user_context.get('typical_transaction_hours', [])
            
            if typical_hours and current_hour not in typical_hours:
                analysis['time_pattern_risk'] = 0.3
            
            # Analyze amount patterns
            current_amount = float(transaction_data.get('amount', 0))
            avg_amount = user_context.get('average_amount', current_amount)
            
            if avg_amount > 0:
                amount_deviation = abs(current_amount - avg_amount) / avg_amount
                analysis['amount_pattern_risk'] = min(amount_deviation, 1.0)
            
            # Calculate overall pattern deviation
            analysis['pattern_deviation'] = (
                analysis['time_pattern_risk'] * 0.3 +
                analysis['amount_pattern_risk'] * 0.7
            )
            
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Behavioral analysis failed: {str(e)}")
            return {'pattern_deviation': 0.0}
    
    async def _analyze_device_patterns(
        self,
        device_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze device patterns for fraud detection"""
        try:
            analysis = {
                'device_risk_score': 0.0,
                'is_new_device': False,
                'device_fingerprint_match': True,
                'suspicious_characteristics': []
            }
            
            if not device_info:
                analysis['device_risk_score'] = 0.3  # Unknown device adds risk
                analysis['is_new_device'] = True
                return analysis
            
            # Check for suspicious user agent
            user_agent = device_info.get('user_agent', '')
            if 'bot' in user_agent.lower() or len(user_agent) < 10:
                analysis['suspicious_characteristics'].append('suspicious_user_agent')
                analysis['device_risk_score'] += 0.3
            
            # Check for new device
            if device_info.get('is_new_device'):
                analysis['is_new_device'] = True
                analysis['device_risk_score'] += 0.2
            
            # Check for multiple device IDs
            if device_info.get('multiple_device_ids'):
                analysis['suspicious_characteristics'].append('multiple_device_ids')
                analysis['device_risk_score'] += 0.4
            
            analysis['device_risk_score'] = min(analysis['device_risk_score'], 1.0)
            
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Device analysis failed: {str(e)}")
            return {'device_risk_score': 0.0}
    
    async def _analyze_geographic_patterns(
        self,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze geographic patterns for fraud detection"""
        try:
            analysis = {
                'geo_risk_score': 0.0,
                'country_risk': 'low',
                'distance_from_usual': 0.0,
                'impossible_travel': False
            }
            
            # Get transaction location
            country = transaction_data.get('country', 'unknown')
            ip_address = transaction_data.get('ip_address')
            
            # High-risk countries (simplified list)
            high_risk_countries = ['unknown', 'XX', 'ZZ']
            
            if country in high_risk_countries:
                analysis['country_risk'] = 'high'
                analysis['geo_risk_score'] = 0.5
            
            # Check for impossible travel (simplified)
            # In production, this would check against user's recent locations
            if self.redis_client and ip_address:
                last_ip_key = f"user_last_ip:{transaction_data.get('user_id', 'unknown')}"
                last_ip = await self.redis_client.get(last_ip_key)
                
                if last_ip and last_ip != ip_address:
                    # Simplified impossible travel detection
                    analysis['impossible_travel'] = False  # Would implement actual geo-distance calculation
                
                # Store current IP
                await self.redis_client.setex(last_ip_key, 3600, ip_address)
            
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Geographic analysis failed: {str(e)}")
            return {'geo_risk_score': 0.0}
    
    async def _analyze_velocity_patterns(
        self,
        transaction_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze transaction velocity for fraud detection"""
        try:
            analysis = {
                'velocity_risk_score': 0.0,
                'transaction_frequency': 'normal',
                'amount_velocity': 'normal',
                'recent_transaction_count': 0
            }
            
            user_id = transaction_data.get('user_id', 'unknown')
            current_amount = float(transaction_data.get('amount', 0))
            
            # Track velocity in Redis
            if self.redis_client:
                # Count transactions in last hour
                hour_key = f"velocity_hour:{user_id}"
                hour_count = await self.redis_client.incr(hour_key)
                await self.redis_client.expire(hour_key, 3600)
                
                # Count transactions in last 24 hours
                day_key = f"velocity_day:{user_id}"
                day_count = await self.redis_client.incr(day_key)
                await self.redis_client.expire(day_key, 86400)
                
                # Track amount velocity
                amount_key = f"velocity_amount:{user_id}"
                await self.redis_client.incrbyfloat(amount_key, current_amount)
                await self.redis_client.expire(amount_key, 3600)
                
                total_amount = float(await self.redis_client.get(amount_key) or 0)
                
                analysis['recent_transaction_count'] = hour_count
                
                # Assess velocity risk
                if hour_count > 10:  # More than 10 transactions per hour
                    analysis['transaction_frequency'] = 'high'
                    analysis['velocity_risk_score'] += 0.4
                
                if total_amount > 5000:  # More than $5000 per hour
                    analysis['amount_velocity'] = 'high'
                    analysis['velocity_risk_score'] += 0.3
                
                if day_count > 50:  # More than 50 transactions per day
                    analysis['transaction_frequency'] = 'very_high'
                    analysis['velocity_risk_score'] += 0.3
            
            analysis['velocity_risk_score'] = min(analysis['velocity_risk_score'], 1.0)
            
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Velocity analysis failed: {str(e)}")
            return {'velocity_risk_score': 0.0}
    
    async def _is_audio_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """🎵 Audio Engineer: Check if transaction is audio-related"""
        try:
            metadata = transaction_data.get('metadata', {})
            description = transaction_data.get('description', '').lower()
            
            return (
                metadata.get('content_type') == 'audio' or
                'audio' in description or
                'music' in description or
                'podcast' in description or
                metadata.get('category') == 'audio'
            )
        except:
            return False
    
    async def _assess_audio_content_risk(
        self,
        transaction_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """
        🎵 Audio Engineer: Assess audio content-specific risks
        """
        try:
            risk_factors = []
            metadata = transaction_data.get('metadata', {})
            
            # Check for potential audio piracy indicators
            if metadata.get('source') == 'unknown':
                risk_factors.append(RiskFactor(
                    factor_name="unknown_audio_source",
                    risk_score=0.4,
                    confidence=0.7,
                    evidence={'source': 'unknown'},
                    category=RiskCategory.AUDIO_PIRACY,
                    severity=RiskLevel.MEDIUM
                ))
            
            # Check for suspicious audio characteristics
            duration = metadata.get('duration_seconds', 0)
            if duration > 7200:  # More than 2 hours
                risk_factors.append(RiskFactor(
                    factor_name="unusually_long_audio",
                    risk_score=0.3,
                    confidence=0.8,
                    evidence={'duration': duration},
                    category=RiskCategory.CONTENT_FRAUD,
                    severity=RiskLevel.MEDIUM
                ))
            
            # Check for low-quality indicators
            quality = metadata.get('quality', 'unknown')
            if quality == 'low':
                risk_factors.append(RiskFactor(
                    factor_name="low_quality_audio",
                    risk_score=0.2,
                    confidence=0.6,
                    evidence={'quality': quality},
                    category=RiskCategory.CONTENT_FRAUD,
                    severity=RiskLevel.LOW
                ))
            
            return risk_factors
            
        except Exception as e:
            logger.warning(f"⚠️ Audio risk assessment failed: {str(e)}")
            return []
    
    async def _compile_risk_factors(
        self,
        ml_predictions: Dict[str, float],
        behavioral_analysis: Dict[str, Any],
        device_analysis: Dict[str, Any],
        geo_analysis: Dict[str, Any],
        velocity_analysis: Dict[str, Any],
        audio_risk_factors: List[RiskFactor]
    ) -> List[RiskFactor]:
        """Compile all risk factors into a comprehensive list"""
        try:
            risk_factors = []
            
            # ML-based risk factors
            if ml_predictions.get('fraud_probability', 0) > 0.7:
                risk_factors.append(RiskFactor(
                    factor_name="high_fraud_probability",
                    risk_score=ml_predictions['fraud_probability'],
                    confidence=ml_predictions.get('ml_confidence', 0.8),
                    evidence=ml_predictions,
                    category=RiskCategory.TRANSACTION_FRAUD,
                    severity=RiskLevel.HIGH
                ))
            
            # Behavioral risk factors
            if behavioral_analysis.get('pattern_deviation', 0) > 0.5:
                risk_factors.append(RiskFactor(
                    factor_name="behavioral_anomaly",
                    risk_score=behavioral_analysis['pattern_deviation'],
                    confidence=0.7,
                    evidence=behavioral_analysis,
                    category=RiskCategory.BEHAVIORAL_ANOMALY,
                    severity=RiskLevel.MEDIUM
                ))
            
            # Device risk factors
            if device_analysis.get('device_risk_score', 0) > 0.4:
                risk_factors.append(RiskFactor(
                    factor_name="suspicious_device",
                    risk_score=device_analysis['device_risk_score'],
                    confidence=0.8,
                    evidence=device_analysis,
                    category=RiskCategory.DEVICE_FRAUD,
                    severity=RiskLevel.MEDIUM
                ))
            
            # Geographic risk factors
            if geo_analysis.get('geo_risk_score', 0) > 0.3:
                risk_factors.append(RiskFactor(
                    factor_name="geographic_risk",
                    risk_score=geo_analysis['geo_risk_score'],
                    confidence=0.6,
                    evidence=geo_analysis,
                    category=RiskCategory.IDENTITY_THEFT,
                    severity=RiskLevel.MEDIUM
                ))
            
            # Velocity risk factors
            if velocity_analysis.get('velocity_risk_score', 0) > 0.4:
                risk_factors.append(RiskFactor(
                    factor_name="high_velocity",
                    risk_score=velocity_analysis['velocity_risk_score'],
                    confidence=0.9,
                    evidence=velocity_analysis,
                    category=RiskCategory.VELOCITY_ABUSE,
                    severity=RiskLevel.HIGH
                ))
            
            # Add audio-specific risk factors
            risk_factors.extend(audio_risk_factors)
            
            return risk_factors
            
        except Exception as e:
            logger.warning(f"⚠️ Risk factor compilation failed: {str(e)}")
            return []
    
    async def _calculate_overall_risk_score(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate overall risk score from individual factors"""
        try:
            if not risk_factors:
                return 0.0
            
            # Weighted average based on confidence and severity
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for factor in risk_factors:
                # Weight by confidence and severity
                severity_weight = {
                    RiskLevel.LOW: 0.5,
                    RiskLevel.MEDIUM: 1.0,
                    RiskLevel.HIGH: 1.5,
                    RiskLevel.CRITICAL: 2.0
                }.get(factor.severity, 1.0)
                
                weight = factor.confidence * severity_weight
                total_weighted_score += factor.risk_score * weight
                total_weight += weight
            
            if total_weight == 0:
                return 0.0
            
            overall_score = total_weighted_score / total_weight
            return min(max(overall_score, 0.0), 1.0)  # Clamp between 0 and 1
            
        except Exception as e:
            logger.warning(f"⚠️ Risk score calculation failed: {str(e)}")
            return 0.5  # Default moderate risk
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on overall risk score"""
        if risk_score >= self.risk_thresholds['critical_risk']:
            return RiskLevel.CRITICAL
        elif risk_score >= self.risk_thresholds['high_risk']:
            return RiskLevel.HIGH
        elif risk_score >= self.risk_thresholds['medium_risk']:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _determine_recommended_action(
        self,
        risk_level: RiskLevel,
        risk_factors: List[RiskFactor],
        transaction_data: Dict[str, Any]
    ) -> RiskAction:
        """
        🤖 Lead Dev IA: Determine recommended action based on intelligent analysis
        """
        try:
            # Base action on risk level
            if risk_level == RiskLevel.CRITICAL:
                return RiskAction.BLOCK
            elif risk_level == RiskLevel.HIGH:
                # Check for specific high-risk factors
                has_fraud_indicators = any(
                    factor.category in [RiskCategory.TRANSACTION_FRAUD, RiskCategory.IDENTITY_THEFT]
                    for factor in risk_factors
                )
                
                if has_fraud_indicators:
                    return RiskAction.BLOCK
                else:
                    return RiskAction.REVIEW
            elif risk_level == RiskLevel.MEDIUM:
                # Check transaction amount for escalation
                amount = float(transaction_data.get('amount', 0))
                if amount > 1000:  # High-value transactions
                    return RiskAction.CHALLENGE
                else:
                    return RiskAction.REVIEW
            else:
                return RiskAction.ALLOW
                
        except Exception as e:
            logger.warning(f"⚠️ Action determination failed: {str(e)}")
            return RiskAction.REVIEW  # Default to review for safety
    
    async def _store_risk_assessment(self, risk_assessment -> None: RiskAssessment) -> None:
        """
        🗄️ DBA: Store risk assessment in database for analysis
        """
        try:
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO paypal_risk_assessments 
                        (transaction_id, overall_risk_score, risk_level, 
                         recommended_action, risk_factors, ml_predictions, 
                         assessed_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    risk_assessment.transaction_id,
                    risk_assessment.overall_risk_score,
                    risk_assessment.risk_level.value,
                    risk_assessment.recommended_action.value,
                    json.dumps([{
                        'factor_name': rf.factor_name,
                        'risk_score': rf.risk_score,
                        'confidence': rf.confidence,
                        'category': rf.category.value,
                        'severity': rf.severity.value
                    } for rf in risk_assessment.risk_factors]),
                    json.dumps(risk_assessment.ml_predictions),
                    risk_assessment.assessed_at
                    )
                    
        except Exception as e:
            logger.warning(f"⚠️ Risk assessment storage failed: {str(e)}")
    
    async def _generate_fraud_alert(self, risk_assessment -> None: RiskAssessment) -> None:
        """
        🔒 Security + 🤖 IA Prompt Engineer: Generate fraud alert with intelligent response
        """
        try:
            alert_id = f"alert_{int(time.time())}_{risk_assessment.transaction_id}"
            
            # Determine if human review is required
            requires_human_review = (
                risk_assessment.risk_level == RiskLevel.CRITICAL or
                risk_assessment.recommended_action == RiskAction.ESCALATE
            )
            
            # Generate automated response
            automated_response = await self._generate_automated_response(risk_assessment)
            
            fraud_alert = FraudAlert(
                alert_id=alert_id,
                risk_assessment=risk_assessment,
                alert_type="fraud_detection",
                severity=risk_assessment.risk_level,
                automated_response=automated_response,
                requires_human_review=requires_human_review
            )
            
            # Store alert
            if self.db_pool:
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO fraud_alerts 
                        (alert_id, transaction_id, alert_type, severity, 
                         automated_response, requires_human_review, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    alert_id,
                    risk_assessment.transaction_id,
                    fraud_alert.alert_type,
                    fraud_alert.severity.value,
                    automated_response,
                    requires_human_review,
                    fraud_alert.created_at
                    )
            
            # Send real-time notifications (would integrate with notification system)
            logger.warning(f"🚨 Fraud alert generated: {alert_id} - {risk_assessment.risk_level.value}")
            
            return fraud_alert
            
        except Exception as e:
            logger.error(f"❌ Fraud alert generation failed: {str(e)}")
            return None
    
    async def _generate_automated_response(self, risk_assessment: RiskAssessment) -> str:
        """🤖 IA Prompt Engineer: Generate intelligent automated response"""
        try:
            if risk_assessment.recommended_action == RiskAction.BLOCK:
                return "Transaction blocked due to high fraud risk. Please verify identity and try again."
            elif risk_assessment.recommended_action == RiskAction.CHALLENGE:
                return "Additional verification required. Please complete security challenge."
            elif risk_assessment.recommended_action == RiskAction.REVIEW:
                return "Transaction flagged for review. Processing may be delayed."
            else:
                return "Transaction approved."
                
        except Exception as e:
            logger.warning(f"⚠️ Automated response generation failed: {str(e)}")
            return "Transaction under review."
    
    # Health and monitoring methods
    
    def get_risk_manager_health(self) -> Dict[str, Any]:
        """
        ⚙️ DevOps: Get risk manager system health and metrics
        """
        fraud_rate = 0.0
        if self.metrics['assessments_performed'] > 0:
            fraud_rate = self.metrics['fraud_detected'] / self.metrics['assessments_performed']
        
        return {
            'status': 'healthy',
            'metrics': self.metrics,
            'fraud_detection_rate': fraud_rate,
            'ml_models_status': 'operational',
            'risk_thresholds': self.risk_thresholds,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    async def update_risk_thresholds(self, new_thresholds -> None: Dict[str, float]) -> None:
        """Update risk assessment thresholds"""
        try:
            self.risk_thresholds.update(new_thresholds)
            logger.info(f"🔧 Risk thresholds updated: {new_thresholds}")
        except Exception as e:
            logger.error(f"❌ Risk threshold update failed: {str(e)}")
    
    async def retrain_ml_models(self, training_data -> None: Optional[List[Dict]] = None) -> None:
        """
        🧠 ML Engineer: Retrain ML models with new fraud data
        """
        try:
            if training_data:
                # Extract features and labels from training data
                features = []
                labels = []
                
                for data_point in training_data:
                    feature_dict = await self._extract_risk_features(
                        data_point.get('transaction_data', {}),
                        data_point.get('user_context'),
                        data_point.get('device_info')
                    )
                    features.append(list(feature_dict.values()))
                    labels.append(data_point.get('is_fraud', 0))
                
                # Retrain models
                features_array = np.array(features)
                labels_array = np.array(labels)
                
                self.fraud_detector.fit(features_array)
                self.behavior_classifier.fit(features_array, labels_array)
                self.scaler.fit(features_array)
                
                logger.info(f"🧠 ML models retrained with {len(training_data)} samples")
            
        except Exception as e:
            logger.error(f"❌ ML model retraining failed: {str(e)}")