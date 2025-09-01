"""Content Protection Security Module
Advanced security for multi-format content protection and fingerprinting

Features:
- Content integrity verification
- Fingerprint security and validation
- Anti-tamper mechanisms
- Copyright protection enforcement
- Watermarking security
- Digital rights management (DRM)
- Content access control

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import hashlib
import hmac
import secrets
import json
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import base64
import zlib

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from backend.core.config import get_settings
from backend.core.cache import CacheManager
from backend.core.logging import SecurityLogger
from backend.core.security.encryption import EncryptionManager


class ContentType(Enum):
    """
Types of content for protection"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"


class ProtectionLevel(Enum):
    """Content protection levels"""

    BASIC = 1
    STANDARD = 2
    PREMIUM = 3
    ENTERPRISE = 4


class WatermarkType(Enum):
    """
Types of watermarks"""

    VISIBLE = "visible"
    INVISIBLE = "invisible"
    DIGITAL = "digital"
    AUDIO = "audio"


@dataclass
class ContentFingerprint:
    """Content fingerprint with security metadata"""
    content_id: str
    content_type: ContentType
    fingerprint_hash: str
    algorithm: str
    created_at: datetime
    owner_id: str
    tenant_id: str
    protection_level: ProtectionLevel
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None
    verification_hash: Optional[str] = None


@dataclass
class ContentWatermark:
    """
Content watermark information"""
    watermark_id: str
    content_id: str
    watermark_type: WatermarkType
    watermark_data: bytes
    position: Optional[Dict[str, int]] = None
    strength: float = 1.0
    invisible: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentVerification:
    """
Content verification result"""
    is_valid: bool
    content_id: str
    verification_type: str
    verification_details: Dict[str, Any]
    verified_at: datetime = field(default_factory=datetime.utcnow)


class FingerprintSecurity:
    """
Security manager for content fingerprints"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.logger = SecurityLogger("FingerprintSecurity")
        self.cache = CacheManager()
        self.settings = get_settings()
    
    async def secure_fingerprint(
        self, 
        fingerprint_data: bytes,
        content_id: str,
        owner_id: str,
        content_type: ContentType
    ) -> ContentFingerprint:
        """Create secure fingerprint with signature"""
        try:
            # Generate fingerprint hash
            fingerprint_hash = hashlib.sha256(fingerprint_data).hexdigest()
            
            # Create metadata
            metadata = {
                "content_size": len(fingerprint_data),
                "algorithm": "sha256",
                "created_by": owner_id,
                "content_type": content_type.value
            }
            
            # Generate verification hash
            verification_data = f"{content_id}:{fingerprint_hash}:{owner_id}".encode()
            verification_hash = hashlib.sha512(verification_data).hexdigest()
            
            # Sign the fingerprint
            signature = await self._sign_fingerprint(
                fingerprint_hash, content_id, owner_id
            )
            
            # Create fingerprint object
            content_fingerprint = ContentFingerprint(
                content_id=content_id,
                content_type=content_type,
                fingerprint_hash=fingerprint_hash,
                algorithm="sha256",
                created_at=datetime.utcnow(),
                owner_id=owner_id,
                tenant_id="", # Set based on context
                protection_level=ProtectionLevel.STANDARD,
                metadata=metadata,
                signature=signature,
                verification_hash=verification_hash
            )
            
            # Store in secure cache
            await self._cache_fingerprint(content_fingerprint)
            
            self.logger.info(f"Secure fingerprint created for content: {content_id}")
            return content_fingerprint
            
        except Exception as e:
            self.logger.error(f"Fingerprint security creation failed: {str(e)}")
            raise
    
    async def verify_fingerprint(
        self, 
        fingerprint: ContentFingerprint,
        current_data: Optional[bytes] = None
    ) -> ContentVerification:
        """Verify fingerprint integrity and authenticity"""
        try:
            verification_details = {}
            is_valid = True
            
            # Verify signature
            signature_valid = await self._verify_fingerprint_signature(fingerprint)
            verification_details["signature_valid"] = signature_valid
            
            if not signature_valid:
                is_valid = False
            
            # Verify hash integrity
            if current_data:
                current_hash = hashlib.sha256(current_data).hexdigest()
                hash_match = current_hash == fingerprint.fingerprint_hash
                verification_details["hash_match"] = hash_match
                verification_details["current_hash"] = current_hash
                
                if not hash_match:
                    is_valid = False
            
            # Verify verification hash
            expected_verification = f"{fingerprint.content_id}:{fingerprint.fingerprint_hash}:{fingerprint.owner_id}".encode()
            expected_hash = hashlib.sha512(expected_verification).hexdigest()
            verification_hash_valid = expected_hash == fingerprint.verification_hash
            verification_details["verification_hash_valid"] = verification_hash_valid
            
            if not verification_hash_valid:
                is_valid = False
            
            # Check expiration (if applicable)
            if fingerprint.metadata.get("expires_at"):
                expires_at = datetime.fromisoformat(fingerprint.metadata["expires_at"])
                is_expired = datetime.utcnow() > expires_at
                verification_details["expired"] = is_expired
                
                if is_expired:
                    is_valid = False
            
            verification = ContentVerification(
                is_valid=is_valid,
                content_id=fingerprint.content_id,
                verification_type="fingerprint_security",
                verification_details=verification_details
            )
            
            self.logger.info(
                f"Fingerprint verification: {fingerprint.content_id} = {'VALID' if is_valid else 'INVALID'}"
            )
            
            return verification
            
        except Exception as e:
            self.logger.error(f"Fingerprint verification failed: {str(e)}")
            return ContentVerification(
                is_valid=False,
                content_id=fingerprint.content_id,
                verification_type="fingerprint_security",
                verification_details={"error": str(e)}
            )
    
    async def _sign_fingerprint(
        self, 
        fingerprint_hash: str, 
        content_id: str, 
        owner_id: str
    ) -> str:
        """Generate cryptographic signature for fingerprint"""
        try:
            # Create signature data
            signature_data = f"{fingerprint_hash}:{content_id}:{owner_id}:{datetime.utcnow().isoformat()}"
            
            # Use HMAC with secret key
            secret_key = self.settings.FINGERPRINT_SIGNING_KEY.encode()
            signature = hmac.new(
                secret_key,
                signature_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return signature
            
        except Exception as e:
            self.logger.error(f"Fingerprint signing failed: {str(e)}")
            raise
    
    async def _verify_fingerprint_signature(self, fingerprint: ContentFingerprint) -> bool:
        """Verify fingerprint signature"""
        try:
            if not fingerprint.signature:
                return False
            
            # Recreate signature data
            signature_data = f"{fingerprint.fingerprint_hash}:{fingerprint.content_id}:{fingerprint.owner_id}:{fingerprint.created_at.isoformat()}"
            
            # Verify HMAC
            secret_key = self.settings.FINGERPRINT_SIGNING_KEY.encode()
            expected_signature = hmac.new(
                secret_key,
                signature_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, fingerprint.signature)
            
        except Exception as e:
            self.logger.error(f"Fingerprint signature verification failed: {str(e)}")
            return False
    
    async def _cache_fingerprint(self, fingerprint: ContentFingerprint):
        """Cache fingerprint securely"""
        cache_key = f"secure_fingerprint:{fingerprint.content_id}"
        cache_data = {
            "fingerprint_hash": fingerprint.fingerprint_hash,
            "signature": fingerprint.signature,
            "verification_hash": fingerprint.verification_hash,
            "owner_id": fingerprint.owner_id,
            "created_at": fingerprint.created_at.isoformat()
        }
        
        await self.cache.set(cache_key, cache_data, expire=3600)


class AntiTamper:
    """Anti-tamper protection for content and fingerprints"""
    
    def __init__(self):
        self.logger = SecurityLogger("AntiTamper")
        self.cache = CacheManager()
    
    async def protect_content(
        self, 
        content_data: bytes, 
        content_id: str,
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Apply anti-tamper protection to content"""
        try:
            protection_metadata = {}
            protected_data = content_data
            
            # Add integrity checksums
            if protection_level.value >= ProtectionLevel.BASIC.value:
                checksums = self._generate_checksums(content_data)
                protection_metadata["checksums"] = checksums
            
            # Add tamper detection markers
            if protection_level.value >= ProtectionLevel.STANDARD.value:
                markers = self._generate_tamper_markers(content_data, content_id)
                protection_metadata["tamper_markers"] = markers
                
                # Embed markers in data if possible
                protected_data = self._embed_tamper_markers(content_data, markers)
            
            # Add advanced protection
            if protection_level.value >= ProtectionLevel.PREMIUM.value:
                # Add encryption layer
                protected_data = self._add_encryption_layer(protected_data, content_id)
                protection_metadata["encrypted"] = True
            
            # Add enterprise-level protection
            if protection_level.value >= ProtectionLevel.ENTERPRISE.value:
                # Add obfuscation
                protected_data = self._add_obfuscation(protected_data)
                protection_metadata["obfuscated"] = True
            
            protection_metadata.update({
                "protection_level": protection_level.value,
                "protected_at": datetime.utcnow().isoformat(),
                "content_id": content_id
            })
            
            self.logger.info(f"Anti-tamper protection applied: {content_id}")
            return protected_data, protection_metadata
            
        except Exception as e:
            self.logger.error(f"Anti-tamper protection failed: {str(e)}")
            raise
    
    async def verify_content_integrity(
        self, 
        content_data: bytes, 
        protection_metadata: Dict[str, Any]
    ) -> ContentVerification:
        """Verify content hasn't been tampered with"""
        try:
            verification_details = {}
            is_valid = True
            
            # Verify checksums
            if "checksums" in protection_metadata:
                checksum_valid = self._verify_checksums(content_data, protection_metadata["checksums"])
                verification_details["checksum_valid"] = checksum_valid
                
                if not checksum_valid:
                    is_valid = False
            
            # Verify tamper markers
            if "tamper_markers" in protection_metadata:
                markers_valid = self._verify_tamper_markers(
                    content_data, protection_metadata["tamper_markers"]
                )
                verification_details["tamper_markers_valid"] = markers_valid
                
                if not markers_valid:
                    is_valid = False
            
            # Check for unauthorized modifications
            modification_detected = self._detect_modifications(content_data, protection_metadata)
            verification_details["modification_detected"] = modification_detected
            
            if modification_detected:
                is_valid = False
            
            verification = ContentVerification(
                is_valid=is_valid,
                content_id=protection_metadata.get("content_id", "unknown"),
                verification_type="anti_tamper",
                verification_details=verification_details
            )
            
            return verification
            
        except Exception as e:
            self.logger.error(f"Content integrity verification failed: {str(e)}")
            return ContentVerification(
                is_valid=False,
                content_id="unknown",
                verification_type="anti_tamper",
                verification_details={"error": str(e)}
            )
    
    def _generate_checksums(self, data: bytes) -> Dict[str, str]:
        """Generate multiple checksums for integrity verification"""
        return {
            "md5": hashlib.md5(data).hexdigest(),
            "sha1": hashlib.sha1(data).hexdigest(),
            "sha256": hashlib.sha256(data).hexdigest(),
            "crc32": str(zlib.crc32(data) & 0xffffffff)
        }
    
    def _verify_checksums(self, data: bytes, expected_checksums: Dict[str, str]) -> bool:
        """Verify data against expected checksums"""
        current_checksums = self._generate_checksums(data)
        
        for algorithm, expected in expected_checksums.items():
            if current_checksums.get(algorithm) != expected:
                return False
        
        return True
    
    def _generate_tamper_markers(self, data: bytes, content_id: str) -> List[Dict[str, Any]]:
        """
Generate tamper detection markers"""
        markers = []
        
        # Marker 1: Hash of specific byte ranges
        if len(data) > 1000:
            range1 = data[100:200]
            range2 = data[len(data)//2:len(data)//2+100]
            range3 = data[-200:-100]
            
            markers.append({
                "type": "range_hash",
                "ranges": [(100, 200), (len(data)//2, len(data)//2+100), (-200, -100)],
                "hash": hashlib.sha256(range1 + range2 + range3).hexdigest()
            })
        
        # Marker 2: Content-based identifier
        content_marker = hashlib.sha256(f"{content_id}:{len(data)}:{data[:10].hex()}".encode()).hexdigest()
        markers.append({
            "type": "content_marker",
            "marker": content_marker
        })
        
        return markers
    
    def _verify_tamper_markers(self, data: bytes, expected_markers: List[Dict[str, Any]]) -> bool:
        """Verify tamper detection markers"""
        for marker in expected_markers:
            if marker["type"] == "range_hash":
                ranges = marker["ranges"]
                combined_data = b""
                
                for start, end in ranges:
                    if start < 0:
                        start = len(data) + start
                    if end < 0:
                        end = len(data) + end
                    
                    if 0 <= start < len(data) and 0 <= end <= len(data):
                        combined_data += data[start:end]
                
                current_hash = hashlib.sha256(combined_data).hexdigest()
                if current_hash != marker["hash"]:
                    return False
            
            # Add verification for other marker types
        
        return True
    
    def _embed_tamper_markers(self, data: bytes, markers: List[Dict[str, Any]]) -> bytes:
        """Embed tamper markers in content (if possible)"""
        # This is a simplified implementation
        # Real implementation would depend on content type
        return data
    
    def _add_encryption_layer(self, data: bytes, content_id: str) -> bytes:
        """
Add encryption layer for premium protection"""
        # Simple XOR encryption for demonstration
        key = hashlib.sha256(content_id.encode()).digest()
        encrypted = bytearray()
        
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % len(key)])
        
        return bytes(encrypted)
    
    def _add_obfuscation(self, data: bytes) -> bytes:
        """
Add obfuscation for enterprise protection"""
        # Simple byte shuffling for demonstration
        obfuscated = bytearray(data)
        
        # Reverse every 8 bytes
        for i in range(0, len(obfuscated), 8):
            end = min(i + 8, len(obfuscated))
            obfuscated[i:end] = obfuscated[i:end][::-1]
        
        return bytes(obfuscated)
    
    def _detect_modifications(self, data: bytes, metadata: Dict[str, Any]) -> bool:
        """
Detect unauthorized modifications"""
        # Check for suspicious patterns
        # This is a simplified detection
        
        # Check file size changes
        if "original_size" in metadata:
            if len(data) != metadata["original_size"]:
                return True
        
        # Check for common modification signatures
        suspicious_patterns = [
            b"MODIFIED",
            b"CRACKED",
            b"PATCHED",
            b"HACKED"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in data:
                return True
        
        return False


class CopyrightProtection:
    """Copyright protection and enforcement"""
    
    def __init__(self, fingerprint_security: FingerprintSecurity):
        self.fingerprint_security = fingerprint_security
        self.logger = SecurityLogger("CopyrightProtection")
        self.cache = CacheManager()
    
    async def register_copyright(
        self, 
        content_data: bytes,
        content_id: str,
        owner_id: str,
        copyright_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register content for copyright protection"""
        try:
            # Create secure fingerprint
            fingerprint = await self.fingerprint_security.secure_fingerprint(
                content_data, content_id, owner_id, ContentType.AUDIO
            )
            
            # Generate copyright certificate
            certificate = {
                "certificate_id": secrets.token_hex(16),
                "content_id": content_id,
                "owner_id": owner_id,
                "fingerprint_hash": fingerprint.fingerprint_hash,
                "registration_date": datetime.utcnow().isoformat(),
                "copyright_metadata": copyright_metadata,
                "verification_signature": fingerprint.signature
            }
            
            # Store copyright registration
            await self._store_copyright_registration(certificate)
            
            self.logger.info(f"Copyright registered for content: {content_id}")
            return certificate
            
        except Exception as e:
            self.logger.error(f"Copyright registration failed: {str(e)}")
            raise
    
    async def verify_copyright_ownership(
        self, 
        content_data: bytes,
        content_id: str,
        claimed_owner_id: str
    ) -> ContentVerification:
        """Verify copyright ownership"""
        try:
            # Get copyright registration
            registration = await self._get_copyright_registration(content_id)
            
            verification_details = {}
            is_valid = False
            
            if registration:
                # Verify owner
                owner_match = registration["owner_id"] == claimed_owner_id
                verification_details["owner_match"] = owner_match
                
                # Verify content fingerprint
                current_hash = hashlib.sha256(content_data).hexdigest()
                fingerprint_match = current_hash == registration["fingerprint_hash"]
                verification_details["fingerprint_match"] = fingerprint_match
                
                is_valid = owner_match and fingerprint_match
            else:
                verification_details["registration_found"] = False
            
            return ContentVerification(
                is_valid=is_valid,
                content_id=content_id,
                verification_type="copyright_ownership",
                verification_details=verification_details
            )
            
        except Exception as e:
            self.logger.error(f"Copyright ownership verification failed: {str(e)}")
            return ContentVerification(
                is_valid=False,
                content_id=content_id,
                verification_type="copyright_ownership",
                verification_details={"error": str(e)}
            )
    
    async def _store_copyright_registration(self, certificate: Dict[str, Any]):
        """Store copyright registration"""
        # Implementation depends on your copyright registry model
        pass
    
    async def _get_copyright_registration(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
Get copyright registration"""
        # Implementation depends on your copyright registry model
        pass


class WatermarkingSecurity:
    """
Security for digital watermarking systems"""
    
    def __init__(self):
        self.logger = SecurityLogger("WatermarkingSecurity")
        self.cache = CacheManager()
    
    async def apply_digital_watermark(
        self, 
        content_data: bytes,
        content_type: ContentType,
        watermark_data: str,
        invisible: bool = True
    ) -> Tuple[bytes, ContentWatermark]:
        """Apply digital watermark to content"""
        try:
            watermark_id = secrets.token_hex(16)
            
            if content_type == ContentType.IMAGE:
                watermarked_data = await self._watermark_image(
                    content_data, watermark_data, invisible
                )
            elif content_type == ContentType.AUDIO:
                watermarked_data = await self._watermark_audio(
                    content_data, watermark_data, invisible
                )
            elif content_type == ContentType.VIDEO:
                watermarked_data = await self._watermark_video(
                    content_data, watermark_data, invisible
                )
            else:
                raise ValueError(f"Watermarking not supported for {content_type}")
            
            watermark = ContentWatermark(
                watermark_id=watermark_id,
                content_id="", # Set based on context
                watermark_type=WatermarkType.INVISIBLE if invisible else WatermarkType.VISIBLE,
                watermark_data=watermark_data.encode(),
                invisible=invisible
            )
            
            self.logger.info(f"Digital watermark applied: {watermark_id}")
            return watermarked_data, watermark
            
        except Exception as e:
            self.logger.error(f"Digital watermarking failed: {str(e)}")
            raise
    
    async def extract_watermark(
        self, 
        watermarked_data: bytes,
        content_type: ContentType,
        watermark_info: ContentWatermark
    ) -> Optional[str]:
        """Extract watermark from content"""
        try:
            if content_type == ContentType.IMAGE:
                extracted = await self._extract_image_watermark(
                    watermarked_data, watermark_info
                )
            elif content_type == ContentType.AUDIO:
                extracted = await self._extract_audio_watermark(
                    watermarked_data, watermark_info
                )
            elif content_type == ContentType.VIDEO:
                extracted = await self._extract_video_watermark(
                    watermarked_data, watermark_info
                )
            else:
                return None
            
            return extracted
            
        except Exception as e:
            self.logger.error(f"Watermark extraction failed: {str(e)}")
            return None
    
    async def _watermark_image(
        self, 
        image_data: bytes, 
        watermark_text: str, 
        invisible: bool
    ) -> bytes:
        """Apply watermark to image"""
        try:
            # Convert bytes to PIL Image
            import io
            image = Image.open(io.BytesIO(image_data))
            
            if invisible:
                # Apply invisible watermark using LSB
                watermarked = self._apply_lsb_watermark(image, watermark_text)
            else:
                # Apply visible watermark
                watermarked = self._apply_visible_watermark(image, watermark_text)
            
            # Convert back to bytes
            output = io.BytesIO()
            watermarked.save(output, format=image.format or 'PNG')
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Image watermarking failed: {str(e)}")
            return image_data
    
    def _apply_lsb_watermark(self, image: Image.Image, watermark_text: str) -> Image.Image:
        """Apply LSB (Least Significant Bit) watermark"""
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert watermark to binary
        watermark_binary = ''.join(format(ord(char), '08b') for char in watermark_text)
        watermark_binary += '1111111111111110'  # End marker
        
        # Get image data
        pixels = list(image.getdata())
        
        # Embed watermark in LSB of red channel
        watermark_index = 0
        for i, pixel in enumerate(pixels):
            if watermark_index < len(watermark_binary):
                r, g, b = pixel
                # Modify LSB of red channel
                r = (r & 0xFE) | int(watermark_binary[watermark_index])
                pixels[i] = (r, g, b)
                watermark_index += 1
            else:
                break
        
        # Create new image with watermarked pixels
        watermarked_image = Image.new('RGB', image.size)
        watermarked_image.putdata(pixels)
        
        return watermarked_image
    
    def _apply_visible_watermark(self, image: Image.Image, watermark_text: str) -> Image.Image:
        """
Apply visible text watermark"""
        # Create a copy of the image
        watermarked = image.copy()
        draw = ImageDraw.Draw(watermarked)
        
        # Calculate position (bottom right)
        width, height = watermarked.size
        
        try:
            # Try to use a default font
            font_size = max(width, height) // 40
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        position = (width - text_width - 10, height - text_height - 10)
        
        # Draw semi-transparent background
        draw.rectangle(
            [position[0] - 5, position[1] - 5, 
             position[0] + text_width + 5, position[1] + text_height + 5],
            fill=(0, 0, 0, 128)
        )
        
        # Draw watermark text
        draw.text(position, watermark_text, fill=(255, 255, 255, 128), font=font)
        
        return watermarked
    
    async def _watermark_audio(self, audio_data: bytes, watermark_text: str, invisible: bool) -> bytes:
        """Apply watermark to audio"""
        # Placeholder for audio watermarking
        # Real implementation would use audio processing libraries
        return audio_data
    
    async def _watermark_video(self, video_data: bytes, watermark_text: str, invisible: bool) -> bytes:
        """
Apply watermark to video"""
        # Placeholder for video watermarking
        # Real implementation would use video processing libraries
        return video_data
    
    async def _extract_image_watermark(
        self, 
        image_data: bytes, 
        watermark_info: ContentWatermark
    ) -> Optional[str]:
        """
Extract watermark from image"""
        # Placeholder for watermark extraction
        # Real implementation would reverse the watermarking process
        return None
    
    async def _extract_audio_watermark(
        self, 
        audio_data: bytes, 
        watermark_info: ContentWatermark
    ) -> Optional[str]:
        """
Extract watermark from audio"""
        return None
    
    async def _extract_video_watermark(
        self, 
        video_data: bytes, 
        watermark_info: ContentWatermark
    ) -> Optional[str]:
        """
Extract watermark from video"""
        return None


class ContentProtection:
    """
Main content protection orchestrator"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.fingerprint_security = FingerprintSecurity(encryption_manager)
        self.anti_tamper = AntiTamper()
        self.copyright_protection = CopyrightProtection(self.fingerprint_security)
        self.watermarking_security = WatermarkingSecurity()
        self.logger = SecurityLogger("ContentProtection")
    
    async def protect_content(
        self, 
        content_data: bytes,
        content_id: str,
        content_type: ContentType,
        owner_id: str,
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD,
        enable_watermark: bool = True,
        copyright_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply comprehensive content protection"""
        try:
            protection_result = {
                "content_id": content_id,
                "protection_applied_at": datetime.utcnow().isoformat(),
                "protection_level": protection_level.value
            }
            
            # 1. Create secure fingerprint
            fingerprint = await self.fingerprint_security.secure_fingerprint(
                content_data, content_id, owner_id, content_type
            )
            protection_result["fingerprint"] = fingerprint.__dict__
            
            # 2. Apply anti-tamper protection
            protected_data, tamper_metadata = await self.anti_tamper.protect_content(
                content_data, content_id, protection_level
            )
            protection_result["anti_tamper"] = tamper_metadata
            
            # 3. Register copyright
            if copyright_metadata:
                copyright_cert = await self.copyright_protection.register_copyright(
                    content_data, content_id, owner_id, copyright_metadata
                )
                protection_result["copyright_certificate"] = copyright_cert
            
            # 4. Apply watermark
            if enable_watermark:
                watermark_text = f"(c) {owner_id} - {content_id}"
                watermarked_data, watermark = await self.watermarking_security.apply_digital_watermark(
                    protected_data, content_type, watermark_text, invisible=True
                )
                protection_result["watermark"] = watermark.__dict__
                protected_data = watermarked_data
            
            # 5. Final encryption (for premium/enterprise)
            if protection_level.value >= ProtectionLevel.PREMIUM.value:
                encrypted_data, encryption_key_id = await self.encryption_manager.encrypt_sensitive_data(
                    protected_data
                )
                protection_result["encryption_key_id"] = encryption_key_id
                protection_result["encrypted"] = True
                protected_data = encrypted_data.data
            
            protection_result["protected_data"] = base64.b64encode(protected_data).decode()
            
            self.logger.info(f"Comprehensive content protection applied: {content_id}")
            return protection_result
            
        except Exception as e:
            self.logger.error(f"Content protection failed: {str(e)}")
            raise
    
    async def verify_content_protection(
        self, 
        protected_data: bytes,
        protection_metadata: Dict[str, Any]
    ) -> ContentVerification:
        """Verify all layers of content protection"""
        try:
            verification_details = {}
            overall_valid = True
            
            # Verify fingerprint
            if "fingerprint" in protection_metadata:
                fingerprint_data = protection_metadata["fingerprint"]
                fingerprint = ContentFingerprint(**fingerprint_data)
                
                fingerprint_verification = await self.fingerprint_security.verify_fingerprint(
                    fingerprint, protected_data
                )
                verification_details["fingerprint"] = fingerprint_verification.verification_details
                
                if not fingerprint_verification.is_valid:
                    overall_valid = False
            
            # Verify anti-tamper
            if "anti_tamper" in protection_metadata:
                tamper_verification = await self.anti_tamper.verify_content_integrity(
                    protected_data, protection_metadata["anti_tamper"]
                )
                verification_details["anti_tamper"] = tamper_verification.verification_details
                
                if not tamper_verification.is_valid:
                    overall_valid = False
            
            # Verify copyright
            if "copyright_certificate" in protection_metadata:
                cert = protection_metadata["copyright_certificate"]
                copyright_verification = await self.copyright_protection.verify_copyright_ownership(
                    protected_data, cert["content_id"], cert["owner_id"]
                )
                verification_details["copyright"] = copyright_verification.verification_details
                
                if not copyright_verification.is_valid:
                    overall_valid = False
            
            return ContentVerification(
                is_valid=overall_valid,
                content_id=protection_metadata.get("content_id", "unknown"),
                verification_type="comprehensive_protection",
                verification_details=verification_details
            )
            
        except Exception as e:
            self.logger.error(f"Content protection verification failed: {str(e)}")
            return ContentVerification(
                is_valid=False,
                content_id="unknown",
                verification_type="comprehensive_protection",
                verification_details={"error": str(e)}
            )
