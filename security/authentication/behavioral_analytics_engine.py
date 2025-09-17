#!/usr/bin/env python3
"""
🔒 Behavioral Analytics Engine - ML Security Intelligence
==========================================================

Advanced behavioral analytics engine with ML-powered user profiling,
anomaly detection, and real-time risk assessment for authentication security.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: ML + Security + Backend + Analytics
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
from collections import defaultdict, deque
import hashlib
import geoip2.database
import user_agents

# ML and analytics imports
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import pandas as pd
from scipy import stats


class BehaviorAnomalyType(Enum):
    """Types of behavioral anomalies"""
    UNUSUAL_LOCATION = "unusual_location"
    UNUSUAL_TIME = "unusual_time"
    UNUSUAL_DEVICE = "unusual_device"
    RAPID_ACTIONS = "rapid_actions"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    VELOCITY_ANOMALY = "velocity_anomaly"
    SESSION_ANOMALY = "session_anomaly"
    TYPING_PATTERN = "typing_pattern"
    MOUSE_BEHAVIOR = "mouse_behavior"
    NETWORK_ANOMALY = "network_anomaly"


class RiskLevel(Enum):
    """Risk assessment levels"""
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class BehaviorMetrics:
    """User behavior metrics"""
    user_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    location: Optional[Dict[str, Any]]
    session_duration: float
    action_count: int
    typing_speed: Optional[float]
    mouse_velocity: Optional[float]
    click_patterns: Optional[List[Dict]]
    keystroke_dynamics: Optional[Dict]
    device_fingerprint: str
    network_metrics: Dict[str, Any]


@dataclass
class UserProfile:
    """Comprehensive user behavioral profile"""
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Location patterns
    common_locations: List[Dict[str, Any]]
    location_variance: float
    
    # Time patterns
    active_hours: List[int]  # Hours of day (0-23)
    active_days: List[int]   # Days of week (0-6)
    session_patterns: Dict[str, Any]
    
    # Device patterns
    known_devices: Set[str]
    device_consistency: float
    
    # Behavioral patterns
    typing_profile: Dict[str, float]
    mouse_profile: Dict[str, float]
    interaction_patterns: Dict[str, Any]
    
    # Risk factors
    risk_score: float
    anomaly_history: List[Dict[str, Any]]
    trust_level: float


@dataclass
class AnomalyResult:
    """Behavioral anomaly detection result"""
    anomaly_type: BehaviorAnomalyType
    risk_level: RiskLevel
    confidence: float
    description: str
    evidence: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment"""
    user_id: str
    overall_risk: RiskLevel
    risk_score: float
    anomalies: List[AnomalyResult]
    contributing_factors: List[str]
    mitigation_actions: List[str]
    expires_at: datetime
    
    
class BehavioralAnalyticsEngine:
    """
    🔒 Enterprise Behavioral Analytics Engine
    
    ML-powered behavioral analysis for advanced security intelligence,
    real-time anomaly detection, and adaptive user profiling.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize behavioral analytics engine"""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "security/config/behavioral_config.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # ML Models
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.risk_classifier = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            max_depth=10
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Clustering for user profiling
        self.clustering_model = DBSCAN(eps=0.5, min_samples=5)
        self.pca = PCA(n_components=10)
        
        # Data storage
        self.user_profiles: Dict[str, UserProfile] = {}
        self.behavior_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        
        # Real-time tracking
        self.active_sessions: Dict[str, Dict] = {}
        self.recent_actions: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        
        # Models training status
        self.models_trained = False
        
        # Initialize GeoIP database (mock path)
        self.geoip_reader = None
        self._initialize_geoip()
        
        # Initialize feature extractors
        self.feature_extractors = {
            'temporal': self._extract_temporal_features,
            'spatial': self._extract_spatial_features,
            'device': self._extract_device_features,
            'behavioral': self._extract_behavioral_features,
            'network': self._extract_network_features
        }
    
    async def analyze_user_behavior(
        self, 
        user_id: str,
        behavior_data: BehaviorMetrics
    ) -> Dict[str, Any]:
        """
        Analyze user behavior and detect patterns
        
        Args:
            user_id: User identifier
            behavior_data: Current behavior metrics
            
        Returns:
            Comprehensive behavior analysis
        """
        try:
            # Store behavior data
            self.behavior_history[user_id].append(behavior_data)
            
            # Extract features
            features = await self._extract_comprehensive_features(
                user_id, behavior_data
            )
            
            # Get or create user profile
            profile = await self._get_or_create_profile(user_id)
            
            # Update profile with new data
            await self._update_user_profile(profile, behavior_data, features)
            
            # Detect anomalies
            anomalies = await self.detect_behavioral_anomalies(
                user_id, behavior_data, features
            )
            
            # Calculate risk score
            risk_assessment = await self.calculate_risk_score(
                user_id, anomalies, features
            )
            
            # Update session tracking
            await self._update_session_tracking(user_id, behavior_data)
            
            return {
                "user_id": user_id,
                "timestamp": behavior_data.timestamp.isoformat(),
                "profile_updated": True,
                "anomalies": [asdict(a) for a in anomalies],
                "risk_assessment": asdict(risk_assessment),
                "features": features,
                "profile_summary": {
                    "trust_level": profile.trust_level,
                    "risk_score": profile.risk_score,
                    "known_devices": len(profile.known_devices),
                    "location_variance": profile.location_variance
                }
            }
            
        except Exception as e:
            self.logger.error(f"Behavior analysis error: {e}")
            raise
    
    async def detect_behavioral_anomalies(
        self,
        user_id: str,
        current_data: BehaviorMetrics,
        features: Dict[str, Any]
    ) -> List[AnomalyResult]:
        """
        Detect behavioral anomalies using ML models
        
        Args:
            user_id: User identifier
            current_data: Current behavior metrics
            features: Extracted features
            
        Returns:
            List of detected anomalies
        """
        try:
            anomalies = []
            
            # Get user profile
            profile = self.user_profiles.get(user_id)
            if not profile:
                return anomalies  # No baseline for new users
            
            # Location anomaly detection
            location_anomaly = await self._detect_location_anomaly(
                profile, current_data
            )
            if location_anomaly:
                anomalies.append(location_anomaly)
            
            # Time-based anomaly detection
            time_anomaly = await self._detect_time_anomaly(
                profile, current_data
            )
            if time_anomaly:
                anomalies.append(time_anomaly)
            
            # Device anomaly detection
            device_anomaly = await self._detect_device_anomaly(
                profile, current_data
            )
            if device_anomaly:
                anomalies.append(device_anomaly)
            
            # Velocity anomaly detection
            velocity_anomaly = await self._detect_velocity_anomaly(
                user_id, current_data
            )
            if velocity_anomaly:
                anomalies.append(velocity_anomaly)
            
            # Behavioral pattern anomalies
            pattern_anomalies = await self._detect_pattern_anomalies(
                profile, current_data, features
            )
            anomalies.extend(pattern_anomalies)
            
            # ML-based anomaly detection
            ml_anomalies = await self._ml_anomaly_detection(
                user_id, features
            )
            anomalies.extend(ml_anomalies)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection error: {e}")
            return []
    
    async def create_user_profile(
        self,
        user_id: str,
        initial_data: Optional[List[BehaviorMetrics]] = None
    ) -> UserProfile:
        """
        Create comprehensive user behavioral profile
        
        Args:
            user_id: User identifier
            initial_data: Optional initial behavior data
            
        Returns:
            Created user profile
        """
        try:
            # Get historical data
            history = list(self.behavior_history.get(user_id, []))
            if initial_data:
                history.extend(initial_data)
            
            if not history:
                # Create minimal profile for new user
                profile = UserProfile(
                    user_id=user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    common_locations=[],
                    location_variance=0.0,
                    active_hours=[],
                    active_days=[],
                    session_patterns={},
                    known_devices=set(),
                    device_consistency=0.0,
                    typing_profile={},
                    mouse_profile={},
                    interaction_patterns={},
                    risk_score=0.5,  # Neutral risk for new users
                    anomaly_history=[],
                    trust_level=0.3  # Low initial trust
                )
            else:
                # Analyze historical data
                profile = await self._analyze_behavior_history(user_id, history)
            
            self.user_profiles[user_id] = profile
            return profile
            
        except Exception as e:
            self.logger.error(f"Profile creation error: {e}")
            raise
    
    async def calculate_risk_score(
        self,
        user_id: str,
        anomalies: List[AnomalyResult],
        features: Dict[str, Any]
    ) -> RiskAssessment:
        """
        Calculate comprehensive risk score
        
        Args:
            user_id: User identifier
            anomalies: Detected anomalies
            features: Behavior features
            
        Returns:
            Risk assessment result
        """
        try:
            # Base risk from anomalies
            anomaly_risk = sum(a.risk_level.value for a in anomalies)
            max_possible_risk = len(anomalies) * 5  # Max risk level
            
            if max_possible_risk > 0:
                normalized_anomaly_risk = anomaly_risk / max_possible_risk
            else:
                normalized_anomaly_risk = 0.0
            
            # Profile-based risk factors
            profile = self.user_profiles.get(user_id)
            profile_risk = 0.0
            
            if profile:
                # Location variance risk
                if profile.location_variance > 1000:  # km
                    profile_risk += 0.2
                
                # Device consistency risk
                if profile.device_consistency < 0.5:
                    profile_risk += 0.3
                
                # Trust level impact
                trust_impact = (1.0 - profile.trust_level) * 0.3
                profile_risk += trust_impact
            
            # Feature-based risk
            feature_risk = await self._calculate_feature_risk(features)
            
            # Combine risk factors
            overall_risk_score = min(1.0, (
                normalized_anomaly_risk * 0.5 +
                profile_risk * 0.3 +
                feature_risk * 0.2
            ))
            
            # Determine risk level
            if overall_risk_score >= 0.8:
                risk_level = RiskLevel.CRITICAL
            elif overall_risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif overall_risk_score >= 0.4:
                risk_level = RiskLevel.MEDIUM
            elif overall_risk_score >= 0.2:
                risk_level = RiskLevel.LOW
            else:
                risk_level = RiskLevel.MINIMAL
            
            # Generate contributing factors
            contributing_factors = []
            if anomalies:
                contributing_factors.append(f"{len(anomalies)} behavioral anomalies detected")
            if profile and profile.location_variance > 1000:
                contributing_factors.append("High location variance")
            if profile and profile.device_consistency < 0.5:
                contributing_factors.append("Low device consistency")
            
            # Generate mitigation actions
            mitigation_actions = []
            if risk_level.value >= 4:
                mitigation_actions.extend([
                    "Require additional authentication factors",
                    "Monitor session closely",
                    "Limit access to sensitive operations"
                ])
            elif risk_level.value >= 3:
                mitigation_actions.extend([
                    "Request additional verification",
                    "Monitor for further anomalies"
                ])
            
            return RiskAssessment(
                user_id=user_id,
                overall_risk=risk_level,
                risk_score=overall_risk_score,
                anomalies=anomalies,
                contributing_factors=contributing_factors,
                mitigation_actions=mitigation_actions,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
        except Exception as e:
            self.logger.error(f"Risk calculation error: {e}")
            raise
    
    # Private methods for feature extraction
    
    async def _extract_comprehensive_features(
        self,
        user_id: str,
        behavior_data: BehaviorMetrics
    ) -> Dict[str, Any]:
        """Extract comprehensive behavioral features"""
        features = {}
        
        for feature_type, extractor in self.feature_extractors.items():
            try:
                features[feature_type] = await extractor(user_id, behavior_data)
            except Exception as e:
                self.logger.warning(f"Feature extraction failed for {feature_type}: {e}")
                features[feature_type] = {}
        
        return features
    
    async def _extract_temporal_features(
        self,
        user_id: str,
        behavior_data: BehaviorMetrics
    ) -> Dict[str, Any]:
        """Extract temporal behavior features"""
        timestamp = behavior_data.timestamp
        
        return {
            "hour_of_day": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "is_weekend": timestamp.weekday() >= 5,
            "is_business_hours": 9 <= timestamp.hour <= 17,
            "session_duration": behavior_data.session_duration,
            "time_since_last_login": await self._get_time_since_last_login(user_id)
        }
    
    async def _extract_spatial_features(
        self,
        user_id: str,
        behavior_data: BehaviorMetrics
    ) -> Dict[str, Any]:
        """Extract spatial/location features"""
        location = behavior_data.location or {}
        
        features = {
            "has_location": behavior_data.location is not None,
            "latitude": location.get("latitude", 0),
            "longitude": location.get("longitude", 0),
            "country": location.get("country", ""),
            "city": location.get("city", ""),
            "is_vpn": location.get("is_vpn", False),
            "is_proxy": location.get("is_proxy", False)
        }
        
        # Calculate distance from common locations
        profile = self.user_profiles.get(user_id)
        if profile and profile.common_locations:
            distances = []
            for common_loc in profile.common_locations:
                distance = self._calculate_distance(
                    location.get("latitude", 0),
                    location.get("longitude", 0),
                    common_loc.get("latitude", 0),
                    common_loc.get("longitude", 0)
                )
                distances.append(distance)
            
            features["min_distance_to_common"] = min(distances) if distances else 0
            features["avg_distance_to_common"] = np.mean(distances) if distances else 0
        
        return features
    
    async def _extract_device_features(
        self,
        user_id: str,
        behavior_data: BehaviorMetrics
    ) -> Dict[str, Any]:
        """Extract device and browser features"""
        # Parse user agent
        user_agent = user_agents.parse(behavior_data.user_agent)
        
        return {
            "browser_family": user_agent.browser.family,
            "browser_version": user_agent.browser.version_string,
            "os_family": user_agent.os.family,
            "os_version": user_agent.os.version_string,
            "device_family": user_agent.device.family,
            "is_mobile": user_agent.is_mobile,
            "is_tablet": user_agent.is_tablet,
            "is_pc": user_agent.is_pc,
            "device_fingerprint": behavior_data.device_fingerprint,
            "is_known_device": await self._is_known_device(user_id, behavior_data.device_fingerprint)
        }
    
    async def _extract_behavioral_features(
        self,
        user_id: str,
        behavior_data: BehaviorMetrics
    ) -> Dict[str, Any]:
        """Extract behavioral interaction features"""
        features = {
            "action_count": behavior_data.action_count,
            "typing_speed": behavior_data.typing_speed or 0,
            "mouse_velocity": behavior_data.mouse_velocity or 0,
            "has_keystroke_dynamics": behavior_data.keystroke_dynamics is not None,
            "has_mouse_patterns": behavior_data.click_patterns is not None
        }
        
        # Add keystroke dynamics features
        if behavior_data.keystroke_dynamics:
            kd = behavior_data.keystroke_dynamics
            features.update({
                "avg_dwell_time": kd.get("avg_dwell_time", 0),
                "avg_flight_time": kd.get("avg_flight_time", 0),
                "typing_rhythm_variance": kd.get("rhythm_variance", 0)
            })
        
        # Add mouse behavior features
        if behavior_data.click_patterns:
            clicks = behavior_data.click_patterns
            features.update({
                "click_count": len(clicks),
                "avg_click_interval": np.mean([c.get("interval", 0) for c in clicks]) if clicks else 0,
                "click_pattern_variance": np.var([c.get("interval", 0) for c in clicks]) if clicks else 0
            })
        
        return features
    
    async def _extract_network_features(
        self,
        user_id: str,
        behavior_data: BehaviorMetrics
    ) -> Dict[str, Any]:
        """Extract network-based features"""
        ip_address = behavior_data.ip_address
        network_metrics = behavior_data.network_metrics
        
        features = {
            "ip_address_hash": hashlib.sha256(ip_address.encode()).hexdigest()[:16],
            "is_known_ip": await self._is_known_ip(user_id, ip_address),
            "latency": network_metrics.get("latency", 0),
            "bandwidth": network_metrics.get("bandwidth", 0),
            "connection_type": network_metrics.get("connection_type", "unknown")
        }
        
        # Analyze IP geolocation
        if self.geoip_reader:
            try:
                response = self.geoip_reader.city(ip_address)
                features.update({
                    "geoip_country": response.country.iso_code,
                    "geoip_city": response.city.name,
                    "geoip_accuracy": response.location.accuracy_radius
                })
            except Exception as e:
                self.logger.warning(f"GeoIP lookup failed: {e}")
        
        return features
    
    # Anomaly detection methods
    
    async def _detect_location_anomaly(
        self,
        profile: UserProfile,
        current_data: BehaviorMetrics
    ) -> Optional[AnomalyResult]:
        """Detect location-based anomalies"""
        if not current_data.location or not profile.common_locations:
            return None
        
        current_lat = current_data.location.get("latitude", 0)
        current_lon = current_data.location.get("longitude", 0)
        
        # Calculate distances to common locations
        distances = []
        for location in profile.common_locations:
            distance = self._calculate_distance(
                current_lat, current_lon,
                location.get("latitude", 0),
                location.get("longitude", 0)
            )
            distances.append(distance)
        
        min_distance = min(distances) if distances else float('inf')
        
        # Anomaly threshold based on profile variance
        threshold = max(100, profile.location_variance * 2)  # km
        
        if min_distance > threshold:
            risk_level = RiskLevel.HIGH if min_distance > threshold * 2 else RiskLevel.MEDIUM
            
            return AnomalyResult(
                anomaly_type=BehaviorAnomalyType.UNUSUAL_LOCATION,
                risk_level=risk_level,
                confidence=min(1.0, min_distance / threshold),
                description=f"Login from unusual location: {min_distance:.1f}km from nearest common location",
                evidence={
                    "current_location": current_data.location,
                    "distance_from_common": min_distance,
                    "threshold": threshold
                },
                recommendations=[
                    "Verify user identity",
                    "Check for VPN/proxy usage",
                    "Monitor subsequent activities"
                ],
                timestamp=datetime.utcnow()
            )
        
        return None
    
    async def _detect_time_anomaly(
        self,
        profile: UserProfile,
        current_data: BehaviorMetrics
    ) -> Optional[AnomalyResult]:
        """Detect time-based anomalies"""
        if not profile.active_hours:
            return None
        
        current_hour = current_data.timestamp.hour
        current_day = current_data.timestamp.weekday()
        
        # Check if current time is unusual
        hour_unusual = current_hour not in profile.active_hours
        day_unusual = current_day not in profile.active_days
        
        if hour_unusual or day_unusual:
            risk_level = RiskLevel.MEDIUM if hour_unusual and day_unusual else RiskLevel.LOW
            
            return AnomalyResult(
                anomaly_type=BehaviorAnomalyType.UNUSUAL_TIME,
                risk_level=risk_level,
                confidence=0.7 if hour_unusual and day_unusual else 0.5,
                description=f"Login at unusual time: {current_hour}:00 on day {current_day}",
                evidence={
                    "current_hour": current_hour,
                    "current_day": current_day,
                    "typical_hours": profile.active_hours,
                    "typical_days": profile.active_days
                },
                recommendations=[
                    "Verify user identity",
                    "Monitor session activity"
                ],
                timestamp=datetime.utcnow()
            )
        
        return None
    
    async def _detect_device_anomaly(
        self,
        profile: UserProfile,
        current_data: BehaviorMetrics
    ) -> Optional[AnomalyResult]:
        """Detect device-based anomalies"""
        device_fingerprint = current_data.device_fingerprint
        
        if device_fingerprint not in profile.known_devices:
            return AnomalyResult(
                anomaly_type=BehaviorAnomalyType.UNUSUAL_DEVICE,
                risk_level=RiskLevel.MEDIUM,
                confidence=0.8,
                description="Login from unrecognized device",
                evidence={
                    "device_fingerprint": device_fingerprint,
                    "user_agent": current_data.user_agent,
                    "known_devices_count": len(profile.known_devices)
                },
                recommendations=[
                    "Require device verification",
                    "Send security notification",
                    "Add to trusted devices after verification"
                ],
                timestamp=datetime.utcnow()
            )
        
        return None
    
    async def _detect_velocity_anomaly(
        self,
        user_id: str,
        current_data: BehaviorMetrics
    ) -> Optional[AnomalyResult]:
        """Detect impossible travel velocity"""
        history = list(self.behavior_history.get(user_id, []))
        
        if len(history) < 2:
            return None
        
        # Get last location
        last_data = None
        for data in reversed(history[:-1]):  # Exclude current
            if data.location:
                last_data = data
                break
        
        if not last_data or not current_data.location:
            return None
        
        # Calculate distance and time difference
        distance = self._calculate_distance(
            last_data.location["latitude"],
            last_data.location["longitude"],
            current_data.location["latitude"],
            current_data.location["longitude"]
        )
        
        time_diff = (current_data.timestamp - last_data.timestamp).total_seconds() / 3600  # hours
        
        if time_diff > 0:
            velocity = distance / time_diff  # km/h
            
            # Impossible travel threshold (commercial flight speed)
            max_velocity = 900  # km/h
            
            if velocity > max_velocity:
                return AnomalyResult(
                    anomaly_type=BehaviorAnomalyType.VELOCITY_ANOMALY,
                    risk_level=RiskLevel.HIGH,
                    confidence=min(1.0, velocity / max_velocity),
                    description=f"Impossible travel velocity: {velocity:.1f} km/h",
                    evidence={
                        "calculated_velocity": velocity,
                        "distance": distance,
                        "time_difference_hours": time_diff,
                        "last_location": last_data.location,
                        "current_location": current_data.location
                    },
                    recommendations=[
                        "Verify user identity immediately",
                        "Check for account compromise",
                        "Review recent activities"
                    ],
                    timestamp=datetime.utcnow()
                )
        
        return None
    
    async def _detect_pattern_anomalies(
        self,
        profile: UserProfile,
        current_data: BehaviorMetrics,
        features: Dict[str, Any]
    ) -> List[AnomalyResult]:
        """Detect behavioral pattern anomalies"""
        anomalies = []
        
        # Typing pattern anomaly
        if (current_data.typing_speed and profile.typing_profile and
            "avg_typing_speed" in profile.typing_profile):
            
            avg_speed = profile.typing_profile["avg_typing_speed"]
            speed_variance = profile.typing_profile.get("typing_speed_variance", 10)
            
            if abs(current_data.typing_speed - avg_speed) > 2 * speed_variance:
                anomalies.append(AnomalyResult(
                    anomaly_type=BehaviorAnomalyType.TYPING_PATTERN,
                    risk_level=RiskLevel.LOW,
                    confidence=0.6,
                    description=f"Unusual typing speed: {current_data.typing_speed} WPM",
                    evidence={
                        "current_speed": current_data.typing_speed,
                        "typical_speed": avg_speed,
                        "variance": speed_variance
                    },
                    recommendations=["Monitor for additional behavioral changes"],
                    timestamp=datetime.utcnow()
                ))
        
        # Mouse behavior anomaly
        if (current_data.mouse_velocity and profile.mouse_profile and
            "avg_mouse_velocity" in profile.mouse_profile):
            
            avg_velocity = profile.mouse_profile["avg_mouse_velocity"]
            velocity_variance = profile.mouse_profile.get("mouse_velocity_variance", 50)
            
            if abs(current_data.mouse_velocity - avg_velocity) > 2 * velocity_variance:
                anomalies.append(AnomalyResult(
                    anomaly_type=BehaviorAnomalyType.MOUSE_BEHAVIOR,
                    risk_level=RiskLevel.LOW,
                    confidence=0.5,
                    description=f"Unusual mouse behavior: {current_data.mouse_velocity} px/s",
                    evidence={
                        "current_velocity": current_data.mouse_velocity,
                        "typical_velocity": avg_velocity,
                        "variance": velocity_variance
                    },
                    recommendations=["Continue monitoring mouse patterns"],
                    timestamp=datetime.utcnow()
                ))
        
        return anomalies
    
    async def _ml_anomaly_detection(
        self,
        user_id: str,
        features: Dict[str, Any]
    ) -> List[AnomalyResult]:
        """ML-based anomaly detection"""
        anomalies = []
        
        if not self.models_trained:
            return anomalies
        
        try:
            # Flatten features for ML model
            feature_vector = self._flatten_features(features)
            feature_array = np.array(feature_vector).reshape(1, -1)
            
            # Scale features
            scaled_features = self.scaler.transform(feature_array)
            
            # Predict anomaly
            anomaly_score = self.anomaly_detector.decision_function(scaled_features)[0]
            is_anomaly = self.anomaly_detector.predict(scaled_features)[0] == -1
            
            if is_anomaly:
                confidence = min(1.0, abs(anomaly_score))
                risk_level = (RiskLevel.HIGH if confidence > 0.8 
                            else RiskLevel.MEDIUM if confidence > 0.5 
                            else RiskLevel.LOW)
                
                anomalies.append(AnomalyResult(
                    anomaly_type=BehaviorAnomalyType.SUSPICIOUS_PATTERN,
                    risk_level=risk_level,
                    confidence=confidence,
                    description="ML model detected suspicious behavioral pattern",
                    evidence={
                        "anomaly_score": anomaly_score,
                        "model_confidence": confidence,
                        "feature_importance": await self._get_feature_importance(features)
                    },
                    recommendations=[
                        "Investigate specific behavioral aspects",
                        "Compare with historical patterns",
                        "Consider additional authentication"
                    ],
                    timestamp=datetime.utcnow()
                ))
        
        except Exception as e:
            self.logger.warning(f"ML anomaly detection failed: {e}")
        
        return anomalies
    
    # Helper methods
    
    def _load_config(self) -> Dict[str, Any]:
        """Load behavioral analytics configuration"""
        default_config = {
            "location_threshold_km": 100,
            "velocity_threshold_kmh": 900,
            "session_timeout_minutes": 30,
            "min_history_for_profile": 10,
            "anomaly_retention_days": 30
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
        except Exception as e:
            self.logger.warning(f"Config loading failed: {e}")
        
        return default_config
    
    def _initialize_geoip(self):
        """Initialize GeoIP database"""
        # In production, use actual GeoIP database
        # For now, mock the initialization
        self.geoip_reader = None
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth radius in km
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = (np.sin(delta_lat / 2) ** 2 +
             np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        return R * c
    
    def _flatten_features(self, features: Dict[str, Any]) -> List[float]:
        """Flatten nested features for ML processing"""
        flattened = []
        
        for category, cat_features in features.items():
            for key, value in cat_features.items():
                if isinstance(value, (int, float)):
                    flattened.append(float(value))
                elif isinstance(value, bool):
                    flattened.append(float(value))
                elif isinstance(value, str):
                    # Hash string values
                    flattened.append(float(hash(value) % 1000) / 1000.0)
        
        return flattened
    
    async def _get_time_since_last_login(self, user_id: str) -> float:
        """Get time since last login in hours"""
        history = list(self.behavior_history.get(user_id, []))
        if len(history) >= 2:
            last_login = history[-2].timestamp
            return (datetime.utcnow() - last_login).total_seconds() / 3600
        return 0.0
    
    async def _is_known_device(self, user_id: str, device_fingerprint: str) -> bool:
        """Check if device is known for user"""
        profile = self.user_profiles.get(user_id)
        return profile and device_fingerprint in profile.known_devices
    
    async def _is_known_ip(self, user_id: str, ip_address: str) -> bool:
        """Check if IP address is known for user"""
        # Simplified check - in production, maintain IP history
        history = list(self.behavior_history.get(user_id, []))
        recent_ips = {data.ip_address for data in history[-10:]}
        return ip_address in recent_ips
    
    async def _get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get existing profile or create new one"""
        if user_id not in self.user_profiles:
            return await self.create_user_profile(user_id)
        return self.user_profiles[user_id]
    
    async def _update_user_profile(
        self,
        profile: UserProfile,
        behavior_data: BehaviorMetrics,
        features: Dict[str, Any]
    ):
        """Update user profile with new behavior data"""
        profile.updated_at = datetime.utcnow()
        
        # Update locations
        if behavior_data.location:
            profile.common_locations.append(behavior_data.location)
            # Keep only recent locations
            profile.common_locations = profile.common_locations[-20:]
            
            # Update location variance
            if len(profile.common_locations) > 1:
                lats = [loc["latitude"] for loc in profile.common_locations]
                lons = [loc["longitude"] for loc in profile.common_locations]
                profile.location_variance = np.std(lats) + np.std(lons)
        
        # Update time patterns
        hour = behavior_data.timestamp.hour
        day = behavior_data.timestamp.weekday()
        
        if hour not in profile.active_hours:
            profile.active_hours.append(hour)
        if day not in profile.active_days:
            profile.active_days.append(day)
        
        # Update device info
        profile.known_devices.add(behavior_data.device_fingerprint)
        
        # Update behavioral profiles
        if behavior_data.typing_speed:
            if "avg_typing_speed" not in profile.typing_profile:
                profile.typing_profile["avg_typing_speed"] = behavior_data.typing_speed
            else:
                # Running average
                current_avg = profile.typing_profile["avg_typing_speed"]
                profile.typing_profile["avg_typing_speed"] = (current_avg * 0.9 + 
                                                            behavior_data.typing_speed * 0.1)
        
        if behavior_data.mouse_velocity:
            if "avg_mouse_velocity" not in profile.mouse_profile:
                profile.mouse_profile["avg_mouse_velocity"] = behavior_data.mouse_velocity
            else:
                current_avg = profile.mouse_profile["avg_mouse_velocity"]
                profile.mouse_profile["avg_mouse_velocity"] = (current_avg * 0.9 + 
                                                             behavior_data.mouse_velocity * 0.1)
        
        # Update trust level (gradually increase with consistent behavior)
        profile.trust_level = min(1.0, profile.trust_level + 0.01)
    
    async def _analyze_behavior_history(
        self,
        user_id: str,
        history: List[BehaviorMetrics]
    ) -> UserProfile:
        """Analyze historical behavior to create profile"""
        # Extract common locations
        locations = [data.location for data in history if data.location]
        
        # Extract time patterns
        hours = [data.timestamp.hour for data in history]
        days = [data.timestamp.weekday() for data in history]
        
        # Extract device patterns
        devices = {data.device_fingerprint for data in history}
        
        # Calculate behavioral metrics
        typing_speeds = [data.typing_speed for data in history if data.typing_speed]
        mouse_velocities = [data.mouse_velocity for data in history if data.mouse_velocity]
        
        # Build profile
        profile = UserProfile(
            user_id=user_id,
            created_at=history[0].timestamp if history else datetime.utcnow(),
            updated_at=datetime.utcnow(),
            common_locations=locations[-10:],  # Recent locations
            location_variance=np.std([loc["latitude"] for loc in locations]) if locations else 0.0,
            active_hours=list(set(hours)),
            active_days=list(set(days)),
            session_patterns={},
            known_devices=devices,
            device_consistency=1.0 if len(devices) <= 3 else 0.8,
            typing_profile={
                "avg_typing_speed": np.mean(typing_speeds) if typing_speeds else 0,
                "typing_speed_variance": np.var(typing_speeds) if typing_speeds else 0
            },
            mouse_profile={
                "avg_mouse_velocity": np.mean(mouse_velocities) if mouse_velocities else 0,
                "mouse_velocity_variance": np.var(mouse_velocities) if mouse_velocities else 0
            },
            interaction_patterns={},
            risk_score=0.3,  # Low risk for established users
            anomaly_history=[],
            trust_level=0.7  # Higher trust for users with history
        )
        
        return profile
    
    async def _update_session_tracking(self, user_id: str, behavior_data: BehaviorMetrics):
        """Update session tracking data"""
        session_id = f"{user_id}_{behavior_data.timestamp.date()}"
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "start_time": behavior_data.timestamp,
                "last_activity": behavior_data.timestamp,
                "action_count": 0,
                "locations": []
            }
        
        session = self.active_sessions[session_id]
        session["last_activity"] = behavior_data.timestamp
        session["action_count"] += behavior_data.action_count
        
        if behavior_data.location:
            session["locations"].append(behavior_data.location)
    
    async def _calculate_feature_risk(self, features: Dict[str, Any]) -> float:
        """Calculate risk based on extracted features"""
        risk_factors = []
        
        # Temporal risk factors
        temporal = features.get("temporal", {})
        if not temporal.get("is_business_hours", True):
            risk_factors.append(0.1)
        if temporal.get("is_weekend", False):
            risk_factors.append(0.05)
        
        # Spatial risk factors
        spatial = features.get("spatial", {})
        if spatial.get("is_vpn", False):
            risk_factors.append(0.2)
        if spatial.get("is_proxy", False):
            risk_factors.append(0.3)
        
        # Device risk factors
        device = features.get("device", {})
        if not device.get("is_known_device", True):
            risk_factors.append(0.2)
        
        return min(1.0, sum(risk_factors))
    
    async def _get_feature_importance(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Get feature importance for ML predictions"""
        # Simplified feature importance
        importance = {}
        
        for category, cat_features in features.items():
            for key, value in cat_features.items():
                if isinstance(value, (int, float, bool)):
                    # Mock importance score
                    importance[f"{category}_{key}"] = np.random.random() * 0.1
        
        return importance


# Export main classes
__all__ = [
    "BehavioralAnalyticsEngine",
    "BehaviorAnomalyType",
    "RiskLevel",
    "BehaviorMetrics",
    "UserProfile",
    "AnomalyResult", 
    "RiskAssessment"
]