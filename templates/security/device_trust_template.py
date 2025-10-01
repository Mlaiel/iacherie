"""Device Trust Template for iacherie Platform
Advanced device trust and management system with fingerprinting, risk assessment,
device registration, and behavioral analysis for creator security enhancement.

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Propriété intellectuelle protégée
"""

import logging
import secrets
import hashlib
import base64
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import aiohttp
from user_agents import parse

from pydantic import BaseModel, Field, validator
from cryptography.fernet import Fernet
import geoip2.database
import numpy as np
from sklearn.ensemble import IsolationForest

from core.config import get_settings
from utils.exceptions import DeviceTrustException, SecurityException
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class DeviceType(Enum):
    """Device types"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    GAMING_CONSOLE = "gaming_console"
    IOT_DEVICE = "iot_device"
    UNKNOWN = "unknown"


class TrustLevel(Enum):
    """Device trust levels"""
    UNKNOWN = "unknown"
    UNTRUSTED = "untrusted"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    TRUSTED = "trusted"


class RiskLevel(Enum):
    """Device risk levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class DeviceStatus(Enum):
    """Device status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPROMISED = "compromised"
    LOST = "lost"
    RETIRED = "retired"


class DeviceFingerprint(BaseModel):
    """Device fingerprint data"""
    fingerprint_id: str = Field(..., description="Unique fingerprint ID")
    user_agent: str = Field(..., description="User agent string")
    screen_resolution: Optional[str] = Field(default=None, description="Screen resolution")
    timezone: Optional[str] = Field(default=None, description="Timezone")
    language: Optional[str] = Field(default=None, description="Browser language")
    platform: Optional[str] = Field(default=None, description="Operating system")
    browser: Optional[str] = Field(default=None, description="Browser name")
    browser_version: Optional[str] = Field(default=None, description="Browser version")
    device_memory: Optional[int] = Field(default=None, description="Device memory")
    hardware_concurrency: Optional[int] = Field(default=None, description="CPU cores")
    color_depth: Optional[int] = Field(default=None, description="Color depth")
    pixel_ratio: Optional[float] = Field(default=None, description="Device pixel ratio")
    touch_support: Optional[bool] = Field(default=None, description="Touch support")
    webgl_vendor: Optional[str] = Field(default=None, description="WebGL vendor")
    webgl_renderer: Optional[str] = Field(default=None, description="WebGL renderer")
    canvas_fingerprint: Optional[str] = Field(default=None, description="Canvas fingerprint")
    audio_fingerprint: Optional[str] = Field(default=None, description="Audio fingerprint")
    plugins: List[str] = Field(default_factory=list, description="Browser plugins")
    fonts: List[str] = Field(default_factory=list, description="Available fonts")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeviceInfo(BaseModel):
    """Device information"""
    device_id: str = Field(..., description="Unique device identifier")
    user_id: str = Field(..., description="Associated user ID")
    device_name: str = Field(..., description="User-defined device name")
    device_type: DeviceType = Field(..., description="Device type")
    fingerprint: DeviceFingerprint = Field(..., description="Device fingerprint")
    trust_level: TrustLevel = Field(default=TrustLevel.UNKNOWN)
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE)
    is_managed: bool = Field(default=False, description="Enterprise managed device")
    is_jailbroken: Optional[bool] = Field(default=None, description="Jailbreak/root status")
    last_seen_ip: Optional[str] = Field(default=None)
    last_seen_location: Optional[Dict[str, Any]] = Field(default=None)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    login_count: int = Field(default=0)
    failed_attempts: int = Field(default=0)
    security_events: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeviceRegistrationRequest(BaseModel):
    """Device registration request"""
    user_id: str = Field(..., description="User ID")
    device_name: str = Field(..., description="Device name")
    fingerprint_data: Dict[str, Any] = Field(..., description="Device fingerprint data")
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    geolocation: Optional[Dict[str, Any]] = Field(default=None)
    device_info: Optional[Dict[str, Any]] = Field(default=None)
    trust_this_device: bool = Field(default=False)


class DeviceTrustRequest(BaseModel):
    """Device trust assessment request"""
    device_id: Optional[str] = Field(default=None)
    fingerprint_data: Dict[str, Any] = Field(..., description="Current fingerprint")
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    behavioral_data: Optional[Dict[str, Any]] = Field(default=None)
    session_data: Optional[Dict[str, Any]] = Field(default=None)


class DeviceTrustResponse(BaseModel):
    """Device trust assessment response"""
    success: bool = Field(..., description="Assessment success")
    device_id: Optional[str] = Field(default=None)
    trust_level: TrustLevel = Field(..., description="Current trust level")
    risk_level: RiskLevel = Field(..., description="Current risk level")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    is_recognized: bool = Field(..., description="Device recognition status")
    is_suspicious: bool = Field(..., description="Suspicious activity detected")
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    additional_verification_required: bool = Field(default=False)
    verification_methods: List[str] = Field(default_factory=list)
    session_restrictions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BehavioralMetrics(BaseModel):
    """Behavioral metrics for device analysis"""
    typing_patterns: Optional[Dict[str, Any]] = Field(default=None)
    mouse_movements: Optional[List[Dict[str, float]]] = Field(default=None)
    click_patterns: Optional[Dict[str, Any]] = Field(default=None)
    scroll_behavior: Optional[Dict[str, Any]] = Field(default=None)
    navigation_patterns: Optional[List[str]] = Field(default=None)
    session_duration: Optional[int] = Field(default=None, description="Session duration in seconds")
    active_time: Optional[int] = Field(default=None, description="Active time in seconds")
    idle_time: Optional[int] = Field(default=None, description="Idle time in seconds")
    error_rate: Optional[float] = Field(default=None, description="User error rate")
    feature_usage: Optional[Dict[str, int]] = Field(default=None)


class DeviceTrustService:
    """Comprehensive device trust and management service for iacherie platform
    
    Provides enterprise-grade device trust assessment with:
    - Advanced device fingerprinting and recognition
    - Behavioral analysis and anomaly detection  
    - Risk assessment and threat detection
    - Device lifecycle management
    - Geolocation and IP reputation analysis
    - Machine learning-based trust scoring
    - Enterprise device management integration
    - Creator security enhancement features
    """
    
    def __init__(self):
        self.metrics_collector = SecurityMetricsCollector()
        self.cipher = Fernet(Fernet.generate_key())
        
        # Device storage
        self.devices: Dict[str, DeviceInfo] = {}
        self.user_devices: Dict[str, List[str]] = {}  # user_id -> device_ids
        self.fingerprint_index: Dict[str, str] = {}  # fingerprint_hash -> device_id
        
        # Risk assessment models
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.behavioral_model = None
        
        # IP reputation and geolocation
        self.known_malicious_ips = set()
        self.known_vpn_ranges = set()
        self.geoip_reader = None
        
        # Trust scoring weights
        self.trust_weights = {
            "fingerprint_match": 0.3,
            "location_consistency": 0.2,
            "behavioral_consistency": 0.2,
            "usage_patterns": 0.15,
            "time_patterns": 0.1,
            "security_history": 0.05
        }
        
        logger.info("Device trust service initialized")
    
    async def register_device(self, request: DeviceRegistrationRequest) -> DeviceTrustResponse:
        """Register new device for user"""
        try:
            # Generate device fingerprint
            fingerprint = await self._generate_device_fingerprint(
                request.fingerprint_data, 
                request.user_agent
            )
            
            # Check for existing device with same fingerprint
            fingerprint_hash = self._hash_fingerprint(fingerprint)
            existing_device_id = self.fingerprint_index.get(fingerprint_hash)
            
            if existing_device_id:
                # Update existing device
                device = self.devices[existing_device_id]
                device.last_seen = datetime.utcnow()
                device.login_count += 1
                
                # Update location if provided
                if request.ip_address:
                    device.last_seen_ip = request.ip_address
                    location = await self._get_location_from_ip(request.ip_address)
                    if location:
                        device.last_seen_location = location
                
                return DeviceTrustResponse(
                    success=True,
                    device_id=existing_device_id,
                    trust_level=device.trust_level,
                    risk_level=device.risk_level,
                    confidence_score=0.9,
                    is_recognized=True,
                    is_suspicious=False
                )
            
            # Create new device
            device_id = f"device_{secrets.token_urlsafe(16)}"
            
            # Determine device type
            device_type = await self._determine_device_type(request.user_agent, request.fingerprint_data)
            
            # Get location
            location = None
            if request.ip_address:
                location = await self._get_location_from_ip(request.ip_address)
            
            # Create device info
            device = DeviceInfo(
                device_id=device_id,
                user_id=request.user_id,
                device_name=request.device_name,
                device_type=device_type,
                fingerprint=fingerprint,
                trust_level=TrustLevel.LOW if request.trust_this_device else TrustLevel.UNKNOWN,
                last_seen_ip=request.ip_address,
                last_seen_location=location,
                login_count=1
            )
            
            # Store device
            self.devices[device_id] = device
            self.fingerprint_index[fingerprint_hash] = device_id
            
            # Update user devices
            if request.user_id not in self.user_devices:
                self.user_devices[request.user_id] = []
            self.user_devices[request.user_id].append(device_id)
            
            # Perform initial risk assessment
            risk_assessment = await self._assess_device_risk(device, request)
            device.risk_level = risk_assessment["risk_level"]
            
            logger.info(f"Registered new device {device_id} for user {request.user_id}")
            
            return DeviceTrustResponse(
                success=True,
                device_id=device_id,
                trust_level=device.trust_level,
                risk_level=device.risk_level,
                confidence_score=risk_assessment["confidence"],
                is_recognized=False,
                is_suspicious=risk_assessment["is_suspicious"],
                risk_factors=risk_assessment["risk_factors"],
                recommendations=risk_assessment["recommendations"]
            )
            
        except Exception as e:
            logger.error(f"Device registration failed: {e}")
            return DeviceTrustResponse(
                success=False,
                trust_level=TrustLevel.UNTRUSTED,
                risk_level=RiskLevel.HIGH,
                confidence_score=0.0,
                is_recognized=False,
                is_suspicious=True,
                risk_factors=["registration_error"],
                additional_verification_required=True
            )
    
    async def assess_device_trust(self, request: DeviceTrustRequest) -> DeviceTrustResponse:
        """Assess device trust level"""
        try:
            # Generate current fingerprint
            current_fingerprint = await self._generate_device_fingerprint(
                request.fingerprint_data,
                request.user_agent
            )
            
            fingerprint_hash = self._hash_fingerprint(current_fingerprint)
            device_id = request.device_id or self.fingerprint_index.get(fingerprint_hash)
            
            if not device_id or device_id not in self.devices:
                # Unknown device
                return DeviceTrustResponse(
                    success=True,
                    trust_level=TrustLevel.UNKNOWN,
                    risk_level=RiskLevel.HIGH,
                    confidence_score=0.0,
                    is_recognized=False,
                    is_suspicious=True,
                    risk_factors=["unknown_device"],
                    additional_verification_required=True,
                    verification_methods=["mfa", "email_verification"],
                    session_restrictions=["limited_access", "monitoring_required"]
                )
            
            device = self.devices[device_id]
            
            # Update device activity
            device.last_seen = datetime.utcnow()
            device.login_count += 1
            
            if request.ip_address:
                device.last_seen_ip = request.ip_address
                location = await self._get_location_from_ip(request.ip_address)
                if location:
                    device.last_seen_location = location
            
            # Perform comprehensive trust assessment
            trust_score = await self._calculate_trust_score(device, request)
            
            # Update trust and risk levels
            new_trust_level = self._determine_trust_level(trust_score)
            new_risk_level = self._determine_risk_level(trust_score, device)
            
            device.trust_level = new_trust_level
            device.risk_level = new_risk_level
            
            # Check for suspicious activity
            is_suspicious = await self._detect_suspicious_activity(device, request)
            
            # Generate recommendations
            recommendations = await self._generate_security_recommendations(device, trust_score)
            
            # Determine additional verification requirements
            verification_required = (
                new_trust_level in [TrustLevel.UNKNOWN, TrustLevel.UNTRUSTED] or
                new_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH, RiskLevel.CRITICAL] or
                is_suspicious
            )
            
            verification_methods = []
            session_restrictions = []
            
            if verification_required:
                verification_methods = self._get_verification_methods(new_risk_level)
                session_restrictions = self._get_session_restrictions(new_risk_level)
            
            # Record metrics
            await self.metrics_collector.record_device_trust_assessment(
                device_id=device_id,
                trust_level=new_trust_level.value,
                risk_level=new_risk_level.value,
                trust_score=trust_score,
                is_suspicious=is_suspicious
            )
            
            return DeviceTrustResponse(
                success=True,
                device_id=device_id,
                trust_level=new_trust_level,
                risk_level=new_risk_level,
                confidence_score=trust_score,
                is_recognized=True,
                is_suspicious=is_suspicious,
                risk_factors=await self._identify_risk_factors(device, request),
                recommendations=recommendations,
                additional_verification_required=verification_required,
                verification_methods=verification_methods,
                session_restrictions=session_restrictions,
                metadata={
                    "fingerprint_match": await self._compare_fingerprints(device.fingerprint, current_fingerprint),
                    "location_change": await self._detect_location_change(device, request.ip_address),
                    "behavioral_anomaly": await self._detect_behavioral_anomaly(device, request.behavioral_data)
                }
            )
            
        except Exception as e:
            logger.error(f"Device trust assessment failed: {e}")
            return DeviceTrustResponse(
                success=False,
                trust_level=TrustLevel.UNTRUSTED,
                risk_level=RiskLevel.CRITICAL,
                confidence_score=0.0,
                is_recognized=False,
                is_suspicious=True,
                risk_factors=["assessment_error"],
                additional_verification_required=True
            )
    
    async def _generate_device_fingerprint(self, fingerprint_data: Dict[str, Any], 
                                         user_agent: Optional[str]) -> DeviceFingerprint:
        """Generate comprehensive device fingerprint"""
        fingerprint_id = secrets.token_urlsafe(16)
        
        # Parse user agent
        browser_info = {}
        if user_agent:
            parsed = parse(user_agent)
            browser_info = {
                "browser": parsed.browser.family,
                "browser_version": f"{parsed.browser.version_string}",
                "platform": f"{parsed.os.family} {parsed.os.version_string}",
                "device": parsed.device.family
            }
        
        return DeviceFingerprint(
            fingerprint_id=fingerprint_id,
            user_agent=user_agent or "",
            screen_resolution=fingerprint_data.get("screen_resolution"),
            timezone=fingerprint_data.get("timezone"),
            language=fingerprint_data.get("language"),
            platform=browser_info.get("platform"),
            browser=browser_info.get("browser"),
            browser_version=browser_info.get("browser_version"),
            device_memory=fingerprint_data.get("device_memory"),
            hardware_concurrency=fingerprint_data.get("hardware_concurrency"),
            color_depth=fingerprint_data.get("color_depth"),
            pixel_ratio=fingerprint_data.get("pixel_ratio"),
            touch_support=fingerprint_data.get("touch_support"),
            webgl_vendor=fingerprint_data.get("webgl_vendor"),
            webgl_renderer=fingerprint_data.get("webgl_renderer"),
            canvas_fingerprint=fingerprint_data.get("canvas_fingerprint"),
            audio_fingerprint=fingerprint_data.get("audio_fingerprint"),
            plugins=fingerprint_data.get("plugins", []),
            fonts=fingerprint_data.get("fonts", [])
        )
    
    def _hash_fingerprint(self, fingerprint: DeviceFingerprint) -> str:
        """Generate hash of device fingerprint for indexing"""
        fingerprint_str = (
            f"{fingerprint.user_agent}|{fingerprint.screen_resolution}|"
            f"{fingerprint.timezone}|{fingerprint.language}|{fingerprint.platform}|"
            f"{fingerprint.browser}|{fingerprint.device_memory}|"
            f"{fingerprint.hardware_concurrency}|{fingerprint.webgl_vendor}|"
            f"{fingerprint.canvas_fingerprint}"
        )
        
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()
    
    async def _determine_device_type(self, user_agent: Optional[str], 
                                   fingerprint_data: Dict[str, Any]) -> DeviceType:
        """Determine device type from fingerprint data"""
        if not user_agent:
            return DeviceType.UNKNOWN
        
        parsed = parse(user_agent)
        
        if parsed.is_mobile:
            return DeviceType.MOBILE
        elif parsed.is_tablet:
            return DeviceType.TABLET
        elif parsed.is_pc:
            return DeviceType.DESKTOP
        elif "smart" in user_agent.lower() and "tv" in user_agent.lower():
            return DeviceType.SMART_TV
        else:
            return DeviceType.UNKNOWN
    
    async def _get_location_from_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get location information from IP address"""
        try:
            # Simplified geolocation - implement actual GeoIP lookup
            # This would use a real GeoIP database
            return {
                "country": "Unknown",
                "region": "Unknown", 
                "city": "Unknown",
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": "UTC"
            }
        except Exception as e:
            logger.error(f"Geolocation lookup failed: {e}")
            return None
    
    async def _assess_device_risk(self, device: DeviceInfo, 
                                request: DeviceRegistrationRequest) -> Dict[str, Any]:
        """Assess initial device risk"""
        risk_factors = []
        is_suspicious = False
        confidence = 0.5
        
        # Check IP reputation
        if request.ip_address:
            if request.ip_address in self.known_malicious_ips:
                risk_factors.append("malicious_ip")
                is_suspicious = True
            
            if await self._is_vpn_or_proxy(request.ip_address):
                risk_factors.append("vpn_proxy_usage")
        
        # Check for unusual device characteristics
        if device.fingerprint.webgl_vendor and "virtualbox" in device.fingerprint.webgl_vendor.lower():
            risk_factors.append("virtual_machine")
            is_suspicious = True
        
        # Determine risk level
        if len(risk_factors) >= 3:
            risk_level = RiskLevel.CRITICAL
        elif len(risk_factors) >= 2:
            risk_level = RiskLevel.HIGH
        elif len(risk_factors) >= 1:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Generate recommendations
        recommendations = []
        if is_suspicious:
            recommendations.extend([
                "require_additional_verification",
                "monitor_device_activity",
                "limit_session_duration"
            ])
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "is_suspicious": is_suspicious,
            "confidence": confidence,
            "recommendations": recommendations
        }
    
    async def _calculate_trust_score(self, device: DeviceInfo, 
                                   request: DeviceTrustRequest) -> float:
        """Calculate comprehensive trust score"""
        scores = {}
        
        # Fingerprint consistency
        if request.fingerprint_data:
            current_fingerprint = await self._generate_device_fingerprint(
                request.fingerprint_data, request.user_agent
            )
            fingerprint_match = await self._compare_fingerprints(device.fingerprint, current_fingerprint)
            scores["fingerprint_match"] = fingerprint_match
        else:
            scores["fingerprint_match"] = 0.5
        
        # Location consistency
        if request.ip_address and device.last_seen_location:
            location_consistency = await self._assess_location_consistency(device, request.ip_address)
            scores["location_consistency"] = location_consistency
        else:
            scores["location_consistency"] = 0.5
        
        # Behavioral consistency
        if request.behavioral_data:
            behavioral_consistency = await self._assess_behavioral_consistency(device, request.behavioral_data)
            scores["behavioral_consistency"] = behavioral_consistency
        else:
            scores["behavioral_consistency"] = 0.5
        
        # Usage patterns
        usage_score = await self._assess_usage_patterns(device)
        scores["usage_patterns"] = usage_score
        
        # Time patterns
        time_score = await self._assess_time_patterns(device)
        scores["time_patterns"] = time_score
        
        # Security history
        security_score = await self._assess_security_history(device)
        scores["security_history"] = security_score
        
        # Calculate weighted trust score
        trust_score = sum(
            scores[factor] * weight 
            for factor, weight in self.trust_weights.items()
        )
        
        return max(0.0, min(1.0, trust_score))
    
    def _determine_trust_level(self, trust_score: float) -> TrustLevel:
        """Determine trust level from score"""
        if trust_score >= 0.9:
            return TrustLevel.TRUSTED
        elif trust_score >= 0.7:
            return TrustLevel.HIGH
        elif trust_score >= 0.5:
            return TrustLevel.MEDIUM
        elif trust_score >= 0.3:
            return TrustLevel.LOW
        else:
            return TrustLevel.UNTRUSTED
    
    def _determine_risk_level(self, trust_score: float, device: DeviceInfo) -> RiskLevel:
        """Determine risk level from trust score and device history"""
        base_risk = 1.0 - trust_score
        
        # Adjust for device history
        if device.failed_attempts > 5:
            base_risk += 0.3
        
        if device.security_events:
            security_events_count = len(device.security_events)
            base_risk += min(0.5, security_events_count * 0.1)
        
        # Convert to risk level
        if base_risk >= 0.9:
            return RiskLevel.CRITICAL
        elif base_risk >= 0.7:
            return RiskLevel.VERY_HIGH
        elif base_risk >= 0.5:
            return RiskLevel.HIGH
        elif base_risk >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _compare_fingerprints(self, stored: DeviceFingerprint, 
                                  current: DeviceFingerprint) -> float:
        """Compare device fingerprints and return similarity score"""
        matches = 0
        total_checks = 0
        
        # Compare key fingerprint elements
        comparisons = [
            (stored.user_agent, current.user_agent),
            (stored.screen_resolution, current.screen_resolution),
            (stored.timezone, current.timezone),
            (stored.language, current.language),
            (stored.platform, current.platform),
            (stored.browser, current.browser),
            (stored.webgl_vendor, current.webgl_vendor),
            (stored.canvas_fingerprint, current.canvas_fingerprint)
        ]
        
        for stored_val, current_val in comparisons:
            if stored_val is not None and current_val is not None:
                total_checks += 1
                if stored_val == current_val:
                    matches += 1
        
        return matches / total_checks if total_checks > 0 else 0.0
    
    async def _detect_suspicious_activity(self, device: DeviceInfo, 
                                        request: DeviceTrustRequest) -> bool:
        """Detect suspicious device activity"""
        suspicious_indicators = []
        
        # Check for rapid location changes
        if request.ip_address and device.last_seen_ip:
            if device.last_seen_ip != request.ip_address:
                time_diff = (datetime.utcnow() - device.last_seen).total_seconds()
                if time_diff < 3600:  # Location change within 1 hour
                    suspicious_indicators.append("rapid_location_change")
        
        # Check login frequency
        if device.login_count > 50 and (datetime.utcnow() - device.first_seen).days < 1:
            suspicious_indicators.append("excessive_login_frequency")
        
        # Check for failed attempts
        if device.failed_attempts > 3:
            suspicious_indicators.append("multiple_failed_attempts")
        
        return len(suspicious_indicators) > 0
    
    async def _is_vpn_or_proxy(self, ip_address: str) -> bool:
        """Check if IP address is from VPN or proxy"""
        # Simplified VPN/proxy detection
        # In production, use actual VPN/proxy detection services
        return ip_address in self.known_vpn_ranges
    
    def _get_verification_methods(self, risk_level: RiskLevel) -> List[str]:
        """Get required verification methods based on risk level"""
        if risk_level == RiskLevel.CRITICAL:
            return ["mfa", "biometric", "admin_approval"]
        elif risk_level == RiskLevel.VERY_HIGH:
            return ["mfa", "email_verification", "sms_verification"]
        elif risk_level == RiskLevel.HIGH:
            return ["mfa", "email_verification"]
        elif risk_level == RiskLevel.MEDIUM:
            return ["email_verification"]
        else:
            return []
    
    def _get_session_restrictions(self, risk_level: RiskLevel) -> List[str]:
        """Get session restrictions based on risk level"""
        if risk_level == RiskLevel.CRITICAL:
            return ["no_access", "admin_review_required"]
        elif risk_level == RiskLevel.VERY_HIGH:
            return ["limited_access", "continuous_monitoring", "short_session"]
        elif risk_level == RiskLevel.HIGH:
            return ["limited_features", "monitoring_required"]
        elif risk_level == RiskLevel.MEDIUM:
            return ["standard_monitoring"]
        else:
            return []
    
    async def get_user_devices(self, user_id: str) -> List[DeviceInfo]:
        """Get all devices for a user"""
        device_ids = self.user_devices.get(user_id, [])
        return [self.devices[device_id] for device_id in device_ids if device_id in self.devices]
    
    async def revoke_device(self, device_id: str, reason: str = "user_request") -> bool:
        """Revoke device trust"""
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.status = DeviceStatus.SUSPENDED
                device.trust_level = TrustLevel.UNTRUSTED
                device.security_events.append({
                    "event": "device_revoked",
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                logger.info(f"Revoked device {device_id}: {reason}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Device revocation failed: {e}")
            return False


# Export service instance
device_trust_service = DeviceTrustService()

__all__ = [
    'DeviceType',
    'TrustLevel',
    'RiskLevel',
    'DeviceStatus',
    'DeviceFingerprint',
    'DeviceInfo',
    'DeviceRegistrationRequest',
    'DeviceTrustRequest',
    'DeviceTrustResponse',
    'BehavioralMetrics',
    'DeviceTrustService',
    'device_trust_service'
]