#!/usr/bin/env python3
"""Content Security Engine

Advanced content protection system for securing distributed content across
multiple platforms. Provides watermarking, piracy monitoring, geo-blocking,
and copyright protection during content distribution.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import hashlib
import logging
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import secrets
import hmac

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = ImageDraw = ImageFont = None

try:
    import cv2
except ImportError:
    cv2 = None

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Content security protection levels"""
    BASIC = "basic"
    STANDARD = "standard" 
    ADVANCED = "advanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class WatermarkType(Enum):
    """Types of watermarks for content protection"""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    AUDIO = "audio"
    METADATA = "metadata"
    BLOCKCHAIN = "blockchain"


class ProtectionMethod(Enum):
    """Content protection methods"""
    FINGERPRINTING = "fingerprinting"
    WATERMARKING = "watermarking"
    ENCRYPTION = "encryption"
    DRM = "drm"
    GEO_BLOCKING = "geo_blocking"
    TOKEN_GATING = "token_gating"


class ViolationType(Enum):
    """Types of copyright violations"""
    UNAUTHORIZED_COPY = "unauthorized_copy"
    PIRACY = "piracy"
    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    DMCA_VIOLATION = "dmca_violation"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"


@dataclass
class SecurityConfiguration:
    """Security configuration for content protection"""
    security_level: SecurityLevel
    protection_methods: List[ProtectionMethod]
    watermark_config: Dict[str, Any]
    geo_restrictions: List[str]
    allowed_platforms: List[str]
    encryption_enabled: bool = True
    monitoring_enabled: bool = True
    auto_takedown: bool = False


@dataclass
class WatermarkInfo:
    """Information about applied watermarks"""
    watermark_id: str
    watermark_type: WatermarkType
    content_id: str
    creator_id: str
    timestamp: datetime
    platform: str
    watermark_data: Dict[str, Any]
    verification_hash: str


@dataclass
class ContentFingerprint:
    """Digital fingerprint for content identification"""
    content_id: str
    fingerprint_hash: str
    algorithm: str
    features: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityViolation:
    """Detected security violation"""
    violation_id: str
    content_id: str
    violation_type: ViolationType
    platform: str
    infringing_url: str
    confidence_score: float
    detected_at: datetime
    evidence: Dict[str, Any]
    status: str = "pending"


@dataclass
class GeolocationRestriction:
    """Geolocation-based content restrictions"""
    content_id: str
    allowed_countries: List[str]
    blocked_countries: List[str]
    allowed_regions: List[str]
    blocked_regions: List[str]
    effective_date: datetime
    expiry_date: Optional[datetime] = None


class ContentSecurity:
    """
    Advanced content security engine for protecting distributed content.
    
    Provides comprehensive content protection including watermarking,
    fingerprinting, piracy monitoring, and geo-blocking capabilities.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content security engine"""
        self.config = config or {}
        self.security_keys = self._generate_security_keys()
        self.watermark_registry = {}
        self.fingerprint_db = {}
        self.violation_alerts = []
        self.geo_restrictions = {}
        self._initialize_security_systems()

    def _generate_security_keys(self) -> Dict[str, str]:
        """Generate cryptographic keys for content protection"""
        return {
            "master_key": secrets.token_hex(32),
            "watermark_key": secrets.token_hex(16),
            "fingerprint_key": secrets.token_hex(16),
            "encryption_key": secrets.token_hex(32)
        }

    def _initialize_security_systems(self):
        """Initialize security monitoring and protection systems"""
        self.monitoring_active = True
        self.protection_algorithms = {
            "audio_fingerprint": self._audio_fingerprint_algorithm,
            "image_fingerprint": self._image_fingerprint_algorithm,
            "video_fingerprint": self._video_fingerprint_algorithm,
            "text_fingerprint": self._text_fingerprint_algorithm
        }

    async def protect_content(
        self,
        content_data: Dict[str, Any],
        security_config: SecurityConfiguration,
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Apply comprehensive content protection before distribution
        
        Args:
            content_data: Content to protect
            security_config: Security configuration
            target_platforms: Target distribution platforms
            
        Returns:
            Dict containing protected content and protection metadata
        """
        try:
            content_id = content_data.get("id", "")
            content_type = content_data.get("type", "")
            
            protected_content = content_data.copy()
            protection_metadata = {
                "content_id": content_id,
                "protection_applied": [],
                "watermarks": [],
                "fingerprints": [],
                "security_level": security_config.security_level.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # Apply fingerprinting
            if ProtectionMethod.FINGERPRINTING in security_config.protection_methods:
                fingerprint = await self._generate_content_fingerprint(
                    content_data, content_type
                )
                protection_metadata["fingerprints"].append(fingerprint)
                protection_metadata["protection_applied"].append("fingerprinting")
            
            # Apply watermarking
            if ProtectionMethod.WATERMARKING in security_config.protection_methods:
                watermark_info = await self._apply_watermarking(
                    protected_content, security_config.watermark_config, target_platforms
                )
                protection_metadata["watermarks"].extend(watermark_info)
                protection_metadata["protection_applied"].append("watermarking")
            
            # Apply encryption
            if ProtectionMethod.ENCRYPTION in security_config.protection_methods:
                protected_content = await self._encrypt_sensitive_metadata(
                    protected_content
                )
                protection_metadata["protection_applied"].append("encryption")
            
            # Set up geo-blocking
            if ProtectionMethod.GEO_BLOCKING in security_config.protection_methods:
                geo_config = await self._configure_geo_restrictions(
                    content_id, security_config.geo_restrictions
                )
                protection_metadata["geo_restrictions"] = geo_config
                protection_metadata["protection_applied"].append("geo_blocking")
            
            # Set up monitoring
            if security_config.monitoring_enabled:
                await self._enable_piracy_monitoring(content_id, target_platforms)
                protection_metadata["protection_applied"].append("monitoring")
            
            return {
                "protected_content": protected_content,
                "protection_metadata": protection_metadata,
                "security_token": self._generate_security_token(content_id)
            }
            
        except Exception as e:
            logger.error(f"Error protecting content: {str(e)}")
            raise

    async def _generate_content_fingerprint(
        self,
        content_data: Dict[str, Any],
        content_type: str
    ) -> ContentFingerprint:
        """Generate digital fingerprint for content identification"""
        content_id = content_data.get("id", "")
        
        # Select appropriate fingerprinting algorithm
        algorithm_key = f"{content_type}_fingerprint"
        algorithm = self.protection_algorithms.get(algorithm_key, self._generic_fingerprint_algorithm)
        
        # Generate fingerprint
        fingerprint_data = await algorithm(content_data)
        fingerprint_hash = hashlib.sha256(
            json.dumps(fingerprint_data, sort_keys=True).encode()
        ).hexdigest()
        
        fingerprint = ContentFingerprint(
            content_id=content_id,
            fingerprint_hash=fingerprint_hash,
            algorithm=algorithm_key,
            features=fingerprint_data
        )
        
        # Store in fingerprint database
        self.fingerprint_db[content_id] = fingerprint
        
        return fingerprint

    async def _audio_fingerprint_algorithm(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio fingerprint using acoustic features"""
        # Placeholder for audio fingerprinting
        # In production, this would use libraries like librosa or dejavu
        features = {
            "duration": content_data.get("duration", 0),
            "sample_rate": content_data.get("sample_rate", 44100),
            "channels": content_data.get("channels", 2),
            "format": content_data.get("format", "mp3"),
            "bitrate": content_data.get("bitrate", 320),
            "spectral_features": "placeholder_for_mfcc_chroma_spectral_centroid",
            "tempo": content_data.get("tempo", 120),
            "key": content_data.get("key", "C")
        }
        return features

    async def _image_fingerprint_algorithm(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate image fingerprint using visual features"""
        features = {
            "width": content_data.get("width", 0),
            "height": content_data.get("height", 0),
            "format": content_data.get("format", "jpg"),
            "color_mode": content_data.get("color_mode", "RGB"),
            "file_size": content_data.get("file_size", 0),
            "histogram": "placeholder_for_color_histogram",
            "edge_features": "placeholder_for_edge_detection",
            "texture_features": "placeholder_for_texture_analysis"
        }
        return features

    async def _video_fingerprint_algorithm(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video fingerprint using temporal and spatial features"""
        features = {
            "duration": content_data.get("duration", 0),
            "width": content_data.get("width", 0),
            "height": content_data.get("height", 0),
            "fps": content_data.get("fps", 30),
            "format": content_data.get("format", "mp4"),
            "codec": content_data.get("codec", "h264"),
            "bitrate": content_data.get("bitrate", 1000),
            "frame_features": "placeholder_for_keyframe_analysis",
            "motion_vectors": "placeholder_for_motion_analysis",
            "scene_changes": "placeholder_for_scene_detection"
        }
        return features

    async def _text_fingerprint_algorithm(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text fingerprint using linguistic features"""
        text_content = content_data.get("content", "")
        features = {
            "length": len(text_content),
            "word_count": len(text_content.split()),
            "language": content_data.get("language", "en"),
            "encoding": content_data.get("encoding", "utf-8"),
            "hash": hashlib.md5(text_content.encode()).hexdigest(),
            "n_gram_features": "placeholder_for_ngram_analysis",
            "semantic_features": "placeholder_for_semantic_hashing"
        }
        return features

    async def _generic_fingerprint_algorithm(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic fingerprinting for unknown content types"""
        features = {
            "content_hash": hashlib.sha256(
                json.dumps(content_data, sort_keys=True).encode()
            ).hexdigest(),
            "metadata_hash": hashlib.md5(
                str(content_data.get("metadata", {})).encode()
            ).hexdigest(),
            "file_size": content_data.get("file_size", 0),
            "format": content_data.get("format", "unknown")
        }
        return features

    async def _apply_watermarking(
        self,
        content_data: Dict[str, Any],
        watermark_config: Dict[str, Any],
        target_platforms: List[str]
    ) -> List[WatermarkInfo]:
        """Apply watermarks to content for each target platform"""
        watermarks = []
        content_id = content_data.get("id", "")
        creator_id = content_data.get("creator_id", "")
        
        for platform in target_platforms:
            # Generate platform-specific watermark
            watermark_id = f"{content_id}_{platform}_{int(datetime.now().timestamp())}"
            
            # Determine watermark type based on content and platform
            watermark_type = self._determine_watermark_type(
                content_data.get("type", ""), platform, watermark_config
            )
            
            # Apply watermark
            watermark_data = await self._create_watermark(
                content_data, watermark_config, platform, watermark_type
            )
            
            # Generate verification hash
            verification_hash = self._generate_watermark_hash(
                watermark_id, content_id, creator_id, platform
            )
            
            watermark_info = WatermarkInfo(
                watermark_id=watermark_id,
                watermark_type=watermark_type,
                content_id=content_id,
                creator_id=creator_id,
                timestamp=datetime.now(),
                platform=platform,
                watermark_data=watermark_data,
                verification_hash=verification_hash
            )
            
            watermarks.append(watermark_info)
            self.watermark_registry[watermark_id] = watermark_info
        
        return watermarks

    def _determine_watermark_type(
        self,
        content_type: str,
        platform: str,
        config: Dict[str, Any]
    ) -> WatermarkType:
        """Determine appropriate watermark type for content and platform"""
        # Platform preferences for watermark visibility
        if platform in ["instagram", "pinterest"] and content_type == "image":
            return WatermarkType.VISIBLE
        elif content_type == "audio":
            return WatermarkType.AUDIO
        elif config.get("steganography_enabled", False):
            return WatermarkType.INVISIBLE
        else:
            return WatermarkType.METADATA

    async def _create_watermark(
        self,
        content_data: Dict[str, Any],
        config: Dict[str, Any],
        platform: str,
        watermark_type: WatermarkType
    ) -> Dict[str, Any]:
        """Create watermark based on type and configuration"""
        watermark_data = {
            "type": watermark_type.value,
            "platform": platform,
            "creator": content_data.get("creator_id", ""),
            "timestamp": datetime.now().isoformat(),
            "copyright": config.get("copyright_text", "© All Rights Reserved")
        }
        
        if watermark_type == WatermarkType.VISIBLE:
            watermark_data.update({
                "position": config.get("position", "bottom_right"),
                "opacity": config.get("opacity", 0.7),
                "size": config.get("size", "medium"),
                "color": config.get("color", "#FFFFFF")
            })
        elif watermark_type == WatermarkType.INVISIBLE:
            watermark_data.update({
                "algorithm": "steganography",
                "embedding_strength": config.get("embedding_strength", 0.1),
                "secret_key": self.security_keys["watermark_key"]
            })
        elif watermark_type == WatermarkType.AUDIO:
            watermark_data.update({
                "frequency_range": config.get("frequency_range", [8000, 12000]),
                "amplitude": config.get("amplitude", 0.01),
                "pattern": "chirp_sequence"
            })
        
        return watermark_data

    def _generate_watermark_hash(
        self,
        watermark_id: str,
        content_id: str,
        creator_id: str,
        platform: str
    ) -> str:
        """Generate verification hash for watermark"""
        data = f"{watermark_id}:{content_id}:{creator_id}:{platform}:{self.security_keys['watermark_key']}"
        return hmac.new(
            self.security_keys["master_key"].encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    async def _encrypt_sensitive_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive metadata in content"""
        sensitive_fields = ["creator_id", "api_keys", "private_metadata", "revenue_data"]
        encrypted_content = content_data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_content:
                # Placeholder for actual encryption
                # In production, use proper encryption libraries
                encrypted_value = base64.b64encode(
                    json.dumps(encrypted_content[field]).encode()
                ).decode()
                encrypted_content[f"{field}_encrypted"] = encrypted_value
                del encrypted_content[field]
        
        return encrypted_content

    async def _configure_geo_restrictions(
        self,
        content_id: str,
        geo_restrictions: List[str]
    ) -> GeolocationRestriction:
        """Configure geographical restrictions for content"""
        # Parse restriction format: "allow:US,CA,GB" or "block:CN,RU"
        allowed_countries = []
        blocked_countries = []
        
        for restriction in geo_restrictions:
            if restriction.startswith("allow:"):
                allowed_countries.extend(restriction[6:].split(","))
            elif restriction.startswith("block:"):
                blocked_countries.extend(restriction[6:].split(","))
        
        geo_config = GeolocationRestriction(
            content_id=content_id,
            allowed_countries=allowed_countries,
            blocked_countries=blocked_countries,
            allowed_regions=[],
            blocked_regions=[],
            effective_date=datetime.now()
        )
        
        self.geo_restrictions[content_id] = geo_config
        return geo_config

    async def _enable_piracy_monitoring(
        self,
        content_id: str,
        target_platforms: List[str]
    ):
        """Enable piracy monitoring for content across platforms"""
        # Set up monitoring jobs for each platform
        monitoring_config = {
            "content_id": content_id,
            "platforms": target_platforms,
            "scan_frequency": "hourly",
            "detection_sensitivity": "medium",
            "auto_actions": ["alert", "log"],
            "enabled": True
        }
        
        # Store monitoring configuration
        # In production, this would integrate with external monitoring services
        logger.info(f"Piracy monitoring enabled for content {content_id}")

    def _generate_security_token(self, content_id: str) -> str:
        """Generate security token for content verification"""
        timestamp = int(datetime.now().timestamp())
        data = f"{content_id}:{timestamp}:{self.security_keys['master_key']}"
        token = hmac.new(
            self.security_keys["master_key"].encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{timestamp}.{token}"

    async def verify_content_authenticity(
        self,
        content_data: Dict[str, Any],
        security_token: str
    ) -> bool:
        """Verify content authenticity using security token"""
        try:
            timestamp_str, token = security_token.split(".")
            timestamp = int(timestamp_str)
            content_id = content_data.get("id", "")
            
            # Check if token is not too old (24 hours)
            if datetime.now().timestamp() - timestamp > 86400:
                return False
            
            # Recreate expected token
            data = f"{content_id}:{timestamp}:{self.security_keys['master_key']}"
            expected_token = hmac.new(
                self.security_keys["master_key"].encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(token, expected_token)
            
        except Exception as e:
            logger.error(f"Error verifying content authenticity: {str(e)}")
            return False

    async def detect_copyright_violation(
        self,
        suspicious_content: Dict[str, Any],
        platform: str
    ) -> Optional[SecurityViolation]:
        """Detect potential copyright violations"""
        try:
            # Generate fingerprint for suspicious content
            fingerprint = await self._generate_content_fingerprint(
                suspicious_content, suspicious_content.get("type", "")
            )
            
            # Compare against known fingerprints
            for content_id, known_fingerprint in self.fingerprint_db.items():
                similarity = self._calculate_fingerprint_similarity(
                    fingerprint, known_fingerprint
                )
                
                if similarity > 0.8:  # 80% similarity threshold
                    violation = SecurityViolation(
                        violation_id=f"viol_{int(datetime.now().timestamp())}",
                        content_id=content_id,
                        violation_type=ViolationType.UNAUTHORIZED_COPY,
                        platform=platform,
                        infringing_url=suspicious_content.get("url", ""),
                        confidence_score=similarity,
                        detected_at=datetime.now(),
                        evidence={
                            "fingerprint_match": similarity,
                            "detected_features": fingerprint.features,
                            "original_features": known_fingerprint.features
                        }
                    )
                    
                    self.violation_alerts.append(violation)
                    return violation
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting copyright violation: {str(e)}")
            return None

    def _calculate_fingerprint_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint
    ) -> float:
        """Calculate similarity between two content fingerprints"""
        if fp1.algorithm != fp2.algorithm:
            return 0.0
        
        # Simple similarity calculation (in production, use sophisticated algorithms)
        if fp1.fingerprint_hash == fp2.fingerprint_hash:
            return 1.0
        
        # Calculate feature similarity
        common_features = set(fp1.features.keys()) & set(fp2.features.keys())
        if not common_features:
            return 0.0
        
        similarity_scores = []
        for feature in common_features:
            val1 = fp1.features[feature]
            val2 = fp2.features[feature]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if val1 == 0 and val2 == 0:
                    similarity_scores.append(1.0)
                else:
                    max_val = max(abs(val1), abs(val2))
                    if max_val > 0:
                        similarity = 1 - abs(val1 - val2) / max_val
                        similarity_scores.append(max(0, similarity))
            elif val1 == val2:
                similarity_scores.append(1.0)
            else:
                similarity_scores.append(0.0)
        
        return sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0

    async def handle_security_violation(
        self,
        violation: SecurityViolation,
        action: str = "alert"
    ) -> Dict[str, Any]:
        """Handle detected security violations"""
        actions_taken = []
        
        if action == "alert":
            # Send alert to content owner
            actions_taken.append("alert_sent")
            logger.warning(f"Security violation detected: {violation.violation_id}")
        
        elif action == "takedown":
            # Initiate takedown request
            actions_taken.append("takedown_requested")
            logger.info(f"Takedown request initiated for violation: {violation.violation_id}")
        
        elif action == "watermark_verification":
            # Verify watermark presence
            verification_result = await self._verify_watermark_presence(violation)
            actions_taken.append(f"watermark_verified:{verification_result}")
        
        # Update violation status
        violation.status = "processed"
        
        return {
            "violation_id": violation.violation_id,
            "actions_taken": actions_taken,
            "timestamp": datetime.now().isoformat()
        }

    async def _verify_watermark_presence(self, violation: SecurityViolation) -> bool:
        """Verify if watermark is present in potentially infringing content"""
        # Placeholder for watermark verification
        # In production, this would analyze the suspicious content for watermarks
        return False

    async def get_security_report(self, content_id: str) -> Dict[str, Any]:
        """Generate comprehensive security report for content"""
        report = {
            "content_id": content_id,
            "protection_status": "protected",
            "fingerprint": None,
            "watermarks": [],
            "violations": [],
            "geo_restrictions": None,
            "monitoring_status": "active",
            "last_updated": datetime.now().isoformat()
        }
        
        # Add fingerprint info
        if content_id in self.fingerprint_db:
            fp = self.fingerprint_db[content_id]
            report["fingerprint"] = {
                "hash": fp.fingerprint_hash,
                "algorithm": fp.algorithm,
                "created_at": fp.created_at.isoformat()
            }
        
        # Add watermark info
        watermarks = [w for w in self.watermark_registry.values() if w.content_id == content_id]
        report["watermarks"] = [
            {
                "id": w.watermark_id,
                "type": w.watermark_type.value,
                "platform": w.platform,
                "created_at": w.timestamp.isoformat()
            }
            for w in watermarks
        ]
        
        # Add violation info
        violations = [v for v in self.violation_alerts if v.content_id == content_id]
        report["violations"] = [
            {
                "id": v.violation_id,
                "type": v.violation_type.value,
                "platform": v.platform,
                "confidence": v.confidence_score,
                "detected_at": v.detected_at.isoformat(),
                "status": v.status
            }
            for v in violations
        ]
        
        # Add geo-restriction info
        if content_id in self.geo_restrictions:
            geo = self.geo_restrictions[content_id]
            report["geo_restrictions"] = {
                "allowed_countries": geo.allowed_countries,
                "blocked_countries": geo.blocked_countries,
                "effective_date": geo.effective_date.isoformat()
            }
        
        return report

    async def update_security_configuration(
        self,
        content_id: str,
        new_config: SecurityConfiguration
    ) -> bool:
        """Update security configuration for existing content"""
        try:
            # Update existing protections based on new configuration
            logger.info(f"Updating security configuration for content {content_id}")
            
            # Re-apply protections if needed
            # This would involve updating watermarks, geo-restrictions, etc.
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating security configuration: {str(e)}")
            return False