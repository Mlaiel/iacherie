#!/usr/bin/env python3
"""
🔒 Risk Assessment Engine - ML-Powered Security Intelligence
============================================================

Advanced risk assessment engine with ML-powered threat analysis,
real-time risk scoring, and adaptive security decision making.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: ML + Security + Analytics + Backend
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import json
import logging
import pickle
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import hashlib

# ML imports for risk assessment
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.calibration import CalibratedClassifierCV
import joblib

# Statistical analysis
from scipy import stats
from scipy.stats import zscore


class RiskLevel(Enum):
    """Risk assessment levels"""
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class RiskCategory(Enum):
    """Risk category types"""
    AUTHENTICATION = "authentication"
    BEHAVIORAL = "behavioral"
    LOCATION = "location"
    DEVICE = "device"
    NETWORK = "network"
    TEMPORAL = "temporal"
    TRANSACTION = "transaction"
    CONTENT = "content"
    REPUTATION = "reputation"


class ThreatType(Enum):
    """Types of security threats"""
    ACCOUNT_TAKEOVER = "account_takeover"
    CREDENTIAL_STUFFING = "credential_stuffing"
    BRUTE_FORCE = "brute_force"
    SOCIAL_ENGINEERING = "social_engineering"
    MALWARE = "malware"
    PHISHING = "phishing"
    FRAUD = "fraud"
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_THREAT = "insider_threat"
    AUTOMATED_ATTACK = "automated_attack"


@dataclass
class RiskFactor:
    """Individual risk factor"""
    factor_id: str
    category: RiskCategory
    name: str
    description: str
    value: float
    weight: float
    confidence: float
    evidence: Dict[str, Any]
    timestamp: datetime


@dataclass
class ThreatIndicator:
    """Security threat indicator"""
    indicator_id: str
    threat_type: ThreatType
    severity: RiskLevel
    confidence: float
    description: str
    iocs: List[str]  # Indicators of Compromise
    ttps: List[str]  # Tactics, Techniques, and Procedures
    evidence: Dict[str, Any]
    first_seen: datetime
    last_seen: datetime


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment result"""
    assessment_id: str
    user_id: str
    session_id: Optional[str]
    timestamp: datetime
    
    # Overall risk
    overall_risk_level: RiskLevel
    overall_risk_score: float
    confidence: float
    
    # Risk factors
    risk_factors: List[RiskFactor]
    threat_indicators: List[ThreatIndicator]
    
    # Category-specific risks
    category_risks: Dict[RiskCategory, float]
    
    # Recommendations
    recommended_actions: List[str]
    security_controls: List[str]
    monitoring_requirements: List[str]
    
    # Metadata
    model_version: str
    assessment_duration_ms: float
    expires_at: datetime


@dataclass
class UserRiskProfile:
    """User's historical risk profile"""
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Historical risk metrics
    avg_risk_score: float
    risk_score_variance: float
    risk_trend: str  # "increasing", "decreasing", "stable"
    
    # Behavioral baselines
    normal_locations: List[Dict[str, Any]]
    normal_devices: Set[str]
    normal_time_patterns: Dict[str, Any]
    normal_behavior_patterns: Dict[str, Any]
    
    # Risk factors
    persistent_risk_factors: List[RiskFactor]
    recent_threats: List[ThreatIndicator]
    
    # Trust metrics
    trust_score: float
    reputation_score: float
    account_age_days: int
    verification_level: int


class RiskAssessmentEngine:
    """
    🔒 Enterprise Risk Assessment Engine
    
    ML-powered risk assessment with comprehensive threat analysis,
    behavioral profiling, and adaptive security decision making.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize risk assessment engine"""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "security/config/risk_config.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # ML Models
        self.risk_classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            class_weight='balanced'
        )
        self.anomaly_detector = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=8,
            random_state=42
        )
        
        # Feature processing
        self.scaler = StandardScaler()
        self.feature_selector = SelectKBest(f_classif, k=50)
        self.label_encoder = LabelEncoder()
        
        # Calibrated classifier for probability estimates
        self.calibrated_classifier = CalibratedClassifierCV(
            self.risk_classifier, 
            method='isotonic',
            cv=3
        )
        
        # Risk data storage
        self.user_risk_profiles: Dict[str, UserRiskProfile] = {}
        self.assessment_history: deque = deque(maxlen=10000)
        self.threat_intelligence: Dict[str, ThreatIndicator] = {}
        
        # Real-time risk tracking
        self.active_sessions: Dict[str, Dict] = {}
        self.risk_thresholds = self._initialize_thresholds()
        
        # Feature extractors
        self.feature_extractors = {
            'authentication': self._extract_auth_features,
            'behavioral': self._extract_behavioral_features,
            'location': self._extract_location_features,
            'device': self._extract_device_features,
            'network': self._extract_network_features,
            'temporal': self._extract_temporal_features,
            'transaction': self._extract_transaction_features,
            'reputation': self._extract_reputation_features
        }
        
        # Models training status
        self.models_trained = False
        
        # Initialize threat intelligence
        self._initialize_threat_intelligence()
    
    async def assess_risk(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> RiskAssessment:
        """
        Perform comprehensive risk assessment
        
        Args:
            user_id: User identifier
            session_data: Current session data
            context: Additional context information
            
        Returns:
            Comprehensive risk assessment
        """
        start_time = datetime.utcnow()
        assessment_id = self._generate_assessment_id(user_id, start_time)
        
        try:
            # Get or create user risk profile
            risk_profile = await self._get_or_create_risk_profile(user_id)
            
            # Extract risk features
            features = await self._extract_comprehensive_features(
                user_id, session_data, context
            )
            
            # Calculate risk factors
            risk_factors = await self._calculate_risk_factors(
                user_id, features, risk_profile
            )
            
            # Detect threat indicators
            threat_indicators = await self._detect_threat_indicators(
                user_id, features, session_data
            )
            
            # Calculate category-specific risks
            category_risks = self._calculate_category_risks(risk_factors)
            
            # ML-based risk scoring
            ml_risk_score, ml_confidence = await self._ml_risk_assessment(
                features, risk_profile
            )
            
            # Combine risk scores
            overall_risk_score, overall_confidence = self._combine_risk_scores(
                risk_factors, threat_indicators, ml_risk_score, ml_confidence
            )
            
            # Determine risk level
            overall_risk_level = self._determine_risk_level(overall_risk_score)
            
            # Generate recommendations
            recommended_actions = self._generate_recommendations(
                overall_risk_level, risk_factors, threat_indicators
            )
            
            security_controls = self._suggest_security_controls(
                overall_risk_level, category_risks
            )
            
            monitoring_requirements = self._determine_monitoring_requirements(
                overall_risk_level, threat_indicators
            )
            
            # Create assessment
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            assessment = RiskAssessment(
                assessment_id=assessment_id,
                user_id=user_id,
                session_id=session_data.get("session_id"),
                timestamp=start_time,
                overall_risk_level=overall_risk_level,
                overall_risk_score=overall_risk_score,
                confidence=overall_confidence,
                risk_factors=risk_factors,
                threat_indicators=threat_indicators,
                category_risks=category_risks,
                recommended_actions=recommended_actions,
                security_controls=security_controls,
                monitoring_requirements=monitoring_requirements,
                model_version="2.0.0",
                assessment_duration_ms=duration_ms,
                expires_at=start_time + timedelta(hours=1)
            )
            
            # Update user risk profile
            await self._update_risk_profile(risk_profile, assessment)
            
            # Store assessment
            self.assessment_history.append(assessment)
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Risk assessment error: {e}")
            raise
    
    async def calculate_threat_score(
        self,
        threat_indicators: List[ThreatIndicator],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive threat score
        
        Args:
            threat_indicators: List of threat indicators
            context: Additional context
            
        Returns:
            Threat scoring result
        """
        try:
            if not threat_indicators:
                return {
                    "threat_score": 0.0,
                    "threat_level": RiskLevel.MINIMAL,
                    "confidence": 1.0,
                    "primary_threats": [],
                    "threat_categories": {}
                }
            
            # Calculate threat scores by type
            threat_scores = defaultdict(list)
            for indicator in threat_indicators:
                threat_scores[indicator.threat_type].append(
                    indicator.severity.value * indicator.confidence
                )
            
            # Aggregate scores by threat type
            threat_type_scores = {}
            for threat_type, scores in threat_scores.items():
                threat_type_scores[threat_type.value] = {
                    "max_score": max(scores),
                    "avg_score": np.mean(scores),
                    "count": len(scores),
                    "total_score": sum(scores)
                }
            
            # Calculate overall threat score
            if threat_type_scores:
                max_scores = [info["max_score"] for info in threat_type_scores.values()]
                overall_threat_score = min(5.0, max(max_scores))
            else:
                overall_threat_score = 0.0
            
            # Determine threat level
            if overall_threat_score >= 4.5:
                threat_level = RiskLevel.CRITICAL
            elif overall_threat_score >= 3.5:
                threat_level = RiskLevel.HIGH
            elif overall_threat_score >= 2.5:
                threat_level = RiskLevel.MEDIUM
            elif overall_threat_score >= 1.5:
                threat_level = RiskLevel.LOW
            else:
                threat_level = RiskLevel.MINIMAL
            
            # Calculate confidence
            confidences = [indicator.confidence for indicator in threat_indicators]
            overall_confidence = np.mean(confidences) if confidences else 0.0
            
            # Identify primary threats
            primary_threats = sorted(
                threat_type_scores.items(),
                key=lambda x: x[1]["max_score"],
                reverse=True
            )[:3]
            
            return {
                "threat_score": overall_threat_score,
                "threat_level": threat_level,
                "confidence": overall_confidence,
                "primary_threats": [threat[0] for threat in primary_threats],
                "threat_categories": threat_type_scores,
                "indicators_count": len(threat_indicators),
                "severity_distribution": self._analyze_severity_distribution(threat_indicators)
            }
            
        except Exception as e:
            self.logger.error(f"Threat score calculation error: {e}")
            raise
    
    async def update_threat_intelligence(
        self,
        indicators: List[ThreatIndicator],
        source: str = "internal"
    ) -> Dict[str, Any]:
        """
        Update threat intelligence database
        
        Args:
            indicators: New threat indicators
            source: Source of intelligence
            
        Returns:
            Update result
        """
        try:
            updated_count = 0
            new_count = 0
            
            for indicator in indicators:
                existing = self.threat_intelligence.get(indicator.indicator_id)
                
                if existing:
                    # Update existing indicator
                    existing.last_seen = indicator.last_seen
                    existing.confidence = max(existing.confidence, indicator.confidence)
                    existing.evidence.update(indicator.evidence)
                    updated_count += 1
                else:
                    # Add new indicator
                    self.threat_intelligence[indicator.indicator_id] = indicator
                    new_count += 1
            
            # Cleanup old indicators
            cleanup_threshold = datetime.utcnow() - timedelta(days=30)
            expired_indicators = [
                iid for iid, indicator in self.threat_intelligence.items()
                if indicator.last_seen < cleanup_threshold
            ]
            
            for iid in expired_indicators:
                del self.threat_intelligence[iid]
            
            return {
                "success": True,
                "updated_indicators": updated_count,
                "new_indicators": new_count,
                "total_indicators": len(self.threat_intelligence),
                "expired_indicators": len(expired_indicators),
                "source": source
            }
            
        except Exception as e:
            self.logger.error(f"Threat intelligence update error: {e}")
            raise
    
    async def train_risk_models(
        self,
        training_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Train ML models for risk assessment
        
        Args:
            training_data: Optional training data
            
        Returns:
            Training result
        """
        try:
            # Use historical data if no training data provided
            if not training_data:
                training_data = self._prepare_training_data()
            
            if not training_data or len(training_data) < 100:
                return {
                    "success": False,
                    "error": "Insufficient training data",
                    "required_samples": 100,
                    "available_samples": len(training_data) if training_data else 0
                }
            
            # Prepare features and labels
            X, y = self._prepare_feature_matrix(training_data)
            
            # Feature selection
            X_selected = self.feature_selector.fit_transform(X, y)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X_selected)
            
            # Train risk classifier
            self.risk_classifier.fit(X_scaled, y)
            
            # Train calibrated classifier
            self.calibrated_classifier.fit(X_scaled, y)
            
            # Train anomaly detector
            # Convert risk levels to binary (normal vs anomalous)
            y_binary = (y >= 3).astype(int)  # HIGH and CRITICAL as anomalous
            self.anomaly_detector.fit(X_scaled, y_binary)
            
            # Evaluate models
            risk_cv_scores = cross_val_score(self.risk_classifier, X_scaled, y, cv=5)
            anomaly_cv_scores = cross_val_score(self.anomaly_detector, X_scaled, y_binary, cv=5)
            
            self.models_trained = True
            
            return {
                "success": True,
                "training_samples": len(training_data),
                "features_selected": X_selected.shape[1],
                "risk_classifier_accuracy": {
                    "mean": np.mean(risk_cv_scores),
                    "std": np.std(risk_cv_scores),
                    "scores": risk_cv_scores.tolist()
                },
                "anomaly_detector_accuracy": {
                    "mean": np.mean(anomaly_cv_scores),
                    "std": np.std(anomaly_cv_scores),
                    "scores": anomaly_cv_scores.tolist()
                },
                "feature_importance": self._get_feature_importance()
            }
            
        except Exception as e:
            self.logger.error(f"Model training error: {e}")
            raise
    
    # Private methods
    
    def _load_config(self) -> Dict[str, Any]:
        """Load risk assessment configuration"""
        default_config = {
            "risk_thresholds": {
                "minimal": 1.0,
                "low": 2.0,
                "medium": 3.0,
                "high": 4.0,
                "critical": 5.0
            },
            "feature_weights": {
                "authentication": 0.25,
                "behavioral": 0.20,
                "location": 0.15,
                "device": 0.15,
                "network": 0.10,
                "temporal": 0.10,
                "reputation": 0.05
            },
            "assessment_expiry_hours": 1,
            "profile_update_threshold": 0.1
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
        except Exception as e:
            self.logger.warning(f"Config loading failed: {e}")
        
        return default_config
    
    def _initialize_thresholds(self) -> Dict[str, float]:
        """Initialize risk thresholds"""
        return self.config.get("risk_thresholds", {
            "minimal": 1.0,
            "low": 2.0,
            "medium": 3.0,
            "high": 4.0,
            "critical": 5.0
        })
    
    def _initialize_threat_intelligence(self):
        """Initialize threat intelligence database"""
        # In production, load from external threat feeds
        # For now, create some basic threat indicators
        
        sample_indicators = [
            ThreatIndicator(
                indicator_id="brute_force_001",
                threat_type=ThreatType.BRUTE_FORCE,
                severity=RiskLevel.HIGH,
                confidence=0.9,
                description="Multiple failed login attempts",
                iocs=["failed_login_threshold_exceeded"],
                ttps=["T1110.001"],  # MITRE ATT&CK: Brute Force - Password Guessing
                evidence={"threshold": 5, "time_window": "5_minutes"},
                first_seen=datetime.utcnow() - timedelta(days=30),
                last_seen=datetime.utcnow()
            ),
            ThreatIndicator(
                indicator_id="account_takeover_001",
                threat_type=ThreatType.ACCOUNT_TAKEOVER,
                severity=RiskLevel.CRITICAL,
                confidence=0.95,
                description="Login from new location with unusual behavior",
                iocs=["new_location", "behavioral_anomaly"],
                ttps=["T1078"],  # MITRE ATT&CK: Valid Accounts
                evidence={"location_distance": "> 1000km", "behavior_change": "significant"},
                first_seen=datetime.utcnow() - timedelta(days=15),
                last_seen=datetime.utcnow()
            )
        ]
        
        for indicator in sample_indicators:
            self.threat_intelligence[indicator.indicator_id] = indicator
    
    def _generate_assessment_id(self, user_id: str, timestamp: datetime) -> str:
        """Generate unique assessment ID"""
        data = f"{user_id}_{timestamp.isoformat()}_{hash(str(timestamp))}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    async def _get_or_create_risk_profile(self, user_id: str) -> UserRiskProfile:
        """Get existing risk profile or create new one"""
        if user_id not in self.user_risk_profiles:
            self.user_risk_profiles[user_id] = UserRiskProfile(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                avg_risk_score=2.0,  # Neutral risk
                risk_score_variance=0.5,
                risk_trend="stable",
                normal_locations=[],
                normal_devices=set(),
                normal_time_patterns={},
                normal_behavior_patterns={},
                persistent_risk_factors=[],
                recent_threats=[],
                trust_score=0.5,
                reputation_score=0.5,
                account_age_days=0,
                verification_level=0
            )
        
        return self.user_risk_profiles[user_id]
    
    async def _extract_comprehensive_features(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract comprehensive risk features"""
        features = {}
        
        for feature_type, extractor in self.feature_extractors.items():
            try:
                features[feature_type] = await extractor(user_id, session_data, context)
            except Exception as e:
                self.logger.warning(f"Feature extraction failed for {feature_type}: {e}")
                features[feature_type] = {}
        
        return features
    
    async def _extract_auth_features(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract authentication-related features"""
        features = {}
        
        # Login attempt patterns
        features["failed_login_count"] = session_data.get("failed_logins", 0)
        features["login_success_rate"] = session_data.get("login_success_rate", 1.0)
        features["time_since_last_login"] = session_data.get("time_since_last_login", 0)
        
        # Authentication methods
        features["mfa_enabled"] = float(session_data.get("mfa_enabled", False))
        features["mfa_success"] = float(session_data.get("mfa_success", False))
        features["auth_method_count"] = session_data.get("auth_method_count", 1)
        
        # Password-related
        features["password_age_days"] = session_data.get("password_age_days", 0)
        features["password_strength"] = session_data.get("password_strength", 0.5)
        features["password_reuse"] = float(session_data.get("password_reuse", False))
        
        return features
    
    async def _extract_behavioral_features(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract behavioral features"""
        features = {}
        
        # Typing patterns
        features["typing_speed"] = session_data.get("typing_speed", 0)
        features["typing_rhythm_variance"] = session_data.get("typing_rhythm_variance", 0)
        
        # Mouse behavior
        features["mouse_velocity"] = session_data.get("mouse_velocity", 0)
        features["click_pattern_variance"] = session_data.get("click_pattern_variance", 0)
        
        # Session behavior
        features["session_duration"] = session_data.get("session_duration", 0)
        features["page_views"] = session_data.get("page_views", 0)
        features["action_count"] = session_data.get("action_count", 0)
        features["idle_time_ratio"] = session_data.get("idle_time_ratio", 0)
        
        # Navigation patterns
        features["unique_pages"] = session_data.get("unique_pages", 0)
        features["back_button_usage"] = session_data.get("back_button_usage", 0)
        features["scroll_speed"] = session_data.get("scroll_speed", 0)
        
        return features
    
    async def _extract_location_features(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract location-based features"""
        features = {}
        
        # Basic location
        location = session_data.get("location", {})
        features["has_location"] = float(bool(location))
        features["latitude"] = location.get("latitude", 0)
        features["longitude"] = location.get("longitude", 0)
        
        # Location risk indicators
        features["is_vpn"] = float(location.get("is_vpn", False))
        features["is_proxy"] = float(location.get("is_proxy", False))
        features["is_tor"] = float(location.get("is_tor", False))
        features["is_hosting_provider"] = float(location.get("is_hosting", False))
        
        # Distance calculations
        features["distance_from_home"] = session_data.get("distance_from_home", 0)
        features["velocity_impossible"] = float(session_data.get("velocity_impossible", False))
        
        # Geographic risk
        features["country_risk_score"] = location.get("country_risk", 0)
        features["region_risk_score"] = location.get("region_risk", 0)
        
        return features
    
    async def _extract_device_features(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract device-related features"""
        features = {}
        
        # Device identification
        features["is_known_device"] = float(session_data.get("is_known_device", False))
        features["device_fingerprint_confidence"] = session_data.get("fingerprint_confidence", 0)
        features["device_change_count"] = session_data.get("device_changes", 0)
        
        # Device characteristics
        features["is_mobile"] = float(session_data.get("is_mobile", False))
        features["is_tablet"] = float(session_data.get("is_tablet", False))
        features["screen_resolution_width"] = session_data.get("screen_width", 0)
        features["screen_resolution_height"] = session_data.get("screen_height", 0)
        
        # Browser and OS
        features["browser_version_age"] = session_data.get("browser_age", 0)
        features["os_version_age"] = session_data.get("os_age", 0)
        features["has_suspicious_plugins"] = float(session_data.get("suspicious_plugins", False))
        
        # Security features
        features["fingerprint_evasion_detected"] = float(session_data.get("evasion_detected", False))
        features["automation_detected"] = float(session_data.get("automation_detected", False))
        
        return features
    
    async def _extract_network_features(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract network-related features"""
        features = {}
        
        # IP characteristics
        ip_info = session_data.get("ip_info", {})
        features["is_known_ip"] = float(session_data.get("is_known_ip", False))
        features["ip_reputation_score"] = ip_info.get("reputation", 0.5)
        features["is_datacenter_ip"] = float(ip_info.get("is_datacenter", False))
        
        # Network behavior
        features["connection_stability"] = session_data.get("connection_stability", 1.0)
        features["latency_ms"] = session_data.get("latency", 0)
        features["bandwidth_mbps"] = session_data.get("bandwidth", 0)
        
        # Traffic patterns
        features["request_rate"] = session_data.get("request_rate", 0)
        features["unusual_traffic_pattern"] = float(session_data.get("unusual_traffic", False))
        
        return features
    
    async def _extract_temporal_features(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract temporal features"""
        features = {}
        
        now = datetime.utcnow()
        
        # Time-based features
        features["hour_of_day"] = now.hour
        features["day_of_week"] = now.weekday()
        features["is_weekend"] = float(now.weekday() >= 5)
        features["is_business_hours"] = float(9 <= now.hour <= 17)
        features["is_unusual_time"] = float(session_data.get("unusual_time", False))
        
        # Account timing
        features["account_age_days"] = session_data.get("account_age_days", 0)
        features["time_since_last_activity"] = session_data.get("time_since_last_activity", 0)
        
        return features
    
    async def _extract_transaction_features(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract transaction-related features"""
        features = {}
        
        # Transaction patterns
        features["transaction_count"] = session_data.get("transaction_count", 0)
        features["transaction_value"] = session_data.get("transaction_value", 0)
        features["unusual_transaction_pattern"] = float(session_data.get("unusual_transactions", False))
        
        # Financial risk
        features["chargeback_history"] = session_data.get("chargeback_count", 0)
        features["fraud_score"] = session_data.get("fraud_score", 0)
        
        return features
    
    async def _extract_reputation_features(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Extract reputation-related features"""
        features = {}
        
        # User reputation
        features["trust_score"] = session_data.get("trust_score", 0.5)
        features["reputation_score"] = session_data.get("reputation_score", 0.5)
        features["community_reports"] = session_data.get("community_reports", 0)
        
        # Historical behavior
        features["policy_violations"] = session_data.get("policy_violations", 0)
        features["security_incidents"] = session_data.get("security_incidents", 0)
        features["positive_feedback_ratio"] = session_data.get("positive_feedback", 0.5)
        
        return features
    
    async def _calculate_risk_factors(
        self,
        user_id: str,
        features: Dict[str, Any],
        risk_profile: UserRiskProfile
    ) -> List[RiskFactor]:
        """Calculate individual risk factors"""
        risk_factors = []
        
        for category_name, category_features in features.items():
            category = RiskCategory(category_name)
            
            for feature_name, feature_value in category_features.items():
                if isinstance(feature_value, (int, float)):
                    # Calculate risk factor
                    risk_value = self._calculate_feature_risk(
                        category, feature_name, feature_value, risk_profile
                    )
                    
                    if risk_value > 0.1:  # Only include significant risk factors
                        risk_factors.append(RiskFactor(
                            factor_id=f"{category_name}_{feature_name}",
                            category=category,
                            name=feature_name,
                            description=f"Risk from {feature_name} in {category_name}",
                            value=risk_value,
                            weight=self.config["feature_weights"].get(category_name, 0.1),
                            confidence=0.8,  # Default confidence
                            evidence={"feature_value": feature_value},
                            timestamp=datetime.utcnow()
                        ))
        
        return risk_factors
    
    async def _detect_threat_indicators(
        self,
        user_id: str,
        features: Dict[str, Any],
        session_data: Dict[str, Any]
    ) -> List[ThreatIndicator]:
        """Detect threat indicators based on features"""
        threat_indicators = []
        
        # Check for brute force attempts
        auth_features = features.get("authentication", {})
        if auth_features.get("failed_login_count", 0) > 5:
            threat_indicators.append(ThreatIndicator(
                indicator_id=f"brute_force_{user_id}_{int(datetime.utcnow().timestamp())}",
                threat_type=ThreatType.BRUTE_FORCE,
                severity=RiskLevel.HIGH,
                confidence=0.9,
                description="Multiple failed login attempts detected",
                iocs=["excessive_failed_logins"],
                ttps=["T1110.001"],
                evidence={"failed_count": auth_features["failed_login_count"]},
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow()
            ))
        
        # Check for credential stuffing
        if (auth_features.get("login_success_rate", 1.0) < 0.3 and
            session_data.get("rapid_login_attempts", False)):
            threat_indicators.append(ThreatIndicator(
                indicator_id=f"credential_stuffing_{user_id}_{int(datetime.utcnow().timestamp())}",
                threat_type=ThreatType.CREDENTIAL_STUFFING,
                severity=RiskLevel.HIGH,
                confidence=0.85,
                description="Potential credential stuffing attack",
                iocs=["low_success_rate", "rapid_attempts"],
                ttps=["T1110.004"],
                evidence={
                    "success_rate": auth_features["login_success_rate"],
                    "rapid_attempts": True
                },
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow()
            ))
        
        # Check for account takeover
        location_features = features.get("location", {})
        behavioral_features = features.get("behavioral", {})
        
        if (location_features.get("distance_from_home", 0) > 1000 and
            behavioral_features.get("typing_speed", 0) > 0 and
            abs(behavioral_features["typing_speed"] - session_data.get("normal_typing_speed", 50)) > 20):
            threat_indicators.append(ThreatIndicator(
                indicator_id=f"account_takeover_{user_id}_{int(datetime.utcnow().timestamp())}",
                threat_type=ThreatType.ACCOUNT_TAKEOVER,
                severity=RiskLevel.CRITICAL,
                confidence=0.8,
                description="Potential account takeover - unusual location and behavior",
                iocs=["unusual_location", "behavioral_change"],
                ttps=["T1078"],
                evidence={
                    "distance": location_features["distance_from_home"],
                    "typing_change": abs(behavioral_features["typing_speed"] - 
                                       session_data.get("normal_typing_speed", 50))
                },
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow()
            ))
        
        # Check for automated attacks
        device_features = features.get("device", {})
        if device_features.get("automation_detected", False):
            threat_indicators.append(ThreatIndicator(
                indicator_id=f"automation_{user_id}_{int(datetime.utcnow().timestamp())}",
                threat_type=ThreatType.AUTOMATED_ATTACK,
                severity=RiskLevel.MEDIUM,
                confidence=0.9,
                description="Automated behavior detected",
                iocs=["bot_behavior"],
                ttps=["T1566"],
                evidence={"automation_confidence": device_features.get("automation_confidence", 0.8)},
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow()
            ))
        
        return threat_indicators
    
    def _calculate_category_risks(self, risk_factors: List[RiskFactor]) -> Dict[RiskCategory, float]:
        """Calculate risk scores by category"""
        category_risks = {}
        
        # Group risk factors by category
        category_factors = defaultdict(list)
        for factor in risk_factors:
            category_factors[factor.category].append(factor)
        
        # Calculate weighted risk for each category
        for category, factors in category_factors.items():
            if factors:
                # Weighted average of risk values
                total_weighted_risk = sum(f.value * f.weight * f.confidence for f in factors)
                total_weight = sum(f.weight * f.confidence for f in factors)
                
                if total_weight > 0:
                    category_risks[category] = min(5.0, total_weighted_risk / total_weight)
                else:
                    category_risks[category] = 0.0
            else:
                category_risks[category] = 0.0
        
        return category_risks
    
    async def _ml_risk_assessment(
        self,
        features: Dict[str, Any],
        risk_profile: UserRiskProfile
    ) -> Tuple[float, float]:
        """ML-based risk assessment"""
        if not self.models_trained:
            # Return baseline risk if models not trained
            return 2.0, 0.5
        
        try:
            # Flatten features
            feature_vector = self._flatten_features(features)
            feature_array = np.array(feature_vector).reshape(1, -1)
            
            # Scale features
            feature_scaled = self.scaler.transform(feature_array)
            
            # Select features
            feature_selected = self.feature_selector.transform(feature_scaled)
            
            # Predict risk score
            risk_probabilities = self.calibrated_classifier.predict_proba(feature_selected)[0]
            risk_score = np.sum(risk_probabilities * np.arange(1, len(risk_probabilities) + 1))
            
            # Calculate confidence
            confidence = np.max(risk_probabilities)
            
            return risk_score, confidence
            
        except Exception as e:
            self.logger.warning(f"ML risk assessment failed: {e}")
            return 2.0, 0.5
    
    def _combine_risk_scores(
        self,
        risk_factors: List[RiskFactor],
        threat_indicators: List[ThreatIndicator],
        ml_risk_score: float,
        ml_confidence: float
    ) -> Tuple[float, float]:
        """Combine different risk scores into overall score"""
        scores = []
        confidences = []
        
        # Factor-based risk
        if risk_factors:
            factor_score = np.mean([f.value for f in risk_factors])
            factor_confidence = np.mean([f.confidence for f in risk_factors])
            scores.append(factor_score)
            confidences.append(factor_confidence)
        
        # Threat-based risk
        if threat_indicators:
            threat_score = np.mean([t.severity.value for t in threat_indicators])
            threat_confidence = np.mean([t.confidence for t in threat_indicators])
            scores.append(threat_score)
            confidences.append(threat_confidence)
        
        # ML-based risk
        scores.append(ml_risk_score)
        confidences.append(ml_confidence)
        
        # Weighted combination
        if scores:
            weights = [0.4, 0.4, 0.2] if len(scores) == 3 else [0.5, 0.5] if len(scores) == 2 else [1.0]
            overall_score = np.average(scores, weights=weights[:len(scores)])
            overall_confidence = np.average(confidences, weights=weights[:len(confidences)])
        else:
            overall_score = 2.0  # Neutral risk
            overall_confidence = 0.5
        
        return min(5.0, overall_score), min(1.0, overall_confidence)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score"""
        if risk_score >= self.risk_thresholds.get("critical", 4.5):
            return RiskLevel.CRITICAL
        elif risk_score >= self.risk_thresholds.get("high", 3.5):
            return RiskLevel.HIGH
        elif risk_score >= self.risk_thresholds.get("medium", 2.5):
            return RiskLevel.MEDIUM
        elif risk_score >= self.risk_thresholds.get("low", 1.5):
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        risk_factors: List[RiskFactor],
        threat_indicators: List[ThreatIndicator]
    ) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Immediately suspend account access",
                "Require emergency verification",
                "Initiate security incident response",
                "Monitor for data exfiltration"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Require additional authentication factors",
                "Limit access to sensitive operations",
                "Monitor session closely",
                "Send security alert to user"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Request additional verification",
                "Monitor for anomalies",
                "Consider device verification"
            ])
        
        # Add specific recommendations based on threat indicators
        threat_types = {indicator.threat_type for indicator in threat_indicators}
        
        if ThreatType.BRUTE_FORCE in threat_types:
            recommendations.append("Implement temporary account lockout")
        
        if ThreatType.ACCOUNT_TAKEOVER in threat_types:
            recommendations.append("Verify user identity through secondary channel")
        
        if ThreatType.AUTOMATED_ATTACK in threat_types:
            recommendations.append("Deploy CAPTCHA challenge")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _suggest_security_controls(
        self,
        risk_level: RiskLevel,
        category_risks: Dict[RiskCategory, float]
    ) -> List[str]:
        """Suggest appropriate security controls"""
        controls = []
        
        # Base controls by risk level
        if risk_level.value >= 4:
            controls.extend([
                "Multi-factor authentication",
                "Session monitoring",
                "Behavioral analysis",
                "Device verification"
            ])
        elif risk_level.value >= 3:
            controls.extend([
                "Additional verification",
                "Rate limiting",
                "Geolocation checks"
            ])
        
        # Category-specific controls
        for category, risk_score in category_risks.items():
            if risk_score >= 3.0:
                if category == RiskCategory.LOCATION:
                    controls.append("Geofencing enforcement")
                elif category == RiskCategory.DEVICE:
                    controls.append("Device fingerprinting validation")
                elif category == RiskCategory.BEHAVIORAL:
                    controls.append("Continuous authentication")
                elif category == RiskCategory.NETWORK:
                    controls.append("IP reputation checking")
        
        return list(set(controls))
    
    def _determine_monitoring_requirements(
        self,
        risk_level: RiskLevel,
        threat_indicators: List[ThreatIndicator]
    ) -> List[str]:
        """Determine monitoring requirements"""
        monitoring = []
        
        if risk_level.value >= 4:
            monitoring.extend([
                "Real-time session monitoring",
                "Continuous behavioral analysis",
                "Network traffic analysis",
                "Security event correlation"
            ])
        elif risk_level.value >= 3:
            monitoring.extend([
                "Enhanced logging",
                "Anomaly detection",
                "Periodic verification"
            ])
        
        # Threat-specific monitoring
        threat_types = {indicator.threat_type for indicator in threat_indicators}
        
        if ThreatType.ACCOUNT_TAKEOVER in threat_types:
            monitoring.append("Identity verification monitoring")
        
        if ThreatType.AUTOMATED_ATTACK in threat_types:
            monitoring.append("Bot detection monitoring")
        
        return list(set(monitoring))
    
    # Helper methods
    
    def _calculate_feature_risk(
        self,
        category: RiskCategory,
        feature_name: str,
        feature_value: float,
        risk_profile: UserRiskProfile
    ) -> float:
        """Calculate risk value for a specific feature"""
        # Simplified risk calculation - in production, use more sophisticated models
        
        # Normalize feature value (0-1 scale)
        normalized_value = min(1.0, abs(feature_value) / 100.0)
        
        # Category-specific risk multipliers
        category_multipliers = {
            RiskCategory.AUTHENTICATION: 2.0,
            RiskCategory.BEHAVIORAL: 1.5,
            RiskCategory.LOCATION: 1.8,
            RiskCategory.DEVICE: 1.3,
            RiskCategory.NETWORK: 1.2,
            RiskCategory.TEMPORAL: 1.0,
            RiskCategory.TRANSACTION: 2.2,
            RiskCategory.REPUTATION: 1.7
        }
        
        multiplier = category_multipliers.get(category, 1.0)
        
        # Calculate risk (0-5 scale)
        risk_value = normalized_value * multiplier
        
        return min(5.0, risk_value)
    
    def _flatten_features(self, features: Dict[str, Any]) -> List[float]:
        """Flatten nested features for ML processing"""
        flattened = []
        
        for category, cat_features in features.items():
            for key, value in cat_features.items():
                if isinstance(value, (int, float)):
                    flattened.append(float(value))
                elif isinstance(value, bool):
                    flattened.append(float(value))
        
        return flattened
    
    def _prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data from historical assessments"""
        training_data = []
        
        for assessment in self.assessment_history:
            # Convert assessment to training sample
            sample = {
                "features": self._extract_features_from_assessment(assessment),
                "risk_level": assessment.overall_risk_level.value,
                "risk_score": assessment.overall_risk_score
            }
            training_data.append(sample)
        
        return training_data
    
    def _prepare_feature_matrix(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare feature matrix and labels for ML training"""
        features = []
        labels = []
        
        for sample in training_data:
            features.append(sample["features"])
            labels.append(sample["risk_level"])
        
        return np.array(features), np.array(labels)
    
    def _extract_features_from_assessment(self, assessment: RiskAssessment) -> List[float]:
        """Extract features from assessment for training"""
        # Simplified feature extraction
        features = []
        
        # Add risk factor values
        for factor in assessment.risk_factors:
            features.append(factor.value)
        
        # Pad or truncate to fixed size
        fixed_size = 50
        if len(features) < fixed_size:
            features.extend([0.0] * (fixed_size - len(features)))
        else:
            features = features[:fixed_size]
        
        return features
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained models"""
        if hasattr(self.risk_classifier, 'feature_importances_'):
            importances = self.risk_classifier.feature_importances_
            feature_names = [f"feature_{i}" for i in range(len(importances))]
            return dict(zip(feature_names, importances.tolist()))
        return {}
    
    def _analyze_severity_distribution(self, indicators: List[ThreatIndicator]) -> Dict[str, int]:
        """Analyze distribution of threat severities"""
        distribution = defaultdict(int)
        for indicator in indicators:
            distribution[indicator.severity.name] += 1
        return dict(distribution)
    
    async def _update_risk_profile(self, profile: UserRiskProfile, assessment: RiskAssessment):
        """Update user risk profile with new assessment"""
        profile.updated_at = assessment.timestamp
        
        # Update average risk score
        alpha = 0.1  # Learning rate
        profile.avg_risk_score = (1 - alpha) * profile.avg_risk_score + alpha * assessment.overall_risk_score
        
        # Update risk variance
        variance_update = (assessment.overall_risk_score - profile.avg_risk_score) ** 2
        profile.risk_score_variance = (1 - alpha) * profile.risk_score_variance + alpha * variance_update
        
        # Update trust score based on assessment
        if assessment.overall_risk_level.value <= 2:
            profile.trust_score = min(1.0, profile.trust_score + 0.05)
        elif assessment.overall_risk_level.value >= 4:
            profile.trust_score = max(0.0, profile.trust_score - 0.1)


# Export main classes
__all__ = [
    "RiskAssessmentEngine",
    "RiskLevel",
    "RiskCategory", 
    "ThreatType",
    "RiskFactor",
    "ThreatIndicator",
    "RiskAssessment",
    "UserRiskProfile"
]