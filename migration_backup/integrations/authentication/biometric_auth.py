# -*- coding: utf-8 -*-
"""
IA Chéries Platform - Enterprise Biometric Authentication
Advanced biometric authentication system with multiple modalities
Author: IA Chéries Team
Version: 2.0.0
Date: 2024
"""

import logging
import json
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
import secrets
import time

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class BiometricType(Enum):
    """Types of biometric authentication"""
    FINGERPRINT = "fingerprint"
    FACE_RECOGNITION = "face_recognition"
    IRIS_SCAN = "iris_scan"
    VOICE_RECOGNITION = "voice_recognition"
    PALM_PRINT = "palm_print"
    RETINA_SCAN = "retina_scan"
    BEHAVIORAL = "behavioral"
    KEYSTROKE_DYNAMICS = "keystroke_dynamics"
    SIGNATURE = "signature"

class AuthenticationResult(Enum):
    """Biometric authentication results"""
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY_REQUIRED = "retry_required"
    QUALITY_TOO_LOW = "quality_too_low"
    NO_MATCH = "no_match"
    TIMEOUT = "timeout"
    ERROR = "error"

class BiometricQuality(Enum):
    """Quality levels for biometric data"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"

@dataclass
class BiometricTemplate:
    """Biometric template data structure"""
    id: str
    user_id: str
    biometric_type: BiometricType
    template_data: str  # Encrypted and encoded template
    quality_score: float  # 0.0 - 1.0
    quality_level: BiometricQuality
    enrollment_date: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BiometricAuthAttempt:
    """Biometric authentication attempt record"""
    id: str
    user_id: str
    biometric_type: BiometricType
    result: AuthenticationResult
    confidence_score: float  # 0.0 - 1.0
    quality_score: float  # 0.0 - 1.0
    template_id: Optional[str] = None
    attempt_time: datetime = field(default_factory=datetime.now)
    processing_time_ms: float = 0.0
    device_info: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None

@dataclass
class BiometricDevice:
    """Biometric device configuration"""
    id: str
    name: str
    device_type: str
    supported_biometrics: List[BiometricType]
    manufacturer: str
    model: str
    firmware_version: str
    is_certified: bool = True
    is_active: bool = True
    last_calibration: Optional[datetime] = None
    configuration: Dict[str, Any] = field(default_factory=dict)

class BiometricAuthenticator:
    """Enterprise Biometric Authentication System"""
    
    def __init__(self):
        """Initialize biometric authenticator"""
        self.templates: Dict[str, BiometricTemplate] = {}
        self.user_templates: Dict[str, List[str]] = {}  # user_id -> template_ids
        self.auth_attempts: List[BiometricAuthAttempt] = []
        self.devices: Dict[str, BiometricDevice] = {}
        self._lock = threading.RLock()
        self._attempt_counter = 0
        
        # Quality thresholds
        self.quality_thresholds = {
            BiometricType.FINGERPRINT: 0.7,
            BiometricType.FACE_RECOGNITION: 0.6,
            BiometricType.IRIS_SCAN: 0.8,
            BiometricType.VOICE_RECOGNITION: 0.5,
            BiometricType.PALM_PRINT: 0.7,
            BiometricType.RETINA_SCAN: 0.8,
            BiometricType.BEHAVIORAL: 0.4,
            BiometricType.KEYSTROKE_DYNAMICS: 0.3,
            BiometricType.SIGNATURE: 0.5
        }
        
        # Confidence thresholds for authentication
        self.auth_thresholds = {
            BiometricType.FINGERPRINT: 0.8,
            BiometricType.FACE_RECOGNITION: 0.75,
            BiometricType.IRIS_SCAN: 0.9,
            BiometricType.VOICE_RECOGNITION: 0.7,
            BiometricType.PALM_PRINT: 0.8,
            BiometricType.RETINA_SCAN: 0.9,
            BiometricType.BEHAVIORAL: 0.6,
            BiometricType.KEYSTROKE_DYNAMICS: 0.5,
            BiometricType.SIGNATURE: 0.7
        }
        
        # Initialize demo devices
        self._initialize_demo_devices()
        
        logger.info("🔎 Biometric Authenticator initialized successfully")
    
    def _initialize_demo_devices(self):
        """Initialize demo biometric devices"""
        demo_devices = [
            BiometricDevice(
                id="fp_scanner_001",
                name="Primary Fingerprint Scanner",
                device_type="fingerprint_scanner",
                supported_biometrics=[BiometricType.FINGERPRINT],
                manufacturer="SecureBio Inc.",
                model="FB-2000X",
                firmware_version="2.1.4",
                configuration={"scan_timeout": 5, "quality_threshold": 0.7}
            ),
            BiometricDevice(
                id="face_cam_001",
                name="AI Face Recognition Camera",
                device_type="face_camera",
                supported_biometrics=[BiometricType.FACE_RECOGNITION],
                manufacturer="VisionTech Corp",
                model="VT-Face-Pro",
                firmware_version="1.8.2",
                configuration={"detection_threshold": 0.75, "liveness_check": True}
            ),
            BiometricDevice(
                id="iris_scanner_001",
                name="Professional Iris Scanner",
                device_type="iris_scanner",
                supported_biometrics=[BiometricType.IRIS_SCAN],
                manufacturer="IrisTech Solutions",
                model="IS-Pro-3000",
                firmware_version="3.0.1",
                configuration={"scan_distance": "10-25cm", "dual_eye": True}
            ),
            BiometricDevice(
                id="voice_mic_001",
                name="Voice Recognition Microphone",
                device_type="voice_recorder",
                supported_biometrics=[BiometricType.VOICE_RECOGNITION],
                manufacturer="AudioSecure Ltd",
                model="AS-Voice-Auth",
                firmware_version="1.5.0",
                configuration={"sample_rate": 16000, "noise_cancellation": True}
            )
        ]
        
        for device in demo_devices:
            self.devices[device.id] = device
        
        logger.info(f"📱 Initialized {len(demo_devices)} demo biometric devices")
    
    def enroll_biometric(self, user_id: str, biometric_type: BiometricType,
                        biometric_data: str, device_id: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Enroll biometric template for user"""
        try:
            with self._lock:
                # Validate input
                if not user_id or not biometric_data:
                    return False, "Invalid user ID or biometric data"
                
                # Check device capability
                if device_id and device_id in self.devices:
                    device = self.devices[device_id]
                    if biometric_type not in device.supported_biometrics:
                        return False, f"Device {device_id} does not support {biometric_type.value}"
                
                # Simulate quality assessment
                quality_score, quality_level = self._assess_quality(biometric_data, biometric_type)
                
                # Check if quality meets threshold
                threshold = self.quality_thresholds.get(biometric_type, 0.5)
                if quality_score < threshold:
                    return False, f"Biometric quality too low: {quality_score:.2f} < {threshold}"
                
                # Generate template ID
                template_id = f"tmpl_{biometric_type.value}_{user_id}_{int(time.time())}"
                
                # Encrypt and encode template data
                encrypted_template = self._encrypt_template(biometric_data)
                
                # Create template
                template = BiometricTemplate(
                    id=template_id,
                    user_id=user_id,
                    biometric_type=biometric_type,
                    template_data=encrypted_template,
                    quality_score=quality_score,
                    quality_level=quality_level,
                    metadata=metadata or {}
                )
                
                # Store template
                self.templates[template_id] = template
                
                # Update user template mapping
                if user_id not in self.user_templates:
                    self.user_templates[user_id] = []
                self.user_templates[user_id].append(template_id)
                
                logger.info(f"✅ Enrolled {biometric_type.value} template for user {user_id}: {template_id}")
                return True, template_id
                
        except Exception as e:
            logger.error(f"❌ Error enrolling biometric: {str(e)}")
            return False, f"Enrollment error: {str(e)}"
    
    def authenticate(self, user_id: str, biometric_type: BiometricType,
                    biometric_data: str, device_id: Optional[str] = None) -> BiometricAuthAttempt:
        """Authenticate user using biometric data"""
        start_time = time.time()
        
        try:
            with self._lock:
                self._attempt_counter += 1
                attempt_id = f"auth_{self._attempt_counter}_{int(time.time())}"
                
                # Assess quality of provided biometric
                quality_score, quality_level = self._assess_quality(biometric_data, biometric_type)
                
                # Check quality threshold
                threshold = self.quality_thresholds.get(biometric_type, 0.5)
                if quality_score < threshold:
                    attempt = BiometricAuthAttempt(
                        id=attempt_id,
                        user_id=user_id,
                        biometric_type=biometric_type,
                        result=AuthenticationResult.QUALITY_TOO_LOW,
                        confidence_score=0.0,
                        quality_score=quality_score,
                        processing_time_ms=(time.time() - start_time) * 1000,
                        error_details=f"Quality {quality_score:.2f} below threshold {threshold}"
                    )
                    self.auth_attempts.append(attempt)
                    return attempt
                
                # Get user templates
                user_template_ids = self.user_templates.get(user_id, [])
                if not user_template_ids:
                    attempt = BiometricAuthAttempt(
                        id=attempt_id,
                        user_id=user_id,
                        biometric_type=biometric_type,
                        result=AuthenticationResult.NO_MATCH,
                        confidence_score=0.0,
                        quality_score=quality_score,
                        processing_time_ms=(time.time() - start_time) * 1000,
                        error_details="No enrolled templates found"
                    )
                    self.auth_attempts.append(attempt)
                    return attempt
                
                # Find matching templates of same type
                matching_templates = [
                    self.templates[tid] for tid in user_template_ids
                    if tid in self.templates and 
                    self.templates[tid].biometric_type == biometric_type and
                    self.templates[tid].is_active
                ]
                
                if not matching_templates:
                    attempt = BiometricAuthAttempt(
                        id=attempt_id,
                        user_id=user_id,
                        biometric_type=biometric_type,
                        result=AuthenticationResult.NO_MATCH,
                        confidence_score=0.0,
                        quality_score=quality_score,
                        processing_time_ms=(time.time() - start_time) * 1000,
                        error_details=f"No {biometric_type.value} templates found"
                    )
                    self.auth_attempts.append(attempt)
                    return attempt
                
                # Perform matching against templates
                best_match = None
                best_confidence = 0.0
                
                for template in matching_templates:
                    confidence = self._match_template(biometric_data, template)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = template
                
                # Determine authentication result
                auth_threshold = self.auth_thresholds.get(biometric_type, 0.7)
                
                if best_confidence >= auth_threshold:
                    result = AuthenticationResult.SUCCESS
                    # Update template usage
                    if best_match:
                        best_match.last_used = datetime.now()
                        best_match.usage_count += 1
                else:
                    result = AuthenticationResult.NO_MATCH
                
                # Create attempt record
                attempt = BiometricAuthAttempt(
                    id=attempt_id,
                    user_id=user_id,
                    biometric_type=biometric_type,
                    result=result,
                    confidence_score=best_confidence,
                    quality_score=quality_score,
                    template_id=best_match.id if best_match else None,
                    processing_time_ms=(time.time() - start_time) * 1000,
                    device_info={"device_id": device_id} if device_id else {}
                )
                
                self.auth_attempts.append(attempt)
                
                logger.info(f"🔍 Biometric auth attempt: {user_id} {biometric_type.value} = {result.value} (confidence: {best_confidence:.2f})")
                return attempt
                
        except Exception as e:
            logger.error(f"❌ Error in biometric authentication: {str(e)}")
            attempt = BiometricAuthAttempt(
                id=f"auth_error_{int(time.time())}",
                user_id=user_id,
                biometric_type=biometric_type,
                result=AuthenticationResult.ERROR,
                confidence_score=0.0,
                quality_score=0.0,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_details=str(e)
            )
            self.auth_attempts.append(attempt)
            return attempt
    
    def _assess_quality(self, biometric_data: str, biometric_type: BiometricType) -> Tuple[float, BiometricQuality]:
        """Assess quality of biometric data"""
        try:
            # Simulate quality assessment based on data characteristics
            data_length = len(biometric_data)
            
            # Simple quality scoring based on data size and type
            base_score = 0.5
            
            if biometric_type == BiometricType.FINGERPRINT:
                # Longer data generally indicates better quality for fingerprints
                base_score += min(data_length / 1000, 0.4)
            elif biometric_type == BiometricType.FACE_RECOGNITION:
                # Face recognition quality depends on image resolution
                base_score += min(data_length / 2000, 0.3)
            elif biometric_type == BiometricType.IRIS_SCAN:
                # Iris scans need high resolution
                base_score += min(data_length / 1500, 0.4)
            elif biometric_type == BiometricType.VOICE_RECOGNITION:
                # Voice quality depends on sample rate and duration
                base_score += min(data_length / 800, 0.3)
            
            # Add some randomness to simulate real quality assessment
            import random
            random.seed(hash(biometric_data) % 1000)
            quality_score = min(base_score + random.uniform(-0.1, 0.1), 1.0)
            quality_score = max(quality_score, 0.0)
            
            # Determine quality level
            if quality_score >= 0.9:
                quality_level = BiometricQuality.EXCELLENT
            elif quality_score >= 0.7:
                quality_level = BiometricQuality.GOOD
            elif quality_score >= 0.5:
                quality_level = BiometricQuality.FAIR
            elif quality_score >= 0.3:
                quality_level = BiometricQuality.POOR
            else:
                quality_level = BiometricQuality.UNUSABLE
            
            return quality_score, quality_level
            
        except Exception:
            return 0.0, BiometricQuality.UNUSABLE
    
    def _encrypt_template(self, template_data: str) -> str:
        """Encrypt biometric template data"""
        try:
            # Simple encryption using hash for demo purposes
            # In production, use proper encryption
            salt = secrets.token_hex(16)
            hashed = hashlib.pbkdf2_hmac('sha256', template_data.encode(), salt.encode(), 100000)
            encrypted = base64.b64encode(salt.encode() + hashed).decode()
            return encrypted
        except Exception:
            return base64.b64encode(template_data.encode()).decode()
    
    def _match_template(self, biometric_data: str, template: BiometricTemplate) -> float:
        """Match biometric data against stored template"""
        try:
            # Simulate template matching
            # In production, this would use sophisticated biometric matching algorithms
            
            # Simple similarity scoring based on data characteristics
            data_hash = hashlib.sha256(biometric_data.encode()).hexdigest()
            template_hash = hashlib.sha256(template.template_data.encode()).hexdigest()
            
            # Count matching characters in hash (simple similarity)
            matches = sum(1 for a, b in zip(data_hash, template_hash) if a == b)
            similarity = matches / len(data_hash)
            
            # Adjust based on template quality
            confidence = similarity * template.quality_score
            
            # Add some biometric-type specific adjustments
            if template.biometric_type == BiometricType.FINGERPRINT:
                confidence *= 1.1  # Fingerprints are generally more reliable
            elif template.biometric_type == BiometricType.BEHAVIORAL:
                confidence *= 0.8  # Behavioral biometrics are less stable
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.0
    
    def get_user_biometrics(self, user_id: str) -> List[BiometricTemplate]:
        """Get all biometric templates for a user"""
        try:
            with self._lock:
                template_ids = self.user_templates.get(user_id, [])
                templates = [self.templates[tid] for tid in template_ids 
                           if tid in self.templates]
                return templates
        except Exception as e:
            logger.error(f"❌ Error getting user biometrics: {str(e)}")
            return []
    
    def remove_biometric(self, user_id: str, template_id: str) -> bool:
        """Remove biometric template"""
        try:
            with self._lock:
                if template_id not in self.templates:
                    return False
                
                template = self.templates[template_id]
                if template.user_id != user_id:
                    return False
                
                # Remove template
                del self.templates[template_id]
                
                # Update user mapping
                if user_id in self.user_templates:
                    self.user_templates[user_id] = [
                        tid for tid in self.user_templates[user_id] if tid != template_id
                    ]
                
                logger.info(f"✅ Removed biometric template: {template_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error removing biometric: {str(e)}")
            return False
    
    def get_authentication_history(self, user_id: Optional[str] = None, 
                                  hours: int = 24) -> List[BiometricAuthAttempt]:
        """Get authentication history with optional filtering"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            filtered_attempts = [
                attempt for attempt in self.auth_attempts
                if attempt.attempt_time >= cutoff_time
            ]
            
            if user_id:
                filtered_attempts = [
                    attempt for attempt in filtered_attempts
                    if attempt.user_id == user_id
                ]
            
            # Sort by attempt time (newest first)
            filtered_attempts.sort(key=lambda x: x.attempt_time, reverse=True)
            return filtered_attempts
            
        except Exception as e:
            logger.error(f"❌ Error getting authentication history: {str(e)}")
            return []
    
    def get_biometric_statistics(self) -> Dict[str, Any]:
        """Get biometric system statistics"""
        try:
            with self._lock:
                total_templates = len(self.templates)
                active_templates = sum(1 for t in self.templates.values() if t.is_active)
                
                # Count by biometric type
                type_counts = {}
                for biometric_type in BiometricType:
                    type_counts[biometric_type.value] = sum(
                        1 for t in self.templates.values() 
                        if t.biometric_type == biometric_type and t.is_active
                    )
                
                # Recent authentication stats
                recent_attempts = self.get_authentication_history(hours=24)
                successful_auths = sum(1 for a in recent_attempts 
                                     if a.result == AuthenticationResult.SUCCESS)
                
                return {
                    "total_templates": total_templates,
                    "active_templates": active_templates,
                    "enrolled_users": len(self.user_templates),
                    "templates_by_type": type_counts,
                    "total_devices": len(self.devices),
                    "active_devices": sum(1 for d in self.devices.values() if d.is_active),
                    "recent_auth_attempts": len(recent_attempts),
                    "recent_successful_auths": successful_auths,
                    "recent_success_rate": (successful_auths / len(recent_attempts) * 100) 
                                          if recent_attempts else 0
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting biometric statistics: {str(e)}")
            return {}
    
    def register_device(self, device: BiometricDevice) -> bool:
        """Register new biometric device"""
        try:
            with self._lock:
                self.devices[device.id] = device
                logger.info(f"✅ Registered biometric device: {device.name} ({device.id})")
                return True
        except Exception as e:
            logger.error(f"❌ Error registering device: {str(e)}")
            return False
    
    def cleanup_old_attempts(self, days: int = 90):
        """Clean up old authentication attempts"""
        try:
            with self._lock:
                cutoff_time = datetime.now() - timedelta(days=days)
                initial_count = len(self.auth_attempts)
                
                self.auth_attempts = [
                    attempt for attempt in self.auth_attempts
                    if attempt.attempt_time >= cutoff_time
                ]
                
                cleaned_count = initial_count - len(self.auth_attempts)
                if cleaned_count > 0:
                    logger.info(f"🧹 Cleaned up {cleaned_count} old auth attempts (>{days} days)")
                    
        except Exception as e:
            logger.error(f"❌ Error cleaning up old attempts: {str(e)}")

# Create global instance
biometric_authenticator = BiometricAuthenticator()

# Export main classes and instance
__all__ = [
    'BiometricAuthenticator',
    'BiometricTemplate',
    'BiometricAuthAttempt',
    'BiometricDevice',
    'BiometricType',
    'AuthenticationResult',
    'BiometricQuality',
    'biometric_authenticator'
]