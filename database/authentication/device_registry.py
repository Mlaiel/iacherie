"""
Device Registry Database Components

Enterprise device management with fingerprinting, trust establishment, and security
monitoring for multi-format creator authentication across devices and platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import uuid
import json
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import geoip2.database
from user_agents import parse as parse_user_agent
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

Base = declarative_base()
logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Device type classifications"""
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    GAMING_CONSOLE = "gaming_console"
    IOT_DEVICE = "iot_device"
    WEARABLE = "wearable"
    EMBEDDED = "embedded"


class DeviceStatus(Enum):
    """Device status states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"
    PENDING_VERIFICATION = "pending_verification"
    COMPROMISED = "compromised"


class TrustLevel(Enum):
    """Device trust levels"""
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"
    COMPROMISED = "compromised"


@dataclass
class DeviceCapabilities:
    """Device capabilities structure"""
    biometric_support: List[str]
    secure_element: bool
    hardware_encryption: bool
    trusted_execution: bool
    camera_available: bool
    microphone_available: bool
    gps_available: bool
    bluetooth_version: Optional[str] = None
    wifi_standards: List[str] = field(default_factory=list)
    screen_resolution: Optional[str] = None
    os_security_features: List[str] = field(default_factory=list)


class DeviceFingerprint(Base):
    """Device fingerprinting data"""
    __tablename__ = "device_fingerprints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    fingerprint_hash = Column(String(255), nullable=False, unique=True, index=True)
    device_name = Column(String(255), nullable=False)
    device_type = Column(String(50), nullable=False, index=True)
    os_name = Column(String(100), nullable=False)
    os_version = Column(String(100), nullable=False)
    browser_name = Column(String(100), nullable=True)
    browser_version = Column(String(100), nullable=True)
    user_agent = Column(Text, nullable=False)
    screen_resolution = Column(String(50), nullable=True)
    timezone = Column(String(100), nullable=True)
    language = Column(String(20), nullable=True)
    hardware_info = Column(JSON, nullable=True)
    network_info = Column(JSON, nullable=True)
    capabilities = Column(JSON, nullable=True)
    fingerprint_score = Column(Integer, nullable=False, default=0)  # Uniqueness score 0-100
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_fingerprint_user_type', 'user_id', 'device_type'),
        Index('idx_fingerprint_os_browser', 'os_name', 'browser_name'),
        Index('idx_fingerprint_score', 'fingerprint_score'),
    )


class TrustedDevice(Base):
    """Trusted device registry"""
    __tablename__ = "trusted_devices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('device_fingerprints.id'), nullable=False)
    device_nickname = Column(String(255), nullable=False)
    trust_level = Column(String(50), nullable=False, default="unknown", index=True)
    device_status = Column(String(50), nullable=False, default="active", index=True)
    verification_method = Column(String(100), nullable=False)  # email, sms, biometric, manual
    verification_token = Column(String(255), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    first_seen_ip = Column(String(45), nullable=True)
    last_seen_ip = Column(String(45), nullable=True)
    location_info = Column(JSON, nullable=True)
    risk_score = Column(Integer, nullable=False, default=0)  # 0-100
    failed_attempts = Column(Integer, nullable=False, default=0)
    successful_logins = Column(Integer, nullable=False, default=0)
    is_primary_device = Column(Boolean, nullable=False, default=False)
    auto_approval_enabled = Column(Boolean, nullable=False, default=False)
    notifications_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    fingerprint = relationship("DeviceFingerprint", backref="trusted_devices")
    
    # Indexes
    __table_args__ = (
        Index('idx_trusted_user_status', 'user_id', 'device_status'),
        Index('idx_trusted_trust_level', 'trust_level', 'verified_at'),
        Index('idx_trusted_risk_score', 'risk_score', 'last_seen_at'),
    )


class DeviceActivity(Base):
    """Device activity tracking"""
    __tablename__ = "device_activity"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey('trusted_devices.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    activity_type = Column(String(100), nullable=False, index=True)  # login, logout, api_call, content_upload
    activity_result = Column(String(50), nullable=False, index=True)  # success, failure, blocked, suspicious
    ip_address = Column(String(45), nullable=True)
    location_info = Column(JSON, nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    request_headers = Column(JSON, nullable=True)
    risk_indicators = Column(JSON, nullable=True)
    anomaly_score = Column(Integer, nullable=True)  # 0-100
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    device = relationship("TrustedDevice", backref="activities")
    
    # Indexes
    __table_args__ = (
        Index('idx_activity_device_type', 'device_id', 'activity_type'),
        Index('idx_activity_user_result', 'user_id', 'activity_result'),
        Index('idx_activity_created_anomaly', 'created_at', 'anomaly_score'),
    )


class DeviceSecurityAlert(Base):
    """Device security alerts"""
    __tablename__ = "device_security_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey('trusted_devices.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)  # low, medium, high, critical
    alert_title = Column(String(255), nullable=False)
    alert_description = Column(Text, nullable=False)
    risk_indicators = Column(JSON, nullable=False)
    recommended_actions = Column(JSON, nullable=True)
    is_resolved = Column(Boolean, nullable=False, default=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String(255), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    device = relationship("TrustedDevice", backref="security_alerts")
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_device_severity', 'device_id', 'severity'),
        Index('idx_alert_user_resolved', 'user_id', 'is_resolved'),
        Index('idx_alert_type_created', 'alert_type', 'created_at'),
    )


class DeviceRegistry:
    """Enterprise device registry and management"""
    
    def __init__(self, db_session: Session, geoip_db_path: Optional[str] = None):
        self.db = db_session
        self.geoip_reader = None
        if geoip_db_path:
            try:
                self.geoip_reader = geoip2.database.Reader(geoip_db_path)
            except Exception as e:
                logger.warning(f"Failed to initialize GeoIP database: {e}")
    
    def _generate_device_fingerprint(
        self,
        user_agent: str,
        ip_address: str,
        additional_headers: Dict[str, str]
    ) -> str:
        """Generate unique device fingerprint"""
        # Parse user agent
        ua = parse_user_agent(user_agent)
        
        # Collect fingerprinting data
        fingerprint_data = {
            "user_agent": user_agent,
            "browser": f"{ua.browser.family} {ua.browser.version_string}",
            "os": f"{ua.os.family} {ua.os.version_string}",
            "device": f"{ua.device.family} {ua.device.brand} {ua.device.model}",
            "accept_language": additional_headers.get("Accept-Language", ""),
            "accept_encoding": additional_headers.get("Accept-Encoding", ""),
            "accept": additional_headers.get("Accept", ""),
            "dnt": additional_headers.get("DNT", ""),
            "connection": additional_headers.get("Connection", ""),
        }
        
        # Create hash
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()
    
    def _get_location_info(self, ip_address: str) -> Dict[str, Any]:
        """Get location information from IP address"""
        if not self.geoip_reader:
            return {}
        
        try:
            response = self.geoip_reader.city(ip_address)
            return {
                "country": response.country.name,
                "country_code": response.country.iso_code,
                "city": response.city.name,
                "region": response.subdivisions.most_specific.name,
                "postal_code": response.postal.code,
                "latitude": float(response.location.latitude) if response.location.latitude else None,
                "longitude": float(response.location.longitude) if response.location.longitude else None,
                "timezone": response.location.time_zone,
                "accuracy_radius": response.location.accuracy_radius
            }
        except Exception as e:
            logger.warning(f"Failed to get location for IP {ip_address}: {e}")
            return {}
    
    def _calculate_fingerprint_score(self, fingerprint_data: Dict[str, Any]) -> int:
        """Calculate uniqueness score for device fingerprint"""
        # Simple scoring based on available data points
        score = 0
        
        # User agent components
        if fingerprint_data.get("browser"):
            score += 20
        if fingerprint_data.get("os"):
            score += 20
        if fingerprint_data.get("device"):
            score += 15
        
        # Headers
        if fingerprint_data.get("accept_language"):
            score += 10
        if fingerprint_data.get("accept_encoding"):
            score += 5
        if fingerprint_data.get("screen_resolution"):
            score += 10
        if fingerprint_data.get("timezone"):
            score += 10
        if fingerprint_data.get("hardware_info"):
            score += 10
        
        return min(100, score)
    
    async def register_device(
        self,
        user_id: str,
        user_agent: str,
        ip_address: str,
        request_headers: Dict[str, str],
        device_name: Optional[str] = None,
        capabilities: Optional[DeviceCapabilities] = None
    ) -> Tuple[str, bool]:
        """Register new device or update existing"""
        try:
            # Generate fingerprint
            fingerprint_hash = self._generate_device_fingerprint(
                user_agent, ip_address, request_headers
            )
            
            # Check if device already exists
            existing_fingerprint = self.db.query(DeviceFingerprint).filter(
                DeviceFingerprint.fingerprint_hash == fingerprint_hash
            ).first()
            
            if existing_fingerprint:
                # Update last seen
                existing_fingerprint.updated_at = datetime.now(timezone.utc)
                await self.db.commit()
                return str(existing_fingerprint.id), False
            
            # Parse user agent
            ua = parse_user_agent(user_agent)
            
            # Get location info
            location_info = self._get_location_info(ip_address)
            
            # Create device fingerprint
            fingerprint_data = {
                "browser": f"{ua.browser.family} {ua.browser.version_string}",
                "os": f"{ua.os.family} {ua.os.version_string}",
                "device": f"{ua.device.family}",
                "screen_resolution": request_headers.get("Screen-Resolution"),
                "timezone": request_headers.get("Timezone"),
                "language": request_headers.get("Accept-Language", "").split(",")[0]
            }
            
            fingerprint = DeviceFingerprint(
                user_id=uuid.UUID(user_id),
                fingerprint_hash=fingerprint_hash,
                device_name=device_name or f"{ua.device.family} {ua.os.family}",
                device_type=self._determine_device_type(ua).value,
                os_name=ua.os.family,
                os_version=ua.os.version_string,
                browser_name=ua.browser.family,
                browser_version=ua.browser.version_string,
                user_agent=user_agent,
                screen_resolution=request_headers.get("Screen-Resolution"),
                timezone=request_headers.get("Timezone"),
                language=request_headers.get("Accept-Language", "").split(",")[0],
                hardware_info=request_headers.get("Hardware-Info", {}),
                network_info={"ip_address": ip_address, "location": location_info},
                capabilities=asdict(capabilities) if capabilities else {},
                fingerprint_score=self._calculate_fingerprint_score(fingerprint_data)
            )
            
            self.db.add(fingerprint)
            await self.db.commit()
            
            logger.info(f"Registered new device fingerprint for user {user_id}")
            return str(fingerprint.id), True
            
        except Exception as e:
            logger.error(f"Failed to register device: {e}")
            await self.db.rollback()
            raise
    
    def _determine_device_type(self, ua) -> DeviceType:
        """Determine device type from user agent"""
        if ua.is_mobile:
            return DeviceType.MOBILE
        elif ua.is_tablet:
            return DeviceType.TABLET
        elif ua.is_pc:
            return DeviceType.DESKTOP
        else:
            return DeviceType.DESKTOP  # Default fallback
    
    async def establish_device_trust(
        self,
        user_id: str,
        fingerprint_id: str,
        verification_method: str,
        device_nickname: str,
        ip_address: str,
        verification_token: Optional[str] = None
    ) -> str:
        """Establish trust relationship with device"""
        try:
            # Get location info
            location_info = self._get_location_info(ip_address)
            
            # Create trusted device entry
            trusted_device = TrustedDevice(
                user_id=uuid.UUID(user_id),
                fingerprint_id=uuid.UUID(fingerprint_id),
                device_nickname=device_nickname,
                trust_level=TrustLevel.MEDIUM.value,  # Start with medium trust
                verification_method=verification_method,
                verification_token=verification_token,
                verified_at=datetime.now(timezone.utc) if verification_method != "pending" else None,
                first_seen_ip=ip_address,
                last_seen_ip=ip_address,
                last_seen_at=datetime.now(timezone.utc),
                location_info=location_info
            )
            
            # Check if this is the first device for user
            existing_devices = self.db.query(TrustedDevice).filter(
                TrustedDevice.user_id == uuid.UUID(user_id)
            ).count()
            
            if existing_devices == 0:
                trusted_device.is_primary_device = True
                trusted_device.trust_level = TrustLevel.HIGH.value
                trusted_device.auto_approval_enabled = True
            
            self.db.add(trusted_device)
            await self.db.commit()
            
            logger.info(f"Established device trust for user {user_id}")
            return str(trusted_device.id)
            
        except Exception as e:
            logger.error(f"Failed to establish device trust: {e}")
            await self.db.rollback()
            raise
    
    async def verify_device_trust(
        self,
        user_id: str,
        fingerprint_hash: str,
        ip_address: str,
        activity_type: str
    ) -> Dict[str, Any]:
        """Verify device trust and calculate risk"""
        try:
            # Find device fingerprint
            fingerprint = self.db.query(DeviceFingerprint).filter(
                DeviceFingerprint.fingerprint_hash == fingerprint_hash,
                DeviceFingerprint.user_id == uuid.UUID(user_id)
            ).first()
            
            if not fingerprint:
                # Unknown device
                await self._log_device_activity(
                    user_id=user_id,
                    device_id=None,
                    activity_type=activity_type,
                    activity_result="blocked",
                    ip_address=ip_address,
                    risk_indicators={"reason": "unknown_device"},
                    anomaly_score=100
                )
                return {
                    "trusted": False,
                    "trust_level": "unknown",
                    "risk_score": 100,
                    "requires_verification": True,
                    "reason": "Unknown device"
                }
            
            # Find trusted device
            trusted_device = self.db.query(TrustedDevice).filter(
                TrustedDevice.fingerprint_id == fingerprint.id,
                TrustedDevice.device_status == DeviceStatus.ACTIVE.value
            ).first()
            
            if not trusted_device:
                # Device not trusted
                await self._log_device_activity(
                    user_id=user_id,
                    device_id=None,
                    activity_type=activity_type,
                    activity_result="pending_verification",
                    ip_address=ip_address,
                    risk_indicators={"reason": "device_not_trusted"},
                    anomaly_score=80
                )
                return {
                    "trusted": False,
                    "trust_level": "unknown",
                    "risk_score": 80,
                    "requires_verification": True,
                    "reason": "Device not trusted"
                }
            
            # Calculate risk score
            risk_score = await self._calculate_device_risk(trusted_device, ip_address)
            
            # Update device activity
            trusted_device.last_seen_at = datetime.now(timezone.utc)
            trusted_device.last_seen_ip = ip_address
            trusted_device.successful_logins += 1
            
            # Log activity
            await self._log_device_activity(
                user_id=user_id,
                device_id=str(trusted_device.id),
                activity_type=activity_type,
                activity_result="success",
                ip_address=ip_address,
                risk_indicators={"risk_score": risk_score},
                anomaly_score=risk_score
            )
            
            await self.db.commit()
            
            return {
                "trusted": True,
                "trust_level": trusted_device.trust_level,
                "risk_score": risk_score,
                "requires_verification": risk_score > 70,
                "device_id": str(trusted_device.id),
                "device_nickname": trusted_device.device_nickname
            }
            
        except Exception as e:
            logger.error(f"Device trust verification failed: {e}")
            return {
                "trusted": False,
                "trust_level": "unknown",
                "risk_score": 100,
                "requires_verification": True,
                "reason": "System error"
            }
    
    async def _calculate_device_risk(self, device: TrustedDevice, current_ip: str) -> int:
        """Calculate device risk score"""
        risk_score = 0
        
        # Base risk from device trust level
        trust_risk = {
            "unknown": 80,
            "low": 60,
            "medium": 30,
            "high": 10,
            "verified": 5,
            "compromised": 100
        }
        risk_score += trust_risk.get(device.trust_level, 80)
        
        # IP address change risk
        if device.last_seen_ip and device.last_seen_ip != current_ip:
            risk_score += 20
        
        # Time since last seen risk
        if device.last_seen_at:
            days_since_seen = (datetime.now(timezone.utc) - device.last_seen_at).days
            if days_since_seen > 30:
                risk_score += 25
            elif days_since_seen > 7:
                risk_score += 10
        
        # Failed attempts risk
        if device.failed_attempts > 0:
            risk_score += min(30, device.failed_attempts * 5)
        
        # Recent security alerts
        recent_alerts = self.db.query(DeviceSecurityAlert).filter(
            DeviceSecurityAlert.device_id == device.id,
            DeviceSecurityAlert.is_resolved == False,
            DeviceSecurityAlert.created_at > datetime.now(timezone.utc) - timedelta(days=7)
        ).count()
        
        if recent_alerts > 0:
            risk_score += min(40, recent_alerts * 15)
        
        return min(100, max(0, risk_score))
    
    async def _log_device_activity(
        self,
        user_id: str,
        activity_type: str,
        activity_result: str,
        ip_address: str,
        device_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_headers: Optional[Dict[str, str]] = None,
        risk_indicators: Optional[Dict[str, Any]] = None,
        anomaly_score: Optional[int] = None
    ):
        """Log device activity"""
        try:
            location_info = self._get_location_info(ip_address)
            
            activity = DeviceActivity(
                device_id=uuid.UUID(device_id) if device_id else None,
                user_id=uuid.UUID(user_id),
                activity_type=activity_type,
                activity_result=activity_result,
                ip_address=ip_address,
                location_info=location_info,
                user_agent=request_headers.get("User-Agent") if request_headers else None,
                session_id=session_id,
                request_headers=request_headers,
                risk_indicators=risk_indicators,
                anomaly_score=anomaly_score
            )
            
            self.db.add(activity)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log device activity: {e}")
    
    async def create_security_alert(
        self,
        device_id: str,
        user_id: str,
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        risk_indicators: Dict[str, Any],
        recommended_actions: Optional[List[str]] = None
    ) -> str:
        """Create security alert for device"""
        try:
            alert = DeviceSecurityAlert(
                device_id=uuid.UUID(device_id),
                user_id=uuid.UUID(user_id),
                alert_type=alert_type,
                severity=severity,
                alert_title=title,
                alert_description=description,
                risk_indicators=risk_indicators,
                recommended_actions=recommended_actions or []
            )
            
            self.db.add(alert)
            await self.db.commit()
            
            logger.warning(f"Created {severity} security alert for device {device_id}")
            return str(alert.id)
            
        except Exception as e:
            logger.error(f"Failed to create security alert: {e}")
            await self.db.rollback()
            raise
    
    async def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's trusted devices"""
        try:
            devices = self.db.query(TrustedDevice).join(DeviceFingerprint).filter(
                TrustedDevice.user_id == uuid.UUID(user_id),
                TrustedDevice.device_status != DeviceStatus.BLOCKED.value
            ).all()
            
            result = []
            for device in devices:
                result.append({
                    "id": str(device.id),
                    "device_nickname": device.device_nickname,
                    "device_type": device.fingerprint.device_type,
                    "os_name": device.fingerprint.os_name,
                    "browser_name": device.fingerprint.browser_name,
                    "trust_level": device.trust_level,
                    "device_status": device.device_status,
                    "is_primary_device": device.is_primary_device,
                    "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
                    "last_seen_ip": device.last_seen_ip,
                    "location_info": device.location_info,
                    "successful_logins": device.successful_logins,
                    "risk_score": device.risk_score,
                    "created_at": device.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get user devices: {e}")
            return []
    
    async def revoke_device_trust(self, user_id: str, device_id: str, reason: str) -> bool:
        """Revoke trust for a device"""
        try:
            device = self.db.query(TrustedDevice).filter(
                TrustedDevice.id == uuid.UUID(device_id),
                TrustedDevice.user_id == uuid.UUID(user_id)
            ).first()
            
            if device:
                device.device_status = DeviceStatus.BLOCKED.value
                device.trust_level = TrustLevel.COMPROMISED.value
                
                # Create security alert
                await self.create_security_alert(
                    device_id=device_id,
                    user_id=user_id,
                    alert_type="device_revoked",
                    severity="high",
                    title="Device Trust Revoked",
                    description=f"Trust revoked for device: {reason}",
                    risk_indicators={"revocation_reason": reason}
                )
                
                await self.db.commit()
                logger.info(f"Revoked trust for device {device_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke device trust: {e}")
            await self.db.rollback()
            return False
