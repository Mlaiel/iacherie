"""
Biometric Authentication Database Components

Enterprise biometric authentication with template storage, verification algorithms,
liveness detection, and multi-modal biometric support for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
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
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from cryptography.fernet import Fernet
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

Base = declarative_base()
logger = logging.getLogger(__name__)


class BiometricType(Enum):
    """Biometric modality types"""
    FINGERPRINT = "fingerprint"
    FACE = "face"
    VOICE = "voice"
    IRIS = "iris"
    PALM = "palm"
    GAIT = "gait"
    SIGNATURE = "signature"
    KEYSTROKE = "keystroke"


class BiometricQuality(Enum):
    """Biometric template quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    REJECTED = "rejected"


class VerificationStatus(Enum):
    """Verification attempt status"""
    SUCCESS = "success"
    FAILURE = "failure"
    LIVENESS_FAILED = "liveness_failed"
    QUALITY_TOO_LOW = "quality_too_low"
    TEMPLATE_NOT_FOUND = "template_not_found"
    SYSTEM_ERROR = "system_error"


@dataclass
class BiometricFeatures:
    """Biometric feature vector structure"""
    feature_vector: List[float]
    quality_score: float
    extraction_algorithm: str
    template_version: str
    confidence_level: float
    liveness_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BiometricTemplate(Base):
    """Biometric template storage"""
    __tablename__ = "biometric_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    biometric_type = Column(String(50), nullable=False, index=True)
    template_name = Column(String(255), nullable=False)
    encrypted_template = Column(LargeBinary, nullable=False)
    feature_hash = Column(String(255), nullable=False, index=True)
    quality_score = Column(Integer, nullable=False)  # 0-100
    template_version = Column(String(50), nullable=False)
    extraction_algorithm = Column(String(100), nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    enrollment_device = Column(String(255), nullable=True)
    enrollment_location = Column(JSON, nullable=True)
    liveness_verified = Column(Boolean, nullable=False, default=False)
    verification_count = Column(Integer, nullable=False, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_biometric_user_type', 'user_id', 'biometric_type'),
        Index('idx_biometric_active_primary', 'is_active', 'is_primary'),
        Index('idx_biometric_quality_type', 'quality_score', 'biometric_type'),
    )


class BiometricVerification(Base):
    """Biometric verification attempts log"""
    __tablename__ = "biometric_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey('biometric_templates.id'), nullable=True)
    biometric_type = Column(String(50), nullable=False, index=True)
    verification_status = Column(String(50), nullable=False, index=True)
    match_score = Column(Integer, nullable=True)  # 0-100
    confidence_score = Column(Integer, nullable=True)  # 0-100
    liveness_score = Column(Integer, nullable=True)  # 0-100
    quality_score = Column(Integer, nullable=True)  # 0-100
    device_info = Column(JSON, nullable=True)
    location_info = Column(JSON, nullable=True)
    verification_time_ms = Column(Integer, nullable=True)
    failure_reason = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Relationships
    template = relationship("BiometricTemplate", backref="verifications")
    
    # Indexes
    __table_args__ = (
        Index('idx_verification_user_status', 'user_id', 'verification_status'),
        Index('idx_verification_created_type', 'created_at', 'biometric_type'),
        Index('idx_verification_session', 'session_id', 'created_at'),
    )


class BiometricPolicy(Base):
    """Biometric authentication policies"""
    __tablename__ = "biometric_policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_name = Column(String(255), nullable=False, unique=True)
    enabled_biometrics = Column(ARRAY(String), nullable=False)
    minimum_quality_score = Column(Integer, nullable=False, default=70)
    minimum_match_score = Column(Integer, nullable=False, default=80)
    require_liveness = Column(Boolean, nullable=False, default=True)
    minimum_liveness_score = Column(Integer, nullable=False, default=90)
    max_enrollment_attempts = Column(Integer, nullable=False, default=3)
    max_verification_attempts = Column(Integer, nullable=False, default=5)
    verification_timeout_seconds = Column(Integer, nullable=False, default=30)
    fallback_auth_enabled = Column(Boolean, nullable=False, default=True)
    multi_modal_required = Column(Boolean, nullable=False, default=False)
    anti_spoofing_enabled = Column(Boolean, nullable=False, default=True)
    template_encryption_required = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class BiometricDevice(Base):
    """Registered biometric devices"""
    __tablename__ = "biometric_devices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    device_fingerprint = Column(String(255), nullable=False, unique=True, index=True)
    device_name = Column(String(255), nullable=False)
    device_type = Column(String(100), nullable=False)  # mobile, desktop, tablet
    supported_biometrics = Column(ARRAY(String), nullable=False)
    device_capabilities = Column(JSON, nullable=True)
    security_level = Column(String(50), nullable=False, default="standard")  # basic, standard, enhanced, military
    is_trusted = Column(Boolean, nullable=False, default=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    enrollment_count = Column(Integer, nullable=False, default=0)
    verification_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_device_user_trusted', 'user_id', 'is_trusted'),
        Index('idx_device_fingerprint_active', 'device_fingerprint', 'last_seen_at'),
    )


class BiometricAuthManager:
    """Enterprise biometric authentication manager"""
    
    def __init__(self, db_session: Session, encryption_key: bytes):
        self.db = db_session
        self.fernet = Fernet(encryption_key)
        self.default_policy = self._get_default_policy()
    
    def _get_default_policy(self) -> Dict[str, Any]:
        """Get default biometric policy"""
        policy = self.db.query(BiometricPolicy).filter(
            BiometricPolicy.is_default == True
        ).first()
        
        if policy:
            return {
                "enabled_biometrics": policy.enabled_biometrics,
                "minimum_quality_score": policy.minimum_quality_score,
                "minimum_match_score": policy.minimum_match_score,
                "require_liveness": policy.require_liveness,
                "minimum_liveness_score": policy.minimum_liveness_score,
                "max_enrollment_attempts": policy.max_enrollment_attempts,
                "max_verification_attempts": policy.max_verification_attempts,
                "verification_timeout_seconds": policy.verification_timeout_seconds,
                "anti_spoofing_enabled": policy.anti_spoofing_enabled
            }
        
        # Default fallback policy
        return {
            "enabled_biometrics": ["fingerprint", "face"],
            "minimum_quality_score": 70,
            "minimum_match_score": 80,
            "require_liveness": True,
            "minimum_liveness_score": 90,
            "max_enrollment_attempts": 3,
            "max_verification_attempts": 5,
            "verification_timeout_seconds": 30,
            "anti_spoofing_enabled": True
        }
    
    def _encrypt_template(self, template_data: bytes) -> bytes:
        """Encrypt biometric template"""



        return self.fernet.encrypt(template_data)
    
    def _decrypt_template(self, encrypted_template: bytes) -> bytes:
        """Decrypt biometric template"""



        return self.fernet.decrypt(encrypted_template)
    
    def _calculate_feature_hash(self, features: BiometricFeatures) -> str:
        """Calculate hash of feature vector for indexing"""
        feature_str = json.dumps(features.feature_vector, sort_keys=True)
        return hashlib.sha256(feature_str.encode()).hexdigest()
    
    def _calculate_quality_score(self, features: BiometricFeatures) -> int:
        """Calculate overall quality score from biometric features"""
        base_quality = int(features.quality_score * 100)
        confidence_bonus = int(features.confidence_level * 10)
        liveness_bonus = int((features.liveness_score or 0) * 5)
        
        total_score = min(100, base_quality + confidence_bonus + liveness_bonus)
        return max(0, total_score)
    
    async def enroll_biometric(
        self,
        user_id: str,
        biometric_type: BiometricType,
        features: BiometricFeatures,
        device_info: Dict[str, Any],
        template_name: Optional[str] = None
    ) -> Optional[str]:
        """Enroll new biometric template"""



        try:
            # Validate quality
            quality_score = self._calculate_quality_score(features)
            if quality_score < self.default_policy["minimum_quality_score"]:
                logger.warning(f"Biometric quality too low: {quality_score}")
                return None
            
            # Check liveness if required
            if self.default_policy["require_liveness"]:
                liveness_score = (features.liveness_score or 0) * 100
                if liveness_score < self.default_policy["minimum_liveness_score"]:
                    logger.warning(f"Liveness check failed: {liveness_score}")
                    return None
            
            # Serialize and encrypt template
            template_data = json.dumps(asdict(features)).encode()
            encrypted_template = self._encrypt_template(template_data)
            
            # Create template record
            template = BiometricTemplate(
                user_id=uuid.UUID(user_id),
                biometric_type=biometric_type.value,
                template_name=template_name or f"{biometric_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                encrypted_template=encrypted_template,
                feature_hash=self._calculate_feature_hash(features),
                quality_score=quality_score,
                template_version=features.template_version,
                extraction_algorithm=features.extraction_algorithm,
                enrollment_device=device_info.get("device_fingerprint"),
                enrollment_location=device_info.get("location"),
                liveness_verified=self.default_policy["require_liveness"]
            )
            
            # Check if this should be primary template
            existing_templates = self.db.query(BiometricTemplate).filter(
                BiometricTemplate.user_id == uuid.UUID(user_id),
                BiometricTemplate.biometric_type == biometric_type.value,
                BiometricTemplate.is_active == True
            ).count()
            
            if existing_templates == 0:
                template.is_primary = True
            
            self.db.add(template)
            await self.db.commit()
            
            logger.info(f"Enrolled {biometric_type.value} biometric for user {user_id}")
            return str(template.id)
            
        except Exception as e:
            logger.error(f"Biometric enrollment failed: {e}")
            await self.db.rollback()
            return None
    
    async def verify_biometric(
        self,
        user_id: str,
        biometric_type: BiometricType,
        features: BiometricFeatures,
        device_info: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify biometric against enrolled templates"""
        verification_start = datetime.now(timezone.utc)
        
        try:
            # Get user's active templates for this biometric type
            templates = self.db.query(BiometricTemplate).filter(
                BiometricTemplate.user_id == uuid.UUID(user_id),
                BiometricTemplate.biometric_type == biometric_type.value,
                BiometricTemplate.is_active == True
            ).order_by(BiometricTemplate.is_primary.desc(), BiometricTemplate.quality_score.desc()).all()
            
            if not templates:
                await self._log_verification(
                    user_id=user_id,
                    biometric_type=biometric_type,
                    status=VerificationStatus.TEMPLATE_NOT_FOUND,
                    device_info=device_info,
                    session_id=session_id,
                    verification_time=verification_start
                )
                return {"success": False, "reason": "No enrolled templates found"}
            
            # Check input quality
            input_quality = self._calculate_quality_score(features)
            if input_quality < self.default_policy["minimum_quality_score"]:
                await self._log_verification(
                    user_id=user_id,
                    biometric_type=biometric_type,
                    status=VerificationStatus.QUALITY_TOO_LOW,
                    device_info=device_info,
                    session_id=session_id,
                    verification_time=verification_start,
                    quality_score=input_quality
                )
                return {"success": False, "reason": "Input quality too low"}
            
            # Check liveness if required
            if self.default_policy["require_liveness"]:
                liveness_score = (features.liveness_score or 0) * 100
                if liveness_score < self.default_policy["minimum_liveness_score"]:
                    await self._log_verification(
                        user_id=user_id,
                        biometric_type=biometric_type,
                        status=VerificationStatus.LIVENESS_FAILED,
                        device_info=device_info,
                        session_id=session_id,
                        verification_time=verification_start,
                        liveness_score=int(liveness_score)
                    )
                    return {"success": False, "reason": "Liveness check failed"}
            
            # Match against templates
            best_match = None
            best_score = 0
            
            for template in templates:
                try:
                    # Decrypt and load template
                    decrypted_data = self._decrypt_template(template.encrypted_template)
                    stored_features = BiometricFeatures(**json.loads(decrypted_data.decode()))
                    
                    # Calculate match score
                    match_score = self._calculate_match_score(features, stored_features)
                    
                    if match_score > best_score:
                        best_score = match_score
                        best_match = template
                        
                except Exception as e:
                    logger.error(f"Error processing template {template.id}: {e}")
                    continue
            
            # Check if best match meets threshold
            if best_score >= self.default_policy["minimum_match_score"]:
                # Successful verification
                if best_match:
                    best_match.verification_count += 1
                    best_match.last_used_at = datetime.now(timezone.utc)
                
                await self._log_verification(
                    user_id=user_id,
                    template_id=str(best_match.id) if best_match else None,
                    biometric_type=biometric_type,
                    status=VerificationStatus.SUCCESS,
                    device_info=device_info,
                    session_id=session_id,
                    verification_time=verification_start,
                    match_score=best_score,
                    quality_score=input_quality
                )
                
                await self.db.commit()
                
                return {
                    "success": True,
                    "match_score": best_score,
                    "template_id": str(best_match.id) if best_match else None,
                    "confidence": features.confidence_level
                }
            else:
                # Verification failed
                await self._log_verification(
                    user_id=user_id,
                    biometric_type=biometric_type,
                    status=VerificationStatus.FAILURE,
                    device_info=device_info,
                    session_id=session_id,
                    verification_time=verification_start,
                    match_score=best_score,
                    quality_score=input_quality,
                    failure_reason=f"Match score {best_score} below threshold {self.default_policy['minimum_match_score']}"
                )
                
                return {"success": False, "reason": "Biometric match failed", "score": best_score}
                
        except Exception as e:
            logger.error(f"Biometric verification error: {e}")
            await self._log_verification(
                user_id=user_id,
                biometric_type=biometric_type,
                status=VerificationStatus.SYSTEM_ERROR,
                device_info=device_info,
                session_id=session_id,
                verification_time=verification_start,
                failure_reason=str(e)
            )
            return {"success": False, "reason": "System error during verification"}
    
    def _calculate_match_score(self, input_features: BiometricFeatures, stored_features: BiometricFeatures) -> int:
        """Calculate biometric match score between templates"""



        try:
            # Convert feature vectors to numpy arrays
            input_vector = np.array(input_features.feature_vector)
            stored_vector = np.array(stored_features.feature_vector)
            
            # Normalize vectors
            input_norm = input_vector / np.linalg.norm(input_vector)
            stored_norm = stored_vector / np.linalg.norm(stored_vector)
            
            # Calculate cosine similarity
            similarity = np.dot(input_norm, stored_norm)
            
            # Convert to percentage score
            match_score = int((similarity + 1) * 50)  # Scale from [-1,1] to [0,100]
            
            # Apply quality weighting
            quality_weight = min(input_features.quality_score, stored_features.quality_score)
            weighted_score = int(match_score * quality_weight)
            
            return max(0, min(100, weighted_score))
            
        except Exception as e:
            logger.error(f"Match score calculation failed: {e}")
            return 0
    
    async def _log_verification(
        self,
        user_id: str,
        biometric_type: BiometricType,
        status: VerificationStatus,
        device_info: Dict[str, Any],
        verification_time: datetime,
        template_id: Optional[str] = None,
        match_score: Optional[int] = None,
        confidence_score: Optional[int] = None,
        liveness_score: Optional[int] = None,
        quality_score: Optional[int] = None,
        failure_reason: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Log biometric verification attempt"""



        try:
            elapsed_ms = int((datetime.now(timezone.utc) - verification_time).total_seconds() * 1000)
            
            verification_log = BiometricVerification(
                user_id=uuid.UUID(user_id),
                template_id=uuid.UUID(template_id) if template_id else None,
                biometric_type=biometric_type.value,
                verification_status=status.value,
                match_score=match_score,
                confidence_score=confidence_score,
                liveness_score=liveness_score,
                quality_score=quality_score,
                device_info=device_info,
                location_info=device_info.get("location"),
                verification_time_ms=elapsed_ms,
                failure_reason=failure_reason,
                ip_address=device_info.get("ip_address"),
                user_agent=device_info.get("user_agent"),
                session_id=session_id
            )
            
            self.db.add(verification_log)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log verification: {e}")
    
    async def get_user_biometrics(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's enrolled biometric templates"""



        try:
            templates = self.db.query(BiometricTemplate).filter(
                BiometricTemplate.user_id == uuid.UUID(user_id),
                BiometricTemplate.is_active == True
            ).all()
            
            result = []
            for template in templates:
                result.append({
                    "id": str(template.id),
                    "biometric_type": template.biometric_type,
                    "template_name": template.template_name,
                    "quality_score": template.quality_score,
                    "is_primary": template.is_primary,
                    "verification_count": template.verification_count,
                    "last_used_at": template.last_used_at.isoformat() if template.last_used_at else None,
                    "created_at": template.created_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get user biometrics: {e}")
            return []
    
    async def delete_biometric_template(self, user_id: str, template_id: str) -> bool:
        """Delete biometric template"""



        try:
            template = self.db.query(BiometricTemplate).filter(
                BiometricTemplate.id == uuid.UUID(template_id),
                BiometricTemplate.user_id == uuid.UUID(user_id)
            ).first()
            
            if template:
                template.is_active = False
                await self.db.commit()
                logger.info(f"Deleted biometric template {template_id} for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete biometric template: {e}")
            await self.db.rollback()
            return False
    
    async def register_device(
        self,
        user_id: str,
        device_fingerprint: str,
        device_name: str,
        device_type: str,
        supported_biometrics: List[str],
        device_capabilities: Dict[str, Any]
    ) -> bool:
        """Register biometric-capable device"""



        try:
            device = BiometricDevice(
                user_id=uuid.UUID(user_id),
                device_fingerprint=device_fingerprint,
                device_name=device_name,
                device_type=device_type,
                supported_biometrics=supported_biometrics,
                device_capabilities=device_capabilities,
                last_seen_at=datetime.now(timezone.utc)
            )
            
            self.db.add(device)
            await self.db.commit()
            
            logger.info(f"Registered biometric device for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register device: {e}")
            await self.db.rollback()
            return False


class BiometricVerification:
    """Biometric verification helper class"""
    
    @staticmethod
    def extract_face_features(image_data: bytes) -> Optional[BiometricFeatures]:
        """Extract facial features from image data"""
        # Implementation would use face recognition libraries
        # like dlib, face_recognition, or OpenCV
        pass
    
    @staticmethod
    def extract_fingerprint_features(image_data: bytes) -> Optional[BiometricFeatures]:
        """Extract fingerprint minutiae from image data"""
        # Implementation would use fingerprint libraries
        # like NIST NBIS or commercial SDKs
        pass
    
    @staticmethod
    def extract_voice_features(audio_data: bytes) -> Optional[BiometricFeatures]:
        """Extract voice features from audio data"""
        # Implementation would use speaker recognition libraries
        # like speechbrain, pyannote, or commercial SDKs
        pass
    
    @staticmethod
    def perform_liveness_detection(image_data: bytes, biometric_type: BiometricType) -> float:
        """Perform liveness detection on biometric sample"""
        # Implementation would use anti-spoofing algorithms
        # to detect if the biometric is from a live person
        pass
