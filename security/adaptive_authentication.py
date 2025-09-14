"""
Adaptive Authentication module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🔒 Adaptive Authentication System - Ainflue Platform
==================================================

Enterprise-grade risk-based adaptive authentication engine that dynamically adjusts
authentication requirements based on real-time risk assessment, user behavior,
device fingerprinting, and threat intelligence.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Role Expert: Lead Dev IA + Backend Senior + ML Engineer + Security Specialist
Version: 1.0.0
Created: 2025-01-09
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import geoip2.database
import user_agents
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import redis
import aioredis
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Authentication risk levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuthenticationMethod(Enum):
    """Available authentication methods"""
    PASSWORD = "password"
    SMS_OTP = "sms_otp"
    EMAIL_OTP = "email_otp"
    TOTP = "totp"
    BIOMETRIC = "biometric"
    HARDWARE_TOKEN = "hardware_token"
    PUSH_NOTIFICATION = "push_notification"
    BEHAVIORAL = "behavioral"

@dataclass
class DeviceFingerprint:
    """Device fingerprinting data"""
    user_agent: str
    screen_resolution: str
    timezone: str
    language: str
    platform: str
    browser: str
    browser_version: str
    plugins: List[str]
    canvas_hash: str
    webgl_hash: str
    fonts: List[str]
    ip_address: str
    device_hash: str

@dataclass
class GeolocationInfo:
    """User geolocation information"""
    country: str
    city: str
    latitude: float
    longitude: float
    isp: str
    organization: str
    is_vpn: bool
    is_tor: bool
    is_hosting: bool

@dataclass
class BehavioralPattern:
    """User behavioral pattern data"""
    typing_rhythm: List[float]
    mouse_patterns: List[Tuple[int, int]]
    session_duration: float
    activity_hours: List[int]
    common_locations: List[str]
    access_patterns: Dict[str, int]
    device_preferences: List[str]

@dataclass
class RiskFactor:
    """Individual risk assessment factor"""
    factor_type: str
    weight: float
    score: float
    description: str
    confidence: float

@dataclass
class AuthenticationDecision:
    """Final authentication decision"""
    user_id: str
    session_id: str
    risk_level: RiskLevel
    risk_score: float
    required_methods: List[AuthenticationMethod]
    allow_access: bool
    additional_verification: bool
    session_duration: timedelta
    monitoring_level: str
    risk_factors: List[RiskFactor]
    timestamp: datetime

class AdaptiveAuthenticationEngine:
    """
    🧠 Enterprise Adaptive Authentication Engine
    
    Features:
    - Real-time risk assessment
    - Machine learning behavior analysis
    - Device fingerprinting
    - Geolocation analysis
    - Threat intelligence integration
    - Dynamic authentication requirements
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.redis_client = None
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Initialize ML models
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
        # Risk assessment weights
        self.risk_weights = {
            'geolocation': 0.2,
            'device_fingerprint': 0.15,
            'behavioral_pattern': 0.25,
            'time_pattern': 0.1,
            'network_analysis': 0.15,
            'threat_intelligence': 0.15
        }
        
        # Authentication method mapping
        self.auth_method_strength = {
            AuthenticationMethod.PASSWORD: 1,
            AuthenticationMethod.SMS_OTP: 2,
            AuthenticationMethod.EMAIL_OTP: 2,
            AuthenticationMethod.TOTP: 3,
            AuthenticationMethod.PUSH_NOTIFICATION: 3,
            AuthenticationMethod.BIOMETRIC: 4,
            AuthenticationMethod.HARDWARE_TOKEN: 5,
            AuthenticationMethod.BEHAVIORAL: 3
        }
        
        logger.info("🔒 Adaptive Authentication Engine initialized")

    async def initialize(self) -> None:
        """Initialize async components"""
        try:
            # Initialize Redis connection
            self.redis_client = await aioredis.create_redis_pool(
                'redis://localhost:6379',
                encoding='utf-8'
            )
            
            # Load historical data for ML training
            await self._train_anomaly_detector()
            
            logger.info("✅ Adaptive Authentication Engine fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize adaptive authentication: {e}")
            raise

    async def assess_authentication_risk(
        self,
        user_id: str,
        session_id: str,
        device_fingerprint: DeviceFingerprint,
        request_data: Dict[str, Any]
    ) -> AuthenticationDecision:
        """
        🎯 Comprehensive risk assessment for authentication request
        """
        try:
            # Collect risk factors
            risk_factors = []
            
            # 1. Geolocation analysis
            geo_risk = await self._assess_geolocation_risk(user_id, device_fingerprint.ip_address)
            risk_factors.append(geo_risk)
            
            # 2. Device fingerprint analysis
            device_risk = await self._assess_device_risk(user_id, device_fingerprint)
            risk_factors.append(device_risk)
            
            # 3. Behavioral pattern analysis
            behavioral_risk = await self._assess_behavioral_risk(user_id, request_data)
            risk_factors.append(behavioral_risk)
            
            # 4. Time pattern analysis
            time_risk = await self._assess_time_pattern_risk(user_id)
            risk_factors.append(time_risk)
            
            # 5. Network analysis
            network_risk = await self._assess_network_risk(device_fingerprint.ip_address)
            risk_factors.append(network_risk)
            
            # 6. Threat intelligence
            threat_risk = await self._assess_threat_intelligence(device_fingerprint.ip_address, user_id)
            risk_factors.append(threat_risk)
            
            # Calculate overall risk score
            risk_score = self._calculate_overall_risk(risk_factors)
            risk_level = self._determine_risk_level(risk_score)
            
            # Determine required authentication methods
            required_methods = self._determine_auth_methods(risk_level, risk_score)
            
            # Make authentication decision
            decision = AuthenticationDecision(
                user_id=user_id,
                session_id=session_id,
                risk_level=risk_level,
                risk_score=risk_score,
                required_methods=required_methods,
                allow_access=self._should_allow_access(risk_level),
                additional_verification=risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL],
                session_duration=self._calculate_session_duration(risk_level),
                monitoring_level=self._determine_monitoring_level(risk_level),
                risk_factors=risk_factors,
                timestamp=datetime.now()
            )
            
            # Store decision for learning
            await self._store_authentication_decision(decision)
            
            logger.info(f"🎯 Authentication risk assessed: {risk_level.value} (score: {risk_score:.3f})")
            return decision
            
        except Exception as e:
            logger.error(f"❌ Risk assessment failed: {e}")
            # Return safe default for high security
            return AuthenticationDecision(
                user_id=user_id,
                session_id=session_id,
                risk_level=RiskLevel.HIGH,
                risk_score=0.8,
                required_methods=[AuthenticationMethod.PASSWORD, AuthenticationMethod.TOTP],
                allow_access=False,
                additional_verification=True,
                session_duration=timedelta(hours=1),
                monitoring_level="high",
                risk_factors=[],
                timestamp=datetime.now()
            )

    async def _assess_geolocation_risk(self, user_id: str, ip_address: str) -> RiskFactor:
        """Assess risk based on geolocation"""
        try:
            # Get current location
            current_location = await self._get_geolocation(ip_address)
            
            # Get user's historical locations
            historical_locations = await self._get_user_locations(user_id)
            
            # Calculate distance from usual locations
            if historical_locations:
                min_distance = min([
                    self._calculate_distance(
                        current_location.latitude,
                        current_location.longitude,
                        loc['latitude'],
                        loc['longitude']
                    ) for loc in historical_locations
                ])
                
                # Risk based on distance (>1000km = higher risk)
                distance_score = min(min_distance / 1000.0, 1.0)
            else:
                distance_score = 0.5  # Unknown location = medium risk
            
            # Additional risk factors
            vpn_score = 0.3 if current_location.is_vpn else 0.0
            tor_score = 0.8 if current_location.is_tor else 0.0
            hosting_score = 0.4 if current_location.is_hosting else 0.0
            
            total_score = min(distance_score + vpn_score + tor_score + hosting_score, 1.0)
            
            return RiskFactor(
                factor_type="geolocation",
                weight=self.risk_weights['geolocation'],
                score=total_score,
                description=f"Location: {current_location.city}, {current_location.country}",
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"❌ Geolocation assessment failed: {e}")
            return RiskFactor(
                factor_type="geolocation",
                weight=self.risk_weights['geolocation'],
                score=0.5,
                description="Geolocation assessment failed",
                confidence=0.1
            )

    async def _assess_device_risk(self, user_id: str, fingerprint: DeviceFingerprint) -> RiskFactor:
        """Assess risk based on device fingerprint"""
        try:
            # Get user's known devices
            known_devices = await self._get_user_devices(user_id)
            
            # Check if device is known
            device_known = any(
                device['device_hash'] == fingerprint.device_hash 
                for device in known_devices
            )
            
            if device_known:
                device_score = 0.1  # Known device = low risk
            else:
                # New device = higher risk
                device_score = 0.7
                
                # Additional checks for suspicious characteristics
                suspicious_patterns = [
                    len(fingerprint.plugins) == 0,  # No plugins
                    fingerprint.canvas_hash == "blocked",  # Canvas blocking
                    fingerprint.webgl_hash == "blocked",  # WebGL blocking
                    len(fingerprint.fonts) < 5,  # Too few fonts
                ]
                
                suspicious_count = sum(suspicious_patterns)
                device_score += suspicious_count * 0.1
            
            device_score = min(device_score, 1.0)
            
            return RiskFactor(
                factor_type="device_fingerprint",
                weight=self.risk_weights['device_fingerprint'],
                score=device_score,
                description=f"Device: {fingerprint.platform} {fingerprint.browser}",
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"❌ Device assessment failed: {e}")
            return RiskFactor(
                factor_type="device_fingerprint",
                weight=self.risk_weights['device_fingerprint'],
                score=0.5,
                description="Device assessment failed",
                confidence=0.1
            )

    async def _assess_behavioral_risk(self, user_id: str, request_data: Dict[str, Any]) -> RiskFactor:
        """Assess risk based on behavioral patterns using ML"""
        try:
            # Get user's behavioral baseline
            baseline_behavior = await self._get_user_behavior_baseline(user_id)
            
            if not baseline_behavior:
                return RiskFactor(
                    factor_type="behavioral_pattern",
                    weight=self.risk_weights['behavioral_pattern'],
                    score=0.3,  # New user = medium risk
                    description="No behavioral baseline available",
                    confidence=0.5
                )
            
            # Extract current behavioral features
            current_features = self._extract_behavioral_features(request_data)
            
            # Use anomaly detection model
            anomaly_score = self.anomaly_detector.decision_function([current_features])[0]
            
            # Convert anomaly score to risk score (lower anomaly score = higher risk)
            risk_score = max(0, (0.5 - anomaly_score) * 2)
            risk_score = min(risk_score, 1.0)
            
            return RiskFactor(
                factor_type="behavioral_pattern",
                weight=self.risk_weights['behavioral_pattern'],
                score=risk_score,
                description=f"Behavioral anomaly score: {anomaly_score:.3f}",
                confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"❌ Behavioral assessment failed: {e}")
            return RiskFactor(
                factor_type="behavioral_pattern",
                weight=self.risk_weights['behavioral_pattern'],
                score=0.5,
                description="Behavioral assessment failed",
                confidence=0.1
            )

    async def _assess_time_pattern_risk(self, user_id: str) -> RiskFactor:
        """Assess risk based on access time patterns"""
        try:
            current_hour = datetime.now().hour
            
            # Get user's typical access hours
            typical_hours = await self._get_user_access_hours(user_id)
            
            if not typical_hours:
                return RiskFactor(
                    factor_type="time_pattern",
                    weight=self.risk_weights['time_pattern'],
                    score=0.2,
                    description="No time pattern baseline",
                    confidence=0.5
                )
            
            # Calculate risk based on how unusual this hour is
            if current_hour in typical_hours:
                hour_frequency = typical_hours.count(current_hour)
                total_accesses = len(typical_hours)
                frequency_ratio = hour_frequency / total_accesses
                
                # Higher frequency = lower risk
                time_score = max(0, 1 - frequency_ratio * 2)
            else:
                # Completely new hour = higher risk
                time_score = 0.6
            
            return RiskFactor(
                factor_type="time_pattern",
                weight=self.risk_weights['time_pattern'],
                score=time_score,
                description=f"Access at hour: {current_hour}",
                confidence=0.7
            )
            
        except Exception as e:
            logger.error(f"❌ Time pattern assessment failed: {e}")
            return RiskFactor(
                factor_type="time_pattern",
                weight=self.risk_weights['time_pattern'],
                score=0.3,
                description="Time pattern assessment failed",
                confidence=0.1
            )

    async def _assess_network_risk(self, ip_address: str) -> RiskFactor:
        """Assess network-based risk factors"""
        try:
            network_score = 0.0
            description_parts = []
            
            # Check against threat intelligence feeds
            is_malicious = await self._check_ip_reputation(ip_address)
            if is_malicious:
                network_score += 0.8
                description_parts.append("Malicious IP")
            
            # Check if IP is from hosting provider
            geo_info = await self._get_geolocation(ip_address)
            if geo_info.is_hosting:
                network_score += 0.3
                description_parts.append("Hosting provider")
            
            # Check for VPN/Proxy
            if geo_info.is_vpn:
                network_score += 0.2
                description_parts.append("VPN/Proxy")
            
            # Check for Tor
            if geo_info.is_tor:
                network_score += 0.6
                description_parts.append("Tor network")
            
            network_score = min(network_score, 1.0)
            description = ", ".join(description_parts) if description_parts else "Clean network"
            
            return RiskFactor(
                factor_type="network_analysis",
                weight=self.risk_weights['network_analysis'],
                score=network_score,
                description=description,
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"❌ Network assessment failed: {e}")
            return RiskFactor(
                factor_type="network_analysis",
                weight=self.risk_weights['network_analysis'],
                score=0.3,
                description="Network assessment failed",
                confidence=0.1
            )

    async def _assess_threat_intelligence(self, ip_address: str, user_id: str) -> RiskFactor:
        """Assess based on threat intelligence"""
        try:
            threat_score = 0.0
            description_parts = []
            
            # Check recent failed login attempts
            recent_failures = await self._get_recent_failures(user_id, ip_address)
            if recent_failures > 3:
                threat_score += min(recent_failures * 0.1, 0.5)
                description_parts.append(f"{recent_failures} recent failures")
            
            # Check for account lockout history
            lockout_history = await self._get_lockout_history(user_id)
            if lockout_history > 0:
                threat_score += min(lockout_history * 0.05, 0.3)
                description_parts.append(f"{lockout_history} past lockouts")
            
            # Check for suspicious activity patterns
            suspicious_patterns = await self._detect_suspicious_patterns(user_id)
            if suspicious_patterns:
                threat_score += 0.4
                description_parts.append("Suspicious patterns detected")
            
            threat_score = min(threat_score, 1.0)
            description = ", ".join(description_parts) if description_parts else "No threats detected"
            
            return RiskFactor(
                factor_type="threat_intelligence",
                weight=self.risk_weights['threat_intelligence'],
                score=threat_score,
                description=description,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"❌ Threat intelligence assessment failed: {e}")
            return RiskFactor(
                factor_type="threat_intelligence",
                weight=self.risk_weights['threat_intelligence'],
                score=0.2,
                description="Threat assessment failed",
                confidence=0.1
            )

    def _calculate_overall_risk(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate weighted overall risk score"""
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for factor in risk_factors:
            weighted_score = factor.score * factor.weight * factor.confidence
            total_weighted_score += weighted_score
            total_weight += factor.weight * factor.confidence
        
        if total_weight == 0:
            return 0.5  # Default medium risk
        
        overall_risk = total_weighted_score / total_weight
        return min(max(overall_risk, 0.0), 1.0)

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert numeric risk score to risk level"""
        if risk_score < 0.2:
            return RiskLevel.VERY_LOW
        elif risk_score < 0.4:
            return RiskLevel.LOW
        elif risk_score < 0.6:
            return RiskLevel.MEDIUM
        elif risk_score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _determine_auth_methods(self, risk_level: RiskLevel, risk_score: float) -> List[AuthenticationMethod]:
        """Determine required authentication methods based on risk"""
        base_methods = [AuthenticationMethod.PASSWORD]
        
        if risk_level == RiskLevel.VERY_LOW:
            return base_methods
        elif risk_level == RiskLevel.LOW:
            return base_methods + [AuthenticationMethod.EMAIL_OTP]
        elif risk_level == RiskLevel.MEDIUM:
            return base_methods + [AuthenticationMethod.TOTP]
        elif risk_level == RiskLevel.HIGH:
            return base_methods + [AuthenticationMethod.TOTP, AuthenticationMethod.PUSH_NOTIFICATION]
        else:  # CRITICAL
            return base_methods + [
                AuthenticationMethod.TOTP,
                AuthenticationMethod.BIOMETRIC,
                AuthenticationMethod.HARDWARE_TOKEN
            ]

    def _should_allow_access(self, risk_level: RiskLevel) -> bool:
        """Determine if access should be allowed based on risk level"""
        return risk_level != RiskLevel.CRITICAL

    def _calculate_session_duration(self, risk_level: RiskLevel) -> timedelta:
        """Calculate session duration based on risk level"""
        durations = {
            RiskLevel.VERY_LOW: timedelta(hours=24),
            RiskLevel.LOW: timedelta(hours=12),
            RiskLevel.MEDIUM: timedelta(hours=4),
            RiskLevel.HIGH: timedelta(hours=1),
            RiskLevel.CRITICAL: timedelta(minutes=15)
        }
        return durations.get(risk_level, timedelta(hours=1))

    def _determine_monitoring_level(self, risk_level: RiskLevel) -> str:
        """Determine monitoring level based on risk"""
        levels = {
            RiskLevel.VERY_LOW: "minimal",
            RiskLevel.LOW: "standard",
            RiskLevel.MEDIUM: "enhanced",
            RiskLevel.HIGH: "intensive",
            RiskLevel.CRITICAL: "maximum"
        }
        return levels.get(risk_level, "standard")

    # Helper methods for data access and processing
    async def _get_geolocation(self, ip_address: str) -> GeolocationInfo:
        """Get geolocation information for IP address"""
        # Placeholder implementation - would use GeoIP2 database
        return GeolocationInfo(
            country="US",
            city="New York",
            latitude=40.7128,
            longitude=-74.0060,
            isp="Example ISP",
            organization="Example Org",
            is_vpn=False,
            is_tor=False,
            is_hosting=False
        )

    async def _get_user_locations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's historical locations"""
        key = f"user_locations:{user_id}"
        if self.redis_client:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        return []

    async def _get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's known devices"""
        key = f"user_devices:{user_id}"
        if self.redis_client:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        return []

    async def _get_user_behavior_baseline(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's behavioral baseline"""
        key = f"user_behavior:{user_id}"
        if self.redis_client:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        return None

    async def _get_user_access_hours(self, user_id: str) -> List[int]:
        """Get user's typical access hours"""
        key = f"user_hours:{user_id}"
        if self.redis_client:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        return []

    def _extract_behavioral_features(self, request_data: Dict[str, Any]) -> List[float]:
        """Extract behavioral features from request data"""
        # Placeholder - would extract real behavioral features
        return [0.5, 0.3, 0.7, 0.2, 0.8]

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

    async def _check_ip_reputation(self, ip_address: str) -> bool:
        """Check IP against threat intelligence feeds"""
        # Placeholder - would check against real threat feeds
        return False

    async def _get_recent_failures(self, user_id: str, ip_address: str) -> int:
        """Get recent failed login attempts"""
        # Placeholder implementation
        return 0

    async def _get_lockout_history(self, user_id: str) -> int:
        """Get account lockout history"""
        # Placeholder implementation
        return 0

    async def _detect_suspicious_patterns(self, user_id: str) -> bool:
        """Detect suspicious activity patterns"""
        # Placeholder implementation
        return False

    async def _train_anomaly_detector(self) -> None:
        """Train the anomaly detection model with historical data"""
        # Placeholder - would train with real historical data
        dummy_data = np.random.rand(1000, 5)
        self.anomaly_detector.fit(dummy_data)
        logger.info("🤖 Anomaly detection model trained")

    async def _store_authentication_decision(self, decision -> None: AuthenticationDecision) -> None:
        """Store authentication decision for learning and auditing"""
        if self.redis_client:
            key = f"auth_decision:{decision.user_id}:{decision.timestamp.isoformat()}"
            data = json.dumps(asdict(decision), default=str)
            encrypted_data = self.cipher.encrypt(data.encode())
            await self.redis_client.setex(key, 86400, encrypted_data)  # 24 hour retention

    async def close(self) -> None:
        """Cleanup resources"""
        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()

# Export main class
__all__ = ['AdaptiveAuthenticationEngine', 'AuthenticationDecision', 'RiskLevel', 'AuthenticationMethod']

if __name__ == "__main__":
    async def test_adaptive_auth() -> None:
        """Test the adaptive authentication system"""
        config = {
            'risk_thresholds': {
                'low': 0.3,
                'medium': 0.6,
                'high': 0.8
            }
        }
        
        auth_engine = AdaptiveAuthenticationEngine(config)
        await auth_engine.initialize()
        
        # Test device fingerprint
        test_fingerprint = DeviceFingerprint(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            screen_resolution="1920x1080",
            timezone="America/New_York",
            language="en-US",
            platform="Win32",
            browser="Chrome",
            browser_version="96.0",
            plugins=["pdf", "flash"],
            canvas_hash="abc123",
            webgl_hash="def456",
            fonts=["Arial", "Times"],
            ip_address="192.168.1.1",
            device_hash="device123"
        )
        
        # Test authentication decision
        decision = await auth_engine.assess_authentication_risk(
            user_id="test_user",
            session_id="session123",
            device_fingerprint=test_fingerprint,
            request_data={"typing_rhythm": [120, 110, 115]}
        )
        
        print(f"🎯 Authentication Decision:")
        print(f"   Risk Level: {decision.risk_level.value}")
        print(f"   Risk Score: {decision.risk_score:.3f}")
        print(f"   Required Methods: {[m.value for m in decision.required_methods]}")
        print(f"   Allow Access: {decision.allow_access}")
        print(f"   Session Duration: {decision.session_duration}")
        
        await auth_engine.close()
    
    # Run test
    asyncio.run(test_adaptive_auth())